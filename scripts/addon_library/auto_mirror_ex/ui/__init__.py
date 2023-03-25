# ui
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"ui_panel",
	"ui_menu",

	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .ui_panel import *
from .ui_menu import *


classes = (
AUTOMIRROR_MT_modifier_add,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
