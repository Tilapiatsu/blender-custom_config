import bpy
import copy
import addon_utils
import os
import time

PIN_GROUP_NAME = 'pinned'
STIFFNESS_GROUP_NAME = 'stiffness'
SHRINKING_GROUP_NAME = 'shrinking'
PRESSURE_GROUP_NAME = 'pressure'

CLOTH_TRIANGULATION = 'cloth_triangulation'
ASSET_FOLDER_NAME = 'BCB cloth assets'
ADDON_NAME = 'Bystedts Cloth Builder'

COLLISION = 'COLLISION'
CLOTH = 'CLOTH'
TRIANGULATE = 'TRIANGULATE'

    
def compare_dictionaries(dic1, dic2):
    # A test function. Useful for figure out difference in context dictionaries
    for key, value in dic1.items():
        if dic1[key] == dic2[key]:
            continue
        print(key + " differs. Dic1 == " + str(dic1[key]) + ", dic2== " + str(dic2[key]))

def get_addon_path():

    for mod in addon_utils.modules():
        if mod.bl_info.get("name") == ADDON_NAME:
            filepath = mod.__file__
            folder = os.path.dirname(filepath)
            return folder

def get_asset_browser_folder():
    path = get_addon_path()
    path = os.path.join(path, ASSET_FOLDER_NAME)
    return path

def add_asset_browser_to_preferences(context):
    if asset_browser_is_added(context):
        return

    path = get_asset_browser_folder()
    bpy.ops.preferences.asset_library_add(directory = path)

def get_asset_browser_index(context):
    for index, library in enumerate(context.preferences.filepaths.asset_libraries):
        if library.name == ASSET_FOLDER_NAME:
            return index
    
    return -1

def asset_browser_is_added(context):
    if get_asset_browser_index(context) > -1:
        return True
    else:
        return False

def remove_asset_browser_from_preferences(context):
    index = get_asset_browser_index(context)
    if index > -1:
        bpy.ops.preferences.asset_library_remove(index=index)

def open_asset_browser_window(context):

    override = context.copy()
    # Add cloth asset browser if not added
    if not asset_browser_is_added(context):
        add_asset_browser_to_preferences(context)
 
    # Create new window
    area =  context.area
    orig_area_type = context.area.ui_type
    
    
    area.ui_type = 'ASSETS'


    def defer():
        if area.spaces.active.params is None:
            return 0
        area.spaces[0].params.asset_library_ref = ASSET_FOLDER_NAME
        area.spaces[0].params.import_type = 'APPEND'
        override = context.copy()
        override['area'] = area
        bpy.ops.screen.area_dupli(override, 'INVOKE_DEFAULT')
        area.ui_type = orig_area_type

    
    bpy.app.timers.register(defer)



    



def test_print(context):
    print("scene = " + context.scene.name)

def get_sim_quality(context):
    return context.scene.BCB_props['sim_quality']

def run_simulation(context):

    # I can't add asset browser during registration for some reason
    # add it if needed during this function in the meanwhile 
    add_asset_browser_to_preferences(context)

    # Set simulation end frame
    context.scene.BCB_props.orig_end_frame = context.scene.frame_end
    context.scene.frame_end = context.scene.BCB_props.simulation_frames
        
    set_modifier_settings(context)
    # Play every frame
    bpy.context.scene.sync_mode = 'NONE'


    bpy.ops.screen.animation_play()

def stop_simulation(context):
    print("init stop simulation")
    if bpy.context.screen.is_animation_playing:
        print("animation playing - stopping sim")
        bpy.ops.screen.animation_play()  
    else:
        print("animation is not playing")

def reset_simulation(context):
    bpy.ops.screen.frame_jump(end=False)
    reset_pin_locations(context)

def reset_hook_modifiers(context, objects):

    # Get mesh objects from selected pin objects
    hooked_objects = get_objects_using_pin(context, objects)


    # Get objects using hook modifier
    objects_with_hook_modifier = filter_objects_using_modifier(context, 'HOOK', objects)

    # Merge object lists
    objects = hooked_objects + objects_with_hook_modifier
    objects = list(set(objects))

    if len(objects) == 0:
        return
    
    # Can't seem to get context override to work properly. 
    # Entering edit mode to fix issue. 
    #############################################
    orig_selected_objects = context.selected_objects
    orig_active_object = context.object

    bpy.ops.object.select_all(action='DESELECT')
    for object in objects:
        object.select_set(state=True)
    context.view_layer.objects.active = objects[0]

    if not context.mode == 'EDIT_MESH':
        orig_context = context.mode
        bpy.ops.object.mode_set(mode = 'EDIT')
    else:
        orig_context = context.mode
    #############################################
    

    override = context.copy()
    
    # Loop through hooked mesh objects and reset hook modifiers
    for object in objects:
        for mod in object.modifiers:

            override = get_context_override(
                context,
                mode = 'EDIT_MESH',
                active_object = object,
                selected_objects = [object]
                )

            if not mod.type == 'HOOK':
                continue

            with context.temp_override(**override):
                bpy.ops.object.hook_reset(modifier=mod.name)
    

    # Transforms to deltas on all pin objects
    pin_objects = get_pin_objects_from_mesh_objects(context, objects)
    override = get_context_override(context, 
        mode = 'OBJECT', 
        active_object=pin_objects[0], 
        selected_objects=pin_objects
        )

    with context.temp_override(**override):
        bpy.ops.object.transforms_to_deltas(mode='ALL')

    # Restore selection and mode
    bpy.ops.object.mode_set(mode = orig_context)
    for object in orig_selected_objects:
        object.select_set(state=True)
    context.view_layer.objects.active = orig_active_object

def add_cloth_to_objects(context, objects = None):
    
    reset_simulation(context)

    if objects == None:
        objects = context.selected_objects   
    
    override = context.copy()

    for object in objects:
        if not object.type == 'MESH':
            continue

        # If object does not have cloth modifier
        if len(get_modifiers(context, 'CLOTH', [object])) > 0:
            continue
        
        # Add cloth modifier
        override = get_context_override(
            context,
            mode = 'OBJECT',
            active_object = object,
            selected_objects = context.selected_objects
            )

        with context.temp_override(**override):
            bpy.ops.object.modifier_add(type='CLOTH') 

        # Set properties of cloth modifier
        set_modifier_settings(context, [object])
        cloth_modifier = get_last_modifier(context, object)
        cloth_modifier.settings.shrink_max = 0.5

        # Add default weights
        add_default_vertex_groups_on_objects(context, [object])

        # Place after collision modifier
        place_relative_to_target_modifer(
            context, cloth_modifier, 'COLLISION', 1)

        # Create triangulate modifier if needed
        if context.scene.BCB_props.use_triangulate:
            add_triangulate_modifier_for_cloth(
                context, [object])

def get_last_modifier(context, object = None):
    if object == None:
        object = context.object
    return object.modifiers[len(object.modifiers)-1]

def add_triangulate_modifier_for_cloth(context, objects = None):

    if objects == None:
        objects = context.selected_objects   

    for object in objects:
        # Create modifier
        override = get_context_override(
            context,
            mode = 'OBJECT',
            active_object = object,
            selected_objects = context.selected_objects
            )

        with context.temp_override(**override):
            bpy.ops.object.modifier_add(type='TRIANGULATE')

        # Settings
        traingulate_mod = object.modifiers[len(object.modifiers)-1]
        traingulate_mod.quad_method = 'LONGEST_DIAGONAL'
        traingulate_mod.keep_custom_normals = True


        # Add custom name to flag that it belongs to cloth
        # This is later used when deleting cloth
        traingulate_mod.name = CLOTH_TRIANGULATION

        # Place it after cloth modifier
        place_relative_to_target_modifer(
            context, traingulate_mod, 'CLOTH',1)

def place_relative_to_target_modifer(context, modifier, target_modifier_type, index_offset):
    # Places the modifier before or after another modifier
    # of a specific modifier.
    # For example: Place a cloth modifier before a 
    # collision modifier

    object = modifier.id_data

    target_mods = get_modifiers(context, target_modifier_type, [object]) 
    
    if len(target_mods) == 0: 
        return
    
    mods = object.modifiers.values()
    target_index = max(mods.index(target_mods[0]) + index_offset, 0)
    bpy.ops.object.modifier_move_to_index(modifier=modifier.name, index=target_index)


def remove_cloth_from_objects(context, objects = None):
    
    if objects == None:
        objects = context.selected_objects       
    
        # Remove cloth modifiers
        mods = get_modifiers(context, CLOTH, objects)  
        for mod in mods:
            mod.id_data.modifiers.remove(mod)

        # Remove triangulate modifiers
        mods = get_modifiers(context, TRIANGULATE, objects)  
        for mod in mods:
            if not mod.name.find(CLOTH_TRIANGULATION) == -1:
                mod.id_data.modifiers.remove(mod)

def add_collision_to_objects(context, objects = None):
    
    if objects == None:
        objects = context.selected_objects  

    override = context.copy()

    for object in objects:
        # If object does not have cloth modifier
        if len(get_modifiers(context, 'COLLISION', [object])) > 0:
            continue
        
        # Add collision modifier
        override = get_context_override(
            context,
            mode = 'OBJECT',
            active_object = object,
            selected_objects = context.selected_objects
            )

        with context.temp_override(**override):
            bpy.ops.object.modifier_add(type='COLLISION') 

        # Set object collision settings
        object.collision.use_normal = True

        set_modifier_settings(context, [object])

def remove_collision_from_objects(context, objects = None):
    
    if objects == None:
        objects = context.selected_objects       
    
    mods = get_modifiers(context, 'COLLISION', objects)  
    for mod in mods:
        mod.id_data.modifiers.remove(mod)

def filter_objects_using_modifier(context, modifier_type, objects = None):
    # Filter the objects that has a modifier by the type modifier_type
    filtered_objects = []

    if objects == None:
        objects = context.scene.objects

    for object in objects:
        for mod in object.modifiers:
            if mod.type == modifier_type:
                filtered_objects.append(object)
                break   

    return filtered_objects

def get_modifiers(context, modifier_type, objects = None, is_shown_in_viewport = None):
    # Return the modifiers of modifier_type used by objects
    # If modifier_type == "*" then any modifer will be returned

    modifiers = []
    if objects == None:
        objects = context.scene.objects
    
    for object in objects:
        for mod in object.modifiers:
            if is_shown_in_viewport == True and mod.show_viewport == False:
                continue
            if is_shown_in_viewport == False and mod.show_viewport == True:
                continue
            if mod.type == modifier_type or modifier_type == "*":
                modifiers.append(mod)
    
    return modifiers

def has_pin_group(context, object):
    for grp in object.vertex_groups:
        if grp.name == PIN_GROUP_NAME:
            return True
    
    return False

def reset_pin_locations(context):
    for object in context.scene.objects:
        if object.get('is_pin'):
            object.location = (0,0,0)
            object.rotation_euler = (0,0,0)
            object.scale = (1,1,1)



def remove_pins_in_scene(context):
    for object in context.scene.objects:
        if object.get('is_pin'):
            remove_pin(context, object)


def add_pin(context):
    orig_object = context.object

    # Handle pinning group
    if not has_pin_group(context, context.object):
        bpy.ops.object.vertex_group_assign_new()
        context.object.vertex_groups.active.name = PIN_GROUP_NAME
    else:
        bpy.ops.object.vertex_group_set_active(group=PIN_GROUP_NAME)
        bpy.ops.object.vertex_group_assign()

    # Add empty
    orig_cursor_loc = copy.copy(bpy.context.scene.cursor.location)
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD')
    bpy.context.scene.cursor.location = orig_cursor_loc
    empty = context.object
    empty.empty_display_type = context.scene.BCB_props.pin_shape
    empty.name = "Pin"
    empty['is_pin'] = True
    empty.empty_display_size = context.scene.BCB_props.pin_scale

    bpy.ops.object.transforms_to_deltas(mode='ALL')


    # Select orig object
    orig_object.select_set(state = True)
    context.view_layer.objects.active = orig_object

    # Add hook modifier
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.object.hook_add_selob(use_bone=False)

    # Handle cloth modifiers properties
    mods = get_modifiers(context, 'CLOTH', [orig_object])
    if len(mods) > 0:
        #bpy.ops.object.modifier_move_to_index(modifier=mods[0].name, index=modifier_count -1)
        mods[0].settings.vertex_group_mass = PIN_GROUP_NAME

    # Move all hook modifiers to first position in modifier list
    hook_modifiers = get_modifiers(context, 'HOOK', objects=[orig_object])
    for mod in hook_modifiers:
        bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)

def delete_pin_modifiers_using_object(context, hook_object):
    for object in context.scene.objects:
        for mod in object.modifiers:
            if not mod.type == 'HOOK':
                continue
            if mod.object == hook_object:
                object.modifiers.remove(mod)

def get_hook_modifiers_using_pin(context, hook_object):
    hook_modifiers = []
    for object in context.scene.objects:
        for mod in object.modifiers:
            if not mod.type == 'HOOK':
                continue
            if mod.object == hook_object:
                hook_modifiers.append(mod)  
    return hook_modifiers

def get_objects_using_pin(context, hook_objects):
    # Return objects that has hook modifiers that uses the hook_objects
    hooked_objects = []

    for hook_object in hook_objects:
        if not hook_object.get('is_pin'):
            continue
        for object in context.scene.objects:
            for mod in object.modifiers:
                if not mod.type == 'HOOK':
                    continue
                if not mod.object == hook_object:
                    continue
                if object in hooked_objects:
                    continue
                hooked_objects.append(object)  

    return hooked_objects

def remove_selected_pins(context):
    print("init remove_selected_pins")
    for object in context.selected_objects:
        remove_pin(context, object)

def remove_pin(context, object):

    if object == None:
        return
    if not object.get('is_pin'):
        print("object " + object.name + "is not a pin")
        return

    hooked_mods = get_hook_modifiers_using_pin(context, object)
    for mod in hooked_mods:
        # Remove associated vertices from group
        mod.id_data.vertex_groups[PIN_GROUP_NAME].remove(mod.vertex_indices)


    delete_pin_modifiers_using_object(context, object)
    bpy.data.objects.remove(object)

def get_pin_objects_from_mesh_objects(context, objects):
    # Get pin objects
    pin_objects = []

    for object in objects:
        for mod in object.modifiers:
            if not mod.type == 'HOOK':
                continue
            if mod.object in pin_objects:
                continue
            pin_objects.append(mod.object)
    
    return pin_objects

def clear_pins(context):
    # Get pin objects
    pin_objects = get_pin_objects_from_mesh_objects(
        context, 
        context.selected_objects)

    for object in pin_objects:
        remove_pin(context, object)
    
def save_shape_key(context):

    subsurf_modifiers = []

    
    if context.scene.BCB_props.apply_subsurf_modifiers:
        apply_subsurf_modifiers(context)

    # Turn off subsurf and multires modifiers that might interfere
    subsurf_modifiers = get_modifiers(context, 'SUBSURF', is_shown_in_viewport=True)
    subsurf_modifiers = subsurf_modifiers + get_modifiers(context, 'MULTIRES', is_shown_in_viewport=True)
    for modifier in subsurf_modifiers:
        modifier.show_viewport = False

    # Get cloth modifiers
    cloth_mods = get_modifiers(context, 'CLOTH', context.selected_objects)   

    for mod in cloth_mods:
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=mod.name)

    # Turn on subsurf and multires modifiers that was
    # temporary turned off
    for modifier in subsurf_modifiers:
        modifier.show_viewport = True

def reshape_multires_modifiers(context, objects):

    orig_selection = context.selected_objects
    orig_active_object = context.active_object

    for object in objects:

        turned_off_modifiers = []

        if get_modifiers(context, 'MULTIRES', [object]) == -1:
            continue

        # Turn off all modifiers except cloth and multires
        for mod in object.modifiers:
            if mod.type == 'CLOTH' or mod.type == 'MULTIRES':
                continue
            if mod.show_viewport == False:
                continue
            mod.show_viewport = False
            turned_off_modifiers.append(mod)


        # Select object only
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = object
        object.select_set(state = True)

        bpy.ops.object.duplicate_move()

        buffer_object = context.active_object

        # Remove cloth modifier from buffer_object
        for modifier in buffer_object.modifiers:
            if modifier.type == 'CLOTH':
                buffer_object.modifiers.remove(modifier)
                
        # Reshape buffer_object with object
        multires_mod = None
        for modifier in buffer_object.modifiers:
            if modifier.type == 'MULTIRES':
                multires_mod = modifier
                break

        object.select_set(state = True)
        bpy.ops.object.multires_reshape(modifier = multires_mod.name)
                
        # Reshape object with buffer_object
        context.view_layer.objects.active = object

        for modifier in buffer_object.modifiers:
            if modifier.type == 'MULTIRES':
                multires_mod = modifier
                break

        bpy.ops.object.multires_reshape(modifier = multires_mod.name)
            
        # Remove buffer object
        bpy.data.objects.remove(buffer_object)

        # Restore modifiers that was turned off
        for mod in turned_off_modifiers:
            mod.show_viewport = True
    
    # Restore selection
    for object in orig_selection:
        object.select_set(state = True)
    context.view_layer.objects.active = orig_active_object
    

def fit_to_active(context, offset = 0.0, corrective_iterations = 5, keep_modifiers = False, objects = None):

    print("init fit_to_active")

    if objects == None:
        objects = context.selected_objects

    reset_simulation(context)

    target_object = context.active_object

    for object in objects:
        if object == context.active_object:
            continue

        override = get_context_override(
            context, 'OBJECT', object, [object])
        
        with context.temp_override(**override):
            # Shrinkwrap
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            modifier = get_last_modifier(context, object)
            modifier.wrap_method = 'TARGET_PROJECT'
            modifier.wrap_mode = 'OUTSIDE_SURFACE'
            modifier.offset = offset
            modifier.target = target_object
            first_shrinkwrap = modifier

            # Corrective 
            first_shrinkwrap.show_viewport = False
            bpy.ops.object.modifier_add(type='CORRECTIVE_SMOOTH')
            modifier = get_last_modifier(context, object)
            modifier.rest_source = 'BIND'
            bpy.ops.object.correctivesmooth_bind(modifier = modifier.name)
            first_shrinkwrap.show_viewport = True

            # One final shrinkwrap after corrective
            # if corrective_iterations == 0
            if corrective_iterations == 0:
                bpy.ops.object.modifier_add(type='SHRINKWRAP')
                modifier = get_last_modifier(context, object)
                modifier.wrap_method = 'TARGET_PROJECT'
                modifier.wrap_mode = 'OUTSIDE_SURFACE'
                modifier.offset = offset
                modifier.target = target_object

            # Apply modifiers
            if not keep_modifiers:
                modifiers = object.modifiers
                if corrective_iterations == 0:
                    end = 3
                else:
                    end = 2

                for i in range(0, end):
                    index = len(modifiers) - (end-i)
                    bpy.ops.object.modifier_apply(modifier = modifiers[index].name)

def apply_base(context):

    override = context.copy()
    subsurf_modifiers = []

    if context.scene.BCB_props.apply_subsurf_modifiers:
        apply_subsurf_modifiers(context)
    else:
        # Turn off subsurf and multires modifiers that might interfere
        subsurf_modifiers = get_modifiers(context, 'SUBSURF', is_shown_in_viewport=True)
        subsurf_modifiers = subsurf_modifiers + get_modifiers(context, 'MULTIRES', is_shown_in_viewport=True)
        for modifier in subsurf_modifiers:
            modifier.show_viewport = False

    # Apply cloth modifier on all objects
    for object in context.selected_objects:
        cloth_mods = get_modifiers(context, 'CLOTH', [object])   

        for mod in cloth_mods:
            override = get_context_override(
                context,
                mode = 'OBJECT',
                active_object = object,
                selected_objects = [object]
                )

            with context.temp_override(**override):
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=mod.name)

                shape_keys = mod.id_data.data.shape_keys.key_blocks
                # Set all shapekeys to zero
                for sk in shape_keys:
                    sk.value = 0

                # Set last shapekey to 1 
                sk_index = len(shape_keys) -1
                shape_keys[sk_index].value = 1

                # Apply shapekey
                for i in range(sk_index + 1):
                    bpy.context.object.active_shape_key_index = 0
                    bpy.ops.object.shape_key_remove(all=False)

    # Reset hook modifiers of objects
    reset_hook_modifiers(context, context.selected_objects)

    # Pin locators - set transforms to deltas
    pin_locs = get_pin_objects_from_mesh_objects(context, [object])
    transforms_to_deltas_on_pin_objects(context, pin_locs)

    
    #reset_simulation(context)

    # Turn on subsurf and multires modifiers 
    # that was temporarily turned off
    for modifier in subsurf_modifiers:
        modifier.show_viewport = True


def transforms_to_deltas_on_pin_objects(context, objects):
    # Use context override to set transforms to deltas
    

    # The override in this function works!
    override = context.copy()

    for object in objects:
        if not object.get('is_pin'):
            continue
        '''
        override['active_object'] = object
        override['object'] = object
        override['selected_objects'] = [object]
        override['selected_editable_objects'] = [object]
        override['mode'] = 'OBJECT'
        '''
        override = get_context_override(
            context,
            mode = 'OBJECT',
            active_object=object,
            selected_objects=[object]
        )
        with context.temp_override(**override):
            bpy.ops.object.transforms_to_deltas(mode='ALL')  
            print("transform to deltas on object " + object.name)
            


def get_self_collision_from_object(context, object):

    if object == None:
        return False

    mods = get_modifiers(context, 'CLOTH', object)

    return mods[0].collision_settings.use_self_collision


def apply_subsurf_modifiers(context, objects = None):

    if objects == None:
        objects = context.selected_objects

    for object in objects:
        modifiers = get_modifiers(context, 'MULTIRES', objects)
        modifiers = modifiers + get_modifiers(context, 'SUBSURF')

    for modifier in modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier.name)

def shake_cloth(context, objects = None, shrink = 0.1, frames = 20):
    
    # Shakes the cloth a bit to create random wrinkles
    '''
    # Settle the cloth if frame is 1
    if context.scene.frame_current == 1:
        for i in range(1,10):
            context.scene.frame_set(context.scene.frame_current + 1)        

    '''    
    start_frame = context.scene.frame_current
    end_frame = start_frame + frames
    moved_frames = 0


    if objects == None:
        objects = context.selected_objects

     # Get cloth modifiers
    cloth_mods = get_modifiers(context, 'CLOTH', objects)    

    # Store orig settings shrink min and max
    shrink_min_settings = []
    shrink_max_settings = []
    for mod in cloth_mods:
        shrink_min_settings.append(mod.settings.shrink_min)
        shrink_max_settings.append(mod.settings.shrink_max)

    # Set initial shrink of cloth
    for mod in cloth_mods:
        mod.settings.shrink_min = mod.settings.shrink_min + shrink
        mod.settings.shrink_max = 0

    # Start progress
    context.window_manager.progress_begin(1,frames)
    
    # Move frames forward
    for i in range(1,int(frames / 2)):
        context.scene.frame_set(context.scene.frame_current + 1)
        moved_frames += 1
        context.window_manager.progress_update(moved_frames)

    # Cloth settings restore shrink min and max
    # TODO reset with original setting

    for i, mod in enumerate(cloth_mods):
        mod.settings.shrink_min = shrink_min_settings[i]    
        mod.settings.shrink_max = shrink_max_settings[i]

    # Move frames forward
    for i in range(1,int(frames / 2)):
        context.scene.frame_set(context.scene.frame_current + 1)
        moved_frames += 1
        context.window_manager.progress_update(moved_frames)

    context.window_manager.progress_end()

def make_duplicate(context, apply_geo_nodes = False, apply_multires_on_duplicate = True):

    orig_context = context.copy()
    new_objects = []

    for object in context.selected_objects:
        # Only select object
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(state = True)
        
        # Temporary turn off geo nodes modifiers
        gn_mods = get_modifiers(context, 'NODES', 
                    [object], is_shown_in_viewport=True)
        for mod in gn_mods:
            mod.show_viewport = False
            
        # Store amount of subdivision
        mods = get_modifiers(context, 'SUBSURF', [object]) + get_modifiers(context, 'MULTIRES',[object])
        subdiv = 0
        for mod in mods:
            subdiv =  subdiv + mod.levels

        # Duplicate mesh
        bpy.ops.object.duplicate()
        duplicate = context.object
        new_objects.append(duplicate)


        # Remove modifiers
        mods = get_modifiers(context, "*", objects = [duplicate])
        for mod in mods:
            if mod.type == 'NODES':
                continue
            else:
                duplicate.modifiers.remove(mod)

        # Add multi res modifier and reshape based on source object
        bpy.ops.object.modifier_add(type='MULTIRES')
        mods = get_modifiers(context, 'MULTIRES', [duplicate])
        print("subdiv = " + str(subdiv))
        for i in range(subdiv):
            print("subddividing object " + context.object.name + " with mod " + mods[0].name)
            bpy.ops.object.multires_subdivide(modifier=mods[0].name, mode='CATMULL_CLARK')
        
        orig_context['active_object'].select_set(state = True)
        bpy.ops.object.multires_reshape(modifier=mods[0].name)
        if apply_multires_on_duplicate:
            bpy.ops.object.modifier_apply(modifier=mods[0].name, report=True)

        # Turn on geo nodes on original
        for mod in gn_mods:
            mod.show_viewport = True
        
        # Turn on geo nodes on duplicate
        gn_mod_names = []
        for mod in gn_mods:
            gn_mod_names.append(mod.name)
        duplicate_gn_mods = get_modifiers(context, 'NODES', [duplicate])
        for mod in duplicate_gn_mods:
            if mod.name in gn_mod_names:
                mod.show_viewport = True
            # Apply geo nodes modifier
            if apply_geo_nodes:
                if mod.show_viewport:
                    bpy.ops.object.modifier_apply(
                        modifier=mod.name, report=True)
                else:
                    duplicate.modifiers.remove(mod)
                    
        # Select new objects
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = new_objects[0]
        for duplicate in new_objects:
            duplicate.select_set(state = True)
            duplicate.name = "Duplicate"


def set_modifier_settings(context, objects = None):

    BCB_props = context.scene.BCB_props

    if objects == None:
        objects = context.scene.objects

    # Get cloth modifiers
    cloth_mods = get_modifiers(context, 'CLOTH', objects)
    
    # Cloth settings
    for mod in cloth_mods:

        # Set modifier settings
        mod.point_cache.frame_end = BCB_props.simulation_frames
        
        if BCB_props.use_global_settings:
            mod.settings.quality = BCB_props.sim_quality
            mod.settings.vertex_group_mass = PIN_GROUP_NAME
            mod.collision_settings.distance_min = BCB_props.collision_distance
            mod.collision_settings.self_distance_min = BCB_props.collision_distance
            mod.collision_settings.collision_quality = BCB_props.collision_quality

    # Collision settings
    if not BCB_props.use_global_settings:
        return

    for object in objects:
        
        if object.collision == None:
            continue

        if object.collision.use == False:
            continue

        object.collision.thickness_outer = BCB_props.collision_distance
        object.collision.thickness_inner = BCB_props.collision_distance


def get_context_override(context, mode = None, active_object = None, selected_objects = None):

    '''
    mode is usually 'EDIT_MESH' or 'OBJECT'
    '''
    override = context.copy()

    if active_object == None:
        active_object = context.active_object
    if selected_objects == None:
        selected_objects = context.selected_objects
    if mode == None:
        'OBJECT'

    override['active_object'] = active_object
    override['object'] = active_object
    if mode == 'EDIT_MESH':
        override['edit_object'] = active_object

    override['selected_objects'] = selected_objects
    override['objects_in_mode'] = selected_objects
    override['selected_editable_objects'] = selected_objects
    override['objects_in_mode_unique_data'] = selected_objects
    
    override['mode'] = mode

    return override


def restore_modifier_settings(context):

    pass
    # Get cloth modifiers
    cloth_mods = get_modifiers(context, 'CLOTH')

    for mod in cloth_mods:
        # Restore orig settings
        #mod.point_cache.frame_end = context.scene.BCB_props.orig_end_frame
        #mod.settings.quality = mod['orig_quality']

        # Delete custom properties
        #del mod['orig_frame_end']
        #del mod['orig_quality']
        pass

def add_default_vertex_groups_on_objects(context, objects):
    
    vtx_group_names = [PIN_GROUP_NAME, STIFFNESS_GROUP_NAME, 
        SHRINKING_GROUP_NAME, PRESSURE_GROUP_NAME]

    # Add vertex groups
    for object in objects:
        for vtx_group_name in vtx_group_names:
            if vertex_group_exists(context, object, vtx_group_name):
                continue
            object.vertex_groups.new(name = vtx_group_name)
            
            # Fill pressure weight
            if not vtx_group_name == PRESSURE_GROUP_NAME:
                continue
            verts = list(range(0,len(object.data.vertices)))
            object.vertex_groups[PRESSURE_GROUP_NAME].add(index = verts, weight = 1, type = 'REPLACE')

    


    # Setup vertex groups on existing cloth modifier
    for object in objects:
        cloth_mods = get_modifiers(context, 'CLOTH', objects = [object])
        cloth_mods[0].settings.vertex_group_bending = STIFFNESS_GROUP_NAME
        cloth_mods[0].settings.vertex_group_shrink = SHRINKING_GROUP_NAME
        cloth_mods[0].settings.vertex_group_mass = PIN_GROUP_NAME
        cloth_mods[0].settings.vertex_group_pressure = PRESSURE_GROUP_NAME


def vertex_group_exists(context, object, vtx_grp_name):
    for vtx_grp in object.vertex_groups:
        if vtx_grp.name == vtx_grp_name:
            return True

    return False

def get_vertex_group_names(context, objects):
    vtx_grp_names = []
    for object in objects:
        for vtx_grp in object.vertex_groups:
            if vtx_grp.name in vtx_grp_names:
                continue
            vtx_grp_names.append(vtx_grp.name)

    return vtx_grp_names

def register():
    pass