import bpy

def create_scene(context, scene_name = 'new scene', delete_after_bake = True):
    bpy.ops.scene.new(type='EMPTY')
    context.window.scene.name = scene_name

    # For some reason, deleting a scene when a function is run within a timer
    # it seems that blender can sometimes crash. I'll solve this by cleaning up after
    # all baking is done
    if delete_after_bake:
        bpy.data.scenes[scene_name]['delete_after_bake'] = True
    
def remove_temporary_scenes_after_bake(context):
    # For some reason, deleting a scene when a function is run within a timer
    # it seems that blender can sometimes crash. I'll solve this by cleaning up after
    # all baking is done    

    for scene in bpy.data.scenes:
        if scene.get("delete_after_bake"):
            #bpy.data.scenes.remove(scene)    
            delete_scene(context, scene.name)

def delete_scene(context, scene_name):
    # Removes the scene from the blender file
    # and also it's active camera unless the camera 
    # is used in other scenes as well

    # TODO: Unclear why I used a string as parameter and not
    # the scene data. I shuold look into this later

    
    scene = bpy.data.scenes[scene_name]
    
    # Return if scene does not exist
    if not scene in bpy.data.scenes.values():
        return

    # Remove the active camera in the scene
    cam = scene.camera
    if not cam == None:
        if cam.users < 2:
            bpy.data.cameras.remove(cam.data)

    # DEBUG      
    print("current scene is " + context.scene.name)
    print("repr(scene) = " + repr(scene))
    if scene in bpy.data.scenes.values():
        print("scene to be deleted exists")
    else:
        print("scene to be deleted does not exist")
    # END DEBUG

    try:
        # DEBUG
        if scene in bpy.data.scenes.values():
            print("scene to be deleted exists")
        else:
            print("scene to be deleted does not exist")
        # END DEBUG
        
        # The row below has caused crashes for unknown reasons. Hard to recreate
        bpy.data.scenes.remove(scene) # temp disabled
    except:
        print("Could not delete scene with name " + scene_name)

def open_scene(context, scene_name):
    # TODO: Unclear why I used a string as parameter and not
    # the scene data. I should look into this later
    try:
        # Wrapping this in a try block, since I got a crash on this line at one point
        context.window.scene = bpy.data.scenes[scene_name]
    except:
        pass

class SCENE_OT_delete_temporary_bake_scenes(bpy.types.Operator):
    '''
    Delete temporary bake scenes
    '''
    bl_idname = "scene.delete_temporary_bake_scenes"
    bl_label = "Delete temporary bake scenes"
    bl_description = "Delete temporary bake scenes that are created under the hood during baking"
    

    def execute(self, context):   
        remove_temporary_scenes_after_bake(context)
        return {'FINISHED'}  

classes = (
    SCENE_OT_delete_temporary_bake_scenes,
)

def register():
    for clas in classes:    
        print("\n #### registered this cool class" + repr(clas))
        bpy.utils.register_class(clas)

def unregister():
    for clas in classes:
        bpy.utils.unregister_class(clas)