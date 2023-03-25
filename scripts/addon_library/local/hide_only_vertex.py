'''
Created by Saidenka, Bookyakuno(Blender2.8x- Updated)
License : GNU General Public License version3 (http://www.gnu.org/licenses/)
'''

bl_info = {
	"name": "Hide Only Vertex",
	"author": "Saidenka, Bookyakuno(Blender2.8x- Updated)",
	"version": (1, 0, 4),
	"blender": (3, 00, 0),
	"location": "Mesh or Curve Edit Mode → Show/Hide → 'Hide Only Vertex'(Ctrl + Shift + H)",
	"description": "Hide and Fix Selected vertices",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"
}

import bpy
from bpy.props import *
from bpy.types import Operator, AddonPreferences, Panel, PropertyGroup
import rna_keymap_ui
import os, csv, codecs #辞書



class HIDEVONLY_MT_AddonPreferences(AddonPreferences):
	bl_idname = __name__

	tab_addon_menu: EnumProperty(
		name="Tab",
		description="",
		items=[
			   ('Keymap', "Keymap", "", "KEYINGSET", 0),
			   ('Link', "Link", "", "URL", 1)],
		default='Keymap')

	def draw(self, context):
		layout = self.layout

		row = layout.row(align=True)
		row.prop(self, "tab_addon_menu", expand=True)

		if self.tab_addon_menu == "Keymap":
			box = layout.box()
			col = box.column()
			col.label(text="Keymap List:",icon="KEYINGSET")


			wm = bpy.context.window_manager
			kc = wm.keyconfigs.user
			old_km_name = ""
			get_kmi_l = []
			for km_add, kmi_add in addon_keymaps:
				for km_con in kc.keymaps:
					if km_add.name == km_con.name:
						km = km_con
						break

				for kmi_con in km.keymap_items:
					if kmi_add.idname == kmi_con.idname:
						if kmi_add.name == kmi_con.name:
							get_kmi_l.append((km,kmi_con))

			get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

			for km, kmi in get_kmi_l:
				if not km.name == old_km_name:
					col.label(text=str(km.name),icon="DOT")
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
				col.separator()
				old_km_name = km.name


		if self.tab_addon_menu == "Link":
			layout.operator( "wm.url_open", text="gumroad", icon="URL").url = "https://gum.co/unuzT"
			layout.operator( "wm.url_open", text="Github(Blender2.79ver)", icon="URL").url = "https://github.com/bookyakuno/Blender-Scramble-Addon"


def hide_vertex_only_menu(self, context):
	layout = self.layout
	layout.separator()
	layout.separator()
	layout.separator()
	layout.operator("hide_vertex_only.hide_vertex_only",icon="PLUGIN").unselected = False
	layout.operator("hide_vertex_only.hide_vertex_only",text="Hide Only Vertex(Unselected)",icon="PLUGIN").unselected = True


class HIDEVONLY_OT_HideVertexOnly(Operator):
	bl_idname = "hide_vertex_only.hide_vertex_only"
	bl_label = "Hide Only Vertex"
	bl_description = "Hide and Fix Selected vertices\nTo restore the display, perform the normal 'Reveal Hidden'"
	bl_options = {'REGISTER', 'UNDO'}

	unselected : BoolProperty(name="Unselected")

	@classmethod
	def poll(cls, context):
		return bpy.context.object

	def execute(self, context):
		act_obj = bpy.context.object
		old_mode = act_obj.mode

		bpy.ops.object.mode_set(mode="OBJECT")

		sel_l = bpy.context.selected_objects
		if not act_obj in sel_l:
			sel_l += act_obj

		for obj in sel_l:
			me = obj.data
			if not obj.type == act_obj.type: # 同じオブジェクトタイプのみ
				continue

			# メッシュ
			if obj.type == "MESH":
				for vert in me.vertices:
					if self.unselected:
						if not vert.select:
							vert.hide = True
					else:
						if vert.select:
							vert.hide = True

			# カーブ
			elif obj.type == "CURVE":
				for sp in me.splines:
					if sp.type == "BEZIER":
						for pt in sp.bezier_points:
							if self.unselected:
								if not pt.select_control_point:
									pt.hide = True
							else:
								if pt.select_control_point:
									pt.hide = True
					else:
						for pt in sp.points:
							if self.unselected:
								if not pt.select:
									pt.hide = True
							else:
								if pt.select:
									pt.hide = True

			# サーフェス
			elif obj.type == "SURFACE":
				for sp in me.splines:
					for pt in sp.points:
						if pt.select:
							pt.hide = True


		bpy.ops.object.mode_set(mode=old_mode)
		return {'FINISHED'}



# HIDEVONLY_translation_dict = {
# 	"en_US": {},
# 	"ja_JP": {
# 		("*", "Hide Only Vertex"): "頂点のみを隠す",
# 		("*", "Hide Only Vertex(Unselected)"): "頂点のみを隠す(非選択物)",
# 		("*", "Hide and Fix Selected vertices\nTo restore the display, perform the normal 'Reveal Hidden'"): "選択している頂点のみを隠して、編集されないように固定します\n表示を元に戻すには、通常の「隠したものを表示」を実行します",
#
# 	}
# }



# 翻訳辞書の取得
def GetTranslationDict():
	dict = {}
	reader = [
	["頂点のみを隠す","Hide Only Vertex"],
	["頂点のみを隠す(非選択物)","Hide Only Vertex(Unselected)"],
	["選択している頂点のみを隠して、編集されないように固定します\n表示を元に戻すには、通常の「隠したものを表示」を実行します","Hide and Fix Selected vertices\nTo restore the display, perform the normal 'Reveal Hidden'"],
	]
	dict['ja_JP'] = {}
	for row in reader:
		for context in bpy.app.translations.contexts:
			dict['ja_JP'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')

	return dict


classes = (
	HIDEVONLY_MT_AddonPreferences,
	HIDEVONLY_OT_HideVertexOnly,
)

addon_keymaps = []


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.VIEW3D_MT_edit_mesh_showhide.append(hide_vertex_only_menu)
	bpy.types.VIEW3D_MT_edit_curve_showhide.append(hide_vertex_only_menu)
	# translation
	try:
		bpy.app.translations.register(__name__, GetTranslationDict())
	except Exception as e: print(e)

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon

	if kc:
		# メッシュ
		km = wm.keyconfigs.addon.keymaps.new(name='Mesh')
		kmi = km.keymap_items.new("hide_vertex_only.hide_vertex_only", 'H', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))
		kmi.active = True
		kmi.properties.unselected = False
		kmi = km.keymap_items.new("hide_vertex_only.hide_vertex_only", 'H', 'PRESS', ctrl=True, shift=True,alt=True)
		addon_keymaps.append((km, kmi))
		kmi.active = True
		kmi.properties.unselected = True

		# カーブ
		km = wm.keyconfigs.addon.keymaps.new(name='Curve')
		kmi = km.keymap_items.new("hide_vertex_only.hide_vertex_only", 'H', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))
		kmi.active = True
		kmi.properties.unselected = False
		kmi = km.keymap_items.new("hide_vertex_only.hide_vertex_only", 'H', 'PRESS', ctrl=True, shift=True,alt=True)
		addon_keymaps.append((km, kmi))
		kmi.active = True
		kmi.properties.unselected = True


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	bpy.types.VIEW3D_MT_edit_mesh_showhide.remove(hide_vertex_only_menu)
	bpy.types.VIEW3D_MT_edit_curve_showhide.remove(hide_vertex_only_menu)
	try:
		bpy.app.translations.unregister(__name__)
	except: pass

	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()


if __name__ == "__main__":
	register()
