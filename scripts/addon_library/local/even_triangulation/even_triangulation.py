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

# from mathutils.geometry import area_tri
import random


from pprint import pprint
# from . import gui

# import itertools
# import numpy as np



class EvenTriangulationOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.even_triangulation_operator"
    bl_label = "Even Triangulation"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="Expand size",
        description="Expand size",
        default=0.5,
        step=0.1,
        min=0.05
    )    
 

    prop_boundary: FloatProperty(
        name="Boundary",
        description="Boundary",
        default=0.99,
        step=0.1,
        min=0,
        max=0.999
    )    

    prop_random: FloatProperty(
        name="Randomness",
        description="Randomness",
        default=0,
        step=0.1,
        max=0.2

    )        





    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm



    def smooth(self, bm, fs, plen):
        # tol = 0.99
        tol = self.prop_boundary
        areas = {}
        cens = {}
        for f1 in fs:
            a1 = f1.calc_area()
            areas[f1] = math.sqrt(a1)
            c1 = f1.calc_center_median()
            cens[f1] = c1
        vs = set()
        for f1 in fs:
            for v1 in f1.verts:
                vs.add(v1)
        for f1 in fs:
            for e1 in f1.edges:
                if e1.is_boundary:
                    a, b = e1.verts
                    if a in vs:
                        vs.remove(a)
                    if b in vs:
                        vs.remove(b)
        vs = list(vs)        
        vmap = [None] * len(vs)
        for k, v1 in enumerate(vs):
            vn = v1.normal
            ms = []
            area = []
            skip = False
            for f2 in v1.link_faces:
                pro = vn.dot(f2.normal)
                if pro < tol:
                    skip = True
                    break
                a1 = areas[f2]
                area.append(a1)
                c1 = cens[f2] * a1
                ms.append(c1)
            if len(ms) == 0 or skip:
                vmap[k] = v1.co
                continue
            v2 = sum(ms, Vector()) / sum(area)
            vmap[k] = v2
        for k, v1 in enumerate(vs):                
            v1.co = vmap[k]                    


    def random_dissolve(self, bm, fs, plen):       
        ra = self.prop_random
        fs2 = set(bm.faces) - set(fs)
        es = set()
        d1 = math.radians(1)
        for f1 in fs:
            for e1 in f1.edges:
                if len(e1.link_faces) != 2:
                    continue
                if e1.is_boundary:
                    continue
                if e1.calc_face_angle() > d1:
                    continue
                if random.random() < ra:
                    es.add(e1)
        es = list(es)
        # dissolve edges
        bmesh.ops.dissolve_edges(bm, edges=es, use_verts=False, use_face_split=False)
        fs = set(bm.faces) - fs2
        return list(fs)
        


    def solve_face(self, bm, sel, plen):
        random.seed(0)
        fs = sel
        # for i in range(100):
        count = 0
        while True:
            count += 1
            if self.prop_random > 0:
                if count < 50:
                    fs = self.random_dissolve(bm, fs, plen)
            res = bmesh.ops.triangulate(bm, faces=fs)
            fs = res['faces']                   
            self.smooth(bm, fs, plen) 
            es = set()
            for f1 in fs:
                for e1 in f1.edges:
                    es.add(e1)

            es = list(es)
            es2 = []
            for e1 in es:
                elen = e1.calc_length()
                if elen > plen:
                    es2.append(e1)
            if len(es2) > 0:
                # bisect
                bmesh.ops.bisect_edges(bm, edges=es2, cuts=1)
            else:
                self.smooth(bm, fs, plen)
                break
                



    def process(self, context):
        bm = self.get_bm() 
        sel = [f1 for f1 in bm.faces if f1.select]
        plen = self.prop_plen

        self.solve_face(bm, sel, plen)

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

