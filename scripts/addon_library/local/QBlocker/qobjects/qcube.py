import bpy
import bmesh
import mathutils
from .qobject import Qobject, GetTransformOffset
from .obj_utils import Create_ScaleMatrix


# ===== QOBJECT CLASS ===== #
class Qcube(Qobject):
    basetype = 1

    def copyData(self, _op):
        newQ = Qcube(_op)
        return newQ

    def CreateQBlock(self):
        qbProps = self.bObject.data.qblock_props
        qbProps.qblockType = 'QCUBE'
        qbProps.is_centered = self.isCentered
        qbProps.is_smooth = self.isSmooth
        qbProps.is_flat = self.isFlat
        qbProps.size = self.saveSize * 2.0

    def UpdateMesh(self):
        bmeshNew = bmesh.new()
        if self.isFlat:
            bmesh.ops.create_grid(bmeshNew,
                                  x_segments=1,
                                  y_segments=1,
                                  size=1.0,
                                  matrix=mathutils.Matrix.Translation((0.0, 0.0, 0.0)),
                                  calc_uvs=True)
        else:
            transformS = GetTransformOffset(self.isCentered)
            bmesh.ops.create_cube(bmeshNew,
                                  size=2.0,
                                  matrix=transformS,
                                  calc_uvs=True)

        bmeshNew.to_mesh(self.bMesh)
        bmeshNew.free()
        self.bMesh.update()
        bpy.context.view_layer.update()


# ===== PARAMETRIC UPDATE ===== #
def update_QCube(self, context):
    bmeshNew = bmesh.new()
    mat_scale = Create_ScaleMatrix(self.size)
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
def draw_cube(self, context):
    layout = self.layout
    Qblock_Data = context.object.data.qblock_props
    layout.prop(Qblock_Data, "is_flat", text="Flat")
    if not Qblock_Data.is_flat:
        layout.prop(Qblock_Data, "is_centered", text="Centered")
        col = layout.column(align=True)
        col.prop(Qblock_Data, "size", text="Scale")
    else:
        col = layout.column(align=True)
        col.label(text="Scale:")
        col.prop(Qblock_Data, "size", text="X", index=0)
        col.prop(Qblock_Data, "size", text="Y", index=1)
