from math import radians
from random import randint

import bmesh
import bpy
from bpy_extras.view3d_utils import region_2d_to_location_3d, region_2d_to_vector_3d
from bpy_types import Operator, Panel
from bpy.props import EnumProperty, FloatProperty, BoolProperty
from mathutils import Vector, Quaternion
from mathutils.geometry import distance_point_to_plane
from mathutils.geometry import intersect_ray_tri
from .._utils import (
    average_vector,
    mouse_raycast,
    tri_points_order,
    correct_normal,
    rotation_from_vector,
    get_islands,
    set_status_text,
    get_view_type,
    unparent,
    get_prefs
)


class UIUnrotatorModule(Panel):
    bl_idname = "UI_PT_M_UNROTATOR"
    bl_label = "Unrotator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_GEO"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)
        col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator",
                     icon="ORIENTATION_NORMAL").ke_unrotator_option = "DEFAULT"
        col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator Duplicate", icon="LINKED").ke_unrotator_option = "DUPE"
        col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator RotOnly",
                     icon="ORIENTATION_LOCAL").ke_unrotator_option = "NO_LOC"
        col.separator()
        col.label(text="Options")
        col.prop(k, "unrotator_connect", text="Auto-Select Linked")
        col.prop(k, "unrotator_nolink", text="Object Duplicate Unlinked")
        col.prop(k, "unrotator_nosnap", text="No Object Modal Snapping")
        col.prop(k, "unrotator_invert", text="Invert Rotation")
        col.prop(k, "unrotator_center", text="Center on Face")
        col.prop(k, "unrotator_rndz", text="Randomize Dupe Z")


def get_snap_settings(context):
    ts = context.scene.tool_settings
    s1 = ts.snap_elements
    s2 = ts.snap_target
    s3 = [ts.use_snap_grid_absolute,
          ts.use_snap_backface_culling,
          ts.use_snap_align_rotation,
          ts.use_snap_self,
          ts.use_snap_peel_object,
          ts.use_snap_translate,
          ts.use_snap_rotate,
          ts.use_snap_scale]
    s4 = ts.use_snap
    return [s1, s2, s3, s4]


def set_snap_settings(context, s):
    ts = context.scene.tool_settings
    ts.snap_elements = s[0]
    ts.snap_target = s[1]
    ts.use_snap_grid_absolute = s[2][0]
    ts.use_snap_backface_culling = s[2][1]
    ts.use_snap_align_rotation = s[2][2]
    ts.use_snap_self = s[2][3]
    ts.use_snap_peel_object = s[2][4]
    ts.use_snap_translate = s[2][5]
    ts.use_snap_rotate = s[2][6]
    ts.use_snap_scale = s[2][7]
    ts.use_snap = s[3]


def calc_face_vectors(active, mtx, obj, vcount):
    eks = obj.data.polygons[active.index].edge_keys
    vecs = []
    # Longest vec is tangent
    for vp in eks:
        vc1 = mtx @ obj.data.vertices[vp[0]].co
        vc2 = mtx @ obj.data.vertices[vp[1]].co
        vecs.append(vc1 - vc2)
    short_sort = sorted(vecs)
    # tri is shortest exception
    if vcount == 3:
        vec = short_sort[0]
    else:
        vec = short_sort[-1]
    normal = correct_normal(mtx, active.normal)
    tangent = Vector(vec).normalized()
    return normal, tangent


def ops_move(offset):
    bpy.ops.transform.translate(
        value=offset,
        orient_type='GLOBAL',
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        orient_matrix_type='GLOBAL', mirror=False,
        use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
        proportional_size=1, use_proportional_connected=False,
        use_proportional_projected=False, snap=True, snap_elements={'FACE'},
        use_snap_project=True, snap_target='ACTIVE', use_snap_self=False,
        use_snap_edit=True, use_snap_nonedit=True,
        use_snap_selectable=False, release_confirm=True
    )


class KeUnrotator(Operator):
    bl_idname = "view3d.ke_unrotator"
    bl_label = "Unrotator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    ke_unrotator_option: EnumProperty(
        items=[("DEFAULT", "Default", "", 1),
               ("DUPE", "Duplicate", "", 2),
               ("NO_LOC", "Rotation Only", "", 3)],
        name="Unrotator Options",
        default="DEFAULT"
    )
    rot_offset: FloatProperty(
        name="Rotation Offset",
        default=0,
        min=-360.0,
        max=360.0,
        step=100,
        subtype='ANGLE',
        precision=0
    )
    inv: BoolProperty(name="Invert", default=False)
    center_override: BoolProperty(name="Face Center", default=False)
    rndz: BoolProperty(name="Randomize Dupe Z", default=False)

    center = False
    mouse_pos = Vector((0, 0))
    set_invert = True
    og_snaps = []
    og_pos = Vector((0, 0, 0))
    og_rot = Vector((0, 0, 0))
    modal_snap = [{'FACE'}, 'ACTIVE', [True, False, True, False, False, True, False, False], True]
    used_modal = False
    f_center = Vector((0, 0, 0))
    setrot = None
    temp_children = []
    og_sel = []

    @classmethod
    def description(cls, context, properties):
        if properties.ke_unrotator_option == "DEFAULT":
            return "Unrotates geo using *active element* as new 'bottom' " \
                   "OR aligns to MOUSE OVER face normal on other mesh or object. " \
                   "OBJECT: Clear rotation OR align/place to geo/grid under MOUSE. " \
                   "Note: Rotation tweak (redo-option) may glitch out if you move the viewport"
        elif properties.ke_unrotator_option == "DUPE":
            return "Duplicates before Unrotate operation"
        elif properties.ke_unrotator_option == "NO_LOC":
            return "Unrotates (incl. rotation from mouse-over geo) but does not move selection"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        if not self.used_modal:
            k = get_prefs()
            layout.use_property_split = True
            col = layout.column()
            col.prop(self, "rot_offset")
            row = col.row(align=True)
            row.alignment = "CENTER"
            row.label(text="Options:")
            col.prop(k, "unrotator_connect", text="Auto-Select Linked", toggle=True)
            col.prop(k, "unrotator_invert", text="Invert Rotation", toggle=True)
            col.prop(k, "unrotator_center", text="Center on Face", toggle=True)
            col.prop(k, "unrotator_rndz", text="Randomize Dupe Z", toggle=True)
            sub = col.column(align=True)
            sub.label(text="Note: Redo requires unchanged viewport")

    def parent_tc(self, active, objects):
        parents = [o for o in objects if o.parent is not None]
        self.temp_children = [o for o in objects if o != active]
        if self.temp_children:
            if parents:
                unparent(self.temp_children)
            for o in self.temp_children:
                o.parent = active
                o.matrix_parent_inverse = active.matrix_world.inverted()

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        automerge = False
        self.used_modal = False
        sel_check, place, noloc, place, dupe = False, False, False, False, False
        normal, tangent, place_quat = None, None, None
        mode = context.mode[:]
        sel_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.active_object
        if not obj:
            self.report({"INFO"}, "Unrotator: No Active Object?")
            return {"CANCELLED"}

        if self.ke_unrotator_option == "DUPE":
            dupe, noloc = True, False
        elif self.ke_unrotator_option == "NO_LOC":
            noloc, dupe = True, False

        connect = k.unrotator_connect
        nolink = k.unrotator_nolink
        nosnap = k.unrotator_nosnap
        actual_invert = k.unrotator_invert
        self.center = k.unrotator_center
        self.rndz = k.unrotator_rndz
        rndz_rot = randint(-360, 360) * 3.141592653589793 / 180
        # obj_coll = obj.users_collection[0]
        self.temp_children = []
        self.og_sel = context.selected_objects[:]

        if self.ke_unrotator_option != "DUPE":
            self.rndz = False

        if self.center_override:
            self.center = True

        #
        # Check mouse over target
        #
        bpy.ops.object.mode_set(mode="OBJECT")
        hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos, evaluated=True)
        # print("HIT:", hit_obj, hit_face, hit_normal)

        # View placement compensation & Z0 drop
        if hit_obj is None and hit_face is None:
            view_vec = region_2d_to_vector_3d(context.region, context.space_data.region_3d, self.mouse_pos)
            view_pos = context.space_data.region_3d.view_matrix.inverted().translation
            raypos = []
            snap = 2
            if get_view_type() != "ORTHO":
                ground = ((0, 0, 0), (0, 1, 0), (1, 0, 0))
                raypos = intersect_ray_tri(ground[0], ground[1], ground[2], view_vec, view_pos, False)
            if raypos:
                hit_wloc = Vector((round(raypos[0], snap), round(raypos[1], snap), 0))
            else:
                hit_wloc = region_2d_to_location_3d(context.region, context.space_data.region_3d,
                                                    self.mouse_pos, obj.location)
            place = True
            hit_normal = Vector((0, 0, 1))

        if mode == "OBJECT" and not nosnap:
            self.rot_offset = 0
            self.center = False

        if mode == "EDIT_MESH":
            bpy.ops.object.mode_set(mode="EDIT")

            automerge = bool(context.scene.tool_settings.use_mesh_automerge)
            if automerge:
                context.scene.tool_settings.use_mesh_automerge = False

            # Get selected obj bm
            obj_mtx = obj.matrix_world.copy()
            od = obj.data
            bm = bmesh.from_edit_mesh(od)

            # Check selections
            sel_poly = [p for p in bm.faces if p.select]
            sel_edges = [e for e in bm.edges if e.select]
            sel_verts = [v for v in bm.verts if v.select]
            linked_verts = []

            active_h = bm.select_history.active
            active_point = None

            # Making sure an active element is in the selection
            if sel_mode[1] and sel_edges:
                if active_h not in sel_edges:
                    bm.select_history.add(sel_edges[-1])
                    active_h = bm.select_history.active
                active_point = active_h.verts[0]

            elif sel_mode[0] and sel_verts:
                if active_h not in sel_verts:
                    bm.select_history.add(sel_verts[-1])
                    active_h = bm.select_history.active
                active_point = active_h

            elif sel_mode[2] and sel_poly:
                if active_h not in sel_poly:
                    bm.select_history.add(sel_poly[-1])
                    active_h = bm.select_history.active
                active_point = active_h.verts[0]

            # Verify valid selections
            if len(sel_verts) >= 3 and active_h:
                if sel_mode[0]:
                    sel_check = True
                elif sel_mode[1] and len(sel_edges) >= 2:
                    sel_check = True
                elif sel_mode[2] and len(sel_poly):
                    sel_check = True

            if not sel_check:
                self.report({"INFO"}, "Unrotator: Selection Error - Incorrect/No geo Selected? Active Element?")
                return {"CANCELLED"}

            # Expand Linked, or not
            if connect:
                bpy.ops.mesh.select_linked()
                linked_verts = [v for v in bm.verts if v.select]

            elif not connect:
                linked_verts = sel_verts  # fall-back
                # still calc the linked avg pos
                islands = get_islands(bm, sel_verts)
                for island in islands:
                    if any(v in sel_verts for v in island):
                        linked_verts = island
                        break

            # Linked Selection center pos
            bm.verts.ensure_lookup_table()
            linked_verts_co = [v.co for v in linked_verts]
            avg_pos = obj_mtx @ Vector(average_vector(linked_verts_co))
            sel_cos = [v.co for v in sel_verts]
            avg_sel_pos = obj_mtx @ Vector(average_vector(sel_cos))
            center_d = Vector(avg_sel_pos - avg_pos).normalized()

            # bmdupe
            if dupe:
                bmesh.ops.duplicate(
                    bm, geom=([v for v in bm.verts if v.select] +
                              [e for e in bm.edges if e.select] +
                              [p for p in bm.faces if p.select])
                )

            #
            # Check mouse over target - place check
            #
            if type(hit_face) == int:

                if hit_obj.name == obj.name:
                    bm.faces.ensure_lookup_table()
                    hit_face_verts = bm.faces[hit_face].verts[:]

                    if any(i in hit_face_verts for i in linked_verts):
                        # print("Mouse over same Obj and selected geo - Unrotate only mode")
                        place = False
                    else:
                        # print("Mouse over same Obj but unselected geo - Unrotate & Place in same mesh mode")
                        place = True
                        n, t = calc_face_vectors(bm.faces[hit_face], obj_mtx, obj, len(hit_face_verts))
                        n.negate()
                        place_quat = rotation_from_vector(n, t).to_quaternion()

                        if self.center:
                            bm.faces.ensure_lookup_table()
                            hit_wloc = average_vector([obj_mtx @ v.co for v in hit_face_verts])

                elif hit_obj.name != obj.name:
                    # print("Mouse over different Object - Unrotate & Place mode")
                    place = True
                    hit_face_verts = hit_obj.data.polygons[hit_face].vertices[:]
                    n, t = calc_face_vectors(hit_obj.data.polygons[hit_face], hit_obj.matrix_world, hit_obj,
                                             len(hit_face_verts))
                    n.negate()
                    place_quat = rotation_from_vector(n, t).to_quaternion()

                    if self.center:
                        hit_vcos = [hit_obj.matrix_world @ hit_obj.data.vertices[i].co for i in hit_face_verts]
                        hit_wloc = average_vector(hit_vcos)

            #
            # Selection processing for normal and tangent vecs
            #
            if sel_mode[0]:
                #
                # VERT MODE
                #
                h = tri_points_order([sel_verts[0].co, sel_verts[1].co, sel_verts[2].co])
                # Vectors from 3 points, hypoT ignored
                p1, p2, p3 = obj_mtx @ sel_verts[h[0]].co, obj_mtx @ sel_verts[h[1]].co, obj_mtx @ sel_verts[
                    h[2]].co
                v2 = p3 - p1
                v1 = p2 - p1
                normal = v1.cross(v2).normalized()
                tangent = Vector(v1).normalized()
                # Direction flip check against center mass
                d = normal.dot(center_d)
                if d <= 0:
                    normal.negate()

            elif sel_mode[1]:
                #
                # EDGE MODE
                #
                bm.edges.ensure_lookup_table()
                # Active edge is tangent
                ev = active_h.verts[:]
                ev1, ev2 = ev[0].co, ev[1].co
                tangent = correct_normal(obj_mtx, Vector((ev1 - ev2)).normalized())
                # B-tangent is shortest vec to v1
                c = [v for v in sel_verts if v not in ev]
                vecs = [Vector((ev1 - v.co).normalized()) for v in c]
                v2 = correct_normal(obj_mtx, sorted(vecs)[0])
                # Normal is crossp
                normal = tangent.cross(v2).normalized()
                # Direction flip check against center mass
                d = normal.dot(center_d)
                if d <= 0:
                    normal.negate()

            elif sel_mode[2]:
                #
                # POLY MODE
                #
                normal, tangent = calc_face_vectors(active_h, obj_mtx, obj, len(sel_verts))

            #
            # Process & Execute transforms!
            #
            if actual_invert:
                normal.negate()
            if self.inv:
                normal.negate()

            rotm = rotation_from_vector(normal, tangent)
            rq = rotm.to_quaternion()

            if self.rot_offset != 0:
                rq @= Quaternion((0, 0, 1), self.rot_offset)

            if self.rndz:
                rq @= Quaternion((0, 0, 1), rndz_rot)

            if place_quat is not None:
                qd = place_quat @ rq.inverted()
            else:
                # rot to place at bottom
                rq @= Quaternion((1, 0, 0), radians(-180.0))
                qd = rq.rotation_difference(Quaternion())

            rot = qd.to_euler("XYZ")
            rx, ry, rz = rot.x * -1, rot.y * -1, rot.z * -1

            # Old macro method to avoid non-uniform scale issues...slow, but works.
            bpy.ops.transform.rotate(value=rx, orient_axis='X', orient_type='GLOBAL', use_proportional_edit=False,
                                     snap=False, orient_matrix_type='GLOBAL')
            bpy.ops.transform.rotate(value=ry, orient_axis='Y', orient_type='GLOBAL', use_proportional_edit=False,
                                     snap=False, orient_matrix_type='GLOBAL')
            bpy.ops.transform.rotate(value=rz, orient_axis='Z', orient_type='GLOBAL', use_proportional_edit=False,
                                     snap=False, orient_matrix_type='GLOBAL')

            # Calc offset
            nv = [v.co for v in linked_verts]
            npos = obj_mtx @ Vector(average_vector(nv))

            if place and not noloc:
                # Move & offset placement
                d = distance_point_to_plane(obj_mtx @ active_point.co, npos, hit_normal)
                offset = hit_normal * d
                hit_vec = hit_wloc - (npos + offset)

                bmesh.ops.translate(bm, vec=hit_vec, space=obj_mtx, verts=linked_verts)
                bmesh.update_edit_mesh(obj.data)

            else:
                # Compensate z pos to rot-in-place-ish
                comp = (npos - avg_pos) * -1
                bpy.ops.transform.translate(value=comp)
                bmesh.update_edit_mesh(obj.data)

        elif mode == 'OBJECT':
            d = self.ke_unrotator_option
            self.og_pos = obj.location.copy()
            self.og_rot = Vector(obj.rotation_euler)
            sel_obj = [o for o in context.selected_objects]
            group_select = True if sel_obj else False

            # Multi-object selection check
            group_reset = False
            if hit_obj:
                target_obj = [o for o in sel_obj if o.name == hit_obj.name]
                group_reset = True if target_obj else False

            # Unrotate to grid
            if not hit_obj:
                if dupe:
                    if nolink:
                        bpy.ops.object.duplicate(linked=False)
                    else:
                        bpy.ops.object.duplicate(linked=True)
                    if not group_select:
                        obj.select_set(False)
                        obj = context.active_object

                if group_select:
                    self.parent_tc(obj, sel_obj)
                    offset = hit_wloc - obj.location
                    obj.rotation_euler = (0, 0, self.rot_offset)
                    ops_move(offset)
                else:
                    obj.rotation_euler = (0, 0, self.rot_offset)
                    obj.location = hit_wloc

            elif d != "DUPE" and hit_obj.name == obj.name or group_reset:
                obj.select_set(True)
                obj.rotation_euler = (0, 0, self.rot_offset)
                for o in sel_obj:
                    o.rotation_euler = (0, 0, self.rot_offset)

            # else, Place (and/or dupe)!
            else:
                obj.select_set(True)
                if dupe:
                    if nolink:
                        bpy.ops.object.duplicate(linked=False)
                    else:
                        bpy.ops.object.duplicate(linked=True)
                    obj = context.active_object
                    obj.select_set(True)

                # TEMP-PARENT TO ACTIVE
                if group_select:
                    sel_obj = [o for o in context.selected_objects]
                    self.parent_tc(obj, sel_obj)

                mtx = hit_obj.matrix_world
                eks = hit_obj.data.polygons[hit_face].edge_keys
                vecs = []

                for vp in eks:
                    vc1 = mtx @ hit_obj.data.vertices[vp[0]].co
                    vc2 = mtx @ hit_obj.data.vertices[vp[1]].co
                    vecs.append(vc1 - vc2)

                short_sort = sorted(vecs)
                start_vec = short_sort[0]

                self.setrot = rotation_from_vector(hit_normal, start_vec, rotate90=True, rw=True).to_quaternion()
                self.setrot @= Quaternion((0, 0, 1), self.rot_offset)
                if self.rndz:
                    self.setrot @= Quaternion((0, 0, 1), rndz_rot)

                if noloc or nosnap:
                    obj.rotation_euler = self.setrot.to_euler()
                    context.evaluated_depsgraph_get().update()

                if not noloc:
                    if self.center and nosnap:
                        hit_wloc = hit_obj.matrix_world @ Vector(hit_obj.data.polygons[hit_face].center)

                    # no snapping place only
                    offset = hit_wloc - obj.location

                    # (1st) PLACE
                    ops_move(offset)

                    if not nosnap:
                        # START MODAL w. SNAPPING
                        obj.rotation_euler = self.setrot.to_euler()
                        self.f_center = hit_obj.matrix_world @ Vector(hit_obj.data.polygons[hit_face].center)
                        self.used_modal = True
                        self.og_snaps = get_snap_settings(context)
                        set_snap_settings(context, self.modal_snap)
                        context.window_manager.modal_handler_add(self)
                        bpy.ops.transform.translate('INVOKE_DEFAULT', True)

                        # UPDATE STATUS BAR (MODAL SNAPPING MODE)
                        status_help = [
                            "[LMB / SPACE / ENTER] Apply",
                            "[LMB + SHIFT] Apply on Face Center",
                            "[RMB / ESC] Cancel",
                            "[CTRL] Toggle Snapping",
                            "[X,Y,Z] Toggle Axis Lock",
                            "[Etc.] as Transform Modal"]
                        set_status_text(context, status_help)

                        return {'RUNNING_MODAL'}

        # Selection revert for non-face selections
        if not sel_mode[2] and mode != "OBJECT":
            bpy.ops.mesh.select_all(action='DESELECT')

            if sel_mode[1]:
                bm.edges.ensure_lookup_table()
                for v in sel_edges:
                    bm.edges[v.index].select = True
            elif sel_mode[0]:
                bm.verts.ensure_lookup_table()
                for v in sel_verts:
                    bm.verts[v.index].select = True

            bm.select_history.clear()
            bm.select_history.add(active_h)
            bmesh.update_edit_mesh(obj.data)

        if automerge:
            context.scene.tool_settings.use_mesh_automerge = True

        if mode == "OBJECT" and self.temp_children:
            unparent(self.temp_children)

        return {"FINISHED"}

    def modal(self, context, event):

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            set_snap_settings(context, self.og_snaps)
            if context.mode == "OBJECT":
                context.object.location = self.og_pos
                context.object.rotation_euler = self.og_rot
                if self.ke_unrotator_option == "DUPE":
                    for o in context.selected_objects:
                        bpy.data.objects.remove(o, do_unlink=True)
                    if self.og_sel:
                        for o in self.og_sel:
                            o.select_set(True)
            context.workspace.status_text_set(None)
            context.area.tag_redraw()
            return {'CANCELLED'}

        elif event.shift and event.type == "LEFTMOUSE":
            set_snap_settings(context, self.og_snaps)
            # need to hide the obj to not raycast on it...
            context.object.hide_viewport = True
            self.mouse_pos[0] = event.mouse_region_x
            self.mouse_pos[1] = event.mouse_region_y
            hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos, evaluated=True)
            if hit_face:
                self.f_center = hit_obj.matrix_world @ Vector(hit_obj.data.polygons[hit_face].center)
            context.object.hide_viewport = False
            if self.temp_children:
                context.object.select_set(True)
                context.object.location = self.f_center
                context.evaluated_depsgraph_get().update()
                unparent(self.temp_children)
            else:
                context.object.location = self.f_center
            context.workspace.status_text_set(None)
            context.area.tag_redraw()
            return {"FINISHED"}

        elif event.type in {"LEFTMOUSE", "SPACE", "RETURN"}:
            set_snap_settings(context, self.og_snaps)
            if self.temp_children:
                unparent(self.temp_children)
            context.workspace.status_text_set(None)
            context.area.tag_redraw()
            return {"FINISHED"}

        return {'RUNNING_MODAL'}
