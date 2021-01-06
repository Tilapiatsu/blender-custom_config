bl_info = {
    "name": "keUnrotator",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (2, 0, 0),
    "blender": (2, 90, 0),
}
import bpy
import bmesh
from .ke_utils import average_vector, mouse_raycast, tri_points_order, getset_transform, restore_transform, get_distance
from mathutils import Vector, Matrix

# Note - This script is just an improvised frankenstein'd mess at this point. But it works well enough, so...
def tri_sort(vertpairs):
    e1 = vertpairs[0]
    vertpairs.pop(0)
    e2 = []
    for e in vertpairs:
        for v in e:
            if v == e1[0]:
                e2 = [x for x in e if x != v][0]
                break
    return [e1[0], e1[1], e2]

def round_abs_float(f, d=6, a=True):
    f = str(f)
    f = f.split(".")
    if len(f[1]) > 6:
        f[1] = f[1][:d]
    f = float(f[0] + "." + f[1])
    if a:
        return round(abs(f), d)
    else:
        return round(f, d)

def is_poly_bmvert_collinear(v, validverts=None):
    le = v.link_edges[:]
    rem = []
    if validverts is not None:
        for e in le:
            if e.other_vert(v) not in validverts:
                rem.append(e)
    le = [e for e in le if e not in rem]
    if len(le) == 2:
        vec1 = Vector(v.co - le[0].other_vert(v).co)
        vec2 = Vector(v.co - le[1].other_vert(v).co)
        if abs(vec1.angle(vec2)) >= 3.1415:
            return True
    return False

def parasort(vpds):
    pv = []
    first = False
    for nr, e in enumerate(vpds):
        ev = Vector(e[0].co - e[1].co).normalized()
        for vp in vpds:
            if vp != e:
                tv = Vector(vp[0].co - vp[1].co).normalized()
                d = round_abs_float(ev.dot(tv), d=3)
                # print(ev.dot(tv), d)
                if 0.995 < d < 1.005 and vp not in pv:
                    if not first:
                        # print("adding", e, vp)
                        pv.append(e)
                        first = True
                    pv.append(vp)
                    break
    return pv

def get_across_vec(p1, p2, avgp):
    mid_point_list = []
    interval = 100

    for i in range(1, interval):
        ival = float(i) / interval
        x = (1 - ival) * p1[0] + ival * p2[0]
        y = (1 - ival) * p1[1] + ival * p2[1]
        z = (1 - ival) * p1[2] + ival * p2[2]
        mid_point_list.append([x, y, z])

    # pick closest candidate
    new_mid_point = []
    for i in mid_point_list:
        a = get_distance(avgp, i)
        ins = [a, i]
        new_mid_point.append(ins)

    new_mid_point.sort()
    newEndPos = Vector(new_mid_point[0][-1])
    r = Vector(newEndPos - avgp).normalized()
    return r

def unrotate(n_v, v_1, v_2, inv=False, set_inv=False, rot_offset=0):
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

    if not set_inv:
        rx, ry, rz = rot.x * -1, rot.y * -1, rot.z * -1
    else:
        rx, ry, rz = rot.x, rot.y, rot.z

    if rot_offset != 0:
        rz += rot_offset

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
    bl_description = "Unrotates geo using *active element* as new 'bottom' OR aligns to MOUSE OVER face normal on other mesh or object." \
                     "OBJECT: Resets rotation OR aligns on MOUSE OVER." \
                     "Note: Rotation tweak (redo-option) may glitch out if you move the viewport"
    bl_options = {'REGISTER', 'UNDO'}

    ke_unrotator_option: bpy.props.EnumProperty(
        items=[("DEFAULT", "Default", "", "DEFAULT", 1),
               ("DUPE", "Duplicate", "", "DUPE", 2),
               ("NO_LOC", "Rotation Only", "", "NOLOC", 3)],
        name="Unrotator Options",
        default="DEFAULT")

    rot_offset: bpy.props.FloatProperty(name="Rotation Offset", default=0, min=-360.0, max=360.0, step=500, subtype='ANGLE', precision=0)

    center = False
    mouse_pos = Vector((0, 0))
    set_invert = True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        col.prop(self, "rot_offset")
        col.separator()
        sub = col.column(align=True)
        sub.label(text= "Note: Rotation Offset requires unchanged viewport")

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        # print(bpy.app.version, (2, 91, 0) > bpy.app.version)
        if (2, 91, 0) > bpy.app.version:
            self.set_invert = False

        sel_check, place, noloc, place, dupe = False, False, False, False, False
        vec_poslist = []
        place_coords = []
        collinear = []
        paravec = None
        mode = bpy.context.mode
        sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
        obj = bpy.context.active_object
        og = getset_transform()

        if self.ke_unrotator_option == "DUPE":
            dupe, noloc = True, False
        elif self.ke_unrotator_option == "NO_LOC":
            noloc, dupe = True, False

        # reset = bpy.context.scene.kekit.unrotator_reset
        reset = False
        connect = bpy.context.scene.kekit.unrotator_connect
        nolink = bpy.context.scene.kekit.unrotator_nolink
        nosnap = bpy.context.scene.kekit.unrotator_nosnap
        actual_invert = bpy.context.scene.kekit.unrotator_invert
        self.center = bpy.context.scene.kekit.unrotator_center

        # Check mouse over target
        bpy.ops.object.mode_set(mode="OBJECT")
        hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)
        # print("HIT:", hit_obj, hit_face, hit_normal)
        if mode == "OBJECT" and not nosnap:
            self.rot_offset = 0
            self.center = False

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
            # boundary convert lacking set active
            if sel_edges and not active_h:
                active_h = sel_edges[-1]

            if len(sel_verts) >= 3 and active_h:
                if sel_mode[0]:
                    sel_check = True
                elif sel_mode[1] and len(sel_edges) >= 2:
                    sel_check = True
                elif sel_mode[2] and len(sel_poly):
                    sel_check = True

            # Collinear check for ngons
            if sel_mode[2] and active_h:
                sel_verts = active_h.verts
                collinear = [v for v in active_h.verts if is_poly_bmvert_collinear(v, validverts=active_h.verts[:])]
                if collinear:
                    sel_verts = [v for v in sel_verts if v not in collinear]
                # print("COLLINEAR",len(collinear), collinear)

            # Expand Linked, or not
            if sel_check and connect:
                bpy.ops.mesh.select_linked()
                linked_verts = [v for v in bm.verts if v.select]
            elif sel_check and not connect:
                linked_verts = sel_verts

            # Check mouse over target - place check
            if type(hit_face) == int and sel_check:
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

                        if self.center:
                            bm.faces.ensure_lookup_table()
                            hit_wloc = average_vector([obj_mtx @ v.co for v in hit_face_verts])

                elif hit_obj.name != obj.name:
                    # print("Mouse over different Object - Unrotate & Place mode")
                    place = True
                    pe = [e for e in hit_obj.data.polygons[hit_face].edge_keys]
                    vt = tri_sort(pe)
                    for v in vt:
                        vc = hit_obj.matrix_world @ hit_obj.data.vertices[v].co
                        place_coords.append(vc)

                        if self.center:
                            hit_face_verts = [hit_obj.matrix_world @ hit_obj.data.vertices[i].co for i in hit_obj.data.polygons[hit_face].vertices]
                            hit_wloc = average_vector(hit_face_verts)

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

                vert_pairs = []
                for e in sel_edges:
                    vp = [v for v in e.verts]
                    vert_pairs.append(vp)

                loopverts = vert_pairs[0]
                # connected corner tri
                if vert_pairs[1][0] in vert_pairs[0] or vert_pairs[1][1] in vert_pairs[0]:
                    loopverts = list(set(vert_pairs[0] + vert_pairs[1]))
                # parallels
                elif len(sel_edges) == 2:
                    cv = get_across_vec(obj_mtx @ vert_pairs[0][0].co, obj_mtx @ vert_pairs[0][1].co,
                                        average_vector([obj_mtx @ v.co for v in vert_pairs[1]]))
                    # dotcheck if cv perpendicular enough
                    v1 = obj_mtx @ vert_pairs[0][1].co - obj_mtx @ vert_pairs[0][0].co
                    if 0.9 > cv.dot(v1):
                        paravec = v1, cv

                else: # trimode
                    a = get_distance(vert_pairs[0][0].co, vert_pairs[1][0].co)
                    b = get_distance(vert_pairs[0][0].co, vert_pairs[1][1].co)
                    if a < b:
                        loopverts.append(vert_pairs[1][0])
                    else:
                        loopverts.append(vert_pairs[1][1])

                if len(loopverts) >= 3:
                    sel_verts = loopverts
                # print([i.index for i in sel_verts])
                h = tri_points_order([sel_verts[0].co, sel_verts[1].co, sel_verts[2].co])
                vec_poslist = sel_verts[h[0]].co, sel_verts[h[1]].co, sel_verts[h[2]].co

            elif sel_mode[2] and sel_check:
                # POLY MODE ---------------------------------------------------------------------------
                pe = [list(e.verts) for e in active_h.edges]

                if len(pe) >= 4:
                    pe = [e for e in pe if not any(e) in collinear]

                    # find parallell vecs
                    paravec = None
                    ppe = parasort(pe)
                    # print("Parasort:", len(pe),len(ppe))

                    if len(pe) == len(ppe):
                        #cylinder prob
                        ppe = ppe[:2]

                    # TERRIBLE methods to find decent perpendicular vec between parallells
                    if len(ppe) >= 2:
                        # pe = ppe
                        mpick = 99
                        stop = False

                        for e in ppe:
                            if not stop:
                                for be in ppe:
                                    if e != be:
                                        v1 = obj_mtx @ e[1].co - obj_mtx @ e[0].co

                                        cv = get_across_vec(obj_mtx @ e[0].co, obj_mtx @ e[1].co,
                                                            average_vector([obj_mtx @ v.co for v in be]))

                                        check = round_abs_float(cv.dot(v1), 6)
                                        if check < 0.05:
                                            if check < mpick:
                                                paravec = v1, cv
                                                mpick = check
                                                # print("parapicks", check, "e", e[0].index, e[1].index, "be", be[0].index,
                                                #       be[1].index)

                    if len(ppe) == 2 and paravec is None:
                        ## i have no idea what im doing, but this is needed for 2 ??
                        p1, p2 = obj_mtx @ ppe[0][0].co, obj_mtx @ ppe[0][1].co
                        v1 = p2 - p1
                        cv = get_across_vec(p1, p2, average_vector([obj_mtx @ v.co for v in ppe[1]]))
                        paravec = v1, cv

                    # fallback tri
                    p1, p2 = pe[0][0], pe[0][1]
                    pc = active_h.edges[1].verts
                    p3 = [v for v in pc if v not in pe[0]][0]
                    c_poslist = p1.co, p2.co, p3.co
                    h = tri_points_order([c_poslist[0], c_poslist[1], c_poslist[2]])
                    vec_poslist = c_poslist[h[0]], c_poslist[h[1]], c_poslist[h[2]]
                else:
                    # print("tri unrotate")
                    h = tri_points_order([sel_verts[0].co, sel_verts[1].co, sel_verts[2].co])
                    vec_poslist = sel_verts[h[0]].co, sel_verts[h[1]].co, sel_verts[h[2]].co
            else:
                self.report({"INFO"}, "Unrotator: Selection Error - Incorrect/No geo Selected? Active Element?")

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

                # print("paracheck", paravec)
                if paravec is not None:
                    v_1, v_2 = paravec[0], paravec[1]
                else:
                    p1, p2, p3 = obj_mtx @ vec_poslist[0], obj_mtx @ vec_poslist[1], obj_mtx @ vec_poslist[2]
                    v_2 = p3 - p1
                    v_1 = p2 - p1

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

                if actual_invert:
                    n_v.negate()

                unrotate(n_v, v_1, v_2, inv=False, set_inv=self.set_invert, rot_offset=self.rot_offset)

                # compensate z pos
                if not place:
                    nv = [v.co for v in bm.verts if v.select]
                    npos = obj_mtx @ Vector(average_vector(nv))
                    comp = (npos - avg_pos) * -1
                    bpy.ops.transform.translate(value=comp)

            if place:
                # Orient and place
                p1, p2, p3 = place_coords[0], place_coords[1], place_coords[2]

                v_1 = p2 - p1
                v_2 = p3 - p1
                n_v = v_1.cross(v_2).normalized()

                # Direction flip check
                if hit_normal.dot(n_v) <= 0:
                    n_v.negate()
                    v_1.negate()
                    v_2.negate()

                # ..again!
                unrotate(n_v, v_1, v_2, inv=True, set_inv=self.set_invert)

                if not noloc:
                    # Place - just using ops & cursor here...
                    cursor = bpy.context.scene.cursor
                    ogcpos = cursor.location.copy()
                    bpy.context.scene.tool_settings.transform_pivot_point = "ACTIVE_ELEMENT"
                    cursor.location = hit_wloc
                    bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                    bpy.ops.view3d.snap_cursor_to_center()
                    #restore
                    cursor.location = ogcpos

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

                if dupe:
                    if nolink:
                        bpy.ops.object.duplicate(linked=False)
                    else:
                        bpy.ops.object.duplicate(linked=True)
                    obj = bpy.context.active_object
                    obj.select_set(True)

                if noloc or nosnap:
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

                    if actual_invert:
                        n_v.negate()

                    obj.rotation_euler = (0,0,self.rot_offset)
                    unrotate(n_v, v_1, v_2, inv=True, set_inv=self.set_invert)

                if not noloc:
                    if self.center and nosnap:
                        hit_wloc = hit_obj.matrix_world @ Vector(hit_obj.data.polygons[hit_face].center)
                        obj.location = hit_wloc

                    if not nosnap:
                        bpy.context.scene.tool_settings.use_snap = True
                        bpy.context.scene.tool_settings.snap_elements = {'FACE'}
                        bpy.context.scene.tool_settings.use_snap_align_rotation = True
                        bpy.context.scene.tool_settings.snap_target = 'ACTIVE'
                        bpy.context.scene.tool_settings.use_snap_project = False
                        bpy.context.scene.tool_settings.use_snap_translate = True

                    obj.location = hit_wloc

                    if not nosnap:
                        bpy.ops.transform.translate('INVOKE_DEFAULT')

        if reset:
            self.ke_unrotator_option = "DEFAULT"

        if sel_mode[1] and mode != "OBJECT":
            #add active edge for reasons..
            bm.edges.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
            for v in sel_edges:
                bm.edges[v.index].select = True
            bm.select_history.clear()
            bm.select_history.add(sel_edges[0])
            bmesh.update_edit_mesh(obj.data, True)

        restore_transform(og)

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
