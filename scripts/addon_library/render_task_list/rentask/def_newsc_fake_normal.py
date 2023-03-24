import bpy, re, random
from bpy.props import *
from bpy.types import Operator


class BUILDENODE_OT_scene_add_pass_faked_normal(Operator):
	bl_idname = "buildenode.add_pass_faked_normal"
	bl_label = "Create Normal Pass Scene"
	bl_description = "Link copy the current scene and create a scene,\nand That can output a 'normal pass' using Matcap"
	bl_options = {'REGISTER','UNDO'}


	def execute(self, context):
		old_scene = bpy.context.scene
		old_scene.use_fake_user = True

		# リンクコピー
		new_sc = old_scene.copy()
		new_sc.use_fake_user = True

		new_sc_name = add_new_scene(self, context, old_scene, new_sc, True, "_Normal")

		self.report({'INFO'}, "New Scene [ " + new_sc_name +  " ]")

		return {'FINISHED'}



# def newsc_fake_normal(self, context, old_scene, new_sc, is_normal, sc_name):
def newsc_fake_normal(self, context):
	old_scene = bpy.context.scene
	old_scene.use_fake_user = True

	# リンクコピー
	new_sc = old_scene.copy()
	new_sc.use_fake_user = True

	old_scene_name = old_scene.name

	# シーン設定を変更
	new_sc.use_fake_user = True
	new_sc.render.engine = 'BLENDER_WORKBENCH'
	new_sc.view_settings.view_transform = 'Standard'
	new_sc.render.film_transparent = True
	new_sc.display.render_aa = '8'
	new_sc.display.shading.single_color = (1, 1, 1)

	# if is_normal:
	new_sc.display.shading.light = 'MATCAP'
	new_sc.display.shading.studio_light = 'check_normal+y.exr'
	new_sc.display.shading.color_type = 'SINGLE'
	# else:
	# 	new_sc.display.shading.light = 'FLAT'
	# 	new_sc.display.shading.color_type = prefs.new_scene_color_type

	# if not prefs.new_scene_move:
	# 	bpy.context.space_data.shading.type = 'RENDERED'


	# リネーム
	new_sc.name = old_scene_name + sc_name
	new_sc_name = new_sc.name

	# if prefs.new_scene_move:
	# 	bpy.context.window.scene = new_sc
	# 	bpy.context.window.scene = old_scene


	return new_sc_name
