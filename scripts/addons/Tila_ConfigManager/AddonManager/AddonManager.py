import os
import sys
import json
import shutil
import subprocess
import stat
import bpy
from . import keymaps
from os import path
from . import admin
from . Logger import Logger
from .log_list import TILA_Config_Log as Log

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
	log_progress = Log(bpy.context.window_manager.tila_config_log_list,
					   'tila_config_log_list_idx')
	if addon_name in bpy.context.preferences.addons:
		print(f'Addon already Enabled : {addon_name}')
		log_progress.start(f'Addon already Enabled : {addon_name}')
		return False
	
	print(f'Enabling Addon : {addon_name}')
	log_progress.start(f'Enabling Addon : {addon_name}')
	bpy.ops.preferences.addon_enable(module=addon_name)
	bpy.context.window_manager.keyconfigs.update()	
	print(f'Enable Done!')
	log_progress.done(f'Enable Done!')

	return True


def disable_addon(addon_name):
	log_progress = Log(bpy.context.window_manager.tila_config_log_list,
					   'tila_config_log_list_idx')
	if addon_name not in bpy.context.preferences.addons:
		print(f'Addon already Disabled : {addon_name}')
		log_progress.start(f'Addon already Disabled : {addon_name}')
		return False
	
	print(f'Disabling Addon : {addon_name}')
	log_progress.start(f'Disabling Addon : {addon_name}')
	bpy.ops.preferences.addon_disable(module=addon_name)
	bpy.context.window_manager.keyconfigs.update()
	print(f'Disable Done!')
	log_progress.done(f'Disable Done!')

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
	
	def save(self, json_dict):
		# Serializing json
		json_object = json.dumps(json_dict, indent=4)
		
		# Writing to output file
		with open(self.path, "w") as outfile:
			outfile.write(json_object)

class PathAM():
	def __init__(self, path):
		self._path = path
		self.log_progress = Log(bpy.context.window_manager.tila_config_log_list,
								'tila_config_log_list_idx')
	
	def __str__(self):
		return self._path if self._path is not None else ''
	
	@property
	def is_set(self):
		return self._path is not None

	@property
	def path(self):
		if self._path is None:
			return None
		else:
			return self._path.replace('#', root_folder)

	@property
	def exists(self):
		if not self.is_set:
			return False
		return path.exists(self.path)
	
	@property
	def is_file(self):
		if not self.is_set:
			return None
		return path.isfile(self.path)
	
	@property
	def is_dir(self):
		if self.path is None:
			return None
		return path.isdir(self.path)
	
	def remove(self):
		if self.is_file:
			target = 'File'
		elif self.is_dir:
			target = 'Directory'

		if path.islink(self.path):
			print(f'Unlink {target} {self.path}')
			self.log_progress.start(f'Unlink {target} {self.path}')
			os.unlink(self.path)
		else:
			print(f'Remove {target} {self.path}')
			self.log_progress.start(f'Remove {target} {self.path}')
			if self.is_file:
				os.remove(self.path)
			elif self.is_dir:
				shutil.rmtree(self.path, onerror=file_acces_handler)


class PathElementAM():
	def __init__(self, path_dict, local_path):
		self._path_dict = path_dict
		self.local_path = local_path
		self.log_progress = Log(bpy.context.window_manager.tila_config_log_list,
								'tila_config_log_list_idx')

	@property
	def is_enable(self):
		return self._path_dict['is_enable']

	@property
	def local_subpath(self):
		return '' if self._path_dict['local_subpath'] is None else self._path_dict['local_subpath']

	@property
	def local_subpath_resolved(self):
		if self._path_dict['local_subpath'] is None:
			return self.local_path
		else:
			return PathAM(path.join(self.local_path.path, self._path_dict['local_subpath']))
	
	@property
	def destination_path(self):
		return PathAM(self._path_dict['destination_path'])
	
	def clean(self, force=False):
		if self.destination_path.exists:
			if not force and self.is_enable:
				return

			self.destination_path.remove()
			print(f'Clean Done!')
			self.log_progress.done(f'Clean Done!')

	def link(self, overwrite=False, force=False):
		if not force and not self.is_enable:
			return None
		
		if self.local_subpath_resolved.path is None or self.destination_path.path is None:
			return None
		
		if self.destination_path.exists:
			if overwrite:
				self.destination_path.remove()
			else:
				# print(f'Path Already Exists : Skipping {self.destination_path.path}')
				return None

		print(f'Linking {self.local_subpath_resolved.path} -> {self.destination_path.path}')
		self.log_progress.start(f'Linking {self.local_subpath_resolved.path} -> {self.destination_path.path}')
		return str([self.local_subpath_resolved.path, self.destination_path.path, self.local_subpath_resolved.is_dir])
	
	def enable(self, force=False):
		if not force and not self.is_enable:
			return
		if not self.destination_path.is_set:
			return
		elif self.destination_path.is_file:
			addon_name = path.splitext(path.basename(self.destination_path.path))[0]

			if not enable_addon(addon_name):
				return
		elif self.destination_path.is_dir:
			addon_name = path.basename(self.destination_path.path)

			if not enable_addon(addon_name):
				return
		
	def disable(self, force=False):
		if not force:
			if self.is_enable:
				return
		
		addon_name = path.splitext(path.basename(self.destination_path.path))[0]
		
		if not disable_addon(addon_name):
			return
			
class ElementAM():
	def __init__(self, element_dict, name):
		self.element_dict = element_dict
		self.name = name
		self.root_folder = root_folder
		self.log_progress = Log(bpy.context.window_manager.tila_config_log_list,
								'tila_config_log_list_idx')
	
	def __str__(self):
		print(self.name)
		s = ''
		s += f'----------------------------------------{self.name}----------------------------------------\n'
		s += f'is_enable = {self.is_enable}\n'
		s += f'is_sync = {self.is_sync}\n'
		s += f'is_submodule = {self.is_submodule}\n'
		s += f'local_path = {self.local_path.path}\n'
		s += f'online_url = {self.online_url}\n'
		s += f'repository_url = {self.repository_url}\n'
		for i in range(len(self.paths)):
			p = self.paths[i]
			s += f'--------------------------------------------------------------------------------\n'
			s += f'path{i}\n'
			s += f'--------------------------------------------------------------------------------\n'
			s += f'paths.is_enable = {p.is_enable}\n'
			s += f'paths.local_subpath_resolved = {p.local_subpath_resolved.path}\n'
			s += f'paths.destination_path = {p.destination_path.path}\n'
			s += ''
			

		return s

	@property
	def is_sync(self):
		return self.element_dict['is_sync']

	@property
	def is_enable(self):
		return self.element_dict['is_enable']
	
	@property
	def is_repository(self):
		return self.repository_url is not None
	
	@property
	def branch(self):
		return self.element_dict['branch']
	
	@property
	def is_submodule(self):
		return self.element_dict['is_submodule']

	@property
	def online_url(self):
		return self.element_dict['online_url']
	
	@property
	def repository_url(self):
		return self.element_dict['repository_url']
	
	@property
	def local_path(self):
		return PathAM(self.element_dict['local_path'])
	
	@property
	def keymaps(self):
		return self.element_dict['keymaps']
	
	@property
	def paths(self):
		if self.element_dict['paths'] is None:
			return []
		else:
			return [PathElementAM(x, self.local_path) for x in self.element_dict['paths']]
	
	def ensure_repo_init(self):
		subdir = os.listdir(self.local_path.path)

		if '.git' not in [path.dirname(s) for s in subdir]:
			repo = git.Repo(root_folder)
			repo.git.submodule('update', '--init')
	
	def clean(self, force=False):
		for p in self.paths:
			p.clean(force=force)

		if force and self.is_sync and not self.is_submodule:
			if self.local_path.exists:
				self.local_path.remove()
				print(f'Clean Done!')
				self.log_progress.done(f'Clean Done!')
			
	def sync(self, overwrite=False, force=False):
		if not force and not self.is_sync:
			return
		if self.repository_url is None or self.local_path.path is None:
			return
		
		if self.local_path.exists and not self.is_submodule:
			if overwrite:
				self.local_path.remove()
			else:
				# print(f'Path Already Exists : Skipping {self.local_path.path}')
				return
		
		print(f'Syncing {self.name} to {self.local_path.path}')
		self.log_progress.start(f'Syncing {self.name} to {self.local_path.path}')
		
		if self.is_submodule:
			self.ensure_repo_init()
			repo = git.Repo(self.local_path.path)
			repo.git.submodule('update', '--init')
			if self.branch is not None:
				repo.git.checkout(self.branch)
		else:
			kwargs = {'branch': self.branch} if self.branch is not None else {}
			# if self.branch is not None:
			git.Repo.clone_from(self.repository_url, self.local_path.path, **kwargs)
		
		print(f'Syncing Done!')
		self.log_progress.done(f'Syncing Done!')

	def link(self, overwrite=False, force=False):
		if self.local_path.path is None:
			return []
		
		link_commands = []
		for p in self.paths:
			command = p.link(overwrite=overwrite, force=force)
			if command is None:
				continue
			link_commands.append(command)
		
		return link_commands
	
	def enable(self, force=False):
		if not force and not self.is_enable:
			return
		
		if not len(self.paths):
			enable_addon(self.name)
		else:
			for p in self.paths:
				p.enable(force=force)

	def disable(self, force=False):
		if not force and self.is_enable:
			return

		if not len(self.paths):
			disable_addon(self.name)
		else:
			for p in self.paths:
				p.disable(force=force)

	def set_keymaps(self):
		if self.keymaps:
			try:
				km = eval(f'keymaps.TILA_Config_Keymaps_{self.name}')
				keymap_instance = km()
				keymap_instance.set_keymaps()
			except AttributeError as e:
				self.log_progress.warning(f'{self.name} Addon have no keymaps Set')
				print(f'{self.name} Addon have no keymaps Set')
				print(f'{e}')

class AddonManager():
	def __init__(self, json_path):
		self._json_path = json_path
		self.json = Json(json_path)
		self.processing = False
		self.queue_list = []
		self.log_progress = Log(bpy.context.window_manager.tila_config_log_list,
								'tila_config_log_list_idx')

	@property
	def elements(self):
		return {k: ElementAM(v, k) for k,v in self.json.json_data.items() if k[0] != '_'}
	
	def save_json(self, json_dict):
		self.json.save(json_dict)
	
	def queue_clean(self, element_name=None, force=False):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.clean, {'element_name': e.name, 'force':force}])
		elif element_name in self.elements.keys():
			self.queue([self.clean, {'element_name': element_name, 'force': force}])
			
	def clean(self, element_name=None, force=False):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.clean(force=force)
		elif element_name in self.elements.keys():
			self.elements[element_name].clean(force=force)

		self.processing = False
	
	def queue_sync(self, element_name=None, overwrite=False, force=False):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.sync, {'element_name': e.name, 'overwrite': overwrite, 'force': force}])
		elif element_name in self.elements.keys():
			self.queue(
				[self.sync, {'element_name': element_name, 'overwrite': overwrite, 'force': force}])

	def sync(self, element_name=None, overwrite=False, force=False):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.sync(overwrite=overwrite, force=force)
		elif element_name in self.elements.keys():
			self.elements[element_name].sync(overwrite=overwrite, force=force)
		
		self.processing = False

	def queue_link(self, element_name=None, overwrite=False):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.link, {'element_name': e.name, 'overwrite': overwrite}])
		elif element_name in self.elements.keys():
			self.queue([self.link, {'element_name': element_name, 'overwrite': overwrite}])

	def link(self, element_name=None, overwrite=False, force=False):
		self.processing = True

		link_command = []
		if element_name is None:
			for e in self.elements.values():
				command = e.link(overwrite=overwrite, force=force)
				if not len(command):
					continue
				link_command += command
		elif element_name in self.elements.keys():
			command = self.elements[element_name].link(overwrite=overwrite, force=force)
			if not len(command):
				return
			link_command = command

		admin.elevate([create_symbolic_link_file, '--', '--file_to_link', *link_command])

		self.processing = False

	def queue_enable(self, element_name=None, force=False):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.enable, {'element_name': e.name, 'force':force}])
		elif element_name in self.elements.keys():
			self.queue([self.enable, {'element_name': element_name, 'force':force}])

	def enable(self, element_name=None, force=False):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.enable(force=force)
		elif element_name in self.elements.keys():
			self.elements[element_name].enable(force=force)

		self.processing = False
	
	def queue_disable(self, element_name=None, force=False):
		if element_name is None:
			for e in self.elements.values():
				self.queue([self.disable, {'element_name': e.name, 'force': force}])
		elif element_name in self.elements.keys():
			self.queue([self.disable, {'element_name': element_name, 'force': force}])

	def disable(self, element_name=None, force=False):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.disable(force=force)
		elif element_name in self.elements.keys():
			self.elements[element_name].disable(force=force)

		self.processing = False

	def queue_set_keymaps(self, element_name=None):
		if element_name is None:
			for e in self.elements.values():
				if not e.keymaps:
					continue

				self.queue([self.set_keymaps, {'element_name': e.name}])
				
		elif element_name in self.elements.keys():
			if not self.elements[element_name].keymaps:
				return
			
			self.queue([self.set_keymaps, {'element_name': element_name}])

	def set_keymaps(self, element_name=None):
		self.processing = True

		if element_name is None:
			for e in self.elements.values():
				e.set_keymaps()
		elif element_name in self.elements.keys():
			self.elements[element_name].set_keymaps()

		self.processing = False

	def queue(self, action):
		self.queue_list.append(action)

	def flush_queue(self):
		self.queue_list = []

	def next_action(self):
		if len(self.queue_list) == 0:
			print('Queue Done !')
			self.log_progress.done('Queue Done !')
			return
		
		action = self.queue_list.pop(0)

		action[0](**action[1])


	def __str__(self):
		s = ''
		for _,v in self.elements.items():
			s += f'{v}\n'
		
		return s
