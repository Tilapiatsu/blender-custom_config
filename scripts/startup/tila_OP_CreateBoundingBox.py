import bpy
import numpy as np
import bmesh

bl_info = {
	"name": "Tila : Create Bounding Box",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}

CUBE_FACE_INDICES = (
    (0, 1, 3, 2),
    (2, 3, 7, 6),
    (6, 7, 5, 4),
    (4, 5, 1, 0),
    (2, 6, 4, 0),
    (7, 3, 1, 5),
)


def gen_cube_verts():
    for x in range(-1, 2, 2):
        for y in range(-1, 2, 2):
            for z in range(-1, 2, 2):
                yield x, y, z


def minimum_bounding_box_pca(points):
    """Calculate minimum bounding box using PCA, return bounding box points and face indices"""
    cov_mat = np.cov(points, rowvar=False, bias=True)
    eig_vals, eig_vecs = np.linalg.eigh(cov_mat)

    change_of_basis_mat = eig_vecs
    inv_change_of_basis_mat = np.linalg.inv(change_of_basis_mat)

    aligned = points.dot(inv_change_of_basis_mat.T)

    bb_min = aligned.min(axis=0)
    bb_max = aligned.max(axis=0)

    center = (bb_max + bb_min) / 2
    center_world = center.dot(change_of_basis_mat.T)

    bb_points = np.array(list(gen_cube_verts()), dtype=np.float64)
    bb_points *= (bb_max - bb_min) / 2
    bb_points = bb_points.dot(change_of_basis_mat.T)
    bb_points += center_world

    return bb_points, CUBE_FACE_INDICES


def convert_to_bounding_box(obj: bpy.types.Object):
    verts = obj.data.vertices
    n = len(verts)
    vert_co_arr = np.empty(n * 3)
    verts.foreach_get("co", vert_co_arr)
    vert_co_arr.shape = n, 3

    corners, faces = minimum_bounding_box_pca(vert_co_arr)

    bbox_mesh = bpy.data.meshes.new("bbox")
    bbox_mesh.from_pydata(corners, [], faces)
    bbox_mesh.validate()

    bm = bmesh.new()
    bm.from_mesh(bbox_mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(bbox_mesh)
    bm.free()

    obj.data = bbox_mesh