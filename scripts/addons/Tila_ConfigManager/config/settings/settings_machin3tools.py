import bpy
from Tila_ConfigManager.config.settings.settings import TILA_Config_Settings_Base

addon_name = "MACHIN3tools"


class TILA_Config_Settings(TILA_Config_Settings_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Settings_Base.print_log()
    def set_settings(self):
        context = bpy.context
        addon = context.preferences.addons.get(self.addon_name)

        self.set_setting(addon, "activate_smart_vert", False)
        self.set_setting(addon, "activate_smart_edge", False)
        self.set_setting(addon, "activate_smart_face", False)
        self.set_setting(addon, "activate_focus", False)
        self.set_setting(addon, "activate_mirror", True)
        self.set_setting(addon, "activate_modes_pie", False)
        self.set_setting(addon, "activate_views_pie", False)
        self.set_setting(addon, "activate_transform_pie", False)
        self.set_setting(addon, "activate_collections_pie", False)
        self.set_setting(addon, "activate_align", True)
        self.set_setting(addon, "activate_filebrowser_tools", True)
        self.set_setting(addon, "activate_extrude", True)
        self.set_setting(addon, "activate_clean_up", True)
        self.set_setting(addon, "activate_edge_constraint", True)
        self.set_setting(addon, "activate_surface_slide", True)
        self.set_setting(addon, "activate_group_tools", False)
        self.set_setting(addon, "activate_mesh_cut", True)
        self.set_setting(addon, "activate_thread", True)
        self.set_setting(addon, "activate_material_picker", True)
        self.set_setting(addon, "activate_save_pie", True)
        self.set_setting(addon, "activate_align_pie", True)
        self.set_setting(addon, "activate_cursor_pie", True)

