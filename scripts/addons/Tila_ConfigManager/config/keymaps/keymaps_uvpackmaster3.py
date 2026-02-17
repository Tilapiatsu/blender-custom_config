from Tila_ConfigManager.config.keymaps.keymaps import TILA_Config_Keymaps_Base

addon_name = "uvpackmaster3"


class TILA_Config_Keymaps(TILA_Config_Keymaps_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        if self.kmi_init(
            name="UV Editor",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            self.kmi_set_replace(
                "uvpackmaster3.pack", "P", "PRESS", ctrl=True, disable_double=True
            )
