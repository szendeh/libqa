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
    print line

def processFiles(pid):
    process_dirname     = 'process_'+ pid
    success_filename    = process_dirname +'/'+ 'process_success_list.txt'
    error_filename      = process_dirname +'/'+ 'process_error_list.txt'

    file_list = fnmatch.filter(os.listdir(process_dirname), 'new*.txt') + fnmatch.filter(os.listdir(process_dirname), 'error*.txt')

    if (len(file_list)):
        try:
            # make sure we capture the list of already-processed files (if any)
            success_list = []

            if (os.path.isfile(success_filename)):
                with open(success_filename, 'r') as success_file:
                    for line in success_file:
                        success_list.push(line)

            with open(success_filename, 'a') as success_file, open(error_filename, 'w') as error_file:
                for filename in file_list:
                    logger.info('processing file: '+ filename)

                    with open(process_dirname +'/'+ filename, 'r') as processing_file:
                        for line in processing_file:
                            if (line not in success_list):
                                if (testLine(line) === True):
                                    success_file.write(line)
                                else:
                                    error_file.write(line)
        except IOError as e:
            print 'ERROR: '+ e

        try:
            if (os.path.getsize(error_filename)):
                shutil.move(error_filename, './error_'+ )

def moveFiles(pid):
    process_dirname = 'process_'+ pid

    file_list = fnmatch.filter(os.listdir('.'), 'new*.txt') + fnmatch.filter(os.listdir('.'), 'error*.txt')

    logger.info(__name__ +' found files: '+ ','.join(file_list))

    if (len(file_list)):
        try:
            os.mkdir(process_dirname)
            
            # move the files to process into a temp processing dir
            for filename in file_list:
                shutil.move(filename, process_dirname +'/'+ filename)
        except IOError as e:
            print 'ERROR: '+ e

    return(file_list)

logger.info('start '+ sys.argv[0])

if (sys.argv[1]):
    # specified an existing run to re-try
    pid = sys.argv[1]

    processFiles(pid)
else:
    # kick off a fresh run
    pid = time.strftime("%Y%m%d_%H%M%S")

    if (len(moveFiles(pid))):
        processFiles(pid)

logger.info('end '+ sys.argv[0])