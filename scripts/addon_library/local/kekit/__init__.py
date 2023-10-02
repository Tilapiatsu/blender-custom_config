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

from . import _prefs
from . import _ui
from .m_bookmarks import m_bookmarks
from .m_cleanup import m_cleanup
from .m_context_tools import m_context_tools
from .m_cursormenu import m_cursormenu
from .m_geometry import m_geometry
from .m_modeling import m_modeling
from .m_modifiers import m_modifiers
from .m_pie_menus import m_pie_menus
from .m_render import m_render
from .m_selection import m_selection
from .m_tt import m_tt

bl_info = {
    "name": "keKit",
    "author": "Kjell Emanuelsson",
    "category": "",
    "blender": (2, 80, 0),
    "version": (3, 0, 1),
    "location": "View3D > Sidebar",
    "warning": "",
    "description": "Extensive Script Collection",
    "doc_url": "https://ke-code.xyz/scripts/wiki.html",
}

kit_cat = ""

modules = (
    _prefs,
    _ui,
    m_geometry,
    m_render,
    m_bookmarks,
    m_selection,
    m_modeling,
    m_modifiers,
    m_context_tools,
    m_tt,
    m_cleanup,
    m_pie_menus,
    m_cursormenu
)


def register():
    # Format version/cat & assign variables
    bv = bl_info['version']
    v = "v" + str(bv[0]) + "." + str(bv[1]) + str(bv[2])
    _ui.kekit_version = v
    _ui.kit_cat = kit_cat
    _prefs.kekit_version = v

    for m in modules:
        m.register()


def unregister():
    for m in modules:
        m.unregister()
