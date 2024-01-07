import os
import bpy
from bpy.types import (
    Operator,
    Context,
)
try:
    from .SIU_Functions import upscale_image
except Exception:
    pass

try:
    import cv2
except Exception:
    pass

#region upscale

class SIU_OT_Upscale(Operator):
    bl_label = "Upscale Images"
    bl_idname = "superimageupscaler.upscale_images"

    def execute(self, context):
        settings = bpy.context.scene.siu_settings

        if not os.path.exists(os.path.join(bpy.path.abspath(settings.input_folder))):
            self.report({'ERROR'}, "Folder does not exist, please choose another folder.")
            return {'CANCELLED'}
        
        if not os.path.exists(os.path.join(bpy.path.abspath(settings.output_folder))):
            os.mkdir(os.path.join(bpy.path.abspath(settings.output_folder)))

        upscale_image()


        return {'FINISHED'}
    
class SIU_OT_OpenFolderUpscaled(Operator):
    bl_idname = "superimageupscaler.openfolderupscaled"
    bl_label = "Open Folder"
    bl_description = "Open Folder with Upscaled Images"

    def execute(self, context: Context):
        settings = bpy.context.scene.siu_settings

        # check if the folder exists
        if not os.path.exists(os.path.join(bpy.path.abspath(settings.output_folder))):
            self.report({'ERROR'}, "Folder does not exist, please upscale first.")
            return {'CANCELLED'}

        os.startfile(os.path.join(bpy.path.abspath(settings.output_folder)))
        return {'FINISHED'}

#endregion upscale

#region models

class SIU_OT_OpenFolderModels(Operator):
    bl_idname = "superimageupscaler.openfoldermodels"
    bl_label = "Open Folder"
    bl_description = "Open Folder with ESRGAN Models"

    def execute(self, context: Context):
        os.startfile(os.path.join(bpy.path.abspath(os.path.join(os.path.dirname(__file__), "esrgan", "models"))))
        return {'FINISHED'}

#endregion models

classes = (
    SIU_OT_Upscale,
    SIU_OT_OpenFolderUpscaled,
    SIU_OT_OpenFolderModels,
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
