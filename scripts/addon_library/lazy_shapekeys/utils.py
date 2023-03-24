import bpy, re
import os, csv, codecs #辞書

def preference():
	preference = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences

	return preference


def get_cb_bone_path():
	dict = {}
	path = os.path.join(os.path.dirname(__file__),"tmp_files", "cb_bone.csv")
	return path


def get_cb_sk_path():
	dict = {}
	path = os.path.join(os.path.dirname(__file__),"tmp_files", "cb_sk.csv")
	return path


# 翻訳辞書の取得
def GetTranslationDict():
	dict = {}
	path = os.path.join(os.path.dirname(__file__), "translation_dictionary.csv")

	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		dict['ja_JP'] = {}
		for row in reader:
			if row:
				for context in bpy.app.translations.contexts:
					dict['ja_JP'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')

	return dict


def get_folder_innner_sk_list(index, sk_data):
	sk_bl = sk_data.key_blocks
	sk_l = []

	# フォルダーがない場合はなにも出さない
	if not [i for i in sk_bl if is_folder(i)]:
		return []

	for i,sk in enumerate(sk_bl):
		if i > index:
			if is_folder(sk):
				break
			sk_l += [sk.name]

	return sk_l


def get_target_obj(obj_name):
	obj = bpy.context.object
	if obj_name:
		if obj_name in bpy.data.objects:
			obj = bpy.data.objects[obj_name]

	return obj


def is_folder(sk):
	return "folder:" in sk.vertex_group


def convert_mini_text_to_dic(text):
	dic = {}
	text_l= text.split(",")
	for i in text_l:
		dic[i.split(":")[0]] = int(i.split(":")[1])

	return dic


def convert_dic_to_mini_text(dic):
	text = str(dic).replace(" ","")
	text = text.replace("{","")
	text = text.replace("}","")
	text = text.replace("'","")
	return text


#
def check_use_keyframe(sks, name_l):
	sc = bpy.context.scene
	use_cur_key_l = []
	is_remove = False

	re_compile = re.compile('key_blocks\[\"(.+)\"\].value')
	if sks.animation_data:
		if sks.animation_data.action:
			for fc in sks.animation_data.action.fcurves:
				matches = re_compile.findall(fc.data_path)
				if matches:
					if matches[0] in name_l:
						for ky in fc.keyframe_points:
							if int(ky.co[0]) == sc.frame_current:
								use_cur_key_l += [fc.data_path]
								continue


	if len(name_l) == len(use_cur_key_l):
		is_remove = True

	return use_cur_key_l, is_remove


# 操作履歴にアクセス
def Get_just_before_history():
	w_m = bpy.context.window_manager
	old_clipboard = w_m.clipboard

	win = w_m.windows[0]
	area = win.screen.areas[0]
	area_type = area.type
	area.type = "INFO"
	override = bpy.context.copy()
	override['window'] = win
	override['screen'] = win.screen
	override['area'] = win.screen.areas[0]
	bpy.ops.info.select_all(override, action='SELECT')
	bpy.ops.info.report_copy(override)
	bpy.ops.info.select_all(override, action='DESELECT')
	area.type = area_type
	clipboard = w_m.clipboard
	if not clipboard:
		return ""
	clipboard = clipboard.split("\n")
	# clipboard = del_line(clipboard)


	w_m.clipboard = old_clipboard
	return clipboard
	# return str(clipboard[-1])


def get_bind_pose_obj(mesh_obj):
	tgt_obj_l = []
	if mesh_obj.type == "MESH":
		for m in mesh_obj.modifiers:
			if m.type == "ARMATURE":
				if m.object:
					tgt_obj_l += [m.object]

	return tgt_obj_l


def get_bind_mesh_obj(pose_obj):
	tgt_obj_l = [chi for chi in pose_obj.children
	if chi.hide_viewport == False
	if chi.hide_get() == False
	if chi.type == "MESH"
	for m in chi.modifiers
	if m.type == "ARMATURE"
	if m.object == pose_obj
	]

	return tgt_obj_l
