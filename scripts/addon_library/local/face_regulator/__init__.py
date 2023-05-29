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
from . import face_regulator


bl_info = {
    "name": "Face Regulator",
    "description": "Face Regulator",
    "author": "Kushiro",
    "version": (2, 0, 0),
    "blender": (2, 83, 0),
    "location": "View3D > Edit > Context Menu (right click)",
    "category": "Mesh",
}



def menu_func(self, context):
    self.layout.operator_context = "INVOKE_DEFAULT";    
    self.layout.operator(face_regulator.FaceRegulatorOperator.bl_idname)

def register():    
    importlib.reload(face_regulator)

    
    bpy.utils.register_class(face_regulator.FaceRegulatorOperator)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)
    #bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)    


def unregister():
    #bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)
    bpy.utils.unregister_class(face_regulator.FaceRegulatorOperator)



    
if __name__ == "__main__":    
    register()

import importlib

def test():    
    #importlib.reload(helper)    
    
    try:
        unregister()
    except :
        pass
    
    try:
        register()
    except :
        pass
    
    print('test loaded')


