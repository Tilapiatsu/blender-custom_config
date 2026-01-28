from Tila_ConfigManager.config.keymaps.keymaps import TILA_Config_Keymaps_Base

addon_name = "atomic_data_manager"


class TILA_Config_Keymaps(TILA_Config_Keymaps_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        if self.kmi_init(
            name="Window",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            self.kmi_set_replace(
                "atomic.invoke_pie_menu_ui",
                "DEL",
                "PRESS",
                ctrl=True,
                shift=True,
                disable_double=True,
            )
