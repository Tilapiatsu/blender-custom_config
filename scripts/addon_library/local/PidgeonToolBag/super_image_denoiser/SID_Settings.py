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

from .SID_Functions import (
    update_diffuse,
    update_glossy,
    update_transmission,
    update_volume,
    update_emission,
    update_environment,
    update_multilayer_exr,
)


def get_percent_complete(self):
    jobs_total = self['jobs_total']
    jobs_done = self['jobs_done']
    return 0 if jobs_total == 0 else 100 * jobs_done / jobs_total


def set_percent_complete(self, value):
    pass


class DenoiseRenderStatus(PropertyGroup):
    is_rendering: BoolProperty(
        name="Rendering",
        description="Currently rendering",
        default=False,
        options=set(),  # Not animatable!
    )

    should_stop: BoolProperty(
        name="Stop",
        description="User requested stop",
        default=False,
        options=set(),  # Not animatable!
    )

    jobs_total: IntProperty(
        name="Total Jobs",
        description="Total number of jobs to run",
        options=set(),  # Not animatable!
    )

    jobs_done: IntProperty(
        name="Jobs Done",
        description="Number of jobs completed",
        options=set(),  # Not animatable!
    )

    jobs_remaining: IntProperty(
        name="Jobs Remaining",
        description="Number of jobs still remaining to complete",
        options=set(),  # Not animatable!
    )

    percent_complete: FloatProperty(
        name="%",
        description="Percentage of jobs completed",
        subtype='PERCENTAGE',
        min=0,
        max=100,
        options=set(),  # Not animatable!
        get=get_percent_complete,
        set=set_percent_complete,
    )


class SID_Settings(PropertyGroup):

    ## General ##

    # Denoiser Type

    denoiser_type: EnumProperty(
        name="Denoiser Type",
        description="Choose the denoiser type.\nSID: Images and Animations.\nSID-Temporal: Animations.",
        items=[
            ('SID', 'SID', 'Super Image Denoiser', "ANTIALIASED", 0),
            ('SIDT', 'SID Temporal', 'Temporal Animation Denoiser using Super Image Denoiser', "TEMP", 1),
        ],
        default="SID",
        options=set(),  # Not animatable!
    )

    # Quality

    quality: EnumProperty(
        name="Quality",
        description="Choose the quality of the final denoised image. Affects memory usage and speed for compositing",
        items=(
            ('Standard', 'Standard', "Standard denoiser quality (fast compositing time, uses least memory)", "IPO_SINE", 0),
            ('High', 'High', "Extra denoiser quality (moderate compositing time, uses a little more memory)", "IPO_QUAD", 1),
            ('Super', 'Super', "Highest denoiser quality (slower compositing time, uses significantly more memory)", "IPO_CUBIC", 2),
        ),
        default="Super",
        options=set(),  # Not animatable!
    )

    # Passes

    diffuse: BoolProperty(
        name="Diffuse",
        description="Denoise the diffuse pass",
        default=True,
        options=set(),  # Not animatable!
        update=update_diffuse,
    )

    glossy: BoolProperty(
        name="Glossy",
        description="Denoise the glossy pass",
        default=True,
        options=set(),  # Not animatable!
        update=update_glossy,
    )

    transmission: BoolProperty(
        name="Transmission",
        description="Denoise the transmission pass",
        default=True,
        options=set(),  # Not animatable!
        update=update_transmission,
    )

    volume: BoolProperty(
        name="Volume",
        description="Denoise the volume pass",
        default=True,
        options=set(),  # Not animatable!
        update=update_volume,
    )

    emission: BoolProperty(
        name="Emission",
        description="Denoise the emission pass",
        default=True,
        options=set(),  # Not animatable!
        update=update_emission,
    )

    environment: BoolProperty(
        name="Environment",
        description="Denoise the environment pass",
        default=True,
        options=set(),  # Not animatable!
        update=update_environment,
    )

    # Multilayer EXR

    multilayer_exr: BoolProperty(
        name="Multilayer EXR",
        description="Outputs a multilayer EXR file in addition to the rendered file,\ncontaining all the denoised Passes.\nThis is useful for when you want to do further compositing in another program",
        default=False,
        update=update_multilayer_exr,
    )

    multilayer_exr_path: StringProperty(
        name="",
        description="The directory where the multilayer EXR files will be saved",
        default="//SID/",
        subtype="DIR_PATH",
    )

    # Working Directory

    working_directory: StringProperty(
        name="Working Directory",
        description="The directory where the rendered and denoised images will be saved",
        default="//SID/",
        subtype="DIR_PATH",
    )

    custom_name: StringProperty(
        name="Custom File Name",
        description="The custom name of the rendered and denoised images.\nLeave empty for default name.",
        default="",
    )

    # Smaller EXR Files

    smaller_exr_files: BoolProperty(
        name="Smaller EXR Files",
        description="Saves the EXR files with the smallest possible file size.\nThis makes the EXR files slower to load in other programs, but saves a lot of disk space\nLossy compression is used, but usually unnoticeable",
        default=False,
    )

    # Preview Render

    preview_render: BoolProperty(
        name="Preview Render",
        description="Render in the background, without a preivew.\nThis option saves a lot of memory, but you can't see the render progress",
        default=True,
    )

    use_sac: BoolProperty(
        name="Use Super Advanced Camera",
        description="Use the Super Advanced Camera addon for compositing effects.\nThis will make the compositor useable again for temporal denoising.\n\nThis option rquieres the Super Advanced Camera addon to be installed and enabled.",
        default=False,
    )

    # Motion Blur
    # Use
    motion_blur: BoolProperty(
        name="Motion Blur",
        description="Use motion blur when denoising",
        default=True,
        options=set(),  # Not animatable!
    )
    # Samples
    motion_blur_samples: IntProperty(
        name="Samples",
        description="The amount of samples to use for motion blur",
        default=32,
        min=1,
        max=256,
        subtype="FACTOR"
    )
    # Shutter Speed
    motion_blur_shutter_speed: FloatProperty(
        name="Shutter Speed",
        description="The shutter speed to use for motion blur",
        default=0.5,
        min=0,
        max=1,
        subtype="FACTOR"
    )
    # Min Speed
    motion_blur_min_speed: IntProperty(
        name="Min Speed",
        description="The minimum intensity of motion blur a pixel will receive.\nThere will always be more motion blur than this, but this is the minimum",
        default=0,
        min=0,
        max=1024,
        subtype="FACTOR"
    )
    # Max Speed
    motion_blur_max_speed: IntProperty(
        name="Max Speed",
        description="The maximum intensity of motion blur a pixel will receive.\nThere will never be more motion blur than this.\n0 for no limit",
        default=0,
        min=0,
        max=1024,
        subtype="FACTOR"
    )
    # Curved Interpolation
    motion_blur_curved_interpolation: BoolProperty(
        name="Curved Interpolation",
        description="Interpolates between frames using a curve instead of linearly.\nThis makes the motion blur look more natural",
        default=False,
    )

    # TED-Filter
    # Source
    ted_source: EnumProperty(
        name="Filter Source",
        items=(
            ('Temporal Albedo', 'Color', "This will use the color of the surfaces to detect artifacts.\nUse this option if your scene has changes in lighting, reflections or shadows.", "IMAGE_RGB_ALPHA", 0),
            ('Image', 'Shaded', "This will use the shaded image to detect artifacts.\nUse this option if your scene has a lot of solid colored materials,\nlike a white wall, Leaves, Grass, etc.", "IMAGE_RGB", 1),
            ('Depth', 'Depth', "This will use the depth of the image to detect artifacts.\nWe recommend this option if your scene has a lot of transparent materials,\nlike glass, water, etc.\nWarning: this option is experimental! If you get good results, please let us know!", "IMAGE_ZDEPTH", 2)
        ),
        default='Image',
        description="Chose the source the TED-Filter will use to detect artifacts.",
        options=set(),  # Not animatable!
    )
    # Threshold
    ted_threshold: FloatProperty(
        name="Filter Threshold",
        default=3,
        min=0,
        max=50,
        subtype="FACTOR",
        description="The higher, the more agressive the TED-Filter will be.\nThe TED-Filter detects artifacts caused by fast movement.\nWe recommend a value between 2 and 5 for most scenes.\nA value of 0 will disable the filter.",
        options=set(),  # Not animatable!
    )
    # Radius
    ted_radius: IntProperty(
        name="Filter Radius",
        default=3,
        min=0,
        max=10,
        subtype="FACTOR",
        description="The higher, the more feathering the TED-Filter will have.\nThis value determins how smooth the transition of the TED-Filter should be.\nWe recommend a value between 2 and 5 for most scenes.\nA value of 0 will disable the filter.",
        options=set(),  # Not animatable!
    )

    # Overscan

    overscan: IntProperty(
        name="Overscan",
        description="The amount of pixels to render outside of the frame.\nUseful on fast camera motion.",
        default=5,
        min=0,
        max=20,
        subtype="PERCENTAGE",
    )

    # Frame Compensation

    frame_compensation: BoolProperty(
        name="Frame Compensation",
        description="Due to the way temporal denoising works, the first and the last 2 frames will be cut off.\nThis option will compensate for that by using non temporal denoised frames as a replacement",
        default=True,
    )

    # File Format

    file_format: EnumProperty(
        name="File Output",
        items=(
            ('PNG','PNG',"This is the slowest option\nsuiteable for final rendering.\nExports as 16bit RGBA PNG, 0% compression.\nWarning: no compression!"),
            ('JPEG','JPEG',"This is the smallest file size and fastest processing option.\nsuiteable for previewing.\nExports as RGB JPG, 90% quality.\nWarning: lossy compression, may cause JPEG artifacts!"),
            ('OPEN_EXR','EXR',"This is the highest quality option\nsuiteable if you want to edit the frames later.\nExports as 32bit RGBA EXR, piz compression.\nWarning: this will use a lot of disk space!"),
            ('TIFF','TIFF',"This is the second highest quality option\nsuiteable if you want to edit the frames later.\nTakes color management into consideration.\nExports as 16bit RGBA TIFF, no compression.\nWarning: this will use a lot of disk space!"),
        ),
        default='PNG',
        description="Choose the file format step 2 will output.",
        options=set(),  # Not animatable!
    )

    file_format_video: EnumProperty(
        name="File Output",
        items=(
            ('H264_in_MP4','H264 in MP4', ''),
            ('Xvid','Xvid', ''),
            ('WebM_VP9','WebM (VP9+Opus)', ''),
            ('Ogg_Theora','Ogg Theora', ''),
            ('H264_in_Matroska','H264 in Matroska', ''),
            ('H264_in_Matroska_for_scrubbing','H264 in Matroska for scrubbing', ''),
        ),
        default='H264_in_MP4',
        description="Choose the file format step 3 will output.\nIf you need more options, let us know!",
        options=set(),  # Not animatable!
    )

    ffmpeg_use_autosplit: BoolProperty(
        name="Autosplit",
        description="Split the video into multiple files if it's too big (2GB)",
        default=False,
    )

    ffmpeg_quality: EnumProperty(
        name="Quality",
        items=(
            ('NONE','Constant Bitrate', ''),
            ('LOSSLESS','Lossless', ''),
            ('PERC_LOSSLESS','Perceptually Lossless', ''),
            ('HIGH','High', ''),
            ('MEDIUM','Medium', ''),
            ('LOW','Low', ''),
            ('VERYLOW','Very Low', ''),
            ('LOWEST','Lowest', ''),
        ),
        default='MEDIUM',
        options=set(),  # Not animatable!
    )

    ffmpeg_preset: EnumProperty(
        name="Encoding Speed",
        items=(
            ('BEST','Slowest', ''),
            ('GOOD','Good', ''),
            ('REALTIME','Realtime', ''),
        ),
        default='GOOD',
        options=set(),  # Not animatable!
    )

    ffmpeg_video_bitrate: IntProperty(
        name="Video Bitrate",
        description="The bitrate of the video in kbps.\nHigher is better, but also bigger",
        default=6000,
        min=0,
        max=1000000,
        subtype="FACTOR",
    )


    # Show Panels

    show_quality: BoolProperty(
        default=True,
    )

    show_passes: BoolProperty(
        default=True,
    )

    show_general: BoolProperty(
        default=True,
    )

    show_advanced: BoolProperty(
        default=False,
    )

    show_sidt_render: BoolProperty(
        default=True,
    )

    show_sidt_denoise: BoolProperty(
        default=True,
    )

    show_sidt_denoise_mb: BoolProperty(
        default=True,
    )

    show_sidt_denoise_ted: BoolProperty(
        default=False,
    )

    show_sidt_combine: BoolProperty(
        default=False,
    )

    show_sidt_combine_video: BoolProperty(
        default=False,
    )


# Register

classes = (
    DenoiseRenderStatus,
    SID_Settings,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sid_denoiserender_status = bpy.props.PointerProperty(type=DenoiseRenderStatus)
    bpy.types.Scene.sid_settings = bpy.props.PointerProperty(type=SID_Settings)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

    try:
        del bpy.types.Scene.sid_settings
    except:
        pass

    try:
        del bpy.types.Scene.sid_denoiserender_status
    except:
        pass