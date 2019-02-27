import bpy
import gpu
import mathutils
from mathutils import Vector
import numpy
import math
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
from .utilities.raycast_utils import *
from .utilities.grid_utils import *
from .utilities.draw_utils import *


def SnapDrawHandler(snapClass, context):
    if snapClass.isSnapActive:
        region = context.region
        rv3d = context.region_data
        # draw snap targets
        posBatch = []
        for pos in snapClass.snaptargets:
            pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
            posBatch.append(pos2D)
        if snapClass.isPolyGridActive:
            cColor = (0.12, 0.56, 1.0, 0.7)
        else:
            cColor = (1.0, 0.56, 0.0, 0.7)
        draw_multicircles_fill_2d(positions=posBatch, color=cColor, radius=5, segments=12, alpha=True)
        # draw closest target
        if snapClass.closestPoint is not None:
            pos = snapClass.closestPoint
            pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
            draw_circle_fill_2d(position=pos2D, color=(1.0, 1.0, 1.0, 1.0), radius=6, segments=12, alpha=True)


class SnappingClass:
    operator = None
    context = None
    targetObject = (False, None, None, None, None, None)
    snaptargets = []
    edgediv = 2
    orig_edgediv = 1
    closestPoint = None
    isSnapActive = False
    isPolyGridActive = False
    gridMatrix = None
    isGridhit = False
    meshCopy = None
    isModifiedMesh = False

    tempMesh = None

    def __init__(self, _operator, _context, _edgediv):
        self.edgediv = _edgediv
        self.context = _context
        self.operator = _operator
        args = (self, _context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(SnapDrawHandler, args, 'WINDOW', 'POST_PIXEL')
        print("SnappingClass created!")

    def CleanUp(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        if self.meshCopy:
            bpy.data.meshes.remove(self.meshCopy, do_unlink=True)
            self.meshCopy = None
        print("SnappingClass cleaned!")

    # set snapping active
    def SetState(self, _state, _mousepos):
        if _state:
            self.isSnapActive = True
            self.CheckSnappingTarget(self.context, _mousepos)
        else:
            self.isSnapActive = False
            self.snaptargets = []
            self.targetObject = (False, None, None, None, None, None)
            if self.meshCopy:
                bpy.data.meshes.remove(self.meshCopy, do_unlink=True)
                self.meshCopy = None

    def SetPolyGrid(self, _state, _mousepos):
        if _state:
            self.isPolyGridActive = True
        else:
            self.isPolyGridActive = False
        if self.isSnapActive:
            self.CheckSnappingTarget(self.context, _mousepos)

    # check snapping target and update list
    def CheckSnappingTarget(self, context, coord):
        # turn off visibility on tool object
        if self.operator.toolstage != 0:
            self.operator.qObject.HideObject(True)

        # check if object is hit, else calc snap on grid
        hitobject_data = self.HitScene(context, coord)
        if hitobject_data[0] and hitobject_data[4].type == 'MESH':
            # check if has modifiers
            if hitobject_data[4] != self.targetObject[4]:
                if len(hitobject_data[4].modifiers) != 0:
                    self.meshCopy = hitobject_data[4].to_mesh(context.depsgraph, apply_modifiers=True)
                    self.meshCopy.name = "TempMesh"
                    self.isModifiedMesh = True

                elif self.isModifiedMesh and self.meshCopy:
                    bpy.data.meshes.remove(self.meshCopy)
                    self.meshCopy = None
                    self.isModifiedMesh = False

            isGridhit = False
            self.targetObject = hitobject_data
            self.UpdateSnapPoints()
        else:
            if self.isModifiedMesh and self.meshCopy:
                bpy.data.meshes.remove(self.meshCopy, do_unlink=True)
                self.isModifiedMesh = False
                self.meshCopy = None

            isGridhit = True
            self.targetObject = (False, None, None, None, None, None)
            self.GetGridVerts(context, coord)
        # turn back visibility
        if self.operator.toolstage != 0:
            self.operator.qObject.HideObject(False)

    # recalculate points at edge divison user input
    def UpdateSnapPoints(self):
        meshData = None
        if self.isModifiedMesh and self.meshCopy:
            meshData = self.meshCopy
        else:
            meshData = self.targetObject[4].data

        self.snaptargets = []
        if self.isPolyGridActive:
            self.GeneratePolyPoints(self.targetObject[4], self.targetObject[3], self.edgediv, meshData)
        else:
            self.AddTargetPolyVerts(self.targetObject[4], self.targetObject[3], meshData)
            self.AddTargetPolyEdges(self.targetObject[4], self.targetObject[3], self.edgediv, meshData)
        self.GetClosestPoint(self.targetObject[1])

    # get closest point to a given position WP
    def GetClosestPoint(self, point):
        if len(self.snaptargets) != 0:
            actDist = numpy.linalg.norm(self.snaptargets[0]-point)
            actID = 0
            counter = 1
            itertargets = iter(self.snaptargets)
            next(itertargets)
            for pos in itertargets:
                dist = numpy.linalg.norm(pos-point)
                if dist < actDist:
                    actID = counter
                    actDist = dist
                counter += 1
            self.closestPoint = self.snaptargets[actID]

    def GetClosestPointOnGrid(self, matrix):
        matrix_inv = matrix.inverted()
        pointS = matrix_inv @ self.closestPoint
        pointS[2] = 0.0
        return pointS

    # Get object and face id at mouse
    def HitScene(self, context, coord):
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        view_vector = region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        hitresult = scene.ray_cast(context.view_layer, ray_origin, view_vector)
        return hitresult

    def GetGridVerts(self, context, coord):
        self.snaptargets = []
        girdsize = context.space_data.overlay.grid_scale
        gridhit = GetGridHitPoint(context, coord)
        gridmat = GetGridMatrix(gridhit[1])
        self.gridMatrix = gridmat
        gridcorners = self.GetGridBRect(girdsize, gridmat, gridhit[0])
        gridpointsall = self.GeneratePoints(gridcorners[0], gridcorners[1], gridmat, self.edgediv)
        self.snaptargets.extend(gridpointsall)
        self.GetClosestPoint(gridhit[0])

    # generate sub-grid points on grid
    def GeneratePoints(self, p1, p2, matrix, _steps):
        if self.isPolyGridActive:
            steps = _steps
        else:
            steps = 1
        points = []
        stepX = (p2.x - p1.x) / steps
        stepY = (p2.y - p1.y) / steps
        for x in range(steps+1):
            for y in range(steps+1):
                posX = p1.x + x * stepX
                posY = p1.y + y * stepY
                point = Vector((posX, posY, 0.0))
                point = matrix @ point
                points.append(point)
        return points

    # get target grid bounding rect corners in GridSpace
    def GetGridBRect(self, gridstep, gridmatrix, position):
        mat_inv = gridmatrix.inverted()
        pos = mathutils.Vector(position)
        pos = mat_inv @ pos
        Xf = math.floor(pos.x / gridstep) * gridstep
        Yf = math.floor(pos.y / gridstep) * gridstep
        Xc = Xf + gridstep
        Yc = Yf + gridstep
        return [Vector((Xf, Yf, 0.0)), Vector((Xc, Yc, 0.0))]

    # get target grid corner points in GridSpace
    def GetGridCorners(self, gridstep, gridmatrix, position):
        mat_inv = gridmatrix.inverted()
        pos = mathutils.Vector(position)
        pos = mat_inv @ pos
        Xf = math.floor(pos.x / gridstep) * gridstep
        Yf = math.floor(pos.y / gridstep) * gridstep
        Xc = Xf + gridstep
        Yc = Yf + gridstep
        points = [Vector((Xf, Yf, 0.0)), Vector((Xc, Yf, 0.0)), Vector((Xc, Yc, 0.0)), Vector((Xf, Yc, 0.0))]
        return points

    # get target polygon data on object for snap
    def AddTargetPolyVerts(self, object, faceID, meshData):
        meshFace = meshData.polygons[faceID]
        matrix = object.matrix_world.copy()
        for v in meshFace.vertices:
            pos = matrix @ (meshData.vertices[v].co)
            self.snaptargets.append(pos)

    # get target polygon data on object for snap
    def AddTargetPolyEdges(self, object, faceID, edgeDiv, meshData):
        mesh_data = meshData
        meshFace = mesh_data.polygons[faceID]
        matrix = object.matrix_world.copy()
        for ek in meshFace.edge_keys:
            edge = mesh_data.edges[mesh_data.edge_keys.index(ek)]
            vert1 = mesh_data.vertices[edge.vertices[0]].co
            vert2 = mesh_data.vertices[edge.vertices[1]].co
            vertc = (vert1 + vert2) / 2
            for d in range(1, edgeDiv):
                div = d / edgeDiv
                dPoint_X = vert1[0] + div * (vert2[0] - vert1[0])
                dPoint_Y = vert1[1] + div * (vert2[1] - vert1[1])
                dPoint_Z = vert1[2] + div * (vert2[2] - vert1[2])
                # transform to world space
                vec = mathutils.Vector((dPoint_X, dPoint_Y, dPoint_Z))
                vec = matrix @ vec
                self.snaptargets.append(vec)

    # generate sub-grid points on grid
    def GeneratePolyPoints(self, object, faceID, steps, meshData):
        points = []
        bbox = self.GetPolyOBB(object, faceID, meshData)
        centerX = (bbox[0].x + bbox[1].x) / 2
        centerY = (bbox[0].y + bbox[1].y) / 2
        stepX = (bbox[1].x - bbox[0].x) / steps
        stepY = (bbox[1].y - bbox[0].y) / steps
        for x in range(steps+1):
            for y in range(steps+1):
                posX = bbox[0].x + x * stepX
                posY = bbox[0].y + y * stepY
                point = Vector((posX, posY, 0.0))
                point = self.gridMatrix @ point
                self.snaptargets.append(point)

    # get oriented bbox for poly
    def GetPolyOBB(self, object, faceID, meshData):
        verts = self.GetTargetPolyVerts(object, faceID, meshData)
        face = meshData.polygons[faceID]

        matrixObj = object.matrix_world.copy()
        faceN = face.normal.copy()
        faceN.normalize()
        faceC = face.center.copy()

        matrix = faceN.to_track_quat('Z', 'X').to_matrix()
        matrix.resize_4x4()
        mat_Trans = mathutils.Matrix.Translation(faceC)
        matrix = mat_Trans @ matrix

        matrix = matrixObj @ matrix
        mat_inv = matrix.inverted()

        # transform verts to poly space
        vertsL = []
        for v in verts:
            v2 = mat_inv @ v
            v2[2] = 0.0
            vertsL.append(v2)
        # calc best rotation
        verts2DL = [(p[0], p[1]) for p in vertsL]
        bboxangle = mathutils.geometry.box_fit_2d(verts2DL)
        rotQuat = mathutils.Quaternion((0.0, 0.0, 1.0), bboxangle)

        mat_rot = mathutils.Matrix.Rotation(-bboxangle, 4, 'Z')
        self.gridMatrix = matrix @ mat_rot
        # rotate to best bbox
        vertsLrot = []
        for v in vertsL:
            v2 = v
            v2.rotate(rotQuat)
            vertsLrot.append(v2)
        # calc brect
        LocBrect = GetBRect(vertsLrot)
        return LocBrect

    # get target polygon data on object for snap
    def GetTargetPolyVerts(self, object, faceID, meshData):
        verts = []
        meshFace = meshData.polygons[faceID]
        matrix = self.targetObject[4].matrix_world.copy()
        for v in meshFace.vertices:
            pos = object.matrix_world @ (meshData.vertices[v].co)
            verts.append(pos)
        return verts
