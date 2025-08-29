from .keymaps import TILA_Config_Keymaps_Base

addon_name = "Poly_Source"

class TILA_Config_Keymaps(TILA_Config_Keymaps_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        if self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW', addon=False, restore_to_default=False):
            self.kmi_set_active(enable=False, idname='wm.call_menu_pie', type=self.k_menu, value='PRESS', properties={'name': 'PS_MT_tk_menu'})
