# ui
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"ui_list_rentask",
	"ui_menu",
	"ui_panel",
	"ui_rentask",
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .ui_list_rentask import *
from .ui_menu import *
from .ui_panel import *
from .ui_rentask import *

classes = (
RENTASKLIST_MT_rentask_filepath,
RENTASKLIST_MT_rentask_other,
RENTASKLIST_PT_cam_panel,
RENTASKLIST_UL_rentask,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
