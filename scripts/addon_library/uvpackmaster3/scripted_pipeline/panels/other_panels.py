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

from ..operators.other_operator import UVPM3_OT_OrientTo3dSpace
from ..modes.other_mode import UVPM3_Mode_Other


class UVPM3_PT_OrientTo3dSpace(UVPM3_PT_SubPanel):

    bl_idname = 'UVPM3_PT_OrientTo3dSpace'
    bl_label = 'Orient UVs To 3D Space'
    # bl_options = {}

    PANEL_PRIORITY = 10000
    ORIENT_TO_3D_SPACE_HELP_URL_SUFFIX = UVPM3_Mode_Other.MODE_HELP_URL_SUFFIX + '/#orient-uvs-to-the-3d-space'

    def draw_axes_to_match(self, prop_name_3d, prop_name_uv, header, layout, *, prop_checker_3d=None):

        col = layout.column(align=True)
        col.label(text=header)
        # box = col.box()
        # col2 = box.column(align=True)
        col2 = col
        box2 = col2.box()
        split = box2.split(factor=0.15, align=True)

        s_col = split.column(align=True)
        row = s_col.row(align=True)
        row.label(text='3D:')

        s_col = split.column(align=True)
        col_flow = s_col.column_flow(columns=3, align=True)
        self.draw_expanded_enum(self.scene_props, prop_name_3d, col_flow, prop_checker_3d)

        box2 = col2.box()
        split = box2.split(factor=0.15, align=True)

        s_col = split.column(align=True)
        row = s_col.row(align=True)
        row.label(text='UV:')

        s_col = split.column(align=True)
        col_flow = s_col.column_flow(columns=4, align=True)
        self.draw_expanded_enum(self.scene_props, prop_name_uv, col_flow)

    def draw_impl(self, context):
        
        layout = self.layout
        col = layout.column(align=True)

        box = col.box()
        self.draw_axes_to_match("orient_prim_3d_axis", "orient_prim_uv_axis", 'Primary Axes To Match:', box)
        self.draw_axes_to_match("orient_sec_3d_axis", "orient_sec_uv_axis", 'Secondary Axes To Match:', box,
                                prop_checker_3d=self.exclude_enum_item_checker(self.scene_props, "orient_prim_3d_axis"))

        self.draw_enum_in_box(self.scene_props, "orient_to_3d_axes_space", Labels.ORIENT_TO_3D_AXES_SPACE_NAME, col, expand=True)

        row = col.row(align=True)
        row.prop(self.scene_props, 'orient_prim_sec_bias')

        col.separator()
        self.operator_with_help(UVPM3_OT_OrientTo3dSpace.bl_idname, col, self.ORIENT_TO_3D_SPACE_HELP_URL_SUFFIX)

