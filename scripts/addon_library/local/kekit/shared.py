import bpy
from .ops.ke_weight_toggle import KeWeightToggle

classes = (
    KeWeightToggle,
)

# Room For future ops that is shared by modules ('global' ops)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
