import bpy
from bpy.props import *
from bpy.types import Menu


class RENTASKLIST_MT_rentask_other(Menu):
	bl_label = "Other"

	def draw(self, context):
		props = bpy.context.scene.rentask
		layout = self.layout
		layout.label(text="End Processing Type",icon="NONE")
		layout.prop(props.rentask_main,"end_processing_type",text="")


class RENTASKLIST_MT_rentask_filepath(Menu):
	bl_label = "Add Text"

	def draw(self, context):
		layout = self.layout
		layout.operator("rentask.rentask_filepath_name_add",text="{path_dir}",icon="ADD").text="{path_dir}"
		layout.operator("rentask.rentask_filepath_name_add",text="{path_name}",icon="ADD").text="{path_name}"
		layout.operator("rentask.rentask_filepath_name_add",text="{path_sc_dir}",icon="ADD").text="{path_sc_dir}"
		layout.operator("rentask.rentask_filepath_name_add",text="{path_sc_name}",icon="ADD").text="{path_sc_name}"
		layout.separator()
		layout.operator("rentask.rentask_filepath_name_add",text="####(Frame)",icon="ADD").text="####"
		layout.operator("rentask.rentask_filepath_name_add",text="{task}",icon="ADD").text="{task}"
		layout.operator("rentask.rentask_filepath_name_add",text="{scene}",icon="SCENE_DATA").text="{scene}"
		layout.operator("rentask.rentask_filepath_name_add",text="{view_layer}",icon="RENDERLAYERS").text="{view_layer}"
		layout.operator("rentask.rentask_filepath_name_add",text="{camera}",icon="CAMERA_DATA").text="{camera}"
		# layout.separator()
		# layout.operator("rentask.rentask_filepath_name_add",text="$reso_x",icon="CAMERA_DATA").text="$reso_x"
		# layout.operator("rentask.rentask_filepath_name_add",text="$reso_y",icon="CAMERA_DATA").text="$reso_y"


class RENTASKLIST_MT_scforlist_item_status(Menu):
	bl_label = "Status Menu"

	def draw(self, context):
		layout = self.layout
		props = context.scene.save_cam_other
		toggle = layout.operator("rentask.filter_all_toggle",text="All On",icon="RADIOBUT_ON")
		toggle.on = True
		toggle = layout.operator("rentask.filter_all_toggle",text="All Off",icon="RADIOBUT_OFF")
		toggle.on = False

		layout.separator()
		layout.separator()
		layout.separator()
		layout.prop(props,"scforlist_filter_cam_type")
		layout.prop(props,"scforlist_filter_camtrans")
		layout.prop(props,"scforlist_filter_res")
		layout.prop(props,"scforlist_filter_frame")
		layout.prop(props,"scforlist_filter_dof")
		layout.prop(props,"scforlist_filter_other")
		layout.separator()
		layout.separator()
		layout.separator()

		layout.prop(props,"scforlist_filter_render")

class RENTASKLIST_MT_rentask_item_status(Menu):
	bl_label = "Filter Menu"

	def draw(self, context):
		layout = self.layout
		props = context.scene.save_cam_other
		layout.prop(props,"rentask_toggle_load",icon="IMPORT")
		layout.prop(props,"rentask_toggle_type",icon="NETWORK_DRIVE")
		layout.prop(props,"rentask_toggle_lens",icon="GIZMO")
		layout.prop(props,"rentask_toggle_resolution",icon="SHADING_BBOX")
		layout.prop(props,"rentask_toggle_frame",icon="KEYFRAME_HLT")
		layout.prop(props,"rentask_toggle_dof",icon="XRAY")
		layout.prop(props,"rentask_toggle_render",icon="RESTRICT_RENDER_OFF")
		layout.separator()
		layout.separator()
		layout.separator()
		layout.operator("rentask.cam_duplicate",icon="DUPLICATE")
		layout.separator()
		layout.separator()
		layout.separator()
		layout.operator("rentask.listitem_export", icon="EXPORT")
		layout.operator("rentask.listitem_import", icon="IMPORT")
