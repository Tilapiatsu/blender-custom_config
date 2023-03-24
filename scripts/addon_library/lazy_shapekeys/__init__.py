'''
Lazy Shapekeys Addon (C) 2021-2022 Bookyakuno
Created by Bookyakuno
License : GNU General Public License version3 (http://www.gnu.org/licenses/)
'''

bl_info = {
	"name" : "Lazy Shapekeys",
	"author" : "Bookyakuno",
	"version" : (1, 0, 36),
	"blender" : (3, 2, 0),
	"location" : "3D View",
	"description" : "Shapekeys Utility. Transfer Shape(Forced) / Create Objects for All Shape Keys.",
	"warning" : "",
	"wiki_url" : "",
	"tracker_url" : "",
	"category" : "UI"
}


if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"op",
	"ui",
	"utils",
	"props",

	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])

from . import (
op,
ui,
utils,
props,
)
from .ui.ui_replace_sk_menu import LAZYSHAPEKEYS_PT_shape_keys
from .ui.ui_panel import LAZYSHAPEKEYS_PT_main
from .utils import *
from .props import *


import bpy
import rna_keymap_ui # キーマップリストに必要
from bpy.props import *
from bpy.types import AddonPreferences, UIList


lmda = lambda s,c:s.layout;None
keep_DATA_PT_shape_keys = bpy.types.DATA_PT_shape_keys.draw


def update_use_folder(self,context):
	addon_prefs = preference()

	if addon_prefs.use_folder:
		bpy.types.DATA_PT_shape_keys.draw = lmda
		bpy.types.DATA_PT_shape_keys.prepend(LAZYSHAPEKEYS_PT_shape_keys)
	else:
		bpy.types.DATA_PT_shape_keys.draw = keep_DATA_PT_shape_keys
		bpy.types.DATA_PT_shape_keys.remove(LAZYSHAPEKEYS_PT_shape_keys)


def update_panel(self, context):
	message = ": Updating Panel locations has failed"
	try:
		cate = context.preferences.addons[__name__.partition('.')[0]].preferences.category
		if cate:
			for panel in panels:
				if "bl_rna" in panel.__dict__:
					bpy.utils.unregister_class(panel)

			for panel in panels:
				panel.bl_category = cate
				bpy.utils.register_class(panel)

		else:
			for panel in panels:
				if "bl_rna" in panel.__dict__:
					bpy.utils.unregister_class(panel)

	except Exception as e:
		print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
	pass



class LAZYSHAPEKEYS_MT_AddonPreferences(AddonPreferences):
	bl_idname = __name__
	category : StringProperty(name="Tab Category", description="Choose a name for the category of the panel", default="Addons", update=update_panel)
	tab_addon_menu : EnumProperty(name="Tab", description="", items=[('OPTION', "Option", "","DOT",0),
	 ('LINK', "Link", "","URL",1)], default='OPTION')
	use_folder : BoolProperty(name="Use Folder in List Menu",description="Make the shape key block with '@' at the beginning of the name line into a folder.\nAdd a step to the shape key list menu to make it easier to classify",update=update_use_folder,default=True)
	sk_menu_use_slider : BoolProperty(name="Use Slider Display",default=True)


	# use_dialog : BoolProperty(default=True, name = "Use Dialog", description = "Menu remains visible unless clicked")
	# menu_width         : IntProperty(default=410, name = "Menu Width", description = "Width setting when menu layout is broken. \n Blender Settings-> Interface-> If 'Resolution Scale' is set to a value smaller than 1,\n  icons may be squished together so closely",min = 0)
	#
	# items = [
	# ("MOUSE","Mouse Position",""),
	# ("MOUSE_RELATIVE","Mouse Relative",""),
	# ("WINDOW_ABSOLUTE","Window Absolute","The X position is from the left edge of the active editor.\nY position is the position from the whole window"),
	# # ("PREV_LOCATION","Previous Position","The window position is memorized only when it is closed by pressing [OK] after it is displayed, and the pop-up dialog is displayed at the same position the next time it is opened"),
	# ]
	# window_position : EnumProperty(default="MOUSE",name="Window Position",items= items)
	# loc_x : IntProperty(name="X Location",default=300)
	# loc_y : IntProperty(name="Y Location",default=600)



	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.prop(self,"tab_addon_menu",expand=True)

		if self.tab_addon_menu == "OPTION":
			layout.prop(self,"category")
			layout.prop(self,"use_folder")

			if self.use_folder:
				box = layout.box()
				box.prop(self,"sk_menu_use_slider")

			# box = layout.box()
			# col = box.column()
			# col.label(text="Sync Key Popup Menu",icon="NONE")
			# col.use_property_split = True
			# col.use_property_decorate = False
			#
			# col.prop(self,"menu_width", expand=True)
			# row = col.row(align=True)
			# row.prop(self,"window_position", expand=True)
			# if not self.window_position == "MOUSE":
			# 	col.prop(self,"loc_x")
			# 	col.prop(self,"loc_y")



		# elif self.tab_addon_menu == "KEYMAP":
		# 	box = layout.box()
		#
		# 	col = box.column()
		# 	col.label(text="Keymap List:",icon="KEYINGSET")
		#
		# 	layout = self.layout
		# 	wm = bpy.context.window_manager
		# 	kc = wm.keyconfigs.user
		# 	old_km_name = ""
		# 	old_id_l = []
		# 	for km_add, kmi_add in addon_keymaps:
		# 	    km = kc.keymaps[km_add.name]
		# 	    for kmi_con in km.keymap_items:
		# 	        if kmi_add.idname == kmi_con.idname:
		# 	            if not kmi_con.id in old_id_l:
		# 	                kmi = kmi_con
		# 	                old_id_l.append(kmi_con.id)
		# 	                break
		# 	    if kmi:
		# 	        if not km.name == old_km_name:
		# 	            col.label(text=km.name,icon="DOT")
		# 	        col.context_pointer_set("keymap", km)
		# 	        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
		# 	        col.separator()
		# 	        old_km_name = km.name
		# 	        kmi = None


		elif self.tab_addon_menu == "LINK":
			row = layout.row()
			row.label(text="Link:")
			row.operator( "wm.url_open", text="gumroad", icon="URL").url = "https://gum.co/VLdwV"


def draw_drag_move_in_graph_editor(self,context):
	layout = self.layout
	sc = bpy.context.scene
	props = sc.lazy_shapekeys
	layout.separator()
	layout.prop(props,"drag_move_multply_value")


def draw_menu(self,context):
	layout = self.layout
	layout.separator()
	layout.operator("lazy_shapekeys.shape_keys_transfer_forced",icon="MOD_DATA_TRANSFER")
	layout.operator("lazy_shapekeys.shape_keys_create_obj_from_all",icon="DUPLICATE")
	if bpy.app.version >= (2,83,0):
		icon_val = "CHECKMARK"
	else:
		icon_val = "NONE"
	layout.operator("lazy_shapekeys.shape_keys_apply_modifier",icon=icon_val)
	layout.operator("lazy_shapekeys.shape_keys_sort",icon="SORTALPHA")
	layout.operator("lazy_shapekeys.shape_keys_separeate",icon="MOD_MIRROR")





panels = (
LAZYSHAPEKEYS_PT_main,
)

classes = (
LAZYSHAPEKEYS_PR_main,
LAZYSHAPEKEYS_sync_colle,
LAZYSHAPEKEYS_sk_folder,
LAZYSHAPEKEYS_sk_data,
LAZYSHAPEKEYS_obj_sk_data,
LAZYSHAPEKEYS_MT_AddonPreferences,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


	op.register()
	ui.register()
	update_panel(None, bpy.context)

	bpy.types.Scene.lazy_shapekeys = PointerProperty(type=LAZYSHAPEKEYS_PR_main)
	bpy.types.Key.lazy_shapekeys = PointerProperty(type=LAZYSHAPEKEYS_sk_data)
	bpy.types.Object.lazy_shapekeys = PointerProperty(type=LAZYSHAPEKEYS_obj_sk_data)
	bpy.types.Scene.lazy_shapekeys_colle = CollectionProperty(type=LAZYSHAPEKEYS_sync_colle)
	bpy.types.MESH_MT_shape_key_context_menu.append(draw_menu)
	# bpy.types.GRAPH_MT_key.append(draw_drag_move_in_graph_editor)
	bpy.types.ShapeKey.lazy_shapekeys = PointerProperty(type=LAZYSHAPEKEYS_sk_folder)
	update_use_folder(None,bpy.context)

	try:
		bpy.app.translations.register(__name__, GetTranslationDict())
	except Exception as e: print(e)




def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


	op.unregister()
	ui.unregister()

	bpy.types.DATA_PT_shape_keys.draw = keep_DATA_PT_shape_keys
	bpy.types.DATA_PT_shape_keys.remove(LAZYSHAPEKEYS_PT_shape_keys)
	# bpy.types.GRAPH_MT_key.remove(draw_drag_move_in_graph_editor)
	bpy.types.MESH_MT_shape_key_context_menu.remove(draw_menu)


	try:
		bpy.app.translations.unregister(__name__)
	except Exception as e: print(e)


	del bpy.types.Scene.lazy_shapekeys
	del bpy.types.Key.lazy_shapekeys
	del bpy.types.Object.lazy_shapekeys
	del bpy.types.Scene.lazy_shapekeys_colle


if __name__ == "__main__":
	register()
