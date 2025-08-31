from . import uv


bl_info = {
    'name': "gret Relax UV Loop",
    'author': "greisane",
    'description': "Collection of Blender tools",
    'version': (1, 4, 0),
    'blender': (4, 0, 1),
    'location': "3D View > Tools",
    'category': "Object",
    'doc_url': "https://github.com/greisane/gret#readme",
    'tracker_url': "https://github.com/greisane/gret/issues",
}


modules = (uv,)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()