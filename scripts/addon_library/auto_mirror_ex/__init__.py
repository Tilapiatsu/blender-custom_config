# b2.80~ update by Bookyakuno
####################################################################
# Quickly set up mirror modifiers and assist mirror modifiers
# Detailed authorship:
#  Bookyakuno(Current support b2.80~)
#  Lapineige(AutoMirror ~b2.79),
#  Robert Fornof & MX(MirrorMirror ~b2.79),
####################################################################


# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
	"name": "Auto Mirror EX",
	"description": "Super fast cutting and mirroring for mesh",
	"author": "Lapineige, Robert Fornof & MX, Bookyakuno(Blender2.8 Update)",
	"version": (2, 9, 5),
	"blender": (3, 00, 0),
	"location": "View 3D > Sidebar > Tools tab > AutoMirror (panel)",
	"warning": "",
	"wiki_url": "https://bookyakuno.com/auto-mirror/",
	"category": "Mesh"}


import bpy
import rna_keymap_ui # Required for displaying keymap list Menu
from bpy.props import *
from bpy.types import AddonPreferences


if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"keymap",
	"props",
	"keymap",
	"utils",
	"ui",
	"op",
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])

from .keymap import *
from .props import *
from .props import AUTOMIRROR_Props
from .ui.ui_panel import AUTOMIRROR_PT_panel
from .utils import GetTranslationDict
from .utils import *
from . import (
	op,
	ui,
)


# Changing the category in which the panel menu is displayed
# Executed when Blender starts or when a checkbox is changed
def update_panel(self, context):
	message = ": Updating Panel locations has failed"
	try:
		for panel in panels:
			if "bl_rna" in panel.__dict__:
				bpy.utils.unregister_class(panel)

		for panel in panels:
			panel.bl_category = context.preferences.addons[__name__].preferences.category
			bpy.utils.register_class(panel)

	except Exception as e:
		print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
		pass



# Add / Remove keymap
# Executed when Blender starts or when a checkbox is changed
def update_keymap(self, context):
	try:
		addon_prefs = preference()
		if addon_prefs.keymap_automirror:
			add_keymap_automirror()
		else:
			remove_keymap_automirror()
	except:
		pass


class AUTOMIRROR_MT_AddonPreferences(AddonPreferences):
	bl_idname = __name__

	category          : StringProperty(name="Tab Category", description="Choose a name for the category of the panel", default="Edit", update=update_panel)
	keymap_automirror : BoolProperty(name = "Add Keymap (X/Y/Z/F + Shift + alt)", update = update_keymap)
	tab_addon_menu : EnumProperty(name="Tab", description="", items=[('Option', "Option", "","DOT",0),('Keymap', "Keymap", "","KEYINGSET",1), ('Link', "Link", "","URL",2)], default='Option')

	def draw(self, context):
		layout = self.layout

		row = layout.row(align=True)
		row.prop(self, "tab_addon_menu",expand=True)
		if self.tab_addon_menu=="Option":
			box = layout.box()

			row = box.row()
			col = row.column()
			col.label(text="Tab Category:")
			col.prop(self, "category", text="")

		# Keymap
		# Search the keymap that matches the operator name and the property status of the keymap registered with the add-on from the Blender keymap setting and display it in the menu
		if self.tab_addon_menu=="Keymap":
			box = layout.box()
			box.prop(self, "keymap_automirror")
			if self.keymap_automirror:
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


		if self.tab_addon_menu=="Link":
			box = layout.box()
			col = box.column(align=True)
			col.label(text="Store Site")
			row = col.row()
			row.operator("wm.url_open", text="gumroad", icon="URL").url = "https://bookyakuno.com/auto-mirror/"
			col.separator()
			col.label(text="Description")
			row = col.row()
			row.operator("wm.url_open", text="Blender Artists", icon="URL").url = "https://blenderartists.org/t/auto-mirror-blender2-8-ver/1151539"
			row.operator("wm.url_open", text="Japanese - bookyakuno.com", icon="URL").url = "https://bookyakuno.com/auto-mirror/"
			col.separator()
			col.label(text="Old version")
			row = col.row()
			row.operator("wm.url_open", text="Old version 2.7x - github", icon="URL").url = "https://github.com/lapineige/Blender_add-ons/blob/master/AutoMirror/AutoMirror_V2-4.py"
			# row.operator("wm.url_open", text="MirrorMirror - github", icon="URL").url = "https://github.com/fornof/BlenderAddons/blob/master/MirrorMirrorTool.py"



# Add-ons Preferences Update Panel. Define Panel classes for updating
panels = (
		AUTOMIRROR_PT_panel,
		)


# define classes for registration
classes = (
	AUTOMIRROR_MT_AddonPreferences,
	AUTOMIRROR_Props,
	)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	op.register()
	ui.register()
	update_panel(None, bpy.context)
	update_keymap(None, bpy.context)

	bpy.types.Scene.automirror = PointerProperty(type=AUTOMIRROR_Props)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	op.unregister()
	ui.unregister()
	del bpy.types.Scene.automirror


if __name__ == "__main__":
	register()
