import bpy
import os
import time
from os import path
from bpy.types import (Operator)
from . settings import TILA_Config_Settings as S
from .AddonManager import AddonManager
from . addon_list import TILA_Config_PathElement


def get_path():
	return os.path.dirname(os.path.realpath(__file__))


AL = path.join(get_path(), 'AddonList.json')

class TILA_Config_SetupBlender(Operator):
	"""One click blender setup. Based on the Json file It will :
    - sync and enable the addons that are are set as enable
    - apply the settings and keymaps
    - save config file"""
	bl_idname = "tila.config_setup_blender"
	bl_label = "Tila Config : Setup Blender"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)

		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"

		self._timer = bpy.context.window_manager.event_timer_add(
			0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		self.report({'INFO'}, 'TilaConfig : Blender Setup Started !')
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			match context.window_manager.tila_setup_blender_progress:
				case 'NONE':
					bpy.ops.tila.config_sync_addon_list('EXEC_DEFAULT')
				case 'SYNC_DONE':
					bpy.ops.tila.config_link_addon_list('EXEC_DEFAULT')
				case 'LINK_DONE':
					bpy.ops.tila.config_enable_addon_list('EXEC_DEFAULT')
				case 'ENABLE_DONE':
					bpy.ops.tila.config_set_settings('EXEC_DEFAULT')
				case 'SET_SETTINGS_DONE':
					bpy.ops.tila.config_register_keymaps('EXEC_DEFAULT')
				case 'REGISTER_KEYMAP_DONE':
					context.window_manager.tila_setup_blender_progress = "NONE"
					self.report({'INFO'}, 'TilaConfig : Blender Setup Done !')
					return {"FINISHED"}

		return {"PASS_THROUGH"}
	
class TILA_Config_UpdateSetupBlender(Operator):
	"""Update Blender setup, to match the changes made in the Json file. It will :
    - disable and unlink the addons that are not enable anymore
    - sync and enable the addons that are are not disabled anymore
    - reapply the settings and keymaps
    - save config file"""
	bl_idname = "tila.config_update_setup_blender"
	bl_label = "Tila Config : Update Setup Blender"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)

		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"

		self._timer = bpy.context.window_manager.event_timer_add(
			0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		self.report({'INFO'}, 'TilaConfig : Update Blender Setup Started !')
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			match context.window_manager.tila_setup_blender_progress:
				case 'NONE':
					bpy.ops.tila.config_disable_addon_list('EXEC_DEFAULT')
				case 'DISABLE_DONE':
					bpy.ops.tila.config_clean_addon_list('EXEC_DEFAULT')
				case 'CLEAN_DONE':
					bpy.ops.tila.config_sync_addon_list('EXEC_DEFAULT')
				case 'SYNC_DONE':
					bpy.ops.tila.config_link_addon_list('EXEC_DEFAULT')
				case 'LINK_DONE':
					bpy.ops.tila.config_enable_addon_list('EXEC_DEFAULT')
				case 'ENABLE_DONE':
					bpy.ops.tila.config_set_settings('EXEC_DEFAULT')
				case 'SET_SETTINGS_DONE':
					bpy.ops.tila.config_register_keymaps('EXEC_DEFAULT')
				case 'REGISTER_KEYMAP_DONE':
					context.window_manager.tila_setup_blender_progress = "NONE"
					self.report({'INFO'}, 'TilaConfig : Update Blender Setup Done !')
					return {"FINISHED"}

		return {"PASS_THROUGH"}

class TILA_Config_PrintAddonList(Operator):
	"""Print all addons list and all its settings and paths"""
	bl_idname = "tila.config_print_addon_list"
	bl_label = "Tila Config : Print Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)
		print(self.AM)
		return {'FINISHED'}


class TILA_Config_RemoveConfig(Operator):
	"""Remove all custom config and revert to default Blender factory settings."""
	bl_idname = "tila.config_remove"
	bl_label = "Tila Config : Remove Config"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)

		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"

		self._timer = bpy.context.window_manager.event_timer_add(
			0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		self.report({'INFO'}, 'TilaConfig : Remove Config Started !')
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			match context.window_manager.tila_setup_blender_progress:
				case 'NONE':
					bpy.ops.tila.config_disable_addon_list('EXEC_DEFAULT', force=True)
				case 'DISABLE_DONE':
					bpy.ops.tila.config_clean_addon_list('EXEC_DEFAULT', force=True)
				case 'CLEAN_DONE':
					context.window_manager.tila_setup_blender_progress = "NONE"
					self.report({'INFO'}, 'TilaConfig : Remove Config Done !')
					return {"FINISHED"}

		return {"PASS_THROUGH"}

class TILA_Config_CleanAddonList(Operator):
	"""Clean Addons that have already been linked and are disabled or not set to linked anymore.
    name : if not set, all addons in the list will be processed. only the named addon will be cleaned
    force : if enabled, all addon in the list will be cleaned"""
	bl_idname = "tila.config_clean_addon_list"
	bl_label = "Tila Config : clean Addon List"
	bl_options = {'REGISTER'}
	
	name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to Clean')
	force: bpy.props.BoolProperty(name="Force Clean", default=False, description='remove all config for a fresh start')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.name == '':
			self.AM.queuqueue_cleane_sync(force=self.force)
		else:
			self.AM.queue_clean(self.name, force=self.force)

		self._timer = bpy.context.window_manager.event_timer_add(
			0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			if len(self.AM.queue_list) == 0:
				self.report({'INFO'}, 'TilaConfig : Clean Done !')
				self.wm.tila_setup_blender_progress = "CLEAN_DONE"
				bpy.context.window_manager.event_timer_remove(self._timer)
				if self.force:
					bpy.ops.wm.read_factory_settings()
					bpy.ops.wm.save_userpref()
				return {"FINISHED"}

			elif not self.AM.processing:
				if self.wm.tila_setup_blender_progress == "NONE":
					self.report({'INFO'}, 'TilaConfig : Start Clean')
					self.wm.tila_setup_blender_progress = "CLEAN_STARTED"
				self.AM.next_action()

		return {"PASS_THROUGH"}


class TILA_Config_SyncAddonList(Operator):
	"""Sync Addons that are set as sync.
    name : if not set, all addons in the list will be processed. only the named addon will be Synced"""
	bl_idname = "tila.config_sync_addon_list"
	bl_label = "Tila Config : Sync Addon List"
	bl_options = {'REGISTER'}

	name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to Sync')
	
	_timer = None

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.name == '':
			self.AM.queue_sync()
		else:
			self.AM.queue_sync(self.name)


		self._timer = bpy.context.window_manager.event_timer_add(0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}
	
	def modal(self, context, event):
		if event.type == 'TIMER':
			if len(self.AM.queue_list) == 0:
				self.report({'INFO'}, 'TilaConfig : Sync Done !')
				self.wm.tila_setup_blender_progress = "SYNC_DONE"
				bpy.context.window_manager.event_timer_remove(self._timer)
				return {"FINISHED"}
		
			elif not self.AM.processing:
				if self.wm.tila_setup_blender_progress == "NONE":
					self.report({'INFO'}, 'TilaConfig : Start Sync')
					self.wm.tila_setup_blender_progress = "SYNC_STARTED"
				self.AM.next_action()

		return {"PASS_THROUGH"}


class TILA_Config_LinkAddonList(Operator):
	"""Link Addons that are set as link.
    name : if not set, all addons in the list will be processed. only the named addon will be linked"""
	bl_idname = "tila.config_link_addon_list"
	bl_label = "Tila Config : Link Addon List"
	bl_options = {'REGISTER'}

	name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to Sync')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.wm.tila_setup_blender_progress = "LINK_STARTED"
		self.report({'INFO'}, 'TilaConfig : Start Link')

		if self.name == '':
			self.AM.link()
		else:
			self.AM.link(self.name)

		time.sleep(1)
		
		bpy.ops.preferences.addon_refresh('EXEC_DEFAULT')

		self.wm.tila_setup_blender_progress = "LINK_DONE"
		
		self.report({'INFO'}, 'TilaConfig : Link Done !')

		return {"FINISHED"}


class TILA_Config_EnableAddonList(Operator):
	"""Enable Addons that are set as enable.
    name : if not set, all addons in the list will be processed. only the named addon will be Enable
    force : if enabled, all addon in the list will be enabled"""
	bl_idname = "tila.config_enable_addon_list"
	bl_label = "Tila Config : Enable Addon List"
	bl_options = {'REGISTER'}

	name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to enable')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.name == '':
			self.AM.queue_enable()
		else:
			self.AM.queue_enable(self.name)

		self._timer = bpy.context.window_manager.event_timer_add(0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			if len(self.AM.queue_list) == 0:
				self.report({'INFO'}, 'TilaConfig : Enable Done !')
				self.wm.tila_setup_blender_progress = "ENABLE_DONE"
				bpy.context.window_manager.event_timer_remove(self._timer)
				return {"FINISHED"}

			elif not self.AM.processing:
				if self.wm.tila_setup_blender_progress == "NONE":
					self.report({'INFO'}, 'TilaConfig : Start Enable')
					self.wm.tila_setup_blender_progress = "ENABLE_STARTED"
				self.AM.next_action()

		return {"PASS_THROUGH"}
	

class TILA_Config_DisableAddonList(Operator):
	"""Disable Addons that are not set as enable.
    name : if not set, all addons in the list will be processed. only the named addon will be disable
    force : if enabled,  all addon in the list will be disabled"""
	bl_idname = "tila.config_disable_addon_list"
	bl_label = "Tila Config : Disable Addon List"
	bl_options = {'REGISTER'}
	
	name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to enable')
	force: bpy.props.BoolProperty(
		name="Force Disable", default=False, description='Disable all addons listed in the list regardless if it is set as enable or not')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.name == '':
			self.AM.queue_disable(force=self.force)
		else:
			self.AM.queue_disable(self.name, force=self.force)

		self._timer = bpy.context.window_manager.event_timer_add(
			0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			if len(self.AM.queue_list) == 0:
				self.report({'INFO'}, 'TilaConfig : Disable Done !')
				self.wm.tila_setup_blender_progress = "DISABLE_DONE"
				bpy.context.window_manager.event_timer_remove(self._timer)
				return {"FINISHED"}

			elif not self.AM.processing:
				if self.wm.tila_setup_blender_progress == "NONE":
					self.report({'INFO'}, 'TilaConfig : Start Disable')
					self.wm.tila_setup_blender_progress = "DISABLE_STARTED"
				self.AM.next_action()

		return {"PASS_THROUGH"}

class TILA_Config_RegisterKeymaps(Operator):
	"""Register keymaps to Blender
    name : register only the named Addon"""
	bl_idname = "tila.config_register_keymaps"
	bl_label = "Tila Config : Register Keymaps"
	bl_options = {'REGISTER'}

	name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to register Keymaps for')
	
	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.name == '':
			self.AM.queue_set_keymaps()
		else:
			self.AM.queue_set_keymaps(self.name)

		self._timer = bpy.context.window_manager.event_timer_add(
			0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			if len(self.AM.queue_list) == 0:
				self.report({'INFO'}, 'TilaConfig : Register Keymaps Done !')
				self.wm.tila_setup_blender_progress = "REGISTER_KEYMAP_DONE"
				bpy.context.window_manager.keyconfigs.update()
				bpy.ops.wm.save_userpref()
				bpy.context.window_manager.event_timer_remove(self._timer)
				return {"FINISHED"}

			elif not self.AM.processing:
				if self.wm.tila_setup_blender_progress == "NONE":
					self.report({'INFO'}, 'TilaConfig : Start Register Keymaps')
					self.wm.tila_setup_blender_progress = "REGISTER_KEYMAP_STARTED"
				self.AM.next_action()

		return {"PASS_THROUGH"}


class TILA_Config_UnregisterKeymaps(Operator):
	bl_idname = "tila.config_unregister_keymaps"
	bl_label = "Tila Config : Unregister Keymaps"
	bl_options = {'REGISTER'}

	def execute(self, context):
		# keymaps.unregister()
		return {'FINISHED'}
	
class TILA_Config_SetSettings(Operator):
	"""Apply Custom Settings to blender"""
	bl_idname = "tila.config_set_settings"
	bl_label = "Tila Config : Set Settings"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.wm = bpy.context.window_manager

		settings = S()

		self.wm.tila_setup_blender_progress = "SET_SETTINGS_STARTED"
		self.report({'INFO'}, 'TilaConfig : Start Set Setting')
		settings.set_settings()
		self.wm.tila_setup_blender_progress = "SET_SETTINGS_DONE"
		self.report({'INFO'}, 'TilaConfig : Start Set Done')
		return {"FINISHED"}

def import_addon_element(source_element, target_element):
	def get_valid_url(path, fallback):
		return fallback if path is None else path
	
	target_element.name = source_element.name
	target_element.is_enable = source_element.is_enable
	target_element.is_repository = source_element.is_repository
	target_element.is_sync = source_element.is_sync
	target_element.online_url = get_valid_url(source_element.online_url, '')
	target_element.repository_url = get_valid_url(source_element.repository_url, '')
	target_element.branch = get_valid_url(source_element.branch, '')
	target_element.is_submodule = source_element.is_submodule
	target_element.local_path = get_valid_url(str(source_element.local_path), '')
	target_element.keymaps = source_element.keymaps
	target_element.paths.clear()
	for p in source_element.paths:
		path = target_element.paths.add()
		path.is_enable = p.is_enable
		path.local_subpath = get_valid_url(str(p.local_subpath), '')
		path.destination_path = get_valid_url(str(p.destination_path), '')


def get_addon_element_dict(element, path_fallback):
	def get_valid_url(path, fallback):
		return fallback if path == '' else path
		
	addon_element_dict = {}

	addon_element_dict['is_enable'] = element.is_enable
	addon_element_dict['is_sync'] = element.is_sync
	addon_element_dict['online_url'] = get_valid_url(element.online_url, path_fallback)
	addon_element_dict['repository_url'] = get_valid_url(element.repository_url, path_fallback)
	addon_element_dict['branch'] = get_valid_url(element.branch, path_fallback)
	addon_element_dict['is_submodule'] = element.is_submodule
	addon_element_dict['local_path'] = get_valid_url(element.local_path, path_fallback)
	addon_element_dict['keymaps'] = element.keymaps

	if not len(element.paths):
		addon_element_dict['paths'] = None
	else:
		addon_element_dict['paths'] = []
		for p in element.paths:
			path = {}
			path['is_enable'] = p.is_enable
			path['local_subpath'] = get_valid_url(p.local_subpath, path_fallback)
			path['destination_path'] = get_valid_url(p.destination_path, path_fallback)
			addon_element_dict['paths'].append(path)

	return addon_element_dict

class TILA_Config_ImportAddonList(Operator):
	"""Import Addon List from Json file. It will revert any changes that Havent been saved yet"""
	bl_idname = "tila.config_import_addon_list"
	bl_label = "Tila Config : Import Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		wm = context.window_manager

		AM = AddonManager.AddonManager(AL)

		wm.tila_config_addon_list.clear()
		for e in AM.elements.values():
			if e.name not in wm.tila_config_addon_list:
				addon_element = wm.tila_config_addon_list.add()
			else:
				addon_element = wm.tila_config_addon_list[e.name]

			import_addon_element(e, addon_element)

		self.report({'INFO'}, 'TilaConfig : Addon List Imported')
		return {"FINISHED"}


class TILA_Config_SaveAddonList(Operator):
	"""Save entire addon list to Json"""
	bl_idname = "tila.config_save_addon_list"
	bl_label = "Tila Config : Save Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		wm = context.window_manager

		AM = AddonManager.AddonManager(AL)

		# wm.tila_config_addon_list.clear()
		json_dict = {}
		for e in wm.tila_config_addon_list:
			json_dict[e.name] = get_addon_element_dict(e, None)

		AM.save_json(json_dict=json_dict)
		self.report({'INFO'}, 'TilaConfig : Addon List Saved')
		return {"FINISHED"}

def update_path_count(self, context):
	if  self.path_count > context.window_manager.tila_path_count :
		self.paths.add()
		context.window_manager.tila_path_count = len(self.paths)
	elif self.path_count < context.window_manager.tila_path_count :
		self.paths.remove(len(self.paths) - 1)
		context.window_manager.tila_path_count = len(self.paths)

class TILA_Config_AddAddon(bpy.types.Operator):
	"""Add addon to addon list. Changes will be added to Json"""
	bl_idname = "tila.config_add_addon"
	bl_label = "Tila Config : Add Addon"
	bl_options = {'REGISTER'}

	name: bpy.props.StringProperty(name="Addon Name", default="", description='name of the addon')
	is_sync: bpy.props.BoolProperty(default=False)
	is_enable: bpy.props.BoolProperty(default=False)
	online_url: bpy.props.StringProperty(
		name="Online URL", default="", description='Path to the website to download the addon')
	repository_url: bpy.props.StringProperty(
		name="Repository URL", default="", description='Path to the git repository of the addon')
	branch: bpy.props.StringProperty(
			name="Branch", default="", description='Name of the branch to sync')
	is_submodule: bpy.props.BoolProperty(default=False)
	local_path: bpy.props.StringProperty(
			name="Local Path", default="", description='Path to the addon on the Addon. The blender Preference setting can be noted as # for relative path')
	keymaps: bpy.props.BoolProperty(default=False)
	path_count: bpy.props.IntProperty(default=1, update=update_path_count)
	paths: bpy.props.CollectionProperty(type=TILA_Config_PathElement)
	
	def invoke(self, context, event):
		for p in range(self.path_count):
			self.paths.add()

		wm = context.window_manager
		wm.tila_path_count = self.path_count

		return wm.invoke_props_dialog(self, width=800)

	def execute(self, context):
		wm = context.window_manager
		json_dict = {}
		
		for e in wm.tila_config_addon_list:
			json_dict[e.name] = get_addon_element_dict(wm.tila_config_addon_list[e.name], None)

		json_dict[self.name] = get_addon_element_dict(self, None)

		AM = AddonManager.AddonManager(AL)

		AM.save_json(json_dict=json_dict)

		if self.name not in wm.tila_config_addon_list:
			addon_element = wm.tila_config_addon_list.add()
		else:
			addon_element = wm.tila_config_addon_list[self.name]
		
		import_addon_element(AM.elements[self.name], addon_element)

		self.report({'INFO'}, f'TilaConfig : {self.name} addon added')
		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.label(text='New Addon')
		col.separator()
		
		col.prop(self, 'name', text='Addon Name')
		col.prop(self, 'is_sync', text=f'sync')
		col.prop(self, 'is_enable', text=f'enable')
		col.prop(self, 'online_url', text=f'online url')
		col.prop(self, 'repository_url', text=f'repository url')
		col.prop(self, 'branch', text=f'branch')
		col.prop(self, 'is_submodule', text=f'submodule')
		col.prop(self, 'local_path', text=f'local path')
		col.prop(self, 'keymaps', text=f'keymaps')
		col.separator()

		col.label(text='Paths:')
		col.prop(self, 'path_count', text=f'Path Count')
		for p in range(self.path_count):
			col.label(text=f'Path {p+1}')
			self.draw_path(col, self.paths[p])


	def draw_path(self, col,  path):
		col.prop(path, 'is_enable', text=f'ienable')
		col.prop(path, 'local_subpath', text=f'local subpath')
		col.prop(path, 'destination_path', text=f'destination path')


class TILA_Config_EditAddon(bpy.types.Operator):
	"""Edit addon from addon list. Changes will be added to Json"""
	bl_idname = "tila.config_edit_addon"
	bl_label = "Tila Config : Edit Addon"
	bl_options = {'REGISTER'}

	name: bpy.props.StringProperty(name="Addon Name", default="", description='name of the addon')
	is_sync: bpy.props.BoolProperty(default=False)
	is_enable: bpy.props.BoolProperty(default=False)
	online_url: bpy.props.StringProperty(
		name="Online URL", default="", description='Path to the website to download the addon')
	repository_url: bpy.props.StringProperty(
		name="Repository URL", default="", description='Path to the git repository of the addon')
	branch: bpy.props.StringProperty(
            name="Branch", default="", description='Name of the branch to sync')
	is_submodule: bpy.props.BoolProperty(default=False)
	local_path: bpy.props.StringProperty(
            name="Local Path", default="", description='Path to the addon on the Addon. The blender Preference setting can be noted as # for relative path')
	keymaps: bpy.props.BoolProperty(default=False)
	path_count: bpy.props.IntProperty(default=1, update=update_path_count)
	paths: bpy.props.CollectionProperty(type=TILA_Config_PathElement)

	def invoke(self, context, event):
		wm = context.window_manager
		if self.name not in wm.tila_config_addon_list:
			self.report({'CANCELLED'}, f'TilaConfig : {self.name} not in the list')
		
		self.previous_name = self.name
		self.element = wm.tila_config_addon_list[self.name]
		self.path_count = len(self.element.paths)

		wm.tila_path_count = self.path_count

		import_addon_element(self.element, self)

		return wm.invoke_props_dialog(self, width=800)

	def execute(self, context):
		wm = context.window_manager
		json_dict = {}

		for e in wm.tila_config_addon_list:
			if e.name == self.previous_name:
				continue
			json_dict[e.name] = get_addon_element_dict(wm.tila_config_addon_list[e.name], None)

		json_dict[self.name] = get_addon_element_dict(self, None)

		AM = AddonManager.AddonManager(AL)

		AM.save_json(json_dict=json_dict)

		import_addon_element(AM.elements[self.name], wm.tila_config_addon_list[self.previous_name])

		self.report({'INFO'}, f'TilaConfig : {self.name} addon edited')
		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.label(text='New Addon')
		col.separator()

		col.prop(self, 'name', text='Addon Name')
		col.prop(self, 'is_sync', text=f'sync')
		col.prop(self, 'is_enable', text=f'enable')
		col.prop(self, 'online_url', text=f'online url')
		col.prop(self, 'repository_url', text=f'repository url')
		col.prop(self, 'branch', text=f'branch')
		col.prop(self, 'is_submodule', text=f'submodule')
		col.prop(self, 'local_path', text=f'local path')
		col.prop(self, 'keymaps', text=f'keymaps')
		col.separator()

		col.label(text='Paths:')
		col.prop(self, 'path_count', text=f'Path Count')
		for p in range(self.path_count):
			col.label(text=f'Path {p+1}')
			self.draw_path(col, self.paths[p])

	def draw_path(self, col,  path):
		col.prop(path, 'is_enable', text=f'enable')
		col.prop(path, 'local_subpath', text=f'local subpath')
		col.prop(path, 'destination_path', text=f'destination path')


class TILA_Config_RemoveAddon(bpy.types.Operator):
	"""Remove addon from addon list. Addon will be removed from Json too"""
	bl_idname = "tila.config_remove_addon"
	bl_label = "Remove Addon ?"
	bl_options = {'REGISTER'}

	name: bpy.props.StringProperty(name="Addon Name", default="", description='name of the addon')

	def invoke(self, context, event):
		wm = context.window_manager
		if self.name not in wm.tila_config_addon_list:
			self.report({'CANCELLED'}, f'TilaConfig : {self.name} not in the list')
		return wm.invoke_confirm(self, event)

	def execute(self, context):
		wm = context.window_manager
		json_dict = {}
		index = None
		for i in range(len(wm.tila_config_addon_list)):
			e = wm.tila_config_addon_list[i]
			if e.name == self.name:
				index = i
				continue
			json_dict[e.name] = get_addon_element_dict(wm.tila_config_addon_list[e.name], None)

		AM = AddonManager.AddonManager(AL)
		AM.save_json(json_dict=json_dict)

		wm.tila_config_addon_list.remove(index)

		self.report({'INFO'}, f'TilaConfig : {self.name} addon removed')

		return {'FINISHED'}