import bpy, os, re
from .op_rentask_item import RENTASKLIST_OT_rentask_item_duplicate
from ..utils import (
get_item_scene,
get_item_camera,
get_item_view_layer
)


# シーンのレンダリング設定を一時的に変更
def pre_set_render_setting(self, context, tgt_sc, item):
	if item.frame:
		if item.mode == "IMAGE":
			if ".." in item.frame:
				tgt_sc.frame_start = int((item.frame).split("..")[0])
				tgt_sc.frame_end = int((item.frame).split("..")[1])
			else:
				tgt_sc.frame_current = int(item.frame)
		elif item.mode == "ANIME":
			if not item.frame_start == -1:
				tgt_sc.frame_start = item.frame_start
			if not item.frame_end == -1:
				tgt_sc.frame_end = item.frame_end

	result_filepath = create_filepath(self, context, tgt_sc, item)
	os.makedirs(os.path.dirname(result_filepath), exist_ok=True) # ディレクトリを作成
	tgt_sc.render.filepath = result_filepath


	# 解像度
	if item.resolution_x:
		tgt_sc.render.resolution_x = item.resolution_x
	if item.resolution_y:
		tgt_sc.render.resolution_y = item.resolution_y
	if not item.resolution_percentage == 0:
		tgt_sc.render.resolution_percentage = item.resolution_percentage

	# ファイルフォーマット
	if not item.file_format == "NONE":
		tgt_sc.render.image_settings.file_format = item.file_format

	# レンダーエンジン
	if not item.engine == "NONE":
		if item.engine == "OTHER":
			tgt_sc.render.engine = item.engine_other
		else:
			tgt_sc.render.engine = item.engine

	# サンプル数
	if not item.samples == 0:
		if tgt_sc.render.engine == "CYCLES":
			tgt_sc.cycles.samples = item.samples
		if tgt_sc.render.engine == "BLENDER_EEVEE":
			tgt_sc.eevee.taa_render_samples = item.samples

	# カメラ
	if item.camera or item.camera_pointer:
		tgt_sc.camera = get_item_camera(item)


	# renderオペレーターのオプションの指定
	if item.mode == "ANIME":
		is_anime = True
	else:
		is_anime = False

	if item.scene:
		scene_name = item.scene
	else:
		scene_name = bpy.context.scene.name

	if item.view_layer:
		view_layer_name = item.view_layer
	else:
		view_layer_name = bpy.context.view_layer.name


	# thread
	# user_script_file
	# user_script_text_block
	# world
	# thread

	return is_anime, scene_name, view_layer_name


# ファイルパス
def create_filepath(self, context, tgt_sc, item):
	sc = bpy.context.scene

	if not item.filepath:
		if item.blendfile:
			return ""
		else:
			return tgt_sc.render.filepath

	outpath = item.filepath
	item_name = item.name
	item_name = item_name.replace("¥","_")
	item_name = item_name.replace("/","_")
	item_name = item_name.replace(":","_")
	item_name = item_name.replace(";","_")
	item_name = item_name.replace("*","_")
	item_name = item_name.replace("?","_")
	item_name = item_name.replace("\"","_")
	item_name = item_name.replace("<","_")
	item_name = item_name.replace(">","_")
	item_name = item_name.replace("|","_")

	if item.mode == "IMAGE":
		if "#" in outpath:
			shape_count = len(re.findall("#",outpath))
			if shape_count <= 2:
				shape_count = 2

			if item.frame:
				frame_text = item.frame.zfill(shape_count)
			else:
				frame_text = str(tgt_sc.frame_current).zfill(shape_count)

			if shape_count >= 4:
				outpath = outpath.replace("#" * shape_count,frame_text)
			elif shape_count == 3:
				outpath = outpath.replace("###",frame_text)
			elif shape_count == 2:
				outpath = outpath.replace("##",frame_text)
			elif shape_count == 1:
				outpath = outpath.replace("##",frame_text)



	outpath = outpath.replace("{scene}",tgt_sc.name)
	outpath = outpath.replace("{view_layer}",get_item_view_layer(item).name)
	# if get_item_camera(item):
	outpath = outpath.replace("{camera}",get_item_camera(item).name)
	outpath = outpath.replace("{path_dir}",os.path.dirname(tgt_sc.render.filepath))
	outpath = outpath.replace("{path_name}",os.path.basename(tgt_sc.render.filepath))
	outpath = outpath.replace("{path_sc_dir}",os.path.dirname(sc.render.filepath))
	outpath = outpath.replace("{path_sc_name}",os.path.basename(sc.render.filepath))
	if item.parent_item_name:
		outpath = outpath.replace("{task}",item.parent_item_name)
	else:
		outpath = outpath.replace("{task}",item.name)

	# 日付
	# import datetime
	#
	# dt_now = datetime.datetime.now()
	#
	# print(dt_now.year)
	# print(dt_now.month)
	# print(dt_now.day)
	# print(dt_now.hour)
	# print(dt_now.minute)
	# print(dt_now.second)
	# print(dt_now.microsecond)


	return outpath


# 非表示
def pre_hide_data(self,item):
	if item.hide_data_type == "NONE":
		return
	if not item.hide_data_name:
		return

	data_i_l = item.hide_data_tmp_list.split(",")
	for data_i in data_i_l:
		if data_i in getattr(bpy.data,item.hide_data_type):
			getattr(bpy.data,item.hide_data_type)[data_i].hide_render = True
