import tempfile
import logging
import time
from logging.handlers import RotatingFileHandler
from os import path
from Tila_ConfigManager.config_const import LOG_PREFIX

root_folder = __file__

def get_log_file():

    log_file = LOG_PREFIX + time.strftime(f"%Y%m%d") + ".log"
    log_file = path.join(tempfile.gettempdir(), log_file)

    print('Tila Config : Log file path :', log_file)

    return log_file

class LOG(object):
    def __init__(self, log_name='ROOT'):
        self.log_name = log_name

        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        self.log_file = get_log_file()
        self.timeformat = '%m/%d/%Y %I:%M:%S %p'
        self.set_basic_config()

        self.success = {}
        self.failure = {}
        self.success_count = 0
        self.failure_count = 0

        self._pretty = '---------------------'

    def info(self, message:str, print_log=True):
        if print_log:
            print(message)
        self.logger.info(message)

    def debug(self, message:str, print_log=True):
        if print_log:
            print(message)
        self.logger.debug(message)

    def warning(self, message:str, print_log=True, store_failure=True):
        message = 'WARNING : ' + str(message)
        if print_log:
            print(message)

        if store_failure:
            self.store_failure(message)

        self.logger.warning(message)

    def error(self, message:str, print_log=True, store_failure=True):
        message = 'ERROR : ' + str(message)
        if print_log:
            print(message)

        if store_failure:
            self.store_failure(message)

        self.logger.error(message)

    def set_basic_config(self):
        self.format = logging.Formatter('%(asctime)s - %(levelname)s :    %(message)s')
        handler = RotatingFileHandler(self.log_file, maxBytes=500000, backupCount=3)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.format)
        self.logger.addHandler(handler)

    def store_success(self, success):
        if self.context not in self.success.keys():
            self.success[self.context] = [success]
        else:
            self.success[self.context].append(success)
        self.success_count += 1

    def store_failure(self, failure):
        if self.context not in self.failure.keys():
            self.failure[self.context] = [failure]
        else:
            self.failure[self.context].append(failure)

        self.failure_count += 1

    def pretty(self, str):

        p = self._pretty

        for c in str:
            p += '-'

        return p

    def reset_log(self):
        self.success = {}
        self.failure = {}
        self.success_count = 0
        self.failure_count = 0