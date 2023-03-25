import bpy
# import mathutils
# import bmesh
# import math
from .qobjects.qcube import update_QCube, draw_cube
from .qobjects.qcornercube import update_QCornerCube
from .qobjects.qcylinder import update_QCylinder, draw_cylinder
from .qobjects.qsphere import update_QSphere, draw_sphere
from .qobjects.qspherecube import update_QSphereCube, draw_spherecube
from .qobjects.qpyramid import update_QPyramid, draw_pyramid
from .qobjects.qtorus import update_QTorus, draw_torus


def draw_plane(self, context):
    layout = self.layout
    layout.label(text="Plane merged into Cube with the Flat option.")


def draw_circle(self, context):
    layout = self.layout
    layout.label(text="Circle merged into Cylinder with the Flat option.")


def update_QObject(self, context):
    current_mode = context.object.mode
    # update mesh only in object mode
    if current_mode == 'OBJECT':
        Qblock_Data = context.object.data.qblock_props
        if Qblock_Data.qblockType == 'QCUBE':
            update_QCube(self, context)
        if Qblock_Data.qblockType == 'QCORNERCUBE':
            update_QCornerCube(self, context)
        if Qblock_Data.qblockType == 'QCYLINDER':
            update_QCylinder(self, context)
        if Qblock_Data.qblockType == 'QSPHERE':
            update_QSphere(self, context)
        if Qblock_Data.qblockType == 'QSPHERECUBE':
            update_QSphereCube(self, context)
        if Qblock_Data.qblockType == 'QPYRAMID':
            update_QPyramid(self, context)
        if Qblock_Data.qblockType == 'QTORUS':
            update_QTorus(self, context)


class QBlockProperties(bpy.types.PropertyGroup):
    QBTypes = [
        ('NONE', "None", ""),
        ('QCUBE', "Cube", ""),
        ('QCORNERCUBE', "CornerCube", ""),
        ('QPLANE', "Plane", ""),
        ('QCYLINDER', "Cylinder", ""),
        ('QCIRCLE', "Circle", ""),
        ('QSPHERE', "Sphere", ""),
        ('QSPHERECUBE', "SphereCube", ""),
        ('QPYRAMID', "Pyramid", ""),
        ('QTORUS', "Torus", "")
    ]

    qblockType: bpy.props.EnumProperty(name="QBlock type", items=QBTypes, default='NONE', update=update_QObject)
    is_flat: bpy.props.BoolProperty(name="is_flat", update=update_QObject)
    is_centered: bpy.props.BoolProperty(name="is_centered", update=update_QObject)
    is_smooth: bpy.props.BoolProperty(name="is_smooth", update=update_QObject)
    size: bpy.props.FloatVectorProperty(name="size", default=(1.0, 1.0, 1.0), precision=3, subtype='XYZ', unit='LENGTH', update=update_QObject)
    aspect: bpy.props.FloatVectorProperty(name="aspect", default=(1.0, 1.0, 1.0), precision=3, subtype='XYZ', update=update_QObject)
    radius: bpy.props.FloatProperty(name="radius", default=1.0, min=0.00001, precision=3, unit='LENGTH', update=update_QObject, options={'ANIMATABLE'})
    segments: bpy.props.IntProperty(name="segments", default=16, min=4, max=256, update=update_QObject, options={'ANIMATABLE'})
    depth: bpy.props.FloatProperty(name="depth", default=1.0, precision=3, unit='LENGTH', update=update_QObject)
    division: bpy.props.IntProperty(name="division", default=4, min=1, max=256, update=update_QObject)


class MESH_PT_QblockPanel(bpy.types.Panel):
    bl_idname = "DATA_PT_QblockPanel"
    bl_label = "QBlock Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (context.object.type == 'MESH')

    def draw(self, context):
        layout = self.layout
        Qblock_Data = context.object.data.qblock_props
        layout.prop(Qblock_Data, "qblockType", text="Type")
        current_mode = context.object.mode
        if current_mode == 'OBJECT':
            if Qblock_Data.qblockType == 'QCUBE':
                draw_cube(self, context)
            if Qblock_Data.qblockType == 'QCORNERCUBE':
                draw_cube(self, context)
            if Qblock_Data.qblockType == 'QPLANE':
                draw_plane(self, context)
            if Qblock_Data.qblockType == 'QCYLINDER':
                draw_cylinder(self, context)
            if Qblock_Data.qblockType == 'QCIRCLE':
                draw_circle(self, context)
            if Qblock_Data.qblockType == 'QSPHERE':
                draw_sphere(self, context)
            if Qblock_Data.qblockType == 'QSPHERECUBE':
                draw_spherecube(self, context)
            if Qblock_Data.qblockType == 'QPYRAMID':
                draw_pyramid(self, context)
            if Qblock_Data.qblockType == 'QTORUS':
                draw_torus(self, context)
        else:
            layout.label(text="Need to be in object mode.")
