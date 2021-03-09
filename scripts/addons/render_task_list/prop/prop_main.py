import bpy
from bpy.props import *
from bpy.types import PropertyGroup
from .prop_rentask_colle import RENTASKLIST_PR_rentask_colle


def update_colle_index(self, context):
	props = bpy.context.scene.rentask
	ptask_main = bpy.context.scene.rentask.rentask_main
	old_index = props.rentask_index

	if ptask_main.bfile_type == "CURRENT":
		props.rentask_index = props.rentask_old_index_current
		props.rentask_old_index_external = old_index

	elif ptask_main.bfile_type == "EXTERNAL":
		props.rentask_index = props.rentask_old_index_external
		props.rentask_old_index_current = old_index


def update_probar(self, context):
	props = bpy.context.scene.rentask.rentask_main
	if props.probar_active:
		bpy.ops.rentask.probar_modal_timer()


class RENTASKLIST_PR_rentask_main(PropertyGroup):
	items = [
		('NONE', "None", "","RADIOBUT_OFF", 0),
		('SHUTDOWN', "ShutDown", "ShutDown the PC","QUIT", 1),
		('REBOOT', "Reboot", "Reboot the PC","FILE_REFRESH", 2),
		('SLEEP', "Sleep", "Sleep the PC","RESTRICT_VIEW_ON", 3),
		('QUIT_BLENDER', "Quit Blender", "","QUIT", 4),
		# ('Pause', "Pause", "","FREEZE", 3),
		]
	end_processing_type : EnumProperty(items=items, name="End Processing Type", default='NONE',description="Only affects .bat file creation")
	items = [
		('CURRENT', "Current .blend", "Render the current blend file","FILE", 0),
		('EXTERNAL', "External .blend", "Render an external blend file","DUPLICATE", 1),
		]
	bfile_type : EnumProperty(items=items, name="Rendering Mode", default='CURRENT',description="",update=update_colle_index)


	frame_current_per : FloatProperty(name="Current Frame",description="",min=0,max=100,subtype='PERCENTAGE')
	time_finish : StringProperty(name="Finish Time", description="",default=" - - - ")
	time_start : StringProperty(name="Start Time", description="")
	time_elapsed  : StringProperty(name="Elapsed Time", description="",default=" - - - ")
	probar_active : BoolProperty(name="Progress", description="Monitor the status of your rendering job", update = update_probar)
	add_number_for_dupname : BoolProperty(name="Add numbers for duplicate filenames",description="Add 3 digits to the end of the number of files with the same name in the output folder to prevent overwriting")


class RENTASKLIST_PR_ui_rentask(PropertyGroup):
	toggle_advanced_settings : BoolProperty(name="Advanced Settings")
	toggle_settings : BoolProperty(name="Settings")


class RENTASKLIST_PR_ui_main(PropertyGroup):
	rentask : PointerProperty(type=RENTASKLIST_PR_ui_rentask)


class RENTASKLIST_PR_main(PropertyGroup):
	rentask_main : PointerProperty(type=RENTASKLIST_PR_rentask_main)
	rentask_colle : CollectionProperty(type=RENTASKLIST_PR_rentask_colle)
	rentask_index : IntProperty(min=0)
	rentask_old_index_current : IntProperty(min=0)
	rentask_old_index_external : IntProperty(min=0)
	ui : PointerProperty(type=RENTASKLIST_PR_ui_main)
