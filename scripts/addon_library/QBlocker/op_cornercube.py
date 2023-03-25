import bpy
import bmesh
import gpu
from .op_mesh import *
from .qobjects.qcornercube import *


# box create op new
class CornerCubeCreateOperator(MeshCreateOperator):
    bl_idname = "object.cornercube_create"
    bl_label = "Corner Cube Create Operator"

    drawcallback = draw_callback_cube
    objectType = 1

    # create Qobject tpye
    def CreateQobject(self):
        self.qObject = QCornercube(self)
