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
from .op_pyramid import *

from .tools.turn_cylinder import *


bl_info = {
    "name": "QBlocker",
    "author": "Balazs Szeleczki",
    "version": (0, 1, 3, 0),
    "description": "",
    "blender": (2, 80, 0),
    "location": "View3D > Add > QBlocker",
    "warning": "",
    "category": "Add Mesh",
    "wiki_url": "https://qblockerdocs.readthedocs.io/"
}


class QBlockerAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    mouse_enum : bpy.props.EnumProperty(
        name="select mouse",
        items=(
        ('LEFT', 'Left', ""),
        ('RIGHT', 'Right', "")
        ),
        default='LEFT'
    )

    axis_bool : bpy.props.BoolProperty(
        name="Show orientation axis",
        description="Show axis while moving mouse in view",
        default = True
    ) 

    segs_int : bpy.props.IntProperty(
        name="Default segments",
        description="Default segments count for cylinder and sphere.",
        default = 16,
        min = 4,
        max = 128
    )

    snap_dist : bpy.props.IntProperty(
        name="Snap Distance",
        description="Default distance between mouse and the vertices in.",
        default = 30,
        min = 5,
        max = 500
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Active mouse button for the addon:")
        layout.row().prop(self, "mouse_enum", expand=True)
        layout.row().prop(self, "axis_bool", expand=True)
        layout.row().prop(self, "segs_int", expand=True)
        layout.row().prop(self, "snap_dist", expand=True)


# right click menu button
class VIEW3D_MT_qbtools(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_qbtools"
    bl_label = "QBlocker"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.box_create", text="Plane / Cube", icon='MESH_CUBE')
        layout.operator("object.cylinder_create", text="Circle / Cylinder", icon='MESH_CYLINDER')
        layout.operator("object.sphere_create", text="Sphere", icon='MESH_UVSPHERE')
        #layout.operator("object.pyramid_create", text="Pyramid", icon='MESH_UVSPHERE')
        layout.separator()
        layout.operator("object.turn_to_cylinder", text="Turn into Cylinder", icon='MESH_UVSPHERE')

           
def qblocker_menu(self, context):
    self.layout.menu("VIEW3D_MT_qbtools")
    self.layout.separator()


classes = (
    BoxCreateOperator,
    CylinderCreateOperator,
    SphereCreateOperator,
    #PyramidCreateOperator,
    Turn_Sphere,
    VIEW3D_MT_qbtools,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(qblocker_menu)
    bpy.types.VIEW3D_MT_add.prepend(qblocker_menu)
    bpy.utils.register_class(QBlockerAddonPreferences)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.remove(qblocker_menu)
    bpy.types.VIEW3D_MT_add.remove(qblocker_menu)
    bpy.utils.unregister_class(QBlockerAddonPreferences)

if __name__ == "__main__":
    register()
