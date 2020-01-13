bl_info = {
    "name": "keUnrotator",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
}
import bpy
import bmesh
from .ke_utils import get_loops, average_vector, get_distance, mouse_raycast
from mathutils import Vector, Matrix


def tri_sort(vertpairs):
    # best vectors from connected edge+vert selection
    e1 = vertpairs[0]
    vertpairs.pop(0)
    e2 = []
    for e in vertpairs:
        for v in e:
            if v == e1[0]:
                e2 = [x for x in e if x != v][0]
                break
    return [e1[0], e1[1], e2]


def tri_points_order(vcoords):
    # Avoiding the hypotenuse (always longest) for vec
    vp = vcoords[0], vcoords[1], vcoords[2]
    vp1 = get_distance(vp[0], vp[1])
    vp2 = get_distance(vp[0], vp[2])
    vp3 = get_distance(vp[1], vp[2])
    vpsort = {"2": vp1, "1": vp2, "0": vp3}
    r = [int(i) for i in sorted(vpsort, key=vpsort.__getitem__)]
    r.reverse()
    return r


def unrotate(n_v, v_1, v_2, inv=False):
    # find the better up/tangent rot
    c1 = n_v.cross(v_1).normalized()
    c2 = n_v.cross(v_2).normalized()
    if c1.dot(n_v) > c2.dot(n_v):
        u_v = c2
    else:
        u_v = c1
    t_v = u_v.cross(n_v).normalized()
    if inv:
        rot = Matrix((t_v, u_v, n_v)).to_4x4().inverted()
    else:
        rot = Matrix((t_v, u_v, n_v)).to_4x4()
    rot = rot.to_euler()
    rx, ry, rz = rot.x * -1, rot.y * -1, rot.z * -1
    # oldskool modo-kit method to avoid non-uniform scale issues...slow, but works.
    bpy.ops.transform.rotate(value=rx, orient_axis='X', orient_type='GLOBAL', use_proportional_edit=False,
                             snap=False, orient_matrix_type='GLOBAL')
    bpy.ops.transform.rotate(value=ry, orient_axis='Y', orient_type='GLOBAL', use_proportional_edit=False,
                             snap=False, orient_matrix_type='GLOBAL')
    bpy.ops.transform.rotate(value=rz, orient_axis='Z', orient_type='GLOBAL', use_proportional_edit=False,
                             snap=False, orient_matrix_type='GLOBAL')


class VIEW3D_OT_ke_unrotator(bpy.types.Operator):
    bl_idname = "view3d.ke_unrotator"
    bl_label = "Unrotator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_description = "EDIT MODE: Unrotates mesh using *active element* vectors as 'bottom' OR " \
                     "aligns to MOUSE OVER face normal on other mesh or object. " \
                     "OBJECT: Resets rotation. MOUSE OVER interactive placement uses blenders face-snapping. " \
                     "Object mode duplicates will be linked instances."
    bl_options = {'REGISTER', 'UNDO'}

    ke_unrotator_option: bpy.props.EnumProperty(
        items=[("DEFAULT", "Default", "", "DEFAULT", 1),
               ("DUPE", "Duplicate", "", "DUPE", 2),
               ("NO_LOC", "Rotation Only", "", "NOLOC", 3)],
        name="Unrotator Options",
        default="DEFAULT")

    mouse_pos = Vector((0, 0))

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        sel_check, place, noloc, place, dupe = False, False, False, False, False
        vec_poslist = []
        place_coords = []
        mode = bpy.context.mode
        sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
        obj = bpy.context.active_object

        if self.ke_unrotator_option == "DUPE":
            dupe, noloc = True, False
        elif self.ke_unrotator_option == "NO_LOC":
            noloc, dupe = True, False

        reset = bpy.context.scene.kekit.unrotator_reset
        connect = bpy.context.scene.kekit.unrotator_connect
        nolink = bpy.context.scene.kekit.unrotator_nolink

        # Check mouse over target
        bpy.ops.object.mode_set(mode="OBJECT")
        hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

        if mode == "EDIT_MESH":
            bpy.ops.object.mode_set(mode="EDIT")

            # Get selected obj bm
            obj_mtx = obj.matrix_world.copy()
            od = obj.data
            bm = bmesh.from_edit_mesh(od)

            # Check selections
            sel_poly = [p for p in bm.faces if p.select]
            sel_edges = [e for e in bm.edges if e.select]
            sel_verts = [v for v in bm.verts if v.select]
            active_h = bm.select_history.active
            if len(sel_verts) >= 3 and active_h:
                if sel_mode[0]:
                    sel_check = True
                elif sel_mode[1] and len(sel_edges) >= 2:
                    sel_check = True
                elif sel_mode[2] and len(sel_poly):
                    sel_check = True

            # Expand Linked, or not
            if sel_check and connect:
                bpy.ops.mesh.select_linked()
                linked_verts = [v for v in bm.verts if v.select]
            elif sel_check and not connect:
                linked_verts = sel_verts

            # Check mouse over target - place check
            if hit_face and sel_check:
                if hit_obj.name == obj.name:
                    bm.faces.ensure_lookup_table()
                    hit_face_verts = [v for v in bm.faces[hit_face].verts]
                    if any(i in hit_face_verts for i in linked_verts):
                        # print("Mouse over same Obj and selected geo - Unrotate only mode")
                        place = False
                    else:
                        # print("Mouse over same Obj but unselected geo - Unrotate & Place mode")
                        place = True
                        pe = [list(e.verts) for e in bm.faces[hit_face].edges]
                        vt = tri_sort(pe)
                        place_coords = obj_mtx @ vt[0].co, obj_mtx @ vt[1].co, obj_mtx @ vt[2].co

                elif hit_obj.name != obj.name:
                    # print("Mouse over different Object - Unrotate & Place mode")
                    place = True
                    pe = [e for e in hit_obj.data.polygons[hit_face].edge_keys]
                    vt = tri_sort(pe)
                    for v in vt:
                        vc = hit_obj.matrix_world @ hit_obj.data.vertices[v].co
                        place_coords.append(vc)

            if sel_check and place and dupe:
                bpy.ops.mesh.duplicate()

            # Selection processing
            if sel_mode[0] and sel_check:
                # VERT MODE ---------------------------------------------------------------------------
                h = tri_points_order([sel_verts[0].co, sel_verts[1].co, sel_verts[2].co])
                vec_poslist = sel_verts[h[0]].co, sel_verts[h[1]].co, sel_verts[h[2]].co

            elif sel_mode[1] and sel_check:
                # EDGE MODE ---------------------------------------------------------------------------
                bm.edges.ensure_lookup_table()
                active_edge = active_h

                vert_pairs = []
                for e in sel_edges:
                    vp = [v for v in e.verts]
                    vert_pairs.append(vp)

                loops = get_loops(vert_pairs)

                if len(loops) > 1 or loops[0][0] == loops[0][-1]:
                    sel_verts = []
                    for loop in loops:
                        if any(v in active_edge.verts for v in loop):
                            sel_verts.extend(loop)
                            active_loop_verts = len(loop)
                            break
                    sel_verts = list(set(sel_verts))
                    sel_verts.reverse()  # gets reversed...so undo i guess...

                    if active_loop_verts >= 3:
                        if len(sel_verts) > 4:  # Ngons, Cylinders
                            vec_poslist.append(sel_verts[0].co)
                            vec_poslist.append(sel_verts[int(len(sel_verts) * 0.33)].co)
                            vec_poslist.append(sel_verts[int(len(sel_verts) * 0.66)].co)
                        else:
                            vec_poslist = sel_verts[0].co, sel_verts[1].co, sel_verts[2].co
                else:
                    h = tri_points_order([sel_verts[0].co, sel_verts[1].co, sel_verts[2].co])
                    vec_poslist = sel_verts[h[0]].co, sel_verts[h[1]].co, sel_verts[h[2]].co


            elif sel_mode[2] and sel_check:
                # POLY MODE ---------------------------------------------------------------------------
                pe = [list(e.verts) for e in active_h.edges]
                if len(pe) >= 4:
                    sel_verts = tri_sort(pe)
                    vec_poslist = sel_verts[0].co, sel_verts[1].co, sel_verts[2].co
                else:
                    h = tri_points_order([sel_verts[0].co, sel_verts[1].co, sel_verts[2].co])
                    vec_poslist = sel_verts[h[0]].co, sel_verts[h[1]].co, sel_verts[h[2]].co

            else:
                self.report({"INFO"}, "Unrotator: Selection Error - Insufficient/No geo Selected? Active Element?")

            # -----------------------------------------------------------------------------------------
            # Process & Execute transforms!
            # -----------------------------------------------------------------------------------------
            if vec_poslist:
                # Linked Selection center pos
                linked_verts_co = [v.co for v in linked_verts]
                avg_pos = obj_mtx @ Vector(average_vector(linked_verts_co))

                # Selection pos
                sel_pos_co = [v.co for v in sel_verts]
                sel_pos = obj_mtx @ Vector(average_vector(sel_pos_co))

                # Vectors
                p1, p2, p3 = obj_mtx @ vec_poslist[0], obj_mtx @ vec_poslist[1], obj_mtx @ vec_poslist[2]
                v_1 = p2 - p1
                v_2 = p3 - p1
                n_v = v_1.cross(v_2).normalized()

                # Direction flip check
                ref_vec = (sel_pos - avg_pos).normalized()
                check = n_v.dot(ref_vec)
                if not check <= 0:
                    n_v.negate()
                    v_1.negate()
                    v_2.negate()

                if not connect:
                    n_v.negate()
                    v_1.negate()
                    v_2.negate()

                unrotate(n_v, v_1, v_2, inv=False)

            if place:
                # Orient and place
                p1, p2, p3 = place_coords[0], place_coords[1], place_coords[2]

                v_1 = p1 - p2
                v_2 = p1 - p3
                n_v = v_1.cross(v_2).normalized()

                # Direction flip check
                if hit_normal.dot(n_v) <= 0:
                    n_v.negate()
                    v_1.negate()
                    v_2.negate()

                # ..again!
                unrotate(n_v, v_1, v_2, inv=True)

                if not noloc:
                    # Place - just using ops & cursor here...
                    cursor = bpy.context.scene.cursor
                    bpy.ops.transform.select_orientation(orientation='GLOBAL')
                    bpy.context.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
                    cursor.location = hit_wloc
                    bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                    bpy.ops.view3d.snap_cursor_to_center()


        elif mode == 'OBJECT':
            # Unrotate only
            if not hit_obj:
                obj.select_set(True)
                bpy.ops.object.rotation_clear()
            elif hit_obj.name == obj.name:
                obj.select_set(True)
                bpy.ops.object.rotation_clear()

            # Place!
            elif hit_obj.name != obj.name:
                obj.select_set(True)

                if dupe:
                    if nolink:
                        bpy.ops.object.duplicate(linked=False)
                    else:
                        bpy.ops.object.duplicate(linked=True)
                    dobj = bpy.context.active_object
                    dobj.select_set(True)

                if noloc:
                    pe = [e for e in hit_obj.data.polygons[hit_face].edge_keys]
                    vt = tri_sort(pe)
                    for v in vt:
                        vc = hit_obj.matrix_world @ hit_obj.data.vertices[v].co
                        place_coords.append(vc)

                    p1, p2, p3 = place_coords[0], place_coords[1], place_coords[2]
                    v_1 = p1 - p2
                    v_2 = p1 - p3
                    n_v = v_1.cross(v_2).normalized()

                    # # Direction flip check
                    if hit_normal.dot(n_v) <= 0:
                        n_v.negate()
                        v_1.negate()
                        v_2.negate()

                    bpy.ops.object.rotation_clear()
                    unrotate(n_v, v_1, v_2, inv=True)

                if not noloc:
                    bpy.context.scene.tool_settings.use_snap = True
                    bpy.context.scene.tool_settings.snap_elements = {'FACE'}
                    bpy.context.scene.tool_settings.use_snap_align_rotation = True
                    bpy.context.scene.tool_settings.snap_target = 'ACTIVE'
                    bpy.context.scene.tool_settings.use_snap_project = False
                    bpy.context.scene.tool_settings.use_snap_translate = True
                    if dupe:
                        dobj.location = hit_wloc
                    else:
                        obj.location = hit_wloc
                    bpy.ops.transform.translate('INVOKE_DEFAULT')

        if reset:
            self.ke_unrotator_option = "DEFAULT"

        if sel_mode[1]:
            bm.edges.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
            for v in sel_edges:
                bm.edges[v.index].select = True
            bm.select_history.clear()
            bm.select_history.add(sel_edges[0])
            bmesh.update_edit_mesh(obj.data, True)

        return {"FINISHED"}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (VIEW3D_OT_ke_unrotator,
           )

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
