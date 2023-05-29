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

from mathutils import Matrix, Vector, Quaternion

import mathutils

import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
)

# from . import gui



class QuadSwordsOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.quad_swords_operator"
    bl_label = "Quad Swords"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    propdensity: FloatProperty(
        name="Slice density",
        description="Define the density of the cuts",
        default=5,
        min = 1,
        step = 1

    )    

    propmargin: FloatProperty(
        name="Margin",
        description="Define the negative margin of the projection",
        default=1.01,
        min = 1,
        max = 5
    )        

    propselected: BoolProperty(
        name="Selected Faces Only",
        description="Only cut the selected faces",
        default=False,
    )

    def draw(self, context):
        layout = self.layout        
        layout.prop(self, "propdensity", expand=True)
        layout.prop(self, "propmargin", expand=True)
        layout.prop(self, "propselected", expand=True)
        

    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        return bm


    def process(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()

        if self.propselected:
            bpy.ops.mesh.select_mode(type="FACE")        
            bpy.ops.mesh.hide(unselected=True)

        vmperp = bpy.context.space_data.region_3d.view_perspective        
        vmold = bpy.context.space_data.region_3d.view_matrix.copy()    

        #bpy.context.space_data.region_3d.view_perspective = 'ORTHO'

        obj = context.edit_object
        mat = obj.matrix_world
        bs = [Vector(p) for p in obj.bound_box]
        x1 = min(bs, key=lambda e:e.x).x
        x2 = max(bs, key=lambda e:e.x).x
        y1 = min(bs, key=lambda e:e.y).y
        y2 = max(bs, key=lambda e:e.y).y
        z1 = min(bs, key=lambda e:e.z).z
        z2 = max(bs, key=lambda e:e.z).z        
        # gui.lines = []
        plen = 1 / self.propdensity
        world = obj.matrix_world

        margin = self.propmargin
        x1 *= margin
        x2 *= margin
        y1 *= margin
        y2 *= margin
        z1 *= margin
        z2 *= margin

        p1 = Vector((x1, y1, z2 + 1))
        p2 = Vector((x2, y1, z2 + 1))
        p3 = Vector((x1, y2, z2 + 1))
        p4 = Vector((x2, y2, z2 + 1))
        move = Matrix.Translation(Vector((0,0,-2)))
        mat3 = move @ world.inverted()        
        self.process_slice(context, obj, plen, world, mat3, p1, p2, p3, p4, True, True)
        #self.process_slice(context, obj, plen, world, mat3, p1, p2, p3, p4, False, True)

        p1 = Vector((x1 - 1, y1, z1))
        p2 = Vector((x1 - 1, y1, z2))
        p3 = Vector((x1 - 1, y2, z1))
        p4 = Vector((x1 - 1, y2, z2))
        rot = Quaternion(Vector((0,1,0)), math.radians(90)).to_matrix().to_4x4()        
        move = Matrix.Translation(Vector((0,0,-2)))
        mat3 = move @ (rot @ world.inverted())
        self.process_slice(context, obj, plen, world, mat3, p1, p3, p2, p4, False, True)
        

        if vmperp == 'ORTHO':
            vmold[2][3] = 1
        bpy.context.space_data.region_3d.view_perspective = vmperp
        bpy.context.space_data.region_3d.view_matrix = vmold
        self.update_view()
        
        if self.propselected:
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='INVERT')


    def update_view(self):        
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.update()

    def process_slice(self, context, obj, plen, world, mat3, p1, p2, p3, p4, vertical, hori):
        lines = []
        if vertical:
            lines += self.fill_lines_view_top(plen, world, p1, p2, p3, p4)
        if hori:
            lines += self.fill_lines_view_top(plen, world, p1, p3, p2, p4)

        if len(lines) == 0:
            return
       
        bpy.context.space_data.region_3d.view_perspective = 'ORTHO'
        bpy.context.space_data.region_3d.view_matrix = mat3        
        self.update_view()
        self.slicing(context, lines, obj)        


    def slicing(self, context, lines, obj):
        me = bpy.data.meshes.new('swords_temp_mesh')
        new_obj = bpy.data.objects.new('swords_temp', me) 
        new_obj.location = (0,0,0)
        new_obj.show_name = True
        bpy.context.collection.objects.link(new_obj)
        bm2 = bmesh.new()
        bm2.from_mesh(me)
        for a, b in lines:
            v1 = bm2.verts.new(a)
            v2 = bm2.verts.new(b)
            e1 = bm2.edges.new((v1, v2))
        bm2.to_mesh(me)        
        override1 = context.copy()        
        override1['selected_objects'] = []
        override1['selected_objects'].append(new_obj)
        override1['selected_objects'].append(obj)
        bpy.ops.mesh.knife_project(override1, cut_through=True)
        bpy.data.objects.remove(new_obj, do_unlink=True)


    def fill_lines_view_top(self, plen, mat, p1, p2, p3, p4):
        lines = []
        lines += self.fill_lines_dir(plen, mat @ p1, mat @ p2, mat @ p3, mat @ p4)
        #lines += self.fill_lines_dir(plen, mat @ p1, mat @ p3, mat @ p2, mat @ p4)
        return lines


    def fill_lines_dir(self, plen, p1, p2, p3, p4):
        lines = []
        m1 = p2 - p1
        m2 = p4 - p3
        ct = math.floor(m1.length / plen)
        if ct == 0:
            return []
        m1s = m1.normalized() * m1.length / ct
        for i in range(ct + 1):
            k1 = p1 + m1s * i
            k2 = p3 + m1s * i
            lines.append((k1, k2))
        return lines        

     

    def invoke(self, context, event):
        if context.edit_object:
            self.process(context)
            #return {'RUNNING_MODAL'} 
            return {'FINISHED'}    
        else:
            return {'CANCELLED'}


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




