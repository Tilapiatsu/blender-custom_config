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


# Interface for this addon.

from bpy.types import Panel
import bmesh

from ..core import report


class Check_ToolBar:
    bl_label = "Mesh Detection"
    bl_idname = "VIEW3D_PT_check_toolBar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


    _type_to_icon = {
        bmesh.types.BMVert: 'VERTEXSEL',
        bmesh.types.BMEdge: 'EDGESEL',
        bmesh.types.BMFace: 'FACESEL',
        }


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    @staticmethod
    def draw_report(rowsub, context,type):
        """Display Reports"""
        info = report.info()
        text = "0"
        bm_type= bmesh.types.BMFace
        i = -1
        if info:
            # print(info)
            obj = context.active_object
            for i, (text, data) in enumerate(info):
                if obj and text.startswith(type):
                    text=text.split(":")[-1]
                    bm_type, bm_array,color = data
                    i = i;
                    break;
                else:
                    i = -1
                    text = "0"
        rowsub.operator("mesh.select_report",text="Select",icon=Check_ToolBar._type_to_icon[bm_type]).index = i
        rowsub.label(text = text)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        check = scene.check


        col = layout.column()
        row = col.row()

        row.prop(check, "mesh_check_use",text="Mesh Detection")
        if check.is_show_color is True:
            icon = "HIDE_OFF"
        else:
            icon = "HIDE_ON"

        col2 = row.column_flow(columns=3)
        col2.prop(check,"is_show_color",icon= icon)
        col2.prop(check,"is_real_update")
        
        if check.is_real_update == "manual":
            #col2.operator("mesh.check_flush_modal_timer", text="Refresh",icon = "FILE_REFRESH").is_real_check = True
            col2.operator("mesh.check_manual_flush", text="Refresh",icon = "FILE_REFRESH")
        
        box = layout.box()
        box.enabled = check.mesh_check_use

        row = box.row()

        col = row.column()
        col.prop(check, "doubles")
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.doubles == True)
        col2.prop(check, "custom_doubles_points_color", text= "")
        col3 = box.row()
        col3.enabled = (check.doubles == True)
        col3.prop(check, "doubles_threshold_value", text="Threshold")
        Check_ToolBar.draw_report(col2, context,"Double Verts")



        row = box.row()
        col = row.column()
        col.prop(check, "loose_points")
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.loose_points == True)
        col2.prop(check, "custom_loose_points_color", text= "")
        Check_ToolBar.draw_report(col2, context,"Loose_Points")
        
        
        row = box.row()
        col = row.column()
        col.prop(check, "loose_edges")
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.loose_edges == True)
        col2.prop(check, "custom_loose_edges_color", text= "")
        Check_ToolBar.draw_report(col2, context,"Loose_Edges")
        
        
        row = box.row()
        col = row.column()
        col.prop(check, "loose_faces")
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.loose_faces == True)
        col2.prop(check, "custom_loose_faces_color", text= "")
        Check_ToolBar.draw_report(col2, context,"Loose Faces")


        row = box.row()
        col = row.column()
        col.prop(check, "triangles")
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.triangles == True)
        col2.prop(check, "custom_tir_color", text= "")
        Check_ToolBar.draw_report(col2, context,"Triangles")


        row = box.row()
        col = row.column()
        col.prop(check, "ngons")
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.ngons == True)
        col2.prop(check, "custom_ngons_color", text= "")
        col3 = box.row()
        col3.enabled = (check.ngons == True)
        col3.prop(check, "ngons_verts_count", text='Polygon Edge Count')
        Check_ToolBar.draw_report(col2, context,"Ngons")


        row = box.row()
        col = row.column()
        col.prop(check,"face_orientation")
        col2 = row.column_flow(columns=3)
        col2.operator("mesh.normals_consistent",text="Outside").inside=False
        col2.operator("mesh.normals_consistent",text="Inside").inside=True
        subrow = box.row(align=True)
        subrow.prop(check,"show_vertex_normals",text="",icon = "NORMALS_VERTEX")
        subrow.prop(check,"show_split_normals",text="",icon = "NORMALS_VERTEX_FACE")
        subrow.prop(check,"show_face_normals",text="",icon = "NORMALS_FACE")
        subrow.prop(check,"normals_length")

        row = box.row()
        col = row.column()
        col.prop(check,"use_verts",text='Poles')
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.use_verts == True)
        col2.prop(check, "use_verts_color", text="")
        Check_ToolBar.draw_report(col2, context,"Use Verts")
        col3 = box.row()
        col3.enabled = (check.use_verts == True)
        col3.prop(check,"use_verts_count", text='Edge Number for Pole')


        row = box.row()
        col = row.column()
        col.prop(check,"use_multi_face", text='Non Manifold')
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.use_multi_face == True)
        col2.prop(check, "use_multi_face_color")
        Check_ToolBar.draw_report(col2, context,"Use Mult Face")
        col3 = box.column_flow(columns=3)
        col3.label(text=" ")
        col3.operator("mesh.loop_region",text="Select Loop Inner Region",icon="FACESEL")
        col3.label(text=" ")
        


        row = box.row()
        col = row.column()
        col.prop(check,"use_boundary", text='Boundaries')
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.use_boundary == True)
        col2.prop(check, "use_boundary_color", text="")
        Check_ToolBar.draw_report(col2, context,"Use Boundary")


        row = box.row()
        col = row.column()
        col.prop(check,"intersect",text='Intersection')
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.intersect == True)
        col2.prop(check, "intersect_color")
        Check_ToolBar.draw_report(col2, context,"Intersect Face")


        row = box.row()
        col = row.column()
        col.prop(check,"distort",text='Distortion')
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.distort == True)
        col2.prop(check, "distorted_color", text="")
        Check_ToolBar.draw_report(col2, context,"Non-Flat Faces")
        col3 = box.column_flow()
        col3.enabled = (check.distort == True)
        col3.prop(check, "angle_distort", text="Distortion Angle")


        row = box.row()
        col = row.column()
        col.prop(check,"degenerate",text='Degenerate Polygons')
        col2 = row.column_flow(columns=3)
        col2.enabled = (check.degenerate == True)
        col2.prop(check, "degenerate_color", text="")
        Check_ToolBar.draw_report(col2, context,"Zero Faces")
        col3 = box.row()
        col3.enabled = (check.degenerate == True)
        col3.prop(check, "threshold_zero", text="Threshold")

# So we can have a panel in both object mode and editmode
# class VIEW3D_PT_Check_Object(Panel, Check_ToolBar):
    # bl_category = "Mesh Detection"
    # bl_idname = "VIEW3D_PT_check_object"
    # bl_context = "objectmode"


class VIEW3D_PT_Check_Mesh(Panel, Check_ToolBar):
    bl_category = "Mesh Detection"
    bl_idname = "VIEW3D_PT_check_mesh"
    bl_context = "mesh_edit"
