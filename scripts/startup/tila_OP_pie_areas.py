bl_info = {
	"name": "Pie Areas",
	"description": "Area Types",
	"author": "Tilapiatsu",
	"version": (0, 1, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"wiki_url": "",
	"category": "Pie Menu"
	}

import bpy
from bpy.types import (
		Menu,
		)
import os

class TILA_MT_pie_areas(Menu):
	bl_label = "Areas"

	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie() 	
		# left
#   	 pie.operator("wm.preview_render", text="Preview Render")

		prop = pie.operator("wm.context_set_enum", text="Timeline")
		prop.data_path = "area.type"
		prop.value = 'DOPESHEET_EDITOR'
		# right
		pie.operator("wm.3dview", text="3D View")
		# bottom
		#block
		prop = pie.operator("wm.context_set_enum", text="Python Console")
		prop.data_path = "area.type"
		prop.value = 'CONSOLE'  

		# top
		pie.operator("screen.screen_full_area", text="Maximize")

		prop = pie.operator("wm.uv_view", text="UV Editor")

		prop = pie.operator("wm.context_set_enum", text="Shader Editor")
		prop.data_path = "area.type"
		prop.value = 'NODE_EDITOR'  	  
		prop = pie.operator("wm.context_set_enum", text="Outliner")
		prop.data_path = "area.type"
		prop.value = 'OUTLINER'  	 
		prop = pie.operator("wm.context_set_enum", text="Properties")
		prop.data_path = "area.type"
		prop.value = 'PROPERTIES'  	 
#		pie.operator("wm.areas_popup", text="Outliner Popup").area = 'OUTLINER'

class TILA_OT_areas_uv_view(bpy.types.Operator):
	bl_idname = 'wm.uv_view'
	bl_label = 'UV View'
	def execute(self, context):
		bpy.ops.wm.context_set_enum(data_path='area.type', value='IMAGE_EDITOR')
		bpy.context.area.ui_type = 'UV'
		return {'FINISHED'}

classes = (
	TILA_MT_pie_areas,
 	TILA_OT_areas_uv_view
)
register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()