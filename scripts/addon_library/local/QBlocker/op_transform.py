import bpy

import math
import mathutils

from .snap_module import *
from .draw_module import *
from .utilities.raycast_utils import GetPlaneLocation, GetHeightLocation
from .qspace import *
from .qwplane import WorkingPlane
from .draw_module import draw_callback_transform


class ActObjects():
    bObject = None
    origPosList = []
    objectList = []
    offsetList = []
    offsetMList = []

    def __init__(self, _objectList=[]):
        self.bObject = None
        self.objectList = _objectList

    def HideObject(self, _state):
        for ob in self.objectList:
            ob.hide_viewport = _state

    def SetObject(self, _objects, _pos):
        self.objectList.extend(_objects)
        for ob in _objects:
            self.origPosList.append(ob.location)
            self.offsetList.append(ob.location - _pos)

    def CalcOffset(self, _pos):
        self.offsetList = []
        for ob in self.objectList:
            self.offsetList.append(ob.location - _pos)
        # print(self.offsetList)

    def CalcMatrixOffset(self, _matrix):
        self.offsetMList = []
        for ob in self.objectList:
            self.offsetMList.append(_matrix.inverted() @ ob.matrix_world)

    def SetPosition(self, _pos):
        id = 0
        for ob in self.objectList:
            ob.location = _pos + self.offsetList[id]
            id += 1

    def SetTransform(self, _matrix):
        mat_rot = mathutils.Matrix.Rotation(math.radians(180.0), 4, 'X')
        id = 0
        for ob in self.objectList:
            ob.matrix_world = _matrix @ mat_rot @ self.offsetMList[id]
            id += 1

    def SelectObjects(self):
        for ob in self.objectList:
            ob.select_set(True)


# box create op new
class ObjectTransformOperator(bpy.types.Operator):
    bl_idname = "object.qtransform"
    bl_label = "Transform objects"
    bl_context = "objectmode"
    bl_options = {'REGISTER', 'UNDO'}

    addon_prefs = None

    drawcallback = draw_callback_transform
    mainMouse = None
    wMatrix = mathutils.Matrix()

    toolstage = 0

    firstPoint = None
    secondPoint = None

    mouse_pos = (0, 0)

    # classes
    qObject = None
    snapClass = None
    coordsysClass = None
    workingplane = None

    # for save to reuse
    isWorkingPlane = False
    isOriented = False
    isWplane = False
    isHelpDraw = True
    edgediv = 2
    object_ignorebehind = 'ALL'
    lastobject_ignorebehind = 'ALL'
    last_isHelpDraw = True

    mouseStart = [0, 0]
    mouseEnd_x = 0
    inc_px = 30

    snapSegHold = False
    wPlaneHold = False
    mScrolled = False

    # set mouse buttons based on preferences
    def GetMainMouseButton(self):
        addonMpref = self.addon_prefs.mouse_enum
        if addonMpref == 'LEFT':
            return ('LEFTMOUSE', 'RIGHTMOUSE')
        elif addonMpref == 'RIGHT':
            return ('RIGHTMOUSE', 'LEFTMOUSE')

    # create Qobject type
    def CreateQobject(self):
        pass

    def ChangeSnapSegments(self):
        allstep = int((self.mouse_pos[0] - self.mouseStart[0]) // self.inc_px)
        prevalue = max(1, min(10, self.snapClass.orig_edgediv + allstep))
        if prevalue != self.snapClass.edgediv:
            self.mouseEnd_x = self.mouseStart[0] + ((prevalue - self.snapClass.orig_edgediv) * self.inc_px)
            self.snapClass.SetSnapPoints(self.mouse_pos, prevalue)

    # Stage One: create object set matrix
    def Stage_One(self, _context):
        self.wMatrix = self.coordsysClass.GetCoordSys(_context, self.mouse_pos, self.isOriented)
        if self.coordsysClass.lastHitresult[0]:
            # check if snap. Set matrix and first point
            if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                self.firstPoint = self.snapClass.closestPoint
                self.wMatrix.translation = self.firstPoint
            else:
                self.firstPoint = self.wMatrix.to_translation()

            # collect object if nothing selected
            if len(self.qObject.objectList) == 0:
                self.qObject.SetObject([self.coordsysClass.lastHitresult[4]], self.firstPoint)
            else:
                #self.qObject.CalcOffset(self.firstPoint)
                self.qObject.CalcMatrixOffset(self.wMatrix)

            # set object matrix
            bpy.context.view_layer.update()
            self.qObject.HideObject(True)
        else:
            self.toolstage = 0

    # Stage Two: set base
    def Stage_Two(self, _context, _event):
        self.qObject.HideObject(False)
        # set second position point on grid or object.
        if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
            self.secondPoint = self.snapClass.closestPoint
        else:
            self.secondPoint = self.wMatrix.to_translation()
        # self.qObject.HideObject(True)
        # self.qObject.SetPosition(self.secondPoint)
        self.qObject.SetTransform(self.wMatrix)

    # main operator loop
    def modal(self, context, event):
        context.area.tag_redraw()

        # allow navigation
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        # click not allowed
        if event.type == self.mainMouse[0] and event.value == 'CLICK':
            return {'RUNNING_MODAL'}

        # pass through alt for maya camera control keys
        if event.type == self.mainMouse[0] and event.alt:
            return {'PASS_THROUGH'}

        # snap active
        if self.snapClass.isSnapActive:
            self.snapClass.CheckSnappingTarget(self.mouse_pos)
        if self.toolstage != 0:
            self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)

        # mouse move event handling
        if event.type == 'MOUSEMOVE':
            # get act mouse pos
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)

            # edge div for snapping
            if self.snapSegHold and not self.mScrolled:
                self.ChangeSnapSegments()

            # of adjust working plane size
            if self.wPlaneHold and event.ctrl and self.isWorkingPlane:
                hMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)
                if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                    hMatrix.translation = self.snapClass.closestPoint
                self.workingplane.SetGridSize(hMatrix)

            # refresh matrix while moving mouse in 0 stage
            elif self.toolstage == 0 and not self.wPlaneHold:
                self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)

            # set second point (mouse move stage)
            elif self.toolstage == 2:
                self.Stage_Two(context, event)

        # left mouse click handling
        elif event.type == self.mainMouse[0] and not self.wPlaneHold:
            # pick object
            if event.value == 'PRESS':
                self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
                # first stage (grab object)
                if self.toolstage == 0:
                    self.Stage_One(context)
                    print("stage one end")
                    self.toolstage = 2
            # release object
            elif event.value == 'RELEASE':
                # if just mouseclick reset state
                # TODO put down object
                print("tool loop end")
                bpy.ops.ed.undo_push(message="QObject Create")
                self.coordsysClass.ToggleAxis(True)
                self.qObject.SelectObjects()
                self.toolstage = 0

        # toggle help text
        if event.type == 'F1' and event.value == 'PRESS':
            self.isHelpDraw = not self.isHelpDraw

        # toggle matrix orientation
        elif event.type == 'Q' and event.value == 'PRESS':
            self.isOriented = not self.isOriented
            self.coordsysClass.ResetResult()
            self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)

        # set snap segments with keyhold
        if event.type == 'C':
            if event.value == 'PRESS':
                if not self.snapSegHold:
                    self.mScrolled = False
                    self.mouseStart = (event.mouse_region_x, event.mouse_region_y)
                    self.mouseEnd_x = self.mouseStart[0]
                    self.snapClass.orig_edgediv = self.snapClass.edgediv
                    self.snapSegHold = True
            elif event.value == 'RELEASE':
                self.snapSegHold = False
                self.mScrolled = False

        # set working plane
        if event.type == 'W' and self.toolstage == 0:
            if event.value == 'PRESS':
                # RESET : if shift key hold, reset working plane to system grid size
                if event.shift and self.isWorkingPlane:
                    self.workingplane.ResetSize(context)
                # SET FIRST : if w not hold set matrix and turn on wplane (it need to avoid repeated press event call)
                elif not self.wPlaneHold:
                    # turn on if exist
                    if not self.isWorkingPlane:
                        hMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)
                        if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                            hMatrix.translation = self.snapClass.closestPoint
                        self.workingplane.SetMatrix(hMatrix)
                        self.workingplane.SetActive(context, True)
                        self.isWorkingPlane = True
                        self.wPlaneHold = True
                    # only turn on size tweak with mouse
                    elif event.ctrl:
                        self.wPlaneHold = True
                    # turn off if exist
                    else:
                        self.workingplane.SetActive(context, False)
                        self.isWorkingPlane = False
            elif event.value == 'RELEASE':
                self.wPlaneHold = False

        # set ignore tpye
        elif event.type == 'E' and event.value == 'PRESS':
            if self.object_ignorebehind == 'ALL':
                self.object_ignorebehind = 'FRONT'
            elif self.object_ignorebehind == 'FRONT':
                self.object_ignorebehind = 'GRID'
            else:
                self.object_ignorebehind = 'ALL'
            self.coordsysClass.ResetResult()
            self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)

        # increase snap points
        if event.type == 'WHEELUPMOUSE':
            if self.snapSegHold:
                self.mScrolled = True
                self.snapClass.ChangeSnapPoints(self.mouse_pos, 1)
            else:
                self.coordsysClass.ResetResult()
                self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)
                return {'PASS_THROUGH'}

        # decrease snap points
        if event.type == 'WHEELDOWNMOUSE':
            if self.snapSegHold:
                self.mScrolled = True
                self.snapClass.ChangeSnapPoints(self.mouse_pos, -1)
            else:
                self.coordsysClass.ResetResult()
                self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)
                return {'PASS_THROUGH'}

        # toggle snap
        if event.type in {'Y', 'Z'} and event.value == 'PRESS':
            self.snapClass.ToggleState(self.mouse_pos, 1)

        if event.type == 'X' and event.value == 'PRESS':
            self.snapClass.ToggleState(self.mouse_pos, 2)

        # exit operator
        if event.type in {self.mainMouse[1], 'ESC'}:  # Cancel
            # save values for next use
            self.__class__.edgediv = self.snapClass.edgediv
            self.__class__.isOriented = self.isOriented
            self.__class__.isHelpDraw = self.isHelpDraw
            self.__class__.lastobject_ignorebehind = self.addon_prefs.object_ignorebehind
            self.__class__.last_isHelpDraw = self.addon_prefs.ishelp
            # remove handlers, cleanup
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.snapClass.CleanUp()
            self.coordsysClass.CleanUp()
            self.workingplane.wasActive = self.workingplane.isActive
            if self.workingplane.isActive:
                self.workingplane.SetActive(context, False)
            context.area.tag_redraw()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            preferences = context.preferences
            self.addon_prefs = preferences.addons[__package__].preferences
            # Instantiate modul classes
            self.coordsysClass = CoordSysClass(context, self, self.addon_prefs.axis_bool, self.addon_prefs)
            self.snapClass = SnappingClass(self, self.coordsysClass, context, self.edgediv, self.addon_prefs)
            self.mainMouse = self.GetMainMouseButton()
            # Get Working Plane
            self.workingplane = WorkingPlane.InvokeClass(context, self.addon_prefs)
            self.isWorkingPlane = self.workingplane.wasActive
            """
            if not WorkingPlane.Instance:
                WorkingPlane.Instance = WorkingPlane(context, mathutils.Matrix(), self.addon_prefs)
            self.workingplane = WorkingPlane.Instance
            if self.workingplane.wasActive:
                self.workingplane.numSteps = self.addon_prefs.grid_count
                self.workingplane.gridcolor = self.addon_prefs.grid_color
                self.isWorkingPlane = True
                self.workingplane.SetActive(context, True)
            """
            # gridhit reload
            if self.lastobject_ignorebehind != self.addon_prefs.object_ignorebehind:
                self.object_ignorebehind = self.addon_prefs.object_ignorebehind
                self.lastobject_ignorebehind = self.addon_prefs.object_ignorebehind
            # Default help state
            if self.last_isHelpDraw != self.addon_prefs.ishelp:
                self.isHelpDraw = self.addon_prefs.ishelp
                self.last_isHelpDraw = self.addon_prefs.ishelp
            # add draw handler
            uidpi = int((72 * preferences.system.ui_scale))
            uifactor = preferences.system.ui_scale * (self.addon_prefs.text_size_int / 14)
            args = (self, context, uidpi, uifactor, self.addon_prefs)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(self.drawcallback, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)

            # get object selection
            self.qObject = ActObjects(bpy.context.selected_objects)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}
