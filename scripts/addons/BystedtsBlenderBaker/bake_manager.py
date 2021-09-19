
import bpy
import os
import functools
import time
import copy
from . import object_manager
from . import high_res_objects_manager
from . import settings_manager
from . import bake_passes
from . import scene_manager
from . import bake_manager
from . import composit_manager
from . import UI
from . import collection_manager
from . import mesh_manager
from . import debug
from . import material_manager
from . import string_manager


def clear_images(context):
    '''
    Clear all images related to selected objects
    '''
    images_to_clear = get_related_bake_images(context.selected_objects)
   
    for image in images_to_clear:
        base_color = bake_passes.get_base_color(bake_passes.get_pass_from_string(image.name))

        # create array with pixels
        new_pixels = []
        for i in range(0, image.size[0] * image.size[1]):
            for j in range(len(base_color)):
                new_pixels.append(base_color[j])

        image.pixels = new_pixels

def delete_bake_images(context, delete_scope = ""):
    '''
    Deletes bake images
    :param delete_scope: The scope of images to delete
        ALL = delete all images that are of type bake_image
        SELECTED = delete all bake_images that are related to the selected objects
    :type delete_scope: string

    '''
    images_to_delete = []
    if delete_scope == "SELECTED":
        images_to_delete = get_related_bake_images(context.selected_objects)
    else:
        for image in bpy.data.images:
            try:
                if image['bake_image'] == True:
                    images_to_delete.append(image)
            except:
                pass
                
    # os needs absolute path when deleting file

    for image in images_to_delete:
        absolute_path = bpy.path.abspath(image.filepath)
        absolute_path = bpy.path.native_pathsep(absolute_path)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
        bpy.data.images.remove(image)

    refresh_file_browser(context)

def refresh_file_browser(context):
    # Refresh file browser
    '''
    # Disabled due to crash
    orig_area = context.area.type
    context.area.type = 'FILE_BROWSER'
    #bpy.ops.file.refresh() # Refresh causes crash. Strange 
    context.area.type = orig_area
    '''
    pass

        
def get_related_bake_images(objects):
    '''
    Returns a list with images related to objects. 
    '''
    return_images = []
    for object in objects:
        image_folder = get_first_bake_collection_name_from_object(context, object)
        image_search_string = get_bake_image_name(context, object)

        for image in bpy.data.images:
            if image in return_images:
                continue
            if image.name.find(image_search_string) > - 1:
                return_images.append(image)

    return return_images

def create_material_if_missing(context, object):
    '''
    Create material if there is no material assigned to object
    '''
    material = object.active_material
    if material is None:
        # Create material
        material = bpy.data.materials.new(name="Material")
        if object.data.materials:
            # Assign to 1st material slot
            object.data.materials[0] = material
        else:
            # No slots
           object.data.materials.append(material)

        material.use_nodes = True
        
        
def create_bake_image_if_missing(context, image_name, bake_render_settings, force_new_image = False):  
    '''
    Check if an image with name [image_name] exists.
    If it does not exist - create it
    bake_render_settings = A dictionary that contains render settings and render related data
    image_folder = the subfolder that the image will be saved in
    '''
    import platform
    
    image_folder = bake_render_settings['image_folder']

    bake_image = None

    
    image_resolution_x = bake_render_settings['resolution_x'] * int(bake_render_settings['sub_pixel_sample'])
    image_resolution_y = bake_render_settings['resolution_y'] * int(bake_render_settings['sub_pixel_sample'])
    
    # Check images if bake image already exists
    for image in bpy.data.images:
        if image.name == image_name:

            # Need extra checks when bake type is AOV
            if (bake_render_settings['bake_pass'].bake_type == "AOV" 
                and not bake_render_settings['bake_pass'].aov_name == image.get('aov_name')):
                continue

            if not image.generated_height == image_resolution_y or not image.generated_width == image_resolution_x:
                resize_image_to_resolution(context, image, bake_render_settings, post_bake = True)
            if not image.colorspace_settings.name == bake_render_settings['color_space']:
                image.colorspace_settings.name = bake_render_settings['color_space']
            
            bake_image = image

    # Create bake image if none is found
    if bake_image == None:
        bpy.ops.image.new(name=image_name, width=image_resolution_x, height=image_resolution_y, color = bake_render_settings['base_color'])
        bake_image = bpy.data.images[image_name]

    bpy.data.images[image_name]['bake_image'] = True # Add attribute to  mark the image as bake image
    bpy.data.images[image_name].colorspace_settings.name = bake_render_settings['color_space']
    bpy.data.images[image_name]['bake_type'] = bake_render_settings['bake_type']
    bpy.data.images[image_name]['normal_space'] = bake_render_settings['bake_pass'].normal_space
    bpy.data.images[image_name]['bit_depth'] = bake_render_settings['bit_depth']
    bpy.data.images[image_name]['image_folder'] = image_folder
    bpy.data.images[image_name]['aov_name'] = bake_render_settings['bake_pass'].aov_name

    return bake_image




def resize_image_to_resolution(context, image, bake_render_settings, post_bake = False):
    '''
    resize image to correct resolution in case sub pixel sampling has been used
    '''

    # Get correct resolution for image. Sub pixel samples is taken into consideration
    # if post_bake = False.
    if post_bake == False:
        resolution_x = bake_render_settings['resolution_x'] * bake_render_settings['sub_pixel_sample']
        resolution_y = bake_render_settings['resolution_y'] * bake_render_settings['sub_pixel_sample']
    
    elif post_bake == True:
        resolution_x = bake_render_settings['resolution_x']
        resolution_y = bake_render_settings['resolution_y']

    # If image already has correct resolution - return
    if (image.generated_height == resolution_y and 
        image.generated_width == resolution_x):
        return

    # For some reason context.area is None when the original operator is modal(?).
    # Therefore I need to create an override to use with area specific operators like image resize etc
    override = context.copy()
    override['area'] = context.screen.areas[0] # perhaps use area parameter?

    # Store original context mode/type
    original_ui_type = override['area'].ui_type

    # Change to image viewer
    override['area'].ui_type = 'IMAGE_EDITOR'

    # Load image in viewer
    override['area'].spaces.active.image = image

    # Do resize
    bpy.ops.image.resize(override, size=(resolution_x, resolution_y))

    # Restore window context
    override['area'].ui_type = original_ui_type

def add_bake_image_to_materials(context, image_name, object):
    '''
    Add image node to active objects material and assign [image_name] 
    to that image node
    '''

    for material_slot in object.material_slots:    
        if material_slot.material == None:
            continue

        material = material_slot.material
        node_tree = material.node_tree
        image_node = node_tree.nodes.new(type='ShaderNodeTexImage')
        image_node.name = image_name

        # Set image to image node and select, make active
        image_node.image = bpy.data.images[image_name]
        image_node.select = True
        node_tree.nodes.active = image_node
        image_node['is_bake_node'] = True

def cleanup_bake_image_nodes_from_objects_materials(context, objects, image = None):
    '''
    Removes image nodes in objects materials where image_node['is_bake_node'] = True
    If image is not None, then remove nodes that uses that image
    '''
    
    for object in objects:
        for material_slot in object.material_slots:    
            if material_slot.material == None:
                continue

            material = material_slot.material
            node_tree = material.node_tree
            for node in node_tree.nodes:
                if node.get('is_bake_node') == True:
                    node_tree.nodes.remove(node)
                elif not image == None:
                    if not node.type == 'TEX_IMAGE':
                        continue
                    if node.image == image:
                        node_tree.nodes.remove(node)


def get_bake_image_name(context, object, bake_pass = None):
    '''
    Returns the name of the image that should be baked.
    Convenient way of getting the correct image name format.
    The rules for naming are collected from the UI
    '''

    collection_name = get_first_bake_collection_name_from_object(context, object)
    separator = context.scene.BBB_props.bake_image_separator

    naming_option = context.scene.BBB_props.bake_image_naming_option


    if (bake_pass.bake_type == "CHANNEL_TRANSFER" and 
        bake_pass.image_name_override == True):
        name = bake_pass.name
        type = bake_pass.name

    # Avoid using same name when there are multiple AOV bake passes
    elif bake_pass.bake_type == "AOV":
  
        # Name
        if not bake_pass.name == "AOV":
            name = bake_pass.name
        else:
            name = bake_pass.bake_type + separator + bake_pass.aov_name

        # Type
        if not bake_pass.name == "AOV":
            type = bake_pass.bake_type + separator + bake_pass.name
        else:
            type = bake_pass.bake_type + separator + bake_pass.aov_name
    
    elif not bake_pass == None:
        name = bake_pass.name
        type = bake_pass.bake_type
    
    else:
        name = ""
        type = ""


    if naming_option == "TYPE_COLLECTION":
        bake_image_name = type + separator + collection_name
    elif naming_option == "NAME_COLLECTION":
        bake_image_name = name + separator + collection_name
    elif naming_option == "COLLECTION_TYPE":
        bake_image_name = collection_name + separator + type
    elif naming_option == "COLLECTION_NAME":
        bake_image_name = collection_name + separator + name

    return bake_image_name

def get_bake_image_folder_name(context, object):
    '''
    Returns the intended name of the folder that the bake image will
    be written to
    '''
    naming_option = context.scene.BBB_props.bake_image_naming_option

    if naming_option.find("COLLECTION") > - 1:
        image_folder_name = get_first_bake_collection_name_from_object(context, object)
    elif naming_option.find("OBJECT") > - 1:
        image_folder_name = object.name

    return image_folder_name
 
def debug_change_area(context, area = None):
    print("init debug_change_area")

    print("Original area.ui_type = " + area.ui_type)
    #context.area = area
    area.ui_type = 'IMAGE_EDITOR'
    #bpy.context.area.ui_type = 'IMAGE_EDITOR'
    
    debug_end_bake_process(context)

def bake_specific_pass(context, objects = None, bake_collections = None, image_folder = '', bake_passes = None, area = None):
    '''
    New baking function
    I need to give user feedback after each baked pass and not have a locked UI to 
    display messages to the user. 
    In order to do that I run that calling operator in modal and 
    show info window in this function. This also means that the current 
    "iteration" integer of bake passes and bake collections needs to be stored 
    in the window manager

    since bake_specific_pass is used via a modal operator, 
    I need to pass on the area as a parameter. Otherwise context.area is None. 
    I don't really know why this is the case
    '''
    

    wm = context.window_manager
    start_time = time.time()

    # End process when all bake collections are baked. 
    # There are also a lot of these checks at the end of this function
    #TODO:
    # There should actually be enough with check_if_progress_should_end at the 
    # bottom, but it isn't enough and I havent' had time to debug
    if wm['current_bake_collection'] >= wm['bake_collections_count']:
        wm['end_process'] = True
        return None


    bake_pass_index = wm['current_bake_pass']
    bake_pass = bake_passes[bake_pass_index]

    bake_collection_index = wm['current_bake_collection']
    bake_collection = bake_collections[wm['current_bake_collection']]

    # Return if bake collection contains no objects     
    if len(bake_collection.objects) == 0:
        timer_value_for_process = check_if_progress_should_end(context, bake_collections)
        return timer_value_for_process        

    # When baking selected objects, it is possible that the objects
    # does not belong to the same bake collection. Therefore objects
    # must be filtered per bake collection 
    objects = collection_manager.filter_objects_by_bake_collections(context, objects, [bake_collection])

    
    # CHANNEL TRANSFER or BAKING
    if bake_pass.bake_type == 'CHANNEL_TRANSFER':
        # Channel transfer
        bake_result = do_channel_transfer(
            context = context, 
            objects = objects, 
            image_folder = "", 
            bake_pass = bake_pass, 
            bake_collection = bake_collection,             
            )   
    else:
        # Do baking here
        bake_result = bake_texture(
            context = context, 
            objects = objects, 
            image_folder = "", 
            bake_pass = bake_pass, 
            bake_collection = bake_collection, 
            )

    handle_message_to_user(context, start_time, bake_collections, bake_passes, bake_result)

    timer_value_for_process = check_if_progress_should_end(context, bake_collections)

    
    return timer_value_for_process



def debug_end_bake_process(context):
    # Debug procedure for ending bake process
    wm = context.window_manager
    wm['end_process'] = True
    return None

def get_per_bake_pass_bake_report(start_time, bake_pass, bake_collection = None, bake_result = 'FINISHED'):
    
    info = "" 
    
    if not bake_collection == None:
        info = bake_collection.name + ", "
    
    if not bake_result == 'FINISHED':
        info += bake_result
        return info
    
    info = info + bake_pass.bake_type + ",  -   Baked at " + time.asctime()

    bake_total_seconds = time.time() - start_time
    bake_minutes = int(bake_total_seconds / 60)
    bake_seconds = int(bake_total_seconds - (bake_minutes * 60))

    info += "  -  Total bake time:  "
    info += str(bake_minutes) + " min, " + str(bake_seconds) + " seconds." 
    
    return info

def initialize_bake_report(context, objects = None, bake_passes = None, bake_collections = None):
    wm = context.window_manager
    
    bake_report = []

    if not bake_collections == None:
        for bake_collection in bake_collections:
            for bake_pass in bake_passes:
                bake_report.append(bake_collection.name + ", " + bake_pass.bake_type + ": Not started")
    else:
        for bake_pass in bake_passes:
            bake_report.append(bake_pass.bake_type + ": Not started")

    wm['bake_report'] = bake_report

def handle_selected_objects_visibility(context, bake_render_settings):
    # Hide selected objects in render so that they don't block the joined object
    # which should be baked   
    if bake_render_settings['bake_scene'] == 'CURRENT':
        objects_hide_render_settings = object_manager.get_hide_render_settings(context.selected_objects)
        for object in context.selected_objects:
            object.hide_render = True 



def handle_bake_scene(context, bake_render_settings):
    # Handle bake scene
    
    if bake_render_settings['bake_scene'] == 'TEMPORARY':       
        bake_scene_name = 'bake scene'
        bake_render_settings['bake_scene_name'] = bake_scene_name
        orig_scene = context.scene
        bake_render_settings['orig_scene'] = orig_scene
        
        scene_manager.create_scene(context, bake_scene_name, delete_after_bake = True)
        #object_manager.link_objects_to_active_scene(context, bake_render_settings['hi_res_objs'])
        object_manager.link_objects_to_active_scene(context, [bake_render_settings['combined_bake_object']])

    if bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES':
    
        # Make list of missing bake objects from selected, 
        # link them to the scene if missing and select them
        #bake_render_settings['missing_bake_objects'] = high_res_objects_manager.get_high_res_objects_missing_in_scene(context, bake_render_settings['objects'])
        #object_manager.link_objects_to_active_scene(context, bake_render_settings['missing_bake_objects'])
        object_manager.link_objects_to_active_scene(context, bake_render_settings['joined_high_poly_objects'])
        
    return bake_render_settings


def post_baking_compositing(context, bake_render_settings):

    compositing_setup_list = []

    #TODO: I think this should be before MIX... test it.
    # Do compositing if necessary
    if bake_render_settings['post_process'] == 'DENOISE':
        compositing_setup_list.append('DENOISE')

    # Anti aliasing
    if bake_render_settings['BBB_props'].use_post_process_anti_aliasing:
        compositing_setup_list.append('ANTI_ALIASING')

    if bake_render_settings['bake_pass'].bake_type == 'POINTINESS':
        compositing_setup_list.append('POINTINESS')

    # Composit bake image with latest image related to this bake pass
    compositing_setup_list.append('MIX')



    composit_manager.create_compositing_tree(
        context, 
        bake_render_settings['objects'][0], 
        bake_render_settings['bake_image'], 
        bake_render_settings['bake_pass'],
        compositing_setup_list,
        bake_render_settings['current_bake_pass_image']
        )   

def delete_intermediate_bake_image(context, bake_render_settings):
    # Delete bake image from blender and also source file
    # delete bake image - important in order to get a new, clean
    # bake image with 0 alpha at each bake
    absolute_path = bpy.path.abspath(bake_render_settings['bake_image'].filepath)
    if os.path.exists(absolute_path):
        os.remove(absolute_path)
    bpy.data.images.remove(bake_render_settings['bake_image'])

def handle_shading_for_non_default_bake_pass(context, bake_render_settings):
    '''
    When baking non default bake pass like "Base color" or "Metallic"
    the shading needs to be set up properly
    '''
    # Manage high res objects
    if bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES':
        # Set up shading if bake type is not a default bake type
        if bake_passes.is_non_default_bake_pass(bake_render_settings['bake_type']):
            set_up_shading_channel_for_baking_by_objects(
                context, 
                bake_render_settings['hi_res_objs'], 
                bake_render_settings)
    
    elif bake_render_settings['bake_workflow'] == 'LOWRES_ONLY':
        # Set up shading if bake type is not a default bake type
        if bake_passes.is_non_default_bake_pass(bake_render_settings['bake_type']):
            set_up_shading_channel_for_baking_by_objects(
                context, 
                [bake_render_settings['combined_bake_object']], 
                bake_render_settings)

def handle_visibility_and_selection_before_baking(context, combined_bake_object, high_res_objects, bake_render_settings):
    
    # Make sure the selection and render settings is correct before baking
    combined_bake_object.hide_render = False
    if bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES':
        object_manager.select_objects(context, 'REPLACE', high_res_objects, True)
        object_manager.select_objects(context, 'ADD', [combined_bake_object], True)
    else:
        object_manager.select_objects(context, 'REPLACE', [combined_bake_object], True)

    # Make sure objects are visible in render
    objects = [combined_bake_object] + high_res_objects
    for object in objects:
        object.hide_render = False


def post_baking_cleanup(context, bake_render_settings):
    '''
    Clean up objects, shading, scene etc after baking
    Restore original objects location
    '''
    
    delete_image_node(context, bake_render_settings['image_name_with_pass'])


    # Handle high res objects - cleanup
    if bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES':
        # Remove temporary high poly objects
        if debug.allow_cleanup()['objects']:
            object_manager.delete_objects(context, bake_render_settings['joined_high_poly_objects'])

        # Reset shading if bake type is not a default bake type
        if bake_passes.is_non_default_bake_pass(bake_render_settings['bake_type']):
            reset_shading_channel_to_original_shading_by_objects(bake_render_settings['hi_res_objs'])

    elif bake_render_settings['bake_workflow'] == 'LOWRES_ONLY':
        # Reset shading if bake type is not a default bake type
        if bake_passes.is_non_default_bake_pass(bake_render_settings['bake_type']):
            reset_shading_channel_to_original_shading_by_objects([bake_render_settings['combined_bake_object']]) 


    # Restore scene
    if bake_render_settings['bake_scene'] == 'TEMPORARY': 
        scene_manager.open_scene(context, bake_render_settings['orig_scene'].name)
        #scene_manager.delete_scene(context, bake_render_settings['bake_scene_name'])
        

    # Restore the high res objects original locations
    if bake_render_settings['bake_locations'] == "EXPLODED":   
        object_manager.reset_objects_original_locations(bake_render_settings['hi_res_objs'])  
        modifier_objects = object_manager.get_objects_connected_to_modifier_that_affects_object_bounding_box(bake_render_settings['hi_res_objs'])
        object_manager.reset_objects_original_locations(modifier_objects)

    cleanup_bake_image_nodes_from_objects_materials(context, [bake_render_settings['combined_bake_object']])
    
    # Delete the combined_bake_object and joined_high_poly_objects
    if debug.allow_cleanup()['objects']:
        object_manager.delete_objects_and_data([bake_render_settings['combined_bake_object']])       
    
def fix_skew_normals(context, source_objects, target_objects):

    #print("skipped fix skew normals")
    #return
    if context.scene.BBB_props.skew_normals_method == 'NONE':
        return

    bevel_method = context.scene.BBB_props.skew_normals_method
    print("source objects:")
    print(repr(source_objects))
    print("target objects:")
    print(repr(target_objects))

    for index, object in enumerate(source_objects):
        print("source = " + object.name + ", target = " + source_objects[index].name)
        object_manager.set_up_modifers_for_skew_normals(
            context, 
            source_object = object, 
            target_object = target_objects[index], 
            bevel_method = bevel_method)


def get_additional_bake_render_settings(context, bake_render_settings, objects,  image_folder, bake_collection, bake_pass):
    
    # TODO: Perhaps I should merge this into get_bake_render_settings

    bake_render_settings['bake_pass'] = bake_pass
    bake_render_settings['objects'] = objects

    # Only work with objects that are possible to bake
    bake_render_settings['objects'] = object_manager.filter_objects_by_type(bake_render_settings['objects'], ['MESH', 'META', 'CURVE', 'FONT', 'SURFACE'])


    # Store scene collection visibility
    bake_render_settings['collection_visiblity_settings'] = collection_manager.get_collection_visibility_settings(context, )


    if image_folder == "":
        bake_render_settings['image_folder'] = bake_collection.name
  
    # Get data based on bounding box
    largest_bb_side = object_manager.get_largest_bounding_box_side(objects)
    bake_render_settings['object_location_spacing'] = largest_bb_side * 1.5
    context.scene.render.bake.max_ray_distance = largest_bb_side * 0.5

    # Get high res objects
    bake_render_settings['hi_res_objs'] = high_res_objects_manager.get_high_res_objects(context, objects)
    bake_render_settings['connected_high_res_object_count'] = len(bake_render_settings['hi_res_objs'])
    
    # Store hide_select state of both bake target objects and high res objects
    all_objects = bake_render_settings['objects'] + bake_render_settings['hi_res_objs']
    bake_render_settings['objs_hide_select_state'] = object_manager.get_object_hide_select_state(context, all_objects)
    
    # Store hide_viewport state of both bake target objects and high res object
    bake_render_settings['objs_hide_viewport_state'] = object_manager.get_object_hide_viewport_state(context, all_objects)

    
    bake_render_settings['image_name_with_pass'] = get_bake_image_name(context, objects[0], bake_pass)



    return bake_render_settings



def bake_texture(context, objects, image_folder = '', bake_pass = None, bake_collection = None):
    '''
    Set cycles bake settings based on UI settings
    Bakes a texture based on input parameters

    since this function is used via a modal operator, 
    I need to pass on the area as a parameter. Otherwise context.area is None. 
    I don't really know why this is the case
    TODO: check if the area parameter is really needed. I used an override
    solution later when textures needs to be resized.
    '''
    import copy
    from . import bake_passes as bake_passes_class
    joined_high_poly_objects = []
    

    # Get render settings for the bake_pass
    bake_render_settings = settings_manager.get_bake_render_settings(context, context.scene, bake_pass)
    bake_render_settings = get_additional_bake_render_settings(context, bake_render_settings, objects, image_folder, bake_collection, bake_pass)
    bake_render_settings['joined_high_poly_objects'] = [] # Empty list, when using lowres baking workflow

    
    # Filter objects with only bakable objects
    objects = bake_render_settings['objects']

    # If no high res objects are connected to the objects
    if (bake_render_settings.get('connected_high_res_object_count') == 0 
        and context.scene.BBB_props.bake_workflow == 'HIGHRES_TO_LOWRES'):
        return "No high res object(s) connected to objects or is excluded in view layer"
    else:

        pass

    # Store lowres and highres objects original hide render settings 
    lowres_and_highres_objects = objects + bake_render_settings['hi_res_objs']
    objects_hide_render_settings = object_manager.get_objects_hide_render_settings(context, lowres_and_highres_objects)

    # Make sure bake collection is visible (and thereby bakeable)
    collection_visibility_settings = collection_manager.ensure_visibility_for_baking(context, bake_collection)

    # Make sure high res collections are visible (and thereby bakeable)
    if context.scene.BBB_props.bake_workflow == 'HIGHRES_TO_LOWRES':
        high_res_objects_manager.ensure_render_visiblity_on_high_res_collections(context, objects)

    # Make sure high res and bake target objects can be selected during baking process
    object_manager.set_object_hide_select_state(context, bake_render_settings, False)

    # Make sure high res and bake target objects are visible in viewport during the baking process
    object_manager.set_object_hide_viewport_state(context, bake_render_settings, False)

    # Duplicate bake target objects so I won't have to mess around with their locations
    object_manager.select_objects(context, 'REPLACE', objects, True)
    orig_objects = objects
    bpy.ops.object.duplicate()

    # Hide the original objects during render and set duplicated 
    # objects as bake target objects, since we will join them for faster bake speed
    for object in objects:
        object.hide_render = True
    objects = context.selected_objects

    # Duplicate high res objects and apply their modifiers before explosion
    # This fixes issues with shrinkwrap (etc) to other objects during explosion 
    if bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES':
        bake_render_settings['joined_high_poly_objects'] = (
            object_manager.duplicate_objects_and_apply_modifiers(
            context, 
            bake_render_settings['hi_res_objs'])
        )
    
    # Handle object positions (explosion)
    object_manager.explode_locations_of_objects_and_highres_objects(
        context, 
        objects, 
        bake_render_settings['bake_locations'], 
        bake_render_settings['object_location_spacing'])
    

    # Set joined_high_poly_objects to have same location as hi_res_objects
    if bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES':
        object_manager.copy_location_from_custom_property_object(
            context, 
            bake_render_settings['joined_high_poly_objects'],
            custom_property = "orig_object"
            )

    # Handle modifiers if using fix for skewed normals
    if bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES':
        fix_skew_normals(context, orig_objects, objects)

    # Join objects to a combined bake object (bake target)
    combined_bake_object = object_manager.join_objects_for_baking(context, objects)
    bake_render_settings['combined_bake_object'] = combined_bake_object

    # List high res objects by poly count. We will avoid joining extremely high
    # res objects to avoid long processing time
    if bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES':
        listed_high_res_objects = object_manager.list_objects_by_poly_count_limit(
            context, 
            objects = bake_render_settings['joined_high_poly_objects'], 
            poly_count_limit = 100000)

    # Join high res objects under vertex count limit to new object 
    if (bake_render_settings['bake_workflow'] == 'HIGHRES_TO_LOWRES' and
        bake_render_settings['BBB_props'].allow_high_poly_objects_to_join):
        print("JOINED high res objects")
        joined_high_poly_objects = object_manager.join_high_poly_objects(
            context, 
            listed_high_res_objects['under_poly_count'])
        # bake_render_settings['joined_high_poly_objects'] is used later in post_baking_cleanup   
        bake_render_settings['joined_high_poly_objects'] = (
            joined_high_poly_objects + 
            listed_high_res_objects['over_poly_count'])
    else:
        print("did NOT join high res objects")


        
    create_material_if_missing(context, combined_bake_object)

    handle_selected_objects_visibility(context, bake_render_settings)

    bake_render_settings = handle_bake_scene(context, bake_render_settings)
    
    handle_shading_for_non_default_bake_pass(context, bake_render_settings)
    
    current_bake_pass_image = create_bake_image_if_missing(context, bake_render_settings['image_name_with_pass'], bake_render_settings, force_new_image = False)
    bake_image = create_bake_image_if_missing(context, "bake_image", bake_render_settings, force_new_image = True)
    bake_render_settings['current_bake_pass_image'] = current_bake_pass_image
    bake_render_settings['bake_image'] = bake_image
 
    add_bake_image_to_materials(context, bake_image.name, combined_bake_object)


    # Resize image if user has changed resolution since last bake 
    # or scale up if sub pixel sampling > 1 is used
    resize_image_to_resolution(context, bake_image, bake_render_settings, False)
 
    settings_manager.set_settings(context, bake_render_settings)

    handle_visibility_and_selection_before_baking(
        context, 
        combined_bake_object, 
        bake_render_settings['joined_high_poly_objects'], 
        bake_render_settings)


    # Do the baking ==============================
    try:
        bpy.ops.object.bake(type = bake_render_settings['cycles_bake_type'])
    except:
        print("Baking failed")
        pass

    #debug_end_bake_process(context)
    #return

    # Resize and save image
    resize_image_to_resolution(context, bake_image, bake_render_settings, True)

    post_baking_cleanup(context, bake_render_settings)

    post_baking_compositing(context, bake_render_settings)

    # Note that scenes are deleted in the modal operator
    # RENDER_OT_bake_with_bake_passes. Specifically the "finish" function.
    # This is to avoid crash when trying to delete scenes in a modal process with timer

    # Temp disabled during debug
    #delete_intermediate_bake_image(context, bake_render_settings)
        
    restore_visibility_and_render_settings(
        context,
        bake_render_settings,
        bake_collection,
        collection_visibility_settings,
        objects_hide_render_settings
    )

    return 'FINISHED'

def restore_visibility_and_render_settings(context, bake_render_settings, bake_collection, collection_visibility_settings, objects_hide_render_settings):
    
    # Restore bake collection visibility settings
    collection_manager.set_visibility(context, bake_collection, collection_visibility_settings)

    # Restore hide_render settings on objects
    settings_manager.set_settings(context, objects_hide_render_settings)
    
    # Restore collection visibility settings and other settings
    collection_manager.set_collection_visibility_settings(bake_render_settings['collection_visiblity_settings'])

    # Restore hide_select_state on high res objects
    object_manager.set_object_hide_select_state(context, bake_render_settings)

    # Restore hide_viewport_state on high res objects and bake target objects
    object_manager.set_object_hide_viewport_state(context, bake_render_settings)
    
def do_channel_transfer(context, objects, image_folder, bake_pass, bake_collection):
    '''
    Handle events when a bake_pass is of type
    'CHANNEL_TRANSFER'
    '''

    # Bake render settings
    bake_render_settings = settings_manager.get_bake_render_settings(
        context = context, 
        bake_settings_scene = context.scene, 
        bake_pass = bake_pass
        )   

    bake_render_settings = get_additional_bake_render_settings(
        context = context, 
        bake_render_settings = bake_render_settings, 
        objects = objects, 
        image_folder = "", 
        bake_collection = bake_collection, 
        bake_pass = bake_pass
        )
    
    # Create bake image
    bake_image = create_bake_image_if_missing(context, "bake_image", bake_render_settings, force_new_image = True)
    bake_render_settings['bake_image'] = bake_image

    # Do compositing
    compositing_setup_list = ['CHANNEL_TRANSFER']

    composit_manager.create_compositing_tree(
        context = context, 
        object = bake_render_settings['objects'][0], 
        image = bake_render_settings['bake_image'], 
        bake_pass = bake_render_settings['bake_pass'],
        setup_type_list = compositing_setup_list,
        background_image = None,
        bake_collection = bake_collection
        )   
    
    cleanup_bake_image_nodes_from_objects_materials(context, objects = bake_render_settings['objects'], image = bake_image)
    
    return 'FINISHED'

def check_if_progress_should_end(context, bake_collections):
    '''
    Check if there is baking passes left to bake of the modal operator process. 
    Return value for the time evalue has a little "pause", which 
    makes it possible to redraw the UI during the baking process
    '''

    # Check if process should end
    wm = context.window_manager
    wm['current_bake_pass'] += 1
    # If all bake passes are baked
    if wm['current_bake_pass'] >= wm['bake_pass_count']:
        if bake_collections == None:
            wm['end_process'] = True
            return None
        wm['current_bake_collection'] += 1
        # If all bake collections are baked
        if wm['current_bake_collection'] >= wm['bake_collections_count']:
            wm['end_process'] = True
            return None
        else:
            wm['current_bake_pass'] = 0

    return 0.5 

def handle_message_to_user(context, start_time, bake_collections, bake_passes, bake_result):
    '''
    Display baking report and progress bar for the user
    '''
    wm = context.window_manager

    # Baking report
    bake_report = wm['bake_report']
    bake_collection_index = wm['current_bake_collection']
    bake_pass_index = wm['current_bake_pass']
    bake_pass = bake_passes[bake_pass_index]
    bake_progress_step = int(100 / (len(bake_collections) * len(bake_passes)))

    if bake_collections == None:
        info = get_per_bake_pass_bake_report(start_time, bake_pass, None, bake_result)
    else:
        info = get_per_bake_pass_bake_report(start_time, bake_pass, bake_collections[bake_collection_index], bake_result)

    bake_report_index = bake_pass_index + (bake_collection_index * wm['bake_pass_count'])
    bake_report_index = min(bake_report_index, len(bake_report)-1)
    bake_report[bake_report_index] = info
    
    wm['bake_report'] = bake_report

    # Progress bar
    context.scene.BBB_props.progress_percentage += bake_progress_step

    # Baking workflow text
    baking_workflow = context.scene.BBB_props.bake_workflow
    if baking_workflow == 'HIGHRES_TO_LOWRES':
        baking_workflow == "Baking highres objects to lowres objects"
    else:
        baking_workflow == "Baking lowres objects surface"

    # Show popup window
    UI.show_info_window(context, wm['bake_report'], "Baking report - " + baking_workflow)


def set_up_shading_channel_for_baking_by_objects(context, objects, bake_render_settings):
    '''
    There currently is no way of natively baking "metal" for instance.
    This procedure temporarily sets up the specified channel to an
    emission material and bakes it
    '''
    print('init set_up_shading_channel_for_baking_by_objects')
    channel_name = bake_render_settings['bake_pass'].bake_type

    for object in objects:
        for material_slot in object.material_slots:
            if not material_slot.material:
                continue
            if channel_name == 'DISPLACEMENT':
                set_up_displacement_for_baking_by_material(material_slot.material)   
            elif channel_name == 'AOV':
                set_up_aov_for_baking_by_material(
                    context, 
                    material_slot.material, 
                    bake_render_settings['bake_pass'])
            elif channel_name == 'POINTINESS':
                set_up_pointiness_for_baking_by_material(
                    context, 
                    material_slot.material, 
                    bake_render_settings['bake_pass'])       
            elif channel_name == 'MATERIAL_ID':
                set_up_material_id_for_baking_by_material(
                    context, 
                    material_slot.material, 
                    bake_render_settings['bake_pass'])   
            else:
                set_up_shading_channel_for_baking_by_material(context, material_slot.material, channel_name)    

def set_up_material_id_for_baking_by_material(context, material, bake_pass):
    
    print("init set_up_material_id_for_baking_by_material")

    # Get shader connected to material output
    material_output_node = material_manager.get_material_output_node(context, material)
    
    # Return if material node is already set up with having been reset
    if not material_output_node.get('original_surface_input') == None:
        return 

    shader_node = material_manager.get_shader_connected_to_material_output(
        context,
        material)
    
    if shader_node == None:
        return

    material_output_node['original_surface_input'] = shader_node.name

    # Create emission shader and connection to material output node
    emission_node = material_manager.connect_emission_to_material_output(context, material, material_output_node)
    emission_node['temp_PBR_channel_bake'] = True # Property used for deleting node later

    emission_node.inputs['Color'].default_value = string_manager.to_color(material.name)

def set_up_pointiness_for_baking_by_material(context, material, bake_pass):

    print("init set_up_pointiness_for_baking_by_material")

    # Get shader connected to material output
    material_output_node = material_manager.get_material_output_node(context, material)
    
    # Return if material node is already set up with having been reset
    if not material_output_node.get('original_surface_input') == None:
        return 

    shader_node = material_manager.get_shader_connected_to_material_output(
        context,
        material)
    
    if shader_node == None:
        return

    material_output_node['original_surface_input'] = shader_node.name

    # Create emission shader and connection to material output node
    emission_node = material_manager.connect_emission_to_material_output(context, material, material_output_node)
    emission_node['temp_PBR_channel_bake'] = True # Property used for deleting node later

    # Setup up shading for pointiness
    node_tree = material.node_tree
    geo_node = node_tree.nodes.new(type="ShaderNodeNewGeometry")
    geo_node['temp_PBR_channel_bake'] = True

    try:
        contrast_node = node_tree.nodes.new(type="ShaderNodeBrightContrast")
        contrast_node.inputs['Contrast'].default_value = bake_pass.pointiness_contrast
        contrast_node['temp_PBR_channel_bake'] = True

        node_tree.links.new(geo_node.outputs['Pointiness'], contrast_node.inputs['Color'])

        node_tree.links.new(contrast_node.outputs['Color'], emission_node.inputs['Color'])

        print("\n settting up pointiness in material " + material.name)
        print("Connecting " + repr(geo_node.outputs['Pointiness']) + " to " + repr(emission_node.inputs['Color']))
    except:
        pass

def set_up_aov_for_baking_by_material(context, material, bake_pass):
    '''
    Find the first AOV node in the material that matches the bake pass.
    Connect its input to an emission shader so it can be baked
    '''
    # Get shader connected to material output
    material_output_node = material_manager.get_material_output_node(context, material)
    
    # Return if material node is already set up with having been reset
    if not material_output_node.get('original_surface_input') == None:
        return 


    shader_node = material_manager.get_shader_connected_to_material_output(
        context,
        material)
    
    if shader_node == None:
        return

    material_output_node['original_surface_input'] = shader_node.name

    # Create emission shader and connection to material output node
    emission_node = material_manager.connect_emission_to_material_output(context, material, material_output_node)
    emission_node['temp_PBR_channel_bake'] = True # Property used for deleting node later
   
    # Get AOV node that matches bake pass data
    aov_nodes = material_manager.get_nodes_of_type(context, material, 'OUTPUT_AOV')

    # If no AOV nodes found
    if len(aov_nodes) == 0:
        emission_node.inputs['Color'].default_value = (0, 0, 0, 1)
        return

    for node in aov_nodes:
        if node.name == bake_pass.aov_name:
            aov_node = node
    
    # Get source socket from AOV nodes input
    if bake_pass.aov_data_type == 'COLOR':
        source_socket = aov_node.inputs['Color'].links[0].from_socket
    else:
        source_socket = aov_node.inputs['Value'].links[0].from_socket
    
    # Connect input to AOV in emission shader
    if not source_socket == None:
        material.node_tree.links.new(
            source_socket, 
            emission_node.inputs['Color'])
    else:
        print("could not find a connection to the AOV input " + bake_pass.aov_data_type)


def set_up_shading_channel_for_baking_by_material(context, material, channel_name):
    '''
    There currently is no way of natively baking "metal" for instance.
    This procedure temporarily sets up the specified channel to an
    emission material and bakes it
    '''

    # Make sure channel name has correct upper and lower case
    channel_name = channel_name.title()

    node_tree = material.node_tree

    # Get shader connected to material output
    material_output_node = material_manager.get_material_output_node(context, material)
    
    # Return if material node is already set up with having been reset
    if not material_output_node.get('original_surface_input') == None:
        return 


    shader_node = material_manager.get_shader_connected_to_material_output(
        context,
        material)
    
    if shader_node == None:
        return

    if not channel_name in shader_node.inputs:
        return

    material_output_node['original_surface_input'] = shader_node.name

    # Create emission shader and connection to material output node
    emission_node = material_manager.connect_emission_to_material_output(context, material, material_output_node)
    emission_node['temp_PBR_channel_bake'] = True # Property used for deleting node later

    # Does shader have node input connection to channel or is it just a set value in the shader?
    if len(shader_node.inputs[channel_name].links) > 0:
        # Get the correct socket that should be connected to the temporary emission shader
        channel_link_socket = shader_node.inputs[channel_name].links[0].from_socket  
    else:
        if shader_node.inputs[channel_name].type == 'VALUE':
            value_node = node_tree.nodes.new(type="ShaderNodeValue")           
            value_node.outputs['Value'].default_value = shader_node.inputs[channel_name].default_value
            channel_link_socket = value_node.outputs['Value']
        elif shader_node.inputs[channel_name].type == 'RGBA' or shader_node.inputs[channel_name].type == 'VECTOR': 
            value_node = node_tree.nodes.new(type="ShaderNodeRGB")
            value_node.outputs['Color'].default_value = shader_node.inputs[channel_name].default_value
            channel_link_socket = value_node.outputs['Color']
        
        value_node['temp_PBR_channel_bake'] = True # Property used for deleting node later

    # Make connection to the temporary emission shader, so the data can be baked
    node_tree.links.new(channel_link_socket, emission_node.inputs['Color'])

def set_up_displacement_for_baking_by_material(material):
    '''
    Sets up what is plugged into the material displacement and sets
    it up as an emission shader for baking 
    '''

    node_tree = material.node_tree
    material_output_node = None
    # Find material output node that is used for shading
    for node in node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL' and node.is_active_output:
            material_output_node = node
            
    # Return if material node is already set up with having been reset
    if not material_output_node.get('original_surface_input') == None:
        return 

    shader_node = material_output_node.inputs['Surface'].links[0].from_node
    material_output_node['original_surface_input'] = shader_node.name

    # Find input to displacement node that is connected to material output node
    try:
        disp_node = material_output_node.inputs['Displacement'].links[0].from_node
    except:
        # No displacement node connected to material output displacement
        disp_node = None
    
    if not disp_node == None:
        try:
            if disp_node.type == 'DISPLACEMENT':
                disp_value_node = disp_node.inputs['Height'].links[0].from_node
                channel_link_socket = disp_node.inputs['Height'].links[0].from_socket
            elif disp_node.type == 'VECTOR_DISPLACEMENT':
                disp_value_node = disp_node.inputs['Vector'].links[0].from_node
                channel_link_socket = disp_node.inputs['Vector'].links[0].from_socket
            else:
                disp_value_node = disp_node
                channel_link_socket = material_output_node.inputs['Displacement'].links[0].from_socket
        except:
            # No displacement value node found
            disp_value_node = None
            print("\nNo disp value node found")

   
    # Create emission shader and connection to material output node
    emission_node = node_tree.nodes.new(type="ShaderNodeEmission")
    emission_node['temp_PBR_channel_bake'] = True # Property used for deleting node later
    node_tree.links.new(emission_node.outputs['Emission'], material_output_node.inputs['Surface'])

    # Set up displacement input with emission shader

    # If disp value node NOT found (i.e. only using flat value)
    if not disp_value_node:
        if disp_node:
            disp_value = disp_node.inputs['Height'].default_value
        else:
            disp_value = 0
        
        # Set up a value node that will be connected to the emission shader
        value_node = node_tree.nodes.new(type="ShaderNodeValue")   
        value_node.outputs['Value'].default_value = disp_value
        channel_link_socket = value_node.outputs['Value']

    # Make connection to the temporary emission shader, so the data can be baked
    node_tree.links.new(channel_link_socket, emission_node.inputs['Color'])    


def reset_shading_channel_to_original_shading_by_objects(objects):
    '''
    Resets the setup done in set_up_shading_channel_for_baking_by_material
    to the original shading setup
    '''   
    for object in objects:
        for material_slot in object.material_slots:
            if not material_slot.material:
                continue
            reset_shading_channel_to_original_shading_by_material(material_slot.material)    

def reset_shading_channel_to_original_shading_by_material(material):
    '''
    Resets the setup done in set_up_shading_channel_for_baking_by_material
    to the original shading setup
    '''   
    # Find the material output node
    material_output_node = None
    for node in material.node_tree.nodes:
        if not node.type == 'OUTPUT_MATERIAL':
            continue
        if node.get('original_surface_input') == None:
            continue
        orig_shader_node_name = node.get('original_surface_input')
        orig_shader_node = material.node_tree.nodes[orig_shader_node_name]
        material_output_node = node

        # Reconnect original shader to material output
        material.node_tree.links.new(orig_shader_node.outputs[0], material_output_node.inputs['Surface'])

        # Delete temporary property on material output node
        del material_output_node['original_surface_input']
    
    
    # Delete all nodes that contain the property 'temp_PBR_channel_bake'
    for node in material.node_tree.nodes:
        if node.get('temp_PBR_channel_bake') == None:
            continue
        material.node_tree.nodes.remove(node)


def turn_off_build_modifiers(object):
    '''
    Turns off rendering for build modifiers on object \n
    This is to avoid overwriting baked pixels because of \
    overlapping uv's 
    Returns list of modifiers that was turned off
    '''
    modifier_list = []
    modifier_settings = {}
    for mod in object.modifiers:
        if modifier_is_build_modifier(mod) and mod.show_render == True:
            mod.show_render = False
            mod.show_viewport = False
            modifier_list.append(mod)
            modifier_settings[repr(mod) + ".show_viewport"] = mod.show_viewport
            modifier_settings[repr(mod) + ".show_render"] = mod.show_render

    return modifier_settings

def modifier_is_build_modifier(modifier):
    '''
    Returns true if modifier is  modifier that can result in
    overlapping uv's
    '''
    build_modifiers = [
        'ARRAY',
        'BOOLEAN',
        'MIRROR',
        'REMESH',
        'SCREW',
        'SKIN',
        'SOLIDIFY',
        'WIREFRAME'
    ]
    if modifier.type in build_modifiers:
        return True

def get_first_bake_collection_name_from_object(context, object):
    '''
    Returning the name of the first collection in the scene that the 
    object belongs to that is a bake collection. 
    '''

    collections = collection_manager.get_bake_collections_by_object(context, object)
    collection_name = collections[0].name

    return collection_name



    

def save_image(context, image_name, file_path, sub_folder = None, bit_depth = None, file_name = None):
    '''
    saves image to disk
    '''
    # TODO: file_path is not used in this function. Delete it 
    # and remove it from all calls to this function

    # TODO: I'd prefer if image_name was reffering to the image instead 
    # of it's name. FIx this later in this function and all calls to this
    # function

    # good info here
    # https://blender.stackexchange.com/questions/27317/saving-a-16-bit-png-using-script
    
   
    if file_name == None:
        file_name = image_name
    if bit_depth == None:
        bit_depth = bpy.data.images[image_name]['bit_depth']
    if sub_folder == None:
        sub_folder = bpy.data.images[image_name]['image_folder']

    original_settings = settings_manager.get_current_render_settings(context)

    context.area.type = 'IMAGE_EDITOR'
    context.area.spaces.active.image = bpy.data.images[image_name]

    file_format = context.scene.BBB_props.image_format
    
    if not sub_folder == "": 
        sub_folder = sub_folder + "\\"
    
    full_save_path = bpy.path.abspath(context.scene.BBB_props.dir_path)

    full_save_path += sub_folder + file_name + "." + file_format  

    context.scene.render.image_settings.color_depth = bit_depth
    context.scene.render.image_settings.file_format = file_format


    try:
        bpy.ops.image.save_as(filepath = full_save_path, save_as_render = True)
        print("Saved image to " + full_save_path)
    except:
        pass
        print("Could not save image " + image_name)

    # Add custom attributes to image
    bpy.data.images[image_name]['bake_image'] = True
    bpy.data.images[image_name]['file path'] = full_save_path

    # Restore original settings
    settings_manager.set_settings(context, original_settings)


def remove_modifiers_for_bake(context):
    # Remove modifiers that are not optimal for baking (array, solidify etc)
    for mod in context.active_object.modifiers:
        if(mod.type == 'ARRAY' or
            mod.type == 'BEVEL' or
            mod.type == 'BUILD' or
            mod.type == 'MASK' or
            mod.type == 'MIRROR' or
            mod.type == 'REMESH' or
            mod.type == 'SCREW' or
            mod.type == 'SKIN' or
            mod.type == 'SOLIDIFY' or
            mod.type == 'WELD' or
            mod.type == 'WIREFRAME'
            ):
            bpy.ops.object.modifier_remove(modifier=mod.name)

def delete_image_node(context, image_name):
    for material_slot in context.active_object.material_slots:
        if material_slot.material == None:
            continue

        material = material_slot.material
        node_tree = material.node_tree

        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                if node.name.startswith(image_name):
                    material.node_tree.nodes.remove(node)

def delete_image(context, image_name):
    for image in bpy.data.images:
        if image.name == image_name:
            bpy.data.images.remove(image)
            pass

def get_bake_image_count(context):
    '''
    Return the number of bake images in the blender file
    '''
    count = 0
    for image in bpy.data.images:
        if image.get('bake_image'):
            count += 1

    return count

def get_bake_images_names(context):
    '''
    Return the names of all bake images
    '''
    bake_image_names = []
    for image in bpy.data.images:
        if image.get('bake_image'):
            bake_image_names.append(image.name)

    return bake_image_names    

def get_extrusion_estimation(context, bake_targets):
    '''
    Estimate bake extrusion by comparing the bounding boxes of \n
    bake target and bake sources
    Bake sources are collected from stored bakeSet object property on bake_targets
    '''
    # IN PROGRESS
    high_ress = high_res_objects_manager.get_high_res_objects(context, bake_targets)
    targets_bb = get_bounding_box_out_bounds(context, bake_targets)
    sources_bb = get_bounding_box_out_bounds(context, high_ress)
    extrusion = 0
    for key in targets_bb:
        difference = abs(targets_bb[key] - sources_bb[key])
        if difference > extrusion:
            extrusion = difference
    
    return extrusion + 0.4 # Slight offset to extrusion just in case

def get_bounding_box_out_bounds(context, object_list):
    '''
    Returns one bounding box of all objects in object_list
    returns dictionary with bounding box max, min. Keys = 'x_max', 'x_min' etc
    '''
    bounding_box = {
        'x_min': 0,
        'x_max': 0,
        'y_min': 0,
        'y_max': 0,
        'z_min': 0,
        'z_max': 0  
    }
  
    for obj in object_list:
        for i in range(8):
            if obj.bound_box[i][0] < bounding_box['x_min']:
                bounding_box['x_min'] = obj.bound_box[i][0]
            if obj.bound_box[i][0] > bounding_box['x_max']:
                bounding_box['x_max'] = obj.bound_box[i][0]
            if obj.bound_box[i][1] < bounding_box['y_min']:
                bounding_box['y_min'] = obj.bound_box[i][0]
            if obj.bound_box[i][1] > bounding_box['y_max']:
                bounding_box['y_max'] = obj.bound_box[i][0]  
            if obj.bound_box[i][2] < bounding_box['z_min']:
                bounding_box['z_min'] = obj.bound_box[i][0]
            if obj.bound_box[i][2] > bounding_box['z_max']:
                bounding_box['z_max'] = obj.bound_box[i][0]

    return bounding_box

classes = (


)