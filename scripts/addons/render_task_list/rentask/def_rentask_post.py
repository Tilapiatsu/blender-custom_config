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


def end_processing_type(self,context):
	props = bpy.context.scene.rentask
	p_rtask = props.rentask_main
	end_cmd_l = []

	# シャットダウンするためのコマンド
	if p_rtask.end_processing_type == "SHUTDOWN":
		end_cmd_l.append("shutdown.exe -s -f -t 0")

	# 再起動するためのコマンド
	elif p_rtask.end_processing_type == "REBOOT":
		end_cmd_l.append("shutdown.exe -r -f -t 0")

	# スリープ（スタンバイ）状態にするためのコマンド
	elif p_rtask.end_processing_type == "SLEEP":
		end_cmd_l.append("rundll32.exe PowrProf.dll,SetSuspendState")

	# 休止状態にするためのコマンド
	elif p_rtask.end_processing_type == "PAUSE":
		end_cmd_l.append("powercfg -h on\n")

	# Blenderを終了
	elif p_rtask.end_processing_type == "QUIT_BLENDER":
		end_cmd_l.append("QUIT_BLENDER")

	if end_cmd_l:
		return end_cmd_l
