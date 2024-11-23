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

import numpy as np
import pprint


def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(AlignUVOperator.bl_idname) 
    layout.operator(SmoothUVOperator.bl_idname)
    layout.operator(SmoothUVInnerOperator.bl_idname)
    layout.operator(SmoothUVEdgeOperator.bl_idname)





class SmoothUVEdgeOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "uv.align_uv_smooth_edge_operator"
    bl_label = "Align UV (Edge)"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"



    prop_iterations: IntProperty(
        name="Engine loops",
        description="Iterations of the process",
        default=100,
        min=0,
    )

    prop_align_xy: BoolProperty(
        name="Align to global XY",
        description="Align to global XY axis",
        default=False
    )



    def get_loc_key(self, p1, uv_layer):
        v1 = p1.vert
        ps = v1.link_loops
        psout = []
        for p2 in ps:
            if p2[uv_layer].uv == p1[uv_layer].uv:
                psout.append(p2)
        # return psout
        return frozenset(psout)
    


    def process_edge(self, bm, uv_layer, prop_align_xy):
        sel = []
        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select_edge:
                    sel.append(p1)
        if len(sel) == 0:
            return
        
        vs = set()        
        for p1 in sel:
            fs = self.get_loc_key(p1, uv_layer)
            vs.add(fs)
            p2 = p1.link_loop_next
            fs2 = self.get_loc_key(p2, uv_layer)
            vs.add(fs2)
        
        pmap = {}
        for fs in vs:
            pmap[fs] = set()

        for fs in vs:
            p1 = list(fs)[0]
            for p2 in fs:                
                p3 = p2.link_loop_next
                fs2 = self.get_loc_key(p3, uv_layer)
                if fs2 not in vs:
                    continue
                pmap[fs].add(fs2)
                pmap[fs2].add(fs)

        for fs in pmap:
            ps = list(pmap[fs])
            if len(ps) < 2:
                continue
            cs = []
            for fs2 in ps:
                p = list(fs2)[0]
                cs.append(p[uv_layer].uv)

            cen = sum(cs, Vector((0,0))) / len(cs)
            for p in fs:
                p[uv_layer].uv = p[uv_layer].uv * 0.9 + cen * 0.1

        if prop_align_xy:
            pmap2 = {}
            for p1 in sel:
                p2 = p1.link_loop_next
                m1 = p2[uv_layer].uv - p1[uv_layer].uv
                if abs(m1.x) > abs(m1.y):                    
                    m1.x = 0
                else:
                    m1.y = 0
                fs2 = self.get_loc_key(p1, uv_layer)
                pmap2[fs2] = m1

            for fs in pmap2:
                v = pmap2[fs]
                for p1 in fs:
                    p1[uv_layer].uv += v * 0.1
                

                    


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def process(self, context):
        bm = self.get_bm()  
        uv_layer = bm.loops.layers.uv.active     

        for i in range(self.prop_iterations):
            self.process_edge(bm, uv_layer, self.prop_align_xy)

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
        return editing and selecting and ('EDGE' in uv_select_mode) # and is_face_mode


    def invoke(self, context, event): 
        self.operation_mode = 'None'                        
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}










class SmoothUVInnerOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "uv.align_uv_smooth_inner_operator"
    bl_label = "Align UV (Inner area)"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_auto_size: BoolProperty(
        name="Auto grid size",
        description="Auto adjust the target grid size for smoothing",
        default=True
    )


    prop_plen: FloatProperty(
        name="Grid size",
        description="Manually set the grid size",
        default=0.05,
        step=0.2,
        min=0.001
    )    


    prop_iterations: IntProperty(
        name="Engine loops",
        description="Iterations of the process",
        default=10,
        min=0,
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
        # return psout
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

    def check_boundary(self, p1, fs, uv_layer):
        v1 = p1.vert
        if len(fs) != len(v1.link_edges):
            return True
        
        total = 0
        for p2 in fs:
            p3 = p2.link_loop_next
            p4 = p2.link_loop_prev
            m1 = p3[uv_layer].uv - p1[uv_layer].uv
            m2 = p4[uv_layer].uv - p1[uv_layer].uv
            angle = abs(m1.angle(m2))
            total += angle

        # print(len(fs), math.degrees(total))
        
        if total < math.pi * 2 - 0.0001:
            return True

        for p2 in fs:
            p3 = p2.link_loop_radial_next
            p3 = p3.link_loop_next
            if p3 not in fs:
                return True
        return False
    

    def reorder_vertices(self, vertices):
        cx = sum(x for x, y in vertices) / len(vertices)
        cy = sum(y for x, y in vertices) / len(vertices)        
        vertices.sort(key=lambda v: math.atan2(v[1] - cy, v[0] - cx))
        return vertices
        

    def polygon_centroid(self, vertices):        
        vertices = self.reorder_vertices(vertices)
        closed_vertices = vertices + [vertices[0]]
        area = 0
        cx = 0
        cy = 0
        for i in range(len(closed_vertices) - 1):
            x0, y0 = closed_vertices[i]
            x1, y1 = closed_vertices[i + 1]
            
            det = (x0 * y1 - x1 * y0)
            area += det
            cx += (x0 + x1) * det
            cy += (y0 + y1) * det

        area = area / 2.0
        if area == 0:
            return None
        cx = cx / (6.0 * area)
        cy = cy / (6.0 * area)

        return Vector((cx, cy))



    def process_uv(self, bm, plen, step, uv_layer):
        # sel = [f1 for f1 in bm.faces if f1.select]
        sel = []
        for face in bm.faces:            
            uv_selected = all(loop[uv_layer].select for loop in face.loops)
            if uv_selected:
                sel.append(face)

        if len(sel) == 0:
            return
        
        pmap = {}
        fsmap1 = []
        fsmap2 = []
        fmap = {}
        for f1 in sel:
            # total = Vector((0,0))
            # cc = 0
            for p1 in f1.loops:
                # print(p1)
                if p1[uv_layer].select:
                    fs = self.get_loc_key(p1, uv_layer)
                    if self.check_boundary(p1, fs, uv_layer) == True:
                        fsmap1.append(fs)
                    else:
                        fsmap2.append(fs)

                    pmap[fs] = Vector((0,0))
                    # total += p1[uv_layer].uv
                    # cc += 1
            # if cc == 0:
            #     continue    
            # fmap[f1] = total / cc

        for fs in fsmap2:
            cs = []       
            ms = 0     
            for p1 in fs:
                p2 = p1.link_loop_next
                if p2.face not in sel:
                    continue
                # d = (p2[uv_layer].uv - p1[uv_layer].uv).length                
                # cs.append( d * p2[uv_layer].uv )
                # ms += d
                cs.append(p2[uv_layer].uv)

            if len(cs) == 0:
                continue
            p1 = list(fs)[0]
            # pmap[fs] += sum(cs, Vector((0,0))) / ms - p1[uv_layer].uv
            center = self.polygon_centroid(cs)
            if center is None:
                continue
            pmap[fs] += center - p1[uv_layer].uv


            # for p1 in fs:
            #     f1 = p1.face
            #     if f1 in fmap:
            #         center = fmap[f1]
            #         cs.append(center)
            # if len(cs) == 0:
            #     continue
            # p1 = list(fs)[0]
            # # pmap[fs] += (sum(cs, Vector((0,0))) / len(cs)) - p1[uv_layer].uv
            # pmap[fs] = sum(cs, Vector((0,0))) / len(cs)

        
        for fs in pmap:
            v1 = pmap[fs]
            # if v1 is None:
            #     continue
            vf = v1 * step
            for p in fs:
                p[uv_layer].uv += vf
                # p[uv_layer].uv = p[uv_layer].uv * 0.9 + v1 * 0.1




    def get_sel(self, bm, uv_layer):
        sel = []
        for face in bm.faces:            
            uv_selected = all(loop[uv_layer].select for loop in face.loops)
            if uv_selected:
                sel.append(face)
        if len(sel) == 0:
            return []
        return sel
    


    def get_mesh_edge_len(self, bm, uv_layer):
        total = 0
        count = 0
        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    p2 = p1.link_loop_next
                    elen = (p2[uv_layer].uv - p1[uv_layer].uv).length
                    total += elen
                    count += 1
        if count == 0:
            return 0
        # en = total / count
        # # en = min(en, 0.1)
        # # en = max(en, 0.05)
        en = 1.0 / math.sqrt(count)
        return en
    


    def process(self, context):
        bm = self.get_bm()        

        plen = self.prop_plen

        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV data found")
            return        

        if self.prop_auto_size:
            plen = self.get_mesh_edge_len(bm, uv_layer)

        sel = self.get_sel(bm, uv_layer)
        if len(sel) == 0:
            return
        
        # ang_list = self.get_ang_list(sel)
        # pdata = self.get_tables(sel, uv_layer, ang_list)

        for i in range(self.prop_iterations):
            self.process_uv(bm, plen, 0.1, uv_layer)
            # self.process_uv_fast(sel, plen, uv_layer, ang_list, pdata)

        # fsmap, plist, _, _, pindexmap = pdata

        # if self.prop_align:
        #     plist = self.simple_align(pdata)
            
        # self.update_data(bm, uv_layer, pindexmap, plist, sel, fsmap)

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






class SmoothUVOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "uv.align_uv_smooth_operator"
    bl_label = "Align UV (Smoothing shape)"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"



    prop_iterations: IntProperty(
        name="Engine loops",
        description="Iterations of the process",
        default=10,
        min=0,
    )

    prop_align: BoolProperty(
        name="Align XY axis",
        description="Align to Global XY Axis",
        default=False
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
        # return psout
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
    


    def get_sel(self, bm, uv_layer):
        sel = []
        for face in bm.faces:            
            uv_selected = all(loop[uv_layer].select for loop in face.loops)
            if uv_selected:
                sel.append(face)
        if len(sel) == 0:
            return []
        return sel
    



    def get_mesh_edge_len(self, bm, uv_layer):
        total = 0
        count = 0
        es = set()
        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    p2 = p1.link_loop_next
                    elen = (p2[uv_layer].uv - p1[uv_layer].uv).length
                    total += elen
                    # count += 1

        return total
            


    
    def rotation(self, angle):
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        # return (cos_theta, sin_theta)
        return np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])

    

    def process_uv(self, bm, step, uv_layer):
        # sel = [f1 for f1 in bm.faces if f1.select]
        sel = []
        for face in bm.faces:            
            uv_selected = all(loop[uv_layer].select for loop in face.loops)
            if uv_selected:
                sel.append(face)

        if len(sel) == 0:
            return
        
        pmap = {}
        rots = []
        for f1 in sel:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    fs = self.get_loc_key(p1, uv_layer)
                    pmap[fs] = Vector((0.0, 0.0))
            pc = len(f1.loops)
            ang = (math.pi * (pc - 2)) / pc
            rot = self.rotation(ang * -1)
            rots.append(rot)

        
        for i, f1 in enumerate(sel):
            # pc = len(f1.loops)
            # cen = self.get_center(f1, uv_layer)
            # sec = math.pi * 2 / pc
            # ang = (math.pi * (pc - 2)) / pc
            # s1 = ang / 2    
            rot = rots[i]

            for p1 in f1.loops:
                if p1[uv_layer].select:
                    fs = self.get_loc_key(p1, uv_layer)
                    p2 = p1.link_loop_next
                    # pmap[fs] += self.balance(p1[uv_layer].uv, p2[uv_layer].uv, plen)
                    p3 = p1.link_loop_prev
                    # pmap[fs] += self.balance(p1[uv_layer].uv, p3[uv_layer].uv, plen)
                    p4 = p3.link_loop_prev
                    # m1 = (p4[uv_layer].uv - p3[uv_layer].uv).normalized() * plen
                    m1 = p4[uv_layer].uv - p3[uv_layer].uv
                    # m2 = self.rotate(m1, ang * -1
                    m2 = rot @ m1   
                    m2 = Vector(m2)
                    target = p3[uv_layer].uv + m2
                    pmap[fs] += (target - p1[uv_layer].uv)
        
        for fs in pmap:
            v = pmap[fs]
            v2 = v * step                        
            for p in fs:
                p[uv_layer].uv += v2
                

    def scale(self, bm, uv_layer, fc):
        center = Vector((0,0))
        count = 0
        fss = set()
        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    center += p1[uv_layer].uv
                    count += 1
        if count == 0:
            return
        center /= count

        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    off = p1[uv_layer].uv - center
                    off *= fc
                    p1[uv_layer].uv = center + off




    def getcen(self, vectors, k, max_iters=100, tolerance=1e-4):
        centroids = vectors[np.random.choice(vectors.shape[0], k, replace=False)]
        
        epsilon = 1e-8
        
        for i in range(max_iters):            
            distances = np.linalg.norm(vectors[:, np.newaxis] - centroids, axis=2)
            labels = np.argmin(distances, axis=1)
            
            new_centroids = np.array([vectors[labels == j].mean(axis=0) for j in range(k)])
            
            for j in range(k):
                if np.sum(labels == j) == 0:
                    new_centroids[j] = vectors[np.random.choice(vectors.shape[0])]
            
            new_centroids = new_centroids / (np.linalg.norm(new_centroids, axis=1)[:, np.newaxis] + epsilon)
            
            if np.linalg.norm(new_centroids - centroids) < tolerance:
                break
            
            centroids = new_centroids

        return centroids, labels
    


    def rotate_mesh(self, bm, uv_layer, angle):        
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        matrix = np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
        # rotate points
        center = Vector((0,0))
        count = 0
        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    center += p1[uv_layer].uv
                    count += 1
        if count == 0:
            return
        center /= count
        
        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    uv = p1[uv_layer].uv
                    uv -= center
                    uv = np.dot(matrix, uv)
                    uv += center
                    p1[uv_layer].uv = uv


    def simple_align(self, bm, uv_layer):
        ps = []
        vs = []        
        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    uv = p1[uv_layer].uv
                    ps.append(uv)
                    p2 = p1.link_loop_next
                    m1 = p2[uv_layer].uv - uv
                    m1.normalize()  
                    if m1.y < 0:
                        m1 = m1 * -1
                    vs.append(m1)

        if len(ps) == 0:
            return
        vs = np.array(vs)
        centroids, labels = self.getcen(vs, 6)

        counts = np.bincount(labels) 
        most_popular_index = np.argmax(counts)        
        axis = centroids[most_popular_index]       

        axis = axis / np.linalg.norm(axis)
        angle = math.atan2(axis[1], axis[0]) * -1
        angle = (angle + math.pi) % math.pi
        angle = (angle + math.pi/2) % (math.pi/2)
        if angle > math.pi / 4:
            angle = angle - math.pi / 2

        self.rotate_mesh(bm, uv_layer, angle)        
        



                

    def process(self, context):
        bm = self.get_bm()        

        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV data found")
            return        

        size1 = self.get_mesh_edge_len(bm, uv_layer)

        sel = self.get_sel(bm, uv_layer)
        if len(sel) == 0:
            return
        
        for i in range(self.prop_iterations):
            self.process_uv(bm, 0.1, uv_layer)


        size2 = self.get_mesh_edge_len(bm, uv_layer)
        fc = size1 / size2
        self.scale(bm, uv_layer, fc)

        
        if  self.prop_align:
            self.simple_align(bm, uv_layer)
        
        # ang_list = self.get_ang_list(sel)
        # pdata = self.get_tables(sel, uv_layer, ang_list)

        # for i in range(self.prop_iterations):
        #     # self.process_uv(bm, plen, 0.1, uv_layer, self.prop_relax, self.prop_balance)
        #     self.process_uv_fast(sel, plen, uv_layer, ang_list, pdata)

        # fsmap, plist, _, _, pindexmap = pdata

        # if self.prop_align:
        #     plist = self.simple_align(pdata)
            
        # self.update_data(bm, uv_layer, pindexmap, plist, sel, fsmap)

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



    prop_auto_size: BoolProperty(
        name="Auto grid size",
        description="Auto adjust the target grid size for smoothing",
        default=True
    )



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
        

    def set_uv(self, p1, uv_layer, uv, fs):
        p1[uv_layer].uv = uv
        for p2 in fs:
            p2[uv_layer].uv = uv
        # p1[uv_layer].uv = uv


    def set_square(self, f1, cen, half, uv_layer, fsmap):
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
        self.set_uv(pv, uv_layer, cen + Vector((-half, -half)), fsmap[pv])
        pv = pv.link_loop_next
        self.set_uv(pv, uv_layer, cen + Vector((half, -half)), fsmap[pv])
        pv = pv.link_loop_next
        self.set_uv(pv, uv_layer, cen + Vector((half, half)), fsmap[pv])
        pv = pv.link_loop_next
        self.set_uv(pv, uv_layer, cen + Vector((-half, half)), fsmap[pv])
        

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


    def get_loc_key(self, p1, uv_layer):
        v1 = p1.vert
        ps = v1.link_loops
        psout = []
        for p2 in ps:
            if p2[uv_layer].uv == p1[uv_layer].uv:
                psout.append(p2)
        return psout
    

    def process_fast(self, bm, plen, uv_layer):
        sel = []
        for face in bm.faces:            
            if len(face.loops) != 4:
                continue
            uv_selected = all(loop[uv_layer].select for loop in face.loops)
            if uv_selected:
                sel.append(face)

        fsmap = {}
        for i, f1 in enumerate(sel):            
            for p1 in f1.loops:                
                if p1[uv_layer].select:
                    fs = self.get_loc_key(p1, uv_layer)
                    fsmap[p1] = fs
        if len(sel) == 0:
            return

        fs_all = sel.copy()

        loaded = set()        
        while len(fs_all) > 0:
            first = fs_all.pop(0)
            if first in loaded:
                continue
            cen = self.face_center(first, uv_layer)        
            half = plen/2            
            self.set_square(first, cen, half, uv_layer, fsmap)    
            linked = [first]
            loaded.add(first)
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
                    m1 = m1.normalized() * plen
                    m2 = self.rotate2d_90_ccw(m1)
                    self.set_uv(k3, uv_layer, p2[uv_layer].uv + m2, fsmap[k3])
                    self.set_uv(k4, uv_layer, p3[uv_layer].uv + m2, fsmap[k4])
                    linked.append(k1.face)
                    loaded.add(k1.face)
                    # loaded.add(f2)


    def get_mesh_edge_len(self, bm, uv_layer):
        total = 0
        count = 0
        for f1 in bm.faces:
            for p1 in f1.loops:
                if p1[uv_layer].select:
                    p2 = p1.link_loop_next
                    elen = (p2[uv_layer].uv - p1[uv_layer].uv).length
                    total += elen
                    count += 1
        if count == 0:
            return 0
        return total / count
    


    def process(self, context):
        bm = self.get_bm()         
        
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV data found")
            return        

        if self.prop_auto_size:
            plen = self.get_mesh_edge_len(bm, uv_layer)

        self.process_fast(bm, plen, uv_layer)

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


