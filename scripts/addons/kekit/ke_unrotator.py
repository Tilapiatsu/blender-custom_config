bl_info = {
    "name": "keUnrotator",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (3, 1, 4),
    "blender": (2, 90, 0),
}

import bpy
import bmesh
from .ke_utils import average_vector, mouse_raycast, tri_points_order, correct_normal, rotation_from_vector, get_islands
from mathutils import Vector, Quaternion
from mathutils.geometry import distance_point_to_plane
from math import radians


class VIEW3D_OT_ke_unrotator(bpy.types.Operator):
    bl_idname = "view3d.ke_unrotator"
    bl_label = "Unrotator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}
    ke_unrotator_option: bpy.props.EnumProperty(
        items=[("DEFAULT", "Default", "", 1),
               ("DUPE", "Duplicate", "", 2),
               ("NO_LOC", "Rotation Only", "", 3)],
        name="Unrotator Options",
        default="DEFAULT")

    rot_offset: bpy.props.FloatProperty(name="Rotation Offset", default=0,
                                        min=-360.0, max=360.0, step=100, subtype='ANGLE', precision=0)
    inv : bpy.props.BoolProperty(name="Invert", default=False)
    center_override : bpy.props.BoolProperty(name="Face Center", default=False)

    center = False
    mouse_pos = Vector((0, 0))
    set_invert = True
    og_snaps = []
    og_pos = Vector((0,0,0))
    modal_snap = [{'FACE'}, 'ACTIVE', [True, False, True, False, True, False, True, False, False], True]
    used_modal = False
    f_center = Vector((0,0,0))
    setrot = None

    @classmethod
    def description(cls, context, properties):
        if properties.ke_unrotator_option == "DEFAULT":
            return "Unrotates geo using *active element* as new 'bottom' " \
                   "OR aligns to MOUSE OVER face normal on other mesh or object. " \
                   "OBJECT: Resets rotation OR aligns to MOUSE OVER geo. " \
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
            layout.use_property_split = True
            col = layout.column()
            col.prop(self, "rot_offset")
            row = col.row(align=True)
            row.prop(self, "inv", toggle=True)
            row.prop(self, "center_override", toggle=True)
            col.separator()
            sub = col.column(align=True)
            sub.label(text="Note: Redo requires unchanged viewport")


    def get_snap_settings(self, context):
        s1 = context.scene.tool_settings.snap_elements
        s2 = context.scene.tool_settings.snap_target
        s3 = [context.scene.tool_settings.use_snap_grid_absolute,
              context.scene.tool_settings.use_snap_backface_culling,
              context.scene.tool_settings.use_snap_align_rotation,
              context.scene.tool_settings.use_snap_self,
              context.scene.tool_settings.use_snap_project,
              context.scene.tool_settings.use_snap_peel_object,
              context.scene.tool_settings.use_snap_translate,
              context.scene.tool_settings.use_snap_rotate,
              context.scene.tool_settings.use_snap_scale]
        s4 = context.scene.tool_settings.use_snap
        return [s1, s2, s3, s4]

    def set_snap_settings(self, context, s):
        context.scene.tool_settings.snap_elements = s[0]
        context.scene.tool_settings.snap_target = s[1]
        context.scene.tool_settings.use_snap_grid_absolute = s[2][0]
        context.scene.tool_settings.use_snap_backface_culling = s[2][1]
        context.scene.tool_settings.use_snap_align_rotation = s[2][2]
        context.scene.tool_settings.use_snap_self = s[2][3]
        context.scene.tool_settings.use_snap_project = s[2][4]
        context.scene.tool_settings.use_snap_peel_object = s[2][5]
        context.scene.tool_settings.use_snap_translate = s[2][6]
        context.scene.tool_settings.use_snap_rotate = s[2][7]
        context.scene.tool_settings.use_snap_scale = s[2][8]
        context.scene.tool_settings.use_snap = s[3]

    def calc_face_vectors(self, active, mtx, obj, vcount):
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


    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        automerge = False
        self.used_modal = False
        sel_check, place, noloc, place, dupe = False, False, False, False, False
        normal, tangent, place_quat = None, None, None
        mode = bpy.context.mode[:]
        sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
        obj = bpy.context.active_object
        if not obj:
            self.report({"INFO"}, "Unrotator: No Active Object?")
            return {"CANCELLED"}

        if self.ke_unrotator_option == "DUPE":
            dupe, noloc = True, False
        elif self.ke_unrotator_option == "NO_LOC":
            noloc, dupe = True, False

        connect = bpy.context.scene.kekit.unrotator_connect
        nolink = bpy.context.scene.kekit.unrotator_nolink
        nosnap = bpy.context.scene.kekit.unrotator_nosnap
        actual_invert = bpy.context.scene.kekit.unrotator_invert
        self.center = bpy.context.scene.kekit.unrotator_center

        if self.center_override:
            self.center = True

        # Check mouse over target -----------------------------------------------------------------------
        bpy.ops.object.mode_set(mode="OBJECT")
        hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos, evaluated=True)
        # print("HIT:", hit_obj, hit_face, hit_normal)

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

            # Expand Linked, or not ------------------------------------------------------------------
            if connect:
                bpy.ops.mesh.select_linked()
                linked_verts = [v for v in bm.verts if v.select]

            elif not connect:
                linked_verts = sel_verts # fall-back
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
                bmesh.ops.duplicate(bm, geom=([v for v in bm.verts if v.select] +
                                              [e for e in bm.edges if e.select] +
                                              [p for p in bm.faces if p.select]))

            # -----------------------------------------------------------------------------------------
            # Check mouse over target - place check
            # -----------------------------------------------------------------------------------------
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
                        n, t = self.calc_face_vectors(bm.faces[hit_face], obj_mtx, obj, len(hit_face_verts))
                        n.negate()
                        place_quat = rotation_from_vector(n, t).to_quaternion()

                        if self.center:
                            bm.faces.ensure_lookup_table()
                            hit_wloc = average_vector([obj_mtx @ v.co for v in hit_face_verts])

                elif hit_obj.name != obj.name:
                    # print("Mouse over different Object - Unrotate & Place mode")
                    place = True
                    hit_face_verts = hit_obj.data.polygons[hit_face].vertices[:]
                    n, t = self.calc_face_vectors(hit_obj.data.polygons[hit_face], hit_obj.matrix_world, hit_obj,
                                                  len(hit_face_verts))
                    n.negate()
                    place_quat = rotation_from_vector(n, t).to_quaternion()

                    if self.center:
                        hit_vcos = [hit_obj.matrix_world @ hit_obj.data.vertices[i].co for i in hit_face_verts]
                        hit_wloc = average_vector(hit_vcos)

            # -----------------------------------------------------------------------------------------
            # Selection processing for normal and tangent vecs
            # -----------------------------------------------------------------------------------------
            if sel_mode[0]:
                # VERT MODE ---------------------------------------------------------------------------
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
                # EDGE MODE ---------------------------------------------------------------------------
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
                # POLY MODE ---------------------------------------------------------------------------
                normal, tangent = self.calc_face_vectors(active_h, obj_mtx, obj, len(sel_verts))

            # -----------------------------------------------------------------------------------------
            # Process & Execute transforms!
            # -----------------------------------------------------------------------------------------
            if actual_invert:
                normal.negate()
            if self.inv:
                normal.negate()

            rotm = rotation_from_vector(normal, tangent)
            rq = rotm.to_quaternion()

            if self.rot_offset != 0:
                rq @= Quaternion((0, 0, 1), self.rot_offset)

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
            # Unrotate only
            if not hit_obj:
                obj.select_set(True)
                obj.rotation_euler = (0, 0, self.rot_offset)

            elif hit_obj.name == obj.name:
                obj.select_set(True)
                obj.rotation_euler = (0, 0, self.rot_offset)

            # Place!
            elif hit_obj.name != obj.name:
                obj.select_set(True)
                self.og_pos = Vector(obj.location)

                if dupe:
                    if nolink:
                        bpy.ops.object.duplicate(linked=False)
                    else:
                        bpy.ops.object.duplicate(linked=True)
                    obj = bpy.context.active_object
                    obj.select_set(True)

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

                if noloc or nosnap:
                    obj.rotation_euler = self.setrot.to_euler()

                if not noloc:
                    if self.center and nosnap:
                        hit_wloc = hit_obj.matrix_world @ Vector(hit_obj.data.polygons[hit_face].center)
                        obj.location = hit_wloc

                    # no snapping place only
                    obj.location = hit_wloc

                    if not nosnap:
                        obj.rotation_euler = self.setrot.to_euler()
                        self.f_center = hit_obj.matrix_world @ Vector(hit_obj.data.polygons[hit_face].center)
                        self.used_modal = True
                        self.og_snaps = self.get_snap_settings(context)
                        self.set_snap_settings(context, self.modal_snap)
                        context.window_manager.modal_handler_add(self)
                        bpy.ops.transform.translate('INVOKE_DEFAULT')
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

        return {"FINISHED"}


    def modal(self, context, event):

        if event.type == 'RIGHTMOUSE':
            context.object.location = self.og_pos
            self.set_snap_settings(context, self.og_snaps)
            context.area.tag_redraw()
            return {'CANCELLED'}

        elif event.type == 'ESC':
            self.set_snap_settings(context, self.og_snaps)
            context.object.location = self.f_center
            context.area.tag_redraw()
            return {"FINISHED"}

        elif event.type == "LEFTMOUSE":
            self.set_snap_settings(context, self.og_snaps)
            context.area.tag_redraw()
            return {"FINISHED"}

        return {'RUNNING_MODAL'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_OT_ke_unrotator)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_ke_unrotator)

if __name__ == "__main__":
    register()
