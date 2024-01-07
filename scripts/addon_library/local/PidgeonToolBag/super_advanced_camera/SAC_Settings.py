import os
import bpy
import math

from bpy.types import (
    PropertyGroup,
)

from bpy.props import (
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    BoolProperty,
    PointerProperty,
    StringProperty,
)


class SAC_Settings(PropertyGroup):

    # EffectTypes
    effect_types = [
        ('SAC_BLUR', 'Blur', 'DISC'),
        ('SAC_BOKEH', 'Bokeh', 'SEQ_CHROMA_SCOPE'),
        ('SAC_CHROMATICABERRATION', 'Chromatic Aberation', 'MOD_EDGESPLIT'),
        ('SAC_DUOTONE', 'Duotone', 'MOD_TINT'),
        ('SAC_EMBOSS', 'Emboss', 'AXIS_TOP'),
        ('SAC_FILMGRAIN', 'Film Grain', 'ALIGN_FLUSH'),
        ('SAC_FISHEYE', 'Fish Eye', 'MESH_UVSPHERE'),
        ('SAC_FOGGLOW', 'Fog Glow', 'ALIGN_FLUSH'),
        ('SAC_GHOST', 'Ghost', 'GHOST_DISABLED'),
        ('SAC_GRADIENTMAP', 'Gradient Map', 'SNAP_INCREMENT'),
        ('SAC_HALFTONE', 'Halftone', 'LIGHTPROBE_GRID'),
        ('SAC_HDR', 'HDR', 'IMAGE_RGB_ALPHA'),
        ('SAC_INFRARED', 'Infrared', 'OUTLINER_DATA_LIGHT'),
        ('SAC_ISONOISE', 'ISO Noise', 'ALIGN_FLUSH'),
        ('SAC_MOSAIC', 'Mosaic', 'MOD_UVPROJECT'),
        ('SAC_NEGATIVE', 'Negative', 'SELECT_DIFFERENCE'),
        ('SAC_OVERLAY', 'Overlay', 'XRAY'),
        ('SAC_PERSPECTIVESHIFT', 'Perspective Shift', 'VIEW_PERSPECTIVE'),
        ('SAC_POSTERIZE', 'Posterize', 'IMAGE_ZDEPTH'),
        ('SAC_STREAKS', 'Streaks', 'LIGHT_SUN'),
        ('SAC_VIGNETTE', 'Vignette', 'CLIPUV_DEHLT'),
        ('SAC_WARP', 'Warp', 'MOD_WARP'),
        ('SAC_GLITCH', 'Glitch', 'LIBRARY_DATA_BROKEN'),
        ('SAC_OILPAINT', 'Oil Paint', 'MOD_FLUIDSIM'),
        ('SAC_POINTILLISM', 'Pointillism', 'PARTICLE_POINT'),
        ('SAC_SKETCH', 'Sketch', 'GREASEPENCIL'),
        ('SAC_WATERCOLOR', 'Watercolor', 'BRUSHES_ALL'),
    ]

    gradient_types = [
        ("Platinum", "Platinum"),
        ("Selenium 1", "Selenium 1"),
        ("Selenium 2", "Selenium 2"),
        ("Sepia 1", "Sepia 1"),
        ("Sepia 2", "Sepia 2"),
        ("Sepia 3", "Sepia 3"),
        ("Sepia 4", "Sepia 4"),
        ("Sepia 5", "Sepia 5"),
        ("Sepia 6", "Sepia 6"),
        ("Sepia Highlights 1", "Sepia Highlights 1"),
        ("Sepia Highlights 2", "Sepia Highlights 2"),
        ("Sepia Midtones", "Sepia Midtones"),
        ("Gold 1", "Gold 1"),
        ("Gold 2", "Gold 2"),
        ("Blue 1", "Blue 1"),
        ("Blue 2", "Blue 2"),
        ("Cyanotype", "Cyanotype"),
        ("Copper 1", "Copper 1"),
        ("Copper 2", "Copper 2"),
        ("Sepia-Selenium 1", "Sepia-Selenium 1"),
        ("Sepia-Selenium 2", "Sepia-Selenium 2"),
        ("Sepia-Selenium 3", "Sepia-Selenium 3"),
        ("Sepia-Cyan", "Sepia-Cyan"),
        ("Sepia-Blue 1", "Sepia-Blue 1"),
        ("Sepia-Blue 2", "Sepia-Blue 2"),
        ("Gold-Sepia", "Gold-Sepia"),
        ("Gold-Selenium 1", "Gold-Selenium 1"),
        ("Gold-Selenium 2", "Gold-Selenium 2"),
        ("Gold-Copper", "Gold-Copper"),
        ("Gold-Blue", "Gold-Blue"),
        ("Blue-Selenium 1", "Blue-Selenium 1"),
        ("Blue-Selenium 2", "Blue-Selenium 2"),
        ("Cyan-Selenium", "Cyan-Selenium"),
        ("Cyan-Sepia", "Cyan-Sepia"),
        ("Copper-Sepia", "Copper-Sepia"),
        ("Cobalt-Iron 1", "Cobalt-Iron 1"),
        ("Cobalt-Iron 2", "Cobalt-Iron 2"),
        ("Cobalt-Iron 3", "Cobalt-Iron 3"),
        ("Hard", "Hard"),
        ("Skies", "Skies"),
    ]

    # Slow Effects
    slow_effects = [
    ]

    bokeh_types = [
        ("CarlZeiss_ContaxPlanar_f2.8_60mm_f2.8", "Carl Zeiss - Contax Planar - 60mm - f/2.8"),
        ("CarlZeiss_ContaxPlanar_f2.8_60mm_f4.0", "Carl Zeiss - Contax Planar - 60mm - f/4.0"),
        ("CarlZeiss_ContaxPlanar_f2.8_60mm_f5.6", "Carl Zeiss - Contax Planar - 60mm - f/5.6"),
        ("CarlZeiss_ContaxPlanar_f2.8_60mm_f8.0", "Carl Zeiss - Contax Planar - 60mm - f/8.0"),
        ("CarlZeiss_ContaxPlanar_f2.8_60mm_f11.0", "Carl Zeiss - Contax Planar - 60mm - f/11.0"),
        ("CarlZeiss_ContaxPlanar_f2.8_60mm_f16.0", "Carl Zeiss - Contax Planar - 60mm - f/16.0"),
        ("CarlZeiss_ContaxPlanar_f2.8_60mm_f22.0", "Carl Zeiss - Contax Planar - 60mm - f/22.0"),

        ("Centon_Centon_2.15m_500mm_f8.0", "Centon - Centon - 500mm - f/8.0 - focus on 2.15m"),
        ("Centon_Centon_Infinity_500mm_f8.0", "Centon - Centon - 500mm - f/8.0 - focus on infinity"),

        ("Cosina_Cosinon_f4.0_200mm_f4.0", "Cosina - Cosinon - 200mm - f/4.0"),
        ("Cosina_Cosinon_f4.0_200mm_f5.6", "Cosina - Cosinon - 200mm - f/5.6"),
        ("Cosina_Cosinon_f4.0_200mm_f8.0", "Cosina - Cosinon - 200mm - f/8.0"),
        ("Cosina_Cosinon_f4.0_200mm_f11.0", "Cosina - Cosinon - 200mm - f/11.0"),
        ("Cosina_Cosinon_f4.0_200mm_f16.0", "Cosina - Cosinon - 200mm - f/16.0"),
        ("Cosina_Cosinon_f4.0_200mm_f22.0", "Cosina - Cosinon - 200mm - f/22.0"),

        ("Jupiter_9_f2.0_85mm_f2.0", "Jupiter - 9 - 85mm - f/2.0"),
        ("Jupiter_9_f2.0_85mm_f2.8", "Jupiter - 9 - 85mm - f/2.8"),
        ("Jupiter_9_f2.0_85mm_f4.0", "Jupiter - 9 - 85mm - f/4.0"),
        ("Jupiter_9_f2.0_85mm_f5.6", "Jupiter - 9 - 85mm - f/5.6"),
        ("Jupiter_9_f2.0_85mm_f8.0", "Jupiter - 9 - 85mm - f/8.0"),
        ("Jupiter_9_f2.0_85mm_f11.0", "Jupiter - 9 - 85mm - f/11.0"),
        ("Jupiter_9_f2.0_85mm_f16.0", "Jupiter - 9 - 85mm - f/16.0"),

        ("Olympus_OmZuiko_f2.8_100mm_f2.8", "Olympus - OmZuiko - 100mm - f/2.8"),
        ("Olympus_OmZuiko_f2.8_100mm_f4.0", "Olympus - OmZuiko - 100mm - f/4.0"),
        ("Olympus_OmZuiko_f2.8_100mm_f5.6", "Olympus - OmZuiko - 100mm - f/5.6"),
        ("Olympus_OmZuiko_f2.8_100mm_f8.0", "Olympus - OmZuiko - 100mm - f/8.0"),
        ("Olympus_OmZuiko_f2.8_100mm_f11.0", "Olympus - OmZuiko - 100mm - f/11.0"),

        ("Pentax_SMC_f2.0_50mm_f2.0", "Pentax - SMC - 50mm - f/2.0"),
        ("Pentax_SMC_f2.0_50mm_f2.8", "Pentax - SMC - 50mm - f/2.8"),
        ("Pentax_SMC_f2.0_50mm_f4.0", "Pentax - SMC - 50mm - f/4.0"),
        ("Pentax_SMC_f2.0_50mm_f5.6", "Pentax - SMC - 50mm - f/5.6"),
        ("Pentax_SMC_f2.0_50mm_f8.0", "Pentax - SMC - 50mm - f/8.0"),
        ("Pentax_SMC_f2.0_50mm_f11.0", "Pentax - SMC - 50mm - f/11.0"),

        ("Takumar_SMC_f3.5_135mm_f3.5", "Takumar - SMC - 135mm - f/3.5"),
        ("Takumar_SMC_f3.5_135mm_f5.6", "Takumar - SMC - 135mm - f/5.6"),
        ("Takumar_SMC_f3.5_135mm_f8.0", "Takumar - SMC - 135mm - f/8.0"),
        ("Takumar_SMC_f3.5_135mm_f11.0", "Takumar - SMC - 135mm - f/11.0"),
        ("Takumar_SMC_f3.5_135mm_f16.0", "Takumar - SMC - 135mm - f/16.0"),
        ("Takumar_SMC_f3.5_135mm_f22.0", "Takumar - SMC - 135mm - f/22.0"),

        ("Takumar_Super_f1.4_50mm_f1.4", "Takumar - Super - 50mm - f/1.4"),
        ("Takumar_Super_f1.4_50mm_f2.0", "Takumar - Super - 50mm - f/2.0"),
        ("Takumar_Super_f1.4_50mm_f2.8", "Takumar - Super - 50mm - f/2.8"),
        ("Takumar_Super_f1.4_50mm_f4.0", "Takumar - Super - 50mm - f/4.0"),
        ("Takumar_Super_f1.4_50mm_f5.6", "Takumar - Super - 50mm - f/5.6"),
        ("Takumar_Super_f1.4_50mm_f8.0", "Takumar - Super - 50mm - f/8.0"),

        ("Takumar_Super_f1.8_55mm_f1.8", "Takumar - Super - 55mm - f/1.8"),
        ("Takumar_Super_f1.8_55mm_f2.8", "Takumar - Super - 55mm - f/2.8"),
        ("Takumar_Super_f1.8_55mm_f4.0", "Takumar - Super - 55mm - f/4.0"),
        ("Takumar_Super_f1.8_55mm_f5.6", "Takumar - Super - 55mm - f/5.6"),
        ("Takumar_Super_f1.8_55mm_f8.0", "Takumar - Super - 55mm - f/8.0"),

        ("Takumar_Super_f2.0_55mm_f2.0", "Takumar - Super - 55mm - f/2.0"),
        ("Takumar_Super_f2.0_55mm_f2.8", "Takumar - Super - 55mm - f/2.8"),
        ("Takumar_Super_f2.0_55mm_f4.0", "Takumar - Super - 55mm - f/4.0"),
        ("Takumar_Super_f2.0_55mm_f5.6", "Takumar - Super - 55mm - f/5.6"),
        ("Takumar_Super_f2.0_55mm_f8.0", "Takumar - Super - 55mm - f/8.0"),

        ("Takumar_Super_f4.0_150mm_f4.0", "Takumar - Super - 150mm - f/4.0"),
        ("Takumar_Super_f4.0_150mm_f5.6", "Takumar - Super - 150mm - f/5.6"),
        ("Takumar_Super_f4.0_150mm_f8.0", "Takumar - Super - 150mm - f/8.0"),
        ("Takumar_Super_f4.0_150mm_f11.0", "Takumar - Super - 150mm - f/11.0"),
        ("Takumar_Super_f4.0_150mm_f16.0", "Takumar - Super - 150mm - f/16.0"),
        ("Takumar_Super_f4.0_150mm_f22.0", "Takumar - Super - 150mm - f/22.0"),

        ("Tamron_Adaptall_f2.5_90mm_f2.5", "Tamron - Adaptall - 90mm - f/2.5"),
        ("Tamron_Adaptall_f2.5_90mm_f4.0", "Tamron - Adaptall - 90mm - f/4.0"),
        ("Tamron_Adaptall_f2.5_90mm_f5.6", "Tamron - Adaptall - 90mm - f/5.6"),
        ("Tamron_Adaptall_f2.5_90mm_f8.0", "Tamron - Adaptall - 90mm - f/8.0"),
        ("Tamron_Adaptall_f2.5_90mm_f11.0", "Tamron - Adaptall - 90mm - f/11.0"),
        ("Tamron_Adaptall_f2.5_90mm_f16.0", "Tamron - Adaptall - 90mm - f/16.0"),
        ("Tamron_Adaptall_f2.5_90mm_f22.0", "Tamron - Adaptall - 90mm - f/22.0"),

        ("Tamron_Adaptall55bb_2m_500mm_f8.0", "Tamron - Adaptall 55bb - 500mm - f/8.0 - focus on 2m"),
        ("Tamron_Adaptall55bb_Infinity_500mm_f8.0", "Tamron - Adaptall 55bb - 500mm - f/8.0 - focus on infinity"),

        ("Topman_MC_f2.8_135mm_f2.8", "Topman - MC - 135mm - f/2.8"),
        ("Topman_MC_f2.8_135mm_f4.0", "Topman - MC - 135mm - f/4.0"),
        ("Topman_MC_f2.8_135mm_f5.6", "Topman - MC - 135mm - f/5.6"),
        ("Topman_MC_f2.8_135mm_f8.0", "Topman - MC - 135mm - f/8.0"),
        ("Topman_MC_f2.8_135mm_f11.0", "Topman - MC - 135mm - f/11.0"),
        ("Topman_MC_f2.8_135mm_f16.0", "Topman - MC - 135mm - f/16.0"),
        ("Topman_MC_f2.8_135mm_f22.0", "Topman - MC - 135mm - f/22.0"),

        ("Vivitar_Vivitar_f2.8_55mm_f2.8", "Vivitar - Vivitar - 55mm - f/2.8"),
        ("Vivitar_Vivitar_f2.8_55mm_f4.0", "Vivitar - Vivitar - 55mm - f/4.0"),
        ("Vivitar_Vivitar_f2.8_55mm_f5.6", "Vivitar - Vivitar - 55mm - f/5.6"),
        ("Vivitar_Vivitar_f2.8_55mm_f8.0", "Vivitar - Vivitar - 55mm - f/8.0"),
        ("Vivitar_Vivitar_f2.8_55mm_f11.0", "Vivitar - Vivitar - 55mm - f/11.0"),
        ("Vivitar_Vivitar_f2.8_55mm_f16.0", "Vivitar - Vivitar - 55mm - f/16.0"),
    ]

    filter_types_bw = (
        ("1920", "1920"),
        ("Dusty", "Dusty"),
        ("Grayed", "Grayed"),
        ("Litho", "Litho"),
        ("Sepia", "Sepia"),
        ("Steel", "Steel"),
        ("Weathered", "Weathered")
    )
    filter_types_vintage = (
        ("Ancient", "Ancient"),
        ("Classic", "Classic"),
        ("Inferno", "Inferno"),
        ("Lomo", "Lomo"),
        ("Lomo 100", "Lomo 100"),
        ("Oldtimer", "Oldtimer"),
        ("Pola SX", "Pola SX"),
        ("Polaroid", "Polaroid"),
        ("Quozi", "Quozi"),
        ("Seventies", "Seventies"),
        ("Snappy", "Snappy"),
        ("Sunny 70s", "Sunny 70s")
    )
    filter_types_neat = (
        ("Candy", "Candy"),
        ("Chestnut", "Chestnut"),
        ("Creamy", "Creamy"),
        ("Fixie", "Fixie"),
        ("Food", "Food"),
        ("Glam", "Glam"),
        ("Goblin", "Goblin"),
        ("Green Gap", "Green Gap"),
        ("High Carb", "High Carb"),
        ("High Contrast", "High Contrast"),
        ("K1", "K1"),
        ("K6", "K6"),
        ("Keen", "Keen"),
        ("Lucid", "Lucid"),
        ("Moss", "Moss"),
        ("Neat", "Neat"),
        ("Pebble", "Pebble"),
        ("Pro 400", "Pro 400"),
        ("Soft", "Soft"),
        ("Softy", "Softy")
    )
    filter_types_cold = (
        ("Colla", "Colla"),
        ("Fridge", "Fridge"),
        ("Joran", "Joran"),
        ("Kalmen", "Kalmen"),
        ("Levante", "Levante"),
        ("Pitched", "Pitched"),
        ("Settled", "Settled"),
        ("Solanus", "Solanus"),
        ("Zephyr", "Zephyr")
    )
    filter_types_warm = (
        ("Flat Black", "Flat Black"),
        ("Golden", "Golden"),
        ("Low Fire", "Low Fire"),
        ("Pale", "Pale"),
        ("Pumpkin", "Pumpkin"),
        ("Summer", "Summer"),
        ("Sunrise", "Sunrise"),
        ("Tender", "Tender"),
        ("Twilight", "Twilight")
    )
    filter_types = [
        ("Default", "Default")
    ]

    filter_types.extend(filter_types_bw)
    filter_types.extend(filter_types_vintage)
    filter_types.extend(filter_types_neat)
    filter_types.extend(filter_types_cold)
    filter_types.extend(filter_types_warm)

    def update_filter_type(self, context):

        scene = bpy.context.scene
        settings = scene.sac_settings

        filter_types = self.filter_types

        filter_types = [
            ("Default", "Default")
        ]

        if settings.filter_type == "BW":
            filter_types.extend(self.filter_types_bw)
        elif settings.filter_type == "Vintage":
            filter_types.extend(self.filter_types_vintage)
        elif settings.filter_type == "Neat":
            filter_types.extend(self.filter_types_neat)
        elif settings.filter_type == "Cold":
            filter_types.extend(self.filter_types_cold)
        elif settings.filter_type == "Warm":
            filter_types.extend(self.filter_types_warm)
        else:
            filter_types.extend(self.filter_types_bw)
            filter_types.extend(self.filter_types_vintage)
            filter_types.extend(self.filter_types_neat)
            filter_types.extend(self.filter_types_cold)
            filter_types.extend(self.filter_types_warm)

        scene.new_filter_type = "Default"
        settings.filter_types = filter_types

    filter_type: EnumProperty(
        name="Filter Type",
        description="Filter the fitlter list by type",
        items=(
            ("All", "All", "All filters", "WORLD", 0),
            ("BW", "Black and White", "An assortment of monochrome filters", "OVERLAY", 1),
            ("Vintage", "Vintage", "An assortment of vintage filters", "DISC", 2),
            ("Neat", "Neat", "An assortment of neat filters", "BOIDS", 3),
            ("Cold", "Cold", "An assortment of cold filters", "FREEZE", 4),
            ("Warm", "Warm", "An assortment of warm filters", "LIGHT_SUN", 5),
        ),
        default="All",
        update=update_filter_type
    )

    # region Colorgrade

    # Enable/Diable Colorgrade
    def update_Colorgrade_Enable(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups["Super Advanced Camera"].nodes[".SAC Colorgrade"].mute = not settings.Colorgrade_Enable

    Colorgrade_Enable: BoolProperty(
        name="Toggle Colorgrade",
        description="Enable/Disable Colorgrade",
        default=True,
        update=update_Colorgrade_Enable
    )

    # White Level
    def update_Colorgrade_Color_WhiteLevel(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC WhiteLevel"].nodes["SAC Colorgrade_Color_WhiteLevel"].inputs[3].default_value[0] = settings.Colorgrade_Color_WhiteLevel[0]
        bpy.data.node_groups[".SAC WhiteLevel"].nodes["SAC Colorgrade_Color_WhiteLevel"].inputs[3].default_value[1] = settings.Colorgrade_Color_WhiteLevel[1]
        bpy.data.node_groups[".SAC WhiteLevel"].nodes["SAC Colorgrade_Color_WhiteLevel"].inputs[3].default_value[2] = settings.Colorgrade_Color_WhiteLevel[2]

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC WhiteLevel"].mute = False
        if (
            settings.Colorgrade_Color_WhiteLevel[0] == 1 and
            settings.Colorgrade_Color_WhiteLevel[1] == 1 and
            settings.Colorgrade_Color_WhiteLevel[2] == 1
        ):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC WhiteLevel"].mute = True

    Colorgrade_Color_WhiteLevel: FloatVectorProperty(
        name="White Balance",
        description="Adjusts the overall color tone of an image to make it appear more natural,\ncompensating for the color temperature of the light source",
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        subtype="COLOR",
        update=update_Colorgrade_Color_WhiteLevel
    )

    # Temperature

    def update_Colorgrade_Color_Temperature(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Temperature"].nodes["SAC Colorgrade_Color_Temperature"].inputs[0].default_value = settings.Colorgrade_Color_Temperature

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Temperature"].mute = False
        if settings.Colorgrade_Color_Temperature == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Temperature"].mute = True

    Colorgrade_Color_Temperature: FloatProperty(
        name="Temperature",
        description="Adjusts the color balance of an image,\nmaking it cooler (bluer) or warmer (more orange)",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Color_Temperature
    )

    # Tint
    def update_Colorgrade_Color_Tint(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Tint"].nodes["SAC Colorgrade_Color_Tint"].inputs[0].default_value = settings.Colorgrade_Color_Tint

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Tint"].mute = False
        if settings.Colorgrade_Color_Tint == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Tint"].mute = True

    Colorgrade_Color_Tint: FloatProperty(
        name="Tint",
        description="Adjusts the green-magenta balance in an image,\ncompensating for color cast from certain light sources",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Color_Tint
    )

    # Saturation
    def update_Colorgrade_Color_Saturation(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Saturation"].nodes["SAC Colorgrade_Color_Saturation"].inputs[2].default_value = settings.Colorgrade_Color_Saturation

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Saturation"].mute = False
        if (settings.Colorgrade_Color_Saturation == 1) and (settings.Colorgrade_Color_Hue == 0.5):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Saturation"].mute = True

    Colorgrade_Color_Saturation: FloatProperty(
        name="Saturation",
        description="Increases or decreases the intensity of colors in an image, from vivid to gray",
        default=1,
        max=2,
        min=0,
        subtype="FACTOR",
        update=update_Colorgrade_Color_Saturation
    )

    # Hue1
    def update_Colorgrade_Color_Hue(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Saturation"].nodes["SAC Colorgrade_Color_Saturation"].inputs[1].default_value = settings.Colorgrade_Color_Hue

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Saturation"].mute = False
        if (settings.Colorgrade_Color_Hue == 0.5) and (settings.Colorgrade_Color_Saturation == 1):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Saturation"].mute = True

    Colorgrade_Color_Hue: FloatProperty(
        name="Hue",
        description="Rotates the hue of all colors in the image around the color wheel",
        default=0.5,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Colorgrade_Color_Hue
    )

    # LIGHT

    # Exposure
    def update_Colorgrade_Light_Exposure(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Exposure"].nodes["SAC Colorgrade_Light_Exposure"].inputs[1].default_value = settings.Colorgrade_Light_Exposure

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Exposure"].mute = False
        if settings.Colorgrade_Light_Exposure == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Exposure"].mute = True

    Colorgrade_Light_Exposure: FloatProperty(
        name="Exposure",
        description="Adjusts the overall brightness of the image",
        default=0,
        max=10,
        soft_max=5,
        min=-10,
        soft_min=-5,
        subtype="FACTOR",
        update=update_Colorgrade_Light_Exposure
    )

    # Contrast
    def update_Colorgrade_Light_Contrast(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Contrast"].nodes["SAC Colorgrade_Light_Contrast"].inputs[2].default_value = settings.Colorgrade_Light_Contrast

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Contrast"].mute = False
        if settings.Colorgrade_Light_Contrast == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Contrast"].mute = True

    Colorgrade_Light_Contrast: FloatProperty(
        name="Contrast",
        description="Modifies the difference between the darkest and lightest parts of an image,\nmaking shadows deeper and highlights brighter",
        default=0,
        max=100,
        soft_max=25,
        min=-100,
        soft_min=-25,
        subtype="FACTOR",
        update=update_Colorgrade_Light_Contrast
    )

    # Highlights
    def update_Colorgrade_Light_Highlights(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Highlights"].nodes["SAC Colorgrade_Light_Highlights"].inputs[0].default_value = settings.Colorgrade_Light_Highlights

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Highlights"].mute = False
        if settings.Colorgrade_Light_Highlights == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Highlights"].mute = True

    Colorgrade_Light_Highlights: FloatProperty(
        name="Highlights",
        description="Adjusts the brightness of the brightest parts of the image",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Light_Highlights
    )

    # Shadows
    def update_Colorgrade_Light_Shadows(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Shadows"].nodes["SAC Colorgrade_Light_Shadows"].inputs[0].default_value = settings.Colorgrade_Light_Shadows

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Shadows"].mute = False
        if settings.Colorgrade_Light_Shadows == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Shadows"].mute = True

    Colorgrade_Light_Shadows: FloatProperty(
        name="Shadows",
        description="Adjusts the brightness of the darkest parts of the image",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Light_Shadows
    )

    # Whites
    def update_Colorgrade_Light_Whites(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Whites"].nodes["SAC Colorgrade_Light_Whites"].inputs[0].default_value = settings.Colorgrade_Light_Whites

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Whites"].mute = False
        if settings.Colorgrade_Light_Whites == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Whites"].mute = True

    Colorgrade_Light_Whites: FloatProperty(
        name="Whites",
        description="Adjusts the luminance level of the very brightest parts of the image,\nhelping to set the white point",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Light_Whites
    )

    # Darks
    def update_Colorgrade_Light_Darks(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Darks"].nodes["SAC Colorgrade_Light_Darks"].inputs[0].default_value = settings.Colorgrade_Light_Darks

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Darks"].mute = False
        if settings.Colorgrade_Light_Darks == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Darks"].mute = True

    Colorgrade_Light_Darks: FloatProperty(
        name="Darks",
        description="Adjusts the luminance level of the very darkest parts of the image,\nhelping to set the black point",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Light_Darks
    )

    # Presets

    # Filter Mix
    def update_Colorgrade_Filter_Mix(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Filter"].nodes["SAC Colorgrade_Filter_Mix"].inputs[0].default_value = settings.Colorgrade_Filter_Mix

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Filter"].mute = False
        if settings.Colorgrade_Filter_Mix == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Filter"].mute = True

    Colorgrade_Filter_Mix: FloatProperty(
        name="Filter Blend",
        description="Adjusts the blend between the original image and the filter",
        default=0.5,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Filter_Mix
    )

    # Extension
    def update_Colorgrade_Filter_Extension(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings

        if settings.Colorgrade_Filter_Extension:
            extend = "HORIZONTAL"
        else:
            extend = "EXTRAPOLATED"

        bpy.data.node_groups[".SAC Filter"].nodes["SAC Colorgrade_Filter_Blue"].mapping.extend = extend
        bpy.data.node_groups[".SAC Filter"].nodes["SAC Colorgrade_Filter_Green"].mapping.extend = extend
        bpy.data.node_groups[".SAC Filter"].nodes["SAC Colorgrade_Filter_Red"].mapping.extend = extend

    Colorgrade_Filter_Extension: BoolProperty(
        name="Extreme Value Correction",
        description="The filter may run into issues at high/low brightness values (above 1 or below 0).\nThis setting eliminates that by clamping the brightness",
        default=True,
        update=update_Colorgrade_Filter_Extension
    )

    # Sharpen

    def update_Colorgrade_Presets_Sharpen(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Sharpen"].nodes["SAC Colorgrade_Presets_Sharpen"].outputs[0].default_value = settings.Colorgrade_Presets_Sharpen

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Sharpen"].mute = False
        if settings.Colorgrade_Presets_Sharpen == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Sharpen"].mute = True

    Colorgrade_Presets_Sharpen: FloatProperty(
        name="Sharpen",
        description="Increases the contrast of edges in the image,\nmaking them appear more defined",
        default=0,
        max=5,
        soft_max=2,
        min=-5,
        soft_min=-2,
        subtype="FACTOR",
        update=update_Colorgrade_Presets_Sharpen
    )

    # Vibrance
    def update_Colorgrade_Presets_Vibrance(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Vibrance"].nodes["SAC Colorgrade_Presets_Vibrance"].inputs[2].default_value = settings.Colorgrade_Presets_Vibrance + 1

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Vibrance"].mute = False
        if settings.Colorgrade_Presets_Vibrance == 0:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Vibrance"].mute = True

    Colorgrade_Presets_Vibrance: FloatProperty(
        name="Vibrance",
        description="Increases the intensity of the more muted colors in the image,\nwithout affecting the already saturated colors",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Presets_Vibrance
    )

    # Saturation
    def update_Colorgrade_Presets_Saturation(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Saturation2"].nodes["SAC Colorgrade_Presets_Saturation"].inputs[2].default_value = settings.Colorgrade_Presets_Saturation

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Saturation2"].mute = False
        if settings.Colorgrade_Presets_Saturation == 1:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Saturation2"].mute = True

    Colorgrade_Presets_Saturation: FloatProperty(
        name="Saturation",
        description="Increases or decreases the intensity of colors in an image, from vivid to gray",
        default=1,
        max=2,
        min=0,
        subtype="FACTOR",
        update=update_Colorgrade_Presets_Saturation
    )

    # Highlight Tint
    def update_Colorgrade_Presets_HighlightTint(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC HighlightTint"].nodes["SAC Colorgrade_Presets_HighlightTint"].inputs[2].default_value[0] = settings.Colorgrade_Presets_HighlightTint[0]
        bpy.data.node_groups[".SAC HighlightTint"].nodes["SAC Colorgrade_Presets_HighlightTint"].inputs[2].default_value[1] = settings.Colorgrade_Presets_HighlightTint[1]
        bpy.data.node_groups[".SAC HighlightTint"].nodes["SAC Colorgrade_Presets_HighlightTint"].inputs[2].default_value[2] = settings.Colorgrade_Presets_HighlightTint[2]

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC HighlightTint"].mute = False
        if (
            settings.Colorgrade_Presets_HighlightTint[0] == 1 and
            settings.Colorgrade_Presets_HighlightTint[1] == 1 and
            settings.Colorgrade_Presets_HighlightTint[2] == 1
        ):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC HighlightTint"].mute = True

    Colorgrade_Presets_HighlightTint: FloatVectorProperty(
        name="Highlight Tint",
        description="Alters the color tint specifically in the highlight regions of an image",
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        subtype="COLOR",
        update=update_Colorgrade_Presets_HighlightTint
    )

    # Shadow Tint
    def update_Colorgrade_Presets_ShadowTint(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC ShadowTint"].nodes["SAC Colorgrade_Presets_ShadowTint"].inputs[2].default_value[0] = settings.Colorgrade_Presets_ShadowTint[0]
        bpy.data.node_groups[".SAC ShadowTint"].nodes["SAC Colorgrade_Presets_ShadowTint"].inputs[2].default_value[1] = settings.Colorgrade_Presets_ShadowTint[1]
        bpy.data.node_groups[".SAC ShadowTint"].nodes["SAC Colorgrade_Presets_ShadowTint"].inputs[2].default_value[2] = settings.Colorgrade_Presets_ShadowTint[2]

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC ShadowTint"].mute = False
        if (
            settings.Colorgrade_Presets_ShadowTint[0] == 1 and
            settings.Colorgrade_Presets_ShadowTint[1] == 1 and
            settings.Colorgrade_Presets_ShadowTint[2] == 1
        ):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC ShadowTint"].mute = True

    Colorgrade_Presets_ShadowTint: FloatVectorProperty(
        name="Shadow Tint",
        description="Alters the color tint specifically in the shadow regions of an image",
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        subtype="COLOR",
        update=update_Colorgrade_Presets_ShadowTint
    )

    # RGB Curves
    def update_Colorgrade_Curves_RGB_Intensity(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Curves"].nodes["SAC Colorgrade_Curves_RGB"].inputs[0].default_value = settings.Colorgrade_Curves_RGB_Intensity

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Curves"].mute = False
        if (settings.Colorgrade_Curves_RGB_Intensity == 0) and (settings.Colorgrade_Curves_HSV_Intensity == 0):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Curves"].mute = True

    Colorgrade_Curves_RGB_Intensity: FloatProperty(
        name="RGB Curves Intensity",
        description="Adjusts the blend between the original image and the curves",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Colorgrade_Curves_RGB_Intensity
    )

    # HSV Curves
    def update_Colorgrade_Curves_HSV_Intensity(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Curves"].nodes["SAC Colorgrade_Curves_HSV"].inputs[0].default_value = settings.Colorgrade_Curves_HSV_Intensity

        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Curves"].mute = False
        if (settings.Colorgrade_Curves_RGB_Intensity == 0) and (settings.Colorgrade_Curves_HSV_Intensity == 0):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Curves"].mute = True

    Colorgrade_Curves_HSV_Intensity: FloatProperty(
        name="HSV Curves Intensity",
        description="Adjusts the blend between the original image and the curves",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Colorgrade_Curves_HSV_Intensity
    )

    # Colorwheel

    # Lift Brightness
    def update_Colorgrade_Colorwheel_Shadows_Brightness(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Shadows_Brightness"].inputs[0].default_value = settings.Colorgrade_Colorwheel_Shadows_Brightness

    Colorgrade_Colorwheel_Shadows_Brightness: FloatProperty(
        name="Shadows Brightness",
        description="Adjusts the brightness of the darkest parts of the image",
        default=1,
        max=2,
        min=-2,
        soft_min=0,
        subtype="FACTOR",
        update=update_Colorgrade_Colorwheel_Shadows_Brightness
    )

    # Lift Intensity
    def update_Colorgrade_Colorwheel_Shadows_Intensity(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Shadows"].inputs[0].default_value = settings.Colorgrade_Colorwheel_Shadows_Intensity

        if (settings.Colorgrade_Colorwheel_Highlights_Intensity == 0) and (settings.Colorgrade_Colorwheel_Midtones_Intensity == 0) and (settings.Colorgrade_Colorwheel_Shadows_Intensity == 0):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Colorwheel"].mute = True
        else:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Colorwheel"].mute = False

    Colorgrade_Colorwheel_Shadows_Intensity: FloatProperty(
        name="Shadows Colorwheel Intensity",
        description="Adjusts the blend between the original image and the colorwheel",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Colorwheel_Shadows_Intensity
    )

    # Gamma Brightness
    def update_Colorgrade_Colorwheel_Midtones_Brightness(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Midtones_Brightness"].inputs[0].default_value = settings.Colorgrade_Colorwheel_Midtones_Brightness

    Colorgrade_Colorwheel_Midtones_Brightness: FloatProperty(
        name="Midtones Brightness",
        description="Adjusts the brightness of the midtones of the image",
        default=1,
        max=2,
        min=-2,
        soft_min=0,
        subtype="FACTOR",
        update=update_Colorgrade_Colorwheel_Midtones_Brightness
    )

    # Gamma Intensity
    def update_Colorgrade_Colorwheel_Midtones_Intensity(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Midtones"].inputs[0].default_value = settings.Colorgrade_Colorwheel_Midtones_Intensity

        if (settings.Colorgrade_Colorwheel_Highlights_Intensity == 0) and (settings.Colorgrade_Colorwheel_Midtones_Intensity == 0) and (settings.Colorgrade_Colorwheel_Shadows_Intensity == 0):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Colorwheel"].mute = True
        else:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Colorwheel"].mute = False

    Colorgrade_Colorwheel_Midtones_Intensity: FloatProperty(
        name="Midtones Colorwheel Intensity",
        description="Adjusts the blend between the original image and the colorwheel",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Colorwheel_Midtones_Intensity
    )

    # Lift Brightness
    def update_Colorgrade_Colorwheel_Highlights_Brightness(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Highlights_Brightness"].inputs[0].default_value = settings.Colorgrade_Colorwheel_Highlights_Brightness

    Colorgrade_Colorwheel_Highlights_Brightness: FloatProperty(
        name="Highlights Brightness",
        description="Adjusts the brightness of the brightest parts of the image",
        default=1,
        max=2,
        min=-2,
        soft_min=0,
        subtype="FACTOR",
        update=update_Colorgrade_Colorwheel_Highlights_Brightness
    )

    # Lift Intensity
    def update_Colorgrade_Colorwheel_Highlights_Intensity(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups[".SAC Colorwheel"].nodes["SAC Colorgrade_Colorwheel_Highlights"].inputs[0].default_value = settings.Colorgrade_Colorwheel_Highlights_Intensity

        if (settings.Colorgrade_Colorwheel_Highlights_Intensity == 0) and (settings.Colorgrade_Colorwheel_Midtones_Intensity == 0) and (settings.Colorgrade_Colorwheel_Shadows_Intensity == 0):
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Colorwheel"].mute = True
        else:
            bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Colorwheel"].mute = False

    Colorgrade_Colorwheel_Highlights_Intensity: FloatProperty(
        name="Highlights Colorwheel Intensity",
        description="Adjusts the blend between the original image and the colorwheel",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Colorgrade_Colorwheel_Highlights_Intensity
    )

    # endregion Colorgrade

    # region Effects

    # Enable/Diable Effects
    def update_Effects_Enable(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        bpy.data.node_groups["Super Advanced Camera"].nodes[".SAC Effects"].mute = not settings.Effects_Enable

    Effects_Enable: BoolProperty(
        name="Toggle Effects",
        description="Enable/Disable Effects",
        default=True,
        update=update_Effects_Enable
    )

    def get_effect_from_list(self, context):
        index = context.scene.sac_effect_list_index
        item = context.scene.sac_effect_list[index] if context.scene.sac_effect_list else None
        if item:
            node_group_name = f".{item.EffectGroup}_{item.ID}"
            return bpy.data.node_groups[node_group_name]
        return None
    
    # Blur
    def update_Effects_Blur_Type(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].filter_type = settings.Effects_Blur_Type
    
    Effects_Blur_Type: EnumProperty(
        name="Type",
        description="The type of the blur effect decides how the blur is applied",
        items=(
            ('FLAT', "Flat", "Simply blurs everything uniformly"),
            ('TENT', "Tent", "Preserves the high and the lows better by making a linear falloff"),
            ('QUAD', "Quadratic", "Looks similar to Gaussian but can be a little faster but slightly worse looking"),
            ('CUBIC', "Cubic", "Preserve the highs, but give an almost out-of-focus blur while smoothing sharp edges"),
            ('GAUSS', "Gaussian", "Gives the best looking results but tends to be the slowest"),
            ('FAST_GAUSS', "Fast Gaussian", "An approximation of the Gaussian"),
            ('CATROM', "Catmull-Rom", "Catmull-Rom keeps sharp contrast edges crisp"),
            ('MITCH', "Mitch", "Preserve the highs, but give an almost out-of-focus blur while smoothing sharp edges"),
        ),
        default='GAUSS',
        update=update_Effects_Blur_Type
    )

    def update_Effects_Blur_Bokeh(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].use_bokeh = settings.Effects_Blur_Bokeh

    Effects_Blur_Bokeh: BoolProperty(
        name="Bokeh",
        description="Force the Blur to use a circular blur filter.\nThis gives higher quality results, but is slower than using a normal filter",
        default=False,
        update=update_Effects_Blur_Bokeh
    )

    def update_Effects_Blur_Gamma(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].use_gamma_correction = settings.Effects_Blur_Gamma

    Effects_Blur_Gamma: BoolProperty(
        name="Gamma",
        description="Applies a gamma correction on the image before blurring it.\nThis can be useful to avoid dark halos around bright objects when using a large blur size",
        default=False,
        update=update_Effects_Blur_Gamma
    )

    def update_Effects_Blur_Relative(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].use_relative = settings.Effects_Blur_Relative
    
    Effects_Blur_Relative: BoolProperty(
        name="Relative",
        description="Percentage Value of the blur radius relative to the image size\nThis is useful to keep the blur radius constant when rendering at different resolutions",
        default=False,
        update=update_Effects_Blur_Relative
    )

    def update_Effects_Blur_AspectCorrection(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].aspect_correction = settings.Effects_Blur_AspectCorrection

    Effects_Blur_AspectCorrection: EnumProperty(
        name="Aspect Correction",
        description="Corrects the blur radius to account for the aspect ratio of the image",
        items=(
            ('NONE', "None", "No aspect correction"),
            ('Y', "Vertical", "Vertical aspect correction"),
            ('X', "Horizontal", "Horizontal aspect correction"),
        ),
        default='NONE',
        update=update_Effects_Blur_AspectCorrection
    )

    def update_Effects_Blur_SizeX(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].size_x = settings.Effects_Blur_SizeX
    
    Effects_Blur_SizeX: IntProperty(
        name="X",
        description="Horizontal Values set the ellipsoid radius in numbers of pixels over which to spread the blur effect",
        default=0,
        min=0,
        max=2048,
        subtype="PIXEL",
        update=update_Effects_Blur_SizeX
    )

    def update_Effects_Blur_SizeY(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].size_y = settings.Effects_Blur_SizeY

    Effects_Blur_SizeY: IntProperty(
        name="Y",
        description="Vertical Values set the ellipsoid radius in numbers of pixels over which to spread the blur effect",
        default=0,
        min=0,
        max=2048,
        subtype="PIXEL",
        update=update_Effects_Blur_SizeY
    )

    def update_Effects_Blur_FactorX(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].factor_x = settings.Effects_Blur_FactorX

    Effects_Blur_FactorX: FloatProperty(
        name="X",
        description="Horizontal Percentage Value of the blur radius relative to the image size.",
        default=0,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        update=update_Effects_Blur_FactorX
    )

    def update_Effects_Blur_FactorY(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].factor_y = settings.Effects_Blur_FactorY

    Effects_Blur_FactorY: FloatProperty(
        name="Y",
        description="Vertical Percentage Value of the blur radius relative to the image size.",
        default=0,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        update=update_Effects_Blur_FactorY
    )

    def update_Effects_Blur_Extend(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].use_extended_bounds = settings.Effects_Blur_Extend

    Effects_Blur_Extend: BoolProperty(
        name="Extend",
        description="Allows the image, that is being blurred, to extend past its original dimension",
        default=False,
        update=update_Effects_Blur_Extend
    )
        
    def update_Effects_Blur_Size(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Blur"].inputs[1].default_value = settings.Effects_Blur_Size

    Effects_Blur_Size: FloatProperty(
        name="Size",
        description="The master blur size, it is used to set the size of the blur in both the X and Y directions",
        default=0,
        min=0,
        max=1,
        subtype="FACTOR",
        update=update_Effects_Blur_Size
    )

    # Duotone
    def update_Effects_DuotoneColor1(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_Colors"].inputs[1].default_value[0] = settings.Effects_Duotone_Color1[0]
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_Colors"].inputs[1].default_value[1] = settings.Effects_Duotone_Color1[1]
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_Colors"].inputs[1].default_value[2] = settings.Effects_Duotone_Color1[2]

    Effects_Duotone_Color1: FloatVectorProperty(
        name="Color 1",
        description="Sets the color for the bright parts of the image",
        min=0.0,
        max=1.0,
        default=(0.01, 0.01, 0.17),
        subtype="COLOR",
        update=update_Effects_DuotoneColor1
    )

    def update_Effects_DuotoneColor2(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_Colors"].inputs[2].default_value[0] = settings.Effects_Duotone_Color2[0]
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_Colors"].inputs[2].default_value[1] = settings.Effects_Duotone_Color2[1]
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_Colors"].inputs[2].default_value[2] = settings.Effects_Duotone_Color2[2]

    Effects_Duotone_Color2: FloatVectorProperty(
        name="Color 2",
        description="Sets the color for the dark parts of the image",
        min=0.0,
        max=1.0,
        default=(1.0, 0.56, 0.06),
        subtype="COLOR",
        update=update_Effects_DuotoneColor2
    )

    def update_Effects_DuotoneBlend(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_Blend"].inputs[0].default_value = settings.Effects_Duotone_Blend

    Effects_Duotone_Blend: FloatProperty(
        name="Blend",
        description="Adjusts the blend between the original image and the duotone",
        default=0,
        min=-1,
        max=1,
        subtype="FACTOR",
        update=update_Effects_DuotoneBlend
    )

    def update_Effects_DuotoneClamp(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_MapRange"].use_clamp = settings.Effects_Duotone_Clamp

    Effects_Duotone_Clamp: BoolProperty(
        name="Clamp",
        description="Clamps the color values to 0 and 1",
        default=False,
        update=update_Effects_DuotoneClamp
    )

    def update_Effects_DuotoneColor1Start(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_MapRange"].inputs[1].default_value = settings.Effects_Duotone_Color1_Start
    
    Effects_Duotone_Color1_Start: FloatProperty(
        name="Color 1 Start",
        description="Sets the start point for the color 1 gradient",
        default=0.1,
        min=-1,
        max=1,
        subtype="FACTOR",
        update=update_Effects_DuotoneColor1Start
    )

    def update_Effects_DuotoneColor2Start(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_MapRange"].inputs[2].default_value = settings.Effects_Duotone_Color2_Start

    Effects_Duotone_Color2_Start: FloatProperty(
        name="Color 2 Start",
        description="Sets the start point for the color 2 gradient",
        default=0.5,
        min=-1,
        max=1,
        subtype="FACTOR",
        update=update_Effects_DuotoneColor2Start
    )

    def update_Effects_DuotoneColor1Mix(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_MapRange"].inputs[3].default_value = 1 - settings.Effects_Duotone_Color1_Mix

    Effects_Duotone_Color1_Mix: FloatProperty(
        name="Overall Color 1",
        description="How much of the color 1 there should be overall",
        default=0,
        min=-1,
        max=1,
        subtype="FACTOR",
        update=update_Effects_DuotoneColor1Mix
    )
    
    def update_Effects_DuotoneColor2Mix(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Duotone_MapRange"].inputs[4].default_value = settings.Effects_Duotone_Color2_Mix

    Effects_Duotone_Color2_Mix: FloatProperty(
        name="Overall Color 2",
        description="How much of the color 2 there should be overall",
        default=0,
        min=-1,
        max=1,
        subtype="FACTOR",
        update=update_Effects_DuotoneColor2Mix
    )

    # Fog Glow
    def update_Effects_FogGlow_Threshold(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_FogGlow"].threshold = settings.Effects_FogGlow_Threshold

    Effects_FogGlow_Threshold: FloatProperty(
        name="Threshold",
        description="Adjusts the threshold for the fog glow effect",
        default=1,
        max=1000,
        min=0,
        subtype="NONE",
        update=update_Effects_FogGlow_Threshold
    )

    def update_Effects_FogGlow_Size(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_FogGlow"].size = settings.Effects_FogGlow_Size + 5

    Effects_FogGlow_Size: IntProperty(
        name="Size",
        description="Adjusts the size of the fog glow effect",
        default=2,
        max=4,
        min=1,
        subtype="FACTOR",
        update=update_Effects_FogGlow_Size
    )

    def update_Effects_FogGlow_Strength(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_FogGlowStrength"].inputs[0].default_value = settings.Effects_FogGlow_Strength
        
    Effects_FogGlow_Strength: FloatProperty(
        name="Strength",
        description="Adjusts the strength of the fog glow effect",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_FogGlow_Strength
    )
    # Streaks

    def update_Effects_Streaks_Threshold(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Streaks"].threshold = settings.Effects_Streaks_Threshold

    Effects_Streaks_Threshold: FloatProperty(
        name="Threshold",
        description="Adjusts the threshold for the streaks effect",
        default=1,
        max=1000,
        min=0,
        subtype="NONE",
        update=update_Effects_Streaks_Threshold
    )

    def update_Effects_Streaks_Count(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Streaks"].streaks = settings.Effects_Streaks_Count

    Effects_Streaks_Count: IntProperty(
        name="Count",
        description="Adjusts the number of streaks",
        default=6,
        max=16,
        min=1,
        subtype="FACTOR",
        update=update_Effects_Streaks_Count
    )

    def update_Effects_Streaks_Angle(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Streaks"].angle_offset = settings.Effects_Streaks_Angle

    Effects_Streaks_Angle: FloatProperty(
        name="Angle",
        description="Adjusts the angle of the streaks",
        default=0.1963495,  # 11.25 degrees
        max=3.1415,  # 180 degrees
        min=0,
        subtype="ANGLE",
        update=update_Effects_Streaks_Angle
    )

    def update_Effects_Streaks_Distortion(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Streaks"].color_modulation = settings.Effects_Streaks_Distortion

    Effects_Streaks_Distortion: FloatProperty(
        name="Distortion",
        description="Adjusts the color modulation of the streaks",
        default=0.25,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Streaks_Distortion
    )

    def update_Effects_Streaks_Fade(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Streaks"].fade = settings.Effects_Streaks_Fade

    Effects_Streaks_Fade: FloatProperty(
        name="Fade",
        description="Adjusts the fade of the streaks",
        default=0.85,
        max=1,
        min=0.75,
        subtype="FACTOR",
        update=update_Effects_Streaks_Fade
    )

    def update_Effects_Streaks_Length(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Streaks"].iterations = settings.Effects_Streaks_Length + 1

    Effects_Streaks_Length: IntProperty(
        name="Length",
        description="Adjusts the length of the streaks",
        default=2,
        max=4,
        min=1,
        subtype="FACTOR",
        update=update_Effects_Streaks_Length
    )

    def update_Effects_Streaks_Strength(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_StreaksStrength"].inputs[0].default_value = settings.Effects_Streaks_Strength

    Effects_Streaks_Strength: FloatProperty(
        name="Strength",
        description="Adjusts the strength of the streaks",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Streaks_Strength
    )

    # Ghosts

    def update_Effects_Ghosts_Threshold(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Ghosts"].threshold = settings.Effects_Ghosts_Threshold

    Effects_Ghosts_Threshold: FloatProperty(
        name="Threshold",
        description="Adjusts the threshold for the ghosts effect",
        default=1,
        max=1000,
        min=0,
        subtype="NONE",
        update=update_Effects_Ghosts_Threshold
    )

    def update_Effects_Ghosts_Distortion(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Ghosts"].color_modulation = settings.Effects_Ghosts_Distortion

    Effects_Ghosts_Distortion: FloatProperty(
        name="Distortion",
        description="Adjusts the color modulation of the ghosts",
        default=0.1,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Ghosts_Distortion
    )

    def update_Effects_Ghosts_Count(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Ghosts"].iterations = settings.Effects_Ghosts_Count

    Effects_Ghosts_Count: IntProperty(
        name="Count",
        description="Adjusts the number of ghosts",
        default=3,
        max=5,
        min=2,
        subtype="FACTOR",
        update=update_Effects_Ghosts_Count
    )

    def update_Effects_Ghosts_Strength(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_GhostsStrength"].inputs[0].default_value = settings.Effects_Ghosts_Strength

    Effects_Ghosts_Strength: FloatProperty(
        name="Strength",
        description="Adjusts the strength of the ghosts",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Ghosts_Strength
    )

    # Emboss

    def update_Effects_Emboss_Strength(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Emboss"].inputs[0].default_value = settings.Effects_Emboss_Strength

    Effects_Emboss_Strength: FloatProperty(
        name="Strength",
        description="Adjusts the strength of the emboss effect",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Effects_Emboss_Strength
    )

    # Posterize

    def update_Effects_Posterize_Steps(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Posterize"].inputs[1].default_value = settings.Effects_Posterize_Steps
        settings.Effects_Posterize_Toggle = True

    Effects_Posterize_Steps: FloatProperty(
        name="Steps",
        description="Adjusts the number of color steps in the posterize effect",
        default=128,
        max=1024,
        soft_max=256,
        min=2,
        subtype="FACTOR",
        update=update_Effects_Posterize_Steps
    )

    # Overlay

    def update_Effects_Overlay_Strength(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Overlay"].inputs[0].default_value = settings.Effects_Overlay_Strength

    Effects_Overlay_Strength: FloatProperty(
        name="Strength",
        description="Adjusts the strength of the overlay effect",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Overlay_Strength
    )

    # Pixelate

    def update_Effects_Pixelate_PixelSize(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Pixelate_Size"].inputs[0].default_value = settings.Effects_Pixelate_PixelSize

    Effects_Pixelate_PixelSize: FloatProperty(
        name="Pixel Size",
        description="Adjusts the size of the pixels in the mosaic effect",
        default=0,
        max=100,
        soft_max=25,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Pixelate_PixelSize
    )

    # Chromatic Aberration

    def update_Effects_ChromaticAberration_Amount(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_ChromaticAberration"].inputs[2].default_value = settings.Effects_ChromaticAberration_Amount
        self.get_effect_from_list(context).nodes["SAC Effects_ChromaticAberration"].inputs[1].default_value = -settings.Effects_ChromaticAberration_Amount/3.5

    Effects_ChromaticAberration_Amount: FloatProperty(
        name="Amount",
        description="Adjusts the amount of chromatic aberration",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_ChromaticAberration_Amount
    )

    # Vignette
    # Intensity
    def update_Effects_Vignette_Intensity(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Viginette_Intensity"].inputs[0].default_value = settings.Effects_Vignette_Intensity

    Effects_Vignette_Intensity: FloatProperty(
        name="Intensity",
        description="Adjusts the intensity of the vignette,\nnegative values make the vignette darker,\npositive values make the vignette brighter",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Effects_Vignette_Intensity
    )

    # Roundness
    def update_Effects_Vignette_Roundness(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Viginette_Roundness"].inputs[0].default_value = settings.Effects_Vignette_Roundness

    Effects_Vignette_Roundness: FloatProperty(
        name="Roundness",
        description="Adjusts the roundness of the vignette,\npositive values make the vignette rounder,\nnegative values make the vignette more square",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Effects_Vignette_Roundness
    )

    # Feather
    def update_Effects_Vignette_Feather(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Viginette_Directional_Blur"].zoom = settings.Effects_Vignette_Feather
        self.get_effect_from_list(context).nodes["SAC Effects_Viginette_Midpoint"].inputs[3].default_value = -settings.Effects_Vignette_Feather/4
        self.get_effect_from_list(context).nodes["SAC Effects_Viginette_Midpoint"].inputs[1].default_value = -0.999-settings.Effects_Vignette_Feather/4

        feather_value = settings.Effects_Vignette_Feather
        node_to_update = self.get_effect_from_list(context).nodes["SAC Effects_Viginette_Directional_Blur"]

        if feather_value <= 0.05:
            node_to_update.iterations = 4
        elif feather_value <= 0.2:
            node_to_update.iterations = 5
        elif feather_value <= 0.4:
            node_to_update.iterations = 6
        else:  # feather_value > 0.4
            node_to_update.iterations = 7

    Effects_Vignette_Feather: FloatProperty(
        name="Feather",
        description="Adjusts the blur of the vignette",
        default=0.25,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Vignette_Feather
    )

    # Midpoint
    def update_Effects_Vignette_Midpoint(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Viginette_Midpoint"].inputs[0].default_value = settings.Effects_Vignette_Midpoint

    Effects_Vignette_Midpoint: FloatProperty(
        name="Midpoint",
        description="Adjusts the midpoint of the vignette",
        default=0,
        max=1,
        min=-0.998,
        subtype="FACTOR",
        update=update_Effects_Vignette_Midpoint
    )

    # Infrared
    # Infrared Blend
    def update_Effects_Infrared_Blend(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Infrared_Mix"].inputs[0].default_value = settings.Effects_Infrared_Blend

    Effects_Infrared_Blend: FloatProperty(
        name="Blend",
        description="Adjusts the blend of the infrared effect",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Infrared_Blend
    )

    # Infrared Offset
    def update_Effects_Infrared_Offset(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Infrared_Add"].inputs[1].default_value = settings.Effects_Infrared_Offset

    Effects_Infrared_Offset: FloatProperty(
        name="Offset",
        description="Adjusts the offset of the infrared effect",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Effects_Infrared_Offset
    )

    # Negative

    def update_Effects_Negative(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Negative"].inputs[0].default_value = settings.Effects_Negative

    Effects_Negative: FloatProperty(
        name="Negative",
        description="Adjusts the strength of the negative effect",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Negative
    )

    # Warp

    def update_Effects_Warp(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        warp_node = self.get_effect_from_list(context).nodes["SAC Effects_Warp"]
        warp_node.zoom = settings.Effects_Warp
        warp_value = settings.Effects_Warp

        if warp_value <= 0.05:
            warp_node.iterations = 4
        elif warp_value <= 0.2:
            warp_node.iterations = 5
        elif warp_value <= 0.4:
            warp_node.iterations = 6
        else:  # warp_value > 0.4
            warp_node.iterations = 7

    Effects_Warp: FloatProperty(
        name="Warp",
        description="Adjusts the strength of the warp effect",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Warp
    )

    # Fisheye

    def update_Effects_Fisheye(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Fisheye"].inputs[1].default_value = settings.Effects_Fisheye

    Effects_Fisheye: FloatProperty(
        name="Fisheye",
        description="Adjusts the strength of the fisheye effect",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Effects_Fisheye
    )

    # Perspective Shift
    # Horizontal
    def update_Effects_PerspectiveShift_Horizontal(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        horizontal_shift = settings.Effects_PerspectiveShift_Horizontal / 2
        if settings.Effects_PerspectiveShift_Horizontal > 0:
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[1].default_value[0] = horizontal_shift
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[2].default_value[0] = 1 - horizontal_shift
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_Scale"].inputs[1].default_value = 1/(1-horizontal_shift*2)
        elif settings.Effects_PerspectiveShift_Horizontal < 0:
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[3].default_value[0] = -horizontal_shift
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[4].default_value[0] = 1 - (-horizontal_shift)
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_Scale"].inputs[1].default_value = 1/(1-horizontal_shift*-2)

        if (settings.Effects_PerspectiveShift_Horizontal == 0):
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[1].default_value[0] = 0
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[2].default_value[0] = 1
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[3].default_value[0] = 0
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[4].default_value[0] = 1
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_Scale"].inputs[1].default_value = 1

    Effects_PerspectiveShift_Horizontal: FloatProperty(
        name="Horizontal",
        description="Adjusts the horizontal perspective shift",
        default=0,
        max=0.999,
        min=-0.999,
        subtype="FACTOR",
        update=update_Effects_PerspectiveShift_Horizontal
    )
    # Vertical

    def update_Effects_PerspectiveShift_Vertical(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        vertical_shift = settings.Effects_PerspectiveShift_Vertical / 2
        if settings.Effects_PerspectiveShift_Vertical > 0:
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[1].default_value[1] = 1 - vertical_shift
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[3].default_value[1] = vertical_shift
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_Scale"].inputs[2].default_value = 1/(1-vertical_shift*2)
        elif settings.Effects_PerspectiveShift_Vertical < 0:
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[2].default_value[1] = 1 - (-vertical_shift)
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[4].default_value[1] = -vertical_shift
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_Scale"].inputs[2].default_value = 1/(1-vertical_shift*-2)

        if settings.Effects_PerspectiveShift_Vertical == 0:
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[1].default_value[1] = 1
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[2].default_value[1] = 1
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[3].default_value[1] = 0
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_CornerPin"].inputs[4].default_value[1] = 0
            self.get_effect_from_list(context).nodes["SAC Effects_PerspectiveShift_Scale"].inputs[2].default_value = 1

    Effects_PerspectiveShift_Vertical: FloatProperty(
        name="Vertical",
        description="Adjusts the vertical perspective shift",
        default=0,
        max=0.999,
        min=-0.999,
        subtype="FACTOR",
        update=update_Effects_PerspectiveShift_Vertical
    )

    # ISO
    # Strength
    def update_ISO_strength(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_ISO_Add"].inputs[0].default_value = settings.ISO_strength

    ISO_strength: FloatProperty(
        name="Strength",
        description="Adjusts the strength of the ISO effect",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_ISO_strength
    )
    # Size

    def update_ISO_size(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_ISO_Despeckle"].inputs[0].default_value = settings.ISO_size

    ISO_size: FloatProperty(
        name="Size",
        description="Adjusts the size of the ISO effect",
        default=1,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_ISO_size
    )

    # Filmgrain
    # Strength

    def update_Filmgrain_strength(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_FilmGrain_Strength"].inputs[0].default_value = settings.Filmgrain_strength

    Filmgrain_strength: FloatProperty(
        name="Strength",
        description="Adjusts the strength of the filmgrain effect",
        default=0,
        max=10,
        min=0,
        subtype="FACTOR",
        update=update_Filmgrain_strength
    )

    # Dust Proportion

    def update_Filmgrain_dustproportion(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_FilmGrain_Blur"].sigma_color = settings.Filmgrain_dustproportion

    Filmgrain_dustproportion: FloatProperty(
        name="Dust Proportion",
        description="Adjusts the proportion of dust in the filmgrain effect",
        default=0.35,
        max=0.5,
        min=0.01,
        subtype="FACTOR",
        update=update_Filmgrain_dustproportion
    )

    # Size

    def update_Filmgrain_size(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_FilmGrain_Blur"].iterations = settings.Filmgrain_size

    Filmgrain_size: IntProperty(
        name="Size",
        description="Adjusts the size of the filmgrain effect",
        default=3,
        max=12,
        min=1,
        subtype="FACTOR",
        update=update_Filmgrain_size
    )

    # Halftone
    # Value

    def update_Effects_Halftone_value(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Halftone_Value"].outputs[0].default_value = settings.Effects_Halftone_value

    Effects_Halftone_value: FloatProperty(
        name="Value",
        description="Adjusts the offset of the halftone effect",
        default=-0.2,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Effects_Halftone_value
    )

    # Delta

    def update_Effects_Halftone_delta(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Halftone_Delta"].outputs[0].default_value = settings.Effects_Halftone_delta

    Effects_Halftone_delta: FloatProperty(
        name="Delta",
        description="Adjusts the brightness range of the halftone effect",
        default=0.2,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Halftone_delta
    )

    # Size

    def update_Effects_Halftone_size(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Halftone_Texture"].inputs[1].default_value[0] = context.scene.render.resolution_x / (settings.Effects_Halftone_size*10)
        self.get_effect_from_list(context).nodes["SAC Effects_Halftone_Texture"].inputs[1].default_value[1] = context.scene.render.resolution_y / (settings.Effects_Halftone_size*10)
        self.get_effect_from_list(context).nodes["SAC Effects_Halftone_SizeSave"].outputs[0].default_value = settings.Effects_Halftone_size

    Effects_Halftone_size: FloatProperty(
        name="Size",
        description="Adjusts the size of the halftone effect",
        default=2,
        max=10,
        min=1,
        subtype="FACTOR",
        update=update_Effects_Halftone_size
    )

    # HDR
    # Blend

    def update_Effects_HDR_blend(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_HDR_Mix"].inputs[0].default_value = settings.Effects_HDR_blend
        
    Effects_HDR_blend: FloatProperty(
        name="Blend",
        description="The strength of the HDR effect",
        default=1,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_HDR_blend
    )

    # Sigma

    def update_Effects_HDR_sigma(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_HDR_Sigma"].inputs[0].default_value = settings.Effects_HDR_sigma

    Effects_HDR_sigma: FloatProperty(
        name="Sigma",
        description="The mix factor of the exposures of the HDR effect",
        default=0.1,
        max=1,
        min=0.01,
        subtype="FACTOR",
        update=update_Effects_HDR_sigma
    )

    # Delta

    def update_Effects_HDR_delta(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_HDR_Under"].inputs["Exposure"].default_value = -settings.Effects_HDR_delta
        self.get_effect_from_list(context).nodes["SAC Effects_HDR_Over"].inputs["Exposure"].default_value = settings.Effects_HDR_delta

    Effects_HDR_delta: FloatProperty(
        name="Delta",
        description="The range of the exposures of the HDR effect",
        default=2,
        max=10,
        min=0.01,
        subtype="FACTOR",
        update=update_Effects_HDR_delta
    )
        
    # Exposure

    def update_Effects_HDR_exposure(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_HDR_Exposure"].inputs[1].default_value = settings.Effects_HDR_exposure

    Effects_HDR_exposure: FloatProperty(
        name="Exposure",
        description="The additional exposure of the HDR effect",
        default=-1.75,
        max=100,
        soft_max=10,
        soft_min=-10,
        min=-100,
        subtype="FACTOR",
        update=update_Effects_HDR_exposure
    )

    # Gradient Map
    # Blend

    def update_Effects_GradientMap_blend(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_GradientMap_Mix"].inputs[0].default_value = settings.Effects_GradientMap_blend

    Effects_GradientMap_blend: FloatProperty(
        name="Blend",
        description="Adjusts the blend of the gradient map effect",
        default=0,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Effects_GradientMap_blend
    )

    # Bokeh
    # Max Size

    def update_Effects_Bokeh_MaxSize(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Blur"].blur_max = settings.Effects_Bokeh_MaxSize

    Effects_Bokeh_MaxSize: FloatProperty(
        name="Max Size",
        description="Adjusts the max size of the bokeh effect.\nLarger will be slower",
        default=16,
        max=512,
        soft_max=64,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Bokeh_MaxSize
    )

    # Offset

    def update_Effects_Bokeh_Offset(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Offset"].inputs[1].default_value = settings.Effects_Bokeh_Offset/100

    Effects_Bokeh_Offset: FloatProperty(
        name="Offset",
        description="Adjusts the focus point of the bokeh effect",
        default=0,
        max=100,
        min=-100,
        subtype="FACTOR",
        update=update_Effects_Bokeh_Offset
    )

    # Range

    def update_Effects_Bokeh_Range(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Range"].inputs[1].default_value = settings.Effects_Bokeh_Range

    Effects_Bokeh_Range: FloatProperty(
        name="Range",
        description="Adjusts the focus range of the bokeh effect",
        default=1,
        max=1000,
        soft_max=10,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Bokeh_Range
    )

    # Image

    def update_Effects_Bokeh_Image(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Image"].image = settings.Effects_Bokeh_image

    Effects_Bokeh_image: PointerProperty(
        name="Image",
        description="The image to use for the bokeh effect",
        type=bpy.types.Image,
        update=update_Effects_Bokeh_Image
    )

    # Rotation

    def update_Effects_Bokeh_Rotation(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Rotation"].inputs[1].default_value = settings.Effects_Bokeh_Rotation

    Effects_Bokeh_Rotation: FloatProperty(
        name="Rotation",
        description="Adjusts the rotation of the bokeh effect",
        default=0,
        max=(math.pi*2),
        min=0,
        subtype="ANGLE",
        update=update_Effects_Bokeh_Rotation
    )

    # Procedural Bokeh
    # Flaps

    def update_Effects_Bokeh_Procedural_Flaps(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Procedural"].flaps = settings.Effects_Bokeh_Procedural_Flaps

    Effects_Bokeh_Procedural_Flaps: IntProperty(
        name="Blades",
        description="Adjusts the number of flaps in the bokeh effect",
        default=6,
        max=24,
        min=3,
        subtype="FACTOR",
        update=update_Effects_Bokeh_Procedural_Flaps
    )

    # Angle

    def update_Effects_Bokeh_Procedural_Angle(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Procedural"].angle = settings.Effects_Bokeh_Procedural_Angle

    Effects_Bokeh_Procedural_Angle: FloatProperty(
        name="Rotation",
        description="Adjusts the angle of the bokeh effect",
        default=0.0785398,
        max=(math.pi*2),
        min=0,
        subtype="ANGLE",
        update=update_Effects_Bokeh_Procedural_Angle
    )

    # Rounding

    def update_Effects_Bokeh_Procedural_Rounding(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Procedural"].rounding = settings.Effects_Bokeh_Procedural_Rounding

    Effects_Bokeh_Procedural_Rounding: FloatProperty(
        name="Rounding",
        description="Adjusts the rounding of the bokeh effect",
        default=0.1,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Bokeh_Procedural_Rounding
    )

    # Catadioptric

    def update_Effects_Bokeh_Procedural_Catadioptric(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Procedural"].catadioptric = settings.Effects_Bokeh_Procedural_Catadioptric

    Effects_Bokeh_Procedural_Catadioptric: FloatProperty(
        name="Catadioptric",
        description="Adjusts the catadioptric of the bokeh effect.\nValues above 0 will adda black circle in the center of the bokeh",
        default=0,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Effects_Bokeh_Procedural_Catadioptric
    )

    # Shift

    def update_Effects_Bokeh_Procedural_Shift(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings
        self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Procedural"].shift = settings.Effects_Bokeh_Procedural_Shift

    Effects_Bokeh_Procedural_Shift: FloatProperty(
        name="Lens Shift",
        description="Adjusts the lens shift of the bokeh effect.\nValues above 0 will shift the bokeh edges to blue,\nvalues below 0 will shift the bokeh edges to red",
        default=0.02,
        max=1,
        min=-1,
        subtype="FACTOR",
        update=update_Effects_Bokeh_Procedural_Shift
    )

    # Type

    def update_Effects_Bokeh_Type(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings

        if settings.Effects_Bokeh_Type == 'PROCEDURAL':
            self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Switch"].check = True
        else:
            self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_Switch"].check = False
            if settings.Effects_Bokeh_Type == 'CUSTOM':
                self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_ImageSwitch"].check = True
            else:
                self.get_effect_from_list(context).nodes["SAC Effects_Bokeh_ImageSwitch"].check = False

    Effects_Bokeh_Type: EnumProperty(
        name="Bokeh Type",
        description="The type of bokeh to use",
        items=(
            ('CAMERA', 'Camera', 'A real camera bokeh image'),
            ('PROCEDURAL', 'Procedural', 'A procedurally generated bokeh image'),
            ('CUSTOM', 'Custom', 'A custom bokeh image of your choice'),
        ),
        default='CAMERA',
        update=update_Effects_Bokeh_Type
    )

    def get_effect_presets(self, context):
        items = []
        directory = os.path.join(os.path.dirname(__file__), "presets")
        for file in os.listdir(directory):
            if file.endswith(".sacpe"):
                items.append((file[:-6], file[:-6], ""))
        return items

    Effects_Presets: EnumProperty(
        name="Presets",
        description="A list of presets to quickly add effects",
        items=get_effect_presets,
    )

    Effects_Preset_Name: StringProperty(
        name="Preset Name",
        description="The name of the preset to save",
        default="My Preset",
    )


# endregion Effects

# region Camera


    def get_camera_items(self, context):
        camera = []
        i = 0
        for cam in bpy.context.scene.objects:
            if cam.type == 'CAMERA':
                camera.extend([(cam.name, cam.name, "", "CAMERA_DATA", i)])
                i += 1
        if camera == []:
            camera = [("None", "No Camera", "", "ERROR", 0)]
        return camera

    selected_camera: EnumProperty(
        name="Camera",
        description="Select a camera from the list",
        items=get_camera_items,
    )

    # Tilt Shift
    # Keep frame

    Camera_TiltShift_KeepFrame: BoolProperty(
        name="Tilt Shift",
        description="Whether to adjust the tilt shift, or the lens shift",
        default=True,
    )

    # Amount X

    def get_Camera_Shift_AmountX(self):
        # OnAfterGetData Trigger
        return self.get("Camera_TiltShift_AmountX", 0)

    def set_Camera_Shift_AmountX(self, tilt_shift_amount):
        # OnBeforeSetData Trigger
        settings: SAC_Settings = bpy.context.scene.sac_settings

        camera_object = bpy.data.objects[settings.selected_camera]
        camera_data = bpy.data.cameras[camera_object.data.name]

        if self.Camera_TiltShift_KeepFrame:
            old_rotation_x = camera_object.rotation_euler.x
            cur_rotation_x = old_rotation_x - math.atan(self.Camera_TiltShift_AmountX / (camera_data.lens/36))
            new_rotation_x = cur_rotation_x + math.atan(tilt_shift_amount / (camera_data.lens/36))

            camera_object.rotation_euler.x = new_rotation_x

        camera_data.shift_y = -tilt_shift_amount

        self["Camera_TiltShift_AmountX"] = tilt_shift_amount

        return None

    Camera_TiltShift_AmountX: FloatProperty(
        name="Vertical Tilt Shift",
        description="Adjusts the vertical tilt shift",
        default=0,
        soft_max=1,
        soft_min=-1,
        subtype="FACTOR",
        get=get_Camera_Shift_AmountX,
        set=set_Camera_Shift_AmountX,
    )

    # Amount Y

    def get_Camera_Shift_AmountY(self):
        # OnAfterGetData Trigger
        return self.get("Camera_TiltShift_AmountY", 0)

    def set_Camera_Shift_AmountY(self, tilt_shift_amount):
        # OnBeforeSetData Trigger
        settings: SAC_Settings = bpy.context.scene.sac_settings

        camera_object = bpy.data.objects[settings.selected_camera]
        camera_data = bpy.data.cameras[camera_object.data.name]

        if self.Camera_TiltShift_KeepFrame:

            old_rotation = camera_object.rotation_euler.to_matrix().to_euler("YZX")
            new_rotation = old_rotation
            cur_rotation_y = old_rotation.y - math.atan(self.Camera_TiltShift_AmountY / (camera_data.lens/36))
            new_rotation.y = cur_rotation_y + math.atan(tilt_shift_amount / (camera_data.lens/36))

            camera_object.rotation_euler = new_rotation.to_matrix().to_euler(camera_object.rotation_mode)

        camera_data.shift_x = tilt_shift_amount

        self["Camera_TiltShift_AmountY"] = tilt_shift_amount

        return None

    Camera_TiltShift_AmountY: FloatProperty(
        name="Horizontal Tilt Shift",
        description="Adjusts the horizontal tilt shift",
        default=0,
        soft_max=1,
        soft_min=-1,
        subtype="FACTOR",
        get=get_Camera_Shift_AmountY,
        set=set_Camera_Shift_AmountY,
    )

    # bokeh

    def update_Camera_Bokeh_Scale(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings

        material = bpy.data.materials[f".SAC_Bokeh_{settings.selected_camera}_Material"]
        material_node_tree = material.node_tree
        material_node_tree.nodes["SAC Camera_Bokeh_Scale"].inputs["Scale"].default_value = settings.Camera_Bokeh_Scale

    Camera_Bokeh_Scale: FloatProperty(
        name="Scale",
        description="Adjusts the scale of the bokeh effect",
        default=10,
        soft_max=30,
        min=0,
        subtype="FACTOR",
        update=update_Camera_Bokeh_Scale
    )

    def update_Camera_Bokeh_Rotation(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings

        material = bpy.data.materials[f".SAC_Bokeh_{settings.selected_camera}_Material"]
        material_node_tree = material.node_tree
        material_node_tree.nodes["SAC Camera_Bokeh_Rotate"].inputs["Angle"].default_value = settings.Camera_Bokeh_Rotation

    Camera_Bokeh_Rotation: FloatProperty(
        name="Rotation",
        description="Adjusts the rotation of the bokeh effect",
        default=0,
        subtype="ANGLE",
        update=update_Camera_Bokeh_Rotation
    )

    def update_Camera_Bokeh_Curves(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings

        material = bpy.data.materials[f".SAC_Bokeh_{settings.selected_camera}_Material"]
        material_node_tree = material.node_tree
        material_node_tree.nodes["SAC Camera_Bokeh_Curves"].inputs[0].default_value = settings.Camera_Bokeh_Curves

    Camera_Bokeh_Curves: FloatProperty(
        name="Exposure Compensation",
        description="Adjusts the exposure compensation of the bokeh effect.\nBokeh naturally darkens the image, this can be used to compensate for that",
        default=1,
        max=1,
        min=0,
        subtype="FACTOR",
        update=update_Camera_Bokeh_Curves
    )

    def update_Camera_Bokeh_Type(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings

        camera_object = bpy.data.objects[settings.selected_camera]
        camera_data = bpy.data.cameras[camera_object.data.name]

        material = bpy.data.materials[f".SAC_Bokeh_{settings.selected_camera}_Material"]
        material_node_tree = material.node_tree

        bokeh_plane = bpy.data.objects[f"SAC_Bokeh_{settings.selected_camera}"]

        bokeh_plane.hide_viewport = False
        bokeh_plane.hide_render = False

        if settings.Camera_Bokeh_Type == 'CAMERA':
            material_node_tree.nodes["SAC Camera_Bokeh_Switch"].mute = True
            camera_data.dof.aperture_blades = 0
            camera_data.dof.aperture_ratio = 1
        elif settings.Camera_Bokeh_Type == 'CUSTOM':
            material_node_tree.nodes["SAC Camera_Bokeh_Switch"].mute = False
            camera_data.dof.aperture_blades = 0
            camera_data.dof.aperture_ratio = 1
        elif settings.Camera_Bokeh_Type == 'PROCEDURAL':
            bokeh_plane.hide_viewport = True
            bokeh_plane.hide_render = True

    Camera_Bokeh_Type: EnumProperty(
        name="Bokeh Type",
        description="The type of bokeh to use",
        items=(
            ('CAMERA', 'Camera', 'A real camera bokeh image'),
            ('PROCEDURAL', 'Procedural', 'A procedurally generated bokeh'),
            ('CUSTOM', 'Custom', 'A custom bokeh image of your choice')
        ),
        default='CAMERA',
        update=update_Camera_Bokeh_Type
    )

    # Frame Stretching

    def update_Camera_FrameStretching(self, context):
        scene = bpy.context.scene
        settings = scene.sac_settings

        if settings.Camera_FrameStretching == 'ORIGINAL':
            scene.render.frame_map_old = 1
            scene.render.frame_map_new = 1
        elif settings.Camera_FrameStretching == 'SLOWMO_1':
            scene.render.frame_map_old = 1
            scene.render.frame_map_new = 2
        elif settings.Camera_FrameStretching == 'SLOWMO_2':
            scene.render.frame_map_old = 1
            scene.render.frame_map_new = 4
        elif settings.Camera_FrameStretching == 'TIMELAPSE_1':
            scene.render.frame_map_old = 2
            scene.render.frame_map_new = 1
        elif settings.Camera_FrameStretching == 'TIMELAPSE_2':
            scene.render.frame_map_old = 4
            scene.render.frame_map_new = 1

    Camera_FrameStretching: EnumProperty(
        name="Presets",
        description="Presets for the frame stretching effect",
        items=(
            ('SLOWMO_2', 'Ultra-Slow-Motion (4x slower)', 'Quadruples the frame rate, allows for ultra-slow-motion'),
            ('SLOWMO_1', 'Slow-Motion (2x slower)', 'Doubles the frame rate, allows for slow-motion'),
            ('ORIGINAL', 'Original', '1:1 mapping, your frame rate will be unchanged'),
            ('TIMELAPSE_1', 'Time-Lapse (2x faster)', 'Halves the frame rate, allows for time-lapse'),
            ('TIMELAPSE_2', 'Ultra-Time-Lapse (4x faster)', 'Quarters the frame rate, allows for ultra-time-lapse'),
        ),
        default='ORIGINAL',
        update=update_Camera_FrameStretching
    )
    # endregion Camera

    # Show Panels

    show_camera: BoolProperty(
        default=False,
    )

    show_rendersettings: BoolProperty(
        default=False,
    )

    show_lenssettings: BoolProperty(
        default=False,
    )

    show_bokeh: BoolProperty(
        default=False,
    )

    show_colorgrading: BoolProperty(
        default=False,
    )

    show_color: BoolProperty(
        default=False,
    )

    show_light: BoolProperty(
        default=False,
    )

    show_presets: BoolProperty(
        default=False,
    )

    show_curves: BoolProperty(
        default=False,
    )

    show_colorwheels: BoolProperty(
        default=False,
    )

    show_effects: BoolProperty(
        default=False,
    )

    show_effectlist: BoolProperty(
        default=False,
    )

    show_effectproperties: BoolProperty(
        default=False,
    )


def register_function():
    bpy.utils.register_class(SAC_Settings)
    bpy.types.Scene.sac_settings = bpy.props.PointerProperty(type=SAC_Settings)


def unregister_function():
    try:
        bpy.utils.unregister_class(SAC_Settings)
    except (RuntimeError, Exception) as e:
        print(f"Failed to unregister SAC_Settings: {e}")

    try:
        del bpy.types.Scene.sac_settings
    except:
        pass
