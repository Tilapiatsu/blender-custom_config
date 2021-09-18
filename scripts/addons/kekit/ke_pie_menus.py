bl_info = {
    "name": "kePies",
    "author": "Kjell Emanuelsson",
    "version": (0, 2, 1),
    "blender": (2, 8, 0),
    "description": "Custom Pie Menus",
    "category": "3D View",}

import bpy
# import os
from bpy.types import Menu, Operator
from . ke_utils import wempty
from math import ceil
import addon_utils

# -------------------------------------------------------------------------------------------------
# Operators
# -------------------------------------------------------------------------------------------------
class VIEW3D_OT_ke_pieops(Operator):
    bl_idname = "ke.pieops"
    bl_label = "Pie Operators"
    bl_options = {'REGISTER'}

    op :  bpy.props.StringProperty(default="GRID")

    def execute(self, context):
        mode = str(context.mode)
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        active = context.active_object
        if sel_obj:
            sel_obj = [i for i in sel_obj if i != active]

        # ABSOLUTE GRID TOGGLE ---------------------------------------------------------------
        if self.op == "GRID":
            context.tool_settings.use_snap_grid_absolute = not context.tool_settings.use_snap_grid_absolute
            return {'FINISHED'}

        # MISC --------------------------------------------------------------------------------------
        if sel_obj or active:

            if "APPLY" in self.op:
                mod_name = str(self.op).split(".")[1]
                if mode == "EDIT_MESH":
                    bpy.ops.object.mode_set(mode="OBJECT")
                for mod in [m for m in active.modifiers if m.name == mod_name]:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                if mode == "EDIT_MESH":
                    bpy.ops.object.mode_set(mode="EDIT")

            elif "DELETE" in self.op:
                mod_name = str(self.op).split(".")[1]
                for mod in [m for m in active.modifiers if m.name == mod_name]:
                    bpy.ops.object.modifier_remove(modifier=mod.name)

            # BEVEL WEIGHTS ---------------------------------------------------------------
            elif self.op == "BWEIGHTS_ON":
                if mode != "EDIT_MESH":
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.transform.edge_bevelweight(value=1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.transform.edge_bevelweight(value=1)

            elif self.op == "BWEIGHTS_OFF":
                if mode != "EDIT_MESH":
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.transform.edge_bevelweight(value=-1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.transform.edge_bevelweight(value=-1)

            # CREASE ---------------------------------------------------------------
            elif self.op == "CREASE_ON":
                if mode != "EDIT_MESH":
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.transform.edge_crease(value=1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.transform.edge_crease(value=1)

            elif self.op == "CREASE_OFF":
                if mode != "EDIT_MESH":
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.transform.edge_crease(value=-1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.transform.edge_crease(value=-1)

            # MODIFIERS ----------------------------------------------------------
            elif self.op == "SUBD":
                if active:
                    bpy.ops.object.modifier_add(type='SUBSURF')
                    s = active.modifiers[-1]
                    s.name = "SubD"
                    s.levels = 3
                    s.render_levels = 3
                    s.boundary_smooth = 'PRESERVE_CORNERS'

            elif self.op == "W_BEVEL":
                if active:
                    bpy.ops.object.modifier_add(type='BEVEL')
                    b = active.modifiers[-1]
                    b.name = "WBevel"
                    b.width = 0.01
                    b.limit_method = 'WEIGHT'
                    b.segments = 2
                    if context.scene.kekit.korean:
                        b.profile = 1
                    bpy.ops.object.modifier_move_to_index(modifier=b.name, index=0)

            elif self.op == "ANGLE_BEVEL":
                if active:
                    bpy.ops.object.modifier_add(type='BEVEL')
                    b = active.modifiers[-1]
                    b.name = "ABevel"
                    b.width = 0.005
                    b.limit_method = 'ANGLE'
                    b.angle_limit = 1.0472
                    if context.scene.kekit.korean:
                        b.profile = 1
                        b.segments = 2
                    else:
                        b.segments = 3

            elif self.op == "LATTICE":
                print("WIP - Lattice")


            elif self.op == "MOD_VIS":
                bpy.ops.object.toggle_apply_modifiers_view()

            elif self.op in {"MOD_EDIT_VIS", "SUBD_EDIT_VIS"}:
                # hacked from addon tools:avoid toggling not exposed modifiers (currently only Collision, see T53406)
                skip_type = ["COLLISION"]
                limited = []
                if self.op == "SUBD_EDIT_VIS":
                    limited.append("SUBSURF")
                # check if the active object has only one non exposed modifier as the logic will fail
                if len(context.active_object.modifiers) == 1 and \
                        context.active_object.modifiers[0].type in skip_type:

                    for obj in context.selected_objects:
                        for mod in obj.modifiers:
                            if mod.type in skip_type:
                                continue
                            if limited and mod.type in limited:
                                mod.show_in_editmode = not mod.show_in_editmode
                            elif not limited:
                                mod.show_in_editmode = not mod.show_in_editmode
                else:
                    for obj in context.selected_objects:
                        for mod in obj.modifiers:
                            if mod.type in skip_type:
                                continue
                            if limited and mod.type in limited:
                                mod.show_in_editmode = not mod.show_in_editmode
                            elif not limited:
                                mod.show_in_editmode = not mod.show_in_editmode

            # MIRROR ---------------------------------------------------------------
            elif self.op in {"MIRROR_X", "MIRROR_Y", "MIRROR_Z", "MIRROR_W", "REM_MIRROR_W"}:
                if active:
                    if self.op == "MIRROR_W" or self.op =="REM_MIRROR_W":
                        e = wempty(context)
                        m = [m for m in active.modifiers if m.type == "MIRROR"]
                        if m and e:
                            if self.op == "REM_MIRROR_W":
                                m[0].mirror_object = None
                            else:
                                m[0].mirror_object = e
                    else:
                        bpy.ops.object.modifier_add(type='MIRROR')
                        m = active.modifiers[-1]
                        if self.op == "MIRROR_Y":
                            m.use_axis = (False, True, False)
                        elif self.op == "MIRROR_Z":
                            m.use_axis = (False, False, True)

            # SOLIDIFY ---------------------------------------------------------------
            elif self.op == "SOLIDIFY":
                if active:
                    bpy.ops.object.modifier_add(type='SOLIDIFY')
                    m = active.modifiers[-1]
                    m.name = "kSolidify"
                    m.thickness = -0.01

            # SOLIDIFY ---------------------------------------------------------------
            elif self.op == "WEIGHTED_NORMAL":
                if active:
                    context.object.data.use_auto_smooth = True
                    bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')
                    m = active.modifiers[-1]
                    m.name = "kWeightedNormal"

            # SHADING ---------------------------------------------------------------
            elif self.op == "SHADE_SMOOTH":
                if context.object.data.is_editmode:
                    bpy.ops.object.mode_set(mode="OBJECT")
                    bpy.ops.object.shade_smooth()
                    bpy.ops.object.mode_set(mode="EDIT")
                else:
                    bpy.ops.object.shade_smooth()

            elif self.op == "SHADE_FLAT":
                if context.object.data.is_editmode:
                    bpy.ops.object.mode_set(mode="OBJECT")
                    bpy.ops.object.shade_flat()
                    bpy.ops.object.mode_set(mode="EDIT")
                else:
                    bpy.ops.object.shade_flat()

        return {'FINISHED'}


class VIEW3D_OT_ke_snap_target(Operator):
    bl_idname = "ke.snap_target"
    bl_label = "Snap Target"
    bl_options = {'REGISTER', 'UNDO'}

    ke_snaptarget: bpy.props.EnumProperty(
        items=[("CLOSEST", "Closest", "Closest", "", 1),
               ("CENTER", "Center", "Center", "", 2),
               ("MEDIAN", "Median", "Median", "", 3),
               ("CENTER", "Center", "Center", "", 4),
               ("ACTIVE", "Active", "Active", "", 5),
               ("PROJECT", "Project Self", "Project Self", "", 6),
               ("ALIGN", "Align Rotation", "Align Rotation", "", 7)],
        name="Snap Target",
        default="CLOSEST")

    def execute(self, context):
        ct = bpy.context.scene.tool_settings
        if self.ke_snaptarget == 'PROJECT':
            ct.use_snap_self = not ct.use_snap_self
        elif self.ke_snaptarget == 'ALIGN':
            ct.use_snap_align_rotation = not ct.use_snap_align_rotation
        else:
            ct.snap_target = self.ke_snaptarget
        return {'FINISHED'}


class VIEW3D_OT_ke_snap_element(Operator):
    bl_idname = "ke.snap_element"
    bl_label = "Snap Element"
    bl_options = {'REGISTER', 'UNDO'}

    ke_snapelement: bpy.props.EnumProperty(
        items=[("INCREMENT", "Increment", "", "SNAP_INCREMENT", 1),
               ("VERTEX", "Vertex", "", "SNAP_VERTEX", 2),
               ("EDGE", "Edge", "", "SNAP_EDGE", 3),
               ("FACE", "Face", "", "SNAP_FACE", 4),
               ("VOLUME", "Volume", "", "SNAP_VOLUME", 5),
               ("MIX", "Element Mix", "", "SNAP_MIX", 6)],
        name="Snap Element",
        default="INCREMENT")


    def execute(self, context):
        ct = bpy.context.scene.tool_settings
        ct.use_snap = True

        if self.ke_snapelement == "MIX":
            ct.snap_elements = {'VERTEX', 'EDGE', 'EDGE_MIDPOINT', 'FACE'}

        elif self.ke_snapelement == "EDGE":
            ct.snap_elements = {'EDGE', 'EDGE_MIDPOINT'}

        elif self.ke_snapelement == "INCREMENT":
            ct.snap_elements = {'INCREMENT'}
            # ctx_mode = bpy.context.mode
            if not ct.use_snap_grid_absolute:
                ct.use_snap_grid_absolute = True
        else:
            ct.snap_elements = {self.ke_snapelement}

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Custom Pie Menus    Note: COMPASS STYLE REF PIE SLOT POSITIONS:   W, E, S, N, NW, NE, SW, SE
# -------------------------------------------------------------------------------------------------

class VIEW3D_MT_PIE_ke_subd(Menu):
    bl_label = "keSubd"
    bl_idname = "VIEW3D_MT_ke_pie_subd"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        # Check existing modifiers
        bevel_mods = []
        mirror_mods = []
        solidify_mods = []
        subd_mods = []

        # ke Transfer Union Surface Object, ke TransferUnion Reciever Object
        # todo: separate pie setup for TU
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
        active = context.active_object
        if not active:
            active = context.object
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

        layout = self.layout
        pie = layout.menu_pie()

        # Bevel Weights
        pie.operator("ke.pieops", text="Bevel Weight -1").op = "BWEIGHTS_OFF"
        pie.operator("ke.pieops", text="Bevel Weight 1").op = "BWEIGHTS_ON"

        # MAIN BOX ----------------------------------------------------------------------------
        main = pie.row(align=True)
        main.alignment = "LEFT"
        main.ui_units_x = 22

        # MIRROR & LATTICE
        c = main.column(align=False)
        c.ui_units_x = 8
        c.scale_y = 0.9

        if mirror_mods:
            for m in mirror_mods:
                col = c.box().column()
                menu = col.row(align=True)
                menu.label(text=m.name, icon="MOD_MIRROR")
                menu.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY." + str(m.name)
                menu.operator("ke.pieops", text="", icon="X").op = "DELETE." + str(m.name)
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
                sub.operator("ke.pieops", text="", icon="ORIENTATION_GLOBAL").op = "MIRROR_W"
                sub.operator("ke.pieops", text="", icon="X").op = "REM_MIRROR_W"
                c.separator(factor=0.7)

        else:
            sub = c.box().column(align=True)
            c.scale_y = 1.0
            sub.label(text="Add Mirror", icon="MOD_MIRROR")
            row = sub.row(align=True)
            row.operator("ke.pieops", text="X").op = "MIRROR_X"
            row.operator("ke.pieops", text="Y").op = "MIRROR_Y"
            row.operator("ke.pieops", text="Z").op = "MIRROR_Z"
            c.separator(factor=0.7)

        # c.separator(factor=0.1)
        c.operator("ke.pieops", text="Add Lattice (WIP)", icon="MOD_LATTICE").op = "LATTICE"


        # MAIN BOX MENU
        main.separator(factor=1)
        c = main.column(align=True)
        c.ui_units_x = 8
        if subd_mods:
            for m in subd_mods:
                s = c.box().column(align=False)
                sub = s.row(align=True)
                sub.label(text=m.name, icon="MOD_SUBSURF")
                s.separator(factor=0.3)
                sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY." + str(m.name)
                sub.operator("ke.pieops", text="", icon="X").op = "DELETE." + str(m.name)
                # s.prop(m, "levels", text="Viewport Level")
                # s.prop(m, "render_levels", text="Render Level")  # todo: Work around RNA bullshit ;D
                s.prop(m, "boundary_smooth", text="Corners")
                c.separator(factor=0.5)
        else:
            s = c.box().column()
            s.operator('view3d.ke_subd', text="SubD Toggle").level_mode = "TOGGLE"
            # s.operator("ke.pieops", text="Add SUBD", icon="MOD_SUBSURF").op = "SUBD"
            c.separator(factor=0.7)

        if solidify_mods:
            for m in solidify_mods:
                s = c.box().column(align=False)
                sub = s.row(align=True)
                sub.label(text=m.name, icon="MOD_SOLIDIFY")
                sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY." + str(m.name)
                sub.operator("ke.pieops", text="", icon="X").op = "DELETE." + str(m.name)
                s.separator(factor=0.3)
                s.prop(m, "thickness", text="Thickness")
                s.prop(m, "offset", text="Offset")
                c.separator(factor=0.7)
                # s.prop(solidify_mod, "use_rim")
                # s.prop(solidify_mod, "use_rim_only")
        else:
            c.separator(factor=0.7)
            c.operator("ke.pieops", text="Add Solidify").op = "SOLIDIFY"

        # c.label(text="(WIP TU)") # Todo Set TransferUnion
        c.separator(factor=0.7)
        c.operator("ke.pieops", text="Weighted Normal").op = "WEIGHTED_NORMAL"
        # top.label(text="(WIP MT)") # Set MaskTransfer

        # BEVEL
        main.separator(factor=1)
        b = main.column(align=True)
        b.ui_units_x = 8
        b.scale_y = 0.9

        if bevel_mods:
            bevm = [m for m in bevel_mods if m.limit_method == "WEIGHT"]
            for m in bevm:
                s = b.box().column(align=False)
                sub = s.row(align=True)
                sub.label(text=m.name, icon="MOD_BEVEL")
                s.separator(factor=0.3)
                sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY." + str(m.name)
                sub.operator("ke.pieops", text="", icon="X").op = "DELETE." + str(m.name)
                s.prop(m, "width", text="Width")
                s.prop(m, "segments", text="Segments")
                s.prop(m, "profile")
                row = s.row(align=True)
                row.prop(m, "miter_outer", expand=True, toggle=True)
                row = s.row(align=True)
                row.alignment = "RIGHT"
                row.prop(m, "use_clamp_overlap", text="Clamp", toggle=False)
                row.prop_menu_enum(m, "offset_type",text="Type >")
                b.separator(factor=0.7)
            if not bevm:
                b.operator("ke.pieops", text="Add Weight Bevel", icon="MOD_BEVEL").op = "W_BEVEL"
                b.separator(factor=0.7)
        else:
            s = b.box().column()
            b.scale_x = 1
            s.operator("ke.pieops", text="Add Weight Bevel", icon="MOD_BEVEL" ).op = "W_BEVEL"
            b.separator(factor=0.7)

        b.separator(factor=0.7)
        if bevel_mods:
            bevm = [m for m in bevel_mods if m.limit_method == "ANGLE"]
            for m in bevm:
                s = b.box().column(align=False)
                sub = s.row(align=True)
                sub.label(text=m.name, icon="MOD_BEVEL")
                s.separator(factor=0.3)
                sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY." + str(m.name)
                sub.operator("ke.pieops", text="", icon="X").op = "DELETE." + str(m.name)
                s.prop(m, "width", text="Width")
                s.prop(m, "segments", text="Segments")
                s.prop(m, "angle_limit", text="Angle")
                s.prop(m, "profile")
                row = s.row(align=True)
                row.prop(m, "miter_outer", expand=True, toggle=True)
                row = s.row(align=True)
                row.alignment = "RIGHT"
                row.prop(m, "use_clamp_overlap", text="Clamp", toggle=False)
                row.prop_menu_enum(m, "offset_type", text="Type >")
                b.separator(factor=0.7)
            if not bevm:
                b.operator("ke.pieops", text="Add Angle Bevel", icon="MOD_BEVEL").op = "ANGLE_BEVEL"
        else:
            b.operator("ke.pieops", text="Add Angle Bevel", icon="MOD_BEVEL").op = "ANGLE_BEVEL"


        # TOP
        m = pie.column(align=True)
        m.ui_units_x = 7
        top = m.box().column(align=True)
        top.operator("ke.pieops", text="Toggle Subd Edit Vis", icon="EDITMODE_HLT").op = "SUBD_EDIT_VIS"
        top.operator("ke.pieops", text="Toggle All Edit Vis",  icon="EDITMODE_HLT").op = "MOD_EDIT_VIS"
        top.operator("ke.pieops", text="Toggle All Viewp Vis", icon="RESTRICT_VIEW_OFF").op = "MOD_VIS"
        top.separator(factor=0.3)
        top.prop(bpy.context.scene.kekit, "korean", text="Korean Bevels")
        row = top.row(align=True)
        row.operator("ke.pieops", text=" Flat ").op = "SHADE_FLAT"
        row.operator("ke.pieops", text="Smooth").op = "SHADE_SMOOTH"
        spacer = m.column()
        spacer.label(text="")


        # Crease
        pie.operator("ke.pieops", text="Crease Weight -1").op = "CREASE_OFF"
        pie.operator("ke.pieops", text="Crease Weight 1").op = "CREASE_ON"

        # blanking SW & SE
        c = pie.row()
        c.separator()
        c = pie.row()
        c.separator()


class VIEW3D_MT_PIE_ke_fitprim(Menu):
    bl_label = "ke.fit_prim"
    bl_idname = "VIEW3D_MT_ke_pie_fitprim"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        cm = context.mode
        layout = self.layout
        pie = layout.menu_pie()

        if cm == "EDIT_MESH":

            W = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            W.ke_fitprim_option = "CYL"
            W.ke_fitprim_pieslot = "W"

            E = pie.operator("view3d.ke_fitprim", text="Cylinder Obj", icon='MESH_CYLINDER')
            E.ke_fitprim_option = "CYL"
            E.ke_fitprim_pieslot = "E"
            E.ke_fitprim_itemize = True

            S = pie.operator("view3d.ke_fitprim", text="Cube", icon='CUBE')
            S.ke_fitprim_option = "BOX"
            S.ke_fitprim_pieslot = "S"

            N = pie.operator("view3d.ke_fitprim", text="Cube Obj", icon='MESH_CUBE')
            N.ke_fitprim_option = "BOX"
            N.ke_fitprim_pieslot = "N"
            N.ke_fitprim_itemize = True

            col = pie.box().column()
            NW = col.operator("view3d.ke_fitprim", text="Sphere", icon='SPHERE')
            NW.ke_fitprim_option = "SPHERE"
            NW.ke_fitprim_pieslot = "NW"
            NW2 = col.operator("view3d.ke_fitprim", text="QuadSphere", icon='SPHERE')
            NW2.ke_fitprim_option = "QUADSPHERE"
            NW2.ke_fitprim_pieslot = "NW"

            col = pie.box().column()
            NE = col.operator("view3d.ke_fitprim", text="Sphere Obj", icon='MESH_UVSPHERE')
            NE.ke_fitprim_option = "SPHERE"
            NE.ke_fitprim_pieslot = "NE"
            NE.ke_fitprim_itemize = True
            NE2 = col.operator("view3d.ke_fitprim", text="QuadSphere Obj", icon='MESH_UVSPHERE')
            NE2.ke_fitprim_option = "QUADSPHERE"
            NE2.ke_fitprim_pieslot = "NE"
            NE2.ke_fitprim_itemize = True

            SW = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            SW.ke_fitprim_option = "PLANE"
            SW.ke_fitprim_pieslot = "SW"

            SE = pie.operator("view3d.ke_fitprim", text="Plane Obj", icon='MESH_PLANE')
            SE.ke_fitprim_option = "PLANE"
            SE.ke_fitprim_pieslot = "SE"
            SE.ke_fitprim_itemize = True


        if cm == "OBJECT":
            # W
            pie.separator()

            E = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            E.ke_fitprim_option = "CYL"
            E.ke_fitprim_pieslot = "E"

            # S
            pie.separator()

            N = pie.operator("view3d.ke_fitprim", text="Cube", icon='MESH_CUBE')
            N.ke_fitprim_option = "BOX"
            N.ke_fitprim_pieslot = "N"

            NW2 = pie.operator("view3d.ke_fitprim", text="QuadSphere", icon='MESH_UVSPHERE')
            NW2.ke_fitprim_option = "QUADSPHERE"
            NW2.ke_fitprim_pieslot = "NW"

            NE = pie.operator("view3d.ke_fitprim", text="Sphere", icon='MESH_UVSPHERE')
            NE.ke_fitprim_option = "SPHERE"
            NE.ke_fitprim_pieslot = "NE"

            # SW
            pie.separator()

            SE = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            SE.ke_fitprim_option = "PLANE"
            SE.ke_fitprim_pieslot = "SE"


class VIEW3D_MT_PIE_ke_fitprim_add(Menu):
    bl_label = "ke.fit_prim_add"
    bl_idname = "VIEW3D_MT_ke_pie_fitprim_add"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        cm = context.mode
        layout = self.layout
        pie = layout.menu_pie()

        if cm == "EDIT_MESH":

            W = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            W.ke_fitprim_option = "CYL"
            W.ke_fitprim_pieslot = "W"

            E = pie.operator("view3d.ke_fitprim", text="Cylinder Obj", icon='MESH_CYLINDER')
            E.ke_fitprim_option = "CYL"
            E.ke_fitprim_pieslot = "E"
            E.ke_fitprim_itemize = True

            S = pie.operator("view3d.ke_fitprim", text="Cube", icon='CUBE')
            S.ke_fitprim_option = "BOX"
            S.ke_fitprim_pieslot = "S"

            N = pie.operator("view3d.ke_fitprim", text="Cube Obj", icon='MESH_CUBE')
            N.ke_fitprim_option = "BOX"
            N.ke_fitprim_pieslot = "N"
            N.ke_fitprim_itemize = True

            col = pie.box().column()
            NW = col.operator("view3d.ke_fitprim", text="Sphere", icon='SPHERE')
            NW.ke_fitprim_option = "SPHERE"
            NW.ke_fitprim_pieslot = "NW"
            NW2 = col.operator("view3d.ke_fitprim", text="QuadSphere", icon='SPHERE')
            NW2.ke_fitprim_option = "QUADSPHERE"
            NW2.ke_fitprim_pieslot = "NW"

            col = pie.box().column()
            NE = col.operator("view3d.ke_fitprim", text="Sphere Obj", icon='MESH_UVSPHERE')
            NE.ke_fitprim_option = "SPHERE"
            NE.ke_fitprim_pieslot = "NE"
            NE.ke_fitprim_itemize = True
            NE2 = col.operator("view3d.ke_fitprim", text="QuadSphere Obj", icon='MESH_UVSPHERE')
            NE2.ke_fitprim_option = "QUADSPHERE"
            NE2.ke_fitprim_pieslot = "NE"
            NE2.ke_fitprim_itemize = True

            SW = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            SW.ke_fitprim_option = "PLANE"
            SW.ke_fitprim_pieslot = "SW"

            SE = pie.operator("view3d.ke_fitprim", text="Plane Obj", icon='MESH_PLANE')
            SE.ke_fitprim_option = "PLANE"
            SE.ke_fitprim_pieslot = "SE"
            SE.ke_fitprim_itemize = True


        if cm == "OBJECT":
            # WEST
            op = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            op.ke_fitprim_option = "CYL"
            op.ke_fitprim_pieslot = "W"

            # EAST
            cbox = pie.box()
            cbox.scale_x = 2.3
            cbox.emboss = "NONE"
            col = cbox.column_flow(columns=2)
            col.emboss = "PULLDOWN_MENU"
            col.menu_contents("VIEW3D_MT_add")
            # Silly filler to get Lights menu on the left column
            col.label(text="")
            col.label(text="")
            col.label(text="")
            col.label(text="")

            # SOUTH
            op = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            op.ke_fitprim_option = "PLANE"
            op.ke_fitprim_pieslot = "S"

            # NORTH
            op = pie.operator("view3d.ke_fitprim", text="Cube", icon='MESH_CUBE')
            op.ke_fitprim_option = "BOX"
            op.ke_fitprim_pieslot = "N"

            # NORTHWEST
            op = pie.operator("view3d.ke_fitprim", text="Sphere", icon='MESH_UVSPHERE')
            op.ke_fitprim_option = "SPHERE"
            op.ke_fitprim_pieslot = "NW"

            # NORTHEAST
            pie.separator()

            # SOUTHWEST
            op = pie.operator("view3d.ke_fitprim", text="QuadSphere", icon='MESH_UVSPHERE')
            op.ke_fitprim_option = "QUADSPHERE"
            op.ke_fitprim_pieslot = "SW"
            # SOUTHEAST - BLANK


class VIEW3D_MT_PIE_ke_align(Menu):
    bl_label = "keSnapAlign"
    bl_idname = "VIEW3D_MT_ke_pie_align"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.cursor_fit_selected_and_orient", text="Cursor Fit&Align", icon="ORIENTATION_CURSOR")

        pie.operator("mesh.ke_zeroscale", text="ZeroScale H", icon="NODE_SIDE").screen_axis = 0

        pie.operator("mesh.ke_zeroscale", text="ZeroScale Cursor", icon="CURSOR").orient_type = "CURSOR"

        pie.operator("mesh.ke_zeroscale", text="ZeroScale V", icon="NODE_TOP").screen_axis = 1

        c = pie.row()
        main = c.column()
        selbox = main.box().column()
        selbox.operator("view3d.snap_selected_to_grid", text="Selection to Grid", icon='RESTRICT_SELECT_OFF')
        selbox.operator("view3d.snap_selected_to_cursor", text="Selection to Cursor", icon='RESTRICT_SELECT_OFF').use_offset = False
        selbox.operator("view3d.snap_selected_to_cursor", text="Sel.to Cursor w.Offset", icon='RESTRICT_SELECT_OFF').use_offset = True
        selbox.operator("view3d.snap_selected_to_active", text="Selection to Active", icon='RESTRICT_SELECT_OFF')
        selbox.operator("view3d.selected_to_origin", text="Sel.to Origin (Set Origin)", icon='RESTRICT_SELECT_OFF')
        spacer = c.column()
        spacer.label(text="")
        main.label(text="")
        main.label(text="")

        pie.operator("mesh.ke_zeroscale", text="ZeroScale Normal", icon="NORMALS_FACE").orient_type = "NORMAL"

        c = pie.row()
        main = c.column()
        main.label(text="")
        main.label(text="")
        cbox = main.box().column()
        cbox.operator("view3d.snap_cursor_to_center", text="Cursor to World Origin", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_selected", text="Cursor to Selected", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_active", text="Cursor to Active", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_grid", text="Cursor to Grid", icon='CURSOR')
        cbox.operator("view3d.ke_cursor_clear_rot", icon='CURSOR')
        spacer = c.column()
        spacer.label(text="")

        spacer = pie.row()
        spacer.label(text="")
        vbox = spacer.column()
        vbox.label(text="")
        vbox.label(text="")
        vbox = vbox.box().column()
        vbox.operator('view3d.align_origin_to_selected', text="Align Origin To Selected", icon="OBJECT_ORIGIN")
        vbox.operator('view3d.ke_origin_to_cursor', text="Align Origin(s) To Cursor", icon="PIVOT_CURSOR")
        vbox.operator('view3d.ke_object_to_cursor', text="Align Object(s) to Cursor", icon="CURSOR")
        vbox.operator('view3d.ke_align_object_to_active', text="Align Object(s) to Active", icon="CON_LOCLIKE")
        vbox.operator('view3d.ke_swap', text="Swap Places", icon="CON_TRANSLIKE")


class VIEW3D_MT_PIE_ke_snapping(Menu):
    bl_label = "keSnapping"
    bl_idname = "VIEW3D_MT_ke_pie_snapping"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        ct = bpy.context.scene.tool_settings
        name1 = bpy.context.scene.kekit.snap_name1
        name2 = bpy.context.scene.kekit.snap_name2
        name3 = bpy.context.scene.kekit.snap_name3
        name4 = bpy.context.scene.kekit.snap_name4
        layout = self.layout
        pie = layout.menu_pie()

        # ELEMENTS & TARGETS BOX
        c = pie.column()
        c.separator(factor=9)
        cbox = c.box().column()
        cbox.ui_units_x = 6.5
        cbox.scale_y = 1.2
        if not ct.use_snap_grid_absolute:
            cbox.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=False).op = "GRID"
        else:
            cbox.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=True).op = "GRID"
        c.separator(factor=0.3)
        cbox = c.box().column()
        cbox.ui_units_x = 6
        cbox.scale_y = 1.2
        cbox.prop(ct, 'snap_elements', expand=True)
        cbox.separator(factor=1)
        cbox.prop(ct, 'snap_target', expand=True)

        # COMBOS
        pie.operator("view3d.ke_snap_combo", icon="KEYTYPE_MOVING_HOLD_VEC", text="%s" % name3).mode = "SET3"
        pie.operator("view3d.ke_snap_combo", icon="KEYTYPE_KEYFRAME_VEC", text="%s" % name4).mode = "SET4"
        pie.operator("view3d.ke_snap_combo", icon="KEYTYPE_JITTER_VEC", text="%s" % name1).mode = "SET1"
        pie.separator()
        pie.operator("view3d.ke_snap_combo", icon="KEYTYPE_EXTREME_VEC", text="%s" % name2).mode = "SET2"
        pie.separator()

        # SETTINGS BOX
        r = pie.row()
        r.separator(factor=2.4)
        c = r.column()
        c.separator(factor=15)
        cbox = c.box().column()
        cbox.scale_y = 1.2
        cbox.ui_units_x = 6
        cbox.prop(ct, 'use_snap', text="Snapping On/Off")
        c.separator(factor=1.4)
        cbox = c.box().column()
        cbox.scale_y = 1.2
        cbox.ui_units_x = 6
        cbox.prop(ct, 'use_snap_align_rotation', text="Align Rotation")
        cbox.prop(ct, 'use_snap_self', text="Project Onto Self")
        cbox.prop(ct, 'use_snap_project', text="Project Ind.Elements")
        cbox.prop(ct, 'use_snap_backface_culling', text="Backface Culling")
        cbox.prop(ct, 'use_snap_peel_object', text="Peel Object")
        row = cbox.row(align=True)
        row.prop(ct, 'use_snap_translate', text="T")
        row.prop(ct, 'use_snap_rotate', text="R")
        row.prop(ct, 'use_snap_scale', text="S")


class VIEW3D_MT_PIE_bsnapping(Menu):
    bl_label = "bSnapping"
    bl_idname = "VIEW3D_MT_bsnapping"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        tool_settings = context.tool_settings
        snap_elements = tool_settings.snap_elements
        obj = context.active_object
        object_mode = 'OBJECT' if obj is None else obj.mode

        layout = self.layout
        pie = layout.menu_pie()
        c = pie.column()
        # sub = c.box().column()
        sub = c.box().column(align=True)
        sub.scale_y = 1.3

        if 'INCREMENT' in snap_elements:
            sub.prop(tool_settings, "use_snap_grid_absolute")

        if snap_elements != {'INCREMENT'}:
            # cbox.label(text="Snap with")
            tsub = c.box().column(align=True)
            tsub.scale_y = 1.3

            tsub.prop(tool_settings, "snap_target", expand=True)
            sub.prop(tool_settings, "use_snap_backface_culling")

            if obj:
                if object_mode == 'EDIT':
                    sub.prop(tool_settings, "use_snap_self")
                if object_mode in {'OBJECT', 'POSE', 'EDIT', 'WEIGHT_PAINT'}:
                    sub.prop(tool_settings, "use_snap_align_rotation")

            if 'FACE' in snap_elements:
                sub.prop(tool_settings, "use_snap_project")

            if 'VOLUME' in snap_elements:
                sub.prop(tool_settings, "use_snap_peel_object")

        # cbox.label(text="Affect")

        sub2 = c.box().column(align=True)
        sub2.prop(tool_settings, "use_snap_translate", text="Move", toggle=True)
        sub2.prop(tool_settings, "use_snap_rotate", text="Rotate", toggle=True)
        sub2.prop(tool_settings, "use_snap_scale", text="Scale", toggle=True)

        c = pie.column()
        rightbox = c.box().column()
        rightbox.scale_y = 1.5

        # rightbox.label(text="Snap to")
        rightbox.prop(tool_settings, "snap_elements", expand=True)



class VIEW3D_MT_PIE_ke_fit2grid(Menu):
    bl_label = "keFit2Grid"
    bl_idname = "VIEW3D_MT_ke_pie_fit2grid"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fit2grid", text="50cm").set_grid = 0.5
        pie.operator("view3d.ke_fit2grid", text="5cm").set_grid = 0.05
        pie.operator("view3d.ke_fit2grid", text="15cm").set_grid = 0.15
        pie.operator("view3d.ke_fit2grid", text="1cm").set_grid = 0.01
        pie.operator("view3d.ke_fit2grid", text="1m").set_grid = 1.0
        pie.operator("view3d.ke_fit2grid", text="2.5cm").set_grid = 0.025
        pie.operator("view3d.ke_fit2grid", text="25cm").set_grid = 0.25
        pie.operator("view3d.ke_fit2grid", text="10cm").set_grid = 0.1


class VIEW3D_MT_PIE_ke_fit2grid_micro(Menu):
    bl_label = "keFit2Grid_micro"
    bl_idname = "VIEW3D_MT_ke_pie_fit2grid_micro"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fit2grid", text="5mm").set_grid = 0.005
        pie.operator("view3d.ke_fit2grid", text="5µm").set_grid = 0.0005
        pie.operator("view3d.ke_fit2grid", text="1.5mm").set_grid = 0.0015
        pie.operator("view3d.ke_fit2grid", text="1µm").set_grid = 0.0001
        pie.operator("view3d.ke_fit2grid", text="1cm").set_grid = 0.01
        pie.operator("view3d.ke_fit2grid", text="2.5µm").set_grid = 0.00025
        pie.operator("view3d.ke_fit2grid", text="5µm").set_grid = 0.0005
        pie.operator("view3d.ke_fit2grid", text="1mm").set_grid = 0.001


class VIEW3D_MT_PIE_ke_multicut(Menu):
    bl_label = "keMultiCut"
    bl_idname = "VIEW3D_MT_ke_pie_multicut"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def get_props(self, preset="0"):
        p = bpy.context.scene.kekit.mc_prefs[:]
        v1, v2, v3, v4 = 0, 0, 0, 0
        if preset == "0":
            v1, v2, v3, v4 = p[0], p[1], p[2], p[3]
        elif preset == "1":
            v1, v2, v3, v4 = p[4], p[5], p[6], p[7]
        elif preset == "2":
            v1, v2, v3, v4 = p[8], p[9], p[10], p[11]
        elif preset == "3":
            v1, v2, v3, v4 = p[12], p[13], p[14], p[15]
        elif preset == "4":
            v1, v2, v3, v4 = p[16], p[17], p[18], p[19]
        elif preset == "5":
            v1, v2, v3, v4 = p[20], p[21], p[22], p[23]
        elif preset == "6":
            v1, v2, v3, v4 = p[24], p[25], p[26], p[27]
        elif preset == "7":
            v1, v2, v3, v4 = p[28], p[29], p[30], p[31]
        return v1, str(int(v2)), v3, bool(v4)

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        op = pie.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name0)
        v1, v2, v3, v4 = self.get_props(preset="0")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name1)
        v1, v2, v3, v4 = self.get_props(preset="1")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name2)
        v1, v2, v3, v4 = self.get_props(preset="2")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name3)
        v1, v2, v3, v4 = self.get_props(preset="3")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name4)
        v1, v2, v3, v4 = self.get_props(preset="4")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name5)
        v1, v2, v3, v4 = self.get_props(preset="5")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name6)
        v1, v2, v3, v4 = self.get_props(preset="6")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name7)
        v1, v2, v3, v4 = self.get_props(preset="7")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"


class VIEW3D_MT_PIE_ke_overlays(Menu):
    bl_label = "keOverlays"
    bl_idname = "VIEW3D_MT_ke_pie_overlays"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        o = context.space_data.overlay
        s = context.space_data.shading

        layout = self.layout
        pie = layout.menu_pie()

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3

        if s.show_backface_culling:
            cbox.operator("view3d.ke_overlays", text="Backface Culling", icon="XRAY", depress=True).overlay = "BACKFACE"
        else:
            cbox.operator("view3d.ke_overlays", text="Backface Culling", icon="XRAY", depress=False).overlay = "BACKFACE"

        cbox.separator(factor=1.5)

        if o.show_floor:
            cbox.operator("view3d.ke_overlays", text="Grid", icon="GRID", depress=True).overlay = "GRID"
        else:
            cbox.operator("view3d.ke_overlays", text="Grid", icon="GRID", depress=False).overlay = "GRID"

        if o.show_extras:
            cbox.operator("view3d.ke_overlays", text="Extras", icon="LIGHT_SUN", depress=True).overlay = "EXTRAS"
        else:
            cbox.operator("view3d.ke_overlays", text="Extras", icon="LIGHT_SUN", depress=False).overlay = "EXTRAS"

        if o.show_cursor:
            cbox.operator("view3d.ke_overlays", text="Cursor", icon="CURSOR", depress=True).overlay = "CURSOR"
        else:
            cbox.operator("view3d.ke_overlays", text="Cursor", icon="CURSOR", depress=False).overlay = "CURSOR"

        if o.show_object_origins:
            cbox.operator("view3d.ke_overlays", text="Origins", icon="OBJECT_ORIGIN", depress=True).overlay = "ORIGINS"
        else:
            cbox.operator("view3d.ke_overlays", text="Origins", icon="OBJECT_ORIGIN", depress=False).overlay = "ORIGINS"

        if o.show_bones:
            cbox.operator("view3d.ke_overlays", text="Bones", icon="BONE_DATA", depress=True).overlay = "BONES"
        else:
            cbox.operator("view3d.ke_overlays", text="Bones", icon="BONE_DATA", depress=False).overlay = "BONES"

        cbox.separator(factor=1.5)

        if o.show_wireframes:
            cbox.operator("view3d.ke_overlays", text="Object Wireframes", icon="MOD_WIREFRAME", depress=True).overlay = "WIREFRAMES"
        else:
            cbox.operator("view3d.ke_overlays", text="Object Wireframes", icon="MOD_WIREFRAME", depress=False).overlay = "WIREFRAMES"

        if o.show_outline_selected:
            cbox.operator("view3d.ke_overlays", text="Select Outline", icon="MESH_CIRCLE", depress=True).overlay = "OUTLINE"
        else:
            cbox.operator("view3d.ke_overlays", text="Select Outline", icon="MESH_CIRCLE", depress=False).overlay = "OUTLINE"

        if s.show_object_outline:
            cbox.operator("view3d.ke_overlays", text="Object Outline", icon="MESH_CIRCLE", depress=True).overlay = "OBJ_OUTLINE"
        else:
            cbox.operator("view3d.ke_overlays", text="Object Outline", icon="MESH_CIRCLE", depress=False).overlay = "OBJ_OUTLINE"

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3
        if o.show_edge_seams:
            cbox.operator("view3d.ke_overlays", text="Edge Seams", icon="UV_ISLANDSEL", depress=True).overlay = "SEAMS"
        else:
            cbox.operator("view3d.ke_overlays", text="Edge Seams", icon="UV_ISLANDSEL", depress=False).overlay = "SEAMS"

        if o.show_edge_sharp:
            cbox.operator("view3d.ke_overlays", text="Edge Sharp", icon="MESH_CUBE", depress=True).overlay = "SHARP"
        else:
            cbox.operator("view3d.ke_overlays", text="Edge Sharp", icon="MESH_CUBE", depress=False).overlay = "SHARP"

        if o.show_edge_crease:
            cbox.operator("view3d.ke_overlays", text="Edge Crease", icon="META_CUBE", depress=True).overlay = "CREASE"
        else:
            cbox.operator("view3d.ke_overlays", text="Edge Crease", icon="META_CUBE", depress=False).overlay = "CREASE"

        if o.show_edge_bevel_weight:
            cbox.operator("view3d.ke_overlays", text="Edge Bevel Weight", icon="MOD_BEVEL", depress=True).overlay = "BEVEL"
        else:
            cbox.operator("view3d.ke_overlays", text="Edge Bevel Weight", icon="MOD_BEVEL", depress=False).overlay = "BEVEL"

        cbox.separator(factor=0.5)

        if o.show_vertex_normals:
            cbox.operator("view3d.ke_overlays", text="Vertex Normals", icon="NORMALS_VERTEX", depress=True).overlay = "VN"
        else:
            cbox.operator("view3d.ke_overlays", text="Vertex Normals", icon="NORMALS_VERTEX", depress=False).overlay = "VN"

        if o.show_split_normals:
            cbox.operator("view3d.ke_overlays", text="Split Normals", icon="NORMALS_VERTEX_FACE", depress=True).overlay = "SN"
        else:
            cbox.operator("view3d.ke_overlays", text="Split Normals", icon="NORMALS_VERTEX_FACE", depress=False).overlay = "SN"

        if o.show_face_normals:
            cbox.operator("view3d.ke_overlays", text="Face Normals", icon="NORMALS_FACE", depress=True).overlay = "FN"
        else:
            cbox.operator("view3d.ke_overlays", text="Face Normals", icon="NORMALS_FACE", depress=False).overlay = "FN"

        cbox.separator(factor=0.5)

        if o.show_face_orientation:
            cbox.operator("view3d.ke_overlays", text="Face Orientation", icon="FACESEL", depress=True).overlay = "FACEORIENT"
        else:
            cbox.operator("view3d.ke_overlays", text="Face Orientation", icon="FACESEL", depress=False).overlay = "FACEORIENT"

        if o.show_weight:
            cbox.operator("view3d.ke_overlays", text="Vertex Weights", icon="GROUP_VERTEX", depress=True).overlay = "WEIGHT"
        else:
            cbox.operator("view3d.ke_overlays", text="Vertex Weights", icon="GROUP_VERTEX", depress=False).overlay = "WEIGHT"

        if o.show_extra_indices:
            cbox.operator("view3d.ke_overlays", text="Indices", icon="LINENUMBERS_ON", depress=True).overlay = "INDICES"
        else:
            cbox.operator("view3d.ke_overlays", text="Indices", icon="LINENUMBERS_ON", depress=False).overlay = "INDICES"


        c = pie.column()
        c.label(text="")
        cbox = c.box().column()
        cbox.scale_y = 1.3
        cbox.operator("view3d.ke_overlays", text="All Overlays", icon="OVERLAY").overlay = "ALL"
        if o.show_stats:
            cbox.operator("view3d.ke_overlays", text="Stats", icon="LINENUMBERS_ON", depress=True).overlay = "STATS"
        else:
            cbox.operator("view3d.ke_overlays", text="Stats", icon="LINENUMBERS_ON", depress=False).overlay = "STATS"

        # cbox.separator(factor=0.5)
        # cbox.separator()
        try:
            if bpy.context.scene.ke_focus[0] or not bpy.context.scene.ke_focus[0]:  #silly existance check

                if not bpy.context.scene.ke_focus[0] and not bpy.context.scene.ke_focus[10]:
                    cbox.operator("view3d.ke_focusmode", text="Focus Mode", icon="FULLSCREEN_ENTER",
                                  depress=False).supermode = False
                    cbox.operator("view3d.ke_focusmode", text="Super Focus Mode", icon="FULLSCREEN_ENTER",
                                  depress=False).supermode = True

                elif bpy.context.scene.ke_focus[0] and not bpy.context.scene.ke_focus[10]:
                    cbox.operator("view3d.ke_focusmode", text="Focus Mode (Off)", icon="FULLSCREEN_EXIT",
                                  depress=True).supermode = False

                elif bpy.context.scene.ke_focus[10]:
                    cbox.operator("view3d.ke_focusmode", text="Super Focus Mode (Off)", icon="FULLSCREEN_EXIT",
                                  depress=True).supermode = True

        except:
            cbox.operator("view3d.ke_focusmode", text="Focus Mode", icon="FULLSCREEN_ENTER",
                          depress=False).supermode = False
            cbox.operator("view3d.ke_focusmode", text="Super Focus", icon="FULLSCREEN_ENTER",
                          depress=False).supermode = True

        pie = layout.menu_pie()
        pie.operator("view3d.ke_overlays", text="All Edge Overlays", icon="UV_EDGESEL").overlay = "ALLEDIT"
        pie.label(text="")


class VIEW3D_MT_PIE_ke_orientpivot(Menu):
    bl_label = "keOrientPivot"
    bl_idname = "VIEW3D_MT_ke_pie_orientpivot"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        mode = bpy.context.mode
        obj = context.active_object
        name1 = bpy.context.scene.kekit.opc1_name
        name2 = bpy.context.scene.kekit.opc2_name
        name3 = bpy.context.scene.kekit.opc3_name
        name4 = bpy.context.scene.kekit.opc4_name

        layout = self.layout
        pie = layout.menu_pie()

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.25
        cbox.ui_units_x = 6.25
        cbox.prop(context.scene.transform_orientation_slots[0], "type", expand=True)
        c.separator(factor=11)

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.25
        cbox.ui_units_x = 6.5
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='BOUNDING_BOX_CENTER')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='CURSOR')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='INDIVIDUAL_ORIGINS')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='MEDIAN_POINT')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='ACTIVE_ELEMENT')
        if (obj is None) or (mode in {'OBJECT', 'POSE', 'WEIGHT_PAINT'}):
            cbox.prop(context.scene.tool_settings, "use_transform_pivot_point_align")
        else:
            c.separator(factor=2)
        c.separator(factor=11)

        pie.operator("view3d.ke_opc", text="%s" % name1, icon="KEYTYPE_JITTER_VEC").combo = "1"
        pie.operator("view3d.ke_opc", text="%s" % name2, icon="KEYTYPE_EXTREME_VEC").combo = "2"
        pie.separator()
        pie.separator()
        pie.operator("view3d.ke_opc", text="%s" % name3, icon="KEYTYPE_MOVING_HOLD_VEC").combo = "3"
        pie.operator("view3d.ke_opc", text="%s" % name4, icon="KEYTYPE_KEYFRAME_VEC").combo = "4"


class KE_MT_SHADING_PIE(Menu):
    '''Extended keKit Shading Pie Menu'''
    bl_label = "keShading"
    bl_idname = "KE_MT_shading_pie"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        if view.type == 'VIEW_3D':
            shading = view.shading
        if shading is None:
            print("Pie Menu not drawn: Incorrect Context Fallback")
            return {'CANCELLED'}

        pie = layout.menu_pie()

        # SLOT --------------------------------------------------------------------------------
        pie.prop(shading, "type", expand=True)

        # SLOT --------------------------------------------------------------------------------
        if shading.type == 'RENDERED':
            c = pie.row()
            b = c.column()
            col = b.box().column()
            col.scale_y = 0.9
            col.prop(shading, "use_scene_lights_render")
            col.prop(shading, "use_scene_world_render")
            col.operator("view3d.ke_bg_sync", icon="SHADING_TEXTURE")
            # col.separator(factor=1.2)

            row = col.row()
            row.prop(shading, "render_pass", text="")
            row.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
            c.separator(factor=2.5)
            b.separator(factor=3.5)
        else:
            pie.separator()

        # SLOT --------------------------------------------------------------------------------
        if shading.type == 'SOLID' and shading.light != 'FLAT':
            spacer = pie.row()
            spacer.label(text="")

            col = spacer.box().column()
            sub = col.row()

            if shading.light == 'STUDIO':
                prefs = context.preferences
                system = prefs.system

                if not system.use_studio_light_edit:
                    sub.scale_y = 0.6
                    sub.scale_x = .738
                    sub.template_icon_view(shading, "studio_light", scale_popup=3.0)
                else:
                    sub.prop(
                        system,
                        "use_studio_light_edit",
                        text="Disable Studio Light Edit",
                        icon='NONE',
                        toggle=True,
                    )
                sub2 = sub.column()
                sub2.scale_x = 1.3
                sub2.scale_y = 1.8
                p = sub2.column(align=False)
                p.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
                p.prop(shading, "use_world_space_lighting", text="", icon='WORLD', toggle=True)
                p.separator(factor=0.3)
                p.prop(shading, "studiolight_rotate_z", text="RotateZ")


            elif shading.light == 'MATCAP':
                sub.scale_y = 0.6
                sub.scale_x = .7
                sub.template_icon_view(shading, "studio_light", scale_popup=3.0)

                sub = sub.column()
                sub.scale_y = 1.8
                sub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
                sub.operator("view3d.toggle_matcap_flip", emboss=False, text="", icon='ARROW_LEFTRIGHT')


        elif shading.type == 'RENDERED' and not shading.use_scene_world_render:
            b = pie.row()
            c = b.column()

            col = b.box().column()
            col.scale_y = 0.65
            col.scale_x = 0.7
            sub = col.row()
            sub.template_icon_view(shading, "studio_light", scale_popup=3)

            sub2 = sub.column()
            sub2.scale_y = 1.4
            sub2.scale_x = 1.1
            sub2.prop(shading, "studiolight_rotate_z", text="RotateZ")
            sub2.prop(shading, "studiolight_intensity", text="Intensity")
            sub2.prop(shading, "studiolight_background_alpha", text="Alpha")
            sub2.prop(shading, "studiolight_background_blur", text="Blur")
            b.separator(factor=13.5)
            c.separator(factor=2.5)

        else:
            pie.separator()

        # SLOT --------------------------------------------------------------------------------
        if shading.type == 'MATERIAL':
            r = pie.row()
            c = r.column()
            c.separator(factor=16)
            col = c.box().column()
            col.scale_y = 0.9
            col.prop(shading, "use_scene_lights")
            col.prop(shading, "use_scene_world")
            col.operator("view3d.ke_bg_sync", icon="SHADING_TEXTURE")
            # col.separator(factor=1.2)
            row = col.row()
            row.prop(shading, "render_pass", text="")
            row.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
            r.separator(factor=2.4)

        else:
            pie.separator()

        # SLOT --------------------------------------------------------------------------------
        r = pie.row()
        r.separator(factor=2.4)
        c = r.column()

        if shading.type == 'SOLID':
            c.separator(factor=3)
            col = c.box().column()
            col.scale_x = 0.9
            lights = col.row()
            lights.prop(shading, "light", expand=True)
            col.separator(factor=0.5)
            col.grid_flow(columns=3, align=True).prop(shading, "color_type", expand=True)
            if shading.color_type == 'SINGLE':
                col.column().prop(shading, "single_color", text="")
            col.separator(factor=0.5)
            opt = col.row(align=False)
            opt.alignment = "CENTER"
            opt.prop(shading, "show_shadows", text="Shadows", toggle=True)
            opt.prop(shading, "show_cavity", text="Cavity", toggle=True)
            opt.prop(shading, "show_specular_highlight", text="Specular", toggle=True)

        elif shading.type == 'MATERIAL':
            if not shading.use_scene_world:
                c.separator(factor=16)
                col = c.box().column()
                sub = col.row()
                sub.scale_y = 0.65
                sub.scale_x = 0.7
                sub.template_icon_view(shading, "studio_light", scale_popup=3)

                sub2 = sub.column()
                sub2.scale_y = 1.4
                sub2.scale_x = 1.1
                sub2.prop(shading, "studiolight_rotate_z", text="RotateZ")
                sub2.prop(shading, "studiolight_intensity", text="Intensity")
                sub2.prop(shading, "studiolight_background_alpha", text="Alpha")
                sub2.prop(shading, "studiolight_background_blur", text="Blur")


class KE_call_pie(bpy.types.Operator):
    '''Custom Pie Operator with preset (temp) hotkey'''
    bl_idname = "ke.call_pie"
    bl_label = "keCallPie"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty()

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            bpy.ops.wm.call_menu_pie(name='%s' % self.name)
        return {'FINISHED'}


class VIEW3D_MT_PIE_ke_materials(Menu):
    bl_label = "keMaterials"
    bl_idname = "VIEW3D_MT_PIE_ke_materials"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        c = addon_utils.check("materials_utils")

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        box = pie.box()
        box.ui_units_x = 7
        col = box.column(align=True)
        col.label(text="Assign ID Material")
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm01)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm01_name).m_id = 1
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm02)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm02_name).m_id = 2
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm03)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm03_name).m_id = 3
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm04)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm04_name).m_id = 4
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm05)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm05_name).m_id = 5
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm06)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm06_name).m_id = 6
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm07)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm07_name).m_id = 7
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm08)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm08_name).m_id = 8
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm09)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm09_name).m_id = 9
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm10)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm10_name).m_id = 10
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm11)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm11_name).m_id = 11
        row = col.row(align=True)
        row.template_node_socket(color=context.scene.kekit.idm12)
        row.operator("view3d.ke_id_material",text=context.scene.kekit.idm12_name).m_id = 12

        if c[0] and c[1]:
            # obj = context.object
            mu_prefs = context.preferences.addons["materials_utils"].preferences
            limit = mu_prefs.search_show_limit
            if limit == 0:
                limit = "Inf."
            mat_count = len(bpy.data.materials)
            if mat_count < 11:
                col_count = 1
            else:
                col_count = ceil((mat_count / 11))

            # ASSIGN MATERIALS BOX - RIGHT -------------------------------------------------
            box = pie.box()
            if col_count < 2:
                box.ui_units_x = 7.5
            box.label(text="Assign Material  [%s / %s]" % (mat_count, limit))
            col = box.column_flow(align=False, columns=col_count)
            col.ui_units_x = 6 * col_count
            col.menu_contents("VIEW3D_MT_materialutilities_assign_material")

            # MATERIALS UTILS MAIN BOX - BOTTOM --------------------------------------------
            main = pie.column()
            main.separator(factor=3)
            box = main.box()
            col = box.column(align=True)
            # col.menu_contents("VIEW3D_MT_materialutilities_main")
            col.menu('VIEW3D_MT_materialutilities_select_by_material',
                        icon='VIEWZOOM')
            col.separator()
            col.operator('VIEW3D_OT_materialutilities_copy_material_to_others',
                            text='Copy Active to Others',
                            icon='COPY_ID')
            col.separator()
            col.menu('VIEW3D_MT_materialutilities_clean_slots',
                        icon='NODE_MATERIAL')
            col.separator()
            col.operator('VIEW3D_OT_materialutilities_replace_material',
                            text='Replace Material',
                            icon='OVERLAY')
            op = col.operator('VIEW3D_OT_materialutilities_fake_user_set',
                                 text='Set Fake User',
                                 icon='FAKE_USER_OFF')
            op.fake_user = mu_prefs.fake_user
            op.affect = mu_prefs.fake_user_affect
            op = col.operator('VIEW3D_OT_materialutilities_change_material_link',
                                 text='Change Material Link',
                                 icon='LINKED')
            op.link_to = mu_prefs.link_to
            op.affect = mu_prefs.link_to_affect
            col.separator()
            col.menu('VIEW3D_MT_materialutilities_specials',
                        icon='SOLO_ON')
        else:
            pie.label(text="Material Utils Add-on Not Enabled")


class VIEW3D_MT_PIE_ke_step_rotate(Menu):
    bl_label = "keVPStepRotate"
    bl_idname = "VIEW3D_MT_ke_pie_step_rotate"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_vp_step_rotate", text="-90", icon="LOOP_BACK").mode = "NROT090"
        pie.operator("view3d.ke_vp_step_rotate", text="90", icon="LOOP_FORWARDS").mode = "ROT090"

        s = pie.column()
        s.separator(factor=1.2)
        box = s.box()
        box.ui_units_x = 8
        box.ui_units_y = 3.15
        row = box.column_flow(columns=2, align=True)
        row.operator("object.ke_object_op", text="X Clear").cmd = "ROT_CLEAR_X"
        row.operator("object.ke_object_op", text="Y Clear").cmd = "ROT_CLEAR_Y"
        row.operator("object.ke_object_op", text="Z Clear").cmd = "ROT_CLEAR_Z"
        row.prop(context.object, "rotation_euler", text="")

        box = s.box()
        box.separator(factor=0.15)
        box.operator("object.ke_straighten", text="Straighten Object", icon="CON_ROTLIMIT").deg = 90
        pie.operator("object.rotation_clear").clear_delta = False
        pie.operator("view3d.ke_vp_step_rotate", text="-45", icon="LOOP_BACK").mode = "NROT045"
        pie.operator("view3d.ke_vp_step_rotate", text="45", icon="LOOP_FORWARDS").mode = "ROT045"
        pie.operator("view3d.ke_vp_step_rotate", text="-180", icon="LOOP_BACK").mode = "NROT180"
        pie.operator("view3d.ke_vp_step_rotate", text="180", icon="LOOP_FORWARDS").mode = "ROT180"


class VIEW3D_MT_PIE_ke_vcbookmarks(Menu):
    bl_label = "View & Cursor Bookmarks "
    bl_idname = "VIEW3D_MT_ke_pie_vcbookmarks"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        q = bpy.context.scene.ke_query_props

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # VIEW BOOKMARKS
        box = pie.box()
        box.ui_units_x = 6.5
        box.label(text="View Bookmarks")
        row = box.grid_flow(row_major=True, columns=2, align=False)

        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET1"
        if sum(bpy.context.scene.ke_vslot1) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 1", depress=False).mode = "USE1"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 1", depress=True).mode = "USE1"

        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET2"
        if sum(bpy.context.scene.ke_vslot2) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 2", depress=False).mode = "USE2"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 2", depress=True).mode = "USE2"

        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET3"
        if sum(bpy.context.scene.ke_vslot3) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 3", depress=False).mode = "USE3"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 3", depress=True).mode = "USE3"

        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET4"
        if sum(bpy.context.scene.ke_vslot4) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 4", depress=False).mode = "USE4"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 4", depress=True).mode = "USE4"

        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET5"
        if sum(bpy.context.scene.ke_vslot5) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 5", depress=False).mode = "USE5"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 5", depress=True).mode = "USE5"

        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET6"
        if sum(bpy.context.scene.ke_vslot6) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 6", depress=False).mode = "USE6"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="Use Slot 6", depress=True).mode = "USE6"

        # sub = box.column(align=True)
        # sub.alignment="CENTER"
        # sub.operator('VIEW3D_OT_ke_viewpos', text="Get").mode = "GET"
        # sub.prop(q, "view_query", text="")
        # sub.operator('VIEW3D_OT_ke_viewpos', text="Set").mode = "SET"

        # CURSOR BOOKMARKS
        box = pie.box()
        box.ui_units_x = 6.5
        box.label(text="Cursor Bookmarks")
        row = box.grid_flow(row_major=True, columns=2, align=False)

        if sum(bpy.context.scene.ke_cslot1) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 1", depress=False).mode = "USE1"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 1", depress=True).mode = "USE1"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET1"

        if sum(bpy.context.scene.ke_cslot2) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 2", depress=False).mode = "USE2"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 2", depress=True).mode = "USE2"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET2"

        if sum(bpy.context.scene.ke_cslot3) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 3", depress=False).mode = "USE3"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 3", depress=True).mode = "USE3"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET3"

        if sum(bpy.context.scene.ke_cslot4) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 4", depress=False).mode = "USE4"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 4", depress=True).mode = "USE4"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET4"

        if sum(bpy.context.scene.ke_cslot5) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 5", depress=False).mode = "USE5"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 5", depress=True).mode = "USE5"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET5"

        if sum(bpy.context.scene.ke_cslot6) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 6", depress=False).mode = "USE6"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="Use Slot 6", depress=True).mode = "USE6"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET6"


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    VIEW3D_OT_ke_snap_element,
    VIEW3D_OT_ke_snap_target,
    VIEW3D_MT_PIE_ke_snapping,
    VIEW3D_MT_PIE_bsnapping,
    VIEW3D_OT_ke_pieops,
    VIEW3D_MT_PIE_ke_fit2grid,
    VIEW3D_MT_PIE_ke_fit2grid_micro,
    VIEW3D_MT_PIE_ke_overlays,
    VIEW3D_MT_PIE_ke_orientpivot,
    VIEW3D_MT_PIE_ke_align,
    VIEW3D_MT_PIE_ke_fitprim,
    VIEW3D_MT_PIE_ke_fitprim_add,
    VIEW3D_MT_PIE_ke_subd,
    VIEW3D_MT_PIE_ke_materials,
    VIEW3D_MT_PIE_ke_step_rotate,
    VIEW3D_MT_PIE_ke_vcbookmarks,
    VIEW3D_MT_PIE_ke_multicut,
    KE_call_pie,
    KE_MT_SHADING_PIE
    )

addon_keymaps = []

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
        kmi = km.keymap_items.new(idname="ke.call_pie", type='ZERO', value='PRESS', ctrl=True, alt=True, shift=True)
        kmi.properties.name = "KE_MT_shading_pie"
        addon_keymaps.append((km, kmi))

def unregister():

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
