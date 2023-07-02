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
		prop = pie.operator("wm.area_split", text="Asset Browser")
		prop.ui_type = 'ASSETS'
		# prop = pie.operator("wm.area_split", text="Split").ui_type = 'VIEW_3D'
		
		
		# Right
		prop = pie.operator("wm.area_split", text="UV Editor").ui_type = 'UV'
		

		# Bottom
		prop = pie.operator("wm.area_split", text="Console")
		prop.ui_type = 'CONSOLE'

		# Top
		pie.operator('screen.area_close', text='Close')
		

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
		pie.operator("wm.3d_view", text="3D View")
		
		# prop.direction = 'HORIZONTAL'
		# prop = pie.operator("wm.context_set_enum", text="Outliner")
		# prop.data_path = "area.type"
		# prop.value = 'OUTLINER'  	

		# Bottom Right
		prop = pie.operator("wm.area_split", text="Geometry Node").ui_type = 'GeometryNodeTree'
		# prop = pie.operator("wm.context_set_enum", text="Properties")
		# prop.data_path = "area.type"
		# prop.value = 'PROPERTIES'

class TILA_OT_areas_3d_view(bpy.types.Operator):
	bl_idname = 'wm.3d_view'
	bl_label = 'UV View'
	def execute(self, context):
		bpy.ops.wm.context_set_enum(data_path='area.type', value='VIEW_3D')

		bpy.context.area.ui_type = 'VIEW_3D'
		return {'FINISHED'}
	
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
											("SPREADSHEET", 'SpreadSheet', ''),
											("CONSOLE", 'Console', '')])

	direction : bpy.props.EnumProperty(items=[("VERTICAL", "Vertical", ""), ("HORIZONTAL", "Horizontal", "")])
	factor : bpy.props.FloatProperty(name='Factor', default=0.5)

	editor_areas = ['NODE_EDITOR', 'IMAGE_EDITOR']
	property_areas = ['SPREADSHEET']
	asset_areas = ['FILE_BROWSER']
	console_areas = ['CONSOLE']

	def execute(self, context):
		self.editor_type = 'VIEW_3D'
		if self.ui_type in ['ShaderNodeTree', 'TextureNodeTree', 'GeometryNodeTree', 'BakeWrangler_Tree', 'CompositorNodeTree']:
			self.editor_type = 'NODE_EDITOR'
		elif self.ui_type in ['UV']:
			self.editor_type = 'IMAGE_EDITOR'
		elif self.ui_type in ['ASSETS']:
			self.editor_type = 'FILE_BROWSER'
		elif self.ui_type in ['SPREADSHEET']:
			self.editor_type = 'SPREADSHEET'
		elif self.ui_type in ['CONSOLE']:
			self.editor_type = 'CONSOLE'

		if self.editor_type in self.editor_areas:
			if self.editor_area is None:
				self.switch_area(self.view3d_area, split=True)
			else:
				self.switch_area(self.editor_area, split=False)

		elif self.editor_type in self.property_areas:
			if self.property_area is None:
				self.switch_area(self.view3d_area, split=True)
			else:
				self.switch_area(self.property_area, split=False)

		elif self.editor_type in self.asset_areas:
			if self.asset_area is None:
				self.switch_area(self.view3d_area, split=True, factor=0.51)
			else:
				self.switch_area(self.asset_area, split=False)
			
		elif self.editor_type in self.console_areas:
			if self.asset_area is None:
				self.switch_area(self.view3d_area, direction='HORIZONTAL', split=True, factor=0.51)
			else:
				self.switch_area(self.asset_area, split=False)
		else:
			self.switch_area(self.view3d_area, split=True)

		# self.switch_area(self.view3d_area)

		return {'FINISHED'}
	
	@property
	def view3d_area(self):
		for i in range(len(bpy.context.screen.areas)):
			area = bpy.context.screen.areas[i]
			if area.type == 'VIEW_3D':
				print(f'Storing {area.type} index {i}')
				bpy.context.window_manager.tila_area_3d_view = i
				break
		else:
			print(f'No 3D Area in the current windows')
			
		return bpy.context.screen.areas[bpy.context.window_manager.tila_area_3d_view]
	
	@property
	def editor_area(self):
		for i in range(len(bpy.context.screen.areas)):
			area = bpy.context.screen.areas[i]
			if area.type in self.editor_areas:
				print(f'Storing {area.type} index {i}')
				bpy.context.window_manager.tila_area_editor = i
				break
		else:
			return None
		return bpy.context.screen.areas[bpy.context.window_manager.tila_area_editor]
	
	@property
	def property_area(self):
		for i in range(len(bpy.context.screen.areas)):
			area = bpy.context.screen.areas[i]
			if area.type in self.property_areas:
				print(f'Storing {area.type} index {i}')
				bpy.context.window_manager.tila_area_property = i
				break
		else:
			return None
		return bpy.context.screen.areas[bpy.context.window_manager.tila_area_property]
	
	@property
	def asset_area(self):
		for i in range(len(bpy.context.screen.areas)):
			area = bpy.context.screen.areas[i]
			if area.type in self.asset_areas:
				print(f'Storing {area.type} index {i}')
				bpy.context.window_manager.tila_area_asset_browser = i
				break
		else:
			return None
		return bpy.context.screen.areas[bpy.context.window_manager.tila_area_asset_browser]
	
	def switch_area(self, area:bpy.types.Area, direction='VERTICAL', factor=0.5, split=False):
		with bpy.context.temp_override(area=area):
			if split:
				print(f'Splitting Area {area.type}')
				bpy.ops.screen.area_split('EXEC_DEFAULT', direction=direction, factor=factor)
			bpy.context.area.ui_type = self.ui_type
			bpy.ops.wm.context_set_enum(data_path='area.type', value=self.editor_type)


	def area_in_range(self, area_index):
		return area_index >= 0 and area_index < len(bpy.context.screen.areas)

classes = (
	TILA_MT_pie_areas,
 	TILA_OT_areas_uv_view,
	TILA_OT_areas_shader_view,
	TILA_OT_area_split,
   	TILA_OT_areas_3d_view
)

def register():

	bpy.types.WindowManager.tila_area_3d_view = bpy.props.IntProperty(name='View3D Area', default=-1)
	bpy.types.WindowManager.tila_area_editor = bpy.props.IntProperty(name='Editor Area', default=-1)
	bpy.types.WindowManager.tila_area_property = bpy.props.IntProperty(name='Property Area', default=-1)
	bpy.types.WindowManager.tila_area_asset_browser = bpy.props.IntProperty(name='Asset Browser Area', default=-1)

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