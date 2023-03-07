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



class UVPM3_PT_SimilarityOptions(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_SimilarityOptions'
    bl_label = 'Similarity Options'
    # bl_options = {}

    PANEL_PRIORITY = 2000


    def draw_impl(self, context):

        layout = self.layout
        col = layout.column(align=True)

        mode_col = self.draw_enum_in_box(self.scene_props, "simi_mode", Labels.SIMI_MODE_NAME, col)

        if UvpmSimilarityMode.is_vertex_based(self.scene_props.simi_mode):
            box = mode_col.box()
            row = box.row()
            row.prop(self.scene_props, 'simi_correct_vertices')

            row = mode_col.row(align=True)
            row.prop(self.scene_props, 'simi_vertex_threshold')

        else:
            mode_col.prop(self.scene_props, "precision")

            row = mode_col.row(align=True)
            row.prop(self.scene_props, 'simi_threshold')

        box = col.box()
        row = box.row(align=True)
        row.prop(self.scene_props, 'flipping_enable')

        box = col.box()
        row = box.row(align=True)
        row.prop(self.scene_props, 'simi_adjust_scale')

        match_col = self.draw_enum_in_box(self.scene_props, "simi_match_3d_axis", Labels.SIMI_MATCH_3D_AXIS_NAME, col, expand=True)
        match_space_col = self.draw_enum_in_box(self.scene_props, "simi_match_3d_axis_space", '', match_col, expand=True)
        match_space_col.enabled = self.scene_props.simi_match_3d_axis != UvpmAxis.NONE.code

        # col.separator()



class AlignPriorityIParamEditUI(IParamEditUI):

    HELP_URL_SUFFIX = '40-miscellaneous-modes/10-aligning-tools#align-priority'
    OPERATOR_PREFIX = 'AlignPriority'
    ENABLED_PROP_NAME = 'align_priority_enable'
    

class UVPM3_PT_AlignPriority(UVPM3_PT_IParamEdit):

    bl_idname = 'UVPM3_PT_AlignPriority'
    bl_label = 'Align Priority'
    # bl_options = {'DEFAULT_CLOSED'}

    PANEL_PRIORITY = 3000
    IPARAM_EDIT_UI = AlignPriorityIParamEditUI
