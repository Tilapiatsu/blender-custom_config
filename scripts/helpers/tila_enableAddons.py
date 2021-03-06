import bpy, os, addon_utils
# from addon_utils import check,paths,enable

modules =   (
			'mesh_f2',
			'TextTools',
			'io_import_images_as_planes',
			'mesh_f2',
			'fspy_blender',
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
			'RenderBurst',
			'magic_uv',
			'photographer',
			'transfer_vertex_order',
			'PolyQuilt',
			'slcad_transform',
			'EasyHDRI',
			'Lodify',
			'bakeToVertexColor',
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
			'mouselook_navigation',
			'vertex_color_master',
			'BakeWrangler',
			'atomic_data_manager',
			'ImagePaste',
			'viewport_timeline_scrub',
			# 'ZWeightTools-1_0_1',
			# 'W_Mesh',
			'uvpackmaster2',
			'uv_toolkit',
			'lineup_maker',
			'Tila_Config'
			)

def register():
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
	kmi = bpy.context.window_manager.keyconfigs.addon.keymaps['Window'].keymap_items
	for k in kmi:
		if k.type == 'S':
			k.active = False
			bpy.context.window_manager.keyconfigs.update()

	# object_collection_manager
	addon = context.preferences.addons.get('object_collection_manager')
	addon.preferences.enable_qcd = False


	# # mouselook_navigation
	addon = context.preferences.addons.get('mouselook_navigation')
	addon.preferences.show_zbrush_border = False
	addon.preferences.show_crosshair = False
	addon.preferences.show_focus = False
	addon.preferences.rotation_snap_subdivs = 1

	# # kekit
	# addon = context.preferences.addons.get('kekit')
	# addon.preferences.category = 'Tools'

	# # viewport_timeline_scrub
	addon = context.preferences.addons.get('viewport_timeline_scrub')
	addon.preferences.keycode = 'SPACE'

def unregister():
	# disabling addons
	for m in modules:
		bpy.ops.preferences.addon_disable(module=m)
		bpy.context.window_manager.keyconfigs.update()

if __name__ == "__main__":
	register()
	# unregister()
	