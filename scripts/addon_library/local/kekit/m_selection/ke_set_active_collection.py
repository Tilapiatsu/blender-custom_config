from bpy.types import Operator
from .._utils import set_active_collection


class KeSetActiveCollection(Operator):
    bl_idname = "view3d.ke_set_active_collection"
    bl_label = "Set Active Collection"
    bl_description = "[keKit] Set selected object's parent collection as Active (also in Object Context Menu)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        set_active_collection(context, context.object)
        return {"FINISHED"}
