from .SID_Functions import *
import bpy
import os
from math import ceil
from bpy.types import (
    Context,
    Operator,
    Event,
    Scene,
    ViewLayer,
    Timer
)

from typing import List, NamedTuple

class SID_OT_AddSID(Operator):
    bl_idname = "superimagedenoiser.addsuperimagedenoiser"
    bl_label = "Add Super Image Denoiser"
    bl_description = "Add Super Image Denoiser to the compositor"

    def execute(self, context: Context):
        connect_render_layers_to_sid()
        return {'FINISHED'}

class SID_OT_DetectPasses(Operator):
    bl_idname = "superimagedenoiser.detectpasses"
    bl_label = "Detect Passes"
    bl_description = "Detect passes from the materials"

    def execute(self, context: Context):
        settings = bpy.context.scene.sid_settings
        used_passes = set()
        # Mapping of node types to their used passes
        node_pass_mapping = {
            'BSDF_DIFFUSE': {'Diffuse'},
            'EMISSION': {'Emission'},
            'BSDF_GLASS': {'Glossy', 'Transmission'},
            'BSDF_GLOSSY': {'Glossy'},
            'BSDF_HAIR': {'Glossy', 'Transmission'},
            'BSDF_HAIR_PRINCIPLED': {'Glossy', 'Transmission'},
            'PRINCIPLED_VOLUME': {'Volume'},
            'VOLUME_ABSORPTION': {'Volume'},
            'VOLUME_SCATTER': {'Volume'},
            'BSDF_REFRACTION': {'Transmission'},
            'BSDF_SHEEN': {'Diffuse', 'Glossy'},
            'SUBSURFACE_SCATTERING': {'Diffuse'},
            'BSDF_TOON': {'Diffuse', 'Glossy'},
            'BSDF_TRANSLUCENT': {'Diffuse'},
            'BACKGROUND': {'Environment'},
        }
        # Check materials
        for mat in bpy.data.materials:
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    # Principled BSDF checks
                    if node.type == 'BSDF_PRINCIPLED':
                        if node.inputs['Metallic'].default_value < 1 or node.inputs['Transmission Weight'].default_value < 1 or node.inputs['Sheen Weight'].default_value > 0:
                            used_passes.add('Diffuse')

                        if node.inputs['Specular IOR Level'].default_value > 0 or \
                                node.inputs['Metallic'].default_value > 0 or \
                                node.inputs['Coat Weight'].default_value > 0:
                            used_passes.add('Glossy')

                        if node.inputs['Transmission Weight'].default_value > 0:
                            used_passes.add('Transmission')
                            used_passes.add('Glossy')

                        if node.inputs['Emission Strength'].default_value > 0:
                            used_passes.add('Emission')

                    # Other node checks
                    used_passes.update(node_pass_mapping.get(node.type, set()))

        # Check world nodes
        if bpy.context.scene.world and bpy.context.scene.world.use_nodes:
            for node in bpy.context.scene.world.node_tree.nodes:
                used_passes.update(node_pass_mapping.get(node.type, set()))

        # Output used passes
        # List of all passes to check
        passes_to_check = ["Diffuse", "Glossy", "Transmission", "Volume", "Emission", "Environment"]

        # Set attributes in `settings` based on the presence of passes in `used_passes`
        for pass_type in passes_to_check:
            setattr(settings, pass_type.lower(), pass_type in used_passes)

        return {'FINISHED'}

# region SID-Temporal

class SavedRenderSettings(NamedTuple):
    old_file_path: str
    old_focal_length: float
    old_render_res: float

class RenderJob(NamedTuple):
    filepath: str
    view_layer: ViewLayer
    view_layer_id: int

def save_render_settings(context: Context):
    scene = context.scene

    return SavedRenderSettings(
        old_file_path=scene.render.filepath,
        old_focal_length=context.scene.camera.data.lens,
        old_render_res=scene.render.resolution_percentage
    )

def restore_render_settings(scene, savedsettings: SavedRenderSettings):
    cleanup_temporal_output_node()

    scene.render.filepath = savedsettings.old_file_path
    scene.camera.data.lens = savedsettings.old_focal_length
    scene.render.resolution_percentage = savedsettings.old_render_res

def setup_render_settings(context: Context):
    scene = context.scene
    settings = bpy.context.scene.sid_settings

    scene.render.filepath = os.path.join(settings.working_directory, "preview", settings.custom_name + "######")
    scene.camera.data.lens = ceil(scene.camera.data.lens * ((100 - settings.overscan) / 100))
    scene.render.resolution_percentage = ceil(scene.render.resolution_percentage * ((100 + settings.overscan) / 100))

def create_render_job(scene: Scene) -> List[RenderJob]:
    settings = bpy.context.scene.sid_settings

    jobs: List[RenderJob] = []

    layer_counter = 0
    for view_layer in scene.view_layers:

        filepath = os.path.join(settings.working_directory, "preview", str(layer_counter), settings.custom_name + "######")
        job = RenderJob(
            filepath=filepath,
            view_layer=view_layer,
            view_layer_id=layer_counter
        )
        if layer_counter == 0:
            jobs.append(job)

        layer_counter += 1

    return jobs

class SID_OT_SIDTRender(Operator):
    bl_idname = "superimagedenoiser.sidtrender"
    bl_label = "Render Animation"
    bl_description = "Render Animation with SID-Temporal"

    timer: Timer = None
    stop: bool = False
    rendering: bool = False
    done: bool = False
    jobs: List[RenderJob] = []
    current_job: RenderJob = None

    # Render callbacks
    def render_pre(self, scene: Scene, dummy):
        self.rendering = True
        render_pre_info = f"Rendering... Frame: {str(scene.frame_current).zfill(len(str(scene.frame_end)))} of {scene.frame_end}"
        print(bcolors.OKCYAN + render_pre_info+ bcolors.ENDC)

    def render_post(self, scene: Scene, dummy):
        self.rendering = False
        render_post_info = f"Finished.... Frame: {str(scene.frame_current).zfill(len(str(scene.frame_end)))} of {scene.frame_end}"
        print(bcolors.OKGREEN + render_post_info+ bcolors.ENDC)

    def render_complete(self, scene: Scene, dummy):
        self.jobs.pop(0)
        self.done = True
        render_complete_info = f"Finished rendering animation from frame {scene.frame_start} to {scene.frame_end}, {scene.frame_end - scene.frame_start + 1} frames in total."
        print(bcolors.SUCCESS + render_complete_info+ bcolors.ENDC, "\n")
        restore_render_settings(scene, self.saved_render_settings)

    def render_cancel(self, scene: Scene, dummy):
        self.stop = True
        render_cancel_info = f"Cancelled rendering animation."
        print(bcolors.ABORT + render_cancel_info+ bcolors.ENDC, "\n")
        restore_render_settings(scene, self.saved_render_settings)

    @classmethod
    def poll(cls, context: Context):
        scene = context.scene
        sid_denoiserender_status = scene.sid_denoiserender_status

        return not sid_denoiserender_status.is_rendering

    def execute(self, context: Context):

        if not context.scene.camera:
            self.report({'ERROR'}, "No camera in scene")
            return {'CANCELLED'}  

        self.saved_render_settings = save_render_settings(context)
        setup_render_settings(context)

        render_start_info = f"Starting to render animation from frame {context.scene.frame_start} to {context.scene.frame_end}, {context.scene.frame_end - context.scene.frame_start + 1} frames in total."
        print(bcolors.OKBLUE + render_start_info+ bcolors.ENDC, "\n")

        connect_render_layers_to_sid()
        create_temporal_output_node()
        sid_denoiserender_status = bpy.context.scene.sid_denoiserender_status

        # Reset state
        self.stop = False
        self.rendering = False
        self.done = False

        # Prepare render jobs
        self.jobs = create_render_job(context.scene)
        self.current_job = None

        sid_denoiserender_status.is_rendering = True
        sid_denoiserender_status.should_stop = False
        sid_denoiserender_status.jobs_done = 0
        sid_denoiserender_status.jobs_remaining = sid_denoiserender_status.jobs_total = len(self.jobs)

        # Attach render callbacks
        bpy.app.handlers.render_pre.append(self.render_pre)
        bpy.app.handlers.render_post.append(self.render_post)
        bpy.app.handlers.render_cancel.append(self.render_cancel)
        bpy.app.handlers.render_complete.append(self.render_complete)

        # Setup timer and modal
        self.timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context: Context, event: Event):
        scene = context.scene

        sid_denoiserender_status = bpy.context.scene.sid_denoiserender_status

        if event.type == 'ESC':
            self.stop = True

        elif event.type == 'TIMER':
            was_cancelled = self.stop or sid_denoiserender_status.should_stop

            if was_cancelled or not self.jobs:

                # Remove callbacks
                bpy.app.handlers.render_pre.remove(self.render_pre)
                bpy.app.handlers.render_post.remove(self.render_post)
                bpy.app.handlers.render_cancel.remove(self.render_cancel)
                bpy.app.handlers.render_complete.remove(self.render_complete)
                context.window_manager.event_timer_remove(self.timer)

                sid_denoiserender_status.should_stop = False
                sid_denoiserender_status.is_rendering = False

                if was_cancelled:
                    return {'CANCELLED'}
                return {'FINISHED'}

            elif self.done or not self.current_job:

                self.start_job(context)

                sid_denoiserender_status.jobs_done += 1
                sid_denoiserender_status.jobs_remaining -= 1

        # Allow stop button to cancel rendering rather than this modal
        return {'PASS_THROUGH'}

    def start_job(self, context: Context):
        self.done = False
        bpy.ops.render.render("INVOKE_DEFAULT", animation=True)
    
class SID_OT_SIDTOpenFolderRendered(Operator):
    bl_idname = "superimagedenoiser.openfolderrendered"
    bl_label = "Open Folder"
    bl_description = "Open Folder with Rendered Images"

    def execute(self, context: Context):
        settings = bpy.context.scene.sid_settings

        # check if the folder exists
        if not os.path.exists(os.path.join(bpy.path.abspath(settings.working_directory), "processing")):
            self.report({'ERROR'}, "Folder does not exist, please render first.")
            return {'CANCELLED'}

        os.startfile(os.path.join(bpy.path.abspath(settings.working_directory), "processing"))
        return {'FINISHED'}

class SID_OT_SIDTDenoise(Operator):
    bl_idname = "superimagedenoiser.sidtdenoise"
    bl_label = "Denoise Animation"
    bl_description = "Denoise Animation with SID-Temporal"

    def execute(self, context: Context):
        settings = bpy.context.scene.sid_settings

        temporal_denoise_scene = bpy.data.scenes[context.scene.name].copy()

        for view_layer in temporal_denoise_scene.view_layers:
            view_layer.use = False
        view_layer.use = True

        # for each folder in the working directory get the name
        processing_frames_path = os.path.join(bpy.path.abspath(settings.working_directory), "processing")
        for folder in os.listdir(processing_frames_path):
            create_temporal_setup(temporal_denoise_scene, folder)
            
            for node in bpy.context.scene.node_tree.nodes:
                if node.label.startswith("SID Image"):
                    bpy.data.images.remove(node.image, do_unlink=True)
    
        print(bcolors.SUCCESS + "Finished denoising animation."+ bcolors.ENDC, "\n")

        print(bcolors.OKBLUE + "Cleaning up..."+ bcolors.ENDC, "\n")

        bpy.data.node_groups.remove(bpy.data.node_groups.get(".SID Temporal Align"))
        bpy.data.node_groups.remove(bpy.data.node_groups.get(".SID Temporal MedianMax"))
        bpy.data.node_groups.remove(bpy.data.node_groups.get(".SID Temporal MedianMin"))
        bpy.data.node_groups.remove(bpy.data.node_groups.get(".SID Temporal Crop"))

        print(bcolors.WARNING + "This error can be ignored."+ bcolors.ENDC)
        bpy.data.scenes.remove(temporal_denoise_scene, do_unlink=True)

        print(bcolors.SUCCESS +"Done!"+ bcolors.ENDC, "\n")
            
        return {'FINISHED'}
    
class SID_OT_SIDTOpenFolderDenoised(Operator):
    bl_idname = "superimagedenoiser.openfolderdenoised"
    bl_label = "Open Folder"
    bl_description = "Open Folder with Denoised Images"

    def execute(self, context: Context):
        settings = bpy.context.scene.sid_settings

        # check if the folder exists
        if not os.path.exists(os.path.join(bpy.path.abspath(settings.working_directory), "completed")):
            self.report({'ERROR'}, "Folder does not exist, please denoise first.")
            return {'CANCELLED'}

        os.startfile(os.path.join(bpy.path.abspath(settings.working_directory), "completed"))
        return {'FINISHED'}

class SID_OT_SIDTCombine(Operator):
    bl_idname = "superimagedenoiser.sidtcombine"
    bl_label = "Combine Frames To Animation"
    bl_description = "Combine Denoised Frames To Animation"

    def execute(self, context: Context):
        settings = bpy.context.scene.sid_settings

        combine_scene = bpy.data.scenes[context.scene.name].copy()

        for view_layer in combine_scene.view_layers:
            view_layer.use = False
        view_layer.use = True
        
        combine_scene.display_settings.display_device = "sRGB"
        combine_scene.sequencer_colorspace_settings.name = 'sRGB'
        combine_scene.view_settings.view_transform = "Standard"
        combine_scene.view_settings.look = "None"
        combine_scene.view_settings.exposure = 0
        combine_scene.view_settings.gamma = 1
        combine_scene.view_settings.use_curve_mapping = False

        # for each folder in the working directory get the name
        completed_frames_path = os.path.join(bpy.path.abspath(settings.working_directory), "processing")
        for folder in os.listdir(completed_frames_path):
            create_combine_setup(combine_scene, folder)
            
            for node in bpy.context.scene.node_tree.nodes:
                if node.label.startswith("SID Image"):
                    bpy.data.images.remove(node.image, do_unlink=True)
                    
        print(bcolors.SUCCESS + "Finished combining frames to animation."+ bcolors.ENDC, "\n")

        print(bcolors.OKBLUE + "Cleaning up..."+ bcolors.ENDC, "\n")

        print(bcolors.WARNING + "This error can be ignored."+ bcolors.ENDC)
        bpy.data.scenes.remove(combine_scene, do_unlink=True)

        print(bcolors.SUCCESS +"Done!"+ bcolors.ENDC, "\n")
        return {'FINISHED'}
    
class SID_OT_SIDTOpenFolderCombined(Operator):
    bl_idname = "superimagedenoiser.openfoldercombined"
    bl_label = "Open Folder"
    bl_description = "Open Folder with Combined Animation"

    def execute(self, context: Context):
        settings = bpy.context.scene.sid_settings

        # check if the folder exists
        if not os.path.exists(os.path.join(bpy.path.abspath(settings.working_directory), "combined")):
            self.report({'ERROR'}, "Folder does not exist, please combine first.")
            return {'CANCELLED'}

        os.startfile(os.path.join(bpy.path.abspath(settings.working_directory), "combined"))
        return {'FINISHED'}    

# endregion SID-Temporal

# register

classes = (
    SID_OT_AddSID,
    SID_OT_DetectPasses,
    SID_OT_SIDTRender,
    SID_OT_SIDTOpenFolderRendered,
    SID_OT_SIDTDenoise,
    SID_OT_SIDTOpenFolderDenoised,
    SID_OT_SIDTCombine,
    SID_OT_SIDTOpenFolderCombined,
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
