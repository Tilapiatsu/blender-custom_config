from bpy.types import Menu
from .._utils import get_prefs


class KePieStepRotate(Menu):
    bl_label = "keVPStepRotate"
    bl_idname = "VIEW3D_MT_ke_pie_step_rotate"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_selection

    def draw(self, context):
        k = get_prefs()
        xp = k.experimental
        op = "view3d.ke_vp_step_rotate"
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator(op, text="-90", icon="LOOP_BACK").rot = -90
        pie.operator(op, text="90", icon="LOOP_FORWARDS").rot = 90

        s = pie.column()
        s.separator(factor=2.5)
        s.scale_x = 0.85
        row = s.row(align=True)
        # row.scale_x = 0.5
        # row.scale_y = 1.2
        row.label(text=" ")
        row.label(text=" ")
        row.operator("object.location_clear", text="LOC").clear_delta = False
        row.operator("object.scale_clear", text="SCL").clear_delta = False
        row.operator("object.ke_object_op", text="CLR").cmd = "CLEAR_LR"
        row.label(text=" ")
        row.label(text=" ")

        box = s.box()
        box.scale_y = 1.1
        row = box.row(align=True)
        # Removing due to "unsupported RNA type 2" errors, solution TBD
        split = row
        if xp:
            split = row.split(factor=0.4, align=True)
            row = split.column(align=True)
        row.operator("object.ke_object_op", text="X Clear").cmd = "ROT_CLEAR_X"
        row.operator("object.ke_object_op", text="Y Clear").cmd = "ROT_CLEAR_Y"
        row.operator("object.ke_object_op", text="Z Clear").cmd = "ROT_CLEAR_Z"
        if xp:
            row = split.column(align=True)
            row.prop(context.object, "rotation_euler", text="")

        box = s.column(align=True)
        box.operator("object.ke_straighten", text="Straighten Object", icon="CON_ROTLIMIT").deg = 90

        pie.operator("object.rotation_clear", text="Rotation (Clear)").clear_delta = False
        pie.operator(op, text="-45", icon="LOOP_BACK").rot = -45
        pie.operator(op, text=" 45", icon="LOOP_FORWARDS").rot = 45
        pie.operator(op, text="-180", icon="LOOP_BACK").rot = -180
        pie.operator(op, text=" 180", icon="LOOP_FORWARDS").rot = 180
