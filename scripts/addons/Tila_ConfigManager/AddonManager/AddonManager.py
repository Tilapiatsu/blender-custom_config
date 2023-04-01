import os
import sys
import json
import shutil
import subprocess
import stat
import bpy
from os import path
from . import admin
from . Logger import Logger

root_folder = path.dirname(bpy.utils.script_path_user())

dependencies = ['gitpython']

create_symbolic_link_file = path.join(path.dirname(path.realpath(__file__)), 'create_symbolic_link.py')


def install_dependencies():
	current_dir = path.dirname(path.realpath(__file__))
	dependencies_path = path.join(current_dir, 'Dependencies')
	print(dependencies_path)
	if dependencies_path not in sys.path:
		sys.path.append(dependencies_path)

	if not path.exists(dependencies_path):
		os.mkdir(dependencies_path)
		install = True
	else:
		install = False
		dependency_subfolder = os.listdir(dependencies_path)

		for d in dependencies:
			found = False
			for s in dependency_subfolder:
				if d.lower() in s.lower():
					found = True
				
			if not found:
				install = True
				break

	if not install:
		return 
	subprocess.check_call([sys.executable, '-m', 'pip', 'install',
						  *dependencies, '--target', dependencies_path])

def enable_addon(addon_name):
	if addon_name in bpy.context.preferences.addons:
		return False
	
	print(f'Enabling Addon : {addon_name}')
	bpy.ops.preferences.addon_enable(module=addon_name)
	bpy.context.window_manager.keyconfigs.update()	
	print(f'Enable Done!')

	return True


def disable_addon(addon_name):
	if addon_name not in bpy.context.preferences.addons:
		return False
	
	print(f'Disabling Addon : {addon_name}')
	bpy.ops.preferences.addon_disable(module=addon_name)
	bpy.context.window_manager.keyconfigs.update()
	print(f'Disable Done!')

	return True
	
def file_acces_handler(func, path, exc_info):
	# print('Handling Error for file ', path)
	# print(exc_info)
	# Check if file access issue
	if not os.access(path, os.W_OK):
		# Try to change the permision of file
		os.chmod(path, stat.S_IWUSR)
		# call the calling function again
		func(path)

try:
	import git
except (ModuleNotFoundError, ImportError) as e:
	print(e)
	install_dependencies()
	import git


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
			return self._path.replace('#', root_folder)

	@property
	def exists(self):
		if self.path is None:
			return False
		return path.exists(self.path)
	
	@property
	def is_file(self):
		if self.path is None:
			return False
		return path.isfile(self.path)
	
	@property
	def is_dir(self):
		if self.path is None:
			return False
		return path.isdir(self.path)
	
	def remove(self):
		if self.is_file:
			target = 'File'
		elif self.is_dir:
			target = 'Directory'

		if path.islink(self.path):
			print(f'Unlink {target} {self.path}')
			os.unlink(self.path)
		else:
			print(f'Remove {target} {self.path}')
			if self.is_file:
				os.remove(self.path)
			elif self.is_dir:
				shutil.rmtree(self.path, onerror=file_acces_handler)


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
	
	def clean(self):
		if self.destination_path.exists:
			if not self.is_enable:
				self.destination_path.remove()
				print(f'Clean Done!')

	def link(self, overwrite=False):
		if not self.is_enable:
			return None
		
		if self.local_subpath.path is None or self.destination_path.path is None:
			return None
		
		if self.destination_path.exists:
			if overwrite:
				self.destination_path.remove()
			else:
				# print(f'Path Already Exists : Skipping {self.destination_path.path}')
				return None

		print(f'Linking {self.local_subpath.path} -> {self.destination_path.path} {self.local_subpath.is_dir}')
		return str([self.local_subpath.path, self.destination_path.path, self.local_subpath.is_dir])
	
	def enable(self):
		if not self.is_enable:
			return
		
		if self.destination_path.is_file:
			addon_name = path.splitext(path.basename(self.destination_path.path))[0]

			if not enable_addon(addon_name):
				return
		elif self.destination_path.is_dir:
			addon_name = path.basename(self.destination_path.path)

			if not enable_addon(addon_name):
				return
		
	def disable(self):
		if self.is_enable:
			return
		
		addon_name = path.splitext(path.basename(self.destination_path.path))[0]
		
		if not disable_addon(addon_name):
			return
			
class ElementAM():
	def __init__(self, element_dict, name):
		self._element_dict = element_dict
		self.name = name
	
	def __str__(self):
		s = ''
		s += f'----------------------------------------{self.name}----------------------------------------\n'
		s += f'is_enable = {self.is_enable}\n'
		s += f'is_sync = {self.is_sync}\n'
		s += f'local_path = {self.local_path.path}\n'
		s += f'online_url = {self.online_url}\n'
		for p in self.paths:
			s += f'paths.is_enable = {p.is_enable}\n'
			s += f'paths.local_subpath = {p.local_subpath.path}\n'
			s += f'paths.destination_path = {p.destination_path.path}\n'

		return s

	@property
	def is_sync(self):
		return self._element_dict['sync']

	@property
	def is_enable(self):
		return self._element_dict['enable']
	
	@property
	def branch(self):
		return self._element_dict['branch']
	
	@property
	def submodule(self):
		return self._element_dict['submodule']

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
	
	def ensure_repo_init(self):
		subdir = os.listdir(self.local_path.path)

		if '.git' not in [path.dirname(s) for s in subdir]:
			repo = git.Repo(root_folder)
			repo.git.submodule('update', '--init')
	
	def clean(self):
		for p in self.paths:
			p.clean()
			
	def sync(self, overwrite=False):
		if not self.is_sync:
			return
		if self.online_url is None or self.local_path.path is None:
			return
		
		if self.local_path.exists and not self.submodule:
			if overwrite:
				self.local_path.remove()
			else:
				# print(f'Path Already Exists : Skipping {self.local_path.path}')
				return
		
		print(f'Syncing {self.name} to {self.local_path.path}')
		if self.submodule:
			self.ensure_repo_init()
			repo = git.Repo(self.local_path.path)
			repo.git.submodule('update', '--init')
			if self.branch is not None:
				repo.git.checkout(self.branch)
		else:
			kwargs = {'branch': self.branch} if self.branch is not None else {}
			# if self.branch is not None:
			git.Repo.clone_from(self.online_url, self.local_path.path, **kwargs)
		
		print(f'Syncing Done!')

	def link(self, overwrite=False):
		if self.local_path.path is None:
			return []
		
		link_commands = []
		for p in self.paths:
			command = p.link(overwrite=overwrite)
			if command is None:
				continue
			link_commands.append(p.link(overwrite=overwrite))
		
		return link_commands
	
	def enable(self):
		if not self.is_enable:
			return
		
		if not len(self.paths):
			enable_addon(self.name)
		else:
			for p in self.paths:
				p.enable()

	def disable(self):
		if self.is_enable:
			return

		if not len(self.paths):
			disable_addon(self.name)
		else:
			for p in self.paths:
				p.disable()

class AddonManager():
	def __init__(self, json_path):
		self._json_path = json_path
		self.json = Json(json_path)
		self.processing = False
		self.queue_list = []
		self.log = Logger('AddonManager')

	@property
	def elements(self):
		return {k: ElementAM(v, k) for k,v in self.json.json_data.items() if k[0] != '_'}
	
	def queue_clean(self, element_name=None):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.clean, {'element_name': e.name}])
		elif element_name in self.elements.keys():
			self.queue([self.clean, {'element_name': element_name}])
			
	def clean(self, element_name=None):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.clean()
		elif element_name in self.elements.keys():
			self.elements[element_name].clean()
		
		self.processing = False
	
	def queue_sync(self, element_name=None, overwrite=False):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.sync, {'element_name': e.name, 'overwrite': overwrite}])
		elif element_name in self.elements.keys():
			self.queue(
				[self.sync, {'element_name': element_name, 'overwrite': overwrite}])

	def sync(self, element_name=None, overwrite=False):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.sync(overwrite=overwrite)
		elif element_name in self.elements.keys():
			self.elements[element_name].sync(overwrite=overwrite)
		
		self.processing = False

	def queue_link(self, element_name=None, overwrite=False):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.link, {'element_name': e.name, 'overwrite': overwrite}])
		elif element_name in self.elements.keys():
			self.queue([self.link, {'element_name': element_name, 'overwrite': overwrite}])

	def link(self, element_name=None, overwrite=False):
		self.processing = True

		link_command = []
		if element_name is None:
			for e in self.elements.values():
				command = e.link(overwrite=overwrite)
				if not len(command):
					continue
				link_command += command
		elif element_name in self.elements.keys():
			command = self.elements[element_name].link(overwrite=overwrite)
			if not len(command):
				return
			link_command = command

		admin.elevate([create_symbolic_link_file, '--', '--file_to_link', *link_command])

		self.processing = False

	def queue_enable(self, element_name=None):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.enable, {'element_name': e.name}])
		elif element_name in self.elements.keys():
			self.queue([self.enable, {'element_name': element_name}])

	def enable(self, element_name=None):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.enable()
		elif element_name in self.elements.keys():
			self.elements[element_name].enable()

		self.processing = False
	
	def queue_disable(self, element_name=None):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.disable, {'element_name': e.name}])
		elif element_name in self.elements.keys():
			self.queue([self.disable, {'element_name': element_name}])

	def disable(self, element_name=None):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.disable()
		elif element_name in self.elements.keys():
			self.elements[element_name].disable()

		self.processing = False

	def queue(self, action):
		self.queue_list.append(action)

	def flush_queue(self):
		self.queue_list = []

	def next_action(self):
		if len(self.queue_list) == 0:
			print('Queue Done !')
			return
		
		action = self.queue_list.pop(0)

		action[0](**action[1])

	def __str__(self):
		s = ''
		for _,v in self.elements.items():
			s += f'{v}\n'
		
		return s
