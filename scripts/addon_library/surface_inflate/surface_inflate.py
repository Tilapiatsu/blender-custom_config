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
# import numpy as np





class SurfaceInflateOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.surface_inflate_operator"
    bl_label = "Surface Inflate"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"

    # add property of enum, two choices
    mode: EnumProperty(
        name="Mode",
        description="Mode",
        items=(
            ("1", "Inflation", ""),
            ("2", "Bezier Curve", ""),
        ),
        default="1",
    )


    prop_plen: FloatProperty(
        name="Inflation ratio",
        description="Inflation ratio",
        default=1.0,
        step=0.1,
    )    


    prop_angle: FloatProperty(
        name="Limit angle",
        description="Angle for limiting the bend",
        default=60,
    )         


    prop_threshold: FloatProperty(
        name="Threshold",
        description="Threadhold for checking the bend area",
        default=0.0001,
    )         




    prop_area: FloatProperty(
        name="Area",
        description="The area",
        default=0.7,
        min=0,
        step=0.1,
    )       


    prop_curve: FloatVectorProperty(
        name="Curve",
        description="Curve",
        default=(0,0.339,0.617,0.635),
        size=4,
        step=0.1,
    )





    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mode", expand=True)

        layout.separator()
        layout.prop(self, "prop_plen")
        col = layout.column()
        col.prop(self, "prop_angle")
        col.prop(self, "prop_threshold")
        
        col2 = layout.column()
        col2.prop(self, "prop_area")
        col2.prop(self, "prop_curve")

        if self.mode == "1":
            col2.enabled = False
        else:
            col.enabled = False



    def expand_faces_two(self, bm, sel):
        plen = abs(self.prop_plen)
        if len(sel) < 2:
            return
        f1, f2 = sel[:2]
        sn = Vector()
        for fx in sel:
            sn = sn + fx.normal
        sn = sn.normalized()
        if sn.length == 0:
            return

        if self.prop_plen < 0:
            sn = sn * -1

        # ms = []
        # for v1 in f1.verts:
        #     for v2 in f2.verts:
        #         m1 = v1.co - v2.co
        #         ms.append((m1.length, v1.co, v2.co))
        # _, c1, c2 = min(ms, key=lambda x: x[0])
        # fcen = c1
        # align_m = c2 - c1
        # if self.prop_all:
        #     sel2 = bm.faces
        # else:
        #     sel2 = self.find_faces(bm, sel)

        fcen = f2.calc_center_median()
        align_m = f1.calc_center_median() - fcen

        sel2 = self.find_faces(bm, sel)
        vs = set()
        ms = []
        for fx in sel2:
            for v1 in fx.verts:
                vs.add(v1)

        # ms = []
        # for v1 in vs:
        #     m1 = v1.co - fcen
        #     m2 = m1.project(align_m)
        #     pm = m2.length
        #     if m2.dot(align_m) < 0:
        #         pm = pm * -1
        #     ms.append(pm)
        # align_min = min(ms)
        # mlen = max(ms) - align_min
        # cen = fcen + align_m.normalized() * (align_min + mlen/2)

        ms = []
        for f3 in sel:
            for v1 in f3.verts:
                m1 = v1.co - fcen
                m2 = m1.project(align_m)
                pm = m2.length
                if m2.dot(align_m) < 0:
                    pm = pm * -1
                ms.append((pm, v1))

        align_min, p1 = min(ms, key=lambda x: x[0])
        align_max, p2 = max(ms, key=lambda x: x[0])
        mlen = align_max - align_min
        mlen2 = mlen/2
        cen = fcen + align_m.normalized() * (align_min + mlen/2)                
        # mlen2 = mlen / 2        

        m1 = mlen2 * sn
        c1 = align_m.cross(sn)

        ths = self.prop_threshold

        for v1 in vs:
            m2 = v1.co - cen
            m2 = m2.project(align_m)

            # limit area            
            if m2.length >= mlen2 + ths:
                continue

            dis = m2.length / mlen2
            if m2.dot(align_m) < 0:
                dis = dis * -1
            d2 = math.pi/2 * dis * -1
            m4 = m1.copy()            
            m4.rotate(Quaternion(c1, d2))

            k1 = cen + m4
            km = k1 - v1.co
            p1 = km.project(align_m)
            p2 = km.project(m1)
            v1.co = v1.co + p1 * plen + p2 * plen
        bm.normal_update()

            

    def find_faces(self, bm, sel):        
        d1 = math.radians(self.prop_angle)
        fs = set()
        for f1 in sel:
            fs2 = [f1]
            for f2 in fs2:
                for e1 in f2.edges:            
                    f3 = self.get_other_face(e1, f2)
                    if f3 is None:
                        continue
                    if f3.normal.angle(f1.normal) <= d1:
                        if f3 not in fs2:
                            fs2.append(f3)
                        fs.add(f3)
        return fs
    

    def get_other_face(self, e1, f1):
        for f2 in e1.link_faces:
            if f2 != f1:
                return f2
        return None





    def expand_simple(self, bm):        
        cs = []
        sel = [f1 for f1 in bm.faces if f1.select]        
        vs1 = set()

        if len(sel) == 0:
            sel = [e1 for e1 in bm.edges if e1.select]
            for e1 in sel:
                vs1.add(e1.verts[0])
                vs1.add(e1.verts[1])
                
                for v1 in e1.verts:
                    s1 = []
                    for f2 in v1.link_faces:
                        if any([e2.select for e2 in f2.edges]):
                            s1.append(f2.normal)
                    if len(s1) > 0:
                        cs.append((v1.co, sum(s1, Vector())/len(s1)))
        else:            
            for f1 in sel:
                for v1 in f1.verts:
                    vs1.add(v1)
                    s1 = []
                    for f2 in v1.link_faces:
                        if f2.select:
                            s1.append(f2.normal)
                    if len(s1) > 0:
                        cs.append((v1.co, sum(s1, Vector())/len(s1)))                    

        # d1 = math.radians(self.prop_keep_angle)
        vmap = {}        
        area = self.prop_area

        vsall = []
        for v1 in bm.verts:
            if v1 in vs1:
                vsall.append(v1)
                continue
            for v2 in vs1:
                m1 = v1.co - v2.co
                if m1.length < area:
                    vsall.append(v1)
        
        for v1 in vsall:
            ms = []
            for v2, sn in cs:                                
                # if self.prop_keep_edge and sn.angle(v1.normal) > d1:
                #     continue
                mk = (v1.co - v2).length                
                if mk < area:
                    ms.append((mk, sn, v2))
            if len(ms) == 0:
                continue
            # ms = sorted(ms, key=lambda x: x[0])
            mk, sn, v2 = min(ms, key=lambda x: x[0])
            # mk2 = math.sqrt(area * area - mk * mk)
            mk2 = self.interpolate_bezier(mk/area) * area

            k1 = sn * mk2 * self.prop_plen
            vmap[v1] = k1

        for v1 in vmap:
            p1 = vmap[v1]
            v1.co = v1.co + p1

        bm.normal_update()

        # for i in range(5):
        #     self.smooth(bm, vmap)

    def interpolate_bezier(self, t):
        c1 = self.prop_curve
        p0 = c1[3]
        p1 = c1[2]
        p2 = c1[1]
        p3 = c1[0]
        val =  (1-t)**3 * p0 + 3*t*(1-t)**2 * p1 + 3*t**2*(1-t) * p2 + t**3 * p3
        return val



    def divide_sets(self, sel):
        fsset = []
        fs1 = list(sel)
        while len(fs1) > 0:
            f1 = fs1.pop()
            fs2 = [f1]
            for f2 in fs2:
                for e1 in f2.edges:
                    f3 = self.get_other_face(e1, f2)
                    if f3.select == False:
                        continue
                    if f3 not in fs2 and f3 in fs1:
                        fs2.append(f3)
                        fs1.remove(f3)
            fsset.append(fs2)
        return fsset



    def process(self, context):
        bm = self.get_bm()
        sel= [f1 for f1 in bm.faces if f1.select] 

        # if len(sel) == 0:
        #     self.mode = 2
        # else:
        #     fsset = self.divide_sets(sel)
        #     if len(fsset) > 1:
        #         if len(fsset) == 2 and len(sel) == 2:
        #             self.mode = 1
        #         else:
        #             self.mode = 2                
        #     else:          
        #         self.mode = 2            

        if self.mode == "1":
            self.expand_faces_two(bm, sel)
        elif self.mode == "2":
            self.expand_simple(bm)

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
        # self.mode = 1                     
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}


