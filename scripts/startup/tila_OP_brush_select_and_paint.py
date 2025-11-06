import bpy
from blender_version import bversion

bl_info = {
	"name": "Tila : Brush Select and Paint",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}

compatible_tools = ['SCULPT', 'VERTEX', 'WEIGHT', 'IMAGE', 'GPENCIL_PAINT', 'GPENCIL_SCULPT', 'GPENCIL_WEIGHT', 'GPENCIL_VERTEX', 'CURVES_SCULPT']

def tools_enum():
    enum = [(t, t.lower().replace('_', ' '), '') for t in compatible_tools]

    return enum


class TILA_brush_select_and_paint(bpy.types.Operator):
	bl_idname = "paint.tila_brush_select_and_paint"
	bl_label = "Select Brush and Paint"

	tool : bpy.props.EnumProperty(name="tool", items=tools_enum(), default='SCULPT')
	default_mode : bpy.props.StringProperty(name="default brush", default='DRAW')
	mode : bpy.props.StringProperty(name="mode", default='DRAW')
	brush : bpy.props.StringProperty(name="brush", default='Mix')
	brush_asset_id : bpy.props.StringProperty(name="brush asset id", default='brushes\essentials_brushes-mesh_sculpt.blend\Brush\Grab')
	brush_asset_library_type : bpy.props.StringProperty(name="brush asset library type", default='ESSENTIALS')

	initial_brush = None
	brush_is_set = False
	press = False

	# @property
	# def compatible_brushes(self):
	# 	return [b.name for b in bpy.data.brushes]

	@property
	def brush_settings(self):
		if bpy.context.mode == 'PAINT_WEIGHT':
			return bpy.context.tool_settings.weight_paint.brush
		elif bpy.context.mode == 'PAINT_VERTEX':
			return bpy.context.tool_settings.vertex_paint.brush
		elif bpy.context.mode == 'PAINT_TEXTURE':
			return bpy.context.tool_settings.image_paint.brush
		elif bpy.context.mode == 'SCULPT':
			return bpy.context.tool_settings.sculpt.brush
		elif bpy.context.mode == 'SCULPT_CURVES':
			return bpy.context.tool_settings.curves_sculpt.brush
		elif bpy.context.mode == 'SCULPT_GREASE_PENCIL':
			return bpy.context.tool_settings.gpencil_sculpt.brush
		elif bpy.context.mode == 'VERTEX_GREASE_PENCIL':
			return bpy.context.tool_settings.gpencil_vertex_paint.brush
		elif bpy.context.mode == 'PAINT_GREASE_PENCIL':
			return bpy.context.tool_settings.gpencil_paint.brush
		elif bpy.context.mode == 'WEIGHT_GREASE_PENCIL':
			return bpy.context.tool_settings.gpencil_weight_paint.brush
	
	@property
	def brush_name(self):
		return self.brush_asset_id.split('\\')[-1]
	
	def get_release_condition(self, event):
		if bversion < 3.2:
			return event.type == 'MOUSEMOVE' and event.value == 'RELEASE'
		else:
			return event.type in ['MOUSEMOVE', 'LEFTMOUSE', 'RIGHTMOUSE', 'WINDOW_DEACTIVATE'] and event.value in ['RELEASE', 'NOTHING'] and self.press
	
	def get_run_condition(self, event) :
		if bversion < 3.2:
			return event.type == 'MOUSEMOVE' and event.value == 'PRESS'
		else:
			return event.type == 'MOUSEMOVE' and event.value == 'NOTHING' and not self.press

	def set_initial_brush(self):
		if self.brush_settings is None:
			return
		brush_settings = self.brush_settings

		self.initial_brush = {'name':brush_settings.name, 'weight':brush_settings.weight, 'strength':brush_settings.strength}

	def set_brush_settings(self, mode, brush):
		if self.brush_settings is None:
			return
		brush_settings = self.brush_settings

		bpy.ops.brush.tila_brush_toggle('INVOKE_DEFAULT', 
										mode=self.tool, 
										relative_asset_identifier= self.brush_asset_id, 
										asset_library_type= self.brush_asset_library_type, 
										asset_library_identifier='', 
										force_strength=False, 
										force_weight=False)
		brush_settings.weight = self.initial_brush['weight']
		brush_settings.strength = self.initial_brush['strength']
		
	def run_tool(self, mode, brush):
		try:
			if self.tool not in compatible_tools:
				return {'CANCELLED'}
			
			if not self.brush_is_set:
				self.set_brush_settings(mode, brush)
			
			if self.tool == 'SCULPT':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT')
			if self.tool == 'VERTEX':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.paint.vertex_paint('INVOKE_DEFAULT')
			if self.tool == 'WEIGHT':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.paint.weight_paint('INVOKE_DEFAULT')
			if self.tool == 'IMAGE':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.paint.image_paint('INVOKE_DEFAULT')
			if self.tool == 'GPENCIL_PAINT':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.grease_pencil.brush_stroke('INVOKE_DEFAULT')
			if self.tool == 'GPENCIL_SCULPT':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.grease_pencil.sculpt_paint('INVOKE_DEFAULT')
			if self.tool == 'GPENCIL_WEIGHT':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.grease_pencil.weight_brush_stroke('INVOKE_DEFAULT')
			if self.tool == 'GPENCIL_VERTEX':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.grease_pencil.vertex_brush_stroke('INVOKE_DEFAULT')
			if self.tool == 'CURVES_SCULPT':
				if mode != self.default_mode or brush != self.initial_brush['name']:
					bpy.ops.sculpt_curves.brush_stroke('INVOKE_DEFAULT')

		except RuntimeError as e:
			print('Runtime Error :\n{}'.format(e))

	def modal(self, context, event):
		if event.type in {'ESC'}:  # Cancel
			self.brush_is_set = False
			self.run_tool(self.default_mode, self.initial_brush['name'])
			self.brush_is_set = False
			return {'CANCELLED'}
		elif self.get_release_condition(event=event):
			self.press = False
			self.brush_is_set = False
			self.run_tool(self.default_mode, self.initial_brush['name'])
			self.brush_is_set = False
			return{'FINISHED'}
		elif self.get_run_condition(event=event):
			self.press = True
			self.run_tool(self.mode, self.brush)
		return {'RUNNING_MODAL'}

	def invoke(self, context, event):
		if self.tool in compatible_tools:
			self.set_initial_brush()
			context.window_manager.modal_handler_add(self)
		else:
			return{'FINISHED'}
		return {'RUNNING_MODAL'}


classes = (
	TILA_brush_select_and_paint,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
	register()