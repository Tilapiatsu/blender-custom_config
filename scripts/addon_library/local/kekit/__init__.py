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

from . import box_primitive
from . import _prefs
from . import _m_duplication
from . import _m_main
from . import _m_render
from . import _m_bookmarks
from . import _m_selection
from . import _m_modeling
from . import _m_direct_loop_cut
from . import _m_multicut
from . import _m_subd
from . import _m_unrotator
from . import _m_fitprim
from . import _m_tt
from . import _m_id_materials
from . import _m_cleanup
from . import _m_contexttools
from . import _m_piemenu_ops
from . import ke_cursormenu

bl_info = {
    "name": "keKit",
    "author": "Kjell Emanuelsson",
    "category": "",
    "blender": (2, 80, 0),
    "version": (2, 2, 7),
    "location": "View3D > Sidebar",
    "warning": "",
    "description": "Extensive Script Collection",
    "doc_url": "https://ke-code.xyz/scripts/wiki.html",
}

kit_cat = ""

modules = (
    _prefs,
    box_primitive,
    _m_duplication,
    _m_main,
    _m_render,
    _m_bookmarks,
    _m_selection,
    _m_modeling,
    _m_direct_loop_cut,
    _m_multicut,
    _m_subd,
    _m_unrotator,
    _m_fitprim,
    _m_tt,
    _m_id_materials,
    _m_cleanup,
    _m_contexttools,
    _m_piemenu_ops,
    ke_cursormenu
)


def register():
    _prefs.kekit_version = bl_info['version']
    _prefs.kit_cat = kit_cat
    for m in modules:
        m.register()


def unregister():
    for m in modules:
        m.unregister()


if __name__ == "__main__":
    register()
