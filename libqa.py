import fnmatch
import logging
import os
import requests
import shutil
import time

logging.basicConfig(level       = logging.INFO, 
                    filename    = 'logs/error.log',
                    format      = '%(asctime)s %(message)s')

pid = time.strftime("%Y%m%d_%H%M%S")

logger = logging

logger.info('start pid '+ pid)

new_file_list = fnmatch.filter(os.listdir('.'), 'new*.txt')
error_file_list = fnmatch.filter(os.listdir('.'), 'error*.txt')

if (len(new_file_list) or len(error_file_list)):
    logger.info('found new/error files. moving new: '+ ', '.join(new_file_list) +' moving error: '+ ', '.join(error_file_list))

    try:
        process_dirname = 'process_'+ pid
        os.mkdir(process_dirname)
        
        # move the files to process into a temp processing dir
        for filename in new_file_list:
            shutil.move(filename, process_dirname +'/'+ filename)
        
        for filename in error_file_list:
            shutil.move(filename, process_dirname +'/'+ filename)

        with open('success_list.txt', 'w+') as success_file, open('error_list.txt', 'w+') as error_file:
            for filename in new_file_list:
                with open(process_dirname +'/'+ filename, 'r') as processing_file:
                    for line in processing_file:
                        print line
                    
    except IOError as e:
        print 'ERROR: '+ e
else:
    logger.info('no new/error files found')

logger.info('end pid '+ pid)