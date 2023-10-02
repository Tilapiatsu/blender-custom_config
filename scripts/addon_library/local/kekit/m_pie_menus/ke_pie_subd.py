from bpy.types import Menu
from .._utils import get_prefs, is_registered


class KePieSubd(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_subd"
    bl_label = "keSubd"

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.active_object)

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        k = get_prefs()

        if k.experimental:
            # Check existing modifiers
            bevel_mods = []
            mirror_mods = []
            solidify_mods = []
            subd_mods = []
            wn_mods = []
            vgicon = "GROUP_VERTEX"

            cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
            active = context.active_object

            if active and active.type in cat:
                for m in active.modifiers:
                    if m.type == "BEVEL":
                        bevel_mods.append(m)
                    elif m.type == "MIRROR":
                        mirror_mods.append(m)
                    elif m.type == "SOLIDIFY":
                        solidify_mods.append(m)
                    elif m.type == "SUBSURF":
                        subd_mods.append(m)
                    elif m.type == "WEIGHTED_NORMAL":
                        wn_mods.append(m)

            vertex_groups = [i for i in active.vertex_groups if i.name[:3] == "V_G"]

            # Bevel Weights
            pie.operator("ke.pieops", text="Bevel Weight -1").op = "BWEIGHTS_OFF"
            pie.operator("ke.pieops", text="Bevel Weight 1").op = "BWEIGHTS_ON"

            # MAIN BOX
            vg = pie.column()
            vg.ui_units_x = 24.5

            # VERTEX GROUPS ASSIGNMENT
            if vertex_groups:
                box = vg.box()
                row = box.row(align=True)
                split = row.split(factor=1, align=True)
                split.operator("ke.pieops", text="Clear").op = "CLEAR_VG"
                row.separator(factor=1)

                n = vertex_groups[0].name
                row.operator("ke.pieops", text=n, icon=vgicon).op = "ADD_VG¤" + n

                if len(vertex_groups) > 1:
                    for group in vertex_groups[1:]:
                        gn = group.name[-3:]
                        row.operator("ke.pieops", text=gn, icon=vgicon).op = "ADD_VG¤" + group.name

                row.separator(factor=1)
                row.operator("ke.pieops", text="New").op = "ADD_VG"
            else:
                row = vg.row()
                split = row.split()
                split.separator(factor=1)
                split.operator("ke.pieops", text="New Bevel VGroup", icon=vgicon).op = "ADD_VG"
                split.separator(factor=1)

            vg.separator()
            main = vg.row(align=True)
            main.alignment = "LEFT"

            # MIRROR & LATTICE
            c = main.column(align=False)
            c.ui_units_x = 9
            c.scale_y = 0.9

            if mirror_mods:
                for m in mirror_mods:
                    col = c.box().column()
                    menu = col.row(align=True)
                    menu.label(text=m.name, icon="MOD_MIRROR")
                    menu.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    menu.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)
                    col.separator(factor=0.5)
                    col.scale_y = 0.8
                    sub = col.row(align=True)
                    sub.label(text="Mirror XYZ")
                    sub.prop(m, "use_axis", icon_only=True)
                    sub = col.row(align=True)
                    sub.label(text="Bisect XYZ")
                    sub.prop(m, "use_bisect_axis", icon_only=True)
                    sub = col.row(align=True)
                    sub.label(text="Flip XYZ")
                    sub.prop(m, "use_bisect_flip_axis", icon_only=True)
                    col.separator(factor=0.5)
                    sub = col.row(align=True)
                    sub.label(text="Use World Origo")
                    mop = sub.operator("ke.pieops", text="", icon="ORIENTATION_GLOBAL")
                    mop.op = "MIRROR_W"
                    mop.mname = m.name
                    xmop = sub.operator("ke.pieops", text="", icon="X")
                    xmop.op = "REM_MIRROR_W"
                    xmop.mname = m.name
                    c.separator(factor=0.7)
            else:
                sub = c.box().column(align=True)
                c.scale_y = 1.0
                sub.label(text="Add Mirror [+Bisect]", icon="MOD_MIRROR")
                row = sub.row(align=True)
                row.operator("ke.pieops", text="X").op = "MIRROR_X"
                row.operator("ke.pieops", text="", icon="EVENT_B").op = "SYM_X"
                row.separator(factor=0.3)
                row.operator("ke.pieops", text="Y").op = "MIRROR_Y"
                row.operator("ke.pieops", text="", icon="EVENT_B").op = "SYM_Y"
                row.separator(factor=0.3)
                row.operator("ke.pieops", text="Z").op = "MIRROR_Z"
                row.operator("ke.pieops", text="", icon="EVENT_B").op = "SYM_Z"
                c.separator(factor=0.7)

            # VG Selection & Removal
            if vertex_groups:
                col = c.box().column()
                for group in vertex_groups:
                    gn = group.name[-3:]
                    row = col.row(align=True)
                    split = row.split(factor=0.4)
                    split.label(text=gn, icon=vgicon)
                    sub = split.row(align=True)
                    sub.operator("ke.pieops", text="", icon="ADD").op = "OPVG¤SEL¤" + gn
                    sub.operator("ke.pieops", text="", icon="REMOVE").op = "OPVG¤DSEL¤" + gn
                    sub.operator("ke.pieops", text="", icon="LOOP_BACK").op = "OPVG¤REM¤" + gn
                    sub.operator("ke.pieops", text="", icon="PANEL_CLOSE").op = "OPVG¤DEL¤" + gn

            # MAIN BOX MENU
            main.separator(factor=1)
            c = main.column(align=True)
            c.ui_units_x = 8

            if subd_mods:
                for m in subd_mods:
                    s = c.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_SUBSURF")
                    s.separator(factor=0.3)
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)
                    s.separator(factor=0.5)
                    s.prop(m, "uv_smooth", text="")
                    s.prop(m, "boundary_smooth", text="")
                    sub = s.row(align=True)
                    sub.prop(m, "use_creases", text="Crease", toggle=True)
                    sub.prop(m, "show_on_cage", text="OnCage", toggle=True)
                    c.separator(factor=0.5)
            else:
                s = c.box().column()
                if is_registered("VIEW3D_OT_ke_subd"):
                    s.operator('view3d.ke_subd', text="SubD Toggle").level_mode = "TOGGLE"
                else:
                    s.enabled = False
                    s.label(text="Subd Toggle N/A")

                c.separator(factor=0.7)

            if solidify_mods:
                for m in solidify_mods:
                    s = c.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_SOLIDIFY")
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)
                    s.separator(factor=0.5)
                    s.prop(m, "thickness", text="Thickness")
                    s.prop(m, "offset", text="Offset")
                    c.separator(factor=0.7)
                    row = s.row(align=True)
                    row.prop(m, "use_even_offset", text="Even", toggle=False)
                    row.prop(m, "use_rim", text="Rim", toggle=False)
                    row.prop(m, "use_rim_only", text="Only Rim", toggle=False)
            else:
                c.separator(factor=0.7)
                c.operator("ke.pieops", text="Add Solidify").op = "SOLIDIFY"

            c.separator(factor=0.7)

            if wn_mods:
                for m in wn_mods:
                    s = c.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_NORMALEDIT")
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)
                    s.separator(factor=0.5)
                    s.prop(m, "mode", text="")
                    s.prop(m, "thresh")
                    c.separator(factor=0.7)
                    row = s.row(align=True)
                    row.prop(m, "keep_sharp", toggle=False)
                    row.prop(m, "use_face_influence", toggle=False)
            else:
                c.separator(factor=0.7)
                c.operator("ke.pieops", text="Add Weighted Normal").op = "WEIGHTED_NORMAL"

            # BEVEL MODS
            main.separator(factor=1)
            b = main.column(align=True)
            b.ui_units_x = 9
            b.scale_y = 0.9

            if bevel_mods:
                bevm = [m for m in bevel_mods if m.limit_method == "WEIGHT"]
                for m in bevm:
                    s = b.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_BEVEL")
                    s.separator(factor=0.5)
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)

                    split = s.split(factor=0.65, align=True)
                    row = split.row(align=True)
                    row.prop_menu_enum(m, "offset_type", text="", icon="DOT")
                    row.prop(m, "width", text="")
                    split.prop(m, "segments", text="")

                    row = s.row(align=True)
                    row.prop(m, "use_clamp_overlap", text="", toggle=False)
                    row.separator(factor=0.3)
                    row.prop(m, "profile")

                    s.separator(factor=0.3)
                    row = s.row(align=True)
                    row.prop(m, "miter_outer", text="")
                    row.prop(m, "miter_inner", text="")
                    b.separator(factor=0.7)

                if not bevm:
                    b.operator("ke.pieops", text="Add Weight Bevel", icon="MOD_BEVEL").op = "W_BEVEL"
                    b.separator(factor=0.7)
            else:
                b.operator("ke.pieops", text="Add Weight Bevel", icon="MOD_BEVEL").op = "W_BEVEL"
                b.separator(factor=0.7)

            b.separator(factor=0.7)
            if bevel_mods:
                bevm = [m for m in bevel_mods if m.limit_method == "ANGLE"]
                for m in bevm:
                    s = b.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_BEVEL")
                    s.separator(factor=0.5)
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)

                    split = s.split(factor=0.65, align=True)
                    row = split.row(align=True)
                    row.prop_menu_enum(m, "offset_type", text="", icon="DOT")
                    row.prop(m, "width", text="")
                    split.prop(m, "segments", text="")

                    row = s.row(align=True)
                    row.prop(m, "use_clamp_overlap", text="", toggle=False)
                    row.separator(factor=0.3)
                    row.prop(m, "profile", text="")
                    row.prop(m, "angle_limit", text="")

                    s.separator(factor=0.3)
                    row = s.row(align=True)
                    row.prop(m, "miter_outer", text="")
                    row.prop(m, "miter_inner", text="")
                    b.separator(factor=0.7)

                if not bevm:
                    b.operator("ke.pieops", text="Add Angle Bevel", icon="MOD_BEVEL").op = "ANGLE_BEVEL"
                    b.separator(factor=0.7)
            else:
                b.operator("ke.pieops", text="Add Angle Bevel", icon="MOD_BEVEL").op = "ANGLE_BEVEL"
                b.separator(factor=0.7)

            if vertex_groups:
                used = []

                if bevel_mods:
                    bevm = [m for m in bevel_mods if m.limit_method == "VGROUP"]
                    for m in bevm:
                        s = b.box().column(align=True)
                        sub = s.row(align=True)
                        sub.label(text=m.name, icon="MOD_BEVEL")
                        s.separator(factor=0.5)
                        sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                        sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)

                        split = s.split(factor=0.65, align=True)
                        row = split.row(align=True)
                        row.prop_menu_enum(m, "offset_type", text="", icon="DOT")
                        row.prop(m, "width", text="")
                        split.prop(m, "segments", text="")

                        row = s.row(align=True)
                        row.prop(m, "use_clamp_overlap", text="", toggle=False)
                        row.prop(m, "profile")

                        s.separator(factor=0.3)
                        row = s.row(align=True)
                        row.prop(m, "miter_outer", text="")
                        row.prop(m, "miter_inner", text="")
                        b.separator(factor=0.7)
                        used.append(m.name)

                for group in vertex_groups:
                    n = group.name
                    if n[:3] == "V_G" and n not in used:
                        b.operator("ke.pieops", text="Add " + group.name + " Bevel",
                                   icon="MOD_BEVEL").op = "VG_BEVEL¤" + n
                        b.separator(factor=0.7)

            # TOP
            m = pie.column(align=True)
            m.ui_units_x = 7.5
            top = m.box().column(align=True)
            row = top.row(align=True)
            row.operator("ke.pieops", text="S", icon="EDITMODE_HLT").op = "SUBD_EDIT_VIS"
            row.operator("ke.pieops", text="E", icon="EDITMODE_HLT").op = "MOD_EDIT_VIS"
            row.operator("ke.pieops", text="V", icon="RESTRICT_VIEW_OFF").op = "MOD_VIS"
            top.separator(factor=0.3)
            top.prop(k, "korean", text="Korean Bevels")
            row = top.row(align=True)
            row.operator("ke.pieops", text="Flat").op = "SHADE_FLAT"
            row.operator("ke.pieops", text="Smooth").op = "SHADE_SMOOTH"

            split = top.split(align=True, factor=0.65)
            split.prop(active.data, "use_auto_smooth", text="AutoSmth", toggle=True)
            split.prop(active.data, "auto_smooth_angle", text="")

            row = top.row(align=True)
            row.operator("object.ke_object_op", text="30").cmd = "AS_30"
            row.operator("object.ke_object_op", text="45").cmd = "AS_45"
            row.operator("object.ke_object_op", text="60").cmd = "AS_60"
            row.operator("object.ke_object_op", text="180").cmd = "AS_180"
            top.separator(factor=0.3)

            row = top.row(align=True)
            if is_registered("VIEW3D_OT_ke_solo_cutter"):
                row.operator('view3d.ke_solo_cutter', text="SoloC").mode = "ALL"
                row.operator('view3d.ke_solo_cutter', text="SoloP").mode = "PRE"
            if is_registered("OBJECT_OT_ke_showcuttermod"):
                row.operator('object.ke_showcuttermod', text="SCM")

            spacer = m.column()
            spacer.label(text="")

            # Crease
            pie.operator("ke.pieops", text="Crease Weight -1").op = "CREASE_OFF"
            pie.operator("ke.pieops", text="Crease Weight 1").op = "CREASE_ON"

            # blanking SW & SE
            # pie.separator()
            # pie.separator()
        else:
            pie.separator()
            pie.separator()
            box = pie.box()
            box.label(text="[ Disabled: Requires keKit Experimental Mode ]")
