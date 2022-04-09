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


import bpy
import os
from bpy.types import Operator,Panel,PropertyGroup,Operator
from bpy.props import BoolProperty,FloatProperty,IntProperty

import bmesh
from ..core import common
from ..core.total_operator import CheckModelTool as CheckModel

blender_version = bool(bpy.app.version >= (2, 80, 0))

class VIEW3D_PT_Check_Model_UI(Panel):
    bl_label = "Object statistics"
    bl_idname = "VIEW3D_PT_Check_Model_UI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI" if blender_version else "TOOLS"
    bl_category = "Object statistics"

    def draw(self,context):
        scene = context.scene
        check = scene.ui_prop
        updata = scene.total_lst

        layout = self.layout
        col = layout.column(align=False)
        col.prop(check,"boolBox")
        row = col.row(align=True)
        row.operator(MESH_OT_CheckModel_UpData.bl_idname,text="Refresh",icon="FILE_REFRESH")
        row.operator(MESH_OT_ShowInfo_UpData.bl_idname,text="Details",icon="INFO")

        label_str = [
                     "Total Count:          ",
                     "Geometries:   ",
                     "Polygons:",
                     "Vertices:",

                     "Objects with Isolated Vertices:",
                     "Isolated Vertices:",
                     "Objects with Isolated Edge:",
                     "Isolated Edge:",
                     "Objects with Isolated Face:",
                     "Isolated Face:",

                     "Objects with Overlapping Vertices:",
                     "Overlapping Vertices:",

                     "Objects with NGons:",
                     "NGons:",

                     "Objects with Overlapping UV Polygons:",
                     "Overlapping UV Polygons:",
                     "Overflowing UV Area:",

                     "Textures:",
                     "Missing Textures:",
                     "Objects with Missing Textures:",
                    ]

        col.prop(check,"boolBox_ob")
        box1 = col.box().grid_flow(align=True,row_major=True,columns=2)
        box1.enabled = check.boolBox_ob

        col.prop(check,"boolBox_loose")
        box2 = col.box().grid_flow(align=True,row_major=True,columns=2)
        box2.enabled = check.boolBox_loose

        col.prop(check,"boolBox_mutl")
        box3 = col.box().grid_flow(align=True,row_major=True,columns=3)
        box3.enabled = check.boolBox_mutl

        col.prop(check,"boolBox_NGons")
        box4 = col.box().grid_flow(align=True,row_major=True,columns=2)
        box4.enabled = check.boolBox_NGons

        col.prop(check,"boolBox_uv")
        box5 = col.box().grid_flow(align=True,row_major=True,columns=3)
        box5.enabled = check.boolBox_uv

        col.prop(check,"boolBox_img")
        box6 = col.box().grid_flow(align=True,row_major=True,columns=3)
        box6.enabled = check.boolBox_img

        for i in range(len(label_str)):
            if i in [0,1,2,3]:
                row = box1.row(align=True).box().row(align=True)
                row.label(text=label_str[i])
                row.label(text=str(updata[0][i]))

            elif i in [4,5,6,7,8,9]:
                row = box2.row(align=True).box().row(align=True)
                row.label(text=label_str[i])
                row.label(text=str(updata[0][i]))

            elif i in [10,11]:
                row = box3.row(align=True).box().row(align=True)
                row.label(text=label_str[i])
                row.label(text=str(updata[0][i]))
                if i == 11:
                    row.prop(check,"threshold_value",text="Threshold")

            elif i in [12,13]:
                row = box4.row(align=True).box().row(align=True)
                row.label(text=label_str[i])
                row.label(text=str(updata[0][i]))
                '''----Start with here'''
                if i == 13:
                    check_mesh = scene.check
                    if check_mesh.ngons:
                        row.prop(check_mesh,"ngons_verts_count",text="Edge Number")
                    else:
                        row.prop(check,"ngons_count",text="Edge Number")
                        
                

            elif i in [14,15,16]:
                row = box5.row(align=True).box().row(align=True)
                row.label(text=label_str[i])
                row.label(text=str(updata[0][i]))

            elif i in [17,18,19]:
                row = box6.row(align=True).box().row(align=True)
                row.label(text=label_str[i])
                row.label(text=str(updata[0][i]))


class MESH_OT_CheckModel_UpData(Operator):
    bl_idname="check_model.updata"
    bl_label = "check_model_updata"

    def execute(self,context):
        scene = context.scene
        check = scene.ui_prop

        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')

        bpy.context.scene.total_lst.clear()
        sc_obs_total = CheckModel().init(mutl_ver_dist=check.threshold_value,
                                         open_ob=check.boolBox_ob,
                                         open_loose=check.boolBox_loose,
                                         open_mutl=check.boolBox_mutl,
                                         open_gnons=check.boolBox_NGons,
                                         open_uv=check.boolBox_uv,
                                         open_img=check.boolBox_img)

        for i in sc_obs_total:
            bpy.context.scene.total_lst.append(i)

        bpy.ops.object.select_all(action='DESELECT')

        return {"FINISHED"}

class MESH_OT_ShowInfo_UpData(Operator):
    bl_idname="show_info.updata"
    bl_label = "ShowInfo"

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=1100)

    def draw(self,context):
        scene = context.scene
        check = scene.ui_prop
        updata = scene.total_lst

        layout = self.layout
        col = layout.column(align=True)

        tab_head = [
                    "Object Name",
                    "Object Location",
                    "Object Rotation",
                    "Object Scale",
                    "Isolated Vertices",
                    "Isolated Edges",
                    "Isolated Faces",
                    "Overlapping Vertices",
                    "NGons",
                    "Overlapping UV Polygons",
                    "UV Area",
                    "UV Overflow",
                    "Missing Textures",
                   ]

        row = col.row(align=True)
        for i in tab_head:
            box = row.box()
            if i == "Object Name":
                box.label(text=i)
                box.scale_x = 450
            else:
                box.scale_x = 10
                box.label(text=i)

        check_data = []
        if check.boolBox:
            check_data = updata[2]
        else:
            check_data = updata[1]

        col = col.column(align=True)
        for item in check_data:
            row = col.row(align=True)
            for j in range(len(item)):
                box = row.box()
                if j == 0:
                    box.label(text=str(item[j]))
                    box.scale_x = 450
                else:
                    box.scale_x = 10
                    box.label(text=str(item[j]))

    def execute(self,context):
        return {"FINISHED"}


class Check_Scene_Props(PropertyGroup):
    boolBox : BoolProperty(name="Display Errors Only", default=True)
    threshold_value: FloatProperty(name="",description="Threshold",subtype="DISTANCE",default=0.0001,min=0.00001,max=10)
    boolBox_ob: BoolProperty(name="Object:",default=True,description="Count objects")
    boolBox_loose : BoolProperty(name="Isolated Elements:",default=True,description="Count the isolated elements")
    boolBox_mutl: BoolProperty(name="Overlapping Vertices:",default=True,description="Count doubles of geometry")
    boolBox_NGons: BoolProperty(name="NGons:",default=True,description="Count the N-gons of geometry")
    boolBox_uv: BoolProperty(name="UV:",default=False,description="Heavy calculations. Off by default.")
    boolBox_img: BoolProperty(name="Images:",default=True,description="Images count")
    '''---Modify--Polygon Edge Count'''
    ngons_count: IntProperty(name="Polygon Edge Count",description="Polygon Edge Count",default = 5,min = 5)