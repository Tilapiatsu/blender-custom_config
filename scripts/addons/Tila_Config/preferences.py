import bpy
import os
from . items import preferences_tabs
from bpy.props import IntProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty

def get_path():
	return os.path.dirname(os.path.realpath(__file__))

def get_name():
	return os.path.basename(get_path())

class TILA_Config_Preferences(bpy.types.AddonPreferences):
	bl_idname = get_name()

	tabs: EnumProperty(name="Tabs", items=preferences_tabs, default="GENERAL")

	def draw(self, context):
		layout = self.layout
		column = layout.column(align=True)
		row = column.row()
		row.prop(self, "tabs", expand=True)

		box = column.box()

		if self.tabs == "GENERAL":
			self.draw_general(box)

		elif self.tabs == "ADDONS":
			self.draw_keymaps(box)

		elif self.tabs == "ABOUT":
			self.draw_about(box)

		box = column.box()

		self.draw_progress(box)

	def draw_general(self, box):
		split = box.split()

		b = split.box()
		b.label(text="General")

		column = b.column(align=True)
		column.operator("tila.config_print_addon_list", text="Print Addon List")
		column.operator("tila.config_sync_addon_list", text="Sync Addon List")

	def draw_keymaps(self, box):
		wm = bpy.context.window_manager
		kc = wm.keyconfigs.user

		split = box.split()

		b = split.box()
		b.label(text="Tools")

	def draw_about(self, box):
		column = box.column(align=True)

		row = column.row(align=True)

		row.scale_y = 1.5
		row.operator("wm.url_open", text='MACHIN3tools',
					icon='INFO').url = 'https://machin3.io/MACHIN3tools/'

	def draw_progress(self, box):
		column = box.column(align=True)
		column.label(text="Progress Box Here")
		column.label(text="Progress Box Here")

