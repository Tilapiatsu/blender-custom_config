from . import preferences, ui, operators

def register():
    ui.register()
    operators.register()
    preferences.register()

def unregister():
    preferences.unregister()
    operators.unregister()
    ui.unregister()