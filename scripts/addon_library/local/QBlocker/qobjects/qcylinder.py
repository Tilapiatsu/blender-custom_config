import bpy
import bmesh
import mathutils
from .qobject import Qobject, GetTransformOffset
from .obj_utils import Create_ScaleMatrix, SetSmoothFaces


# ===== QOBJECT CLASS ===== #
class QCylinder(Qobject):
    basetype = 3
    isSmooth = True

    def copyData(self, _op):
        newQ = QCylinder(_op)
        return newQ

    def GetRadiusAspect(self, size):
        maxv = 0
        if size[0] > size[1]:
            maxv = size[0]
        else:
            maxv = size[1]
        return (maxv, (size / maxv))

    def CreateQBlock(self):
        qbProps = self.bObject.data.qblock_props
        qbProps.qblockType = 'QCYLINDER'
        qbProps.is_centered = self.isCentered
        qbProps.is_smooth = self.isSmooth
        qbProps.depth = self.saveSize[2] * 2.0
        qbProps.is_flat = self.isFlat
        qbProps.segments = self.meshSegments
        radius, aspect = self.GetRadiusAspect(self.saveSize)
        qbProps.aspect[0] = aspect[0]
        qbProps.aspect[1] = aspect[1]
        qbProps.aspect[2] = 1.0
        qbProps.radius = radius

    def UpdateMesh(self):
        bmeshNew = bmesh.new()
        if self.isFlat:
            bmesh.ops.create_circle(bmeshNew,
                                    segments=self.meshSegments,
                                    cap_ends=True,
                                    cap_tris=False,
                                    radius=1.0,
                                    matrix=mathutils.Matrix.Translation((0.0, 0.0, 0.0)),
                                    calc_uvs=True)
        else:
            transformS = GetTransformOffset(self.isCentered)
            bmesh.ops.create_cone(bmeshNew,
                                  segments=self.meshSegments,
                                  cap_ends=True,
                                  cap_tris=False,
                                  radius1=1.0,
                                  radius2=1.0,
                                  depth=2.0,
                                  matrix=transformS,
                                  calc_uvs=True)
        bmeshNew.to_mesh(self.bMesh)
        bmeshNew.free()
        self.bMesh.auto_smooth_angle = 1.386
        self.SetSmoothFaces()
        self.bMesh.update()
        bpy.context.view_layer.update()


# ===== PARAMETRIC UPDATE ===== #
def update_QCylinder(self, context):
    bmeshNew = bmesh.new()
    if self.is_flat:
        mat_scale = Create_ScaleMatrix(self.aspect)
        bmesh.ops.create_circle(bmeshNew,
                                segments=self.segments,
                                cap_ends=True,
                                cap_tris=False,
                                radius=self.radius,
                                matrix=mat_scale,
                                calc_uvs=True)
    else:
        mat_scale = Create_ScaleMatrix((self.aspect.x, self.aspect.y, 1.0))
        if not self.is_centered:
            mat_scale = mathutils.Matrix.Translation((0.0, 0.0, (self.depth / 2.0))) @ mat_scale
        bmesh.ops.create_cone(bmeshNew,
                              segments=self.segments,
                              cap_ends=True,
                              cap_tris=False,
                              radius1=self.radius,
                              radius2=self.radius,
                              depth=self.depth,
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
def draw_cylinder(self, context):
    layout = self.layout
    # layout.use_property_split = True
    # layout.use_property_decorate = True
    Qblock_Data = context.object.data.qblock_props
    layout.prop(Qblock_Data, "is_flat", text="Flat")
    if not Qblock_Data.is_flat:
        layout.prop(Qblock_Data, "is_centered", text="Centered")
        layout.prop(Qblock_Data, "is_smooth", text="Smooth")
    layout.prop(Qblock_Data, "radius", text="Radius")
    layout.prop(Qblock_Data, "segments", text="Segments")
    if not Qblock_Data.is_flat:
        layout.prop(Qblock_Data, "depth", text="Depth")
    col = layout.column(align=True)
    # col.prop(Qblock_Data, "aspect", text = "Aspect")
    col.label(text="Aspect:")
    col.prop(Qblock_Data, "aspect", text="X", index=0)
    col.prop(Qblock_Data, "aspect", text="Y", index=1)
