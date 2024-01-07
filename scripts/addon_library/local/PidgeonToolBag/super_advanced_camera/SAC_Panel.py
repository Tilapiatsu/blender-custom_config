import bpy

from ..pidgeon_tool_bag.PTB_PropertiesRender_Panel import PTB_PT_Panel

from bpy.types import (
    Context,
    Panel,
)

from .SAC_Settings import SAC_Settings
from .SAC_Functions import (
    frames_to_time,
)
from ..pidgeon_tool_bag.PTB_Functions import (
    template_boxtitle,
)

# Main

class SAC_PT_SAC_Panel(PTB_PT_Panel, Panel):
    bl_label = "Super Advanced Camera"
    bl_parent_id = "PTB_PT_PTB_Panel"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="CAMERA_DATA")

    def draw(self, context: Context):
        settings = context.scene.sac_settings
        scene = context.scene

        colmain = self.layout.column(align=False)
        boxmain = colmain.box()
        boxcol = boxmain.column()
        template_boxtitle(settings, boxcol, "camera", "Camera", "OUTLINER_DATA_CAMERA")
        if settings.show_camera:

            if settings.selected_camera == "None":
                boxcol.label(text="No camera found in scene.")
                boxcol.label(text="Please add a camera to the scene.")
            else: 
                boxcol.prop(settings, "selected_camera", text="Camera")

                camera_object = bpy.data.objects[settings.selected_camera]
                camera_data = bpy.data.cameras[camera_object.data.name]

                boxbox = boxcol.box()
                template_boxtitle(settings, boxbox, "rendersettings", "Render Settings", "SETTINGS")
                if settings.show_rendersettings:
                    col = boxbox.column(align=True)

                    boxboxresolution = col.box()
                    boxboxresolution = boxboxresolution.column()
                    boxboxresolution.label(text="Resolution", icon="IMAGE_PLANE")
                    row = boxboxresolution.row(align=True)
                    row.prop(context.scene.render, "resolution_x", text="Width")
                    row.prop(context.scene.render, "resolution_y", text="Height")
                    boxboxresolution.prop(context.scene.render, "resolution_percentage", text="Scale")

                    # start frame
                    boxboxframes = col.box()
                    boxboxframes = boxboxframes.column()
                    boxboxframes.label(text="Frames", icon="NODE_COMPOSITING")
                    row = boxboxframes.row(align=True)
                    if not scene.use_preview_range:
                        row.prop(scene, "frame_start", text="Start")
                        row.prop(scene, "frame_end", text="End")
                        row.prop(scene, "frame_step", text="Step")

                    else:
                        row.prop(scene, "frame_preview_start", text="Start")
                        row.prop(scene, "frame_preview_end", text="End")
                        subrow = row.row(align=True)
                        subrow.enabled = False
                        subrow.prop(scene, "frame_step", text="Step")
                    row = boxboxframes.row(align=True)
                    row.enabled = False
                    row.label(text=f"Start: {frames_to_time(scene.frame_start, scene.render.fps//scene.render.fps_base)}")
                    row.label(text=f"End: {frames_to_time(scene.frame_end, scene.render.fps//scene.render.fps_base)}")
                    row.label(text=f"Total: {frames_to_time((scene.frame_end - scene.frame_start + 1)//scene.frame_step, scene.render.fps//scene.render.fps_base)}")
                    boxboxframes.prop(scene, "use_preview_range", text="Use Preview Range", toggle=True)

                    row = boxboxframes.row(align=True)
                    row.operator("superadvancedcamera.set_start_frame")
                    row.operator("superadvancedcamera.set_end_frame")

                    row = boxboxframes.row(align=True)
                    row.prop(scene, "show_subframe", text="Show Subframes")
                    subcol = row.column(align=True)
                    if scene.show_subframe:
                        subcol.prop(scene, "frame_float", text="Current")
                    else:
                        subcol.prop(scene, "frame_current", text="Current")
                    subcol_inactive = subcol.column(align=True)
                    subcol_inactive.active = False
                    subcol_inactive.label(text=f"Current: {frames_to_time(scene.frame_float, scene.render.fps//scene.render.fps_base)}")

                    row = boxboxframes.row(align=True)
                    row.label(text="Frame Rate: " + str(round(scene.render.fps/scene.render.fps_base, 2)) + " fps")
                    row.active = False
                    row = boxboxframes.row(align=True)
                    row.prop(scene.render, "fps")
                    row.prop(scene.render, "fps_base", text="Base")

                    # time stretching
                    boxboxtimestretching = col.box()
                    boxboxtimestretching = boxboxtimestretching.column()
                    boxboxtimestretching.label(text="Time Stretching", icon="TEMP")
                    boxboxtimestretching.prop(settings, "Camera_FrameStretching")
                    row = boxboxtimestretching.row(align=True)
                    row.prop(scene.render, "frame_map_old", text="Original duration")
                    row.prop(scene.render, "frame_map_new", text="New duration")

                boxbox = boxcol.box()
                template_boxtitle(settings, boxbox, "lenssettings", "Lens Settings", "PROP_PROJECTED")
                if settings.show_lenssettings:
                    col = boxbox.column(align=True)

                    if settings.Camera_TiltShift_KeepFrame == True:
                        shift_x_text = "Vertical Tilt Shift"
                        shift_y_text = "Horizontal Tilt Shift"
                        shift_text = "Tilt Shift"
                        shift_icon = "MOD_LATTICE"
                    else:
                        shift_x_text = "Vertical Lens Shift"
                        shift_y_text = "Horizontal Lens Shift"
                        shift_text = "Lens Shift"
                        shift_icon = "VIEW_PERSPECTIVE"

                    col_shift = col.column(align=False)
                    row_shift = col_shift.row(align=True)
                    row_shift.label(text=shift_text, icon=shift_icon)
                    row_shift.prop(settings, "Camera_TiltShift_KeepFrame", toggle=True)
                    col_shift.prop(settings, "Camera_TiltShift_AmountX", text=shift_x_text)
                    col_shift.prop(settings, "Camera_TiltShift_AmountY", text=shift_y_text)
                    col.separator()

                    col_focal = col.row(align=True)
                    col_focal.prop(camera_data, "lens")
                    col_focal.prop(camera_data, "angle")

                    col_clip = col.row(align=True)
                    col_clip.prop(camera_data, "clip_start", text="Min. Visible Distance")
                    col_clip.prop(camera_data, "clip_end", text="Max. Visible Distance")
                    col.separator()

                    col_film = col.row(align=True)
                    col_film.prop(scene.cycles, "pixel_filter_type", text="Lens Blur Type")
                    col_film = col.column()
                    col_film.prop(scene.cycles, "filter_width", text="Lens Blur Strength")

                boxbox = boxcol.box()
                template_boxtitle(settings, boxbox, "bokeh", "Bokeh", "SEQ_CHROMA_SCOPE")
                if settings.show_bokeh:
                    coltitle = boxbox.column(align=False)
                    coltitle.prop(camera_data.dof, "use_dof", text="Use Bokeh", toggle=True)
                    col = boxbox.column(align=True)

                    col.active = camera_data.dof.use_dof

                    boxcol = col.box()
                    boxcol.prop(camera_data.dof, "focus_object")
                    boxcol.prop(camera_data.dof, "focus_distance")
                    boxcol.prop(camera_data.dof, "aperture_fstop")
                    boxcol.separator()

                    boxcol = col.box()
                    try:
                        bpy.data.objects[f"SAC_Bokeh_{settings.selected_camera}"]
                    except:
                        boxcol.label(text="No Bokeh Plane found.")
                        boxcol.label(text="Please apply Bokeh first.")
                        boxcol.operator("superadvancedcamera.apply_camera_bokeh", icon="SEQ_CHROMA_SCOPE")
                        return
                    
                    boxcol.label(text="Bokeh Type")
                    row_bokeh_type = boxcol.row(align=True)
                    row_bokeh_type.prop(settings, "Camera_Bokeh_Type", expand=True)
                    boxcol.separator(factor=0.5)
                    boxcol = boxcol.column()

                    if settings.Camera_Bokeh_Type == "CAMERA":
                        row = boxcol.row(align=True)
                        left = row.column(align=True)
                        left.scale_x = 1
                        left.scale_y = 8
                        left.operator("superadvancedcamera.previous_camera_bokeh", text="", icon="TRIA_LEFT")
                        center = row.column()
                        center.template_icon_view(context.scene, "new_camera_bokeh_type", show_labels=True, scale=8.0, scale_popup=4.0)
                        right = row.column(align=True)
                        right.scale_x = 1
                        right.scale_y = 8
                        right.operator("superadvancedcamera.next_camera_bokeh", text="", icon="TRIA_RIGHT")

                        bokeh_type = context.scene.new_camera_bokeh_type.split("_")
                        col_bokeh_description = boxcol.column(align=True)
                        col_bokeh_description.active = False

                        row_bokeh_description = col_bokeh_description.row(align=True)
                        row_bokeh_description.label(text="Manufacturer:")
                        row_bokeh_description.label(text=bokeh_type[0])

                        row_bokeh_description = col_bokeh_description.row(align=True)
                        row_bokeh_description.label(text="Model:")
                        row_bokeh_description.label(text=f"{bokeh_type[1]} - {bokeh_type[3]} - {bokeh_type[2]}")

                        row_bokeh_description = col_bokeh_description.row(align=True)
                        row_bokeh_description.label(text="Aperture:")
                        row_bokeh_description.label(text=bokeh_type[4])

                        col_bokeh_description.label(text="Special thanks to Prof. Dr. Matt Gunn for the Bokeh textures.")

                        boxcol.separator()
                        boxcol.prop(settings, "Camera_Bokeh_Scale")
                        boxcol.prop(settings, "Camera_Bokeh_Rotation")
                        boxcol.prop(settings, "Camera_Bokeh_Curves")
                        boxcol.separator()
                        boxcol.operator("superadvancedcamera.apply_camera_bokeh", icon="SEQ_CHROMA_SCOPE")

                    elif settings.Camera_Bokeh_Type == "PROCEDURAL":
                        boxcol.prop(camera_data.dof, "aperture_blades")
                        boxcol.prop(camera_data.dof, "aperture_rotation")
                        boxcol.prop(camera_data.dof, "aperture_ratio")

                    elif settings.Camera_Bokeh_Type == "CUSTOM":
                        material = bpy.data.materials[f".SAC_Bokeh_{settings.selected_camera}_Material"]
                        material_node_tree = material.node_tree
                        bokeh_image = material_node_tree.nodes["SAC Camera_Bokeh_Custom_Texture"]

                        boxcol.template_ID_preview(bokeh_image, "image", open="image.open", rows=3, cols=8)
                        boxcol.prop(settings, "Camera_Bokeh_Scale")
                        boxcol.prop(settings, "Camera_Bokeh_Rotation")
                        boxcol.prop(settings, "Camera_Bokeh_Curves")

        boxmain = colmain.box()
        boxcol = boxmain.column()
        template_boxtitle(settings, boxcol, "colorgrading", "Color Grading", "MOD_HUE_SATURATION")
        if settings.show_colorgrading:
            found = False
            if not context.scene.use_nodes:
                boxcol.label(text="You need to enable the Compositor to use this feature!", icon="ERROR")
                boxcol.prop(context.scene, "use_nodes", text="Enable Compositor?", toggle=True)
            else:
                for node in bpy.context.scene.node_tree.nodes:
                    if node.name.startswith("Super Advanced Camera"):
                        found = True
                        break
                if not found:
                    boxcol.label(text="You need to initialize SAC to use this feature!", icon="ERROR")
                    boxcol.operator("superadvancedcamera.superadvancedcamerainit", text="Initialize Super Advanced Camera", icon="SHADERFX")
                else:

                    rgb_curves_node = bpy.data.node_groups[".SAC Curves"].nodes["SAC Colorgrade_Curves_RGB"]
                    hsv_curves_node = bpy.data.node_groups[".SAC Curves"].nodes["SAC Colorgrade_Curves_HSV"]
                    color_wheel_node_lift = bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Shadows"]
                    color_wheel_node_gamma = bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Midtones"]
                    color_wheel_node_gain = bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Highlights"]

                    icon_checkbox = "CHECKBOX_HLT" if settings.Colorgrade_Enable else "CHECKBOX_DEHLT"
                    boxcol.prop(settings, "Colorgrade_Enable", text="Use Color Grading", toggle=True, icon=icon_checkbox)
                    boxcol.separator()

                    boxbox = boxcol.box()
                    template_boxtitle(settings, boxbox, "color", "Color", "COLOR")
                    if settings.show_color:
                        col = boxbox.column()
                        row = col.row(align=True)
                        row.prop(settings, "Colorgrade_Color_WhiteLevel")
                        col.prop(settings, "Colorgrade_Color_Temperature")
                        col.prop(settings, "Colorgrade_Color_Tint")
                        col.prop(settings, "Colorgrade_Color_Saturation")
                        col.prop(settings, "Colorgrade_Color_Hue")

                    boxbox = boxcol.box()
                    template_boxtitle(settings, boxbox, "light", "Light", "OUTLINER_OB_LIGHT")
                    if settings.show_light:
                        col = boxbox.column()
                        col.prop(settings, "Colorgrade_Light_Exposure")
                        col.prop(settings, "Colorgrade_Light_Contrast")
                        col.prop(settings, "Colorgrade_Light_Highlights")
                        col.prop(settings, "Colorgrade_Light_Shadows")
                        col.prop(settings, "Colorgrade_Light_Whites")
                        col.prop(settings, "Colorgrade_Light_Darks")

                    boxbox = boxcol.box()
                    template_boxtitle(settings, boxbox, "presets", "Presets", "PRESET")
                    if settings.show_presets:
                        col = boxbox.column()

                        col.prop(settings, "filter_type")

                        row = col.row(align=True)
                        left = row.column(align=True)
                        left.scale_x = 1
                        left.scale_y = 8
                        left.operator("superadvancedcamera.previous_filter", text="", icon="TRIA_LEFT")
                        center = row.column()
                        center.template_icon_view(context.scene, "new_filter_type", show_labels=True, scale=8.0, scale_popup=4.0)
                        right = row.column(align=True)
                        right.scale_x = 1
                        right.scale_y = 8
                        right.operator("superadvancedcamera.next_filter", text="", icon="TRIA_RIGHT")
                        center_column = col.row(align=True)
                        center_column.label(text="Filter Name:")
                        center_column.label(text=f"{scene.new_filter_type}")

                        col.operator("superadvancedcamera.apply_filter", icon="BRUSHES_ALL")
                        col.prop(settings, "Colorgrade_Filter_Mix")
                        col.prop(settings, "Colorgrade_Filter_Extension")
                        col.separator()
                        col.prop(settings, "Colorgrade_Presets_Sharpen")
                        col.prop(settings, "Colorgrade_Presets_Vibrance")
                        col.prop(settings, "Colorgrade_Presets_Saturation")
                        row = col.row(align=True)
                        row.prop(settings, "Colorgrade_Presets_HighlightTint")
                        row = col.row(align=True)
                        row.prop(settings, "Colorgrade_Presets_ShadowTint")

                    boxbox = boxcol.box()
                    template_boxtitle(settings, boxbox, "curves", "Curves", "FCURVE")
                    if settings.show_curves:
                        col = boxbox.column()

                        box = col.box()
                        boxcol_curves = box.column()
                        boxcol_curves.label(text="RGB Curves", icon="MOD_INSTANCE")
                        boxcol_curves.template_curve_mapping(rgb_curves_node, "mapping", type='COLOR')
                        boxcol_curves.prop(settings, "Colorgrade_Curves_RGB_Intensity")

                        box = col.box()
                        boxcol_curves = box.column()
                        boxcol_curves.label(text="HSV Curves", icon="MOD_OCEAN")
                        boxcol_curves.template_curve_mapping(hsv_curves_node, "mapping", type='HUE')
                        boxcol_curves.prop(settings, "Colorgrade_Curves_HSV_Intensity")

                    boxbox = boxcol.box()
                    template_boxtitle(settings, boxbox, "colorwheels", "Colorwheels", "MESH_CIRCLE")
                    if settings.show_colorwheels:
                        row = boxbox.row(align=True)

                        box_1 = row.box()
                        col_1 = box_1.column()
                        col_1.label(text="Shadows", icon="PMARKER")
                        col_1.template_color_picker(color_wheel_node_lift, "lift")
                        col_1.prop(settings, "Colorgrade_Colorwheel_Shadows_Brightness", text="Brightness")
                        col_1.prop(settings, "Colorgrade_Colorwheel_Shadows_Intensity", text="Intensity")

                        box_2 = row.box()
                        col_2 = box_2.column()
                        col_2.label(text="Midtones", icon="PMARKER_SEL")
                        col_2.template_color_picker(color_wheel_node_gamma, "gamma")
                        col_2.prop(settings, "Colorgrade_Colorwheel_Midtones_Brightness", text="Brightness")
                        col_2.prop(settings, "Colorgrade_Colorwheel_Midtones_Intensity", text="Intensity")

                        box_3 = row.box()
                        col_3 = box_3.column()
                        col_3.label(text="Highlights", icon="PMARKER_ACT")
                        col_3.template_color_picker(color_wheel_node_gain, "gain")
                        col_3.prop(settings, "Colorgrade_Colorwheel_Highlights_Brightness", text="Brightness")
                        col_3.prop(settings, "Colorgrade_Colorwheel_Highlights_Intensity", text="Intensity")

        boxmain = colmain.box()
        boxcol = boxmain.column()
        template_boxtitle(settings, boxcol, "effects", "Effects", "IMAGE")
        if settings.show_effects:
            
            found = False
            if not context.scene.use_nodes:
                boxcol.label(text="You need to enable the Compositor to use this feature!", icon="ERROR")
                boxcol.prop(context.scene, "use_nodes", text="Enable Compositor?", toggle=True)
            else:
                for node in bpy.context.scene.node_tree.nodes:
                    if node.name.startswith("Super Advanced Camera"):
                        found = True
                        break
                if not found:
                    boxcol.label(text="You need to initialize SAC to use this feature!", icon="ERROR")
                    boxcol.operator("superadvancedcamera.superadvancedcamerainit", text="Initialize Super Advanced Camera", icon="SHADERFX")
                else:

                    icon_checkbox = "CHECKBOX_HLT" if settings.Effects_Enable else "CHECKBOX_DEHLT"
                    boxcol.prop(settings, "Effects_Enable", text="Use Effects", toggle=True, icon=icon_checkbox)
                    boxcol.separator()

                    col = boxcol.column()
                    col.prop(settings, "Effects_Presets", text="Effect Presets")
                    colrow = col.row(align=True)
                    colrow.operator("superadvancedcamera.apply_effect_preset", icon="BRUSHES_ALL")
                    colrow.operator("superadvancedcamera.open_preset_folder", icon="FILE_FOLDER", text="")
                    row = col.row(align=True)
                    left = row.column(align=True)
                    left.scale_x = 1
                    left.scale_y = 8
                    left.operator("superadvancedcamera.previous_effect", text="", icon="TRIA_LEFT")
                    center = row.column()
                    center.template_icon_view(context.scene, "new_effect_type", show_labels=True, scale=8.0, scale_popup=4.0)
                    right = row.column(align=True)
                    right.scale_x = 1
                    right.scale_y = 8
                    right.operator("superadvancedcamera.next_effect", text="", icon="TRIA_RIGHT")

                    row = col.row()
                    row.template_list("SAC_UL_List", "", scene, "sac_effect_list", scene, "sac_effect_list_index")

                    col = row.column(align=True)
                    col.scale_x = 1  # Set a fixed width
                    col.operator("superadvancedcamera.add_effect", text="", icon='ADD')
                    col.operator("superadvancedcamera.remove_effect", text="", icon='REMOVE')
                    col.separator()
                    col.operator("superadvancedcamera.move_effect_up", text="", icon='TRIA_UP')
                    col.operator("superadvancedcamera.move_effect_down", text="", icon='TRIA_DOWN')

                    index = context.scene.sac_effect_list_index
                    item = context.scene.sac_effect_list[index] if context.scene.sac_effect_list else None

                    boxeffectproperties = boxcol.box()
                    col = boxeffectproperties.column()

                    if item is None:
                        col.label(text="No effect selected.")
                        col.active = False
                        return

                    boxeffectproperties.active = not item.mute

                    node_group_name = f".{item.EffectGroup}_{item.ID}"

                    col.label(text=f"Settings for: {item.name}.")
                    #region effectgroups
                    # Blur
                    if item.EffectGroup == "SAC_BLUR":
                        col.prop(settings, "Effects_Blur_Type")
                        row = col.row(align=True)
                        row.prop(settings, "Effects_Blur_Bokeh", toggle=True)
                        row.prop(settings, "Effects_Blur_Gamma", toggle=True)
                        col.prop(settings, "Effects_Blur_Relative", toggle=True)
                        row = col.row(align=True)
                        row.prop(settings, "Effects_Blur_AspectCorrection", expand=True)
                        if settings.Effects_Blur_Relative:
                            col.prop(settings, "Effects_Blur_FactorX")
                            col.prop(settings, "Effects_Blur_FactorY")
                        else:
                            row.enabled = False
                            col.prop(settings, "Effects_Blur_SizeX")
                            col.prop(settings, "Effects_Blur_SizeY")
                        col.prop(settings, "Effects_Blur_Extend")
                        col.prop(settings, "Effects_Blur_Size")

                    # Bokeh
                    elif item.EffectGroup == "SAC_BOKEH":
                        col.prop(settings, "Effects_Bokeh_MaxSize")
                        col.prop(settings, "Effects_Bokeh_Offset")
                        col.prop(settings, "Effects_Bokeh_Range")
                        col.separator()
                        col.label(text="Bokeh Type")
                        row_bokeh_type = col.row(align=True)
                        row_bokeh_type.prop(settings, "Effects_Bokeh_Type", expand=True)
                        col.separator(factor=0.5)

                        if settings.Effects_Bokeh_Type == "CAMERA":
                            row = col.row(align=True)
                            left = row.column(align=True)
                            left.scale_x = 1
                            left.scale_y = 8
                            left.operator("superadvancedcamera.previous_effect_bokeh", text="", icon="TRIA_LEFT")
                            center = row.column()
                            center.template_icon_view(context.scene, "new_bokeh_type", show_labels=True, scale=8.0, scale_popup=4.0)
                            right = row.column(align=True)
                            right.scale_x = 1
                            right.scale_y = 8
                            right.operator("superadvancedcamera.next_effect_bokeh", text="", icon="TRIA_RIGHT")

                            bokeh_type = context.scene.new_bokeh_type.split("_")
                            col_bokeh_description = col.column(align=True)
                            col_bokeh_description.active = False

                            row_bokeh_description = col_bokeh_description.row(align=True)
                            row_bokeh_description.label(text="Manufacturer:")
                            row_bokeh_description.label(text=bokeh_type[0])

                            row_bokeh_description = col_bokeh_description.row(align=True)
                            row_bokeh_description.label(text="Model:")
                            row_bokeh_description.label(text=f"{bokeh_type[1]} - {bokeh_type[3]} - {bokeh_type[2]}")

                            row_bokeh_description = col_bokeh_description.row(align=True)
                            row_bokeh_description.label(text="Aperture:")
                            row_bokeh_description.label(text=bokeh_type[4])

                            col_bokeh_description.label(text="Special thanks to Prof. Dr. Matt Gunn for the Bokeh textures.")
                            col.prop(settings, "Effects_Bokeh_Rotation")
                            col.separator()
                            col.operator("superadvancedcamera.apply_effect_bokeh", icon="SEQ_CHROMA_SCOPE")

                        elif settings.Effects_Bokeh_Type == "CUSTOM":
                            bokeh_image = bpy.data.node_groups[node_group_name].nodes["SAC Effects_Bokeh_Custom_Image"]
                            col.template_ID_preview(bokeh_image, "image", open="image.open")
                            col.prop(settings, "Effects_Bokeh_Rotation")

                        elif settings.Effects_Bokeh_Type == "PROCEDURAL":
                            col.prop(settings, "Effects_Bokeh_Procedural_Flaps")
                            col.prop(settings, "Effects_Bokeh_Procedural_Angle")
                            col.prop(settings, "Effects_Bokeh_Procedural_Rounding")
                            col.prop(settings, "Effects_Bokeh_Procedural_Catadioptric")
                            col.prop(settings, "Effects_Bokeh_Procedural_Shift")
                    # Chromatic Aberration
                    elif item.EffectGroup == "SAC_CHROMATICABERRATION":
                        col.prop(settings, "Effects_ChromaticAberration_Amount")
                    # Duotone
                    elif item.EffectGroup == "SAC_DUOTONE":
                        row = col.row(align=True)
                        row.prop(settings, "Effects_Duotone_Color1")
                        row = col.row(align=True)
                        row.prop(settings, "Effects_Duotone_Color2")
                        col.prop(settings, "Effects_Duotone_Blend")
                        col.prop(settings, "Effects_Duotone_Clamp")
                        row = col.row()
                        row.prop(settings, "Effects_Duotone_Color1_Start")
                        row.prop(settings, "Effects_Duotone_Color2_Start")
                        row = col.row()
                        row.prop(settings, "Effects_Duotone_Color1_Mix")
                        row.prop(settings, "Effects_Duotone_Color2_Mix")
                    # Emboss
                    elif item.EffectGroup == "SAC_EMBOSS":
                        col.prop(settings, "Effects_Emboss_Strength")
                    # Film Grain
                    elif item.EffectGroup == "SAC_FILMGRAIN":
                        col.prop(settings, "Filmgrain_strength")
                        col.prop(settings, "Filmgrain_dustproportion")
                        col.prop(settings, "Filmgrain_size")
                    # Fish Eye
                    elif item.EffectGroup == "SAC_FISHEYE":
                        col.prop(settings, "Effects_Fisheye")
                    # Fog Glow
                    elif item.EffectGroup == "SAC_FOGGLOW":
                        col.prop(settings, "Effects_FogGlow_Strength")
                        col.prop(settings, "Effects_FogGlow_Threshold")
                        col.prop(settings, "Effects_FogGlow_Size")
                    # Ghost
                    elif item.EffectGroup == "SAC_GHOST":
                        col.prop(settings, "Effects_Ghosts_Strength")
                        col.prop(settings, "Effects_Ghosts_Threshold")
                        col.prop(settings, "Effects_Ghosts_Count")
                        col.prop(settings, "Effects_Ghosts_Distortion")
                    # Gradient Map
                    elif item.EffectGroup == "SAC_GRADIENTMAP":
                        row = col.row(align=True)
                        left = row.column(align=True)
                        left.scale_x = 1
                        left.scale_y = 8
                        left.operator("superadvancedcamera.previous_gradient", text="", icon="TRIA_LEFT")
                        center = row.column()
                        center.template_icon_view(context.scene, "new_gradient_type", show_labels=True, scale=8.0, scale_popup=4.0)
                        right = row.column(align=True)
                        right.scale_x = 1
                        right.scale_y = 8
                        right.operator("superadvancedcamera.next_gradient", text="", icon="TRIA_RIGHT")
                        center_column = col.row(align=True)
                        center_column.label(text="Gradient Name:")
                        center_column.label(text=f"{context.scene.new_gradient_type}")
                        col.operator("superadvancedcamera.apply_gradient", icon="NODE_TEXTURE")
                        col.separator()
                        gradient_map_node = bpy.data.node_groups[node_group_name].nodes["SAC Effects_GradientMap"]
                        col.template_color_ramp(gradient_map_node, "color_ramp")
                        col.separator()
                        col.prop(settings, "Effects_GradientMap_blend")
                    # Halftone
                    elif item.EffectGroup == "SAC_HALFTONE":
                        col.prop(settings, "Effects_Halftone_value")
                        col.prop(settings, "Effects_Halftone_delta")
                        col.prop(settings, "Effects_Halftone_size")
                    # HDR
                    elif item.EffectGroup == "SAC_HDR":
                        col.prop(settings, "Effects_HDR_blend")
                        col.prop(settings, "Effects_HDR_exposure")
                        col.prop(settings, "Effects_HDR_sigma")
                        col.prop(settings, "Effects_HDR_delta")
                    # Infrared
                    elif item.EffectGroup == "SAC_INFRARED":
                        col.prop(settings, "Effects_Infrared_Blend")
                        col.prop(settings, "Effects_Infrared_Offset")
                    # ISO Noise
                    elif item.EffectGroup == "SAC_ISONOISE":
                        col.prop(settings, "ISO_strength")
                        col.prop(settings, "ISO_size")
                    # Mosaic
                    elif item.EffectGroup == "SAC_MOSAIC":
                        col.prop(settings, "Effects_Pixelate_PixelSize")
                    # Negative
                    elif item.EffectGroup == "SAC_NEGATIVE":
                        col.prop(settings, "Effects_Negative")
                    # Overlay
                    elif item.EffectGroup == "SAC_OVERLAY":
                        overlay_texture = bpy.data.node_groups[node_group_name].nodes["SAC Effects_Overlay_Texture"]
                        col.template_ID(overlay_texture, "image", open="image.open")
                        col.prop(settings, "Effects_Overlay_Strength")
                    # Perspective Shift
                    elif item.EffectGroup == "SAC_PERSPECTIVESHIFT":
                        col.prop(settings, "Effects_PerspectiveShift_Horizontal")
                        col.prop(settings, "Effects_PerspectiveShift_Vertical")
                    # Posterize
                    elif item.EffectGroup == "SAC_POSTERIZE":
                        col.prop(settings, "Effects_Posterize_Steps")
                    # Streaks
                    elif item.EffectGroup == "SAC_STREAKS":
                        col.prop(settings, "Effects_Streaks_Strength")
                        col.prop(settings, "Effects_Streaks_Threshold")
                        col.prop(settings, "Effects_Streaks_Count")
                        col.prop(settings, "Effects_Streaks_Length")
                        col.prop(settings, "Effects_Streaks_Fade")
                        col.prop(settings, "Effects_Streaks_Angle")
                        col.prop(settings, "Effects_Streaks_Distortion")
                    # Vignette
                    elif item.EffectGroup == "SAC_VIGNETTE":
                        col.prop(settings, "Effects_Vignette_Intensity")
                        col.prop(settings, "Effects_Vignette_Roundness")
                        col.prop(settings, "Effects_Vignette_Feather")
                        col.prop(settings, "Effects_Vignette_Midpoint")
                    # Warp
                    elif item.EffectGroup == "SAC_WARP":
                        col.prop(settings, "Effects_Warp")
                    # Error
                    else:
                        col.label(text="Oops, that's not supposed to happen.")
                        col.label(text=f"Effect: {item.EffectGroup} was selected.")
                        col.label(text="Please report this to us.")
                        col.operator("wm.url_open", text="Our Discord").url = "https://discord.gg/cnFdGQP"
                    #endregion effectgroups

                    boxpresets = boxcol.box()
                    colrow = boxpresets.row(align=True)
                    colrow.prop(settings, "Effects_Preset_Name", text="Custom Preset Name")
                    colrow.operator("superadvancedcamera.add_effect_preset", icon="ADD", text="")

classes = (
    SAC_PT_SAC_Panel,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")
