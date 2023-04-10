bl_info = {
	"name": "Tila : Pie Areas",
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

		# Left
		prop = pie.operator("wm.area_split", text="Split").ui_type = 'VIEW_3D'
		
		
		# Right
		pie.operator("wm.3dview", text="3D View")

		# Bottom
		pie.operator('screen.area_close', text='Close')
		# pie.operator("wm.uv_view", text="UV Editor")

		# Top
		prop = pie.operator("wm.area_split", text="Geometry Node").ui_type = 'GeometryNodeTree'

		# Top Left
		prop = pie.operator("wm.area_split", text="Spreadsheet").ui_type = 'SPREADSHEET'

		# prop = pie.operator("wm.context_set_enum", text="Python Console")
		# prop.data_path = "area.type"
		# prop.value = 'CONSOLE'

		# Top Right
		prop = pie.operator("wm.area_split", text="Shader Editor").ui_type = 'ShaderNodeTree'
		# prop = pie.operator("wm.context_set_enum", text="Timeline")
		# prop.data_path = "area.type"
		# prop.value = 'DOPESHEET_EDITOR'

		# Bottom Left
		prop = pie.operator("wm.area_split", text="Asset Browser")
		prop.ui_type = 'ASSETS'
		# prop.direction = 'HORIZONTAL'
		# prop = pie.operator("wm.context_set_enum", text="Outliner")
		# prop.data_path = "area.type"
		# prop.value = 'OUTLINER'  	

		# Bottom Right
		prop = pie.operator("wm.area_split", text="UV Editor").ui_type = 'UV'
		# prop = pie.operator("wm.context_set_enum", text="Properties")
		# prop.data_path = "area.type"
		# prop.value = 'PROPERTIES'

class TILA_OT_areas_uv_view(bpy.types.Operator):
	bl_idname = 'wm.uv_view'
	bl_label = 'UV View'
	def execute(self, context):
		bpy.ops.wm.context_set_enum(data_path='area.type', value='IMAGE_EDITOR')
		bpy.context.area.ui_type = 'UV'
		return {'FINISHED'}

class TILA_OT_areas_shader_view(bpy.types.Operator):
	bl_idname = 'wm.shader_view'
	bl_label = 'UV View'
	ui_type : bpy.props.EnumProperty(items=[("ShaderNodeTree", "Shader", ""), ("TextureNodeTree", "Texture", ""), ("GeometryNodeTree", "Geometry", ""), ("BakeWrangler_Tree", "Bake", ""), ("CompositorNodeTree", "Compositor", "")])
	def execute(self, context):
		bpy.ops.wm.context_set_enum(data_path='area.type', value='NODE_EDITOR')
		bpy.context.area.ui_type = self.ui_type
		return {'FINISHED'}

class TILA_OT_area_split(bpy.types.Operator):
	bl_idname = 'wm.area_split'
	bl_label = 'Area Split'

	ui_type : bpy.props.EnumProperty(items=[("ShaderNodeTree", "Shader", ""),
					 						("TextureNodeTree", "Texture", ""),
											("GeometryNodeTree", "Geometry", ""),
											("BakeWrangler_Tree", "Bake", ""),
											("CompositorNodeTree", "Compositor", ""),
											("UV", "Uv", ""),
											("VIEW_3D", 'View 3D', ''),
											("ASSETS", 'Asset Browser', ''),
											("SPREADSHEET", 'SpreadSheet', '')])

	direction : bpy.props.EnumProperty(items=[("VERTICAL", "Vertical", ""), ("HORIZONTAL", "Horizontal", "")])
	factor : bpy.props.FloatProperty(name='Factor', default=0.5)

	def execute(self, context):
		window = context.window_manager.windows[0]
		bpy.ops.screen.area_split(direction=self.direction, factor=self.factor, cursor=(0, 0))

		

		editor_type = 'VIEW_3D'
		if self.ui_type in ['ShaderNodeTree', 'TextureNodeTree', 'GeometryNodeTree', 'BakeWrangler_Tree', 'CompositorNodeTree']:
			editor_type = 'NODE_EDITOR'
		elif self.ui_type in ['UV']:
			editor_type = 'IMAGE_EDITOR'
		elif self.ui_type in ['ASSETS']:
			editor_type = 'FILE_BROWSER'
		elif self.ui_type in ['SPREADSHEET']:
			editor_type = 'SPREADSHEET'


		bpy.ops.wm.context_set_enum(data_path='area.type', value=editor_type)
		bpy.context.area.ui_type = self.ui_type
		return {'FINISHED'}
	
	@property
	def view3d_area(self):
		if bpy.context.window_manager.tila_area_3d_view is None:
			for area in bpy.context.screen.areas:
				if area.type == 'VIEW_3D':
					bpy.context.window_manager.tila_area_3d_view = area
		
		if bpy.context.window_manager.tila_area_3d_view is None:
			print(f'No 3D Area in the current windows')
		return bpy.context.window_manager.tila_area_3d_view
	
	def split_area(self, area, direction='VERTICAL', factor=0.5):
		with bpy.context.temp_override(area=area):
			bpy.ops.screen.area_split('EXEC_DEFAULT', direction=direction, factor=factor)

classes = (
	TILA_MT_pie_areas,
 	TILA_OT_areas_uv_view,
	TILA_OT_areas_shader_view,
	TILA_OT_area_split
)

def register():

	bpy.types.WindowManager.tila_area_3d_view = bpy.props.PointerProperty(name='View3D Area', type=bpy.types.Area)
	bpy.types.WindowManager.tila_area_editor = bpy.props.PointerProperty(name='Editor Area', type=bpy.types.Area)
	bpy.types.WindowManager.tila_area_property = bpy.props.PointerProperty(name='Property Area', type=bpy.types.Area)
	bpy.types.WindowManager.tila_area_asset_browser = bpy.props.PointerProperty(name='Asset Browser Area', type=bpy.types.Area)

	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():

	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	del bpy.types.WindowManager.tila_area_asset_browser
	del bpy.types.WindowManager.tila_area_property
	del bpy.types.WindowManager.tila_area_editor
	del bpy.types.WindowManager.tila_area_3d_view

if __name__ == "__main__":
	register()