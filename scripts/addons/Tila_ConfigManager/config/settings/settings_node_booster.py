import bpy
from .settings import TILA_Config_Settings_Base

addon_name = 'node_booster'
class TILA_Config_Settings(TILA_Config_Settings_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Settings_Base.print_log()
    def set_settings(self):
        kmi = bpy.context.window_manager.keyconfigs.addon.keymaps['Node Editor'].keymap_items
        for k in kmi:
            if k.idname == 'noodler.draw_route':
                k.type = 'E'
            if k.idname == 'noodler.chamfer':
                k.ctrl = False
            if k.idname == 'noodler.draw_frame':
                k.ctrl = True