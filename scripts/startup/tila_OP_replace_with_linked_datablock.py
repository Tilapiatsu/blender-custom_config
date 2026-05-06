bl_info = {
    "name": "Link Datablocks From Blend",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Outliner > Context Menu",
    "description": "Replace selected datablocks with linked versions from another .blend file",
    "category": "Outliner",
}

import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


# ----------------------------------------------------------
# Utilities
# ----------------------------------------------------------

SUPPORTED_DATATYPE = [
    "actions",
    "annotations",
    "armatures",
    "brushes",
    "cameras",
    "collections",
    "curves",
    "fonts",
    "grease_pencils",
    "hair_curves",
    "images",
    "lattices",
    "libraries",
    "lightprobes",
    "lights",
    "linestyles",
    "masks",
    "materials",
    "meshes",
    "metaballs",
    "movieclips",
    "node_groups",
    "objects",
    "paint_curves",
    "palettes",
    "particles",
    "pointclouds",
    "scenes",
    "screens",
    "shape_keys",
    "sounds",
    "speakers",
    "texts",
    "textures",
    "volumes",
    "window_managers",
    "workspaces",
    "worlds",
]


def conform_path(path):
    return os.path.normpath(bpy.path.abspath(path))


def get_library_folder(idblock):
    name = idblock.name
    for d in SUPPORTED_DATATYPE:
        data_type = getattr(bpy.data, d, None)
        if data_type is not None:
            if name in data_type.keys():
                return d
    return None


def find_selected_ids(context):
    """
    Outliner selected IDs.
    Works in recent Blender versions.
    """
    ids = []

    if hasattr(context, "selected_ids"):
        ids.extend(context.selected_ids)

    # remove duplicates
    unique = []
    seen = set()

    for x in ids:
        ptr = x.as_pointer()
        if ptr not in seen:
            unique.append(x)
            seen.add(ptr)

    return unique


def load_linked_id(filepath, folder_name, datablock_name):
    """
    Link one datablock by name from external blend.
    """
    with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
        available = getattr(data_from, folder_name, None)

        if datablock_name not in available:
            return None

        # assign destination list
        setattr(data_to, folder_name, [datablock_name])

    # fetch newly linked datablock
    db = getattr(bpy.data, folder_name, None)
    if db is not None:
        linked = [
            d
            for d in db
            if d.library is not None and d.name == datablock_name and conform_path(d.library.filepath) == filepath
        ]

        if not len(linked):
            return None

        return linked[0]


def replace_id_references(data_name, old_id, new_id):
    """
    Replace all usages of old_id by new_id.
    """
    try:
        old_id.user_remap(new_id)
        print("replacing ", old_id.name)

        data = getattr(bpy.data, data_name, None)

        if data is not None:
            data.remove(old_id)

    except Exception as e:
        print("Remap failed:", e)


# ----------------------------------------------------------
# Operator
# ----------------------------------------------------------


class OUTLINER_OT_relink_selected_from_blend(Operator, ImportHelper):
    bl_idname = "outliner.relink_selected_from_blend"
    bl_label = "Replace By Linked Datablock"
    bl_description = "Replace selected datablocks by linked versions from another .blend file"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".blend"
    filter_glob: StringProperty(default="*.blend", options={"HIDDEN"})

    def execute(self, context):
        filepath = self.filepath

        if not os.path.exists(filepath):
            self.report({"ERROR"}, "File not found")
            return {"CANCELLED"}

        ids = find_selected_ids(context)

        if not ids:
            self.report({"WARNING"}, "No datablocks selected")
            return {"CANCELLED"}

        replaced = 0
        missing = 0
        unsupported = 0

        for old_id in ids:
            folder = get_library_folder(old_id)

            if folder is None:
                unsupported += 1
                continue

            linked = load_linked_id(filepath, folder, old_id.name)

            if linked is None:
                missing += 1
                continue

            replace_id_references(folder, old_id, linked)

            replaced += 1

        self.report({"INFO"}, f"Replaced: {replaced} | Missing: {missing} | Unsupported: {unsupported}")

        return {"FINISHED"}


# ----------------------------------------------------------
# Menu
# ----------------------------------------------------------


def outliner_menu_func(self, context):
    self.layout.separator()
    self.layout.operator(OUTLINER_OT_relink_selected_from_blend.bl_idname, icon="LINK_BLEND")


# ----------------------------------------------------------
# Register
# ----------------------------------------------------------

classes = (OUTLINER_OT_relink_selected_from_blend,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.OUTLINER_MT_context_menu.append(outliner_menu_func)


def unregister():
    bpy.types.OUTLINER_MT_context_menu.remove(outliner_menu_func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
