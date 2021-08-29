import bpy

def create_scene(context, scene_name = 'new scene'):
    bpy.ops.scene.new(type='EMPTY')
    context.window.scene.name = scene_name
    

def delete_scene(scene_name):
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
    
    try:
        # The row below has caused crashes for unknown reasons. Hard to recreate
        bpy.data.scenes.remove(scene)
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

classes = (

)