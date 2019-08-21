import bpy
# import bmesh
# import gpu
import math
# import copy
from .snap_module import *
from .draw_module import *
from .utilities.raycast_utils import *
from .qspace import *
from .qwplane import *

# box create op new
class MeshCreateOperator(bpy.types.Operator):
    bl_idname = ""
    bl_label = ""
    bl_context = "objectmode"

    addon_prefs = None

    drawcallback = None
    mainMouse = None
    wMatrix = mathutils.Matrix()

    objectType = 1
    basetype = 1

    toolstage = 0

    firstPoint = None
    secondPoint = None

    mouse_pos = (0, 0)

    # classes
    qObject = None
    snapClass = None
    coordsysClass = None
    workingplane = None

    snapSegHold = False
    wPlaneHold = False


    # for save to reuse
    isWorkingPlane = False
    isSmooth = False
    isCentered = False
    isIncrement = False
    isFlat = False
    isOriented = False
    isWplane = False
    meshSegments = 0
    lastdefmeshSegs = 0
    edgediv = 2

    mouseStart = [0, 0]
    mouseEnd_x = 0
    inc_px = 30

    segkeyHold = False
    ckeyHold = False

    # set mouse buttons based on preferences
    def GetMainMouseButton(self):
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

    # create Qobject type
    def CreateQobject(self):
        pass

    def ChangeSnapSegments(self):
        allstep = int((self.mouse_pos[0] - self.mouseStart[0]) // self.inc_px)
        prevalue = max(1, min(10, self.snapClass.orig_edgediv + allstep))
        if prevalue != self.snapClass.edgediv:
            self.mouseEnd_x = self.mouseStart[0] + ((prevalue - self.snapClass.orig_edgediv) * self.inc_px)
            self.snapClass.edgediv = prevalue
            self.snapClass.CheckSnappingTarget(self.mouse_pos)
            self.snapClass.closestPoint = None

    # Stage One: create object set matrix 
    def Stage_One(self, _context):
        self.wMatrix = self.coordsysClass.GetCoordSys(_context, self.mouse_pos, self.isOriented)
        # check if snap. Set matrix and first point
        if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
            self.firstPoint = self.snapClass.closestPoint
            self.wMatrix.translation = self.firstPoint
        else:           
            self.firstPoint = self.wMatrix.to_translation()
        # create object
        self.qObject.CreateBObject()
        # set object matrix
        if self.snapClass.snapState == 2:
            self.qObject.SetMatrix(self.wMatrix)
        else:
            self.qObject.SetMatrix(self.wMatrix)
        # bpy.context.scene.update()
        bpy.context.view_layer.update()
        self.qObject.SelectObject()
        self.qObject.bObject.hide_viewport = True

    # Stage Two: set base
    def Stage_Two(self, _context, _event):
        self.qObject.bObject.hide_viewport = False
        # change base type with ctrl and shift
        if _event.ctrl and not _event.shift:
            self.basetype = self.qObject.SetBaseType(2)
        elif not _event.ctrl and _event.shift:
            self.basetype = self.qObject.SetBaseType(3)
        elif _event.ctrl and _event.shift:  
            self.basetype = self.qObject.SetBaseType(4)  
        else:
            self.basetype = self.qObject.SetBaseType(1)

        if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
            self.secondPoint = self.snapClass.GetClosestPointOnGrid(self.qObject.bMatrix)
        else:
            self.secondPoint = GetPlaneLocation(_context, self.mouse_pos, self.qObject.bMatrix)

        self.qObject.UpdateBase(self.firstPoint, self.secondPoint)

    # Stage Three: set height
    def Stage_Height(self, _context):
        if not self.segkeyHold:
            if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                mat_inv = self.qObject.bMatrix.inverted()
                heightcoord = mat_inv @ self.snapClass.closestPoint
                heightcoord = heightcoord[2]
            else:
                heightcoord = GetHeightLocation(_context, self.mouse_pos, self.qObject.bMatrix, self.secondPoint)
            if self.isIncrement:
                gridstep = _context.space_data.overlay.grid_scale
                heightcoord = math.floor((heightcoord / gridstep)) * gridstep
            self.qObject.UpdateHeight(heightcoord)

    # main operator loop
    def modal(self, context, event):
        context.area.tag_redraw()

        # allow navigation
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        # click not allowed
        if event.type == self.mainMouse[0] and event.value == 'CLICK':
            print("mouseclick")
            return {'RUNNING_MODAL'}

        # pass through alt for maya camera control keys
        if event.type == self.mainMouse[0] and event.alt:
            return {'PASS_THROUGH'}

        # snap active
        if self.snapClass.isSnapActive:
            if self.toolstage != 0:
                self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)
            self.snapClass.CheckSnappingTarget(self.mouse_pos)

        # mouse move event handling
        if event.type == 'MOUSEMOVE':
            # get act mouse pos
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
           
            # segments calculation
            if self.segkeyHold:
                self.ChangeMeshSegments()

            # edge div for snapping
            elif self.snapSegHold: 
                self.ChangeSnapSegments()

            # refresh matrix while moving mouse in 0 stage
            elif self.toolstage == 0 and not self.wPlaneHold:
                self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)
                 # change base type with ctrl and shift
                if event.ctrl and not event.shift:
                    self.basetype = self.qObject.SetBaseType(2)
                elif not event.ctrl and event.shift:
                    self.basetype = self.qObject.SetBaseType(3)
                elif event.ctrl and event.shift:  
                    self.basetype = self.qObject.SetBaseType(4)  
                else:
                    self.basetype = self.qObject.SetBaseType(1)

            # set second point (mouse move stage)
            elif self.toolstage == 2:
                self.Stage_Two(context, event)

            # set height (mouse move stage)
            elif self.toolstage == 3:
                self.Stage_Height(context)

        # left mouse click handling
        elif event.type == self.mainMouse[0]:
            if event.value == 'PRESS':
                coord = event.mouse_region_x, event.mouse_region_y       
                # first stage (create object and matrix)
                if self.toolstage == 0:
                    self.Stage_One(context)
                    self.toolstage = 2
                # last stage end
                elif self.toolstage == 3:
                    self.toolstage = 0
            # set height
            elif event.value == 'RELEASE':
                # if just mouseclick reset state
                if self.toolstage == 2 and not self.secondPoint:
                    self.qObject.DeleteBObject()
                    self.secondPoint = None
                    self.firstPoint = None
                    self.coordsysClass.ToggleAxis(True)
                    self.toolstage = 0
                # skip height stage if Uniform All
                elif self.toolstage == 2 and not self.qObject.basetype == 4 and not self.qObject.isFlat:
                    self.coordsysClass.ToggleAxis(False)
                    self.toolstage = 3
                else:
                    # finalize mesh scale and normals, create new class instance
                    self.qObject.FinalizeMeshData()
                    self.qObject = self.qObject.copyData(self)
                    bpy.ops.ed.undo_push(message="QObject Create")
                    self.secondPoint = None
                    self.firstPoint = None
                    self.coordsysClass.ToggleAxis(True)
                    self.toolstage = 0


        # toggle matrix orientation
        if event.type == 'Q' and event.value == 'PRESS':
                self.isOriented = not self.isOriented
                self.coordsysClass.ResetResult()
                self.wMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)

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

        # set working plane
        if event.type == 'W':
            if event.value == 'PRESS':
                if self.isWorkingPlane:
                    self.workingplane.SetActive(context, False)
                    self.isWorkingPlane = False
                else:
                    hMatrix = self.coordsysClass.GetCoordSys(context, self.mouse_pos, self.isOriented)
                    if self.snapClass.isSnapActive and self.snapClass.closestPoint is not None:
                        hMatrix.translation = self.snapClass.closestPoint
                    self.workingplane.SetMatrix(hMatrix)
                    self.workingplane.SetActive(context, True)
                    self.isWorkingPlane = True
                self.wPlaneHold = True
            elif event.value == 'RELEASE':
                self.wPlaneHold = False

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

        # hold for snap point change (need to save this value for the other events)
        if event.type == 'C':
            if event.value == 'PRESS':
                self.ckeyHold = True
            elif event.value == 'RELEASE':    
                self.ckeyHold = False

        # increase snap points
        if event.type == 'WHEELUPMOUSE':
            if self.ckeyHold:
                self.snapClass.ChangeSnapPoints(self.mouse_pos, 1)
            else:
                return {'PASS_THROUGH'}

        # decrease snap points
        if event.type == 'WHEELDOWNMOUSE':
            if self.ckeyHold:
                self.snapClass.ChangeSnapPoints(self.mouse_pos, -1)
            else:
                return {'PASS_THROUGH'}

        # toggle increments
        if event.type == 'LEFT_SHIFT' and self.toolstage == 3:
            if event.value == 'PRESS':
                self.isIncrement = True
            elif event.value == 'RELEASE':
                self.isIncrement = False

        # toggle snap
        if event.type in {'Y', 'Z'} and event.value == 'PRESS':
            self.snapClass.ToggleState(self.mouse_pos, 1)  

        if event.type == 'X' and event.value == 'PRESS':
            self.snapClass.ToggleState(self.mouse_pos, 2)  

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
            self.__class__.isOriented = self.isOriented
            self.__class__.lastdefmeshSegs = self.addon_prefs.segs_int
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
            self.coordsysClass = CoordSysClass(context, self, self.addon_prefs.axis_bool)
            self.snapClass = SnappingClass(self, self.coordsysClass, context, self.edgediv, self.addon_prefs.snap_dist)
            self.mainMouse = self.GetMainMouseButton()
            # Handle Working Plane
            if not WorkingPlane.Instance:
                WorkingPlane.Instance = WorkingPlane(context, mathutils.Matrix())
            self.workingplane = WorkingPlane.Instance
            if self.workingplane.wasActive:
                self.isWorkingPlane = True
                self.workingplane.SetActive(context, True)
            # Mesh segment reload
            if self.lastdefmeshSegs != self.addon_prefs.segs_int:
                self.meshSegments = self.addon_prefs.segs_int
                self.lastdefmeshSegs = self.addon_prefs.segs_int
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
