import bpy
import mathutils
import copy
import numpy
from . import high_res_objects_manager
from . import bake_manager
from . import collection_manager
from . import mesh_manager
from . import bound_box_manager
from . import debug


def link_objects_to_active_scene(context, object_list):
    for object in object_list:
        try:
            context.collection.objects.link(object)
        except:
            print("Could not move " + object.name + "to temporary scene collection. Perhaps it's alredy added")

def delete_objects(context, object_list):
    '''
    Deletes objects in list and handles selection
    '''
    # TODO: Why in the world have I used selection when deleting?? Fix!
    orig_selection = context.selected_objects
    bpy.ops.object.select_all(action = 'DESELECT')

    for object in object_list:
        #object.select_set(True)   
        #bpy.ops.object.delete(use_global=False, confirm=False)
        bpy.data.objects.remove(object)
    
    for object in orig_selection:
        try:
            object.select_set(True)
        except:
            print("Could not select object. It does not seem to exist")

def get_hide_render_settings(objects):
    '''
    Return a dictionary with settings for hide_render of objects
    '''
    hide_render_settings = {}
    for object in objects:
        hide_render_settings['bpy.data.objects[\"' + object.name + '\"].hide_render'] = object.hide_render
    
    return hide_render_settings

def add_materials_to_objects_in_collection(context, collection):
    '''
    Adds a material to objects in the collection if they don't have a material
    '''   
    original_selection = context.selected_objects
    active_object = context.active_object

    objects = collection.objects
    
    for object in objects:
        has_material = False

        for slot in object.material_slots:
            if slot.material:
                has_material = True
                continue

        if has_material:
            continue

        # Create material
        select_objects(context, 'REPLACE', [object], set_first_as_active = True)
        
        if len(object.material_slots) == 0:
            bpy.ops.object.material_slot_add()

        material = bpy.data.materials.new(name="Material")
        material.use_nodes = True
        object.material_slots[0].material = material
        
    # Restore selection
    select_objects(context, 'REPLACE', original_selection, active_object = active_object)

def flag_objects_for_recalculate_normals(context, objects):
    '''
    If object has negative scale in any axis - flag for normal recalculate
    in a custom attribute
    '''
    for object in objects:
        for i in range(0,3):
            if object.scale[i] < 0:
                object['recalculate_normals'] = True
                continue

def select_objects(context, action, object_list, set_first_as_active = False, active_object = None):
    '''
    Selects objects. action can be 'ADD' or 'REPLACE'
    '''
    # Make sure object_list is a list, even if it is just one object
    my_list = []
    if not type(object_list) is list and not type(object_list) is tuple :
        my_list.append(object_list)
        object_list = my_list

    if action == 'REPLACE':
        bpy.ops.object.select_all(action = 'DESELECT')
        # Always set first as active. Otherwise an unselected, but
        # active object can be used in an operation
        set_first_as_active = True

    for obj in object_list:
        try:
            obj.select_set(state=True)
        except:
            if repr(obj).find("invalid") > -1 or obj == None:
                obj_name = "the object"
            else:
                obj_name = obj.name
            print("Could not select " + obj_name)

    if set_first_as_active:
        try:
            context.view_layer.objects.active = object_list[0]
        except:
            if len(object_list) == 0:
                print("Could not make the object active, since the object list is empty")
            else:
                print("Could not make " + object_list[0].name + " active.")

    if active_object:
        context.view_layer.objects.active = active_object

def deselect_objects(context, object_list):
    '''
    Deselects objects in object_list
    '''
    for object in object_list:
        object.select_set(False)  

def select_only_active_object(context):
    '''
    Select only the active object
    '''
    active_object = context.active_object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[active_object.name].select_set(state=True)
    context.view_layer.objects.active = active_object


def clear_location(objects):
    '''
    Clear location, rotation and scale of objects
    '''
    for object in objects:
        object.location = mathutils.Vector((0,0,0))
        object.rotation_euler = mathutils.Vector((0,0,0))
        object.scale = mathutils.Vector((1,1,1))
        



def get_location_list(objects):
    
    '''
    returns a list with vectors that represent the location, rotation or scale of each object in objects
    '''
    # TODO - clean this up once it's working
    import copy
    location_list = []
    for object in objects:
        location_list.append([[copy.copy(object.location)], [copy.copy(object.rotation_euler)], [copy.copy(object.scale)]])

    return location_list.copy() # Return a copy of the list



def set_location_by_list(objects, location_list):
    '''
    set position of objects based on list. \n 
    If number of objects are larger than positon_list, the postion list will be clamped to it's length 
    '''
    for i, object in enumerate(objects):
        object.location = location_list[i][0][0]
        object.rotation_euler = location_list[i][1][0]
        object.scale = location_list[i][2][0]

def get_closest_to_object_bounding_box(source_object, compare_objects, space):
    '''
    return object that best matches bounding box of source_object \n
    space can be OBJECT or WORLD. ignore_negative_scale will ignore 
    negative scale on objects
    '''

    if space == 'WORLD':
        world_matrix = True
    else:
        world_matrix = False

    smallest_bb_diff = 1000000000000000
    closest_object = None
  
    for compare_object in compare_objects:
        if compare_object == source_object:
            continue

        bb_diff = bound_box_manager.get_bounding_box_difference_distance(
            source_object, 
            compare_object, 
            world_matrix
            ) 
        if bb_diff < smallest_bb_diff:
            smallest_bb_diff = bb_diff
            closest_object = compare_object
           
    return closest_object

def duplicate_objects_and_apply_modifiers(context, objects, hide_render_orig_objects = True):
    '''
    Duplicate objects and apply modifiers. 
    Each duplicated object has a custom property that 
    points to the original object
    Hides original objects in render by default
    Returns duplicated objects
    '''    
    orig_objects = objects
    
    
    # Duplicate each object and add a custom property that points
    # to the original object
    duplicated_objects = []
    for object in orig_objects:
        select_objects(context, 'REPLACE', [object])
        bpy.ops.object.duplicate()
        duplicated_object = context.active_object
        duplicated_objects.append(duplicated_object)
        duplicated_object['orig_object'] = object

    # Select the duplicated objects
    select_objects(context, 'REPLACE', duplicated_objects)

    # Make local & unique objects and data
    bpy.ops.object.make_local(type='SELECT_OBDATA')
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)

    # Delete modifier if not used in render, turn on if used in render
    for object in duplicated_objects:
        for modifier in object.modifiers:
            if modifier.show_render == False:
                object.modifiers.remove(modifier)
            else:
                modifier.show_viewport = True

    # Set view settings as render settings in each modifier (multires and subdiv)
    for object in duplicated_objects:
        for modifier in object.modifiers:
            if modifier.type == "SUBSURF" or modifier.type == "MULTIRES":
                modifier.levels = modifier.render_levels
    

    # Select the duplicated objects - for some reason, selection seems to get lost
    # after last select_objects()
    select_objects(context, 'REPLACE', duplicated_objects)
    
    # Apply modifiers
    apply_modifiers(context, duplicated_objects, type)

    # Hide render visibility of original objects
    if hide_render_orig_objects:
        for object in orig_objects:
            object.hide_render = True

    return duplicated_objects

def join_objects_and_rename(context, objects, new_name = ""):
    '''
    Join objects and rename. Return joined object. Assumes objects exists
    in active scene
    '''
    select_objects(context, 'REPLACE', objects, set_first_as_active = True)
    bpy.ops.object.join()
    joined_object = context.active_object
    
    if not new_name == "":
        joined_object.name = new_name
        joined_object.data.name = new_name + " mesh data"    
    
    return context.active_object

def apply_modifiers(context, objects, type):
    '''
    Applies modifiers to the object.
    If type == 'RENDER', modifiers uses render settings before applying
    modifiers
    '''
    orig_selection = context.selected_objects
    active_object = context.active_object
    
    for object in objects:
        if type == 'RENDER':
            for modifier in object.modifiers:
                # Change viewport settings
                try:
                    modifier.levels = modifier.render_levels
                    modifier.show_viewport = modifier.show_render

                    # TODO: Have I forgotten any other render property? 
                except:
                    pass
    
    # Apply modifiers
    select_objects(context, 'REPLACE', objects)
    bpy.ops.object.convert(target='MESH')

    # Restore selection
    select_objects(context, 'REPLACE', orig_selection)
    context.view_layer.objects.active = active_object

def list_objects_by_poly_count_limit(context, objects, poly_count_limit):
    '''
    Returns a dictionary with two lists. 
    listed_objects['under_poly_count'] = objects below poly limit
    listed_objects['over_poly_count'] = object above poly limit
    '''    
    dg = context.evaluated_depsgraph_get()
    listed_objects = {}
    listed_objects['under_poly_count'] = []
    listed_objects['over_poly_count'] = []

    for object in objects:

        poly_count = len(object.data.vertices)
        modifier_found = False

        # Get vertex count with modifiers
        # Check if object has subdiv or multires modifier
        # Code is a little lazy since it does not take other modifiers
        # into account
        for modifier in object.modifiers:
            if modifier.type == 'SUBSURF' or modifier.type == 'MULTIRES':
                modifier_found = True
                poly_count = poly_count * modifier.render_levels

        # Get poly count if object does not use subdiv or multires
        if not modifier_found:    
            eval_object = object.evaluated_get(dg)
            poly_count = len(eval_object.data.vertices)
        
        
        if poly_count > poly_count_limit:
            listed_objects['over_poly_count'].append(object)
        else:
            listed_objects['under_poly_count'].append(object)

    return listed_objects

def join_high_poly_objects(context, objects):
    '''
    Apply modifiers, transforms etc and join objects. Return
    resulting object

    Do not join objects with high polygon count, but return them. This
    is handy for sculpted objects with a multires modifier. This
    is taken hand of outside of this function, but worth noting here
    '''   

    # Select objects
    select_objects(context, 'REPLACE', objects, set_first_as_active = True)
    
    # Unparent - Tricky to detect negative scale when parented. Therefore unparent
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    # Flag if objects should recalculate normals (when scale is inverted)
    flag_objects_for_recalculate_normals(context, objects)
    
    # Apply transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Set normals to outside, after applying transform
    mesh_manager.set_normals_to_outside(context, objects)

    # Rename uv maps if needed for the join process
    # Make sure all objects active UV has same name so that it is not lost during the join process
    mesh_manager.handle_uv_naming_before_joining_objects(context, objects)
    
    # Store duplicated objects meshes
    meshes_to_remove = mesh_manager.get_meshes_list_from_objects(context.selected_objects, [context.active_object])

    # Apply custom split normal to each object
    mesh_manager.apply_custom_split_normal(context, objects)

    # Join objects
    joined_object = join_objects_and_rename(context, objects, "Joined high poly object")

    '''
    # Make sure normals are pointing out since inverted scale migh be used
    mesh_manager.set_normals_to_outside(context, [joined_object])
    '''

    # Delete the old duplicated meshes so that they don't take up memory
    mesh_manager.delete_meshes(context, meshes_to_remove)

    return context.selected_objects


def join_objects_for_baking(context, objects, make_duplicate = False):
    '''
    Join objects that are acting as bake target. 
    Make sure source objects connected high res objects are kept. 
    Make sure uv's are kept
    '''
    
    # Duplicate objects so that we don't mess with the original objects
    select_objects(context, 'REPLACE', objects, True)
    if make_duplicate == True:
        bpy.ops.object.duplicate()
    
    dupli_objects = context.selected_objects
    hi_res_objs = high_res_objects_manager.get_high_res_objects(context, dupli_objects)

    # Unparent - Tricky to detect negative scale when parented. Therefore unparent
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    for object in dupli_objects:
        # Make sure no modifiers that can result in overlapping
        bake_manager.turn_off_build_modifiers(object) # TODO: don't turn off mirror modifiers where UV's are offsetted
        
    # Rename uv maps if needed for the join process
    # Make sure all objects active UV has same name so that it is not lost during the join process
    mesh_manager.handle_uv_naming_before_joining_objects(context, objects)

    # Apply visual geometry and join objects, since it's faster during baking 
    apply_modifiers(context, [object], 'RENDER')
    meshes_to_remove = mesh_manager.get_meshes_list_from_objects(objects)
    
    # Flag if objects should recalculate normals (when scale is inverted)
    flag_objects_for_recalculate_normals(context, objects)

    # Apply scale to fix issues with extrusion if scale is not 1,1,1
    select_objects(context, 'REPLACE', objects, True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Apply custom split normal to each object
    mesh_manager.apply_custom_split_normal(context, objects)

    # Make sure normals are pointing out since inverted scale migh be used
    mesh_manager.set_normals_to_outside(context, objects)

    # Join and rename
    joined_object = join_objects_and_rename(context, objects, "Joined bake target object")
    
    # Add connection to high res objects to the new joined object
    high_res_objects_manager.add_high_res_objects_to_objects(context, hi_res_objs, [joined_object])
    
    # Delete the duplicated objects meshes from blender file
    meshes_to_remove.remove(joined_object.data)
    mesh_manager.delete_meshes(context, meshes_to_remove)

    return joined_object

def explode_locations_of_objects_and_highres_objects(context, objects, bake_locations, explode_distance = None):
    # Rename this to handle_positions_of_objects_during_baking
    
    '''
    if bake_location == EXPLODED: Position objects in a two dimensional 
    grid in order to avoid intersection during the baking process. 

    Corresponding high res objects will match the positions of the objects
    
    If distance = None, then distance will be the longest side of the biggest 
    bounding box multiplied with 1.5
    '''
    from math import sqrt
    # duplicate objects
    #import object_manager
    select_objects(context, 'REPLACE', objects, True)

    dupli_objects = objects #TODO: rename variable later 
    # get largest bounding box for distance
    if explode_distance == None:
        explode_distance = get_largest_bounding_box_side(dupli_objects) * 1.5

    all_high_res_objects = []

    rows = sqrt(len(dupli_objects))
    rows = int(rows)
    object_count = len(dupli_objects)

    # Oversized placement grid because it's simpler to wrap my brain around
    # Using object_count + 1 to leave the 0,0,0 placement empty. That placement
    # is reserved for objects with mirror modifiers with mirror_object that uses
    # all axes in the mirror modifier
    placement_grid = [[[False for x in range(object_count + 1)] for y in range(object_count + 1)] for z in range(object_count + 1)]

    if bake_locations == 'EXPLODED':
        # Explode objects
        for object in dupli_objects:

            # Update depsgraph so that matrix_world.translation will be correct
            # Object might be a child to another object that has been moved
            context.evaluated_depsgraph_get().update()

            hi_res_objs = high_res_objects_manager.get_high_res_objects(context, object)

            ok_offset_axes = get_non_used_axes_from_mirror_modifiers(hi_res_objs)
            
            coord = get_first_free_grid_placement(placement_grid, ok_offset_axes)
            placement_grid[coord[0]][coord[1]][coord[2]] = object

            #low_poly_position_vector = object.matrix_world.translation + (mathutils.Vector(coord) * explode_distance)
            low_poly_position_vector = mathutils.Vector(coord) * explode_distance
            low_poly_orig_position_vector = copy.copy(object.matrix_world.translation)
            move_object_to_world_vector(object, low_poly_position_vector)

            all_high_res_objects = all_high_res_objects + hi_res_objs
            
            # Move high res objects to same location as low poly
            # Use world matrix to avoid issues caused by parenting
            for high_res_object in hi_res_objs:
                                
                # Move object to it's original locations to avoid issues with 
                # new location, due to inconsistent offset
                if not high_res_object.get('orig location') == None:
                    high_res_object.location = high_res_object.get('orig location')

                # Store original location
                high_res_object['orig location'] = high_res_object.location
                
                # Update depsgraph so that matrix_world.translation will be correct
                context.evaluated_depsgraph_get().update()
                
                high_res_object_orig_world_matrix = high_res_object.matrix_world.copy()
                offset = high_res_object_orig_world_matrix.translation - low_poly_orig_position_vector
                move_object_to_target_location(high_res_object, object, offset)

                # Check if high res has deformer with modifier origin object. If so, that object
                # needs to be moved as well
                modifier_objects = get_objects_connected_to_modifier_that_affects_object_bounding_box([high_res_object])
                if len(modifier_objects) == 0:
                    continue
                
                # Move modifier object to corresponding high poly with offset
                for modifier_object in modifier_objects:
                    # Don't move modifier object if it has already been moved
                    if not modifier_object.get('orig location') == None:
                        continue
                    # get offset to original matrix
                    modifier_object['orig location'] = modifier_object.location
                    offset = high_res_object_orig_world_matrix.to_translation() - modifier_object.matrix_world.to_translation()
                    move_object_to_target_location(modifier_object, high_res_object, offset)


def copy_object_location(context, source_objects, target_objects):
    '''
    Copy location from source_object to target_objects by 
    list index. End when end of list on source_objects or target_objects
    has been reached.
    '''
    for index, source_object in enumerate(source_objects):
        if index >= len(target_objects):
            return
        target_objects[index].location = source_object.location

def copy_location_from_custom_property_object(context, objects, custom_property):
    '''
    Assumes that each object has a custom property that points to 
    another object. If that custom property exists, the location
    will be copied from that object
    '''   
    for object in objects:
        source_object = object.get(custom_property)
        if source_object:
            object.location = source_object.location

def delete_objects_and_data(objects):
    '''
    Delete objects of type 'MESH' and their data
    WARNING! The data can belong to other objects (instances) 
    This procedure does not care about that. It just nukes!
    '''

    for object in objects:
        # If object already is deleted
        if repr(object).find("Object invalid") > -1 :
            continue
        # If object is mesh
        if not object.type == 'MESH':
            continue        
        try:
            bpy.data.meshes.remove(object.data)
            bpy.data.objects.remove(object)
        except:
            print("Could not delete object and data")

def get_largest_bounding_box_side(objects):
    '''
    Return the longest side on an objects bounding box
    '''
    longest_length = 0
    for object in objects:
        for i in range(7):
            bb = object.bound_box
            bb_length = (mathutils.Vector(bb[i]) - mathutils.Vector(bb[i+1])).length
            if bb_length > longest_length: 
                longest_length = bb_length

    return longest_length

def get_vertex_count(context, object, evaluated = True):
   
    if evaluated:
        object = object.evaluated_get(context.evaluated_depsgraph_get())
   
    return len(object.data.vertices)

def filter_objects_by_type(objects, type_list):
    '''
    Returns all objects in objects that matches the type in type_list
    '''
    return_objects = []
    for object in objects:
        if object.type in type_list:
            return_objects.append(object)
    
    return return_objects

def reset_objects_original_locations(objects):
    '''
    Assumes each object in objects has a vector property called
    'orig location' that has the original position of the object stored.
    This property will be deleted after the position is restored
    '''
    for object in objects:

        if object.get('orig location') == None:
            continue

        orig_location = mathutils.Vector(object.get('orig location'))

        object.location = orig_location
        del object['orig location']


def get_object_list_dictionary_per_bake_collection(objects, scene = None):
    '''
    Sort objects in dictionary divided per bake collection
    Return dictionary:
    Key = Bake collection name
    [0] = Bake collection
    [1] = filtered list of objects that belong to Bake collection
    '''
    return_dictionary = {}

    if scene == None:
        scene = bpy.context.scene

    for object in objects:
        
        collection = collection_manager.get_bake_collections_by_object(context, object)

        if type(collection) == list:
            collection = collection[0]

        if return_dictionary.get(collection.name) == None:
            return_dictionary[collection.name] = [[],[]]
            return_dictionary[collection.name][0] = collection
            return_dictionary[collection.name][1] = [object]
        else:
            return_dictionary[collection.name][1].append(object)

    return return_dictionary
        
def filter_objects_that_has_highres_connection(context, objects):
    '''
    Return a list with all objects in objects that has connected high res objects
    '''
    filtered_objects = []
    for object in objects:
        high_res_objects = high_res_objects_manager.get_high_res_objects(context, [object])
        if len(high_res_objects) > 0:
            filtered_objects.append(object)
    
    return filtered_objects

def filter_bakable_high_res_objects(objects):
    '''
    Remove objects from 'objects' that can not be used as a bake source
    '''
    filtered_objects = filter_objects_by_type(objects, ['MESH', 'META', 'CURVE', 'FONT', 'SURFACE'])

    return filtered_objects
            
def can_be_bakable_high_res_object(obj):
    '''
    Return True if object can be used as a bake source
    '''
    filter_type_list = ['MESH', 'META', 'CURVE', 'FONT', 'SURFACE']
    
    return obj.type in filter_type_list

def get_object_hide_viewport_state(context, objects):
    '''
    Return hide viewport state of each object as a dictionary
    Bake target objects must be visible in viewport in order to bake
    '''
    hide_viewport_state = {}
    for object in objects:
        hide_viewport_state[object.name] = object.hide_viewport
    
    return hide_viewport_state

def set_object_hide_viewport_state(context, bake_render_settings, hide_viewport_state = None):
    '''
    Sets hide_select_state of objects. Assumes bake_render_settings
    has a key like 
    bake_render_settings['hi_res_objs_hide_select_state']
    with object and hide_viewport_state
    if hide_viewport_state is not None, it will override the value
    '''

    # If not using hide_viewport_state, then use value from dictionary
    if hide_viewport_state == None:
        for key, value in bake_render_settings['objs_hide_viewport_state'].items():
            bpy.data.objects[key].hide_set(value)
    # Use hide_viewport_state value from hide_select_state
    else:
        for key, value in bake_render_settings['objs_hide_viewport_state'].items():
            bpy.data.objects[key].hide_set(hide_viewport_state)
    

def get_objects_hide_render_settings(context, objects):
    '''
    Return a dictionary with each objects hide render property and it's hide render value 
    '''
    objects_hide_render_settings = {}
    for object in objects:
        #objects_hide_render_settings[object] = object.hide_render
        property = "bpy.data.objects[\'" + object.name + "\'].hide_render"
        objects_hide_render_settings[property] = object.hide_render

    return objects_hide_render_settings

def get_object_hide_select_state(context, objects):
    '''
    Return selectable state of each object as a dictionary
    hide_select = True, object CAN'T be selected 
    hide_select = False, object CAN be selected 
    High res objects must be selectable in order to use during baking
    '''
    hide_select_state = {}
    for object in objects:
        hide_select_state[object.name] = object.hide_select
    
    return hide_select_state

def set_object_hide_select_state(context, bake_render_settings, hide_select_state = None):
    '''
    Sets hide_select_state of objects. Assumes bake_render_settings
    has a key like 
    bake_render_settings['hi_res_objs_hide_select_state']
    with object and hide_select_state
    if hide_select_stat is not None, it will override the value
    '''
    # If not using hide_select_state, then use value from dictionary
    if hide_select_state == None:
        for key, value in bake_render_settings['objs_hide_select_state'].items():
            try:
                bpy.data.objects[key].hide_select = value
            except:
                print("Could not set hide_select on object " + bpy.data.objects[key].name)
    # Use hide_select_state value from hide_select_state
    else:
        for key, value in bake_render_settings['objs_hide_select_state'].items():
            try:
                bpy.data.objects[key].hide_select = hide_select_state
            except:
                print("Could not set hide_select on object " + bpy.data.objects[key].name)

def object_has_bsdf_connected_to_material_output(object):
    '''
    Returns True if object has a material with a BSDF plugged into material output
    '''

    for material_slot in object.material_slots:
        if material_slot.material == None:
            continue
        for node in material_slot.material.node_tree.nodes:
            if node.type == 'OUTPUT_MATERIAL':
                if node.inputs['Surface'].links[0].from_node.type == 'BSDF_PRINCIPLED':
                    return True

    return False

def get_objects_connected_to_modifier_that_affects_object_bounding_box(objects):
    '''
    Returns a list with all objects has modifier with 
    connected object to modifier (such as a mirror modifier with a mirror object)
    '''
    modifier_object_list = []
    modifier_list = ['ARMATURE', 'CAST', 'CURVE', 'HOOK', 'LATTICE', 'SIMPLE_DEFORM']
    for object in objects:
        for modifier in object.modifiers:
            
            if modifier.type == 'MIRROR' and not modifier.mirror_object == None:
                if not modifier.mirror_object in modifier_object_list:
                    pass
                    # Ignore mirror modifier objects, since I'm moving affected mesh objects instead
                    #modifier_object_list.append(modifier.mirror_object)
            elif modifier.type in modifier_list and not modifier.object == None:
                if not modifier.object in modifier_object_list:         
                    modifier_object_list.append(modifier.object)
            elif modifier.type == 'SHRINKWRAP' and not modifier.target == None:
                if not modifier.target in modifier_object_list:  
                    modifier_object_list.append(modifier.target)
            elif modifier.type == 'WARP':
                if modifier.object_from != None and not modifier.object_from in modifier_object_list:
                    modifier_object_list.append(modifier.object_from)
                if modifier.object_to != None and not modifier.object_to in modifier_object_list:
                    modifier_object_list.append(modifier.object_to)

                
    return modifier_object_list

def move_object_to_target_location(object, target_object, offset = mathutils.Vector([0,0,0])):
    '''
    Moves object to the same location as target
    by using world_matrix. This makes it less complicated when the object
    and target_object might be parent and/or child to other objects
    '''
    world_vector = target_object.matrix_world.to_translation()
    move_object_to_world_vector(object, world_vector, offset)


def move_object_to_world_vector(object, world_vector, offset = mathutils.Vector([0,0,0])):
    
    # Make sure world vector is a matrix for matrix calculation later
    if type(world_vector) == list:
        world_vector = mathutils.Vector(world_vector)

    # Remove location from objects matrix. Objects rotation and scale is kept
    object.matrix_world = object.matrix_world.to_3x3().to_4x4()
        
    goal_matrix = mathutils.Matrix.Translation(world_vector + offset)
    
    object.matrix_world = goal_matrix @ object.matrix_world


def get_non_used_axes_from_mirror_modifiers(objects):
    ''''
    Check for mirror modifier on object
    Check if modifier has modifier object that sets mirror point
    Return the axes that are safe to use to  transform the object 
    '''
    # TODO writing this
    non_used_axes = ""
    used_axes = ""
    # Get all used axes from all mirror modifiers that has a mirror object 
    # in the objects
    for object in objects:
        for modifier in object.modifiers:
            if not modifier.type == "MIRROR":
                continue
            if modifier.mirror_object == None:
                continue
            if modifier.use_axis[0]:
                used_axes += "X"
            if modifier.use_axis[1]:
                used_axes += "Y"       
            if modifier.use_axis[2]:
                used_axes += "Z"

    if not 'X' in used_axes:
        non_used_axes += "X"
    if not 'Y' in used_axes:
        non_used_axes += "Y"
    if not 'Z' in used_axes:
        non_used_axes += "Z"

    return non_used_axes

def get_first_free_grid_placement(grid, ok_axes_placement):
    '''
    Returns an array with the coordinates of the first free
    grid placement to be used when exploding objects.
    
    Objects with mirror modifiers using mirror_object makes placement 
    extra important. We don't want to offset an objects location 
    on the same axis that the mirror modifier with mirror_object uses.
    This is why ok_axes_placement is used
    '''
    if ok_axes_placement == "":
        return [0,0,0]

    start_location = 1

    # TODO: Issue with this function. Since my start location == 1, some objects that needs
    # to be on 0 axis are not

    # Set max placement per grid axis
    # This is used to avoid getting unwanted issues with
    # potential mirror modifiers
    if "X" in ok_axes_placement:
        min_x = 1
        max_x = len(grid[0])
    else:
        min_x = 0
        max_x = 1

    if "Y" in ok_axes_placement:
        min_y = 1
        max_y = len(grid[0])
    else:
        min_y = 0
        max_y = 1   

    if "Z" in ok_axes_placement:
        min_z = 1
        max_z = len(grid[0])
    else:
        min_z = 0
        max_z = 1   

    #print("max xyz = " + str(max_x) + ", " + str(max_y) + ", " + str(max_z))
    
    for z in range(min_z,max_z):
        #print("z = " + str(z))
        for y in range(min_y, max_y):
            #print("y = " + str(y))
            for x in range(min_x, max_x):
                #print("x = " + str(x))
                if grid[x][y][z] == False:
                    return [x, y, z]

    #print("Could not find an empty grid placement. Returning 0,0,0")
    return [0,0,0]

