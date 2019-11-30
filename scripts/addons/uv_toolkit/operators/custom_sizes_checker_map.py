import bpy


class CustomSizesCheckerMap(bpy.types.Operator):
    bl_idname = "uv.toolkit_custom_sizes_checker_map"
    bl_label = "Create Checker Map"
    bl_description = "Create checker map"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        uv_toolkit = context.scene.uv_toolkit

        bpy.ops.uv.toolkit_create_checker_map(width=uv_toolkit.checker_map_width,
                                              height=uv_toolkit.checker_map_height)
        return {'FINISHED'}
