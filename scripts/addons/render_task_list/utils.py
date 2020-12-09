import bpy, re
import os, csv, codecs #辞書


def preference():
	preference = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences

	return preference


# 翻訳辞書の取得
def GetTranslationDict():
	dict = {}
	path = os.path.join(os.path.dirname(__file__), "translation_dictionary.csv")
	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		dict['ja_JP'] = {}
		for row in reader:
			for context in bpy.app.translations.contexts:
				dict['ja_JP'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')

	return dict


# フレーム文字列を最適化
def frame_set_format(frame_num):
	flame_l = frame_num.replace(' ', '').replace(',,', ',').replace('-', '..') # ゴミを除去する
	flame_l = flame_l.split(",") # リストにする
	flame_l = [fl for fl in flame_l if not re.findall("^\.\.",fl)]

	flame_l = sorted(set(flame_l), key=flame_l.index) # 重複を削除
	return flame_l

# シーンを取得
def get_item_scene(item):
	if not bpy.data.scenes.find(item.scene) == -1:
		return bpy.data.scenes[item.scene]
	else:
		return bpy.context.scene

# カメラを取得
def get_item_camera(item):
	if item.blendfile:
		return get_item_scene(item).camera
	else:
		if item.camera_pointer:
			if not bpy.data.objects.find(item.camera_pointer.name) == -1:
				return item.camera_pointer
		elif not bpy.data.objects.find(item.camera) == -1:
			return bpy.data.objects[item.camera]
		else:
			tgt_sc = get_item_scene(item)
			return tgt_sc.camera

# ビューレイヤーを取得
def get_item_view_layer(item):
	tgt_sc = get_item_scene(item)
	if not tgt_sc.view_layers.find(item.view_layer) == -1:
		return tgt_sc.view_layers[item.view_layer]
	else:
		return bpy.context.view_layer


# タスクのパス
def get_task_temp_path():
	# addon_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
	addon_path = os.path.split(os.path.abspath(__file__))[0]
	temp_path = os.path.join(addon_path,"scripts","rentask_task_temp.py")
	return temp_path


def get_bfile_run_path():
	# addon_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
	addon_path = os.path.split(os.path.abspath(__file__))[0]
	temp_path = os.path.join(addon_path,"rentask","def_rentask_bfile.py")
	return temp_path


# ログファイルのパス
def get_log_file_path():
	addon_path = os.path.split(os.path.abspath(__file__))[0]
	temp_path = os.path.join(addon_path,"scripts","render_log.log")
	return temp_path
