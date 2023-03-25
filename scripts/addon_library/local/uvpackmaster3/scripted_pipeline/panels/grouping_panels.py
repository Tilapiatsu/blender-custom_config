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

from ...utils import get_prefs, in_debug_mode
from ...panel import UVPM3_PT_Registerable, GroupingSchemeAccess
from ...labels import Labels
from ...enums import GroupLayoutMode, TexelDensityGroupPolicy
from ...operator_islands import UVPM3_OT_SetManualGroupIParam, UVPM3_OT_SelectManualGroupIParam, UVPM3_OT_ShowManualGroupIParam, UVPM3_OT_ApplyGroupingToScheme
from ...presets_grouping_scheme import UVPM3_PT_PresetsGroupingScheme

from ...grouping_scheme import\
    (UVPM3_OT_NewGroupingScheme,
     UVPM3_OT_RemoveGroupingScheme,
     UVPM3_OT_NewGroupInfo,
     UVPM3_OT_RemoveGroupInfo,
     UVPM3_OT_NewTargetBox,
     UVPM3_OT_RemoveTargetBox,
     UVPM3_OT_MoveGroupInfo,
     UVPM3_OT_MoveTargetBox)

from ...grouping_scheme_ui import UVPM3_MT_BrowseGroupingSchemes, UVPM3_UL_GroupInfo, UVPM3_UL_TargetBoxes

from ...box_ui import GroupingSchemeBoxesEditUI


class UVPM3_PT_GroupingBase(UVPM3_PT_Registerable, GroupingSchemeAccess):

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        scene_props = context.scene.uvpm3_props
        return prefs.get_mode(scene_props.active_main_mode_id, context).grouping_enabled()

    def should_draw_grouping_options(self):
        return hasattr(self.active_mode, 'draw_grouping_options')

    def draw_grouping_options(self, g_options, layout, g_scheme=None):
        self.active_mode.draw_grouping_options(g_scheme, g_options, layout)

    def draw_impl(self, context):

        self.init_access(context, ui_drawing=True)
        self.draw_impl2(context)


class UVPM3_PT_Grouping(UVPM3_PT_GroupingBase):

    bl_idname = 'UVPM3_PT_Grouping'
    bl_label = 'Island Grouping'
    # bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 800
    APPLY_GROUPING_TO_SCHEME_HELP_URL_SUFFIX = '30-packing-modes/30-groups-to-tiles/#apply-automatic-grouping-to-a-grouping-scheme'

    def draw_grouping_schemes_presets(self, context, layout):
        layout.emboss = 'NONE'
        layout.popover(panel=UVPM3_PT_PresetsGroupingScheme.__name__, icon='PRESET', text="")

    def draw_grouping_schemes(self, context, layout):

        main_col = layout.column(align=True)
        main_col.label(text='Select a grouping scheme:')

        row = main_col.row(align=True)
        row.menu(UVPM3_MT_BrowseGroupingSchemes.bl_idname, text="", icon='GROUP_UVS')

        if self.active_g_scheme is not None:
            row.prop(self.active_g_scheme, "name", text="")

        row.operator(UVPM3_OT_NewGroupingScheme.bl_idname, icon='ADD', text='' if self.active_g_scheme is not None else UVPM3_OT_NewGroupingScheme.bl_label)

        if self.active_g_scheme is not None:
            row.operator(UVPM3_OT_RemoveGroupingScheme.bl_idname, icon='REMOVE', text='')

        box = row.box()
        box.scale_y = 0.5
        self.draw_grouping_schemes_presets(context, box)

        if self.active_g_scheme is None:
            return None

        if self.should_draw_grouping_options():
            main_col.separator()
            main_col.separator()
            main_col.label(text='Scheme options:')
            self.draw_grouping_options(self.active_g_scheme.options, main_col, self.active_g_scheme)
            

    def draw_impl2(self, context):

        layout = self.layout

        col = layout.column(align=True)
        box = col.box()
        col2 = box.column(align=True)
        col2.label(text=Labels.GROUP_METHOD_NAME + ':')
        row = col2.row(align=True)
        row.prop(self.scene_props, "group_method", text='')

        if self.scene_props.auto_grouping_enabled():
            if self.should_draw_grouping_options():
                options_box = col.box()
                options_col = options_box.column(align=True)
                options_col.label(text='Grouping options:')
                # options_box = options_col.box()

                self.draw_grouping_options(self.scene_props.auto_group_options, options_col)
            
            box = col.box()
            self.operator_with_help(UVPM3_OT_ApplyGroupingToScheme.bl_idname, box, self.APPLY_GROUPING_TO_SCHEME_HELP_URL_SUFFIX)

        else:
            # col.separator()
            box = col.box()
            self.draw_grouping_schemes(context, box)

    
class UVPM3_PT_SchemeGroups(UVPM3_PT_GroupingBase):

    bl_idname = 'UVPM3_PT_SchemeGroups'
    bl_label = 'Scheme Groups'
    bl_parent_id = UVPM3_PT_Grouping.bl_idname
    # bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 810

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.uvpm3_props
        return super().poll(context) and\
                scene_props.active_grouping_scheme(context) is not None

    def draw_impl2(self, context):

        layout = self.layout
        main_col = layout.column(align=True)

        groups_layout = main_col # .box()

        show_more = self.active_g_scheme is not None and len(self.active_g_scheme.groups) > 1

        row = groups_layout.row()
        row.template_list(UVPM3_UL_GroupInfo.bl_idname, "", self.active_g_scheme, "groups",
                            self.active_g_scheme,
                            "active_group_idx", rows=4 if show_more else 2)

        col = row.column(align=True)
        col.operator(UVPM3_OT_NewGroupInfo.bl_idname, icon='ADD', text="")
        col.operator(UVPM3_OT_RemoveGroupInfo.bl_idname, icon='REMOVE', text="")

        if show_more:
            col.separator()
            col.operator(UVPM3_OT_MoveGroupInfo.bl_idname, icon='TRIA_UP', text="").direction = 'UP'
            col.operator(UVPM3_OT_MoveGroupInfo.bl_idname, icon='TRIA_DOWN', text="").direction = 'DOWN'

        if self.active_group is None:
            return
            
        col = groups_layout.column(align=True)
        col.separator()

        if hasattr(self.active_mode, 'draw_group_options'):
            col.label(text='Group options:')
            col2 = col.column(align=True)

            props_count = self.active_mode.draw_group_options(self.active_g_scheme, self.active_group, col2)

            if props_count == 0:
                box = col2.box()
                box.label(text='No group options available the for currently selected modes')

        col.separator()
        col.separator()
        row = col.row(align=True)
        row.operator(UVPM3_OT_SetManualGroupIParam.bl_idname)
        col.separator()

        col.label(text="Select islands assigned to the group:")
        row = col.row(align=True)

        op = row.operator(UVPM3_OT_SelectManualGroupIParam.bl_idname, text="Select")
        op.select = True
        op = row.operator(UVPM3_OT_SelectManualGroupIParam.bl_idname, text="Deselect")
        op.select = False

        row = col.row(align=True)
        row.operator(UVPM3_OT_ShowManualGroupIParam.bl_idname)


class UVPM3_PT_GroupTargetBoxes(UVPM3_PT_GroupingBase):

    bl_idname = 'UVPM3_PT_GroupTargetBoxes'
    bl_label = 'Group Target Boxes'
    bl_parent_id = UVPM3_PT_Grouping.bl_idname
    # bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 820

    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False

        prefs = get_prefs()
        scene_props = context.scene.uvpm3_props
        active_mode = prefs.get_active_main_mode(scene_props, context)

        if not active_mode.group_target_box_editing():
            return False

        active_g_scheme = scene_props.active_grouping_scheme(context)
        if active_g_scheme is None:
            return False

        return active_g_scheme.group_target_box_editing()
                

    def draw_impl2(self, context):

        layout = self.layout
        complementary_group_is_active = self.active_g_scheme.complementary_group_is_active()

        target_boxes_col = layout.column(align=True)
        target_boxes_col.enabled = not complementary_group_is_active

        if complementary_group_is_active:
            target_boxes_text='Group Target Boxes: (target boxes of the complementary group cannot be edited)'
            target_boxes_icon='ERROR'
            row = target_boxes_col.row()
            row.label(text=target_boxes_text, icon=target_boxes_icon)


        show_more = self.active_group is not None and len(self.active_group.target_boxes) > 1

        row = target_boxes_col.row()
        row.template_list(UVPM3_UL_TargetBoxes.bl_idname, "", self.active_group, "target_boxes",
                          self.active_group,
                          "active_target_box_idx", rows=4 if show_more else 2)
        col = row.column(align=True)
        col.operator(UVPM3_OT_NewTargetBox.bl_idname, icon='ADD', text="")
        col.operator(UVPM3_OT_RemoveTargetBox.bl_idname, icon='REMOVE', text="")

        if show_more:
            col.separator()
            col.operator(UVPM3_OT_MoveTargetBox.bl_idname, icon='TRIA_UP', text="").direction = 'UP'
            col.operator(UVPM3_OT_MoveTargetBox.bl_idname, icon='TRIA_DOWN', text="").direction = 'DOWN'

        # col = groups_layout.column(align=True)

        target_boxes_col.separator()
        box_edit_UI = GroupingSchemeBoxesEditUI(context, self.scene_props)
        box_edit_UI.draw(target_boxes_col)
