import bpy

from bpy.types import (
    PropertyGroup,
)

from bpy.props import (
    BoolProperty,
)

class SRS_Settings(PropertyGroup):

    ## General ##

    # Show Panels

    show_dummy: BoolProperty(
        default=True,
    )


# Register

classes = (
    SRS_Settings,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.srs_settings = bpy.props.PointerProperty(type=SRS_Settings)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

    try:
        del bpy.types.Scene.srs_settings
    except:
        pass
