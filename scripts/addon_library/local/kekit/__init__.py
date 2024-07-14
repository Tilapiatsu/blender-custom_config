# ##### BEGIN GPL LICENSE BLOCK #####
#
#  keKit - General Tool Kit / Script Collection for Blender
#  Copyright (C) 2023  Kjell Emanuelsson (ke-code.xyz)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see https://www.gnu.org/licenses
#
# ##### END GPL LICENSE BLOCK #####

from . import _prefs
from . import _ui
from . import shared
from . import m_bookmarks
from . import m_cleanup
from . import m_context_tools
from . import m_geometry
from . import m_modeling
from . import m_modifiers
from . import m_pie_menus
from . import m_render
from . import m_selection
from . import m_tt

bl_info = {
    "name": "keKit",
    "author": "Kjell Emanuelsson",
    "category": "",
    "blender": (2, 80, 0),
    "version": (3, 2, 4),
    "location": "View3D > Sidebar",
    "warning": "",
    "description": "Extensive Script Collection - Pro Version",
    "doc_url": "https://ke-code.xyz/scripts/wiki.html",
}

kit_cat = "Pro"

modules = (
    _prefs,
    _ui,
    shared,
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
)


def register():
    # Format version/cat & assign variables
    bv = bl_info['version']
    v = "v" + str(bv[0]) + "." + str(bv[1]) + str(bv[2])
    _ui.kekit_version = v
    _ui.kit_cat = kit_cat
    _prefs.kekit_version = v
    _prefs.kkv = v[1] + v[3] + v[4]

    for m in modules:
        m.register()


def unregister():
    for m in modules:
        m.unregister()
