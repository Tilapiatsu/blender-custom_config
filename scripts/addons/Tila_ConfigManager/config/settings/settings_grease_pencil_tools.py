import bpy
from .settings import TILA_Config_Settings_Base


addon_name = 'bl_ext.blender_org.grease_pencil_tools'
class TILA_Config_Settings(TILA_Config_Settings_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Settings_Base.print_log()
    def set_settings(self):
        context = bpy.context
        addon = context.preferences.addons.get(self.addon_name)
        self.set_setting(addon, 'canvas_use_hud', False)
        self.set_setting(addon, 'rc_angle_step', 45 * 0.0174533)
        self.set_setting(addon, 'ts.use_ctr', False)
        self.set_setting(addon, 'ts.use_alt', False)
        self.set_setting(addon, 'ts.use_shift', True)
        self.set_setting(addon, 'ts.keycode', 'SPACE')