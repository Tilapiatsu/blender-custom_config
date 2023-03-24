import bpy
from . import object_manager
from . import operator_manager

def UV_pack_selected_per_collection():
    '''
    Get scene collections from selected \n
    Select all objects in collections \n
    UV pack objects per collection
    '''   

    object_collections = get_collections_from_selected(context)
    UV_layout_per_collection(context, object_collections)

def get_collections_from_selected(context):
    '''
    Return list with the collections that the selected objects belong in the current scene
    '''
    return_collections = []
    scene_collections = context.scene.collection.children.values()

    for object in context.selected_objects:
        object_collections = context.object.users_collection
        
        for collection in reversed(object_collections): #use reversed to get collection order from top in outliner
            if collection in scene_collections:
                if not collection in return_collections:
                    return_collections.append(collection)
    
    return return_collections


def UV_layout_per_collection(context, collection_list):
    '''
    select all objects per collection in collection_list and do UV layout per collection
    '''
    orig_selection = context.selected_objects

    for collection in collection_list:
        collection_objects = collection.all_objects.values()
        object_manager.select_objects(context, 'REPLACE',collection_objects, set_first_as_active=True)
        UV_pack_selected(context)
        bpy.ops.object.select_all(action='DESELECT')

    object_manager.select_objects(context, 'REPLACE', orig_selection, True)

def UV_pack_selected(context):
    '''
    UV pack selected objects
    '''
    # Original settings
    orig_ui_type = context.area.ui_type
    orig_mode = context.mode

    context.area.ui_type = 'VIEW_3D'

    if context.mode == 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT') #error - wrong context
    
    bpy.ops.mesh.select_all(action = 'SELECT')
    
    context.area.ui_type = 'UV'
    bpy.ops.uv.select_all(action='SELECT')
    # TODO: Perhaps figure out margin from resolution
    
    '''
    # THis does not work due to some context issue with uv packmaster
    if operator_manager.operator_exists("uvpackmaster2.uv_pack"):
        bpy.ops.uvpackmaster2.uv_pack()
    else:
        bpy.ops.uv.pack_islands(margin=0.001)
    '''
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(margin=0.01)

    # Restore original settings
    context.area.ui_type = orig_ui_type
    bpy.ops.object.mode_set(mode=orig_mode) 






