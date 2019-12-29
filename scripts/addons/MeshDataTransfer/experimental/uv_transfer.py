import bpy
from ..mesh_data_transfer import MeshData, MeshDataTransfer
import bmesh

class UVMeshDataTransfer (object):
    def __init__(self, source, target, world_space = False, deformed_source=False,
                 deformed_target=False, search_method="CLOSEST"):
        self.world_space = world_space
        self.deformed_target = deformed_target
        self.deformed_source = deformed_source
        self.search_method = search_method
        self.source = UVMeshData(source,  deformed=deformed_source , world_space=world_space)
        self.source.get_mesh_data()
        self.source.generate_slice_bvhtree()
        self.target = UVMeshData(target, deformed=deformed_target , world_space=world_space)
        self.target.get_mesh_data()

        self.missed_projections = None
        self.ray_casted = None
        self.hit_faces = None
        self.related_ids = None  # this will store the indexing between

        self.target_shrinked_bmesh = self.target.generate_bmesh(deformed=deformed_target, world_space=world_space)
        self.target_shrinked_bvhtree = None

        self.transfer_uvs()
        # self.cast_verts()
        # self.barycentric_coords = self.get_barycentric_coords(self.ray_casted, self.hit_faces)

    def transfer_uvs(self):

        #let's just brutally transfer all the UVs not caring about the seams
        self.target.transfer_bmesh.verts.ensure_lookup_table ()
        self.target.transfer_bmesh.faces.ensure_lookup_table ()

        self.target_shrinked_bmesh.verts.ensure_lookup_table()
        self.source.transfer_bmesh.faces.ensure_lookup_table ()
        # setting up the np array that is going to contain the transferred uvs
        uv_data = np.zeros (self.target.loops_count * 2 , dtype=np.float64)
        uv_data.shape = (self.target.loops_count, 2)
        # this is an array that is going to check if the vertex has already been processed
        done = np.zeros (self.target.vert_count, dtype=np.bool)

        # getting the uv layer
        uv_layer = self.source.transfer_bmesh.loops.layers.uv.active

        for face in self.target.mesh.polygons:
            for vert_idx , loop_idx in zip (face.vertices , face.loop_indices):

                # get the vertex id
                v = self.target.mesh.vertices[vert_idx]
                # project the mesh the vertex on the source mesh

                if self.search_method == "CLOSEST":
                    projection = self.source.bvhtree.find_nearest (v.co)
                else:
                    v_normal = v.normal
                    projection = self.source.bvhtree.ray_cast (v.co , v_normal)
                    # project in the opposite direction if the ray misses
                    if not projection[0]:
                        projection = self.source.bvhtree.ray_cast (v.co , (v_normal * -1.0))
                if projection[0]:
                    self.target_shrinked_bmesh.verts[vert_idx].co = projection[0]
                    hit_face = self.source.transfer_bmesh.faces[projection[2]] # getting the hit face
                    # getting the corresponding UV coords
                    uv1 = Vector ((hit_face.loops[0][uv_layer].uv[0] , hit_face.loops[0][uv_layer].uv[1] , 0.0))
                    uv2 = Vector ((hit_face.loops[1][uv_layer].uv[0] , hit_face.loops[1][uv_layer].uv[1] , 0.0))
                    uv3 = Vector ((hit_face.loops[2][uv_layer].uv[0] , hit_face.loops[2][uv_layer].uv[1] , 0.0))

                    uv_co = barycentric_transform (projection[0] , hit_face.verts[0].co , hit_face.verts[1].co,
                                                   hit_face.verts[2].co, uv1, uv2, uv3)
                    self.target.mesh.uv_layers.active.data[loop_idx].uv = [uv_co[0],uv_co[1]]
                    uv_data[loop_idx] = [uv_co[0],uv_co[1]]

        self.target_shrinked_bvhtree = BVHTree.FromBMesh(self.target_shrinked_bmesh)
        overlapping_faces = self.get_intersecting_faces(debug=True)
        # readjusting the overlapping uvs
        for face_id in overlapping_faces:
            face = self.target_shrinked_bmesh.faces[face_id]
            # getting the intersecting edges
            intersecting_edges = list()
            intersecting_faces = overlapping_faces[face_id]
            for intersect_id in intersecting_faces:
                edge_id = uv_data.face_edge[intersect_id]
                edge_plane = uv_data.mesh.edges[edge_id]
                v1_id = edge_plane.vertices[0]
                v2_id = edge_plane.vertices[1]
                v1 = uv_data.mesh.vertices[v1_id]
                v2 = uv_data.mesh.vertices[v2_id]
                intersecting_edges.append((v1, v2))

        print(overlapping_faces)

    def get_intersecting_faces(self, debug=False):
        """
        returns the faces on the slice mesh that intersect the mesh_data mesh.
        """
        overlaped_faces = {}
        overlap = self.target_shrinked_bvhtree.overlap (self.source.slice_bvhtree)
        overlap_mesh = self.target.mesh
        faces = overlap_mesh.polygons
        verts = overlap_mesh.vertices
        for face in overlap:
            face_id = face[0]
            if face_id in overlaped_faces.keys ():
                if face[1] not in overlaped_faces[face_id]:
                    overlaped_faces[face_id].append (face[1])
            else:
                overlaped_faces[face_id] = [face[1]]

        if not debug:
            return overlaped_faces
        # -------------------debug------------------------
        flattened = [x[0] for x in overlap]
        current_object = bpy.context.object
        current_mode = bpy.context.object.mode
        if not current_object == self.target.obj:
            if current_mode is not "OBJECT":
                bpy.ops.object.mode_set (mode="OBJECT")
                bpy.context.view_layer.objects.active = self.target.obj
        if not bpy.context.object.mode == "EDIT":
            bpy.ops.object.mode_set (mode="EDIT")
        # get selected vertices
        bpy.ops.mesh.select_all (action='DESELECT')
        bpy.ops.object.mode_set (mode="OBJECT")
        for face_id in flattened:
            if face_id < len (faces):
                faces[face_id].select = True

        bpy.context.view_layer.objects.active = current_object
        bpy.ops.object.mode_set (mode=current_mode)

        return overlaped_faces


    @staticmethod
    def get_barycentric_coords(verts_co, triangles):
        """
        Calculate the barycentric coordinates
        :param verts_co:
        :param triangles:
        :return:
        """

        barycentric_coords = verts_co.copy()
        # calculate vectors from point f to vertices p1, p2 and p3:

        vert_to_corners = np.copy(triangles)
        vert_to_corners[:, 0] -= verts_co  # f1 point 1 of the triangle coord
        vert_to_corners[:, 1] -= verts_co  # f2 point 2 of the triangle coord
        vert_to_corners[:, 2] -= verts_co  # f3 point 3 of the triangle coord

        # main triangle area
        main_triangle_areas = np.cross((triangles[:, 0] - triangles[:, 1]),
                                        (triangles[:, 0] - triangles[:, 2]))  # va
        # calculate vert corners areas
        va1 = np.cross(vert_to_corners[:, 1], vert_to_corners[:, 2])  # va1
        va2 = np.cross(vert_to_corners[:, 2], vert_to_corners[:, 0])  # va2
        va3 = np.cross(vert_to_corners[:, 0], vert_to_corners[:, 1])  # va2
        # getting the magnitude of main triangle areas
        a = np.sqrt ((main_triangle_areas * main_triangle_areas).sum (axis=1))
        # magnitude of the vert corners areas
        barycentric_coords[:, 0] = np.sqrt((va1 * va1).sum (axis=1)) / a * np.sign (
            (va1 * main_triangle_areas).sum(1))
        barycentric_coords[:, 1] = np.sqrt((va2 * va2).sum (axis=1)) / a * np.sign (
            (va2 * main_triangle_areas).sum(1))
        barycentric_coords[:, 2] = np.sqrt((va3 * va3).sum (axis=1)) / a * np.sign (
            (va3 * main_triangle_areas).sum(1))
        return (barycentric_coords)

    @staticmethod
    def calculate_barycentric_location(uv_coords , coords):
        """
        Calculate the vertex position based on the coords
        :param uv_coords:
        :param coords:
        :return:
        """
        # print("UV_coords[0,0] is: ", uv_coords[0, 0])
        # print ("Coords[0,0] is: " , coords[0, 0])
        location = uv_coords[:, 0] * coords[:, 0, None] + \
                   uv_coords[:, 1] * coords[:, 1, None] + \
                   uv_coords[:, 2] * coords[:, 2, None]
        return location

class UVMeshData (MeshData):

    def __init__(self, obj,  deformed=False, world_space=False, uv_space=False, triangulate = True, slice_plane_size=0.1):
        # self.obj = obj
        # self.mesh = obj.data
        super(UVMeshData, self).__init__(obj, deformed=deformed, world_space=world_space,
                                         uv_space=uv_space, triangulate = triangulate)

        self.seam_edges = self.get_seam_edges ()
        self.slice_plane_size = slice_plane_size
        self.face_edge = list()
        self.slice_bvhtree = None

        self.loops_count = len(self.mesh.loops)
        self.vert_count = len(self.mesh.vertices)

        self.uv_data = np.zeros(self.loops_count*2, dtype = np.float64)
        # these arrays are to sort by face and vertex id
        self.face_ids = np.zeros (self.loops_count, dtype=np.int)
        self.vertex_ids = np.zeros (self.loops_count , dtype=np.int)

    def get_uv_coords(self):
        '''
        Get the uv values of the current mesh sorted by polygon
        :return: uvs
        '''
        for face in self.mesh.polygons:
            for vert_idx , loop_idx in zip (face.vertices , face.loop_indices):
                uv_coords = self.mesh.uv_layers.active.data[loop_idx].uv
                self.uv_data[loop_idx] = [uv_coords.x , uv_coords.y]
                self.face_ids[loop_idx] = face.index
                self.vertex_ids[loop_idx] = vert_idx
                # print("face idx: %i, vert idx: %i, uvs: %f, %f" % (face.index, vert_idx, uv_coords.x, uv_coords.y))

    def set_uv_coords(self, uv_coords):
        self.mesh.uv_layers.active.data.foreach_set ("uv" , uv_coords.ravel())

    def get_use_seam_values(self):
        edges = self.mesh.edges
        edges_array = [True] * len (edges)
        edges.foreach_get ("use_seam" , edges_array)
        return edges_array

    def set_use_seam_values(self , edges_array):
        edges = self.mesh.edges
        edges.foreach_set ("use_seam" , edges_array)

    def get_seam_edges(self):

        current_object = bpy.context.object
        current_mode = bpy.context.object.mode
        if not current_object == self.obj:
            if current_mode is not "OBJECT":
                bpy.ops.object.mode_set (mode="OBJECT")
                bpy.context.view_layer.objects.active = self.obj
        if not bpy.context.object.mode == "EDIT":
            bpy.ops.object.mode_set (mode="EDIT")
        # get selected vertices

        verts = self.mesh.vertices
        edges = self.mesh.edges
        current_selection = [0] * len (verts)
        verts.foreach_get ("select" , current_selection)
        # select all edges
        edges.foreach_set ("select" , [True] * len (edges))

        current_edges = self.get_use_seam_values ()

        bpy.ops.uv.seams_from_islands (mark_seams=True , mark_sharp=False)

        verts.foreach_set("select", current_selection)

        bpy.ops.object.mode_set (mode="OBJECT")

        marked_edges = self.get_use_seam_values ()

        self.set_use_seam_values (current_edges)

        seam_edges = list ()
        for i in range (len (edges)):
            edge = edges[i]
            marked = marked_edges[i]
            edge.select = marked
            if marked:
                seam_edges.append (edge)

        bpy.context.view_layer.objects.active = current_object

        bpy.ops.object.mode_set (mode=current_mode)

        return seam_edges

    def generate_slice_bvhtree(self):
        self.slice_bvhtree = self.create_slice_mesh()

    def create_slice_mesh(self):
        '''
        generate a slice mesh from a list of edges
        '''
        plane_size = self.slice_plane_size
        mesh_verts = self.mesh.vertices
        faces = list ()
        verts = list ()
        self.face_edge = list ()

        for edge in self.seam_edges:
            face = list ()
            v1 = mesh_verts[edge.vertices[0]]
            v2 = mesh_verts[edge.vertices[1]]
            face.append (len (verts))
            verts.append (v1.co + ((v1.normal * plane_size) * -1.0))
            face.append (len (verts))
            verts.append (v1.co + (v1.normal * plane_size))
            face.append (len (verts))
            verts.append (v2.co + (v2.normal * plane_size))
            face.append (len (verts))
            verts.append (v2.co + ((v2.normal * plane_size) * -1.0))
            faces.append (face)
            self.face_edge.append (edge.index)

        mesh = bpy.data.meshes.new ("mesh")  # add the new mesh
        mesh.from_pydata (verts , [] , faces)

        # Get a BMesh representation
        bm = bmesh.new()  # create an empty BMesh
        bm.from_mesh(mesh)  # fill it in from a Mesh
        if self.world_space:
            bm.transform(self.obj.matrix_world)
        bmesh.ops.remove_doubles (bm , verts=bm.verts , dist=0.00001)
        bmesh.ops.recalc_face_normals (bm , faces=bm.faces)
        bvhtree = BVHTree.FromBMesh (bm)
        bm.to_mesh(mesh)
        bm.free()
        #bpy.data.meshes.remove(mesh)
        ob = bpy.data.objects.new (mesh.name , mesh)
        col = bpy.data.collections.get ("Collection")
        col.objects.link (ob)

        return bvhtree




def get_intersecting_faces(uv_data, mesh_data, debug=False):
    """
    returns the faces on the slice mesh that intersect the mesh_data mesh.
    """
    overlaped_faces = {}
    overlap = mesh_data.bvhtree.overlap(uv_data.slice_bvhtree)
    overlap_mesh = mesh_data.mesh
    faces = overlap_mesh.polygons
    verts = overlap_mesh.vertices
    for face in overlap:
        face_id = face[0]
        if face_id in overlaped_faces.keys():
            if face[1] not in overlaped_faces[face_id]:
                overlaped_faces[face_id].append(face[1])
        else:
            overlaped_faces[face_id] = [face[1]]

    if debug:
        return overlaped_faces
    # -------------------debug------------------------
    flattened = [x[0] for x in overlap]
    current_object = bpy.context.object
    current_mode = bpy.context.object.mode
    if not current_object == mesh_data.obj:
        if current_mode is not "OBJECT":
            bpy.ops.object.mode_set (mode="OBJECT")
            bpy.context.view_layer.objects.active = mesh_data.obj
    if not bpy.context.object.mode == "EDIT":
        bpy.ops.object.mode_set (mode="EDIT")
    # get selected vertices
    bpy.ops.mesh.select_all (action='DESELECT')
    bpy.ops.object.mode_set (mode="OBJECT")
    for face_id in flattened:
        if face_id < len(faces):
            faces[face_id].select=True

    bpy.context.view_layer.objects.active = current_object
    bpy.ops.object.mode_set (mode=current_mode)

    return overlaped_faces



def create_projected_mesh(source, target,  search_method = "CLOSEST"):
    '''
    create a shrink wrapped mesh
    '''
    data_transfer = MeshDataTransfer(source, target , search_method = search_method)
    vert_position = data_transfer.get_projected_vertices_on_source()
    # print(vert_position)
    # create a mesh
    # Get a BMesh representation
    mesh = target.data.copy()
    mesh.name = "{}_progected".format(target.data.name)
    mesh.vertices.foreach_set("co", vert_position.ravel())

    ob = bpy.data.objects.new ("{}_projectd".format(target.name) , mesh)
    col = bpy.data.collections.get ("Collection")
    col.objects.link (ob)
    return ob


def project_point_on_edge(vertex, previous_vertex, next_vertex , edge , flip_normal=False):
    '''

    :param point:
    :param edge:
    :param flip_normal:
    :return:
    '''
    stuck = False
    epsilon = sys.float_info.epsilon
    v1 = edge[0]
    v2 = edge[1]
    # edge normal
    edge_normal = (v1.normal + v2.normal) * 0.5
    edge_normal.normalize()
    both_norm_dir = edge_normal.dot (vertex.normal)
    if both_norm_dir < epsilon:
        # print("\n================================\nVertex normal and edge normal are inverse.\n================================\n")
        return

    # getting the edge direction
    edge_direction = (v1.co - v2.co)
    edge_direction.normalize ()
    # getting the plane perpendicular to the edge normal
    plane_no = edge_normal.cross (edge_direction)
    plane_co = (v1.co + v2.co) * 0.5
    if flip_normal:
        plane_no = plane_no * -1.0
    # check if the vertex position is on the right side of the plane
    dist = distance_point_to_plane (vertex.co , plane_co , plane_no)
    # if the distance is negative it means this point is on the other side
    if dist < epsilon:
        # print("{} Point is on the other side of the plane.".format(vertex.index))
        return

    crossing_coords = list()

    # checking if the edges of the vertex are crossing the edge plane
    if distance_point_to_plane(next_vertex.co , plane_co , plane_no) < 0.0:
        # print("next vertex is crossing the plan")
        crossing_coords.append(next_vertex.co)

    if distance_point_to_plane (previous_vertex.co , plane_co , plane_no) < 0.0:
        # print ("previous vertex is crossing the plan")
        crossing_coords.append (previous_vertex.co)

    # calculating edge direction
    if crossing_coords:
        opposite_point = crossing_coords[0]
        if len(crossing_coords) == 2: # getting the average of the normal
            opposite_point = (crossing_coords[0] + crossing_coords[1])*0.5
        point_on_plane = intersect_line_plane(opposite_point, vertex.co, plane_co, plane_no)
    # if the
    else:
        print("Sticking {} on plane \n =======================".format(vertex.index))
        stuck = True
        point_on_plane = ((plane_no * -1.0) * dist) + vertex.co
    # checking if the point is between the the vertex planes
    # print(point_on_plane)
    if not point_on_plane:
        print("\n=============================\nMissed projection for {}.\n=============================".format(vertex.index))
        return
    # calculating the v1 plane
    v1_plane = (v1.normal.cross(edge_normal)).cross(v1.normal)

    v1_dist = distance_point_to_plane (point_on_plane , v1.co , v1_plane )
    if not stuck:
        if v1_dist <= epsilon:
            print ("\n================================\nPoint {} is  not between edges.\n================================\n".format(vertex.index))
            return
        # calculating the v1 plane
        v2_plane = (v2.normal.cross(edge_normal)).cross(v2.normal)

        v2_dist = distance_point_to_plane (point_on_plane , v2.co , v2_plane)
        if v2_dist <= epsilon:
            print ("\n================================\nPoint {} is  not between edges.\n================================\n".format(vertex.index))
            return

    # moving on the edge
    point_on_line = intersect_point_line (point_on_plane , v1.co , v2.co)
    # adding a small offset to the edge
    offset = plane_no * 0.01

    point = point_on_line[0] # - offset


    return point


def project_vertex_on_edges(vertex, previous_vertex, next_vertex, edges, flip_normal=False):

    for edge in edges:
        # print ("Edge is: \n" , edge)
        # print("vertex is: \n", vertex,"==============\n")
        p = project_point_on_edge(vertex, previous_vertex, next_vertex, edge, flip_normal=flip_normal)
        if p:
            return p

def get_seam_face(face_mesh, face, cut_edges):
    # print("Calculating regular face.\n\n")
    regular_face = get_cut_face(face_mesh, face, cut_edges, flip_normal=False)
    # print ("Calculating flipped face.\n\n")
    flipped_face = get_cut_face(face_mesh, face, cut_edges, flip_normal=True)
    regular_area = polygon_area(regular_face)
    # print ("Regular area is: ",regular_area,"\n====================\n")
    flipped_area = polygon_area(flipped_face)
    # print("Flipped area is: ",flipped_area,"\n====================\n")
    if regular_area >= flipped_area:
        return regular_face
    else:
        return flipped_face

def get_cut_face(face_mesh, face, cut_edges, flip_normal=False):
    # intersecting_pair = list()
    intersecting_points = list()

    verts = face_mesh.vertices
    cut_face = list()
    for i in range(len(face.vertices)):
        previous_v = verts[face.vertices[i-1]]
        v = verts[face.vertices[i]]
        next_v_id = i+1
        if next_v_id > len(face.vertices)-1:
            next_v_id = 0
        next_v = verts[face.vertices[next_v_id]]

        p = project_vertex_on_edges(v,previous_v, next_v, cut_edges, flip_normal=flip_normal)
        if p:
            cut_face.append(p)
        else:
            cut_face.append(v.co)

    return cut_face


def polygon_area(points):
    """Return the area of the polygon whose vertices are given by the
    sequence points.

    """
    area = 0
    q = points[-1]
    for p in points:
        area += p[0] * q[1] - p[1] * q[0]
        q = p
    return abs(area / 2)





# def is_between( a , b , c):
#     '''
#     Check if point c is on segment a, b
#     '''
#     crossproduct = (b - a).cross (c - a)
#     crossproduct = crossproduct.length
#     # compare versus epsilon for floating point values, or != 0 if using integers
#     print (crossproduct)
#     epsilon = sys.float_info.epsilon
#     if round (abs (crossproduct)) > epsilon:
#         # print("not parallel")
#         return False
#
#     dotproduct = (b - a).dot (c - a)
#     if dotproduct < 0.0:
#         return False
#
#     squaredlengthba = (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y) + (b.z - a.z) * (b.z - a.z)
#     if dotproduct > squaredlengthba:
#         return False
#
#     return True
#
#
# def intersect_edges_plane_on_edge( edge_plane , edge):
#     """
#     find the intersection between a given edge and the plane projected from an other edge
#     """
#     epsilon = sys.float_info.epsilon
#
#     # get the perpendicular plane to the edge
#     edge_plane_normal = (edge_plane[0].normal + edge_plane[1].normal) * 0.5
#     edge_normal = (edge[0].normal + edge[1].normal) * 0.5
#     # check if the edges are facing the same direction, return if they don't
#     both_norm_dir = edge_normal.dot (edge_plane_normal)
#     if both_norm_dir < epsilon:
#         return
#
#     # find the intersection between the vector and the plane
#     edge_plane_direction = (edge_plane[0].co - edge_plane[1].co)
#     edge_plane_direction.normalize ()
#     print ("edge plane direction is: " , edge_plane_direction)
#     edge_cross_plane = edge_plane_normal.cross (edge_plane_direction)
#     edge_plane_position = (edge_plane[0].co + edge_plane[1].co) * 0.5
#     p = intersect_line_plane (edge[0].co , edge[1].co , edge_plane_position , edge_cross_plane , False)
#     # check if the point is actually on the edge
#     if not p:
#         print("missed projection")
#         return
#     is_on_edge = is_between (edge[0].co , edge[1].co , p)
#     # return in the intersected point is not on edge
#     if not is_on_edge:
#         print ("point is not on edge")
#         return
#     # project the point on the segment back to the plane
#     edge_plane_direction = edge_plane_direction.cross (Vector ((0.0 , 1.0 , 0.0)))
#
#     inverted = edge_plane_normal.cross (edge_plane_direction)
#     planes_intersect = intersect_line_plane (edge_plane[0].co , edge_plane[1].co , p , inverted , False)
#     is_on_edge = is_between (edge_plane[0].co , edge_plane[1].co , planes_intersect)
#     if not is_on_edge:
#         print ("point is not on edge")
#         return
#
#     return p

def transfer_uvs(source, target, world_space):
    uv_data = UVMeshData (source, slice_plane_size=0.1)
    uv_data.get_mesh_data()
    uv_data.generate_slice_bvhtree ()
    proj_mesh = create_projected_mesh (source , target)
    print("Projected mesh is: {} \n=========================\n".format(proj_mesh.name))
    mesh_data = UVMeshData (proj_mesh , world_space=world_space, triangulate=False)
    mesh_data.get_mesh_data()
    overlapped_faces=get_intersecting_faces (uv_data , mesh_data)
    #print("overlapped \n", overlapped_faces, "\n===============\n")
    # generating the cut mesh for projection
    uv_faces = list()
    uv_verts = list()
    # create a separate polygons mesh

    for face in proj_mesh.data.polygons:
        uv_face = list()
        print("Face {} on : {}\n".format(face.index, target.name))
        #getting the planes intersecting with the face
        for v in face.vertices:
            v = proj_mesh.data.vertices[v]
            uv_face.append(len(uv_verts))
            uv_verts.append(v.co)
        uv_faces.append(uv_face)

    # moving the overlapping edges
    proj_verts = proj_mesh.data.vertices
    for face_id in overlapped_faces:
        ref_face = proj_mesh.data.polygons[face_id]
        intersecting_edges = list()
        intersected_faces = overlapped_faces[face_id]
        # getting all the intersecting edges
        for intersect_id in intersected_faces:
            edge_id = uv_data.face_edge[intersect_id]
            edge_plane = uv_data.mesh.edges[edge_id]
            v1_id = edge_plane.vertices[0]
            v2_id = edge_plane.vertices[1]
            v1 = uv_data.mesh.vertices[v1_id]
            v2 = uv_data.mesh.vertices[v2_id]
            intersecting_edges.append((v1, v2))
        cut_face = get_seam_face(proj_mesh.data, ref_face, intersecting_edges)

        uv_face = uv_faces[face_id]
        if len(cut_face) == len(uv_face):
            for i in range (len (uv_face)):
                cut_co = cut_face[i]
                v_id = uv_face[i]
                uv_verts[v_id] = cut_co

    mesh = bpy.data.meshes.new ("uv_mesh")  # add the new mesh
    mesh.from_pydata (uv_verts , [] , uv_faces)
    ob = bpy.data.objects.new (mesh.name , mesh)
    col = bpy.data.collections.get ("Collection")
    col.objects.link (ob)




    # face_id = face.index
    # if face_id in overlapped_faces:
    #     # getting the seam edges intesecting
    #     intersecting_edges = list ()
    #     for id in overlapped_faces[face_id]:
    #
    #         edge_id = uv_data.face_edge[id]
    #         edge_plane = uv_data.mesh.edges[edge_id]
    #         intersecting_edges.append(edge_plane.vertices)
    #     print (intersecting_edges,"\n")
    #     intersect_points = []
    #     uv_face=list()
    #     for i in range(len(face.vertices)):
    #
    #         next_vertex = i +1
    #         if i == len(face.vertices)-1:
    #             next_vertex = 0
    #         edge = (face.vertices[i], face.vertices[next_vertex])
    #         for plane_edge in intersecting_edges:
    #             intersecting_point = intersect_edges_plane_on_edge(plane_edge.vertices, edge)
    #             if intersect_points:
    #                 intersect_points.append()







