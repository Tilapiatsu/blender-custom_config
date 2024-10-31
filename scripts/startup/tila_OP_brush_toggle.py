import bpy
from blender_version import bversion

bl_info = {
    "name": "Tila : Brush toggle",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}

class TILA_brush_toggle(bpy.types.Operator):
    bl_idname = "paint.tila_brush_toggle"
    bl_label = "Brush Toggle"

    mode : bpy.props.StringProperty(name="mode", default='SCULPT')
    default_brush_asset : bpy.props.StringProperty(name="default brush", default='brushes\essentials_brushes-mesh_sculpt.blend\Brush\Grab')
    brush_asset : bpy.props.StringProperty(name="brush", default='brushes\essentials_brushes-mesh_sculpt.blend\Brush\Grab')
    brush : bpy.props.StringProperty(name="brush", default='Mix')
    toggle_on_release : bpy.props.BoolProperty(name='toggle on release', default=False)

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
        if self.mode == 'SCULPT':
            brush = bpy.context.tool_settings.sculpt.brush
            self.initial_brush = {'name':brush.name, 'weight':brush.weight, 'strength':brush.strength}
        if self.mode == 'VERTEX':
            brush = bpy.context.tool_settings.vertex_paint.brush
            self.initial_brush = {'name':brush.name, 'weight':brush.weight, 'strength':brush.strength}
        if self.mode == 'WEIGHT':
            brush = bpy.context.tool_settings.weight_paint.brush
            self.initial_brush = {'name':brush.name, 'weight':brush.weight, 'strength':brush.strength}
        if self.mode == 'IMAGE':
            brush = bpy.context.tool_settings.image_paint.brush
            self.initial_brush = {'name':brush.name, 'weight':brush.weight, 'strength':brush.strength}
        if self.mode == 'GPENCIL':
            pass

    def set_brush_settings(self, brush_asset, brush):
        if self.mode == 'SCULPT':
            # bpy.ops.paint.brush_select('INVOKE_DEFAULT', sculpt_tool=mode, toggle=False)
            bpy.ops.brush.asset_activate(relative_asset_identifier= brush_asset, asset_library_type= 'ESSENTIALS', asset_library_identifier='')
            bpy.context.tool_settings.sculpt.brush = bpy.data.brushes[brush]
            bpy.context.tool_settings.sculpt.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.sculpt.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True
            
        elif self.mode == 'VERTEX':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', vertex_tool=brush_asset, toggle=False)
            bpy.context.tool_settings.vertex_paint.brush = bpy.data.brushes[brush]
            bpy.context.tool_settings.vertex_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.vertex_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.mode == 'WEIGHT':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', weight_tool=brush_asset, toggle=False)
            bpy.context.tool_settings.weight_paint.brush = bpy.data.brushes[brush]
            bpy.context.tool_settings.weight_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.weight_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.mode == 'IMAGE':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', image_tool=brush_asset, toggle=False)
            bpy.context.tool_settings.image_paint.brush = bpy.data.brushes[brush]
            bpy.context.tool_settings.image_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.image_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.mode == 'GPENCIL':
            bpy.ops.paint.brush_select('INVOKE_DEFAULT', gpencil_tool=brush_asset, toggle=False)
            self.brush_is_set = True

    def run_tool(self, brush_asset, brush):
        try:
            if self.mode not in self.compatible_tools:
                return {'CANCELLED'}
            
            if not self.brush_is_set:
                self.set_brush_settings(brush_asset, brush)
            
            if self.mode == 'SCULPT':
                if brush_asset != self.default_brush_asset or brush != self.initial_brush['name']:
                    bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT')
            if self.mode == 'VERTEX':
                if brush_asset != self.default_brush_asset or brush != self.initial_brush['name']:
                    bpy.ops.paint.vertex_paint('INVOKE_DEFAULT')
            if self.mode == 'WEIGHT':
                if brush_asset != self.default_brush_asset or brush != self.initial_brush['name']:
                    bpy.ops.paint.weight_paint('INVOKE_DEFAULT')
            if self.mode == 'IMAGE':
                if brush_asset != self.default_brush_asset or brush != self.initial_brush['name']:
                    bpy.ops.paint.image_paint('INVOKE_DEFAULT')
            if self.mode == 'GPENCIL':
                if brush_asset != self.default_brush_asset or brush != self.initial_brush['name']:
                    bpy.ops.gpencil.draw('INVOKE_DEFAULT')

        except RuntimeError as e:
            print('Runtime Error :\n{}'.format(e))

    def modal(self, context, event):
        if event.type in {'ESC'}:  # Cancel
            self.brush_is_set = False
            self.run_tool(self.default_brush_asset, self.initial_brush['name'])
            self.brush_is_set = False
            return {'CANCELLED'}
        elif self.get_release_condition(event=event):
            self.press = False
            self.brush_is_set = False
            self.run_tool(self.default_brush_asset, self.initial_brush['name'])
            self.brush_is_set = False
            return{'FINISHED'}
        elif self.get_run_condition(event=event):
            self.press = True
            self.run_tool(self.brush_asset, self.brush)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if self.mode in self.compatible_tools and self.brush in self.compatible_brushes:
            self.set_initial_brush()
            if self.toggle_on_release:
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                self.run_tool(self.brush_asset, self.brush)
        else:
            return{'FINISHED'}


classes = (
    TILA_brush_toggle,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.WindowManager.previous_brush = bpy.props.StringProperty(name='Previous Brush', default='')


def unregister():

    del bpy.types.WindowManager.previous_brush 

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()