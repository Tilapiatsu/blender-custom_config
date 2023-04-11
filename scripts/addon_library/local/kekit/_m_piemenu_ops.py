import math

import bpy
from bpy.types import Panel, Operator
from ._utils import wempty
from . import _pie_menus


#
# MODULE UI
#
class UIPieMenusModule(Panel):
    bl_idname = "UI_PT_M_PIEMENUS_KEKIT"
    bl_label = "Pie Menus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        m_modeling = context.preferences.addons[__package__].preferences.m_modeling
        m_selection = context.preferences.addons[__package__].preferences.m_selection
        m_fitprim = context.preferences.addons[__package__].preferences.m_fitprim
        m_bookmarks = context.preferences.addons[__package__].preferences.m_bookmarks
        m_multicut = context.preferences.addons[__package__].preferences.m_multicut
        m_idmaterials = context.preferences.addons[__package__].preferences.m_idmaterials

        layout = self.layout
        pie = layout.column()
        # pie.operator("wm.call_menu", text="keAdd", icon="DOT").name = "VIEW3D_MT_ke_add"
        pie.operator("ke.call_pie", text="keShading", icon="DOT").name = "KE_MT_shading_pie"

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="keSnapping", icon="DOT").name = "VIEW3D_MT_ke_pie_snapping"
        else:
            row.enabled = False
            row.label(text="keSnapping N/A")

        row = pie.row(align=True)
        if m_selection:
            row.operator("wm.call_menu_pie", text="keStepRotate", icon="DOT").name = "VIEW3D_MT_ke_pie_step_rotate"
        else:
            row.enabled = False
            row.label(text="keStepRotate N/A")

        row = pie.row(align=True)
        if m_modeling:
            row.operator("wm.call_menu_pie", text="keFit2Grid", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid"
            row.operator("wm.call_menu_pie", text="F2G Micro", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid_micro"
        else:
            row.enabled = False
            row.label(text="keFit2Grid N/A")

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="keOrientPivot", icon="DOT").name = "VIEW3D_MT_ke_pie_orientpivot"
        else:
            row.enabled = False
            row.label(text="keOrientPivot N/A")

        pie.operator("wm.call_menu_pie", text="keOverlays", icon="DOT").name = "VIEW3D_MT_ke_pie_overlays"

        row = pie.row(align=True)
        if m_modeling and m_selection:
            row.operator("wm.call_menu_pie", text="keSnapAlign", icon="DOT").name = "VIEW3D_MT_ke_pie_align"
        else:
            row.enabled = False
            row.label(text="keSnapAlign N/A")

        row = pie.row(align=True)
        if m_fitprim:
            row.operator("wm.call_menu_pie", text="keFitPrim", icon="DOT").name = "VIEW3D_MT_ke_pie_fitprim"
            row.operator("wm.call_menu_pie", text="+Add", icon="DOT").name = "VIEW3D_MT_ke_pie_fitprim_add"
        else:
            row.enabled = False
            row.label(text="keFitPrim N/A")

        pie.operator("wm.call_menu_pie", text="keSubd", icon="DOT").name = "VIEW3D_MT_ke_pie_subd"

        row = pie.row(align=True)
        if m_idmaterials:
            row.operator("wm.call_menu_pie", text="keMaterials", icon="DOT").name = "VIEW3D_MT_PIE_ke_materials"
        else:
            row.enabled = False
            row.label(text="keMaterials N/A")

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="View&CursorBookmarks",
                         icon="DOT").name = "VIEW3D_MT_ke_pie_vcbookmarks"
        else:
            row.enabled = False
            row.label(text="View&CursorBookmarks N/A")

        row = pie.row(align=True)
        if m_multicut:
            row.operator("wm.call_menu_pie", text="keMultiCut", icon="DOT").name = "VIEW3D_MT_ke_pie_multicut"
        else:
            row.enabled = False
            row.label(text="keMultiCut N/A")

        row = pie.row(align=True)
        row.operator("wm.call_menu_pie", text="keMisc", icon="DOT").name = "VIEW3D_MT_ke_pie_misc"


class UIPieMenusBlender(Panel):
    bl_idname = "UI_PT_M_PIEMENUS_BLENDER"
    bl_label = "Blender Default Pie Menus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_PIEMENUS_KEKIT"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie().column()
        pie.operator("wm.call_menu_pie", text="Falloffs Pie",
                     icon="DOT").name = "VIEW3D_MT_proportional_editing_falloff_pie"
        pie.operator("wm.call_menu_pie", text="View Pie", icon="DOT").name = "VIEW3D_MT_view_pie"
        pie.operator("wm.call_menu_pie", text="Pivot Pie", icon="DOT").name = "VIEW3D_MT_pivot_pie"
        pie.operator("wm.call_menu_pie", text="Orientation Pie", icon="DOT").name = "VIEW3D_MT_orientations_pie"
        pie.operator("wm.call_menu_pie", text="Shading Pie", icon="DOT").name = "VIEW3D_MT_shading_pie"
        pie.operator("wm.call_menu_pie", text="Snap Pie", icon="DOT").name = "VIEW3D_MT_snap_pie"
        pie.operator("wm.call_menu_pie", text="UV: Snap Pie", icon="DOT").name = "IMAGE_MT_uvs_snap_pie"
        pie.separator()
        pie.operator("wm.call_menu_pie", text="Clip: Tracking", icon="DOT").name = "CLIP_MT_tracking_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Solving", icon="DOT").name = "CLIP_MT_solving_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Marker", icon="DOT").name = "CLIP_MT_marker_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Reconstruction", icon="DOT").name = "CLIP_MT_reconstruction_pie"


#
# MODULE OPERATORS (MISC)
#
class KeCallPie(bpy.types.Operator):
    """Custom Pie Operator with preset (temp) hotkey"""
    bl_idname = "ke.call_pie"
    bl_label = "keCallPie"

    name: bpy.props.StringProperty()

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            bpy.ops.wm.call_menu_pie(name='%s' % self.name)
        return {'FINISHED'}


class KeSnapElement(Operator):
    bl_idname = "ke.snap_element"
    bl_label = "Snap Element"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[("INCREMENT", "Increment", "", "", 1),
               ("VERTEX", "Vertex", "", "", 2),
               ("EDGE", "Edge", "", "", 3),
               ("FACE", "Face", "", "", 4),
               ("VOLUME", "Volume", "", "", 5),
               ("EDGE_MIDPOINT", "Edge Midpoint", "", "", 6),
               ("EDGE_PERPENDICULAR", "Edge Perpendicular", "", "", 7),
               ],
        name="Snap Element",
        default="INCREMENT", options={"HIDDEN"})

    def execute(self, context):
        ct = context.scene.tool_settings
        ct.use_snap = True
        ct.snap_elements = {self.mode}
        return {'FINISHED'}


class KePieOps(Operator):
    bl_idname = "ke.pieops"
    bl_label = "Pie Operators"
    bl_options = {'REGISTER', 'INTERNAL'}

    op: bpy.props.StringProperty(default="GRID")
    mirror_ops = {"MIRROR_X", "MIRROR_Y", "MIRROR_Z", "MIRROR_W", "REM_MIRROR_W", "SYM_X", "SYM_Y", "SYM_Z"}
    mname: bpy.props.StringProperty(default="None")

    @classmethod
    def description(cls, context, properties):
        v = properties.op
        if v == "MOD_VIS":
            return "Toggle All Modifiers Viewport Visibility"
        elif v == "MOD_EDIT_VIS":
            return "Toggle All Modifiers Edit-Mode Visibility"
        elif v == "SUBD_EDIT_VIS":
            return "Toggle Subd Modifiers Edit-Mode Visibility"
        elif v == "GRID":
            return "Toggle Absolute Grid"
        elif v == "CLEAR_VG":
            return "Remove selected elements from *ALL* Bevel Vertex Groups"
        elif v[:4] == "OPVG":
            return "Select verts, Deselect verts, Remove selected (from VG), Delete VG"
        elif v in cls.mirror_ops:
            return "Mirror modifer ops (with bisect added presets)"
        else:
            return "To-do: Description"

    def execute(self, context):
        mode = str(context.mode)
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        active = context.active_object
        if sel_obj:
            sel_obj = [i for i in sel_obj if i != active]

        #
        # ABSOLUTE GRID TOGGLE
        #
        if self.op == "GRID":
            context.tool_settings.use_snap_grid_absolute = not context.tool_settings.use_snap_grid_absolute
            return {'FINISHED'}

        #
        # MISC
        #
        if sel_obj or active:

            if "APPLY" in self.op:
                mod_name = str(self.op).split("¤")[1]
                if mode == "EDIT_MESH":
                    bpy.ops.object.mode_set(mode="OBJECT")
                for mod in [m for m in active.modifiers if m.name == mod_name]:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                if mode == "EDIT_MESH":
                    bpy.ops.object.mode_set(mode="EDIT")

            elif "DELETE" in self.op:
                mod_name = str(self.op).split("¤")[1]
                for mod in [m for m in active.modifiers if m.name == mod_name]:
                    bpy.ops.object.modifier_remove(modifier=mod.name)

            #
            # BEVEL WEIGHTS
            #
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

            #
            # CREASE
            #
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

            #
            # MODIFIERS
            #
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
                    if context.preferences.addons[__package__].preferences.korean:
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
                    if context.preferences.addons[__package__].preferences.korean:
                        b.profile = 1
                        b.segments = 2
                    else:
                        b.segments = 3

            elif "VG_BEVEL" in self.op:
                if active:
                    n = str(self.op).split("¤")[1]
                    bpy.ops.object.modifier_add(type='BEVEL')
                    b = active.modifiers[-1]
                    b.name = n
                    b.width = 0.005
                    b.limit_method = 'VGROUP'
                    b.vertex_group = n
                    if context.preferences.addons[__package__].preferences.korean:
                        b.profile = 1
                        b.segments = 2
                    else:
                        b.segments = 3

            elif "ADD_VG" in self.op:
                if active:
                    assign_mode = False

                    if "¤" in self.op:
                        n = str(self.op).split("¤")[1]
                        bpy.ops.object.vertex_group_set_active(group=n)
                        # active.vertex_groups.active_index = active.vertex_groups[n].index
                        assign_mode = True

                    if mode != "EDIT_MESH":
                        bpy.ops.object.mode_set(mode="EDIT")
                        bpy.ops.mesh.select_all(action='SELECT')
                        if not assign_mode:
                            active.vertex_groups.new(name="V_G")
                        bpy.ops.object.vertex_group_assign()
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode="OBJECT")
                    else:
                        if assign_mode:
                            bpy.ops.object.vertex_group_assign()
                        else:
                            active.vertex_groups.new(name="V_G")
                            bpy.ops.object.vertex_group_assign()

            elif self.op == "CLEAR_VG":
                if active:
                    if mode != "EDIT_MESH":
                        bpy.ops.object.mode_set(mode="EDIT")
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.object.vertex_group_remove_from(use_all_groups=True)
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode="OBJECT")
                    else:
                        bpy.ops.object.vertex_group_remove_from(use_all_groups=True)

            elif "OPVG" in self.op:
                if active:
                    op = str(self.op).split("¤")
                    n = op[2]
                    action = op[1]
                    if n == "V_G":
                        name = n
                    else:
                        name = "V_G." + n
                    bpy.ops.object.vertex_group_set_active(group=name)

                    if mode == "EDIT_MESH":
                        if action == "SEL":
                            bpy.ops.object.vertex_group_select()
                        elif action == "DSEL":
                            bpy.ops.object.vertex_group_deselect()
                        elif action == "REM":
                            bpy.ops.object.vertex_group_remove_from(use_all_groups=False)
                    if action == "DEL":
                        bpy.ops.object.vertex_group_remove(all=False)

            # elif self.op == "LATTICE":
            #     print("WIP - Lattice")

            elif self.op in {"MOD_EDIT_VIS", "SUBD_EDIT_VIS", "MOD_VIS"}:
                # hacked from addon tools:
                # avoid toggling not exposed modifiers (currently only Collision, see T53406)
                skip_type = ["COLLISION"]
                limited = []
                if self.op == "SUBD_EDIT_VIS":
                    limited.append("SUBSURF")
                # check if the active object has only one non-exposed modifier as the logic will fail
                if len(context.active_object.modifiers) == 1 and \
                        context.active_object.modifiers[0].type in skip_type:

                    for obj in context.selected_objects:
                        for mod in obj.modifiers:
                            if mod.type in skip_type:
                                continue
                            if limited and mod.type in limited:
                                mod.show_in_editmode = not mod.show_in_editmode
                            elif not limited:
                                if self.op == "MOD_VIS":
                                    mod.show_viewport = not mod.show_viewport
                                else:
                                    mod.show_in_editmode = not mod.show_in_editmode
                else:
                    for obj in context.selected_objects:
                        for mod in obj.modifiers:
                            if mod.type in skip_type:
                                continue
                            if limited and mod.type in limited:
                                mod.show_in_editmode = not mod.show_in_editmode
                            elif not limited:
                                if self.op == "MOD_VIS":
                                    mod.show_viewport = not mod.show_viewport
                                else:
                                    mod.show_in_editmode = not mod.show_in_editmode

            #
            # MIRROR
            #
            elif self.op in self.mirror_ops:
                if active:
                    if self.op == "MIRROR_W" or self.op == "REM_MIRROR_W":
                        e = wempty(context)
                        mods = [m for m in active.modifiers if m.type == "MIRROR"]
                        if mods and e:
                            active_m = [m for m in mods if m.name == self.mname]
                            if active_m:
                                active_m = active_m[0]
                            else:
                                active_m = mods[0]

                            if self.op == "REM_MIRROR_W":
                                active_m.mirror_object = None
                            else:
                                active_m.mirror_object = e
                    else:
                        bpy.ops.object.modifier_add(type='MIRROR')
                        m = active.modifiers[-1]
                        if self.op == "MIRROR_Y":
                            m.use_axis = (False, True, False)
                        elif self.op == "MIRROR_Z":
                            m.use_axis = (False, False, True)
                        elif self.op == "SYM_X":
                            m.use_bisect_axis = (True, False, False)
                        elif self.op == "SYM_Y":
                            m.use_axis = (False, True, False)
                            m.use_bisect_axis = (False, True, False)
                        elif self.op == "SYM_Z":
                            m.use_axis = (False, False, True)
                            m.use_bisect_axis = (False, False, True)

            #
            # SOLIDIFY
            #
            elif self.op == "SOLIDIFY":
                if active:
                    bpy.ops.object.modifier_add(type='SOLIDIFY')
                    m = active.modifiers[-1]
                    m.name = "kSolidify"
                    m.thickness = -0.01

            #
            # SOLIDIFY
            #
            elif self.op == "WEIGHTED_NORMAL":
                if active:
                    context.object.data.use_auto_smooth = True
                    bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')
                    m = active.modifiers[-1]
                    m.name = "kWeightedN"
                    m.keep_sharp = True

            #
            # SHADING
            #
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

        #
        # AUTO SORT MODIFIERS (Just n-weight for now)
        #
        for m in active.modifiers:
            if m.type == "WEIGHTED_NORMAL":
                bpy.ops.object.modifier_move_to_index(modifier=m.name, index=len(active.modifiers) - 1)

        return {'FINISHED'}


class KeOverlays(Operator):
    bl_idname = "view3d.ke_overlays"
    bl_label = "Overlay Options & Toggles"
    bl_description = "Overlay Options & Toggles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    overlay: bpy.props.EnumProperty(
        items=[("WIRE", "Show Wireframe", "", 1),
               ("EXTRAS", "Show Extras", "", 2),
               ("SEAMS", "Show Edge Seams", "", 3),
               ("SHARP", "Show Edge Sharp", "", 4),
               ("CREASE", "Show Edge Crease", "", 5),
               ("BEVEL", "Show Edge Bevel Weight", "", 6),
               ("FACEORIENT", "Show Face Orientation", "", 7),
               ("INDICES", "Show Indices", "", 8),
               ("ALLEDIT", "Toggle Edit Overlays", "", 9),
               ("ALL", "Toggle Overlays", "", 10),
               ("VN", "Vertex Normals", "", 11),
               ("SN", "Split Normals", "", 12),
               ("FN", "Face Normals", "", 13),
               ("BACKFACE", "Backface Culling", "", 14),
               ("ORIGINS", "Show Origins", "", 15),
               ("CURSOR", "Show Cursor", "", 16),
               ("OUTLINE", "Show Selection Outline", "", 17),
               ("WIREFRAMES", "Show Object Wireframes", "", 18),
               ("GRID", "Show Grid (3D View)", "", 19),
               ("OBJ_OUTLINE", "Show Object Outline", "", 20),
               ("WEIGHT", "Show Vertex Weights", "", 21),
               ("BONES", "Show Bones", "", 22),
               ("STATS", "Show Stats", "", 23),
               ("GRID_ORTHO", "Show Ortho Grid", "", 24),
               ("GRID_BOTH", "Show Floor & Ortho Grid", "", 25),
               ("LENGTHS", "Show Lengths", "", 26),
               ("LINES", "Relationship Lines", "", 27),
               ],
        name="Overlay Type",
        default="WIRE")

    def execute(self, context):
        o = context.space_data.overlay
        s = context.space_data.shading

        # Same for Edit mode and Object mode
        if self.overlay == "GRID" or self.overlay == "GRID_BOTH":
            status = o.show_floor
            o.show_floor = not status
            if not o.show_floor:
                o.show_axis_x = False
                o.show_axis_y = False
            # o.show_axis_z = False
            else:
                o.show_axis_x = True
                o.show_axis_y = True
            # o.show_axis_z = False
            if self.overlay == "GRID_BOTH":
                o.show_ortho_grid = not o.show_ortho_grid

        elif self.overlay == "GRID_ORTHO":
            o.show_ortho_grid = not o.show_ortho_grid

        elif self.overlay == "EXTRAS":
            o.show_extras = not o.show_extras

        elif self.overlay == "ALL":
            o.show_overlays = not o.show_overlays

        elif self.overlay == "ORIGINS":
            o.show_object_origins = not o.show_object_origins

        elif self.overlay == "OUTLINE":
            o.show_outline_selected = not o.show_outline_selected

        elif self.overlay == "CURSOR":
            o.show_cursor = not o.show_cursor

        elif self.overlay == "OBJ_OUTLINE":
            s.show_object_outline = not s.show_object_outline

        elif self.overlay == "BACKFACE":
            s.show_backface_culling = not s.show_backface_culling

        elif self.overlay == "FACEORIENT":
            o.show_face_orientation = not o.show_face_orientation

        elif self.overlay == "BONES":
            o.show_bones = not o.show_bones

        elif self.overlay == "STATS":
            o.show_stats = not o.show_stats

        elif self.overlay == "LINES":
            o.show_relationship_lines = not o.show_relationship_lines

        # Mode contextual
        if context.mode == "EDIT_MESH":

            if self.overlay == "SEAMS":
                o.show_edge_seams = not o.show_edge_seams

            elif self.overlay == "SHARP":
                o.show_edge_sharp = not o.show_edge_sharp

            elif self.overlay == "CREASE":
                o.show_edge_crease = not o.show_edge_crease

            elif self.overlay == "BEVEL":
                o.show_edge_bevel_weight = not o.show_edge_bevel_weight

            elif self.overlay == "INDICES":
                o.show_extra_indices = not o.show_extra_indices

            elif self.overlay == "LENGTHS":
                o.show_extra_edge_length = not o.show_extra_edge_length

            elif self.overlay == "ALLEDIT":
                if o.show_edge_seams or o.show_edge_sharp:
                    o.show_edge_seams = False
                    o.show_edge_sharp = False
                    o.show_edge_crease = False
                    o.show_edge_bevel_weight = False
                else:
                    o.show_edge_seams = True
                    o.show_edge_sharp = True
                    o.show_edge_crease = True
                    o.show_edge_bevel_weight = True

            elif self.overlay == "VN":
                o.show_vertex_normals = not o.show_vertex_normals

            elif self.overlay == "SN":
                o.show_split_normals = not o.show_split_normals

            elif self.overlay == "FN":
                o.show_face_normals = not o.show_face_normals

            elif self.overlay == "WEIGHT":
                o.show_weight = not o.show_weight

        elif context.mode == "OBJECT":

            if self.overlay == "WIRE":
                o.show_wireframes = not o.show_wireframes

            elif self.overlay == "WIREFRAMES":
                o.show_wireframes = not o.show_wireframes

        return {'FINISHED'}


def get_og_overlay_ui(c):
    global og_ui
    og_gizmo = c.space_data.show_gizmo_navigate
    og_floor = c.space_data.overlay.show_floor
    og_x = c.space_data.overlay.show_axis_x
    og_y = c.space_data.overlay.show_axis_y
    og_z = c.space_data.overlay.show_axis_z
    og_text = c.space_data.overlay.show_text
    og_extras = c.space_data.overlay.show_extras

    for area in c.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    og_ui = space.show_region_ui
                    og_tb = space.show_region_toolbar

    return [og_gizmo, og_floor, og_x, og_y, og_z, og_text, og_extras, og_ui, og_tb]


class KeObjectOp(Operator):
    bl_idname = "object.ke_object_op"
    bl_label = "Object Control"
    bl_description = "Misc pie menu ops & such"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    cmd: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.object is not None

    @classmethod
    def description(cls, context, properties):
        v = properties.cmd
        if "ROT" in v:
            return "Clear Specified Rotation Axis"
        elif "AS" in v:
            return "Auto-smooth Angle"
        elif v == "CLEAR_LR":
            return "Clear both Location & Rotation"
        else:
            return "Misc pie menu ops & such"

    def execute(self, context):

        if "ROT" in self.cmd:
            if self.cmd == "ROT_CLEAR_X":
                context.object.rotation_euler[0] = 0
            elif self.cmd == "ROT_CLEAR_Y":
                context.object.rotation_euler[1] = 0
            elif self.cmd == "ROT_CLEAR_Z":
                context.object.rotation_euler[2] = 0

        elif "AS" in self.cmd:
            sel = [o for o in context.selected_objects if o.type == "MESH"]
            v = math.radians(30)
            if self.cmd == "AS_180":
                v = math.radians(180)
            elif self.cmd == "AS_60":
                v = math.radians(60)
            if self.cmd == "AS_45":
                v = math.radians(45)

            if len(sel) > 1:
                for o in sel:
                    o.data.auto_smooth_angle = v
            else:
                context.object.data.auto_smooth_angle = v

        elif self.cmd == "CLEAR_LR":
            bpy.ops.object.location_clear(clear_delta=False)
            bpy.ops.object.rotation_clear(clear_delta=False)

        return {"FINISHED"}


#
# MODULE REGISTRATION
#
classes = (
    UIPieMenusModule,
    UIPieMenusBlender,
    KeCallPie,
    KeSnapElement,
    KePieOps,
    KeOverlays,
    KeObjectOp,
)

modules = (
    _pie_menus,
)

addon_keymaps = []


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_piemenus:
        for c in classes:
            bpy.utils.register_class(c)

        for m in modules:
            m.register()

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if kc:
            km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
            kmi = km.keymap_items.new(idname="ke.call_pie", type='ZERO', value='PRESS', ctrl=True, alt=True, shift=True)
            kmi.properties.name = "KE_MT_shading_pie"
            addon_keymaps.append((km, kmi))


def unregister():
    if "bl_rna" in UIPieMenusModule.__dict__:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()

        for c in reversed(classes):
            bpy.utils.unregister_class(c)

        for m in modules:
            m.unregister()


if __name__ == "__main__":
    register()
