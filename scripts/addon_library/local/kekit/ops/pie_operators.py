from math import radians
import bpy
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
        elif v in cls.mirror_ops:
            return "Mirror modifer ops (with bisect added presets)"
        else:
            return "To-do: Description"

    def execute(self, context):
        k = get_prefs()
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
        # Note: Re-using 'VG' naming for EDGE GROUPS...
        elif self.op == "SUBD":
            bpy.ops.object.modifier_add(type='SUBSURF')
            s = active.modifiers[-1]
            s.name = "SubD"
            s.levels = 3
            s.render_levels = 3
            s.boundary_smooth = 'PRESERVE_CORNERS'

        elif self.op == "W_BEVEL":
            bpy.ops.object.modifier_add(type='BEVEL')
            b = active.modifiers[-1]
            b.name = "WBevel"
            b.width = 0.01
            b.limit_method = 'WEIGHT'
            b.miter_outer = 'MITER_ARC'
            if k.korean:
                b.profile = 1
                b.segments = 2
            else:
                b.segments = 3
            bpy.ops.object.modifier_move_to_index(modifier=b.name, index=0)

        elif self.op == "ANGLE_BEVEL":
            bpy.ops.object.modifier_add(type='BEVEL')
            b = active.modifiers[-1]
            b.name = "ABevel"
            b.width = 0.005
            b.limit_method = 'ANGLE'
            b.angle_limit = 1.0472
            b.miter_outer = 'MITER_ARC'
            if k.korean:
                b.profile = 1
                b.segments = 2
            else:
                b.segments = 3

        elif "VG_BEVEL" in self.op:
            n = str(self.op).split("¤")[1]
            bpy.ops.object.modifier_add(type='BEVEL')
            b = active.modifiers[-1]
            b.name = n
            b.width = 0.005
            b.miter_outer = 'MITER_ARC'
            b.limit_method = 'VGROUP'
            b.vertex_group = n
            if k.korean:
                b.profile = 1
                b.segments = 2
            else:
                b.segments = 3

        elif "ADD_VG" in self.op:
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

        elif self.op == "SOLIDIFY":
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            m = active.modifiers[-1]
            m.name = "kSolidify"
            m.thickness = -0.01

        elif self.op == "WEIGHTED_NORMAL":
            context.object.data.use_auto_smooth = True
            bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')
            m = active.modifiers[-1]
            m.name = "kWeightedN"
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
            context.object.data.use_auto_smooth = True
            bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')
            m = active.modifiers[-1]
            m.name = "kWeightedN"
            m.keep_sharp = True

        # AUTO SORT
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

        elif self.cmd == "CLEAR_LR":
            bpy.ops.object.location_clear(clear_delta=False)
            bpy.ops.object.rotation_clear(clear_delta=False)

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

        elif context.mode == "OBJECT":

            if self.overlay == "WIRE":
                o.show_wireframes = not o.show_wireframes

            elif self.overlay == "WIREFRAMES":
                o.show_wireframes = not o.show_wireframes

        return {'FINISHED'}
