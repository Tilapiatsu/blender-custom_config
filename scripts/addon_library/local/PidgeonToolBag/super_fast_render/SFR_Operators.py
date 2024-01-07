import bpy
import os
from bpy.types import (
    Context,
    Operator,
)
from .SFR_Functions import *
from distutils.dir_util import copy_tree
from ..pidgeon_tool_bag.PTB_Functions import render_image, format_time, get_subframes, calculate_object_distance, clamp

#region bechmark_frame

class SFR_OT_Benchmark_Frame(Operator):
    bl_idname = "superfastrender.benchmark_frame"
    bl_label = "Frame Benchmark"
    bl_description = "Starts the benchmarking process for a single frame"
    
    # Dictionary to manage bounce data
    bounce_data = {
        "diffuse_bounces": {"bounces": [], "times": [], "brightness": []},
        "glossy_bounces": {"bounces": [], "times": [], "brightness": []},
        "transmission_bounces": {"bounces": [], "times": [], "brightness": []},
        "volume_bounces": {"bounces": [], "times": [], "brightness": []},
        "transparent_max_bounces": {"bounces": [], "times": [], "brightness": []},
        "caustics_reflective": {"bounces": [], "times": [], "brightness": []},
        "caustics_refractive": {"bounces": [], "times": [], "brightness": []}
    }
    
    # Helper method to setup render settings
    def setup_render_settings(self, context):
        settings = context.scene.sfr_settings
        cycles = context.scene.cycles
        
        # Backup old settings
        old_settings = {
            "render_resolution": context.scene.render.resolution_percentage,
            "denoiser": cycles.use_denoising,
            "samples": cycles.samples,
            "adaptive_sampling": cycles.use_adaptive_sampling,
            "output_format": context.scene.render.image_settings.file_format,
            "compositor": context.scene.use_nodes
        }

        # Apply new settings
        context.scene.render.resolution_percentage = settings.benchmark_resolution
        cycles.use_denoising = False
        cycles.samples = 10000
        cycles.use_adaptive_sampling = False
        cycles.use_animated_seed = False
        cycles.use_adaptive_sampling = False
        cycles.sample_clamp_direct = 0
        cycles.sample_clamp_indirect = 0
        cycles.use_light_tree = True
        cycles.blur_glossy = 1
        cycles.debug_use_spatial_splits = True
        cycles.debug_use_hair_bvh = True
        cycles.debug_use_compact_bvh = False
        context.scene.render.use_persistent_data = True
        context.scene.render.image_settings.file_format = 'PNG'
        context.scene.render.image_settings.color_mode = 'RGBA'
        context.scene.render.image_settings.color_depth = '16'
        context.scene.render.image_settings.compression = 0
        context.scene.use_nodes = False
        
        return old_settings
    
    # Helper method to restore render settings
    def restore_render_settings(self, context, old_settings):
        cycles = context.scene.cycles
        context.scene.render.resolution_percentage = old_settings["render_resolution"]
        cycles.use_denoising = old_settings["denoiser"]
        cycles.samples = old_settings["samples"]
        cycles.use_adaptive_sampling = old_settings["adaptive_sampling"]
        context.scene.render.image_settings.file_format = old_settings["output_format"]
        cycles.sample_clamp_indirect = 10
    
    # Render callbacks
    def execute(self, context: Context):
        print(bcolors.OKGREEN + "Starting benchmarking..." + bcolors.ENDC)
        settings = bpy.context.scene.sfr_settings
        cycles = context.scene.cycles

        # Clear data from previous benchmark
        for bounce_name in self.bounce_data:
            self.bounce_data[bounce_name]["bounces"].clear()
            self.bounce_data[bounce_name]["times"].clear()
            self.bounce_data[bounce_name]["brightness"].clear()

        # Setup render settings
        old_settings = self.setup_render_settings(context)

        # Determine benchmark scene type
        if settings.benchmark_scene_type == "INTERIOR":
            bounces = [4, 4, 4, 0, 2, 0, 0]
        elif settings.benchmark_scene_type == "EXTERIOR":
            bounces = [0, 0, 0, 0, 0, 0, 0]
        elif settings.benchmark_scene_type == "CUSTOM":
            bounces = [cycles.diffuse_bounces, cycles.glossy_bounces, cycles.transmission_bounces, cycles.volume_bounces, cycles.transparent_max_bounces, 1 if cycles.caustics_reflective else 0, 1 if cycles.caustics_refractive else 0]
        else:
            bounces = [0, 0, 0, 0, 0, 0, 0]

        bounce_order = [int(b) for b in settings.benchmark_scene_bounce_order.split(",")]
        threshold = settings.benchmark_threshold * 10

        for bounce_type in bounce_order:
            
            bounce_type_name = [
                "diffuse_bounces",
                "glossy_bounces",
                "transmission_bounces",
                "volume_bounces",
                "transparent_max_bounces",
                "caustics_reflective",
                "caustics_refractive"
            ][bounce_type]

            print(bcolors.OKCYAN + f"Benchmarking {['diffuse', 'glossy', 'transmission', 'volume', 'transparent', 'reflective', 'refractive'][bounce_type]} bounces..."+ bcolors.ENDC)
            previous_image_path = None

            while True:
                # Render current settings
                set_bounces(bounces)
                if settings.benchmark_add_keyframes:  context.scene.keyframe_insert(data_path=f"cycles.{bounce_type_name}")
                current_image_path = bpy.path.abspath(f"{settings.benchmark_path}/Benchmark/image_{bounce_type}_{sum(bounces)}.png")
                render_time = render_image(current_image_path)
                render_time = round(render_time, 2)
                bounces[bounce_type] += 1

                # Compare with previous image if it exists
                if previous_image_path:
                    image_a = cv2.imread(previous_image_path, cv2.IMREAD_UNCHANGED)
                    image_b = cv2.imread(current_image_path, cv2.IMREAD_UNCHANGED)

                    if image_a is None or image_b is None:
                        raise Exception(f"Failed to load images: {previous_image_path}, {current_image_path}")

                    brightness_difference = calculate_brightness_difference(image_a, image_b)

                    # Store data for plotting

                    # Correctly map numeric keys to string names
                    bounce_name = [
                        "diffuse_bounces", "glossy_bounces", "transmission_bounces", 
                        "volume_bounces", "transparent_max_bounces", 
                        "caustics_reflective", "caustics_refractive"
                    ][bounce_type]

                    self.bounce_data[bounce_name]["bounces"].append(bounces[bounce_type] - 2)
                    self.bounce_data[bounce_name]["times"].append(render_time)
                    self.bounce_data[bounce_name]["brightness"].append(brightness_difference)

                    # Check if the difference is below the threshold
                    if brightness_difference <= threshold:
                        print(bcolors.OKBLUE + f"No significant improvement in {bounce_name}. Reverting."+ bcolors.ENDC)
                        bounces[bounce_type] -= 2
                        set_bounces(bounces)
                        if settings.benchmark_add_keyframes: context.scene.keyframe_insert(data_path=f"cycles.{bounce_type_name}")
                        break
                    
                    plot_data_rso(self.bounce_data[bounce_name]["times"], self.bounce_data[bounce_name]["brightness"], self.bounce_data[bounce_name]["bounces"], bounce_name)
            
                previous_image_path = current_image_path

        # Restore settings after benchmarking
        self.restore_render_settings(context, old_settings)

        # Remove files then folder
        if os.path.exists(os.path.join(bpy.path.abspath(settings.benchmark_path), "Benchmark")):
            for file in os.listdir(os.path.join(bpy.path.abspath(settings.benchmark_path), "Benchmark")):
                os.remove(os.path.join(bpy.path.abspath(settings.benchmark_path), "Benchmark", file))
            os.rmdir(os.path.join(bpy.path.abspath(settings.benchmark_path), "Benchmark"))
            
        print(bcolors.OKGREEN + "Benchmarking complete."+ bcolors.ENDC)
        self.report({'INFO'}, "Benchmarking complete.")

        return {'FINISHED'}
    
class SFR_OT_OpenFolderBenchmarked(Operator):
    bl_idname = "superfastrender.openfolderbenchmark"
    bl_label = "Open Folder"
    bl_description = "Open Folder with Benchmarked Images"

    def execute(self, context: Context):
        settings = bpy.context.scene.sfr_settings

        # check if the folder exists
        if not os.path.exists(os.path.join(bpy.path.abspath(settings.benchmark_path))):
            self.report({'ERROR'}, "Folder does not exist, please benchmark first.")
            return {'CANCELLED'}

        os.startfile(os.path.join(bpy.path.abspath(settings.benchmark_path)))
        return {'FINISHED'}


#endregion bechmark_frame

#region previews
class SFR_OT_Preset_Preview(Operator):
    bl_idname = "superfastrender.preset_preview"
    bl_label = "Preview Preset"
    bl_description = "Fastest possible render settings - for previewing."

    def execute(self, context: Context):
        cycles = bpy.context.scene.cycles
        render = bpy.context.scene.render

        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.5
        cycles.adaptive_min_samples = 0
        cycles.samples = 1024
        cycles.time_limit = 0
        cycles.use_preview_adaptive_sampling = False
        cycles.preview_samples = 32
        render.preview_pixel_size = '8'
        
        cycles.max_bounces = 0
        cycles.diffuse_bounces = 0
        cycles.glossy_bounces = 0
        cycles.transmission_bounces = 0
        cycles.volume_bounces = 0
        cycles.transparent_max_bounces = 0
        cycles.caustics_reflective = False
        cycles.caustics_refractive = False
        cycles.sample_clamp_direct = 0
        cycles.sample_clamp_indirect = 10
        cycles.use_light_tree = True
        cycles.auto_scrambling_distance = False
        cycles.scrambling_distance = 0.6
        cycles.preview_scrambling_distance = True

        cycles.volume_step_rate = 10
        cycles.volume_preview_step_rate = 10
        cycles.volume_max_steps = 64

        cycles.use_auto_tile = True
        cycles.tile_size = 2048

        cycles.debug_use_spatial_splits = True
        cycles.debug_use_hair_bvh = True
        render.use_persistent_data = True

        render.use_simplify = True
        render.simplify_subdivision = 0
        render.simplify_child_particles = 0.1
        cycles.texture_limit = "128"
        render.simplify_volumes = 0.1
        render.simplify_subdivision_render = 2
        render.simplify_child_particles_render = 0.1
        cycles.texture_limit_render = "128"

        cycles.use_camera_cull = True
        cycles.camera_cull_margin = 0.1
        cycles.use_distance_cull = True
        cycles.distance_cull_margin = 50

        self.report({'INFO'}, "Applied Preview Preset")

        return {'FINISHED'}

class SFR_OT_Preset_Fast(Operator):
    bl_idname = "superfastrender.preset_fast"
    bl_label = "Fast Preset"
    bl_description = "Fast render settings - for quick renders."

    def execute(self, context: Context):
        cycles = bpy.context.scene.cycles
        render = bpy.context.scene.render

        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.1
        cycles.adaptive_min_samples = 0
        cycles.samples = 1024
        cycles.time_limit = 0
        cycles.use_preview_adaptive_sampling = False
        cycles.preview_samples = 32
        render.preview_pixel_size = '2'
        
        cycles.max_bounces = 3
        cycles.diffuse_bounces = 1
        cycles.glossy_bounces = 1
        cycles.transmission_bounces = 1
        cycles.volume_bounces = 0
        cycles.transparent_max_bounces = 1
        cycles.caustics_reflective = False
        cycles.caustics_refractive = False
        cycles.sample_clamp_direct = 0
        cycles.sample_clamp_indirect = 10
        cycles.use_light_tree = True
        cycles.auto_scrambling_distance = False
        cycles.scrambling_distance = 0.8
        cycles.preview_scrambling_distance = True

        cycles.volume_step_rate = 5
        cycles.volume_preview_step_rate = 10
        cycles.volume_max_steps = 128

        cycles.use_auto_tile = True
        cycles.tile_size = 2048

        cycles.debug_use_spatial_splits = True
        cycles.debug_use_hair_bvh = True
        render.use_persistent_data = True

        render.use_simplify = True
        render.simplify_subdivision = 1
        render.simplify_child_particles = 0.1
        cycles.texture_limit = "512"
        render.simplify_volumes = 0.3
        render.simplify_subdivision_render = 3
        render.simplify_child_particles_render = 0.5
        cycles.texture_limit_render = "512"

        cycles.use_camera_cull = True
        cycles.camera_cull_margin = 0.1
        cycles.use_distance_cull = True
        cycles.distance_cull_margin = 150

        self.report({'INFO'}, "Applied Fast Preset")

        return {'FINISHED'}

class SFR_OT_Preset_Default(Operator):
    bl_idname = "superfastrender.preset_default"
    bl_label = "Default Preset"
    bl_description = "Default blender render settings. No optimizations."

    def execute(self, context: Context):
        cycles = bpy.context.scene.cycles
        render = bpy.context.scene.render

        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.01
        cycles.adaptive_min_samples = 0
        cycles.samples = 4096
        cycles.time_limit = 0
        cycles.use_preview_adaptive_sampling = True
        cycles.preview_adaptive_threshold = 0.1
        cycles.preview_adaptive_min_samples = 0
        cycles.preview_samples = 1024
        render.preview_pixel_size = 'AUTO'

        cycles.max_bounces = 12
        cycles.diffuse_bounces = 4
        cycles.glossy_bounces = 4
        cycles.transmission_bounces = 12
        cycles.volume_bounces = 0
        cycles.transparent_max_bounces = 8
        cycles.caustics_reflective = True
        cycles.caustics_refractive = True
        cycles.blur_glossy = 1
        cycles.sample_clamp_direct = 0
        cycles.sample_clamp_indirect = 10
        cycles.use_light_tree = True
        cycles.light_sampling_threshold = 0.01
        cycles.auto_scrambling_distance = False
        cycles.scrambling_distance = 1
        cycles.preview_scrambling_distance = False

        cycles.volume_step_rate = 1
        cycles.volume_preview_step_rate = 1
        cycles.volume_max_steps = 1024

        cycles.use_auto_tile = True
        cycles.tile_size = 2048

        cycles.debug_use_spatial_splits = False
        cycles.debug_use_hair_bvh = True
        render.use_persistent_data = False

        render.use_simplify = False
        render.simplify_subdivision = 6
        render.simplify_child_particles = 1
        cycles.texture_limit = "OFF"
        render.simplify_volumes = 1
        render.simplify_subdivision_render = 6
        render.simplify_child_particles_render = 1
        cycles.texture_limit_render = "OFF"

        cycles.use_camera_cull = False
        cycles.camera_cull_margin = 0.1
        cycles.use_distance_cull = False
        cycles.distance_cull_margin = 50

        self.report({'INFO'}, "Applied Blender Default Preset")

        return {'FINISHED'}

class SFR_OT_Preset_High(Operator):
    bl_idname = "superfastrender.preset_high"
    bl_label = "High Preset"
    bl_description = "High quality render settings - for final renders."

    def execute(self, context: Context):
        cycles = bpy.context.scene.cycles
        render = bpy.context.scene.render

        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.01
        cycles.adaptive_min_samples = 0
        cycles.samples = 4096
        cycles.time_limit = 0
        cycles.use_preview_adaptive_sampling = True
        cycles.preview_adaptive_threshold = 0.1
        cycles.preview_adaptive_min_samples = 0
        cycles.preview_samples = 1024
        render.preview_pixel_size = 'AUTO'

        cycles.max_bounces = 42
        cycles.diffuse_bounces = 8
        cycles.glossy_bounces = 8
        cycles.transmission_bounces = 24
        cycles.volume_bounces = 2
        cycles.transparent_max_bounces = 24
        cycles.caustics_reflective = True
        cycles.caustics_refractive = True
        cycles.blur_glossy = 0.5
        cycles.sample_clamp_direct = 0
        cycles.sample_clamp_indirect = 50
        cycles.use_light_tree = True
        cycles.auto_scrambling_distance = False
        cycles.scrambling_distance = 0.9
        cycles.preview_scrambling_distance = False

        cycles.volume_step_rate = 1
        cycles.volume_preview_step_rate = 1
        cycles.volume_max_steps = 1024

        cycles.use_auto_tile = True
        cycles.tile_size = 2048

        cycles.debug_use_spatial_splits = True
        cycles.debug_use_hair_bvh = True
        render.use_persistent_data = True

        render.use_simplify = False

        cycles.use_camera_cull = True
        cycles.camera_cull_margin = 0.1
        cycles.use_distance_cull = False

        self.report({'INFO'}, "Applied High Preset")

        return {'FINISHED'}

class SFR_OT_Preset_Ultra(Operator):
    bl_idname = "superfastrender.preset_ultra"
    bl_label = "Ultra Preset"
    bl_description = "Best possible render settings - for fun renders."

    def execute(self, context: Context):
        cycles = bpy.context.scene.cycles
        render = bpy.context.scene.render

        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.001
        cycles.adaptive_min_samples = 0
        cycles.samples = 8192
        cycles.time_limit = 0
        cycles.use_preview_adaptive_sampling = False
        cycles.preview_samples = 0
        render.preview_pixel_size = '1'

        cycles.max_bounces = 264
        cycles.diffuse_bounces = 64
        cycles.glossy_bounces = 64
        cycles.transmission_bounces = 128
        cycles.volume_bounces = 8
        cycles.transparent_max_bounces = 256
        cycles.caustics_reflective = True
        cycles.caustics_refractive = True
        cycles.blur_glossy = 0
        cycles.sample_clamp_direct = 0
        cycles.sample_clamp_indirect = 0
        cycles.use_light_tree = True
        cycles.auto_scrambling_distance = False
        cycles.scrambling_distance = 1
        cycles.preview_scrambling_distance = False

        cycles.volume_step_rate = 0.5
        cycles.volume_preview_step_rate = 0.5
        cycles.volume_max_steps = 2048

        cycles.use_auto_tile = True
        cycles.tile_size = 2048

        cycles.debug_use_spatial_splits = True
        cycles.debug_use_hair_bvh = True
        render.use_persistent_data = True

        render.use_simplify = False

        cycles.use_camera_cull = False
        cycles.use_distance_cull = False

        self.report({'INFO'}, "Applied Ultra Preset")

        return {'FINISHED'}

#endregion previews

# region textures
class SFR_OT_Texture_Optimization(Operator):
    bl_idname = "superfastrender.texture_optimization"
    bl_label = "Texture Optimization"
    bl_description = "Optimize textures for lower memory usage."

    def execute(self, context: Context):
        bpy.ops.file.pack_all()
        bpy.ops.file.unpack_all(method="USE_LOCAL")
        settings = bpy.context.scene.sfr_settings
        path = bpy.path.abspath("//textures/")
        
        if settings.backup_textures:
            print(bcolors.OKCYAN + "Backing up textures..."+ bcolors.ENDC)
            from_dir = path
            to_dir = bpy.path.abspath("//textures_backup/")
            if not os.path.exists(to_dir):
                os.makedirs(to_dir)
            try:
                copy_tree(from_dir, to_dir)
            except:
                print(bcolors.WARNING + "Failed to backup textures."+ bcolors.ENDC)
                return {'CANCELLED'}
            print(bcolors.OKGREEN + "Backup complete."+ bcolors.ENDC)

        # turn strings separated by comma to array
        diffuse_textures = settings.diffuse_strings.split(",")
        ao_textures= settings.ao_strings.split(",")
        metallic_textures = settings.metallic_strings.split(",")
        roughness_textures = settings.roughness_strings.split(",")
        normal_textures = settings.normal_strings.split(",")
        opacity_textures = settings.opacity_strings.split(",")
        displacement_textures = settings.displacement_strings.split(",")
        custom1_textures = settings.custom1_strings.split(",")
        custom2_textures = settings.custom2_strings.split(",")

        # Don't resize the same texture more than once
        resized_textures = {}

        for file in os.listdir(path):
            if not os.path.isfile(os.path.join(path, file)):
                continue

            results = [
                resize_texture(file, settings.diffuse_factor, diffuse_textures, "diffuse", resized_textures),
                resize_texture(file, settings.ao_factor, ao_textures, "ao", resized_textures),
                resize_texture(file, settings.metallic_factor, metallic_textures, "metallic", resized_textures),
                resize_texture(file, settings.roughness_factor, roughness_textures, "roughness", resized_textures),
                resize_texture(file, settings.normal_factor, normal_textures, "normal", resized_textures),
                resize_texture(file, settings.opacity_factor, opacity_textures, "opacity", resized_textures),
                resize_texture(file, settings.displacement_factor, displacement_textures, "displacement", resized_textures),
                resize_texture(file, settings.custom1_factor, custom1_textures, "custom1", resized_textures),
                resize_texture(file, settings.custom2_factor, custom2_textures, "custom2", resized_textures)
            ]
            if True in results:
                remap_texture(file)

        print(bcolors.OKGREEN + "Texture optimization complete."+ bcolors.ENDC)
        return {'FINISHED'}
    
# endregion textures

#region mesh
class SFR_OT_Mesh_Optimization_Frame(Operator):
    bl_idname = "superfastrender.mesh_optimization_frame"
    bl_label = "Frame Optimization"
    bl_description = "Optimizes the mesh for selected objects. (uses modifiers)"

    def execute(self, context: Context):
        # remove the optimization first
        bpy.ops.superfastrender.mesh_optimization_remove()
        print(bcolors.OKGREEN + "Starting Mesh Optimization..." + bcolors.ENDC)
        # set some variables
        settings = bpy.context.scene.sfr_settings
        active_camera_loc = bpy.context.scene.camera.location
        depsgraph = bpy.context.evaluated_depsgraph_get()
        objects_to_optimize = []

        if settings.decimation_selected:
            objects_to_optimize = bpy.context.selected_objects
        else:
            objects_to_optimize = bpy.context.scene.objects

        for object_to_optimize in objects_to_optimize:
            if object_to_optimize.type not in {'MESH'}:
                continue
                
            object_mesh = object_to_optimize.evaluated_get(depsgraph).to_mesh()
            if len(object_mesh.polygons) < 3:
                continue

            polygon_density = len(object_mesh.polygons) / ((object_to_optimize.dimensions[0] + 0.01) * (object_to_optimize.dimensions[1] + 0.01) * (object_to_optimize.dimensions[2] + 0.01)) / 1000
            object_distance = calculate_object_distance(object_to_optimize.location, active_camera_loc)

            decimation_ratio_render = clamp((1-((object_distance * polygon_density) * (settings.decimation_ratio_render/100) / 100))**5,(settings.decimation_min_render/100),(settings.decimation_max_render/100))
            decimation_ratio_render = decimation_ratio_render if settings.decimation_dynamic_render else (settings.decimation_render_factor/100)

            decimation_ratio_viewport = clamp((1-((object_distance * polygon_density) * (settings.decimation_ratio_viewport/100) / 100))**5,(settings.decimation_min_viewport/100),(settings.decimation_max_viewport/100))
            decimation_ratio_viewport = decimation_ratio_viewport if settings.decimation_dynamic_viewport else (settings.decimation_viewport_factor/100)
            
            # Render
            if ("[SFR] - Decimate - Render" not in object_to_optimize.modifiers) and settings.decimation_render:
                decimate_modifier = object_to_optimize.modifiers.new(name="[SFR] - Decimate - Render", type='DECIMATE')
                decimate_modifier.show_viewport = False
                decimate_modifier.use_collapse_triangulate = True
                decimate_modifier.ratio = decimation_ratio_render
                print(bcolors.OKCYAN + "Adding Render Optimization: " + object_to_optimize.name + bcolors.ENDC)
            else:
                try:
                    object_to_optimize.modifiers.get("[SFR] - Decimate - Render").ratio = decimation_ratio_render
                    print(bcolors.OKCYAN + "Updating Render Optimization: " + object_to_optimize.name + bcolors.ENDC)
                except:
                    pass

            # Viewport
            if ("[SFR] - Decimate - Viewport" not in object_to_optimize.modifiers) and settings.decimation_viewport:
                decimate_modifier = object_to_optimize.modifiers.new(name="[SFR] - Decimate - Viewport", type='DECIMATE')
                decimate_modifier.show_render = False
                decimate_modifier.use_collapse_triangulate = True
                decimate_modifier.ratio = decimation_ratio_viewport
                print(bcolors.OKCYAN + "Adding Viewport Optimization: " + object_to_optimize.name + bcolors.ENDC)
            else:
                try:
                    object_to_optimize.modifiers.get("[SFR] - Decimate - Viewport").ratio = decimation_ratio_viewport
                    print(bcolors.OKCYAN + "Updating Viewport Optimization: " + object_to_optimize.name + bcolors.ENDC)
                except:
                    pass

            if settings.decimation_keyframe:
                try: 
                    object_to_optimize.keyframe_insert(data_path= 'modifiers["[SFR] - Decimate - Render"].ratio')
                    object_to_optimize.keyframe_insert(data_path= 'modifiers["[SFR] - Decimate - Viewport"].ratio')
                except:
                    pass
        print(bcolors.OKGREEN + "Mesh Optimization complete."+ bcolors.ENDC)
        return {'FINISHED'}

class SFR_OT_Mesh_Optimization_Remove(Operator):
    bl_idname = "superfastrender.mesh_optimization_remove"
    bl_label = "Remove Optimization"
    bl_description = "Removes the mesh optimization for the selected objects."

    def execute(self, context: Context):
        print(bcolors.OKGREEN + "Removing Mesh Optimization..." + bcolors.ENDC)
        settings = bpy.context.scene.sfr_settings

        objects_to_remove = []
        if settings.decimation_selected:
            objects_to_remove = bpy.context.selected_objects
        else:
            objects_to_remove = bpy.context.scene.objects

        for object_to_remove in objects_to_remove:
            if "[SFR] - Decimate - Render" not in object_to_remove.modifiers:
                continue
            else:
                print(bcolors.OKCYAN + "Removing Render Optimization: " + object_to_remove.name + bcolors.ENDC)
                object_to_remove.modifiers.remove(object_to_remove.modifiers.get("[SFR] - Decimate - Render"))
                
            if "[SFR] - Decimate - Viewport" not in object_to_remove.modifiers:
                continue
            else:
                print(bcolors.OKCYAN + "Removing Viewport Optimization: " + object_to_remove.name + bcolors.ENDC)
                object_to_remove.modifiers.remove(object_to_remove.modifiers.get("[SFR] - Decimate - Viewport"))
        
        return{'FINISHED'}
#endregion mesh

#region estimator
class SFR_OT_Estimator_Time(Operator):
    bl_idname = "superfastrender.estimator_time"
    bl_label = "Estimate Render Time"
    bl_description = "Estimates the render time for the animation"


    def execute(self, context: Context):
        print(bcolors.OKCYAN + "Starting Estimation..." + bcolors.ENDC)
        settings = bpy.context.scene.sfr_settings
        
        # Setup render settings
        old_resolution = context.scene.render.resolution_percentage
        old_current_frame = context.scene.frame_current
        context.scene.render.resolution_percentage = int((context.scene.render.resolution_percentage / (settings.renderestimator_divisions+1)))

        if settings.renderestimator_subframes == -1:
            subframes = int((context.scene.frame_end - context.scene.frame_start) / 120)
            print(subframes)
        else:
            subframes = settings.renderestimator_subframes

        total_render_time = []
        total_frames = []
        for i in get_subframes(subframes):
            print(bcolors.OKCYAN + f"Rendering frame {i} of {context.scene.frame_end}" + bcolors.ENDC)
            render_time = render_image(bpy.path.abspath(f"{settings.benchmark_path}/estimator/{i}.png"))
            total_render_time.append(round(render_time,2))
            total_frames.append(i)

            plot_data_estimator(total_render_time, total_frames)
        
        # Calculate average render time
        average_div_render_time = (sum(total_render_time) / len(total_render_time))
        average_frm_render_time = average_div_render_time * (4 ** settings.renderestimator_divisions)
        total_render_time = average_frm_render_time * (context.scene.frame_end - context.scene.frame_start)

        # turn average render time into a string for time formatted like 00:00:00 (hours:minutes:seconds)
        total_render_time_string = format_time(total_render_time)

        settings.renderestimator_duration = total_render_time_string
        
        # Restore settings after benchmarking
        context.scene.render.resolution_percentage = old_resolution
        context.scene.frame_current = old_current_frame

        # Remove files then folder
        if os.path.exists(os.path.join(bpy.path.abspath(settings.benchmark_path), "estimator")):
            for file in os.listdir(os.path.join(bpy.path.abspath(settings.benchmark_path), "estimator")):
                os.remove(os.path.join(bpy.path.abspath(settings.benchmark_path), "estimator", file))
            os.rmdir(os.path.join(bpy.path.abspath(settings.benchmark_path), "estimator"))

        print(bcolors.OKGREEN + "Estimation complete."+ bcolors.ENDC)
        return {'FINISHED'}
#endregion estimator

classes = (
    SFR_OT_Benchmark_Frame,
    SFR_OT_OpenFolderBenchmarked,

    SFR_OT_Preset_Preview,
    SFR_OT_Preset_Fast,
    SFR_OT_Preset_Default,
    SFR_OT_Preset_High,
    SFR_OT_Preset_Ultra,

    SFR_OT_Texture_Optimization,

    SFR_OT_Mesh_Optimization_Frame,
    SFR_OT_Mesh_Optimization_Remove,

    SFR_OT_Estimator_Time,
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
