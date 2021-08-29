import bpy

def get_image_by_bake_type(bake_type, bake_collection):
    '''
    Returns the first image that matches bake_type and 
    bake_collection.name
    '''
    for image in bpy.data.images:
                
        if (image.get('bake_type') == bake_type and 
            image.get('image_folder') == bake_collection.name):
            return image

    return None