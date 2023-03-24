import bpy
import bmesh
import mathutils
import math
import numpy


class Turn_Sphere(bpy.types.Operator):
    """Turn mesh into cylinder"""
    bl_idname = "object.turn_to_cylinder"
    bl_label = "Turn to cylinder"
    bl_options = {'REGISTER', 'UNDO'}

    segments_int : bpy.props.IntProperty(
        name="Segments",
        description="Segments of the cylinder",
        min=4,
        max=128,
        default=16
    )

    origin_bool : bpy.props.BoolProperty(
        name="Origin centered",
        description="Use origin as the mesh center.",
        default = True
    )

    bottom_origin_bool : bpy.props.BoolProperty(
        name="Origin at the bottom",
        description="Use the origin as the bottom of the mesh.",
        default = False
    )

    uniform_bool : bpy.props.BoolProperty(
        name="Uniform radius",
        description="Use the wider diameter only.",
        default = False
    )

    radius_bool : bpy.props.BoolProperty(
        name="Use custom radius",
        description="Use user defined radius.",
        default = False
    )

    radius_float : bpy.props.FloatProperty(
        name="Radius",
        description="Radius of the cylinder",
        min=0.00001,
        default=1.0
    )

    # custom layout to disable elements
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        layout.prop(self, "segments_int")
        layout.prop(self, "origin_bool")
        layout.prop(self, "bottom_origin_bool")
        layout.separator()
        layout.prop(self, "uniform_bool")
        row1 = layout.row()   
        row1.prop(self, "radius_bool")
        row1.active = False
        row2 = layout.row()   
        row2.prop(self, "radius_float")
        row2.active = False

        if self.uniform_bool:
            row1.active = True
            if self.radius_bool:    
                row2.active = True


    def getMeshOScenter(self, obj):
        bbox = obj.bound_box
        sum = mathutils.Vector((0.0, 0.0, 0.0))
        for corner in bbox:
            sum += mathutils.Vector((corner))
        return (sum / 8)

    def getMeshRadius(self, obj, center):
        biggest = mathutils.Vector((0.0, 0.0, 0.0))
        for corner in self.bbox:
            cornerC = mathutils.Vector(corner) - center
            if abs(cornerC[0]) > abs(biggest.x):
                biggest.x = cornerC[0]
            if abs(cornerC[1]) > abs(biggest.y):
                biggest.y = cornerC[1]
            if abs(cornerC[2]) > abs(biggest.z):
                biggest.z = cornerC[2]
        return biggest

    def getOSRadius(self, obj):
        biggest = mathutils.Vector((0.0, 0.0, 0.0))
        for cornerC in self.bbox:
            if abs(cornerC[0]) > abs(biggest.x):
                biggest.x = cornerC[0]
            if abs(cornerC[1]) > abs(biggest.y):
                biggest.y = cornerC[1]
            if abs(cornerC[2]) > abs(biggest.z):
                biggest.z = cornerC[2]
        return biggest
      
    def execute(self, context):
        # active object
        active_obj = context.view_layer.objects.active
        mesh_scale = (self.act_dim / self.act_scale) / 2.0
        # origin centered
        if self.origin_bool:
            # loc matrix
            mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
            biggestrad = self.getOSRadius(active_obj)
            # uniform radius
            if self.uniform_bool:   
                if abs(biggestrad.x * self.act_scale[0]) >= abs(biggestrad.y * self.act_scale[1]):
                    biggestrad.y = biggestrad.x * (self.act_scale[0] / self.act_scale[1])
                else:
                    biggestrad.x = biggestrad.y * (self.act_scale[1] / self.act_scale[0])
                if self.radius_bool:
                    height = (self.bbox[1][2] - self.bbox[0][2]) / 2.0
                    mesh_scale = mathutils.Vector((self.radius_float / self.act_scale[0], self.radius_float / self.act_scale[1], height))
                else:
                    mesh_scale = biggestrad  
            else:
                biggestrad.y = biggestrad.y * (self.act_scale[0] / self.act_scale[1])
                biggestrad.x = biggestrad.x * (self.act_scale[1] / self.act_scale[0])
                mesh_scale = biggestrad  
        # mesh volume centered
        else:      
            # loc matrix
            center = self.getMeshOScenter(active_obj)
            mat_loc = mathutils.Matrix.Translation(center)
            # uniform radius
            if self.uniform_bool:
                biggestrad = self.getMeshRadius(active_obj, center)
                if abs(biggestrad.x * self.act_scale[0]) >= abs(biggestrad.y * self.act_scale[1]):
                    biggestrad.y = biggestrad.x * (self.act_scale[0] / self.act_scale[1])
                else:
                    biggestrad.x = biggestrad.y * (self.act_scale[1] / self.act_scale[0])
                if self.radius_bool:
                    mesh_scale = mathutils.Vector((self.radius_float / self.act_scale[0], self.radius_float / self.act_scale[1], biggestrad[2]))
                else:
                    mesh_scale = biggestrad

        
        # create mesh matrix
        transM_X = mathutils.Matrix.Scale(mesh_scale[0], 4, (1.0, 0.0, 0.0))
        transM_Y = mathutils.Matrix.Scale(mesh_scale[1], 4, (0.0, 1.0, 0.0))
        transM_Z = mathutils.Matrix.Scale(mesh_scale[2], 4, (0.0, 0.0, 1.0))
        # origin at the bottom
        if self.bottom_origin_bool:
            height = (self.bbox[1][2] - self.bbox[0][2]) / 2.0
            matOffset = mathutils.Matrix.Translation( mathutils.Vector((0, 0, height)))
            mat_loc = mat_loc @ matOffset

        transMatrix = mat_loc @ transM_X @ transM_Y @ transM_Z
        # create cylinder bmesh
        bmeshNew = bmesh.new()
        bmesh.ops.create_cone(bmeshNew,
                                    segments=self.segments_int,
                                    cap_ends=True,
                                    cap_tris=False,
                                    diameter1=1.0,
                                    diameter2=1.0,
                                    depth=2.0,
                                    matrix=transMatrix, 
                                    calc_uvs=True)
        # apply mesh to active object
        bmeshNew.to_mesh(active_obj.data)
        active_obj.data.update()
        bpy.context.view_layer.update()
        bmeshNew.free()

        return {'FINISHED'}

    def invoke(self, context, event):
        active_obj = context.view_layer.objects.active
        self.act_scale = numpy.array(active_obj.scale)
        self.act_dim = numpy.array(active_obj.dimensions)
        #self.bbox = active_obj.bound_box
        self.bbox = []
        for item in active_obj.bound_box: self.bbox.append(mathutils.Vector((item[0],item[1],item[2])))
        return self.execute(context)




