import bpy
import os
import functools
from ..blender_version.blender_version import bversion
from ..preferences.ui.log_list import TILA_Config_Log as log_list

# https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

class TILA_Config_Settings:
    addon_name = 'NONE'

    def __init__(self):
        self.log_progress = log_list(bpy.context.window_manager.tila_config_log_list, 'tila_config_log_list_idx')

    def print_log(func):
        def wrapper(self):
            if self.addon_name in bpy.context.preferences.addons:
                self.log_progress.start(f'Applying {self.addon_name} Settings')
                func(self)
                self.log_progress.done(f'{self.addon_name} Settings Applied')

        return wrapper

    def set_setting(self, setting_root:bpy.types.bpy_struct, setting_name:str, value):
        if rgetattr(setting_root.preferences, setting_name, None) is None:
            self.log_progress.error(f'Setting "{setting_name}" not found in {self.addon_name} addon')
            return
        if rgetattr(setting_root.preferences, setting_name) == value:
            return

        self.log_progress.info(f'{self.addon_name} : Set {setting_name} = {value}')
        rsetattr(setting_root.preferences, setting_name, value)


class TILA_Config_Settings_Global(TILA_Config_Settings):
    addon_name = "Global"

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @property
    def get_gpu_device(self):
        cycles_preferences = bpy.context.preferences.addons['cycles'].preferences
        devices = cycles_preferences.get_devices()
        return devices

    def set_settings(self):
        log_progress = log_list(bpy.context.window_manager.tila_config_log_list, 'tila_config_log_list_idx')
        log_progress.start(f'Applying {self.addon_name} Settings')

        context = bpy.context
        # # Set Theme to Tila
        root_path = bpy.utils.resource_path('USER')
        theme_filepath = os.path.join(
            root_path, 'scripts', 'presets', 'interface_theme', 'Tila_Ide.xml')
        bpy.ops.script.execute_preset(
            filepath=theme_filepath, menu_idname='USERPREF_MT_interface_theme_presets')

        # # Set Asset Library
        if 'Tilapiatsu' not in context.preferences.filepaths.asset_libraries:
            library_name = '00_Blender_Asset_Library'
            asset_library_path = os.path.join('R:\\', 'Mon Drive', library_name)
            bpy.ops.preferences.asset_library_add(
                'EXEC_DEFAULT', directory=asset_library_path)
            if bversion < 3.2:
                library_name = ''

            context.preferences.filepaths.asset_libraries[library_name].import_method = 'LINK'
            context.preferences.filepaths.asset_libraries[library_name].name = 'Tilapiatsu'

        # View Settings
        self.set_setting(context, 'view.show_tooltips', True)
        self.set_setting(context, 'view.show_tooltips_python', True)
        self.set_setting(context, 'view.render_display_type', "WINDOW")
        self.set_setting(context, 'view.use_weight_color_range', True)
        self.set_setting(context, 'view.show_developer_ui', True)
        self.set_setting(context, 'view.show_statusbar_memory', True)
        if self.get_gpu_device is not None:
            self.set_setting(context, 'view.show_statusbar_vram', True)

        # Edit Weight color
        for c in enumerate(context.preferences.view.weight_color_range.elements):
            if len(context.preferences.view.weight_color_range.elements)>1:
                context.preferences.view.weight_color_range.elements.remove(context.preferences.view.weight_color_range.elements[0])

        context.preferences.view.weight_color_range.elements[0].color = (1,0,1,1)
        context.preferences.view.weight_color_range.elements[0].position = 1

        context.preferences.view.weight_color_range.elements.new(0)
        context.preferences.view.weight_color_range.elements[0].color = (0,0,0,1)

        context.preferences.view.weight_color_range.elements.new(0.25)
        context.preferences.view.weight_color_range.elements[1].color = (0,0,1,1)

        context.preferences.view.weight_color_range.elements.new(0.5)
        context.preferences.view.weight_color_range.elements[2].color = (1,1,0,1)

        context.preferences.view.weight_color_range.elements.new(0.75)
        context.preferences.view.weight_color_range.elements[3].color = (1,0,0,1)

        self.set_setting(context, 'view.color_picker_type', 'SQUARE_SV')

        # Edit Settings
        self.set_setting(context, 'edit.object_align', 'CURSOR')
        self.set_setting(context, 'edit.undo_steps', 200)
        self.set_setting(context, 'edit.keyframe_new_interpolation_type', 'LINEAR')


        # Input Settings
        self.set_setting(context, 'inputs.view_zoom_axis', 'HORIZONTAL')
        self.set_setting(context, 'inputs.view_rotate_method', 'TRACKBALL')
        self.set_setting(context, 'inputs.view_rotate_sensitivity_trackball', 2)
        self.set_setting(context, 'inputs.drag_threshold_mouse', 1)
        self.set_setting(context, 'inputs.drag_threshold_tablet', 1)
        self.set_setting(context, 'inputs.drag_threshold', 1)
        self.set_setting(context, 'inputs.use_auto_perspective', True)
        self.set_setting(context, 'inputs.use_mouse_depth_navigate', True)
        self.set_setting(context, 'inputs.use_numeric_input_advanced', True)
        self.set_setting(context, 'inputs.use_zoom_to_mouse', True)
        self.set_setting(context, 'inputs.pressure_softness', -0.5)

        log_progress.done(f'{self.addon_name} Settings Applied')


class TILA_Config_Settings_PolyQuilt(TILA_Config_Settings):
    addon_name = 'PolyQuilt'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context

        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'is_debug', False)


class TILA_Config_Settings_MACHIN3tools(TILA_Config_Settings):
    addon_name = 'MACHIN3tools'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)

            self.set_setting(addon, 'activate_smart_vert' , False)
            self.set_setting(addon, 'activate_smart_edge' , False)
            self.set_setting(addon, 'activate_smart_face' , False)
            self.set_setting(addon, 'activate_focus' , False)
            self.set_setting(addon, 'activate_mirror' , True)
            self.set_setting(addon, 'activate_modes_pie' , False)
            self.set_setting(addon, 'activate_views_pie' , False)
            self.set_setting(addon, 'activate_transform_pie' , False)
            self.set_setting(addon, 'activate_collections_pie' , False)
            self.set_setting(addon, 'activate_align' , True)
            self.set_setting(addon, 'activate_filebrowser_tools' , True)
            self.set_setting(addon, 'activate_extrude' , True)
            self.set_setting(addon, 'activate_clean_up' , True)
            self.set_setting(addon, 'activate_edge_constraint' , True)
            self.set_setting(addon, 'activate_surface_slide' , True)
            self.set_setting(addon, 'activate_group_tools' , False)
            self.set_setting(addon, 'activate_mesh_cut' , True)
            self.set_setting(addon, 'activate_thread' , True)
            self.set_setting(addon, 'activate_material_picker' , True)
            self.set_setting(addon, 'activate_save_pie' , True)
            self.set_setting(addon, 'activate_align_pie' , True)
            self.set_setting(addon, 'activate_cursor_pie' , True)

class TILA_Config_Settings_collection_manager(TILA_Config_Settings):
    addon_name = 'bl_ext.blender_org.collection_manager'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'enable_qcd', False)
            self.set_setting(addon, 'enable_qcd_3dview_header_widget', False)

class TILA_Config_Settings_EasyHDRI(TILA_Config_Settings):
    addon_name = 'EasyHDRI'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'default_folder', 'R:\\Mon Drive\\00_Blender_Asset_Library\\Hdri')
            self.set_setting(addon, 'rot_text_size', 12)

class TILA_Config_Settings_noodler(TILA_Config_Settings):
    addon_name = 'noodler'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        # # noodler
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            kmi = bpy.context.window_manager.keyconfigs.addon.keymaps['Node Editor'].keymap_items
            for k in kmi:
                if k.idname == 'noodler.draw_route':
                    k.type = 'E'
                if k.idname == 'noodler.chamfer':
                    k.ctrl = False
                if k.idname == 'noodler.draw_frame':
                    k.ctrl = True

class TILA_Config_Settings_mouselook_navigation(TILA_Config_Settings):
    addon_name = 'mouselook_navigation'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'show_zbrush_border', False)
            self.set_setting(addon, 'show_crosshair', False)
            self.set_setting(addon, 'show_focus', False)
            self.set_setting(addon, 'rotation_snap_subdivs', 1)

class TILA_Config_Settings_kekit(TILA_Config_Settings):
    addon_name = 'kekit'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'category', 'Tools')

class TILA_Config_Settings_grease_pencil_tools(TILA_Config_Settings):
    addon_name = 'bl_ext.blender_org.grease_pencil_tools'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'canvas_use_hud', False)
            self.set_setting(addon, 'rc_angle_step', 45 * 0.0174533)
            self.set_setting(addon, 'ts.use_ctr', False)
            self.set_setting(addon, 'ts.use_alt', False)
            self.set_setting(addon, 'ts.use_shift', True)
            self.set_setting(addon, 'ts.keycode', 'SPACE')

class TILA_Config_Settings_atomic_data_manager(TILA_Config_Settings):
    addon_name = 'atomic_data_manager'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'enable_missing_file_warning', False)

class TILA_Config_Settings_Auto_Reload(TILA_Config_Settings):
    addon_name = 'Auto_Reload'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'update_check_launch', False)

class TILA_Config_Settings_pin_verts(TILA_Config_Settings):
    addon_name = 'pin_verts'

    def __init__(self):
        super().__init__()

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            self.set_setting(addon, 'sna_auto_enabledisable_falloff', False)
            self.set_setting(addon, 'sna_show_header_button_editmode', False)
