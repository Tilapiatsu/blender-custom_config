import bpy
import json
import os
import mathutils
from bpy.types import (
    Context,
    Operator
)
from .groups.SuperAdvancedCamera import connect_renderLayer_node
from .SAC_Settings import SAC_Settings
from .SAC_Functions import load_image_once, create_dot_texture, hex_to_rgb, get_gradient, get_filter
from ..pidgeon_tool_bag.PTB_Functions import link_nodes


class SAC_OT_Initialize(Operator):
    bl_idname = "superadvancedcamera.superadvancedcamerainit"
    bl_label = "Initialize Super Advanced Camera"
    bl_description = ""

    def execute(self, context: Context):
        create_dot_texture()
        connect_renderLayer_node()

        return {'FINISHED'}


class SAC_OT_PreviousFilter(Operator):
    bl_idname = "superadvancedcamera.previous_filter"
    bl_label = ""
    bl_description = "Sets the previous filter as the active filter"

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        filters = []
        filter_type_list = settings.filter_types
        for index, filter_type in enumerate(filter_type_list):
            filters.append(filter_type[0])

        current_filter = context.scene.new_filter_type
        index = filters.index(current_filter)

        if index == 0:
            context.scene.new_filter_type = filters[len(filters)-1]
        else:
            context.scene.new_filter_type = filters[index-1]

        bpy.ops.superadvancedcamera.apply_filter()

        return {'FINISHED'}


class SAC_OT_NextFilter(Operator):
    bl_idname = "superadvancedcamera.next_filter"
    bl_label = ""
    bl_description = "Set the next filter as the active filter"

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        filters = []
        filter_type_list = settings.filter_types
        for index, filter_type in enumerate(filter_type_list):
            filters.append(filter_type[0])

        current_filter = context.scene.new_filter_type
        index = filters.index(current_filter)

        if index == len(filters)-1:
            context.scene.new_filter_type = filters[0]
        else:
            context.scene.new_filter_type = filters[index+1]

        bpy.ops.superadvancedcamera.apply_filter()

        return {'FINISHED'}


class SAC_OT_ApplyFilter(Operator):
    bl_idname = "superadvancedcamera.apply_filter"
    bl_label = "Apply Filter"
    bl_description = "Sets the current filter as the active filter"

    def execute(self, context: Context):
        bpy.data.node_groups[".SAC Colorgrade"].nodes["SAC Filter"].mute = False

        filter_channels = get_filter(context.scene.new_filter_type)
        channels = [
            bpy.data.node_groups[".SAC Filter"].nodes["SAC Colorgrade_Filter_Red"],
            bpy.data.node_groups[".SAC Filter"].nodes["SAC Colorgrade_Filter_Green"],
            bpy.data.node_groups[".SAC Filter"].nodes["SAC Colorgrade_Filter_Blue"]
        ]

        for channel, filter_channel in enumerate(filter_channels):
            channel_node = channels[channel]
            for curve, filter_curve in enumerate(filter_channel):
                channel_mapping = channel_node.mapping.curves[curve]
                for point, filter_point in enumerate(reversed(filter_curve)):
                    channel_mapping.points[point].location = (point/(len(filter_curve)-1), filter_point)
            channel_node.mapping.update()

        bpy.data.node_groups[".SAC Filter"].nodes["SAC Colorgrade_Filter_Mix"].inputs[0].default_value += 0

        return {'FINISHED'}


class SAC_OT_PreviousEffect(Operator):
    bl_idname = "superadvancedcamera.previous_effect"
    bl_label = ""
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        effects = []
        effect_type_list = settings.effect_types
        for index, effect_type in enumerate(effect_type_list):
            effects.append(effect_type[0])

        current_effect = context.scene.new_effect_type
        index = effects.index(current_effect)

        if index == 0:
            context.scene.new_effect_type = effects[len(effects)-1]
        else:
            context.scene.new_effect_type = effects[index-1]

        return {'FINISHED'}


class SAC_OT_NextEffect(Operator):
    bl_idname = "superadvancedcamera.next_effect"
    bl_label = ""
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        effects = []
        effect_type_list = settings.effect_types
        for index, effect_type in enumerate(effect_type_list):
            effects.append(effect_type[0])

        current_effect = context.scene.new_effect_type
        index = effects.index(current_effect)

        if index == len(effects)-1:
            context.scene.new_effect_type = effects[0]
        else:
            context.scene.new_effect_type = effects[index+1]

        return {'FINISHED'}


class SAC_OT_AddEffect(Operator):
    bl_idname = "superadvancedcamera.add_effect"
    bl_label = "Add a new effect to the list"

    def execute(self, context):
        item = context.scene.sac_effect_list.add()
        new_effect_type = context.scene.new_effect_type
        settings: SAC_Settings = context.scene.sac_settings

        # for each view layer, enable the Z pass
        for view_layer in context.scene.view_layers:
            view_layer.use_pass_z = True

        # Create the item_type_info dictionary from item_types
        item_type_info = {internal: (name, icon, internal) for internal, name, icon in settings.effect_types}

        item.name, item.icon, item.EffectGroup = item_type_info.get(new_effect_type, ('Untitled', 'NONE', ''))
        # Set the ID using the Scene property and increment it
        item.ID = str(context.scene.last_used_id).zfill(2)
        context.scene.last_used_id += 1

        # If the item is in array "slow", set the warning to True
        item.warn = new_effect_type in settings.slow_effects

        connect_renderLayer_node()
        context.scene.sac_effect_list_index = len(context.scene.sac_effect_list) - 1
        return {'FINISHED'}


class SAC_OT_RemoveEffect(Operator):
    bl_idname = "superadvancedcamera.remove_effect"
    bl_label = "Remove the selected effect from the list"

    @classmethod
    def poll(cls, context):
        return context.scene.sac_effect_list

    def execute(self, context):
        list_data = context.scene.sac_effect_list
        index = context.scene.sac_effect_list_index

        list_data.remove(index)
        connect_renderLayer_node()
        context.scene.sac_effect_list_index = min(max(0, index - 1), len(list_data) - 1)
        return {'FINISHED'}


class SAC_OT_MoveEffectUp(Operator):
    bl_idname = "superadvancedcamera.move_effect_up"
    bl_label = "Move the selected effect up in the list"

    @classmethod
    def poll(cls, context):
        return context.scene.sac_effect_list_index > 0

    def execute(self, context):
        list = context.scene.sac_effect_list
        index = context.scene.sac_effect_list_index

        list.move(index, index-1)
        context.scene.sac_effect_list_index = index - 1
        connect_renderLayer_node()
        return {'FINISHED'}


class SAC_OT_MoveEffectDown(Operator):
    bl_idname = "superadvancedcamera.move_effect_down"
    bl_label = "Move the selected effect down in the list"

    @classmethod
    def poll(cls, context):
        return context.scene.sac_effect_list_index < len(context.scene.sac_effect_list) - 1

    def execute(self, context):
        list = context.scene.sac_effect_list
        index = context.scene.sac_effect_list_index

        list.move(index, index+1)
        context.scene.sac_effect_list_index = index + 1
        connect_renderLayer_node()
        return {'FINISHED'}


class SAC_OT_ApplyEffectPreset(Operator):
    bl_idname = "superadvancedcamera.apply_effect_preset"
    bl_label = "Apply Effect Preset"
    bl_description = "Apply the selected effect preset to the list"

    def execute(self, context: Context):
        settings = context.scene.sac_settings
  
        # get the selected effect preset
        effect_preset = settings.Effects_Presets
        effect_preset_file = os.path.join(os.path.dirname(__file__), "presets", f"{effect_preset}.sacpe")
        effect_preset_json = open(effect_preset_file, "r")
        effect_preset_data = json.load(effect_preset_json)
        effect_preset_json.close()

        # print every effect name in the effect preset
        for effect in effect_preset_data["effects"]:
            context.scene.new_effect_type = effect["name"]
            bpy.ops.superadvancedcamera.add_effect()
            for setting in effect["settings"]:
                setattr(settings, setting, effect["settings"][setting])


        return {'FINISHED'}
    
class SAC_OT_OpenPresetFolder(Operator):
    bl_idname = "superadvancedcamera.open_preset_folder"
    bl_label = "Open Preset Folder"
    bl_description = "Open the folder containing the effect presets"

    def execute(self, context: Context):
        presets_dir = os.path.join(os.path.dirname(__file__), "presets")
        os.startfile(presets_dir)
        return {'FINISHED'}
    
class SAC_OT_AddEffectPreset(Operator):
    bl_idname = "superadvancedcamera.add_effect_preset"
    bl_label = "Add Effect Preset"
    bl_description = "Add the current effects to the selected effect preset"

    def execute(self, context: Context):
        settings = context.scene.sac_settings

        preset_name = settings.Effects_Preset_Name
        preset_file = os.path.join(os.path.dirname(__file__), "presets", f"{preset_name}.sacpe")
        if not os.path.exists(preset_file):
            preset_json = open(preset_file, "w")
            preset_json.write("{\n\t\"effects\": [\n\t]\n}")
            preset_json.close()
        else:
            self.report({'ERROR'}, "Preset already exists")
  
        # get every effect and its settings, and add it to the json file
        effect_preset_json = open(preset_file, "r")
        effect_preset_data = json.load(effect_preset_json)
        effect_preset_json.close()
        effect_list = []
        effect_id = 0
        for effect in context.scene.sac_effect_list:
            # select each effect
            context.scene.sac_effect_list_index = effect_id
            effect_dict = {}
            effect_dict["name"] = effect.EffectGroup
            effect_dict["settings"] = {}
            if effect.EffectGroup == "SAC_CHROMATICABERRATION":
                effect_dict["settings"]["Effects_ChromaticAberration_Amount"] = settings.Effects_ChromaticAberration_Amount
            elif effect.EffectGroup == "SAC_DUOTONE":
                effect_dict["settings"]["Effects_Duotone_Color1"] = settings.Effects_Duotone_Color1
                effect_dict["settings"]["Effects_Duotone_Color2"] = settings.Effects_Duotone_Color2
                effect_dict["settings"]["Effects_Duotone_Clamp"] = settings.Effects_Duotone_Blend
                effect_dict["settings"]["Effects_Duotone_Color1_Start"] = settings.Effects_Duotone_Color1_Start
                effect_dict["settings"]["Effects_Duotone_Color2_Start"] = settings.Effects_Duotone_Color2_Start
                effect_dict["settings"]["Effects_Duotone_Color1_Mix"] = settings.Effects_Duotone_Color1_Mix
                effect_dict["settings"]["Effects_Duotone_Color2_Mix"] = settings.Effects_Duotone_Color2_Mix
                effect_dict["settings"]["Effects_Duotone_Blend"] = settings.Effects_Duotone_Blend
            elif effect.EffectGroup == "SAC_EMBOSS":
                effect_dict["settings"]["Effects_Emboss_Strength"] = settings.Effects_Emboss_Strength
            elif effect.EffectGroup == "SAC_FILMGRAIN":
                effect_dict["settings"]["Filmgrain_strength"] = settings.Filmgrain_strength
                effect_dict["settings"]["Filmgrain_dustproportion"] = settings.Filmgrain_dustproportion
                effect_dict["settings"]["Filmgrain_size"] = settings.Filmgrain_size
            elif effect.EffectGroup == "SAC_FISHEYE":
                effect_dict["settings"]["Effects_Fisheye"] = settings.Effects_Fisheye
            elif effect.EffectGroup == "SAC_FOGGLOW":
                effect_dict["settings"]["Effects_FogGlow_Strength"] = settings.Effects_FogGlow_Strength
                effect_dict["settings"]["Effects_FogGlow_Threshold"] = settings.Effects_FogGlow_Threshold
                effect_dict["settings"]["Effects_FogGlow_Size"] = settings.Effects_FogGlow_Size
            elif effect.EffectGroup == "SAC_GHOST":
                effect_dict["settings"]["Effects_Ghosts_Strength"] = settings.Effects_Ghost_Strength
                effect_dict["settings"]["Effects_Ghosts_Threshold"] = settings.Effects_Ghost_Threshold
                effect_dict["settings"]["Effects_Ghosts_Count"] = settings.Effects_Ghosts_Count
                effect_dict["settings"]["Effects_Ghosts_Distortion"] = settings.Effects_Ghosts_Distortion
            elif effect.EffectGroup == "SAC_GRADIENTMAP":
                effect_dict["settings"]["Effects_GradientMap_blend"] = settings.Effects_GradientMap_blend
            elif effect.EffectGroup == "SAC_HALFTONE":
                effect_dict["settings"]["Effects_Halftone_value"] = settings.Effects_Halftone_value
                effect_dict["settings"]["Effects_Halftone_delta"] = settings.Effects_Halftone_delta
                effect_dict["settings"]["Effects_Halftone_size"] = settings.Effects_Halftone_size
            elif effect.EffectGroup == "SAC_HDR":
                effect_dict["settings"]["Effects_HDR_blend"] = settings.Effects_HDR_blend
                effect_dict["settings"]["Effects_HDR_exposure"] = settings.Effects_HDR_exposure
                effect_dict["settings"]["Effects_HDR_sigma"] = settings.Effects_HDR_sigma
                effect_dict["settings"]["Effects_HDR_delta"] = settings.Effects_HDR_delta
            elif effect.EffectGroup == "SAC_INFRARED":
                effect_dict["settings"]["Effects_Infrared_Blend"] = settings.Effects_Infrared_Blend
                effect_dict["settings"]["Effects_Infrared_Offset"] = settings.Effects_Infrared_Offset
            elif effect.EffectGroup == "SAC_ISONOISE":
                effect_dict["settings"]["ISO_strength"] = settings.ISO_strength
                effect_dict["settings"]["ISO_size"] = settings.ISO_size
            elif effect.EffectGroup == "SAC_MOSAIC":
                effect_dict["settings"]["Effects_Pixelate_PixelSize"] = settings.Effects_Pixelate_PixelSize
            elif effect.EffectGroup == "SAC_NEGATIVE":
                effect_dict["settings"]["Effects_Negative"] = settings.Effects_Negative
            elif effect.EffectGroup == "SAC_OVERLAY":
                effect_dict["settings"]["Effects_Overlay_Strength"] = settings.Effects_Overlay_Strength
            elif effect.EffectGroup == "SAC_PERSPECTIVESHIFT":
                effect_dict["settings"]["Effects_PerspectiveShift_Horizontal"] = settings.Effects_PerspectiveShift_Horizontal
                effect_dict["settings"]["Effects_PerspectiveShift_Vertical"] = settings.Effects_PerspectiveShift_Vertical
            elif effect.EffectGroup == "SAC_POSTERIZE":
                effect_dict["settings"]["Effects_Posterize_Steps"] = settings.Effects_Posterize_Steps
            elif effect.EffectGroup == "SAC_STREAKS":
                effect_dict["settings"]["Effects_Streaks_Strength"] = settings.Effects_Streaks_Strength
                effect_dict["settings"]["Effects_Streaks_Threshold"] = settings.Effects_Streaks_Threshold
                effect_dict["settings"]["Effects_Streaks_Count"] = settings.Effects_Streaks_Count
                effect_dict["settings"]["Effects_Streaks_Length"] = settings.Effects_Streaks_Length
                effect_dict["settings"]["Effects_Streaks_Fade"] = settings.Effects_Streaks_Fade
                effect_dict["settings"]["Effects_Streaks_Angle"] = settings.Effects_Streaks_Angle
                effect_dict["settings"]["Effects_Streaks_Distortion"] = settings.Effects_Streaks_Distortion
            elif effect.EffectGroup == "SAC_VIGNETTE":
                effect_dict["settings"]["Effects_Vignette_Intensity"] = settings.Effects_Vignette_Intensity
                effect_dict["settings"]["Effects_Vignette_Roundness"] = settings.Effects_Vignette_Roundness
                effect_dict["settings"]["Effects_Vignette_Feather"] = settings.Effects_Vignette_Feather
                effect_dict["settings"]["Effects_Vignette_Midpoint"] = settings.Effects_Vignette_Midpoint
            elif effect.EffectGroup == "SAC_WARP":
                effect_dict["settings"]["Effects_Warp"] = settings.Effects_Warp
            elif effect.EffectGroup == "SAC_BLUR":
                effect_dict["settings"]["Effects_Blur_Type"] = settings.Effects_Blur_Type
                effect_dict["settings"]["Effects_Blur_Bokeh"] = settings.Effects_Blur_Bokeh
                effect_dict["settings"]["Effects_Blur_Gamma"] = settings.Effects_Blur_Gamma
                effect_dict["settings"]["Effects_Blur_Relative"] = settings.Effects_Blur_Relative
                effect_dict["settings"]["Effects_Blur_AspectCorrection"] = settings.Effects_Blur_AspectCorrection
                effect_dict["settings"]["Effects_Blur_FactorX"] = settings.Effects_Blur_FactorX
                effect_dict["settings"]["Effects_Blur_FactorY"] = settings.Effects_Blur_FactorY
                effect_dict["settings"]["Effects_Blur_SizeX"] = settings.Effects_Blur_SizeX
                effect_dict["settings"]["Effects_Blur_SizeY"] = settings.Effects_Blur_SizeY
                effect_dict["settings"]["Effects_Blur_Extend"] = settings.Effects_Blur_Extend
                effect_dict["settings"]["Effects_Blur_Size"] = settings.Effects_Blur_Size
            else:
                print(f"Effect {effect.EffectGroup} not found or not supported")

            effect_list.append(effect_dict)
            effect_id += 1

        effect_preset_data["effects"] = effect_list

        effect_preset_json = open(preset_file, "w")
        json.dump(effect_preset_data, effect_preset_json, indent=4)
        effect_preset_json.close()

        return {'FINISHED'}


class SAC_OT_PreviousBokeh(Operator):
    bl_idname = "superadvancedcamera.previous_effect_bokeh"
    bl_label = ""
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        bokehs = []
        bokeh_type_list = settings.bokeh_types
        for index, bokeh_type in enumerate(bokeh_type_list):
            bokehs.append(bokeh_type[0])

        current_bokeh = context.scene.new_bokeh_type
        index = bokehs.index(current_bokeh)

        if index == 0:
            context.scene.new_bokeh_type = bokehs[len(bokehs)-1]
        else:
            context.scene.new_bokeh_type = bokehs[index-1]

        try:
            bpy.ops.superadvancedcamera.apply_effect_bokeh()
        except:
            print("No camera selected")

        return {'FINISHED'}


class SAC_OT_NextBokeh(Operator):
    bl_idname = "superadvancedcamera.next_effect_bokeh"
    bl_label = ""
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        bokehs = []
        bokeh_type_list = settings.bokeh_types
        for index, bokeh_type in enumerate(bokeh_type_list):
            bokehs.append(bokeh_type[0])

        current_bokeh = context.scene.new_bokeh_type
        index = bokehs.index(current_bokeh)

        if index == len(bokehs)-1:
            context.scene.new_bokeh_type = bokehs[0]
        else:
            context.scene.new_bokeh_type = bokehs[index+1]

        try:
            bpy.ops.superadvancedcamera.apply_effect_bokeh()
        except:
            print("No camera selected")

        return {'FINISHED'}


class SAC_OT_ApplyBokeh(Operator):
    bl_idname = "superadvancedcamera.apply_effect_bokeh"
    bl_label = "Apply selected Bokeh to the effect"
    bl_description = ""

    def execute(self, context: Context):

        bokeh_dir = os.path.join(os.path.dirname(__file__), "bokeh")
        image_name = f"{bpy.context.scene.new_bokeh_type}.jpg"
        image_path = os.path.join(bokeh_dir, image_name)

        image = load_image_once(image_path, image_name)

        index = context.scene.sac_effect_list_index
        item = context.scene.sac_effect_list[index] if context.scene.sac_effect_list else None

        node_group_name = f".{item.EffectGroup}_{item.ID}"
        bpy.data.node_groups[node_group_name].nodes["SAC Effects_Bokeh_Image"].image = image

        return {'FINISHED'}


class SAC_OT_PreviousCameraBokeh(Operator):
    bl_idname = "superadvancedcamera.previous_camera_bokeh"
    bl_label = ""
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        bokehs = []
        bokeh_type_list = settings.bokeh_types
        for index, bokeh_type in enumerate(bokeh_type_list):
            bokehs.append(bokeh_type[0])

        current_bokeh = context.scene.new_camera_bokeh_type
        index = bokehs.index(current_bokeh)

        if index == 0:
            context.scene.new_camera_bokeh_type = bokehs[len(bokehs)-1]
        else:
            context.scene.new_camera_bokeh_type = bokehs[index-1]

        try:
            bpy.ops.superadvancedcamera.apply_camera_bokeh()
        except:
            print("No camera selected")

        return {'FINISHED'}


class SAC_OT_NextCameraBokeh(Operator):
    bl_idname = "superadvancedcamera.next_camera_bokeh"
    bl_label = ""
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        bokehs = []
        bokeh_type_list = settings.bokeh_types
        for index, bokeh_type in enumerate(bokeh_type_list):
            bokehs.append(bokeh_type[0])

        current_bokeh = context.scene.new_camera_bokeh_type
        index = bokehs.index(current_bokeh)

        if index == len(bokehs)-1:
            context.scene.new_camera_bokeh_type = bokehs[0]
        else:
            context.scene.new_camera_bokeh_type = bokehs[index+1]

        try:
            bpy.ops.superadvancedcamera.apply_camera_bokeh()
        except:
            print("No camera selected")

        return {'FINISHED'}


class SAC_OT_ApplyCameraBokeh(Operator):
    bl_idname = "superadvancedcamera.apply_camera_bokeh"
    bl_label = "Apply Bokeh"
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        bokeh_dir = os.path.join(os.path.dirname(__file__), "bokeh")
        image_name = f"{bpy.context.scene.new_camera_bokeh_type}.jpg"
        image_path = os.path.join(bokeh_dir, image_name)

        image = load_image_once(image_path, image_name)

        camera_object = bpy.data.objects[settings.selected_camera]
        camera_data = bpy.data.cameras[camera_object.data.name]

        plane_name = f"SAC_Bokeh_{settings.selected_camera}"

        camera_location = camera_object.location
        camera_rotation = camera_object.rotation_euler
        matrix_rotation = camera_rotation.to_matrix()
        camera_data.clip_start = 0.0025

        forward_vector = mathutils.Vector((0, 0, -1))
        rotated_forward_vector = matrix_rotation @ forward_vector
        scaled_forward_vector = rotated_forward_vector * 0.003
        plane_location = camera_location + scaled_forward_vector

        try:
            bokeh_plane = bpy.data.objects[plane_name]

        except KeyError:
            bpy.ops.mesh.primitive_plane_add(size=0.2, enter_editmode=False, align='WORLD', location=plane_location, rotation=camera_rotation)
            bpy.context.view_layer.objects.active.name = plane_name
            bokeh_plane = bpy.data.objects[plane_name]
            bpy.ops.object.select_all(action='DESELECT')
            bokeh_plane.select_set(True)
            bpy.data.objects[settings.selected_camera].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[settings.selected_camera]
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            bokeh_plane.hide_select = True
            bokeh_plane.visible_diffuse = False
            bokeh_plane.visible_glossy = False
            bokeh_plane.visible_transmission = False
            bokeh_plane.visible_volume_scatter = False
            bokeh_plane.visible_shadow = False
            bokeh_plane.display_type = 'BOUNDS'
            bokeh_plane.cycles.use_motion_blur = False

        material_name = f".{plane_name}_Material"
        try:
            material = bpy.data.materials[material_name]
            material_node_tree = material.node_tree
            material_node_tree.nodes["SAC Camera_Bokeh_Image"].image = image

            for material_slot in bokeh_plane.material_slots:
                bokeh_plane.data.materials.clear()
            bokeh_plane.data.materials.append(material)

        except KeyError:
            material = bpy.data.materials.new(name=material_name)
            bokeh_plane.data.materials.append(material)
            material.use_nodes = True
            material_node_tree = material.node_tree

            for node in material_node_tree.nodes:
                material_node_tree.nodes.remove(node)

            texture_coordinate_node = material_node_tree.nodes.new(type='ShaderNodeTexCoord')

            vector_subtract_node = material_node_tree.nodes.new(type='ShaderNodeVectorMath')
            vector_subtract_node.operation = 'SUBTRACT'
            vector_subtract_node.inputs[1].default_value = (0.5, 0.5, 0.0)

            vector_rotate_node = material_node_tree.nodes.new(type='ShaderNodeVectorRotate')
            vector_rotate_node.rotation_type = 'Z_AXIS'
            vector_rotate_node.name = "SAC Camera_Bokeh_Rotate"

            vector_scale_node = material_node_tree.nodes.new(type='ShaderNodeVectorMath')
            vector_scale_node.operation = 'SCALE'
            vector_scale_node.inputs["Scale"].default_value = 10
            vector_scale_node.name = "SAC Camera_Bokeh_Scale"

            vector_add_node = material_node_tree.nodes.new(type='ShaderNodeVectorMath')
            vector_add_node.operation = 'ADD'
            vector_add_node.inputs[1].default_value = (0.5, 0.5, 0.0)

            image_texture_node = material_node_tree.nodes.new(type='ShaderNodeTexImage')
            image_texture_node.extension = 'CLIP'
            image_texture_node.image = image
            image_texture_node.name = "SAC Camera_Bokeh_Image"

            switch_node = material_node_tree.nodes.new(type='ShaderNodeMix')
            switch_node.data_type = "RGBA"
            switch_node.inputs["Factor"].default_value = 1
            switch_node.mute = True
            switch_node.name = "SAC Camera_Bokeh_Switch"

            custom_texture_node = material_node_tree.nodes.new(type='ShaderNodeTexImage')
            custom_texture_node.extension = 'CLIP'
            custom_texture_node.image = load_image_once(os.path.join(os.path.join(os.path.dirname(__file__), "bokeh"), "PidgeonTools.png"), "PidgeonTools.png")
            custom_texture_node.name = "SAC Camera_Bokeh_Custom_Texture"

            rgb_curves_node = material_node_tree.nodes.new(type='ShaderNodeRGBCurve')
            # add a new point to the curve
            rgb_curves_node.mapping.curves[3].points.new(0.25, 0.75)
            rgb_curves_node.name = "SAC Camera_Bokeh_Curves"

            transparent_bsdf_node = material_node_tree.nodes.new(type='ShaderNodeBsdfTransparent')
            material_output_node = material_node_tree.nodes.new(type='ShaderNodeOutputMaterial')

            # link the nodes
            link_nodes(material_node_tree, texture_coordinate_node, 'UV', vector_subtract_node, 0)
            link_nodes(material_node_tree, vector_subtract_node, 0, vector_rotate_node, 0)
            link_nodes(material_node_tree, vector_rotate_node, 0, vector_scale_node, 0)
            link_nodes(material_node_tree, vector_scale_node, 0, vector_add_node, 0)
            link_nodes(material_node_tree, vector_add_node, 0, image_texture_node, 0)
            link_nodes(material_node_tree, vector_add_node, 0, custom_texture_node, 0)
            link_nodes(material_node_tree, image_texture_node, 0, switch_node, 6)
            link_nodes(material_node_tree, custom_texture_node, 0, switch_node, 7)
            link_nodes(material_node_tree, switch_node, 2, rgb_curves_node, 1)
            link_nodes(material_node_tree, rgb_curves_node, 0, transparent_bsdf_node, 0)
            link_nodes(material_node_tree, transparent_bsdf_node, 0, material_output_node, 0)

        return {'FINISHED'}


class SAC_OT_SetStartFrame(Operator):
    bl_idname = "superadvancedcamera.set_start_frame"
    bl_label = "Set Start Frame"
    bl_description = "Sets the current frame as the start frame"

    def execute(self, context: Context):
        scene = context.scene
        if scene.use_preview_range:
            scene.frame_preview_start = scene.frame_current
        else:
            scene.frame_start = scene.frame_current

        return {'FINISHED'}


class SAC_OT_SetEndFrame(Operator):
    bl_idname = "superadvancedcamera.set_end_frame"
    bl_label = "Set End Frame"
    bl_description = "Sets the current frame as the end frame"

    def execute(self, context: Context):
        scene = context.scene
        if scene.use_preview_range:
            scene.frame_preview_end = scene.frame_current
        else:
            scene.frame_end = scene.frame_current

        return {'FINISHED'}


class SAC_OT_PreviousGradient(Operator):
    bl_idname = "superadvancedcamera.previous_gradient"
    bl_label = ""
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        gradients = []
        gradient_type_list = settings.gradient_types
        for index, gradient_type in enumerate(gradient_type_list):
            gradients.append(gradient_type[0])

        current_gradient = context.scene.new_gradient_type
        index = gradients.index(current_gradient)

        if index == 0:
            context.scene.new_gradient_type = gradients[len(gradients)-1]
        else:
            context.scene.new_gradient_type = gradients[index-1]

        try:
            bpy.ops.superadvancedcamera.apply_gradient()
        except:
            print("No camera selected")

        return {'FINISHED'}


class SAC_OT_NextGradient(Operator):
    bl_idname = "superadvancedcamera.next_gradient"
    bl_label = ""
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings

        gradients = []
        gradient_type_list = settings.gradient_types
        for index, gradient_type in enumerate(gradient_type_list):
            gradients.append(gradient_type[0])

        current_gradient = context.scene.new_gradient_type
        index = gradients.index(current_gradient)

        if index == len(gradients)-1:
            context.scene.new_gradient_type = gradients[0]
        else:
            context.scene.new_gradient_type = gradients[index+1]

        try:
            bpy.ops.superadvancedcamera.apply_gradient()
        except:
            print("No camera selected")

        return {'FINISHED'}


class SAC_OT_ApplyGradient(Operator):
    bl_idname = "superadvancedcamera.apply_gradient"
    bl_label = "Apply Gradient"
    bl_description = ""

    def execute(self, context: Context):
        settings: SAC_Settings = context.scene.sac_settings
        index = context.scene.sac_effect_list_index
        item = context.scene.sac_effect_list[index] if context.scene.sac_effect_list else None
        node_group_name = f".{item.EffectGroup}_{item.ID}"
        node = bpy.data.node_groups[node_group_name].nodes["SAC Effects_GradientMap"]

        # print(context.scene.new_gradient_type)
        while len(node.color_ramp.elements) > 1:
            node.color_ramp.elements.remove(node.color_ramp.elements[1])

        gradient_elements = get_gradient(context.scene.new_gradient_type)
        # for every element in the gradient, except the first
        for element in gradient_elements[1:]:
            # add a new element
            new_element = node.color_ramp.elements.new(element[0])
            # set the color of the new element
            new_element.color = hex_to_rgb(element[1])

        node.color_ramp.elements[0].position = gradient_elements[0][0]
        node.color_ramp.elements[0].color = hex_to_rgb(gradient_elements[0][1])

        return {'FINISHED'}


classes = (
    SAC_OT_Initialize,
    SAC_OT_PreviousFilter,
    SAC_OT_NextFilter,
    SAC_OT_ApplyFilter,
    SAC_OT_PreviousEffect,
    SAC_OT_NextEffect,
    SAC_OT_AddEffect,
    SAC_OT_RemoveEffect,
    SAC_OT_MoveEffectUp,
    SAC_OT_MoveEffectDown,
    SAC_OT_ApplyEffectPreset,
    SAC_OT_OpenPresetFolder,
    SAC_OT_AddEffectPreset,
    SAC_OT_PreviousBokeh,
    SAC_OT_NextBokeh,
    SAC_OT_ApplyBokeh,
    SAC_OT_NextCameraBokeh,
    SAC_OT_PreviousCameraBokeh,
    SAC_OT_ApplyCameraBokeh,
    SAC_OT_SetStartFrame,
    SAC_OT_SetEndFrame,
    SAC_OT_PreviousGradient,
    SAC_OT_NextGradient,
    SAC_OT_ApplyGradient,
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
