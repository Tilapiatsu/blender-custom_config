import bpy
from .ops.ke_weight_toggle import KeWeightToggle

classes = (
    KeWeightToggle,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
