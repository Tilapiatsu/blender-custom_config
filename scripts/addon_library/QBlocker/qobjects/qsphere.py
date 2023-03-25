import bpy
import bmesh
import mathutils
from .qobject import Qobject, GetTransformOffset
from .obj_utils import Create_ScaleMatrix, SetSmoothFaces


# ===== QOBJECT CLASS ===== #
class QSphere(Qobject):
    basetype = 4
    isSmooth = True
    isCentered = True

    def copyData(self, _op):
        newQ = QSphere(_op)
        return newQ

    def GetRadiusAspect(self, size):
        maxv = 0
        for s in size:
            if s > maxv:
                maxv = s
        return (maxv, (size / maxv))

    def CreateQBlock(self):
        qbProps = self.bObject.data.qblock_props
        qbProps.qblockType = 'QSPHERE'
        qbProps.is_centered = self.isCentered
        qbProps.is_smooth = self.isSmooth
        qbProps.segments = self.meshSegments
        radius, aspect = self.GetRadiusAspect(self.saveSize)
        qbProps.aspect = aspect
        qbProps.radius = radius

    def UpdateMesh(self):
        bmeshNew = bmesh.new()
        transformS = GetTransformOffset(self.isCentered)
        bmesh.ops.create_uvsphere(bmeshNew,
                                  u_segments=self.meshSegments,
                                  v_segments=int(self.meshSegments / 2),
                                  radius=1.0,
                                  matrix=transformS,
                                  calc_uvs=True)
        bmeshNew.to_mesh(self.bMesh)
        bmeshNew.free()
        self.bMesh.auto_smooth_angle = 1.386
        self.SetSmoothFaces()
        self.bMesh.update()
        bpy.context.view_layer.update()


# ===== PARAMETRIC UPDATE ===== #
def update_QSphere(self, context):
    bmeshNew = bmesh.new()
    mat_scale = Create_ScaleMatrix(self.aspect)
    if not self.is_centered:
        mat_scale = mathutils.Matrix.Translation((0.0, 0.0, (self.aspect[2]) * self.radius)) @ mat_scale
    bmesh.ops.create_uvsphere(bmeshNew,
                              u_segments=self.segments,
                              v_segments=int(self.segments / 2),
                              radius=self.radius,
                              matrix=mat_scale,
                              calc_uvs=True)

    bmesh.ops.recalc_face_normals(bmeshNew, faces=bmeshNew.faces)
    bmeshNew.to_mesh(self.id_data)
    if self.is_smooth:
        self.id_data.auto_smooth_angle = 1.386
        SetSmoothFaces(self.id_data)
    bpy.context.view_layer.update()
    bmeshNew.free()


# ===== PARAMETRIC UI ===== #
def draw_sphere(self, context):
    layout = self.layout
    Qblock_Data = context.object.data.qblock_props
    layout.prop(Qblock_Data, "is_centered", text="Centered")
    layout.prop(Qblock_Data, "is_smooth", text="Smooth")
    layout.prop(Qblock_Data, "radius", text="Radius")
    layout.prop(Qblock_Data, "segments", text="Segments")
    col = layout.column(align=True)
    col.prop(Qblock_Data, "aspect", text="Aspect")
