import bpy
import os
from .settings import TILA_Config_Settings_Base
from ...bversion import BVERSION


addon_name = "Global"
class TILA_Config_Settings(TILA_Config_Settings_Base):
    addon_name = addon_name

    def __init__(self):
        super().__init__()

    @property
    def get_gpu_device(self):
        cycles_preferences = bpy.context.preferences.addons['cycles'].preferences
        devices = cycles_preferences.get_devices()
        return devices

    @TILA_Config_Settings_Base.print_log(False)
    def set_settings(self):
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
            if BVERSION < 3.2:
                library_name = ''

            context.preferences.filepaths.asset_libraries[library_name].import_method = 'PACK'
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
        self.set_setting(context, 'inputs.tablet_api', 'WINDOWS_INK')
        self.set_setting(context, 'inputs.use_auto_perspective', True)
        self.set_setting(context, 'inputs.use_mouse_depth_navigate', True)
        self.set_setting(context, 'inputs.use_numeric_input_advanced', True)
        self.set_setting(context, 'inputs.use_zoom_to_mouse', True)
        self.set_setting(context, 'inputs.pressure_softness', -0.5)

        # System
        self.set_setting(context, 'system.gpu_backend', 'VULKAN')