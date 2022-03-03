import bpy, os, addon_utils 
# from addon_utils import check,paths,enable

modules =   (
			'mesh_f2',
			# 'TexTools',
			'io_import_images_as_planes',
			'mesh_f2',
			'fspy',
			'object_print3d_utils',
			'mesh_looptools',
			'MACHIN3tools',
			'UvSquares',
			'Auto_Reload',
			# 'mesh_mesh_align_plus',
			'node_wrangler',
			'node_presets',
			'mesh_snap_utilities_line',
			# 'Principled-Baker',
			'object_boolean_tools',
			'optiloops',
			# 'DNoise',
			# 'RenderBurst',
			'magic_uv',
			# 'photographer',
			'transfer_vertex_order',
			'PolyQuilt',
			'slcad_transform',
			'EasyHDRI',
			'Lodify',
			'BystedtsBlenderBaker',
			'SSGI',
			# 'MeasureIt-ARCH',
			'RetopoFlow',
			'add_curve_extra_objects',
			'add_mesh_extra_objects',
			'io_scene_fbx',
			'io_scene_obj',
			'io_scene_x3d',
			'io_scene_gltf2',
			'io_mesh_stl',
			'io_curve_svg',
			'io_mesh_ply',
			'io_mesh_uv_layout',
			'object_collection_manager',
			'space_view3d_copy_attributes',
			'space_view3d_modifier_tools',
			'EdgeFlow',
			'mesh_tools',
			'space_view3d_align_tools',
			'cycles',
			'Polycount',
			'mira_tools',
			'Neltulz_Smart_Sharpen',
			'Neltulz_Symmetry',
			'MeshDataTransfer',
			'keentools_facebuilder',
			'kekit',
			'Poly_Source',
			'maxivz_tools',
			'rotate_an_hdri',
			'blenderbezierutils',
			'oscurart_edit_split_normals',
			# 'mouselook_navigation',
			'vertex_color_master',
			'BakeWrangler',
			'atomic_data_manager',
			# 'ImagePaste',
			'greasepencil_tools',
			'keymesh',
			# 'ZWeightTools-1_0_1',
			# 'W_Mesh',
			'uvpackmaster3',
			'uv_toolkit',
			'noodler',
			# 'lineup_maker',
			'Tila_Config'
			)

def register(enable_addon=True):
	if enable_addon:
		# Enabling addons
		for m in modules:
			# is_enabled, _ = check(m)
			# print(is_enabled, m)
			# if is_enabled:
			#     bpy.ops.preferences.addon_disable(module=m)
			#     bpy.context.window_manager.keyconfigs.update()
			#     print("disableing addon {}".format(m))

			bpy.ops.preferences.addon_enable(module=m)
			print('Enabling Addon : {}'.format(m))
			bpy.context.window_manager.keyconfigs.update()


		
	
	# Set Theme to Tila
	root_path = bpy.utils.resource_path('USER')
	theme_filepath = os.path.join(root_path, 'scripts', 'presets', 'interface_theme', 'tila.xml')
	bpy.ops.script.execute_preset(filepath=theme_filepath, menu_idname='USERPREF_MT_interface_theme_presets')

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
	addon.preferences.activate_mirror = False
	addon.preferences.activate_modes_pie = False
	addon.preferences.activate_views_pie = False
	addon.preferences.activate_transform_pie = False
	addon.preferences.activate_collections_pie = False
	addon.preferences.activate_align = True
	addon.preferences.activate_filebrowser_tools = True
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
	addon.preferences.mouse_click = 'RIGHTMOUSE'
	addon.preferences.rc_angle_step = 45 * 0.0174533 #45 deg to rad
	addon.preferences.use_ctrl = False
	addon.preferences.use_alt = True
	addon.preferences.use_shift = False

	addon.preferences.ts.use_ctrl = False
	addon.preferences.ts.use_alt = False
	addon.preferences.ts.use_shift = True
	addon.preferences.ts.keycode = 'SPACE'

	user_pref_path = bpy.utils.resource_path(type='USER')
	asset_library_path = os.path.join(user_pref_path, 'datafiles', 'scene', '00_Asset_Library')
	bpy.ops.preferences.asset_library_add('EXEC_DEFAULT', directory=asset_library_path)
	bpy.context.preferences.filepaths.asset_libraries[''].name = 'Tilapiatsu'

	bpy.ops.wm.save_userpref()



def unregister():
	# disabling addons
	for m in modules:
		bpy.ops.preferences.addon_disable(module=m)
		bpy.context.window_manager.keyconfigs.update()

if __name__ == "__main__":
	register()
	# unregister()
	