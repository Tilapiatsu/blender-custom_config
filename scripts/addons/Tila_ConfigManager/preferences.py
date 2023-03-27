import bpy
import os
import textwrap
from . items import preferences_tabs
from bpy.props import IntProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty

def get_path():
	return os.path.dirname(os.path.realpath(__file__))

def get_name():
	return os.path.basename(get_path())


def _label_multiline(context, text, parent):
	chars = int(context.region.width / 7)   # 7 pix on 1 character
	wrapper = textwrap.TextWrapper(width=chars)
	text_lines = wrapper.wrap(text=text)
	for text_line in text_lines:
		parent.label(text=text_line)
		
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
			self.draw_addons(box)

		elif self.tabs == "ABOUT":
			self.draw_about(box)

		box = column.box()

		self.draw_progress(box)

	def draw_general(self, box):
		split = box.split()

		b = split.box()
		
		column = b.column(align=True)
		column.operator("tila.config_print_addon_list", text="Print Addon List")
		column.separator()
		column.operator("tila.config_clean_addon_list", text="Clean Addon List")
		column.operator("tila.config_sync_addon_list", text="Sync Addon List")
		column.operator("tila.config_link_addon_list", text="Link Addon List")
		column.operator("tila.config_enable_addon_list", text="Enable Addon List")
		column.operator("tila.config_register_keymaps", text="Register Keymaps")
		column.operator("tila.config_set_settings", text="Set Settings")
		

	def draw_addons(self, box):
		wm = bpy.context.window_manager
		kc = wm.keyconfigs.user

		split = box.split()

		b = split.box()
		# b.label(text="Tools")

	def draw_about(self, box):
		column = box.column(align=True)

		row = column.row(align=True)

		row.scale_y = 1.5
		# row.operator("wm.url_open", text='MACHIN3tools',
		# 			icon='INFO').url = 'https://machin3.io/MACHIN3tools/'

	def draw_progress(self, box):
		row = box.row(align=True)
		b1 = row.box()
		b1.label(text="Status")
		b2 = row.box()
		b2.label(text="Progress")
		
		# progress = get_progress()
		# b2.label(text=progress)
