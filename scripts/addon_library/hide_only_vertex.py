'''
Created by Saidenka, Bookyakuno(Blender2.8x- Updated)
License : GNU General Public License version3 (http://www.gnu.org/licenses/)
'''

bl_info = {
	"name": "Hide Only Vertex",
	"author": "Saidenka, Bookyakuno(Blender2.8x- Updated)",
	"version": (1, 0, 2),
	"blender": (2, 91, 0),
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
	layout.operator("hide_vertex_only.hide_vertex_only",icon="PLUGIN")




class HIDEVONLY_OT_HideVertexOnly(Operator):
	bl_idname = "hide_vertex_only.hide_vertex_only"
	bl_label = "Hide Only Vertex"
	bl_description = "Hide and Fix Selected vertices\nTo restore the display, perform the normal 'Reveal Hidden'"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		obj = context.active_object

		if obj.type == "MESH":
			bpy.ops.object.mode_set(mode="OBJECT")
			me = obj.data
			for vert in me.vertices:
				if vert.select:
					vert.hide = True
			bpy.ops.object.mode_set(mode="EDIT")

		elif obj.type == "CURVE":
			bpy.ops.object.mode_set(mode="OBJECT")
			me = obj.data
			for sp in me.splines:
				if sp.type == "BEZIER":
					for pt in sp.bezier_points:
						if pt.select_control_point:
							pt.hide = True
				else:
					for pt in sp.points:
						if pt.select:
							pt.hide = True

			bpy.ops.object.mode_set(mode="EDIT")

		elif obj.type == "SURFACE":
			bpy.ops.object.mode_set(mode="OBJECT")
			me = obj.data
			for sp in me.splines:
				for pt in sp.points:
					if pt.select:
						pt.hide = True
			bpy.ops.object.mode_set(mode="EDIT")
		# elif obj.type == "ARMATURE":
			# bpy.ops.object.mode_set(mode="OBJECT")
			# me = obj.data
			# for bn in me.bones:
			# 	if bn.select:
			# 		bn.hide = True
					# bn.hide_select = False
					# bn.select = False
			# bpy.ops.object.mode_set(mode="EDIT")

		# elif obj.type == "GPENCIL":
		# 	bpy.ops.object.mode_set(mode="OBJECT")
		# 	me = obj.data
		# 	obj.data.layers[0].frames[0].strokes[0].select
		# 	for sp in me.layers:
		# 		# for pt in sp.frames:
		# 		# 	for pt in sp.strokes:
		# 		# 		if pt.select:
		# 					pt.hide = True
		# 	bpy.ops.object.mode_set(mode="EDIT_GPENCIL")

		else:
			self.report(
				type={"ERROR"}, message="Running on Mesh or Curve object is active")
		return {'FINISHED'}



HIDEVONLY_translation_dict = {
	"en_US": {},
	"ja_JP": {
		("*", "Running on Mesh or Curve object is active"): "メッシュもしくはアクティブオブジェクトでの実行がアクティブです",
		("*", "Hide Only Vertex"): "頂点のみを隠す",
		("*", "Hide and Fix Selected vertices\nTo restore the display, perform the normal 'Reveal Hidden'"): "選択している頂点のみを隠して、編集されないように固定します\n表示を元に戻すには、通常の「隠したものを表示」を実行します",

	}
}


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
	try:
		bpy.app.translations.register(__name__, HIDEVONLY_translation_dict)  # 辞書
	except: pass

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon

	if kc:
		km = wm.keyconfigs.addon.keymaps.new(name='Mesh')
		kmi = km.keymap_items.new("hide_vertex_only.hide_vertex_only", 'H', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))
		kmi.active = True
		km = wm.keyconfigs.addon.keymaps.new(name='Curve')
		kmi = km.keymap_items.new("hide_vertex_only.hide_vertex_only", 'H', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))
		kmi.active = True

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
