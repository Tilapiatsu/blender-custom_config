import bpy
from . import custom_properties
from . import debug
from . import object_manager
from . import UI
from . import collection_manager
from . import high_res_objects_manager

import copy


class OBJECT_OT_add_selected_objects_as_high_res_object_to_active_object_in_UI(bpy.types.Operator):
    
    bl_idname = 'object.add_selected_objects_to_high_res_on_active'
    bl_label = 'Add selected objects as high res object connected to object'
    bl_description = 'Add selected objects as high res object connected to object'

    def execute(self, context):
        self.report({'INFO'}, 'Init add objects to high res.')
        active_object_in_UI = UI.get_active_object_from_UI(context)
        message = add_selected_objects_as_high_res_object_to_active_object_in_UI(context)
        cleanup_high_res_object_slots(context, [active_object_in_UI])
        
        if not message == "":
            self.report({'ERROR'}, message)

        return {'FINISHED'}

class OBJECT_OT_remove_selected_objects_as_high_res_object_to_active_object_in_UI(bpy.types.Operator):
    
    bl_idname = 'object.remove_selected_objects_from_high_res_on_active'
    bl_label = 'Remove selected objects from high res object connected to object'
    bl_description = 'Remove selected objects from high res object connected to object'
    
    def execute(self, context):
        self.report({'INFO'}, 'Init remove objects from high res.')

        active_object_in_UI = UI.get_active_object_from_UI(context)
        remove_high_res_objects_from_object(context, context.selected_objects, [active_object_in_UI])
        cleanup_high_res_object_slots(context, [active_object_in_UI])
        
        return {'FINISHED'}

class OBJECT_OT_clear_high_res_object_from_selected_objects(bpy.types.Operator):
    
    bl_idname = 'object.clear_high_res_objects_from_selected'
    bl_label = 'Remove high res object connections to selected objects'
    bl_description = 'Remove high res object connections to selected objects'


    @classmethod
    def poll(cls, context):
        UI_object = UI.get_active_object_from_UI(context)
        return len(UI_object.high_res_objects) > 0


    def execute(self, context):

        objects = context.selected_objects

        active_object_from_UI = UI.get_active_object_from_UI(context)
        
        if not active_object_from_UI in objects:
            objects.append(active_object_from_UI)
        
        for object in objects:
            object.high_res_objects.clear()

        return {'FINISHED'}

class OBJECT_OT_add_high_res_object_slot(bpy.types.Operator):
    
    bl_idname = 'object.add_high_res_object_slot'
    bl_label = 'Add high res object slot to active object'
    bl_description = 'Add slot for high res object'
    
    def execute(self, context):

        active_object_from_UI = UI.get_active_object_from_UI(context)
        
        active_object_from_UI.high_res_objects.add()


        return {'FINISHED'}

class OBJECT_OT_remove_empty_high_res_object_slots(bpy.types.Operator):
    
    bl_idname = 'object.remove_empty_high_res_object_slots'
    bl_label = 'Remove empty high res object slots'
    bl_description = 'Remove empty high res object slots'

    def execute(self, context):
        
        active_object_from_UI = UI.get_active_object_from_UI(context)
        cleanup_high_res_object_slots(context, [active_object_from_UI])

        return {'FINISHED'}

class OBJECT_OT_select_high_res_objects(bpy.types.Operator):
    '''
    Deselects all objects and select high res object that is
    connected to selected objects
    '''
    bl_idname = "object.select_high_res_objects"
    bl_label = 'Select high res objects'
    bl_description = "Deselects all objects and select high res object that is connected to selected objects"

    @classmethod
    def poll(cls, context):
        UI_object = UI.get_active_object_from_UI(context)
        return high_res_objects_manager.high_res_exists(context, UI_object)

    def execute(self, context):
        select_high_res_objects(context, 'REPLACE')
        return {'FINISHED'}

class OBJECT_OT_link_high_res_objects_to_scene(bpy.types.Operator):
    bl_idname = "object.link_high_res_objects_to_scene"
    bl_label = "Link high res objects to scene"
    bl_description = "Link high res objects to scene"

    def execute(self, context):
        link_high_res_objects_to_scene(context)
        return {'FINISHED'}


def add_selected_objects_as_high_res_object_to_active_object_in_UI(context):
    '''
    Connect selected objects to UI's active object as high res objects
    '''
    target_object = UI.get_active_object_from_UI(context)
    message = ""

    for object in context.selected_objects:
        if object == target_object:
            continue
        if not object_manager.can_be_bakable_high_res_object(object):
            if message == "":
                message = "Was not able to add the following object(s), since it's not bakeable: "
            message = message + object.name + ", "
            continue
        else:
            add_high_res_objects_to_objects(context, [object], [target_object])

    return message
        
def add_high_res_objects_to_objects(context, high_res_objects, objects):
    '''
    Connect high_res_objects to objects
    Checks if the high res object is the same object as object or
    if it is already connected before connecting
    '''
    for object in objects:
        connected_high_res_objects = get_high_res_objects(context, object)
        for high_res_object in high_res_objects:
            
            if high_res_object in connected_high_res_objects:
                continue
            if high_res_object == object:
                continue

            prop = object.high_res_objects.add()
            prop.high_res_object = high_res_object

def remove_high_res_objects_from_object(context, high_res_objects_to_remove, objects):
    '''
    Remove connection to high res objects on each object in objects
    '''
    for object in objects:
        for high_res_object_prop in object.high_res_objects:
            high_res_object = high_res_object_prop.high_res_object
            if high_res_object in high_res_objects_to_remove:
                high_res_object_prop.high_res_object = None


def select_high_res_objects(context, select_action):
    '''
    Get high res objects from selected objects and select them
    select_action can be "ADD" or "REPLACE"
    Only 'MESH' type objects will be selected
    '''
    active_object = UI.get_active_object_from_UI(context)
    high_res_objects = get_high_res_objects(context, active_object)
    if select_action == 'REPLACE':
        bpy.ops.object.select_all(action='DESELECT')
    
    high_res_objects = object_manager.filter_objects_by_type(high_res_objects, ['MESH', 'META', 'CURVE', 'FONT', 'SURFACE'])
    object_manager.select_objects(context, 'ADD', high_res_objects)

def link_high_res_objects_to_scene(context):
    '''
    Collect all high res objects that are connected to selected objects
    link the high res objects into the current scene if they don't exist 
    in the current scene
    '''
    obj_missing_in_scene = get_high_res_objects_missing_in_scene(context, context.selected_objects)

    for obj in obj_missing_in_scene:
        context.collection.objects.link(obj)

def remove_high_res(context, object):
    '''
    Remove the high res objects connected to object
    NEW FIXED!
    '''
    object.high_res_objects.clear()

def high_res_exists(context, object):
    '''
    Returns True if high res exists
    NEW FIXED!
    '''
    high_res_objects = get_high_res_objects(context, object)
    return len(high_res_objects) > 0

def high_res_is_empty(context, object):
    '''
    Returns True if high res does not exist or has no data
    NEW FIXED!
    '''
    high_res_objects = get_high_res_objects(context, object)
    return len(high_res_objects) == 0



def get_objects_with_high_res_objects(context):
    '''
    Returns a list with all objects in the blender file that is connected
    to high res objects

    Rename this later to get_objects_with_high_res_objects
    NEW FIXED!
    '''
    objects_with_high_res_objects = []

    for object in bpy.data.objects.values():
        if len(object.high_res_objects) > 0:
             objects_with_high_res_objects.append(object)

    return objects_with_high_res_objects



def get_high_res_objects(context, objects):
    '''
    returns a list with all high res objects connected to objects
    NEW FIXED!
    '''
    # Ensure objects can be iterated
    if not type(objects) == list:
        objects = [objects]

    high_res_object_list = []
    
    for object in objects:
        for hi_res_object_prop in object.high_res_objects:
            high_res_object = hi_res_object_prop.high_res_object
            if high_res_object and not high_res_object in high_res_object_list:
                high_res_object_list.append(high_res_object)

    return high_res_object_list

def purge_objects_without_scene_user(context, objects):
    '''
    Completely remove objects that is not used in any scene
    Return filtered list with objects that exists in a scene
    NEW FIXED!
    '''

    # Ensure objects can be iterated
    if not type(objects) == list:
        objects = [objects]

    objects_used_in_a_scene = []

    for object in objects:

        # Continue if high_res_objects is returned as an empty array etc
        if not type(object) is bpy.types.Object:
            continue

        # If object exist in a scene
        if not str(object) == '<bpy_struct, Object invalid>' and not len(object.users_scene) == 0:
            objects_used_in_a_scene.append(object)
        else:
            try:
                bpy.data.objects.remove(object)
            except:
                print("Could not delete object " + str(object))    

    return objects_used_in_a_scene


def get_high_res_objects_missing_in_scene(context, objects):
    '''
    Collects high res objects from selected objects. 
    Returns a list with missing bake objects in the active scene
    NEW FIXED!
    '''
    high_res_objects = get_high_res_objects(context, objects)
    objects_missing_in_scene = []
    for object in high_res_objects:
        if not object in context.scene.objects.values():
            objects_missing_in_scene.append(object)
    
    return objects_missing_in_scene

def ensure_render_visiblity_on_high_res_collections(context, objects):
    '''
    Make all high res objects collections visible in render
    '''
    high_res_objs = get_high_res_objects(context, objects)
    high_res_collection_names = [] # I need to use names, since I cant compare bpy.data.collection with view layer collections

   
    # Collect high res collection names
    for object in high_res_objs:
        collections = collection_manager.get_parent_collections_by_object(context, object)
       
       # If an object does not return any collections - continue
        if not collections:
            continue

        for collection in collections:
            if not collection.name in high_res_collection_names:
                high_res_collection_names.append(collection.name)


    # Set hide render if they are a high res collections
    for collection in bpy.data.collections:
        if collection.name in high_res_collection_names:
            collection.hide_render = False 
    
    # collect collections in view layer
    view_layer_collections = collection_manager.get_all_collections_by_view_layer(context.view_layer)

    # Set hide viewport for collection if they are a high res collection
    for collection in view_layer_collections:
        if collection.name in high_res_collection_names:
            #collection.hide_render = False   # TODO: generates error. Don't remember why this was added. Save for now
            collection.hide_viewport = False 

class OBJECT_OT_find_hipoly_by_bounding_box(bpy.types.Operator):
    '''
    Find matching hipoly objects based on each selected objects bounding box. 
    Filter objects per scene
    
    '''
 
    bl_idname = "object.find_hipoly_by_bounding_box"
    bl_label = "Find highpoly by bounding box"
    bl_description = "Find matching hipoly objects based on each selected objects bounding box."


    source_scene: bpy.props.StringProperty(
        name = "Source scene",
        description = "The scene where to look for high poly objects",
        default = "All scenes",
    )
    space: bpy.props.StringProperty(
        name = "Space",
        description = "Match bounding box in WORLD or OBJECT space",
        default = "WORLD"
    )



    def execute(self, context):
        '''
        This function is using 
        get_closest_to_object_bounding_box 
        in
        object_manager.py
        '''
        from . import object_manager
        source_objects = context.selected_objects
        scene_objects = []
        compare_objects = []
        info_text = []

        # Get initial list of objects
        if self.source_scene == "All scenes":
            scene_objects = bpy.data.objects
        else:
            scene_objects = bpy.data.scenes[self.source_scene].objects

        # Don't include source_objects in compare_objects
        for object in scene_objects: 
            if object not in source_objects:
                compare_objects.append(object)

        # Find matching high poly objects
        for object in source_objects:
            match_object = object_manager.get_closest_to_object_bounding_box(object, compare_objects, self.space)
            remove_high_res(context, object)
            add_high_res_objects_to_objects(context, [match_object], [object])
            info_text.append( "Connected " + match_object.name + " to " + object.name)
        
        # Give feedback to user
        self.report({'INFO'}, "Connected " + str(len(info_text)) + " high res objects")

        return {'FINISHED'}

def has_free_high_res_object_slot(context, object):
    '''
    returns True if object has free high res object slot
    '''
    has_free_slot = False

    for high_res_object_prop in object.high_res_objects:
        if high_res_object_prop.high_res_object == None:
            has_free_slot = True
            break
    
    return has_free_slot

def cleanup_high_res_object_slots(context, objects):
    '''
    Removes empty "slots" in the high res object collection 
    property on each object in objects
    '''
    for object in objects:
        if has_free_high_res_object_slot(context, object):
            high_res_objects = get_high_res_objects(context, object)
            object.high_res_objects.clear()
            add_high_res_objects_to_objects(context, high_res_objects, [object])
        

def on_high_res_object_pointer_property_update(self, context):
    '''
    Runs after high res object pointer property has been updated
    with picker etc in the UI.
    Watch out for infinite recursion!
    
    Note to self: hard to solve double instances of objects in the properties.
    It's also not a big issue 
    '''
    object = self.id_data
    #high_res_objects_not_to_add = get_high_res_objects(context, object)
    #high_res_objects_not_to_add.append(object)

    for high_res_object_prop in object.high_res_objects:
        
        high_res_object = high_res_object_prop.high_res_object
        
        if high_res_object == None:
            continue

        if high_res_object == object:
            high_res_object_prop.high_res_object = None
        elif not object_manager.can_be_bakable_high_res_object(high_res_object):
            high_res_object_prop.high_res_object = None
    


class HighResObject(bpy.types.PropertyGroup):
    kewl_name: bpy.props.StringProperty(name="Cool Name", default="Unknown")
    high_res_object: bpy.props.PointerProperty(name = "High res object", type=bpy.types.Object, update = on_high_res_object_pointer_property_update) 

classes = (
    OBJECT_OT_add_selected_objects_as_high_res_object_to_active_object_in_UI,
    OBJECT_OT_remove_selected_objects_as_high_res_object_to_active_object_in_UI,
    OBJECT_OT_add_high_res_object_slot,
    OBJECT_OT_remove_empty_high_res_object_slots,
    OBJECT_OT_clear_high_res_object_from_selected_objects,
    OBJECT_OT_select_high_res_objects,
    OBJECT_OT_link_high_res_objects_to_scene,
    OBJECT_OT_find_hipoly_by_bounding_box,
    HighResObject

)

def register():
    for clas in classes:
        bpy.utils.register_class(clas)
    
    bpy.types.Object.high_res_objects = bpy.props.CollectionProperty(type=HighResObject)
    bpy.types.Object.active_high_res_object = bpy.props.IntProperty(name = "Active high res object", default = 0)


def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)
    
    del bpy.types.Object.high_res_objects
    del bpy.types.Object.active_high_res_object
