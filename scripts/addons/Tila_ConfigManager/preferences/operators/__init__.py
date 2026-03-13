from . import log_file, open_folder


def register():
    log_file.register()
    open_folder.register()


def unregister():
    log_file.unregister()
    open_folder.unregister()

