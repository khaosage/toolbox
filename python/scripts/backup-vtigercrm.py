#!/usr/bin/python

from subprocess import Popen, PIPE, STDOUT
from subprocess import call as subcall
from time import time, strftime
from shutil import rmtree
import os, errno
import logging
from logging.config import dictConfig

staging_db = "vtiger_test"
production_db = "vtiger"

timestr = strftime("%Y-%m-%d")

logfile="/backup/backup.log"

logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}
         },
    handlers = {
         'h': {'class': 'logging.FileHandler',
               'filename': logfile,
               'formatter': 'f',
               'level': logging.INFO}
         },
    loggers = {
         'Main': {'handlers': ['h'],
                  'level': logging.INFO},
         'CreateDirs': {'handlers': ['h'],
                  'level': logging.INFO},
         'CleanUp': {'handlers': ['h'],
                  'level': logging.INFO}
         }
)

dictConfig(logging_config)
logger = logging.getLogger('Main')

def mk_backup_dirs(timestr, environment):
    dictConfig(logging_config)
    logger = logging.getLogger('CreateDir')
    path = ("/backup/" + timestr + "/" + environment)
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            logger.error("%s" % err)

def get_source(environment, directory):
    source=("/home/deployer/" + environment + "/" + directory)
    return source

def get_destination(timestr, environment):
    destination=("/backup/" + timestr + "/" + environment)
    return destination

def sync(source, destination):
    subcall(['rsync','-WLa', source, destination])

def do_sync(environment, directory):
    source = get_source(environment, directory)
    destination = get_destination(timestr, environment)
    sync(source, destination)

def dump_db(environment, db_name):
    dump_name = ( db_name + "-" + environment + "-" + timestr + ".sql.gz")
    outfile = ("/backup/" + timestr + "/" + environment + "/" + dump_name)

    args = ['/usr/bin/mysqldump', db_name]

    with open(outfile, 'wb', 0) as f:
        p1 = Popen(args, stdout=PIPE)
        p2 = Popen('gzip', stdin=p1.stdout, stdout=f)

    p1.stdout.close()
    p2.wait()
    p1.wait()

def do_clean():
    numdays = 86400*7
    now = time()
    dictConfig(logging_config)
    logger = logging.getLogger('CleanUp')

    for dir in os.listdir('/backup'):
        logger = logging.getLogger('CleanUp')
        timestamp = os.path.getmtime("/backup/" + dir)
        if now-numdays > timestamp:
            try:
                rmtree("/backup/" + dir)
                logger.info("Removing Directory: /backup/%s" % dir)
            except Exception,e:
                logger.error("%s" % e)

def main():
    logger.debug(" [%s] Started Backup for Staging" % timestr)
    
    mk_backup_dirs(timestr=timestr, environment="staging")
    do_sync(environment="staging", directory="current")
    do_sync(environment="staging", directory="shared")
    dump_db(environment="staging", db_name=staging_db)
    logger.info("Completed Staging for [%s]" % timestr)

    mk_backup_dirs(timestr=timestr, environment="production")
    do_sync(environment="production", directory="current")
    do_sync(environment="production", directory="shared")
    dump_db(environment="production", db_name=production_db)
    logger.info("Completed Production for [%s]" % timestr)

    do_clean()
    logger.info("Completed CleanUp for [%s]" % timestr)

if __name__=='__main__':
    main()