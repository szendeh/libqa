import fnmatch
import logging
import os
import requests
import shutil
import sys
import time

logging.basicConfig(level       = logging.INFO, 
                    filename    = 'log.txt',
                    format      = '%(asctime)s %(message)s')

logger = logging

def testLine(line):
    try:
        r = requests.get(line)
        if (r.status_code == 200):
            return True
        else:
            print "{} '{}'".format('status:', r.status_code)
            return False
    except requests.exceptions.RequestException as e:
        logger.error(e)
        print e
        return False

def processFiles(pid):
    """once there are files in a temp dir, this will:
    1. build a list of all urls to test ('process list')
    2. opens any existing success file
        - if none exists, create a new one
        - build an array of already succeeded urls from that file
    3. opens a new failed file for writing, overwriting the old file
    4. opens the success file for appending
    5. iterates through process list
        - skip if url exists in success list
        - test the url
        - if success, add url to success file
        - if failed, add to failed file
    6. move the failed file back to app root
    7. clean up temp dir
    """

    process_dirname     = 'process_'+ pid
    success_filename    = process_dirname +'/'+ 'process_success_list.txt'
    failed_filename     = process_dirname +'/'+ 'process_failed_list.txt'

    file_list = fnmatch.filter(os.listdir(process_dirname), 'new*.txt') + fnmatch.filter(os.listdir(process_dirname), 'failed*.txt')

    if (len(file_list)):
        try:
            # maintain a list of already-tested links *for this run*
            # note that this can be different than just the success_file list
            # because we may simply have duplicate urls, and we don't want to bother
            # re-testing them in any single run, whether or not they succeed
            tested_list = []

            if (os.path.isfile(success_filename)):
                with open(success_filename, 'r') as success_file:
                    for line in success_file:
                        tested_list.append(line.strip())

            with open(success_filename, 'a') as success_file, open(failed_filename, 'w') as failed_file:
                for filename in file_list:
                    logger.info('processing file: '+ filename)

                    with open(process_dirname +'/'+ filename, 'r') as processing_file:
                        for line in processing_file:
                            line = line.strip()

                            if (line == ''):
                                logger.info('blank line')
                            elif (line in tested_list):
                                logger.info("duplicate line '"+ line +"'")
                            else:
                                logger.info("testing url '"+ line +"'")

                                if (testLine(line) == True):
                                    success_file.write(line +"\n")
                                else:
                                    failed_file.write(line +"\n")

                                tested_list.append(line)

            if (os.path.getsize(failed_filename)):
                shutil.move(failed_filename, './failed_'+ pid +'.txt')

            shutil.rmtree(process_dirname)
        except IOError as e:
            logger.error(e)

def moveFiles(pid):
    """when there are existing files in the app root dir
    the app will move them to a temp dir for processing
    this eliminates the chance that running this app twice
    will cause problems"""

    process_dirname = 'process_'+ pid

    file_list = fnmatch.filter(os.listdir('.'), 'new*.txt') + fnmatch.filter(os.listdir('.'), 'failed*.txt')

    logger.info('found files: '+ ','.join(file_list))

    if (len(file_list)):
        try:
            os.mkdir(process_dirname)
            
            # move the files to process into a temp processing dir
            for filename in file_list:
                shutil.move(filename, process_dirname +'/'+ filename)
        except IOError as e:
            logger.error(e)

    return(file_list)

def main():
    logger.info('start '+ sys.argv[0])

    # specified an existing run to re-try
    if (len(sys.argv)>1):
        pid = sys.argv[1]

        processFiles(pid)

    # kick off a fresh run
    else:
        pid = time.strftime("%Y%m%d_%H%M%S")

        if (len(moveFiles(pid))):
            processFiles(pid)

    logger.info('end '+ sys.argv[0])

if __name__ == "__main__":
   main()