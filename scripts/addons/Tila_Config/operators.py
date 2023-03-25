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
		AM = AddonManager.AddonManager(AL)
		print(AM)
		return {'FINISHED'}


class TILA_Config_SyncAddonList(Operator):
	bl_idname = "tila.config_sync_addon_list"
	bl_label = "TilaConfig : Sync Addon List"
	bl_options = {'REGISTER'}

	def execute(self, context):
		AM = AddonManager.AddonManager(AL)
		AM.sync()
		return {'FINISHED'}
