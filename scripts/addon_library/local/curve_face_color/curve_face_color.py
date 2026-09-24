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
import bpy
import bmesh

'''
import blf
import bgl
from mathutils import Matrix, Vector, Quaternion
from mathutils import bvhtree
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader
'''

import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
)


import random


class CurveFaceColorOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.curve_face_color_operator"
    bl_label = "Curve Face Color"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"

    operation_mode : EnumProperty(
                #(identifier, name, description, icon, number)
        items = [('Edge Angle','Edge Angle','','',0),
                 ('Seam','Seam (marked)','','',1), 
                 ('Sharp','Sharp (marked)','','',2),
                 ],
        name = "Operation Mode",
        default = 'Edge Angle')

    propangle: FloatProperty(
        name="Edge Angle",
        description="Define sharp edges by this angle",
        default=45
    )    

    def draw(self, context):
        layout = self.layout                
        row = layout.row()
        layout.prop(self, "operation_mode", expand=True)
        layout.prop(self, "propangle", expand=True)


    def get_bm(self, context):
        obj = context.edit_object
        me = obj.data
        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        return bm


    def process(self, context):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.mode_set(mode = 'EDIT')   
        bm = self.get_bm(context)

        if self.operation_mode == 'Edge Angle':
            deg = math.radians(self.propangle)
            bpy.ops.mesh.edges_select_sharp(sharpness=deg)
            map1 = self.put_set(bm)
            self.assign_materials(map1)
        elif self.operation_mode == 'Seam':            
            self.select_seam(bm)
            map1 = self.put_set(bm)
            self.assign_materials(map1)
        elif self.operation_mode == 'Sharp':
            self.select_sharp(bm)
            map1 = self.put_set(bm)
            self.assign_materials(map1)                    

        bpy.ops.mesh.select_mode(type="FACE")


    def select_seam(self, bm):        
        seam = False
        for edge in bpy.context.object.data.edges:
            if edge.use_seam:
                seam = True
                break
        if seam == False:
            return
        for e1 in bm.edges:
            if e1.seam:
                e1.select = True


    def select_sharp(self, bm):
        sharp = False
        for edge in bpy.context.object.data.edges:
            if edge.use_edge_sharp:
                sharp = True
                break
        if sharp == False:
            return
        for e1 in bm.edges:
            if e1.smooth == False:
                e1.select = True


    def assign_materials(self, map1):
        obj = bpy.context.active_object #Set active object to variable
        for p in map1:
            mat = bpy.data.materials.new(name="Generated") #set new material to variable
            obj.data.materials.append(mat) #add the material to the object
            r = random.random()
            g = random.random()
            b = random.random()
            mat.diffuse_color = (r, g, b, 1)
            idx = obj.data.materials.find(mat.name)
            s1 = map1[p]
            for f1 in s1:
                f1.material_index = idx
                #bpy.context.object.active_material.diffuse_color = (1, 0, 0) #change color


    def put_set(self, bm):
        map1 = {}
        if bm == None:
            return
        #bm.faces.ensure_lookup_table()
        map1 = {}        
        for f1 in bm.faces:
            map1[f1] = set([f1])

        mer = [(f1, self.other_face(f1, e1)) for f1 in bm.faces for e1 in f1.edges if e1.select == False]               

        for f1, f2 in mer:    
            if f1 is None or f2 is None:
                continue
            s1 = map1[f1]            
            s2 = map1[f2]            
            for f3 in s2:
                s1.add(f3)
                map1[f3] = s1                
        map2 = {}
        for p in map1:
            s1 = map1[p]
            key = id(s1)
            if key in map2:
                continue
            else:
                map2[key] = s1
        
        '''
        for p in map2:
            for f1 in map2[p]:
                print(f1)
            print('===========')
        '''
        return map2  
        
                
    def other_face(self, f1, e1):
        if len(e1.link_faces) == 1:
            return None
        f2, f3 = e1.link_faces
        if f1 == f2:
            return f3
        else:
            return f2


    def execute(self, context):
        self.process(context)
        return {'FINISHED'}    

    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == 'MESH'        
        editing = context.mode == 'EDIT_MESH' 
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return selecting and editing and (is_face_mode or is_edge_mode)




