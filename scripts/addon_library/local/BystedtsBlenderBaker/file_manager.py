import bpy
import platform
import os

def open_folder(context, path):
    os_platform = platform.system()
    path = bpy.path.abspath(path)
    
    if os_platform == 'Windows':
        os.startfile(path)
        
    elif os_platform == 'Linux':
        os.system('xdg-open "%s"' % path)

    # If mac
    elif os_platform == 'Darwin':
        os.system('open "%s"' % path)


def open_bake_collection_folder(context, collection_name):
    path = context.scene.BBB_props.dir_path + collection_name + "/"
    open_folder(context, path)
    