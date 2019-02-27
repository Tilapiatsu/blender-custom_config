import bpy
import bmesh
import gpu
import math
import copy
from .snap_module import *
from .draw_module import *
from .utilities.raycast_utils import *
# from .qobject import *


# box create op new
class MeshCreateOperator(bpy.types.Operator):
    bl_idname = ""
    bl_label = ""
    bl_context = "objectmode"

    addon_prefs = None

    drawcallback = None
    mainMouse = None

    # for 0.11
    qObject = None

    objectType = 1
    basetype = 1

    toolstage = 0

    firstPoint = None
    secondPoint = None

    mouse_pos = (0, 0)

    lmb = False
    coordsys = False
    actMatrix = None

    # snapping variables
    snapClass = None
    snapSegHold = False

    # for save to reuse
    isSmooth = False
    isCentered = False
    isIncrement = False
    isFlat = False
    meshSegments = 16
    edgediv = 2

    mouseStart = [0, 0]
    mouseEnd_x = 0
    inc_px = 30

    segkeyHold = False

    # set mouse buttons based on preferences
    def GetMainMouseButton(self, context):
        addonMpref = self.addon_prefs.mouse_enum
        if addonMpref == 'LEFT':
            return ('LEFTMOUSE', 'RIGHTMOUSE')
        elif addonMpref == 'RIGHT':
            return ('RIGHTMOUSE', 'LEFTMOUSE')

    # overide it if need smoothing
    def ToggleMeshSmooth(self):
        pass

    # set mesh segments dinamically
    def ChangeMeshSegments(self):
        pass

    # save values for later use
    def SaveLocalData(self):
        pass

    # create Qobject type
    def CreateQobject(self):
        pass

    def ChangeSnapSegments(self):
        allstep = int((self.mouse_pos[0] - self.mouseStart[0]) // self.inc_px)
        prevalue = max(1, min(8, self.snapClass.orig_edgediv + allstep))
        if prevalue != self.snapClass.edgediv:
            self.mouseEnd_x = self.mouseStart[0] + ((prevalue - self.snapClass.orig_edgediv) * self.inc_px)
            self.snapClass.edgediv = prevalue
            if self.snapClass.targetObject[0]:
                self.snapClass.UpdateSnapPoints()
                self.snapClass.closestPoint = None

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} and not self.snapClass.isSnapActive:
            # allow navigation
            return {'PASS_THROUGH'}

        if event.type == 'MIDDLEMOUSE':
            # allow navigation
            return {'PASS_THROUGH'}

        # click not allowed
        if event.type == self.mainMouse[0] and event.value == 'CLICK':
            return {'RUNNING_MODAL'}

        # pass through alt for maya camera control keys
        if event.type == self.mainMouse[0] and event.alt:
            return {'PASS_THROUGH'}

        # snap active
        if self.snapClass.isSnapActive:
            mcoord = event.mouse_region_x, event.mouse_region_y
            self.snapClass.CheckSnappingTarget(context, mcoord)

        if event.type == 'MOUSEMOVE':
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            # segments calculation
            if self.segkeyHold:
                self.ChangeMeshSegments()
            # edge div for snapping
            if self.snapSegHold:
                self.ChangeSnapSegments()

            # left mouse button down
            if self.lmb:
                if self.toolstage == 0:
                    # create object
                    self.qObject.CreateBObject()
                    # set object matrix
                    if self.snapClass.isPolyGridActive and self.snapClass.isSnapActive:
                        self.qObject.SetObjectMatrix(self.snapClass.gridMatrix, self.firstPoint)
                    else:
                        self.qObject.SetObjectMatrixVec(self.coordsys, self.firstPoint)
                    bpy.context.scene.update()
                    self.actMatrix = self.qObject.bObject.matrix_world.copy()
                    bpy.context.scene.update()
                    self.qObject.SelectObject()
                    self.qObject.bObject.hide_viewport = True
                    self.toolstage = 1

                elif self.toolstage == 1:
                    self.qObject.bObject.hide_viewport = False
                    # set second point
                    if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                        self.secondPoint = self.snapClass.GetClosestPointOnGrid(self.actMatrix)
                    else:
                        self.secondPoint = GetPlaneLocation(context, self.mouse_pos, self.actMatrix)
                    self.qObject.UpdateBase(self.firstPoint, self.secondPoint)

            elif self.toolstage == 2:
                # set height
                if not self.segkeyHold:
                    if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                        heightcoord = self.snapClass.closestPoint
                        mat_inv = self.actMatrix.inverted()
                        heightcoord = mat_inv @ heightcoord
                        heightcoord = heightcoord[2]
                    else:
                        heightcoord = GetHeightLocation(context, self.mouse_pos, self.actMatrix, self.secondPoint)
                    if self.isIncrement:
                        gridstep = context.space_data.overlay.grid_scale
                        heightcoord = math.floor((heightcoord / gridstep)) * gridstep
                    self.qObject.UpdateHeight(heightcoord)

        # left mouse click handling
        elif event.type == self.mainMouse[0]:
            # start object creation
            if event.value == 'PRESS':
                coord = event.mouse_region_x, event.mouse_region_y
                if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                    self.firstPoint = self.snapClass.closestPoint
                    self.coordsys = GetCoordSys(context, coord)
                else:
                    self.coordsys = GetCoordSys(context, coord)
                    self.firstPoint = self.coordsys[0]
                self.lmb = True
            # set height
            elif event.value == 'RELEASE':
                if self.toolstage == 1 and not self.qObject.basetype == 4 and not self.qObject.isFlat:
                    self.toolstage = 2
                else:
                    # finalize mesh scale and normals, create new class instance
                    self.qObject.FinalizeMeshData()
                    self.qObject = self.qObject.copyData(self)
                    bpy.ops.ed.undo_push(message="QObject Create")
                    self.toolstage = 0

                self.lmb = False

        # toggle base type
        if event.type == 'A' and event.value == 'PRESS':
                self.basetype = self.qObject.UpdateBaseType()

        # toggle centered
        if event.type == 'O' and event.value == 'PRESS':
                self.isCentered = self.qObject.ToggleMeshCenter()

        # toggle flat
        if event.type == 'H' and event.value == 'PRESS':
            if self.objectType != 3:
                self.isFlat = self.qObject.SwitchMeshType()
            else:
                self.isFlat = False

        # set snap segments with keyshold
        if event.type == 'F':
            if event.value == 'PRESS':
                if not self.snapSegHold:
                    self.mouseStart = (event.mouse_region_x, event.mouse_region_y)
                    self.mouseEnd_x = self.mouseStart[0]
                    self.snapClass.orig_edgediv = self.snapClass.edgediv
                    self.snapSegHold = True
            elif event.value == 'RELEASE':
                self.snapSegHold = False

        # toggle smooth mesh (virtual)
        if event.type == 'D' and event.value == 'PRESS':
            self.ToggleMeshSmooth()

        # set mesh segments (virtual)
        if event.type == 'S':
            if event.value == 'PRESS':
                if not self.segkeyHold:
                    self.mouseStart = (event.mouse_region_x, event.mouse_region_y)
                    self.mouseEnd_x = self.mouseStart[0]
                    self.qObject.originalSegments = self.qObject.meshSegments
                    self.segkeyHold = True
            elif event.value == 'RELEASE':
                self.segkeyHold = False

        if event.type == 'WHEELUPMOUSE' and self.snapClass.isSnapActive:
            mcoord = event.mouse_region_x, event.mouse_region_y
            if self.snapClass.edgediv < 8:
                self.snapClass.edgediv += 1
                if self.snapClass.targetObject[0]:
                    self.snapClass.UpdateSnapPoints()
                    self.snapClass.closestPoint = None

        if event.type == 'WHEELDOWNMOUSE' and self.snapClass.isSnapActive:
            mcoord = event.mouse_region_x, event.mouse_region_y
            if self.snapClass.edgediv > 1:
                self.snapClass.edgediv -= 1
                if self.snapClass.targetObject[0]:
                    self.snapClass.UpdateSnapPoints()
                    self.snapClass.closestPoint = None

        # toggle increments
        if event.type == 'LEFT_SHIFT':
            if event.value == 'PRESS':
                self.isIncrement = True
            elif event.value == 'RELEASE':
                self.isIncrement = False

        # toggle snap
        if event.type in {'LEFT_CTRL', 'RIGHT_CTRL'}:
            if event.value == 'PRESS':
                self.snapClass.SetState(True, self.mouse_pos)
            elif event.value == 'RELEASE':
                self.snapClass.SetState(False, self.mouse_pos)

        # activate snapgrid
        if event.type == 'X':
            if event.value == 'PRESS':
                self.snapClass.SetPolyGrid(True, self.mouse_pos)
            elif event.value == 'RELEASE':
                self.snapClass.SetPolyGrid(False, self.mouse_pos)

        # exit operator
        if event.type in {self.mainMouse[1], 'ESC'}:  # Cancel
            # delete object if creation not finished

            if self.toolstage != 0 and self.qObject:
                self.qObject.DeleteBObject()
                self.qObject.DeleteBMesh()
            else:
                self.qObject.DeleteBMesh()
            # save values for next use
            self.__class__.edgediv = self.snapClass.edgediv
            self.__class__.isFlat = self.isFlat
            self.__class__.isCentered = self.isCentered
            self.__class__.isSmooth = self.isSmooth
            self.__class__.meshSegments = self.qObject.meshSegments
            self.__class__.basetype = self.basetype
            self.SaveLocalData()
            # remove handlers, cleanup
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.snapClass.CleanUp()
            context.area.tag_redraw()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            preferences = context.preferences
            self.addon_prefs = preferences.addons[__package__].preferences
            # build shader for screespace draw
            self.snapClass = SnappingClass(self, context, self.edgediv)
            self.mainMouse = self.GetMainMouseButton(context)

            # add draw handler
            uidpi = int((72 * preferences.system.ui_scale))
            args = (self, context, uidpi, preferences.system.ui_scale)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(self.drawcallback, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)

            # set first mesh data
            self.CreateQobject()
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}
