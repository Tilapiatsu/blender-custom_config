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
# Created by Kushiro
import bpy


from bpy.props import (
        FloatProperty,
        IntProperty,
        BoolProperty,
        EnumProperty,
        )


#from . import helper
from . import align_uv
import importlib
# from . import gui


bl_info = {
    "name": "Align UV",
    "description": "Align UV",
    "author": "Kushiro",
    "version": (1, 0, 0),
    "blender": (2, 83, 0),
    "location": "UV Editing > Context Menu (right click)",
    "category": "UV",
}




def register():    
    importlib.reload(align_uv)
    # importlib.reload(gui)
    
    bpy.utils.register_class(align_uv.AlignUVOperator)
    bpy.utils.register_class(align_uv.SmoothUVOperator)
    bpy.types.IMAGE_MT_uvs_context_menu.append(align_uv.menu_func)



def unregister():
    bpy.types.IMAGE_MT_uvs_context_menu.remove(align_uv.menu_func)
    bpy.utils.unregister_class(align_uv.AlignUVOperator)
    bpy.utils.unregister_class(align_uv.SmoothUVOperator)
    
    
if __name__ == "__main__":    
    register()

import importlib

def test():    
    #importlib.reload(helper)    
    
    try:
        unregister()   
    except:
        pass
    
    register()

    
    print('test loaded')


