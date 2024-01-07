import bpy
import os
import math
from .SAC_Settings import SAC_Settings

def load_effect_previews():
    pcoll_effects = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons", "effect")

    for item_type, _, _ in SAC_Settings.effect_types:
        icon_path = os.path.join(my_icons_dir, f"{item_type}.webp")
        pcoll_effects.load(item_type, icon_path, 'IMAGE')

    return pcoll_effects

def load_bokeh_previews():
    pcoll_bokeh = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons", "bokeh")

    for item_type, _ in SAC_Settings.bokeh_types:
        icon_path = os.path.join(my_icons_dir, f"{item_type}.webp")
        pcoll_bokeh.load(item_type, icon_path, 'IMAGE')

    return pcoll_bokeh


def load_filter_previews():
    pcoll_filter = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons", "filter")

    for item_type, _ in SAC_Settings.filter_types:
        icon_path = os.path.join(my_icons_dir, f"{item_type}.webp")
        pcoll_filter.load(item_type, icon_path, 'IMAGE')

    return pcoll_filter


def load_gradient_previews():
    pcoll_gradient = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons", "gradient")

    for item_type, _ in SAC_Settings.gradient_types:
        icon_path = os.path.join(my_icons_dir, f"{item_type}.webp")
        pcoll_gradient.load(item_type, icon_path, 'IMAGE')

    return pcoll_gradient


def enum_previews_from_directory_effects(self, context):
    """Dynamic list of available previews."""
    enum_items = []

    if context is None:
        return enum_items

    pcoll_effects = bpy.types.Scene.effect_previews
    for i, (item_type, name, _) in enumerate(SAC_Settings.effect_types):
        icon = pcoll_effects[item_type].icon_id
        enum_items.append((item_type, name, "", icon, i))

    return enum_items


def enum_previews_from_directory_bokeh(self, context):
    """Dynamic list of available previews."""
    enum_items = []

    if context is None:
        return enum_items

    pcoll_bokeh = bpy.types.Scene.bokeh_previews
    for i, (item_type, name) in enumerate(SAC_Settings.bokeh_types):
        icon = pcoll_bokeh[item_type].icon_id
        enum_items.append((item_type, name, "", icon, i))

    return enum_items


def enum_previews_from_directory_filter(self, context):
    """Dynamic list of available previews."""
    enum_items = []

    if context is None:
        return enum_items

    pcoll_filter = bpy.types.Scene.filter_previews
    for i, (item_type, name) in enumerate(SAC_Settings.filter_types):
        icon = pcoll_filter[item_type].icon_id
        enum_items.append((item_type, name, "", icon, i))

    return enum_items


def enum_previews_from_directory_gradient(self, context):
    """Dynamic list of available previews."""
    enum_items = []

    if context is None:
        return enum_items

    pcoll_gradient = bpy.types.Scene.gradient_previews
    for i, (item_type, name) in enumerate(SAC_Settings.gradient_types):
        icon = pcoll_gradient[item_type].icon_id
        enum_items.append((item_type, name, "", icon, i))

    return enum_items


def load_image_once(image_path, image_name):
    image = bpy.data.images.get(image_name)
    if image is None:
        image = bpy.data.images.load(image_path)
    return image


def create_dot_texture():
    texture = bpy.data.textures.get(".SAC Dot Screen")
    if texture is None:
        texture = bpy.data.textures.new(name=".SAC Dot Screen", type='MAGIC')
    texture.noise_depth = 1  # Depth
    texture.turbulence = 6.0  # Turbulence
    texture.use_color_ramp = True
    texture.color_ramp.interpolation = 'CONSTANT'
    texture.color_ramp.elements[1].position = 0.65


def mute_update(self, context):
    bpy.data.node_groups[".SAC Effects"].nodes[f"{self.EffectGroup}_{self.ID}"].mute = self.mute


def active_effect_update(self, context):
    settings = context.scene.sac_settings
    try:
        item = context.scene.sac_effect_list[self.sac_effect_list_index]
    except IndexError:
        return
    node_name = f"{item.EffectGroup}_{item.ID}"
    node_group_name = f".{node_name}"
    node_group = bpy.data.node_groups[node_group_name]
    # Blur
    if item.EffectGroup == "SAC_BLUR":
        settings.Effects_Blur_Type = node_group.nodes["SAC Effects_Blur"].filter_type
        settings.Effects_Blur_Bokeh = node_group.nodes["SAC Effects_Blur"].use_bokeh
        settings.Effects_Blur_Gamma = node_group.nodes["SAC Effects_Blur"].use_gamma_correction
        settings.Effects_Blur_Relative = node_group.nodes["SAC Effects_Blur"].use_relative
        settings.Effects_Blur_AspectCorrection = node_group.nodes["SAC Effects_Blur"].aspect_correction
        settings.Effects_Blur_FactorX = node_group.nodes["SAC Effects_Blur"].factor_x
        settings.Effects_Blur_FactorY = node_group.nodes["SAC Effects_Blur"].factor_y
        settings.Effects_Blur_SizeX = node_group.nodes["SAC Effects_Blur"].size_x
        settings.Effects_Blur_SizeY = node_group.nodes["SAC Effects_Blur"].size_y
        settings.Effects_Blur_Extend = node_group.nodes["SAC Effects_Blur"].use_extended_bounds
        settings.Effects_Blur_Size = node_group.nodes["SAC Effects_Blur"].inputs[1].default_value
    # Bokeh
    if item.EffectGroup == "SAC_BOKEH":
        settings.Effects_Bokeh_MaxSize = node_group.nodes["SAC Effects_Bokeh_Blur"].blur_max
        settings.Effects_Bokeh_Range = node_group.nodes["SAC Effects_Bokeh_Range"].inputs[1].default_value
        settings.Effects_Bokeh_Offset = node_group.nodes["SAC Effects_Bokeh_Offset"].inputs[1].default_value
        settings.Effects_Bokeh_Rotation = node_group.nodes["SAC Effects_Bokeh_Rotation"].inputs[1].default_value
        settings.Effects_Bokeh_Procedural_Flaps = node_group.nodes["SAC Effects_Bokeh_Procedural"].flaps
        settings.Effects_Bokeh_Procedural_Angle = node_group.nodes["SAC Effects_Bokeh_Procedural"].angle
        settings.Effects_Bokeh_Procedural_Rounding = node_group.nodes["SAC Effects_Bokeh_Procedural"].rounding
        settings.Effects_Bokeh_Procedural_Catadioptric = node_group.nodes["SAC Effects_Bokeh_Procedural"].catadioptric
        settings.Effects_Bokeh_Procedural_Shift = node_group.nodes["SAC Effects_Bokeh_Procedural"].shift

        if node_group.nodes["SAC Effects_Bokeh_Switch"].check == True:
            settings.Effects_Bokeh_Type = "PROCEDURAL"
        else:
            if node_group.nodes["SAC Effects_Bokeh_ImageSwitch"].check == True:
                settings.Effects_Bokeh_Type = "CUSTOM"
            else:
                settings.Effects_Bokeh_Type = "CAMERA"
    # Chromatic Aberration
    elif item.EffectGroup == "SAC_CHROMATICABERRATION":
        settings.Effects_ChromaticAberration_Amount = node_group.nodes["SAC Effects_ChromaticAberration"].inputs[2].default_value
    # Duotone
    elif item.EffectGroup == "SAC_DUOTONE":
        # Color 1
        settings.Effects_Duotone_Color1[0] = node_group.nodes["SAC Effects_Duotone_Colors"].inputs[1].default_value[0]
        settings.Effects_Duotone_Color1[1] = node_group.nodes["SAC Effects_Duotone_Colors"].inputs[1].default_value[1]
        settings.Effects_Duotone_Color1[2] = node_group.nodes["SAC Effects_Duotone_Colors"].inputs[1].default_value[2]
        # Color 2
        settings.Effects_Duotone_Color2[0] = node_group.nodes["SAC Effects_Duotone_Colors"].inputs[2].default_value[0]
        settings.Effects_Duotone_Color2[1] = node_group.nodes["SAC Effects_Duotone_Colors"].inputs[2].default_value[1]
        settings.Effects_Duotone_Color2[2] = node_group.nodes["SAC Effects_Duotone_Colors"].inputs[2].default_value[2]
        # Map Range
        settings.Effects_Duotone_Clamp = node_group.nodes["SAC Effects_Duotone_MapRange"].use_clamp
        settings.Effects_Duotone_Color1_Start = node_group.nodes["SAC Effects_Duotone_MapRange"].inputs[1].default_value
        settings.Effects_Duotone_Color2_Start = node_group.nodes["SAC Effects_Duotone_MapRange"].inputs[2].default_value
        settings.Effects_Duotone_Color1_Mix = node_group.nodes["SAC Effects_Duotone_MapRange"].inputs[3].default_value
        settings.Effects_Duotone_Color2_Mix = node_group.nodes["SAC Effects_Duotone_MapRange"].inputs[4].default_value
        # Blend
        settings.Effects_Duotone_Blend = node_group.nodes["SAC Effects_Duotone_Blend"].inputs[0].default_value
    # Emboss
    elif item.EffectGroup == "SAC_EMBOSS":
        settings.Effects_Emboss_Strength = node_group.nodes["SAC Effects_Emboss"].inputs[0].default_value
    # Film Grain
    elif item.EffectGroup == "SAC_FILMGRAIN":
        settings.Filmgrain_strength = node_group.nodes["SAC Effects_FilmGrain_Strength"].inputs[0].default_value
        settings.Filmgrain_dustproportion = node_group.nodes["SAC Effects_FilmGrain_Blur"].sigma_color
        settings.Filmgrain_size = node_group.nodes["SAC Effects_FilmGrain_Blur"].iterations
    # Fish Eye
    elif item.EffectGroup == "SAC_FISHEYE":
        settings.Effects_Fisheye = node_group.nodes["SAC Effects_Fisheye"].inputs[1].default_value
    # Fog Glow
    elif item.EffectGroup == "SAC_FOGGLOW":
        settings.Effects_FogGlow_Strength = node_group.nodes["SAC Effects_FogGlowStrength"].inputs[0].default_value
        settings.Effects_FogGlow_Threshold = node_group.nodes["SAC Effects_FogGlow"].threshold
        settings.Effects_FogGlow_Size = node_group.nodes["SAC Effects_FogGlow"].size
    # Ghost
    elif item.EffectGroup == "SAC_GHOST":
        settings.Effects_Ghosts_Strength = node_group.nodes["SAC Effects_GhostsStrength"].inputs[0].default_value
        settings.Effects_Ghosts_Threshold = node_group.nodes["SAC Effects_Ghosts"].threshold
        settings.Effects_Ghosts_Count = node_group.nodes["SAC Effects_Ghosts"].iterations
        settings.Effects_Ghosts_Distortion = node_group.nodes["SAC Effects_Ghosts"].color_modulation
    # Gradient Map
    elif item.EffectGroup == "SAC_GRADIENTMAP":
        settings.Effects_GradientMap_blend = node_group.nodes["SAC Effects_GradientMap_Mix"].inputs[0].default_value
    # Halftone
    elif item.EffectGroup == "SAC_HALFTONE":
        settings.Effects_Halftone_value = node_group.nodes["SAC Effects_Halftone_Value"].outputs[0].default_value
        settings.Effects_Halftone_delta = node_group.nodes["SAC Effects_Halftone_Delta"].outputs[0].default_value
        settings.Effects_Halftone_size = node_group.nodes["SAC Effects_Halftone_SizeSave"].outputs[0].default_value
    # HDR
    elif item.EffectGroup == "SAC_HDR":
        settings.Effects_HDR_blend = node_group.nodes["SAC Effects_HDR_Mix"].inputs[0].default_value
        settings.Effects_HDR_exposure = node_group.nodes["SAC Effects_HDR_Exposure"].inputs[1].default_value
        settings.Effects_HDR_sigma = node_group.nodes["SAC Effects_HDR_Sigma"].inputs[0].default_value
        settings.Effects_HDR_delta = node_group.nodes["SAC Effects_HDR_Over"].inputs["Exposure"].default_value
    # Infrared
    elif item.EffectGroup == "SAC_INFRARED":
        settings.Effects_Infrared_Blend = node_group.nodes["SAC Effects_Infrared_Mix"].inputs[0].default_value
        settings.Effects_Infrared_Offset = node_group.nodes["SAC Effects_Infrared_Add"].inputs[1].default_value
    # ISO Noise
    elif item.EffectGroup == "SAC_ISONOISE":
        settings.ISO_strength = node_group.nodes["SAC Effects_ISO_Add"].inputs[0].default_value
        settings.ISO_size = node_group.nodes["SAC Effects_ISO_Despeckle"].inputs[0].default_value
    # Mosaic
    elif item.EffectGroup == "SAC_MOSAIC":
        settings.Effects_Pixelate_PixelSize = node_group.nodes["SAC Effects_Pixelate_Size"].inputs[0].default_value
    # Negative
    elif item.EffectGroup == "SAC_NEGATIVE":
        settings.Effects_Negative = node_group.nodes["SAC Effects_Negative"].inputs[0].default_value
    # Overlay
    elif item.EffectGroup == "SAC_OVERLAY":
        settings.Effects_Overlay_Strength = node_group.nodes["SAC Effects_Overlay"].inputs[0].default_value
    # Perspective Shift
    elif item.EffectGroup == "SAC_PERSPECTIVESHIFT":
        if node_group.nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[1].default_value[0] > 0:
            settings.Effects_PerspectiveShift_Horizontal = node_group.nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[1].default_value[0] * 2
        else:
            settings.Effects_PerspectiveShift_Horizontal = -node_group.nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[3].default_value[0] * 2

        if node_group.nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[3].default_value[1] > 0:
            settings.Effects_PerspectiveShift_Vertical = node_group.nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[3].default_value[1] * 2
        else:
            settings.Effects_PerspectiveShift_Vertical = -node_group.nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[4].default_value[1] * 2
    # Posterize
    elif item.EffectGroup == "SAC_POSTERIZE":
        settings.Effects_Posterize_Steps = node_group.nodes["SAC Effects_Posterize"].inputs[1].default_value
    # Streaks
    elif item.EffectGroup == "SAC_STREAKS":
        settings.Effects_Streaks_Strength = node_group.nodes["SAC Effects_StreaksStrength"].inputs[0].default_value
        settings.Effects_Streaks_Threshold = node_group.nodes["SAC Effects_Streaks"].threshold
        settings.Effects_Streaks_Count = node_group.nodes["SAC Effects_Streaks"].streaks
        settings.Effects_Streaks_Length = node_group.nodes["SAC Effects_Streaks"].iterations
        settings.Effects_Streaks_Fade = node_group.nodes["SAC Effects_Streaks"].fade
        settings.Effects_Streaks_Angle = node_group.nodes["SAC Effects_Streaks"].angle_offset
        settings.Effects_Streaks_Distortion = node_group.nodes["SAC Effects_Streaks"].color_modulation
    # Vignette
    elif item.EffectGroup == "SAC_VIGNETTE":
        settings.Effects_Vignette_Intensity = node_group.nodes["SAC Effects_Viginette_Intensity"].inputs[0].default_value
        settings.Effects_Vignette_Roundness = node_group.nodes["SAC Effects_Viginette_Roundness"].inputs[0].default_value
        settings.Effects_Vignette_Feather = node_group.nodes["SAC Effects_Viginette_Directional_Blur"].zoom
        settings.Effects_Vignette_Midpoint = node_group.nodes["SAC Effects_Viginette_Midpoint"].inputs[0].default_value
    # Warp
    elif item.EffectGroup == "SAC_WARP":
        settings.Effects_Warp = node_group.nodes["SAC Effects_Warp"].zoom


def frames_to_time(frames, fps):
    frames_abs = math.ceil(abs(frames))
    total_seconds = frames_abs // fps
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    excess_frames = int(frames_abs % fps)

    if frames >= 0:
        return f"{minutes:02}m:{seconds:02}s+{excess_frames:02}f"
    return f"-{minutes:02}m:{seconds:02}s+{excess_frames:02}f"


def hex_to_rgb(value):
    value = value.lstrip('#')
    r = round(int(value[0:2], 16)/255, 3)
    g = round(int(value[2:4], 16)/255, 3)
    b = round(int(value[4:6], 16)/255, 3)
    return (r, g, b, 1.0)

def get_gradient(gradient):
    if gradient == "Platinum":
        gradient_tuple = (
            (0.0, "080706"),
            (1.0, "fff9f2")
        )
    elif gradient == "Selenium 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.1, "413f3e"),
            (0.25, "77736a"),
            (0.75, "bebbb4"),
            (1.0, "ffffff")
        )
    elif gradient == "Selenium 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.1, "1b1a1b"),
            (0.25, "47443f"),
            (0.75, "d6d3cf"),
            (1.0, "ffffff")
        )
    elif gradient == "Sepia 1":
        gradient_tuple = (
            (0.0, "000000"),
            (0.2, "3b2410"),
            (0.5, "7f7d7c"),
            (0.9, "f4dfc5"),
            (1.0, "ffffff")
        )
    elif gradient == "Sepia 2":
        gradient_tuple = (
            (0.0, "080808"),
            (0.15, "382a1b"),
            (0.5, "7b7367"),
            (0.9, "eddec5"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Sepia 3":
        gradient_tuple = (
            (0.0, "030303"),
            (0.1, "382a1b"),
            (0.5, "857c6e"),
            (0.9, "eddec5"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Sepia 4":
        gradient_tuple = (
            (0.0, "080808"),
            (0.1, "383127"),
            (0.5, "978061"),
            (0.85, "dfd0b8"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Sepia 5":
        gradient_tuple = (
            (0.0, "030303"),
            (0.1, "383735"),
            (0.5, "8f7254"),
            (0.9, "fac893"),
            (1.0, "f5ede4")
        )
    elif gradient == "Sepia 6":
        gradient_tuple = (
            (0.0, "000000"),
            (0.25, "543318"),
            (1.0, "c08d4e")
        )
    elif gradient == "Sepia Highlights 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.2, "333333"),
            (0.5, "808080"),
            (1.0, "808080")
        )
    elif gradient == "Sepia Highlights 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.5, "808080"),
            (0.9, "eddec5"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Sepia Midtones":
        gradient_tuple = (
            (0.0, "030303"),
            (0.2, "343434"),
            (0.35, "5a5a5a"),
            (0.5, "a38c73"),
            (0.7, "bcb3a8"),
            (0.85, "dadada"),
            (1.0, "ffffff")
        )
    elif gradient == "Gold 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "462f1f"),
            (0.25, "5b3c21"),
            (0.5, "a88347"),
            (0.75, "d9b675"),
            (0.98, "fcf6d0"),
            (1.0, "ffffff")
        )
    elif gradient == "Gold 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "161512"),
            (0.25, "5a3b02"),
            (0.5, "997b3f"),
            (0.75, "d9bd81"),
            (0.98, "f3edc9"),
            (1.0, "ffffff")
        )
    elif gradient == "Blue 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "131818"),
            (0.25, "2e597b"),
            (0.5, "4d90b4"),
            (0.75, "94cef1"),
            (0.98, "f2ffff"),
            (1.0, "ffffff")
        )
    elif gradient == "Blue 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "0f1919"),
            (0.25, "2a5157"),
            (0.5, "558586"),
            (0.75, "a4cdcb"),
            (0.98, "e0faf9"),
            (1.0, "ffffff")
        )
    elif gradient == "Cyanotype":
        gradient_tuple = (
            (0.0, "030303"),
            (0.1, "0d2f4b"),
            (0.25, "144a68"),
            (0.5, "4b90a5"),
            (0.75, "92cfd2"),
            (0.98, "e0f7eb"),
            (1.0, "ffffff")
        )
    elif gradient == "Copper 1":
        gradient_tuple = (
            (0.0, "130a09"),
            (0.25, "583c39"),
            (0.5, "94726a"),
            (0.75, "d0bab0"),
            (1.0, "f5e8e0")
        )
    elif gradient == "Copper 2":
        gradient_tuple = (
            (0.0, "130e18"),
            (0.25, "663844"),
            (0.5, "a66c72"),
            (0.75, "e9b1b0"),
            (1.0, "fdcdcb")
        )
    elif gradient == "Sepia-Selenium 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "0e0e16"),
            (0.2, "413f3e"),
            (0.5, "7f7d7c"),
            (0.9, "f4dfc5"),
            (1.0, "ffffff")
        )
    elif gradient == "Sepia-Selenium 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.05, "0e0e16"),
            (0.3, "413f3e"),
            (0.5, "978061"),
            (0.85, "978061"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Sepia-Selenium 3":
        gradient_tuple = (
            (0.0, "030303"),
            (0.05, "0c0b0b"),
            (0.3, "3a3732"),
            (0.5, "77736a"),
            (0.85, "dfd0b8"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Sepia-Cyan":
        gradient_tuple = (
            (0.0, "030303"),
            (0.1, "0b2840"),
            (0.3, "144a68"),
            (0.5, "808080"),
            (0.75, "cfaa86"),
            (0.85, "dfd0b8"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Sepia-Blue 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.05, "131818"),
            (0.15, "193042"),
            (0.5, "808080"),
            (0.75, "cfaa86"),
            (0.85, "dfd0b8"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Sepia-Blue 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.05, "131818"),
            (0.3, "2a5157"),
            (0.5, "808080"),
            (0.75, "cfaa86"),
            (0.9, "dfd0b8"),
            (1.0, "fdfdfe")
        )
    elif gradient == "Gold-Sepia":
        gradient_tuple = (
            (0.0, "030303"),
            (0.03, "3d2410"),
            (0.25, "583b1c"),
            (0.5, "828282"),
            (0.75, "d9bd81"),
            (1.0, "f3edc9")
        )
    elif gradient == "Gold-Selenium 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.03, "0c0b0b"),
            (0.25, "3a3732"),
            (0.5, "828282"),
            (0.75, "d9bd81"),
            (1.0, "f3edc9")
        )
    elif gradient == "Gold-Selenium 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.03, "0e0e16"),
            (0.25, "413f3e"),
            (0.5, "77736a"),
            (0.75, "d9b675"),
            (1.0, "fcf6d0")
        )
    elif gradient == "Gold-Copper":
        gradient_tuple = (
            (0.0, "030303"),
            (0.03, "130e18"),
            (0.25, "663844"),
            (0.5, "828282"),
            (0.75, "d9bd81"),
            (1.0, "f3edc9")
        )
    elif gradient == "Gold-Blue":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "131818"),
            (0.25, "2e597b"),
            (0.5, "808080"),
            (0.75, "d9bd81"),
            (0.98, "f3edc9"),
            (1.0, "ffffff")
        )
    elif gradient == "Blue-Selenium 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.05, "0c0b0b"),
            (0.33, "5e5b57"),
            (0.5, "4d90b4"),
            (0.85, "94cef1"),
            (0.98, "f2ffff"),
            (1.0, "fcfcfc")
        )
    elif gradient == "Blue-Selenium 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.03, "0c0b0b"),
            (0.25, "47443f"),
            (0.5, "827e76"),
            (0.75, "94cef1"),
            (0.98, "f2ffff"),
            (1.0, "fcfcfc")
        )
    elif gradient == "Cyan-Selenium":
        gradient_tuple = (
            (0.0, "030303"),
            (0.03, "0c0b0b"),
            (0.3, "3a3732"),
            (0.5, "77736a"),
            (0.85, "92b9cc"),
            (0.98, "cfe0e8"),
            (1.0, "fcfcfc")
        )
    elif gradient == "Cyan-Sepia":
        gradient_tuple = (
            (0.0, "000000"),
            (0.1, "3b2410"),
            (0.5, "7f7d7c"),
            (0.7, "92b9cc"),
            (0.98, "e0f7eb"),
            (1.0, "fcfcfc")
        )
    elif gradient == "Copper-Sepia":
        gradient_tuple = (
            (0.0, "000000"),
            (0.1, "3b2410"),
            (0.5, "7f7d7c"),
            (0.7, "92b9cc"),
            (0.98, "e0f7eb"),
            (1.0, "fcfcfc")
        )
    elif gradient == "Cobalt-Iron 1":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "03151b"),
            (0.25, "225059"),
            (0.5, "59919f"),
            (0.75, "bec1c4"),
            (0.96, "fdf4ef"),
            (1.0, "ffffff")
        )
    elif gradient == "Cobalt-Iron 2":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "041320"),
            (0.25, "34464f"),
            (0.5, "8a7f89"),
            (0.75, "c6bcc1"),
            (0.96, "fbfbf9"),
            (1.0, "ffffff")
        )
    elif gradient == "Cobalt-Iron 3":
        gradient_tuple = (
            (0.0, "030303"),
            (0.02, "07151d"),
            (0.25, "284d56"),
            (0.5, "6e8491"),
            (0.75, "c7bcc4"),
            (0.96, "f5eae9"),
            (1.0, "ffffff")
        )
    elif gradient == "Hard":
        gradient_tuple = (
            (0.45, "080706"),
            (0.55, "fff9f2")
        )
    elif gradient == "Skies":
        gradient_tuple = (
            (0.0, "565e6c"),
            (1.0, "58b4c1")
        )

    return (gradient_tuple)

def get_filter(filter):
    if filter == "Default":
        filter_tuple = (
            [
                [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
            ]
        )

    # BW

    elif filter == "1920":
        filter_tuple = (
            [
                [0.0667, 0.0353, 0.0079, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0667, 0.0353, 0.0079, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0667, 0.0353, 0.0079, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.8196, 0.7098, 0.6, 0.498, 0.3922, 0.2863, 0.1765, 0.0706, 0.0, 0.0, 0.0],
                [0.8196, 0.7098, 0.6, 0.498, 0.3922, 0.2863, 0.1765, 0.0706, 0.0, 0.0, 0.0],
                [0.8196, 0.7098, 0.6, 0.498, 0.3922, 0.2863, 0.1765, 0.0706, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ]
        )

    elif filter == "Grayed":
        filter_tuple = (
            [
                [0.2118, 0.1922, 0.1687, 0.1491, 0.1294, 0.1059, 0.0824, 0.0627, 0.0431, 0.0196, 0.0],
                [0.2118, 0.1922, 0.1687, 0.1491, 0.1294, 0.1059, 0.0824, 0.0627, 0.0431, 0.0196, 0.0],
                [0.2118, 0.1922, 0.1687, 0.1491, 0.1294, 0.1059, 0.0824, 0.0627, 0.0431, 0.0196, 0.0]
            ], [
                [0.7137, 0.6392, 0.5686, 0.498, 0.4275, 0.3569, 0.2824, 0.2157, 0.1412, 0.0706, 0.0],
                [0.7137, 0.6392, 0.5686, 0.498, 0.4275, 0.3569, 0.2824, 0.2157, 0.1412, 0.0706, 0.0],
                [0.7137, 0.6392, 0.5686, 0.498, 0.4275, 0.3569, 0.2824, 0.2157, 0.1412, 0.0706, 0.0]
            ], [
                [0.0706, 0.0667, 0.0589, 0.051, 0.0431, 0.0353, 0.0314, 0.0196, 0.0157, 0.0039, 0.0],
                [0.0706, 0.0667, 0.0589, 0.051, 0.0431, 0.0353, 0.0314, 0.0196, 0.0157, 0.0039, 0.0],
                [0.0706, 0.0667, 0.0589, 0.051, 0.0431, 0.0353, 0.0314, 0.0196, 0.0157, 0.0039, 0.0]
            ]
        )

    elif filter == "Dusty":
        filter_tuple = (
            [
                [0.3491, 0.3059, 0.2628, 0.2236, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118],
                [0.3491, 0.3059, 0.2628, 0.2236, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118],
                [0.3491, 0.3059, 0.2628, 0.2236, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118]
            ], [
                [0.349, 0.3059, 0.2627, 0.2235, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118],
                [0.349, 0.3059, 0.2627, 0.2235, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118],
                [0.349, 0.3059, 0.2627, 0.2235, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118]
            ], [
                [0.349, 0.3059, 0.2627, 0.2235, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118],
                [0.349, 0.3059, 0.2627, 0.2235, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118],
                [0.349, 0.3059, 0.2627, 0.2235, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118, 0.2118]
            ]
        )

    elif filter == "Litho":
        filter_tuple = (
            [
                [0.6353, 0.5373, 0.451, 0.3725, 0.3137, 0.2745, 0.2353, 0.2039, 0.1647, 0.1255, 0.0902],
                [0.5765, 0.4863, 0.4039, 0.3294, 0.2706, 0.2275, 0.1843, 0.149, 0.1098, 0.0706, 0.0392],
                [0.5765, 0.4863, 0.4039, 0.3294, 0.2706, 0.2275, 0.1843, 0.149, 0.1098, 0.0706, 0.0392]
            ], [
                [0.8902, 0.8353, 0.7529, 0.6392, 0.5059, 0.3882, 0.3059, 0.251, 0.2, 0.1451, 0.0902],
                [0.8471, 0.7765, 0.6902, 0.5765, 0.451, 0.3412, 0.2588, 0.2, 0.1451, 0.0863, 0.0392],
                [0.8471, 0.7765, 0.6902, 0.5765, 0.451, 0.3412, 0.2588, 0.2, 0.1451, 0.0863, 0.0392]
            ], [
                [0.1725, 0.1647, 0.1529, 0.1451, 0.1373, 0.1255, 0.1216, 0.1098, 0.1059, 0.0941, 0.0902],
                [0.1176, 0.1098, 0.098, 0.0902, 0.0784, 0.0706, 0.0667, 0.0588, 0.0549, 0.0431, 0.0392],
                [0.1176, 0.1098, 0.098, 0.0902, 0.0824, 0.0745, 0.0667, 0.0588, 0.0549, 0.0431, 0.0392]
            ]
        )

    elif filter == "Sepia":
        filter_tuple = (
            [
                [0.1373, 0.1334, 0.1295, 0.1255, 0.1255, 0.1216, 0.1216, 0.1216, 0.1216, 0.1176, 0.1176],
                [0.0824, 0.0785, 0.0745, 0.0745, 0.0706, 0.0706, 0.0706, 0.0667, 0.0667, 0.0667, 0.0667],
                [0.0549, 0.051, 0.0471, 0.0471, 0.0471, 0.0432, 0.0431, 0.0431, 0.0431, 0.0431, 0.0431]
            ], [
                [0.6, 0.5176, 0.4353, 0.3569, 0.2941, 0.2275, 0.1765, 0.149, 0.1294, 0.1216, 0.1176],
                [0.5216, 0.4314, 0.3412, 0.2667, 0.2039, 0.1529, 0.1137, 0.0902, 0.0745, 0.0706, 0.0667],
                [0.4824, 0.3843, 0.2941, 0.2196, 0.1608, 0.1176, 0.0824, 0.0627, 0.051, 0.0431, 0.0431]
            ], [
                [0.7529, 0.6824, 0.5961, 0.498, 0.3961, 0.3098, 0.2275, 0.1725, 0.1373, 0.1216, 0.1176],
                [0.7059, 0.6196, 0.5176, 0.4078, 0.302, 0.2196, 0.1529, 0.1059, 0.0824, 0.0706, 0.0667],
                [0.6745, 0.5843, 0.4745, 0.3647, 0.2549, 0.1765, 0.1176, 0.0745, 0.0549, 0.0431, 0.0431]
            ]
        )

    elif filter == "Weathered":
        filter_tuple = (
            [
                [0.0667, 0.0471, 0.0275, 0.0196, 0.0157, 0.0118, 0.0078, 0.0039, 0.0039, 0.0, 0.0],
                [0.0667, 0.0471, 0.0275, 0.0196, 0.0157, 0.0118, 0.0078, 0.0039, 0.0039, 0.0, 0.0],
                [0.0667, 0.0471, 0.0275, 0.0196, 0.0157, 0.0118, 0.0078, 0.0039, 0.0039, 0.0, 0.0]
            ], [
                [0.3608, 0.298, 0.2471, 0.2, 0.149, 0.098, 0.0471, 0.0157, 0.0118, 0.0039, 0.0],
                [0.3569, 0.298, 0.2471, 0.2, 0.149, 0.098, 0.0471, 0.0157, 0.0118, 0.0039, 0.0],
                [0.3529, 0.298, 0.2471, 0.2, 0.149, 0.098, 0.0471, 0.0157, 0.0118, 0.0039, 0.0]
            ], [
                [0.5451, 0.4353, 0.3412, 0.2745, 0.2157, 0.1529, 0.0902, 0.0353, 0.0157, 0.0039, 0.0],
                [0.5216, 0.4235, 0.3412, 0.2745, 0.2157, 0.1529, 0.0902, 0.0353, 0.0157, 0.0039, 0.0],
                [0.4902, 0.4118, 0.3373, 0.2745, 0.2157, 0.1529, 0.0902, 0.0353, 0.0157, 0.0039, 0.0]
            ]
        )

    elif filter == "Steel":
        filter_tuple = (
            [
                [0.4196, 0.3373, 0.2785, 0.2471, 0.2118, 0.1804, 0.1529, 0.1294, 0.1098, 0.0941, 0.0824],
                [0.4824, 0.4079, 0.353, 0.3255, 0.302, 0.2745, 0.251, 0.2275, 0.2, 0.1843, 0.1725],
                [0.5843, 0.5216, 0.4863, 0.4667, 0.451, 0.4353, 0.4157, 0.3922, 0.3608, 0.3412, 0.3255]
            ], [
                [0.3334, 0.2824, 0.251, 0.2196, 0.1922, 0.1647, 0.1412, 0.1255, 0.1059, 0.0902, 0.0824],
                [0.404, 0.3569, 0.3295, 0.3059, 0.2863, 0.2627, 0.2392, 0.2196, 0.2, 0.1843, 0.1725],
                [0.5216, 0.4863, 0.4706, 0.4549, 0.4392, 0.4235, 0.4039, 0.3804, 0.3569, 0.3412, 0.3255]
            ], [
                [0.2863, 0.2549, 0.2275, 0.2039, 0.1765, 0.1569, 0.1333, 0.1176, 0.1059, 0.0902, 0.0824],
                [0.3608, 0.3334, 0.3098, 0.2941, 0.2745, 0.251, 0.2314, 0.2157, 0.1961, 0.1804, 0.1725],
                [0.4863, 0.4745, 0.4588, 0.4471, 0.4314, 0.4157, 0.3961, 0.3765, 0.3569, 0.3373, 0.3255]
            ]
        )

    # Vintage

    elif filter == "Ancient":
        filter_tuple = (
            [
                [0.5765, 0.5137, 0.4588, 0.4078, 0.3569, 0.3059, 0.2549, 0.2039, 0.1529, 0.0941, 0.0275],
                [0.102, 0.102, 0.0942, 0.0863, 0.0784, 0.0706, 0.0627, 0.0549, 0.051, 0.0392, 0.0314],
                [0.0667, 0.0628, 0.0549, 0.051, 0.0431, 0.0392, 0.0314, 0.0235, 0.0196, 0.0157, 0.0196]
            ], [
                [0.0039, 0.0863, 0.1647, 0.1961, 0.1922, 0.1686, 0.1412, 0.1098, 0.0863, 0.0549, 0.0275],
                [0.7922, 0.6745, 0.5686, 0.4824, 0.4039, 0.3373, 0.2745, 0.2196, 0.1569, 0.098, 0.0314],
                [0.1804, 0.1882, 0.1804, 0.1686, 0.149, 0.1216, 0.098, 0.0745, 0.051, 0.0314, 0.0196]
            ], [
                [0.2118, 0.2078, 0.1922, 0.1725, 0.149, 0.1216, 0.102, 0.0824, 0.0667, 0.051, 0.0275],
                [0.1216, 0.1098, 0.098, 0.0902, 0.0784, 0.0706, 0.0667, 0.0549, 0.0471, 0.0392, 0.0314],
                [0.5608, 0.4863, 0.4275, 0.3804, 0.3373, 0.2902, 0.2431, 0.1922, 0.1373, 0.0784, 0.0196]
            ]
        )

    elif filter == "Polaroid":
        filter_tuple = (
            [
                [0.9725, 0.8824, 0.7843, 0.6745, 0.5569, 0.4471, 0.349, 0.2706, 0.2, 0.1373, 0.0549],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0157, 0.0314, 0.0314, 0.0392, 0.0392, 0.0353],
                [0.2588, 0.251, 0.2353, 0.2275, 0.2118, 0.2, 0.1843, 0.1725, 0.1608, 0.1451, 0.1373]
            ], [
                [0.4353, 0.2353, 0.0196, 0.0, 0.0, 0.0, 0.0314, 0.0784, 0.0824, 0.0745, 0.0549],
                [0.8353, 0.8078, 0.7608, 0.6941, 0.6039, 0.4863, 0.3529, 0.2431, 0.1569, 0.0941, 0.0353],
                [0.3686, 0.3412, 0.3137, 0.298, 0.2824, 0.2706, 0.2549, 0.2314, 0.2039, 0.1725, 0.1373]
            ], [
                [0.349, 0.2431, 0.1373, 0.0314, 0.0078, 0.0, 0.0, 0.0078, 0.0078, 0.0275, 0.0549],
                [0.0, 0.0196, 0.0157, 0.0353, 0.0314, 0.0314, 0.0353, 0.0392, 0.0392, 0.0353, 0.0353],
                [0.7176, 0.702, 0.6784, 0.6431, 0.6, 0.549, 0.4863, 0.4196, 0.3373, 0.251, 0.1373]
            ]
        )

    elif filter == "Sunny 70s":
        filter_tuple = (
            [
                [0.898, 0.8863, 0.8667, 0.8392, 0.8, 0.7294, 0.6157, 0.4902, 0.349, 0.2588, 0.2549],
                [0.204, 0.204, 0.204, 0.204, 0.204, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039],
                [0.204, 0.204, 0.204, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039]
            ], [
                [0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549],
                [0.9412, 0.9255, 0.8941, 0.8471, 0.7569, 0.6431, 0.5098, 0.3686, 0.2549, 0.2039, 0.2039],
                [0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039]
            ], [
                [0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549, 0.2549],
                [0.204, 0.204, 0.204, 0.204, 0.204, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039, 0.2039],
                [0.7765, 0.7451, 0.7098, 0.6627, 0.6078, 0.5373, 0.4431, 0.3216, 0.2235, 0.1922, 0.2039]
            ]
        )

    elif filter == "Seventies":
        filter_tuple = (
            [
                [0.749, 0.6784, 0.6118, 0.5412, 0.4784, 0.4118, 0.3569, 0.3059, 0.2588, 0.2157, 0.1765],
                [0.0, 0.0, 0.0157, 0.0157, 0.0353, 0.0431, 0.051, 0.0588, 0.0549, 0.0588, 0.0588],
                [0.1844, 0.1804, 0.1765, 0.1725, 0.1686, 0.1647, 0.1647, 0.1608, 0.1569, 0.1529, 0.149]
            ], [
                [0.2471, 0.204, 0.1765, 0.1804, 0.1961, 0.2, 0.2, 0.1922, 0.1843, 0.1804, 0.1765],
                [0.7569, 0.6745, 0.5882, 0.498, 0.4078, 0.3216, 0.2471, 0.1882, 0.1333, 0.0902, 0.0588],
                [0.1725, 0.1647, 0.1686, 0.1686, 0.1686, 0.1686, 0.1647, 0.1569, 0.1569, 0.1529, 0.149]
            ], [
                [0.2471, 0.2314, 0.2196, 0.2118, 0.2078, 0.2, 0.1961, 0.1922, 0.1882, 0.1804, 0.1765],
                [0.1804, 0.1687, 0.1529, 0.1412, 0.1216, 0.1098, 0.0941, 0.0784, 0.0706, 0.0627, 0.0588],
                [0.6627, 0.6039, 0.5451, 0.4902, 0.4353, 0.3765, 0.3216, 0.2706, 0.2235, 0.1843, 0.149]
            ]
        )

    elif filter == "Oldtimer":
        filter_tuple = (
            [
                [0.9294, 0.9176, 0.8902, 0.8392, 0.7176, 0.5765, 0.4392, 0.349, 0.302, 0.2824, 0.2824],
                [0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922],
                [0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824]
            ], [
                [0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824],
                [0.7529, 0.6941, 0.6392, 0.5843, 0.5294, 0.4706, 0.4118, 0.3608, 0.302, 0.2471, 0.1922],
                [0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824]
            ], [
                [0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824, 0.2824],
                [0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922, 0.1922],
                [0.5922, 0.5569, 0.5255, 0.498, 0.4667, 0.4353, 0.4039, 0.3725, 0.3451, 0.3098, 0.2824]
            ]
        )

    elif filter == "Inferno":
        filter_tuple = (
            [
                [1.0, 1.0, 0.9961, 0.9843, 0.9451, 0.8706, 0.7686, 0.6549, 0.5294, 0.4196, 0.3216],
                [0.1687, 0.1687, 0.1687, 0.1687, 0.1686, 0.1686, 0.1686, 0.1686, 0.1686, 0.1686, 0.1686],
                [0.3687, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686]
            ], [
                [0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216],
                [0.9176, 0.8431, 0.7569, 0.6745, 0.5961, 0.5216, 0.451, 0.3765, 0.3137, 0.2314, 0.1686],
                [0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686, 0.3686]
            ], [
                [0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216, 0.3216],
                [0.1687, 0.1687, 0.1687, 0.1687, 0.1686, 0.1686, 0.1686, 0.1686, 0.1686, 0.1686, 0.1686],
                [0.8745, 0.7647, 0.6588, 0.5804, 0.5216, 0.4784, 0.4471, 0.4235, 0.4078, 0.3843, 0.3686]
            ]
        )

    elif filter == "Snappy":
        filter_tuple = (
            [
                [1.0, 1.0, 0.9529, 0.8549, 0.7294, 0.5961, 0.4667, 0.3725, 0.2745, 0.1569, 0.0],
                [0.0981, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0, 0.0039, 0.0],
                [0.302, 0.2824, 0.2549, 0.2235, 0.1922, 0.1569, 0.1137, 0.0784, 0.0392, 0.0118, 0.0]
            ], [
                [0.5882, 0.4627, 0.2589, 0.004, 0.0, 0.0, 0.0118, 0.1255, 0.1294, 0.0627, 0.0],
                [0.9608, 0.9333, 0.8941, 0.8431, 0.7529, 0.6353, 0.4667, 0.3098, 0.1843, 0.098, 0.0],
                [0.4275, 0.4, 0.3765, 0.3647, 0.3451, 0.3216, 0.2863, 0.2431, 0.1647, 0.0824, 0.0]
            ], [
                [0.4745, 0.3686, 0.2588, 0.1569, 0.0667, 0.0157, 0.0039, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0079, 0.0, 0.0, 0.0039, 0.0, 0.0039, 0.0],
                [0.9176, 0.8706, 0.8196, 0.7686, 0.7098, 0.6392, 0.5647, 0.502, 0.4157, 0.2627, 0.0]
            ]
        )

    elif filter == "Classic":
        filter_tuple = (
            [
                [0.9922, 0.8902, 0.7647, 0.6392, 0.5059, 0.3804, 0.2706, 0.1804, 0.102, 0.0392, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.004, 0.0157, 0.0118, 0.0157, 0.0078, 0.0078, 0.0],
                [0.0118, 0.0236, 0.0079, 0.0196, 0.0157, 0.0078, 0.0078, 0.0118, 0.0078, 0.0039, 0.0]
            ], [
                [0.4824, 0.3451, 0.1804, 0.0471, 0.0236, 0.0196, 0.0314, 0.0392, 0.0275, 0.0157, 0.0],
                [0.8706, 0.8118, 0.7412, 0.6471, 0.5294, 0.4078, 0.2863, 0.1882, 0.102, 0.0353, 0.0],
                [0.2196, 0.1804, 0.1176, 0.0784, 0.0549, 0.0471, 0.0392, 0.0314, 0.0118, 0.0118, 0.0]
            ], [
                [0.2, 0.0627, 0.0235, 0.0118, 0.0157, 0.0196, 0.0353, 0.0392, 0.0157, 0.0157, 0.0],
                [0.051, 0.0589, 0.051, 0.0432, 0.0353, 0.0314, 0.0157, 0.0118, 0.0118, 0.0039, 0.0],
                [0.8314, 0.7608, 0.6745, 0.5686, 0.4549, 0.3451, 0.2392, 0.1529, 0.0824, 0.0275, 0.0]
            ]
        )

    elif filter == "Quozi":
        filter_tuple = (
            [
                [0.7294, 0.6863, 0.6275, 0.5686, 0.498, 0.4314, 0.3647, 0.3098, 0.2627, 0.2275, 0.1961],
                [0.2706, 0.2432, 0.2196, 0.2, 0.1804, 0.1608, 0.149, 0.1333, 0.1255, 0.1137, 0.1059],
                [0.4196, 0.3882, 0.3569, 0.3255, 0.2941, 0.2627, 0.2392, 0.2235, 0.2078, 0.2, 0.1961]
            ], [
                [0.5725, 0.5176, 0.4706, 0.4235, 0.3804, 0.3373, 0.298, 0.2706, 0.2392, 0.2157, 0.1961],
                [0.8235, 0.7922, 0.7412, 0.6902, 0.6235, 0.5255, 0.4118, 0.3059, 0.2078, 0.1451, 0.1059],
                [0.6196, 0.5882, 0.549, 0.5098, 0.4667, 0.4157, 0.349, 0.2941, 0.2392, 0.2078, 0.1961]
            ], [
                [0.2392, 0.2353, 0.2275, 0.2235, 0.2196, 0.2157, 0.2118, 0.2039, 0.2039, 0.1961, 0.1961],
                [0.1451, 0.1412, 0.1334, 0.1334, 0.1255, 0.1216, 0.1216, 0.1137, 0.1137, 0.1059, 0.1059],
                [0.6431, 0.6157, 0.5765, 0.5373, 0.4902, 0.4392, 0.3765, 0.3098, 0.2471, 0.2078, 0.1961]
            ]
        )

    elif filter == "Lomo":
        filter_tuple = (
            [
                [0.7843, 0.8118, 0.8235, 0.8, 0.749, 0.5765, 0.2392, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.7843, 0.8118, 0.8235, 0.8, 0.749, 0.5765, 0.2392, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.7843, 0.8118, 0.8235, 0.8, 0.749, 0.5765, 0.2392, 0.0, 0.0, 0.0, 0.0]
            ]
        )

    elif filter == "Lomo 100":
        filter_tuple = (
            [
                [1.0, 1.0, 1.0, 0.9255, 0.7608, 0.5922, 0.4275, 0.2902, 0.1686, 0.0784, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.5137, 0.1295, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0],
                [1.0, 1.0, 1.0, 0.9725, 0.8549, 0.698, 0.5059, 0.3333, 0.1843, 0.0745, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0]
            ], [
                [0.0745, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 0.9922, 0.9098, 0.7843, 0.6392, 0.4706, 0.3255, 0.1922, 0.0863, 0.0]
            ]
        )

    elif filter == "Pola SX":
        filter_tuple = (
            [
                [0.8431, 0.8431, 0.8431, 0.7882, 0.6078, 0.4039, 0.2078, 0.051, 0.0, 0.0, 0.0],
                [0.0432, 0.0432, 0.0432, 0.0393, 0.0314, 0.0196, 0.0118, 0.0, 0.0, 0.0, 0.0],
                [0.0432, 0.0432, 0.0432, 0.0393, 0.0314, 0.0196, 0.0118, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.1451, 0.1412, 0.1177, 0.0902, 0.0667, 0.0431, 0.0235, 0.0078, 0.0, 0.0, 0.0],
                [0.9412, 0.9294, 0.7569, 0.5882, 0.4353, 0.2941, 0.1647, 0.0549, 0.0, 0.0, 0.0],
                [0.1451, 0.1412, 0.1176, 0.0902, 0.0667, 0.0431, 0.0235, 0.0078, 0.0, 0.0, 0.0]
            ], [
                [0.0157, 0.0157, 0.0118, 0.0118, 0.0078, 0.0078, 0.0039, 0.0039, 0.0, 0.0, 0.0],
                [0.0157, 0.0157, 0.0118, 0.0118, 0.0078, 0.0078, 0.0039, 0.0039, 0.0, 0.0, 0.0],
                [0.8157, 0.8157, 0.7647, 0.6471, 0.5255, 0.4078, 0.2824, 0.1647, 0.0431, 0.0, 0.0]
            ]
        )

    # Smooth

    elif filter == "Chestnut":
        filter_tuple = (
            [
                [1.0, 0.8431, 0.7373, 0.6784, 0.6314, 0.5725, 0.4627, 0.3373, 0.2039, 0.0941, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 0.8588, 0.7412, 0.651, 0.5647, 0.4902, 0.4, 0.3098, 0.2078, 0.1059, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 0.851, 0.7294, 0.6314, 0.5373, 0.4549, 0.3765, 0.2941, 0.2039, 0.1059, 0.0]
            ]
        )

    elif filter == "Softy":
        filter_tuple = (
            [
                [0.9216, 0.8235, 0.7294, 0.6392, 0.5451, 0.4549, 0.3608, 0.2667, 0.1725, 0.0784, 0.0],
                [0.2236, 0.204, 0.1844, 0.1647, 0.1451, 0.1216, 0.0941, 0.0745, 0.051, 0.0235, 0.0],
                [0.1216, 0.102, 0.0824, 0.0667, 0.0471, 0.0314, 0.0235, 0.0078, 0.0118, 0.0039, 0.0]
            ], [
                [0.2667, 0.2393, 0.2, 0.1608, 0.1098, 0.0549, 0.0353, 0.0157, 0.0078, 0.0078, 0.0],
                [0.9412, 0.8431, 0.749, 0.6627, 0.5725, 0.4863, 0.3961, 0.3098, 0.2157, 0.1216, 0.0],
                [0.2627, 0.2353, 0.2039, 0.1725, 0.1333, 0.098, 0.0667, 0.0431, 0.0235, 0.0078, 0.0]
            ], [
                [0.1686, 0.149, 0.1098, 0.0941, 0.0745, 0.0706, 0.0392, 0.0392, 0.0275, 0.0078, 0.0],
                [0.204, 0.1844, 0.1608, 0.1412, 0.1216, 0.098, 0.0745, 0.0549, 0.0314, 0.0157, 0.0],
                [0.9529, 0.8549, 0.7569, 0.6667, 0.5686, 0.4784, 0.3765, 0.2863, 0.1882, 0.0902, 0.0]
            ]
        )

    elif filter == "Pebble":
        filter_tuple = (
            [
                [0.7647, 0.7529, 0.7255, 0.6667, 0.5843, 0.4824, 0.3765, 0.298, 0.2196, 0.1176, 0.0],
                [0.0628, 0.0628, 0.0589, 0.0549, 0.0471, 0.0393, 0.0314, 0.0235, 0.0196, 0.0078, 0.0],
                [0.0628, 0.0628, 0.0589, 0.0549, 0.0471, 0.0393, 0.0314, 0.0235, 0.0196, 0.0078, 0.0]
            ], [
                [0.2157, 0.2118, 0.204, 0.1883, 0.1647, 0.1333, 0.1059, 0.0824, 0.0588, 0.0314, 0.0],
                [0.9137, 0.902, 0.8667, 0.8039, 0.698, 0.5765, 0.451, 0.3569, 0.2627, 0.1373, 0.0],
                [0.2157, 0.2118, 0.2039, 0.1882, 0.1647, 0.1333, 0.1059, 0.0824, 0.0588, 0.0314, 0.0]
            ], [
                [0.0235, 0.0196, 0.0196, 0.0196, 0.0157, 0.0118, 0.0118, 0.0078, 0.0078, 0.0039, 0.0],
                [0.0236, 0.0196, 0.0196, 0.0196, 0.0157, 0.0118, 0.0118, 0.0078, 0.0078, 0.0039, 0.0],
                [0.7216, 0.7137, 0.6863, 0.6314, 0.549, 0.451, 0.3569, 0.2824, 0.2118, 0.1098, 0.0]
            ]
        )

    elif filter == "Moss":
        filter_tuple = (
            [
                [0.9333, 0.8392, 0.7451, 0.6549, 0.5569, 0.4627, 0.3725, 0.2784, 0.1843, 0.0863, 0.0],
                [0.0236, 0.0236, 0.0236, 0.0157, 0.0196, 0.0275, 0.0235, 0.0078, 0.0118, 0.0078, 0.0],
                [0.0, 0.0079, 0.004, 0.0079, 0.0118, 0.0039, 0.0, 0.0078, 0.0078, 0.0039, 0.0]
            ], [
                [0.1334, 0.0981, 0.0902, 0.0824, 0.0589, 0.0471, 0.051, 0.0392, 0.0275, 0.0157, 0.0],
                [0.9294, 0.8314, 0.7373, 0.651, 0.5529, 0.4627, 0.3686, 0.2745, 0.1804, 0.0863, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0078, 0.0, 0.0078, 0.0078, 0.0]
            ], [
                [0.2196, 0.1961, 0.1608, 0.1333, 0.1137, 0.0863, 0.0588, 0.0431, 0.0314, 0.0118, 0.0],
                [0.0079, 0.0314, 0.0118, 0.0236, 0.0079, 0.0196, 0.0118, 0.0078, 0.0078, 0.0078, 0.0],
                [0.8549, 0.7647, 0.6784, 0.5961, 0.5098, 0.4235, 0.3373, 0.251, 0.1647, 0.0784, 0.0]
            ]
        )

    elif filter == "Soft":
        filter_tuple = (
            [
                [1.0, 0.9373, 0.8392, 0.7412, 0.6314, 0.5137, 0.3843, 0.2627, 0.1569, 0.0667, 0.0],
                [0.0118, 0.0079, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0078, 0.0],
                [0.0, 0.0, 0.004, 0.004, 0.0157, 0.0079, 0.0039, 0.0078, 0.0078, 0.0039, 0.0]
            ], [
                [0.4236, 0.3647, 0.2981, 0.2353, 0.149, 0.0471, 0.0275, 0.0235, 0.0314, 0.0196, 0.0],
                [0.9529, 0.8667, 0.7765, 0.6863, 0.5922, 0.4941, 0.3804, 0.2667, 0.1529, 0.0667, 0.0],
                [0.2784, 0.2314, 0.1843, 0.1373, 0.0784, 0.0392, 0.0314, 0.0196, 0.0157, 0.0118, 0.0]
            ], [
                [0.3216, 0.2549, 0.1725, 0.0902, 0.0314, 0.0157, 0.0157, 0.0118, 0.0196, 0.0118, 0.0],
                [0.0667, 0.0667, 0.0628, 0.051, 0.051, 0.0353, 0.0314, 0.0157, 0.0118, 0.0078, 0.0],
                [0.9412, 0.8549, 0.7686, 0.6863, 0.5882, 0.4902, 0.3765, 0.2627, 0.1529, 0.0627, 0.0]
            ]
        )

    elif filter == "Lemon":
        filter_tuple = (
            [
                [0.8549, 0.7843, 0.698, 0.5922, 0.4627, 0.3373, 0.2235, 0.1373, 0.0667, 0.0235, 0.0],
                [0.051, 0.0471, 0.0393, 0.0314, 0.0275, 0.0196, 0.0196, 0.0118, 0.0039, 0.0, 0.0],
                [0.1295, 0.1177, 0.1059, 0.0942, 0.0785, 0.0667, 0.0549, 0.0392, 0.0235, 0.0078, 0.0]
            ], [
                [0.153, 0.1295, 0.1059, 0.0824, 0.0628, 0.0471, 0.0353, 0.0235, 0.0157, 0.0039, 0.0],
                [0.9451, 0.898, 0.8275, 0.7294, 0.5843, 0.4235, 0.2784, 0.1686, 0.0863, 0.0314, 0.0],
                [0.1922, 0.1843, 0.1725, 0.1608, 0.1451, 0.1255, 0.1059, 0.0784, 0.0549, 0.0275, 0.0]
            ], [
                [0.0157, 0.0118, 0.0118, 0.0078, 0.0078, 0.0039, 0.0039, 0.0, 0.0, 0.0, 0.0],
                [0.0157, 0.0118, 0.0118, 0.0118, 0.0079, 0.0039, 0.0039, 0.0, 0.0, 0.0, 0.0],
                [0.6784, 0.6588, 0.6118, 0.5216, 0.4, 0.2824, 0.2078, 0.1725, 0.1333, 0.0706, 0.0]
            ]
        )

    elif filter == "Green Gap":
        filter_tuple = (
            [
                [1.0, 0.9529, 0.8431, 0.6863, 0.4902, 0.2941, 0.1059, 0.0, 0.0, 0.0, 0.0],
                [0.0275, 0.0196, 0.0157, 0.0079, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 0.9922, 0.8667, 0.7294, 0.5961, 0.4667, 0.3412, 0.2353, 0.1373, 0.0471, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 0.898, 0.7843, 0.6667, 0.5294, 0.3961, 0.2667, 0.1412, 0.0235, 0.0, 0.0]
            ]
        )

    elif filter == "High Carb":
        filter_tuple = (
            [
                [0.9922, 0.898, 0.7882, 0.6824, 0.5686, 0.4588, 0.3412, 0.2353, 0.1294, 0.0392, 0.0],
                [0.0589, 0.0353, 0.0196, 0.0157, 0.0079, 0.004, 0.0039, 0.0078, 0.0039, 0.0078, 0.0],
                [0.0785, 0.0549, 0.0471, 0.0275, 0.0275, 0.0196, 0.0078, 0.0118, 0.0078, 0.0039, 0.0]
            ], [
                [0.5176, 0.4353, 0.3569, 0.2824, 0.2157, 0.1529, 0.098, 0.051, 0.0275, 0.0157, 0.0],
                [0.8941, 0.8196, 0.7373, 0.6431, 0.5412, 0.4392, 0.3294, 0.2314, 0.1294, 0.0392, 0.0],
                [0.4039, 0.3608, 0.3059, 0.2549, 0.2, 0.149, 0.102, 0.0549, 0.0196, 0.0118, 0.0]
            ], [
                [0.3216, 0.2392, 0.1608, 0.102, 0.0667, 0.0314, 0.0275, 0.0157, 0.0078, 0.0118, 0.0],
                [0.1844, 0.1608, 0.1373, 0.1098, 0.0824, 0.051, 0.0353, 0.0157, 0.0157, 0.0039, 0.0],
                [0.9137, 0.8431, 0.7608, 0.6667, 0.5608, 0.4549, 0.3412, 0.2392, 0.1373, 0.0431, 0.0]
            ]
        )

    # Neat

    elif filter == "Candy":
        filter_tuple = (
            [
                [1.0, 1.0, 0.9608, 0.851, 0.7255, 0.5961, 0.4588, 0.3255, 0.1882, 0.0824, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0, 0.0]
            ], [
                [0.4079, 0.2824, 0.1177, 0.0353, 0.004, 0.0, 0.0, 0.0, 0.0078, 0.0118, 0.0],
                [1.0, 0.9608, 0.8824, 0.7922, 0.6863, 0.5725, 0.4471, 0.3216, 0.1922, 0.0784, 0.0],
                [0.0118, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0]
            ], [
                [0.2549, 0.1176, 0.0196, 0.0078, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0118, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.004, 0.0, 0.0078, 0.0078, 0.0039, 0.0],
                [1.0, 0.9569, 0.8745, 0.7843, 0.6784, 0.5647, 0.4392, 0.3137, 0.1882, 0.0784, 0.0]
            ]
        )

    elif filter == "Colorful":
        filter_tuple = (
            [
                [1.0, 0.9333, 0.8471, 0.7529, 0.651, 0.5412, 0.4157, 0.2941, 0.1569, 0.0549, 0.0],
                [0.2353, 0.1765, 0.1098, 0.0549, 0.0157, 0.004, 0.0039, 0.0039, 0.0039, 0.0078, 0.0],
                [0.0667, 0.0589, 0.0353, 0.0393, 0.0236, 0.0275, 0.0157, 0.0118, 0.0118, 0.0039, 0.0]
            ], [
                [0.5333, 0.4549, 0.3726, 0.2863, 0.1844, 0.098, 0.0392, 0.0039, 0.0078, 0.0157, 0.0],
                [0.9647, 0.898, 0.8275, 0.749, 0.651, 0.5529, 0.4353, 0.3137, 0.1843, 0.0627, 0.0],
                [0.3569, 0.298, 0.2353, 0.1765, 0.1059, 0.0431, 0.0157, 0.0078, 0.0118, 0.0078, 0.0]
            ], [
                [0.4235, 0.349, 0.2745, 0.1922, 0.098, 0.0314, 0.0039, 0.0039, 0.0118, 0.0118, 0.0],
                [0.1334, 0.102, 0.0745, 0.0628, 0.0432, 0.0353, 0.0314, 0.0196, 0.0118, 0.0078, 0.0],
                [0.949, 0.8824, 0.8118, 0.7333, 0.6353, 0.5373, 0.4235, 0.3059, 0.1765, 0.0627, 0.0]
            ]
        )

    elif filter == "Creamy":
        filter_tuple = (
            [
                [1.0, 0.9843, 0.9137, 0.8118, 0.6824, 0.5451, 0.3961, 0.2667, 0.1451, 0.0471, 0.0],
                [0.3138, 0.2236, 0.1255, 0.051, 0.0196, 0.0118, 0.0118, 0.0118, 0.0118, 0.0118, 0.0],
                [0.1687, 0.1491, 0.1295, 0.1059, 0.0824, 0.0549, 0.0392, 0.0157, 0.0157, 0.0039, 0.0]
            ], [
                [0.7765, 0.6745, 0.5647, 0.4627, 0.349, 0.2471, 0.1569, 0.0941, 0.0471, 0.0196, 0.0],
                [0.8588, 0.8431, 0.8, 0.7294, 0.6392, 0.5255, 0.3922, 0.2667, 0.1451, 0.051, 0.0],
                [0.502, 0.4471, 0.3961, 0.3569, 0.298, 0.2235, 0.1569, 0.098, 0.0431, 0.0157, 0.0]
            ], [
                [0.5804, 0.4902, 0.4078, 0.3294, 0.2471, 0.1725, 0.1137, 0.0706, 0.0392, 0.0157, 0.0],
                [0.2706, 0.2628, 0.251, 0.2314, 0.1961, 0.1529, 0.1059, 0.0627, 0.0275, 0.0118, 0.0],
                [0.7451, 0.7255, 0.6863, 0.6314, 0.5569, 0.4588, 0.3412, 0.2275, 0.1216, 0.0353, 0.0]
            ]
        )

    elif filter == "Fixie":
        filter_tuple = (
            [
                [1.0, 0.9569, 0.8784, 0.7765, 0.6471, 0.5137, 0.3725, 0.251, 0.1333, 0.051, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 0.9529, 0.8745, 0.7608, 0.6235, 0.4902, 0.3569, 0.2431, 0.1373, 0.051, 0.0],
                [0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216, 0.1216]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.8784, 0.8157, 0.7373, 0.6549, 0.5647, 0.4902, 0.4118, 0.3412, 0.2706, 0.1961, 0.1216]
            ]
        )

    elif filter == "Food":
        filter_tuple = (
            [
                [1.0, 1.0, 1.0, 0.9294, 0.7882, 0.651, 0.5098, 0.3725, 0.2353, 0.0902, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 0.9098, 0.7961, 0.6745, 0.5529, 0.4314, 0.3137, 0.1922, 0.0667, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 0.9686, 0.8196, 0.6784, 0.5255, 0.3882, 0.2431, 0.0902, 0.0]
            ]
        )

    elif filter == "Glam":
        filter_tuple = (
            [
                [0.0196, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0393, 0.004, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0236, 0.004, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.9176, 0.8196, 0.6627, 0.4863, 0.3098, 0.1804, 0.0863, 0.0235, 0.0, 0.0, 0.0],
                [0.8431, 0.7255, 0.6078, 0.498, 0.3843, 0.2706, 0.1529, 0.0431, 0.0, 0.0, 0.0],
                [0.7686, 0.6118, 0.4824, 0.3725, 0.2706, 0.1804, 0.098, 0.0235, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ]
        )

    elif filter == "Goblin":
        filter_tuple = (
            [
                [0.6, 0.5373, 0.4745, 0.4196, 0.3608, 0.298, 0.2392, 0.1843, 0.1216, 0.0588, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.1961, 0.1804, 0.1569, 0.1373, 0.1176, 0.098, 0.0784, 0.0588, 0.0392, 0.0196, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.698, 0.6275, 0.5529, 0.4902, 0.4196, 0.349, 0.2784, 0.2118, 0.1373, 0.0706, 0.0],
                [0.3294, 0.298, 0.2627, 0.2314, 0.1961, 0.1647, 0.1294, 0.098, 0.0627, 0.0314, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ]
        )

    elif filter == "High Contrast":
        filter_tuple = (
            [
                [1.0, 1.0, 1.0, 0.9843, 0.8431, 0.6549, 0.4627, 0.2784, 0.1569, 0.0667, 0.0],
                [0.2902, 0.1295, 0.004, 0.0, 0.0, 0.0, 0.004, 0.0235, 0.0196, 0.0118, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0, 0.0]
            ], [
                [0.7059, 0.6157, 0.4824, 0.2196, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0],
                [1.0, 0.9843, 0.9529, 0.9059, 0.8392, 0.7373, 0.5765, 0.4039, 0.2353, 0.102, 0.0],
                [0.5843, 0.4902, 0.3294, 0.0275, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0]
            ], [
                [0.498, 0.2353, 0.004, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0118, 0.0196, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0157, 0.0157, 0.0157, 0.0078, 0.0118, 0.0039, 0.0],
                [1.0, 1.0, 0.9961, 0.9569, 0.8863, 0.7922, 0.6706, 0.4392, 0.1569, 0.0392, 0.0]
            ]
        )

    elif filter == "K1":
        filter_tuple = (
            [
                [0.9216, 0.8784, 0.8196, 0.7451, 0.6235, 0.4902, 0.3412, 0.2118, 0.1059, 0.0392, 0.0],
                [0.0196, 0.0196, 0.0196, 0.0157, 0.0157, 0.0118, 0.0078, 0.0039, 0.0039, 0.0, 0.0],
                [0.0196, 0.0196, 0.0196, 0.0157, 0.0157, 0.0118, 0.0078, 0.0039, 0.0039, 0.0, 0.0]
            ], [
                [0.0706, 0.0706, 0.0628, 0.0589, 0.0471, 0.0353, 0.0275, 0.0157, 0.0078, 0.0039, 0.0],
                [0.9725, 0.9255, 0.8667, 0.7843, 0.6588, 0.5137, 0.3608, 0.2235, 0.1137, 0.0431, 0.0],
                [0.0706, 0.0706, 0.0627, 0.0588, 0.0471, 0.0353, 0.0275, 0.0157, 0.0078, 0.0039, 0.0]
            ], [
                [0.0078, 0.0078, 0.0078, 0.0039, 0.0039, 0.0039, 0.0039, 0.0, 0.0, 0.0, 0.0],
                [0.0079, 0.0079, 0.0079, 0.004, 0.004, 0.004, 0.0039, 0.0, 0.0, 0.0, 0.0],
                [0.9059, 0.8627, 0.8078, 0.7373, 0.6157, 0.4824, 0.3373, 0.2078, 0.1059, 0.0392, 0.0]
            ]
        )

    elif filter == "K6":
        filter_tuple = (
            [
                [0.6078, 0.5412, 0.4784, 0.4235, 0.3647, 0.302, 0.2392, 0.1843, 0.1216, 0.0588, 0.0],
                [0.1059, 0.0981, 0.0824, 0.0745, 0.0628, 0.051, 0.0431, 0.0314, 0.0235, 0.0078, 0.0],
                [0.1059, 0.0981, 0.0824, 0.0745, 0.0628, 0.051, 0.0431, 0.0314, 0.0235, 0.0078, 0.0]
            ], [
                [0.3569, 0.3216, 0.2863, 0.251, 0.2157, 0.1765, 0.1412, 0.1098, 0.0706, 0.0353, 0.0],
                [0.8588, 0.7686, 0.6824, 0.6, 0.5137, 0.4275, 0.3412, 0.2588, 0.1686, 0.0863, 0.0],
                [0.3569, 0.3216, 0.2863, 0.251, 0.2157, 0.1765, 0.1412, 0.1098, 0.0706, 0.0353, 0.0]
            ], [
                [0.0353, 0.0314, 0.0275, 0.0235, 0.0196, 0.0196, 0.0157, 0.0118, 0.0078, 0.0039, 0.0],
                [0.0353, 0.0314, 0.0275, 0.0236, 0.0196, 0.0196, 0.0157, 0.0118, 0.0078, 0.0039, 0.0],
                [0.5373, 0.4824, 0.4235, 0.3725, 0.3216, 0.2667, 0.2118, 0.1608, 0.1059, 0.051, 0.0]
            ]
        )

    elif filter == "Keen":
        filter_tuple = (
            [
                [1.0, 0.9765, 0.8745, 0.7647, 0.6431, 0.5216, 0.3961, 0.2902, 0.1843, 0.0824, 0.0],
                [0.0236, 0.004, 0.0, 0.0, 0.004, 0.0079, 0.0118, 0.0039, 0.0118, 0.0078, 0.0],
                [0.0432, 0.0236, 0.0275, 0.0236, 0.0157, 0.0196, 0.0118, 0.0078, 0.0118, 0.0039, 0.0]
            ], [
                [0.3883, 0.2589, 0.051, 0.0079, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0118, 0.0],
                [1.0, 0.9333, 0.8549, 0.7647, 0.6627, 0.549, 0.4275, 0.3137, 0.2, 0.0902, 0.0],
                [0.1451, 0.098, 0.0588, 0.0431, 0.0431, 0.0471, 0.0353, 0.0275, 0.0196, 0.0078, 0.0]
            ], [
                [0.1608, 0.0588, 0.0078, 0.0, 0.0039, 0.0, 0.0, 0.0039, 0.0039, 0.0078, 0.0],
                [0.0079, 0.004, 0.0118, 0.0118, 0.0079, 0.0157, 0.0118, 0.0078, 0.0078, 0.0039, 0.0],
                [1.0, 0.9294, 0.8392, 0.749, 0.6392, 0.5373, 0.4353, 0.3373, 0.2275, 0.1098, 0.0]
            ]
        )

    elif filter == "Lucid":
        filter_tuple = (
            [
                [0.8902, 0.7882, 0.6902, 0.5922, 0.4902, 0.3961, 0.3059, 0.2353, 0.1686, 0.1059, 0.0235],
                [0.0706, 0.0549, 0.0549, 0.0549, 0.0549, 0.0627, 0.0667, 0.0549, 0.051, 0.0353, 0.0235],
                [0.1883, 0.1726, 0.153, 0.1333, 0.1176, 0.098, 0.0784, 0.0627, 0.051, 0.0392, 0.0235]
            ], [
                [0.0785, 0.0589, 0.0627, 0.0549, 0.0824, 0.102, 0.102, 0.0941, 0.0706, 0.0549, 0.0235],
                [0.6157, 0.549, 0.4784, 0.4078, 0.3373, 0.2667, 0.2078, 0.1569, 0.1137, 0.0784, 0.0235],
                [0.2235, 0.2078, 0.1922, 0.1765, 0.1569, 0.1333, 0.1137, 0.0941, 0.0706, 0.051, 0.0235]
            ], [
                [0.1059, 0.0863, 0.0588, 0.0627, 0.0431, 0.0431, 0.0314, 0.0392, 0.0275, 0.0314, 0.0235],
                [0.0745, 0.0784, 0.0784, 0.0745, 0.0706, 0.0667, 0.0627, 0.0549, 0.051, 0.0392, 0.0235],
                [0.6588, 0.5922, 0.5294, 0.4745, 0.4196, 0.3647, 0.3137, 0.2588, 0.1922, 0.1216, 0.0235]
            ]
        )

    elif filter == "Neat":
        filter_tuple = (
            [
                [0.8471, 0.7686, 0.6824, 0.5882, 0.4941, 0.4, 0.3059, 0.2235, 0.1412, 0.0627, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0, 0.0078, 0.0039, 0.0078, 0.0],
                [0.004, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0039, 0.0078, 0.0039, 0.0]
            ], [
                [0.2942, 0.1255, 0.0118, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0118, 0.0118, 0.0],
                [0.9843, 0.9059, 0.8275, 0.7412, 0.6314, 0.5176, 0.3961, 0.2863, 0.1804, 0.0824, 0.0],
                [0.102, 0.0275, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0]
            ], [
                [0.0706, 0.0157, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0118, 0.0118, 0.0],
                [0.0236, 0.0157, 0.004, 0.0, 0.0, 0.0039, 0.0, 0.0039, 0.0039, 0.0039, 0.0],
                [0.9922, 0.9137, 0.8353, 0.749, 0.6431, 0.5255, 0.4039, 0.2902, 0.1843, 0.0824, 0.0]
            ]
        )

    elif filter == "Pro 400":
        filter_tuple = (
            [
                [1.0, 0.9216, 0.8157, 0.7098, 0.5843, 0.4588, 0.3333, 0.2196, 0.1216, 0.0471, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0078, 0.0078, 0.0],
                [0.0236, 0.0275, 0.0236, 0.0118, 0.0118, 0.004, 0.0078, 0.0078, 0.0078, 0.0039, 0.0]
            ], [
                [0.4432, 0.302, 0.1138, 0.0079, 0.0, 0.0, 0.0, 0.0039, 0.0196, 0.0118, 0.0],
                [0.9608, 0.8902, 0.8157, 0.7255, 0.6118, 0.4902, 0.3608, 0.2431, 0.1333, 0.0471, 0.0],
                [0.2118, 0.1176, 0.0275, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0, 0.0078, 0.0]
            ], [
                [0.1804, 0.0353, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0118, 0.0],
                [0.0393, 0.0275, 0.0196, 0.0275, 0.0118, 0.0157, 0.0078, 0.0078, 0.0118, 0.0039, 0.0],
                [0.9647, 0.8902, 0.8157, 0.7294, 0.6157, 0.4902, 0.3608, 0.2431, 0.1333, 0.0471, 0.0]
            ]
        )

    # Cold

    elif filter == "Colla":
        filter_tuple = (
            [
                [0.8824, 0.8235, 0.7412, 0.6314, 0.4902, 0.3569, 0.2275, 0.1294, 0.0549, 0.0235, 0.0],
                [0.3177, 0.251, 0.1883, 0.1412, 0.102, 0.0667, 0.0471, 0.0314, 0.0157, 0.0118, 0.0],
                [0.3059, 0.2785, 0.2432, 0.2, 0.153, 0.1059, 0.0588, 0.0275, 0.0157, 0.0078, 0.0]
            ], [
                [0.7529, 0.6471, 0.5216, 0.3922, 0.2549, 0.1451, 0.0824, 0.0549, 0.0392, 0.0157, 0.0],
                [0.8588, 0.8196, 0.7608, 0.6863, 0.5765, 0.4431, 0.2941, 0.1686, 0.0745, 0.0235, 0.0],
                [0.5647, 0.498, 0.4353, 0.3608, 0.2824, 0.2039, 0.1333, 0.0784, 0.0353, 0.0157, 0.0]
            ], [
                [0.5137, 0.4314, 0.3529, 0.2784, 0.2039, 0.1412, 0.0863, 0.0549, 0.0275, 0.0157, 0.0],
                [0.3844, 0.3608, 0.3295, 0.2902, 0.2431, 0.1843, 0.1216, 0.0706, 0.0275, 0.0118, 0.0],
                [0.7451, 0.7059, 0.6627, 0.6, 0.5059, 0.3922, 0.2667, 0.1647, 0.0784, 0.0235, 0.0]
            ]
        )

    elif filter == "Solanus":
        filter_tuple = (
            [
                [0.5608, 0.5451, 0.5216, 0.4941, 0.451, 0.3961, 0.3333, 0.2588, 0.1765, 0.098, 0.0157],
                [0.2118, 0.2079, 0.1961, 0.1883, 0.1726, 0.1529, 0.1294, 0.1059, 0.0745, 0.0471, 0.0157],
                [0.2981, 0.2902, 0.2824, 0.2745, 0.2589, 0.2353, 0.2157, 0.1882, 0.1608, 0.1294, 0.102]
            ], [
                [0.4, 0.4, 0.4, 0.3765, 0.3137, 0.2235, 0.1451, 0.0902, 0.051, 0.0314, 0.0157],
                [0.749, 0.749, 0.749, 0.7059, 0.5843, 0.4118, 0.2588, 0.1569, 0.0863, 0.0431, 0.0157],
                [0.4863, 0.4863, 0.4863, 0.4627, 0.4, 0.3098, 0.2314, 0.1765, 0.1373, 0.1137, 0.102]
            ], [
                [0.0706, 0.0706, 0.0667, 0.0627, 0.0588, 0.051, 0.0431, 0.0314, 0.0275, 0.0196, 0.0157],
                [0.0706, 0.0706, 0.0667, 0.0628, 0.0589, 0.051, 0.0431, 0.0314, 0.0275, 0.0196, 0.0157],
                [0.4196, 0.4078, 0.3922, 0.3765, 0.3451, 0.302, 0.251, 0.1961, 0.1529, 0.1216, 0.102]
            ]
        )

    elif filter == "Fridge":
        filter_tuple = (
            [
                [0.8627, 0.749, 0.6392, 0.5373, 0.4353, 0.3412, 0.251, 0.1765, 0.1059, 0.0471, 0.0353],
                [0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471],
                [0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098]
            ], [
                [0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353],
                [0.8235, 0.8039, 0.7725, 0.7098, 0.6, 0.4941, 0.3882, 0.2941, 0.1961, 0.0941, 0.0471],
                [0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098, 0.1098]
            ], [
                [0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353, 0.0353],
                [0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471, 0.0471],
                [0.8627, 0.8627, 0.8588, 0.8392, 0.7961, 0.7216, 0.5961, 0.4588, 0.3216, 0.2078, 0.1098]
            ]
        )

    elif filter == "Kalmen":
        filter_tuple = (
            [
                [0.6706, 0.6039, 0.5412, 0.4824, 0.4235, 0.3569, 0.2941, 0.2353, 0.1725, 0.1098, 0.0392],
                [0.4157, 0.3765, 0.3373, 0.298, 0.2627, 0.2235, 0.1804, 0.149, 0.1098, 0.0745, 0.0392],
                [0.3844, 0.3491, 0.3137, 0.2745, 0.2431, 0.2078, 0.1686, 0.1373, 0.102, 0.0706, 0.0392]
            ], [
                [0.4784, 0.4353, 0.3882, 0.3451, 0.298, 0.251, 0.2078, 0.1686, 0.1216, 0.0784, 0.0392],
                [0.902, 0.8157, 0.7333, 0.651, 0.5686, 0.4824, 0.3961, 0.3137, 0.2235, 0.1451, 0.0392],
                [0.4235, 0.3804, 0.3412, 0.302, 0.2667, 0.2275, 0.1843, 0.1529, 0.1137, 0.0784, 0.0392]
            ], [
                [0.3647, 0.3294, 0.2941, 0.2588, 0.2275, 0.1922, 0.1608, 0.1333, 0.098, 0.0706, 0.0392],
                [0.2471, 0.2275, 0.2, 0.1804, 0.1608, 0.1373, 0.1137, 0.098, 0.0784, 0.0549, 0.0392],
                [0.9255, 0.8392, 0.7529, 0.6706, 0.5843, 0.498, 0.4078, 0.3216, 0.2314, 0.1451, 0.0392]
            ]
        )

    elif filter == "Joran":
        filter_tuple = (
            [
                [0.5137, 0.4627, 0.4118, 0.3686, 0.3216, 0.2745, 0.2275, 0.1882, 0.1412, 0.102, 0.0588],
                [0.451, 0.4078, 0.3647, 0.3255, 0.2863, 0.2471, 0.2039, 0.1686, 0.1294, 0.0941, 0.0588],
                [0.4471, 0.4039, 0.3647, 0.3216, 0.2863, 0.2431, 0.2039, 0.1686, 0.1294, 0.0941, 0.0588]
            ], [
                [0.5255, 0.4667, 0.4157, 0.3686, 0.3373, 0.2941, 0.2471, 0.2039, 0.1569, 0.1098, 0.0588],
                [0.8275, 0.749, 0.6706, 0.5961, 0.5059, 0.4235, 0.3451, 0.2745, 0.2039, 0.1373, 0.0588],
                [0.5686, 0.5137, 0.4549, 0.4078, 0.3647, 0.3176, 0.2667, 0.2157, 0.1647, 0.1137, 0.0588]
            ], [
                [0.4314, 0.3725, 0.3137, 0.2667, 0.2196, 0.1804, 0.149, 0.1255, 0.102, 0.0863, 0.0588],
                [0.3295, 0.2942, 0.2627, 0.2392, 0.2196, 0.1922, 0.1647, 0.1412, 0.1137, 0.0824, 0.0588],
                [0.7216, 0.7098, 0.6824, 0.6431, 0.5882, 0.5216, 0.4431, 0.3647, 0.2706, 0.1765, 0.0588]
            ]
        )

    elif filter == "Levante":
        filter_tuple = (
            [
                [0.6471, 0.5725, 0.502, 0.4353, 0.3686, 0.302, 0.2392, 0.1843, 0.1176, 0.0588, 0.0],
                [0.1491, 0.1334, 0.1177, 0.1059, 0.0902, 0.0745, 0.0588, 0.0471, 0.0314, 0.0118, 0.0],
                [0.1569, 0.1373, 0.1216, 0.1098, 0.0942, 0.0784, 0.0588, 0.0471, 0.0314, 0.0118, 0.0]
            ], [
                [0.2745, 0.251, 0.2196, 0.1922, 0.1647, 0.1333, 0.1059, 0.0824, 0.051, 0.0235, 0.0],
                [0.7804, 0.698, 0.6235, 0.5529, 0.4745, 0.3961, 0.3137, 0.2392, 0.1569, 0.0784, 0.0],
                [0.3059, 0.2784, 0.2431, 0.2157, 0.1843, 0.1529, 0.1216, 0.0941, 0.0588, 0.0275, 0.0]
            ], [
                [0.051, 0.0471, 0.0392, 0.0353, 0.0275, 0.0235, 0.0196, 0.0118, 0.0039, 0.0, 0.0],
                [0.0549, 0.051, 0.0432, 0.0393, 0.0314, 0.0275, 0.0235, 0.0157, 0.0078, 0.0, 0.0],
                [0.5608, 0.5098, 0.451, 0.4, 0.3451, 0.2863, 0.2275, 0.1725, 0.1137, 0.0549, 0.0]
            ]
        )

    elif filter == "Zephyr":
        filter_tuple = (
            [
                [0.9647, 0.8471, 0.7373, 0.6353, 0.5294, 0.4353, 0.3373, 0.2549, 0.1961, 0.1176, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0118, 0.0078, 0.0039, 0.0],
                [0.2275, 0.2275, 0.2118, 0.1882, 0.1451, 0.102, 0.0549, 0.0235, 0.0157, 0.0039, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.004, 0.0039, 0.0118, 0.0588, 0.1176, 0.0471, 0.0],
                [0.9922, 0.8784, 0.7569, 0.651, 0.5373, 0.4314, 0.3216, 0.2196, 0.1255, 0.0706, 0.0],
                [0.0863, 0.1333, 0.1725, 0.1961, 0.2157, 0.2235, 0.2275, 0.2039, 0.1137, 0.0275, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0235, 0.0275, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.004, 0.0079, 0.004, 0.0196, 0.0078, 0.0, 0.0039, 0.0039, 0.0],
                [0.9922, 0.8824, 0.7725, 0.6745, 0.5765, 0.4902, 0.4039, 0.3412, 0.2824, 0.2118, 0.0]
            ]
        )

    elif filter == "Pitched":
        filter_tuple = (
            [
                [0.7608, 0.6784, 0.5961, 0.5176, 0.4392, 0.3647, 0.2902, 0.2275, 0.1686, 0.1176, 0.0549],
                [0.0, 0.0079, 0.0196, 0.0118, 0.0275, 0.0353, 0.0353, 0.0392, 0.0431, 0.0314, 0.0235],
                [0.0236, 0.0157, 0.0236, 0.0275, 0.0275, 0.0235, 0.0196, 0.0157, 0.0157, 0.0157, 0.0157]
            ], [
                [0.3059, 0.1059, 0.0078, 0.0, 0.0, 0.0039, 0.0353, 0.0627, 0.0745, 0.0745, 0.0549],
                [0.8902, 0.8431, 0.7765, 0.6941, 0.5961, 0.4902, 0.3765, 0.2784, 0.1804, 0.1059, 0.0235],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0118, 0.0157, 0.0275, 0.0157, 0.0157]
            ], [
                [0.0745, 0.0784, 0.0824, 0.0784, 0.0824, 0.0863, 0.0863, 0.0784, 0.0745, 0.0667, 0.0549],
                [0.0353, 0.0353, 0.0392, 0.0392, 0.0431, 0.0392, 0.0353, 0.0314, 0.0314, 0.0275, 0.0235],
                [0.5098, 0.4549, 0.4, 0.349, 0.298, 0.2471, 0.2, 0.1529, 0.1098, 0.0667, 0.0157]
            ]
        )

    elif filter == "Settled":
        filter_tuple = (
            [
                [1.0, 0.9882, 0.8824, 0.7647, 0.6431, 0.5176, 0.3804, 0.2549, 0.149, 0.0627, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0078, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0078, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0],
                [1.0, 0.9765, 0.8941, 0.7922, 0.6706, 0.5529, 0.4196, 0.2902, 0.1647, 0.0667, 0.0],
                [0.1216, 0.0196, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0078, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0, 0.0],
                [1.0, 1.0, 0.9725, 0.902, 0.7961, 0.6706, 0.5176, 0.3725, 0.2196, 0.0902, 0.0]
            ]
        )

    # Warm

    elif filter == "Golden":
        filter_tuple = (
            [
                [1.0, 1.0, 0.9373, 0.8157, 0.6902, 0.5765, 0.4667, 0.3686, 0.2667, 0.1804, 0.1451],
                [0.1334, 0.0628, 0.051, 0.0589, 0.0745, 0.0785, 0.0745, 0.0745, 0.0824, 0.0941, 0.0941],
                [0.0628, 0.0628, 0.0589, 0.0628, 0.0667, 0.0628, 0.0667, 0.0667, 0.0667, 0.0627, 0.0667]
            ], [
                [0.4589, 0.3491, 0.2549, 0.2, 0.1882, 0.1922, 0.1804, 0.1608, 0.149, 0.1451, 0.1451],
                [0.9294, 0.8627, 0.7882, 0.698, 0.5961, 0.4941, 0.3922, 0.302, 0.2078, 0.1373, 0.0941],
                [0.2039, 0.1765, 0.149, 0.1333, 0.1176, 0.102, 0.0863, 0.0745, 0.0667, 0.0667, 0.0667]
            ], [
                [0.4039, 0.1647, 0.0, 0.0, 0.0235, 0.1098, 0.1608, 0.1569, 0.1451, 0.1451, 0.1451],
                [0.0745, 0.004, 0.0, 0.0, 0.0039, 0.0196, 0.0431, 0.0667, 0.0824, 0.0941, 0.0941],
                [1.0, 1.0, 1.0, 0.9176, 0.7765, 0.6157, 0.4588, 0.3412, 0.2314, 0.1294, 0.0667]
            ]
        )

    elif filter == "Low Fire":
        filter_tuple = (
            [
                [1.0, 1.0, 0.902, 0.7608, 0.6118, 0.4627, 0.302, 0.1725, 0.0745, 0.0235, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0039, 0.0],
                [0.1098, 0.0981, 0.0824, 0.0628, 0.0471, 0.0314, 0.0157, 0.0118, 0.0078, 0.0039, 0.0]
            ], [
                [0.6784, 0.4471, 0.1177, 0.004, 0.0157, 0.0549, 0.0157, 0.0235, 0.0235, 0.0157, 0.0],
                [0.9882, 0.9843, 0.9333, 0.8196, 0.6275, 0.4353, 0.2824, 0.1608, 0.0706, 0.0196, 0.0],
                [0.0471, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0118, 0.0078, 0.0]
            ], [
                [0.2785, 0.004, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0118, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0039, 0.0, 0.0],
                [1.0, 1.0, 0.9529, 0.8431, 0.6863, 0.5098, 0.3373, 0.1961, 0.098, 0.0353, 0.0]
            ]
        )

    elif filter == "Sunrise":
        filter_tuple = (
            [
                [0.9765, 0.8588, 0.7333, 0.6118, 0.4863, 0.3725, 0.2745, 0.2118, 0.1569, 0.0941, 0.0706],
                [0.0, 0.0, 0.0, 0.0, 0.0157, 0.0392, 0.0549, 0.0588, 0.0549, 0.0667, 0.0667],
                [0.0785, 0.0824, 0.0785, 0.0706, 0.0667, 0.0588, 0.0588, 0.0588, 0.0627, 0.0627, 0.0627]
            ], [
                [0.0157, 0.0, 0.0, 0.0, 0.0157, 0.051, 0.0941, 0.098, 0.0706, 0.0627, 0.0706],
                [0.8235, 0.7333, 0.6314, 0.5255, 0.4157, 0.3137, 0.2235, 0.1647, 0.1216, 0.0863, 0.0667],
                [0.0392, 0.0235, 0.0353, 0.0627, 0.0784, 0.0902, 0.0863, 0.0745, 0.0627, 0.0627, 0.0627]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0275, 0.0627, 0.0471, 0.0588, 0.0706],
                [0.0, 0.0, 0.0, 0.0, 0.0196, 0.0314, 0.0392, 0.0471, 0.0588, 0.0667, 0.0667],
                [1.0, 0.9373, 0.8196, 0.7059, 0.5765, 0.4549, 0.3373, 0.2392, 0.1647, 0.098, 0.0627]
            ]
        )

    elif filter == "Flat Black":
        filter_tuple = (
            [
                [1.0, 0.9098, 0.8392, 0.7608, 0.6392, 0.5176, 0.4314, 0.3216, 0.1569, 0.1569, 0.1569],
                [0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569],
                [0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569]
            ], [
                [0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569],
                [1.0, 0.9098, 0.8392, 0.7608, 0.6392, 0.5176, 0.4314, 0.3216, 0.1569, 0.1569, 0.1569],
                [0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569]
            ], [
                [0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569],
                [0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569, 0.1569],
                [1.0, 0.9098, 0.8392, 0.7608, 0.6392, 0.5176, 0.4314, 0.3216, 0.1569, 0.1569, 0.1569]
            ]
        )

    elif filter == "Mellow":
        filter_tuple = (
            [
                [1.0, 0.9412, 0.8784, 0.8196, 0.749, 0.6706, 0.5804, 0.4941, 0.3843, 0.2118, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.8471, 0.7608, 0.6745, 0.5922, 0.5059, 0.4235, 0.3373, 0.2549, 0.1686, 0.0824, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ], [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.5137, 0.4588, 0.4078, 0.3608, 0.3098, 0.2549, 0.2, 0.1529, 0.102, 0.051, 0.0]
            ]
        )

    elif filter == "Pumpkin":
        filter_tuple = (
            [
                [1.0, 1.0, 0.9216, 0.8078, 0.6863, 0.5647, 0.4392, 0.3216, 0.2039, 0.0941, 0.0],
                [0.0, 0.0, 0.0196, 0.0118, 0.0118, 0.0118, 0.0157, 0.0118, 0.0157, 0.0078, 0.0],
                [0.0393, 0.0393, 0.0157, 0.0275, 0.0157, 0.0235, 0.0157, 0.0078, 0.0078, 0.0039, 0.0]
            ], [
                [0.3295, 0.2079, 0.1059, 0.0628, 0.051, 0.0432, 0.0314, 0.0275, 0.0196, 0.0196, 0.0],
                [0.949, 0.8667, 0.7765, 0.6784, 0.5765, 0.4784, 0.3725, 0.2745, 0.1725, 0.0824, 0.0],
                [0.9922, 0.9137, 0.8275, 0.7294, 0.6235, 0.5098, 0.4, 0.2941, 0.1882, 0.0863, 0.0]
            ], [
                [0.0196, 0.0235, 0.0157, 0.0235, 0.0196, 0.0196, 0.0235, 0.0157, 0.0157, 0.0118, 0.0],
                [0.0393, 0.0353, 0.0236, 0.0275, 0.0157, 0.0196, 0.0157, 0.0078, 0.0118, 0.0078, 0.0],
                [0.8784, 0.7922, 0.702, 0.6157, 0.5176, 0.4275, 0.3333, 0.2471, 0.1569, 0.0745, 0.0]
            ]
        )

    elif filter == "Pale":
        filter_tuple = (
            [
                [0.9373, 0.8745, 0.7961, 0.7059, 0.6039, 0.502, 0.3882, 0.2863, 0.1843, 0.0863, 0.0],
                [0.2471, 0.2, 0.1569, 0.1177, 0.0902, 0.0667, 0.0549, 0.0353, 0.0275, 0.0118, 0.0],
                [0.1373, 0.1177, 0.102, 0.0824, 0.0667, 0.0471, 0.0353, 0.0157, 0.0118, 0.0078, 0.0]
            ], [
                [0.5647, 0.4824, 0.3961, 0.3137, 0.2314, 0.1529, 0.0902, 0.0549, 0.0314, 0.0196, 0.0],
                [0.8588, 0.8078, 0.7451, 0.6784, 0.5961, 0.502, 0.4039, 0.302, 0.1961, 0.0941, 0.0],
                [0.3059, 0.2627, 0.2275, 0.1922, 0.1569, 0.1216, 0.0863, 0.0627, 0.0353, 0.0118, 0.0]
            ], [
                [0.4706, 0.4039, 0.3412, 0.2824, 0.2235, 0.1686, 0.1137, 0.0745, 0.0431, 0.0157, 0.0],
                [0.1922, 0.1726, 0.153, 0.1295, 0.1098, 0.0863, 0.0588, 0.0431, 0.0196, 0.0118, 0.0],
                [0.7333, 0.6784, 0.6196, 0.5608, 0.4941, 0.4235, 0.3412, 0.2627, 0.1765, 0.0863, 0.0]
            ]
        )

    elif filter == "Summer":
        filter_tuple = (
            [
                [1.0, 0.9529, 0.8392, 0.7294, 0.6118, 0.4941, 0.3765, 0.2667, 0.1647, 0.0745, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.004, 0.0118, 0.0078, 0.0078, 0.0078, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0039, 0.0078, 0.0, 0.0]
            ], [
                [0.5725, 0.3883, 0.1883, 0.0275, 0.0079, 0.0, 0.0, 0.0039, 0.0118, 0.0118, 0.0],
                [0.898, 0.8706, 0.7922, 0.6902, 0.5843, 0.4784, 0.3608, 0.2588, 0.1569, 0.0706, 0.0],
                [0.3373, 0.0863, 0.0, 0.0039, 0.0196, 0.0157, 0.0196, 0.0196, 0.0157, 0.0118, 0.0]
            ], [
                [0.4157, 0.2588, 0.1059, 0.0314, 0.0, 0.0, 0.0, 0.0039, 0.0118, 0.0078, 0.0],
                [0.1295, 0.0628, 0.0628, 0.051, 0.0432, 0.0353, 0.0235, 0.0118, 0.0118, 0.0039, 0.0],
                [0.9216, 0.851, 0.7647, 0.6706, 0.5725, 0.4706, 0.3608, 0.2588, 0.1569, 0.0706, 0.0]
            ]
        )

    elif filter == "Tender":
        filter_tuple = (
            [
                [0.7294, 0.6549, 0.5843, 0.5098, 0.4392, 0.3647, 0.2902, 0.2196, 0.1451, 0.0863, 0.0549],
                [0.0079, 0.0, 0.0, 0.004, 0.0, 0.0118, 0.0039, 0.0196, 0.0275, 0.0275, 0.0235],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0078, 0.0118, 0.0157, 0.0157]
            ], [
                [0.3725, 0.2627, 0.1843, 0.1059, 0.0588, 0.0667, 0.0706, 0.0745, 0.0667, 0.0549, 0.0549],
                [0.851, 0.8078, 0.7412, 0.6588, 0.5569, 0.4549, 0.3529, 0.2549, 0.1608, 0.0824, 0.0235],
                [0.0549, 0.0039, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0157]
            ], [
                [0.1059, 0.0745, 0.0667, 0.051, 0.051, 0.0392, 0.0392, 0.0549, 0.0549, 0.0588, 0.0549],
                [0.0, 0.0118, 0.0235, 0.0235, 0.0275, 0.0275, 0.0275, 0.0275, 0.0275, 0.0235, 0.0235],
                [0.502, 0.4549, 0.4039, 0.3569, 0.3059, 0.251, 0.1961, 0.1373, 0.0745, 0.0235, 0.0157]
            ]
        )

    elif filter == "Twilight":
        filter_tuple = (
            [
                [1.0, 1.0, 0.902, 0.7608, 0.6118, 0.4627, 0.302, 0.1725, 0.0745, 0.0235, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0039, 0.0],
                [0.1098, 0.0981, 0.0824, 0.0628, 0.0471, 0.0314, 0.0157, 0.0118, 0.0078, 0.0039, 0.0]
            ], [
                [0.6784, 0.4471, 0.1177, 0.004, 0.0157, 0.0549, 0.0157, 0.0235, 0.0235, 0.0157, 0.0],
                [0.9882, 0.9843, 0.9333, 0.8196, 0.6275, 0.4353, 0.2824, 0.1608, 0.0706, 0.0196, 0.0],
                [0.0471, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0078, 0.0118, 0.0078, 0.0]
            ], [
                [0.2785, 0.004, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0118, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0039, 0.0078, 0.0039, 0.0, 0.0],
                [1.0, 1.0, 0.9529, 0.8431, 0.6863, 0.5098, 0.3373, 0.1961, 0.098, 0.0353, 0.0]
            ]
        )

    return (filter_tuple)
