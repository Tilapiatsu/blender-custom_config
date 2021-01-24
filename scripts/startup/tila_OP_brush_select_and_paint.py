import bpy


class TILA_brush_select_and_paint(bpy.types.Operator):
    bl_idname = "paint.tila_brush_select_and_paint"
    bl_label = "Select Brush and Paint"

    tool : bpy.props.StringProperty(name="tool", default='SCULPT')
    default_brush : bpy.props.StringProperty(name="default brush", default='DRAW')
    brush : bpy.props.StringProperty(name="brush", default='DRAW')

    compatible_tools = ['SCULPT', 'VERTEX', 'WEIGHT', 'IMAGE', 'GPENCIL']

    def run_tool(self, brush):
        try:
            if self.tool not in self.compatible_tools:
                return {'CANCELLED'}
            else:
                if self.tool == 'SCULPT':
                    bpy.ops.paint.brush_select('INVOKE_DEFAULT', sculpt_tool=brush, toggle=False)
                    if brush != self.default_brush:
                        bpy.ops.sculpt.brush_stroke('INVOKE_DEFAULT')
                if self.tool == 'VERTEX':
                    bpy.ops.paint.brush_select('INVOKE_DEFAULT', vertex_tool=brush, toggle=False)
                    if brush != self.default_brush:
                        bpy.ops.paint.vertex_paint('INVOKE_DEFAULT')
                if self.tool == 'WEIGHT':
                    bpy.ops.paint.brush_select('INVOKE_DEFAULT', weight_tool=brush, toggle=False)
                    if brush != self.default_brush:
                        bpy.ops.paint.weight_paint('INVOKE_DEFAULT')
                if self.tool == 'IMAGE':
                    bpy.ops.paint.brush_select('INVOKE_DEFAULT', image_tool=brush, toggle=False)
                    if brush != self.default_brush:
                        bpy.ops.paint.image_paint('INVOKE_DEFAULT')
                if self.tool == 'GPENCIL':
                    bpy.ops.paint.brush_select('INVOKE_DEFAULT', gpencil_tool=brush, toggle=False)
                    if brush != self.default_brush:
                        bpy.ops.gpencil.draw('INVOKE_DEFAULT')

        except RuntimeError as e:
            print('Runtime Error :\n{}'.format(e))

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE' and event.value == 'PRESS':
            self.run_tool(self.brush)
            return {'RUNNING_MODAL'}
        if event.type in {'ESC'}:  # Cancel
            self.run_tool(self.default_brush)
            return {'CANCELLED'}
        elif event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
            self.run_tool(self.default_brush)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if self.tool in self.compatible_tools:
            # self.run_tool(self.brush)
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