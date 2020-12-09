bl_info = {
    "name": "kePies",
    "author": "Kjell Emanuelsson",
    "version": (0, 1, 0),
    "blender": (2, 8, 0),
    "description": "Custom Pie Menus",
    "category": "3D View",}

import bpy
from bpy.types import Menu, Operator, Panel
from . ke_utils import get_selected

# -------------------------------------------------------------------------------------------------
# Operators
# -------------------------------------------------------------------------------------------------
class VIEW3D_OT_ke_pieops(Operator):
    bl_idname = "ke.pieops"
    bl_label = "Pie Operators"
    bl_options = {'REGISTER'}

    # pop: bpy.props.IntProperty(default=0)
    op :  bpy.props.StringProperty(default="GRID")

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        active = context.active_object
        if sel_obj:
            sel_obj = [i for i in sel_obj if i != active]

        # ABSOLUTE GRID TOGGLE
        if self.op == "GRID":
            context.tool_settings.use_snap_grid_absolute = not context.tool_settings.use_snap_grid_absolute

        # BEVEL WEIGHTS
        elif self.op == "BWEIGHTS_ON":
            if not context.object.data.is_editmode:
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.edge_bevelweight(value=1)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                bpy.ops.transform.edge_bevelweight(value=1)

        elif self.op == "BWEIGHTS_OFF":
            if not context.object.data.is_editmode:
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.edge_bevelweight(value=-1)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                bpy.ops.transform.edge_bevelweight(value=-1)

        # W-SUBD
        elif self.op == "WSUBD":
            o = get_selected(context)
            # Add bevel modifier prepped for subd
            if o:
                bpy.ops.object.modifier_add(type='BEVEL')
                b = o.modifiers[-1]
                b.name = "kSubBevel"
                b.width = 0.025
                b.limit_method = 'WEIGHT'
                b.segments = 2
                # Add subd modifier
                bpy.ops.object.modifier_add(type='SUBSURF')
                s = o.modifiers[-1]
                s.name = "kSubD"
                s.levels = 3
                s.render_levels = 3
                s.boundary_smooth = 'PRESERVE_CORNERS'

        # WEIGHTED NORMAL MODFIER
        elif self.op == "WNORMAL":
            bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')

        # TOGGLE SUBD CORNERS
        elif self.op == "SUBCORNERS":
            for mod in [m for m in context.object.modifiers if m.name == 'kSubD']:
                if mod.boundary_smooth == "PRESERVE_CORNERS":
                    mod.boundary_smooth = 'ALL'
                else:
                    mod.boundary_smooth = "PRESERVE_CORNERS"

        elif self.op == "MOD_VIS":
            bpy.ops.object.toggle_apply_modifiers_view()

        elif self.op in {"MIRROR_X", "MIRROR_Y", "MIRROR_Z"}:
            if active:
                bpy.ops.object.modifier_add(type='MIRROR')
                m = active.modifiers[-1]
                m.name = "kMirror"
                if self.op == "MIRROR_Y":
                    m.use_axis = (False, True, False)
                elif self.op == "MIRROR_Z":
                    m.use_axis = (False, False, True)

        elif self.op == "SOLIDIFY":
            if active:
                bpy.ops.object.modifier_add(type='SOLIDIFY')
                m = active.modifiers[-1]
                m.name = "kSolidify"

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


    def draw(self, context):
        # Check existing modifiers
        bevel_mod = ""
        mirror_mod = ""
        solidify_mod = ""
        # ke Transfer Union Surface Object, ke TransferUnion Reciever Object
        ktuso = ""
        kturo = ""
        # ke Mask Transfer Surface Object, ke Mask Transfer Reciever Object
        kmtso = ""
        kmtro = ""

        if context.object and context.object.type == "MESH":
            for m in context.object.modifiers:
                if m.name == "kSubBevel":
                    bevel_mod = m
                if m.name == "kMirror":
                    mirror_mod = m
                if m.name == "kSolidify":
                    solidify_mod = m

        layout = self.layout
        pie = layout.menu_pie()

        # Bevel Weights
        pie.operator("ke.pieops", text="Bevel Weight -1").op = "BWEIGHTS_OFF"
        pie.operator("ke.pieops", text="Bevel Weight 1").op = "BWEIGHTS_ON"

        # Toggles
        c = pie.column(align=True)
        btm = c.box()
        btm.operator("ke.pieops", text="Toggle Stack Visibility").op = "MOD_VIS"
        btm.operator("ke.pieops", text="Toggle SubD Corners").op = "SUBCORNERS"
        c.separator()
        btm = c.box()
        btm.label(text="(WIP)") # Set MaskTransfer
        btm.label(text="(WIP)") # Set TransferUnion

        # SUBD MAIN
        pie.operator("ke.pieops", text="Set W-SUBD").op = "WSUBD"

        # Lattice
        c = pie.column()
        c.label(text="WIP") # Lattice

        # Solidify
        spacer = pie.row()
        spacer.label(text="")
        slot = spacer.column()
        if solidify_mod:
            s = slot.box().column()
            s.label(text="Solidify Settings")
            s.prop(solidify_mod, "thickness")
            s.prop(solidify_mod, "offset")
            # s.prop(solidify_mod, "use_rim")
            # s.prop(solidify_mod, "use_rim_only")
        else:
            slot.operator("ke.pieops", text="Solidify Modifier").op = "SOLIDIFY"
        slot.label(text="")

        # Mirror
        c = pie.row()
        main = c.column()
        main.label(text="")
        if not mirror_mod:
            main.label(text="")

        s = main.box().column()
        if mirror_mod:
            sub = s.row(align=True)
            sub.label(text="Mirror XYZ")
            sub.prop(mirror_mod, "use_axis", icon_only=True)
            sub = s.row(align=True)
            sub.label(text="Bisect XYZ")
            sub.prop(mirror_mod, "use_bisect_axis", icon_only=True)
            sub = s.row(align=True)
            sub.label(text="Flip XYZ")
            sub.prop(mirror_mod, "use_bisect_flip_axis", icon_only=True)
        else:
            s.label(text="Mirror Modifier")
            s.operator("ke.pieops", text="X Mirror").op = "MIRROR_X"
            s.operator("ke.pieops", text="Y Mirror").op = "MIRROR_Y"
            s.operator("ke.pieops", text="Z Mirror").op = "MIRROR_Z"
        spacer = c.column()
        spacer.label(text="")

        # Bevel Settings
        if bevel_mod:
            spacer = pie.row()
            spacer.label(text="")
            slot = spacer.column()
            slot.label(text="")
            s = slot.box().column()
            sub = s.row()
            sub.label(text="Bevel")
            sub.prop_menu_enum(bevel_mod, "offset_type")
            s.prop(bevel_mod, "width", text="Width")
            s.prop(bevel_mod, "segments", text="Segments")
        else:
            spacer = pie.row()
            spacer.label(text="")
            slot = spacer.column()
            slot.label(text="[ Bevel Settings N/A]")


class VIEW3D_MT_PIE_ke_fitprim(Menu):
    bl_label = "ke.fit_prim"
    bl_idname = "VIEW3D_MT_ke_pie_fitprim"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fitprim", text="Cylinder Obj", icon='MESH_CYLINDER').ke_fitprim_option = 'CYL_OBJ_PM'
        pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER').ke_fitprim_option = 'CYL_PM'
        pie.operator("view3d.ke_fitprim", text="Cube Obj", icon="MESH_CUBE").ke_fitprim_option = 'BOX_OBJ_PM'
        pie.operator("view3d.ke_fitprim", text="Cube", icon="CUBE").ke_fitprim_option = 'BOX_PM'
        pie.operator("view3d.ke_fitprim", text="Sphere Obj", icon='MESH_UVSPHERE').ke_fitprim_option = 'SPHERE_OBJ_PM'
        pie.operator("view3d.ke_fitprim", text="Sphere", icon='SPHERE').ke_fitprim_option = 'SPHERE_PM'
        pie.operator("view3d.ke_fitprim", text="Quadsphere Obj", icon="CLIPUV_HLT").ke_fitprim_option = 'QUADSPHERE_OBJ_PM'
        pie.operator("view3d.ke_fitprim", text="Quadsphere", icon="MOD_SUBSURF").ke_fitprim_option = 'QUADSPHERE_PM'


class VIEW3D_MT_PIE_ke_align(Menu):
    bl_label = "keSnapAlign"
    bl_idname = "VIEW3D_MT_ke_pie_align"

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
        cbox.operator("view3d.snap_cursor_to_grid", text="Cursor to Grid", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_selected", text="Cursor to Selected", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_active", text="Cursor to Active", icon='CURSOR')
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

    def draw(self, context):
        ct = bpy.context.scene.tool_settings
        layout = self.layout

        pie = layout.menu_pie()
        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3

        if not ct.use_snap_grid_absolute:
            cbox.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=False).op = "GRID"
        else:
            cbox.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=True).op = "GRID"

        cbox.separator()

        if not ct.snap_target == "MEDIAN":
            cbox.operator("ke.snap_target", text="Median", icon="PIVOT_MEDIAN", depress=False).ke_snaptarget = "MEDIAN"
        else:
            cbox.operator("ke.snap_target", text="Median", icon="PIVOT_MEDIAN", depress=True).ke_snaptarget = "MEDIAN"

        if not ct.snap_target == "ACTIVE":
            cbox.operator("ke.snap_target", text="Active", icon="PIVOT_ACTIVE", depress=False).ke_snaptarget = "ACTIVE"
        else:
            cbox.operator("ke.snap_target", text="Active", icon="PIVOT_ACTIVE", depress=True).ke_snaptarget = "ACTIVE"

        if not ct.snap_target == "CLOSEST":
            cbox.operator("ke.snap_target", text="Closest", icon="NORMALS_VERTEX_FACE", depress=False).ke_snaptarget = "CLOSEST"
        else:
            cbox.operator("ke.snap_target", text="Closest", icon="NORMALS_VERTEX_FACE", depress=True).ke_snaptarget = "CLOSEST"

        if not ct.snap_target == "CENTER":
            cbox.operator("ke.snap_target", text="Center", icon="SNAP_FACE_CENTER", depress=False).ke_snaptarget = "CENTER"
        else:
            cbox.operator("ke.snap_target", text="Center", icon="SNAP_FACE_CENTER", depress=True).ke_snaptarget = "CENTER"

        cbox.separator()

        if not ct.use_snap_self:
            cbox.operator("ke.snap_target", text="Project Self", icon="PROP_PROJECTED",depress=False).ke_snaptarget = "PROJECT"
        else:
            cbox.operator("ke.snap_target", text="Project Self", icon="PROP_PROJECTED",depress=True).ke_snaptarget = "PROJECT"

        if not ct.use_snap_align_rotation:
            cbox.operator("ke.snap_target", text="Align Rotation", icon="ORIENTATION_NORMAL", depress=False).ke_snaptarget = "ALIGN"
        else:
            cbox.operator("ke.snap_target", text="Align Rotation", icon="ORIENTATION_NORMAL", depress=True).ke_snaptarget = "ALIGN"

        pie = layout.menu_pie()
        pie.operator("ke.snap_element", text="Vertex", icon="SNAP_VERTEX").ke_snapelement = "VERTEX"
        pie.operator("ke.snap_element", text="Element Mix", icon="SNAP_ON").ke_snapelement = "MIX"
        pie.operator("ke.snap_element", text="Increment/Grid", icon="SNAP_GRID").ke_snapelement = "INCREMENT"
        pie.separator()
        pie.operator("ke.snap_element", text="Edge", icon="SNAP_EDGE").ke_snapelement = "EDGE"
        pie.separator()
        pie.operator("ke.snap_element", text="Face", icon="SNAP_FACE").ke_snapelement = "FACE"


class VIEW3D_MT_PIE_bsnapping(Menu):
    bl_label = "bSnapping"
    bl_idname = "VIEW3D_MT_bsnapping"

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


class VIEW3D_MT_PIE_ke_overlays(Menu):
    bl_label = "keOverlays"
    bl_idname = "VIEW3D_MT_ke_pie_overlays"

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

        if o.show_extra_indices:
            cbox.operator("view3d.ke_overlays", text="Indices", icon="LINENUMBERS_ON", depress=True).overlay = "INDICES"
        else:
            cbox.operator("view3d.ke_overlays", text="Indices", icon="LINENUMBERS_ON", depress=False).overlay = "INDICES"

        cbox.separator()

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

        cbox.separator()

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

        cbox.separator()

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

        cbox.separator()

        if o.show_face_orientation:
            cbox.operator("view3d.ke_overlays", text="Face Orientation", icon="FACESEL", depress=True).overlay = "FACEORIENT"
        else:
            cbox.operator("view3d.ke_overlays", text="Face Orientation", icon="FACESEL", depress=False).overlay = "FACEORIENT"

        if o.show_weight:
            cbox.operator("view3d.ke_overlays", text="Vertex Weights", icon="GROUP_VERTEX", depress=True).overlay = "WEIGHT"
        else:
            cbox.operator("view3d.ke_overlays", text="Vertex Weights", icon="GROUP_VERTEX", depress=False).overlay = "WEIGHT"


        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3
        cbox.operator("view3d.ke_overlays", text="All Overlays", icon="OVERLAY").overlay = "ALL"
        cbox.separator()
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


class VIEW3D_MT_PIE_ke_orientpivot(Menu):
    bl_label = "keOrientPivot"
    bl_idname = "VIEW3D_MT_ke_pie_orientpivot"

    def draw(self, context):
        mode = bpy.context.mode
        obj = context.active_object
        layout = self.layout
        pie = layout.menu_pie()

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3
        cbox.prop(context.scene.transform_orientation_slots[0], "type", expand=True)
        cbox.separator()
        cbox.separator()
        cbox.operator("view3d.ke_opc", text=" O&P Combo 3  ", icon="HANDLETYPE_FREE_VEC").combo = "3"

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3

        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='BOUNDING_BOX_CENTER')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='CURSOR')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='INDIVIDUAL_ORIGINS')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='MEDIAN_POINT')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='ACTIVE_ELEMENT')
        if (obj is None) or (mode in {'OBJECT', 'POSE', 'WEIGHT_PAINT'}):
            cbox.prop(context.scene.tool_settings, "use_transform_pivot_point_align")
        else:
            cbox.separator()
            cbox.separator()
        cbox.separator()
        cbox.separator()
        cbox.operator("view3d.ke_opc", text="O&P Combo 4", icon="HANDLETYPE_FREE_VEC").combo = "4"

        # pie.separator()
        pie.operator("view3d.ke_opc", text="O&P Combo 1", icon="KEYTYPE_BREAKDOWN_VEC").combo = "1"
        pie.operator("view3d.ke_opc", text="O&P Combo 2", icon="KEYTYPE_JITTER_VEC").combo = "2"


def get_shading(context):
    # Get settings from 3D viewport or OpenGL render engine
    view = context.space_data
    if view.type == 'VIEW_3D':
        return view.shading
    else:
        # return context.scene.display.shading
        return None


class VIEW3D_MT_PIE_ke_shading(Menu):
    bl_space_type = 'VIEW_3D'
    bl_label = "keShading"
    bl_idname = "VIEW3D_MT_ke_pie_shading"

    @classmethod
    def poll(cls, context):
        # return context.space_data.type == "VIEW_3D"
        shading = get_shading(context)
        engine = context.scene.render.engine
        return shading.type in {'SOLID', 'MATERIAL'} or engine == 'BLENDER_EEVEE' and shading.type == 'RENDERED'

    def draw(self, context):
        view = context.space_data
        layout = self.layout

        shading = get_shading(context)
        if shading is None:
            return {'CANCELLED'}
        pie = layout.menu_pie()

        # SLOT --------------------------------------------------------------------------------
        pie.prop(view.shading, "type", expand=True)

        # SLOT --------------------------------------------------------------------------------
        if shading.type == 'RENDERED':
            c = pie.row()
            col = c.box().column()
            col.prop(shading, "use_scene_lights")
            col.prop(shading, "use_scene_world")
            col.separator()
            col.prop(shading, "render_pass", text="")

            spacer = c.column()
            spacer.label(text="")
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
                    sub.scale_y = 0.6  # smaller studiolight preview
                    sub.template_icon_view(shading, "studio_light", scale_popup=3.0)
                else:
                    sub.prop(
                        system,
                        "use_studio_light_edit",
                        text="Disable Studio Light Edit",
                        icon='NONE',
                        toggle=True,
                    )

                # Todo: When using search, blender spams "unsupported rna type" etc for these props. MEH!
                # sub2 = sub.column()
                # sub2.scale_y = 1.8
                # sub2.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
                # sub2.prop(shading, "use_world_space_lighting", text="", icon='WORLD', toggle=True)
                # # sub2.active = shading.use_world_space_lighting
                # sub2.prop(shading, "studiolight_rotate_z", text="")


            elif shading.light == 'MATCAP':
                sub.scale_y = 0.6  # smaller matcap preview
                sub.template_icon_view(shading, "studio_light", scale_popup=3.0)

                sub = sub.column()
                sub.scale_y = 1.8
                sub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
                sub.operator("view3d.toggle_matcap_flip", emboss=False, text="", icon='ARROW_LEFTRIGHT')


        elif shading.type == 'RENDERED' and not shading.use_scene_world:
            spacer = pie.row()
            spacer.label(text="")

            col = spacer.box().column()
            sub = col.row()
            sub.scale_y = 0.6
            sub.template_icon_view(shading, "studio_light", scale_popup=3)

            # Todo: When using search, blender spams "unsupported rna type" etc for these props. MEH!
            # sub2 = sub.column()
            # sub2.scale_y = 1.8
            # sub2.prop(shading, "studiolight_rotate_z", text="")
            # sub2.prop(shading, "studiolight_intensity", text="")
            # sub2.prop(shading, "studiolight_background_alpha", text="")
            #
            psub = sub.column()
            psub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')

        else:
            pie.separator()


        # SLOT --------------------------------------------------------------------------------
        if shading.type == 'MATERIAL':
            c = pie.row()
            col = c.box().column()
            col.prop(shading, "use_scene_lights")
            col.prop(shading, "use_scene_world")
            col.separator()
            col.prop(shading, "render_pass", text="")

            spacer = c.column()
            spacer.label(text="")
        else:
            pie.separator()


        # SLOT --------------------------------------------------------------------------------
        c = pie.row()
        spacer = c.column()

        if shading.type == 'SOLID':
            spacer.label(text="")
            col = c.box().column()
            lights = col.row()
            lights.prop(shading, "light", expand=True)
            col.separator()
            col.grid_flow(columns=3, align=True).prop(shading, "color_type", expand=True)
            if shading.color_type == 'SINGLE':
                col.column().prop(shading, "single_color", text="")

            opt = c.box().column()
            opt.prop(shading, "show_cavity", text="Cavity")
            opt.prop(shading, "show_specular_highlight", text="Specular")


        elif shading.type == 'MATERIAL':
            if not shading.use_scene_world:
                spacer.label(text="")

                col = c.box().column()
                sub = col.row()
                sub.scale_y = 0.6
                sub.template_icon_view(shading, "studio_light", scale_popup=3)

                # Todo: When using search, blender spams "unsupported rna type" etc for these props. MEH!
                # sub2 = sub.column()
                # sub2.scale_y = 1.4
                # sub2.prop(shading, "studiolight_rotate_z", text="")
                # sub2.prop(shading, "studiolight_intensity", text="")
                # sub2.prop(shading, "studiolight_background_alpha", text="")
                # sub2.prop(shading, "studiolight_background_blur", text="")

                psub = sub.column()
                psub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')


# class VIEW3D_MT_PIE_ke_testpie(Menu):
#     bl_label = "keTestPie"
#     bl_idname = "VIEW3D_MT_ke_pie_test"
#
#     def draw(self, context):
#         layout = self.layout
#         pie = layout.menu_pie()
#         pie.operator("view3d.ke_get_set_material", text="Get Material", icon="MATERIAL").offset = (-168,0)
#



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
    VIEW3D_MT_PIE_ke_shading,
    VIEW3D_MT_PIE_ke_align,
    VIEW3D_MT_PIE_ke_fitprim,
    VIEW3D_MT_PIE_ke_subd
    )

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
