from Tila_ConfigManager.config.keymaps.keymaps import TILA_Config_Keymaps_Base

addon_name = "MACHIN3tools"


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
                "wm.call_menu_pie",
                "S",
                "PRESS",
                ctrl=True,
                shift=True,
                properties={"name": "MACHIN3_MT_save_pie"},
                disable_double=True,
            )

        if self.kmi_init(
            name="UV Editor",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            self.kmi_set_replace(
                "wm.call_menu_pie",
                "D",
                "PRESS",
                alt=True,
                shift=True,
                properties={"name": "MACHIN3_MT_uv_align_pie"},
                disable_double=True,
            )

        if self.kmi_init(
            name="Mesh",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            self.kmi_set_replace(
                "machin3.clean_up", "ZERO", "PRESS", ctrl=True, alt=True, shift=True
            )
            self.kmi_set_active(
                True,
                "machin3.clean_up",
                "ZERO",
                "PRESS",
                ctrl=True,
                alt=True,
                shift=True,
            )
            self.kmi_set_replace(
                "wm.call_menu_pie",
                "D",
                "PRESS",
                alt=True,
                shift=True,
                properties={"name": "MACHIN3_MT_align_pie"},
                disable_double=True,
            )
            self.kmi_set_active(False, "machin3.select")
            self.kmi_set_active(False, "machin3.symmetrize")

        if self.kmi_init(
            name="3D View Generic",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            self.kmi_set_active(True, "machin3.material_picker")
            k = self.kmi_find("machin3.material_picker")
            if k:
                k.map_type = "KEYBOARD"
                k.type = "M"

        if self.kmi_init(
            name="Object Mode",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            self.kmi_set_replace(
                "machin3.align", "A", "PRESS", alt=True, disable_double=False
            )
            # self.kmi_set_replace('machin3.mirror', 'X', "PRESS", alt=True, shift=True, properties={'flick': True, 'remove': False}, disable_double=False)
            self.kmi_set_active(
                True,
                "machin3.mirror",
                "X",
                "PRESS",
                alt=True,
                shift=True,
                properties={"flick": True, "remove": False},
            )

        if self.kmi_init(
            name="Pose",
            space_type="EMPTY",
            region_type="WINDOW",
            addon=False,
            restore_to_default=False,
        ):
            self.kmi_set_replace(
                "machin3.align", "A", "PRESS", alt=True, disable_double=False
            )
