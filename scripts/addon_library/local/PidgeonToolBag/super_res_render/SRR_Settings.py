import bpy

from bpy.types import (
    PropertyGroup,
)

from bpy.props import (
    EnumProperty,
    BoolProperty,
    PointerProperty,
    IntProperty,
    FloatProperty,
)

class SRR_RenderStatus(PropertyGroup):
    # private state
    is_rendering: BoolProperty(
        name="Rendering",
        description="Currently rendering",
        default=False,
        options=set(), # Not animatable!
    )

    should_stop: BoolProperty(
        name="Stop",
        description="User requested stop",
        default=False,
        options=set(), # Not animatable!
    )

    tiles_total: IntProperty(
        name="Total Tiles",
        description="Total number of tiles to render",
        options=set(), # Not animatable!
        )

    tiles_done: IntProperty(
        name="Tiles Done",
        description="Number of tiles rendered",
        options=set(), # Not animatable!
        )

    percent_complete: FloatProperty(
        name="%",
        description="Percentage of tiles rendered",
        subtype='PERCENTAGE',
        min=0,
        max=100,
        options=set(), # Not animatable!
        get=(lambda self: 0 if self.tiles_total == 0 else 100 * self.tiles_done / self.tiles_total),
        set=(lambda self, value: None),
    )

RENDER_METHODS = (
    ('camshift', "Camera shift", "Break the image into tiles using camera shift"),
    ('border', "Render border", "Break the image into tiles using render border regions"),
    ('camsplit', "Split camera", "Subdivide the camera, creating a new camera for each tile"),
)

SUBDIVISION_SIZES = (
    ('1', "2 x 2", "Break the render into 2 x 2 tiles"),
    ('2', "4 x 4", "Break the render into 4 x 4 tiles"),
    ('3', "8 x 8", "Break the render into 8 x 8 tiles"),
    ('4', "16 x 16", "Break the render into 16 x 16 tiles"),
)

class SRR_Settings(PropertyGroup):

    ## General ##

    render_method: EnumProperty(
        name="Method",
        items=RENDER_METHODS,
        default='camshift',
        description="Method used to divide image into tiles while rendering",
        options=set(), # Not animatable!
    )

    render_path: bpy.props.StringProperty(
        name="Render Path",
        description="The path where the tiles will be rendered to.",
        default = "//SRR/",
        subtype='DIR_PATH',
    )

    subdivisions: EnumProperty(
        name="Tiles",
        items=SUBDIVISION_SIZES,
        default='1',
        description="Subdivisions of rendered image into tiles",
        options=set(), # Not animatable!
    )

    status: PointerProperty(
        name="Status",
        type=SRR_RenderStatus,
        options=set(), # Not animatable!
    )

    start_tile: IntProperty(
        name="Start Tile",
        description="The Tile it starts rendering from.",
        default = 1,
        min = 1,
        max = 256,
    )

    # Show Panels

    show_general: BoolProperty(
        default=True,
    )

    show_info: BoolProperty(
        default=True,
    )


# Register

classes = (
    SRR_RenderStatus,
    SRR_Settings,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.srr_settings = bpy.props.PointerProperty(type=SRR_Settings)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

    try:
        del bpy.types.Scene.srr_settings
    except:
        pass