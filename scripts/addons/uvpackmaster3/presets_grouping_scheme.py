import bpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

from .utils import get_prefs
from .presets import UVPM3_PT_PresetsBase, UVPM3_OT_SavePresetBase, UVPM3_OT_LoadPresetBase, LoadPresetInvokeHelper
from .grouping_scheme import UVPM3_GroupingScheme, GroupingSchemeAccess
from .version import UvpmVersionInfo

GROUPING_SCHEME_PRESET_FILENAME_EXT = "uvpmg"
GROUPING_SCHEME_PRESET_FILENAME_DOT_EXT = '.' + GROUPING_SCHEME_PRESET_FILENAME_EXT


class GroupingSchemePresetFilenameMixin:

    filename_ext = GROUPING_SCHEME_PRESET_FILENAME_DOT_EXT
    filter_glob : StringProperty(
        default="*{}".format(GROUPING_SCHEME_PRESET_FILENAME_DOT_EXT),
        options={'HIDDEN'},
    )


class UVPM3_PT_PresetsGroupingScheme(UVPM3_PT_PresetsBase, GroupingSchemeAccess, bpy.types.Panel):

    bl_label = 'Grouping Scheme Presets'
    show_remove_button = True
    show_save_button = True

    @staticmethod
    def get_load_operator_idname():
        return UVPM3_OT_LoadGroupingSchemePreset.bl_idname

    @staticmethod
    def get_save_operator_idname():
        return UVPM3_OT_SaveGroupingSchemePreset.bl_idname

    def get_preset_path(self):
        prefs = get_prefs()
        return prefs.get_grouping_schemes_preset_path()

    def get_preset_dot_ext(self):
        return GROUPING_SCHEME_PRESET_FILENAME_DOT_EXT

    def is_save_button_enabled(self):
        return len(self.get_grouping_schemes()) > 0

    def get_default_preset_name(self):
        grouping_scheme = self.get_active_grouping_scheme()
        return "{}{}".format(grouping_scheme.name, GROUPING_SCHEME_PRESET_FILENAME_DOT_EXT) if grouping_scheme is not None else ""

    def draw(self, context):
        self.init_access(context, ui_drawing=True)
        super().draw(context)


class UVPM3_OT_SaveGroupingSchemePreset(UVPM3_OT_SavePresetBase, ExportHelper,
                                        GroupingSchemeAccess, GroupingSchemePresetFilenameMixin):
    bl_idname = 'uvpackmaster3.save_grouping_scheme_preset'
    bl_label = 'Save Scheme'
    bl_description = 'Save the active grouping scheme to a file'

    def set_preset_version(self, json_struct):
        json_struct['grouping_scheme_version'] = UvpmVersionInfo.GROUPING_SCHEME_VERSION

    def get_collection_props(self, context):
        return self.active_g_scheme

    def execute(self, context):
        self.init_access(context)
        return super().execute(context)


class UVPM3_OT_LoadGroupingSchemePreset(LoadPresetInvokeHelper, GroupingSchemePresetFilenameMixin,
                                        UVPM3_OT_LoadPresetBase, ImportHelper, GroupingSchemeAccess):

    bl_idname = 'uvpackmaster3.load_grouping_scheme_preset'
    bl_label = 'Load Scheme'
    bl_options = {'UNDO'}
    bl_description = 'Load Grouping Scheme from a file'

    CREATE_NEW_PROP_NAME = 'Create New'
    create_new : BoolProperty(name=CREATE_NEW_PROP_NAME, default=False, options={'SKIP_SAVE'})

    success_msg = 'Grouping Scheme loaded.'
    props_to_load_default = True

    g_scheme_to_overwrite = None
    g_scheme_to_overwrite_idx = -1

    def translate_props(self, grouping_scheme_version, props_dict):
        pass

    def get_preset_version(self, json_struct):
        return json_struct['grouping_scheme_version']

    def validate_preset_version(self, preset_version):
        return preset_version == UvpmVersionInfo.GROUPING_SCHEME_VERSION

    def show_confirm_popup(self, context):
        self.init_access(context)

        preset_uuid = self.props_dict.get('uuid')
        if not UVPM3_GroupingScheme.uuid_is_valid(preset_uuid):
            self.raise_invalid_format()

        g_schemes = self.get_grouping_schemes()
        for idx, g_scheme in enumerate(g_schemes):
            if g_scheme.uuid == preset_uuid:
                self.g_scheme_to_overwrite = g_scheme
                self.g_scheme_to_overwrite_idx = idx
                return True

        return False

    def draw(self, context):
        if not self.should_show_confirm_popup:
            return super().draw(context)

        layout = self.layout
        col = layout.column()
        col.label(text='The operation is going to overwrite a grouping scheme already present in the blend file:')
        col.label(text='  "{}"'.format(self.g_scheme_to_overwrite.name))
        col.label(text='(because the internal IDs of the grouping scheme and the preset are the same). Press OK to continue.')

        col.separator()
        col.label(text="Check '{}' to force creating a new grouping scheme (instead of overwriting):".format(self.CREATE_NEW_PROP_NAME))
        col.prop(self, 'create_new')

    def load_properties(self):
        temp_grouping_scheme = UVPM3_GroupingScheme()
        self.set_props(temp_grouping_scheme, self.props_dict, self.props_to_load)

        if not temp_grouping_scheme.is_valid():
            self.raise_invalid_format()

        if self.g_scheme_to_overwrite is not None and not self.create_new:
            self.g_scheme_to_overwrite.copy_from(temp_grouping_scheme)
            self.scene_props.active_grouping_scheme_idx = self.g_scheme_to_overwrite_idx
        else:
            if self.g_scheme_to_overwrite is not None:
                temp_grouping_scheme.regenerate_uuid()

            new_grouping_scheme = self.scene_props.grouping_schemes.add()
            new_grouping_scheme.copy_from(temp_grouping_scheme)
            self.scene_props.active_grouping_scheme_idx = len(self.scene_props.grouping_schemes) - 1
