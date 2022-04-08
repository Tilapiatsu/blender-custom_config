# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Copyright (C) 2022 VFX Grace - All Rights Reserved
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


# All Operator

import bpy
from bpy.types import Operator,SpaceView3D
from bpy.props import (
    IntProperty,
    BoolProperty,
    FloatProperty,
    StringProperty,
)
from collections import Counter
import bmesh
import array
import threading
import functools
from . import (
    mesh_helpers,
    report,
)


# -- Globals -- #
info=[]
mesh_check_real_handle = []

def setup_environment(flag):
    """set the mode as edit, select mode as vertices, and reveal hidden vertices"""
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type=flag.upper())
    bpy.ops.mesh.reveal()


class MESH_OT_Check_LoosePointsSelect(Operator):
    bl_idname = "mesh.select_loose_points"
    bl_label = "Select Isolated Vertices"
    bl_description = "Select isolated vertices of active object"
    
    @staticmethod
    def main_check(check,info,bm):
        setup_environment("VERT")
        bpy.ops.mesh.select_loose()
        custom_rgb = check.custom_loose_points_color  
        bm_array  = []      
        for v in bm.verts:
            if v.select is True:
                bm_array.append(v.index)
        if len(bm_array)>0:
            verts = array.array('i',bm_array)
            info.append(("Loose_Points: %d" % len(bm_array),(bmesh.types.BMVert,verts,custom_rgb)))

        

class MESH_OT_Check_LooseEdgesSelect(Operator):
    bl_idname = "mesh.select_loose_edges"
    bl_label = "Select Isolated Edges"
    bl_description = "Select isolated edges of active object"
    @staticmethod
    def main_check(check,info,bm):
        setup_environment('EDGE') 
        bpy.ops.mesh.select_loose()
        custom_rgb = check.custom_loose_edges_color
        bm_array = []
        for v in bm.edges:
            if v.select is True:
                bm_array.append(v.index)
        if len(bm_array)>0:
            edges = array.array('i',bm_array)
            info.append(("Loose_Edges: %d" % len(bm_array),(bmesh.types.BMEdge,edges,custom_rgb)))
            

class MESH_OT_Check_LooseFacesSelect(Operator):
    bl_idname = "mesh.select_loose_faces"
    bl_label = "Select Isolated Faces"
    bl_description = "Select isolated Faces of active object"
    @staticmethod
    def main_check(check,info,bm):
        setup_environment('FACE') 
        bpy.ops.mesh.select_loose()
        custom_rgb = check.custom_loose_faces_color
        bm_array = []
        for v in bm.faces:
            if v.select is True:
                bm_array.append(v.index)
        if len(bm_array)>0:
            faces = array.array('i',bm_array)
            info.append(("Loose Faces: %d" % len(bm_array),(bmesh.types.BMFace,faces,custom_rgb)))
        

class MESH_OT_Check_Select_Doubles(Operator):
    bl_idname = "mesh.select_doubles"
    bl_label = "Select Doubles"
    bl_options = {'REGISTER','UNDO'}
   
    def execute(self,context):
        obj = context.active_object
        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=False, triangulate=False)
        setup_environment('VERT')
        doubles_count = 0

        double_dist = context.scene.check.doubles_threshold_value
        select = bmesh.ops.find_doubles(bm, verts=bm.verts, keep_verts=[], dist=double_dist)

        double_selects = []

        for i, (text, data) in enumerate(info):
            if text.startswith('Double Verts'):
                info.pop(i)
        if len(select["targetmap"]) > 0:
            for k,v in select['targetmap'].items():
                k.select_set(True)
                double_selects.append(k.index)
            custom_rgb = context.scene.check.custom_doubles_points_color
            info.append(("Double Verts: %d" % len(select["targetmap"]),
                        (bmesh.types.BMVert, double_selects,custom_rgb)))
        report.update(*info)
   
    
class MESH_OT_Check_TirsSelect(Operator):
    bl_idname = "mesh.select_tirs"
    bl_label = "Select Triangles"
    bl_description = "Select Triangles of active object"
    bl_options = {'REGISTER','UNDO'}
    
    @staticmethod
    def main_check(check,info,bm):
        setup_environment('FACE')
        custom_rgb = check.custom_tir_color
        bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
       
        bm_array = []
        for e in bm.faces:
            if e.select is True:
                bm_array.append(e.index)
       
        if len(bm_array)>0:
            face = array.array('i',bm_array)
            info.append(("Triangles: %d" % len(bm_array),
                        (bmesh.types.BMFace,bm_array,custom_rgb)))
            bpy.ops.mesh.select_all(action='DESELECT')

class MESH_OT_Check_Face_Orientation(Operator):
    """Checking face orientation"""
    bl_idname = "mesh.face_orientation"
    bl_label = "Check Degenerate"
 
    def execute(self, context):
        check = context.scene.check
        bpy.context.space_data.overlay.show_face_orientation = check.face_orientation
        
    
        bpy.context.space_data.overlay.show_vertex_normals = check.show_vertex_normals
        bpy.context.space_data.overlay.show_split_normals = check.show_split_normals
        bpy.context.space_data.overlay.show_face_normals = check.show_face_normals
        
        if check.show_vertex_normals == True or check.show_split_normals == True or check.show_face_normals == True:
            bpy.context.space_data.overlay.normals_length = check.normals_length
        
      
      

class MESH_OT_Recalculate_Normals(Operator):
    """Recalculate Normal"""
    bl_idname = "mesh.normals_consistent"
    bl_label = "normals consistent"
    bl_description = "Recalculate Normal: Make face and vertex normals point either outside or inside the mesh.        "
    
    inside:BoolProperty(
        name = "Recalculate Normal",
        )
        
    def execute(self, context):
        if self.inside == False:
            bpy.ops.mesh.normals_make_consistent(inside=False)
        else:
            bpy.ops.mesh.normals_make_consistent(inside=True)
            
        return {'FINISHED'}


class MESH_OT_Check_NgonsSelect(Operator):
    '''Checking polygons'''
    bl_idname = "mesh.select_ngons"
    bl_label = "Select Polygons"
    bl_description = "Select Polygons of active object"
    bl_options = {'REGISTER','UNDO'}
  
    def execute(self, context):
        bm = mesh_helpers.bmesh_from_object(bpy.context.active_object)
        custom_rgb = context.scene.check.custom_ngons_color
        setup_environment('FACE')
        count = context.scene.check.ngons_verts_count-1
        bpy.ops.mesh.select_face_by_sides(number = count, type='GREATER')
        
        bm_array = []
        
        for e in bm.faces:
            if e.select is True:
                bm_array.append(e.index)
        
        for i, (text, data) in enumerate(info):
            if text.startswith('Ngons'):
                info.pop(i) 
        if len(bm_array)>0:
            face = array.array('i',bm_array)
            info.append(("Ngons: %d" % len(bm_array),(bmesh.types.BMFace,bm_array,custom_rgb)))
        report.update(*info)


class MESH_OT_Check_Intersections(Operator):
    """Checking intersection"""
    bl_idname = "mesh.check_intersect"
    bl_label = "Check Intersections"
    
    @staticmethod
    def main_check(check,info,bm):
        custom_rgb  =check.intersect_color
        obj = bpy.context.active_object
     
        faces_intersect = mesh_helpers.bmesh_check_self_intersect_object(obj)
        if len(faces_intersect)>0:
            info.append(("Intersect Face: %d" % len(faces_intersect),
                        (bmesh.types.BMFace, faces_intersect,custom_rgb)))



class MESH_OT_Check_Degenerate(Operator):
    """Checking degenerate polygons """
    bl_idname = "mesh.check_degenerate"
    bl_label = "Check Degenerate"
    
    def execute(self, context):
        bm = mesh_helpers.bmesh_from_object(bpy.context.active_object)
        degenerate = context.scene.check.degenerate
        custom_rgb = context.scene.check.degenerate_color    
        threshold = context.scene.check.threshold_zero
        faces_zero = array.array('i', (i for i, ele in enumerate(bm.faces) if ele.calc_area() <= threshold))
        
        for i, (text, data) in enumerate(info):
            if text.startswith('Zero Faces'):
                info.pop(i)
        if len(faces_zero) > 0:
            info.append(("Zero Faces: %d" % len(faces_zero),(bmesh.types.BMFace, faces_zero,custom_rgb)))
        report.update(*info)
      


class MESH_OT_Check_Distorted(Operator):
    """Checking distortion"""
    bl_idname = "mesh.check_distort"
    bl_label = "Check Distorted Faces"

    def execute(self, context):
        bm = mesh_helpers.bmesh_from_object(bpy.context.active_object)
        angle_distort = context.scene.check.angle_distort
        custom_rgb = context.scene.check.distorted_color
        bm.normal_update()
        faces_distort = []
        faces_distort = array.array(
                'i',
                (i for i, ele in enumerate(bm.faces) if mesh_helpers.face_is_distorted(ele, angle_distort))
                )
        
        for i, (text, data) in enumerate(info):
            if text.startswith('Non-Flat Faces'):
                info.pop(i)
        if len(faces_distort)>0:
            info.append(("Non-Flat Faces: %d" % len(faces_distort),
                        (bmesh.types.BMFace, faces_distort,custom_rgb)))
        report.update(*info)
     
        
 

class MESH_OT_Check_Select_Multi_Face(Operator):
    """Checking non manifold and boundaries """
    bl_idname = "mesh.check_select_multi_face"
    bl_label = "Check Distorted Faces"
    
    @staticmethod
    def main_check(check,info,bm):
        setup_environment('EDGE')
        custom_rgb = check.use_multi_face_color
        bpy.ops.mesh.select_non_manifold(
                extend=False,
                use_wire=False,
                use_boundary=False,
                use_multi_face=True,
                use_non_contiguous=False,
                use_verts=False,
                )
       
        bm_array = []
        for e in bm.edges:
            if e.select is True:
                bm_array.append(e.index)
   
        if len(bm_array)>0:
            edges = array.array('i',bm_array)
            info.append(("Use Mult Face: %d" % len(bm_array),(bmesh.types.BMEdge,edges,custom_rgb)))
   


class MESH_OT_Check_Select_Verts(Operator):
    """Checking Poles"""
    bl_idname = "mesh.check_use_verts"
    bl_label = "Check Distorted Faces"
    
    def execute(self,context):
        custom_rgb = context.scene.check.use_verts_color
        bm = bmesh.from_edit_mesh(bpy.context.edit_object.data)
        check_use_verts = []
        for ele in bm.edges:
            for i in range(2):
                check_use_verts.append(ele.verts[i].index)
        C = Counter(check_use_verts)
        use_verts_count=context.scene.check.use_verts_count
        bm_array = [k for k,v in C.items() if v>=use_verts_count]
        for i, (text, data) in enumerate(info):
                if text.startswith('Use Verts'):
                    info.pop(i)
        if len(bm_array)>0:
            info.append(("Use Verts: %d" % len(bm_array),
                        (bmesh.types.BMVert,bm_array,custom_rgb)))
        report.update(*info)
    
class MESH_OT_Check_Select_Use_Boundary(Operator):

    """Checking degenerate polygons"""
    bl_idname = "mesh.check_select_use_boundary"
    bl_label = "Check Distorted Faces"

    @staticmethod
    def main_check(check,info,bm):
        setup_environment('EDGE')
        custom_rgb = check.use_boundary_color
        bpy.ops.mesh.select_non_manifold(
                extend=False,
                use_wire=False,
                use_boundary=True,
                use_multi_face=False,
                use_non_contiguous=False,
                use_verts=False,
                )
        bm_array = []
        for e in bm.edges:
            if e.select is True:
                bm_array.append(e.index)
        
        for i, (text, data) in enumerate(info):
            if text.startswith('Non-Flat Faces'):
                info.pop(i)
        if len(bm_array)>0:
            edges = array.array('i',bm_array)
            info.append(("Use Boundary: %d" % len(bm_array),(bmesh.types.BMEdge,edges,custom_rgb)))
        report.update(*info)

    
           
class MESH_OT_Check_Loop_Region(Operator):
    bl_idname = "mesh.loop_region"
    bl_label = "Select Loop Inner Region"

    def execute(self, context):
        
        bpy.ops.mesh.loop_to_region()
        return {'FINISHED'}
        
        

class MESH_OT_Check_Flush(Operator):
    bl_idname = "mesh.check_flush_modal_timer"
    bl_label = "Toggle real-time refresh"
   
    _timer = None
   
    def modal(self,context,event):
        scene = context.scene
        check = scene.check
        mesh_check_use = check.mesh_check_use
        if ((context.area.type != 'VIEW_3D') or (not mesh_check_use)):
            self.cancel(context)
            return {'FINISHED'}
        if context.area.type == 'VIEW_3D' and context.active_object.mode == "EDIT" and check.is_real_update == "auto" and mesh_check_use and event.type == 'TIMER':
            get_select_class(self,context)
        return {'PASS_THROUGH'}
        
    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step = 3,window = context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        
    def cancel(self,context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        return {'CANCLE'}

'''Access the data selected by the user'''        
def get_cur_mode_select_data(bm,select_mode_list):
    my_verts=[]
    my_edges=[]
    my_faces=[]
    for select_mode in select_mode_list:
        if select_mode == "VERT":
            my_verts = [v.index for v in bm.verts if v.select == True]
        elif select_mode == "EDGE":
            my_edges = [e.index for e in bm.edges if e.select == True]
        elif select_mode == "FACE": 
            my_faces = [f.index for f in bm.faces if f.select == True]
    return my_verts,my_edges,my_faces



'''Access the objects to be checked'''
def get_select_class(self,context):
    check = context.scene.check
    check_cls = []
    check_cls_execute = []   
    info.clear()
    report.update(*info)
    # bpy.ops.object.mode_set(mode='EDIT')
    me = context.active_object.data
    bm = bmesh.from_edit_mesh(me)
    select_mode_list = list(bm.select_mode)
    
    my_verts,my_edges,my_faces = get_cur_mode_select_data(bm,select_mode_list)

    if check.loose_points:check_cls.append(MESH_OT_Check_LoosePointsSelect)
    if check.loose_edges:check_cls.append(MESH_OT_Check_LooseEdgesSelect)
    if check.loose_edges:check_cls.append(MESH_OT_Check_LooseFacesSelect)
    if check.triangles:check_cls.append(MESH_OT_Check_TirsSelect) 
    if check.use_multi_face :check_cls.append(MESH_OT_Check_Select_Multi_Face)
    if check.use_boundary:check_cls.append(MESH_OT_Check_Select_Use_Boundary)
    if check.intersect:check_cls.append(MESH_OT_Check_Intersections)
    
    if check.degenerate:check_cls_execute.append(MESH_OT_Check_Degenerate)
    if check.ngons:check_cls_execute.append(MESH_OT_Check_NgonsSelect)
    if check.doubles:check_cls_execute.append(MESH_OT_Check_Select_Doubles)
    if check.use_verts:check_cls_execute.append(MESH_OT_Check_Select_Verts)
    if check.distort:check_cls_execute.append(MESH_OT_Check_Distorted)
    if check.face_orientation:check_cls_execute.append(MESH_OT_Check_Face_Orientation)
    
    for cls in check_cls:
        cls.main_check(check,info,bm)    
    for cls in check_cls_execute:
        cls.execute(self,context)
    report.update(*info)
    bpy.ops.mesh.select_all(action='DESELECT')  
    
    '''Reset the set mode and selected data after checking, or the selected data will be disappear when refreshing.'''
    for select_mode in select_mode_list:    
        bpy.ops.mesh.select_mode(type=select_mode)
        if select_mode == "VERT" and len(my_verts)>0:
            bm.verts.ensure_lookup_table()
            for index in my_verts:
                bm.verts[index].select_set(True)                
        elif select_mode == "EDGE" and len(my_edges)>0:
            bm.edges.ensure_lookup_table()
            for index in my_edges:
                bm.edges[index].select_set(True)   
        elif select_mode == "FACE" and len(my_faces)>0:
            bm.faces.ensure_lookup_table()
            for index in my_faces:
                bm.faces[index].select_set(True)   
    bmesh.update_edit_mesh(me, loop_triangles=True)
        
        
class MESH_OT_Check_manual_Flush(Operator):
    bl_idname = "mesh.check_manual_flush"
    bl_label = "Manual refresh"
    
    def execute(self,context):
        check = context.scene.check
        if check.is_real_update == "manual":
            get_select_class(self,context) 
        else:
            bpy.ops.mesh.check_flush_modal_timer()
        return {'FINISHED'}
        

def check_all(self, context):
    scene = bpy.context.scene
    check = scene.check
    mesh_check_use = check.mesh_check_use
    check.doubles = mesh_check_use
    check.loose_points = mesh_check_use
    check.loose_edges = mesh_check_use
    check.loose_faces = mesh_check_use
    check.intersect = mesh_check_use
    check.degenerate = mesh_check_use
    check.distort = mesh_check_use
    check.use_boundary= mesh_check_use
    check.use_multi_face=mesh_check_use
    check.use_verts = mesh_check_use
    check.triangles = mesh_check_use
    check.ngons = mesh_check_use
    MESH_OT_Check_manual_Flush.execute(self, context)


class MESH_OT_Check_Display(Operator):
    """Display Color On/Off"""
    bl_idname = "mesh.show"
    bl_label = "Display hint data manager"
    bl_description = "Main control for enabling or disabling the display of measurements in the viewport"

    _handle = None  # keep function handler

    def execute(self, context):
        scene = bpy.context.scene
        check = scene.check
        is_show_color = check.is_show_color
        if context.area.type == 'VIEW_3D' and is_show_color:
            if context.window_manager.measureit_run_openglt is False:
                if MESH_OT_Check_Display._handle is None:
                    # Enable gl drawing adding handler
                    MESH_OT_Check_Display._handle = SpaceView3D.draw_handler_add(mesh_helpers.draw_callback,(),'WINDOW', 'POST_VIEW')
                    context.window_manager.measureit_run_openglt = True
            else:
                if MESH_OT_Check_Display._handle is not None:
                    bpy.types.SpaceView3D.draw_handler_remove(MESH_OT_Check_Display._handle, 'WINDOW')
                    MESH_OT_Check_Display._handle = None
                    context.window_manager.measureit_run_openglt = False

            return None
        else:
            bpy.types.SpaceView3D.draw_handler_remove(MESH_OT_Check_Display._handle, 'WINDOW')
            MESH_OT_Check_Display._handle = None
            context.window_manager.measureit_run_openglt = False

        return None
        


class MESH_OT_Check_Select_Report(Operator):
    """Select the data associated with this report"""
    bl_idname = "mesh.select_report"
    bl_label = "Select Report"
    bl_options = {'INTERNAL'}

    index: IntProperty()


    _type_to_mode = {
        bmesh.types.BMVert: 'VERT',
        bmesh.types.BMEdge: 'EDGE',
        bmesh.types.BMFace: 'FACE',
        }

    _type_to_attr = {
        bmesh.types.BMVert: "verts",
        bmesh.types.BMEdge: "edges",
        bmesh.types.BMFace: "faces",
        }

    def execute(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        obj = context.edit_object
        info = report.info()
        if self.index == -1:
            return {'FINISHED'}
        text, data = info[self.index]
        bm_type,bm_array,color = data
        if len(bm_array)>0:
            bpy.ops.mesh.select_mode(type=self._type_to_mode[bm_type])
            bm = bmesh.from_edit_mesh(obj.data)
            elems = getattr(bm, MESH_OT_Check_Select_Report._type_to_attr[bm_type])[:]
            try:
                for i in bm_array:
                    elems[i].select_set(True)
            except:
                # possible arrays are out of sync
                self.report({'WARNING'}, "Report is out of date, re-run check")

            # cool, but in fact annoying
            bpy.ops.view3d.view_selected(use_all_regions=False)

        return {'FINISHED'}



