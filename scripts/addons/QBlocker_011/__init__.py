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

import bpy
from .op_cube import *
from .op_cylinder import *
from .op_sphere import *


bl_info = {
    "name": "QBlocker",
    "author": "Balazs Szeleczki",
    "version": (0, 1, 1),
    "description": "",
    "blender": (2, 80, 0),
    "location": "View3D > Add > QBlocker",
    "warning": "",
    "category": "Add Mesh"
}


class QBlockerAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    mouse_enum : bpy.props.EnumProperty(
        name="select mouse",
        items=(
        ('LEFT', 'Left', ""),
        ('RIGHT', 'Right', "")
        ),
        default='LEFT',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Active mouse button for the addon:")
        layout.row().prop(self, "mouse_enum", expand=True)


# right click menu button
class VIEW3D_MT_bstools(bpy.types.Menu):
    bl_label = "QBlocker"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.box_create", text="Plane / Cube", icon='MESH_CUBE')
        layout.operator("object.cylinder_create", text="Circle / Cylinder", icon='MESH_CYLINDER')
        layout.operator("object.sphere_create", text="Sphere", icon='MESH_UVSPHERE')


def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_bstools")
    self.layout.separator()


classes = (
    BoxCreateOperator,
    CylinderCreateOperator,
    SphereCreateOperator,
    VIEW3D_MT_bstools,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_specials.prepend(menu_func)
    bpy.types.VIEW3D_MT_add.prepend(menu_func)
    bpy.utils.register_class(QBlockerAddonPreferences)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object_specials.remove(menu_func)
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    bpy.utils.unregister_class(QBlockerAddonPreferences)

if __name__ == "__main__":
    register()
