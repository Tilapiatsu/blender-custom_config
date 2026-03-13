import bpy
import sys
import subprocess
from pathlib import Path
from Tila_ConfigManager.logger import LOG


class UI_TilaConfig_OpenFolder(bpy.types.Operator):
    bl_idname = "tila.config_open_folder"
    bl_label = "Open Folder"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Open given path in default explorer"

    path: bpy.props.StringProperty(name="Path")

    def execute(self, context):
        self.valid_path = Path(self.path)
        if not self.valid_path.exists():
            LOG.error(f"Path is invalid : {self.valid_path}")
            return {"CANCELLED"}

        if self.valid_path.is_file():
            self.valid_path = self.valid_path.parent

        print(self.valid_path, sys.platform)

        match sys.platform:
            case "windows":
                subprocess.Popen(["open", "--", str(self.valid_path)])
            case "linux":
                subprocess.Popen(["dolphin", str(self.valid_path)])
            case _:
                pass

        return {"FINISHED"}


classes = (UI_TilaConfig_OpenFolder,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
