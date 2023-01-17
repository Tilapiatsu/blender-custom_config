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

from ...panel import *
from ...labels import Labels

from ...box_ui import CustomTargetBoxEditUI
from ...operator_misc import UVPM3_MT_SetRotStepScene, UVPM3_MT_SetPixelMarginTexSizeScene


import multiprocessing


class UVPM3_PT_TileLayout(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_TileLayout'
    bl_label = 'Tile Layout'

    PANEL_PRIORITY = 500

    def draw_impl(self, context):
        layout = self.layout
        col = layout.column(align=True)

        box = col.box()
        box.prop(self.scene_props, "use_blender_tile_grid")

        col2 = col.column(align=True)
        col2.enabled = not self.scene_props.use_blender_tile_grid
        col2.prop(self.scene_props, "tile_count_x")
        col2.prop(self.scene_props, "tile_count_y")


class UVPM3_PT_PackOptions(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_PackOptions'
    bl_label = 'Packing Options'

    PANEL_PRIORITY = 1000
    HELP_URL_SUFFIX = '15-basic-usage-and-options'

    def draw_impl(self, context):
        layout = self.layout
        col = layout.column(align=True)

        self.prop_with_help(self.scene_props, "precision", col)

        row = col.row(align=True)
        margin_supported = not self.prefs.pixel_margin_enabled(self.scene_props)
        margin_not_supported_msg = 'The Margin option is ignored when Pixel Margin is enabled'
        self.handle_prop(self.scene_props, "margin", margin_supported, margin_not_supported_msg, row)

        # Rotation Resolution
        box = col.box()
        box.enabled = self.prefs.FEATURE_island_rotation

        row = box.row()
        # TODO: missing feature check
        row.prop(self.scene_props, "rotation_enable")

        box = col.box()
        row = box.row()
        row.enabled = self.scene_props.rotation_enable
        row.prop(self.scene_props, "pre_rotation_disable")

        row = col.row(align=True)
        row.enabled = self.scene_props.rotation_enable
        self.draw_prop_with_set_menu(self.scene_props, "rotation_step", row, UVPM3_MT_SetRotStepScene)

        # Flipping enable
        box = col.box()
        row = box.row()
        row.prop(self.scene_props, "flipping_enable")

        # Fixed Scale
        box = col.box()
        fs_supported, fs_not_supported_msg = self.prefs.fixed_scale_supported(self.scene_props)

        row = box.row()
        self.handle_prop(self.scene_props, "fixed_scale", fs_supported, fs_not_supported_msg, row)

        # box = col.box()
        col2 = box.column()
        col2.enabled = self.prefs.fixed_scale_enabled(self.scene_props)
        col2.label(text=Labels.FIXED_SCALE_STRATEGY_NAME + ':')

        row = col2.row(align=True)
        row.prop(self.scene_props, "fixed_scale_strategy", text='')

        # Normalize islands
        box = col.box()
        norm_supported, norm_not_supported_msg = self.prefs.normalize_islands_supported(self.scene_props)

        row = box.row()
        self.handle_prop(self.scene_props, "normalize_islands", norm_supported, norm_not_supported_msg, row)


class UVPM3_PT_PixelMargin(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_PixelMargin'
    bl_label = 'Pixel Margin'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 3000
    HELP_URL_SUFFIX = '20-packing-functionalities/30-pixel-margin'

    def get_main_property(self):
        return 'pixel_margin_enable'

    def draw_impl(self, context):
        layout = self.layout
        col = layout.column(align=True)

        # Pixel margin
        self.prop_with_help(self.scene_props, "pixel_margin", col)

        # Pixel padding
        row = col.row(align=True)
        row.prop(self.scene_props, "pixel_padding")

        # Pixel margin to others
        row = col.row(align=True)
        row.prop(self.scene_props, "extra_pixel_margin_to_others")

        # Pixel Margin Tex Size
        row = col.row(align=True)
        self.draw_prop_with_set_menu(self.scene_props, "pixel_margin_tex_size", row, UVPM3_MT_SetPixelMarginTexSizeScene)

        if self.prefs.pack_ratio_enabled(self.scene_props):
            row.enabled = False
            col.label(text='Active texture dimensions are used to calculate pixel margin', icon='ERROR')



class UVPM3_PT_Heuristic(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_Heuristic'
    bl_label = 'Heuristic Search'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 4000
    HELP_URL_SUFFIX = '20-packing-functionalities/40-heuristic-search'

    def get_main_property(self):
        return 'heuristic_enable'

    def draw_impl(self, context):
        layout = self.layout

        col = layout.column(align=True)

        self.prop_with_help(self.scene_props, "heuristic_search_time", col)
        row = col.row(align=True)
        row.prop(self.scene_props, "heuristic_max_wait_time")

        # Advanced Heuristic
        box = col.box()
        box.enabled = self.prefs.advanced_heuristic_available(self.scene_props)
        row = box.row()
        self.handle_prop(self.scene_props, "advanced_heuristic", self.prefs.FEATURE_advanced_heuristic, Labels.FEATURE_NOT_SUPPORTED_MSG, row)
        

class UVPM3_PT_LockOverlapping(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_LockOverlapping'
    bl_label = 'Lock Overlapping'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 4400
    HELP_URL_SUFFIX = '20-packing-functionalities/50-lock-overlapping'

    def get_main_property(self):
        return 'lock_overlapping_enable'

    def draw_impl(self, context):
        layout = self.layout
        col = layout.column(align=True)

        # Lock overlapping
        self.draw_enum_in_box(self.scene_props, "lock_overlapping_mode", Labels.LOCK_OVERLAPPING_MODE_NAME, col, self.HELP_URL_SUFFIX)
        

class UVPM3_PT_LockGroups(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_LockGroups'
    bl_label = 'Lock Groups'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 4500
    HELP_URL_SUFFIX = '20-packing-functionalities/50-lock-overlapping#lock-groups'

    def get_main_property(self):
        return 'lock_groups_enable'

    def draw_impl(self, context):
        layout = self.layout

        col = layout.column(align=True)

        self.prop_with_help(self.scene_props, "lock_group_num", col)

        row = col.row(align=True)
        row.operator(UVPM3_OT_SetLockGroupIParam.bl_idname)

        row = col.row(align=True)
        row.operator(UVPM3_OT_SetFreeLockGroupIParam.bl_idname)
        
        col.separator()

        col.label(text="Select islands assigned to the lock group:")
        row = col.row(align=True)

        op = row.operator(UVPM3_OT_SelectLockGroupIParam.bl_idname, text="Select")
        op.select = True
        op = row.operator(UVPM3_OT_SelectLockGroupIParam.bl_idname, text="Deselect")
        op.select = False

        row = col.row(align=True)
        row.operator(UVPM3_OT_ResetLockGroupIParam.bl_idname)

        row = col.row(align=True)
        row.operator(UVPM3_OT_ShowLockGroupIParam.bl_idname)


class UVPM3_PT_NonSquarePacking(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_NonSquarePacking'
    bl_label = 'Non-Square Packing'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 5000
    HELP_URL_SUFFIX = '20-packing-functionalities/60-non-square-packing'

    def get_main_property(self):
        return 'tex_ratio'

    def draw_impl(self, context):
        layout = self.layout
        col = layout.column(align=True)

        self.operator_with_help(UVPM3_OT_AdjustIslandsToTexture.bl_idname, col, self.HELP_URL_SUFFIX)

        row = col.row(align=True)
        row.operator(UVPM3_OT_UndoIslandsAdjustemntToTexture.bl_idname)



class UVPM3_PT_TargetBox(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_TargetBox'
    bl_label = 'Custom Target Box'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 6000

    def get_main_property(self):
        return 'custom_target_box_enable'

    def draw_header_preset(self, _context):
        UVPM3_PT_PresetsCustomTargetBox.draw_panel_header(self.layout)

    def draw_impl(self, context):
        layout = self.layout

        col = layout.column(align=True)
        # box = col.box()
        # row = box.row(align=True)
        # row.prop(self.scene_props, "custom_target_box_enable")

        # if self.scene_props.custom_target_box_enable:
        # box = col.box()

        box_edit_UI = CustomTargetBoxEditUI(context, self.scene_props)
        box_edit_UI.draw(col)

        # col2.separator()
        # col2.label(text='Set target box to UDIM tile:')
        # row = col2.row(align=True)
        # row.prop(self.scene_props, "target_box_tile_x")
        # row.prop(self.scene_props, "target_box_tile_y")

        # row = col2.row(align=True)
        # row.operator(UVPM3_OT_SetGroupingSchemeBoxToTile.bl_idname)
        
        # col2.separator()
        # col2.label(text='Islands inside box:')

        # row = col2.row(align=True)
        # row.operator(UVPM3_OT_SelectIslandsInsideTargetBox.bl_idname, text="Select").select = True
        # row.operator(UVPM3_OT_SelectIslandsInsideTargetBox.bl_idname, text="Deselect").select = False

        # box = col2.box()
        # box.prop(self.scene_props, "fully_inside")


class RotStepIParamEditUI(IParamEditUI):

    HELP_URL_SUFFIX = '20-packing-functionalities/80-island-rotation-step'
    OPERATOR_PREFIX = 'RotStep'
    ENABLED_PROP_NAME = 'island_rot_step_enable'
    

class UVPM3_PT_IslandRotStep(UVPM3_PT_IParamEdit):

    bl_idname = 'UVPM3_PT_IslandRotStep'
    bl_label = 'Island Rotation Step'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 7000
    IPARAM_EDIT_UI = RotStepIParamEditUI


class ScaleLimitIParamEditUI(IParamEditUI):

    HELP_URL_SUFFIX = '20-packing-functionalities/90-island-scale-limit'
    OPERATOR_PREFIX = 'ScaleLimit'
    ENABLED_PROP_NAME = 'island_scale_limit_enable'


class UVPM3_PT_IslandScaleLimit(UVPM3_PT_IParamEdit):

    bl_idname = 'UVPM3_PT_IslandScaleLimit'
    bl_label = 'Island Scale Limit'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 8000
    IPARAM_EDIT_UI = ScaleLimitIParamEditUI


class UVPM3_PT_Statistics(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_Statistics'
    bl_label = 'Statistics'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 11000

    def draw_impl(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text='Last operation statistics:')

        for idx, dev in enumerate(self.prefs.device_array()):
            col.separator()
            col.label(text=dev.name)
            box = col.box()
            box.label(text='Iteration count: ' + str(dev.bench_entry.iter_count))

            box = col.box()
            box.label(text='Total packing time: ' + str(dev.bench_entry.total_time) + ' ms')

            box = col.box()
            box.label(text='Average iteration time: ' + str(dev.bench_entry.avg_time) + ' ms')



class UVPM3_PT_Help(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_Help'
    bl_label = 'Hints / Help'
    bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 12000

    def draw_impl(self, context):
        layout = self.layout
        col = layout.column(align=True)

        hints = []

        if self.prefs.thread_count < multiprocessing.cpu_count():
            hints.append("'Thread Count' value is lower than the number of cores in your system - consider increasing that parameter in order to increase the packer speed.")

        if self.scene_props.precision < 200:
            hints.append("Setting 'Precision' to a value lower than 200 is not recommended.")

        if self.scene_props.precision > 1000:
            hints.append("Setting 'Precision' to a value greater than 1000 is usually need only if you want to achieve very small margin between islands - increase the 'Precision' value with care as it may significantly increase packing time.")

        if not self.scene_props.rotation_enable:
            hints.append('Packing will not be optimal with island rotations disabled. Disabling rotations might be reasonable only if you really need to improve the packing speed.')
        else:
            if self.scene_props.rotation_step not in UVPM3_MT_SetRotStepScene.VALUES:
                hints.append("It is usually recommended that the Rotation Step value is a divisor of 90 (or 180 at rare cases). You can use the 'Set' menu, next to the 'Rotation Step' parameter, to choose a step from the set of all recommended values.")

        if self.prefs.FEATURE_island_rotation and self.scene_props.pre_rotation_disable:
            hints.append('Pre-rotation usually optimizes packing, disable it only if you have a good reason.')

        if self.prefs.pack_ratio_supported():
            try:
                ratio = get_active_image_ratio(context)

                if not self.scene_props.tex_ratio and ratio != 1.0:
                    hints.append("The active texture is non-square, but the 'Use Texture Ratio' option is disabled. Did you forget to enable it?")
            except:
                pass

        if self.prefs.advanced_heuristic_available(self.scene_props) and self.scene_props.advanced_heuristic:
            hints.append("'Advanced Hueristic' is useful only for UV maps containing a small number of islands. Read the option description to learn more.")
            
        # if self.prefs.pack_groups_together(self.scene_props) and not self.prefs.heuristic_enabled(self.scene_props):
        #     hints.append('Packing groups together requires the heuristic search to produce an optimal result - it is strongy recommended to enable it.')

        # if self.prefs.pack_groups_together(self.scene_props) and self.prefs.fixed_scale_enabled(self.scene_props):
        #     hints.append("The 'Grouping Compactness' parameter may have a limited impact on the result, when the 'Fixed Scale' option is on.")

        if len(hints) == 0:
            hints.append('No hints for the currently selected parameters')

        col.label(text='Parameter hints:')
        self.messages_in_boxes(col, hints)
