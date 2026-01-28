import bpy
from Tila_ConfigManager.config.settings.settings import TILA_Config_Settings_Base

addon_name = "cycles"


class TILA_Config_Settings(TILA_Config_Settings_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @TILA_Config_Settings_Base.print_log()
    def set_settings(self):
        context = bpy.context

        addon = context.preferences.addons.get(self.addon_name)
        self.set_setting(addon, "compute_device_type", "OPTIX")
