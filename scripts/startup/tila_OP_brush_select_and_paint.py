import bpy
from bversion import BVERSION

bl_info = {
    "name": "Tila : Brush Select and Paint",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}

compatible_modes = ['SCULPT', 'VERTEX', 'WEIGHT', 'IMAGE', 'GPENCIL_PAINT', 'GPENCIL_SCULPT', 'GPENCIL_WEIGHT', 'GPENCIL_VERTEX', 'SCULPT_CURVES']

def modes_enum():
    enum = [(t, t.lower().replace('_', ' '), '') for t in compatible_modes]

    return enum

compatible_asset_library_types = ['ALL', 'LOCAL', 'ESSENTIALS', 'CUSTOM']

class TILA_Brush():
    def __init__(   self,
                    name:str,
                    relative_asset_identifier:str,
                    asset_library_type:str,
                    asset_library_identifier:str,
                    weight:float,
                    strength:float) -> None :
        self.name = name
        self.relative_asset_identifier = relative_asset_identifier
        if asset_library_type not in compatible_asset_library_types:
            raise AttributeError
        self.asset_library_type = asset_library_type
        self.asset_library_identifier = asset_library_identifier
        self.weight = weight
        self.strength = strength

class TILA_brush_select_and_paint(bpy.types.Operator):
    bl_idname = "paint.tila_brush_select_and_paint"
    bl_label = "Select Brush and Paint"

    mode : bpy.props.EnumProperty(name="mode", items=modes_enum(), default='SCULPT')
    relative_asset_identifier : bpy.props.StringProperty(name="relative asset identifier", default='brushes\essentials_brushes-mesh_sculpt.blend\Brush\Grab')
    asset_library_type : bpy.props.StringProperty(name="asset library type", default='ESSENTIALS')
    asset_library_identifier : bpy.props.StringProperty(name="asset library identifier", default='')

    initial_brush_settings = None
    brush_is_set = False
    press = False

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
    def brush_asset_reference(self):
        if bpy.context.mode == 'PAINT_WEIGHT':
            return bpy.context.tool_settings.weight_paint.brush_asset_reference
        elif bpy.context.mode == 'PAINT_VERTEX':
            return bpy.context.tool_settings.vertex_paint.brush_asset_reference
        elif bpy.context.mode == 'PAINT_TEXTURE':
            return bpy.context.tool_settings.image_paint.brush_asset_reference
        elif bpy.context.mode == 'SCULPT':
            return bpy.context.tool_settings.sculpt.brush_asset_reference
        elif bpy.context.mode == 'SCULPT_CURVES':
            return bpy.context.tool_settings.curves_sculpt.brush_asset_reference
        elif bpy.context.mode == 'SCULPT_GREASE_PENCIL':
            return bpy.context.tool_settings.gpencil_sculpt.brush_asset_reference
        elif bpy.context.mode == 'VERTEX_GREASE_PENCIL':
            return bpy.context.tool_settings.gpencil_vertex_paint.brush_asset_reference
        elif bpy.context.mode == 'PAINT_GREASE_PENCIL':
            return bpy.context.tool_settings.gpencil_paint.brush_asset_reference
        elif bpy.context.mode == 'WEIGHT_GREASE_PENCIL':
            return bpy.context.tool_settings.gpencil_weight_paint.brush_asset_reference

    @property
    def brush_name(self):
        return self.brush_settings.name

    def get_release_condition(self, event):
        if BVERSION < 3.2:
            return event.type == 'MOUSEMOVE' and event.value == 'RELEASE'
        else:
            return event.type in ['MOUSEMOVE', 'LEFTMOUSE', 'RIGHTMOUSE', 'WINDOW_DEACTIVATE'] and event.value in ['RELEASE', 'NOTHING'] and self.press

    def get_run_condition(self, event) :
        if BVERSION < 3.2:
            return event.type == 'MOUSEMOVE' and event.value == 'PRESS'
        else:
            return event.type == 'MOUSEMOVE' and event.value == 'NOTHING' and not self.press

    def get_brush_settings(self) -> TILA_Brush:
        if self.brush_settings is None or self.brush_asset_reference is None:
            return

        brush_settings = self.brush_settings
        brush_asset_reference = self.brush_asset_reference

        return TILA_Brush(  brush_settings.name,
                            brush_asset_reference.relative_asset_identifier,
                            brush_asset_reference.asset_library_type,
                            brush_asset_reference.asset_library_identifier,
                            brush_settings.weight,
                            brush_settings.strength)

    def get_target_brush_settings(self) -> TILA_Brush:
        if self.brush_settings is None:
            return

        brush_settings = self.brush_settings

        return TILA_Brush(  self.relative_asset_identifier.split('\\')[-1],
                            self.relative_asset_identifier,
                            self.asset_library_type,
                            self.asset_library_identifier,
                            brush_settings.weight,
                            brush_settings.strength)

    def set_brush_settings(self, brush:TILA_Brush):
        if self.brush_settings is None:
            return

        brush_settings = self.brush_settings

        bpy.ops.brush.tila_brush_toggle('INVOKE_DEFAULT',
                                        mode=self.mode,
                                        relative_asset_identifier=brush.relative_asset_identifier,
                                        asset_library_type=brush.asset_library_type,
                                        asset_library_identifier=brush.asset_library_identifier,
                                        force_strength=False,
                                        force_weight=False)

        brush_settings.weight = brush.weight
        brush_settings.strength = brush.strength

    def run_tool(self, brush:TILA_Brush):
        try:
            if self.mode not in compatible_modes:
                return {'CANCELLED'}

            if not self.brush_is_set:
                self.set_brush_settings(brush)

            if brush.name != self.initial_brush_settings.name:
                if self.mode == 'SCULPT':
                    bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT')
                elif self.mode == 'VERTEX':
                    bpy.ops.paint.vertex_paint('INVOKE_DEFAULT')
                elif self.mode == 'WEIGHT':
                    bpy.ops.paint.weight_paint('INVOKE_DEFAULT')
                elif self.mode == 'IMAGE':
                    bpy.ops.paint.image_paint('INVOKE_DEFAULT')
                elif self.mode == 'GPENCIL_PAINT':
                    bpy.ops.grease_pencil.vertex_brush_stroke('INVOKE_DEFAULT')
                elif self.mode == 'GPENCIL_SCULPT':
                    bpy.ops.grease_pencil.sculpt_paint('INVOKE_DEFAULT')
                elif self.mode == 'GPENCIL_WEIGHT':
                    bpy.ops.grease_pencil.weight_brush_stroke('INVOKE_DEFAULT')
                elif self.mode == 'GPENCIL_VERTEX':
                    bpy.ops.grease_pencil.vertex_brush_stroke('INVOKE_DEFAULT')
                elif self.mode == 'SCULPT_CURVES':
                    bpy.ops.sculpt_curves.brush_stroke('INVOKE_DEFAULT')

        except RuntimeError as e:
            print('Runtime Error :\n{}'.format(e))

    def modal(self, context, event):
        if event.type in {'ESC'}:  # Cancel
            self.brush_is_set = False
            self.run_tool(self.initial_brush_settings)
            self.brush_is_set = False
            return {'CANCELLED'}

        elif self.get_release_condition(event=event):
            self.press = False
            self.brush_is_set = False
            self.run_tool(self.initial_brush_settings)
            self.brush_is_set = False
            return{'FINISHED'}

        elif self.get_run_condition(event=event):
            self.press = True
            brush = self.get_target_brush_settings()
            self.run_tool(brush)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if self.mode in compatible_modes:
            self.initial_brush_settings = self.get_brush_settings()
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