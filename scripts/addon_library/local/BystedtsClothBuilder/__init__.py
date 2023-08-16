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
    "name" : "Bystedts Cloth Builder",
    "author" : "Daniel Bystedt",    
    "description" : "Addon for cloth creation and simulation",
    "blender" : (3, 6, 0),
    "version" : (1, 0, 1),
    "location" : "View3D > Sidebar",
    "warning" : "",
    "support": "COMMUNITY",
    "category" : "Simulation",
    "doc_url": "",
}

import bpy
import importlib

########## TEMP CLEAR CONSOLE ##############
import os
os.system('clear')
########## TEMP CLEAR CONSOLE ##############

addon_folder = 'BystedtsClothBuilder'

# MODULES=======================
# Modules that should be reloaded with blenders [reload scripts] goes here
# It's very convinient for all modules to be listed here during addon development


modules = (
    '.addon',
    '.ui',
    '.simulation',
)


def import_modules():
    for mod in modules:
        print("importing " + str(mod))
        importlib.import_module(mod, addon_folder)

def reimport_modules():
    '''
    Reimports the modules. Extremely useful while developing the addon
    '''
    for mod in modules:
        # Reimporting modules during addon development
        want_reload_module = importlib.import_module(mod, addon_folder)
        importlib.reload(want_reload_module)   

import_modules()
reimport_modules()

from . import addon
from . import ui
from . import simulation

def register():

    import_modules()  
    addon.register()
    ui.register()
    simulation.register()
    

    # Sybren example
    # https://docs.blender.org/api/master/bpy.props.html#collection-example
    # Use collection properties instad
    #bpy.types.Scene.BBB_props = bpy.props.PointerProperty(type = UI.RENDER_PG_bystedts_blender_baker)   
    
    

def unregister():  
    addon.unregister()
    ui.unregister()
    simulation.remove_asset_browser_from_preferences(bpy.context)
    