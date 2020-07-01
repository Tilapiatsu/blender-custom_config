# -*- coding:utf-8 -*-

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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110- 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# ----------------------------------------------------------
# Author: Stephen Leger (s-leger)
#
# ----------------------------------------------------------


bl_info = {
    'name': 'CAD Transform',
    'description': 'Cad like transform',
    'author': '<s-leger> support@blender-archipack.org',
    'license': 'GPL',
    'deps': '',
    'blender': (2, 80, 0),
    'version': (0, 0, 8),
    'location': 'View3D > Tools > Cad',
    'warning': '',
    'wiki_url': 'https://github.com/s-leger/blender_cad_transforms/wiki',
    'tracker_url': 'https://github.com/s-leger/blender_cad_transforms/issues',
    'link': 'https://github.com/s-leger/blender_cad_transforms',
    'support': 'COMMUNITY',
    'category': '3D View'
    }

__author__ = bl_info['author']
__version__ = ".".join(map(str, bl_info['version']))


if "slcad_transform" in locals():
    pass

else:
    from .slcad_transform import register, unregister


if __name__ == "__main__":
    register()
