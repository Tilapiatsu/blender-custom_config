import bpy
import bmesh
import os
from mathutils import Matrix, Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
from math import radians, sqrt


def get_view_type():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if len(space.region_quadviews) > 0:
                        return "QUAD"
                    elif space.region_3d.is_perspective:
                        return "PERSP"
                    else:
                        return "ORTHO"


def refresh_ui():
    # Redraw everything!
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            for region in area.regions:
                region.tag_redraw()


def pie_pos_offset(xy, v):
    scl = bpy.context.preferences.view.ui_scale
    r = None
    if v == "N":
        r = xy[0], xy[1] - (115 * scl)
    elif v == "S":
        r = xy[0], xy[1] + (115 * scl)
    elif v == "W":
        r = xy[0] + (152 * scl), xy[1]
    elif v == "E":
        r = xy[0] - (152 * scl), xy[1]
    elif v == "NW":
        r = xy[0] + (124 * scl), xy[1] - (71 * scl)
    elif v == "NE":
        r = xy[0] - (124 * scl), xy[1] - (71 * scl)
    elif v == "SW":
        r = xy[0] + (136 * scl), xy[1] + (70 * scl)
    elif v == "SE":
        r = xy[0] - (136 * scl), xy[1] + (70 * scl)
    if v and r is not None:
        return int(r[0]), int(r[1])
    else:
        return xy


def set_status_text(context, text_list, spacing=5, mb="\u25cf", kb="\u25a0"):
    """Unicode-icon statusbar modal-printing - remember to set to None"""
    if text_list is not None:
        separator = "\u2003" * spacing
        message = ""
        for line in text_list:
            if "WHEEL" in line or "MB" in line:
                message += mb + " " + line + separator
            else:
                message += kb + " " + line + separator
        context.workspace.status_text_set(message)
    else:
        context.workspace.status_text_set(None)


def getset_transform(o="GLOBAL", p="MEDIAN_POINT", setglobal=True):
    og = [bpy.context.scene.transform_orientation_slots[0].type, bpy.context.scene.tool_settings.transform_pivot_point]
    if setglobal:
        bpy.ops.transform.select_orientation(orientation=o)
        bpy.context.scene.tool_settings.transform_pivot_point = p
    return og


def restore_transform(og_op):
    bpy.ops.transform.select_orientation(orientation=og_op[0])
    bpy.context.scene.tool_settings.transform_pivot_point = og_op[1]


def apply_transform(obj, use_location=False, use_rotation=True, use_scale=True):
    mb = obj.matrix_basis
    idmat = Matrix()
    loc, rot, scale = mb.decompose()
    trmat = Matrix.Translation(loc)
    rotmat = mb.to_3x3().normalized().to_4x4()
    sclmat = Matrix.Diagonal(scale).to_4x4()
    transform = [idmat, idmat, idmat]
    basis = [trmat, rotmat, sclmat]

    def swap(i):
        transform[i], basis[i] = basis[i], transform[i]

    if use_location:
        swap(0)
    if use_rotation:
        swap(1)
    if use_scale:
        swap(2)

    mat = transform[0] @ transform[1] @ transform[2]
    if hasattr(obj.data, "transform"):
        obj.data.transform(mat)
    for c in obj.children:
        c.matrix_local = mat @ c.matrix_local
    obj.matrix_basis = basis[0] @ basis[1] @ basis[2]
    bpy.context.evaluated_depsgraph_get().update()


def get_layer_collection(layer_coll, coll_name):
    # todo: find better solution to set active coll
    if layer_coll.name == coll_name:
        return layer_coll
    for layer in layer_coll.children:
        found = get_layer_collection(layer, coll_name)
        if found:
            return found
    return None


def set_active_collection(context, obj):
    avail = [i.name for i in context.view_layer.layer_collection.children]
    obj_collection = obj.users_collection[0]
    # Making sure there is no garbage invisible collection used
    for c in context.object.users_collection:
        if c.name in avail:
            obj_collection = c
            break
    layer_collection = context.view_layer.layer_collection
    layer_coll = get_layer_collection(layer_collection, obj_collection.name)
    context.view_layer.active_layer_collection = layer_coll


def wempty(context):
    exist = [o for o in context.scene.objects if o.type == "EMPTY" and o.name == "World Origo Empty"]
    if not exist:
        e = bpy.data.objects.new("empty", None)
        context.scene.collection.objects.link(e)
        e.name = "World Origo Empty"
        e.empty_display_size = 1
        e.empty_display_type = 'PLAIN_AXES'
        e.hide_viewport = True
        return e
    return exist[0]


def get_duplicates(dl):
    # credJohnLaRooy
    seen = set()
    seen2 = set()
    seen_add = seen.add
    seen2_add = seen2.add
    for item in dl:
        if item in seen:
            seen2_add(item)
        else:
            seen_add(item)
    return list(seen2)


def get_selected(context, sel_type="MESH", use_cat=False, cat=None):
    # Get a selected Object by Type, Active or not
    if cat is None:
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
    obj = None
    sel_obj = [o for o in context.selected_objects]
    ao = context.active_object

    if sel_obj and not use_cat:
        sel_obj = [o for o in sel_obj if o.type == sel_type]
        if ao:
            if ao.type == sel_type:
                obj = ao
    else:
        sel_obj = [o for o in sel_obj if o.type in cat]
        if ao:
            if ao.type in cat:
                obj = ao
    if not obj and sel_obj:
        obj = sel_obj[0]
    return obj


def vertloops(vertpairs):
    """Sort verts from list of vert pairs"""
    loop_vp = [i for i in vertpairs]
    loops = []
    while len(loop_vp) > 0:
        vpsort = [loop_vp[0][0], loop_vp[0][1]]
        loop_vp.pop(0)
        loops.append(vpsort)
        for n in range(0, len(vertpairs)):
            i = 0
            for e in loop_vp:
                if vpsort[0] == e[0]:
                    vpsort.insert(0, e[1])
                    loop_vp.pop(i)
                    break
                elif vpsort[0] == e[1]:
                    vpsort.insert(0, e[0])
                    loop_vp.pop(i)
                    break
                elif vpsort[-1] == e[0]:
                    vpsort.append(e[1])
                    loop_vp.pop(i)
                    break
                elif vpsort[-1] == e[1]:
                    vpsort.append(e[0])
                    loop_vp.pop(i)
                    break
                else:
                    i = i + 1
    return loops


# def get_loops(vertpairs, legacy=False):
#     # sort list of edges (vert index pairs)
#     loop_vp = [i for i in vertpairs]
#     # og_verts = list(set(flatten(loop_vp)))
#     og_verts = [v for vp in loop_vp for v in vp]
#     loops = []
#     while (len(loop_vp) - 1) > 0:
#         vpsort = [loop_vp[0][0], loop_vp[0][1]]
#         loop_vp.pop(0)
#         loops.append(vpsort)
#
#         for n in range(0, len(vertpairs)):
#             i = 0
#             for e in loop_vp:
#                 if vpsort[0] == e[0]:
#                     vpsort.insert(0, e[1])
#                     loop_vp.pop(i)
#                     break
#                 elif vpsort[0] == e[1]:
#                     vpsort.insert(0, e[0])
#                     loop_vp.pop(i)
#                     break
#                 elif vpsort[-1] == e[0]:
#                     vpsort.append(e[1])
#                     loop_vp.pop(i)
#                     break
#                 elif vpsort[-1] == e[1]:
#                     vpsort.append(e[0])
#                     loop_vp.pop(i)
#                     break
#                 else:
#                     i = i + 1
#     # check...bcause it doesn't work on single edges...
#     # end vert on closed loop is dupe of start vert; as intended (check for closed loops), also the +1 below:
#     if not legacy:
#         if loops[0][0] == loops[0][-1]:
#             counter = len(og_verts) + 1
#         else:
#             counter = len(og_verts)
#
#         if len(loops) == 1 and len(loops[0]) != counter:
#             missing_island = [v for v in og_verts if v not in loops[0]]
#             loops.append(missing_island)
#
#     return loops


def get_area_of_type(type_name):
    for area in bpy.context.screen.areas:
        if area.type == type_name:
            return area


def get_3d_view():
    return get_area_of_type('VIEW_3D').spaces[0]


def get_area_and_type():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if len(space.region_quadviews) > 0:
                        return area, "QUAD"
                    elif space.region_3d.is_perspective:
                        return area, "PERSP"
                    else:
                        return area, "ORTHO"


def override_by_active_view3d(context, mouse_x, mouse_y):
    # Make context override with active view3d region by mouse pos
    ctx = context.copy()
    for a in context.screen.areas:
        if a.type == 'VIEW_3D':
            is_quad = bool(len(a.spaces.active.region_quadviews) > 0)
            if not is_quad:
                if a.x <= mouse_x < a.width + a.x and a.y <= mouse_y < a.height + a.y:
                    ctx['area'] = a
                    ctx['region'] = a.regions[-1]
                    return ctx
            elif is_quad:
                for r in a.regions:
                    if r.type == "WINDOW":
                        if r.x <= mouse_x < r.width + r.x and r.y <= mouse_y < r.height + r.y:
                            ctx['area'] = a
                            ctx['region'] = r
                            return ctx
    return ctx


def rotation_from_vector(n, t, rotate90=True, rw=True):
    u = t.cross(n).normalized()
    mat = Matrix((t, n, u)).to_4x4().inverted()
    if rotate90:
        mat_rot = Matrix.Rotation(radians(-90.0), 4, 'X')
        matrix = mat @ mat_rot
        if rw:
            mat_rot = Matrix.Rotation(radians(90.0), 4, 'Z')  # nicer world alignment...
            mat = matrix @ mat_rot
    return mat


def rotation_towards(n, up=None):
    if up is None:
        up = n.orthogonal().normalized()
    t = n.cross(up).normalized()
    return rotation_from_vector(n, t, rotate90=False)


def vector_from_matrix(mtx_world, axis=3):
    rot = mtx_world.to_quaternion()
    if axis == 0:
        return rot @ Vector((1.0, 0.0, 0.0))
    elif axis == 1:
        return rot @ Vector((0.0, 1.0, 0.0))
    elif axis == 2:
        return rot @ Vector((0.0, 0.0, 1.0))
    else:
        return rot @ Vector((1.0, 0.0, 0.0)), rot @ Vector((0.0, 1.0, 0.0)), rot @ Vector((0.0, 0.0, 1.0))


def sort_quad(vl):
    """sort verts in CW -or- CCW quad, for when it doesn't matter"""
    vcos = [v.co for v in vl]
    tri = tri_points_order(vcos)
    vs = [vl[tri[0]], vl[tri[1]], vl[tri[2]]]
    last = [i for i in vl if i not in vs][0]
    vs.insert(2, last)
    return vs


def tri_order(p):
    """Sort (min) 3 first verts from tuple or tuple of tuples (obj, vertlist)"""
    sets = []
    tri = []
    if len(p) > 1 and type(p[0]) != tuple:
        p = ((p),)
    # setup paired lists
    for pair in p:
        if pair[1]:
            s = [pair[0], [v for v in pair[1]]]
            sets.append(s)
    sets = sorted(sets, key=len)
    # get three first verts+
    count = 0
    for s in sets:
        if count < 3:
            if type(s[1]) != list:
                sl = [s[1], ]
            else:
                sl = s[1]
            for i in sl:
                tri.append([s[0], i])
                count += 1
    # Fail insufficient points
    if count < 3:
        return None
    # side lengths -hypot for tri
    vc1 = tri[0][0].matrix_world @ tri[0][1].co
    vc2 = tri[1][0].matrix_world @ tri[1][1].co
    vc3 = tri[2][0].matrix_world @ tri[2][1].co
    torder = tri_points_order((vc1, vc2, vc3))
    ot = [tri[i] for i in torder]
    q = [i for i in tri if i not in ot]
    if q:
        for i in q:
            ot.append(i)
    return ot


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


def tri_points_vectors(objmtx, normal, coords):
    """ input normal to check/force z flip """
    h = tri_points_order([coords[0], coords[1], coords[2]])
    vec_poslist = coords[h[0]], coords[h[1]], coords[h[2]]

    # Vectors
    p1, p2, p3 = objmtx @ vec_poslist[0], objmtx @ vec_poslist[1], objmtx @ vec_poslist[2]
    v_1 = p2 - p1
    v_2 = p3 - p1
    n_v = v_1.cross(v_2).normalized()

    # pick tan vec
    c1 = n_v.cross(v_1).normalized()
    c2 = n_v.cross(v_2).normalized()
    if c1.dot(n_v) > c2.dot(n_v):
        u_v = c2
    else:
        u_v = c1
    t_v = u_v.cross(n_v).normalized()

    # check inverse Z
    if n_v.dot(normal) < 0:
        n_v.negate()

    return n_v, t_v


def mouse_sc_raycast(context, co2d):
    """ Raycast that works in edit mode - caution: returns evaluated face idx does not match """
    view_vector = region_2d_to_vector_3d(context.region, context.region_data, co2d)
    ray_origin = region_2d_to_origin_3d(context.region, context.region_data, co2d)
    viewlayer = context.view_layer

    hidden = []
    hit_index = None
    hit_obj = None
    hit_loc = None
    hit_normal = None
    hit_mtx = None
    hit = False
    is_visible = False

    # scene invisible is dfferent from view invisible, so we must do this dance?
    while not is_visible:
        result, location, normal, index, obj, matrix = context.scene.ray_cast(context.evaluated_depsgraph_get(),
                                                                              ray_origin, view_vector, distance=9001)
        if obj is not None:
            is_visible = obj.visible_get(view_layer=viewlayer)

            if not is_visible:
                obj.hide_viewport = True
                hidden.append(obj)

            if is_visible:
                if obj.type == 'MESH':
                    hit_index = index
                    hit_obj = obj
                    hit_normal = normal
                    # hit_normal = correct_normal(matrix, normal)
                    hit_loc = location
                    hit_mtx = matrix
                    hit = result
        else:
            hit_obj = None
            hit_index = None
            is_visible = True

    if hidden:
        for o in hidden:
            o.hide_viewport = False

    return hit, hit_loc, hit_normal, hit_index, hit_obj, hit_mtx


def obj_raycast(obj, matrix, ray_origin, ray_target):
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj
    success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

    if success:
        return location, normal, face_index
    else:
        return None, None, None


def mouse_raycast(context, mouse_pos, evaluated=False):
    region = context.region
    rv3d = context.region_data

    view_vector = region_2d_to_vector_3d(region, rv3d, mouse_pos)
    ray_origin = region_2d_to_origin_3d(region, rv3d, mouse_pos)
    ray_target = ray_origin + view_vector

    hit_length_squared = -1.0
    hit_obj, hit_wloc, hit_normal, hit_face = None, None, None, None

    # cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
    cat = ["MESH"]
    # todo: Make hit curves returnable objs w. evaluated

    if not evaluated:
        objects = [o for o in context.visible_objects]
        depsgraph = objects.copy()
        objects = [o.name for o in context.visible_objects]
    else:
        objects = [o.name for o in context.visible_objects]
        depsgraph = context.evaluated_depsgraph_get()
        depsgraph = depsgraph.object_instances

    for dup in depsgraph:
        if evaluated:
            if dup.is_instance:
                obj = dup.instance_object
                obj_mtx = dup.matrix_world.copy()
            else:
                obj = dup.object
                obj_mtx = obj.matrix_world.copy()
        else:
            obj = dup
            obj_mtx = obj.matrix_world.copy()

        if obj.type in cat and obj.name in objects:
            try:
                hit, normal, face_index = obj_raycast(obj, obj_mtx, ray_origin, ray_target)
            except RuntimeError:
                print("Raycast Failed: Unsupported object type?")
                pass

            if hit is not None:
                hit_world = obj_mtx @ hit
                length_squared = (hit_world - ray_origin).length_squared
                if hit_obj is None or length_squared < hit_length_squared:
                    hit_normal = correct_normal(obj_mtx, normal)
                    hit_wloc = hit_world
                    hit_face = face_index
                    hit_length_squared = length_squared
                    hit_obj = obj

    if hit_obj:
        return hit_obj, hit_wloc, hit_normal, hit_face
    else:
        return None, None, None, None


def point_axis_raycast(context, vec_point, axis=2, targetcap=-10000):
    vec_dir = vec_point.to_3d()
    vec_dir[axis] = targetcap
    ray_origin = vec_point
    ray_target = vec_dir
    best_length_squared = -1.0
    best_obj, hit_wloc, hit_normal, hit_face = None, None, None, None

    depsgraph = context.evaluated_depsgraph_get()

    for dup in depsgraph.object_instances:

        if dup.is_instance:
            obj = dup.instance_object
            obj_mtx = dup.matrix_world.copy()
        else:
            obj = dup.object
            obj_mtx = obj.matrix_world.copy()

        if obj.type == 'MESH':
            hit, normal, face_index = obj_raycast(obj, obj_mtx, ray_origin, ray_target)

            if hit is not None:
                hit_world = obj_mtx @ hit
                length_squared = (hit_world - ray_origin).length_squared
                if best_obj is None or length_squared < best_length_squared:
                    hit_normal = normal
                    hit_wloc = hit_world
                    hit_face = face_index
                    best_length_squared = length_squared
                    best_obj = obj

    if best_obj:
        return best_obj, hit_wloc, hit_normal, hit_face
    else:
        return None, None, None, None


def walk_island(vert, sedges=[]):
    vert.tag = True
    yield vert
    if sedges:
        linked_verts = []
        for e in vert.link_edges:
            if e in sedges:
                ov = e.other_vert(vert)
                if not ov.tag:
                    linked_verts.append(ov)
    else:
        linked_verts = [e.other_vert(vert) for e in vert.link_edges
                        if not e.other_vert(vert).tag]
    for v in linked_verts:
        if v.tag:
            continue
        yield from walk_island(v, sedges=sedges)


def get_islands(bm, verts, same_part_edges=[]):
    def tag(vs, switch):
        for i in vs:
            i.tag = switch
    if not same_part_edges:
        tag(bm.verts, True)
    tag(verts, False)
    islands = []
    verts = set(verts)
    while verts:
        v = verts.pop()
        verts.add(v)
        island = set(walk_island(v, sedges=same_part_edges))
        islands.append(list(island))
        tag(island, False)
        verts -= island
    return islands


def get_face_islands(bm, sel_verts=[], sel_edges=[], sel_faces=[]):
    # Not super optimal, but convenient reuse ;>
    if not sel_verts:
        sel_verts = [v for v in bm.verts if v.select]
    if not sel_edges:
        sel_edges = [e for e in bm.edges if e.select]
    if not sel_faces:
        sel_faces = [f for f in bm.faces if f.select]
    v_islands = get_islands(bm, verts=sel_verts, same_part_edges=sel_edges)
    f_islands = []
    for vi in v_islands:
        f_island = [f for f in sel_faces if f.verts[0] in vi]
        f_islands.append(f_island)
    return f_islands


def get_selection_islands(sel_faces, active_face):
    # Old legacy garbage that only sorts two islands? - should prob remove
    sortfaces = [p for p in sel_faces if p != active_face]
    first_island, second_island = active_face.verts[:], []
    maxcount = len(sortfaces) * 4
    while maxcount:
        maxcount -= 1
        for p in sortfaces:
            faceverts = p.verts[:]
            for v in faceverts:
                if v in first_island:
                    first_island.extend(faceverts)
                    sortfaces.remove(p)
                    break
    for p in sortfaces:
        second_island.extend(p.verts)
    return list(set(first_island)), list(set(second_island))


def correct_normal(world_matrix, vec_normal):
    n = (world_matrix.to_quaternion() @ vec_normal).to_4d()
    n.w = 0
    return world_matrix.to_quaternion() @ (world_matrix.inverted() @ n).to_3d().normalized()


def flatten(nested):
    for item in nested:
        try:
            yield from flatten(item)
        except TypeError:
            yield item


def flattened(nested):
    return list(flatten(nested))


def get_distance(v1, v2):
    dist = [(a - b) ** 2 for a, b in zip(v1, v2)]
    return sqrt(sum(dist))


def get_midpoint(p1, p2):
    mid_p = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2]
    return mid_p


def chunk(cl, n):
    return [cl[i:i + n] for i in range(0, len(cl), n)]


def remap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def average_vector(vectors):
    try:
        return Vector(sum(vectors, Vector()) / len(vectors))
    except ZeroDivisionError:
        print("Zero Division Error: Invalid Selection?")
        return None


def cross_coords(coordlist):
    # first 3 coords as tri-plane
    x1, y1, z1 = coordlist[0][0], coordlist[0][1], coordlist[0][2]
    x2, y2, z2 = coordlist[1][0], coordlist[1][1], coordlist[1][2]
    x3, y3, z3 = coordlist[2][0], coordlist[2][1], coordlist[2][2]
    v1 = [x2 - x1, y2 - y1, z2 - z1]
    v2 = [x3 - x1, y3 - y1, z3 - z1]
    cross_product = [v1[1] * v2[2] - v1[2] * v2[1], -1 * (v1[0] * v2[2] - v1[2] * v2[0]), v1[0] * v2[1] - v1[1] * v2[0]]
    return cross_product


def point_to_plane(first_point, point_verts, plane_verts):
    # or, point on plane to plane
    length = 0
    # cross source selection
    cr = cross_coords(point_verts)

    sqrLenN = cr[0] * cr[0] + cr[1] * cr[1] + cr[2] * cr[2]
    if sqrt(sqrLenN) != 0:
        invLenN = 1.0 / sqrt(sqrLenN)
    else:
        return 0
    rayDir = [cr[0] * invLenN, cr[1] * invLenN, cr[2] * invLenN]

    # cross target plane
    cr = cross_coords(plane_verts)

    x2, y2, z2 = plane_verts[1][0], plane_verts[1][1], plane_verts[1][2]
    x, y, z = first_point[0], first_point[1], first_point[2]

    sqrLenN = cr[0] * cr[0] + cr[1] * cr[1] + cr[2] * cr[2]

    if sqrLenN != 0:
        invLenN = 1.0 / sqrt(sqrLenN)
        planeN = [cr[0] * invLenN, cr[1] * invLenN, cr[2] * invLenN]

        planeD = -(planeN[0] * x2 + planeN[1] * y2 + planeN[2] * z2)

        d1 = planeN[0] * x + planeN[1] * y + planeN[2] * z + planeD
        d2 = planeN[0] * rayDir[0] + planeN[1] * rayDir[1] + planeN[2] * rayDir[2]

        if d2 == 0:
            length = 0
        else:
            length = -(d1 / d2)

    # Round off in case the plane returns zero (or near)
    if length - 0.0001 <= 0 <= 0.0001:
        length = 0

    return length


def get_closest_midpoint(first_island_pos1, first_island_pos2, second_island_pos):
    # Interpolate new midpoint candidates on long edge
    mid_point_list = []
    interval = 100

    for i in range(1, interval):
        ival = float(i) / interval
        x = (1 - ival) * first_island_pos1[0] + ival * first_island_pos2[0]
        y = (1 - ival) * first_island_pos1[1] + ival * first_island_pos2[1]
        z = (1 - ival) * first_island_pos1[2] + ival * first_island_pos2[2]
        mid_point_list.append([x, y, z])

    # pick closest candidate
    new_mid_point = []

    for i in mid_point_list:
        a = get_distance(second_island_pos, i)
        ins = [a, i]
        new_mid_point.append(ins)

    new_mid_point.sort()

    distance = new_mid_point[0][0]
    newEndPos = new_mid_point[0][-1]
    position = get_midpoint(newEndPos, second_island_pos)

    return distance, position


def mouse_over_element(bm, mouse_pos):
    # selection or mouse over
    verts_sel = [v.select for v in bm.verts]
    edges_sel = [e.select for e in bm.edges]
    faces_sel = [f.select for f in bm.faces]

    try:
        geom = bm.select_history[-1]
    except IndexError:
        geom = None

    ret = bpy.ops.view3d.select(extend=True, location=mouse_pos)
    if ret == {'PASS_THROUGH'}:
        print("no close-by geom")
        return {'CANCELLED'}

    try:
        geom2 = bm.select_history[-1]
        # print("geom2 sel 1st", geom2.select)
    except IndexError:
        geom2 = None

    if geom is None:
        geom = geom2

    if isinstance(geom, bmesh.types.BMVert):
        geom_sel = verts_sel
        bm_geom = bm.verts
    elif isinstance(geom, bmesh.types.BMEdge):
        geom_sel = edges_sel
        bm_geom = bm.edges
    elif isinstance(geom, bmesh.types.BMFace):
        geom_sel = faces_sel
        bm_geom = bm.faces

    for sel, g in zip(geom_sel, bm_geom):
        if sel != g.select:
            g.select_set(False)
            bm.select_history.remove(g)
            bm.select_flush_mode()
            break

    return geom


def get_vert_nearest_mouse(context, mousepos, verts, mtx):
    nearest = 100000
    merge_point = []
    for v in verts:
        vpos = mtx @ Vector(v.co)
        vscreenpos = location_3d_to_region_2d(context.region, context.space_data.region_3d, vpos)
        if vscreenpos:
            dist = (mousepos - vscreenpos).length
            if dist < nearest:
                merge_point = v
                nearest = dist
    return merge_point


def pick_closest_edge(context, mtx, mousepos, edges):
    pick, prev = None, 9001
    for e in edges:
        emp = average_vector([mtx @ v.co for v in e.verts])
        p = location_3d_to_region_2d(context.region, context.space_data.region_3d, emp)
        dist = sqrt((mousepos[0] - p.x) ** 2 + (mousepos[1] - p.y) ** 2)
        if dist < prev:
            pick, prev = e, dist
    return pick


def get_scene_unit(value, nearest=False):
    """Converts value to current scene setting"""
    unit_length = bpy.context.scene.unit_settings.length_unit
    unit_scale = bpy.context.scene.unit_settings.scale_length
    unit_system = bpy.context.scene.unit_settings.system
    value = value * unit_scale
    factor, unit = 1, ""

    if unit_length == 'ADAPTIVE':
        nearest = True

    if nearest and unit_system == 'METRIC':
        if value == 0:
            unit = 'm'
        elif value >= 1000:
            unit, value = 'km', value * 0.001
        elif 999 > value >= 0.9999:
            unit = 'm'
        elif 1 > value >= 0.009999:
            unit, value = 'cm', value * 100
        elif 0.01 > value >= 0.0009999:
            unit, value = 'mm', value * 1000
        elif value < 0.001:
            unit, value = '\u00b5' + 'm', value * 1000000

    elif nearest and unit_system == 'IMPERIAL':
        if value == 0:
            unit = '\u0027'
        else:
            value = round((value * 3.280839895013123), 3)  # feet
            if value >= 5280:
                unit, value = 'mi', value / 5280
            elif value >= 1:
                unit, value = '\u0027', value
            elif value > 0.0833333333:
                unit, value = '\u0022', round((value * 12), 2)
            else:
                unit, value = ' thou', int(value * 12000)

    elif unit_length == 'KILOMETERS':
        unit, factor = 'km', 0.001
    elif unit_length == 'METERS':
        unit, factor = 'm', 1
    elif unit_length == 'CENTIMETERS':
        unit, factor = 'cm', 100
    elif unit_length == 'MILLIMETERS':
        unit, factor = 'mm', 1000
    elif unit_length == 'MICROMETERS':
        unit, factor = '\u00b5' + 'm', 1000000
    elif unit_length == 'MILES':
        unit, factor = 'mi', 0.00062137119223733
    elif unit_length == 'FEET':
        unit, factor = '\u0027', 3.280839895013123
    elif unit_length == 'INCHES':
        unit, factor = '\u0022', 39.37007874015748
    elif unit_length == 'THOU':
        unit, factor = 'thou', 39370.07874015748
    else:
        unit, factor = 'bu', 1

    value = value / factor
    value = round(value, 4)
    # de-floating whole nrs
    if value.is_integer():
        value = int(value)

    return unit, value


def shift_list(a, s):
    s %= len(a)
    s *= -1
    return a[s:] + a[:s]


def traverse_tree(o):
    yield o
    for child in o.children:
        yield from traverse_tree(child)


def parent_lookup(sc_coll):
    parent_look = {}
    for sc_coll in traverse_tree(sc_coll):
        for c in sc_coll.children.keys():
            parent_look.setdefault(c, sc_coll.name)
    return parent_look


def get_coll_parent(ctx, coll):
    coll_parents = parent_lookup(ctx.scene.collection)
    pname = coll_parents.get(coll.name)
    if pname is None or pname.startswith("Scene"):
        return ctx.scene.collection
    else:
        return bpy.data.collections.get(pname)


def find_parents(o):
    p = [o]
    run = True
    while run:
        c = p[-1].parent
        if c is not None:
            p.append(c)
        else:
            run = False
    return [i for i in p if i != o]


def unparent(children):
    omtx = [(o, o.matrix_world.copy()) for o in children]
    for o, mtx in omtx:
        o.parent = None
        o.matrix_world = mtx


def append_nodegroup(path, identifier):
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.isfile(filepath):
        return None
    with bpy.data.libraries.load(filepath, link=False) as (data_src, ng_import):
        for ng in data_src.node_groups:
            if ng == identifier:
                ng_import.node_groups.append(ng)
                break
    if not ng_import.node_groups:
        return None
    return ng_import.node_groups[0]
