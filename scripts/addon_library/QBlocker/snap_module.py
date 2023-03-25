import bpy
from mathutils import Vector
import numpy
import math
from bpy_extras.view3d_utils import location_3d_to_region_2d
# from .utilities.raycast_utils import *
# from .utilities.grid_utils import *
from .utilities.draw_utils import draw_multicircles_fill_2d, draw_circle_fill_2d
from .utilities.math_utils import GetBRect2D


def SnapDrawHandler(snapClass, context):
    if snapClass.isSnapActive and len(snapClass.snaptargets) > 0:
        addon_prefs = snapClass.addon_prefs
        dotsize = addon_prefs.snap_dotsize * snapClass.ui_scale
        region = context.region
        rv3d = context.region_data
        # draw snap targets
        posBatch = []
        for pos in snapClass.snaptargets:
            pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
            posBatch.append(pos2D)
        if snapClass.snapState == 2:
            cColor = addon_prefs.snap_gridpointsColor
        else:
            cColor = addon_prefs.snap_pointsColor
        draw_multicircles_fill_2d(positions=posBatch, color=cColor, radius=(5 * dotsize), segments=12, alpha=True)
        # draw snap radius
        draw_circle_fill_2d(position=snapClass.mousePos, color=(1.0, 1.0, 1.0, 0.2), radius=snapClass.minDist, segments=16, alpha=True)
        # draw closest target
        if snapClass.closestPoint is not None:
            pos = snapClass.closestPoint
            pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
            draw_circle_fill_2d(position=pos2D, color=addon_prefs.snap_closestColor, radius=(6 * dotsize), segments=12, alpha=False)


class SnappingClass:
    operator = None
    context = None
    ui_scale = 1.0
    addon_prefs = None
    snaptargets = []
    edgediv = 2
    orig_edgediv = 1
    closestPoint = None
    isSnapActive = False
    gridMatrix = None
    snapState = 0
    minDist = 20
    mousePos = None

    def __init__(self, _operator, _qspace,  _context, _edgediv, _addon_prefs):
        self.addon_prefs = _addon_prefs
        self.minDist = self.addon_prefs.snap_dist
        self.edgediv = _edgediv
        self.context = _context
        self.operator = _operator
        self.coordsys = _qspace
        self.ui_scale = _context.preferences.system.ui_scale

        args = (self, _context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(SnapDrawHandler, args, 'WINDOW', 'POST_PIXEL')

    def CleanUp(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

    # toggle snapping state
    # 0 : no snap, 1: vert/edge, 2: polygrid
    def ToggleState(self, _mousepos, _state):
        if _state == 0:
            self.snapState = 0
            self.isSnapActive = False
            self.snaptargets = []
        elif self.snapState == _state:
            self.snapState = 0
            self.isSnapActive = False
            self.snaptargets = []
        else:
            self.snapState = _state
            self.isSnapActive = True
            self.CheckSnappingTarget(_mousepos)

    # set state directly
    def SetState(self, _mousepos, _state):
        if _state == 0:
            self.snapState = 0
            self.isSnapActive = False
            self.snaptargets = []
        else:
            self.snapState = _state
            self.isSnapActive = True
            self.CheckSnappingTarget(_mousepos)

    # increment snap point counts (mousewheel)
    def ChangeSnapPoints(self, _mouse_pos, _val):
        if _val == 1 and self.edgediv < 10:
            self.edgediv += 1
        if _val == -1 and self.edgediv > 1:
            self.edgediv -= 1
        self.CheckSnappingTarget(_mouse_pos)
        self.closestPoint = None

    # set snap point counts
    def SetSnapPoints(self, _mouse_pos, _val):
        if _val > 0 and _val < 11:
            self.edgediv = _val
        self.CheckSnappingTarget(_mouse_pos)
        self.closestPoint = None

    # check snapping target and update list
    def CheckSnappingTarget(self, _coord):
        self.mousePos = _coord
        # if grid hit, else calc on mesh data
        if self.coordsys.isGridhit:
            # if wplane size tweaking ignore grids and reset snapping points.
            if self.operator.wPlaneHold:
                self.snaptargets = []
                self.closestPoint = None
            else:
                if self.operator.isWorkingPlane:
                    self.GetGridVerts(self.operator.workingplane.matrix.translation, self.operator.workingplane.gridstep)
                else:
                    self.GetGridVerts(Vector((0, 0, 0)), self.context.space_data.overlay.grid_scale_unit)
        else:
            self.UpdateSnapPoints()

    # recalculate points at edge divison user input
    def UpdateSnapPoints(self):
        if self.coordsys.lastHitresult[0]:
            self.snaptargets = []
            meshdata = self.coordsys.mesh_data
            # generate snap points
            if self.snapState == 2:
                self.GenPolyGridPoints(self.coordsys.lastHitresult[4], self.coordsys.lastHitresult[3], meshdata)
            else:
                self.GenPolyPoints(self.coordsys.lastHitresult[4], self.coordsys.lastHitresult[3], meshdata)
            # calc closest point if exist
            self.GetClosestPoint2D(self.coordsys.lastHitresult[1])

    def distance(self, pointA, pointB, _norm=numpy.linalg.norm):
        return _norm(pointA - pointB)

    # get the closest snap point to mouse in screenspace
    def GetClosestPoint2D(self, _point):
        actDist = math.inf
        region = self.context.region
        rv3d = self.context.region_data
        point2D = location_3d_to_region_2d(region, rv3d, _point, default=None)
        if point2D is not None:
            if len(self.snaptargets) != 0:
                actID = 0
                counter = 0
                itertargets = iter(self.snaptargets)
                for pos in itertargets:
                    pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
                    if pos2D is None:
                        return
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
        points = []
        stepsXY = (p2 - p1) / _steps
        # create  grid points
        if self.snapState == 2:
            for x in range(_steps+1):
                for y in range(_steps+1):
                    posX = p1.x + x * stepsXY.x
                    posY = p1.y + y * stepsXY.y
                    point = matrix @ (Vector((posX, posY, 0.0)))
                    points.append(point)
        # create only on edges of the cell
        elif self.snapState == 1:
            for x in range(_steps+1):
                posX = p1.x + x * stepsXY.x
                point = matrix @ (Vector((posX, p1.y, 0.0)))
                points.append(point)
                point = matrix @ (Vector((posX, p2.y, 0.0)))
                points.append(point)
            for y in range(_steps-1):
                posY = p1.y + y * stepsXY.y + stepsXY.y
                point = matrix @ (Vector((p1.x, posY, 0.0)))
                points.append(point)
                point = matrix @ (Vector((p2.x, posY, 0.0)))
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
    def GenPolyPoints(self, object, faceID, mesh_data):
        md_verts = mesh_data.vertices
        meshFace = mesh_data.polygons[faceID]
        meshFace_verts = meshFace.vertices
        mesh_Face_edges = meshFace.edge_keys
        matrix = object.matrix_world.copy()
        # add verts
        self.snaptargets = [(matrix @ md_verts[item].co) for item in meshFace_verts]
        # add edges
        snap_append = self.snaptargets.append
        edgeDiv = self.edgediv
        for ek in mesh_Face_edges:
            # edge = md_edges[mesh_data.edge_keys.index(ek)]
            # vert1 = md_verts[edge.vertices[0]].co
            # vert2 = md_verts[edge.vertices[1]].co
            vert1 = md_verts[ek[0]].co
            vert2 = md_verts[ek[1]].co
            vertdif = (vert2 - vert1)
            for d in range(1, edgeDiv):
                div = d / edgeDiv
                vec = matrix @ (vert1 + (vertdif * div))
                snap_append(vec)

    # generate sub-grid points on grid
    def GenPolyGridPoints(self, object, faceID, mesh_data):
        snap_append = self.snaptargets.append
        steps = self.edgediv
        bbox = self.GetPolyOBB(object, faceID, mesh_data)
        stepXY = (bbox[1] - bbox[0]) / steps
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
        # calc brect
        LocBrect = GetBRect2D(verts)
        return LocBrect
