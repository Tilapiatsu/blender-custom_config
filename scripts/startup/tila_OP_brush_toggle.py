import bpy
from os import path
from blender_version import bversion

bl_info = {
    "name": "Tila : Brush toggle",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}

class TILA_Brush:
    def __init__(self, relative_asset_identifier:str, asset_library_type:str, asset_library_identifier:str):
        self.relative_asset_identifier = path.normpath(relative_asset_identifier)
        self.asset_library_type = asset_library_type
        self.asset_library_identifier = asset_library_identifier
    
    @property
    def name(self):
        return path.basename(self.relative_asset_identifier)

    def activate(self):
        bpy.ops.brush.asset_activate(relative_asset_identifier= self.relative_asset_identifier, asset_library_type= self.asset_library_type, asset_library_identifier=self.asset_library_identifier)

    def __eq__(self, other):
        if isinstance(other, TILA_Brush):
            return (self.relative_asset_identifier == other.relative_asset_identifier and
                    self.asset_library_type == other.asset_library_type and 
                    self.asset_library_identifier == other.asset_library_identifier)
        return False

class TILA_PG_Brush(bpy.types.PropertyGroup):
    relative_asset_identifier : bpy.props.StringProperty(name='relative_asset_identifier', default='')
    asset_library_type :        bpy.props.StringProperty(name='asset_library_type', default='')
    asset_library_identifier :  bpy.props.StringProperty(name='asset_library_identifier', default='')


class TILA_Brush_toggle(bpy.types.Operator):
    bl_idname = "brush.tila_brush_toggle"
    bl_label = "Brush Toggle"

    mode : bpy.props.StringProperty(name="mode", default='SCULPT')
    default_relative_asset_identifier : bpy.props.StringProperty(name="default brush", default='brushes\essentials_brushes-mesh_sculpt.blend\Brush\Grab')
    default_asset_library_type : bpy.props.StringProperty(name="asset library type", default='ESSENTIALS')
    default_asset_library_identifier : bpy.props.StringProperty(name="asset library identifier", default='')
    relative_asset_identifier : bpy.props.StringProperty(name="brush", default='brushes\essentials_brushes-mesh_sculpt.blend\Brush\Grab')
    asset_library_type : bpy.props.StringProperty(name="asset library type", default='ESSENTIALS')
    asset_library_identifier : bpy.props.StringProperty(name="asset library identifier", default='')
    toggle_back_on_release : bpy.props.BoolProperty(name='toggle back on release', default=False)

    compatible_modes = ['SCULPT', 'VERTEX', 'WEIGHT', 'IMAGE', 'GPENCIL']

    initial_brush = None
    brush_is_set = False
    press = False
    
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
            tools = bpy.context.tool_settings.sculpt
            self.initial_brush = {'name':tools.brush.name, 'weight':tools.brush.weight, 'strength':tools.brush.strength}
        elif self.mode == 'VERTEX':
            tools = bpy.context.tool_settings.vertex_paint
            self.initial_brush = {'name':tools.brush.name, 'weight':tools.brush.weight, 'strength':tools.brush.strength}
        elif self.mode == 'WEIGHT':
            tools = bpy.context.tool_settings.weight_paint
            self.initial_brush = {'name':tools.brush.name, 'weight':tools.brush.weight, 'strength':tools.brush.strength}
        elif self.mode == 'IMAGE':
            tools = bpy.context.tool_settings.image_paint
            self.initial_brush = {'name':tools.brush.name, 'weight':tools.brush.weight, 'strength':tools.brush.strength}
        elif self.mode == 'GPENCIL':
            tools = bpy.context.tool_settings.gpencil_paint
            self.initial_brush = {'name':tools.brush.name, 'weight':tools.brush.weight, 'strength':tools.brush.strength}

        self.target_brush = TILA_Brush(self.relative_asset_identifier, self.asset_library_type, self.asset_library_identifier)
        self.default_brush = TILA_Brush(self.default_relative_asset_identifier, self.default_asset_library_type, self.default_asset_library_identifier)
        self.previous_brush = TILA_Brush(bpy.context.window_manager.tila_previous_brush.relative_asset_identifier, 
                                         bpy.context.window_manager.tila_previous_brush.asset_library_type,
                                         bpy.context.window_manager.tila_previous_brush.asset_library_identifier)
        self.current_brush = TILA_Brush(tools.brush_asset_reference.relative_asset_identifier,
                                        tools.brush_asset_reference.asset_library_type,
                                        tools.brush_asset_reference.asset_library_identifier)

    def store_previous_brush(self, relative_asset_identifier, asset_library_type, asset_library_identifier):
        bpy.context.window_manager.tila_previous_brush.relative_asset_identifier = relative_asset_identifier
        bpy.context.window_manager.tila_previous_brush.asset_library_type = asset_library_type
        bpy.context.window_manager.tila_previous_brush.asset_library_identifier = asset_library_identifier

    def set_brush_settings(self, brush:TILA_Brush):
        if self.mode == 'SCULPT':
            self.store_previous_brush(  bpy.context.tool_settings.sculpt.brush_asset_reference.relative_asset_identifier,
                                        bpy.context.tool_settings.sculpt.brush_asset_reference.asset_library_type,
                                        bpy.context.tool_settings.sculpt.brush_asset_reference.asset_library_identifier)
            brush.activate()
            bpy.context.tool_settings.sculpt.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.sculpt.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.mode == 'VERTEX':
            self.store_previous_brush(  bpy.context.tool_settings.vertex_paint.brush_asset_reference.relative_asset_identifier,
                                        bpy.context.tool_settings.vertex_paint.brush_asset_reference.asset_library_type,
                                        bpy.context.tool_settings.vertex_paint.brush_asset_reference.asset_library_identifier)
            brush.activate()
            bpy.context.tool_settings.vertex_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.vertex_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.mode == 'WEIGHT':
            self.store_previous_brush(  bpy.context.tool_settings.weight_paint.brush_asset_reference.relative_asset_identifier,
                                        bpy.context.tool_settings.weight_paint.brush_asset_reference.asset_library_type,
                                        bpy.context.tool_settings.weight_paint.brush_asset_reference.asset_library_identifier)
            brush.activate()
            bpy.context.tool_settings.weight_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.weight_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.mode == 'IMAGE':
            self.store_previous_brush(  bpy.context.tool_settings.image_paint.brush_asset_reference.relative_asset_identifier,
                                        bpy.context.tool_settings.image_paint.brush_asset_reference.asset_library_type,
                                        bpy.context.tool_settings.image_paint.brush_asset_reference.asset_library_identifier)
            brush.activate()
            bpy.context.tool_settings.image_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.image_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

        elif self.mode == 'GPENCIL':
            self.store_previous_brush(  bpy.context.tool_settings.gpencil_paint.brush_asset_reference.relative_asset_identifier,
                                        bpy.context.tool_settings.gpencil_paint.brush_asset_reference.asset_library_type,
                                        bpy.context.tool_settings.gpencil_paint.brush_asset_reference.asset_library_identifier)
            brush.activate()
            bpy.context.tool_settings.gpencil_paint.brush.weight = self.initial_brush['weight']
            bpy.context.tool_settings.gpencil_paint.brush.strength = self.initial_brush['strength']
            self.brush_is_set = True

    def run_tool(self, brush:TILA_Brush):
        try:
            if self.mode not in self.compatible_modes:
                return {'CANCELLED'}
            
            if not self.brush_is_set:
                if brush == self.current_brush:
                    brush = self.previous_brush
                elif brush == self.default_brush and self.current_brush == self.default_brush:
                    brush = self.previous_brush
                elif brush == self.previous_brush:
                    brush == self.default_brush

                self.set_brush_settings(brush)
            
            if self.toggle_back_on_release:
                if self.mode == 'SCULPT':
                    if brush != self.default_brush:
                        bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT')
                elif self.mode == 'VERTEX':
                    if brush != self.default_brush:
                        bpy.ops.paint.vertex_paint('INVOKE_DEFAULT')
                elif self.mode == 'WEIGHT':
                    if brush != self.default_brush:
                        bpy.ops.paint.weight_paint('INVOKE_DEFAULT')
                elif self.mode == 'IMAGE':
                    if brush != self.default_brush:
                        bpy.ops.paint.image_paint('INVOKE_DEFAULT')
                elif self.mode == 'GPENCIL':
                    if brush != self.default_brush:
                        bpy.ops.gpencil.draw('INVOKE_DEFAULT')

        except RuntimeError as e:
            print('Runtime Error :\n{}'.format(e))

    def modal(self, context, event):
        if event.type in {'ESC'}:  # Cancel
            self.brush_is_set = False
            self.run_tool(self.default_brush)
            self.brush_is_set = False
            return {'CANCELLED'}
        elif self.get_release_condition(event=event):
            self.press = False
            self.brush_is_set = False
            self.run_tool(self.default_brush)
            self.brush_is_set = False
            return{'FINISHED'}
        elif self.get_run_condition(event=event):
            self.press = True
            self.run_tool(self.target_brush)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if self.mode in self.compatible_modes:
            self.set_initial_brush()
            if self.toggle_back_on_release:
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                self.run_tool(self.target_brush)
                self.brush_is_set = False
                return{'FINISHED'}
        else:
            return{'FINISHED'}


classes = (
    TILA_Brush_toggle,
    TILA_PG_Brush
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.WindowManager.tila_previous_brush = bpy.props.PointerProperty(name='Previous Brush', type=TILA_PG_Brush)


def unregister():

    del bpy.types.WindowManager.previous_brush 

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()