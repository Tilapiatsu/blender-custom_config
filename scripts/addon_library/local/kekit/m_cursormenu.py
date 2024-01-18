from math import radians, copysign

import bpy
from bpy.props import EnumProperty
from bpy.types import Header, Panel, Operator
from mathutils import Vector, Matrix, Quaternion
from ._utils import rotation_from_vector, get_prefs


class KeCursorMenuHeader(Header):
    bl_idname = "VIEW3D_HT_KCM"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'
    bl_label = "keKit Cursor Menu"

    def draw(self, context):
        layout = self.layout
        layout.popover(panel="VIEW3D_PT_KCM", icon="CURSOR", text="")


class KeCursorMenuPanel(Panel):
    bl_idname = "VIEW3D_PT_KCM"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'
    bl_label = "KCM"

    def draw(self, context):
        k = get_prefs()
        xp = k.experimental
        bookmarks = bool(k.m_bookmarks)
        temp = context.scene.kekit_temp
        layout = self.layout
        c = layout.column()

        c.operator("view3d.ke_cursor_rotation", text="Align Cursor To View").mode = "VIEW"

        c.label(text="Step Rotate")
        col = c.column(align=True)
        row = col.row(align=True)
        row.prop(temp, "kcm_axis", expand=True)

        row = col.row(align=True)
        row.prop(temp, "kcm_rot_preset", expand=True)

        # flagged as "experimental"  due to "unsupported RNA type 2" error-spam, solution TBD
        row = col.row(align=True)
        if xp:
            row.prop(temp, "kcm_custom_rot")

        row = col.row(align=True)
        row.operator("view3d.ke_cursor_rotation", text="Step Rotate").mode = "STEP"

        if xp:
            c.label(text="Target Object")
            c.prop_search(context.scene, "kekit_cursor_obj", bpy.data, "objects", text="")
        row = c.row(align=True)
        row.operator("view3d.ke_cursor_rotation", text="Point To Obj").mode = "OBJECT"
        row.operator("view3d.ke_cursor_rotation", text="Copy Obj Rot").mode = "MATCH"

        c.label(text="Snap Cursor To")
        col = c.column(align=True)
        row = col.row(align=True)
        row.operator("view3d.snap_cursor_to_selected", text="Sel.")
        row.operator("view3d.snap_cursor_to_active", text="Active")
        row.operator("view3d.snap_cursor_to_grid", text="Grid")
        row.operator("view3d.ke_cursor_ortho_snap", text="Ortho")

        if bookmarks:
            c.label(text="Cursor Bookmarks")
            row = c.grid_flow(row_major=True, columns=6, align=True)
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET1"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET2"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET3"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET4"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET5"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET6"

            if sum(temp.cursorslot1) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="1", depress=False).mode = "USE1"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="1", depress=True).mode = "USE1"
            if sum(temp.cursorslot2) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="2", depress=False).mode = "USE2"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="2", depress=True).mode = "USE2"
            if sum(temp.cursorslot3) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="3", depress=False).mode = "USE3"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="3", depress=True).mode = "USE3"
            if sum(temp.cursorslot4) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="4", depress=False).mode = "USE4"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="4", depress=True).mode = "USE4"
            if sum(temp.cursorslot5) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="5", depress=False).mode = "USE5"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="5", depress=True).mode = "USE5"
            if sum(temp.cursorslot6) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="6", depress=False).mode = "USE6"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="6", depress=True).mode = "USE6"

        if xp:
            # flagged as "experimental" due to "unsupported RNA type 2" error-spam, solution TBD
            cf = c.column_flow(columns=2, align=True)
            cf.prop(context.scene.cursor, "location", text="Cursor Location", expand=True)
            cf.operator("view3d.snap_cursor_to_center", text="Clear Loc")
            cf.prop(context.scene.cursor, "rotation_euler", text="Cursor Rotation", expand=True)
            cf.operator("view3d.ke_cursor_clear_rot", text="Clear Rot")
        else:
            c.separator(factor=1)
            row = c.row(align=True)
            row.operator("view3d.snap_cursor_to_center", text="Clear Loc")
            row.operator("view3d.ke_cursor_clear_rot", text="Clear Rot")

        c.operator("view3d.snap_cursor_to_center", text="Reset Cursor")


class KeCursorRotation(Operator):
    bl_idname = "view3d.ke_cursor_rotation"
    bl_label = "Cursor Rotation"
    bl_options = {'REGISTER'}

    mode: EnumProperty(items=[
        ("STEP", "Step Rotate", "", 1),
        ("VIEW", "Align To View", "", 2),
        ("OBJECT", "Point To Object", "", 3),
        ("MATCH", "Match Object Rot", "", 4)],
        name="Mode", default="STEP", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "STEP":
            return "Rotate the cursor along chosen AXIS with either PRESET -or- CUSTOM degrees"
        elif properties.mode == "VIEW":
            return "Aligns the cursor Z axis to the view camera"
        elif properties.mode == "OBJECT":
            return "Rotate the cursor Z towards chosen object"
        else:
            return "Cursor uses chosen object's rotation"

    def execute(self, context):
        obj = bpy.data.objects.get(context.scene.kekit_cursor_obj)
        if not obj:
            obj = context.object
        cursor = context.scene.cursor
        qc = context.scene.cursor.matrix

        if self.mode == "VIEW":
            rv3d = context.space_data.region_3d
            cursor.rotation_euler = rv3d.view_rotation.to_euler()

        elif self.mode == "OBJECT":
            if obj:
                v = Vector(obj.location - cursor.location).normalized()
                if round(abs(v.dot(Vector((1, 0, 0)))), 3) == 1:
                    u = Vector((0, 0, 1))
                else:
                    u = Vector((-1, 0, 0))
                t = v.cross(u).normalized()
                rot_mtx = rotation_from_vector(v, t, rw=False)
                cursor.rotation_euler = rot_mtx.to_euler()
            else:
                self.report({"INFO"}, "No Object Selected")

        elif self.mode == "MATCH":
            if obj:
                cursor.rotation_euler = obj.rotation_euler
            else:
                self.report({"INFO"}, "No Object Selected")

        elif self.mode == "STEP":
            axis = context.scene.kekit_temp.kcm_axis
            custom_rot = context.scene.kekit_temp.kcm_custom_rot
            preset_rot = context.scene.kekit_temp.kcm_rot_preset
            if custom_rot != 0:
                rval = custom_rot
            else:
                rval = radians(int(preset_rot))
            rot_mtx = qc @ Matrix.Rotation(rval, 4, axis)
            cursor.rotation_euler = rot_mtx.to_euler()

        return {"FINISHED"}


class KeCursorOrthoSnap(Operator):
    bl_idname = "view3d.ke_cursor_ortho_snap"
    bl_label = "Cursor Otho Snap"
    bl_description = "Snap-Aligns the Cursor Z-axis to the nearest world (ortho) axis, relative to the viewport camera"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        # 90 Degree Value (for quat)
        ndv = 0.7071068286895752
        cursor = context.scene.cursor
        og_mode = str(cursor.rotation_mode)
        rm = context.space_data.region_3d.view_matrix
        v = Vector(rm[2])
        x, y, z = abs(v.x), abs(v.y), abs(v.z)

        if x > y and x > z:
            axis = copysign(1, v.x), 0, 0
        elif y > x and y > z:
            axis = 0, copysign(1, v.y), 0
        else:
            axis = 0, 0, copysign(1, v.z)

        if sum(axis) < 0:
            if bool(axis[2]):
                q = Quaternion((-0.0, ndv, ndv, 0.0))
            elif bool(axis[1]):
                q = Quaternion((ndv, ndv, 0.0, 0.0))
            else:
                q = Quaternion((ndv, 0.0, -ndv, 0.0))
        else:
            if bool(axis[2]):
                q = Quaternion((ndv, 0.0, 0.0, -ndv))
            elif bool(axis[1]):
                q = Quaternion((ndv, -ndv, 0.0, 0.0))
            else:
                q = Quaternion((ndv, 0.0, ndv, 0.0))

        cursor.rotation_mode = "QUATERNION"
        cursor.rotation_quaternion = q
        cursor.rotation_mode = og_mode

        return {'FINISHED'}


classes = (
    KeCursorMenuHeader,
    KeCursorMenuPanel,
    KeCursorRotation,
    KeCursorOrthoSnap,
)


def register():
    k = get_prefs()
    if k.m_selection:
        for c in classes:
            bpy.utils.register_class(c)

        if k.kcm:
            bpy.types.VIEW3D_MT_editor_menus.append(KeCursorMenuHeader.draw)


def unregister():
    if "bl_rna" in KeCursorMenuHeader.__dict__:
        bpy.types.VIEW3D_MT_editor_menus.remove(KeCursorMenuHeader.draw)

        for c in reversed(classes):
            bpy.utils.unregister_class(c)
