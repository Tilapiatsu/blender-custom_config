from . import addon_list, log_list

def register():
    addon_list.register()
    log_list.register()

def unregister():
    log_list.unregister()
    addon_list.unregister()