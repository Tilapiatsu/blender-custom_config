import os
import sys
import json
import tempfile
import logging
import shutil
from os import path

current_folder = os.getcwd()


def get_log_file():
	try:
		filepath = current_folder
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
		self.format = 'LINEUP MAKER : %(asctime)s - %(levelname)s : {} :    %(message)s'.format(
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
	

class File(object):
	def __init__(self, path):
		self.log = Logger('LMFile')
		self.path = path
		self._name = None
		self._file = None
		self._ext = None
		self._is_compatible_ext = None
		self._compatible_format = None

	@property
	def name(self):
		if self._name is None:
			self._name = path.basename(path.splitext(self.path)[0])

		return self._name

	@property
	def file(self):
		if self._file is None:
			self._file = path.basename(self.path)

		return self._file

	@property
	def ext(self):
		if self._ext is None:
			self._ext = path.splitext(self.file)[1].lower()

		return self._ext

	@property
	def dirname(self):
		return path.dirname(self.path)

	@property
	def is_compatible_ext(self):
		if self._is_compatible_ext is None:
			self._is_compatible_ext = self.ext in self.compatible_formats.keys()

		return self._is_compatible_ext

	@property
	def compatible_format(self):
		if self._compatible_format is None:
			if self._is_compatible_ext:
				self._compatible_format = self.compatible_formats[self.ext]
			else:
				self._compatible_format = False

		return self._compatible_format

	@property
	def compatible_formats(self):
		return {}


class Json(File):
	def __init__(self, json_path):
		super(Json, self).__init__(json_path)
		self.log = Logger('LMJson')
		self._json_data = None


	# Properties
	@property
	def is_valid(self):
		return path.isfile(self.path)

	@property
	def json_data(self):
		self._json_data = self.get_json_data()

		return self._json_data

	def get_json_attr(self, attr):
		if not self.json_data:
			return ''
		else:
			if attr in self.json_data:
				return self.json_data[attr]
			else:
				self.log.warning('Attribute "{}" doesn\'t exist in json data'.format(attr))
				return ''

	def get_json_data(self):
		json_data = {}
		if not self.is_valid:
			return False

		with open(self.path, 'r', encoding='utf-8-sig') as json_file:
			data = json.load(json_file)
			json_data = data

		return json_data

class PathAM():
	def __init__(self, path):
		self._path = path

	@property
	def path(self):
		if self._path is None:
			return None
		else:
			return self._path.replace('#', current_folder)

	@property
	def exists(self):
		return path.exists(self.path)
	
	@property
	def is_file(self):
		return path.isfile(self.path)
	
	@property
	def is_dir(self):
		return path.isdir(self.path)
	
	def remove(self):
		if self.is_file:
			target = 'Dir'
		elif self.is_dir:
			target = 'File'

		if path.islink(self.path):
			print(f'Unlink {target} {self.path}')
			os.unlink(self.path)
		else:
			print(f'Remove {target} {self.path}')
			if self.is_file:
				os.remove(self.path)
			elif self.is_dir:
				shutil.rmtree(self.path)


class PathElementAM():
	def __init__(self, path_dict, local_path):
		self._path_dict = path_dict
		self.local_path = local_path

	@property
	def is_enable(self):
		return self._path_dict['enable']

	@property
	def local_subpath(self):
		if self._path_dict['local_subpath'] is None:
			return self.local_path
		else:
			return PathAM(path.join(self.local_path.path, self._path_dict['local_subpath']))
	
	@property
	def destination_path(self):
		return PathAM(self._path_dict['destination_path'])
	

class ElementAM():
	def __init__(self, element_dict, name):
		self._element_dict = element_dict
		self.name = name

	@property
	def is_sync(self):
		return self._element_dict['sync']

	@property
	def is_enable(self):
		return self._element_dict['enable']
	
	@property
	def online_url(self):
		return self._element_dict['online_url']
	
	@property
	def local_path(self):
		return PathAM(self._element_dict['local_path'])
	
	@property
	def paths(self):
		if self._element_dict['paths'] is None:
			return []
		else:
			return [PathElementAM(x, self.local_path) for x in self._element_dict['paths']]
		


class AddonManager():
	def __init__(self, json_path):
		self._json_path = json_path
		self.json = Json(json_path)

	@property
	def elements(self):
		return {k: ElementAM(v, k) for k,v in self.json.json_data.items() if k[0] != '_'}
	
	def sync(self):
		pass
	
	def link(self):
		pass

	def __str__(self):
		s = ''
		for k,v in self.elements.items():
			s += f'----------------------------------------{k}----------------------------------------\n'
			s += f'is_enable = {v.is_enable}\n'
			s += f'is_sync = {v.is_sync}\n'
			s += f'local_path = {v.local_path.path}\n'
			s += f'online_url = {v.online_url}\n'
			for p in v.paths:
				s += f'paths.is_enable = {p.is_enable}\n'
				s += f'paths.local_subpath = {p.local_subpath.path}\n'
				s += f'paths.destination_path = {p.destination_path.path}\n'
		
		return s

if __name__ == '__main__':
	AM = AddonManager(path.join(current_folder, 'EnabledAddons.json'))

	print(AM)
