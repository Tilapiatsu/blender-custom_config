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

class TILA_brush_select_and_paint(bpy.types.Operator):
    bl_idname = "paint.tila_brush_select_and_paint"
    bl_label = "Select Brush and Paint"

    tool : bpy.props.StringProperty(name="tool", default='SCULPT')
    default_mode : bpy.props.StringProperty(name="default brush", default='DRAW')
    mode : bpy.props.StringProperty(name="mode", default='DRAW')
    brush : bpy.props.StringProperty(name="brush", default='Mix')

    compatible_tools = ['SCULPT', 'VERTEX', 'WEIGHT', 'IMAGE', 'GPENCIL']

    initial_brush = None
    brush_is_set = False
    press = False

    @property
    def compatible_brushes(self):
        return [b.name for b in bpy.data.brushes]
    
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
        if self.tool == 'SCULPT':
            brush = bpy.context.tool_settings.sculpt.brush
            self.initial_brush = {'name':brush.name, 'weight':brush.weight, 'strength':brush.strength}
        if self.tool == 'VERTEX':
            brush = bpy.context.tool_settings.vertex_paint.brush
            self.initial_brush = {'name':brush.name, 'weight':brush.weight, 'strength':brush.strength}
        if self.tool == 'WEIGHT':
            brush = bpy.context.tool_settings.weight_paint.brush
            self.initial_brush = {'name':brush.name, 'weight':brush.weight, 'strength':brush.strength}
        if self.tool == 'IMAGE':
            brush = bpy.context.tool_settings.image_paint.brush
            self.initial_brush = {'name':brush.name, 'weight':brush.weight, 'strength':brush.strength}
        if self.tool == 'GPENCIL':
            pass

    def set_brush_settings(self, mode, brush):
        if self.tool == 'SCULPT':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', sculpt_tool=mode, toggle=False)
            bpy.context.tool_settings.sculpt.brush = bpy.data.brushes[brush]
            bpy.context.tool_settings.sculpt.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.sculpt.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True
            
        elif self.tool == 'VERTEX':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', vertex_tool=mode, toggle=False)
            bpy.context.tool_settings.vertex_paint.brush = bpy.data.brushes[brush]
            bpy.context.tool_settings.vertex_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.vertex_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.tool == 'WEIGHT':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', weight_tool=mode, toggle=False)
            bpy.context.tool_settings.weight_paint.brush = bpy.data.brushes[brush]
            bpy.context.tool_settings.weight_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.weight_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.tool == 'IMAGE':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', image_tool=mode, toggle=False)
            bpy.context.tool_settings.image_paint.brush = bpy.data.brushes[brush]
            bpy.context.tool_settings.image_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.image_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.tool == 'GPENCIL':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', gpencil_tool=mode, toggle=False)
            self.brush_is_set = True

    def run_tool(self, mode, brush):
        try:
            if self.tool not in self.compatible_tools:
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
            if self.tool == 'GPENCIL':
                if mode != self.default_mode or brush != self.initial_brush['name']:
                    bpy.ops.gpencil.draw('INVOKE_DEFAULT')

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
        if self.tool in self.compatible_tools and self.brush in self.compatible_brushes:
            self.set_initial_brush()
            context.window_manager.modal_handler_add(self)
        else:
            return{'FINISHED'}
        return {'RUNNING_MODAL'}


classes = (
    TILA_brush_select_and_paint,
)


register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()