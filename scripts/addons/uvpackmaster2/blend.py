
inside_blender = True

try:
    import bpy
except:
    inside_blender = False


def get_prefs():
    return bpy.context.preferences.addons['uvpackmaster2'].preferences

def is_blender28():
    return True

def get_release_suffix():
    return 'blend2.8'