
import multiprocessing

from .prefs import get_prefs
from .operator import *
from .operator_islands import *
from .operator_box import *
from .utils import *
from .presets import *
from .labels import UvpLabels
from .register import UVP2_OT_SelectUvpEngine

import bpy


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

        col.separator()
        col.label(text='Option presets:')
        row = col.row(align=True)
        row.operator(UVP2_OT_SavePreset.bl_idname)
        row.operator(UVP2_OT_LoadPreset.bl_idname)
        
        
class UVP2_PT_PackingDeviceBase(UVP2_PT_Generic):
    bl_label = 'Packing Devices'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.template_list("UVP2_UL_DeviceList", "", self.prefs, "dev_array",
                          self.prefs, "sel_dev_idx")

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
        row.prop(self.scene_props, "rot_step")

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

        row = col.row(align=True)
        row.enabled = self.prefs.heuristic_enabled(self.scene_props)
        row.prop(self.scene_props, "heuristic_search_time")

        # Advanced Heuristic
        box = col.box()
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
            col2
            row = col2.row(align=True)
            row.prop(self.scene_props, "tiles_in_row")

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

        # Lock overlapping
        box = col.box()
        row = box.row()
        self.handle_prop("lock_overlapping", self.prefs.FEATURE_lock_overlapping, UvpLabels.FEATURE_NOT_SUPPORTED_MSG, row)

        # Similarity threshold
        row = col.row(align=True)
        row.prop(self.scene_props, "similarity_threshold")
        row.operator(UVP2_OT_SimilarityDetectionHelp.bl_idname, icon='HELP', text='')

        row = col.row(align=True)
        row.operator(UVP2_OT_SelectSimilarOperator.bl_idname, text=UVP2_OT_SelectSimilarOperator.bl_label + demo_suffix)

        row = col.row(align=True)
        row.operator(UVP2_OT_AlignSimilarOperator.bl_idname, text=UVP2_OT_AlignSimilarOperator.bl_label + demo_suffix)

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

        # Pixel Margin Adjust Time
        row = pm_col.row(align=True)
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


class UVP2_PT_WarningsBase(UVP2_PT_Generic):
    bl_label = 'Warnings'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw_specific(self, context):
        layout = self.layout
        col = layout.column(align=True)

        active_dev = self.prefs.dev_array[self.prefs.sel_dev_idx] if self.prefs.sel_dev_idx < len(self.prefs.dev_array) else None
        warnings = []

        if self.prefs.thread_count < multiprocessing.cpu_count():
            warnings.append('Thread Count value is lower than the number of cores in your system - consider increasing that parameter in order to increase the packer speed')

        if not self.scene_props.rot_enable:
            warnings.append('Packing is not optimal for most UV maps with island rotations disabled. Disable rotations only when packing a UV map with a huge number of small islands')

        if self.prefs.FEATURE_island_rotation and self.scene_props.prerot_disable:
            warnings.append('Pre-rotation usually optimizes packing, disable it only if you have a good reason')

        if self.prefs.pack_ratio_supported():
            try:
                ratio = get_active_image_ratio(context)

                if not self.scene_props.tex_ratio and ratio != 1.0:
                    warnings.append("The active texture is non-square, but the 'Use Texture Ratio' option is disabled. Did you forget to enable it?")

                if self.scene_props.tex_ratio and ratio < 1.0:
                    warnings.append('Packing is slower when packing into a vertically oriented texture. Consider changing the texture orientation')
            except:
                pass

        if self.prefs.pixel_margin_enabled(self.scene_props) and self.scene_props.pixel_margin_adjust_time > 1:
            warnings.append("The pixel margin adjustment time set to one second should be enough for a usual UV map. Set the adjustment time to greater values only if the resulting pixel margin after packing is not accurate enough for you.")

        for warn in warnings:
            box = col.box()

            warn_split = split_by_chars(warn, 40)
            if len(warn_split) > 0:
                box.separator()
                for warn_part in warn_split:
                    box.label(text=warn_part)
                box.separator()


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
