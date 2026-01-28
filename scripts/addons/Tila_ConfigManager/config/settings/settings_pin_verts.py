import bpy
from Tila_ConfigManager.config.settings.settings import TILA_Config_Settings_Base

addon_name = "pin_verts"


class TILA_Config_Settings(TILA_Config_Settings_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Settings_Base.print_log()
    def set_settings(self):
        context = bpy.context
        addon = context.preferences.addons.get(self.addon_name)
        self.set_setting(addon, "sna_auto_enabledisable_falloff", False)
        self.set_setting(addon, "sna_show_header_button_editmode", False)

