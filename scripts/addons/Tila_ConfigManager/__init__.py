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
from . operators import (	TILA_Config_RegisterKeymaps,
							TILA_Config_UnregisterKeymaps,
						 	TILA_Config_PrintAddonList,
							TILA_Config_CleanAddonList,
						  	TILA_Config_SyncAddonList,
							TILA_Config_LinkAddonList,
							TILA_Config_EnableAddonList, 
							TILA_Config_SetSettings,
							TILA_Config_SetupBlender)


bl_info = {
	"name" : "Tila Config Manager",
	"author" : "Tilapiatsu",
	"description" : "",
	"blender" : (2, 80, 0),
	"location" : "",
	"warning" : "",
	"category" : "Preferences"
}
		
classes = (	TILA_Config_PrintAddonList,
			TILA_Config_CleanAddonList,
			TILA_Config_SyncAddonList,
			TILA_Config_LinkAddonList,
			TILA_Config_EnableAddonList,
	   		TILA_Config_RegisterKeymaps,
		   	TILA_Config_UnregisterKeymaps,
		   	TILA_Config_Preferences,
			TILA_Config_SetSettings,
			TILA_Config_SetupBlender)

def register():
	bpy.types.WindowManager.tila_setup_blender_progress = bpy.props.EnumProperty(default="NONE", items=setup_blender_progress)
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	
	del bpy.types.WindowManager.tila_setup_blender_progress
	
if __name__ == "__main__":
	register()