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


import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
    StringProperty
)

from pprint import pprint

import itertools
import numpy as np
from mathutils.geometry import intersect_line_line

import random


class Vert:
    def __init__(self) -> None:
        self.co = None


class Loop:
    def __init__(self) -> None:
        self.vert = Vert()
        self.link_loop_next = None
        self.link_loop_prev = None
        self.deg = None
        self.next = None
        self.realvert = None
        self.remain = 0
        self.fix = False
        self.mid = None
        self.value = 0
        self.index = 0


mat = None

def link_loops(ps):
    for i , p1 in enumerate(ps):
        p2 = ps[(i + 1) % len(ps)]
        p1.link_loop_next = p2
        p2.link_loop_prev = p1



def create_ps(f1, mat):
    ps = []
    for p1 in f1.loops:
        p2 = Loop()
        p2.index = p1.vert.index
        p2.vert.co = mat @ p1.vert.co
        p2.realvert = p1.vert
        ps.append(p2)
    link_loops(ps)        
    return ps
    

def intersect2d(p1, p2, p3, p4):
    res = mathutils.geometry.intersect_line_line_2d(p1.xy, p2.xy, p3.xy, p4.xy)
    if res != None:
        return Vector((res[0], res[1], 0))
    return None


def get_matrix_face(f1):
    p1 = f1.loops[0]
    m1 = Vector()
    for p2 in f1.loops:
        p3 = p2.link_loop_next
        m1 = p3.vert.co - p2.vert.co
        if m1.length > 0:
            break
    if m1.length == 0:
        return None
    m2 = f1.normal.cross(m1)
    mat = get_matrix(m1, m2, f1.normal, p1.vert.co)
    return mat.inverted()



def get_matrix(m1, m2, m3, cen):
    if m1.length == 0 or m2.length == 0 or m3.length == 0:
        return Matrix.Identity(4)            
    m = Matrix.Identity(4)        
    m[0][0:3] = m1.normalized()
    m[1][0:3] = m2.normalized()
    m[2][0:3] = m3.normalized()
    m[3][0:3] = cen.copy()
    m = m.transposed()
    return m    



def get_mid(m1, m2, sn):
   c1 = m1.cross(sn) * -1
   c2 = m2.cross(sn)
   c3 = c1.normalized() + c2.normalized()
   return c3.normalized() 


def get_ps_mid(p1, sn):
    p2 = p1.link_loop_next
    p3 = p1.link_loop_prev
    m1 = p2.vert.co - p1.vert.co
    m2 = p3.vert.co - p1.vert.co
    return get_mid(m1, m2, sn)

def angle(p1):
    p2 = p1.link_loop_next
    p3 = p1.link_loop_prev
    m1 = p2.vert.co - p1.vert.co
    m2 = p3.vert.co - p1.vert.co
    if m1.length == 0 or m2.length == 0:
        return 0
    return m1.angle(m2)



def is_concave(p1, sn):
    p2 = p1.link_loop_next
    p3 = p1.link_loop_prev
    m1 = p2.vert.co - p1.vert.co
    m2 = p3.vert.co - p1.vert.co
    c1 = m1.cross(m2)
    if c1.dot(sn) < 0:
        return True
    return False

def make_mid_loop(ps, sn, mlen):
    ps2 = []
    for p1 in ps:
        # if is_concave(p1, sn):
        #     p2 = Loop()
        #     p2.vert.co = p1.vert.co.copy()
        # else:
        mid = get_ps_mid(p1, sn)
        p2 = Loop()
        d1 = angle(p1)
        p1.deg = math.sin(d1 / 2)
        if p1.deg == 0:
            p2.vert.co = p1.vert.co.copy()
        else:
            d2 = mlen / p1.deg
            p2.vert.co = p1.vert.co + mid * d2
        p1.next = p2
        
        ps2.append(p2)
    link_loops(ps2)
    return ps2



def filter_same(ps):
    psk = list(ps)
    while True:
        ps2 = []
        changed = False
        for i in range(len(psk)):
            i2 = (i + 1) % len(psk)
            v1 = psk[i]
            v2 = psk[i2]
            if v1 == v2:
                changed = True
                continue
            ps2.append(v1)
        psk = ps2
        if not changed:
            break
    return psk


def get_links(v1, v2):
    if v1 == v2:
        return []
    vk = v1
    vs = []
    while True:
        vk = vk.link_loop_next        
        if vk == None:
            return []
        if vk == v2:
            return vs
        if vk == v1:
            return None
        vs.append(vk)


def edge_dist(A, B, P):
    C = B - A
    if C.length == 0:
        return (P - A).length
    diff = P - A
    t = diff.dot(C) / C.dot(C)
    t = min(max(t, 0), 1)
    K = A + C * t
    d1 = (K - P).length    
    return d1



def min_value(d1, d2):
    if d1 == None and d2 == None:
        return None
    if d1 == None:
        return d2
    elif d2 == None:
        return d1
    return min(d1, d2)



def distance_point_to_segment(p, a, b):
    v = b - a
    w = p - a
    t = w.dot(v) / v.dot(v)
    if t < 0.0:
        return (p - a).length
    elif t > 1.0:
        return (p - b).length
    else:
        projection = a + t * v
        return (p - projection).length
    





def get_ps_center(ps):
    cen = Vector((0, 0, 0))
    for p1 in ps:
        cen += p1.vert.co
    cen /= len(ps)
    return cen



def merge_ps(ps, ps2, offset):
    dsize = len(ps2)
    links = np.zeros((dsize, dsize))
    for i in range(len(ps2)):
        i2 = (i + 1) % len(ps2)
        v1 = ps2[i]
        v2 = ps2[i2]
        m1 = v1.vert.co - v2.vert.co
        if m1.length < offset * 5:
            links[i, i2] = 1
            links[i2, i] = 1
    visited = set()
    ps4 = []
    for i in range(len(ps2)):
        p1 = ps2[i]
        if p1 in visited:
            continue
        visited.add(p1)
        ps3 = [p1]
        for k in range(len(ps2)):
            if links[i, k] == 0:
                continue
            p2 = ps2[k]
            if p2 in visited:
                continue
            visited.add(p2)
            ps3.append(p2)
        vs = [p3.vert.co for p3 in ps3]
        cen = sum(vs, Vector((0, 0, 0))) / len(vs)
        vsrem = [p3.remain for p3 in ps3]
        rem = min(vsrem)
        p4 = Loop()
        p4.vert.co = cen
        p4.remain = rem
        p4.fix = False        
        # if any([p3.fix for p3 in ps3]):
        #     p4.fix = True
        ps4.append(p4)
        for pe in ps:
            if pe.next in ps3:
                pe.next = p4
    link_loops(ps4)
    # print(len(ps4))
    return ps4





def get_intersect_edge(i, ps, sn):
    mid = get_ps_mid(ps[i], sn)
    ms = []
    for k in range(len(ps)):
        k2 = (k + 1) % len(ps)
        if k == i or k2 == i:
            continue
        p1 = ps[k].vert.co
        p2 = ps[k2].vert.co
        pin = intersect2d(ps[i].vert.co, ps[i].vert.co + mid * 1000, 
                        p1, p2)
        if pin == None:
            continue
        d1 = (pin - ps[i].vert.co).length    
        ms.append((d1, k))
    if len(ms) == 0:
        return None, None
    d1, k = min(ms, key=lambda x: x[0])
    return d1, k






def check_line_hit(p1, mid1, p2, mid2, deg1, deg2):
    xA = p1.vert.co.x
    yA = p1.vert.co.y
    xB = mid1.x
    yB = mid1.y
    xC = p2.vert.co.x
    yC = p2.vert.co.y
    xD = mid2.x
    yD = mid2.y
    if xB - xD == 0:
        return None
    if yB - yD == 0:
        return None
    t1 = -(deg1*deg2*xA - deg1*deg2*xC)/(deg2*xB - deg1*xD)
    t2 = -(deg1*deg2*yA - deg1*deg2*yC)/(deg2*yB - deg1*yD)
    if t1 != t2:
        return None
    if t1 < 0 or t2 < 0:
        return None
    return t1


def get_max_bound(ps):
    vs = [p1.vert.co for p1 in ps]
    x_max = max([v1.x for v1 in vs])
    x_min = min([v1.x for v1 in vs])
    y_max = max([v1.y for v1 in vs])
    y_min = min([v1.y for v1 in vs])
    width = x_max - x_min
    height = y_max - y_min
    return max(width, height)




def check_med(ps, offset, bm, plen):  
    global mat
    sn = Vector((0,0,1))
    maxlen = get_max_bound(ps)
    mids = []
    for i in range(len(ps)):
        p1 = ps[i]
        p1.deg = math.sin(angle(p1)/2)
        mid = get_ps_mid(p1, sn)
        mids.append(mid)

    pks = []
    for i in range(len(ps)):
        p1 = ps[i]
        mid = mids[i]
        # dmin = plen / p1.deg
        if p1.deg == 0:
            dmin = maxlen
        else:
            dmin = maxlen / p1.deg
        d1 = mid * dmin
        pk = Loop()
        pk.vert.co = p1.vert.co + d1
        pks.append(pk)

    for i in range(len(pks)):
        pk = pks[i]        
        pk.vert.co.z = maxlen

    ps2 = []
    for i in range(len(ps)):        
        i2 = (i + 1) % len(ps)
        i3 = (i - 1) % len(ps)
        p1 = ps[i]
        pk = pks[i]
        ms = []
        mid1 = mids[i]
        for k in range(len(pks)):
            k2 = (k + 1) % len(pks)
            if k == i or k2 == i:
                continue
            p2 = ps[k]
            p3 = ps[k2]
            pk2 = pks[k]
            pk3 = pks[k2] 
            poly = [p2.vert.co, p3.vert.co, pk3.vert.co, pk2.vert.co]
            s1 = get_sn(poly)                     
            pin = line_poly_intersect(p1, pk, poly, s1, offset)            
            if pin != None:                                
                pin.z = 0 
                d1 = (pin - p1.vert.co).length                               
                ms.append((d1, pin, k, k2))

        sd1 = ps[i2]
        sd2 = ps[i3]
        mid2 = mids[i2]
        mid3 = mids[i3]
        pin = intersect2d(p1.vert.co, p1.vert.co + mid1 * 1000, sd1.vert.co, sd1.vert.co + mid2 * 1000)
        if pin != None:
            d1 = (pin - p1.vert.co).length
            ms.append((d1, pin, i2, None))
        pin2 = intersect2d(p1.vert.co, p1.vert.co + mid1 * 1000, sd2.vert.co, sd2.vert.co + mid3 * 1000)
        if pin2 != None:
            d1 = (pin2 - p1.vert.co).length
            ms.append((d1, pin2, i3, None))                     

        if len(ms) == 0:
            dlen = 0
            pin = p1.vert.co.copy()
        else:
            dlen, pin, k, k2 = min(ms, key=lambda x: x[0])
        # d1 = dlen * p1.deg
        if p1.deg == 0:
            d1 = 0
        else:
            d2 = plen / p1.deg
        d1 = min(dlen, d2)
        pk = Loop()
        mid = mids[i]
        off2 = max(1.0 - offset, 0)
        pk.vert.co = p1.vert.co + mid * d1 * off2
        p1.next = pk
        ps2.append(pk)     

    adds = []  
    for i in range(len(ps2)):        
        i2 = (i + 1) % len(ps2)
        p3 = ps2[i]
        p4 = ps2[i2]
        # ms = []
        for k in range(len(ps2)):
            if k == i or k == i2:
                continue
            p1 = ps[k]
            p2 = ps2[k]            
            # pin = intersect2d(p1.vert.co, p2.vert.co, p3.vert.co, p4.vert.co)
            p3b = ps[i]
            p4b = ps[i2]
            pin = is_cross_region(p1.vert.co, p2.vert.co, [p3b.vert.co, p4b.vert.co, p4.vert.co, p3.vert.co])
            if pin != None:
                d1 = (pin - p2.vert.co).length
                arrow = p2.vert.co - p1.vert.co
                pa = p1.vert.co + (arrow.length + offset) * arrow.normalized()
                adds.append((p3, pin, pa))
                # pa = p2.vert.co.copy()
                # ms.append((d1, pin, pa))
        # if len(ms) == 0:
        #     continue
        # dlen, pin, v1 = max(ms, key=lambda x: x[0])
        # adds.append((p3, pin, v1))
    
    for p3, pin, v1 in adds:
        idx = ps2.index(p3)
        pk = Loop()
        pk.vert.co = v1
        ps2.insert(idx + 1, pk)

    link_loops(ps2)    
    return ps2



def is_cross_region(p1, p2, poly):
    # for i in range(len(poly)):
    #     i2 = (i + 1) % len(poly)
    #     k1 = poly[i]
    #     k2 = poly[i2]
    #     pin = intersect2d(p1, p2, k1, k2)
    #     if pin != None:
    #         return pin
    v1 = poly[0]
    v2 = poly[1]
    pin = intersect2d(p1, p2, v1, v2)
    if pin != None:
        return pin    
    if is_inside(p1, poly):
        return p2
    if is_inside(p2, poly):
        return p2
    return None



def get_sn(poly):
    A = poly[0]
    B = poly[1]
    C = poly[2]
    AB = B - A
    AC = C - A
    n = AB.cross(AC)
    n.normalize()
    return n




def point_line_near(pin, pe1, pe2, offset):
    m1 = pe2 - pe1
    m2 = pin - pe1
    pro = m1.dot(m2) / m1.dot(m1)
    # if pro < 0 or pro > 1:
    #     return False
    pro_v = pe1 + m1 * pro
    h1 = pin - pro_v

    if h1.length < offset:
        return True
    return False



def line_poly_intersect(p1, p2, poly, normal, offset):
    cen = sum(poly, Vector()) / len(poly) 
    # cen = (poly[0] + poly[1])/2
    # cen = poly[0]   
    pin = line_plane_intersection(p1.vert.co, p2.vert.co, cen, normal)
    if pin == None:
        return None
    
    poly2 = []
    for p in poly:
        m1 = p - cen
        m2 = m1.normalized()
        p2 = cen + m2 * (m1.length + offset)
        poly2.append(p2)
    poly = poly2
    
    k1 = poly[0]
    k2 = poly[1]
    k3 = poly[2]
    k4 = poly[3]
    n1 = point_line_near(pin, k1, k4, offset)
    n2 = point_line_near(pin, k2, k3, offset)
             
    if n1 or n2 or is_point_inside_polygon(pin, poly, normal, cen): 
        return pin
    return None


def line_plane_intersection(P1, P2, P0, normal):
    num = normal.dot(P0 - P1)
    den = normal.dot(P2 - P1)
    if abs(den) < 1e-6:
        return None
    t = num / den
    intersection = P1 + t * (P2 - P1)
    if t < 0 or t > 1:
        return None
    return intersection


def is_point_inside_polygon(point, polygon, sn, cen):
    mat = get_matrix_vs(polygon, sn, cen)
    ps2 = [mat @ p for p in polygon]
    point2 = mat @ point
    # return is_point_inside_polygon_flat(point2, ps2)
    return is_inside(point2, ps2)



def is_left(p0, p1, p2):
    return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1])


def is_inside(point, polygon):
    wn = 0
    n = len(polygon)    
    for i in range(n):
        if polygon[i][1] <= point[1]:
            if polygon[(i + 1) % n][1] > point[1]:
                if is_left(polygon[i], polygon[(i + 1) % n], point) > 0:
                    wn += 1
        else:
            if polygon[(i + 1) % n][1] <= point[1]:
                if is_left(polygon[i], polygon[(i + 1) % n], point) < 0:
                    wn -= 1
    return wn > 0



def get_matrix_vs(ps, sn, cen):
    m1 = Vector()
    for i in range(len(ps)):
        p2 = ps[i]
        p3 = ps[(i + 1) % len(ps)]
        m1 = p3 - p2
        if m1.length > 0:
            break
    if m1.length == 0:
        return None
    m2 = sn.cross(m1)
    mat = get_matrix(m1, m2, sn, cen)
    return mat.inverted()



def solve_face(bm, pso, plen, offset):
    global mat
    ps = list(pso)
    ps = check_med(ps, offset, bm, plen)    
    return ps




def local_loop(bm, ps, ps2):
    global mat
    fs2 = []
    cen = get_ps_center(ps)
    if len(ps2) < 2:
        pk = Loop()
        pk.vert.co = cen
        v1 = bm.verts.new(mat @ cen)
        pk.realvert = v1
        for p1 in ps:
            p1.next = pk     
        v1.select = True
        
    elif len(ps2) == 2:       
        vs = []
        for i in range(len(ps2)):
            v1 = bm.verts.new(mat @ ps2[i].vert.co)
            ps2[i].realvert = v1
            vs.append(v1)
        e2 = bm.edges.new(vs) 
        e2.select = True

    else:
        vs = []
        for i in range(len(ps2)):
            v1 = bm.verts.new(mat @ ps2[i].vert.co)
            ps2[i].realvert = v1
            vs.append(v1)

        for i in range(len(ps2)):
            i2 = (i + 1) % len(ps2)
            # v1 = vs[i]
            # v2 = vs[i2]
            v1 = ps2[i].realvert
            v2 = ps2[i2].realvert
            bm.edges.new([v1, v2])
        f2 = bm.faces.new(vs)    
        f2.select = True
        fs2.append(f2)

    return fs2


def vertical_loop(bm, ps):
    es = []
    for i in range(len(ps)):
        v1 = ps[i].realvert
        # p2 = get_final_node(ps[i])
        p2 = ps[i].next
        v2 = p2.realvert
        if v1 == None or v2 == None:
            continue
        if v1 == v2:
            continue
        bm.edges.new([v1, v2])
        es.append((ps[i], p2))
    return es



def fan_loop(bm, f1, es, ps, ps2):
    fs2 = []
    if len(es) == 0:
        return []
    bmesh.ops.delete(bm, geom=[f1], context='FACES_ONLY')

    for i in range(len(es)):
        i2 = (i + 1) % len(es)
        e1 = es[i]
        e2 = es[i2]
        a, b = e1
        c, d = e2
        vs = get_links(a, c)
        vs2 = list(reversed(get_links(b, d)))
        vsf = [c, d] + vs2 + [b, a] + vs
        vsf2 = filter_same(vsf)
        if len(vsf2) < 3:
            continue
        vsr = [v1.realvert for v1 in vsf2]
        f2 = bm.faces.new(vsr)
        fs2.append(f2)
    return fs2





def process_face(bm, f1, plen, offset):
    global mat
    matp = get_matrix_face(f1)
    ps = create_ps(f1, matp)
    mat = matp.inverted()
    ps2 = solve_face(bm, ps, plen, offset)
    tops = local_loop(bm, ps, ps2)
    es = vertical_loop(bm, ps)
    fans = fan_loop(bm, f1, es, ps, ps2)
    return tops, fans

    
def get_connected_es(fs2):
    es = set()
    for f1 in fs2:
        for e1 in f1.edges:
            es.add(e1)
    es = list(es)
    es2 = []
    for e1 in es:
        elen = len(e1.link_loops)
        if elen != 2:
            continue   
        es2.append(e1)
    return es2 
    

def solve_fs(bm, fs, plen, merge, mergedist, offset):
    fso = set(bm.faces) - set(fs)
    nosel = set()
    for f1 in fs:
        f1.select = False
        tops, fans = process_face(bm, f1, plen, offset)
        if len(fans) > 0:
            for f2 in fans:
                nosel.add(f2)
        if merge:
            for f1 in tops:
                bmesh.ops.remove_doubles(bm, 
                        verts=f1.verts, dist=mergedist)
    bm.normal_update()
    fs2 = set(bm.faces) - fso - nosel
    for f1 in fs2:
        f1.select = True
        

def filter_fs(fss):
    fs = []
    for v1 in fss:
        if v1 not in fs:
            fs.append(v1)
    return fs


def get_loop_vert(f1, v1):
    for p1 in f1.loops:
        if p1.vert == v1:
            return p1
    return None

        
        

def forward(p1, ct):
    for i in range(ct):
        p1 = p1.link_loop_next
    return p1


def get_final_node(p1):
    pk = p1
    while True:        
        p2 = pk.next
        if p2 == None:
            return pk
        if p2 == p1:
            return pk
        pk = p2    


class SafeInsetOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.safe_inset_operator"
    bl_label = "Safe Inset"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="Inset size",
        description="Inset size",
        default=0.15,
        step=0.2,
        min=0,
    )    

    prop_ths: FloatProperty(
        name="Threshold",
        description="The threshold for checking limit",
        default=0.01,
        step=0.2,
        min=0
    )          


    prop_merge: BoolProperty(
        name="Merge Result",
        description="Merge close vertices of the result",
        default=False,
    )    



    prop_mdist: FloatProperty(
        name="Merge Distance",
        description="Merge Distance",
        default=0.04,
        step=0.2,
        min=0
    )    


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm



    def process(self, context):
        bm = self.get_bm() 
        sel = [f1 for f1 in bm.faces if f1.select]
        fs1 = sel
        solve_fs(bm, fs1, self.prop_plen, 
                 self.prop_merge, self.prop_mdist, 
                 self.prop_ths)
        bm.normal_update()

        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)  


    def execute(self, context):
        self.process(context)      
        return {'FINISHED'}    

    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == 'MESH'        
        editing = context.mode == 'EDIT_MESH' 
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return selecting and editing 


    def invoke(self, context, event): 
        self.prop_plen = 0.15 
        self.prop_ths = 0.01                    
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}


