from pathlib import Path

#https://www.pythonmorsels.com/dynamically-importing-modules/
def get_module_members(module_root:Path, file_prefix:str, separator:str='_') -> dict:
    import importlib.util
    import sys
    def import_from_path(module_name: str, file_path: Path):
        """Import a module given its name and file path."""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    members = [f for f in module_root.glob('*.py') if f.stem.startswith(file_prefix) and separator in f.stem]
    module_path = Path(str(module_root).split(__package__)[0])

    members_dict = {}

    for m in members:
        module_relative_path = Path(str(m).replace(str(module_path), ''))
        module_relative_name = str(module_relative_path).replace('\\', r'.')[1:-3]

        module = import_from_path(module_relative_name, m)

        members_dict[module.addon_name] = module

    return members_dict

