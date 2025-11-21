# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Tila Config Manager",
    "author" : "Tilapiatsu",
    "description" : "",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Preferences"
}

from .dependencies.dependencies import Dependencies

def register():
    Dependencies.install()
    from Tila_ConfigManager import preferences
    from Tila_ConfigManager import operators
    modules =   (	preferences,
                    operators
                )
    for m in modules:
        m.register()


def unregister():
    from Tila_ConfigManager import preferences
    from Tila_ConfigManager import operators
    modules =   (	preferences,
                    operators
                )
    for m in reversed(modules):
        m.unregister()
    
if __name__ == "__main__":
    register()