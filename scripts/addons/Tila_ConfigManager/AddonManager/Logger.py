import tempfile
import logging
import os
from os import path
import bpy

root_folder = path.dirname(bpy.utils.script_path_user())

def get_log_file():
	try:
		filepath = root_folder
	except AttributeError:
		filepath = ''
	if path.exists(filepath):
		log_file = path.join(path.dirname(filepath), '{}.log'.format(
			path.splitext(path.basename(filepath))[0]))
	else:
		tempf = tempfile.TemporaryFile().name
		log_file = '{}.log'.format(tempf)

	return log_file

class Logger(object):
	def __init__(self, context='ROOT'):
		self.context = context

		self.log_file = get_log_file()
		self.timeformat = '%m/%d/%Y %I:%M:%S %p'
		self.set_basic_config()

		self.success = []
		self.failure = []
		# self.message_list = []

		self._pretty = '---------------------'

	def info(self, message, asset=None, print_log=True):
		self.set_basic_config()
		if asset is not None:
			warning = asset.warnings.add()
			warning.message = message
		# if print_log:
		# 	self.message_list.append(message)
		# 	print_progress(bpy.context, self.message_list, title=self.context, icon='NONE')
		logging.info(message)

	def debug(self, message, asset=None, print_log=True):
		self.set_basic_config()
		if asset is not None:
			warning = asset.warnings.add()
			warning.message = message
		# if print_log:
		# 	self.message_list.append(message)
		# 	print_progress(bpy.context, self.message_list, title=self.context, icon='NONE')
		logging.debug(message)

	def warning(self, message, asset=None, print_log=True):
		self.set_basic_config()
		if asset is not None:
			warning = asset.warnings.add()
			warning.message = message
		# if print_log:
		# 	self.message_list.append(message)
		# 	print_progress(bpy.context, self.message_list, title=self.context, icon='NONE')
		logging.warning(message)

	def error(self, message, asset=None, print_log=True):
		self.set_basic_config()
		if asset is not None:
			warning = asset.warnings.add()
			warning.message = message
		# if print_log:
		# 	self.message_list.append(message)
		# 	print_progress(bpy.context, self.message_list, title=self.context, icon='NONE')
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