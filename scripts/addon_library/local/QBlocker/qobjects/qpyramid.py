import bpy
import bmesh
import mathutils
from .qobject import Qobject, GetTransformOffset
from .obj_utils import Create_ScaleMatrix


Pverts = [[-1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [1.0, 1.0, -1.0], [1.0, -1.0, -1.0], [0, 0, 1.0]]
Pfaces = [[0, 1, 2, 3], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]


class Qpyramid(Qobject):
    basetype = 1

    def copyData(self, _op):
        newQ = Qpyramid(_op)
        return newQ

    def CreateQBlock(self):
        qbProps = self.bObject.data.qblock_props
        qbProps.qblockType = 'QPYRAMID'
        qbProps.is_centered = self.isCentered
        qbProps.size = self.saveSize * 2.0

    def UpdateMesh(self):
        transformS = GetTransformOffset(self.isCentered)
        bvertList = []
        bmeshNew = bmesh.new()
        for newvert in Pverts:
            actVert = bmeshNew.verts.new(newvert)
            bvertList.append(actVert)
        for newface in Pfaces:
            bvseq = []
            for vi in newface:
                bvseq.append(bvertList[vi])
            bmeshNew.faces.new(bvseq)

        bmeshNew.to_mesh(self.bMesh)
        self.bMesh.transform(transformS)
        self.bMesh.update()
        bpy.context.view_layer.update()


# ===== PARAMETRIC UPDATE ===== #
def update_QPyramid(self, context):
    bmeshNew = bmesh.new()
    mat_scale = Create_ScaleMatrix(self.size / 2.0)

    if not self.is_centered:
        mat_scale = mathutils.Matrix.Translation((0.0, 0.0, (self.size[2] / 2.0))) @ mat_scale

    bvertList = []
    for newvert in Pverts:
        actVert = bmeshNew.verts.new(newvert)
        bvertList.append(actVert)
    for newface in Pfaces:
        bvseq = []
        for vi in newface:
            bvseq.append(bvertList[vi])
        bmeshNew.faces.new(bvseq)

    bmesh.ops.recalc_face_normals(bmeshNew, faces=bmeshNew.faces)
    bmeshNew.to_mesh(self.id_data)
    self.id_data.transform(mat_scale)
    bpy.context.view_layer.update()
    bmeshNew.free()


# ===== PARAMETRIC UI ===== #
def draw_pyramid(self, context):
    layout = self.layout
    Qblock_Data = context.object.data.qblock_props
    layout.prop(Qblock_Data, "is_centered", text="Centered")
    col = layout.column(align=True)
    col.prop(Qblock_Data, "size", text="Scale")
