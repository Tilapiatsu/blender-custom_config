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


import multiprocessing

from .prefs import get_prefs
from .operator import *
from .operator_islands import *
from .operator_box import *
from .operator_uv import *
from .utils import *
from .presets import *
from .labels import UvpLabels
from .register import UVP2_OT_SelectUvpEngine

import bpy



class UVP2_OT_SetRotStep(bpy.types.Operator):

    bl_idname = 'uvpackmaster2.set_rot_step'
    bl_label = 'Set Rotation Step'
    bl_description = "Set Rotation Step to one of the suggested values"

    rot_step = IntProperty(
        name='Rotation Step',
        description='',
        default=90)


    def execute(self, context):
        
        scene_props = context.scene.uvp2_props
        scene_props.rot_step = self.rot_step
        return {'FINISHED'}
    

class UVP2_MT_SetRotStep(bpy.types.Menu):

    bl_idname = "UVP2_MT_SetRotStep"
    bl_label = "Set Rotation Step"

    STEPS = [1, 2, 3, 5, 6, 9, 10, 15, 18, 30, 45, 90, 180]

    def draw(self, context):

        layout = self.layout

        for step in self.STEPS:
            operator = layout.operator(UVP2_OT_SetRotStep.bl_idname, text=str(step))
            operator.rot_step = step


class UVP2_UL_DeviceList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        dev_name = str(item.name)

        row = layout.row()
        icon_id = 'NONE'

        if not item.supported:
            dev_name += ' ' + UvpLabels.FEATURE_NOT_SUPPORTED_MSG
            icon_id = UvpLabels.FEATURE_NOT_SUPPORTED_ICON

        row.label(text=dev_name, icon=icon_id)


class UVP2_PT_Generic(bpy.types.Panel):

    def draw(self, context):

        self.prefs = get_prefs()
        self.scene_props = context.scene.uvp2_props
        
        self.draw_specific(context)


    def handle_prop(self, prop_name, supported, not_supported_msg, ui_elem):

        if supported:
            ui_elem.prop(self.scene_props, prop_name)
        else:
            ui_elem.enabled = False
            split = ui_elem.split(factor=0.4)
            col_s = split.column()
            col_s.prop(self.scene_props, prop_name)
            col_s = split.column()
            col_s.label(text=not_supported_msg)

    def handle_prop_enum(self, prop_name, prop_label, supported, not_supported_msg, ui_elem):

        prop_label_colon = prop_label + ':'

        if supported:
            ui_elem.label(text=prop_label_colon)
        else:
            split = ui_elem.split(factor=0.4)
            col_s = split.column()
            col_s.label(text=prop_label_colon)
            col_s = split.column()
            col_s.label(text=not_supported_msg)

        ui_elem.prop(self.scene_props, prop_name, text='')
        ui_elem.enabled = supported

    def messages_in_boxes(self, ui_elem, messages):

        for msg in messages:
            box = ui_elem.box()

            msg_split = split_by_chars(msg, 60)
            if len(msg_split) > 0:
                # box.separator()
                for msg_part in msg_split:
                    box.label(text=msg_part)
                # box.separator()


class UVP2_PT_MainBase(UVP2_PT_Generic):
    bl_idname = 'UVP2_PT_MainBase'
    bl_label = 'UVPackmaster2'
    bl_context = ''

    def draw_specific(self, context):
        layout = self.layout
        demo_suffix = " (DEMO)" if self.prefs.FEATURE_demo else ''

        row = layout.row()
        row.label(text=self.prefs.label_message)

        if not self.prefs.uvp_initialized:
            row.operator(UVP2_OT_UvpSetupHelp.bl_idname, icon='HELP', text='')

        row = layout.row()

        row2 = row.row()
        row2.enabled = False
        row2.prop(self.prefs, 'uvp_path')
        select_icon = 'FILEBROWSER' if is_blender28() else 'FILE_FOLDER'
        row.operator(UVP2_OT_SelectUvpEngine.bl_idname, icon=select_icon, text='')

        col = layout.column(align=True)
        col.separator()

        if in_debug_mode():
            box = col.box()
            col2 = box.column(align=True)
            col2.label(text="Debug options:")
            row = col2.row(align=True)
            row.prop(self.prefs, "write_to_file")
            row = col2.row(align=True)
            row.prop(self.prefs, "simplify_disable")
            row = col2.row(align=True)
            row.prop(self.prefs, "wait_for_debugger")
            row = col2.row(align=True)
            row.prop(self.prefs, "seed")
            row = col2.row(align=True)
            row.prop(self.prefs, "test_param")
            col.separator()

        col.label(text="Engine operations:")
        row = col.row(align=True)
        row.enabled = self.prefs.FEATURE_overlap_check

        row.operator(UVP2_OT_OverlapCheckOperator.bl_idname)
        if not self.prefs.FEATURE_overlap_check:
            row.label(text=UvpLabels.FEATURE_NOT_SUPPORTED_MSG)

        col.operator(UVP2_OT_MeasureAreaOperator.bl_idname)

        # Validate operator

        row = col.row(align=True)
        row.enabled = self.prefs.FEATURE_validation

        row.operator(UVP2_OT_ValidateOperator.bl_idname, text=UVP2_OT_ValidateOperator.bl_label + demo_suffix)
        if not self.prefs.FEATURE_validation:
            row.label(text=UvpLabels.FEATURE_NOT_SUPPORTED_MSG)

        row = col.row(align=True)
        row.scale_y = 1.75
        row.operator(UVP2_OT_PackOperator.bl_idname, text=UVP2_OT_PackOperator.bl_label + demo_suffix)

        col.label(text="Last operation status:")
        box = col.box()
        box.label(text=self.prefs['op_status'] if self.prefs['op_status'] is not '' else '------')
        col.separator()

        if len(self.prefs['op_warnings']) > 0:
            row = col.row()
            row.label(text="WARNINGS:", icon=UvpLabels.FEATURE_NOT_SUPPORTED_ICON)
            self.messages_in_boxes(col, self.prefs['op_warnings'])
            col.separator()

        col.separator()

        col.label(text="Other operations:")
        row = col.row(align=True)
        row.operator(UVP2_OT_SplitOverlappingIslands.bl_idname)
        
        row = col.row(align=True)
        row.operator(UVP2_OT_UndoIslandSplit.bl_idname)
        
        row = col.row(align=True)
        row.operator(UVP2_OT_AdjustScaleToUnselected.bl_idname)
        
        if in_debug_mode():
            row = col.row(align=True)
            row.operator(UVP2_OT_DebugIslands.bl_idname)

        col.separator()
        col.label(text='Option presets:')
        row = col.row(align=True)
        row.operator(UVP2_OT_SavePreset.bl_idname)
        row.operator(UVP2_OT_LoadPreset.bl_idname)

        row = col.row(align=True)
        row.operator(UVP2_OT_ResetToDefaults.bl_idname)
        
        
class UVP2_PT_PackingDeviceBase(UVP2_PT_Generic):
    bl_label = 'Packing Devices'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.template_list("UVP2_UL_DeviceList", "", self.prefs, "dev_array",
                          self.prefs, "sel_dev_idx")

        box = col.box()
        box.label(text=UvpLabels.PACKING_DEVICE_WARNING)
        box.enabled = False

        # Multi device
        box = col.box()
        box.enabled = self.prefs.FEATURE_multi_device_pack

        row = box.row()
        self.handle_prop("multi_device_pack", self.prefs.FEATURE_multi_device_pack, UvpLabels.FEATURE_NOT_SUPPORTED_MSG, row)


class UVP2_PT_BasicOptionsBase(UVP2_PT_Generic):
    bl_label = 'Basic Options'
    bl_context = ''

    def draw_specific(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.prop(self.prefs, "thread_count")
        col.prop(self.scene_props, "margin")
        col.prop(self.scene_props, "precision")

        # Rotation Resolution
        box = col.box()
        box.enabled = self.prefs.FEATURE_island_rotation

        row = box.row()
        # TODO: missing feature check
        row.prop(self.scene_props, "rot_enable")

        row = box.row()
        row.enabled = self.scene_props.rot_enable
        row.prop(self.scene_props, "prerot_disable")

        row = col.row(align=True)
        row.enabled = self.scene_props.rot_enable

        split = row.split(factor=0.8, align=True)

        col_s = split.row(align=True)
        col_s.prop(self.scene_props, "rot_step")

        col_s = split.row(align=True)
        col_s.menu(UVP2_MT_SetRotStep.bl_idname, text='Set')

        # Pre validate
        pre_validate_name = UvpLabels.PRE_VALIDATE_NAME
        if self.prefs.FEATURE_demo:
            pre_validate_name += ' (DEMO)'

        box = col.box()
        box.enabled = self.prefs.FEATURE_validation
        row = box.row()
        self.handle_prop("pre_validate", self.prefs.FEATURE_validation, UvpLabels.FEATURE_NOT_SUPPORTED_MSG, row)


class UVP2_PT_IslandRotStepBase(UVP2_PT_Generic):
    bl_label = 'Island Rotation Step'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout

        panel_enabled = True

        if not self.prefs.FEATURE_island_rotation_step:
            layout.label(text=UvpLabels.FEATURE_NOT_SUPPORTED_MSG)
            panel_enabled = False
        elif not self.scene_props.rot_enable:
            layout.label(text='Island rotations must be enabled to activate this panel', icon='ERROR')
            panel_enabled = False

        col = layout.column(align=True)
        col.enabled = panel_enabled

        box = col.box()
        row = box.row()
        row.prop(self.scene_props, "island_rot_step_enable")
        row.operator(UVP2_OT_IslandRotStepHelp.bl_idname, icon='HELP', text='')

        box = col.box()
        box.enabled = self.scene_props.island_rot_step_enable
        col2 = box.column(align=True)

        row = col2.row(align=True)
        row.prop(self.scene_props, "island_rot_step")

        row = col2.row(align=True)
        row.operator(UVP2_OT_SetRotStepIslandParam.bl_idname)

        col2.separator()
        row = col2.row(align=True)
        row.operator(UVP2_OT_ResetRotStepIslandParam.bl_idname)

        row = col2.row(align=True)
        row.operator(UVP2_OT_ShowRotStepIslandParam.bl_idname)


class UVP2_PT_ManualGroupingBase(UVP2_PT_Generic):
    bl_label = 'Manual Grouping'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout

        panel_enabled = True

        if not self.prefs.FEATURE_grouping:
            layout.label(text=UvpLabels.FEATURE_NOT_SUPPORTED_MSG)
            panel_enabled = False

        col = layout.column(align=True)
        col.enabled = panel_enabled

        container = col

        row = container.row(align=True)
        row.prop(self.scene_props, "manual_group_num")
        row.operator(UVP2_OT_ManualGroupingHelp.bl_idname, icon='HELP', text='')

        row = container.row(align=True)
        row.operator(UVP2_OT_SetManualGroupIslandParam.bl_idname)
        container.separator()

        container.label(text="Select islands assigned to a group:")
        row = container.row(align=True)

        op = row.operator(UVP2_OT_SelectManualGroupIslandParam.bl_idname, text="Select")
        op.select = True
        op = row.operator(UVP2_OT_SelectManualGroupIslandParam.bl_idname, text="Deselect")
        op.select = False

        # container.separator()
        # row = container.row(align=True)
        # row.operator(UVP2_OT_ResetManualGroupIslandParam.bl_idname)

        row = container.row(align=True)
        row.operator(UVP2_OT_ShowManualGroupIslandParam.bl_idname)


class UVP2_PT_HeuristicBase(UVP2_PT_Generic):
    bl_label = 'Heuristic'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout

        heurstic_supported, not_supported_msg = self.prefs.heuristic_supported(self.scene_props)

        col = layout.column(align=True)
        col.enabled = heurstic_supported

        # Heuristic search
        box = col.box()
        box.enabled = self.prefs.FEATURE_heuristic_search

        row = box.row()
        self.handle_prop("heuristic_enable", heurstic_supported, not_supported_msg, row)
        row.operator(UVP2_OT_HeuristicSearchHelp.bl_idname, icon='HELP', text='')

        col2 = col.column(align=True)
        col2.enabled = self.prefs.heuristic_enabled(self.scene_props)

        row = col2.row(align=True)
        row.prop(self.scene_props, "heuristic_search_time")
        row = col2.row(align=True)
        row.prop(self.scene_props, "heuristic_max_wait_time")

        # Advanced Heuristic
        box = col2.box()
        box.enabled = self.prefs.advanced_heuristic_available(self.scene_props)
        row = box.row()
        self.handle_prop("advanced_heuristic", self.prefs.FEATURE_advanced_heuristic, UvpLabels.FEATURE_NOT_SUPPORTED_MSG, row)
        

class UVP2_PT_NonSquarePackingBase(UVP2_PT_Generic):
    bl_label = 'Non-Square Packing'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout
        col = layout.column(align=True)

        # Tex ratio
        box = col.box()
        row = box.row()
        self.handle_prop("tex_ratio", self.prefs.pack_ratio_supported(), UvpLabels.FEATURE_NOT_SUPPORTED_MSG, row)

        col.separator()
        row = col.row(align=True)
        row.operator(UVP2_OT_AdjustIslandsToTexture.bl_idname)
        row.operator(UVP2_OT_NonSquarePackingHelp.bl_idname, icon='HELP', text='')

        row = col.row(align=True)
        row.operator(UVP2_OT_UndoIslandsAdjustemntToTexture.bl_idname)

class UVP2_PT_AdvancedOptionsBase(UVP2_PT_Generic):
    bl_label = 'Advanced Options'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout

        demo_suffix = " (DEMO)" if self.prefs.FEATURE_demo else ''
        col = layout.column(align=True)

        # Grouped pack
        box = col.box()

        col2 = box.column(align=True)
        col2.label(text=UvpLabels.PACK_MODE_NAME + ':')
        row = col2.row(align=True)

        row.prop(self.scene_props, "pack_mode", text='')

        if self.prefs.tiles_enabled(self.scene_props):
            row.operator(UVP2_OT_UdimSupportHelp.bl_idname, icon='HELP', text='')
            
        if self.prefs.pack_to_tiles(self.scene_props):
            row = col2.row(align=True)
            row.prop(self.scene_props, "tile_count")

        if self.prefs.tiles_enabled(self.scene_props):
            row = col2.row(align=True)
            row.prop(self.scene_props, "tiles_in_row")

        if self.prefs.pack_groups_together(self.scene_props):
            row = col2.row(align=True)
            row.prop(self.scene_props, "group_compactness")

        if self.prefs.grouping_enabled(self.scene_props):
            box = col.box()
            col2 = box.column()
            col2.label(text=UvpLabels.GROUP_METHOD_NAME + ':')

            row = col2.row(align=True)
            row.prop(self.scene_props, "group_method", text='')

            if self.scene_props.group_method == UvGroupingMethod.MANUAL.code:
                row.operator(UVP2_OT_ManualGroupingHelp.bl_idname, icon='HELP', text='')
                
            # col2.separator()

        # Pack to others
        box = col.box()
        pto_supported, pto_not_supported_msg = self.prefs.pack_to_others_supported(self.scene_props)

        row = box.row()
        self.handle_prop("pack_to_others", pto_supported, pto_not_supported_msg, row)

        # Fixed Scale
        box = col.box()
        fs_supported, fs_not_supported_msg = self.prefs.fixed_scale_supported(self.scene_props)

        row = box.row()
        self.handle_prop("fixed_scale", fs_supported, fs_not_supported_msg, row)

        # Normalize islands
        box = col.box()
        norm_supported, norm_not_supported_msg = self.prefs.normalize_islands_supported(self.scene_props)

        row = box.row()
        self.handle_prop("normalize_islands", norm_supported, norm_not_supported_msg, row)

        # Lock overlapping
        box = col.box()
        col2 = box.column()
        self.handle_prop_enum("lock_overlapping_mode", UvpLabels.LOCK_OVERLAPPING_MODE_NAME, self.prefs.FEATURE_lock_overlapping, UvpLabels.FEATURE_NOT_SUPPORTED_MSG, col2)

        # Similarity threshold
        row = col.row(align=True)
        row.prop(self.scene_props, "similarity_threshold")
        row.operator(UVP2_OT_SimilarityDetectionHelp.bl_idname, icon='HELP', text='')

        row = col.row(align=True)
        row.operator(UVP2_OT_SelectSimilar.bl_idname, text=UVP2_OT_SelectSimilar.bl_label + demo_suffix)

        row = col.row(align=True)
        row.operator(UVP2_OT_AlignSimilar.bl_idname, text=UVP2_OT_AlignSimilar.bl_label + demo_suffix)

        col.separator()
        col.label(text='Pixel Margin Options:')

        # Pixel margin
        row = col.row(align=True)
        row.prop(self.scene_props, "pixel_margin")
        row.operator(UVP2_OT_PixelMarginHelp.bl_idname, icon='HELP', text='')

        pm_col = col.column(align=True)
        pm_col.enabled = self.prefs.pixel_margin_enabled(self.scene_props)

        # Pixel padding
        row = pm_col.row(align=True)
        row.prop(self.scene_props, "pixel_padding")

        # Pixel margin method
        pix_method_enabled, pix_method_msg = self.prefs.pixel_margin_method_enabled(self.scene_props)

        box = pm_col.box()
        box.enabled = pix_method_enabled

        col2 = box.column(align=True)
        # col2.label(text=UvpLabels.PIXEL_MARGIN_METHOD_NAME + ':')

        if not pix_method_enabled:
            split = col2.split(factor=0.3)
            row = split.column()
            # row = col2.row(align=True)
            row.label(text='Method:')

            row = split.column()
            row.label(text=pix_method_msg)
        else:
            row = col2.row(align=True)
            row.label(text='Method:')

        row = col2.row(align=True)
        row.prop(self.scene_props, "pixel_margin_method", text='')

        # Pixel Margin Adjust Time
        if self.prefs.pixel_margin_adjust_time_enabled(self.scene_props):
            row = col2.row(align=True)
            row.prop(self.scene_props, "pixel_margin_adjust_time")

        # Pixel Margin Tex Size
        row = pm_col.row(align=True)
        row.prop(self.scene_props, "pixel_margin_tex_size")

        if self.prefs.pack_ratio_enabled(self.scene_props):
            row.enabled = False
            pm_col.label(text='Active texture dimensions are used to calculate pixel margin', icon='ERROR')


class UVP2_PT_TargetBoxBase(UVP2_PT_Generic):
    bl_label = 'Packing Box'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.enabled = self.prefs.FEATURE_target_box

        row = col.row(align=True)
        if self.prefs.target_box_enable:
            row.operator(UVP2_OT_DisableTargetBox.bl_idname)
        else:
            row.operator(UVP2_OT_EnableTargetBox.bl_idname)

        if not self.prefs.FEATURE_target_box:
            row.label(text=UvpLabels.FEATURE_NOT_SUPPORTED_MSG)

        box = col.box()
        box.enabled = self.prefs.target_box_enable
        col2 = box.column(align=True)

        row = col2.row(align=True)
        row.operator(UVP2_OT_DrawTargetBox.bl_idname)

        row = col2.row(align=True)
        row.operator(UVP2_OT_LoadTargetBox.bl_idname)


        col2.separator()
        col2.label(text='Set packing box to UDIM tile:')
        row = col2.row(align=True)
        row.prop(self.scene_props, "target_box_tile_x")
        row.prop(self.scene_props, "target_box_tile_y")

        row = col2.row(align=True)
        row.operator(UVP2_OT_SetTargetBoxTile.bl_idname)
        
        col2.separator()
        col2.label(text='Islands inside box:')

        row = col2.row(align=True)
        row.operator(UVP2_OT_SelectIslandsInsideTargetBox.bl_idname, text="Select").select = True
        row.operator(UVP2_OT_SelectIslandsInsideTargetBox.bl_idname, text="Deselect").select = False

        box = col2.box()
        box.prop(self.scene_props, "fully_inside")

        col2.separator()
        col2.label(text='Move packing box to adjacent tile:')

        row = col2.row(align=True)

        col3 = row.column(align=True)
        op = col3.operator(UVP2_OT_MoveTargetBoxTile.bl_idname, text="↖")
        op.dir_x = -1
        op.dir_y = 1
        op = col3.operator(UVP2_OT_MoveTargetBoxTile.bl_idname, text="←")
        op.dir_x = -1
        op.dir_y = 0
        op = col3.operator(UVP2_OT_MoveTargetBoxTile.bl_idname, text="↙")
        op.dir_x = -1
        op.dir_y = -1

        col3 = row.column(align=True)
        op = col3.operator(UVP2_OT_MoveTargetBoxTile.bl_idname, text="↑")
        op.dir_x = 0
        op.dir_y = 1
        col3.label(text="")
        op = col3.operator(UVP2_OT_MoveTargetBoxTile.bl_idname, text="↓")
        op.dir_x = 0
        op.dir_y = -1

        col3 = row.column(align=True)
        op = col3.operator(UVP2_OT_MoveTargetBoxTile.bl_idname, text="↗")
        op.dir_x = 1
        op.dir_y = 1
        op = col3.operator(UVP2_OT_MoveTargetBoxTile.bl_idname, text="→")
        op.dir_x = 1
        op.dir_y = 0
        op = col3.operator(UVP2_OT_MoveTargetBoxTile.bl_idname, text="↘")
        op.dir_x = 1
        op.dir_y = -1

        box = col2.box()
        box.prop(self.scene_props, "move_islands")

        col2.separator()
        col2.label(text='Packing box coordinates:')
        row = col2.row(align=True)
        row.prop(self.scene_props, "target_box_p1_x")

        row = col2.row(align=True)
        row.prop(self.scene_props, "target_box_p1_y")

        row = col2.row(align=True)
        row.prop(self.scene_props, "target_box_p2_x")

        row = col2.row(align=True)
        row.prop(self.scene_props, "target_box_p2_y")


class UVP2_PT_HintsBase(UVP2_PT_Generic):
    bl_label = 'Hints'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout
        col = layout.column(align=True)

        hints = []

        if self.prefs.thread_count < multiprocessing.cpu_count():
            hints.append("'Thread Count' value is lower than the number of cores in your system - consider increasing that parameter in order to increase the packer speed.")

        if self.scene_props.precision < 200:
            hints.append("Setting 'Precision' to a value lower than 200 is not recommended.")

        if self.scene_props.precision > 1000:
            hints.append("Setting 'Precision' to a value greater than 1000 is usually need only if you want to achieve very small margin between islands - increase the 'Precision' value with care as it may significantly increase packing time.")

        if not self.scene_props.rot_enable:
            hints.append('Packing will not be optimal with island rotations disabled. Disabling rotations might be reasonable only if you really need to improve the packing speed.')
        else:
            if self.scene_props.rot_step not in UVP2_MT_SetRotStep.STEPS:
                hints.append("It is usually recommended that the Rotation Step value is a divisor of 90 (or 180 at rare cases). You can use the 'Set' menu, next to the 'Rotation Step' parameter, to choose a step from the set of all recommended values.")

        if self.prefs.FEATURE_island_rotation and self.scene_props.prerot_disable:
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

        if self.prefs.pixel_margin_enabled(self.scene_props) and self.prefs.pixel_margin_method_enabled(self.scene_props)[0]:
            
            if self.prefs.pixel_margin_adjust_time_enabled(self.scene_props) and self.scene_props.pixel_margin_adjust_time > 1:
                hints.append("The pixel margin adjustment time set to 1 second should be enough for a usual UV map. Set the adjustment time to greater values only if the resulting pixel margin after packing is not accurate enough for you.")

            if self.prefs.pixel_margin_iterative_enabled(self.scene_props):
                hints.append("'Adjustment Time' is the recommended method for determing pixel margin. Use the 'Iterative' method only if you really need to.")

        if self.prefs.pack_groups_together(self.scene_props) and not self.prefs.heuristic_enabled(self.scene_props):
            hints.append('Packing groups together requires the heuristic search to produce an optimal result - it is strongy recommended to enable it.')

        if self.prefs.pack_groups_together(self.scene_props) and self.prefs.fixed_scale_enabled(self.scene_props):
            hints.append("The 'Grouping Compactness' parameter may have a limited impact on the result, when the 'Fixed Scale' option is on.")

        if len(hints) == 0:
            hints.append('No hints for currently selected parameters')

        col.label(text='Parameter hints:')
        self.messages_in_boxes(col, hints)


class UVP2_PT_StatisticsBase(UVP2_PT_Generic):
    bl_label = 'Statistics'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text='Last operation statistics:')
        col.separator()

        if self.prefs.stats_area >= 0.0:
            box = col.box()
            box.label(text='Area: ' + str(round(self.prefs.stats_area, 3)))

        for idx, stats in enumerate(self.prefs.stats_array):
            col.separator()
            col.label(text=stats.dev_name)
            box = col.box()
            box.label(text='Iteration count: ' + str(stats.iter_count))

            box = col.box()
            box.label(text='Total packing time: ' + str(stats.total_time) + ' ms')

            box = col.box()
            box.label(text='Average iteration time: ' + str(stats.avg_time) + ' ms')

class UVP2_PT_HelpBase(UVP2_PT_Generic):
    bl_label = 'Help'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout

        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator(UVP2_OT_UvpSetupHelp.bl_idname, icon='HELP', text='UVP Setup')
        row = col.row(align=True)
        row.operator(UVP2_OT_HeuristicSearchHelp.bl_idname, icon='HELP', text='Heuristic Search')
        row = col.row(align=True)
        row.operator(UVP2_OT_UdimSupportHelp.bl_idname, icon='HELP', text='UDIM Support')
        row = col.row(align=True)
        row.operator(UVP2_OT_ManualGroupingHelp.bl_idname, icon='HELP', text='Manual Grouping')
        row = col.row(align=True)
        row.operator(UVP2_OT_NonSquarePackingHelp.bl_idname, icon='HELP', text='Non-Square Packing')
        row = col.row(align=True)
        row.operator(UVP2_OT_SimilarityDetectionHelp.bl_idname, icon='HELP', text='Similarity Detection')
        row = col.row(align=True)
        row.operator(UVP2_OT_PixelMarginHelp.bl_idname, icon='HELP', text='Pixel Margin')
        row = col.row(align=True)
        row.operator(UVP2_OT_IslandRotStepHelp.bl_idname, icon='HELP', text='Island Rotation Step')
        row = col.row(align=True)
        row.operator(UVP2_OT_InvalidTopologyHelp.bl_idname, icon='HELP', text='Invalid Topology')
