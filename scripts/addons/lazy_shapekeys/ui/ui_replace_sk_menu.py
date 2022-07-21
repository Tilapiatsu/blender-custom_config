import bpy,re
from bpy.props import *
from bpy.types import Panel, UIList
from ..utils import *
import ast

# シェイプキーリスト
class LAZYSHAPEKEYS_UL_replace_menu(UIList):
	filter_by_name: StringProperty(default='')
	sort_invert: BoolProperty(default=False)
	order_by_random_prop: BoolProperty(default=False)

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		draw_replace_shapekeys_list(self, context, layout, data, item, icon, active_data, active_propname, index, True, False)


	def filter_items(self, context, data, propname):
		filtered, ordered = filter_items_replace_menu(self, context, data, propname)
		return filtered,ordered


# シェイプキーリスト
class LAZYSHAPEKEYS_UL_replace_menu_misc_menu(UIList):
	filter_by_name: StringProperty(default='')
	sort_invert: BoolProperty(default=False)
	order_by_random_prop: BoolProperty(default=False)

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		draw_replace_shapekeys_list(self, context, layout, data, item, icon, active_data, active_propname, index, True, True)


	def filter_items(self, context, data, propname):
		filtered, ordered = filter_items_replace_menu(self, context, data, propname)
		return filtered,ordered


def filter_items_replace_menu(self, context, data, propname):
	filtered = []
	ordered = []
	items = getattr(data, propname)
	helper_funcs = bpy.types.UI_UL_list

	# Initialize with all items visible
	filtered = [self.bitflag_filter_item] * len(items)

	# 文字列でのフィルター
	if self.filter_name:
		filtered = helper_funcs.filter_items_by_name(
		self.filter_name,
		self.bitflag_filter_item,
		items,
		"name",
		reverse=self.use_filter_sort_reverse)


	# [名前順にソート]オプションとフォルダー機能は共存できないので、有効化すると折りたたみや並び順は無視されます
	if self.use_filter_sort_alpha:
		ordered = helper_funcs.sort_items_by_name(items, "name")

	else:
		# 除去
		sk_bl = data.key_blocks

		hide_sk_l = []
		all_count = len(items) -1
		# 非表示にするアイテムをまとめる
		for i, item in enumerate(items):
			if is_folder(item): # フォルダーアイテム
				dic = convert_mini_text_to_dic(item.vertex_group)

				if dic["exp"] == 0: # 開いていない
					hide_sk_l += get_folder_innner_sk_list(i, data) # フォルダー内のアイテム

		if hide_sk_l:
			for i,sk in enumerate(sk_bl):
				if sk.name in hide_sk_l:
					filtered[i] &= ~self.bitflag_filter_item


	return filtered,ordered


# リストのメニュー
def draw_replace_shapekeys_list(self, context, layout, data, item, icon, active_data, active_propname, index, is_defpanel, is_popup):
	addon_prefs = preference()
	obj = active_data
	key_block = item
	# print(8888,obj)


	use_open_window = False
	if data.animation_data:
		if data.animation_data.action:
			if data.animation_data.action.fcurves:
				for fc in data.animation_data.action.fcurves:
					if fc.data_path == 'key_blocks["%s"].value' % item.name:
						use_open_window = True
			else:
				use_open_window = "no_fc"
		else:
			use_open_window = "no_fc"
	else:
		use_open_window = "no_fc"


	if is_folder(item):
		dic = convert_mini_text_to_dic(item.vertex_group)
		if dic["exp"] == 1:
			exp_icon = "TRIA_DOWN"
		else:
			exp_icon = "TRIA_RIGHT"

		sp = layout.split(align=True,factor=0.7)
		row = sp.row(align=True)
		op = row.operator("lazy_shapekeys.toggle_expand",text="",icon=exp_icon,emboss=False)
		op.index = index
		op.obj_name =  obj.name
		row.prop(key_block, "name", text="", emboss=False, icon="FILE_FOLDER")


		row = sp.row(align=True)
		row.alignment="RIGHT"


		op = row.operator("lazy_shapekeys.folder_move_sk",text="",icon="IMPORT",emboss=False)
		op.index = -1
		op.folder_name = item.name
		op.obj_name =  obj.name


		op = row.operator("lazy_shapekeys.shapekeys_batch_keyframe_insert",text="",icon="DECORATE_KEYFRAME",emboss=False)
		op.obj_name = obj.name
		op.is_def_listmenu = True
		op.index = index
		# if not use_open_window == "no_fc":
		row.label(text="",icon="BLANK1")


		if dic["mute"] == 1:
			icon_val = "CHECKBOX_DEHLT"
		else:
			icon_val = "CHECKBOX_HLT"
		op = row.operator("lazy_shapekeys.shapekeys_batch_mute",text="",icon=icon_val,emboss=False)
		op.sks_name = data.name
		op.index = index

		return



	if self.layout_type in {'DEFAULT', 'COMPACT'}:
		split = layout.split(factor=0.4, align=False)
		row = split.row(align=True)

		use_folder_l = [sk for i,sk in enumerate(obj.data.shape_keys.key_blocks) if is_folder(sk)]
		if use_folder_l and is_defpanel:
			row.label(text="",icon="BLANK1")

		row.prop(key_block, "name", text="",icon="SHAPEKEY_DATA", emboss=False)



		row = split.row(align=True)
		if addon_prefs.sk_menu_use_slider:
			row.emboss = "NORMAL"
		else:
			row.emboss = 'NONE_OR_STATUS'


		if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
			row.active = False

		if not item.id_data.use_relative:
			row.prop(key_block, "frame", text="")

		elif index > 0:
			if is_popup:
				rows = row.row(align=True)
				rows.prop(key_block, "value", text="",slider=addon_prefs.sk_menu_use_slider)

				use_cur_key_l, is_remove = check_use_keyframe(data, [item.name])

				if is_remove:
					icon_val = "KEYFRAME_HLT"
				else:
					icon_val = "KEYFRAME"

				op = rows.operator("lazy_shapekeys.shapekeys_one_keyframe_insert",text="",icon=icon_val,emboss=False)
				op.sk_name = item.name
				op.obj_name = obj.name
				op.is_def_listmenu = is_defpanel
				op.index = index

			else:
				rows = row.row(align=True)
				rows.use_property_split = True
				rows.use_property_decorate = True
				rows.prop(key_block, "value", text="",slider=addon_prefs.sk_menu_use_slider)


		else:
			row.label(text="")


		if use_open_window == "no_fc":
			row.label(text="",icon="BLANK1")
		elif use_open_window:
			op = row.operator("lazy_shapekeys.shapekeys_open_window",text="",icon="WINDOW",emboss=False)
			op.sk_name = item.name

		else:
			row.label(text="",icon="BLANK1")


		row.prop(key_block, "mute", text="", emboss=False)



	elif self.layout_type == 'GRID':
		layout.alignment = 'CENTER'
		layout.label(text="", icon_value=icon)


def LAZYSHAPEKEYS_PT_shape_keys(self, context):
	layout = self.layout
	LAZYSHAPEKEYS_PT_shape_keys_innner(self, context, False, layout, None, True)


# シェイプキーメニューのメイン
def LAZYSHAPEKEYS_PT_shape_keys_innner(self, context, is_misc_menu, layout, tgt_obj, is_propeditor):
	sc = bpy.context.scene
	props = sc.lazy_shapekeys
	if not tgt_obj:
		tgt_obj = bpy.context.object
	ob = tgt_obj

	key = ob.data.shape_keys
	kb = ob.active_shape_key

	enable_edit = ob.mode != 'EDIT'
	enable_edit_value = False
	enable_pin = False

	if enable_edit or (ob.use_shape_key_edit_mode and ob.type == 'MESH'):
		enable_pin = True
		if ob.show_only_shape_key is False:
			enable_edit_value = True

	row = layout.row(align=True)
	row.prop(props,"list_mode",expand=True)
	if props.list_mode == "FOLDER":
		draw_folder(self, context, layout, tgt_obj, is_misc_menu)
	elif props.list_mode == "SYNC":
		draw_sync(self, context ,layout)

	else:
		rows = 3
		if kb:
			rows = 5
		row = layout.row()
		if is_misc_menu:
			row.template_list("LAZYSHAPEKEYS_UL_replace_menu_misc_menu", "", key, "key_blocks", ob, "active_shape_key_index", rows=rows)
		else:
			row.template_list("LAZYSHAPEKEYS_UL_replace_menu", "", key, "key_blocks", ob, "active_shape_key_index", rows=rows)

		col = row.column(align=True)

		draw_sidebar(self, context, col, tgt_obj,False)



	if kb and not is_misc_menu:

		split = layout.split(factor=0.4)
		row = split.row()
		row.enabled = enable_edit
		row.prop(key, "use_relative")

		row = split.row()
		row.alignment = 'RIGHT'

		sub = row.row(align=True)
		sub.label()  # XXX, for alignment only
		subsub = sub.row(align=True)
		subsub.active = enable_pin
		subsub.prop(ob, "show_only_shape_key", text="")
		sub.prop(ob, "use_shape_key_edit_mode", text="")

		sub = row.row()
		if key.use_relative:
			sub.operator("object.shape_key_clear", icon='X', text="")
		else:
			sub.operator("object.shape_key_retime", icon='RECOVER_LAST', text="")


		if not is_folder(kb):
			if key.use_relative:
				if ob.active_shape_key_index != 0:
					row = layout.row()
					row.active = enable_edit_value
					row.prop(kb, "value")

					col = layout.column()
					sub.active = enable_edit_value
					sub = col.column(align=True)
					sub.prop(kb, "slider_min", text="Range Min")
					sub.prop(kb, "slider_max", text="Max")

					col.prop_search(kb, "vertex_group", ob, "vertex_groups", text="Vertex Group")
					col.prop_search(kb, "relative_key", key, "key_blocks", text="Relative To")

			else:
				layout.prop(kb, "interpolation")
				row = layout.column()
				row.active = enable_edit_value
				row.prop(key, "eval_time")


	if not is_propeditor:
		if bpy.context.mode == "EDIT_MESH":
			if ob.data.shape_keys:
				layout.separator()
				layout.operator("mesh.blend_from_shape",icon="AUTOMERGE_ON")
				layout.operator("mesh.shape_propagate_to_all",icon="INDIRECT_ONLY_ON")
			# layout.operator("lazy_shapekeys.shape_keys_separeate",icon="MOD_MIRROR")



# フォルダー
def draw_folder(self,context,layout, tgt_obj, is_misc_menu):
	ob = tgt_obj
	key = ob.data.shape_keys
	kb = ob.active_shape_key

	is_use_folder = False
	folder_l = []
	if key:
		folder_l = [ky for ky in key.key_blocks if is_folder(ky)]
	if folder_l:
		is_use_folder = True


	sp = layout.split(align=True,factor=0.4)
	row = sp.row(align=True)
	op = row.operator("lazy_shapekeys.item_add", icon='NEWFOLDER', text="")
	op.obj_name = ob.name
	rows = row.row(align=True)
	rows.active = is_use_folder
	op = rows.operator("lazy_shapekeys.sk_item_remove", icon='REMOVE', text="")
	op.obj_name = ob.name
	op.is_folder_remove = True
	rows.separator()
	op = rows.operator("lazy_shapekeys.item_move_item", icon='TRIA_UP', text="")
	op.direction = 'UP'
	op.is_def_list = False
	op.obj_name = tgt_obj.name
	op = rows.operator("lazy_shapekeys.item_move_item", icon='TRIA_DOWN', text="")
	op.direction = 'DOWN'
	op.is_def_list = False
	op.obj_name = tgt_obj.name
	row.separator()
	row = sp.row()
	row.active = is_use_folder

	# if bpy.context.mode == "POSE":
	# 	rows.separator()
	# 	op = rows.operator("lazy_shapekeys.bone_create_skname", icon='BONE_DATA', text="")
	# 	op.obj_name = tgt_obj.name

	op = row.operator("lazy_shapekeys.shapekeys_batch_keyframe_insert",icon="DECORATE_KEYFRAME")
	op.obj_name = tgt_obj.name
	op.is_def_listmenu = False

	op = row.operator("lazy_shapekeys.shapekeys_batch_value_reset",text="",icon="X")
	op.obj_name = tgt_obj.name
	row.label(text="",icon="BLANK1")





	sp = layout.split(align=True,factor=0.3)
	row = sp.row()
	if key:
		row.template_list("LAZYSHAPEKEYS_UL_folder_colle", "", key, "key_blocks", tgt_obj.lazy_shapekeys, "folder_colle_index",rows=15)
	else:
		row.label(text="",icon="NONE")



	row = sp.row()
	if is_misc_menu:
		row.template_list("LAZYSHAPEKEYS_UL_folder_inner_sk_misc_menu", "", key, "key_blocks", ob, "active_shape_key_index",rows=15)
	else:
		row.template_list("LAZYSHAPEKEYS_UL_folder_inner_sk", "", key, "key_blocks", ob, "active_shape_key_index",rows=15)
	col = row.column(align=True)
	draw_sidebar(self, context, col, tgt_obj, True)


# シェイプキーリストのサイドバー
def draw_sidebar(self, context, layout, tgt_obj, is_in_folder):
	col = layout
	ob = tgt_obj
	key = ob.data.shape_keys
	kb = ob.active_shape_key

	op = col.operator("lazy_shapekeys.sk_item_add", icon='ADD', text="")
	op.obj_name = ob.name
	op.is_in_folder = is_in_folder
	# col.operator("object.shape_key_remove", icon='REMOVE', text="").all = False
	op = col.operator("lazy_shapekeys.sk_item_remove", icon='REMOVE', text="")
	op.obj_name = ob.name
	op.is_folder_remove = False


	col.separator()

	col.menu("MESH_MT_shape_key_context_menu", icon='DOWNARROW_HLT', text="")

	if kb:
		col.separator()

		sub = col.column(align=True)
		op = sub.operator("lazy_shapekeys.item_move_item", icon='TRIA_UP', text="")
		op.direction = 'UP'
		op.is_def_list = True
		op.obj_name = tgt_obj.name
		op = sub.operator("lazy_shapekeys.item_move_item", icon='TRIA_DOWN', text="")
		op.direction = 'DOWN'
		op.is_def_list = True
		op.obj_name = tgt_obj.name

	col.separator()
	op = col.operator("lazy_shapekeys.item_add", icon='NEWFOLDER', text="")
	op.obj_name = ob.name



# 同期
def draw_sync(self, context ,layout):
	props = bpy.context.scene.lazy_shapekeys
	colle = bpy.context.scene.lazy_shapekeys_colle

	layout.operator("lazy_shapekeys.shape_keys_sync_update",icon="NONE")
	layout.prop(props,"tgt_colle")
	layout.separator()
	layout.template_list("LAZYSHAPEKEYS_UL_sync_list", "", bpy.context.scene, "lazy_shapekeys_colle", props, "sync_colle_index", rows=5)
