import bpy
from bpy.types import Operator


class KeViewBookmarkCycle(Operator):
    bl_idname = "view3d.ke_view_bookmark_cycle"
    bl_label = "Cycle View Bookmarks"
    bl_description = "Cycle stored Viewport Bookmarks"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        kt = context.scene.kekit_temp
        slots = [bool(sum(kt.viewslot1)), bool(sum(kt.viewslot2)),
                 bool(sum(kt.viewslot3)), bool(sum(kt.viewslot4)),
                 bool(sum(kt.viewslot5)), bool(sum(kt.viewslot6))]

        current = int(kt.viewcycle)

        if any(slots):

            available = []
            next_slot = None

            for i, slot in enumerate(slots):
                if slot:
                    available.append(i)
                    if i > current:
                        next_slot = i
                        break

            if next_slot is None and available:
                next_slot = available[0]

            if next_slot is not None:
                kt.viewcycle = next_slot
                bpy.ops.view3d.ke_view_bookmark(mode="USE" + str(next_slot + 1))

        return {"FINISHED"}
