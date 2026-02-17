import bpy
from Tila_ConfigManager.config.settings.settings import TILA_Config_Settings_Base

addon_name = "bl_ext.blender_org.collection_manager"


class TILA_Config_Settings(TILA_Config_Settings_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Settings_Base.print_log()
    def set_settings(self):
        context = bpy.context
        addon = context.preferences.addons.get(self.addon_name)
        self.set_setting(addon, "enable_qcd", False)
        self.set_setting(addon, "enable_qcd_3dview_header_widget", False)

