from .keymaps import TILA_Config_Keymaps_Base

addon_name = "bl_ext.blender_org.Non_Destructive_Primitives"

class TILA_Config_Keymaps(TILA_Config_Keymaps_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        if self.kmi_init(name='Object Mode', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
            self.kmi_set_active(False, idname='wm.call_menu_pie', type='A', shift=True, properties={'name':'ND_PRIMITIVES_MT_add_objects_pie_menu'})
