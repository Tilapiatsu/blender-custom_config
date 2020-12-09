import bpy, subprocess,ast, re
from bpy.app.handlers import persistent
from bpy.types import Operator
import datetime

class RENTASKLIST_OT_probar_modaltimer(Operator):
	bl_idname = "rentask.probar_modal_timer"
	bl_label = "Modal Timer Operator"

	_timer = None

	def modal(self, context, event):
		sc = bpy.context.scene
		props = sc.rentask.rentask_main
		colle = sc.rentask.rentask_colle

		if not props.probar_active:
			context.window_manager.event_timer_remove(self._timer) #オフなら除去
			return {'FINISHED'}

		if event.type == 'TIMER': # n秒ごとに実行
			# for item in colle:
			# 	if not item.complete:
			# 		probar_update_status(item)

			if bpy.context.region:
				bpy.context.region.tag_redraw()
		return {'PASS_THROUGH'}

	def execute(self, context):
		sc = bpy.context.scene
		props = sc.rentask.rentask_main

		wm = context.window_manager
		# prefs = context.preferences.addons[__name__.partition('.')[0]].preferences

		# n秒ごとに機会を出力するタイマーを設定
		# self._timer = wm.event_timer_add(prefs.probar_monitoring_interval, window=context.window)
		self._timer = wm.event_timer_add(1, window=context.window)
		wm.modal_handler_add(self)

		return {'RUNNING_MODAL'}
