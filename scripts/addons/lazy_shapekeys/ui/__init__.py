# ui
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"ui_panel",
	"ui_replace_sk_menu",
	"ui_list",
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .ui_panel import *
from .ui_replace_sk_menu import *
from .ui_list import *

classes = (
# LAZYSHAPEKEYS_PT_main,
LAZYSHAPEKEYS_UL_sync_list,
# LAZYSHAPEKEYS_PT_shape_keys,
LAZYSHAPEKEYS_UL_folder_colle,
LAZYSHAPEKEYS_UL_replace_menu,
LAZYSHAPEKEYS_UL_replace_menu_misc_menu,
LAZYSHAPEKEYS_PT_misc_menu,
LAZYSHAPEKEYS_UL_folder_inner_sk,
LAZYSHAPEKEYS_UL_folder_inner_sk_misc_menu,
LAZYSHAPEKEYS_OT_main,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
