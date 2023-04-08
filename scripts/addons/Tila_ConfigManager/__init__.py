# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from . preferences import TILA_Config_Preferences
from . items import setup_blender_progress
from .AddonManager.log_list import (TILA_Config_LogElement,
                        			TILA_Config_LogList,
									TILA_Config_SatusList)

from . operators import (	TILA_Config_RegisterKeymaps,
							TILA_Config_UpdateSetupBlender,
							TILA_Config_UnregisterKeymaps,
						 	TILA_Config_PrintAddonList,
							TILA_Config_RemoveConfig,
							TILA_Config_CleanAddonList,
						  	TILA_Config_SyncAddonList,
							TILA_Config_LinkAddonList,
							TILA_Config_EnableAddonList,
							TILA_Config_DisableAddonList, 
							TILA_Config_SetSettings,
							TILA_Config_SetupBlender,
							TILA_Config_ImportAddonList,
							TILA_Config_SaveAddonList,
							TILA_Config_RemoveAddon,
							TILA_Config_AddAddon,
							TILA_Config_EditAddon,
                          	TILA_Config_ClearStatusList,
                         	TILA_Config_ClearLogList)

from . addon_list import ( 	TILA_Config_PathElement,
			  				TILA_Config_AddonElement,
							TILA_Config_AddonList)


bl_info = {
	"name" : "Tila Config Manager",
	"author" : "Tilapiatsu",
	"description" : "",
	"blender" : (2, 80, 0),
	"location" : "",
	"warning" : "",
	"category" : "Preferences"
}
		
classes = (	
			TILA_Config_LogElement,
            TILA_Config_LogList,
	    	TILA_Config_SatusList,
            TILA_Config_PathElement,
	   		TILA_Config_AddonElement,
			TILA_Config_AddonList,
            TILA_Config_ClearStatusList,
            TILA_Config_ClearLogList,
			TILA_Config_PrintAddonList,
			TILA_Config_CleanAddonList,
			TILA_Config_RemoveConfig,
			TILA_Config_SyncAddonList,
			TILA_Config_LinkAddonList,
			TILA_Config_EnableAddonList,
			TILA_Config_DisableAddonList,
	   		TILA_Config_RegisterKeymaps,
		   	TILA_Config_UnregisterKeymaps,
			TILA_Config_ImportAddonList,
			TILA_Config_SaveAddonList,
			TILA_Config_RemoveAddon,
			TILA_Config_AddAddon,
			TILA_Config_EditAddon,
		   	TILA_Config_Preferences,
			TILA_Config_SetSettings,
			TILA_Config_SetupBlender,
			TILA_Config_UpdateSetupBlender)

def register():
	bpy.types.WindowManager.tila_setup_blender_progress = bpy.props.EnumProperty(default="NONE", items=setup_blender_progress)
	bpy.types.WindowManager.tila_path_count = bpy.props.IntProperty(default=1)
	
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.WindowManager.tila_config_addon_list_idx = bpy.props.IntProperty()
	bpy.types.WindowManager.tila_config_addon_list = bpy.props.CollectionProperty(type=TILA_Config_AddonElement)
	bpy.types.WindowManager.tila_config_log_list_idx = bpy.props.IntProperty()
	bpy.types.WindowManager.tila_config_log_list = bpy.props.CollectionProperty(type=TILA_Config_LogElement)
	bpy.types.WindowManager.tila_config_status_list_idx = bpy.props.IntProperty()
	bpy.types.WindowManager.tila_config_status_list = bpy.props.CollectionProperty(type=TILA_Config_LogElement)

def unregister():
	del bpy.types.WindowManager.tila_setup_blender_progress
	del bpy.types.WindowManager.tila_config_log_list
	del bpy.types.WindowManager.tila_config_log_list_idx
	del bpy.types.WindowManager.tila_config_status_list
	del bpy.types.WindowManager.tila_config_status_list_idx

	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	
	del bpy.types.WindowManager.tila_path_count
	del bpy.types.WindowManager.tila_config_addon_list
	del bpy.types.WindowManager.tila_config_addon_list_idx
	
if __name__ == "__main__":
	register()