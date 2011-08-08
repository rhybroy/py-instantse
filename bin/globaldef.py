# encoding:utf-8
# author: TroyCheng
# email: frostmourn716@gmail.com
# filename: global.py
# intro: Mainly contains the global variables and functions

import os
import sys
import ConfigParser
import logging
import logging.config 
from multiprocessing import Queue

# current working path
CUR_PATH = sys.path[0] + os.sep

# config files location
CONFIG_FILE = CUR_PATH + "../conf/search.cfg"
LOG_CONFIG = CUR_PATH + "../conf/logger.cfg"

# get the global logger
logging.config.fileConfig(LOG_CONFIG)
slog = logging.getLogger('search')
plog = logging.getLogger('push')
ilog = logging.getLogger('index')

# define config file parser class
class Config(object):

    def __init__(self):
        self.__parser = ConfigParser.ConfigParser()
        self.__configFile = CONFIG_FILE 
        self.__info = "info"
        self.__xapian = "xapian"

    def __getValue(self, sec, key):
        if not sec or not key:
            slog.error("Invalid parameter. [sec]: %s, [key]: %s" % (sec, key))
            return False

        try:
            fp = open(self.__configFile)
            self.__parser.readfp(fp)
            value = self.__parser.get(sec, key)
            fp.close()
        except Exception,e:
            slog.critical("Exception caught, [Exception]: %s" % e)
            return False
        else:
            return value

    def get(self, key):
        return self.__getValue(self.__info, key)

    def getXapian(self, key):
        return self.__getValue(self.__xapian, key)

# define Global Config object
config = Config()

# define the message Queue
MAX_MSG_QUEUESIZE = int(config.get("message_queue"))
MSG_QUEUE = Queue(MAX_MSG_QUEUESIZE)
