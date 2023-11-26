from bpy.props import EnumProperty, FloatVectorProperty
from bpy.types import Operator


class KeCursorBookmarks(Operator):
    bl_idname = "view3d.ke_cursor_bookmark"
    bl_label = "Cursor Bookmarks"
    bl_description = "Store & Use Cursor Transforms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    mode : EnumProperty(
        items=[("SET1", "Set Cursor Slot 1", "", 1),
               ("SET2", "Set Cursor Slot 2", "", 2),
               ("SET3", "Set Cursor Slot 3", "", 3),
               ("SET4", "Set Cursor Slot 4", "", 4),
               ("SET5", "Set Cursor Slot 5", "", 5),
               ("SET6", "Set Cursor Slot 6", "", 6),
               ("USE1", "Use Cursor Slot 1", "", 7),
               ("USE2", "Use Cursor Slot 2", "", 8),
               ("USE3", "Use Cursor Slot 3", "", 9),
               ("USE4", "Use Cursor Slot 4", "", 10),
               ("USE5", "Use Cursor Slot 5", "", 11),
               ("USE6", "Use Cursor Slot 6", "", 12)
               ],
        name="Cursor Bookmarks",
        options={'HIDDEN'},
        default="SET1")

    val : FloatVectorProperty(size=6, options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        if properties.mode in {"SET1", "SET2", "SET3", "SET4", "SET5", "SET6"}:
            return "Store Cursor Transform in slot " + properties.mode[-1]
        else:
            return "Recall Cursor Transform from slot " + properties.mode[-1]

    def execute(self, context):
        kt = context.scene.kekit_temp
        c = context.scene.cursor
        if c.rotation_mode == "QUATERNION" or c.rotation_mode == "AXIS_ANGLE":
            self.report({"INFO"}, "Cursor Mode is not Euler: Not supported - Aborted.")

        if "SET" in self.mode:
            op = "SET"
        else:
            op = "USE"

        nr = int(self.mode[-1])
        if nr == 1:
            slot = kt.cursorslot1
        elif nr == 2:
            slot = kt.cursorslot2
        elif nr == 3:
            slot = kt.cursorslot3
        elif nr == 4:
            slot = kt.cursorslot4
        elif nr == 5:
            slot = kt.cursorslot5
        elif nr == 6:
            slot = kt.cursorslot6

        if op == "SET":
            self.val = c.location[0], c.location[1], c.location[2], c.rotation_euler[0], c.rotation_euler[1], \
                       c.rotation_euler[2]
            slot[0] = self.val[0]
            slot[1] = self.val[1]
            slot[2] = self.val[2]
            slot[3] = self.val[3]
            slot[4] = self.val[4]
            slot[5] = self.val[5]

        elif op == "USE":
            self.val[0] = slot[0]
            self.val[1] = slot[1]
            self.val[2] = slot[2]
            self.val[3] = slot[3]
            self.val[4] = slot[4]
            self.val[5] = slot[5]

            c.location = self.val[0], self.val[1], self.val[2]
            c.rotation_euler = self.val[3], self.val[4], self.val[5]

        return {"FINISHED"}
