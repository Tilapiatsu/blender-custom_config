import bpy
import time
from . import high_res_objects_manager
from . import viewport_manager
from . import debug


from bpy.props import (
    IntProperty,
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
)

def debug_print_objects_in_collection(context, collection, extra_text = ""):
    '''
    Print all object in collection for debugging
    '''
    if not extra_text == "":
        extra_text = " - " + extra_text
    print("\n")
    print("debug_print_objects_in_collection" + extra_text)
    for object in collection.objects:
        print(object.name)
    print("\n")

def ensure_visibility_for_baking(context, collection):
    '''
    Make sure collection is visible for baking. Return original visibility
    as a dictionary, so that it can be restored later
    '''
    
    visibility_settings = {
        'hide_select': collection.hide_select,
        'hide_viewport': collection.hide_viewport,
        'hide_render': collection.hide_render,
        'view_layer_hide_viewport': context.view_layer.layer_collection.children[collection.name].hide_viewport,
        'exclude': context.view_layer.layer_collection.children[collection.name].exclude
    }

    collection.hide_select = False
    collection.hide_viewport = False
    collection.hide_render = False
    context.view_layer.layer_collection.children[collection.name].hide_viewport = False
    context.view_layer.layer_collection.children[collection.name].exclude = False

    return visibility_settings

def set_visibility(context, collection, visibility_settings):
    '''
    Set visibility settings of collection
    '''
    
    collection.hide_select = visibility_settings['hide_select']
    collection.hide_viewport = visibility_settings['hide_viewport']
    collection.hide_render = visibility_settings['hide_render']   
    context.view_layer.layer_collection.children[collection.name].hide_viewport = visibility_settings['view_layer_hide_viewport']
    context.view_layer.layer_collection.children[collection.name].exclude = visibility_settings['exclude']

def filter_objects_by_bake_collections(context, objects, collections):
    '''
    Return all objects that somehow is a child to any collection in "collections"
    '''
    filtered_objects = []

    for object in objects:
        bake_collections = get_bake_collections_by_object(context, object, context.scene) 

        for collection in collections:
            if collection in bake_collections:
                filtered_objects.append(object)

    return filtered_objects

def create_bake_collection(context, add_selected_objects = True):
    name = "Bake collection"
    i = 1
    base_name = "Bake collection"
    while not bpy.data.collections.get(name) == None:
        name = base_name + "." + str(i)
        i += 1
        if i > 100:
            break

    if add_selected_objects:
        bpy.ops.object.link_to_collection(collection_index=0, is_new=True, new_collection_name = name)
        # Remove objects from scene collection
        for object in context.selected_objects:
            try:
                context.scene.collection.objects.unlink(object)
            except:
                pass
        new_collection = bpy.data.collections[name]

    else:
        new_collection = bpy.data.collections.new(name = name)
        context.scene.collection.children.link(new_collection)
    
    new_collection['is_bake_collection'] = True
    new_collection.color_tag = 'COLOR_06'


def get_bake_collections_by_scene(scene):

    collections = get_all_collections_by_scene(scene)
    bake_collections = []

    for collection in collections:
        if collection.get('is_bake_collection') == True:
            bake_collections.append(collection)
            
    return bake_collections    

def get_scene_collections_by_object(context, object):
    '''
    Returns all collections in the current scene that the object 
    belongs to. Excludes scene.collection
    '''
    scene_collections = get_all_collections_by_scene(context.scene)
    object_collections = object.users_collection
    object_scene_collections = []
    
    # Check if objects collections exists in active scene
    for collection in object_collections:
        if collection in scene_collections:
            object_scene_collections.append(collection)

    if len(object_scene_collections) == 0:
        return None
    else:
        return object_scene_collections

def get_parent_collections_by_object(context, object, scene = None):
    '''
    Returns all parental collection to the object in the scene
    Context scene used if scene == None
    '''

    if scene == None:
        scene = context.scene

    try:
        object_collections = object.users_collection
        # Convert from tuple to list if needed
        if type(object_collections) == tuple:
            object_collections = list(object_collections)
    except:
        print("Could not set current_collection for " + str(object))
        return None
    
    
    
    scene_collections = get_all_collections_by_scene(scene)
    # Remove object collections that does not exist in scene
    for collection in object_collections.copy():
        if not collection in scene_collections:
            object_collections.remove(collection)
    

    return_collections = object_collections.copy()

    panic = 0
    for current_collection in object_collections: 
        all_parent_collections_checked = False

        # Loop until a top hierachy collection is found
        while (all_parent_collections_checked == False):

            '''
            panic += 1
            if panic > 50:
                break
            '''

            # If current collection is top hierarchy collection
            if current_collection in scene.collection.children.values():
                if not current_collection in return_collections:  
                    return_collections.append(current_collection)
                all_parent_collections_checked = True
                break
            

            # Check if collection is a parent collection to current_collection
            for collection in scene_collections:
                if current_collection in collection.children.values():
                    # Add collection if it is not already added
                    if not collection in return_collections:  
                        return_collections.append(collection)
                    current_collection = collection
                    break   
                    
    return return_collections

def get_bake_collections_by_objects(context, objects, scene = None):
    import time
    start_time = time.time()

    if scene == None:
        scene = context.scene

    bake_collections = []

    for object in objects:
        collections = get_parent_collections_by_object(context, object, scene)
        
        for collection in collections:
            if collection.get('is_bake_collection') == True and collection not in bake_collections:
                bake_collections.append(collection)
        

    return bake_collections


def get_bake_collections_by_object(context, object, scene = None):

    if scene == None:
        scene = context.scene

    collections = get_parent_collections_by_object(context, object, scene)

    if collections == None:
        print("no collections found")
        return None

    bake_collections = []

    for collection in collections:

        if collection.get('is_bake_collection') == True:
            bake_collections.append(collection)
            
    return bake_collections

def get_all_collections_by_scene(scene):
    '''
    Return all collections in scene
    '''
    '''
    collections_to_process = []
    #top_hierarchy_collections = scene.collection.children.values
    for collection in scene.collection.children.values:
        collections_to_process.append(collection)
    '''
    collections_to_process = scene.collection.children.values()
    collections_in_scene = []
    while len(collections_to_process) > 0:
        collection = collections_to_process[0]

        if collection in collections_in_scene:
            continue

        collections_in_scene.append(collection)
        collections_to_process.remove(collection)
        for child in collection.children:
            collections_to_process.append(child)

    return collections_in_scene

def get_all_collections_by_view_layer(view_layer):
    '''
    Return all collections in view layer as type "layer collection"
    '''
    view_layer_collections = []
    collections_to_process = view_layer.layer_collection.children.values()

    while len(collections_to_process) > 0:
        view_layer_collections.append(collections_to_process[0])
        children = collections_to_process[0].children.values()
        collections_to_process = collections_to_process + children
        collections_to_process.remove(collections_to_process[0])

    return view_layer_collections

def get_collection_visibility_settings(context, scene = None):
    '''
    Return a dictionary with visibility settings for all collections in scene.
    This can later be used to reset visibility settings if it is changed
    during baking.

    dictionary format example:
    key: "1 hide render"
    value (list): [collection, collection.hide_render] 
    '''

    if scene == None:
        scene = context.scene    

    #scene_collections = get_all_collections_by_scene(scene)

    visibility_settings = {}
    
    # Create dictionary items for hide_render
    for index, collection in enumerate(get_all_collections_by_scene(scene)):
        visibility_settings[str(index) + ' hide_render'] = [collection, collection.hide_render]
    # Create dictionary items for hide_viewport
    for index, collection in enumerate(get_all_collections_by_view_layer(context.view_layer)):
        visibility_settings[str(index) + ' hide_viewport'] = [collection, collection.hide_viewport]

    return visibility_settings

def set_collection_visibility_settings(visibility_settings):
    '''
    Sets the render visibility of collections in visibility_settings
    '''
    for key, value in visibility_settings.items():
        if key.find('render') >= 0:
            value[0].hide_render = value[1]
        elif key.find('viewport') >= 0:
            value[0].hide_viewport = value[1]

def set_bake_collection(collection, is_bake_collection):
    
    if is_bake_collection == True:
        collection['is_bake_collection'] = True
    else:
        del collection['is_bake_collection']


class COLLECTION_OT_create_bake_collection(bpy.types.Operator):
    '''
    Create a collection that is defined as a bake collection. 
    Low poly objects that should be baked needs to belong to a bake collection.
    Objects in the collection must share 0-1 uv space
    '''
    bl_idname = "collection.create_bake_collection"
    bl_label = "Create bake collection"
    
    add_selected_objects: BoolProperty(
        name="Add selected objects",
        description="Add selected objects",
        default=True, 
    )       



    def execute(self, context):   
        if viewport_manager.get_local_view(context):
            message = "Can't create bake collection in local view"
            self.report({'ERROR'}, message)
        else:
            create_bake_collection(context, self.add_selected_objects)
    
        return {'FINISHED'}    

class COLLECTION_OT_set_bake_collection(bpy.types.Operator):
    '''
    Set if the collection should be a bake collection or not
    '''
    bl_idname = "collection.set_bake_collection"
    bl_label = "Set bake collection"
    
    is_bake_collection: BoolProperty(
        name="Is bake collection",
        description="Is bake collection",
        default=True, 
    )     
    collection_name: StringProperty(
        name = "Collection name"
    )  

    def execute(self, context):   
        collection = self.collection_name
        set_bake_collection(collection, self.is_bake_collection)
        return {'FINISHED'}    

class COLLECTION_OT_delete_collection(bpy.types.Operator):
    '''
    Delete bake collection
    '''
    bl_idname = "collection.delete_collection_by_name"
    bl_label = "Delete"
     
    collection_name: StringProperty(
        name = "Collection name"
    )  

    def execute(self, context):   
        collection = bpy.data.collections[self.collection_name]
        
        # Put the object in the scene collection unless it is existing in another
        # collection in the scene
        for object in collection.all_objects:
            object_collections = get_scene_collections_by_object(context, object)
            if len(object_collections) > 1:
                continue
            try:
                context.scene.collection.objects.link(object)
            except:
                pass
        bpy.data.collections.remove(collection)
        return {'FINISHED'}    


classes = (
    COLLECTION_OT_create_bake_collection,
    COLLECTION_OT_set_bake_collection,
    COLLECTION_OT_delete_collection

)

def register():
    for clas in classes:
        bpy.utils.register_class(clas)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)