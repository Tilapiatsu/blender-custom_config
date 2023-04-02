import bpy
import os
import time
from os import path
from bpy.types import (Operator)
from . keymaps import TILA_Config_Keymaps as KM
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

	force: bpy.props.BoolProperty(name="Force Clean", default=False, description='remove all config for a fresh start')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		self.AM.queue_clean(self.force)

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
	
	_timer = None

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		self.AM.queue_sync()

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

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.wm.tila_setup_blender_progress = "LINK_STARTED"
		self.report({'INFO'}, 'TilaConfig : Start Link')
		
		self.AM.link()
		time.sleep(1)
		
		bpy.ops.preferences.addon_refresh('EXEC_DEFAULT')

		self.wm.tila_setup_blender_progress = "LINK_DONE"
		
		self.report({'INFO'}, 'TilaConfig : Link Done !')

		return {"FINISHED"}


class TILA_Config_EnableAddonList(Operator):
	bl_idname = "tila.config_enable_addon_list"
	bl_label = "Tila Config : Enable Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		self.AM.queue_enable()

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

	force: bpy.props.BoolProperty(
		name="Force Disable", default=False, description='remove all config for a fresh start')

	def execute(self, context):
		self.wm = bpy.context.window_manager
		self.wm.tila_setup_blender_progress = "NONE"
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		self.AM.queue_disable(self.force)

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
					self.report({'INFO'}, 'TilaConfig : Disable Enable')
					self.wm.tila_setup_blender_progress = "DISABLE_STARTED"
				self.AM.next_action()

		return {"PASS_THROUGH"}

class TILA_Config_RegisterKeymaps(Operator):
	bl_idname = "tila.config_register_keymaps"
	bl_label = "Tila Config : Register Keymaps"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.wm = bpy.context.window_manager

		keymap = KM()

		self.wm.tila_setup_blender_progress = "REGISTER_KEYMAP_STARTED"
		self.report({'INFO'}, 'TilaConfig : Start Register Keymaps')
		keymap.set_tila_keymap()
		bpy.context.window_manager.keyconfigs.update()
		bpy.ops.wm.save_userpref()
		self.wm.tila_setup_blender_progress = "REGISTER_KEYMAP_DONE"
		self.report({'INFO'}, 'TilaConfig : Start Register Done')

		return {'FINISHED'}


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
