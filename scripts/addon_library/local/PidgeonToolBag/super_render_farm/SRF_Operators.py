import bpy
import os
from sys import platform
from bpy.types import (
    Context,
    Operator,
)

from .SRF_Functions import (
    display_progress_thread,
    start_pidgeon_render_farm,
    save_settings,
    download_latest_release,
)

# class SFR_OT_OpenFolder(Operator):
#     bl_idname = "superrenderfarm.open_folder"
#     bl_label = ""
#     bl_description = "Open Folder for Images"

#     def execute(self, context: Context):

#         path = os.path.dirname(os.path.realpath(__file__))
#         path = os.path.join(path, "pidgeon_render_farm")

#         os.startfile(path)
#         return {'FINISHED'}

class SFR_OR_PackExternalAndSave(Operator):
    bl_idname = "superrenderfarm.pack_external_and_save"
    bl_label = ""
    bl_description = "Pack external data and save the file"

    def execute(self, context: Context):
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile()

        return {'FINISHED'}
    
class SFR_OT_DownloadMaster(Operator):
    bl_idname = "superrenderfarm.download_master"
    bl_label = ""
    bl_description = "Download the latest master release"

    def execute(self, context: Context):

        download_latest_release(True)

        return {'FINISHED'}


class SRF_OT_StartRender(Operator):
    bl_idname = "superrenderfarm.start_render"
    bl_label = "Start Render"
    bl_description = "Uses the settings to start the render farm"

    def execute(self, context):
        print("Starting render...")

        scene = context.scene
        settings = scene.srf_settings

        project = start_pidgeon_render_farm(self, context)

        if settings.rs_close_blender:
            bpy.ops.wm.quit_blender()
        else:
            import threading

            thread = threading.Thread(target=display_progress_thread, args=(context,project))
            thread.start()

        return {"FINISHED"}
    
class SRF_OT_GoToOutputs(Operator):
    bl_idname = "superrenderfarm.gotooutput"
    bl_label = "Go To Outputs"
    bl_description = "Brings you to the outputs settings"

    def execute(self, context):
        context.space_data.context = "OUTPUT"

        return {'FINISHED'}
    
class SRF_OT_SaveMasterSettings(Operator):
    bl_idname = "superrenderfarm.save_master_settings"
    bl_label = "Save Master Settings"
    bl_description = "Saves the master settings to a file"

    def execute(self, context):
        print("Saving master settings...")
        settings = context.scene.srf_settings
        
        save_settings(settings)

        return {'FINISHED'}
    
class SRF_OT_OpenFolderRender(Operator):
    bl_idname = "superrenderfarm.openfolderrender"
    bl_label = "Open Folder"
    bl_description = "Open Folder with Rendered Images"

    def execute(self, context: Context):
        settings = context.scene.srf_settings

        # check if the folder exists
        if not os.path.exists(os.path.join(bpy.path.abspath(settings.master_working_directory))):
            self.report({'ERROR'}, "Folder does not exist, please render first.")
            return {'CANCELLED'}

        os.startfile(os.path.join(bpy.path.abspath(settings.master_working_directory)))
        return {'FINISHED'}

classes = (
    SFR_OR_PackExternalAndSave,
    SRF_OT_StartRender,
    SRF_OT_GoToOutputs,
    SRF_OT_OpenFolderRender,
    SRF_OT_SaveMasterSettings,
    SFR_OT_DownloadMaster,
    #SFR_OT_OpenFolder,
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
