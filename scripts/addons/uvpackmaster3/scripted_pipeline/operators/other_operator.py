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


from ...enums import UvpmCoordSpace
from ...operator import UVPM3_OT_Engine, ModeIdAttributeMixin
from ...prefs_scripted_utils import ScriptParams


class UVPM3_OT_OrientTo3dSpace(UVPM3_OT_Engine):

    bl_idname = 'uvpackmaster3.orient_to_3d_space'
    bl_label = 'Orient UVs'
    bl_description = "Rotate every selected UV island so that the resulting mapping transforms a given 3D axis to a given UV axis. Click the help button for more info"

    SCENARIO_ID = 'other.orient_to_3d_space'

    def skip_topology_parsing(self):
        return True
    
    def send_verts_3d(self):
        return self.scene_props.orient_to_3d_axes_space == UvpmCoordSpace.LOCAL.code

    def send_verts_3d_global(self):
        return self.scene_props.orient_to_3d_axes_space == UvpmCoordSpace.GLOBAL.code

    def setup_script_params(self):

        script_params = ScriptParams()

        script_params.add_param('prim_3d_axis', self.scene_props.orient_prim_3d_axis)
        script_params.add_param('prim_uv_axis', self.scene_props.orient_prim_uv_axis)
        script_params.add_param('sec_3d_axis', self.scene_props.orient_sec_3d_axis)
        script_params.add_param('sec_uv_axis', self.scene_props.orient_sec_uv_axis)
        script_params.add_param('axes_space', self.scene_props.orient_to_3d_axes_space)
        
        script_params.add_param('prim_sec_bias', self.scene_props.orient_prim_sec_bias)

        return script_params
