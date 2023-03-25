import bpy, os
from ..utils import (
get_item_scene,
get_item_camera,
get_item_view_layer
)


def restore_setting(self):
	item = self.plan_sc_list[0]
	tgt_sc = get_item_scene(item)

	# レンダリング設定を元に戻す
	tgt_sc.render.filepath = self.backup_dic[tgt_sc]["filepath"]
	tgt_sc.render.resolution_x = self.backup_dic[tgt_sc]["resolution_x"]
	tgt_sc.render.resolution_y = self.backup_dic[tgt_sc]["resolution_y"]
	tgt_sc.render.resolution_percentage = self.backup_dic[tgt_sc]["resolution_percentage"]
	tgt_sc.render.image_settings.file_format = self.backup_dic[tgt_sc]["file_format"]
	tgt_sc.render.engine = self.backup_dic[tgt_sc]["engine"]
	tgt_sc.camera = bpy.data.objects[self.backup_dic[tgt_sc]["camera"]]
	tgt_sc.frame_start = self.backup_dic[tgt_sc]["frame_start"]
	tgt_sc.frame_end = self.backup_dic[tgt_sc]["frame_end"]
	tgt_sc.frame_current = self.backup_dic[tgt_sc]["frame_current"]
	if tgt_sc.render.engine == "CYCLES":
		tgt_sc.cycles.samples = self.backup_dic[tgt_sc]["cycles_samples"]
	if tgt_sc.render.engine == "BLENDER_EEVEE":
		tgt_sc.eevee.taa_render_samples = self.backup_dic[tgt_sc]["eevee_samples"]
	tgt_sc.view_settings.view_transform = self.backup_dic[tgt_sc]["view_transform"]


	# コンポジットノードのシーンとビューレイヤーを元に戻す
	if item.change_render_layer_node:
		for nd, nd_scene, nd_layer in self.backup_dic[tgt_sc]["compnode"]:
			nd.scene = nd_scene
			nd.layer = nd_layer


	# 非表示データを元に戻す
	if not item.hide_data_type == "NONE":
		if item.hide_data_name:
			data_i_l = item.hide_data_tmp_list.split(",")
			for data_i in data_i_l:
				if data_i in getattr(bpy.data,item.hide_data_type):
					getattr(bpy.data,item.hide_data_type)[data_i].hide_render = False

	# シーンを元に戻す
	item.scene = item.material_override_restore_scene_name
	item.material_override_restore_scene_name = ""
	item.hide_data_tmp_list = ""
	item.parent_item_name = ""
