# op
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"op_sk_transfer",
	"op_sk_create",
	"op_sk_mod",
	"sk_utils",
	"op_sync",
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .op_sk_transfer import *
from .op_sk_create import *
from .op_sk_mod import *
from .sk_utils import *
from .op_sync import *

classes = (
LAZYSHAPEKEYS_OT_shape_keys_sync_update,
LAZYSHAPEKEYS_OT_shape_keys_transfer_forced,
LAZYSHAPEKEYS_OT_shape_keys_create_obj_from_all,
OBJECT_OT_shape_keys_apply_modifier,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
