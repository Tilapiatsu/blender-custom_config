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
    "name" : "Batch UV Maps",
    "author" : "Arnas Karmaza",
    "description" : "Extra Batch UV Operators",
    "blender" : (2, 93, 0),
    "version" : (1, 0, 5),
    'location': 'Properties > Mesh Properties > UV Maps',
    "warning" : "",
    "category" : "Object"
}

import bpy

from . operators import (OBJECT_OT_set_active_render_uv,
 OBJECT_OT_set_active_uv,
  OBJECT_OT_delete_active_uv,
    OBJECT_OT_copy_unique_uv_layers,
    OBJECT_OT_move_UV_layer_down,
    OBJECT_OT_move_UV_layer_up,
    OBJECT_OT_sync_uv_layer_order)
from . operators import Operator 


#defining classes here
classes = (
    OBJECT_OT_set_active_uv,
    OBJECT_OT_delete_active_uv,
    OBJECT_OT_set_active_render_uv,
    OBJECT_OT_copy_unique_uv_layers,
    OBJECT_OT_move_UV_layer_down,
    OBJECT_OT_move_UV_layer_up,
    OBJECT_OT_sync_uv_layer_order
)

def draw(self, context):
    layout = self.layout
    row = layout.row()
    row.alignment = 'CENTER'
    row.label(text="Batch UV Tools")
    row = layout.row()  
    col1 = row.column(align=True)
    col1.label(text="Selected Objects:")
    col1.operator('object.set_active_uv_for_selected_objects', icon ='RIGHTARROW', text="Set Or Create")
    col1.operator('object.delete_active_uv_layer_for_selected_objects', icon='TRASH', text="Delete")
    col1.operator('object.set_active_uv_render_layer_for_selected_objects', icon='RESTRICT_RENDER_OFF', text="Set Active Render")
    col1.operator('object.copy_unique_uv_layers_for_selected_objects', icon='MOD_ARRAY', text="Copy Unique")
    col1.operator('object.sync_uv_layer_order_for_selected_objects', icon='SORTSIZE', text="Sync Layers Order")
    layout.separator()

    col2 = row.column(align=True)
    col2.label(text="Active Object:")
    col2.scale_x = 0.8
    col2.operator("object.move_uv_layer_up",text = 'Up', icon='TRIA_UP')
    col2.operator("object.move_uv_layer_down",text = 'Down', icon='TRIA_DOWN')
    
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

   #Drawing the Operator in UV maps panel
    bpy.types.DATA_PT_uv_texture.append(draw)
   

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

   #Removing the operator from UV maps panel
    bpy.types.DATA_PT_uv_texture.remove(draw)

