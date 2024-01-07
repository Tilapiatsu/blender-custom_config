
import os
import bpy

from bpy.types import (
    PropertyGroup,
)

from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    FloatProperty,
)

class SIU_Settings(PropertyGroup):

    install_dependencies: BoolProperty(
        name="Install Dependencies",
        description="Installs the dependencies required by the Super Image Upscaler addon.\nThis is required for the Super Image Upscaler tools to work.\n\nThis will take up additional space on your disk.",
        default=False
    )

    ## General ##

    upscaler_type: EnumProperty(
        name="Upscaler Type",
        description="The upscaler that will be used to upscale the images.",
        items=(
            ("esrgan", "ESRGAN", "Uses ESRGAN to upscale the images.\nRecommended for most users."),
            ("stable", "Stable Diffusion", "Uses Stable Diffusion to upscale the images.\nRecommended for users powerful hardware."),
        ),
        default="esrgan"
    )

    input_folder: StringProperty(
        name="Input Folder",
        description="The folder where the low resolution images are stored.",
        default="//SIU/LowResImages/",
        subtype='DIR_PATH'
    )

    output_folder: StringProperty(
        name="Output Folder",
        description="The high resolution images will be stored here.",
        default="//SIU/HighResImages/",
        subtype='DIR_PATH'
    )

    output_prefix: StringProperty(
        name="Output Prefix",
        description="The prefix that will be added to the output images.",
        default=""
    )

    output_suffix: StringProperty(
        name="Output Suffix",
        description="The suffix that will be added to the output images.",
        default="_Upscaled"
    )

    output_format: EnumProperty(
        name="Output Format",
        description="The format that will be used to save the images.",
        items=(("jpg", "JPG", "Save the images in JPG format."),
               ("png", "PNG", "Save the images in PNG format."),
               ("tiff", "TIFF", "Save the images in TIFF format.")),
        default="jpg"
    )

    device: EnumProperty(
        name="Device",
        description="The device that will be used to upscale the images.",
        items=(
            ("cpu", "CPU", "Uses the CPU to upscale the images.\nThis is slower than using the GPU.\nRecommended for users without a Nvidia GPU."),
            ("cuda", "CUDA", "Uses the GPU to upscale the images.\nThis is faster than using the CPU.\nRecommended for users with a Nvidia GPU.")
        ),
        default="cuda"
    )

    mode_type: EnumProperty(
        name="Mode Type",
        description="The mode that will be used to upscale the images.",
        items=(
            ("nearest", "Nearest", "Uses the nearest pixel to upscale the images.\nThis mode works with the base model"),
            ("bilinear", "Bilinear", "Uses the bilinear algorithm to upscale the images"),
            ("bicubic", "Bicubic", "Uses the bicubic algorithm to upscale the images"),
        ),
        default="nearest"
    )

    scale_factor: EnumProperty(
        name="Scale Factor",
        description="The scale factor that will be used to upscale the images.",
        items=(
            ("0.5", "0.25x", "Downscales the images by 4x"),
            ("1", "1x", "Does not upscale the images"),
            ("2", "4x", "Upscales the images by 4x"),
        ),
        default="2"
    )

    def get_model_list(self, context):
        from glob import glob

        model_list = []

        for path in glob(os.path.join(os.path.dirname(__file__), "esrgan", "models", "*.pth")):
            model_list.append((path, os.path.splitext(os.path.basename(path))[0], ""))

        return model_list
    
    model_primary: EnumProperty(
        name="Primary Model",
        description="The first model that will be used to upscale the images.",
        items=get_model_list,
    )

    model_secondary: EnumProperty(
        name="Secondary Model",
        description="The second model that will be used to upscale the images.",
        items=get_model_list,
    )

    model_blend: FloatProperty(
        name="Blend Factor",
        description="The amount of blending between the two models.\n0.0 = 100% Primary Model\n1.0 = 100% Secondary Model",
        min=0.0,
        max=1.0,
        default=0.4,
        subtype='FACTOR'
    )

    # Show Panels

    show_general: BoolProperty(
        default=True,
    )

    show_advanced: BoolProperty(
        default=False,
    )


# Register

classes = (
    SIU_Settings,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.siu_settings = bpy.props.PointerProperty(type=SIU_Settings)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

    try:
        del bpy.types.Scene.siu_settings
    except:
        pass
