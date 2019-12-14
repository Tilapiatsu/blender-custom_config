import bpy, os

modules =   (
            'mesh_f2',
            'TextTools',
            'io_import_images_as_planes',
            'mesh_f2',
            'fspy_blender',
            'object_print3d_utils',
            'mesh_looptools',
            'MACHIN3tools',
            'mesh_mesh_align_plus',
            'node_wrangler',
            'node_presets',
            'mesh_snap_utilities_line',
            'Principled-Baker',
            'object_boolean_tools',
            'optiloops',
            'DNoise',
            'RenderBurst',
            'magic_uv',
            'photographer',
            'transfer_vertex_order',
            'PolyQuilt',
            'ExtraInfo',
            'EasyHDRI',
            'MeasureIt-ARCH',
            'retopoflow',
            'add_curve_extra_objects',
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
            'uvpackmaster2',
            'uv_toolkit',
            'lineup_maker',
            'Tila_Config'
            )

def register():
    # Enabling addons
    for m in modules:
        bpy.ops.preferences.addon_enable(module=m)
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
    addon.preferences.activate_mode_pie = False
    addon.preferences.activate_views_pie = False
    addon.preferences.activate_transform_pie = False
    addon.preferences.activate_collections_pie = False

def unregister():
    # disabling addons
    for m in modules:
        bpy.ops.preferences.addon_disable(module=m)
        bpy.context.window_manager.keyconfigs.update()

if __name__ == "__main__":
    register()
    # unregister()
    