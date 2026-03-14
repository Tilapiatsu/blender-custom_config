import bpy
from abc import abstractmethod
from ...keymap_manager import KeymapManager

# TODO
#  Need to read : https://wiki.blender.org/wiki/Source/Depsgraph
# - Create an action center pie menu : https://blenderartists.org/t/modo-me-the-modo-action-centers-in-blender-and-more-2-80-2-79/1145899
# 		- Automatic
# 		- Selection
# 		- Selection Border
# 		- Selection Center Auto Axis
# 		- Element
# 		- View --> OK
# 		- Origin
# 		- Parent
# 		- Local --> OK
# 		- Pivot
# 		- Pivot Center Parent Axis
# 		- Pivot Wold Axis
# 		- Cursor
# 		- Custom
# - Fix th area pie menu shortcut which dosn't workin in all context
# - Remove double with modal control
# - Vertex Normal Pie Menu :  Thief
# - Need to fix the rotate/scaling pivot point in UV context
# - Create a simple Bevel like Modo Does : Bevel + Inset + Segment count
# - Script to visualize Texture checker in all objects in the viewport
# - Fix the smart edit mode in UV context


class TILA_Config_Keymaps_Base(KeymapManager.KeymapManager):
    k_viewfit = "MIDDLEMOUSE"
    k_manip = "LEFTMOUSE"
    k_cursor = "MIDDLEMOUSE"
    k_nav = "MIDDLEMOUSE"
    k_menu = "SPACE"
    k_select = "LEFTMOUSE"
    k_lasso = "RIGHTMOUSE"
    k_lasso_through = "MIDDLEMOUSE"
    k_box = "LEFTMOUSE"
    k_box_through = "MIDDLEMOUSE"
    k_select_attatched = "MIDDLEMOUSE"
    k_context = "RIGHTMOUSE"
    k_more = "UP_ARROW"
    k_less = "DOWN_ARROW"
    k_linked = "W"
    k_vert_mode = "ONE"
    k_edge_mode = "TWO"
    k_face_mode = "THREE"
    k_move = "G"
    k_rotate = "R"
    k_scale = "S"

    addon_name = ""

    def __init__(self):
        super().__init__()

    @staticmethod
    def print_assigning_keymap(message=None):
        def decorator(func):
            set_addon_name = False
            custom_message = ""
            if message is None:
                set_addon_name = True
            else:
                custom_message = message

            def print_message(self):
                if set_addon_name:
                    message = self.addon_name
                else:
                    message = custom_message

                self.print_status(f"Assigning {message} Keymaps")
                func(self)
                self.print_status(f"Assignment of {message} Keymaps complete", start=False)

            return print_message

        return decorator

    @abstractmethod
    def set_keymaps(self):
        pass

    def print_status(self, message, start=True):
        if start:
            self.log_progress.start(f"{message}")
        else:
            self.log_progress.done(f"{message}")

    def keymap_restore(self, all=True):
        if all:
            if not bpy.context.window_manager.tila_config_keymap_restored:
                # for i in range(100):
                bpy.ops.preferences.keymap_restore(all=all)
                bpy.context.window_manager.tila_config_keymap_restored = True
        else:
            pass


class TILA_Config_Keymaps_Base_Empty(TILA_Config_Keymaps_Base):
    addon_name = "Empty"

    def __init__(self):
        super().__init__()

    @TILA_Config_Keymaps_Base.print_assigning_keymap()
    def set_keymaps(self):
        pass
