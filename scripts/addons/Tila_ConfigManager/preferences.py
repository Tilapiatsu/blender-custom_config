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
		wm = bpy.context.window_manager
		row = column.row()
		row.prop(self, "tabs", expand=True)

		box = column.box()

		if self.tabs == "GENERAL":
			self.draw_general(box)

		elif self.tabs == "ADDONS":
			self.draw_addons(box, wm)

		elif self.tabs == "ABOUT":
			self.draw_about(box)

		box = column.box()

		self.draw_progress(box, wm)

	def draw_general(self, box):
		split = box.split()

		b = split.box()
		
		column = b.column(align=True)
		row = column.row()
		row.scale_y = 3
		row.operator("tila.config_setup_blender", text="Setup Blender", icon='SHADERFX')
		row.operator("tila.config_update_setup_blender", text="Update Blender Setup", icon='FILE_REFRESH')
		column.separator()
		column.operator("tila.config_print_addon_list", text="Print Addon List", icon='ALIGN_JUSTIFY')
		column.separator()
		column.operator("tila.config_remove", text="Remove Config", icon='TRASH')
		column.operator("tila.config_disable_addon_list", text="Disable All Addons", icon='CHECKBOX_DEHLT').force=True
		column.operator("tila.config_clean_addon_list", text="Clean Addon List", icon='BRUSH_DATA').force=False
		column.operator("tila.config_sync_addon_list", text="Sync Addon List", icon='URL')
		column.operator("tila.config_link_addon_list", text="Link Addon List", icon='LINKED')
		column.operator("tila.config_enable_addon_list", text="Enable Addon List", icon='CHECKBOX_HLT')
		column.operator("tila.config_set_settings", text="Set Settings", icon='TOOL_SETTINGS')
		column.operator("tila.config_register_keymaps", text="Register Keymaps", icon='KEYINGSET')
		

	def draw_addons(self, box, wm):
		split = box.split()

		row = split.row()
		rows = 11 if len(wm.tila_config_addon_list) > 10 else len(wm.tila_config_addon_list) + 1
		
		row.template_list('TILA_UL_Config_addon_list', '', wm, 'tila_config_addon_list', wm, 'tila_config_addon_list_idx', rows=rows)
		c = row.column(align=True)
		c.operator('tila.config_import_addon_list', text='', icon='FILE_REFRESH')
		c.operator('tila.config_save_addon_list', text='', icon='CURRENT_FILE')
		c.operator('tila.config_add_addon', text='', icon='ADD')
		

	def draw_about(self, box):
		column = box.column(align=True)

		row = column.row(align=True)

		row.scale_y = 1.5
		# row.operator("wm.url_open", text='MACHIN3tools', icon='INFO').url = 'https://machin3.io/MACHIN3tools/'

	def draw_progress(self, box, wm):
		status = box.row(align=True)
		b1 = status.box()
		b1.label(text="Status")
		row = b1.row()
		rows = 11 if len(wm.tila_config_status_list) > 10 else len(wm.tila_config_status_list) + 1

		row.template_list('TILA_UL_Config_status_list', '', wm, 'tila_config_status_list', wm, 'tila_config_status_list_idx', rows=rows)
		row.operator('tila.config_clear_status_list', text='', icon='TRASH')

		b2 = status.box()
		b2.label(text="Progress")
		row = b2.row()
		rows = 11 if len(wm.tila_config_log_list) > 10 else len(wm.tila_config_log_list) + 1

		row.template_list('TILA_UL_Config_log_list', '', wm, 'tila_config_log_list', wm, 'tila_config_log_list_idx', rows=rows)
		
		row.operator('tila.config_clear_log_list', text='', icon='TRASH')

