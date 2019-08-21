import bpy
import bmesh
import gpu
from .op_mesh import *
from .qpyramid import *


# box create op new
class PyramidCreateOperator(MeshCreateOperator):
    bl_idname = "object.pyramid_create"
    bl_label = "Pyramid Create Operator"

    drawcallback = draw_callback_cube
    objectType = 1

    # create Qobject tpye
    def CreateQobject(self):
        self.qObject = Qpyramid(self)
