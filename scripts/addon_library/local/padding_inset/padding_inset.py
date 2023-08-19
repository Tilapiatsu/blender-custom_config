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

from pprint import pprint

import itertools
import numpy as np

from mathutils.geometry import intersect_line_line

import random



class Vert:
    def __init__(self) -> None:
        self.co = None


class Loop:
    base = 0
    def __init__(self) -> None:
        self.vert = Vert()
        self.link_loop_next = None
        self.link_loop_prev = None
        # self.deg = None
        self.next = None
        self.realvert = None
        self.index = Loop.base
        Loop.base += 1
        # self.remain = 0

    def link(self, p2):
        self.link_loop_next = p2
        p2.link_loop_prev = self



def link_loops(ps):
    for i , p1 in enumerate(ps):
        p2 = ps[(i + 1) % len(ps)]
        p1.link_loop_next = p2
        p2.link_loop_prev = p1



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


def create_ps(f1):
    ps = []
    mat = get_matrix_face(f1)
    if mat == None:
        return None, None
    for p1 in f1.loops:
        p2 = Loop()
        p2.vert.co = mat @ p1.vert.co
        p2.realvert = p1.vert
        ps.append(p2)
    link_loops(ps)        
    return ps, mat
    


def intersect2d(p1, p2, p3, p4):
    res = mathutils.geometry.intersect_line_line_2d(p1.xy, p2.xy, p3.xy, p4.xy)
    if res != None:
        return Vector((res[0], res[1], 0))
    return None


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
    if c1.dot(sn) <= 0:
        return True
    return False


def turn(p1, sn):
    p2 = p1.link_loop_next
    m1 = (p2.vert.co - p1.vert.co).normalized()
    c1 = m1.cross(sn) * -1
    return c1.normalized()



def merge_ps(ps):    
    while True:
        ps2 = []
        change = False
        for i in range(len(ps)):
            i2 = (i + 1) % len(ps)
            p1 = ps[i]
            p2 = ps[i2]
            m1 = p2.vert.co - p1.vert.co
            if m1.length < 0.001:
                change = True
                continue
            ps2.append(p1)
        ps = ps2
        if not change:
            break
    link_loops(ps)
    return ps


def print_ps(ps):
    for p1 in ps:
        print(p1.index, p1.vert.co, p1.link_loop_next.index)
    print()


def line_edge(bm, a, b):
    v1 = bm.verts.new(a.copy())
    v2 = bm.verts.new(b.copy())
    e1 = bm.edges.new((v1, v2))
    e1.select = True


mat = None


def solve(bm, f1, plen, flat, align, connect):
    random.seed(0)
    ps, matp = create_ps(f1)
    if ps == None:
        return
    global mat
    mat = matp.inverted()
    # sn = f1.normal
    sn = Vector((0, 0, 1))
    # ps = merge_ps(ps)
    bs = []
    for i in range(len(ps)):
        i2 = (i + 1) % len(ps)
        p1 = ps[i]
        p2 = ps[i2]

        con1 = is_concave(p1, sn)
        con2 = is_concave(p2, sn)

        if con1 == False:
            pk0 = Loop()
            pk0.vert.co = p1.vert.co.copy()
            pk0.next = p1
            bs.append(pk0)
        else:
            if flat:
                mid1 = get_ps_mid(p1, sn) * plen
                pk0 = Loop()
                pk0.vert.co = p1.vert.co + mid1
                pk0.next = p1
                bs.append(pk0)                

        if con1:
            if flat == False:
                d1 = plen / math.sin(angle(p1)/2)
                mid1 = get_ps_mid(p1, sn) * d1
            else:
                mid1 = turn(p1, sn) * plen  
        else:
            mid1 = turn(p1, sn) * plen           
        pk1 = Loop()
        pk1.vert.co = p1.vert.co + mid1
        pk1.next = p1

        if con2:
            if flat == False:
                d1 = plen / math.sin(angle(p2)/2)
                mid1 = get_ps_mid(p2, sn) * d1
            else:
                mid1 = turn(p1, sn) * plen
        else:
            mid1 = turn(p1, sn) * plen
        pk2 = Loop()
        pk2.vert.co = p2.vert.co + mid1
        pk2.next = p2
        bs.append(pk1)
        bs.append(pk2)        

    link_loops(bs)    
    maxv = Vector((0,1,0)) 
    rotate = Quaternion((0, 0, 1), align * 3)
    maxv = rotate @ maxv
    maxv.normalize()

    bss = divide_all(bs)

    tops = []
    bss2 = []

    for b1 in bss:        
        cen = find_cen_point(b1, sn, maxv)           
        if solve_bound(bss, b1, sn, maxv, cen):  
            b1 = merge_ps(b1)
            if len(b1) < 3:
                continue            

            f2 = make_face(bm, b1)
            f2.select = True
            tops.append(f2)
            bss2.append(b1)
        # else:
        #     f2 = make_face(bm, b1)
            # draw_poly(bs)
    # draw_poly(bss[0])    
    f1.select = False

    if len(tops) == 0:
        return

    if connect:
        es1 = set([p1.edge for p1 in f1.loops])
        for f3 in tops:
            for e1 in f3.edges:
                es1.add(e1)

        vpair = []
        for b1 in bss2:
            es, vp = vertical_loop(bm, b1)
            es1 = es1 | es
            vpair += vp
        f1.select = False                  
        sn_real = f1.normal
        bmesh.ops.delete(bm, geom=[f1], context='FACES_ONLY')
        fill_holes(bm, vpair, ps, es1, sn_real)
    bm.normal_update()



def get_full_angle(m1, m2, sn):
    if m1.length == 0 or m2.length == 0:
        return None
    d1 = m1.angle(m2)
    if m1.cross(m2).dot(sn) < 0:
        d1 = math.pi * 2 - d1
    return d1


def get_cw_next(v1, v2, es1, sn):
    ms = []
    m1 = v1.co - v2.co
    for e1 in v2.link_edges:
        if e1 not in es1:        
            continue
        vk = e1.other_vert(v2)        
        if vk == v1:
            continue
        m2 = vk.co - v2.co        
        d1 = get_full_angle(m2, m1, sn)    
        if d1 == None:
            continue
        ms.append((d1, vk))
    if len(ms) == 0:
        return None
    d1, vk = min(ms, key=lambda x: x[0])    
    return vk


def get_open_loop(v1, v2, es1, sn):
    vs = [v1, v2]
    while True:        
        v3 = get_cw_next(v1, v2, es1, sn)
        if v3 == None:
            break
        if v3 in vs:
            break
        vs.append(v3)
        v1, v2 = v2, v3
    return vs



def fill_holes(bm, vpair, ps, es1, sn):    
    vss = []

    for a, b in vpair:
        # if p1 in used or p2 in used:
        #     continue
        vs = get_open_loop(b, a, es1, sn)
        if len(vs) < 3:
            continue
        vss.append(vs)

    # for i in range(len(ps)):
    #     i2 = (i + 1) % len(ps)
    #     p1 = ps[i].realvert
    #     p2 = ps[i2].realvert
    #     # if p1 in used or p2 in used:
    #     #     continue
    #     vs = get_open_loop(p1, p2, es1, sn)
    #     if len(vs) < 3:
    #         continue
    #     vss.append(vs)

    for vs in vss:
        try:
            f2 = bm.faces.new(vs)
        except:
            continue


def get_final_node(p1):
    pk = p1
    while True:        
        p2 = pk.next
        if p2 == None:
            return pk
        if p2 == p1:
            return pk
        pk = p2    



def vertical_loop(bm, ps):
    es = []
    vpair = []
    for i in range(len(ps)):
        p2 = ps[i]
        v2 = p2.realvert
        p1 = p2.next
        if p1 == None:
            continue
        v1 = p1.realvert
        if v1 == None or v2 == None:
            continue
        if v1 == v2:
            continue
        e1 = bm.edges.new([v1, v2])
        es.append(e1)
        vpair.append((v1, v2))
    return set(es), vpair


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



def is_concave(p1, sn):
    p2 = p1.link_loop_next
    p3 = p1.link_loop_prev
    m1 = p2.vert.co - p1.vert.co
    m2 = p3.vert.co - p1.vert.co
    c1 = m1.cross(m2)
    if c1.dot(sn) < 0:
        return True
    return False



def find_cen_point(ps, sn, maxv):
    vs = [p1.vert.co for p1 in ps]
    cen = sum(vs, Vector()) / len(vs)
    pk = maxv
    ins = []
    for p1 in ps:
        p2 = p1.link_loop_next
        pin = intersect2d(cen, cen + pk * 1000, p1.vert.co, p2.vert.co)
        if pin != None:
            ins.append(pin)
    ct = len(ins)
    if ct % 2 == 1:
        return cen
    else:
        if ct >= 2:
            return (ins[0] + ins[1]) / 2
    return cen
   


def get_ps_center(ps):
    vs = [p1.vert.co for p1 in ps]
    cen = sum(vs, Vector()) / len(vs)       
    return cen


def solve_bound(bss, bs, sn, mk, cen):
    count = 0
    global mat
    for b1 in bss:
        for i in range(len(b1)):
            i2 = (i + 1) % len(b1)
            p1 = b1[i]
            p2 = b1[i2]
            pin = intersect2d(cen, cen + mk * 1000, p1.vert.co, p2.vert.co)
            if pin == None:
                continue
            m1 = p1.vert.co - cen
            c1 = m1.cross(mk).normalized()
            if c1.dot(sn) > 0:
                count += 1
            else:
                count -= 1
    return count > 0


def make_face(bm, bs):
    global mat
    vs = []
    for p1 in bs:
        v1 = bm.verts.new(mat @ p1.vert.co)
        vs.append(v1)
        p1.realvert = v1
    f1 = bm.faces.new(vs)
    return f1


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

    
def is_ccw(ps):
    ccw = 0
    for i in range(len(ps)):
        i2 = (i + 1) % len(ps)
        v1 = ps[i].vert.co
        v2 = ps[i2].vert.co
        x1, y1 = v1.x, v1.y
        x2, y2 = v2.x, v2.y
        a = x1 * y2 - x2 * y1
        ccw += a
    return ccw > 0

        

def draw_poly(bs):
    global mat
    for i in range(len(bs)):
        i2 = (i + 1) % len(bs)
        p1 = bs[i]
        p2 = bs[i2]



def find_inter(bs, p1, p2):
    for p3 in bs:
        p4 = p3.link_loop_next
        if p1.vert == p3.vert \
            or p1.vert == p4.vert \
                or p2.vert == p3.vert \
                    or p2.vert == p4.vert:
            continue
        pin = intersect2d(p1.vert.co, p2.vert.co, p3.vert.co, p4.vert.co)
        if pin != None:
            m1 = pin - p1.vert.co
            m2 = pin - p2.vert.co
            m3 = pin - p3.vert.co
            m4 = pin - p4.vert.co
            ths = 0.00001
            if m1.length <= ths or m2.length <= ths or \
                m3.length <= ths or m4.length <= ths:
                continue

            return pin, p3, p4
    return None, None, None



def tri_area(ps):
    if len(ps) != 3:
        return 0
    p1, p2, p3 = ps
    m1 = p2.vert.co - p1.vert.co
    m2 = p3.vert.co - p1.vert.co
    return m1.cross(m2).length / 2



def divide_all(bs1):
    bs = list(bs1)
    pps = []
    global mat
    # pks = []
    i = 0
    while len(bs) > 0:
        if len(bs) == 0:
            break
        p1 = bs.pop()
        p2 = p1.link_loop_next
        pin, p3, p4 = find_inter(bs, p1, p2)
        if pin == None:
            pps.append(p1)
            continue
        v1 = Vert()
        v1.co = pin
        pk1 = Loop()
        pk1.vert = v1
        pk1.next = p2.next
        p1.link(pk1)
        pk1.link(p4)
        pk2 = Loop()
        pk2.vert = v1
        pk2.next = p4.next
        p3.link(pk2)
        pk2.link(p2)
        bs.append(pk1)
        bs.append(pk2)
        bs.append(p1)
    pps = set(pps)
    poly = []
    while len(pps) > 0:
        p1 = pps.pop()
        ps1, res = get_loop(p1)
        pps = pps - set(ps1)
        if res:
            poly.append(ps1)
    return poly


def get_loop(p1):
    pk = p1
    ps = []
    while True:
        ps.append(pk)
        pk = pk.link_loop_next
        if pk == None:
            return ps, False
        if pk == p1:
            break
    return ps, True


def get_loops(p1, p2):
    pk = p1
    ps = [pk]
    while True:        
        pk = pk.link_loop_next
        ps.append(pk)
        if pk == p2 or pk == p1:
            break        
    return ps


def split_poly(bs, i, i2, j, j2, pin):    
    v1 = Vert()
    v1.co = pin
    pk = Loop()
    pk.vert = v1
    pk2 = Loop()
    pk2.vert = v1
    ps1 = get_loops(bs[i2], bs[j]) + [pk]
    ps2 = get_loops(bs[j2], bs[i]) + [pk2]
    link_loops(ps1)
    link_loops(ps2)
    return [ps1, ps2]





class PaddingInsetOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.padding_inset_operator"
    bl_label = "Padding Inset"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="Inset size",
        description="Inset size",
        default=0.2,
        step=0.2,
        min=0.0001
    )    

    prop_align: FloatProperty(
        name="Alignment",
        description="The alignment of the inset algorithm's checking",
        default=0,
        step=1,
    )        


    prop_flat: BoolProperty(
        name="Flat Concave",
        description="Flat Concave",
        default=False,
    )            


    prop_connect: BoolProperty(
        name="Connected",
        description="Connect the inset face with the original edges",
        default=True,
    )            



    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def process(self, context):
        bm = self.get_bm() 
        sel = [f1 for f1 in bm.faces if f1.select]

        for f1 in sel:
            solve(bm, f1, self.prop_plen, self.prop_flat, self.prop_align, self.prop_connect)

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
        self.operation_mode = 'None'                        
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}



