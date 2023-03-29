import bpy
import os
from . blender_version import bversion

class TILA_Config_Settings():
	def __init__(self):
		pass
	
	def set_machin3tool_settings(self, context, setting_name, value):
		if getattr(context.preferences.addons.get('MACHIN3tools').preferences, setting_name) == value:
			return
		
		setattr(context.preferences.addons.get('MACHIN3tools').preferences, setting_name, value)
		

	def set_settings(self):
		context = bpy.context

		# # Set Theme to Tila
		root_path = bpy.utils.resource_path('USER')
		theme_filepath = os.path.join(
			root_path, 'scripts', 'presets', 'interface_theme', 'tila.xml')
		bpy.ops.script.execute_preset(
			filepath=theme_filepath, menu_idname='USERPREF_MT_interface_theme_presets')
		
		# # Set Asset Library
		library_name = '00_Blender_Asset_Library'
		asset_library_path = os.path.join('R:\\', 'Mon Drive', library_name)
		bpy.ops.preferences.asset_library_add(
			'EXEC_DEFAULT', directory=asset_library_path)
		if bversion < 3.2:
			library_name = ''

		context.preferences.filepaths.asset_libraries[library_name].name = 'Tilapiatsu'
		
		#########################
		# Adjust addon Preference
		#########################

		# # PolyQuilt
		addon_name = 'PolyQuilt'
		if addon_name in bpy.context.preferences.addons:
			addon = context.preferences.addons.get(addon_name)
			addon.preferences.is_debug = False

		# # Machin3Tools
		addon_name = 'MACHIN3tools'
		if addon_name in bpy.context.preferences.addons:
			addon = context.preferences.addons.get(addon_name)
			
			self.set_machin3tool_settings(context, 'activate_smart_vert' , False)
			self.set_machin3tool_settings(context, 'activate_smart_edge' , False)
			self.set_machin3tool_settings(context, 'activate_smart_face' , False)
			self.set_machin3tool_settings(context, 'activate_focus' , False)
			self.set_machin3tool_settings(context, 'activate_mirror' , True)
			self.set_machin3tool_settings(context, 'activate_modes_pie' , False)
			self.set_machin3tool_settings(context, 'activate_views_pie' , False)
			self.set_machin3tool_settings(context, 'activate_transform_pie' , False)
			self.set_machin3tool_settings(context, 'activate_collections_pie' , False)
			self.set_machin3tool_settings(context, 'activate_align' , True)
			self.set_machin3tool_settings(context, 'activate_filebrowser_tools' , True)
			self.set_machin3tool_settings(context, 'activate_extrude' , True)
			self.set_machin3tool_settings(context, 'activate_clean_up' , True)
			self.set_machin3tool_settings(context, 'activate_edge_constraint' , True)
			self.set_machin3tool_settings(context, 'activate_surface_slide' , True)
			self.set_machin3tool_settings(context, 'activate_group' , False)
			self.set_machin3tool_settings(context, 'activate_mesh_cut' , True)
			self.set_machin3tool_settings(context, 'activate_thread' , True)
			self.set_machin3tool_settings(context, 'activate_material_picker' , True)
			self.set_machin3tool_settings(context, 'activate_save_pie' , True)
			self.set_machin3tool_settings(context, 'activate_align_pie' , True)
			self.set_machin3tool_settings(context, 'activate_cursor_pie' , True)

		# # object_collection_manager
		addon_name = 'object_collection_manager'
		if addon_name in bpy.context.preferences.addons:
			addon = context.preferences.addons.get(addon_name)
			addon.preferences.enable_qcd = False

		# # noodler
		addon_name = 'noodler'
		if addon_name in bpy.context.preferences.addons:
			addon = context.preferences.addons.get(addon_name)
			kmi = bpy.context.window_manager.keyconfigs.addon.keymaps['Node Editor'].keymap_items
			for k in kmi:
				if k.idname == 'noodler.draw_route':
					k.type = 'E'
				if k.idname == 'noodler.chamfer':
					k.ctrl = False
				if k.idname == 'noodler.draw_frame':
					k.ctrl = True

		# # mouselook_navigation
		# addon_name = 'mouselook_navigation'
		# if addon_name in bpy.context.preferences.addons:
			# addon = context.preferences.addons.get('mouselook_navigation')
			# addon.preferences.show_zbrush_border = False
			# addon.preferences.show_crosshair = False
			# addon.preferences.show_focus = False
			# addon.preferences.rotation_snap_subdivs = 1

		# # kekit
		# addon_name = 'kekit'
		# if addon_name in bpy.context.preferences.addons:
			# addon = context.preferences.addons.get(addon_name)
			# addon.preferences.category = 'Tools'

		# # greasepencil_tools
		addon_name = 'greasepencil_tools'
		if addon_name in bpy.context.preferences.addons:
			addon = context.preferences.addons.get(addon_name)
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

		# # Atomic Data Manager
		addon_name = 'atomic_data_manager'
		if addon_name in bpy.context.preferences.addons:
			addon = context.preferences.addons.get(addon_name)
			addon.preferences.enable_missing_file_warning = False

		# # Auto Reload
		addon_name = 'Auto_Reload'
		if addon_name in bpy.context.preferences.addons:
			addon = context.preferences.addons.get(addon_name)
			addon.preferences.update_check_launch = False

		# Save Preference
		bpy.ops.wm.save_userpref()
