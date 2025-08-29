import bpy
import functools
from ...preferences.ui.log_list import TILA_Config_Log as log_list

# https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

class TILA_Config_Settings_Base:
    addon_name = 'NONE'

    def __init__(self):
        self.log_progress = log_list(bpy.context.window_manager.tila_config_log_list, 'tila_config_log_list_idx')

    def print_log(test_addon_exists=True):
        def decorator(func):
            def wrapper(self):
                if test_addon_exists:
                    if self.addon_name not in bpy.context.preferences.addons:
                        self.log_progress.start(f'Addon {self.addon_name} is not enable: skipping')
                        return

                self.log_progress.start(f'Applying {self.addon_name} Settings')
                func(self)
                self.log_progress.done(f'{self.addon_name} Settings Applied')

            return wrapper
        return decorator

    def set_setting(self, setting_root:bpy.types.bpy_struct, setting_name:str, value):
        if rgetattr(setting_root.preferences, setting_name, None) is None:
            self.log_progress.error(f'Setting "{setting_name}" not found in {self.addon_name} addon')
            return
        if rgetattr(setting_root.preferences, setting_name) == value:
            return

        self.log_progress.info(f'{self.addon_name} : Set {setting_name} = {value}')
        rsetattr(setting_root.preferences, setting_name, value)

