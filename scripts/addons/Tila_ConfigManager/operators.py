import bpy
import os
import time
from os import path
from bpy.types import (Operator)
from .AddonManager.keymaps import TILA_Config_Keymaps_Global as KM
from . settings import TILA_Config_Settings as S
from .AddonManager import AddonManager


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


class TILA_Config_UpdateAddonList(Operator):
	bl_idname = "tila.config_update_addon_list"
	bl_label = "Tila Config : Update Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		wm = bpy.context.window_manager

		AM = AddonManager.AddonManager(AL)

		wm.tila_config_addon_list.clear()
		for e in AM.elements.values():
			self.update_element(e, wm)

		self.report({'INFO'}, 'TilaConfig : Addon List Updated')
		return {"FINISHED"}
	
	def update_element(self, element, window_manager):
		if element.name in ['Global']:
			return
		
		if element.name not in window_manager.tila_config_addon_list:
			addon_element = window_manager.tila_config_addon_list.add()
		else:
			addon_element = window_manager.tila_config_addon_list[element.name]
		addon_element.name = element.name
		addon_element.enable = element.is_enable
		addon_element.sync = element.is_sync
		addon_element.online_url = '' if element.online_url is None else element.online_url
		addon_element.branch = '' if element.branch is None else element.branch
		addon_element.submodule = element.submodule
		addon_element.local_path = '' if element.local_path.path is None else element.local_path.path
		addon_element.keymaps = element.keymaps
		addon_element.paths.clear()
		for p in element.paths:
			path = addon_element.paths.add()
			path.enable = p.is_enable
			path.local_subpath = '' if p.local_subpath.path is None else p.local_subpath.path
			path.destination_path = '' if p.destination_path.path is None else p.destination_path.path