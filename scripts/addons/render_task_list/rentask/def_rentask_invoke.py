import bpy, os, re
from .op_rentask_item import RENTASKLIST_OT_rentask_item_duplicate
from ..utils import (
frame_set_format,
get_item_scene,
get_item_camera,
get_item_view_layer
)

# メイン invoke
def invoke_setting(self, context, event,cmd_dic):
	sc = bpy.context.scene
	props = sc.rentask
	colle = props.rentask_colle


	# 複数項目をレンダリングする場合は、タスクを分割する
	split_task_frame(self,context,event)
	split_task_scene(self,context,event)
	split_task_view_layer(self,context,event)
	split_task_camera(self,context,event)


	# レンダリングタスクに追加
	for item in colle:
		if item.blendfile:
			continue
		if item.is_excluse_item:
			continue
		if not item.use_render:
			continue

		# レンダリングタスクに追加
		self.plan_sc_list.append(item)

		# マテリアルオーバーライド
		set_material_override(self,item)

		# フェイクノーマル
		set_sc_fake_normal(self, item)

		# 非表示データ
		set_hide_data(self,item)


# マテリアルオーバーライド
def set_material_override(self,item):
	if not item.material_override_mat:
		return
	if not item.material_override_mat in bpy.data.materials:
		return

	item.material_override_restore_scene_name = item.scene

	dup_sc = duplicate_scene(self,'FULL_COPY')
	self.remove_sc_l.append(dup_sc)
	for obj in dup_sc.collection.all_objects:
		if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'GPENCIL'}:
			if len(obj.data.materials):
				obj.data.materials.clear()
			obj.data.materials.append(bpy.data.materials[item.material_override_mat])

	item.scene = dup_sc.name



# フェイクノーマル
def set_sc_fake_normal(self, item):
	if not item.fake_normal:
		return

	item.material_override_restore_scene_name = item.scene
	dup_sc = duplicate_scene(self,'LINK_COPY')
	self.remove_sc_l.append(dup_sc)

	# シーン設定を変更
	dup_sc.use_fake_user = True
	dup_sc.render.engine = 'BLENDER_WORKBENCH'
	dup_sc.view_settings.view_transform = 'Standard'
	dup_sc.render.film_transparent = True
	dup_sc.display.render_aa = '8'
	dup_sc.display.shading.single_color = (1, 1, 1)
	dup_sc.display.shading.light = 'MATCAP'
	dup_sc.display.shading.studio_light = 'check_normal+y.exr'
	dup_sc.display.shading.color_type = 'SINGLE'

	item.scene = dup_sc.name



# 非表示データ
def set_hide_data(self,item):
	if item.hide_data_type == "NONE":
		return
	if not item.hide_data_name:
		return

	hide_data_name = item.hide_data_name.replace(",  ",",").replace(", ",",")
	data_i_l = hide_data_name.split(",")
	hide_data_tmp_l = []
	for data_i in data_i_l:
		if data_i in getattr(bpy.data,item.hide_data_type):
			if not getattr(bpy.data,item.hide_data_type)[data_i].hide_render:
				hide_data_tmp_l.append(data_i)

	item.hide_data_tmp_list = ",".join(hide_data_tmp_l)




# タスクの分割 : フレーム
def split_task_frame(self,context,event):
	sc = bpy.context.scene
	props = sc.rentask
	colle = props.rentask_colle


	# フレーム
	for item in colle:
		if item.blendfile:
			continue
		if not item.use_render:
			continue
		if not item.frame:
			continue
		if item.mode == "ANIME":
			continue

		flame_l = frame_set_format(item.frame)
		for fl in flame_l:
			# new_item = RENTASKLIST_OT_rentask_item_duplicate.duplicate_item(self, bpy.context ,item , "")
			new_item = colle.add()
			for prop in dir(new_item):
				try:
					attr = getattr(item,prop)
					setattr(new_item, prop, attr)
				except:
					pass

			new_item.frame = fl
			new_item.is_tmp_item = True
			new_item.parent_item_name = item.name
			if ".." in fl:
				new_item.mode = "ANIME"
				new_item.frame_start = int((fl).split("..")[0])
				new_item.frame_end = int((fl).split("..")[1])
			else:
				new_item.mode = "IMAGE"


		item.is_excluse_item = True


# タスクの分割 : 全シーン
def split_task_scene(self,context,event):
	sc = bpy.context.scene
	props = sc.rentask
	colle = props.rentask_colle

	for item in colle:
		if item.blendfile:
			continue
		if not item.use_render:
			continue
		if not item.scene_all:
			continue

		for scn in bpy.data.scenes:
			if not scn.camera.hide_render:
				new_item = RENTASKLIST_OT_rentask_item_duplicate.duplicate_item(self,bpy.context,item ,"_%s" % scn.name)
				new_item.scene = scn.name
				new_item.is_tmp_item = True

		item.is_excluse_item = True


# タスクの分割 : 全ビューレイヤー
def split_task_view_layer(self,context,event):
	sc = bpy.context.scene
	props = sc.rentask
	colle = props.rentask_colle

	for item in colle:
		if item.blendfile:
			continue
		if item.is_excluse_item:
			continue
		if not item.use_render:
			continue
		if not item.view_layer_all:
			continue

		tgt_sc = get_item_scene(item)
		for vl in tgt_sc.view_layers:
			if vl.use:
				new_item = RENTASKLIST_OT_rentask_item_duplicate.duplicate_item(self,bpy.context ,item ,"_%s" % vl.name)
				new_item.view_layer = vl.name
				new_item.is_tmp_item = True

		item.is_excluse_item = True


# タスクの分割 : 全カメラ
def split_task_camera(self,context,event):
	sc = bpy.context.scene
	props = sc.rentask
	colle = props.rentask_colle

	for item in colle:
		if item.blendfile:
			continue
		if item.is_excluse_item:
			continue
		if not item.use_render:
			continue
		if not item.camera_all:
			continue

		tgt_sc = get_item_scene(item)
		for obj in tgt_sc.collection.all_objects:
			if not obj.hide_render:
				if obj.type == "CAMERA":
					new_item = RENTASKLIST_OT_rentask_item_duplicate.duplicate_item(self,bpy.context ,item ,"_%s" % obj.name)
					new_item.camera = obj.name
					new_item.is_tmp_item = True

		item.is_excluse_item = True


# シーンの複製
def duplicate_scene(self,sc_type):
	item = self.plan_sc_list[0]
	tgt_sc = get_item_scene(item)
	old_scene_name = tgt_sc.name

	# シーンの複製
	bpy.ops.scene.new(type=sc_type)
	new_sc = bpy.context.scene
	new_sc.name = old_scene_name + "_tmp"

	# アクティブシーンを戻す
	bpy.context.window.scene = tgt_sc

	return new_sc


# 設定のバックアップ
def invoke_backup_dic(self, context, event):
	self.backup_dic = {get_item_scene(c):{
		"filepath":get_item_scene(c).render.filepath,
		"resolution_x":get_item_scene(c).render.resolution_x,
		"resolution_y":get_item_scene(c).render.resolution_y,
		"resolution_percentage":get_item_scene(c).render.resolution_percentage,
		"file_format":get_item_scene(c).render.image_settings.file_format,
		"engine":get_item_scene(c).render.engine,
		"camera":get_item_scene(c).camera.name,
		"frame_start":get_item_scene(c).frame_start,
		"frame_end":get_item_scene(c).frame_end,
		"frame_current":get_item_scene(c).frame_current,
		"cycles_samples":get_item_scene(c).cycles.samples,
		"eevee_samples":get_item_scene(c).eevee.taa_render_samples,
		"view_transform":get_item_scene(c).view_settings.view_transform,
		"compnode":[(nd, nd.scene, nd.layer)
				for nd in bpy.context.scene.node_tree.nodes
				if nd.type == "R_LAYERS"
			],
		}
		for c in self.plan_sc_list
		}
