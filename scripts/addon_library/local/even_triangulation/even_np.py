

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Created by Kushiro

import math
from operator import indexOf

import bpy
import bmesh
import bmesh.utils

from mathutils import Matrix, Vector, Quaternion, Euler

import mathutils
import time


import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
    StringProperty
)


import random
import itertools



from pprint import pprint
# from . import gui

# import itertools

from . import piptool

piptool.install_package('scipy')

import numpy as np
from scipy.spatial import Delaunay





def dotmat(point, mat):
    point_homogeneous = np.append(point, 1)
    transformed_point = np.dot(mat, point_homogeneous)    
    return transformed_point[:2]




def point_in_polygon(point, polygon):
    x, y = point
    n_vertices = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n_vertices + 1):
        p2x, p2y = polygon[i % n_vertices]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_intersect = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= x_intersect:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside




def get_mat(basis1, sn, origin=None):
    if origin is None:
        origin = np.zeros(3)        
    basis2 = np.cross(sn, basis1)    
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, 0] = basis1
    transformation_matrix[:3, 1] = basis2
    transformation_matrix[:3, 2] = sn
    transformation_matrix[:3, 3] = origin
    return transformation_matrix.T


def normalize(v):
    return v / np.linalg.norm(v)




def make_points(bm, ts, prop_plen):
    edge1 = ts[:, 1] - ts[:, 0]
    edge2 = ts[:, 2] - ts[:, 0]
    cross_product = np.cross(edge1, edge2)
    areas = 0.5 * np.linalg.norm(cross_product, axis=1)
    normalized_areas = areas / np.sum(areas)
    cdf = np.cumsum(normalized_areas)

    num_samples = int(1.0 / (prop_plen * prop_plen * prop_plen))

    random_numbers = np.random.uniform(0, 1.0, num_samples)
    sampled_indices = np.searchsorted(cdf, random_numbers)
    sam = ts[sampled_indices]

    # weight = np.random.uniform(0, 1.0, (num_samples, 3))
    # # normalize weights of each row to 1
    # weight = weight / np.sum(weight, axis=1)[:, None]
    sqrts = np.sqrt(np.random.random((num_samples, 1)))
    t1 = np.random.random((num_samples, 1))
    weight = np.hstack((1 - sqrts, sqrts * (1 - t1), sqrts * t1))    
    
    # points = np.sum(sam * weight[:, :, None], axis=1)  
    # use numpy einsum to speed up
    points = np.einsum('ij,ijk->ik', weight, sam)
    
    
    return points, sampled_indices





def get_faces_points(bm, sel, prop_plen):
    res = bmesh.ops.duplicate(bm, geom=sel)
    dup = [f for f in res['geom'] if isinstance(f, bmesh.types.BMFace)]
    fmap2 = res['face_map']
    selvs = {}
    for f1 in dup:
        ori = fmap2[f1]
        # vs = [v for v in ori.verts]
        selvs[f1] = ori

    res = bmesh.ops.triangulate(bm, faces=dup)
    fs = res['faces']
    fmap = res['face_map']
    tri_sel = {}    
    for tri in fs:
        if tri not in fmap:
            tri_sel[tri] = selvs[tri]
        else:
            dup = fmap[tri]
            tri_sel[tri] = selvs[dup]
    tri = []
    fsvs = []
    sns = []
    for f1 in fs:
        t1 = [v1.co for v1 in f1.verts]
        fsvs.append(list(f1.verts))
        tri.append(t1)
        sns.append(np.array(f1.normal))
    tss = np.array(tri)
    # bmesh.ops.delete(bm, geom=fs, context='FACES')
    vs2, si = make_points(bm, tss, prop_plen)
    return vs2, si, fsvs, sns, tri_sel, fs

    

def split_edges(bm, sel, plen):
    es = set()
    for f1 in sel:
        for e1 in f1.edges:
            es.add(e1)
    es = list(es)
    plen2 = plen * 2
    for e1 in es:
        elen = e1.calc_length()
        num = int(elen / plen2)
        if num > 0:            
            # bmesh.ops.subdivide_edges(bm, edges=[e1], cuts=num)
            bmesh.ops.bisect_edges(bm, edges=[e1], cuts=num)



def smooth(triangles, vlen, vs3, nt2):
    tris = nt2[triangles]    
    cens = np.mean(tris, axis=1)
    area = np.linalg.norm(np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]), axis=1)
    # area = np.sqrt(area)
    cens2 = cens * area[:, None]

    pslen = len(vs3)
    vmap = []
    areas = []
    for i in range(pslen):
        vmap.append([])
        areas.append(0)

    for i, tri in enumerate(triangles):
        for idx in tri:
            vmap[idx].append(cens2[i])
            areas[idx] += area[i]

    for i, p in enumerate(vs3):
        if i < vlen:
            continue
        cs = vmap[i]
        if len(cs) > 2:
            cs2 = np.vstack(cs)
            # v2 = np.mean(cs2, axis=0)
            v2 = np.sum(cs2, axis=0) / areas[i]
        elif len(cs) == 1:
            v2 = cs[0]
        else:
            continue
        # print(v2)
        p.co = Vector(v2)
   





def points_inside_polygon(points, vertices):
    n_vertices = len(vertices)
    inside = np.zeros(points.shape[0], dtype=bool)
    p1 = vertices[0]
    for i in range(n_vertices + 1):
        p2 = vertices[i % n_vertices]
        min_p1_p2_y = np.minimum(p1[1], p2[1])
        max_p1_p2_y = np.maximum(p1[1], p2[1])
        max_p1_p2_x = np.maximum(p1[0], p2[0])
        in_range_y = np.logical_and(points[:, 1] > min_p1_p2_y, points[:, 1] <= max_p1_p2_y)
        in_range_x = points[:, 0] <= max_p1_p2_x
        if p1[1] != p2[1]:
            x_intercepts = (points[:, 1] - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
            in_range = np.logical_and(in_range_y, in_range_x)
            crossing = np.logical_and(in_range, points[:, 0] <= x_intercepts)
            inside[crossing] = np.logical_not(inside[crossing])
        p1 = p2
    return inside




def triangulate(bd, allvs, sn):
    m1 = bd[1] - bd[0]
    m1 = normalize(m1)
    sn = normalize(sn)
    mat = get_mat(m1, sn, bd[0])
    mat2 = np.linalg.inv(mat)

    b1 = np.hstack((bd, np.ones((len(bd), 1))))
    bounds = np.dot(b1, mat2)
    bounds = bounds[:, :2]

    psh2 = np.hstack((allvs, np.ones((len(allvs), 1))))
    ps2 = np.dot(psh2, mat2)
    ps2 = ps2[:, :2]

    hull = Delaunay(ps2)
    tri = hull.simplices
    v1 = ps2[tri[:, 0]]
    v2 = ps2[tri[:, 1]]
    v3 = ps2[tri[:, 2]]
    cen = (v1 + v2 + v3) / 3
    # print(tri)

    valid = points_inside_polygon(cen, bounds)
    # print(valid)
    tri = tri[valid]
    # triangles = [[vs[tri[i, 0]], vs[tri[i, 1]], vs[tri[i, 2]]] for i in range(len(tri))]
    return tri




def gen_poly(sel, indices_dict, tfs, tri_sel, vs2):
    poly = {}
    for f1 in sel:
        poly[f1] = list(f1.verts)

    for k in indices_dict:
        tri = tfs[k]
        # t1 = fsvs[k]        
        f1 = tri_sel[tri]
        vs4 = []
        for i in indices_dict[k]:
            v1 = vs2[i]
            vs4.append(v1)        
        poly[f1].extend(vs4)
    return poly


def gen_tris(sel, poly):
    tris = []
    for f1 in sel:
        vs3 = poly[f1]
        nt1 = np.array([v.co for v in f1.verts])
        nt2 = np.array([v.co for v in vs3])
        sn = np.array(f1.normal)
        triangles = triangulate(nt1, nt2, sn)
        tris.append((triangles, vs3, nt2, len(f1.verts)))
    return tris



def get_points(bm, sel, prop_plen):
    res = get_faces_points(bm, sel, prop_plen)
    if res == None:
        return None
    points, si, fsvs, sns, tri_sel, tfs = res

    split_edges(bm, sel, prop_plen)
    vs2 = []
    for v1 in points:
        k1 = bm.verts.new(v1)
        vs2.append(k1)

    uni, inverse = np.unique(si, return_inverse=True)
    # print(si)
    # print(uni)
    # print(inverse)
    indices_dict = {value: [] for value in uni}
    # bmesh.ops.delete(bm, geom=sel, context='FACES_ONLY')

    for idx, inv in enumerate(inverse):
        indices_dict[uni[inv]].append(idx) 

        # smooth(triangles, len(f1.verts), vs3, nt2)
    poly = gen_poly(sel, indices_dict, tfs, tri_sel, vs2)

    for i in range(3):
        tris = gen_tris(sel, poly)
        for triangles, vs3, nt2, vlen in tris:
            smooth(triangles, vlen, vs3, nt2)

    tris = gen_tris(sel, poly)

    for triangles, vs3, _, _ in tris:
        for t in triangles:
            p1, p2, p3 = t
            v1 = vs3[p1]
            v2 = vs3[p2]
            v3 = vs3[p3]
            try:      
                bm.faces.new([v1, v2, v3])     
            except:
                pass
                # print('error')

    bmesh.ops.delete(bm, geom=sel, context='FACES_ONLY')
    bmesh.ops.delete(bm, geom=tfs, context='FACES')



        


# class SDModelerOperator(bpy.types.Operator):
#     """Tooltip"""
#     bl_idname = "mesh.sd_modeler_operator"
#     bl_label = "testing"
#     bl_options = {"REGISTER", "UNDO"}
#     #, "GRAB_CURSOR", "BLOCKING"


#     prop_plen: FloatProperty(
#         name="Size",
#         description="Size",
#         default=0.1,
#         step=0.01,
#         min=0.001
#     )    
 



#     def get_bm(self):
#         obj = bpy.context.active_object
#         me = obj.data
#         bm = bmesh.from_edit_mesh(me)
#         return bm



            

#     def process(self, context):
#         bm = self.get_bm() 
#         sel = [f1 for f1 in bm.faces if f1.select]
#         get_points(bm, sel, self.prop_plen)
    
#         obj = bpy.context.active_object                
#         me = bpy.context.active_object.data
#         bmesh.update_edit_mesh(me)  


