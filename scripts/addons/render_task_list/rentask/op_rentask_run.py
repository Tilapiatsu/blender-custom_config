import bpy, os, sys, subprocess, datetime
import ast # 文字列を辞書にする
from bpy.props import *
from bpy.types import Operator
from .def_rentask_pre import create_filepath
from ..utils import (
get_item_scene,
get_task_temp_path,
get_log_file_path,
)
from .def_rentask_invoke import *
from .def_rentask_pre import *
from .def_rentask_post import *
from .op_rentask_convert_dic import *
from .def_rentask_bfile import *
from .def_rentask_bfile_call import *


class RENTASKLIST_OT_rentask_run(Operator):
	bl_idname = "rentask.rentask_run"
	bl_label = "Render Task Run"
	bl_description = ""
	bl_options = {'REGISTER','UNDO'}

	run_from_script_text : StringProperty()


	# @classmethod
	# def poll(cls, context):
	# 	sc = bpy.context.scene
	# 	props = sc.rentask
	# 	ptask_main = props.rentask_main
	# 	colle = props.rentask_colle
	# 	return not (len(colle) == 0 and ptask_main.bfile_type == "EXTERNAL")


	# invoke
	def invoke(self, context, event):
		sc = bpy.context.scene
		props = sc.rentask
		ptask_main = props.rentask_main
		colle = props.rentask_colle

		self._timer = None
		self.stop = None
		self.rendering = False
		self.old_scene = sc
		self.plan_sc_list = []
		self.remove_sc_l = []
		self.render_count_now = 1
		self.filepath = ""
		cmd_dic = {}


		# 外部blendファイルモードの場合、タスク用辞書を作成
		temp_path = get_task_temp_path()

		if ptask_main.bfile_type == "EXTERNAL" and not self.run_from_script_text:
			if not len(colle):
				bpy.ops.render.render('INVOKE_DEFAULT')
				return{'FINISHED'}

			cmd_dic = convert_items_to_dic(self,context)

			with open(temp_path, mode='w') as f:
				f.write(str(cmd_dic))
			self.report({'INFO'}, "Open Blend File and Render")
			bfile_subprocess_call(str(cmd_dic))
			return{'FINISHED'}
		else:
			# クリーンに
			with open(temp_path, mode='w') as f:
				f.write("")

			# ログをクリーンに
			with open(get_log_file_path(), mode='w') as f:
				f.write("")


		# 外部blendファイルから実行した場合、辞書を元にアイテムを作る
		if self.run_from_script_text:
			# 既存のアイテムはすべて削除
			colle.clear()

			# 辞書のデータをアイテムにする
			cmd_dic = ast.literal_eval(self.run_from_script_text)
			item = colle.add()
			for key in cmd_dic.keys():
				setattr(item,key,cmd_dic[key])

			item.blendfile = ""
			self.plan_sc_list.append(item)



			# もろもろの設定変更
			invoke_setting(self, context, event,cmd_dic=cmd_dic)
			# 設定のバックアップ
			invoke_backup_dic(self, context, event)
			# マテリアルオーバーライド
			set_material_override(self,item)
			# 非表示データ
			set_hide_data(self,item)
			self.plan_count = len(self.plan_sc_list)
			self.do_rendering(context)


		# リストアイテムがないなら通常のレンダリングをして終了
		if not len(colle):
			bpy.ops.render.render('INVOKE_DEFAULT')
			return{'FINISHED'}

		# もろもろの設定変更
		invoke_setting(self, context, event,cmd_dic=cmd_dic)

		# 設定のバックアップ
		invoke_backup_dic(self, context, event)

		self.plan_count = len(self.plan_sc_list)

		# ハンドラーの追加
		bpy.app.handlers.render_init.append(self.pre)
		bpy.app.handlers.render_complete.append(self.post)
		bpy.app.handlers.render_cancel.append(self.cancelled)
		self._timer = bpy.context.window_manager.event_timer_add(0.5, window=bpy.context.window)
		bpy.context.window_manager.modal_handler_add(self)


		# ログレベルを DEBUG に変更

		return {"RUNNING_MODAL"}


	# モーダル
	def modal(self, context, event):
		if not event.type == 'TIMER':
			return {'RUNNING_MODAL'}

		# モーダルを終了
		is_cancel = (self.stop is True or event.type == "ESC")
		end_list = (not self.plan_sc_list, self.stop is True, event.type == "ESC")
		if True in end_list:
			self.end_process(context,is_cancel=is_cancel)
			return{'FINISHED'}

		# ログ情報をプロパティへ
		ptask_main = bpy.context.scene.rentask.rentask_main
		if ptask_main.bfile_type == "EXTERNAL":
			self.set_job_status()


		# レンダリング
		if self.rendering is False:
			self.do_rendering(context)

		return {'RUNNING_MODAL'}


	# レンダリング開始時
	def pre(self, dummy, thrd = None):
		self.rendering = True


	# レンダリング終了時
	def post(self, dummy, thrd = None):
		restore_setting(self)

		# レンダリング予定リストから削除
		self.plan_sc_list.pop(0)

		self.render_count_now += 1
		self.rendering = False


	# キャンセル
	def cancelled(self, dummy, thrd = None):
		restore_setting(self)
		self.stop = True


	# レンダリング実行
	def do_rendering(self,context):

		item = self.plan_sc_list[0]
		tgt_sc = get_item_scene(item)

		# レンダリング前の様々な設定変更
		is_anime, scene_name, view_layer_name = pre_set_render_setting(self, context, tgt_sc=tgt_sc, item=item)

		pre_hide_data(self, item)
		sc = bpy.context.scene


		# 進捗メッセージ
		info_text = "[%s / %s] : '%s'" % (
			str(self.render_count_now),
			str(self.plan_count),
			item.name,
			)
		self.report({'INFO'}, info_text)

		# render
		bpy.ops.render.render('INVOKE_DEFAULT',
		animation=is_anime,
		scene=scene_name,
		layer=view_layer_name,
		write_still=True,
		)

	# 終了時の処理
	def end_process(self,context,is_cancel):
		sc = self.old_scene
		props = sc.rentask
		colle = props.rentask_colle

		# 追加したハンドラーを削除
		bpy.app.handlers.render_init.remove(self.pre)
		bpy.app.handlers.render_complete.remove(self.post)
		bpy.app.handlers.render_cancel.remove(self.cancelled)
		bpy.context.window_manager.event_timer_remove(self._timer)

		for c in self.remove_sc_l:
			bpy.data.scenes.remove(c)


		# 一時アイテムを削除 (逆順から)
		colle_count = len(colle)
		for id,im in enumerate(reversed(colle)):
			my_id = colle_count -1 - id
			im.is_excluse_item = False
			if im.is_tmp_item:
				colle.remove(my_id)


		# タスク用辞書の最初のキーを削除
		temp_path = get_task_temp_path()
		with open(temp_path, mode='r+') as f:
			jobs = f.read()
			if jobs:
				jobs_dic = ast.literal_eval(jobs)
				del jobs_dic[list(jobs_dic.keys())[0]]

				f.write(str(jobs_dic))


		# 終了メッセージ
		if is_cancel:
			self.report({'WARNING'}, "Stop Rendering")
		else:
			self.report({'INFO'}, "End of Rendering")

			# スリープなどの処理
			end_cmd_l = end_processing_type(self,context)
			if end_cmd_l:
				# print(end_cmd_l)
				if end_cmd_l[0] == "QUIT_BLENDER":
					bpy.ops.wm.quit_blender()
				else:
					subprocess.Popen(end_cmd_l)

			if self.run_from_script_text:
				# bpy.ops.wm.quit_blender()
				sys.exit(0)


	# ログ情報をプロパティへ
	def set_job_status(self):
		sc = bpy.context.scene
		props = sc.rentask
		ptask_main = props.rentask_main

		# {'wtime': '2020-12-09 14:49:21.090222', 'par': '4.166666666666666', 'frame': '24', 'mem': '113.83M', 'elapsed': '00:01.93', 'remaining': '00:02.41', 'tiles_done': '1', 'tiles_todo': '24'}
		with open(get_log_file_path(), mode='r') as f:
			log_l = f.readlines()
			if len(log_l):
				for line in log_l:
					if not line in {"",None}:
						continue
					line_dic = ast.literal_eval(line)


					if 'par' in line_dic:
						ptask_main.frame_current_per = float(line_dic["par"])
					if 'wtime' in line_dic:
						ptask_main.time_finish = str(datetime.datetime.strptime(line_dic["wtime"], "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=0))

				# par
				if line == "Blender quit":
					if 'wtime' in line_dic:
						ptask_main.time_finish = str(datetime.datetime.strptime(line_dic["wtime"], "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=0))






	# スクリプトから起動した場合のみ実行される
	def execute(self, context):
		print("")
		print("_____________  Render Setup  _____________")
		print("")

		self.invoke(context,None)

		return {'FINISHED'}
