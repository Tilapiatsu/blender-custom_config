import bpy
from mathutils import Vector
import numpy
import math
from bpy_extras.view3d_utils import location_3d_to_region_2d
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
        if snapClass.snapState == 2:
            cColor = (0.12, 0.56, 1.0, 0.7)
        else:
            cColor = (1.0, 0.56, 0.0, 0.7)
        draw_multicircles_fill_2d(positions=posBatch, color=cColor, radius=5, segments=12, alpha=True)
        # draw snap radius
        draw_circle_fill_2d(position=snapClass.mousePos, color=(1.0, 1.0, 1.0, 0.2), radius=snapClass.minDist, segments=16, alpha=True)
        # draw closest target
        if snapClass.closestPoint is not None:
            pos = snapClass.closestPoint 
            pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
            draw_circle_fill_2d(position=pos2D, color=(1.0, 1.0, 1.0, 1.0), radius=6, segments=12, alpha=False)


class SnappingClass:
    operator = None
    context = None
    snaptargets = []
    edgediv = 2
    orig_edgediv = 1
    closestPoint = None
    isSnapActive = False
    gridMatrix = None
    snapState = 0
    minDist = 20
    mousePos = None

    def __init__(self, _operator, _qspace,  _context, _edgediv, _snapDist):
        self.minDist = _snapDist
        self.edgediv = _edgediv
        self.context = _context
        self.operator = _operator
        self.coordsys = _qspace
        args = (self, _context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(SnapDrawHandler, args, 'WINDOW', 'POST_PIXEL')
        print("SnappingClass created!")

    def CleanUp(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        print("SnappingClass cleaned!")

    # toggle snapping state
    # 0 : no snap, 1: vert/edge, 2: polygrid
    def ToggleState(self, _mousepos, _state):
        if self.snapState == _state:
            self.snapState = 0
            self.isSnapActive = False
            self.snaptargets = []
        else:
            self.snapState = _state
            self.isSnapActive = True
            self.CheckSnappingTarget(_mousepos)   

    # change snap point counts
    def ChangeSnapPoints(self,mouse_pos, val):
        if val == 1 and self.edgediv < 10:
            self.edgediv += 1
        if val == -1 and self.edgediv > 1:
            self.edgediv -= 1
        self.CheckSnappingTarget(mouse_pos)
        self.closestPoint = None         

    # check snapping target and update list
    def CheckSnappingTarget(self, coord):
        self.mousePos = coord
        if self.coordsys.isGridhit:
            if self.operator.isWorkingPlane:
                self.GetGridVerts(self.operator.workingplane.matrix.translation, self.operator.workingplane.gridstep )
            else:
                self.GetGridVerts(Vector((0, 0, 0)), self.context.space_data.overlay.grid_scale_unit )
        else:
            self.UpdateSnapPoints()

    # recalculate points at edge divison user input
    def UpdateSnapPoints(self):
        self.snaptargets = []
        meshdata = None
        if self.coordsys.isModifiedMesh:
            meshdata = self.coordsys.mesh_data
        else:
            meshdata = self.coordsys.lastHitresult[4].data

        if self.snapState == 2:
            self.GeneratePolyPoints(self.coordsys.lastHitresult[4], self.coordsys.lastHitresult[3], meshdata)
        else:
            self.AddTargetPolyPoints(self.coordsys.lastHitresult[4], self.coordsys.lastHitresult[3], meshdata)
        self.GetClosestPoint2D(self.coordsys.lastHitresult[1])

    def distance(self, pointA, pointB, _norm=numpy.linalg.norm):
        return _norm(pointA - pointB)

    def GetClosestPoint2D(self, _point):
        region = self.context.region
        rv3d = self.context.region_data
        point2D = location_3d_to_region_2d(region, rv3d, _point, default=None)
        if len(self.snaptargets) != 0:
            pos2D = location_3d_to_region_2d(region, rv3d, self.snaptargets[0], default=None)
            actDist = self.distance(pos2D, point2D)
            actID = 0
            counter = 1
            itertargets = iter(self.snaptargets)
            next(itertargets)
            for pos in itertargets:
                pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
                dist = self.distance(pos2D, point2D)
                if dist < actDist:
                    actID = counter
                    actDist = dist
                counter += 1
            if actDist < self.minDist:
                self.closestPoint = self.snaptargets[actID]
            else:
                self.closestPoint = None


    def GetClosestPointOnGrid(self, matrix):
        matrix_inv = matrix.inverted()
        pointS = matrix_inv @ self.closestPoint
        pointS[2] = 0.0
        return pointS

    def GetGridVerts(self, _position, _girdsize):
        self.snaptargets = []
        gridhit = self.operator.wMatrix.translation
        matW = self.operator.wMatrix.copy()
        matW.translation = _position
        gridcorners = self.GetGridBRect(_girdsize, matW, gridhit)
        gridpointsall = self.GeneratePoints(gridcorners[0], gridcorners[1], matW, self.edgediv)
        self.snaptargets.extend(gridpointsall)
        self.GetClosestPoint2D(gridhit)

    # get target grid bounding rect corners in GridSpace
    def GetGridBRect(self, gridstep, gridmatrix, position):
        mat = gridmatrix.copy()
        mat_inv = mat.inverted()
        pos = Vector(position)
        pos = mat_inv @ pos
        Xf = math.floor(pos.x / gridstep) * gridstep
        Yf = math.floor(pos.y / gridstep) * gridstep
        Xc = Xf + gridstep
        Yc = Yf + gridstep
        return [Vector((Xf, Yf, 0.0)), Vector((Xc, Yc, 0.0))]

    # generate sub-grid points on grid
    def GeneratePoints(self, p1, p2, matrix, _steps):
        if self.snapState == 2:
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
                point = matrix @ (Vector((posX, posY, 0.0)))
                points.append(point)
        return points


    # get target grid corner points in GridSpace
    def GetGridCorners(self, gridstep, gridmatrix, position):
        mat_inv = gridmatrix.inverted()
        pos = Vector(position)
        pos = mat_inv @ pos
        Xf = math.floor(pos.x / gridstep) * gridstep
        Yf = math.floor(pos.y / gridstep) * gridstep
        Xc = Xf + gridstep
        Yc = Yf + gridstep
        points = [Vector((Xf, Yf, 0.0)), Vector((Xc, Yf, 0.0)), Vector((Xc, Yc, 0.0)), Vector((Xf, Yc, 0.0))]
        return points

    # get target polygon data on object for snap
    def AddTargetPolyPoints(self, object, faceID, mesh_data):
        md_verts = mesh_data.vertices
        md_edges = mesh_data.edges
        meshFace = mesh_data.polygons[faceID]
        meshFace_verts = meshFace.vertices
        matrix = object.matrix_world.copy()
        # add verts
        self.snaptargets = [(matrix @ md_verts[item].co) for item in meshFace_verts] 
        # add edges
        snap_append = self.snaptargets.append
        edgeDiv = self.edgediv
        for ek in meshFace.edge_keys:
            edge = md_edges[mesh_data.edge_keys.index(ek)]
            vert1 = md_verts[edge.vertices[0]].co
            vert2 = md_verts[edge.vertices[1]].co
            vertdif = (vert2 - vert1)
            for d in range(1, edgeDiv):
                div = d / edgeDiv
                vec = matrix @ (vert1 + (vertdif * div))
                snap_append(vec)

    # generate sub-grid points on grid
    def GeneratePolyPoints(self, object, faceID, mesh_data):
        snap_append = self.snaptargets.append
        steps = self.edgediv
        bbox = self.GetPolyOBB(object, faceID, mesh_data)
        stepXY = (bbox[1] - bbox[0] ) / steps
        for x in range(steps+1):
            for y in range(steps+1):
                posX = bbox[0].x + x * stepXY[0]
                posY = bbox[0].y + y * stepXY[1]
                point = self.coordsys.wMatrix @ Vector((posX, posY, 0.0))
                snap_append(point)

    # get oriented bbox for poly
    def GetPolyOBB(self, object, faceID, mesh_data):
        # get target polygon verts in polyspace
        meshFace_verts = mesh_data.polygons[faceID].vertices
        md_verts = mesh_data.vertices
        mat_inv = self.coordsys.wMatrix.inverted()
        matrix = object.matrix_world.copy()
        matrix_poly = mat_inv @ matrix
        verts = [(matrix_poly @ md_verts[item].co) for item in meshFace_verts] 
        # flatten verts to polyspace
        vertsL = []
        vertsL_append = vertsL.append
        for v in verts:
            v[2] = 0.0
            vertsL_append(v)
        # calc brect
        LocBrect = GetBRect(vertsL)
        return LocBrect

        
