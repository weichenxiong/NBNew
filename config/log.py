# coding=utf-8

__all__ = [
    'getLogger',
    'DEBUG',
    'INFO',
    'WARN',
    'ERROR',
    'FATAL']

import os
import time
import logging
import logging.handlers
from logging import getLogger, INFO, WARN, DEBUG, ERROR, FATAL, WARNING, CRITICAL


LOG_FILE_MAX_BYTES = 1024 * 1024 * 100
LOG_FILE_BACKUP_COUNT = 1000
LOG_LEVEL = logging.DEBUG

FORMAT = '%(asctime)s %(levelname) 8s <%(name)s> {%(filename)s:%(lineno)s} -> %(message)s'
formatter = logging.Formatter(FORMAT)

level_dict = {
    "debug": logging.DEBUG,
    "DEBUG": logging.DEBUG,
    "info": logging.INFO,
    "INFO": logging.INFO,
    "warn": logging.WARN,
    "WARN": logging.WARN,
    "error": logging.ERROR,
    "ERROR": logging.ERROR
}

class LOG(object):

    def __init__(self):
        self._normal = None
        self._error = None
        self.name = None
        self.log_dir = None
        self.last_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))   # 存放上一次打印日志的时间(字符串)

    def get_normal_log(self, level):
        """生成日志"""
        date_format = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        file_name = '{0}/{1}_{2}.log'.format(self.log_dir, self.name, date_format)
        logging.basicConfig(level=level)
        file_log_handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=LOG_FILE_MAX_BYTES,
                                                              backupCount=LOG_FILE_BACKUP_COUNT)                                                    
        formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
        file_log_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_log_handler)

    def init(self, module_name, log_dir, level):
        self.set_module_name(module_name)
        self.set_log_dir(log_dir)
        self.set_log_level(level)

    def set_module_name(self, name):
        self.name = name

    def set_log_dir(self, log_dir):
        """
        设置日志目录
        """
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.system("mkdir -p %s" % log_dir)

    def set_log_level(self, level):
        """设置日志级别"""
        level = level_dict.get(level)
        self.get_normal_log(level)

logger = LOG()
