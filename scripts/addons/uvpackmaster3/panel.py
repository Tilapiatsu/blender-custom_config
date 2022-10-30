# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


from .prefs import get_prefs
from .operator import *
from .operator_islands import *
from .utils import *
from .presets import *
from .mode import ModeType, UVPM3_MT_BrowseModes

import bpy
import bpy_types


UVPM3_PT_SPACE_TYPE = 'IMAGE_EDITOR'
UVPM3_PT_REGION_TYPE = 'UI'
UVPM3_PT_CATEGORY = 'UVPackmaster3'
UVPM3_PT_CONTEXT = ''


class UVPM3_PT_Generic(bpy.types.Panel):

    bl_space_type = UVPM3_PT_SPACE_TYPE
    bl_region_type = UVPM3_PT_REGION_TYPE
    bl_category = UVPM3_PT_CATEGORY
    bl_context = UVPM3_PT_CONTEXT
    bl_order = 1

    @classmethod
    def _draw_help_operator(self, layout, help_url_suffix):

        help_op = layout.operator(UVPM3_OT_Help.bl_idname, icon='HELP', text='')
        help_op.url_suffix = help_url_suffix

    @classmethod
    def draw_enum_in_box(self, obj, prop_id, prop_name, layout, help_url_suffix=None, expand=False):

        prop_kwargs = { 'expand' : expand }
        if not expand:
            prop_kwargs['text'] = ''

        box = layout.box()
        col = box.column(align=True)

        if prop_name:
            col.label(text=prop_name + ':')
            
        row = col.row(align=True)
        row.prop(obj, prop_id, **prop_kwargs)

        if help_url_suffix:
            self._draw_help_operator(row, help_url_suffix)

        return col

    @classmethod
    def draw_prop_with_set_menu(self, obj, prop_id, layout, menu_class):
        split = layout.split(factor=0.8, align=True)

        col_s = split.row(align=True)
        col_s.prop(obj, prop_id)
        col_s = split.row(align=True)
        col_s.menu(menu_class.bl_idname, text='Set')
        
    @classmethod
    def handle_prop(self, obj, prop_name, supported, not_supported_msg, layout):

        if supported:
            layout.prop(obj, prop_name)
        else:
            layout.enabled = False
            split = layout.split(factor=0.4)
            col_s = split.column()
            col_s.prop(obj, prop_name)
            col_s = split.column()
            col_s.label(text=not_supported_msg)


    def get_main_property(self):
        return None

    def draw_header(self, context):

        main_property = self.get_main_property()
        if main_property is None:
            return

        layout = self.layout
        scene_props = context.scene.uvpm3_props

        col = layout.column()
        row = col.row()
        row.prop(scene_props, main_property, text='')
        row.row()

    def draw(self, context):

        self.prefs = get_prefs()
        self.scene_props = context.scene.uvpm3_props
        self.scripted_props = context.scene.uvpm3_props.scripted_props
        self.active_mode = self.prefs.get_active_main_mode(self.scene_props, context)

        main_property = self.get_main_property()

        if main_property is not None:
            self.layout.enabled = getattr(self.scene_props, main_property)
        
        self.draw_impl(context)

    def prop_with_help(self, obj, prop_id, layout):

        row = layout.row(align=True)
        row.prop(obj, prop_id)
        self._draw_help_operator(row, self.HELP_URL_SUFFIX)

    def operator_with_help(self, op_idname, layout, help_url_suffix):

        row = layout.row(align=True)
        row.operator(op_idname)
        self._draw_help_operator(row, help_url_suffix)

    def handle_prop_enum(self, obj, prop_name, prop_label, supported, not_supported_msg, layout):

        prop_label_colon = prop_label + ':'

        if supported:
            layout.label(text=prop_label_colon)
        else:
            split = layout.split(factor=0.4)
            col_s = split.column()
            col_s.label(text=prop_label_colon)
            col_s = split.column()
            col_s.label(text=not_supported_msg)

        layout.prop(obj, prop_name, text='')
        layout.enabled = supported

    def messages_in_boxes(self, ui_elem, messages):

        for msg in messages:
            box = ui_elem.box()

            msg_split = split_by_chars(msg, 60)
            if len(msg_split) > 0:
                # box.separator()
                for msg_part in msg_split:
                    box.label(text=msg_part)
                # box.separator()


class EngineStatusMeta(bpy_types.RNAMeta):
    @property
    def bl_label(self):
        prefs = get_prefs()
        return prefs.engine_status_msg


class UVPM3_PT_EngineStatus(UVPM3_PT_Generic, metaclass=EngineStatusMeta):

    bl_idname = 'UVPM3_PT_EngineStatus'
    bl_context = ''
    bl_order = 0

    bl_options = {'DEFAULT_CLOSED'}
    # MUSTDO: add 'HEADER_LAYOUT_EXPAND' to bl_options

    def draw_header(self, context):

        self.prefs = get_prefs()
        layout = self.layout
        row = layout.row()
        row.alert = True
        # demo_suffix = " (DEMO)" if self.prefs.FEATURE_demo else ''
        self.prefs.draw_engine_status_help_button(row)

    def draw_impl(self, context):

        layout = self.layout
        col = layout.column(align=True)
        
        self.prefs.draw_general_options(col)

        if in_debug_mode():
            col.separator()

            dopt_layout = col
            dopt_layout.label(text="Debug options:")

            box = dopt_layout.box()
            row = box.row(align=True)
            row.prop(self.prefs, "write_to_file")

            box = dopt_layout.box() 
            row = box.row(align=True)
            row.prop(self.prefs, "wait_for_debugger")

            row = dopt_layout.row(align=True)
            row.prop(self.prefs, "seed")
            row = dopt_layout.row(align=True)
            row.prop(self.prefs, "test_param")
            

class UVPM3_PT_AuxOperations(UVPM3_PT_Generic):

    bl_idname = 'UVPM3_PT_AuxOperations'
    bl_label = 'Auxiliary Operations'
    bl_context = ''

    def draw_impl(self, context):

        layout = self.layout
        col = layout.column(align=True)

        aux_modes = self.prefs.get_modes(ModeType.AUX)

        if len(aux_modes) > 0:
            # col.label(text="Auxiliary operations:")
            for mode_id, mode_cls in aux_modes:
                row = col.row(align=True)
                row.operator(mode_cls.OPERATOR_IDNAME)


class UVPM3_PT_Main(UVPM3_PT_Generic):

    bl_idname = 'UVPM3_PT_Main'
    bl_label = 'Main Mode'
    bl_context = ''

    def draw_header_preset(self, _context):
        UVPM3_PT_Presets.draw_panel_header(self.layout)

    def draw_impl(self, context):

        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)

        active_mode = self.prefs.get_active_main_mode(self.scene_props, context)
        row.menu(UVPM3_MT_BrowseModes.bl_idname, text=type(active_mode).enum_name(), icon='COLLAPSEMENU')

        if active_mode.MODE_HELP_URL_SUFFIX:
            help_op = row.operator(UVPM3_OT_MainModeHelp.bl_idname, icon='HELP', text='')
            help_op.url_suffix = active_mode.MODE_HELP_URL_SUFFIX

        col.separator()

        mode_id = self.scene_props.active_main_mode_id
        mode = self.prefs.get_mode(mode_id, context)

        mode_layout = col
        mode.draw(mode_layout)


class UVPM3_PT_Registerable(UVPM3_PT_Generic):

    bl_order = 10
    PANEL_PRIORITY = sys.maxsize


class UVPM3_PT_SubPanel(UVPM3_PT_Registerable):
    
    bl_parent_id = UVPM3_PT_Main.bl_idname

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        scene_props = context.scene.uvpm3_props

        try:
            return cls.bl_idname in prefs.get_mode(scene_props.active_main_mode_id, context).subpanels_base()

        except:
            return False


class UVPM3_PT_IParamEdit(UVPM3_PT_SubPanel):

    def get_main_property(self):
        return self.IPARAM_EDIT_UI.ENABLED_PROP_NAME

    def draw_impl(self, context):

        self.IPARAM_EDIT_UI(context, self.scene_props).draw(self.layout)
