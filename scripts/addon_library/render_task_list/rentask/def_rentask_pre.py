import bpy, os, re
from .op_rentask_item import RENTASKLIST_OT_rentask_item_duplicate
from ..utils import (
get_item_scene,
get_item_camera,
get_item_view_layer,
save_number_from_files,
preference,
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
	else:
		if item.mode == "ANIME":
			if not item.frame_start == -1:
				tgt_sc.frame_start = item.frame_start
			if not item.frame_end == -1:
				tgt_sc.frame_end = item.frame_end

	result_filepath = create_filepath(self, context, tgt_sc, item)


	if not os.path.dirname(result_filepath) in {"/tmp\\","","\\\\","\\"}:
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

	# ビュー空間
	if not item.view_transform == "NONE":
		tgt_sc.view_settings.view_transform = item.view_transform


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

	# コンポジットノードのシーンとビューレイヤーを変更
	set_composite_node(self, context, tgt_sc, item)


	return is_anime, scene_name, view_layer_name


# ファイルパス
def create_filepath(self, context, tgt_sc, item):
	addon_pref = preference()
	sc = bpy.context.scene
	ptask_main = sc.rentask.rentask_main

	if not item.filepath:
		if item.blendfile:
			return ""
		else:
			return tgt_sc.render.filepath

	outpath = item.filepath
	item_name = item.name
	rep_l = ["¥", "/", ":", ";", "*", "?", "\\", "<", ">", "|"]
	for i in rep_l:
		 item_name = item_name.replace(i,"_")

	if os.path.isdir(outpath):
		outpath = os.path.join(outpath,"####")

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


	# if not ptask_main.add_number_for_dupname:
	# 	if item.scene_all:
	# 		if not "{scene}" in outpath:
	# 			outpath += "_{scene}"
	# 	if item.view_layer_all:
	# 		if not "{view_layer}" in outpath:
	# 			outpath += "_{view_layer}"
	# 	if item.camera_all:
	# 		if not "{camera}" in outpath:
	# 			outpath += "_{camera}"

	if item.filepath_auto_add_data_name:
		if item.scene or item.scene_all:
			if not "{scene}" in outpath:
				outpath += "_{scene}"
		if item.view_layer or item.view_layer_all:
			if not "{view_layer}" in outpath:
				outpath += "_{view_layer}"
		if item.camera_pointer or item.camera_all:
			if not "{camera}" in outpath:
				outpath += "_{camera}"
		if item.material_override_mat:
			outpath += "_" + item.material_override_mat
		if item.fake_normal:
			outpath += "_normal"

	outpath = outpath.replace("{scene}",tgt_sc.name)
	outpath = outpath.replace("{view_layer}",get_item_view_layer(item).name)
	outpath = outpath.replace("{camera}",get_item_camera(item).name)
	outpath = outpath.replace("{path_dir}",os.path.dirname(tgt_sc.render.filepath))
	outpath = outpath.replace("{path_name}",os.path.basename(tgt_sc.render.filepath))
	outpath = outpath.replace("{path_sc_dir}",os.path.dirname(sc.render.filepath))
	outpath = outpath.replace("{path_sc_name}",os.path.basename(sc.render.filepath))

	if item.parent_item_name:
		outpath = outpath.replace("{task}",item.parent_item_name)
	else:
		outpath = outpath.replace("{task}",item.name)


	# ファイル名が重複しないようにする
	if ptask_main.add_number_for_dupname:
		IMAGE_EXTENSIONS = (
			'bmp', 'rgb', 'png', 'jpg', 'jp2', 'tga', 'cin', 'dpx', 'exr', 'hdr', 'tif'
		)

		o_dirname = os.path.split(outpath)[0]
		o_basename = os.path.split(outpath)[1]
		if os.path.isdir(o_dirname):
			files = [f for f in os.listdir(o_dirname)
					 if f.lower().endswith(IMAGE_EXTENSIONS)]
			if files:
				save_number = save_number_from_files(files,o_basename)
				if not save_number == "000":
					outpath = os.path.join(o_dirname,o_basename + "_" + save_number)


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


def pre_hide_data(self,item):
	if item.hide_data_type == "NONE":
		return
	if not item.hide_data_name:
		return

	data_i_l = item.hide_data_tmp_list.split(",")
	for data_i in data_i_l:
		if data_i in getattr(bpy.data,item.hide_data_type):
			getattr(bpy.data,item.hide_data_type)[data_i].hide_render = True


# コンポジットノードのシーンとビューレイヤーを変更
def set_composite_node(self, context, tgt_sc, item):
	if not item.change_render_layer_node:
		return
	if not item.scene and not item.view_layer:
		return

	sc = bpy.context.scene
	for nd in sc.node_tree.nodes:
		if nd.type == "R_LAYERS":
			if item.scene:
				nd.scene = item.scene
			if item.view_layer:
				nd.layer = item.view_layer
