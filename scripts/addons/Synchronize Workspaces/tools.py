from mathutils import Quaternion, Vector
import bpy


def copy_space_settings(f, t):
    t.use_local_camera = f.use_local_camera
    t.camera = f.camera
    t.clip_end = f.clip_end
    t.clip_start = f.clip_start
    t.lens = f.lens
    t.lock_bone = f.lock_bone
    t.lock_camera = f.lock_camera
    t.lock_cursor = f.lock_cursor
    t.lock_object = f.lock_object
    t.mirror_xr_session = f.mirror_xr_session
    t.show_gizmo = f.show_gizmo
    t.show_gizmo_camera_dof_distance = f.show_gizmo_camera_dof_distance
    t.show_gizmo_camera_lens = f.show_gizmo_camera_lens
    t.show_gizmo_context = f.show_gizmo_context
    t.show_gizmo_empty_force_field = f.show_gizmo_empty_force_field
    t.show_gizmo_empty_image = f.show_gizmo_empty_image
    t.show_gizmo_light_look_at = f.show_gizmo_light_look_at
    t.show_gizmo_light_size = f.show_gizmo_light_size
    t.show_gizmo_navigate = f.show_gizmo_navigate
    t.show_gizmo_object_rotate = f.show_gizmo_object_rotate
    t.show_gizmo_object_scale = f.show_gizmo_object_scale
    t.show_gizmo_object_translate = f.show_gizmo_object_translate
    t.show_gizmo_tool = f.show_gizmo_tool
    # t.show_locked_time = f.show_locked_time
    t.show_object_select_armature = f.show_object_select_armature
    t.show_object_select_camera = f.show_object_select_camera
    t.show_object_select_curve = f.show_object_select_curve
    t.show_object_select_empty = f.show_object_select_empty
    t.show_object_select_font = f.show_object_select_font
    t.show_object_select_grease_pencil = f.show_object_select_grease_pencil
    t.show_object_select_hair = f.show_object_select_hair
    t.show_object_select_lattice = f.show_object_select_lattice
    t.show_object_select_light = f.show_object_select_light
    t.show_object_select_light_probe = f.show_object_select_light_probe
    t.show_object_select_mesh = f.show_object_select_mesh
    t.show_object_select_meta = f.show_object_select_meta
    t.show_object_select_pointcloud = f.show_object_select_pointcloud
    t.show_object_select_speaker = f.show_object_select_speaker
    t.show_object_select_surf = f.show_object_select_surf
    t.show_object_select_volume = f.show_object_select_volume
    t.show_object_viewport_armature = f.show_object_viewport_armature
    t.show_object_viewport_camera = f.show_object_viewport_camera
    t.show_object_viewport_curve = f.show_object_viewport_curve
    t.show_object_viewport_empty = f.show_object_viewport_empty
    t.show_object_viewport_font = f.show_object_viewport_font
    t.show_object_viewport_grease_pencil = f.show_object_viewport_grease_pencil
    t.show_object_viewport_hair = f.show_object_viewport_hair
    t.show_object_viewport_lattice = f.show_object_viewport_lattice
    t.show_object_viewport_light = f.show_object_viewport_light
    t.show_object_viewport_light_probe = f.show_object_viewport_light_probe
    t.show_object_viewport_mesh = f.show_object_viewport_mesh
    t.show_object_viewport_meta = f.show_object_viewport_meta
    t.show_object_viewport_pointcloud = f.show_object_viewport_pointcloud
    t.show_object_viewport_speaker = f.show_object_viewport_speaker
    t.show_object_viewport_surf = f.show_object_viewport_surf
    t.show_object_viewport_volume = f.show_object_viewport_volume
    t.show_reconstruction = f.show_reconstruction
    t.show_stereo_3d_cameras = f.show_stereo_3d_cameras
    t.show_stereo_3d_convergence_plane = f.show_stereo_3d_convergence_plane
    t.show_stereo_3d_volume = f.show_stereo_3d_volume
    t.stereo_3d_camera = f.stereo_3d_camera
    t.stereo_3d_convergence_plane_alpha = f.stereo_3d_convergence_plane_alpha
    # t.stereo_3d_eye = f.stereo_3d_eye
    t.stereo_3d_volume_alpha = f.stereo_3d_volume_alpha
    t.tracks_display_size = f.tracks_display_size
    t.tracks_display_type = f.tracks_display_type
    t.use_local_collections = f.use_local_collections
    t.use_render_border = f.use_render_border


def setView(area, rotation):
    backVec = Vector((0.0, 0.0, -1.0))
    backVec = rotation @ backVec

    # rightVec = mathutils.Vector((1.0, 0.0, 0.0))
    # rightVec = rotation @ backVec

    context = bpy.context.copy()
    context['area'] = area
    for region in area.regions:
        if region.type == "WINDOW":
            break
    context['region'] = region
    context['space_data'] = area.spaces[0]

    axis = "FRONT"
    if backVec.y > 0.9:
        axis = "FRONT"
    if backVec.y < -0.9:
        axis = "BACK"
    if backVec.x > 0.9:
        axis = "LEFT"
    if backVec.x < -0.9:
        axis = "RIGHT"
    if backVec.z > 0.9:
        axis = "BOTTOM"
    if backVec.z < -0.9:
        axis = "TOP"
    # TODO no way to set 90 180 -90 views:
    #  x:1 => TOP Def ; y:-1 => TOP90 x:-1 => TOP180 y:1 => TOP-90
    #  x:1 => Bottom Def y:1 => Bottom90 x:-1 => Bottom180 y:-1 => Bottom-90

    bpy.ops.view3d.view_axis(context, type=axis)


def copy_shading_settings(f, t):
    t.aov_name = f.aov_name
    t.background_color = f.background_color
    t.background_type = f.background_type
    t.cavity_ridge_factor = f.cavity_ridge_factor
    t.cavity_type = f.cavity_type
    t.cavity_valley_factor = f.cavity_valley_factor
    t.color_type = f.color_type
    t.curvature_ridge_factor = f.curvature_ridge_factor
    t.curvature_valley_factor = f.curvature_valley_factor
    t.light = f.light
    t.object_outline_color = f.object_outline_color
    t.render_pass = f.render_pass
    # t.selected_studio_light = f.selected_studio_light
    t.shadow_intensity = f.shadow_intensity
    t.show_backface_culling = f.show_backface_culling
    t.show_cavity = f.show_cavity
    t.show_object_outline = f.show_object_outline
    t.show_shadows = f.show_shadows
    t.show_specular_highlight = f.show_specular_highlight
    t.show_xray = f.show_xray
    t.show_xray_wireframe = f.show_xray_wireframe
    t.single_color = f.single_color
    t.studio_light = f.studio_light
    t.studiolight_background_alpha = f.studiolight_background_alpha
    t.studiolight_background_blur = f.studiolight_background_blur
    t.studiolight_intensity = f.studiolight_intensity
    t.studiolight_rotate_z = f.studiolight_rotate_z
    t.use_dof = f.use_dof
    t.use_scene_lights = f.use_scene_lights
    t.use_scene_lights_render = f.use_scene_lights_render
    t.use_scene_world = f.use_scene_world
    t.use_scene_world_render = f.use_scene_world_render
    t.use_studiolight_view_rotation = f.use_studiolight_view_rotation
    t.use_world_space_lighting = f.use_world_space_lighting
    t.vr_show_controllers = f.vr_show_controllers
    t.vr_show_landmarks = f.vr_show_landmarks
    t.vr_show_virtual_camera = f.vr_show_virtual_camera
    t.wireframe_color_type = f.wireframe_color_type
    t.xray_alpha = f.xray_alpha
    t.xray_alpha_wireframe = f.xray_alpha_wireframe


def copy_overlays_settings(f, t):
    t.backwire_opacity = f.backwire_opacity
    t.display_handle = f.display_handle
    t.fade_inactive_alpha = f.fade_inactive_alpha
    t.gpencil_fade_layer = f.gpencil_fade_layer
    t.gpencil_fade_objects = f.gpencil_fade_objects
    t.gpencil_grid_opacity = f.gpencil_grid_opacity
    t.gpencil_vertex_paint_opacity = f.gpencil_vertex_paint_opacity
    t.grid_lines = f.grid_lines
    t.grid_scale = f.grid_scale
    # t.grid_scale_unit = f.grid_scale_unit
    t.grid_subdivisions = f.grid_subdivisions
    t.normals_constant_screen_size = f.normals_constant_screen_size
    t.normals_length = f.normals_length
    t.sculpt_mode_face_sets_opacity = f.sculpt_mode_face_sets_opacity
    t.sculpt_mode_mask_opacity = f.sculpt_mode_mask_opacity
    t.show_annotation = f.show_annotation
    t.show_axis_x = f.show_axis_x
    t.show_axis_y = f.show_axis_y
    t.show_axis_z = f.show_axis_z
    t.show_bones = f.show_bones
    t.show_cursor = f.show_cursor
    t.show_curve_normals = f.show_curve_normals
    t.show_edge_bevel_weight = f.show_edge_bevel_weight
    t.show_edge_crease = f.show_edge_crease
    t.show_edge_seams = f.show_edge_seams
    t.show_edge_sharp = f.show_edge_sharp
    t.show_edges = f.show_edges
    t.show_extra_edge_angle = f.show_extra_edge_angle
    t.show_extra_edge_length = f.show_extra_edge_length
    t.show_extra_face_angle = f.show_extra_face_angle
    t.show_extra_face_area = f.show_extra_face_area
    t.show_extra_indices = f.show_extra_indices
    t.show_extras = f.show_extras
    t.show_face_center = f.show_face_center
    t.show_face_normals = f.show_face_normals
    t.show_face_orientation = f.show_face_orientation
    t.show_faces = f.show_faces
    t.show_fade_inactive = f.show_fade_inactive
    t.show_floor = f.show_floor
    t.show_freestyle_edge_marks = f.show_freestyle_edge_marks
    t.show_freestyle_face_marks = f.show_freestyle_face_marks
    t.show_look_dev = f.show_look_dev
    t.show_motion_paths = f.show_motion_paths
    t.show_object_origins = f.show_object_origins
    t.show_object_origins_all = f.show_object_origins_all
    t.show_occlude_wire = f.show_occlude_wire
    t.show_onion_skins = f.show_onion_skins
    t.show_ortho_grid = f.show_ortho_grid
    t.show_outline_selected = f.show_outline_selected
    t.show_overlays = f.show_overlays
    t.show_paint_wire = f.show_paint_wire
    t.show_relationship_lines = f.show_relationship_lines
    t.show_split_normals = f.show_split_normals
    t.show_stats = f.show_stats
    t.show_statvis = f.show_statvis
    t.show_text = f.show_text
    t.show_vertex_normals = f.show_vertex_normals
    t.show_weight = f.show_weight
    t.show_wireframes = f.show_wireframes
    t.show_wpaint_contours = f.show_wpaint_contours
    t.show_xray_bone = f.show_xray_bone
    t.texture_paint_mode_opacity = f.texture_paint_mode_opacity
    t.use_gpencil_canvas_xray = f.use_gpencil_canvas_xray
    t.use_gpencil_edit_lines = f.use_gpencil_edit_lines
    t.use_gpencil_fade_gp_objects = f.use_gpencil_fade_gp_objects
    t.use_gpencil_fade_layers = f.use_gpencil_fade_layers
    t.use_gpencil_fade_objects = f.use_gpencil_fade_objects
    t.use_gpencil_grid = f.use_gpencil_grid
    t.use_gpencil_multiedit_line_only = f.use_gpencil_multiedit_line_only
    t.use_gpencil_onion_skin = f.use_gpencil_onion_skin
    t.use_gpencil_show_directions = f.use_gpencil_show_directions
    t.use_gpencil_show_material_name = f.use_gpencil_show_material_name
    t.vertex_opacity = f.vertex_opacity
    t.vertex_paint_mode_opacity = f.vertex_paint_mode_opacity
    t.weight_paint_mode_opacity = f.weight_paint_mode_opacity
    t.wireframe_opacity = f.wireframe_opacity
    t.wireframe_threshold = f.wireframe_threshold
    t.xray_alpha_bone = f.xray_alpha_bone
