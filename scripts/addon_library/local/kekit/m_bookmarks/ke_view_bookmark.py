import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from mathutils import Vector, Quaternion


class KeViewBookmark(Operator):
    bl_idname = "view3d.ke_view_bookmark"
    bl_label = "View Bookmarks"
    bl_description = "Store & Use Viewport Placement (persp/ortho, loc, rot)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    mode : EnumProperty(
        items=[("SET1", "Set Cursor Slot 1", "", "SET1", 1),
               ("SET2", "Set Cursor Slot 2", "", "SET2", 2),
               ("SET3", "Set Cursor Slot 3", "", "SET3", 3),
               ("SET4", "Set Cursor Slot 4", "", "SET4", 4),
               ("SET5", "Set Cursor Slot 5", "", "SET5", 5),
               ("SET6", "Set Cursor Slot 6", "", "SET6", 6),
               ("USE1", "Use Cursor Slot 1", "", "USE1", 7),
               ("USE2", "Use Cursor Slot 2", "", "USE2", 8),
               ("USE3", "Use Cursor Slot 3", "", "USE3", 9),
               ("USE4", "Use Cursor Slot 4", "", "USE4", 10),
               ("USE5", "Use Cursor Slot 5", "", "USE5", 11),
               ("USE6", "Use Cursor Slot 6", "", "USE6", 12)
               ],
        name="View Bookmarks", options={"HIDDEN"},
        default="SET1")

    @classmethod
    def description(cls, context, properties):
        if properties.mode in {"SET1", "SET2", "SET3", "SET4", "SET5", "SET6"}:
            return "Store Viewport placement in slot " + properties.mode[-1]
        else:
            return "Recall Viewport placement from slot " + properties.mode[-1]

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        kt = context.scene.kekit_temp
        rv3d = context.space_data.region_3d
        v = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        nr = int(self.mode[-1])
        if nr == 2:
            slot = kt.viewslot2
        elif nr == 3:
            slot = kt.viewslot3
        elif nr == 4:
            slot = kt.viewslot4
        elif nr == 5:
            slot = kt.viewslot5
        elif nr == 6:
            slot = kt.viewslot6
        else:
            slot = kt.viewslot1

        if "SET" in self.mode:
            p = [int(rv3d.is_perspective)]
            d = [rv3d.view_distance]
            loc = [i for i in rv3d.view_location]
            rot = [i for i in rv3d.view_rotation]
            v = p + d + loc + rot
            if v == list(slot):
                # "Clearing" slot if assigning the same view as stored
                v = [0, 0, 0, 0, 0, 0, 0, 0, 0]

            slot[0] = v[0]
            slot[1] = v[1]
            slot[2] = v[2]
            slot[3] = v[3]
            slot[4] = v[4]
            slot[5] = v[5]
            slot[6] = v[6]
            slot[7] = v[7]
            slot[8] = v[8]
            kt.viewcycle = nr - 1

        else:
            # USE
            v[0] = slot[0]
            v[1] = slot[1]
            v[2] = slot[2]
            v[3] = slot[3]
            v[4] = slot[4]
            v[5] = slot[5]
            v[6] = slot[6]
            v[7] = slot[7]
            v[8] = slot[8]

            if sum(v) != 0:
                kt.viewcycle = nr - 1
                if not rv3d.is_perspective and bool(v[0]):
                    bpy.ops.view3d.view_persportho()
                rv3d.view_distance = v[1]
                rv3d.view_location = Vector(v[2:5])
                rv3d.view_rotation = Quaternion(v[5:9])
            else:
                print("View Bookmark: Empty slot - cancelled")

        return {"FINISHED"}
