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




def link_loops(ps):
    for i , p1 in enumerate(ps):
        p2 = ps[(i + 1) % len(ps)]
        p1.link_loop_next = p2
        p2.link_loop_prev = p1



def create_ps(f1):
    ps = []
    for p1 in f1.loops:
        p2 = Loop()
        p2.vert.co = p1.vert.co
        p2.realvert = p1.vert
        ps.append(p2)
    link_loops(ps)        
    return ps
    



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


def is_inside(p1, p2, k):
    m1 = p2 - p1
    m2 = k - p1
    m3 = k - p2
    if m2.length + m3.length > m1.length + 0.001:
        return False
    return True

        
def intersect(p1, p2, p3, p4):
    res = intersect_line_line(p1, p2, p3, p4)
    if res == None:
        return None
    a, b = res
    if a == None or b == None:
        return None
    # if (b - a).length < 0.00001:
    if is_inside(p1, p2, a) and is_inside(p3, p4, b):            
        return (b + a)/2
    else:            
        return None
    # return None


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



def get_concave_pair(ps, i, mid):
    p1 = ps[i]
    ms = []
    for k in range(len(ps)):
        k2 = (k + 1) % len(ps)
        if k == i or k2 == i:
            continue
        p3 = ps[k].vert.co
        p4 = ps[k2].vert.co
        pin = intersect(p1.vert.co, p1.vert.co + mid.normalized() * 1000, 
                        p3, p4)
        if pin == None:
            continue
        d1 = (pin - p1.vert.co).length
        ms.append((d1, k))
    if len(ms) == 0:
        return None, None
    d1, k = min(ms, key=lambda x: x[0])
    return d1, k


def get_concave_pair_reverse(ps, i, i2, sn, ps2):
    p1 = ps2[i]
    p2 = ps2[i2]
    ms = []
    for k in range(len(ps)):
        if k == i or k == i2:
            continue
        if is_concave(ps[k], sn) == False:
            continue
        pk = ps[k]
        mid = get_ps_mid(ps[k], sn)
        pin = intersect(p1.vert.co, p2.vert.co,
                        pk.vert.co - mid * 1000, pk.vert.co + mid * 1000)
        if pin == None:
            continue
        d1 = (pin - ps[k].vert.co).length
        ms.append((d1, k))
    if len(ms) == 0:
        return float('inf'), 0
    d1, k = min(ms, key=lambda x: x[0])
    return d1, k


def cross_dist(ps, ps2, sn):
    pokes = {}
    sides = {}
    for i in range(len(ps)):
        if is_concave(ps[i], sn) == False:
            # pokes[i] = (None, None)
            continue
        mid = get_ps_mid(ps[i], sn)
        dlen, k = get_concave_pair(ps, i, mid)
        if dlen == None:
            pass
        else:
            dlen2 = max(dlen/2 - 0.01, 0)
            pokes[i] = (dlen2, k)

    for i in range(len(ps)):
        i2 = (i + 1) % len(ps)
        i3 = (i - 1) % len(ps)
        dlen, k = get_concave_pair_reverse(ps, i, i2, sn, ps2)
        dlen2, k2 = get_concave_pair_reverse(ps, i, i3, sn, ps2)
        dlen3 = min(dlen, dlen2)
        if dlen3 == float('inf'):
            continue
        else:
            dlen4 = max(dlen3/2 - 0.01, 0)
            sides[i] = (dlen4, k)
        

    return pokes, sides



def merge_ps2(ps, ps2, offset):
    ps3 = []
    last = None
    for i in range(len(ps2)):
        i2 = (i - 1) % len(ps2)
        v1 = ps2[i]
        v2 = ps2[i2]
        m1 = v1.vert.co - v2.vert.co
        if m1.length < offset * 5:  
            if last != None:
                for pk in ps:
                    if pk.next == v1:
                        pk.next = last
                continue
        ps3.append(v1)
        last = v1
    link_loops(ps3)
    return ps3



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


def min_edge_dist(k, ps, pk, offset):
    ms = []
    for i in range(len(ps)):
        i2 = (i + 1) % len(ps)
        if i == k or i2 == k:
            continue
        p1 = ps[i].vert.co
        p2 = ps[i2].vert.co
        d1 = edge_dist(p1, p2, pk.vert.co)
        ms.append((d1, i))
    if len(ms) == 0:
        return None, None
    d1, i = min(ms, key=lambda x: x[0])
    d2 = d1 / 2 - offset
    d2 = max(d2, 0)
    return d2, i


def min_edge_dist_rev(k, ps, pk, offset):
    k2 = (k + 1) % len(ps)
    k3 = (k - 1) % len(ps)
    pk2 = ps[k2]
    pk3 = ps[k3]
    ms = []
    for i in range(len(ps)):
        if i == k or i == k2 or i == k3:
            continue
        p1 = ps[i].vert.co
        d1 = edge_dist(pk.vert.co, pk2.vert.co, p1)
        d2 = edge_dist(pk.vert.co, pk3.vert.co, p1)
        d1 = min(d1, d2)
        ms.append((d1, i))
    if len(ms) == 0:
        return None, None
    d1, i = min(ms, key=lambda x: x[0])
    d2 = d1 / 2 - offset
    d2 = max(d2, 0)
    return d2, i


def get_ps_mid_complex(p1, sn, mlen1, mlen2):
    p2 = p1.link_loop_next
    p3 = p1.link_loop_prev
    m1 = (p2.vert.co - p1.vert.co).normalized()
    m2 = (p3.vert.co - p1.vert.co).normalized()
    mv1 = m1.cross(sn) * -1
    mv2 = m2.cross(sn)
    mv1 = mv1.normalized() * mlen1
    mv2 = mv2.normalized() * mlen2
    pro = mv1.project(mv2)
    h1 = mv1 - pro
    return (h1 + mv2).normalized()



def min_edge_dist_rev_simple(ps, k, k2, offset):
    pk = ps[k]
    pk2 = ps[k2]
    ms = []
    for i in range(len(ps)):
        if i == k or i == k2:
            continue
        p1 = ps[i].vert.co
        d1 = edge_dist(pk.vert.co, pk2.vert.co, p1)
        # d1 = min(d1, d2)
        ms.append((d1, i))
    d1, i = min(ms, key=lambda x: x[0])
    d2 = d1 / 2 - offset
    d2 = max(d2, 0)
    return d2, i



# def check_walk(ps, sn, offset):
#     ps2 = []
#     for i in range(len(ps)):
#         mlen = ps[i].remain
#         p1 = ps[i]
#         d1, _ = min_edge_dist(i, ps, p1, offset)
#         d2, _ = min_edge_dist_rev(i, ps, p1, offset)
#         d1 = min(d1, d2)
#         deg = angle(p1)
#         if deg == 0:
#             dd = 0
#         else:
#             real = mlen / math.sin(deg / 2)
#             dd = min(d1, real)
#         dd = max(dd, 0)
#         pk = Loop()
#         mid = get_ps_mid(p1, sn)
#         pk.vert.co = p1.vert.co + mid * dd
#         pk.remain = p1.remain - dd
#         pk.remain = max(pk.remain, 0)
#         ps[i].next = pk
#         ps2.append(pk)
#     link_loops(ps2)
#     return ps2
        


def min_value(d1, d2):
    if d1 == None and d2 == None:
        return None
    if d1 == None:
        return d2
    elif d2 == None:
        return d1
    return min(d1, d2)


def check_walk(ps, sn, offset):
    ms = []
    for i in range(len(ps)):
        mlen = ps[i].remain
        p1 = ps[i]
        d1, _ = min_edge_dist(i, ps, p1, offset)
        d2, _ = min_edge_dist_rev(i, ps, p1, offset)
        d1 = min_value(d1, d2)
        if d1 == None:
            continue
        deg = angle(p1)
        if deg == 0:
            continue
        else:
            real = mlen / math.sin(deg / 2)
            dd = min(d1, real)
        dd = max(dd, 0)
        if p1.fix == False:
            ms.append(dd)
    if len(ms) == 0:
        dd = 0
    else:
        dd = min(ms)
    ps2 = []
    for i in range(len(ps)):
        p1 = ps[i]
        pk = Loop()
        mid = get_ps_mid(p1, sn)
        if p1.fix:
            dmin2 = 0
        else:
            dmin2 = dd
        pk.vert.co = p1.vert.co + mid * dmin2
        cost = dmin2 * math.sin(angle(p1)/2)
        pk.remain = p1.remain - cost
        pk.remain = max(pk.remain, 0)
        pk.fix = p1.fix
        ps[i].next = pk
        ps2.append(pk)
    link_loops(ps2)
    # print(dd, len(ms))
    return ps2, dd



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
        if any([p3.fix for p3 in ps3]):
            p4.fix = True
        ps4.append(p4)
        for pe in ps:
            if pe.next in ps3:
                pe.next = p4
    link_loops(ps4)
    # print(len(ps4))
    return ps4
            


def solve_face(bm, pso, sn, plen, agg, offset):
    ps = list(pso)
    mlen = plen
    cen = get_ps_center(ps)
    for p in ps:
        p.remain = mlen
    # offset = 0.01
    for step in range(100):
        ps2, dmin = check_walk(ps, sn, offset)
        # pcon = False
        # for p in ps2:
        #     if p.remain > offset:
        #         pcon = True
        #         break
        if agg:
            ps2 = merge_ps(ps, ps2, offset)
            if len(ps2) == 0:
                ps = ps2
                break
            cen = get_ps_center(ps2)
        check_skip(ps2, offset)
        ps = ps2
        if len(ps) < 2:
            break
        # if pcon == False:
        #     break
        if dmin < offset:
            break
    return ps, cen


def check_skip(ps2, offset):
    for i in range(len(ps2)):
        p1 = ps2[i]
        d1, _ = min_edge_dist(i, ps2, p1, offset)
        d2, _ = min_edge_dist_rev(i, ps2, p1, offset)
        d2 = min_value(d1, d2)
        if d2 == None:
            continue
        if d2 <= offset:
            p1.fix = True
    



def local_loop(bm, ps, ps2, cen):
    fs2 = []
    if len(ps2) < 2:
        pk = Loop()
        pk.vert.co = cen
        v1 = bm.verts.new(cen)
        pk.realvert = v1
        for p1 in ps:
            p1.next = pk     
        v1.select = True
        
    elif len(ps2) == 2:       
        vs = []
        for i in range(len(ps2)):
            v1 = bm.verts.new(ps2[i].vert.co)
            ps2[i].realvert = v1
            vs.append(v1)
        e2 = bm.edges.new(vs) 
        e2.select = True

    elif len(ps2) == 3:       
        vs = []
        for i in range(len(ps2)):
            v1 = bm.verts.new(ps2[i].vert.co)
            ps2[i].realvert = v1
            vs.append(v1)
        f2 = bm.faces.new(vs) 
        f2.select = True
        fs2.append(f2)
    else:
        vs = []
        for i in range(len(ps2)):
            v1 = bm.verts.new(ps2[i].vert.co)
            ps2[i].realvert = v1
            vs.append(v1)

        for i in range(len(ps2)):
            i2 = (i + 1) % len(ps2)
            v1 = vs[i]
            v2 = vs[i2]
            bm.edges.new([v1, v2])
        f2 = bm.faces.new(vs)    
        f2.select = True
        fs2.append(f2)

    # for p1 in ps2:
    #     if p1.fix:
    #         p1.realvert.select = True

        # for p1 in ps:
        #     print(p1.next)
    return fs2


def vertical_loop(bm, ps):
    es = []
    for i in range(len(ps)):
        v1 = ps[i].realvert
        p2 = get_final_node(ps[i])
        v2 = p2.realvert
        if v1 == None or v2 == None:
            continue
        if v1 == v2:
            continue
        bm.edges.new([v1, v2])
        es.append((ps[i], p2))
    return es


def fan_loop(bm, f1, es):
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
        vsf = vs + [a, c] + vs2 + [d, b]
        vsf2 = filter_same(vsf)
        if len(vsf2) < 3:
            continue
        vsr = [v1.realvert for v1 in vsf2]
        f2 = bm.faces.new(vsr)
        fs2.append(f2)
    return fs2
    


def process_face(bm, f1, plen, agg, offset):
    ps = create_ps(f1)
    ps2, cen = solve_face(bm, ps, f1.normal, plen, agg, offset)
    tops = local_loop(bm, ps, ps2, cen)
    es = vertical_loop(bm, ps)
    fans = fan_loop(bm, f1, es)
    return tops

    
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
    

def solve_fs(bm, fs, plen, merge, mergedist, agg, offset):
    for f1 in fs:
        f1.select = False
        tops = process_face(bm, f1, plen, agg, offset)
        if merge:
            for f1 in tops:
                bmesh.ops.remove_doubles(bm, 
                        verts=f1.verts, dist=mergedist)
        

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
        min=0
    )    

    prop_ths: FloatProperty(
        name="Threshold",
        description="The threshold for checking limit",
        default=0.01,
        step=0.2,
        min=0
    )        

    prop_agg: BoolProperty(
        name="Aggressive mode",
        description="Continue the inset more aggressively (may overlap)",
        default=True,
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
                 self.prop_agg, self.prop_ths)
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
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}


