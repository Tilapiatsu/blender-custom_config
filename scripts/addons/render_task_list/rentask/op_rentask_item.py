import bpy, re, os, glob
from bpy.props import *
from bpy.types import Operator, OperatorFileListElement

from ..modules import blendfile # 高速blendデータ(カレントシーン名・スタート・エンド)取得
from bpy.types import Operator, OperatorFileListElement
from bpy_extras.io_utils import ImportHelper
from ..utils import (
get_item_scene,
get_item_camera,
get_item_view_layer
)


class RENTASKLIST_OT_rentask_bfile_add(Operator, ImportHelper):
	bl_idname = "rentask.rentask_bfile_add"
	bl_label = "Import .blend File"
	bl_description = "Add the blend file to use for rendering to the list\nIf no file is specified, all .blend files in the folder will be added"
	bl_options = {'UNDO'}

	filename_ext = ".blend"
	success_msg = 'Preset Import'

	filter_glob : StringProperty(default="*.blend", options={'HIDDEN'},maxlen=255, )
	files       : CollectionProperty(name="BVH files", type=OperatorFileListElement, )
	directory   : StringProperty(subtype='DIR_PATH')


	def execute(self, context):
		sc = bpy.context.scene
		props = sc.rentask.rentask_main
		colle = sc.rentask.rentask_colle

		is_bfile  = [f for f in self.files if re.findall(".blend$",f.name)]

		if is_bfile: # 選択したものがblendファイルがある場合
			# 複数ファイルを読み込む
			directory = self.directory
			for file in self.files:
				filepath = os.path.join(directory, file.name)
				item = add_bfile_item(self,context,filepath)

			self.report({'INFO'}, "Add New Item " + str(len(self.files)))


		else: # パスを選択した場合はそのディレクトリ内のblendファイルを読み込む
			filepath_l = [p for p in glob.glob(self.directory + "*.blend") if os.path.isfile(p)]
			for filepath in filepath_l:
				item = add_bfile_item(self,context,filepath)

			self.report({'INFO'}, "Add New Item " + str(len(filepath_l)))

		sc.rentask.rentask_index = len(colle) - 1
		return{'FINISHED'}


def add_bfile_item(self,context,filepath):
	sc = bpy.context.scene
	colle = sc.rentask.rentask_colle
	props = sc.rentask.rentask_main

	item = colle.add()

	# bfile
	item.blendfile = filepath

	# name
	f_name = os.path.basename(filepath)
	itemname = f_name
	count = [i.name for i in colle if re.findall("^" + f_name,i.name)]
	if count:
		count = str(len(count) + 1)
		itemname = f_name + " " + count
	item.name = itemname
	props.rentask_index = (len(colle)-1)

	try:
		quick_get_bfile_status(self,context,item,filepath)
	except Exception as e:
		self.report({'INFO'}, "Failed to read status")
		print(type(e) , str(e))

	return item


def quick_get_bfile_status(self,context,item,filepath):

	dic = {}
	# view_layers = []
	with blendfile.open_blend(filepath) as blend:
		for block in blend.blocks:
			if block.code == b'WM':
				window = block.get_pointer(b'winactive')
				current_scene = window.get_pointer(b'scene')
				current_scene_name = current_scene[b'id', b'name'][2:].decode('utf-8')

			# if block.dna_type_name == 'ViewLayer':
			# 	view_layers.append(block.get((b'name')))

		scenes = [b for b in blend.blocks if b.code == b'SC']
		for scene in scenes:
			# view_layers = []
			# for k, v in scene.items():
			# 	if k == b'view_layers':
			# 		for vl in v:
			# 			view_layers += [vl]

			scene_name    = scene[b'id', b'name'][2:].decode('utf-8')
			engine        = scene[b'r', b'engine'].decode('utf-8')
			frame_current = scene[b'r', b'cfra']
			frame_start   = scene[b'r', b'sfra']
			frame_end     = scene[b'r', b'efra']
			outpath       = scene[b'r', b'pic'].decode('utf-8')
			sc_camera     = scene.get_pointer(b'camera')
			frame_end     = scene[b'r', b'efra']
			# view_layers =   scene[b'view_layers']
			# view_layers =   scene.get_pointer(b'view_layers')

			new_dic = {scene_name : {
			"current" : str(frame_current),
			"start"   : str(frame_start),
			"end"     : str(frame_end),
			"outpath" : outpath,
			"engine" : engine,
			"scene_camera"  : repr(sc_camera),
			# "viewlayer"  : view_layers,

			}}


			dic.update(new_dic)

	# set_status(self,context,item,dic,current_scene_name,True)

	# item.sc_data = str(dic)
	return


class RENTASKLIST_OT_rentask_item_add(Operator):
	bl_idname = "rentask.rentask_item_add"
	bl_label = "Add"
	bl_description = "Add"
	bl_options = {"REGISTER","UNDO"}

	def execute(self, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		item_name = "task"
		if len(colle):
			count = [i.name for i in colle if re.findall("^" + item_name,i.name)]
			if count:
				count = str(len(count) + 1)

				item_name = item_name + " " + count

		item = colle.add()
		item.name = item_name
		item.filepath = "{path_dir}\{path_name}"

		props.rentask_index = len(colle) - 1
		return {'FINISHED'}


class RENTASKLIST_OT_rentask_item_save_setting(Operator):
	bl_idname = "rentask.rentask_item_save_setting"
	bl_label = "Add(Save Current Setting)"
	bl_description = "Add a task item based on the settings of the current scene"
	bl_options = {"REGISTER","UNDO"}

	frame : BoolProperty(name="Frame",default=True)
	filepath : BoolProperty(name="Filepath",default=True)
	resolution_x : BoolProperty(name="Resolution X",default=True)
	resolution_y : BoolProperty(name="Resolution Y",default=True)
	resolution_percentage : BoolProperty(name="Resolution Percentage",default=True)
	file_format : BoolProperty(name="File Format",default=True)
	engine : BoolProperty(name="Engine",default=True)
	samples : BoolProperty(name="Samples",default=True)
	camera : BoolProperty(name="Camera",default=True)
	scene : BoolProperty(name="Scene",default=True)
	view_layer : BoolProperty(name="View Layer",default=True)

	def execute(self, context):
		sc = bpy.context.scene
		props = sc.rentask
		colle = props.rentask_colle
		item_name = "task"
		if len(colle):
			count = [i.name for i in colle if re.findall("^" + item_name,i.name)]
			if count:
				count = str(len(count) + 1)

				item_name = item_name + " " + count

		item = colle.add()
		item.name = item_name
		item.filepath = "{path_dir}\{path_name}"


		# フレーム
		if self.frame:
			item.frame = str(sc.frame_current)

		# ファイルパス
		if self.filepath:
			item.filepath = sc.render.filepath


		# 解像度
		if self.resolution_x:
			item.resolution_x = sc.render.resolution_x
		if self.resolution_y:
			item.resolution_y = sc.render.resolution_y
		if self.resolution_percentage:
			item.resolution_percentage = sc.render.resolution_percentage

		# ファイルフォーマット
		if self.file_format:
			item.file_format = sc.render.image_settings.file_format

		# レンダーエンジン
		if self.engine:
			try:
				item.engine = sc.render.engine
			except:
				item.engine = "OTHER"
				item.engine_other = sc.render.engine

		if self.samples:
			if sc.render.engine == "CYCLES":
				item.samples = sc.cycles.samples
			if sc.render.engine == "BLENDER_EEVEE":
				item.samples = sc.eevee.taa_render_samples

		# カメラ
		if self.camera:
			try:
				item.camera_pointer = sc.camera
			except:
				sc.camera = sc.camera


		if self.scene:
			item.scene = bpy.context.scene.name

		if self.view_layer:
			item.view_layer = bpy.context.view_layer.name


		props.rentask_index = len(colle) - 1
		return {'FINISHED'}


class RENTASKLIST_OT_rentask_item_remove(Operator):
	bl_idname = "rentask.rentask_item_remove"
	bl_label = "Remove"
	bl_description = "Remove"
	bl_options = {"REGISTER","UNDO"}

	item : IntProperty(name="Item")

	@classmethod
	def poll(cls, context):
		return len(bpy.context.scene.rentask.rentask_colle) > 0

	def execute(self, context):
		index = self.item
		props = bpy.context.scene.rentask
		colle = props.rentask_colle

		colle.remove(index)
		for cam in colle:
			if cam.cindex > index:
				cam.cindex = cam.cindex - 1
			if len(colle) == index:
				props.rentask_index = index - 1
			else:
				props.rentask_index = index
		return {'FINISHED'}


class RENTASKLIST_OT_rentask_item_duplicate(Operator):
	bl_idname = "rentask.rentask_item_duplicate"
	bl_label = "Duplicate Active Item"
	bl_description = "Duplicate Active Item"
	bl_options = {'REGISTER', 'UNDO'}


	@classmethod
	def poll(cls, context):
		return len(bpy.context.scene.rentask.rentask_colle) > 0

	def execute(self, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle

		old_im = colle[props.rentask_index]
		item = self.duplicate_item(context,old_im,"")

		return{'FINISHED'}

	def duplicate_item(self, context,old_item,name_text):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		count_name = ""

		count = [i.name for i in colle if re.findall("^" + old_item.name,i.name)]
		if count:
			count_name = old_item.name + " " + str(len(count) + 1)

		new_item = colle.add()

		for prop in dir(new_item):
			try:
				attr = getattr(old_item,prop)
				setattr(new_item, prop, attr)
			except:
				pass

		if name_text:
			new_item.name = old_item.name + name_text
		else:
			new_item.name = count_name

		return new_item


class RENTASKLIST_OT_rentask_item_move(Operator):
	bl_idname = "rentask.rentask_item_move"
	bl_label = "Move an item in the list"

	direction : EnumProperty(items=(('UP', 'Up', ""), ('DOWN', 'Down', ""),))

	@classmethod
	def poll(cls, context):
		return len(bpy.context.scene.rentask.rentask_colle) > 0

	def move_index(self):
		""" Move index of an item render queue while clamping it. """
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		index = props.rentask_index
		list_length = len(colle) - 1 # (index starts at 0)
		new_index = index + (-1 if self.direction == 'UP' else 1)
		props.rentask_index = max(0, min(new_index, list_length))


	def execute(self, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		index = props.rentask_index

		neighbor = index + (-1 if self.direction == 'UP' else 1)
		colle.move(neighbor, index)
		self.move_index()

		return{'FINISHED'}


class RENTASKLIST_OT_rentask_hide_data_name_set(Operator):
	bl_idname = "rentask.rentask_hide_data_name_set"
	bl_label = "Set Hide Data Name"
	bl_description = "Set Hide Data Name"
	bl_options = {"REGISTER","UNDO"}

	@classmethod
	def poll(cls, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		if len(colle):
			return len(colle)

	def execute(self, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		item = colle[props.rentask_index]

		hide_data_name = item.hide_data_name.replace(",  ",",").replace(", ",",")
		data_i_l = hide_data_name.split(",")

		if item.hide_data_type == "objects":
			for obj in bpy.context.selected_objects:
				data_i_l.append(obj.name)

		elif item.hide_data_type == "collections":
			data_i_l.append(bpy.context.view_layer.active_layer_collection.name)

		data_i_l = sorted(set(data_i_l), key=data_i_l.index)
		# data_i_l = [i for i in data_i_l if not i == ","]

		item.hide_data_name = ",".join(data_i_l)

		return {'FINISHED'}


class RENTASKLIST_OT_rentask_filepath_name_add(Operator):
	bl_idname = "rentask.rentask_filepath_name_add"
	bl_label = "Add Filepath Name"
	bl_description = "Add Filepath Name"
	bl_options = {"REGISTER","UNDO"}

	text : StringProperty(name="Text")

	@classmethod
	def poll(cls, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		if len(colle):
			return len(colle)

	def execute(self, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		item = colle[props.rentask_index]
		add_text = self.text
		if item.filepath:
			if not re.findall("/$",item.filepath):
				add_text = "_" + self.text
		item.filepath += add_text

		return {'FINISHED'}

class RENTASKLIST_OT_rentask_load_setting(Operator):
	bl_idname = "rentask.rentask_load_setting"
	bl_label = "Load Settings"
	bl_description = "Load Settings"
	bl_options = {"REGISTER","UNDO"}

	item : IntProperty(name="Item",options={"HIDDEN"})

	frame : BoolProperty(name="Frame",default=True)
	filepath : BoolProperty(name="Filepath",default=True)
	resolution_x : BoolProperty(name="Resolution X",default=True)
	resolution_y : BoolProperty(name="Resolution Y",default=True)
	resolution_percentage : BoolProperty(name="Resolution Percentage",default=True)
	file_format : BoolProperty(name="File Format",default=True)
	engine : BoolProperty(name="Engine",default=True)
	samples : BoolProperty(name="Samples",default=True)
	camera : BoolProperty(name="Camera",default=True)
	scene : BoolProperty(name="Scene",default=True)
	view_layer : BoolProperty(name="View Layer",default=True)


	@classmethod
	def poll(cls, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		if len(colle):
			return len(colle)

	def execute(self, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		item = colle[self.item]
		tgt_sc = get_item_scene(item)

		props.rentask_index = self.item

		if self.frame:
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



		# 解像度
		if self.resolution_x:
			if item.resolution_x:
				tgt_sc.render.resolution_x = item.resolution_x
		if self.resolution_y:
			if item.resolution_y:
				tgt_sc.render.resolution_y = item.resolution_y
		if self.resolution_percentage:
			if not item.resolution_percentage == 0:
				tgt_sc.render.resolution_percentage = item.resolution_percentage

		# ファイルフォーマット
		if self.file_format:
			if not item.file_format == "NONE":
				tgt_sc.render.image_settings.file_format = item.file_format

		# レンダーエンジン
		if self.engine:
			if not item.engine == "NONE":
				if item.engine == "OTHER":
					tgt_sc.render.engine = item.engine_other
				else:
					tgt_sc.render.engine = item.engine

		# サンプル数
		if self.samples:
			if not item.samples == 0:
				if tgt_sc.render.engine == "CYCLES":
					tgt_sc.cycles.samples = item.samples
				if tgt_sc.render.engine == "BLENDER_EEVEE":
					tgt_sc.eevee.taa_render_samples = item.samples
		# カメラ
		if self.camera:
			if item.camera or item.camera_pointer:
				tgt_sc.camera = get_item_camera(item)


		# renderオペレーターのオプションの指定
		# if item.mode == "ANIME":
		# 	is_anime = True
		# else:
		# 	is_anime = False

		# if self.scene:
		# 	if item.scene:
		# 		scene_name = item.scene
		# 	else:
		# 		scene_name = bpy.context.scene.name

		if self.view_layer:
			if item.view_layer:
				bpy.context.window.view_layer = tgt_sc.view_layers[item.view_layer]

		self.report({'INFO'}, "Load Setting")
		return {'FINISHED'}
