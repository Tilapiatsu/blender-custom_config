# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# source : https://gist.github.com/ithil/ffc48aba19771d6850d1c2fc6a84d6c0

bl_info = {
    "name": "Lock View",
    "description": "Exposes rotation locking in the 3D View to a specific viewing angle",
    "author": "Jason van Gumster (Fweeb)",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "3D View > Properties Region > View",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}

import bpy


def lock_ui(self, context):
    layout = self.layout

    layout.prop(context.space_data.region_3d, 'lock_rotation', text='Lock View Rotation')


def register():
    bpy.types.VIEW3D_PT_view3d_properties.append(lock_ui)


def unregister():
    bpy.types.VIEW3D_PT_view3d_properties.remove(lock_ui)


if __name__ == "__main__":
    register()