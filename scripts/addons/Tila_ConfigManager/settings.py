import bpy
import os
from . blender_version import bversion

class TILA_Config_Settings():
	def __init__(self):
		pass

	def set_settings(self):
		# Set Theme to Tila
		root_path = bpy.utils.resource_path('USER')
		theme_filepath = os.path.join(
			root_path, 'scripts', 'presets', 'interface_theme', 'tila.xml')
		bpy.ops.script.execute_preset(
			filepath=theme_filepath, menu_idname='USERPREF_MT_interface_theme_presets')

		# Adjust addon Preference
		context = bpy.context

		# PolyQuilt
		addon = context.preferences.addons.get('PolyQuilt')
		addon.preferences.is_debug = False

		# Machin3Tools
		addon = context.preferences.addons.get('MACHIN3tools')
		addon.preferences.activate_smart_vert = False
		addon.preferences.activate_smart_edge = False
		addon.preferences.activate_smart_face = False
		addon.preferences.activate_focus = False
		addon.preferences.activate_mirror = True
		addon.preferences.activate_modes_pie = False
		addon.preferences.activate_views_pie = False
		addon.preferences.activate_transform_pie = False
		addon.preferences.activate_collections_pie = False
		addon.preferences.activate_align = True
		addon.preferences.activate_filebrowser_tools = True
		addon.preferences.activate_extrude = True
		addon.preferences.activate_clean_up = True
		addon.preferences.activate_edge_constraint = True
		addon.preferences.activate_surface_slide = True
		addon.preferences.activate_group = False
		addon.preferences.activate_mesh_cut = True
		addon.preferences.activate_thread = True
		addon.preferences.activate_material_picker = True
		addon.preferences.activate_save_pie = True
		addon.preferences.activate_align_pie = True
		addon.preferences.activate_cursor_pie = True
		# kmi = bpy.context.window_manager.keyconfigs.addon.keymaps['Window'].keymap_items
		# for k in kmi:
		# 	if k.type == 'S' and k.properties.name == 'MACHIN3_MT_save_pie':
		# 		k.shift = True
		# 		bpy.context.window_manager.keyconfigs.update()

		# object_collection_manager
		addon = context.preferences.addons.get('object_collection_manager')
		addon.preferences.enable_qcd = False

		# noodler
		addon = context.preferences.addons.get('noodler')
		kmi = bpy.context.window_manager.keyconfigs.addon.keymaps['Node Editor'].keymap_items
		for k in kmi:
			if k.idname == 'noodler.draw_route':
				k.type = 'E'
			if k.idname == 'noodler.chamfer':
				k.ctrl = False
			if k.idname == 'noodler.draw_frame':
				k.ctrl = True

		# mouselook_navigation
		# addon = context.preferences.addons.get('mouselook_navigation')
		# addon.preferences.show_zbrush_border = False
		# addon.preferences.show_crosshair = False
		# addon.preferences.show_focus = False
		# addon.preferences.rotation_snap_subdivs = 1

		# kekit
		# addon = context.preferences.addons.get('kekit')
		# addon.preferences.category = 'Tools'

		# # greasepencil_tools
		addon = context.preferences.addons.get('greasepencil_tools')
		addon.preferences.canvas_use_hud = False
		# addon.preferences.mouse_click = 'RIGHTMOUSE'
		addon.preferences.rc_angle_step = 45 * 0.0174533  # 45 deg to rad
		# addon.preferences.use_ctrl = False
		# addon.preferences.use_alt = True
		# addon.preferences.use_shift = False

		addon.preferences.ts.use_ctrl = False
		addon.preferences.ts.use_alt = False
		addon.preferences.ts.use_shift = True
		addon.preferences.ts.keycode = 'SPACE'

		# user_pref_path = bpy.utils.resource_path(type='USER')
		# asset_library_path = os.path.join(user_pref_path, 'datafiles', 'scene', '00_Asset_Library')
		library_name = '00_Blender_Asset_Library'
		asset_library_path = os.path.join('R:\\', 'Mon Drive', library_name)
		bpy.ops.preferences.asset_library_add(
			'EXEC_DEFAULT', directory=asset_library_path)
		if bversion < 3.2:
			library_name = ''
		bpy.context.preferences.filepaths.asset_libraries[library_name].name = 'Tilapiatsu'

		# # Atomic Data Manager
		addon = context.preferences.addons.get('atomic_data_manager')
		addon.preferences.enable_missing_file_warning = False

		# # Auto Reload
		addon = context.preferences.addons.get('Auto_Reload')
		addon.preferences.update_check_launch = False
