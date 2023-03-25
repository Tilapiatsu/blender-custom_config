import bpy
import bmesh
import mathutils
import math
import numpy


# convertrer operator class
class ConvertToQBlock(bpy.types.Operator):
    """Turn mesh into cylinder"""
    bl_idname = "object.convert_to_qblock"
    bl_label = "Convert to Qblock"
    bl_options = {'REGISTER', 'UNDO'}

    QBTypes = [
        ('NONE', "None", ""),
        ('QCUBE', "Cube", ""),
        ('QCORNERCUBE', "CornerCube", ""),
        ('QCYLINDER', "Cylinder", ""),
        ('QSPHERE', "Sphere", ""),
        ('QSPHERECUBE', "SphereCube", "")
    ]

    # qblock mirrored data properties
    qblockType: bpy.props.EnumProperty(name="QBlock type", items=QBTypes, default='QCUBE')
    is_flat: bpy.props.BoolProperty(name="is_flat", default=False)
    is_centered: bpy.props.BoolProperty(name="is_centered")
    is_smooth: bpy.props.BoolProperty(name="is_smooth")
    size: bpy.props.FloatVectorProperty(name="size", default=(1.0, 1.0, 1.0), precision=3, subtype='XYZ', unit='LENGTH')
    aspect: bpy.props.FloatVectorProperty(name="aspect", default=(1.0, 1.0, 1.0), precision=3, subtype='XYZ')
    radius: bpy.props.FloatProperty(name="radius", default=1.0, min=0.00001, precision=3, unit='LENGTH')
    segments: bpy.props.IntProperty(name="segments", default=16, min=4, max=256)
    depth: bpy.props.FloatProperty(name="depth", default=1.0, precision=3, unit='LENGTH')
    division: bpy.props.IntProperty(name="division", default=4, min=1, max=256)

    origin_bool: bpy.props.BoolProperty(
        name="Origin centered Mesh",
        description="Use origin as the mesh center.",
        default=True
    )

    # draw undo layout
    def draw_cube(self, context):
        layout = self.layout
        layout.prop(self, "is_flat", text="Flat")
        if not self.is_flat:
            layout.prop(self, "is_centered", text="Centered")
            col = layout.column(align=True)
            col.prop(self, "size", text="Scale")
        else:
            col = layout.column(align=True)
            col.label(text="Scale:")
            col.prop(self, "size", text="X", index=0)
            col.prop(self, "size", text="Y", index=1)

    def draw_cylinder(self, context):
        layout = self.layout
        layout.prop(self, "is_flat", text="Flat")
        if not self.is_flat:
            layout.prop(self, "is_centered", text="Centered")
            layout.prop(self, "is_smooth", text="Smooth")
        layout.prop(self, "radius", text="Radius")
        layout.prop(self, "segments", text="Segments")
        if not self.is_flat:
            layout.prop(self, "depth", text="Depth")
        col = layout.column(align=True)
        col.label(text="Aspect:")
        col.prop(self, "aspect", text="X", index=0)
        col.prop(self, "aspect", text="Y", index=1)

    def draw_sphere(self, context):
        layout = self.layout
        layout.prop(self, "is_centered", text="Centered")
        layout.prop(self, "is_smooth", text="Smooth")
        layout.prop(self, "radius", text="Radius")
        layout.prop(self, "segments", text="Segments")
        col = layout.column(align=True)
        col.prop(self, "aspect", text="Aspect")

    def draw_spherecube(self, context):
        layout = self.layout
        layout.prop(self, "is_centered", text="Centered")
        layout.prop(self, "is_smooth", text="Smooth")
        layout.prop(self, "radius", text="Radius")
        layout.prop(self, "division", text="Division")
        col = layout.column(align=True)
        col.prop(self, "aspect", text="Aspect")

    # custom layout to disable elements
    def draw(self, context):
        layout = self.layout
        # qblock parameters
        layout.prop(self, "qblockType", text="Type")
        if self.qblockType == 'QCUBE':
            self.draw_cube(context)
        elif self.qblockType == 'QCORNERCUBE':
            self.draw_cube(context)
        elif self.qblockType == 'QCYLINDER':
            self.draw_cylinder(context)
        elif self.qblockType == 'QSPHERE':
            self.draw_sphere(context)
        elif self.qblockType == 'QSPHERECUBE':
            self.draw_spherecube(context)
        # generator parameters
        # layout.separator()
        # layout.prop(self, "origin_bool")

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
                biggest.x = abs(cornerC[0])
            if abs(cornerC[1]) > abs(biggest.y):
                biggest.y = abs(cornerC[1])
            if abs(cornerC[2]) > abs(biggest.z):
                biggest.z = abs(cornerC[2])
        return biggest

    def execute(self, context):
        Qblock_Data = context.view_layer.objects.active.data.qblock_props
        Qblock_Data.qblockType = self.qblockType
        Qblock_Data.is_flat = self.is_flat
        Qblock_Data.is_centered = self.is_centered
        Qblock_Data.is_smooth = self.is_smooth
        Qblock_Data.size = self.size
        Qblock_Data.aspect = self.aspect
        Qblock_Data.radius = self.radius
        Qblock_Data.segments = self.segments
        Qblock_Data.depth = self.depth
        Qblock_Data.division = self.division
        # if object with radius convert aspect to scale
        if self.qblockType == 'QCYLINDER':
            self.size = self.aspect * self.radius * 2.0
            self.size.z = self.depth
            self.aspect.z = self.depth / self.radius / 2.0
            self.division = self.segments

        # if object without radius, convert size to aspect and depth
        elif self.qblockType == 'QCUBE' or self.qblockType == 'QCORNERCUBE':
            biggest = mathutils.Vector((0.0, 0.0, 0.0))
            if abs(self.size[0]) > abs(biggest.x):
                biggest.x = abs(self.size[0])
            if abs(self.size[1]) > abs(biggest.y):
                biggest.y = abs(self.size[1])
            if abs(self.size[2]) > abs(biggest.z):
                biggest.z = abs(self.size[2])
            maxrad = 1.0
            if biggest.x >= biggest.y:
                maxrad = biggest.x
            else:
                maxrad = biggest.y

            self.aspect = biggest / maxrad
            self.radius = maxrad / 2.0
            self.depth = self.size.z
            self.aspect.z = self.depth / self.radius / 2.0

        # if object sphere
        elif self.qblockType == 'QSPHERE':
            self.size = self.aspect * self.radius * 2.0
            self.depth = self.aspect.z * self.radius * 2.0
            self.division = self.segments
        # if object spherecube
        elif self.qblockType == 'QSPHERECUBE':
            self.size = self.aspect * self.radius * 2.0
            self.depth = self.aspect.z * self.radius * 2.0
            self.segments = self.division

        return {'FINISHED'}

    def invoke(self, context, event):
        active_obj = context.view_layer.objects.active
        # Qblock_Data = context.view_layer.objects.active.data.qblock_props
        self.act_scale = numpy.array(active_obj.scale)
        self.act_dim = numpy.array(active_obj.dimensions)
        self.mesh_scale = (self.act_dim / self.act_scale)
        self.size = self.mesh_scale
        self.bbox = []
        for item in active_obj.bound_box:
            self.bbox.append(mathutils.Vector((item[0], item[1], item[2])))

        # calc aspect and radius for cylinder
        self.biggestrad = mathutils.Vector((0.0, 0.0, 0.0))
        # set radius
        local_rad_max = self.getOSRadius(active_obj)
        maxrad = 1.0
        if local_rad_max.x >= local_rad_max.y:
            maxrad = local_rad_max.x
        else:
            maxrad = local_rad_max.y
        self.biggestrad = local_rad_max
        # set aspect from size
        self.aspect = self.biggestrad / maxrad
        if self.qblockType == 'QCYLINDER':
            self.aspect.z = 1.0
        else:
            self.aspect.z /= 2.0
        self.radius = maxrad
        self.depth = self.mesh_scale[2]

        return self.execute(context)
