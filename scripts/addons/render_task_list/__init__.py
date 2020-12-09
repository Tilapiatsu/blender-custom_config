'''
Render Task List Addon (C) 2020 Bookyakuno
Created by Bookyakuno
License : GNU General Public License version3 (http://www.gnu.org/licenses/)
'''

bl_info = {
	"name": "Render Task List",
	"author": "Bookyakuno",
	"description": "Manage rendering settings, batch rendering",
	"version": (1, 0, 0),
	"blender": (2, 91, 0),
	"location": "View3D > Side Menu(N key) > Addons > Render Task List",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "3D View"}

import bpy
from bpy.props import *
from bpy.types import AddonPreferences


if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"prop",
	"rentask",
	"utils",
	"ui",
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .utils import GetTranslationDict
from .ui.ui_panel import RENTASKLIST_PT_cam_panel

from . import (
prop,
rentask,
ui,
)


def update_panel(self, context):
	message = ": Updating Panel locations has failed"
	try:
		for panel in panels:
			if "bl_rna" in panel.__dict__:
				bpy.utils.unregister_class(panel)

		for panel in panels:
			panel.bl_category = context.preferences.addons[__name__.partition('.')[0]].preferences.category
			bpy.utils.register_class(panel)

	except Exception as e:
		print("\n[{}]\n{}\n\nError:\n{}".format(__name__.partition('.')[0], message, e))
		pass


class RENTASKLIST_MT_AddonPreferences(AddonPreferences):
	bl_idname = __name__.partition('.')[0]

	category : StringProperty( name="Tab Category", description="Choose a name for the category of the panel", default="Addons", update=update_panel)


	def draw(self, context):
		layout = self.layout

		row = layout.row()
		row.label(text="Tab Category:")
		row.prop(self, "category", text="")



panels = (
		RENTASKLIST_PT_cam_panel,
		)


classes = (
RENTASKLIST_MT_AddonPreferences,
)


def register():
	prop.register()
	rentask.register()
	ui.register()

	for cls in classes:
		bpy.utils.register_class(cls)


	update_panel(None, bpy.context)


	try:
		translation_dict = GetTranslationDict()
		bpy.app.translations.register(__name__, translation_dict)
	except: pass


def unregister():
	prop.unregister()
	rentask.unregister()
	ui.unregister()

	for cls in classes:
		bpy.utils.unregister_class(cls)

	try:
		bpy.app.translations.unregister(__name__)
	except: pass

if __name__ == "__main__":
	register()
