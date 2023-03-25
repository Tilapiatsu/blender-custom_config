import bpy
import bmesh
import mathutils
import math
from .qobject import Qobject, GetTransformOffset
from .obj_utils import Create_ScaleMatrix, SetSmoothFaces


# ===== QOBJECT CLASS ===== #
class QTorus(Qobject):
    basetype = 3
    isSmooth = True
    radius = 0.1
    height = 0.1

    def copyData(self, _op):
        newQ = QTorus(_op)
        return newQ

    def CreateQBlock(self):
        qbProps = self.bObject.data.qblock_props
        qbProps.qblockType = 'QTORUS'
        qbProps.is_centered = self.isCentered
        qbProps.is_smooth = self.isSmooth
        qbProps.depth = self.height
        qbProps.segments = self.meshSegments
        aspect = (1.0, 1.0)
        qbProps.aspect[0] = aspect[0]
        qbProps.aspect[1] = aspect[1]
        qbProps.aspect[2] = 1.0
        qbProps.radius = self.radius

    def UpdateMesh(self):
        # generate mesh data #
        # TODO need to change the other segments too
        bmeshNew = Gen_Mesh(self.meshSegments*2, self.meshSegments, self.radius, self.height, self.isCentered)
        # finalize
        bmeshNew.to_mesh(self.bMesh)
        self.bMesh.auto_smooth_angle = 1.386
        self.SetSmoothFaces()
        # self.bMesh.update()
        bpy.context.view_layer.update()
        bmeshNew.free()

    def ToggleMeshCenter(self):
        self.isCentered = (not self.isCentered)
        self.UpdateMesh()
        return self.isCentered

    # ===== Object Base Positioning ===== #

    # corner to corner positioning
    def TransformPtoP(self, _matrix):
        self.bObject.location = self.firstPoint
        self.radius = self.secondPoint.length
        self.bObject.scale = (1.0, 1.0, 1.0)
        self.UpdateMesh()

   # set base point, update scale
    def UpdateBase(self, _firstP, _secondP):
        # get corners
        self.firstPoint = _firstP
        self.secondPoint = _secondP
        # transform position by type
        self.TransformPtoP(self.bMatrix)

    # set height, update scale
    def UpdateHeight(self, _height):
        self.height = _height
        self.UpdateMesh()


# ===== PARAMETRIC UPDATE ===== #
def update_QTorus(self, context):
    # generate mesh data #
    bmeshNew = Gen_Mesh(self.segments*2, self.segments, self.radius, self.depth, self.is_centered)

    # finalize
    bmesh.ops.recalc_face_normals(bmeshNew, faces=bmeshNew.faces)
    bmeshNew.to_mesh(self.id_data)
    if self.is_smooth:
        self.id_data.auto_smooth_angle = 1.386
        SetSmoothFaces(self.id_data)
    bpy.context.view_layer.update()

    bmeshNew.free()


# shared mesh gen #
def Gen_Mesh(rings, segs, radT, radC, isCentered):
    bmeshNew = bmesh.new()

    bvertList = []

    ringRadius = radC  # use depth as ring radius

    verticalAngularStride = (math.pi * 2.0) / rings
    horizontalAngularStride = (math.pi * 2.0) / segs

    # generate vertices
    for act_ring in range(rings):
        theta = verticalAngularStride * act_ring
        for act_seg in range(segs):
            phi = horizontalAngularStride * act_seg
            # position
            x = math.cos(theta) * (radT + ringRadius * math.cos(phi))
            y = ringRadius * math.sin(phi)
            z = math.sin(theta) * (radT + ringRadius * math.cos(phi))

            if isCentered:
                y += radC
            position = [x, z, y]
            actVert = bmeshNew.verts.new(position)
            bvertList.append(actVert)

    # generate face indices

    for act_ring in range(rings):
        for act_seg in range(segs):

            lt = act_seg + act_ring * segs
            lb = act_seg + ((act_ring + 1) % rings) * segs

            rt = ((act_seg + 1) % segs) + act_ring * segs
            rb = ((act_seg + 1) % segs) + ((act_ring + 1) % rings) * segs

            bvseq = [bvertList[lt], bvertList[rt], bvertList[rb], bvertList[lb]]
            bmeshNew.faces.new(bvseq)

    return bmeshNew


# ===== PARAMETRIC UI ===== #
def draw_torus(self, context):
    layout = self.layout
    Qblock_Data = context.object.data.qblock_props
    # layout.prop(Qblock_Data, "is_flat", text="Flat")
    if not Qblock_Data.is_flat:
        layout.prop(Qblock_Data, "is_centered", text="Centered")
        layout.prop(Qblock_Data, "is_smooth", text="Smooth")
    layout.prop(Qblock_Data, "radius", text="Radius")
    layout.prop(Qblock_Data, "segments", text="Segments")
    if not Qblock_Data.is_flat:
        layout.prop(Qblock_Data, "depth", text="Disk radius")
    col = layout.column(align=True)
    # col.prop(Qblock_Data, "aspect", text = "Aspect")
    # col.label(text="Aspect:")
    # col.prop(Qblock_Data, "aspect", text="X", index=0)
    # col.prop(Qblock_Data, "aspect", text="Y", index=1)
