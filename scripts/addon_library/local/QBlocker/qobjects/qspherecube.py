import bpy
import bmesh
import mathutils
import math
from .qobject import Qobject, GetTransformOffset
from .obj_utils import Create_ScaleMatrix, SetSmoothFaces


# ===== QOBJECT CLASS ===== #
class QSphereCube(Qobject):
    basetype = 4
    meshtype = 'QSPHERECUBE'
    isSmooth = True
    isCentered = True
    meshSegments = 4

    def copyData(self, _op):
        newQ = QSphereCube(_op)
        return newQ

    def GetRadiusAspect(self, size):
        maxv = 0
        for s in size:
            if s > maxv:
                maxv = s
        return (maxv, (size / maxv))

    def CreateQBlock(self):
        qbProps = self.bObject.data.qblock_props
        qbProps.qblockType = self.meshtype
        qbProps.is_centered = self.isCentered
        qbProps.is_smooth = self.isSmooth
        qbProps.division = self.meshSegments
        radius, aspect = self.GetRadiusAspect(self.saveSize)
        qbProps.aspect = aspect
        qbProps.radius = radius

    def UpdateMesh(self):
        bmeshNew = bmesh.new()
        transformS = GetTransformOffset(self.isCentered)
        bmesh.ops.create_cube(bmeshNew,
                              size=2.0,
                              matrix=transformS,
                              calc_uvs=True)

        # subdivide cube
        bmesh.ops.subdivide_edges(bmeshNew, edges=bmeshNew.edges, cuts=self.meshSegments, use_grid_fill=True)

        # spherify vertices
        radian = math.radians(45)
        for vert in bmeshNew.verts:
            pos = vert.co
            vertXtan = math.tan(pos.x * radian)
            vertYtan = math.tan(pos.y * radian)
            vertZtan = math.tan(pos.z * radian)
            posT = mathutils.Vector((vertXtan, vertYtan, vertZtan))
            posT = posT.normalized()
            vert.co = posT

        bmeshNew.to_mesh(self.bMesh)
        bmeshNew.free()
        self.bMesh.auto_smooth_angle = 1.386
        self.SetSmoothFaces()
        self.bMesh.update()
        bpy.context.view_layer.update()


# ===== PARAMETRIC UPDATE ===== #
def update_QSphereCube(self, context):
    bmeshNew = bmesh.new()
    mat_scale = Create_ScaleMatrix(self.aspect)
    if not self.is_centered:
        mat_scale = mathutils.Matrix.Translation((0.0, 0.0, (self.aspect[2]) * self.radius)) @ mat_scale

    # create cube data
    bmesh.ops.create_cube(bmeshNew,
                          size=2.0,
                          matrix=mathutils.Matrix(),
                          calc_uvs=True)
    # subdivide
    bmesh.ops.subdivide_edges(bmeshNew, edges=bmeshNew.edges, cuts=self.division, use_grid_fill=True)

    # spherify vertices
    radian = math.radians(45)
    for vert in bmeshNew.verts:
        pos = vert.co
        vertXtan = math.tan(pos.x * radian)
        vertYtan = math.tan(pos.y * radian)
        vertZtan = math.tan(pos.z * radian)
        posT = mathutils.Vector((vertXtan, vertYtan, vertZtan))
        posT = posT.normalized() * self.radius
        vert.co = posT

    # transform aspect and centered after spherify
    bmesh.ops.transform(bmeshNew, matrix=mat_scale, verts=bmeshNew.verts)

    bmesh.ops.recalc_face_normals(bmeshNew, faces=bmeshNew.faces)
    bmeshNew.to_mesh(self.id_data)
    if self.is_smooth:
        self.id_data.auto_smooth_angle = 1.386
        SetSmoothFaces(self.id_data)
    bpy.context.view_layer.update()
    bmeshNew.free()


# ===== PARAMETRIC UI ===== #
def draw_spherecube(self, context):
    layout = self.layout
    Qblock_Data = context.object.data.qblock_props
    layout.prop(Qblock_Data, "is_centered", text="Centered")
    layout.prop(Qblock_Data, "is_smooth", text="Smooth")
    layout.prop(Qblock_Data, "radius", text="Radius")
    layout.prop(Qblock_Data, "division", text="Division")
    col = layout.column(align=True)
    col.prop(Qblock_Data, "aspect", text="Aspect")
