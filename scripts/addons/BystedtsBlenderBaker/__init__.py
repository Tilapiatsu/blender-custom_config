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
    "name" : "Bystedts Blender Baker",
    "author" : "Daniel Bystedt",    
    "description" : "Simplify Blender baking workflow",
    "blender" : (2, 93, 0),
    "version" : (1, 0, 0),
    "location" : "View3D > Sidebar",
    "warning" : "",
    "support": "COMMUNITY",
    "category" : "Render",
    "doc_url": "",
}

import bpy
import importlib

addon_folder = 'BystedtsBlenderBaker'

# MODULES=======================
# Modules that should be reloaded with blenders [reload scripts] goes here
# It's very convinient for all modules to be listed here during addon development


modules = (
    '.addon',
    '.bake_manager',
    '.high_res_objects_manager',
    '.image_manager',
    '.custom_properties',
    '.debug',
    '.object_manager',
    '.settings_manager',
    '.UI',
    '.uv_manager',
    '.composit_manager',
    '.bake_passes',
    '.material_preview_manager',
    '.collection_manager',
    '.operator_manager',
    '.scene_manager',
    '.viewport_manager',
    '.file_manager',
    '.mesh_manager',
    '.bound_box_manager'
)


def import_modules():
    for mod in modules:
        #print('importing with importlib.import_module =' + str(mod) + "=")
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

from . import custom_properties
from . import addon
from . import high_res_objects_manager
from . import image_manager
from . import debug 
from . import UI
from . import bake_manager
from . import bake_passes
from . import material_preview_manager
from . import collection_manager
from . import viewport_manager
from . import file_manager
from . import mesh_manager
from . import scene_manager
from . import bound_box_manager


''''''
def register():

    import_modules()  
    addon.register()
    high_res_objects_manager.register()
    debug.register()
    bake_passes.register()
    collection_manager.register()
    UI.register()
    material_preview_manager.register()

    pass

    # Sybren example
    # https://docs.blender.org/api/master/bpy.props.html#collection-example
    # TODO: bpy.types.Scene.bake_passes = bpy.props.CollectionProperty(type=YourPropertyGroupType)
    # Use collection properties instad
    #bpy.types.Scene.BBB_props = bpy.props.PointerProperty(type = UI.RENDER_PG_bystedts_blender_baker)   
    
    

def unregister():
    

    del bpy.types.Scene.BBB_props
    
    material_preview_manager.unregister()    
    UI.unregister()
    bake_passes.unregister()
    debug.unregister()
    high_res_objects_manager.unregister()
    addon.unregister()
    collection_manager.unregister()

    pass
    