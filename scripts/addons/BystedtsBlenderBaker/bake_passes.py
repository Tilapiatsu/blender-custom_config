import bpy
from . import bake_manager
from enum import Enum

from bpy.props import (
    IntProperty,
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
    PointerProperty
)

class BakeType(Enum):
    TRANSMISSION = 0,
    GLOSSY = 1,
    DIFFUSE = 2,
    ENVIRONMENT = 3,
    EMIT = 4,
    ROUGHNESS = 5,
    UV = 6,
    NORMAL = 7,
    SHADOW = 8,
    AO = 9,
    COMBINED = 10,
    METALLIC = 11,
    BASE_COLOR = 12,
    CHANNEL_TRANSFER = 13

def get_bake_type_string(bake_type, no_underscore = False):
    '''
    Returns the bake type as string ("BASE_COLOR" etc)
    Since I'm using custom attributes on the fly it seems
    that it's not possible(?) to get the the enum string value.
    I just get the basic value (integer) when I use bake_pass['bake_type']
    '''
    # TODO: Check if this function is still used
    # OBS! 
    bake_types_list = [
    "TRANSMISSION",
    "GLOSSY",
    "DIFFUSE",
    "ENVIRONMENT",
    "EMIT",
    "ROUGHNESS",
    "UV",
    "NORMAL",
    "SHADOW",
    "AO",
    "COMBINED",
    "METALLIC",
    "BASE_COLOR",
    "CHANNEL_TRANSFER"        
    ]
    bake_type = bake_types_list[bake_type].replace("_", " ", 1000)
    return bake_type


class BakePass(bpy.types.PropertyGroup):

    auto_description = "Trust Bystedts preferred settings depending on the bake type"
    global_description = "Use the setting in the global settings in the top of the UI"
    temporary_description = "Use a temporary scene. This usually saves time, since less objects needs to be loaded. Lights will not be transferred to the temporary scene"


    #("GLOBAL_SETTINGS", "Global settings", global_description, 0),
    
    value_keyword_items = [
        ("AUTO", "Auto", auto_description, 0),
        ("SET", "Set", "", 1)
    ]



    name: bpy.props.StringProperty(name="Name", default="Unknown")

    ui_display: bpy.props.BoolProperty(name="UI display", default = False,  description = "Show or hide in UI")

    bake_type_items = [
        ("TRANSMISSION", "Transmission", "", 0),
        ("GLOSSY", "Glossy", "", 1),
        ("DIFFUSE", "Diffuse", "", 2),
        ("ENVIRONMENT",  "Environment", "", 3),
        ("EMIT",  "Emit", "", 4),
        ("ROUGHNESS", "Roughness", "", 5),
        ("UV",  "Uv", "", 6),
        ("NORMAL", "Normal", "", 7),
        ("SHADOW", "Shadow", "", 8),
        ("AO", "Ambient occlusion", "", 9),
        ("COMBINED", "Combined", "", 10),
        ("METALLIC", "Metallic", "", 11),
        ("BASE COLOR", "Base Color", "", 12),
        ("DISPLACEMENT", "Displacement", "", 13),
        ("ALPHA", "Alpha", "", 14),
        ("CHANNEL_TRANSFER", "Channel transfer", "", 15),  
    ]

    bake_type: bpy.props.EnumProperty(
        name="Bake type", 
        description = "Bake type", 
        items = bake_type_items, 
        default = "BASE COLOR")
    
    sample_type: bpy.props.EnumProperty(
        name="Sample type", 
        description = "Samples type", 
        default = "AUTO", 
        items = value_keyword_items)
    

    # I removed AUTO from bake space
    bake_locations_items = [
        ("AUTO", "Auto", "", 0),
        ("CURRENT_LOCATION", "Current location", "Use objects Current location during baking. Can result in wrong surface being hit", 1),
        ("EXPLODED", "Exploded", "Place objects far from each other during baking. Will avoid wrong surface being hit.", 2)
    ]

    bake_locations: bpy.props.EnumProperty(
        name="Bake space",
        description = "Bake space", 
        items = bake_locations_items)
    

    sub_pixel_sample_items = [
        ("AUTO", "Auto", auto_description, 0),
        ("1", "X 1", "", 1),
        ("2", "X 2", "", 2),
        ("4", "X 4", "", 3),       
    ]

    # Note to self: I used to set sub pixel sample per bake pass
    # changed my mind and used an over all setting instead
    sub_pixel_sample: bpy.props.EnumProperty(name="Sub pixel sample", description = "Higher sub pixel sample improves anti aliasing", items = sub_pixel_sample_items)


    bake_scene_items = [
        ("AUTO", "Auto", auto_description, 0),
        ("CURRENT", "Current scene", "Use current scene for baking", 1),
        ("TEMPORARY", "Temporary scene", temporary_description, 2),
    ]

    bake_scene: bpy.props.EnumProperty(
        name="Bake scene", 
        description = "Which scene to bake in", 
        default = "AUTO", 
        items = bake_scene_items)
  
    samples: bpy.props.IntProperty(
        name="Samples", 
        description = "Amount of samples during baking", 
        default=1, 
        min = 0, 
        soft_max = 256)

    normal_map_type_items = [
        ("OPEN_GL", "Open GL", "", 0),
        ("DIRECT_X", "Direct X", "", 1)
    ]

    normal_map_type: bpy.props.EnumProperty(
        name="Normal map type", 
        description = "Type of normal map", 
        items = normal_map_type_items, 
        default="OPEN_GL")

    post_process_items = [
        ("NO_POST_PROCESS", "No post process", "Don't perform post process", 0),
        ("AUTO", "Auto", "Trust Bystedts preferred settings", 1),
        ("DENOISE", "Denoise", "Use denoise", 2)

    ]

    post_process: bpy.props.EnumProperty(
        name="Post process", 
        description = "Which post process to perform on image after baking", 
        default = "AUTO", 
        items = post_process_items)

    
    image_name_override: bpy.props.BoolProperty(
        name="Image name override", 
        description = "Always use the bake pass name when naming images and files", 
        )       
 

    #-----
    R_source: bpy.props.StringProperty(
        name="R source", 
        description = "Which image to transfer red channel from", 
        )   

    G_source: bpy.props.StringProperty(
        name="G source", 
        description = "Which image to transfer green channel from", 
        )  

    B_source: bpy.props.StringProperty(
        name="B source", 
        description = "Which image to transfer blue channel from", 
        )   
    #-----
    
    
    channel_items = [
        ("R", "R", "Red channel", 0),
        ("G", "G", "Green channel", 1),
        ("B", "B", "Blue channel", 2),
        ("NONE", "None", "Don't transfer the channel", 3),
    ]

    transfer_target_channel_R: bpy.props.EnumProperty(
        name="Target channel red", 
        description = "Channel to transfer red to", 
        default = "R", 
        items = channel_items
        )
    
    transfer_target_channel_G: bpy.props.EnumProperty(
        name="Target channel green", 
        description = "Channel to transfer green to", 
        default = "G", 
        items = channel_items
        )
    
    transfer_target_channel_B: bpy.props.EnumProperty(
        name="Target channel blue", 
        description = "Channel to transfer bluie to", 
        default = "B", 
        items = channel_items
        )

    preview_bake_texture: bpy.props.BoolProperty(name = "Preview bake texture", default = 0)



def is_non_default_bake_pass(bake_pass_type):
    bake_pass_type = bake_pass_type.upper()
    list = [
        'METALLIC',
        'BASE COLOR',
        'DISPLACEMENT',
        'ALPHA'
    ]
    return bake_pass_type in list

def is_low_sample_pass(bake_pass):
    bake_pass_type = bake_pass.bake_type.upper()
    list = [
        'GLOSSY', 'DIFFUSE', 'EMIT', 'ROUGHNESS', 'UV', 'NORMAL',
        'METALLIC', 'BASE COLOR', 'DISPLACEMENT', 'ALPHA'
    ]
    return bake_pass_type in list   

def is_temporary_scene_bake_pass(bake_pass):

    bake_pass_type = bake_pass.bake_type.upper()
    list = [
        'GLOSSY', 'DIFFUSE', 'EMIT', 'ROUGHNESS', 'UV', 'NORMAL',
        'METALLIC', 'BASE COLOR', 'DISPLACEMENT', 'AO', 'SHADOW',
        'ALPHA'
    ]
    return bake_pass_type in list       

def add_bakepass(context, BakeType):
    new_bake_pass = context.scene.bake_passes.add()
    new_bake_pass.name = "New bake pass"

class RENDER_OT_delete_bake_pass(bpy.types.Operator):
    """Delete bake pass"""

    bl_idname = "render.delete_bake_pass"
    bl_label = "Delete bake pass"
    bl_description = "Delete bake pass"

    bake_pass_index: IntProperty(
        name="Index to delete",
        description="Index of the bake pass to delete",
        min=0, 
    )   

    def execute(self, context):
        context.scene.bake_passes.remove(self.bake_pass_index)
        return {'FINISHED'}

class RENDER_OT_toggle_bake_pass_ui_display(bpy.types.Operator):
    """Toggle bakepass ui display"""
    bl_idname = "render.toggle_bake_pass_ui_display"
    bl_label = "Expand/collapse"
    bl_description = "Toggle bakepass ui display"

    bake_pass_index: IntProperty(
        name="Index to toggle ui display",
        description="Index of the bake pass to toggle ui display",
        min=0, 
    )   

    def execute(self, context):

        if context.scene.bake_passes[self.bake_pass_index].ui_display == True:
            context.scene.bake_passes[self.bake_pass_index].ui_display = False
        else:
            context.scene.bake_passes[self.bake_pass_index].ui_display = True
       
       
        return {'FINISHED'}

def get_base_color(bake_type, alpha = 0.0):
    if bake_type == "NORMAL" or bake_type == "UV":
        base_color = [0.5, 0.5, 1.0, alpha]
    elif bake_type == "AO":
        base_color = [1.0, 1.0, 1.0, alpha]
    elif bake_type == "EMIT":
        base_color = [0, 0, 0, alpha]    
    elif bake_type == "ALPHA":
        base_color = [0, 0, 0, alpha]  
    else:
        base_color = [0.5, 0.5, 0.5, alpha]

    return base_color

def get_pass_from_string(bake_pass_string):
    index_start = bake_pass_string.rindex("_") + 1
    pass_name = bake_pass_string[index_start : len(bake_pass_string)]
    for bake_type in BakeType:
        if pass_name == str(bake_type.name):
            return bake_type         

def get_sorted_bake_passes_list(context):
    '''
    Return a list with all bakepasses in scene where
    they are sorted after which order they should be
    processed. Bake passes of type "channel_transfer"
    should be processed last for example
    '''
    prio_1_list = []
    prio_2_list = []
    for bake_pass in context.scene.bake_passes:
        if bake_pass.bake_type == 'CHANNEL_TRANSFER':
            prio_2_list.append(bake_pass)
        else:
            prio_1_list.append(bake_pass)

    sorted_bake_pass_list =  prio_1_list + prio_2_list

    return sorted_bake_pass_list


classes = (
    BakePass,
    RENDER_OT_delete_bake_pass,
    RENDER_OT_toggle_bake_pass_ui_display,
)

def register():
    for clas in classes:
        bpy.utils.register_class(clas)

    bpy.types.Scene.bake_passes = bpy.props.CollectionProperty(type=BakePass)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)

    del bpy.types.Scene.bake_passes