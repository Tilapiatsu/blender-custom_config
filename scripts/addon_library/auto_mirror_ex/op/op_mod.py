import bpy
from bpy.props import *
from bpy.types import Operator
from ..utils import (
		mesh_mod_items,
		gp_mod_items,
	)


# ミラーモディファイアの一括切り替え
class AUTOMIRROR_OT_mirror_toggle(Operator):
	bl_idname = "automirror.toggle_mirror"
	bl_label = "Toggle Mirror"
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Switch on / off the Mirror Modifier"


	show_viewport     : BoolProperty(name="Viewport",default=True)
	show_render     : BoolProperty(name="Render")
	show_in_editmode     : BoolProperty(name="In edit mode")
	show_on_cage     : BoolProperty(name="On cage")

	only_same_name     : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="Mirror",name="Modifier Name")

	global mesh_mod_items
	mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mesh_mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		row.prop(self, "mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")
		# row = col.row(align=True)
		# row.prop(self, "move_count")

		row = layout.row(align=True)
		row.prop(self, "show_render",text="",icon="RESTRICT_RENDER_OFF" if self.show_render else "RESTRICT_RENDER_ON")
		row.prop(self, "show_viewport",text="",icon="RESTRICT_VIEW_OFF" if self.show_viewport else "RESTRICT_VIEW_ON")
		row.prop(self, "show_in_editmode",text="",icon="EDITMODE_HLT")
		row.prop(self, "show_on_cage",text="",icon="OUTLINER_DATA_MESH")



	def toggle_status(self, context,mod):
		if self.show_viewport:
			if mod.show_viewport == True:
				mod.show_viewport = False
			else:
				mod.show_viewport = True

		if self.show_render:
			if mod.show_render == True:
				mod.show_render = False
			else:
				mod.show_render = True

		if self.show_in_editmode:
			if mod.show_in_editmode == True:
				mod.show_in_editmode = False
			else:
				mod.show_in_editmode = True

		if self.show_on_cage:
			if mod.show_on_cage == True:
				mod.show_on_cage = False
			else:
				mod.show_on_cage = True


	def execute(self, context):
		old_act = bpy.context.view_layer.objects.active

		for obj in bpy.context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			if not len(obj.modifiers):
				continue
			for mod in obj.modifiers:
				if self.only_same_name:
					if mod.name == self.mod_name:
						self.toggle_status(context,mod)
				else:
					if mod.type == self.mod_type:
						self.toggle_status(context,mod)


		bpy.context.view_layer.objects.active = old_act

		return {'FINISHED'}


# ミラーモディファイアの一括ターゲット設定
class AUTOMIRROR_OT_mirror_target_set(Operator):
	bl_idname = "automirror.target_set"
	bl_label = "Target Set"
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Set the Active object as the 'mirror target object' of the mirror modifier"

	clear : BoolProperty(name="Clear")
	only : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="mirror_mirror",name="Modifier Name")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.prop(self, "clear")

		col = layout.column(align=True)
		col.prop(self, "only")
		row = col.row(align=True)
		if not self.only:
			row.active=False
		row.prop(self, "mod_name")

	def execute(self, context):
		if self.clear:
			try:
				for obj in bpy.context.selected_objects:
					for mod in obj.modifiers:
						if mod.type == "MIRROR":
							if self.only:
								if mod.name == self.mod_name:
									mod.mirror_object = None
							else:
								mod.mirror_object = None
			except: pass
			return {'FINISHED'}


		act_obj = bpy.context.object
		try:
			for obj in bpy.context.selected_objects:
				if obj == act_obj:
					continue
				for mod in obj.modifiers:
					if mod.type == "MIRROR":
						if self.only:
							if mod.name == self.mod_name:
								mod.mirror_object = act_obj
						else:
							mod.mirror_object = act_obj
		except: pass

		return {'FINISHED'}


# モディファイアの一括追加
class AUTOMIRROR_OT_modifier_add(Operator):
	bl_idname = "automirror.modifier_add"
	bl_label = "Add Modifier"
	bl_description = "Add a specific modifier on the selected object"
	bl_options = {'REGISTER', 'UNDO'}

	only_same_name     : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="",name="Modifier Name")

	global mesh_mod_items
	global gp_mod_items
	mesh_mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mesh_mod_items)
	gp_mod_type : EnumProperty(default="GP_MIRROR",name="Modifier Type", description="",items = gp_mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		if bpy.context.view_layer.objects.active.type == "GPENCIL":
			row.prop(self, "gp_mod_type")
		else:
			row.prop(self, "mesh_mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")


	def execute(self, context):
		old_obj = bpy.context.view_layer.objects.active

		# アクティブがグリースペンシルならグリースペンシル用のプロパティを利用
		if old_obj.type == "GPENCIL":
			global gp_mod_items
			tgt_mod_items =  gp_mod_items
			tgt_modtype = self.gp_mod_type
		else:
			global mesh_mod_items
			tgt_mod_items =  mesh_mod_items
			tgt_modtype = self.mesh_mod_type


		# 名前を決定
		if self.mod_name:
			mod_name = self.mod_name
		else:
			mod_name = tgt_modtype.capitalize()
			for keyname, label, desc, icon_val, num in tgt_mod_items:
				if tgt_modtype == keyname:
					mod_name = label


		# モディファイアを追加
		for obj in bpy.context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			if old_obj.type == "GPENCIL":
				if obj.type in {"GPENCIL"}:
					mod = obj.grease_pencil_modifiers.new(mod_name, tgt_modtype)
			else:
				if obj.type in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
					mod = obj.modifiers.new(mod_name, tgt_modtype)


		bpy.context.view_layer.objects.active = old_obj
		self.report({'INFO'}, "Add Modifier [%s]" % tgt_modtype.capitalize())
		return {'FINISHED'}


# モディファイアの一括適用
class AUTOMIRROR_OT_mirror_apply(Operator):
	bl_idname = "automirror.apply"
	bl_label = "Apply Modifier"
	bl_description = "Apply a specific modifier on the selected object"
	bl_options = {'REGISTER', 'UNDO'}

	only_same_name     : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="Mirror",name="Modifier Name")

	global mesh_mod_items
	global gp_mod_items
	mesh_mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mesh_mod_items)
	gp_mod_type : EnumProperty(default="GP_MIRROR",name="Modifier Type", description="",items = gp_mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		if bpy.context.view_layer.objects.active.type == "GPENCIL":
			row.prop(self, "gp_mod_type")
		else:
			row.prop(self, "mesh_mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")


	def invoke(self, context,event):
		obj = bpy.context.view_layer.objects.active
		try:
			if obj.type == "GPENCIL":
				if len(obj.grease_pencil_modifiers):
					self.gp_mod_type = obj.grease_pencil_modifiers.active.type
			else:
				if len(obj.modifiers):
					self.mesh_mod_type = obj.modifiers.active.type
		except Exception as e: print(e)
		return self.execute(context)


	def execute(self, context):
		old_act = bpy.context.view_layer.objects.active


		# アクティブがグリースペンシルならグリースペンシル用のプロパティを利用
		if old_act.type == "GPENCIL":
			tgt_modtype = self.gp_mod_type
		else:
			tgt_modtype = self.mesh_mod_type


		# モディファイアを適用
		for obj in bpy.context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			if old_act.type == "GPENCIL":
				if obj.type in {"GPENCIL"}:
					for mod in obj.grease_pencil_modifiers:
						if self.only_same_name:
							if mod.name == self.mod_name:
								bpy.ops.object.gpencil_modifier_apply(modifier=mod.name)
						else:
							if mod.type == tgt_modtype:

								bpy.ops.object.gpencil_modifier_apply(modifier=mod.name)
			else:
				if obj.type in {"MESH"}:
					for mod in obj.modifiers:
						if self.only_same_name:
							if mod.name == self.mod_name:
								bpy.ops.object.modifier_apply(modifier=mod.name)
						else:
							if mod.type == tgt_modtype:

								bpy.ops.object.modifier_apply(modifier=mod.name)


		bpy.context.view_layer.objects.active = old_act
		self.report({'INFO'}, "Apply Modifier [%s]" % tgt_modtype.capitalize())
		return {'FINISHED'}


# モディファイアの一括削除
class AUTOMIRROR_OT_mirror_remove(Operator):
	bl_idname = "automirror.remove"
	bl_label = "Remove Modifier"
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Remove a specific modifier on the selected object"

	only_same_name : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="Mirror",name="Modifier Name")

	global mesh_mod_items
	global gp_mod_items
	mesh_mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mesh_mod_items)
	gp_mod_type : EnumProperty(default="GP_MIRROR",name="Modifier Type", description="",items = gp_mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0


	def invoke(self, context,event):
		obj = bpy.context.view_layer.objects.active
		try:
			if obj.type == "GPENCIL":
				if len(obj.grease_pencil_modifiers):
					self.gp_mod_type = obj.grease_pencil_modifiers.active.type
			else:
				if len(obj.modifiers):
					self.mesh_mod_type = obj.modifiers.active.type
		except Exception as e: print(e)
		return self.execute(context)

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		if bpy.context.view_layer.objects.active.type == "GPENCIL":
			row.prop(self, "gp_mod_type")
		else:
			row.prop(self, "mesh_mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")

	def execute(self, context):
		old_act = bpy.context.view_layer.objects.active

		# アクティブがグリースペンシルならグリースペンシル用のプロパティを利用
		if old_act.type == "GPENCIL":
			tgt_modtype = self.gp_mod_type
		else:
			tgt_modtype = self.mesh_mod_type


		for obj in bpy.context.selected_objects:
			if old_act.type == "GPENCIL":
				if obj.type in {"GPENCIL"}:
					for mod in obj.grease_pencil_modifiers:
						if self.only_same_name:
							if mod.name == self.mod_name:
								obj.grease_pencil_modifiers.remove(greasepencil_modifier=mod)
						else:
							if mod.type == tgt_modtype:
								obj.grease_pencil_modifiers.remove(greasepencil_modifier=mod)

			else:
				if obj.type in {"MESH", "CURVE", "SURFACE", "META", "FONT","VOLUME"}:
					for mod in obj.modifiers:
						if self.only_same_name:
							if mod.name == self.mod_name:
								obj.modifiers.remove(modifier=mod)
						else:
							if mod.type == tgt_modtype:
								obj.modifiers.remove(modifier=mod)


		self.report({'INFO'}, "Remove Modifier [%s]" % tgt_modtype.capitalize())
		return {'FINISHED'}


# モディファイアの順番の変更
class AUTOMIRROR_OT_modifier_sort(Operator):
	bl_idname = "automirror.modifier_sort"
	bl_label = "Modifier Sort"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}


	is_down     : BoolProperty(name="Down")
	only_same_name     : BoolProperty(name="Only Modifier Name")
	mod_name : StringProperty(default="Mirror",name="Modifier Name")
	move_count : IntProperty(default=0,name="Move Count",min=0)

	global mesh_mod_items
	global gp_mod_items
	mesh_mod_type : EnumProperty(default="MIRROR",name="Modifier Type", description="",items = mesh_mod_items)
	gp_mod_type : EnumProperty(default="GP_MIRROR",name="Modifier Type", description="",items = gp_mod_items)


	@classmethod
	def poll(cls, context):
		return not len(bpy.context.selected_objects) == 0

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.active=(not self.only_same_name)
		if bpy.context.view_layer.objects.active.type == "GPENCIL":
			row.prop(self, "gp_mod_type")
		else:
			row.prop(self, "mesh_mod_type")

		col.prop(self, "only_same_name")

		row = col.row(align=True)
		row.active=self.only_same_name
		row.prop(self, "mod_name")
		col.separator()
		row = col.row(align=True)
		row.label(text="",icon="SORT_ASC")
		row.prop(self, "is_down")
		row = col.row(align=True)
		row.label(text="",icon="BLANK1")
		row.prop(self, "move_count")

	def execute(self, context):
		old_act = bpy.context.view_layer.objects.active

		# アクティブがグリースペンシルならグリースペンシル用のプロパティを利用
		if old_act.type == "GPENCIL":
			global gp_mod_items
			tgt_mod_items =  gp_mod_items
			tgt_modtype = self.gp_mod_type
		else:
			global mesh_mod_items
			tgt_mod_items =  mesh_mod_items
			tgt_modtype = self.mesh_mod_type


		for obj in bpy.context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			if not len(obj.modifiers) > 1:
				continue
			for mod in obj.modifiers:
				if self.only_same_name:
					if mod.name == self.mod_name:
						self.mod_sort_fanc(context,obj,mod)

				else:
					if mod.type == self.mod_type:
						self.mod_sort_fanc(context,obj,mod)


		bpy.context.view_layer.objects.active = old_act

		return {'FINISHED'}


	def mod_sort_fanc(self, context, obj, mod):
			if self.move_count == 0:
				modindex = len(obj.modifiers) - self.move_count
			else:
				modindex = self.move_count

			for i in range(modindex):
				if self.is_down:
					bpy.ops.object.modifier_move_down(modifier=mod.name)
				else:
					bpy.ops.object.modifier_move_up(modifier=mod.name)



		# モディファイアの数だけ繰り返して一番最初に移動する
		# modindex = len(obj.modifiers)
		#
		# # if self.move_count < 0:
		# # 	modindex = len(obj.modifiers) - self.move_count
		# # else:
		# # 	modindex = len(obj.modifiers) - self.move_count
		# #
		# #
		# for i in range(modindex):
		# 	# 順番が同じなら終了
		# 	tgt_mod_index = obj.modifiers.find(mod.name)
		# 	if tgt_mod_index == len(obj.modifiers):
		# 		return
		# 	if self.move_count < 0:
		#
		#
		# 		bpy.ops.object.modifier_move_down(modifier=mod.name)
		# 	else:
		# 		if tgt_mod_index == 0:
		# 			return
		# 		bpy.ops.object.modifier_move_up(modifier=mod.name)
