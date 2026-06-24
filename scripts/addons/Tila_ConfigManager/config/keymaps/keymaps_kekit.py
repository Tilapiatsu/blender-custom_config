from Tila_ConfigManager.config.keymaps.keymaps import TILA_Config_Keymaps_Base

addon_name = "kekit"


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
            self.kmi_set_replace("view3d.ke_get_set_material", "M", "PRESS", shift=True)

        if self.kmi_init(
            name="Mesh",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            # kmi = self.kmi_find(idname="wm.call_menu", type="C", ctrl=True)
            # if kmi is not None:
            #     kmi.shift = True
            #
            # kmi = self.kmi_find(idname="wm.call_menu", type="V", ctrl=True)
            # if kmi is not None:
            #     kmi.shift = True
            #
            # self.kmi_set_replace(
            #     "view3d.ke_copyplus",
            #     "C",
            #     "PRESS",
            #     ctrl=True,
            #     properties={"mode": "COPY"},
            #     disable_double=True,
            # )
            # self.kmi_set_replace(
            #     "view3d.ke_copyplus",
            #     "X",
            #     "PRESS",
            #     ctrl=True,
            #     properties={"mode": "CUT"},
            #     disable_double=True,
            # )
            # self.kmi_set_replace(
            #     "view3d.ke_copyplus",
            #     "V",
            #     "PRESS",
            #     ctrl=True,
            #     properties={"mode": "PASTE"},
            #     disable_double=True,
            # )

            self.kmi_set_replace(
                "mesh.ke_direct_loop_cut",
                "C",
                "PRESS",
                alt=True,
                shift=True,
                properties={"mode": "SLIDE"},
                disable_double=True,
            )
