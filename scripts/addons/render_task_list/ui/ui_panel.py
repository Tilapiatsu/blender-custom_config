import bpy
from bpy.props import *
from bpy.types import Panel
# from .ui_render_batch import *
# from .ui_render_sc import *
# from .ui_obcam import draw_panel_cam_menu
# from ..op.op_rentask import prop_rentask_menu
# from .ui_list_rentask import rentask_list
# from .ui_render_bg import *
from .ui_rentask import *
# from .ui_view_layer import viewlayer_list_menu


class RENTASKLIST_PT_cam_panel(Panel):
	bl_label = "Render Task List"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Tools"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		
		draw_rentask_menu(self,context,layout)




def scforlist_menu(self,context,layout):
	props = context.scene.save_cam_other
	sc = bpy.context.scene
	colle = sc.save_cam_collection
	index = sc.save_cam_collection_index

	sp = layout.split(align=True,factor=0.9)
	sp_count = sp.row(align=True)
	rowsp_count = sp_count.row(align=True)
	rowsp_count.scale_x = 1.5
	rowsp_count.alignment="CENTER"
	row_c = rowsp_count.row(align=True)

	rowsp_count.separator()



	box = rowsp_count.box()
	row = box.row(align=True)
	row.prop(props,"scforlist_filter_type",text="",expand=True)

	box = rowsp_count.box()
	row = box.row(align=True)

	row.prop(props,"scforlist_filter_render",text="",icon="RESTRICT_RENDER_ON")


	##################################################################
	box = layout.box()
	if not len(colle) == 0:
		col = box.column(align=True)

		new_l = []
		for item in colle:
			# cam_type
			if props.scforlist_filter_type == "Camera type":
				if item.cam_type_load and not item.camtrans_load and not item.res_load and not item.frame_load and not item.dof_load:

					if not item.render:
						if props.scforlist_filter_render:
							new_l.append(item)

					else:
						new_l.append(item)

			# Transform
			elif props.scforlist_filter_type == "Transform":
				if not item.cam_type_load and item.camtrans_load and not item.res_load and not item.frame_load and not item.dof_load:
					if not item.render:
						if props.scforlist_filter_render:
							new_l.append(item)

					else:
						new_l.append(item)


			# Resolution
			elif props.scforlist_filter_type == "Resolution":
				if not item.cam_type_load and not item.camtrans_load and item.res_load and not item.frame_load and not item.dof_load:
					if not item.render:
						if props.scforlist_filter_render:
							new_l.append(item)

					else:
						new_l.append(item)

			# Frame Range
			elif props.scforlist_filter_type == "Frame Range":
				if not item.cam_type_load and not item.camtrans_load and not item.res_load and item.frame_load and not item.dof_load:
					if not item.render:
						if props.scforlist_filter_render:
							new_l.append(item)

					else:
						new_l.append(item)


			# Dof
			elif props.scforlist_filter_type == "Dof":
				if not item.cam_type_load and not item.camtrans_load and not item.res_load and not item.frame_load and item.dof_load:
					if not item.render:
						if props.scforlist_filter_render:
							new_l.append(item)

					else:
						new_l.append(item)




			elif props.scforlist_filter_type == "Other":
				ll = item.cam_type_load + item.camtrans_load + item.res_load + item.frame_load + item.dof_load
				if ll >=2:
					if not item.render:
						if props.scforlist_filter_render:
							new_l.append(item)
					else:
						new_l.append(item)




		sorted(set(new_l), key=new_l.index)
		row_c.label(text=str(len(new_l)) + " / " + str(len(colle)),icon="NONE")

		for item in new_l:
			item_index = colle.find(item.name)
			rentask_list(self,context,col,item,item_index,True,False)
	else:
		box.label(text="No Item",icon="NONE")


class RENTASKLIST_PT_dopesheet_panel(Panel):
	bl_label = "Frame Range"
	bl_space_type = "DOPESHEET_EDITOR"
	bl_region_type = "UI"
	bl_category = "Tools"

	def draw(self, context):
		layout = self.layout

		props = context.scene.save_cam_other
		sc = bpy.context.scene
		colle = sc.save_cam_collection
		index = sc.save_cam_collection_index

		row = layout.row(align=True)

		row.operator("anim.start_frame_set",text="Set Start",icon="REW")
		row.operator("anim.end_frame_set",text="Set End",icon="FF")

		layout.separator()
		camadd = layout.operator("rentask.cam_add",text="New",icon="ADD")

		camadd.cam_type_load = False
		camadd.camtrans_load = False
		camadd.res_load = False
		camadd.frame_load = True
		camadd.dof_load = False
		box = layout.box()
		if not len(colle) == 0:
			col = box.column(align=True)

			new_l = []
			for item in colle:
				# Frame Range
				if not item.cam_type_load and not item.camtrans_load and not item.res_load and item.frame_load and not item.dof_load:
					new_l.append(item)



			sorted(set(new_l), key=new_l.index)

			for item in new_l:
				item_index = colle.find(item.name)
				rentask_list(self,context,col,item,item_index,True,True)
		else:
			box.label(text="No Item",icon="NONE")
