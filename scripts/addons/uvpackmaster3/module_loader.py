import importlib
import sys
import os


def unload_uvpm3_modules(_locals=None):
    if _locals is None:
        _locals = locals()
    if "bpy" not in _locals:
        return False

    loaded_modules_names = list(sys.modules.keys())
    for module_name in loaded_modules_names:
        if module_name.startswith("{}.".format(__package__)):
            del sys.modules[module_name]
    return True


def registrable_classes(module, sub_class, required_vars):
    for member_name in dir(module):
        member = getattr(module, member_name)
        if isinstance(member, type) and member.__module__ == module.__name__ and all(True if v in member.__dict__ else False for v in required_vars):
            if sub_class is not None and not issubclass(member, sub_class):
                continue
            yield member


def get_registrable_classes(modules, sub_class=None, required_vars=("bl_idname",)):
    classes = []
    for module in modules:
        classes.extend(registrable_classes(module, sub_class=sub_class, required_vars=required_vars))
    return classes


def import_submodules(module):
    submodules = []
    if hasattr(module.__path__, "_path"):
        module_path = module.__path__._path[0]
    else:
        module_path = module.__path__[0]

    for file in os.listdir(module_path):
        file_parts = file.split(".")
        if len(file_parts) == 2 and file_parts[1] == "py":
            submodule = importlib.import_module("{}.{}".format(module.__name__, file_parts[0]))
            submodules.append(submodule)
    return submodules

