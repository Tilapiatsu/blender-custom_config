import tempfile
import logging
import time
from os import path
from ...config_const import LOG_PREFIX

root_folder = __file__

def get_log_file():

    log_file = LOG_PREFIX + time.strftime(f"%Y%m%d") + ".log"
    log_file = path.join(tempfile.gettempdir(), log_file)
    
    print('Tila Config : Log file path :', log_file)

    return log_file

class LOG(object):
	def __init__(self, context='ROOT'):
		self.context = context

		self.log_file = get_log_file()
		self.timeformat = '%m/%d/%Y %I:%M:%S %p'
		self.set_basic_config()

		self.success = []
		self.failure = []
		# self.message_list = []

		self._pretty = '---------------------'

	def info(self, message, print_log=True):
		if print_log:
			print(message)
		self.set_basic_config()
		logging.info(message)

	def debug(self, message, print_log=True):
		if print_log:
			print(message)
		self.set_basic_config()
		logging.debug(message)

	def warning(self, message, print_log=True):
		if print_log:
			print(message)
		self.set_basic_config()
		logging.warning(message)

	def error(self, message, print_log=True):
		if print_log:
			print(message)
		self.set_basic_config()
		logging.error(message)

	def set_basic_config(self):
		self.format = '%(asctime)s - %(levelname)s : {} :    %(message)s'.format(
			self.context)
		logging.basicConfig(filename=self.log_file, level=logging.DEBUG,
                      datefmt=self.timeformat, filemode='w', format=self.format)

	def store_success(self, success):
		self.success.append(success)

	def store_failure(self, failure):
		self.failure.append(failure)

	def pretty(self, str):

		p = self._pretty

		for c in str:
			p += '-'

		return p