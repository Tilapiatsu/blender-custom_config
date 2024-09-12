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



def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(AlignUVOperator.bl_idname) 
    layout.operator(SmoothUVOperator.bl_idname)




class SmoothUVOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "uv.align_uv_smooth_operator"
    bl_label = "Align UV (Smoothing)"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="Grid Size",
        description="Grid size",
        default=0.05,
        step=0.2,
        min=0.001
    )    


    # prop_step: FloatProperty(
    #     name="Step Size",
    #     description="Smaller step size is slower, but improves accuracy a bit",
    #     default=0.1,
    #     step=0.2,
    #     min=0.0001
    # )        

    prop_iterations: IntProperty(
        name="Engine Loops",
        description="Iterations of the process",
        default=100,
        min=0,
    )

    prop_align: BoolProperty(
        name="Align XY Axis",
        description="Align to Global XY Axis",
        default=True
    )


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm

    def balance(self, p1, p2, plen):
        off = p2 - p1
        norm = off.normalized()
        length = off.length
        return norm * (length - plen)/2
    

    def get_loc_key(self, p1, uv_layer):
        v1 = p1.vert
        ps = v1.link_loops
        psout = []
        for p2 in ps:
            if p2[uv_layer].uv == p1[uv_layer].uv:
                psout.append(p2)
        return frozenset(psout)
    
    def get_angle(self, p1, uv_layer):
        p2 = p1.link_loop_next
        p3 = p2.link_loop_prev
        a = p1[uv_layer].uv
        b = p2[uv_layer].uv
        c = p3[uv_layer].uv
        m1 = b - a
        m2 = c - a
        deg = m1.angle_signed(m2)
        return deg
    
    def get_center(self, f1, uv_layer):
        cen = Vector((0,0))
        ct = 0
        for p1 in f1.loops:
            cen += p1[uv_layer].uv
            ct += 1
        if ct == 0:
            return Vector((0,0))
        cen /= ct
        return cen

    def rotate(self, m1, deg):
        cos_theta = math.cos(deg)
        sin_theta = math.sin(deg)
        x = m1.x
        y = m1.y
        x_rotated = x * cos_theta - y * sin_theta
        y_rotated = x * sin_theta + y * cos_theta        
        return Vector((x_rotated, y_rotated))
    


    def process_uv(self, bm, plen, step):
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV data found")
            return
                
        # sel = [f1 for f1 in bm.faces if f1.select]
        sel = []
        for face in bm.faces:            
            uv_selected = all(loop[uv_layer].select for loop in face.loops)
            if uv_selected:
                sel.append(face)

        if len(sel) == 0:
            return
        
        pmap = {}
        for f1 in sel:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    fs = self.get_loc_key(p1, uv_layer)
                    pmap[fs] = Vector((0.0, 0.0))
        
        for f1 in sel:
            pc = len(f1.loops)
            # cen = self.get_center(f1, uv_layer)
            # sec = math.pi * 2 / pc
            ang = (math.pi * (pc - 2)) / pc
            # s1 = ang / 2                        

            for p1 in f1.loops:
                if p1[uv_layer].select:
                    fs = self.get_loc_key(p1, uv_layer)
                    p2 = p1.link_loop_next
                    pmap[fs] += self.balance(p1[uv_layer].uv, p2[uv_layer].uv, plen)
                    p3 = p1.link_loop_prev
                    pmap[fs] += self.balance(p1[uv_layer].uv, p3[uv_layer].uv, plen)

                    p4 = p3.link_loop_prev
                    m1 = (p4[uv_layer].uv - p3[uv_layer].uv).normalized() * plen
                    m2 = self.rotate(m1, ang * -1)
                    target = p3[uv_layer].uv + m2

                    p5 = p2.link_loop_next
                    m1 = (p5[uv_layer].uv - p2[uv_layer].uv).normalized() * plen
                    m2 = self.rotate(m1, ang)
                    target2 = p2[uv_layer].uv + m2

                    tar3 = (target + target2) / 2

                    pmap[fs] += (tar3 - p1[uv_layer].uv)                    
        
        for fs in pmap.keys():
            v = pmap[fs]
            for p in fs:
                p[uv_layer].uv += v * step



    def align_uv(self, bm):
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            return
                
        sel = []
        for face in bm.faces:            
            uv_selected = all(loop[uv_layer].select for loop in face.loops)
            if uv_selected:
                sel.append(face)

        if len(sel) == 0:
            return
        
        pmap = {}
        for f1 in sel:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    fs = self.get_loc_key(p1, uv_layer)
                    pmap[fs] = Vector((0.0, 0.0))
        
        d90 = math.pi / 2
        index_count = [0,0]
        psmap = {}
        for f1 in sel:
            for p1 in f1.loops:                
                a, b = p1[uv_layer].uv, p1.link_loop_next[uv_layer].uv
                off = b - a
                deg = math.atan2(off.y, off.x) + math.pi
                deg = deg % d90
                if math.isnan(deg):
                    continue                
                deg_align_index = round(deg / d90)
                index_count[deg_align_index] += 1
                psmap[p1] = [deg_align_index, deg]
        
        max_index = index_count.index(max(index_count))
        rotate_target = max_index * d90        
        avg_rotate = 0
        avg_count = 0

        for p1 in psmap.keys():
            deg_align_index, deg = psmap[p1]
            if deg_align_index != max_index:
                continue
            diff = rotate_target - deg
            avg_rotate += diff
            avg_count += 1

        if avg_count == 0:
            return
        avg_rotate /= avg_count

        center = Vector((0,0))
        cc = 0
        for f1 in sel:
            for p1 in f1.loops:                
                a = p1[uv_layer].uv
                center += a
                cc += 1
        if cc == 0:
            return
        center /= cc

        for fs in pmap.keys():   
            for p1 in fs:            
                a = p1[uv_layer].uv
                a -= center
                cos_theta = math.cos(avg_rotate)
                sin_theta = math.sin(avg_rotate)
                x = a.x * cos_theta - a.y * sin_theta
                y = a.x * sin_theta + a.y * cos_theta                    
                p1[uv_layer].uv = Vector((x, y)) + center
                
                

    def process(self, context):
        bm = self.get_bm()        

        for i in range(self.prop_iterations):
            self.process_uv(bm, self.prop_plen, 0.1)

        # if self.prop_align:
        #     self.align_uv(bm)   

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
        # is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        uv_select_mode = bpy.context.tool_settings.uv_select_mode

        # print(uv_select_mode)
        return editing and selecting and ('FACE' in uv_select_mode) # and is_face_mode


    def invoke(self, context, event): 
        self.operation_mode = 'None'                        
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}








class AlignUVOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "uv.align_uv_operator"
    bl_label = "Align UV"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="Grid Size",
        description="Grid size",
        default=0.05,
        step=0.2,
        min=0.001
    )


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm

    def face_center(self, face, uv_layer):
        center = Vector((0,0))
        for p1 in face.loops:
            center += p1[uv_layer].uv
        center /= len(face.loops)
        return center
    
    def is_linked_edge(self, p1, uv_layer):
        p2 = p1.link_loop_next
        k1 = p1.link_loop_radial_next
        k2 = k1.link_loop_next
        if p1[uv_layer].uv != k2[uv_layer].uv:
            return False
        if p2[uv_layer].uv != k1[uv_layer].uv:
            return False
        return True
        

    def set_uv(self, p1, uv_layer, uv):
        v1 = p1.vert
        ps = v1.link_loops
        ms = []
        for p2 in ps:
            if p2[uv_layer].uv == p1[uv_layer].uv:                
                ms.append(p2)
        for p2 in ms:
            p2[uv_layer].uv = uv
        # p1[uv_layer].uv = uv


    def set_square(self, f1, cen, half, uv_layer):
        pv = f1.loops[0]
        nodes = [Vector((-half, -half)), Vector((half, -half)), Vector((half, half)), Vector((-half, half))]
        ds = []
        for i in range(len(f1.loops)):
            offset = pv[uv_layer].uv - cen
            offset.normalize()
            sim = offset.dot(nodes[0])
            ds.append((sim, pv))
            pv = pv.link_loop_next
        _, pv = max(ds)
        self.set_uv(pv, uv_layer, cen + Vector((-half, -half)))
        pv = pv.link_loop_next
        self.set_uv(pv, uv_layer, cen + Vector((half, -half)))
        pv = pv.link_loop_next
        self.set_uv(pv, uv_layer, cen + Vector((half, half)))
        pv = pv.link_loop_next
        self.set_uv(pv, uv_layer, cen + Vector((-half, half)))        

    def rotate2d_90_ccw(self, m1):
        return Vector((-m1.y, m1.x))
    

    def get_center(self, sel, uv_layer):
        center = Vector((0,0))
        ct = 0
        for f1 in sel:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    center += p1[uv_layer].uv
                    ct += 1
        if ct == 0:
            return Vector((0,0))
        center /= ct        
        return center


    def process_fast(self, bm, plen, step):
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV data found")
            return
                
        # sel = [f1 for f1 in bm.faces if f1.select]
        sel = []
        for face in bm.faces:            
            if len(face.loops) != 4:
                continue
            uv_selected = all(loop[uv_layer].select for loop in face.loops)
            if uv_selected:
                sel.append(face)

        if len(sel) == 0:
            return

        fs_all = sel.copy()
        # center = self.get_center(sel, uv_layer)

        loaded = set()        
        while len(fs_all) > 0:
            first = fs_all.pop(0)
            if first in loaded:
                continue
            cen = self.face_center(first, uv_layer)        
            half = plen/2            
            self.set_square(first, cen, half, uv_layer)            
            linked = [first]
            while len(linked) > 0:
                f2 = linked.pop(0)     
                for p2 in f2.loops:
                    p3 = p2.link_loop_next
                    k1 = p2.link_loop_radial_next
                    if k1.face not in sel:
                        continue
                    if k1.face in loaded:
                        continue
                    if not self.is_linked_edge(p2, uv_layer):
                        continue                                      
                    k2 = k1.link_loop_next
                    k3 = k2.link_loop_next
                    k4 = k3.link_loop_next
                    m1 = p2[uv_layer].uv - p3[uv_layer].uv
                    m2 = self.rotate2d_90_ccw(m1)
                    self.set_uv(k3, uv_layer, p2[uv_layer].uv + m2)
                    self.set_uv(k4, uv_layer, p3[uv_layer].uv + m2)
                    linked.append(k1.face)
                loaded.add(f2)


    def process(self, context):
        bm = self.get_bm()         
        

        # for i in range(self.prop_iterations):
        #     self.process_uv(bm, self.prop_plen, 0.1)

        # if self.prop_align:
        #     self.align_uv(bm)   

        self.process_fast(bm, self.prop_plen, 0.1)

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
        # is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        uv_select_mode = bpy.context.tool_settings.uv_select_mode

        # print(uv_select_mode)
        return editing and selecting and ('FACE' in uv_select_mode) # and is_face_mode


    def invoke(self, context, event): 
        self.operation_mode = 'None'                        
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}


