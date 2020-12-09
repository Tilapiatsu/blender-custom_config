# rentask
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"def_rentask_bfile_call",
	"def_rentask_bfile",
	"def_rentask_covert_log",
	"def_rentask_invoke",
	"def_rentask_post",
	"def_rentask_pre",
	"op_rentask_cmd",
	"op_rentask_convert_dic",
	"op_rentask_item",
	"op_rentask_probar",
	"op_rentask_run",
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])

from .def_rentask_bfile import *
from .def_rentask_bfile_call import *
from .def_rentask_covert_log import *
from .def_rentask_invoke import *
from .def_rentask_post import *
from .def_rentask_pre import *
from .op_rentask_cmd import *
from .op_rentask_convert_dic import *
from .op_rentask_item import *
from .op_rentask_probar import *
from .op_rentask_run import *

classes = (
RENTASKLIST_OT_probar_modaltimer,
RENTASKLIST_OT_rentask_bfile_add,
RENTASKLIST_OT_rentask_cmd,
RENTASKLIST_OT_rentask_filepath_name_add,
RENTASKLIST_OT_rentask_hide_data_name_set,
RENTASKLIST_OT_rentask_item_add,
RENTASKLIST_OT_rentask_item_duplicate,
RENTASKLIST_OT_rentask_item_move,
RENTASKLIST_OT_rentask_item_remove,
RENTASKLIST_OT_rentask_item_save_setting,
RENTASKLIST_OT_rentask_load_setting,
RENTASKLIST_OT_rentask_run,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
