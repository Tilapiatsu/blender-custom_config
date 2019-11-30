import bpy


class MirrorSeam(bpy.types.Operator):
    bl_idname = "uv.toolkit_mirror_seam"
    bl_label = "Mirror Seam"
    bl_description = "Mirror Seam"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        mirror_settings = context.object.data.use_mirror_topology
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_seam(clear=False)

        context.object.data.use_mirror_topology = True
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_seam(clear=False)
        context.object.data.use_mirror_topology = mirror_settings
        return {'FINISHED'}
