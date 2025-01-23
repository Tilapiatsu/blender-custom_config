from math import radians
import bpy
import bmesh
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
from .._utils import get_prefs, wempty


class KeCallPie(Operator):
    """Custom Pie Operator with preset (temp) hotkey"""
    bl_idname = "ke.call_pie"
    bl_label = "keCallPie"

    name: StringProperty()

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            bpy.ops.wm.call_menu_pie(name='%s' % self.name)
        return {'FINISHED'}


class KePieOps(Operator):
    bl_idname = "ke.pieops"
    bl_label = "Pie Operators"
    bl_options = {'REGISTER', 'INTERNAL'}

    op: StringProperty(default="GRID")
    mirror_ops = {"MIRROR_X", "MIRROR_Y", "MIRROR_Z", "MIRROR_W", "REM_MIRROR_W", "SYM_X", "SYM_Y", "SYM_Z"}
    mname: StringProperty(default="None")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

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
            vgop = str(v).split("¤")[1]
            if vgop == "SEL":
                return "Select elements in group"
            elif vgop == "DSEL":
                return "Deselect elements in group"
            elif vgop == "REM":
                return "Remove selected elements from group"
            elif vgop == "DEL":
                return "Delete group"
        elif v[:6] == "ADD_VG":
            if len(v) > 6:
                return "Add selected elements to group"
            else:
                return "Add new group"
        elif v[:4] == "OPEG":
            egop = str(v).split("¤")[1]
            if egop == "ADD":
                return "Add elements to group"
            if egop == "SEL":
                return "Select elements in group"
            elif egop == "DSEL":
                return "Deselect elements in group"
            elif egop == "REM":
                return "Remove selected elements from group"
            elif egop == "DEL":
                return "Delete group"
        elif v in cls.mirror_ops:
            return "Mirror modifer ops (with bisect added presets)"
        else:
            return "To-do: Description"

    def execute(self, context):
        k = get_prefs()
        run_bevel_tweaker = k.bt_auto
        new_bevel = False
        mode = str(context.mode)
        active = context.active_object
        # Check for Auto Add WN for Bevels
        wmod = [m for m in active.modifiers if m.type == "WEIGHTED_NORMAL"]

        #
        # ABSOLUTE GRID TOGGLE
        #
        if self.op == "GRID":
            context.tool_settings.use_snap_grid_absolute = not context.tool_settings.use_snap_grid_absolute
            return {'FINISHED'}

        #
        # MISC
        #
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
            m = active.modifiers.new("SubD", "SUBSURF")
            m.levels = k.vp_level
            m.render_levels = k.render_level
            m.boundary_smooth = 'PRESERVE_CORNERS'

        elif self.op == "W_BEVEL":
            m = active.modifiers.new("WBevel", "BEVEL")
            m.width = 0.01
            m.limit_method = 'WEIGHT'
            m.miter_outer = 'MITER_ARC'
            if k.korean:
                m.profile = 1
                m.segments = 2
            else:
                m.segments = k.cb_seg
            new_bevel = True

        elif self.op == "ANGLE_BEVEL":
            m = active.modifiers.new("ABevel", "BEVEL")
            m.width = 0.005
            m.limit_method = 'ANGLE'
            m.angle_limit = 1.0472
            m.miter_outer = 'MITER_ARC'
            if k.korean:
                m.profile = 1
                m.segments = 2
            else:
                m.segments = k.cb_seg
            new_bevel = True

        elif "VG_BEVEL" in self.op:
            n = str(self.op).split("¤")[1]
            m = active.modifiers.new(n, "BEVEL")
            m.width = 0.005
            m.miter_outer = 'MITER_ARC'
            m.limit_method = 'VGROUP'
            m.vertex_group = n
            if k.korean:
                m.profile = 1
                m.segments = 2
            else:
                m.segments = k.cb_seg
            new_bevel = True

        elif "ADD_VG" in self.op:
            # todo: TBD if vgroup ops can be less reliant on bpy.ops - macro-fest?
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
            if mode != "EDIT_MESH":
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.vertex_group_remove_from(use_all_groups=True)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                bpy.ops.object.vertex_group_remove_from(use_all_groups=True)

        elif "OPVG" in self.op:
            # Op Vertex Group
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

        elif "OPEG" in self.op:
            # Op Edge Group
            _op, action, attr_name = str(self.op).split("¤")
            bm = bmesh.from_edit_mesh(active.data)
            eg_layer = bm.edges.layers.float.get(attr_name)

            if action == "NEW":
                new = active.data.attributes.new(name=attr_name, type="FLOAT", domain="EDGE")
                eg_layer = bm.edges.layers.float.get(new.name)
                m = active.modifiers.new("WBevel", "BEVEL")
                m.width = 0.01
                m.limit_method = 'WEIGHT'
                m.miter_outer = 'MITER_ARC'

                if k.korean:
                    m.profile = 1
                    m.segments = 2
                else:
                    m.segments = k.cb_seg
                m.edge_weight = new.name

                for e in (e for e in bm.edges if e.select):
                    e[eg_layer] = 1
                new_bevel = True

            if mode == "EDIT_MESH":
                if action == "ADD":
                    for e in (e for e in bm.edges if e.select):
                        e[eg_layer] = 1

                elif action == "SEL":
                    for e in bm.edges:
                        if e[eg_layer]:
                            e.select = True

                elif action == "DSEL":
                    for e in bm.edges:
                        if e[eg_layer]:
                            e.select = False

                elif action == "REM":
                    for e in (e for e in bm.edges if e.select):
                        e[eg_layer] = 0

                elif action == "DEL":
                    attr = active.data.attributes[attr_name]
                    try:
                        active.data.attributes.remove(attr)
                    except Exception as e:
                        print("Error while removing edge attribute:", e)

            bmesh.update_edit_mesh(active.data)

        if new_bevel and run_bevel_tweaker:
            bpy.ops.view3d.ke_bevel_tweaker('INVOKE_DEFAULT', skip_pie=True)

        # elif self.op == "LATTICE":
        #     print("WIP - Lattice" ??)

        elif self.op in {"MOD_EDIT_VIS", "SUBD_EDIT_VIS", "MOD_VIS"}:
            # from addon tools:
            # avoid toggling not exposed modifiers (currently only Collision, see T53406)
            skip_type = ["COLLISION"]
            limited = []
            if self.op == "SUBD_EDIT_VIS":
                limited.append("SUBSURF")
            # check if the active object has only one non-exposed modifier as the logic will fail
            if len(context.active_object.modifiers) == 1 and \
                    context.active_object.modifiers[0].type in skip_type:
                pass
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

        elif self.op in self.mirror_ops:
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
                m = active.modifiers.new("Mirror", "MIRROR")
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

        elif self.op == "SOLIDIFY":
            m = active.modifiers.new("kSolidify", "SOLIDIFY")
            m.thickness = -0.01

        elif self.op == "WEIGHTED_NORMAL":
            if bpy.app.version < (4, 1):
                active.data.use_auto_smooth = True
            m = active.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
            m.keep_sharp = True
            # Set as bool:
            wmod = True

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

        # Auto Add WN if Bevel Added
        if self.op in {"W_BEVEL", "ANGLE_BEVEL", "VG_BEVEL"} and not wmod:
            if bpy.app.version < (4, 1):
                active.data.use_auto_smooth = True
                m = active.modifiers.new("kWeightedN", "WEIGHTED_NORMAL")
                m.keep_sharp = True

        # AUTO SORT (LEGACY)
        if bpy.app.version < (4, 1):
            bpy.ops.ke.mod_order(obj_name=active.name, mod_type='WEIGHTED_NORMAL', top=False)

        return {'FINISHED'}


class KeObjectOp(Operator):
    bl_idname = "object.ke_object_op"
    bl_label = "Object Control"
    bl_description = "Misc pie menu ops & such"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    cmd: StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.object is not None

    @classmethod
    def description(cls, context, properties):
        v = properties.cmd
        if "AS" in v:
            return "Auto-smooth Angle"
        elif "CLEAR" in v:
            return "Clear Values"
        elif v == "SCL_APPLY":
            return "Apply Scale"
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
            if bpy.app.version < (4, 1):
                sel = [o for o in context.selected_objects if o.type == "MESH"]
                v = radians(30)
                if self.cmd == "AS_180":
                    v = radians(180)
                elif self.cmd == "AS_60":
                    v = radians(60)
                if self.cmd == "AS_45":
                    v = radians(45)

                if len(sel) > 1:
                    for o in sel:
                        o.data.auto_smooth_angle = v
                else:
                    context.object.data.auto_smooth_angle = v
            else:
                print("N/A - Only for pre 4.1")

        elif self.cmd == "SCL_APPLY":
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        return {"FINISHED"}


class KeOverlays(Operator):
    bl_idname = "view3d.ke_overlays"
    bl_label = "Overlay Options & Toggles"
    bl_description = "Overlay Options & Toggles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    overlay: EnumProperty(
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

        # elif context.mode == "OBJECT":
        if self.overlay == "WIRE":
            o.show_wireframes = not o.show_wireframes

        elif self.overlay == "WIREFRAMES":
            o.show_wireframes = not o.show_wireframes

        return {'FINISHED'}


class KeModFocus(Operator):
    bl_idname = "view3d.ke_modfocus"
    bl_label = "Modifier Focus"
    bl_description = ("Opens Modifier Tab in Properties Panel\n"
                      "& stacks all modifers except 'focus' modifier (set as Active + Expanded)")
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER'}

    modname: StringProperty(default="", options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        # Only open modifier tab if not already open
        p_area = None
        m_active = False
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.ui_type == 'PROPERTIES':
                    p_area = area
                    if area.spaces.active.context == 'MODIFIER':
                        m_active = True
                        break

        if not m_active and p_area:
            p_area.spaces.active.context = 'MODIFIER'
        elif not m_active and not p_area:
            self.report({"INFO"}, "No Properties panel found in UI")
            return {"CANCELLED"}

        obj = context.active_object
        modifiers = obj.modifiers
        target_mod = modifiers.get(self.modname)

        if len(modifiers) and target_mod:
            for mod in modifiers:
                if mod.name == target_mod.name:
                    mod.show_expanded = True
                    mod.is_active = True
                else:
                    mod.show_expanded = False
        else:
            print("No modifier to focus. Somehow.")
            return {'CANCELLED'}

        for area in context.screen.areas:
            area.tag_redraw()

        return {'FINISHED'}
