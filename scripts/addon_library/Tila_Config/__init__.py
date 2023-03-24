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

bl_info = {
	"name" : "Tila_Config",
	"author" : "Tilapiatsu",
	"description" : "",
	"blender" : (2, 80, 0),
	"location" : "",
	"warning" : "",
	"category" : "Preferences"
}
import bpy
from . import tila_keymaps

class TILA_OP_RegisterKeymaps(bpy.types.Operator):
	bl_idname = "wm.tila_register_keymaps"
	bl_label = "Tilapiatsu : Register Keymaps"
	bl_options = {'REGISTER'}
	
	def execute(self,context):
		tila_keymaps.register()
		return {'FINISHED'}
 

class TILA_OP_UnegisterKeymaps(bpy.types.Operator):
	bl_idname = "wm.tila_unregister_keymaps"
	bl_label = "Tilapiatsu : Unregister Keymaps"
	bl_options = {'REGISTER'}
	
	
	def execute(self,context):
		tila_keymaps.unregister()
		return {'FINISHED'}
		
		

classes = (TILA_OP_RegisterKeymaps, TILA_OP_UnegisterKeymaps)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	
if __name__ == "__main__":
	register()