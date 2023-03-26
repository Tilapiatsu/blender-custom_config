import bpy
import os
from os import path
from bpy.types import (Operator)
from . keymaps import TILA_Config_Keymaps as KM
from .AddonManager import AddonManager


def get_path():
	return os.path.dirname(os.path.realpath(__file__))


AL = path.join(get_path(), 'AddonList.json')

class TILA_Config_RegisterKeymaps(Operator):
	bl_idname = "tila.config_register_keymaps"
	bl_label = "Tila Config : Register Keymaps"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.ops.script.reload()
		KM.set_tila_keymap()
		return {'FINISHED'}


class TILA_Config_UnregisterKeymaps(Operator):
	bl_idname = "tila.config_unregister_keymaps"
	bl_label = "TilaConfig : Unregister Keymaps"
	bl_options = {'REGISTER'}

	def execute(self, context):
		# keymaps.unregister()
		return {'FINISHED'}


class TILA_Config_PrintAddonList(Operator):
	bl_idname = "tila.config_print_addon_list"
	bl_label = "TilaConfig : Print Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)
		print(self.AM)
		return {'FINISHED'}


class TILA_Config_CleanAddonList(Operator):
	bl_idname = "tila.config_clean_addon_list"
	bl_label = "TilaConfig : clean Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		self.AM.queue_clean()

		self._timer = bpy.context.window_manager.event_timer_add(
			0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			if len(self.AM.queue_list) == 0:
				self.report({'INFO'}, 'TilaConfig : Clean Done !')
				bpy.context.window_manager.event_timer_remove(self._timer)
				return {"FINISHED"}

			elif not self.AM.processing:
				self.AM.next_action()

		return {"PASS_THROUGH"}


class TILA_Config_SyncAddonList(Operator):
	bl_idname = "tila.config_sync_addon_list"
	bl_label = "TilaConfig : Sync Addon List"
	bl_options = {'REGISTER'}
	
	_timer = None

	def execute(self, context):
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
				bpy.context.window_manager.event_timer_remove(self._timer)
				return {"FINISHED"}
		
			elif not self.AM.processing:
				self.AM.next_action()

		return {"PASS_THROUGH"}


class TILA_Config_LinkAddonList(Operator):
	bl_idname = "tila.config_link_addon_list"
	bl_label = "TilaConfig : Link Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)

		self.AM.link()
		
		bpy.ops.preferences.addon_refresh()

		return {"FINISHED"}


class TILA_Config_EnableAddonList(Operator):
	bl_idname = "tila.config_enable_addon_list"
	bl_label = "TilaConfig : Enable Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.AM = AddonManager.AddonManager(AL)

		self.AM.flush_queue()
		self.AM.queue_enable()

		self._timer = bpy.context.window_manager.event_timer_add(
			0.1, window=context.window)
		bpy.context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			if len(self.AM.queue_list) == 0:
				self.report({'INFO'}, 'TilaConfig : Enable Done !')
				bpy.context.window_manager.event_timer_remove(self._timer)
				return {"FINISHED"}

			elif not self.AM.processing:
				self.AM.next_action()

		return {"PASS_THROUGH"}
