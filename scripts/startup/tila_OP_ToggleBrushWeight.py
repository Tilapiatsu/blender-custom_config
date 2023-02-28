import bpy


bl_info = {
    "name": "Tila : Toggle BrushWeight",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class TILA_ToggleBrushWeight(bpy.types.Operator):
    bl_idname = "paint.toggle_brushweight"
    bl_label = "TILA: Toggle Brush Weight"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode == 'PAINT_WEIGHT':
            bpy.context.tool_settings.weight_paint.brush.weight = 1 - bpy.context.tool_settings.weight_paint.brush.weight
        if bpy.context.mode == 'PAINT_VERTEX':
            pass
        return {'FINISHED'}

classes = (TILA_ToggleBrushWeight,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()