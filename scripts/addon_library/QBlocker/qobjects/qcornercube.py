import bpy
import bmesh
import mathutils
from .qobject import Qobject
from .obj_utils import Create_ScaleMatrix


def GetTransformOffsetH(isCentered):
    if isCentered:
        return mathutils.Matrix.Translation((0.0, 0.0, 0.0))
    else:
        return mathutils.Matrix.Translation((0.0, 0.0, 0.5))


def sign(a):
    return 1 if a > 0 else -1 if a < 0 else 0


# ===== QOBJECT CLASS ===== #
class QCornercube(Qobject):
    basetype = 1

    def copyData(self, _op):
        newQ = QCornercube(_op)
        return newQ

    def CreateQBlock(self):
        qbProps = self.bObject.data.qblock_props
        qbProps.qblockType = 'QCORNERCUBE'
        qbProps.is_centered = self.isCentered
        qbProps.is_smooth = self.isSmooth
        qbProps.is_flat = self.isFlat
        qbProps.size = self.saveSize

    def UpdateMesh(self):
        bmeshNew = bmesh.new()
        if self.isFlat:
            bmesh.ops.create_grid(bmeshNew,
                                  x_segments=1,
                                  y_segments=1,
                                  size=0.5,
                                  matrix=mathutils.Matrix.Translation((0.5, 0.5, 0.0)),
                                  calc_uvs=True)
        else:
            transformS = GetTransformOffsetH(self.isCentered)
            transformS = transformS @ mathutils.Matrix.Translation((0.5, 0.5, 0.0))
            bmesh.ops.create_cube(bmeshNew,
                                  size=1.0,
                                  matrix=transformS,
                                  calc_uvs=True)

        bmeshNew.to_mesh(self.bMesh)
        bmeshNew.free()
        self.bMesh.update()
        bpy.context.view_layer.update()
        bmeshNew.free()

    # set height, update scale
    def UpdateHeight(self, _height):
        self.height = _height
        self.height = _height * 2.0 if self.isCentered else _height
        self.bObject.scale[2] = self.height

    # ===== Object Base Positioning ===== #

    # corner to corner positioning
    def TransformPtoP(self, _matrix):
        self.bObject.location = self.firstPoint
        self.bObject.scale = ((self.secondPoint.x), (self.secondPoint.y), self.height)

    # center position, separated axis
    def TransformCenter(self):
        self.bObject.location = self.firstPoint
        self.bObject.scale = ((self.secondPoint.x), (self.secondPoint.y), self.height)

    # center position, uniform base axis
    def TransformUniformBase(self):
        self.bObject.location = self.firstPoint
        pointXabs = abs(self.secondPoint.x)
        pointYabs = abs(self.secondPoint.y)
        signM = sign(self.secondPoint.x / self.secondPoint.y)
        if pointYabs < pointXabs:
            self.bObject.scale = (self.secondPoint.x, self.secondPoint.x * signM, self.height)
        else:
            self.bObject.scale = (self.secondPoint.y * signM, self.secondPoint.y, self.height)

    # center position, uniform all axis
    def TransformUniformAll(self):
        self.bObject.location = self.firstPoint
        pointXabs = abs(self.secondPoint.x)
        pointYabs = abs(self.secondPoint.y)
        signM = sign(self.secondPoint.x / self.secondPoint.y)
        if pointYabs < pointXabs:
            self.bObject.scale = (self.secondPoint.x, self.secondPoint.x * signM, abs(pointXabs))
        else:
            self.bObject.scale = (self.secondPoint.y * signM, self.secondPoint.y, abs(pointYabs))


# ===== PARAMETRIC UPDATE ===== #
def update_QCornerCube(self, context):
    bmeshNew = bmesh.new()
    mat_scale = Create_ScaleMatrix(self.size)
    mat_scale = mat_scale @ mathutils.Matrix.Translation((0.5, 0.5, 0.0))
    if self.is_flat:
        bmesh.ops.create_grid(bmeshNew,
                              x_segments=1,
                              y_segments=1,
                              size=0.5,
                              matrix=mat_scale,
                              calc_uvs=True)
    else:
        if not self.is_centered:
            mat_scale = mathutils.Matrix.Translation((0.0, 0.0, (self.size[2] / 2.0))) @ mat_scale
        bmesh.ops.create_cube(bmeshNew,
                              size=1.0,
                              matrix=mat_scale,
                              calc_uvs=True)

    bmesh.ops.recalc_face_normals(bmeshNew, faces=bmeshNew.faces)
    bmeshNew.to_mesh(self.id_data)
    bpy.context.view_layer.update()
    bmeshNew.free()


# ===== PARAMETRIC UI ===== #
# No need. same as the cube
