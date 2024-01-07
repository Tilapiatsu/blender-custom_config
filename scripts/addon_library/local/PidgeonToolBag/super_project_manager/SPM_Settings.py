import bpy
from bpy.props import (
    BoolProperty,
)
import typing

class AddonPreferences():
    previous_set: str
    custom_folders: typing.List['ProjectFolderProps']
    automatic_folders: typing.List['ProjectFolderProps']
    project_paths: list
    active_project_path: int
    layout_tab: tuple
    folder_structure_sets: str
    prefix_with_project_name: bool
    auto_set_render_outputpath: bool
    default_project_location: str
    save_folder: tuple
    preview_subfolders: bool

class ProjectFolderProps():

    render_outputpath: bool
    """If this folder input is used for setting the output path for your renders,
    defaults to False)"""

    folder_name: str
    """The folder name/path for a folder.
    defaults to ''"""

class SPM_Settings(bpy.types.PropertyGroup):

    ## General ##

    render_path: bpy.props.StringProperty(
        name="Render Path",
        description="The path where the tiles will be rendered to.",
        default = "//SRR/",
        subtype='DIR_PATH',
    )

    # Show Panels

    show_main: BoolProperty(
        default=True,
    )

    show_general: BoolProperty(
        default=True,
    )

    show_folders: BoolProperty(
        default=True,
    )

    show_project_starter: BoolProperty(
        default=True,
    )


# Register

classes = (
    SPM_Settings,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.spm_settings = bpy.props.PointerProperty(type=SPM_Settings)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

    try:
        del bpy.types.Scene.spm_settings
    except:
        pass