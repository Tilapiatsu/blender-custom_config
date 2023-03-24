import bpy
import os
from . import scene_manager
from . import bake_manager
from . import settings_manager
from . import image_manager

# create scene
# open scene
# create compositing tree 
# save image
# reload target image
'''
'''
def my_save_handler(context):
    # This function is used to only save once the compositor is done rendering.
    if context.scene['save_image'] == True:
  
        # Store originial UI
        original_ui = context.area.ui_type
        context.area.ui_type = 'IMAGE_EDITOR'
        context.area.spaces.active.image = bpy.data.images['Viewer Node']
        
        # Get save data from scene
        image_name= context.scene['image_name']
        image_subfolder = context.scene['image_subfolder']
        image_bit_depth = context.scene['image_bit_depth']

        bake_manager.save_image(context, image_name, "tramspath", image_subfolder, image_bit_depth)
        # Restore original UI
        context.area.ui_type = original_ui

        context.scene['save_image'] = False

def initialize_compositing_scene(context, bake_render_settings):
    '''
    Initialize a compositing scene with correct settings
    '''
    # initialize new scene
    scene_manager.create_scene(context, "comp_scene", delete_after_bake = True)

    context.scene.view_settings.view_transform = 'Standard'
    context.scene.view_settings.look = 'None'
    
    # Use linear color space when working with Non-Color
    if bake_render_settings['color_space'] == 'Non-Color':
        context.scene.display_settings.display_device = 'None' # color space

    context.scene.render.resolution_x = bake_render_settings['resolution_x']
    context.scene.render.resolution_y = bake_render_settings['resolution_y']
    settings_manager.set_settings(context, bake_render_settings)

    print("before adding a cameera, mode is " + str(context.mode))
    context_override = {'scene': bpy.data.scenes['comp_scene']}
    bpy.ops.object.camera_add(context_override)

    # Assign camera as render camera
    for object in context.scene.objects:
        if object.type == 'CAMERA':
            context.scene.camera = object


    context.scene.use_nodes = True
    comp_scene = context.window.scene
    node_tree = context.scene.node_tree

    return comp_scene

def create_compositing_tree(context, object, image, bake_pass, setup_type_list, background_image = None, bake_collection = None):
    '''
    Create a compositing tree and process image
    setup_types = 'CHANNEL_TRANSFER', 'DENOISE', 'MIX', 'ANTI_ALIASING', 'NORMALIZE', 'POINTINESS'
    '''    
    original_scene = context.window.scene
    image_name = bake_manager.get_bake_image_name(context, object, bake_pass)
    image_folder_name = bake_manager.get_bake_image_folder_name(context, object)  
    file_name = image.name

    render_settings = settings_manager.get_bake_render_settings(context, context.scene, bake_pass)   
    
    comp_scene = initialize_compositing_scene(context, render_settings)
    node_tree = comp_scene.node_tree

    if not 'CHANNEL_TRANSFER' in setup_type_list:
        # Set up initial source image
        image_node = node_tree.nodes.new("CompositorNodeImage")
        image_node.image = image
        latest_node = image_node

        for setup_type in setup_type_list:
            if (setup_type == 'DENOISE'):
                latest_node = setup_denoise(context, latest_node, bake_pass)
            
            if (setup_type == 'ANTI_ALIASING'):
                latest_node = setup_anti_aliasing(context, latest_node, bake_pass)    

            if setup_type == 'MIX':
                bake_manager.resize_image_to_resolution(context, background_image, render_settings, post_bake = True)
                latest_node = setup_mix(context, latest_node, background_image, bake_pass)
                file_name = background_image.name

            if setup_type == 'NORMALIZE':
                latest_node = setup_normalize(context, latest_node, bake_pass)

        # Output compositior node
        compositor_node = setup_node(context, latest_node, "CompositorNodeComposite")

        render_and_save_image(context, render_settings, image_folder_name, file_name)

    # Channel transfer 
    if 'CHANNEL_TRANSFER' in setup_type_list:
                
        image.name = image_name
        latest_node = setup_channel_transfer(context, bake_pass, bake_collection)
            
        # Connect compositior node to channel transfer
        compositor_node = setup_node(context, latest_node, "CompositorNodeComposite")
        render_and_save_image(context, render_settings, image_folder_name, image_name)


    # Restore original scene - use scene name in order to not crash 
    # when the bake takes a long time (not joining high poly objects)
    try:
        context.window.scene = bpy.data.scenes[original_scene.name]
    except:
        pass
    
def render_and_save_image(context, render_settings, image_folder_name, file_name):


    # Do render
    bpy.ops.render.render()

    file_format = render_settings['file_extension']   # file format is set in set_settings
    full_save_path = bpy.path.abspath(context.scene.BBB_props.dir_path)
    full_save_path += image_folder_name + "\\" + file_name + "." + file_format  

    # Create the folder if it does not exist
    target_folder = bpy.path.abspath(context.scene.BBB_props.dir_path) + image_folder_name
    absolute_folder_path = bpy.path.abspath(target_folder)
    if not os.path.exists(absolute_folder_path):
        os.makedirs(absolute_folder_path)    


    # Convert path from backslash to frontslash 
    full_save_path = full_save_path.replace("\\", "/")
    try:
        bpy.data.images[file_name].filepath = full_save_path
    except:
        pass
    
    # Save image - important to have after convert path because of linux
    bpy.data.images["Render Result"].save_render(filepath = full_save_path)

    # Reload image
    bpy.data.images[file_name].source = 'FILE'
    bpy.data.images[file_name].reload()


def setup_node(context, input_node, new_node_bl_idname):
    node_tree = context.scene.node_tree
    node_1 = node_tree.nodes.new(new_node_bl_idname)    
    node_tree.links.new(input_node.outputs[0], node_1.inputs["Image"])
    return node_1


def setup_denoise(context, input_node, bake_pass = None):
    node_tree = context.scene.node_tree
    node_1 = node_tree.nodes.new("CompositorNodeDenoise")    

    node_tree.links.new(input_node.outputs["Image"], node_1.inputs["Image"])
    return node_1

def setup_anti_aliasing(context, input_node, bake_pass = None):
    node_tree = context.scene.node_tree
    node_1 = node_tree.nodes.new('CompositorNodeAntiAliasing')    

    node_tree.links.new(input_node.outputs["Image"], node_1.inputs["Image"])
    node_1.threshold = 0
    node_1.contrast_limit = 0.25
    node_1.corner_rounding = 0.25

    return node_1

def setup_normalize(context, input_node, bake_pass = None):
    

    node_tree = context.scene.node_tree
    node_1 = node_tree.nodes.new('CompositorNodeNormalize')
    
    node_tree.links.new(input_node.outputs["Image"], node_1.inputs["Value"])
    
    return node_1

def setup_contrast_for_pointiness(context, input_node, bake_pass = None):

    node_tree = context.scene.node_tree
    node_1 = node_tree.nodes.new('CompositorNodeBrightContrast')
    node_1.inputs['Contrast'].default_value = 90
    node_tree.links.new(input_node.outputs["Image"], node_1.inputs["Image"])
    
    return node_1

def setup_mix(context, input_node, mix_image, bake_pass = None):
    
    if bake_pass == None:
        base_color = (0.5,0.5,0.5,1)
    else:
        render_settings = settings_manager.get_bake_render_settings(context, None, bake_pass)
        base_color = render_settings['base_color']
        base_color[3] = 1.0

    node_tree = context.scene.node_tree

    image_node = node_tree.nodes.new('CompositorNodeImage')
    image_node.image = mix_image
    
    mix_node_1 = node_tree.nodes.new('CompositorNodeMixRGB')
    mix_node_1.use_alpha = True

    
    mix_node_2 = node_tree.nodes.new('CompositorNodeMixRGB')
    mix_node_2.use_alpha = False    

    # Make sure background is solid
    RGB_node = node_tree.nodes.new('CompositorNodeRGB')
    RGB_node.outputs[0].default_value = base_color

    # Connect nodes
    node_tree.links.new(image_node.outputs["Image"], mix_node_1.inputs[1])
    node_tree.links.new(input_node.outputs["Image"], mix_node_1.inputs[2])
    node_tree.links.new(RGB_node.outputs[0], mix_node_2.inputs[1])
    node_tree.links.new(mix_node_1.outputs["Image"], mix_node_2.inputs[2])

    return mix_node_2

def setup_channel_transfer(context, bake_pass, bake_collection):

    node_tree = context.scene.node_tree

    combine_RGBA_node = node_tree.nodes.new("CompositorNodeCombRGBA")

    # Get image RGB sources
    try:
        R_source_image = image_manager.get_image_by_bake_type(bake_pass.R_source, bake_collection)
        G_source_image = image_manager.get_image_by_bake_type(bake_pass.G_source, bake_collection)
        B_source_image = image_manager.get_image_by_bake_type(bake_pass.B_source, bake_collection)
        A_source_image = image_manager.get_image_by_bake_type(bake_pass.A_source, bake_collection)

    except:
        print("Could not find source image during setup_channel_transfer")
        return None


    # Connect R
    if not bake_pass.R_source == "" and not bake_pass.transfer_source_channelR == 'NONE':
        R_image_node = node_tree.nodes.new("CompositorNodeImage")
        R_image_node.image = R_source_image
        R_sep_RGBA_node = node_tree.nodes.new("CompositorNodeSepRGBA")
        node_tree.links.new(R_image_node.outputs["Image"], R_sep_RGBA_node.inputs["Image"])
        source_channel = bake_pass.transfer_source_channelR
        node_tree.links.new(R_sep_RGBA_node.outputs[source_channel], combine_RGBA_node.inputs["R"])

    # Connect G
    if not bake_pass.G_source == "" and not bake_pass.transfer_source_channelG == 'NONE':
        G_image_node = node_tree.nodes.new("CompositorNodeImage")
        G_image_node.image = G_source_image
        G_sep_RGBA_node = node_tree.nodes.new("CompositorNodeSepRGBA")
        node_tree.links.new(G_image_node.outputs["Image"], G_sep_RGBA_node.inputs["Image"])
        source_channel = bake_pass.transfer_source_channelG
        node_tree.links.new(G_sep_RGBA_node.outputs[source_channel], combine_RGBA_node.inputs["G"])

    # Connect B
    if not bake_pass.B_source == "" and not bake_pass.transfer_source_channelB == 'NONE':
        B_image_node = node_tree.nodes.new("CompositorNodeImage")
        B_image_node.image = B_source_image
        B_sep_RGBA_node = node_tree.nodes.new("CompositorNodeSepRGBA")
        node_tree.links.new(B_image_node.outputs["Image"], B_sep_RGBA_node.inputs["Image"])
        source_channel = bake_pass.transfer_source_channelB
        node_tree.links.new(B_sep_RGBA_node.outputs[source_channel], combine_RGBA_node.inputs["B"])

    # Connect Alpha
    if not bake_pass.A_source == "" and not bake_pass.transfer_source_channelA == 'NONE':
        A_image_node = node_tree.nodes.new("CompositorNodeImage")
        A_image_node.image = A_source_image
        A_sep_RGBA_node = node_tree.nodes.new("CompositorNodeSepRGBA")
        node_tree.links.new(A_image_node.outputs["Image"], A_sep_RGBA_node.inputs["Image"])
        source_channel = bake_pass.transfer_source_channelA
        node_tree.links.new(A_sep_RGBA_node.outputs[source_channel], combine_RGBA_node.inputs["A"])


    # Return latest node
    return combine_RGBA_node

def get_compositing_setup(type):
    
    nodes = []
    if type == "DENOISE":
        nodes.append({"node_type" : "CompositorNodeDenoise",  "filter_type" : ""})
    return nodes

def add_node(context, node_type, filter_type = None, image = None, link_to_active = True):
    active_node = context.scene.node_tree.nodes.active
    new_node = context.scene.node_tree.nodes.new(node_type)
    if filter_type:
        new_node.filter_type = filter_type
    if image:
        new_node.image = image
    if link_to_active:
        context.scene.node_tree.links.new(new_node.inputs[0], active_node.outputs[0])
   
    context.scene.node_tree.nodes.active = new_node
    return new_node

classes = (

)