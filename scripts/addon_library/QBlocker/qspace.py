import bpy
import gpu
import bgl
# import bmesh
from gpu_extras.batch import batch_for_shader
import mathutils
# import numpy
from .utilities.grid_utils import GetGridVector
from .utilities.math_utils import LinePlaneCollision
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from .utilities.qspace_utils import VecToMatrix, Distance


redC = (0.984, 0.2, 0.318, 1.0)
greenC = (0.525, 0.824, 0.012, 1.0)
blueC = (0.157, 0.557, 0.988, 1.0)
aVcolors = [greenC, greenC, redC, redC, blueC, blueC]


def QSpaceDrawHandler(qSpace, context):
    bgl.glLineWidth(2)
    pos = qSpace.wMatrix.translation
    mat = qSpace.wMatrix.to_3x3()
    vecX = pos + mat.col[0]
    vecY = pos + mat.col[1]
    vecZ = pos + mat.col[2]

    coords = [pos, vecX, pos, vecY, pos, vecZ]
    shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": coords, "color": aVcolors})

    shader.bind()
    batch.draw(shader)


class CoordSysClass:
    operator = None
    addon_prefs = None
    context = None
    lastHitresult = (False, None, None, None, None, None)
    isGridhit = False
    isModifiedMesh = False
    mesh_data = None
    wMatrix = mathutils.Matrix()
    isPropAxis = True
    object_eval = None

    scene = None
    region = None
    rv3d = None

    def __init__(self, _context, _op, _isAxis, _addon_prefs):
        self.addon_prefs = _addon_prefs
        self.operator = _op
        self.context = _context
        self.isPropAxis = _isAxis
        self.scene = self.context.scene
        self.region = self.context.region
        self.rv3d = self.context.region_data

        if _isAxis:
            args = (self, _context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(QSpaceDrawHandler, args, 'WINDOW', 'POST_VIEW')

    def CleanUp(self):
        if self.isPropAxis and self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

    def ToggleAxis(self, _state):
        if self.isPropAxis:
            if _state:
                if not self._handle:
                    args = (self, self.context)
                    self._handle = bpy.types.SpaceView3D.draw_handler_add(QSpaceDrawHandler, args, 'WINDOW', 'POST_VIEW')
            else:
                if self._handle:
                    bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                    self._handle = None

    # raycast into scene from mouse pos
    def HitScene(self, coord):
        view_vector = region_2d_to_vector_3d(self.region, self.rv3d, coord)
        ray_origin = region_2d_to_origin_3d(self.region, self.rv3d, coord)

        # mod if version 2.91 or 3.0
        appversion = bpy.app.version

        if appversion[0] == 3:
            hitresult = self.scene.ray_cast(self.context.view_layer.depsgraph, ray_origin, view_vector)
        elif bpy.app.version[1] >= 91:
            hitresult = self.scene.ray_cast(self.context.view_layer.depsgraph, ray_origin, view_vector)
        else:
            hitresult = self.scene.ray_cast(self.context.view_layer, ray_origin, view_vector)

        return hitresult

    def ResetResult(self):
        self.lastHitresult = (False, None, None, None, None, None)
        if self.isModifiedMesh:
            self.RemoveTempMesh()

    def UpdateMeshEditMode(self):
        if self.mesh_data is not None and self.lastHitresult[4] is not None:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            self.object_eval = bpy.context.active_object.evaluated_get(depsgraph)
            self.mesh_data = self.object_eval.to_mesh()

    def RemoveTempMesh(self):
        self.object_eval.to_mesh_clear()
        self.mesh_data = None
        self.isModifiedMesh = False
        self.isGridhit = True

    def IsFiltered(self, coord, hitresult):
        # if grid only always hit grid
        if self.operator.object_ignorebehind == 'GRID':
            return False
        # if front of grid, check if object is behind
        elif self.operator.object_ignorebehind == 'FRONT' and hitresult[0]:
            ray_origin = region_2d_to_origin_3d(self.region, self.rv3d, coord)
            hitDist = Distance(hitresult[1], ray_origin)
            gridMat = self.GetActiveGridAlign(coord)
            gridHitDist = Distance(gridMat.to_translation(), ray_origin)
            if not hitDist + 0.0001 < gridHitDist:
                return False
        return True

    # main function
    def GetCoordSys(self, context, coord, isoriented):
        # time_start = time.time() # timetest
        if self.operator.toolstage != 0:
            self.operator.qObject.HideObject(True)
        hitresult = self.HitScene(coord)
        cSysMatrix = None
        # if object hit
        if hitresult[0] and hitresult[4].type == 'MESH' and self.IsFiltered(coord, hitresult):
            if hitresult[4] != self.operator.qObject.bObject:
                # if not the same object, then create evaluated mesh data
                if hitresult[4] != self.lastHitresult[4]:
                    # remove last mesh if that was modified
                    if self.isModifiedMesh:
                        self.RemoveTempMesh()
                    # check if hit modified object
                    if len(hitresult[4].modifiers) != 0:
                        depsgraph = context.evaluated_depsgraph_get()
                        self.object_eval = hitresult[4].evaluated_get(depsgraph)
                        self.mesh_data = self.object_eval.to_mesh()
                        self.isModifiedMesh = True
                    else:
                        self.mesh_data = hitresult[4].data
            # Get matrix if oriented or axis aligned
            if isoriented:
                cSysMatrix = self.GetOrientedAlign(hitresult)
            else:
                cSysMatrix = self.GetAxisAlign(hitresult)
            self.isGridhit = False
            self.lastHitresult = hitresult
        # if gridhit
        else:
            if not self.isGridhit:
                self.ResetResult()
                self.isGridhit = True
            cSysMatrix = self.GetActiveGridAlign(coord)
            self.lastHitresult = (False, None, None, None, None, None)

        if self.operator.toolstage != 0:
            self.operator.qObject.HideObject(False)

        self.wMatrix = cSysMatrix
        return cSysMatrix

    # Get space align (wqrking plane or world grid)
    def GetActiveGridAlign(self, coord):
        cSysMatrix = None
        if self.operator.isWorkingPlane and not self.operator.wPlaneHold:
            cSysMatrix = self.GetWPlaneAlign(coord, self.operator.workingplane.matrix)
        else:
            cSysMatrix = self.GetGridAlign(coord)
        return cSysMatrix

    # WPLANE ALIGNED
    def GetWPlaneAlign(self, coord, _matrix):
        # get view ray
        view_vector = region_2d_to_vector_3d(self.region, self.rv3d, coord)
        ray_origin = region_2d_to_origin_3d(self.region, self.rv3d, coord)
        # check grid and collide with view ray
        grid_vector = _matrix.col[2].xyz
        hitpoint = LinePlaneCollision(view_vector, ray_origin, _matrix.translation, grid_vector)
        # create matrix
        ret_matrix = _matrix.copy()
        ret_matrix.translation = hitpoint
        return ret_matrix

    # GRID ALIGNED
    def GetGridAlign(self, coord):
        # get view ray
        view_vector = region_2d_to_vector_3d(self.region, self.rv3d, coord)
        ray_origin = region_2d_to_origin_3d(self.region, self.rv3d, coord)
        # check grid and collide with view ray
        grid_vector = GetGridVector(self.context)
        hitpoint = LinePlaneCollision(view_vector, ray_origin, (0.0, 0.0, 0.0), grid_vector)
        # create matrix
        grid_vector = mathutils.Vector(grid_vector)
        ret_matrix = VecToMatrix(grid_vector, hitpoint)
        return ret_matrix

    # AXIS ALIGNED
    def GetAxisAlign(self, _hitresult):
        return VecToMatrix(_hitresult[2], _hitresult[1])

    # ORIENTED ALIGN
    def GetOrientedAlign(self, _hitresult):
        # if same object and face, only move the matrix
        if _hitresult[4] == self.lastHitresult[4] and _hitresult[3] == self.lastHitresult[3]:
            self.wMatrix.translation = _hitresult[1]
            return self.wMatrix
        else:
            verts = self.GetTargetPolyVerts(_hitresult)
            # create matrix from face normal
            matrix = VecToMatrix(_hitresult[2], _hitresult[1])
            mat_inv = matrix.inverted()
            # transform verts to poly space
            vertsL = [(mat_inv @ v) for v in verts]
            # calc best rotation
            verts2DL = [(p[0], p[1]) for p in vertsL]
            bboxangle = mathutils.geometry.box_fit_2d(verts2DL)
            mat_rot = mathutils.Matrix.Rotation(-bboxangle, 4, 'Z')
            ret_matrix = matrix @ mat_rot
            return ret_matrix

    # get vertices from polygon in world space
    def GetTargetPolyVerts(self, _hitresult):
        meshFace = self.mesh_data.polygons[_hitresult[3]]
        matrix = _hitresult[4].matrix_world.copy()
        return [(matrix @ self.mesh_data.vertices[v].co) for v in meshFace.vertices]
