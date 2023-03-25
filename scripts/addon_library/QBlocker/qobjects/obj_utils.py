import mathutils


def Create_ScaleMatrix(size):
    mat_scaleX = mathutils.Matrix.Scale(size[0], 4, (1.0, 0.0, 0.0))
    mat_scaleY = mathutils.Matrix.Scale(size[1], 4, (0.0, 1.0, 0.0))
    mat_scaleZ = mathutils.Matrix.Scale(size[2], 4, (0.0, 0.0, 1.0))
    return (mat_scaleX @ mat_scaleY @ mat_scaleZ)


def SetSmoothFaces(bMesh):
    bMesh.use_auto_smooth = True
    for face in bMesh.polygons:
        face.use_smooth = True
