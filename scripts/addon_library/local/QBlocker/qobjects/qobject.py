import bpy
import mathutils
import bmesh


def GetTransformOffset(isCentered):
    if isCentered:
        return mathutils.Matrix.Translation((0.0, 0.0, 0.0))
    else:
        return mathutils.Matrix.Translation((0.0, 0.0, 1.0))


class Qobject:
    bObject = None
    bMesh = None
    bMatrix = mathutils.Matrix()

    firstPoint = mathutils.Vector((0, 0, 0))
    secondPoint = mathutils.Vector((0, 0, 0))
    height = 0

    meshSegments = 16
    originalSegments = 16

    basetype = 1
    isFlat = False
    isCentered = False
    isSmooth = False
    isHidden = False
    saveSize = (0.0, 0.0, 0.0)

    # init class instance
    def __init__(self, _op):
        self.bMesh = bpy.data.meshes.new("ToolMesh")
        self.basetype = _op.basetype
        self.meshSegments = _op.meshSegments
        self.isFlat = _op.isFlat
        self.isCentered = _op.isCentered
        self.isSmooth = _op.isSmooth

    def copyData(self, _op):
        pass

    def CreateQBlock(self):
        pass

    def CreateBObject(self):
        self.bObject = bpy.data.objects.new("QBlock", self.bMesh)
        bpy.context.collection.objects.link(self.bObject)
        self.bMesh = self.bObject.data

        bpy.context.view_layer.update()
        self.bMatrix = self.bObject.matrix_world.copy()
        self.UpdateMesh()
        # put in local view
        spacedata = bpy.context.space_data
        if spacedata.local_view:
            self.bObject.local_view_set(spacedata, True)

    def DeleteBObject(self):
        if self.bObject:
            bpy.data.objects.remove(self.bObject, do_unlink=True)
            self.bObject = None

    def DeleteBMesh(self):
        if self.bMesh:
            bpy.data.meshes.remove(self.bMesh, do_unlink=True)
            self.bMesh = None

    # regenerate mesh geom (virtual)
    def UpdateMesh(self):
        pass

    # hide object for raycast ignore
    def HideObject(self, _state):
        if self.bObject:
            self.isHidden = _state
            self.bObject.hide_viewport = _state

    def SelectObject(self):
        bpy.ops.object.select_all(action='DESELECT')
        self.bObject.select_set(state=True)

    # change base type
    def UpdateBaseType(self):
        if self.basetype < 4:
            self.basetype += 1
        else:
            self.basetype = 1

        if self.bObject:
            self.UpdateBase(self.firstPoint, self.secondPoint)
        return self.basetype

    # set base type
    def SetBaseType(self, _type):
        self.basetype = _type
        return self.basetype

    # switch to alternative mesh type
    def SwitchMeshType(self):
        self.isFlat = (not self.isFlat)
        if self.bMesh:
            self.UpdateMesh()
        return self.isFlat

    # set base point, update scale
    def UpdateBase(self, _firstP, _secondP):
        # get corners
        self.firstPoint = _firstP
        self.secondPoint = _secondP
        # transform position by type
        if self.basetype == 1:
            self.TransformPtoP(self.bMatrix)
        elif self.basetype == 2:
            self.TransformCenter()
        elif self.basetype == 3:
            self.TransformUniformBase()
        elif self.basetype == 4:
            self.TransformUniformAll()

    # set height, update scale
    def UpdateHeight(self, _height):
        self.height = _height
        self.height = _height if self.isCentered else _height / 2
        self.bObject.scale[2] = self.height

    # apply scale, fix normals, set selection
    def FinalizeMeshData(self):
        if self.bObject:
            self.saveSize = mathutils.Vector(self.bObject.scale)
            activeOB = bpy.context.active_object
            if activeOB is None or activeOB.mode != 'EDIT':
                bpy.context.view_layer.objects.active = self.bObject
                bpy.ops.object.select_all(action='DESELECT')
                self.bObject.select_set(state=True)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True, properties=True)

            bm = bmesh.new()
            bm.from_mesh(self.bObject.data)

            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

            if activeOB is not None and activeOB.mode == 'EDIT':
                # transform mesh to world and edit mesh space
                bmesh.ops.transform(bm, matrix=self.bObject.matrix_world, space=self.bObject.matrix_world, verts=bm.verts)
                bmesh.ops.transform(bm, matrix=activeOB.matrix_world.inverted(), verts=bm.verts)
                bm.to_mesh(self.bObject.data)
                self.bObject.data.update()
                # add mesh to active object data
                activeObMesh = bmesh.from_edit_mesh(activeOB.data)
                activeObMesh.from_mesh(self.bObject.data)
                bmesh.update_edit_mesh(activeOB.data, loop_triangles=True, destructive=True)
                # delete qobject
                bpy.data.meshes.remove(self.bObject.data, do_unlink=True, do_id_user=True, do_ui_user=True)
                # bpy.data.objects.remove(self.bObject, do_unlink=True)
            else:
                bm.to_mesh(self.bObject.data)
                self.bObject.data.update()
                self.CreateQBlock()

            bm.clear()
            bm.free()

    # set scale for centering origin
    def ToggleMeshCenter(self):
        self.isCentered = (not self.isCentered)
        if self.bObject:
            if self.isCentered:
                if self.basetype != 4:
                    self.bObject.scale[2] *= 2
            else:
                if self.basetype != 4:
                    self.bObject.scale[2] /= 2
            self.UpdateMesh()
        return self.isCentered

    # smooth mesh faces toggle
    def ToggleSmoothFaces(self):
        self.isSmooth = not self.isSmooth
        self.bMesh.use_auto_smooth = self.isSmooth
        for face in self.bMesh.polygons:
            face.use_smooth = self.isSmooth
        return self.isSmooth

    # smooth mesh faces set
    def SetSmoothFaces(self):
        self.bMesh.use_auto_smooth = self.isSmooth
        for face in self.bMesh.polygons:
            face.use_smooth = self.isSmooth
        return self.isSmooth

    # ===== Set Object Matrix ===== #

    # apply matrix and position
    def SetMatrix(self, _matrix):
        self.bObject.matrix_world = _matrix
        # bpy.context.scene.update()
        bpy.context.view_layer.update()
        self.bMatrix = self.bObject.matrix_world.copy()

    # ===== Object Base Positioning ===== #

    # corner to corner positioning
    def TransformPtoP(self, _matrix):
        secondPoint_W = _matrix @ self.secondPoint
        self.bObject.location = (self.firstPoint + secondPoint_W) / 2.0
        self.bObject.scale = (abs(self.secondPoint.x) / 2.0, abs(self.secondPoint.y) / 2.0, self.height)

    # center position, separated axis
    def TransformCenter(self):
        self.bObject.location = self.firstPoint
        self.bObject.scale = (abs(self.secondPoint.x), abs(self.secondPoint.y), self.height)

    # center position, uniform base axis
    def TransformUniformBase(self):
        self.bObject.location = self.firstPoint
        pointXabs = abs(self.secondPoint.x)
        pointYabs = abs(self.secondPoint.y)
        if pointYabs < pointXabs:
            self.bObject.scale = (pointXabs, pointXabs, self.height)
        else:
            self.bObject.scale = (pointYabs, pointYabs, self.height)

    # center position, uniform all axis
    def TransformUniformAll(self):
        self.bObject.location = self.firstPoint
        pointXabs = abs(self.secondPoint.x)
        pointYabs = abs(self.secondPoint.y)
        if pointYabs < pointXabs:
            self.bObject.scale = (pointXabs, pointXabs, pointXabs)
        else:
            self.bObject.scale = (pointYabs, pointYabs, pointYabs)
