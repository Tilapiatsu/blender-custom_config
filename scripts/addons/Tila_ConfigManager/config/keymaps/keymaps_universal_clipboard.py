from Tila_ConfigManager.config.keymaps.keymaps import TILA_Config_Keymaps_Base

addon_name = "universal_clipboard"


class TILA_Config_Keymaps(TILA_Config_Keymaps_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        if self.kmi_init(
            name="3D View",
            space_type="VIEW_3D",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            kmi = self.kmi_find(idname="wm.call_menu", type="C", ctrl=True)
            if kmi is not None:
                kmi.shift = True

            kmi = self.kmi_find(idname="wm.call_menu", type="V", ctrl=True)
            if kmi is not None:
                kmi.shift = True

            kmi = self.kmi_find(idname="mesh.dissolve_mode", type="X", ctrl=True)
            if kmi is not None:
                kmi.active = False

            self.kmi_set_replace(
                "view3d.ucopy",
                "C",
                "PRESS",
                ctrl=True,
                disable_double=True,
            )
            self.kmi_set_replace(
                "view3d.ucut",
                "X",
                "PRESS",
                ctrl=True,
                disable_double=True,
            )
            self.kmi_set_replace(
                "view3d.upaste",
                "V",
                "PRESS",
                ctrl=True,
                disable_double=True,
            )
