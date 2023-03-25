from .op_mesh import MeshCreateOperator
from .qobjects.qcube import Qcube
from .draw_module import draw_callback_cube


# box create op new
class BoxCreateOperator(MeshCreateOperator):
    bl_idname = "object.box_create"
    bl_label = "Box Create Operator"

    drawcallback = draw_callback_cube
    objectType = 1

    # create Qobject tpye
    def CreateQobject(self):
        self.qObject = Qcube(self)
