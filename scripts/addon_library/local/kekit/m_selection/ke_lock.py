from bpy.types import Operator
from bpy.props import EnumProperty


class KeLock(Operator):
    bl_idname = "view3d.ke_lock"
    bl_label = "Lock & Unlock"

    mode : EnumProperty(
        items=[("LOCK", "Lock", "", 1),
               ("LOCK_UNSELECTED", "Lock Unselected", "", 2),
               ("UNLOCK", "Unlock", "", 3)
               ],
        name="Lock & Unlock",
        options={'HIDDEN'},
        default="LOCK")

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "LOCK":
            return "Lock: Disable Selection for selected object(s)\nSee selection status in Outliner"
        if properties.mode == "LOCK_UNSELECTED":
            return "Lock Unselected: Disable Selection for all unselected object(s)\nSee selection status in Outliner"
        else:
            return "Unlock: Enables Selection for -all- objects"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):

        if self.mode == "LOCK":
            for obj in context.selected_objects:
                obj.hide_select = True

        elif self.mode == "LOCK_UNSELECTED":
            sel = context.selected_objects[:]
            for obj in context.scene.objects:
                if obj not in sel:
                    obj.hide_select = True

        elif self.mode == "UNLOCK":
            for obj in context.scene.objects:
                obj.hide_select = False

        return {'FINISHED'}
