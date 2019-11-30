import bpy
from bpy.props import BoolProperty


class MirrorUv(bpy.types.Operator):
    bl_idname = "uv.toolkit_mirror_uv"
    bl_label = "Mirror selected UV"
    bl_description = "Mirror UV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    x: BoolProperty(name="x", options={'HIDDEN'})
    y: BoolProperty(name="y", options={'HIDDEN'})
    z: BoolProperty(name="z", options={'HIDDEN'})

    def execute(self, context):
        bpy.ops.transform.mirror('EXEC_DEFAULT', constraint_axis=(self.x, self.y, self.z))
        return {'FINISHED'}
