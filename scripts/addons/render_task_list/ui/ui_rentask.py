import bpy, re, ast
from ..rentask.def_rentask_pre import create_filepath
from ..utils import (
frame_set_format,
get_item_scene,
get_log_file_path,
)


def draw_rentask_menu(self,context,layout):
	sc = bpy.context.scene
	props = sc.rentask
	ptask_main = props.rentask_main
	colle = props.rentask_colle
	index = props.rentask_index



	# box = layout.box()
	# col = box.column(align=True)
	# col.prop(ptask_main,"time_start",emboss=False)
	# col.prop(ptask_main,"time_finish",emboss=False)
	# col.prop(ptask_main,"time_elapsed",emboss=False)


	# op = layout.operator("rentask.rentask_run",icon="CONSOLE")
	# op.run_from_script_text = "{'task': {'name': 'task', 'view_layer_all': False, 'scene_all': False, 'mode': 'IMAGE', 'blendfile': '13', 'thread': 36, 'resolution_percentage': 0, 'scene': 'bb', 'material_override_restore_scene_name': '', 'hide_data_tmp_list': '', 'parent_item_name': '', 'camera_pointer': bpy.data.objects['A'], 'view_layer': '', 'camera_all': False, 'resolution_x': 77, 'resolution_y': 77, 'material_override_mat': '', 'hide_data_type': 'objects', 'filepath': 'C:\\Users\\sdt\\Desktop\\render\\ren\\moge_task0555', 'frame': '555', 'camera': 'ee'}}"
	#
	# layout.separator()
	# layout.operator("rentask.rentask_cmd",icon="CONSOLE")
	# layout.separator()

	row = layout.row(align=True)
	row.scale_y = 1.5
	op = row.operator("rentask.rentask_run",text="Render",icon="RESTRICT_RENDER_OFF")
	op.run_from_script_text = ""
	row.menu("RENTASKLIST_MT_rentask_other",text="",icon="DOWNARROW_HLT")

	row = layout.row(align=True)
	row.prop(ptask_main,"bfile_type",expand=True)

	# list
	row = layout.row()
	row.template_list("RENTASKLIST_UL_rentask", "", props, "rentask_colle", props, "rentask_index",rows=3)
	col = row.column()
	if ptask_main.bfile_type == "EXTERNAL":
		col.operator("rentask.rentask_bfile_add",text="",icon="ADD")
		col.label(text="",icon="BLANK1")
	elif ptask_main.bfile_type == "CURRENT":
		col.operator("rentask.rentask_item_add",text="",icon="ADD")
		col.operator("rentask.rentask_item_save_setting",text="",icon="PLUS")

	col.operator("rentask.rentask_item_remove",text="",icon="REMOVE").item = props.rentask_index
	col.separator()
	col.operator("rentask.rentask_item_duplicate",text="",icon="DUPLICATE")
	if len(colle) >= 2:
		col_sub = col.column(align=True)
		move = col_sub.operator("rentask.rentask_item_move", icon="TRIA_UP", text='')
		move.direction ="UP"
		move = col_sub.operator("rentask.rentask_item_move", icon="TRIA_DOWN", text='')
		move.direction ="DOWN"

	# ログ
	draw_probar(self, context, layout)

	# 設定
	draw_setting(self, context, layout)

def draw_probar(self, context, layout):
	sc = bpy.context.scene
	ptask_main = sc.rentask.rentask_main
	props = sc.rentask.rentask_main

	if not ptask_main.bfile_type == "EXTERNAL":
		return


	sp = layout.split(factor=0.9)
	row = sp.row()
	row.prop(props,"probar_active",text="",icon="TRIA_DOWN" if props.probar_active else "TRIA_RIGHT", emboss=False)
	row.prop(props,"probar_active",icon="HIDE_OFF" if props.probar_active else "HIDE_ON")

	# sp.separator()

	if props.probar_active:
		box = layout.box()
		if ptask_main.bfile_type == "CURRENT":
			row = box.row(align=True)
			row.active = False
			row.label(text="Progress view is not available for current Blend file rendering",icon="NONE")
			return
		with open(get_log_file_path(), mode='r') as f:
			if f:
				log_l = f.readlines()
				if log_l:
					log_l = [i for i in log_l if not i in {"\n","",None}]
					{'wtime': '2020-12-09 15:43:54.819970', 'par': '4.166666666666666', 'frame': '24', 'mem': '113.85M', 'elapsed': '00:01.50', 'remaining': '00:01.86', 'tiles_done': '1', 'tiles_todo': '24'}
					line = log_l[-1]
					line_dic = ast.literal_eval(line)
					line_text = line
					right_time_text = ""
					wtime_text = ""
					par_text = ""
					frame_text = ""
					mem_text = ""
					elapsed_text = ""
					remaining_text = ""
					tiles_done_text = ""
					tiles_todo_text = ""

					if "wtime" in line_dic:
						wtime_text = line_dic["wtime"]
					if "par" in line_dic:
						par_text = line_dic["par"]
						par_text = round(float(par_text),0)

					if "frame" in line_dic:
						frame_text = line_dic["frame"]
					if "mem" in line_dic:
						mem_text = line_dic["mem"]
					if "elapsed" in line_dic:
						elapsed_text = line_dic["elapsed"]
					if "remaining" in line_dic:
						remaining_text = line_dic["remaining"]
					if "tiles_done" in line_dic:
						tiles_done_text = line_dic["tiles_done"]
					if "tiles_todo" in line_dic:
						tiles_todo_text = line_dic["tiles_todo"]

					if "endtime" in line_dic:
						line_text = "Finished %s" % (line_dic["endtime"] )
						right_time_text = wtime_text.split(".")[0]
					else:
						line_text = "%s Frame : %s %s  (%s)" % (frame_text, par_text,"%", mem_text)
						right_time_text = elapsed_text
					sp = box.split(align=True,factor=0.6)
					sp.label(text=line_text)
					row = sp.row(align=True)
					row.alignment="RIGHT"
					row.label(text=right_time_text,icon="NONE")
				else:
					box.label(text="...")


def draw_setting(self, context, layout):
	sc = bpy.context.scene
	props = sc.rentask
	colle = props.rentask_colle
	index = props.rentask_index

	if not len(colle):
		return
	item = colle[index]

	row = layout.row(align=True)
	row.alignment="LEFT"
	row.prop(props.ui.rentask,"toggle_settings",icon="TRIA_DOWN" if props.ui.rentask.toggle_settings else "TRIA_RIGHT", emboss=False)
	if not props.ui.rentask.toggle_settings:
		return
	if props.rentask_main.bfile_type == "EXTERNAL":
		if not item.blendfile:
			return
	else:
		if item.blendfile:
			return

	tgt_sc = get_item_scene(item)

	box = layout.box()

	col = box.column(align=True)
	row = col.row(align=True)
	row.label(text="",icon="FILE_BLEND")
	row.active = (item.blendfile != "")
	row.alert = bool(re.match("^//",item.blendfile))
	row.prop(item,"blendfile")
	if re.match("^//",item.blendfile):
		col_alert = col.column(align=True)
		col_alert.alert = True
		col_alert.label(text="Don't support relative path!!")

	col.separator()
	row = col.row(align=True)
	row.scale_y = 1.2
	row.prop(item,"mode",expand=True)
	col.separator()


	col.separator()

	# ファイルパス
	row = col.row(align=True)
	row.active = (item.filepath != "" and item.filepath != "$main_path\&task_name")
	row.label(text="",icon="BLANK1")
	row_fp = row.row(align=True)
	row_fp.prop(item,"filepath")
	row_fp.menu("RENTASKLIST_MT_rentask_filepath",text="",icon="COLLAPSEMENU")
	if not item.blendfile:
		if item.filepath:
			# ファイルパスのプレビュー
			result_filepath = create_filepath(self, context, tgt_sc, item)
			col.label(text=result_filepath,icon="BLANK1")

		else:
			col.label(text="")
	else:
		col.label(text="")

	col.separator()

	if item.mode == "IMAGE":
		sp = col.split(align=True,factor=0.9)
		row = sp.row(align=True)
		# row.alert = (item.blendfile != "" and not item.frame)
		row.active = bool(item.frame)
		row.label(text="",icon="BLANK1")
		row.prop(item,"frame")
		row.label(text="",icon="RIGHTARROW")
		frame_l = frame_set_format(item.frame)
		new_fl_l = []
		for fl in frame_l:
			if ".." in fl:
				f_count = int(fl.split("..")[1]) - int(fl.split("..")[0])
				for i in range(f_count):
					new_fl_l.append(i)
			else:
				new_fl_l.append(fl)
		row = sp.row(align=True)
		row.alignment="RIGHT"
		row.label(text="(%s)" % str(len(new_fl_l)))
	elif item.mode == "ANIME":
		row = col.row(align=True)
		row.alignment="RIGHT"
		all_f = tgt_sc.frame_end - tgt_sc.frame_start + 1
		row.label(text="%s-%s (%s)" % (tgt_sc.frame_start,str(tgt_sc.frame_end),str(all_f)))

		col_frame = col.column(align=True)
		col_frame.use_property_split = True
		col_frame.use_property_decorate = False
		row = col_frame.row(align=True)
		row.active = bool(not item.frame_start == -1)
		row.prop(item,"frame_start")
		row = col_frame.row(align=True)
		row.active = bool(not item.frame_end == -1)
		row.prop(item,"frame_end")



	elif not item.scene_all:
		row = col.row(align=True)
		row.alignment="RIGHT"
		all_f = tgt_sc.frame_end - tgt_sc.frame_start + 1
		row.label(text="%s-%s (%s)" % (tgt_sc.frame_start,str(tgt_sc.frame_end),str(all_f)))
	else:
		col.label(text="")

	col.separator()
	if item.blendfile:
		row = col.row(align=True)
		row.active = bool(item.thread)
		row.use_property_split = True
		row.use_property_decorate = False
		row.prop(item,"thread")
		col.separator()


	# Resolution
	if item.resolution_percentage != 0:
		per = item.resolution_percentage
	else:
		if item.blendfile:
			per = 100
		else:
			per = tgt_sc.render.resolution_percentage

	if item.resolution_x != 0:
		reso_x = item.resolution_x
	else:
		if item.blendfile:
			reso_x = 0
		else:
			reso_x = tgt_sc.render.resolution_x
	if item.resolution_y != 0:
		reso_y = item.resolution_y
	else:
		if item.blendfile:
			reso_y = 0
		else:
			reso_y = tgt_sc.render.resolution_y
	final_res_x = (reso_x * per) / 100
	final_res_y = (reso_y * per) / 100
	reso_text = "{} x {}".format(str(int(final_res_x)), str(int(final_res_y)))

	row = col.row(align=True)
	row.alignment="LEFT"
	boxs = col.box()
	boxs.use_property_split = True
	boxs.use_property_decorate = False
	cols = boxs.column(align=True)
	row = cols.row(align=True)
	row.active = bool(item.resolution_x)
	row.prop(item, "resolution_x", text="Resolution X")
	row = cols.row(align=True)
	row.active = bool(item.resolution_y)
	row.prop(item, "resolution_y", text="Y")
	cols.separator()
	row = cols.row(align=True)
	row.label(text=reso_text)
	row.active = bool(item.resolution_percentage != 0)
	row.prop(item, "resolution_percentage", text="%")

	col.separator()
	row = col.row(align=True)
	row.active = (not item.file_format == "NONE")
	row.label(text="",icon="FILE")
	row.prop(item, "file_format")
	row = col.row(align=True)
	row.active = (not item.samples == 0)
	row.use_property_split = True
	row.use_property_decorate = False
	row.label(text="",icon="IPO_QUAD")
	row.prop(item, "samples")

	col.separator()


	draw_advanced_settings(self, context, col)


def draw_advanced_settings(self, context, layout):
	sc = bpy.context.scene
	props = sc.rentask
	colle = props.rentask_colle
	index = props.rentask_index
	col = layout

	item = colle[index]
	tgt_sc = get_item_scene(item)


	row = col.row(align=True)
	row.alignment="LEFT"
	row.prop(props.ui.rentask,"toggle_advanced_settings",icon="TRIA_DOWN" if props.ui.rentask.toggle_advanced_settings else "TRIA_RIGHT", emboss=False)
	if not props.ui.rentask.toggle_advanced_settings:
		return

	row = col.row(align=True)
	row.active = (not item.engine == "NONE")
	row.label(text="",icon="SHADING_RENDERED")
	row.prop(item, "engine")
	if item.engine == "OTHER":
		col.prop(item, "engine_other")
	col.separator()
	# other
	row = col.row(align=True)
	row.active = (not item.hide_data_type == "NONE" and not item.material_override_mat)
	row.label(text="",icon="HIDE_ON")
	row.prop(item, "hide_data_type")
	if not item.hide_data_type == "NONE":
		row = col.row(align=True)
		row.active = (not item.material_override_mat)
		row.label(text="",icon="BLANK1")
		row.prop(item, "hide_data_name")
		row.operator("rentask.rentask_hide_data_name_set",text="",icon="IMPORT")

	col.separator()


	# シーン
	sp = col.split(align=True)
	row = sp.row(align=True)
	row.label(text="Scene",icon="SCENE_DATA")
	row.separator()
	if not item.blendfile:
		row_all = row.row(align=True)
		row_all.alignment="RIGHT"
		row_all.prop(item,"scene_all",text="All")
	row_ind = sp.row(align=True)
	row_ind.active = (not item.scene_all)
	if item.blendfile:
		row_ind.prop(item,"scene",text="")
	else:
		if item.scene_all:
			sc_l = [o for o in bpy.data.scenes if not o.camera.hide_render]
			row_ind.label(text=str(len(sc_l)))
		else:
			row_ind.prop_search(item, "scene", bpy.data, "scenes", text="")


	# ビューレイヤー
	sp = col.split(align=True)
	row = sp.row(align=True)
	row.label(text="View Layer",icon="RENDERLAYERS")
	row.separator()
	if not item.blendfile:
		row_all = row.row(align=True)
		row_all.alignment="RIGHT"
		row_all.prop(item,"view_layer_all",text="All")
	row_ind = sp.row(align=True)
	row_ind.active = (not item.view_layer_all)
	if item.blendfile:
		row_ind.prop(item,"view_layer",text="")
	else:
		if item.view_layer_all:
			vl_l = [o for o in tgt_sc.view_layers if o.use]
			row_ind.label(text=str(len(vl_l)))
		else:
			row_ind.prop_search(item, "view_layer", tgt_sc, "view_layers", text="")


	# カメラ
	sp = col.split(align=True)
	row = sp.row(align=True)
	row.label(text="Camera",icon="CAMERA_DATA")
	row.separator()
	if not item.blendfile:
		row_all = row.row(align=True)
		row_all.alignment="RIGHT"
		row_all.prop(item,"camera_all",text="All")
	row_ind = sp.row(align=True)
	row_ind.active = (not item.camera_all)
	if item.blendfile:
		row_ind.prop(item,"camera",text="")
	else:
		if item.camera_all:
			cam_l = [o for o in tgt_sc.collection.all_objects if not o.hide_render if o.type == "CAMERA"]
			row_ind.label(text=str(len(cam_l)))
		else:
			row_ind.prop(item,"camera_pointer",text="")
			# row_ind.prop_search(item, "camera", tgt_sc.collection, "all_objects", text="")


	sp = col.split(align=True,factor=0.5)
	row = sp.row(align=True)
	row.label(text="Material Override",icon="MATERIAL_DATA")
	if item.blendfile:
		sp.prop(item,"material_override_mat",text="")
	else:
		sp.prop_search(item, "material_override_mat", bpy.data, "materials",text="")
