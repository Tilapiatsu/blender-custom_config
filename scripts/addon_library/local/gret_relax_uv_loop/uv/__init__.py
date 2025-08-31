from . import relax_uv_loop

modules = (relax_uv_loop,)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()