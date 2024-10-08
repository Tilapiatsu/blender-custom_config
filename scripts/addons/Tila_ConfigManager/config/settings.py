import bpy
import os
from ..blender_version.blender_version import bversion
from ..preferences.ui.log_list import TILA_Config_Log as log_list

class TILA_Config_Settings:
    addon_name = 'NONE'

    
    def print_log(func):
        def wrapper(self):
            if self.addon_name in bpy.context.preferences.addons:
                log_progress = log_list(bpy.context.window_manager.tila_config_log_list, 'tila_config_log_list_idx')
                log_progress.start(f'Applying {self.addon_name} Settings')
                func(self)
                log_progress.done(f'{self.addon_name} Settings Applied')

        return wrapper

class TILA_Config_Settings_Global(TILA_Config_Settings):
    addon_name = "Global"

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
        context.preferences.view.show_tooltips = True
        context.preferences.view.show_tooltips_python = True
        context.preferences.view.render_display_type = "WINDOW"
        context.preferences.view.use_weight_color_range = True
        context.preferences.view.show_developer_ui = True
        context.preferences.view.show_statusbar_memory = True
        if self.get_gpu_device is not None:
            context.preferences.view.show_statusbar_vram = True

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

        context.preferences.view.color_picker_type = 'SQUARE_SV'

        # Edit Settings
        context.preferences.edit.object_align = "CURSOR"
        context.preferences.edit.undo_steps = 200
        context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"

        # Input Settings
        context.preferences.inputs.view_zoom_axis = "HORIZONTAL"
        context.preferences.inputs.ndof_view_navigate_method = "FREE"
        context.preferences.inputs.view_rotate_method = "TRACKBALL"
        context.preferences.inputs.view_rotate_sensitivity_trackball = 2
        context.preferences.inputs.drag_threshold_tablet = 1
        context.preferences.inputs.ndof_view_rotate_method = "TRACKBALL"
        context.preferences.inputs.use_auto_perspective = True
        context.preferences.inputs.use_mouse_depth_navigate = True
        context.preferences.inputs.use_numeric_input_advanced = True
        # context.preferences.inputs.use_mouse_emulate_3_button = True
        context.preferences.inputs.use_zoom_to_mouse = True
        context.preferences.inputs.pressure_softness = -0.5

        log_progress.done(f'{self.addon_name} Settings Applied')


class TILA_Config_Settings_PolyQuilt(TILA_Config_Settings):
    addon_name = 'PolyQuilt'

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.is_debug = False

class TILA_Config_Settings_MACHIN3tools(TILA_Config_Settings):
    addon_name = 'MACHIN3tools'

    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    def set_machin3tool_settings(self, context, setting_name, value):
        if getattr(context.preferences.addons.get('MACHIN3tools').preferences, setting_name) == value:
            return
        
        setattr(context.preferences.addons.get('MACHIN3tools').preferences, setting_name, value)
    
    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            
            self.set_machin3tool_settings(context, 'activate_smart_vert' , False)
            self.set_machin3tool_settings(context, 'activate_smart_edge' , False)
            self.set_machin3tool_settings(context, 'activate_smart_face' , False)
            self.set_machin3tool_settings(context, 'activate_focus' , False)
            self.set_machin3tool_settings(context, 'activate_mirror' , True)
            self.set_machin3tool_settings(context, 'activate_modes_pie' , False)
            self.set_machin3tool_settings(context, 'activate_views_pie' , False)
            self.set_machin3tool_settings(context, 'activate_transform_pie' , False)
            self.set_machin3tool_settings(context, 'activate_collections_pie' , False)
            self.set_machin3tool_settings(context, 'activate_align' , True)
            self.set_machin3tool_settings(context, 'activate_filebrowser_tools' , True)
            self.set_machin3tool_settings(context, 'activate_extrude' , True)
            self.set_machin3tool_settings(context, 'activate_clean_up' , True)
            self.set_machin3tool_settings(context, 'activate_edge_constraint' , True)
            self.set_machin3tool_settings(context, 'activate_surface_slide' , True)
            self.set_machin3tool_settings(context, 'activate_group' , False)
            self.set_machin3tool_settings(context, 'activate_mesh_cut' , True)
            self.set_machin3tool_settings(context, 'activate_thread' , True)
            self.set_machin3tool_settings(context, 'activate_material_picker' , True)
            self.set_machin3tool_settings(context, 'activate_save_pie' , True)
            self.set_machin3tool_settings(context, 'activate_align_pie' , True)
            self.set_machin3tool_settings(context, 'activate_cursor_pie' , True)

class TILA_Config_Settings_collection_manager(TILA_Config_Settings):
    addon_name = 'bl_ext.blender_org.collection_manager'
    
    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.enable_qcd = False
            addon.preferences.enable_qcd_3dview_header_widget = False

class TILA_Config_Settings_EasyHDRI(TILA_Config_Settings):
    addon_name = 'EasyHDRI'
    
    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.default_folder = 'R:\\Mon Drive\\00_Blender_Asset_Library\\Hdri'
            addon.preferences.rot_text_size = 12

class TILA_Config_Settings_noodler(TILA_Config_Settings):
    addon_name = 'noodler'
    
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
    
    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.show_zbrush_border = False
            addon.preferences.show_crosshair = False
            addon.preferences.show_focus = False
            addon.preferences.rotation_snap_subdivs = 1

class TILA_Config_Settings_kekit(TILA_Config_Settings):
    addon_name = 'kekit'
    
    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.category = 'Tools'

class TILA_Config_Settings_grease_pencil_tools(TILA_Config_Settings):
    addon_name = 'bl_ext.blender_org.grease_pencil_tools'
    
    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.canvas_use_hud = False
            # addon.preferences.mouse_click = 'RIGHTMOUSE'
            addon.preferences.rc_angle_step = 45 * 0.0174533  # 45 deg to rad
            # addon.preferences.use_ctrl = False
            # addon.preferences.use_alt = True
            # addon.preferences.use_shift = False

            addon.preferences.ts.use_ctrl = False
            addon.preferences.ts.use_alt = False
            addon.preferences.ts.use_shift = True
            addon.preferences.ts.keycode = 'SPACE'

class TILA_Config_Settings_atomic_data_manager(TILA_Config_Settings):
    addon_name = 'atomic_data_manager'
    
    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.enable_missing_file_warning = False

class TILA_Config_Settings_Auto_Reload(TILA_Config_Settings):
    addon_name = 'Auto_Reload'
    
    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.update_check_launch = False

class TILA_Config_Settings_pin_verts(TILA_Config_Settings):
    addon_name = 'pin_verts'
    
    def print_log(func):
        return TILA_Config_Settings.print_log(func)

    @print_log
    def set_settings(self):
        context = bpy.context
        if self.addon_name in context.preferences.addons:
            addon = context.preferences.addons.get(self.addon_name)
            addon.preferences.sna_auto_enabledisable_falloff = False
            addon.preferences.sna_show_header_button_editmode = False
