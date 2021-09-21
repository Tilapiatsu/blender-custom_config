import bpy
from . import bake_manager
from . import string_manager
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
    DISPLACEMENT = 13,
    ALPHA = 14,
    CHANNEL_TRANSFER = 15,
    AOV = 16,
    POINTINESS = 17

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
    "DISPLACEMENT",
    "ALPHA",
    "CHANNEL_TRANSFER",
    "AOV",
    "POINTINESS"      
    ]
    bake_type = bake_types_list[bake_type].replace("_", " ", 1000)
    return bake_type

def on_bake_type_update(self, context):

    from . import string_manager as sm

    # Get bake_pass from id data from self
    scene_string = repr(self.id_data)
    bake_pass_string = repr(self.path_from_id())
    bake_pass_string = bake_pass_string.replace("'", "")
    bake_pass = eval(scene_string + "." + bake_pass_string)
    bake_type = bake_pass.bake_type

    # Set old type if the custom attribute is missing
    old_type = bake_pass.get('old_type')
    if not old_type:
        bake_pass['old_type'] = bake_type
        old_type = ""

    # Rename if name is empty
    if bake_pass.name == "":
        print("renamed because name was empty")
        bake_pass.name = bake_type
        bake_pass['old_type'] = bake_type
        return

    print("\n old_type = " + old_type)
    old_name = ""
    new_name = ""

    print(bake_pass.name +".find(" + sm.to_camelcase(old_type) + ") = " + str(bake_pass.name.find(sm.to_camelcase(old_type))))
    
    if old_type == "":
        bake_pass.name = bake_type
        bake_pass['old_type'] = bake_type
        return

    # Camelcase
    if bake_pass.name.find(sm.to_camelcase(old_type)) > -1:
        print(old_type + " is camelcase")
        old_name = sm.to_camelcase(old_type)
        new_name = sm.to_camelcase(bake_type)
        
    # Underscore
    elif bake_pass.name.find(sm.to_underscore(old_type)) > -1:
        print(old_type + " is underscore")
        old_name = sm.to_underscore(old_type)
        new_name = sm.to_underscore(bake_type)

    # Uppercase
    elif bake_pass.name.find(old_type.upper()) > -1:
        print(old_type + " is uppercase")
        old_name = old_type.upper()
        new_name = bake_type.upper()

    print("working with " + bake_pass.name + ". Replaceing " + old_name + " with " + new_name)
    bake_pass.name = bake_pass.name.replace(old_name, new_name)
    bake_pass['old_type'] = bake_type



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

    # Don't forget to possibly add new passes to is_non_defualt_bake_pass 
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
        ("AOV", "AOV", "", 16),
        ("POINTINESS", "Pointiness", "", 17),
        ("MATERIAL_ID", "Material ID", "", 18),
    ]

    bake_type: bpy.props.EnumProperty(
        name="Bake type", 
        description = "Bake type", 
        items = bake_type_items, 
        default = "BASE COLOR",
        update = on_bake_type_update)
    
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

    # Normal ========================

    normal_space_items = [
        ("OBJECT", "Object", "", 0),
        ("TANGENT", "Tangent", "", 1)
    ]

    normal_space: bpy.props.EnumProperty(
        name="Space", 
        description = "Choose normal space for baking", 
        items = normal_space_items, 
        default="TANGENT")

    normal_map_type_items = [
        ("OPEN_GL", "Open GL", "", 0),
        ("DIRECT_X", "Direct X", "", 1)
    ]

    normal_map_type: bpy.props.EnumProperty(
        name="Normal map type", 
        description = "Type of normal map", 
        items = normal_map_type_items, 
        default="OPEN_GL")


    normal_map_swizzle_items = [
        ("POS_X", "+ X", "", 0),
        ("POS_Y", "+ Y", "", 1),
        ("POS_Z", "+ Z", "", 2),
        ("NEG_X", "+ X", "", 3),
        ("NEG_Y", "+ Y", "", 4),
        ("NEG_Z", "+ Z", "", 5)        
    ]

    normal_r: bpy.props.EnumProperty(
        name="Swizzle R", 
        description = "Type of normal map", 
        items = normal_map_swizzle_items, 
        default="POS_X")

    normal_g: bpy.props.EnumProperty(
        name="Swizzle G", 
        description = "Type of normal map", 
        items = normal_map_swizzle_items, 
        default="POS_Y")

    normal_b: bpy.props.EnumProperty(
        name="Swizzle B", 
        description = "Type of normal map", 
        items = normal_map_swizzle_items, 
        default="POS_Z")

    # Post process ========================

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
 
    # Channel transfer
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

    A_source: bpy.props.StringProperty(
        name="Alpha source", 
        description = "Which image to transfer alpha channel from", 
        )   
    #-----
    
    
    channel_items = [
        ("R", "R", "Red channel", 0),
        ("G", "G", "Green channel", 1),
        ("B", "B", "Blue channel", 2),
        ("A", "A", "Alpha channel", 3),
        ("NONE", "None", "Don't transfer the channel", 4),
    ]

    transfer_source_channelR: bpy.props.EnumProperty(
        name="Target channel red", 
        description = "Channel to transfer red to", 
        default = "R", 
        items = channel_items
        )
    
    transfer_source_channelG: bpy.props.EnumProperty(
        name="Target channel green", 
        description = "Channel to transfer green to", 
        default = "G", 
        items = channel_items
        )
    
    transfer_source_channelB: bpy.props.EnumProperty(
        name="Target channel blue", 
        description = "Channel to transfer blue to", 
        default = "B", 
        items = channel_items
        )

    transfer_source_channelA: bpy.props.EnumProperty(
        name="Target channel alpha", 
        description = "Channel to transfer alpha to", 
        default = "A", 
        items = channel_items
        )

    # AOV
    aov_name: bpy.props.StringProperty(
        name="AOV name", 
        description = "Name of the AOV in the shading network to bake", 
        default = "", 
        )

    aov_data_type_items = [
        ("COLOR", "Color", "Bake aov color value", 0),
        ("VALUE ", "Value", "Bake aov color value", 1),
    ]


    aov_data_type: bpy.props.EnumProperty(
        name="AOV data type", 
        description = "Bake AOV color or value", 
        default = "COLOR", 
        items = aov_data_type_items
        )

    # Pointiness
    pointiness_contrast: bpy.props.FloatProperty(
        name="Pointiness contrast", 
        description = "Amount of contrast to use on the pointiness", 
        default = 20, 
        )


    

    preview_bake_texture: bpy.props.BoolProperty(
        name = "Preview bake texture", 
        default = 0)



def is_non_default_bake_pass(bake_pass_type):
    bake_pass_type = bake_pass_type.upper()
    list = [
        'METALLIC',
        'BASE COLOR',
        'DISPLACEMENT',
        'ALPHA',
        'AOV',
        'POINTINESS',
        'MATERIAL_ID',
    ]
    return bake_pass_type in list

def is_low_sample_pass(bake_pass):
    bake_pass_type = bake_pass.bake_type.upper()
    list = [
        'GLOSSY', 'DIFFUSE', 'EMIT', 'ROUGHNESS', 'UV', 'NORMAL',
        'METALLIC', 'BASE COLOR', 'DISPLACEMENT', 'ALPHA',
        'AOV', 'POINTINESS', 'MATERIAL_ID'
    ]
    return bake_pass_type in list   

def is_temporary_scene_bake_pass(bake_pass):

    bake_pass_type = bake_pass.bake_type.upper()
    list = [
        'GLOSSY', 'DIFFUSE', 'EMIT', 'ROUGHNESS', 'UV', 'NORMAL',
        'METALLIC', 'BASE COLOR', 'DISPLACEMENT', 'AO', 'SHADOW',
        'ALPHA', 'AOV', "POINTINESS", 'MATERIAL_ID'
    ]
    return bake_pass_type in list       

def add_bakepass(context, BakeType):
    new_bake_pass = context.scene.bake_passes.add()
    new_bake_pass.name = "Base Color"

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
    elif bake_type == "EMIT" or bake_type == "AOV":
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