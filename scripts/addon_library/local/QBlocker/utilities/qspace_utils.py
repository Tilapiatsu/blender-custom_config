import mathutils
import numpy


def Distance(pointA, pointB, _norm=numpy.linalg.norm):
    return _norm(pointA - pointB)


def VecToMatrix(_vecZ, _pos):
    vecZ = _vecZ.normalized()
    if abs(vecZ[2]) == 1:
        vecY = vecZ.cross(mathutils.Vector((1.0, 0.0, 0.0)))
    else:
        vecY = vecZ.cross(mathutils.Vector((0.0, 0.0, -1.0)))
    vecY.normalize()
    vecX = vecY.cross(vecZ)
    vecX.normalize()

    matrix = mathutils.Matrix()
    matrix[0].xyz = vecX[0], vecY[0], vecZ[0]
    matrix[1].xyz = vecX[1], vecY[1], vecZ[1]
    matrix[2].xyz = vecX[2], vecY[2], vecZ[2]
    matrix.translation = _pos
    return matrix
