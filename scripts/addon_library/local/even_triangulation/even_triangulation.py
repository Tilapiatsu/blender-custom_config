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


import importlib

def is_package_installed(package_name):
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


class EvenTriangulationOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.even_triangulation_operator"
    bl_label = "Even Triangulation"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="Size",
        description="Size",
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

    prop_random: BoolProperty(
        name="Randomize (slower)",
        description="Randomize",
        default=False,

    )        


    prop_seed: IntProperty(
        name="Random Seed",
        description="Random Seed",
        default=0,        
    )    


    prop_use_scipy: BoolProperty(
        name="Use Scipy",
        description="Use Scipy",
        default=False,

    )        



    prop_plen2: FloatProperty(
        name="Size",
        description="Size",
        default=0.1,
        step=0.01,
        min=0.001
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
        ra = 0.15
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
                if e1.select:
                    continue
                if random.random() < ra:
                    es.add(e1)
        es = list(es)
        # dissolve edges
        bmesh.ops.dissolve_edges(bm, edges=es, use_verts=False, use_face_split=False)
        fs = set(bm.faces) - fs2
        return list(fs)
    

        


    def solve_face(self, bm, sel, plen):
        random.seed(self.prop_seed)
        fs = sel
        # for i in range(100):
        count = 0
        while True:
            count += 1
            if self.prop_random:
                if count < 100:
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
        if self.prop_use_scipy:
            self.process_scipy(context)
            return
        
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
        

    def draw(self, context):
        installed_scipy = is_package_installed('scipy')
        layout = self.layout

        col2 = layout.column(align=True)          
        col2.prop(self, 'prop_plen')
        col2.prop(self, 'prop_boundary')
        col2.prop(self, 'prop_random')
        col2.prop(self, 'prop_seed')  
        # separator
        col2.separator() 
        col2.separator()                

        col3 = layout.column(align=True)  

        col3.operator("piptool.install_scipy_operator", text="Install Scipy library")

        col3.prop(self, 'prop_use_scipy')
        col3.separator()  
        col3.separator()  
        
        col = layout.column(align=True)          
        col.label(text='Use scipy')
        col.prop(self, 'prop_plen2')   

        if self.prop_use_scipy and installed_scipy:
            col.enabled = True
            col2.enabled = False
        else:
            col.enabled = False
            col2.enabled = True
        
        


    def process_scipy(self, context):
        if is_package_installed('scipy') == False:
            return        

        import numpy as np
        from scipy.spatial import Delaunay
        from . import even_np

        bm = self.get_bm() 
        sel = [f1 for f1 in bm.faces if f1.select]
        even_np.get_points(bm, sel, self.prop_plen2)
    
        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)          




class InstallScipyOperator(bpy.types.Operator):
    """Install Scipy"""
    bl_idname = "piptool.install_scipy_operator"
    bl_label = "Install Scipy"

    def execute(self, context):
        # Code to install Scipy goes here
        try:
            from . import piptool
            piptool.install_package('scipy')            
            import scipy
        except ImportError:
            return {'CANCELLED'}
        
        self.report({'INFO'}, "Scipy installed successfully.")
        return {'FINISHED'}














