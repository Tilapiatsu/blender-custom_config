import bpy
# import bmesh
import gpu
from .op_mesh import *
from .qobjects.qtorus import QTorus


# box create op new
class TorusCreateOperator(MeshCreateOperator):
    bl_idname = "object.torus_create"
    bl_label = "Torus Create Operator"

    drawcallback = draw_callback_torus
    objectType = 2
    basetype = 3
    isSmooth = True
    isCentered = False

    meshSegments = 16
    originalSegments = 16
    minSegment = 4

    # create Qobject tpye
    def CreateQobject(self):
        self.qObject = QTorus(self)

    # toggle smooth mesh
    def ToggleMeshSmooth(self):
        self.isSmooth = self.qObject.ToggleSmoothFaces()

    def ChangeMeshSegments(self):
        allstep = int((self.mouse_pos[0] - self.mouseStart[0]) // self.inc_px)
        prevalue = max(self.minSegment, min(128, self.qObject.originalSegments + allstep))
        if prevalue != self.qObject.meshSegments:
            self.qObject.meshSegments = prevalue
            self.mouseEnd_x = self.mouseStart[0] + ((prevalue - self.qObject.originalSegments) * self.inc_px)
            self.qObject.UpdateMesh()
        self.meshSegments = self.qObject.meshSegments

    # step mesh segments dinamically
    def StepMeshSegments(self, _val):
        if _val == 1 and self.meshSegments < 128:
            self.meshSegments += 1
            self.qObject.meshSegments = self.meshSegments
            self.qObject.UpdateMesh()
        if _val == -1 and self.meshSegments > self.minSegment:
            self.meshSegments -= 1
            self.qObject.meshSegments = self.meshSegments
            self.qObject.UpdateMesh()

    # Stage Three: set height
    def Stage_Height(self, _context):
        if not self.segkeyHold:
            # if snap active
            if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                mat_inv = self.qObject.bMatrix.inverted()
                radius2pos = mat_inv @ self.snapClass.closestPoint
                # heightcoord = heightcoord[2]
                heightcoord = radius2pos.length - self.qObject.radius
            else:  # no snap
                # heightcoord = GetHeightLocation(_context, self.mouse_pos, self.qObject.bMatrix, self.secondPoint)
                radius2pos = GetPlaneLocation(_context, self.mouse_pos, self.qObject.bMatrix)
                heightcoord = radius2pos.length - self.qObject.radius
            # if increment height
            if self.isIncrement:
                gridstep = _context.space_data.overlay.grid_scale
                heightcoord = math.floor((heightcoord / gridstep)) * gridstep
            self.qObject.UpdateHeight(heightcoord)
