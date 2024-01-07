import bpy

from bpy.types import (
    PropertyGroup,
)

from bpy.props import (
    EnumProperty,
    BoolProperty,
    StringProperty,
    IntProperty,
    FloatProperty,
)

class SFR_Settings(PropertyGroup):

    install_dependencies: BoolProperty(
        name="Install Dependencies",
        description="Installs the dependencies required by the Super Fast Render addon.\nThis is required for the Super Fast Render tools to work.\n\nThis will take up additional space on your disk.",
        default=True
    )

    # Show Panels

    show_rso: BoolProperty(
        default=True,
    )

    show_rso_auto_settings: BoolProperty(
        default=True,
    )

    show_rso_auto_passes: BoolProperty(
        default=True,
    )

    show_rso_auto_light: BoolProperty(
        default=True,
    )

    show_rso_general: BoolProperty(
        default=True,
    )

    show_to: BoolProperty(
        default=True,
    )

    show_to_general: BoolProperty(
        default=True,
    )

    show_to_advanced: BoolProperty(
        default=False,
    )

    show_mo: BoolProperty(
        default=True,
    )

    show_renderestimator: BoolProperty(
        default=True,
    )

    # Optimization Method

    optimization_method: EnumProperty(
        items=[
            ("AUTO", "Automatic", "Use the benchmark to determine the best settings"),
            ("MANUAL", "Manual", "Use presets or custom settings to optimize the scene"),
        ],
        default="AUTO",
        name="Optimization Method",
        description="The optimization method to use.\nRecommended: Automatic",
    )

    # General Settings

    benchmark_path: StringProperty(
        default="//SFR/",
        name="Benchmark Path",
        description="The working directory for the benchmark.\nRecommended: //SFR/",
        subtype="DIR_PATH",
    )

    benchmark_resolution: IntProperty(
        default=5,
        min=1,
        max=20,
        name="Benchmark Resolution",
        description="Render the scene at a scaled resolution to speed up the benchmark.\nHigher values will result in a more accurate benchmark, but will take longer to process.\nRecommended: 5%",
        subtype="PERCENTAGE",
    )

    benchmark_threshold: FloatProperty(
        default=0.1,
        min=0.01,
        max=1.0,
        name="Threshold",
        description="The threshold for the benchmark.\nLower values will result in a more accurate benchmark, but will take longer to process.\nRecommended: 0.1",
        subtype="FACTOR",
    )

    benchmark_add_keyframes: BoolProperty(
        default=True,
        name="Add Keyframes",
        description="Keyframes the settings set by the benchmark.\nUseful for animation.\nRecommended: Enabled",
    )

    benchmark_scene_type: EnumProperty(
        items=[
            ("INTERIOR", "Interior Scene", "Interior Scenes need a few more bounces, take that into consieration when benchmarking"),
            ("EXTERIOR", "Exterior Scene", "Exterior Scene need fewer bounces, take that into consieration when benchmarking"),
            ("CUSTOM", "Custom", "Set a custom benchmarking approach")
        ],
        default="INTERIOR",
        name="Scene Type",
        description="Depending on the scene, you may need a different benchmarking approach",
    )

    benchmark_scene_bounce_order: StringProperty(
        default="4,0,1,2,4,3,5,6",
        name="Bounce Order",
        description="Determines the order in which the bounces are benchmarked.\nRecommended: 4,0,1,2,4,3,5,6",
    )

    # Texture Optimization

    diffuse_factor: IntProperty(
        default=0,
        min=0,
        max=7,
        name="Diffuse / Albedo",
        description="Diffuse",
        subtype="FACTOR",
    )

    ao_factor: IntProperty(
        default=2,
        min=0,
        max=7,
        name="Ambient Occlusion",
        description="Ambient Occlusion",
        subtype="FACTOR",
    )

    metallic_factor: IntProperty(
        default=2,
        min=0,
        max=7,
        name="Metallic / Specular",
        description="Metallic",
        subtype="FACTOR",
    )

    roughness_factor: IntProperty(
        default=2,
        min=0,
        max=7,
        name="Roughness / Glossiness",
        description="Roughness",
        subtype="FACTOR",
    )

    normal_factor: IntProperty(
        default=1,
        min=0,
        max=7,
        name="Normal / Bump",
        description="Normal",
        subtype="FACTOR",
    )

    opacity_factor: IntProperty(
        default=1,
        min=0,
        max=7,
        name="Opacity / Transparency",
        description="Opacity",
        subtype="FACTOR",
    )

    translucency_factor: IntProperty(
        default=1,
        min=0,
        max=7,
        name="Translucency",
        description="Translucency",
        subtype="FACTOR",
    )

    emission_factor: IntProperty(
        default=0,
        min=0,
        max=7,
        name="Emission",
        description="Emission",
        subtype="FACTOR",
    )

    displacement_factor: IntProperty(
        default=0,
        min=0,
        max=7,
        name="Displacement",
        description="Displacement",
        subtype="FACTOR",
    )
    
    custom1_factor: IntProperty(
        default=0,
        min=0,
        max=7,
        name="Custom 1",
        description="Custom 1",
        subtype="FACTOR",
    )

    custom2_factor: IntProperty(
        default=0,
        min=0,
        max=7,
        name="Custom 2",
        description="Custom 2",
        subtype="FACTOR",
    )

    diffuse_strings: StringProperty(
        default="diffuse,albedo,col,diff,dif,color",
        name="Diffuse / Albedo",
        description="Diffuse",
    )

    ao_strings: StringProperty(
        default="ao,ambientocclusion,occlusion",
        name="Ambient Occlusion",
        description="Ambient Occlusion",
    )

    metallic_strings: StringProperty(
        default="metallic,metal,met,metalness,specular,specularity,spec,reflection,refl,ref",
        name="Metallic / Specular",
        description="Metallic",
    )

    roughness_strings: StringProperty(
        default="roughness,rough,glossiness,gloss,smoothness,smooth",
        name="Roughness / Glossiness",
        description="Roughness",
    )

    normal_strings: StringProperty(
        default="normal,norm,nor,nrm,bump,bmp,height",
        name="Normal / Bump",
        description="Normal",
    )

    opacity_strings: StringProperty(
        default="opacity,alpha,presence,transparency,transp",
        name="Opacity / Transparency",
        description="Opacity",
    )

    translucency_strings: StringProperty(
        default="translucency,translucence,translucent,transmission",
        name="Translucency",
        description="Translucency",
    )

    emission_strings: StringProperty(
        default="emission,emissive,emit,glow",
        name="Emission",
        description="Emission",
    )

    displacement_strings: StringProperty(
        default="displacement,displace,disp",
        name="Displacement",
        description="Displacement",
    )

    custom1_strings: StringProperty(
        default="custom1",
        name="Custom 1",
        description="Custom 1",
    )

    custom2_strings: StringProperty(
        default="custom2",
        name="Custom 2",
        description="Custom 2",
    )

    backup_textures: BoolProperty(
        default=True,
        name="Create Backup",
        description="Backup Textures",
    )

    converted_texture_format: EnumProperty(
        items=[
            ("png", "PNG", "PNG"),
            ("jpg", "JPEG", "JPEG (no alpha)"),
            ("tiff", "TIFF", "TIFF"),
        ],
        default="png",
        name="Converted Texture Format",
        description="The format to convert textures to.\nRecommended: PNG",
    )

    # Mesh Optimization

    decimation_render: BoolProperty(
        default=True,
        name="Render Decimation",
        description="Decimation",
    )

    decimation_viewport: BoolProperty(
        default=True,
        name="Viewport Decimation",
        description="Decimation",
    )

    decimation_dynamic_render: BoolProperty(
        default=True,
        name="Dynamic",
        description="Render",
    )

    decimation_max_render: FloatProperty(
        default=100,
        min=1,
        max=100,
        name="Max. Quality",
        description="Max",
        subtype="PERCENTAGE",
    )

    decimation_min_render: FloatProperty(
        default=1,
        min=1,
        max=100,
        name="Min. Quality",
        description="Min",
        subtype="PERCENTAGE",
    )

    decimation_ratio_render: FloatProperty(
        default=10,
        min=1,
        max=100,
        name="Quality Change",
        description="Ratio",
        subtype="PERCENTAGE",
    )

    decimation_render_factor: FloatProperty(
        default=50,
        min=1,
        max=100,
        name="Render Factor",
        description="Render Factor",
        subtype="PERCENTAGE",
    )

    decimation_dynamic_viewport: BoolProperty(
        default=True,
        name="Dynamic",
        description="Viewport",
    )

    decimation_max_viewport: FloatProperty(
        default=100,
        min=1,
        max=100,
        name="Max. Quality",
        description="Max",
        subtype="PERCENTAGE",
    )

    decimation_min_viewport: FloatProperty(
        default=1,
        min=1,
        max=100,
        name="Min. Quality",
        description="Min",
        subtype="PERCENTAGE",
    )

    decimation_ratio_viewport: FloatProperty(
        default=10,
        min=1,
        max=100,
        name="Quality Change",
        description="Ratio",
        subtype="PERCENTAGE",
    )

    decimation_viewport_factor: FloatProperty(
        default=50,
        min=1,
        max=100,
        name="Viewport Factor",
        description="Viewport Factor",
        subtype="PERCENTAGE",
    )

    decimation_selected: BoolProperty(
        default=False,
        name="Selected Only",
        description="Selected",
    )

    decimation_keyframe: BoolProperty(
        default=True,
        name="Keyframe",
        description="Keyframe",
    )

    # Render Estimator

    renderestimator_duration: StringProperty(
        default="00:00:00",
        name="Duration",
    )

    renderestimator_subframes: IntProperty(
        default=3,
        min=-1,
        name="Subframes",
        description="How many subframes to render.\n-1 = Auto",
    )

    renderestimator_divisions: IntProperty(
        default=1,
        min=0,
        max=2,
        name="Divisions",
        description="How many times the render should be divided.",
    )

# Register

classes = (
    SFR_Settings,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sfr_settings = bpy.props.PointerProperty(type=SFR_Settings)

def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

    try:
        del bpy.types.Scene.sfr_settings
    except:
        pass