# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Copyright (C) 2022 VFX Grace - All Rights Reserved
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bmesh
import bpy
import bgl
import gpu
from gpu_extras.batch import batch_for_shader
from sys import exc_info
from bmesh import from_edit_mesh
from bpy_extras import view3d_utils, mesh_utils
from math import fabs, degrees, radians, sqrt, cos, sin, pi
from mathutils.geometry import tessellate_polygon as tessellate
from bgl import (
        glLineWidth,
        glEnable,
        glDisable,
        GL_DEPTH_TEST,
        GL_BLEND,
        )
from . import report
from . import operators

if not bpy.app.background:
    single_color_shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
else:
    single_color_shader = None

COLOR_POINT = (1.0, 0.0, 1.0, 1)
COLOR_LINE = (0.0623639, 0.0623639, 0.0622395, 0.3) #(0.5, 0.5, 1, 1)
draw_enabled = [False]
edge_width = [1.0]
bm_old = [None]


def draw_poly(points,rgba):
    batch = batch_from_points(points, "TRIS")
    single_color_shader.bind()
    single_color_shader.uniform_float("color",rgba)
    batch.draw(single_color_shader)

def draw_points(points,rgba):
    batch = batch_from_points(points, "POINTS")
    single_color_shader.bind()
    single_color_shader.uniform_float("color", rgba)
    batch.draw(single_color_shader)

def draw_line(points,rgba):
    batch = batch_from_points(points, "LINES")
    single_color_shader.bind()
    single_color_shader.uniform_float("color", rgba)
    batch.draw(single_color_shader)

def batch_from_points(points, type):
    return batch_for_shader(single_color_shader, type, {"pos" : points})



def draw_callback():
    obj = bpy.context.object
    check = bpy.context.scene.check
    is_show_color = check.is_show_color
    if obj and obj.type == 'MESH':
        # if draw_enabled[0]:s
        mesh = obj.data
        matrix_world = obj.matrix_world

        glLineWidth(edge_width[0])

        if bpy.context.mode == 'EDIT_MESH':
            use_occlude = True

            if bm_old[0] is None or not bm_old[0].is_valid:
                bm = bm_old[0] = bmesh.from_edit_mesh(mesh)
                bm = bmesh.from_edit_mesh(mesh)
            else:
                bm = bm_old[0]

            obfaces = bm.faces
            obedges = bm.edges
            obverts = bm.verts


            info = report.info()
            myverts_list = []
            my_edges = []
            my_faces_vertices = []
            my_edges_vertices = []
            for i, (text, data) in enumerate(info):
                bm_type, bm_array,custom_rgb = data
                rgba = (custom_rgb[0], custom_rgb[1], custom_rgb[2], 1.0)

                if bm_type == bmesh.types.BMVert:
                    if check.loose_points and text.startswith("Loose_Points"):
                        myverts_list.append((bm_array,rgba))
                    elif check.doubles and text.startswith("Double Verts"):
                        myverts_list.append((bm_array,rgba))
                    elif check.use_verts and text.startswith("Use Verts"):
                        myverts_list.append((bm_array,rgba))

                if bm_type == bmesh.types.BMEdge:
                    if (check.use_multi_face and text.startswith("Use Mult Face") or (check.use_boundary and text.startswith("Use Boundary")) or (check.loose_edges and text.startswith("Loose_Edges"))):
                        if len(bm_array) > 0:
                            for e in bm_array:
                                my_edges_vertices.append((e,[(obedges[e].verts[i].co) for i in range(len(obedges[e].verts))],rgba))



                if bm_type == bmesh.types.BMFace:
                    rgba = (custom_rgb[0], custom_rgb[1], custom_rgb[2], 0.4)
                    if (check.triangles and text.startswith("Triangles") or check.ngons and text.startswith("Ngons")
                        or check.distort and text.startswith("Non-Flat Faces") or check.intersect and text.startswith("Intersect Face")
                        or check.degenerate and text.startswith("Zero Faces") or check.loose_faces and text.startswith("Loose Faces")):
                        if len(bm_array) > 0:
                            for f in bm_array:
                                my_faces_vertices.append((f,[(obfaces[f].verts[i].co) for i in range(len(obfaces[f].verts))],rgba))
            
            if len(myverts_list) >0:
                for i,(bm_array,rgba) in enumerate(myverts_list):
                    verts = [tuple((matrix_world @ obverts[i].co).to_3d()) for i in bm_array]
                    #color = myverts_list[i][1]
                    #rgba = (color[0], color[1], color[2], 1.0)
                    draw_points(verts,rgba)

          
            # if len(my_edges) > 0:
                # for j in range(len(my_edges)):
                    # #print(my_edges)
                    # for i in my_edges[j][0]:
                        # #edge = obedges[i]
                        # edges = [tuple((matrix_world @ vert.co).to_3d()) for vert in obedges[i].verts]
                        # color = my_edges[j][1]
                        # rgba = (color[0], color[1], color[2], 1.0)
                        # draw_line(edges,rgba)
            if len(my_edges_vertices) > 0:
                for i,(f,verts,rgba) in enumerate(my_edges_vertices):
                    edges = [tuple((matrix_world @ vert).to_3d()) for vert in verts]
                    draw_line(edges,rgba)

            if len(my_faces_vertices) > 0:
                for i,(f,verts,rgba) in enumerate(my_faces_vertices):
                    if len(verts) == 3:
  
                        # faces = [tuple((matrix_world @ vert.co).to_3d()) for i in range(len(obfaces)) for vert in obfaces[i].verts]
                        # draw_poly(faces,COLOR_LINE)

                        faces = [tuple((matrix_world @ vert).to_3d()) for vert in verts]
                        draw_poly(faces,rgba)

                        for edge in obfaces[f].edges:
                            if edge.is_valid:
                                edges = [tuple((matrix_world @ vert.co).to_3d()) for vert in edge.verts]
                                draw_line(edges,COLOR_LINE)

                    elif len(verts) >= 4:
                            new_faces = []
                            faces = []
                            face = obfaces[f]
                            indices = [v.index for v in face.verts]
                            for pol in tessellate([verts]):
                                new_faces.append([indices[i] for i in pol])

                            for f in new_faces:
                                faces.append(
                                        [((matrix_world @ bm.verts[i].co)[0] + face.normal.x * 0.001,
                                        (matrix_world @ bm.verts[i].co)[1] + face.normal.y * 0.001,
                                        (matrix_world @ bm.verts[i].co)[2] + face.normal.z * 0.001)
                                        for i in f]
                                        )

                            for f in faces:
                                draw_poly(f,rgba)

                            for edge in face.edges:
                                if edge.is_valid:
                                    edges = [matrix_world @ vert.co for vert in edge.verts]
                                    draw_line(edges,COLOR_LINE)
            glDisable(GL_BLEND)
            glLineWidth(edge_width[0])
            glEnable(GL_DEPTH_TEST)



def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=False):
    """
    Returns a transformed, triangulated copy of the mesh
    """

    assert obj.type == 'MESH'

    if apply_modifiers and obj.modifiers:
        import bpy
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        me = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        obj_eval.to_mesh_clear()
        del bpy
    else:
        me = obj.data
        if obj.mode == 'EDIT':
            bm_orig = from_edit_mesh(me)
            bm = bm_orig.copy()
        else:
            bm = bmesh.new()
            bm.from_mesh(me)



    if transform:
        bm.transform(obj.matrix_world)

    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm


def bmesh_from_object(obj):
    """
    Object/Edit Mode get mesh, use bmesh_to_object() to write back.
    """
    me = obj.data
    is_editmode = (obj.mode == 'EDIT')
    if is_editmode:
        bm = bmesh.from_edit_mesh(me)
    else:
        bm = bmesh.new()
        bm.from_mesh(me)
    return bm




def bmesh_check_self_intersect_object(obj):
    """
    Check if any faces self intersect

    returns an array of edge index values.
    """
    import array
    import mathutils

    if not obj.data.polygons:
        return array.array('i', ())

    bm = bmesh_copy_from_object(obj, transform=False, triangulate=False)
    tree = mathutils.bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
    overlap = tree.overlap(tree)
    faces_error = {i for i_pair in overlap for i in i_pair}

    return array.array('i', faces_error)


def face_is_distorted(ele,distort_min,angle_distort):
    no = ele.normal
    angle_fn = no.angle

def face_is_distorted(ele, angle_distort):
    no = ele.normal
    angle_fn = no.angle

    for loop in ele.loops:
        loopno = loop.calc_normal()

        if loopno.dot(no) < 0.0:
            loopno.negate()

        if angle_fn(loopno, 1000.0) > angle_distort:
            return True
    return False
