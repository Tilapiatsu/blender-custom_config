from Tila_ConfigManager.config.keymaps.keymaps import TILA_Config_Keymaps_Base

addon_name = "node_booster"


class TILA_Config_Keymaps(TILA_Config_Keymaps_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        self.kmi_init(
            name="Node Editor",
            space_type="NODE_EDITOR",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        )
        self.kmi_set_replace(
            "nodebooster.draw_route", "E", "PRESS", disable_double=True
        )
        self.kmi_set_replace("nodebooster.chamfer", "B", "PRESS", disable_double=True)
        self.kmi_set_replace("nodebooster.draw_frame", "J", "PRESS")
        # self.kmi_set_replace('nodebooster.dependency_select', self.k_manip, 'DOUBLE_CLICK', shift=True, properties={'mode': "downstream", 'repsel': True}, disable_double=True)
        # self.kmi_set_replace('nodebooster.dependency_select', self.k_manip, 'DOUBLE_CLICK', ctrl=True, properties={'mode': "upstream", 'repsel': True}, disable_double=True)
