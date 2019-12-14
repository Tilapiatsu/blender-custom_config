import os
import bpy
bl_info = {
    "name": "Tilapiatsu Settings",
            "description": "Settings",
            "author": "Tilapiatsu",
            "version": (0, 1, 0),
            "blender": (2, 80, 0),
            "location": "",
            "warning": "",
            "wiki_url": "",
            "category": "Settings"
}


def register():
    pass


print("Loading Tilapiatu's user preferences")

# View Settings
bpy.context.preferences.view.show_tooltips = True
bpy.context.preferences.view.show_tooltips_python = True
bpy.context.preferences.view.render_display_type = "NONE"

# Edit Settings
bpy.context.preferences.edit.undo_steps = 200

# Input Settings
bpy.context.preferences.inputs.view_zoom_axis = "HORIZONTAL"
bpy.context.preferences.inputs.use_trackpad_natural = True
bpy.context.preferences.inputs.ndof_view_navigate_method = "FREE"
bpy.context.preferences.inputs.ndof_view_rotate_method = "TRACKBALL"
bpy.context.preferences.inputs.view_rotate_method = "TRACKBALL"
bpy.context.preferences.inputs.use_auto_perspective = True
bpy.context.preferences.inputs.use_mouse_depth_navigate = True
# bpy.context.preferences.inputs.use_mouse_emulate_3_button = True
bpy.context.preferences.inputs.use_zoom_to_mouse = True

# Theme tweak
root_path = os.path.join(os.path.realpath(__file__), os.pardir)
theme_filepath = os.path.join(root_path, 'presets', 'interface_theme', 'tila.xml')
bpy.ops.script.execute_preset(filepath=theme_filepath)

# Enabling addon
bpy.ops.preferences.addon_enable(module='mesh_f2')
bpy.ops.preferences.addon_enable(module='io_import_images_as_planes')
bpy.ops.preferences.addon_enable(module='mesh_f2')
bpy.ops.preferences.addon_enable(module='fspy_blender')
bpy.ops.preferences.addon_enable(module='object_print3d_utils')
bpy.ops.preferences.addon_enable(module='mesh_looptools')
bpy.ops.preferences.addon_enable(module='MACHIN3tools')
bpy.ops.preferences.addon_enable(module='mesh_mesh_align_plus')
bpy.ops.preferences.addon_enable(module='node_wrangler')
bpy.ops.preferences.addon_enable(module='node_presets')
bpy.ops.preferences.addon_enable(module='mesh_snap_utilities_line')
bpy.ops.preferences.addon_enable(module='Principled-Baker')
bpy.ops.preferences.addon_enable(module='object_bolean_tools')
bpy.ops.preferences.addon_enable(module='optiloops')
bpy.ops.preferences.addon_enable(module='DNoise')
bpy.ops.preferences.addon_enable(module='RenderBurst')
bpy.ops.preferences.addon_enable(module='magic_uv')
bpy.ops.preferences.addon_enable(module='TexTools')
bpy.ops.preferences.addon_enable(module='photographer')
bpy.ops.preferences.addon_enable(module='transfer_vertex_order')
bpy.ops.preferences.addon_enable(module='PolyQuilt')
bpy.ops.preferences.addon_enable(module='ExtraInfo')
bpy.ops.preferences.addon_enable(module='EasyHDRI')
bpy.ops.preferences.addon_enable(module='MesureIt-ARCH')
bpy.ops.preferences.addon_enable(module='retopoflow')
bpy.ops.preferences.addon_enable(module='add_curve_extra_objects')
bpy.ops.preferences.addon_enable(module='io_scene_fbx')
bpy.ops.preferences.addon_enable(module='io_scene_obj')
bpy.ops.preferences.addon_enable(module='io_scene_x3d')
bpy.ops.preferences.addon_enable(module='io_scene_gltf2')
bpy.ops.preferences.addon_enable(module='io_mesh_stl')
bpy.ops.preferences.addon_enable(module='io_curve_svg')
bpy.ops.preferences.addon_enable(module='io_mesh_ply')
bpy.ops.preferences.addon_enable(module='io_mesh_uv_layout')
bpy.ops.preferences.addon_enable(module='object_collection_manager')
bpy.ops.preferences.addon_enable(module='space_view3d_copy_attributes')
bpy.ops.preferences.addon_enable(module='space_view3d_modifier_tools')
bpy.ops.preferences.addon_enable(module='EdgeFlow')
bpy.ops.preferences.addon_enable(module='mesh_tools')
bpy.ops.preferences.addon_enable(module='space_view3d_align_tools')
bpy.ops.preferences.addon_enable(module='cycle')
bpy.ops.preferences.addon_enable(module='Polycount')
bpy.ops.preferences.addon_enable(module='mira_tools')
bpy.ops.preferences.addon_enable(module='uvpackmaster2')
bpy.ops.preferences.addon_enable(module='uv_toolkit')
bpy.ops.preferences.addon_enable(module='lineup_maker')
bpy.ops.preferences.addon_enable(module='Tila_Config')

print("Loading Tilapiatu's user preferences Completed")
