import bpy
import os
import time
from os import path
from bpy.types import (Operator)
from .AddonManager.keymaps import TILA_Config_Keymaps_Global as KM
from . settings import TILA_Config_Settings as S
from .AddonManager import AddonManager
from . addon_list import TILA_Config_PathElement


def get_path():
	return os.path.dirname(os.path.realpath(__file__))


AL = path.join(get_path(), 'AddonList.json')

class TILA_Config_SetupBlender(Operator):
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
	bl_idname = "tila.config_print_addon_list"
	bl_label = "Tila Config : Print Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)
		print(self.AM)
		return {'FINISHED'}


class TILA_Config_RemoveConfig(Operator):
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
	bl_idname = "tila.config_clean_addon_list"
	bl_label = "Tila Config : clean Addon List"
	bl_options = {'REGISTER'}
	
	addon_name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to Clean')
	force: bpy.props.BoolProperty(name="Force Clean", default=False, description='remove all config for a fresh start')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.addon_name == '':
			self.AM.queuqueue_cleane_sync(force=self.force)
		else:
			self.AM.queue_clean(self.addon_name, force=self.force)

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
	bl_idname = "tila.config_sync_addon_list"
	bl_label = "Tila Config : Sync Addon List"
	bl_options = {'REGISTER'}

	addon_name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to Sync')
	
	_timer = None

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.addon_name == '':
			self.AM.queue_sync()
		else:
			self.AM.queue_sync(self.addon_name)


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
	bl_idname = "tila.config_link_addon_list"
	bl_label = "Tila Config : Link Addon List"
	bl_options = {'REGISTER'}

	addon_name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to Sync')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.wm.tila_setup_blender_progress = "LINK_STARTED"
		self.report({'INFO'}, 'TilaConfig : Start Link')

		if self.addon_name == '':
			self.AM.link()
		else:
			self.AM.link(self.addon_name)

		time.sleep(1)
		
		bpy.ops.preferences.addon_refresh('EXEC_DEFAULT')

		self.wm.tila_setup_blender_progress = "LINK_DONE"
		
		self.report({'INFO'}, 'TilaConfig : Link Done !')

		return {"FINISHED"}


class TILA_Config_EnableAddonList(Operator):
	bl_idname = "tila.config_enable_addon_list"
	bl_label = "Tila Config : Enable Addon List"
	bl_options = {'REGISTER'}

	addon_name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to enable')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.addon_name == '':
			self.AM.queue_enable()
		else:
			self.AM.queue_enable(self.addon_name)

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
	bl_idname = "tila.config_disable_addon_list"
	bl_label = "Tila Config : Disable Addon List"
	bl_options = {'REGISTER'}
	
	addon_name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to enable')
	force: bpy.props.BoolProperty(
		name="Force Disable", default=False, description='Disable all addons listed in the list regardless if it is set as enable or not')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.addon_name == '':
			self.AM.queue_disable(force=self.force)
		else:
			self.AM.queue_disable(self.addon_name, force=self.force)

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
	bl_idname = "tila.config_register_keymaps"
	bl_label = "Tila Config : Register Keymaps"
	bl_options = {'REGISTER'}

	addon_name : bpy.props.StringProperty(name="Addon Name", default="", description='Name of the addon to register Keymaps for')
	
	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		if self.addon_name == '':
			self.AM.queue_set_keymaps()
		else:
			self.AM.queue_set_keymaps(self.addon_name)

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


class TILA_Config_ImportAddonList(Operator):
	bl_idname = "tila.config_import_addon_list"
	bl_label = "Tila Config : Import Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		wm = bpy.context.window_manager

		AM = AddonManager.AddonManager(AL)

		wm.tila_config_addon_list.clear()
		for e in AM.elements.values():
			self.update_element(e, wm)

		self.report({'INFO'}, 'TilaConfig : Addon List Imported')
		return {"FINISHED"}
	
	def update_element(self, element, window_manager):		
		if element.name not in window_manager.tila_config_addon_list:
			addon_element = window_manager.tila_config_addon_list.add()
		else:
			addon_element = window_manager.tila_config_addon_list[element.name]
		addon_element.name = element.name
		addon_element.enable = element.is_enable
		addon_element.is_repository = element.is_repository
		addon_element.sync = element.is_sync
		addon_element.online_url = '' if element.online_url is None else element.online_url
		addon_element.repository_url = '' if element.repository_url is None else element.repository_url
		addon_element.branch = '' if element.branch is None else element.branch
		addon_element.submodule = element.submodule
		addon_element.local_path = '' if element.local_path.path is None else element.local_path._path
		addon_element.keymaps = element.keymaps
		addon_element.paths.clear()
		for p in element.paths:
			path = addon_element.paths.add()
			path.enable = p.is_enable
			path.local_subpath = '' if p.local_subpath.path is None else p.local_subpath._path
			path.destination_path = '' if p.destination_path.path is None else p.destination_path._path


class TILA_Config_SaveAddonList(Operator):
	bl_idname = "tila.config_save_addon_list"
	bl_label = "Tila Config : Save Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		wm = context.window_manager

		AM = AddonManager.AddonManager(AL)

		# wm.tila_config_addon_list.clear()
		json_dict = {}
		for e in AM.elements.values():
			json_dict[e.name] = self.update_element(e, wm)

		AM.save_json(json_dict=json_dict)
		self.report({'INFO'}, 'TilaConfig : Addon List Saved')
		return {"FINISHED"}
	
	def update_element(self, element, window_manager):
		if element.name not in window_manager.tila_config_addon_list:
			return element.element_dict

		new_element = window_manager.tila_config_addon_list[element.name]

		addon_element = {}

		addon_element['name'] = new_element.name
		addon_element['enable'] = new_element.enable
		addon_element['sync'] = new_element.sync
		addon_element['online_url'] = None if new_element.online_url == '' else new_element.online_url
		addon_element['repository_url'] = None if new_element.repository_url == '' else new_element.repository_url
		addon_element['branch'] = None if new_element.branch == '' else new_element.branch
		addon_element['submodule'] = new_element.submodule
		addon_element['local_path'] = None if new_element.local_path == '' else new_element.local_path
		addon_element['keymaps'] = new_element.keymaps
		if not len(new_element.paths):
			addon_element['paths'] = None
		else:
			addon_element['paths'] = []
			for p in new_element.paths:
				path = {}
				path['enable'] = p.enable
				path['local_subpath'] = None if p.local_subpath == '' else p.local_subpath
				path['destination_path'] = None if p.destination_path == '' else p.destination_path
				addon_element['paths'].append(path)

		return addon_element


def update_path_count(self, context):
	print(self.path_count)
	if  self.path_count > context.window_manager.tila_path_count :
		self.paths.add()
		context.window_manager.tila_path_count = len(self.path)
	elif self.path_count < context.window_manager.tila_path_count :
		self.paths.remove(len(self.path) - 1)
		context.window_manager.tila_path_count = len(self.path)

class TILA_Config_AddAddon(bpy.types.Operator):
	bl_idname = "tila.config_add_addon"
	bl_label = "Tila Config : Add Addon"
	bl_options = {'REGISTER'}

	addon_name: bpy.props.StringProperty(name="Addon Name", default="", description='name of the addon')
	sync: bpy.props.BoolProperty(default=False)
	enable: bpy.props.BoolProperty(default=False)
	online_url: bpy.props.StringProperty(
		name="Online URL", default="", description='Path to the website to download the addon')
	repository_url: bpy.props.StringProperty(
		name="Repository URL", default="", description='Path to the git repository of the addon')
	branch: bpy.props.StringProperty(
            name="Branch", default="", description='Name of the branch to sync')
	submodule: bpy.props.BoolProperty(default=False)
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
		
		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.label(text='New Addon')
		col.separator()
		
		col.prop(self, 'addon_name', text='Addon Name')
		col.prop(self, 'sync', text=f'sync')
		col.prop(self, 'enable', text=f'enable')
		col.prop(self, 'online_url', text=f'online url')
		col.prop(self, 'repository_url', text=f'repository url')
		col.prop(self, 'branch', text=f'branch')
		col.prop(self, 'submodule', text=f'submodule')
		col.prop(self, 'local_path', text=f'local path')
		col.prop(self, 'keymaps', text=f'keymaps')
		col.separator()

		col.label(text='Paths:')
		col.prop(self, 'path_count', text=f'Path Count')
		for p in range(self.path_count):
			col.label(text=f'Path {p+1}')
			self.draw_path(col, self.paths[p])


	def draw_path(self, col,  path):
		col.prop(path, 'enable', text=f'enable')
		col.prop(path, 'local_subpath', text=f'local subpath')
		col.prop(path, 'destination_path', text=f'destination path')

