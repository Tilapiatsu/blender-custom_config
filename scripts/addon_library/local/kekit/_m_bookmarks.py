import bpy
from bpy.types import Panel, Operator
from bpy.props import EnumProperty, StringProperty, FloatVectorProperty, IntProperty
from mathutils import Vector, Quaternion
from ._prefs import pcoll


#
# MODULE UI
#
class UIBookmarksModule(Panel):
    bl_idname = "UI_PT_M_BOOKMARKS"
    bl_label = "Bookmarks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_options = {'DEFAULT_CLOSED'}

    info_cursor = "Store & Recall Cursor Transforms (loc & rot)\n" \
                  "Clear Slot: Reset cursor (zero loc & rot) and store\n" \
                  "(Reset Cursor transform = Slot default)"

    info_view = "Store & Recall Viewport Placement (persp/ortho, loc, rot)\n" \
                "Clear Slot: Use & Set a stored view to the same slot\n" \
                "(without moving the viewport camera)"

    def draw(self, context):
        kt = context.scene.kekit_temp

        layout = self.layout
        # CURSOR BOOKMARKS
        row = layout.row(align=True)
        row.label(text="Cursor Bookmarks")
        row.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_cursor

        row = layout.grid_flow(row_major=True, columns=6, align=True)
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET1"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET2"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET3"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET4"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET5"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET6"

        if sum(kt.cursorslot1) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="1", depress=False).mode = "USE1"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="1", depress=True).mode = "USE1"
        if sum(kt.cursorslot2) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="2", depress=False).mode = "USE2"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="2", depress=True).mode = "USE2"
        if sum(kt.cursorslot3) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="3", depress=False).mode = "USE3"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="3", depress=True).mode = "USE3"
        if sum(kt.cursorslot4) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="4", depress=False).mode = "USE4"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="4", depress=True).mode = "USE4"
        if sum(kt.cursorslot5) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="5", depress=False).mode = "USE5"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="5", depress=True).mode = "USE5"
        if sum(kt.cursorslot6) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="6", depress=False).mode = "USE6"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="6", depress=True).mode = "USE6"

        # VIEW BOOKMARKS
        row = layout.row(align=True)
        row.label(text="View Bookmarks")
        row.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_view

        row = layout.grid_flow(row_major=True, columns=6, align=True)
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET1"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET2"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET3"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET4"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET5"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET6"
        if sum(kt.viewslot1) == 0:
            row.operator('view3d.ke_view_bookmark', text="1", depress=False).mode = "USE1"
        else:
            row.operator('view3d.ke_view_bookmark', text="1", depress=True).mode = "USE1"
        if sum(kt.viewslot2) == 0:
            row.operator('view3d.ke_view_bookmark', text="2", depress=False).mode = "USE2"
        else:
            row.operator('view3d.ke_view_bookmark', text="2", depress=True).mode = "USE2"
        if sum(kt.viewslot3) == 0:
            row.operator('view3d.ke_view_bookmark', text="3", depress=False).mode = "USE3"
        else:
            row.operator('view3d.ke_view_bookmark', text="3", depress=True).mode = "USE3"
        if sum(kt.viewslot4) == 0:
            row.operator('view3d.ke_view_bookmark', text="4", depress=False).mode = "USE4"
        else:
            row.operator('view3d.ke_view_bookmark', text="4", depress=True).mode = "USE4"
        if sum(kt.viewslot5) == 0:
            row.operator('view3d.ke_view_bookmark', text="5", depress=False).mode = "USE5"
        else:
            row.operator('view3d.ke_view_bookmark', text="5", depress=True).mode = "USE5"
        if sum(kt.viewslot6) == 0:
            row.operator('view3d.ke_view_bookmark', text="6", depress=False).mode = "USE6"
        else:
            row.operator('view3d.ke_view_bookmark', text="6", depress=True).mode = "USE6"

        sub = layout.row(align=True)
        sub.alignment = "CENTER"
        sub.operator('view3d.ke_viewpos', text="Get").mode = "GET"
        sub.prop(kt, "view_query", text="")
        sub.operator('view3d.ke_viewpos', text="Set").mode = "SET"

        row = layout.row()
        row.operator('view3d.ke_view_bookmark_cycle', text="Cycle View Bookmarks")


class UISnapComboNames(Panel):
    bl_idname = "UI_PT_ke_snapping_combo_names"
    bl_label = "SnapCombo Names"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'UI_PT_M_BOOKMARKS'
    bl_options = {'DEFAULT_CLOSED'}

    info_combos = "Snapping Combos: Store & Restore snapping settings\n" \
                  "Define Snapping Combos in the regular Blender SNAPPING MENU.\n" \
                  "Rename slots here (& set AutoSnap option)"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_combos

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        s1 = pcoll['kekit']['ke_snap1'].icon_id
        s2 = pcoll['kekit']['ke_snap2'].icon_id
        s3 = pcoll['kekit']['ke_snap3'].icon_id
        s4 = pcoll['kekit']['ke_snap4'].icon_id
        s5 = pcoll['kekit']['ke_snap5'].icon_id
        s6 = pcoll['kekit']['ke_snap6'].icon_id
        f = 0.06
        layout = self.layout
        col = layout.column(align=True)
        # row = col.row(align=True)
        # split = row.split(factor=f, align=True)
        # split.label(text="#")
        # split.label(text="  Slot Name")
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="1")
        split.prop(k, "snap_name1", text="", icon_value=s1)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="2")
        split.prop(k, "snap_name2", text="", icon_value=s2)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="3")
        split.prop(k, "snap_name3", text="", icon_value=s3)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="4")
        split.prop(k, "snap_name4", text="", icon_value=s4)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="5")
        split.prop(k, "snap_name5", text="", icon_value=s5)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="6")
        split.prop(k, "snap_name6", text="", icon_value=s6)
        col.prop(k, "combo_autosnap")


class UISnapCombos(Panel):
    bl_idname = "UI_PT_ke_snapping_combos"
    bl_label = "Snapping Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_parent_id = "VIEW3D_PT_snapping"

    def draw(self, context):
        f = 0.6
        s1 = pcoll['kekit']['ke_snap1'].icon_id
        s2 = pcoll['kekit']['ke_snap2'].icon_id
        s3 = pcoll['kekit']['ke_snap3'].icon_id
        s4 = pcoll['kekit']['ke_snap4'].icon_id
        s5 = pcoll['kekit']['ke_snap5'].icon_id
        s6 = pcoll['kekit']['ke_snap6'].icon_id
        layout = self.layout
        row = layout.row(align=True)
        col = row.column_flow(columns=6, align=True)
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="  1")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET1"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s1).mode = "SET1"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="2")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET2"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s2).mode = "SET2"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="3")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET3"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s3).mode = "SET3"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="4")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET4"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s4).mode = "SET4"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="5")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET5"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s5).mode = "SET5"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="6")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET6"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s6).mode = "SET6"


#
# MODULE OPERATORS (MISC)
#
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


class KeViewPos(Operator):
    bl_idname = "view3d.ke_viewpos"
    bl_label = "Get & Set Viewpos"
    bl_description = "Get & Set Viewpos"
    bl_options = {'REGISTER', 'UNDO'}

    mode : EnumProperty(
        items=[("GET", "Get Viewpos", "", "GET", 1),
               ("SET", "Set Viewpos", "", "SET", 2),
               ],
        name="Viewpos", options={"HIDDEN"},
        default="SET")

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "GET":
            return "Get Viewport placement values"
        else:
            return "Set Viewport placement values"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        rv3d = context.space_data.region_3d

        if self.mode == "GET":
            p = [int(rv3d.is_perspective)]
            d = [rv3d.view_distance]
            loc = [i for i in rv3d.view_location]
            rot = [i for i in rv3d.view_rotation]
            v = p + d + loc + rot
            v = str(v)
            context.scene.kekit_temp.view_query = v

        else:
            try:
                q = str(context.scene.kekit_temp.view_query)[1:-1]
                qs = q.split(",")
                v = [float(i) for i in qs]
            except Exception as e:
                print("\n", e, "\n Incorrect values. Aborting.")
                return {'CANCELLED'}

            if len(v) == 9:
                if not rv3d.is_perspective and bool(v[0]):
                    bpy.ops.view3d.view_persportho()
                rv3d.view_distance = v[1]
                rv3d.view_location = Vector(v[2:5])
                rv3d.view_rotation = Quaternion(v[5:9])

        return {'FINISHED'}


def get_snap_settings(context):
    ct = context.scene.tool_settings
    s1 = ""
    for i in ct.snap_elements:
        s1 = s1 + str(i) + ','
    s1 = s1[:-1]
    s2 = str(ct.snap_target)
    s3 = [bool(ct.use_snap_grid_absolute),
          bool(ct.use_snap_backface_culling),
          bool(ct.use_snap_align_rotation),
          bool(ct.use_snap_self),
          bool(ct.use_snap_project),
          bool(ct.use_snap_peel_object),
          bool(ct.use_snap_translate),
          bool(ct.use_snap_rotate),
          bool(ct.use_snap_scale)]
    return s1, s2, s3


def set_snap_settings(context, s1, s2, s3):
    ct = context.scene.tool_settings
    ct.snap_elements = s1
    ct.snap_target = s2
    ct.use_snap_grid_absolute = s3[0]
    ct.use_snap_backface_culling = s3[1]
    ct.use_snap_align_rotation = s3[2]
    ct.use_snap_self = s3[3]
    ct.use_snap_project = s3[4]
    ct.use_snap_peel_object = s3[5]
    ct.use_snap_translate = s3[6]
    ct.use_snap_rotate = s3[7]
    ct.use_snap_scale = s3[8]


class KeSnapCombo(Operator):
    bl_idname = "view3d.ke_snap_combo"
    bl_label = "Snapping Setting Combos"
    bl_description = "Store & Restore snapping settings. (Custom naming in keKit panel)"
    bl_options = {'REGISTER', "UNDO"}

    mode: StringProperty(default="SET1", options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        if "SET" in properties.mode:
            return "Recall stored snapping settings from slot" + properties.mode[-1]
        else:
            return "Store current snapping settings in slot %s" % properties.mode[-1]

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        mode = self.mode[:3]
        slot = int(self.mode[3:])

        if mode == "GET":
            s1, s2, s3 = get_snap_settings(context)
            if slot == 1:
                k.snap_elements1 = s1
                k.snap_targets1 = s2
                k.snap_bools1 = s3
            elif slot == 2:
                k.snap_elements2 = s1
                k.snap_targets2 = s2
                k.snap_bools2 = s3
            elif slot == 3:
                k.snap_elements3 = s1
                k.snap_targets3 = s2
                k.snap_bools3 = s3
            elif slot == 4:
                k.snap_elements4 = s1
                k.snap_targets4 = s2
                k.snap_bools4 = s3
            elif slot == 5:
                k.snap_elements5 = s1
                k.snap_targets5 = s2
                k.snap_bools5 = s3
            elif slot == 6:
                k.snap_elements6 = s1
                k.snap_targets6 = s2
                k.snap_bools6 = s3

        elif mode == "SET":
            if slot == 1:
                c = k.snap_elements1
                s1 = set(c.split(","))
                s2 = k.snap_targets1
                s3 = k.snap_bools1
            elif slot == 2:
                c = k.snap_elements2
                s1 = set(c.split(","))
                s2 = k.snap_targets2
                s3 = k.snap_bools2
            elif slot == 3:
                c = k.snap_elements3
                s1 = set(c.split(","))
                s2 = k.snap_targets3
                s3 = k.snap_bools3
            elif slot == 4:
                c = k.snap_elements4
                s1 = set(c.split(","))
                s2 = k.snap_targets4
                s3 = k.snap_bools4
            elif slot == 5:
                c = k.snap_elements5
                s1 = set(c.split(","))
                s2 = k.snap_targets5
                s3 = k.snap_bools5
            elif slot == 6:
                c = k.snap_elements6
                s1 = set(c.split(","))
                s2 = k.snap_targets6
                s3 = k.snap_bools6

            set_snap_settings(context, s1, s2, s3)

            if k.combo_autosnap:
                context.scene.tool_settings.use_snap = True

        return {'FINISHED'}


#
# O & P
#
class UIOpcModule(Panel):
    bl_idname = "UI_PT_M_OPC"
    bl_label = "O&P Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'UI_PT_M_BOOKMARKS'
    bl_options = {'DEFAULT_CLOSED'}

    info_combos = "Orientation & Pivot Combos:\n" \
                  "Store & Restore O&P combinations for both Object & Edit Mode in hotkeyable slots"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_combos

    def draw(self, context):
        layout = self.layout


class UIopc1(Panel):
    bl_idname = "UI_PT_OPC1"
    bl_label = "OPC 1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        name = k.opc1_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc1_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc1'].icon_id, text="%s" % name).combo = "1"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC1 Object Mode")
        col.prop(k, 'opc1_obj_o')
        col.prop(k, 'opc1_obj_p')
        col.label(text="OPC1 Edit Mode")
        col.prop(k, 'opc1_edit_o')
        col.prop(k, 'opc1_edit_p')


class UIopc2(Panel):
    bl_idname = "UI_PT_OPC2"
    bl_label = "OPC 2"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        name = k.opc2_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc2_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc2'].icon_id, text="%s" % name).combo = "2"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC2 Object Mode")
        col.prop(k, 'opc2_obj_o')
        col.prop(k, 'opc2_obj_p')
        col.label(text="OPC2 Edit Mode")
        col.prop(k, 'opc2_edit_o')
        col.prop(k, 'opc2_edit_p')


class UIopc3(Panel):
    bl_idname = "UI_PT_OPC3"
    bl_label = "OPC 3"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        name = k.opc3_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc3_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc3'].icon_id, text="%s" % name).combo = "3"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC3 Object Mode")
        col.prop(k, 'opc3_obj_o')
        col.prop(k, 'opc3_obj_p')
        col.label(text="OPC3 Edit Mode")
        col.prop(k, 'opc3_edit_o')
        col.prop(k, 'opc3_edit_p')


class UIopc4(Panel):
    bl_idname = "UI_PT_OPC4"
    bl_label = "OPC 4"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        name = k.opc4_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc4_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc4'].icon_id, text="%s" % name).combo = "4"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC4 Object Mode")
        col.prop(k, 'opc4_obj_o')
        col.prop(k, 'opc4_obj_p')
        col.label(text="OPC4 Edit Mode")
        col.prop(k, 'opc4_edit_o')
        col.prop(k, 'opc4_edit_p')


class UIopc5(Panel):
    bl_idname = "UI_PT_OPC5"
    bl_label = "OPC 5"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        name = k.opc5_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc5_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc5'].icon_id, text="%s" % name).combo = "5"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC5 Object Mode")
        col.prop(k, 'opc5_obj_o')
        col.prop(k, 'opc5_obj_p')
        col.label(text="OPC5 Edit Mode")
        col.prop(k, 'opc5_edit_o')
        col.prop(k, 'opc5_edit_p')


class UIopc6(Panel):
    bl_idname = "UI_PT_OPC6"
    bl_label = "OPC 6"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        name = k.opc6_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc6_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc6'].icon_id, text="%s" % name).combo = "6"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC6 Object Mode")
        col.prop(k, 'opc6_obj_o')
        col.prop(k, 'opc6_obj_p')
        col.label(text="OPC6 Edit Mode")
        col.prop(k, 'opc6_edit_o')
        col.prop(k, 'opc6_edit_p')


#
# MODULE OPERATORS (MISC)
#
class KeOPC(Operator):
    bl_idname = "view3d.ke_opc"
    bl_label = "Orientation and Pivot Combo"
    bl_description = "Orientation and Pivot Combo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    combo: EnumProperty(
        items=[("1", "OPC1", "", 1),
               ("2", "OPC2", "", 2),
               ("3", "OPC3", "", 3),
               ("4", "OPC4", "", 4),
               ("5", "OPC5", "", 5),
               ("6", "OPC6", "", 6)],
        name="Combo",
        default="1")

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        ctx_mode = context.mode
        orientation = "GLOBAL"
        pivot = "MEDIAN_POINT"

        if ctx_mode == "OBJECT":
            if self.combo == "1":
                orientation = k.opc1_obj_o
                pivot = k.opc1_obj_p
            elif self.combo == "2":
                orientation = k.opc2_obj_o
                pivot = k.opc2_obj_p
            elif self.combo == "3":
                orientation = k.opc3_obj_o
                pivot = k.opc3_obj_p
            elif self.combo == "4":
                orientation = k.opc4_obj_o
                pivot = k.opc4_obj_p
            elif self.combo == "5":
                orientation = k.opc5_obj_o
                pivot = k.opc5_obj_p
            elif self.combo == "6":
                orientation = k.opc6_obj_o
                pivot = k.opc6_obj_p

        else:
            if self.combo == "1":
                orientation = k.opc1_edit_o
                pivot = k.opc1_edit_p
            elif self.combo == "2":
                orientation = k.opc2_edit_o
                pivot = k.opc2_edit_p
            elif self.combo == "3":
                orientation = k.opc3_edit_o
                pivot = k.opc3_edit_p
            elif self.combo == "4":
                orientation = k.opc4_edit_o
                pivot = k.opc4_edit_p
            elif self.combo == "5":
                orientation = k.opc5_edit_o
                pivot = k.opc5_edit_p
            elif self.combo == "6":
                orientation = k.opc6_edit_o
                pivot = k.opc6_edit_p

        bpy.ops.transform.select_orientation(orientation=orientation)
        context.tool_settings.transform_pivot_point = pivot
        return {'FINISHED'}


#
# MODULE REGISTRATION
#
classes = (
    UIBookmarksModule,
    KeCursorBookmarks,
    KeViewBookmark,
    KeViewBookmarkCycle,
    KeViewPos,
    KeSnapCombo,
    UISnapCombos,
    UISnapComboNames,
    KeOPC,
    UIOpcModule,
    UIopc1,
    UIopc2,
    UIopc3,
    UIopc4,
    UIopc5,
    UIopc6,
)

modules = ()


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_bookmarks:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():

    if "bl_rna" in UIBookmarksModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
