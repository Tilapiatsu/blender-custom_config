# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Copyright (C) 2020 Wheatfield Media INC
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


bl_info = {
    "name": "CheckToolBox_v1_2",
    "author": "Wheatfield Media INC",
    "blender": (2, 80, 0),
    "location": "3D View > Toolbox",
    "description": "Check for 3D model",
    "category": "Mesh",
    }


from .ui import total_ui

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    # importlib.reload(operators)
    # importlib.reload(mesh_helpers)

else:
    import math

    import bpy
    from bpy.props import (
            StringProperty,
            BoolProperty,
            FloatProperty,
            EnumProperty,
            PointerProperty,
            FloatVectorProperty,
            IntProperty,
            CollectionProperty,
            )
    from bpy.types import (
            AddonPreferences,
            PropertyGroup,
            )

    from .core import (
            operators,
            )
    from .ui import (
            ui,
            )

class Check_Scene_Props(PropertyGroup):


    is_real_update:bpy.props.EnumProperty(
        name = "",
        description = "Toggle real-time refresh",
        items =(
            ("manual"," Manual refresh",""),
            ("auto","Real-time refresh",""),
        ),
        update = operators.MESH_OT_Check_manual_Flush.execute
    )
    
      
    mesh_check_use:BoolProperty(
            name = "Mesh Detection",
            description = "Mesh Detection On/Off",
            default=False,
            update = operators.check_all
            )


    is_show_color:BoolProperty(
            name = "Display Color",
            description = "Display Color On/Off",
            default=False,
            update = operators.MESH_OT_Check_Display.execute
            )

    loose_points:BoolProperty(
            name = "Isolated Edges",
            description = "Detect isolated vertices in active objects",
            default=False,
            )
            
    custom_loose_points_color:FloatVectorProperty(
            name = "",
            description = "Custom isolated vertex color",
            min=0.0,
            max=1.0,
            default=(0.42, 0.65, 0.98),
            subtype='COLOR',
            )
            
    loose_edges:BoolProperty(
            name = "Isolated Edges",
            description = "Detect isolated edges in active objects",
            default=False,
            )
    custom_loose_edges_color:FloatVectorProperty(
            name = "",
            description = "Custom isolated edge color",
            min=0.0,
            max=1.0,
            default=(0, 0.97, 0.98),
            subtype='COLOR',
            )
            
    loose_faces:BoolProperty(
            name = "Isolated Faces",
            description = "Detect isolated faces in active objects",
            default=False,
            )
    custom_loose_faces_color:FloatVectorProperty(
            name = "",
            description = "Custom isolated face color",
            min=0.0,
            max=1.0,
            default=(0, 0.47, 0.87),
            subtype='COLOR',
            )
            
    doubles: BoolProperty(
            name = "Doubles",
            description = "Detect Doubles",
            default=False,
            )

    custom_doubles_points_color: FloatVectorProperty(
            name = "",
            description = "Custom color for the coincidence points",
            min=0.0,
            max=1.0,
            default=(0, 0.0077525, 1),
            subtype='COLOR',
            )

    doubles_threshold_value: FloatProperty(
        name="Threshold",
        description="Set double threshold",
        default=0.0001,
        step = 1,
        precision = 5,
        min=0.00001,max=10,
        update = operators.MESH_OT_Check_Select_Doubles.execute,
    )

    face_orientation: BoolProperty(
            name = "Face Orientation",
            description = "Display face orientation",
            default=False,
            update = operators.MESH_OT_Check_Face_Orientation.execute,
            )
                       
    show_vertex_normals: BoolProperty(
            name = "Display Vertex Normal",
            description = "Display vertex normals as lines",
            default=False,
            update = operators.MESH_OT_Check_Face_Orientation.execute,
            )
            
    show_split_normals: BoolProperty(
            name = "Display Split Normal",
            description = "Display vertex-per-face normals as lines",
            default=False,
            update = operators.MESH_OT_Check_Face_Orientation.execute,
            )
            
    show_face_normals: BoolProperty(
            name = "Display Normal",
            description = "Display face normals as lines",
            default=False,
            update = operators.MESH_OT_Check_Face_Orientation.execute,
            )
            
    normals_length: FloatProperty(
            name = "Size",
            description = "Display size of the normals in the 3D View",
            min = 0.01,
            soft_min = 0.01,
            soft_max = 2.00,
            default = 0.5,
            update = operators.MESH_OT_Check_Face_Orientation.execute,
            )
            
    triangles: BoolProperty(
            name = " Triangles",
            description = "Detect the triangles of the active object",
            default=False,
            )
            
    custom_tir_color: FloatVectorProperty(
            name = "",
            description = "Custom triangle color",
            min=0.0,
            max=1.0,
            default=(1, 0.75, 0),
            subtype='COLOR',
            )
            
    ngons: BoolProperty(
            name = "Polygons",
            description = "Detect the polygons of the active object",
            default=False,
            )
            
    custom_ngons_color: FloatVectorProperty(
            name = "",
            description = "Custom Polygons color",
            min=0.0,
            max=1.0,
            default=(0.98, 0.5, 0.2),
            subtype='COLOR',
            )
            
    ngons_verts_count: IntProperty(
        name="Polygon Edge Count",
        description="Polygon Edge Count",
        default = 5,
        min = 5,
        update = operators.MESH_OT_Check_NgonsSelect.execute,
    )

    threshold_zero: FloatProperty(
        name="Threshold",
        description="Degenerate Polygons Threshold",
        default=0.0001,
        precision=5,
        min=0.0, max=0.2,
        update = operators.MESH_OT_Check_Degenerate.execute,
    )

    angle_distort: FloatProperty(
        name="Angle",
        description="Limit for checking distorted faces",
        subtype='ANGLE',
        default=math.radians(45.0),
        min=0.0, max=math.radians(180.0),
        update = operators.MESH_OT_Check_Distorted.execute,
    )

    distort:BoolProperty(
        name="Distortion",
        description="The vertices on a polygon are not laid on one plane",
        default=False,
    )

    intersect:BoolProperty(
        name="Intersection",
        description="Two faces intersect each other.",
        default=False,
    )
    degenerate:BoolProperty(
        name="Degenerate Polygons",
        description="Polygons with zero area",
        default=False,
    )
    use_verts: BoolProperty(
        name="Poles",
        description="Vertices,Vertices connecting multiple face",
        default=False,
    )
    use_verts_count: IntProperty(
        name="Edge Number for Pole",
        description="Max Edge Number of Pole",
        default=6,
        min=0,
        update = operators.MESH_OT_Check_Select_Verts.execute,
    )
    use_boundary: BoolProperty(
        name="Boundary",
        description="Boundary edges（Edges only incident to one face.）",
        default=False,
    )
    use_multi_face: BoolProperty(
        name="Polygon(non-manifold)",
        description="Edges shared by 3+ faces ",
        default=False,
    )
    intersect_color: FloatVectorProperty(
        name="",
        description=("select intersect_color "),
        precision=4, step=0.01, min=0,
        default=(0.96, 0.25, 0.006),subtype='COLOR')

    distorted_color: FloatVectorProperty(
        name="",
        description=("select intersect_color "),
        precision=4, step=0.01, min=0,
        default=(0.97, 0.26, 0.28), subtype='COLOR')

    degenerate_color: FloatVectorProperty(
        name="",
        description=("select intersect_color "),
        precision=4, step=0.01, min=0,
        default=(0.96, 0.9, 0.3), options={'ANIMATABLE'}, subtype='COLOR')

    use_multi_face_color: FloatVectorProperty(
        name="",
        description=("select intersect_color "),
        precision=4, step=0.01, min=0, #max=inf, soft_max=1,
        default=(0.88, 0.056, 0.072), options={'ANIMATABLE'}, subtype='COLOR')

    use_verts_color: FloatVectorProperty(
        name="",
        description=("select intersect_color "),
        precision=4, step=0.01, min=0,
        default=(0.4, 0.4, 0.93), subtype='COLOR')

    use_boundary_color: FloatVectorProperty(
        name="",
        description=("select intersect_color "),
        precision=4, step=0.01, min=0,
        default=(0.07, 1, 0.25), subtype='COLOR')

classes = (
    # ui.VIEW3D_PT_Check_Object,
    ui.VIEW3D_PT_Check_Mesh,

    operators.MESH_OT_Check_Face_Orientation,
    operators.MESH_OT_Recalculate_Normals,
    operators.MESH_OT_Check_Degenerate,
    operators.MESH_OT_Check_Distorted,
    operators.MESH_OT_Check_Intersections,
    operators.MESH_OT_Check_Select_Multi_Face,
    operators.MESH_OT_Check_Select_Report,
    operators.MESH_OT_Check_Select_Doubles,
    operators.MESH_OT_Check_LoosePointsSelect,
    operators.MESH_OT_Check_LooseEdgesSelect,
    operators.MESH_OT_Check_LooseFacesSelect,
    operators.MESH_OT_Check_NgonsSelect,
    operators.MESH_OT_Check_TirsSelect,
    operators.MESH_OT_Check_Display,
    operators.MESH_OT_Check_Select_Use_Boundary,
    operators.MESH_OT_Check_Select_Verts,
    operators.MESH_OT_Check_Loop_Region,
    operators.MESH_OT_Check_Flush,
    operators.MESH_OT_Check_manual_Flush,
    Check_Scene_Props,

    total_ui.VIEW3D_PT_Check_Model_UI,
    total_ui.MESH_OT_ShowInfo_UpData,
    total_ui.MESH_OT_CheckModel_UpData,
    total_ui.Check_Scene_Props,

)




addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.check = PointerProperty(type=Check_Scene_Props)
    wmt = bpy.types.WindowManager
    wmt.measureit_run_openglt = BoolProperty(
            name = "Display",
            description = "Display area color",
            default=False,)
  
    bpy.types.Scene.ui_prop = PointerProperty(type=total_ui.Check_Scene_Props)
    bpy.types.Scene.total_lst = [[i * 0 for i in range(1,40)],[],[]]


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.check
    del bpy.types.Scene.ui_prop
    del bpy.types.Scene.total_lst

