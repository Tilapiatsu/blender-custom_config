# prop
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"prop_rentask_colle",
	"prop_main",
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])

from .prop_main import *
from .prop_rentask_colle import *

classes = (
RENTASKLIST_PR_ui_rentask,
RENTASKLIST_PR_ui_main,
RENTASKLIST_PR_rentask_colle,
RENTASKLIST_PR_rentask_main,

RENTASKLIST_PR_main,

)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.rentask = PointerProperty(type=RENTASKLIST_PR_main)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	del bpy.types.Scene.rentask


if __name__ == "__main__":
	register()
