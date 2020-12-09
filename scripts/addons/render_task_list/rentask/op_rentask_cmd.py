import bpy, os, sys, subprocess
from bpy.props import *
from bpy.types import Operator


class RENTASKLIST_OT_rentask_cmd(Operator):
	bl_idname = "rentask.rentask_cmd"
	bl_label = "Cmd"
	bl_description = ""
	bl_options = {'REGISTER','UNDO'}


	def execute(self, context):
		props = bpy.context.scene.rentask
		colle = props.rentask_colle
		cmd_dic = {}

		for item in colle:
			if not item.use_render:
				continue

			tgt_sc = get_item_scene(item)

			item_option_dic = {}
			for key in item.keys():

				# blendファイル
				if key == "blendfile":
					if item.blendfile:
						item_option_dic[key] = getattr(item,key)
					else:
						item_option_dic[key] = bpy.data.filepath

				# ファイルパス
				elif key == "filepath":
					result_filepath = create_filepath(self, context, tgt_sc, item)
					item_option_dic[key] = result_filepath

				else:
					item_option_dic[key] = getattr(item,key)


			cmd_dic[item.name] = item_option_dic

		self.report({'INFO'}, str(cmd_dic))

		# Command Line Arguments — Blender Manual
		# https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html

		# result_cmd_dic = {}
		# app_path = sys.argv[0]
		# for dic in cmd_dic:
		# 	cmd = [app_path, '-b']
		#
		# 	for key in cmd_dic[dic].keys():
		#
		# 		# blendファイル
		# 		if key == "blendfile":
		# 			cmd = [app_path, '-b', cmd_dic[dic]["blendfile"]]
		#
		# 		# 出力パス
		# 		if key == "filepath":
		# 			cmd += ["--render-output", cmd_dic[dic]["filepath"]]
		# 		# シーン名
		# 		if key == "scene":
		# 			if cmd_dic[dic]["scene"]:
		# 				cmd += ["--scene", cmd_dic[dic]["scene"]]
		# 		# シード
		# 		if key == "thread":
		# 			if cmd_dic[dic]["thread"]:
		# 				cmd += ['-t', str(cmd_dic[dic]["thread"])]
		# 		# エンジン
		# 		if key == "engine":
		# 			if not cmd_dic[dic]["engine"] == "NONE":
		# 				cmd += ['-E', cmd_dic[dic]["engine"]]
		# 		# フォーマット
		# 		if key == "file_format":
		# 			if not cmd_dic[dic]["file_format"] == "NONE":
		# 				cmd += [' -F', cmd_dic[dic]["file_format"]]
		#
		#
		# 		# レンダリングのフレーム指定は最後にすること
		# 		# フレーム
		# 		if key == "mode":
		# 			if cmd_dic[dic]["mode"] == 'IMAGE':
		# 				if key == "frame":
		# 					cmd += ['-f',cmd_dic[dic]["frame"]]
		#
		# 			elif key["mode"] == 'ANIME':
		# 				cmd += ['-a']
		#
		# 	result_cmd_dic[dic] = cmd
		#
		#
		#
		# self.report({'INFO'}, str(result_cmd_dic))

		return {'FINISHED'}
