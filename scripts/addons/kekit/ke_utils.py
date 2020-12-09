import bpy
from mathutils import Matrix, Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
from math import radians, sqrt


def get_duplicates(alist):
    checked = {}
    dupes = []
    for x in alist:
        if x not in checked:
            checked[x] = 1
        else:
            if checked[x] == 1:
                dupes.append(x)
            checked[x] += 1
    return dupes


def get_selected(context, sel_type="MESH"):
    '''Get a selected Object by Type, Active or not'''
    obj = None
    sel_obj = [o for o in context.selected_objects]
    if sel_obj:
        sel_obj = [o for o in sel_obj if o.type == sel_type]
    if context.active_object:
        if context.active_object.type == sel_type:
            obj = context.active_object
    if not obj and sel_obj:
        obj = sel_obj[0]
    return obj


def get_loops(vertpairs, legacy=False):
    # sort list of edges (vert index pairs)
    loop_vp = [i for i in vertpairs]
    # og_verts = list(set(flatten(loop_vp)))
    og_verts = [v for vp in loop_vp for v in vp]
    loops = []
    while (len(loop_vp) - 1) > 0:
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
    # check...bcause it doesn't work on single edges...
    # end vert on closed loop is dupe of start vert; as intended (check for closed loops), also the +1 below:
    if not legacy:
        if loops[0][0] == loops[0][-1]: counter = len(og_verts)+1
        else: counter = len(og_verts)

        if len(loops) == 1 and len(loops[0]) != counter:
            missing_island = [v for v in og_verts if v not in loops[0]]
            loops.append(missing_island)

    return loops


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


def rotation_from_vector(normal_vec, tangent_vec, rotate90=True, rw=True):
    up_vec = Vector((0, 0, 1))
    if normal_vec.dot(up_vec) <= 0.00001: up_vec = Vector((1, 0, 0))
    up_vec = tangent_vec.cross(normal_vec).normalized()
    matrix = Matrix((tangent_vec, normal_vec, up_vec)).to_4x4().inverted()
    if rotate90:
        mat_rot = Matrix.Rotation(radians(-90.0), 4, 'X')
        matrix = matrix @ mat_rot
        if rw:
            mat_rot = Matrix.Rotation(radians(90.0), 4, 'Z')  # nicer world alignment...
            matrix = matrix @ mat_rot
    return matrix


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
    """input normal to check/force z flip"""
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


def mouse_raycast(context, mouse_pos):
    region = context.region
    rv3d = context.region_data

    view_vector = region_2d_to_vector_3d(region, rv3d, mouse_pos)
    ray_origin = region_2d_to_origin_3d(region, rv3d, mouse_pos)
    ray_target = ray_origin + view_vector

    hit_length_squared = -1.0
    hit_obj, hit_wloc, hit_normal, hit_face = None, None, None, None

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
                if hit_obj is None or length_squared < hit_length_squared:
                    hit_normal = correct_normal(obj_mtx, normal)
                    hit_wloc = hit_world
                    hit_face = face_index
                    hit_length_squared = length_squared
                    hit_obj = obj

    if hit_obj:
        return  hit_obj, hit_wloc, hit_normal, hit_face
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


def relative_position_to_mouse(context, pos, mouse_pos):
    # TBD - WIP: return distance?, world axis direction
    return None


def walk_island(vert):
    vert.tag = True
    yield(vert)
    linked_verts = [e.other_vert(vert) for e in vert.link_edges
            if not e.other_vert(vert).tag]

    for v in linked_verts:
        if v.tag:
            continue
        yield from walk_island(v)


def get_islands(bm, verts):
    #Cred:batFINGER(sxc)
    def tag(verts, switch):
        for v in verts:
            v.tag = switch
    tag(bm.verts, True)
    tag(verts, False)
    islands = []
    verts = set(verts)
    while verts:
        v = verts.pop()
        verts.add(v)
        island = set(walk_island(v))
        islands.append(list(island))
        tag(island, False)
        verts -= island
    return islands


def get_selection_islands(sel_faces, active_face):

    sortfaces = [p for p in sel_faces if p != active_face]
    first_island, second_island = active_face.verts[:], []

    maxcount = len(sortfaces) * 4  # todo: Terrible. better sort tbd.
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
    # stackx to the rescue, with tweaks.
    n = (world_matrix.to_quaternion() @ vec_normal).to_4d()
    n.w = 0
    return world_matrix.to_quaternion() @ (world_matrix.inverted() @ n).to_3d().normalized()


def flatten(nested):
    for item in nested:
        try:
            yield from flatten(item)
        except TypeError:
            yield item


def get_distance(v1, v2):
    dist = [(a - b)**2 for a, b in zip(v1, v2)]
    return sqrt(sum(dist))


def get_midpoint(p1, p2):
	midP = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2]
	return midP


def chunk(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def average_vector(vectors):
    return Vector(sum(vectors, Vector()) / len(vectors))


def cross_coords(coordlist):
    # first 3 coords as tri-plane
    x1, y1, z1 = coordlist[0][0], coordlist[0][1], coordlist[0][2]
    x2, y2, z2 = coordlist[1][0], coordlist[1][1], coordlist[1][2]
    x3, y3, z3 = coordlist[2][0], coordlist[2][1], coordlist[2][2]
    v1 = [x2 - x1, y2 - y1, z2 - z1]
    v2 = [x3 - x1, y3 - y1, z3 - z1]
    cross_product = [v1[1] * v2[2] - v1[2] * v2[1], -1 * (v1[0] * v2[2] - v1[2] * v2[0]), v1[0] * v2[1] - v1[1] * v2[0]]
    return cross_product


def  point_to_plane(first_point, point_verts, plane_verts):
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
        print("geom2 sel 1st", geom2.select)
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


def get_scene_unit(value):
    #insp:Jayanam
    unit_length = bpy.context.scene.unit_settings.length_unit
    unit_scale = bpy.context.scene.unit_settings.scale_length
    value = value * unit_scale
    if unit_length == 'KILOMETERS' :
        return 'km', value * 0.001
    elif unit_length == 'METERS':
        return 'm', value
    elif unit_length == 'CENTIMETERS':
        return 'cm', value * 100
    elif unit_length == 'MILLIMETERS':
        return 'mm', value * 1000
    elif unit_length == 'MICROMETERS':
        return '\u00b5'+'m', value * 1000000
    elif unit_length == 'MILES':
        return 'mi', value * 0.00062137119223733
    elif unit_length == 'FEET':
        return '\u0027', value * 3.280839895013123
    elif unit_length == 'INCHES':
        return '\u0022', value * 39.37007874015748
    elif unit_length == 'THOU':
        return 'thou', value * 39370.07874015748
    else:
        return 'bu', value #1


def shift_list(array, s):
    """Shifts the elements of a list to the left or right."""
    s %= len(array)
    s *= -1
    shifted_array = array[s:] + array[:s]
    return shifted_array