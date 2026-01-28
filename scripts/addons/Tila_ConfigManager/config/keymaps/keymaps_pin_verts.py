from Tila_ConfigManager.config.keymaps.keymaps import TILA_Config_Keymaps_Base

addon_name = "pin_verts"


class TILA_Config_Keymaps(TILA_Config_Keymaps_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        if self.kmi_init(
            name="Mesh",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            self.kmi_set_replace(
                "mesh.pin_unselected",
                "P",
                "PRESS",
                ctrl=True,
                alt=True,
                shift=True,
                disable_double=True,
            )
