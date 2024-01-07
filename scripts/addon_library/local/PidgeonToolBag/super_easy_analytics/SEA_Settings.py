import bpy

from bpy.types import (
    PropertyGroup,
)

from bpy.props import (
    BoolProperty,
)

class SEA_Settings(PropertyGroup):

    ## General ##

    # Show Panels

    show_dummy: BoolProperty(
        default=True,
    )


# Register

classes = (
    SEA_Settings,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sea_settings = bpy.props.PointerProperty(type=SEA_Settings)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

    try:
        del bpy.types.Scene.sea_settings
    except:
        pass
