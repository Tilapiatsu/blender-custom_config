# op
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"op_automirror",
	"op_mirrormirror",
	"op_mod",

	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .op_automirror import *
from .op_mirrormirror import *
from .op_mod import *


classes = (
AUTOMIRROR_OT_automirror,
AUTOMIRROR_OT_mirror_apply,
AUTOMIRROR_OT_mirror_remove,
AUTOMIRROR_OT_mirror_target_set,
AUTOMIRROR_OT_mirror_toggle,
AUTOMIRROR_OT_mirrormirror,
AUTOMIRROR_OT_modifier_add,
AUTOMIRROR_OT_modifier_sort,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
