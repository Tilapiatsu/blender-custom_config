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
from .op_cube import BoxCreateOperator
from .op_cornercube import CornerCubeCreateOperator
from .op_cylinder import CylinderCreateOperator
from .op_sphere import SphereCreateOperator
from .op_spherecube import SphereCubeCreateOperator
from .op_pyramid import PyramidCreateOperator
from .op_torus import TorusCreateOperator
from .op_transform import ObjectTransformOperator

from .qblock_prop import QBlockProperties, MESH_PT_QblockPanel
from .qblock.qblock_convert import ConvertToQBlock


bl_info = {
    "name": "QBlocker",
    "author": "Balazs Szeleczki",
    "version": (0, 1, 5, 2),
    "description": "",
    "blender": (3, 0, 0),
    "location": "View3D > Add > QBlocker",
    "warning": "",
    "category": "Add Mesh",
    "wiki_url": "https://qblockerdocs.readthedocs.io/"
}


class QBlockerAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # General settings #
    mouse_enum: bpy.props.EnumProperty(
        name="select mouse",
        items=(
            ('LEFT', 'Left', ""),
            ('RIGHT', 'Right', "")
        ),
        default='LEFT'
    )

    ishelp: bpy.props.BoolProperty(
        name="Show help text",
        description="Change the default state of the help text.",
        default=True
    )

    axis_bool: bpy.props.BoolProperty(
        name="Show orientation axis",
        description="Show axis while moving mouse in view",
        default=True
    )

    object_ignorebehind: bpy.props.EnumProperty(
        name="Hit Filter",
        description="Hit only the grid or objects in front of it.",
        items=(
            ('ALL', "Hit all", "", 0),
            ('FRONT', "Front of Grid", "", 1),
            ('GRID', "Grid Only", "", 2)
        ),
        default='ALL',
    )

    text_size_int: bpy.props.IntProperty(
        name="Text size",
        description="Default segments count for cylinder and sphere.",
        default=14,
        min=4,
        max=128
    )

    header_color: bpy.props.FloatVectorProperty(
        name="Header color",
        description="The help section header color.",
        subtype='COLOR',
        default=[1.0, 0.38, 0.38, 1.0],
        size=4,
        min=0, max=1
    )

    text_color: bpy.props.FloatVectorProperty(
        name="Text color",
        description="The help section element color.",
        subtype='COLOR',
        default=[1.0, 1.0, 1.0, 1.0],
        size=4,
        min=0, max=1
    )

    hotkey_color: bpy.props.FloatVectorProperty(
        name="Hotkey color",
        description="The help section hotkey color.",
        subtype='COLOR',
        default=[1.0, 0.86, 0.0, 1.0],
        size=4,
        min=0, max=1
    )

    # working plane settings #
    grid_count: bpy.props.IntProperty(
        name="Grid cell count",
        description="The amount of grid division.",
        default=5,
        min=2,
        max=20
    )

    grid_color: bpy.props.FloatVectorProperty(
        name="Grid lines color",
        description="The color of the working plane grid lines.",
        subtype='COLOR',
        default=[0.655, 0.655, 0.655, 0.2],
        size=4,
        min=0, max=1
    )

    # Snap settings #
    zsnaptoggle_bool: bpy.props.BoolProperty(
        name="Turn off snapping in height stage.",
        description="Turn off snapping when in height set mode.",
        default=True
    )

    snap_dist: bpy.props.IntProperty(
        name="Snap Distance",
        description="Snap distance between mouse position and snap points.",
        default=30,
        min=5,
        max=500
    )

    snap_dotsize: bpy.props.FloatProperty(
        name="Dot size factor",
        description="Snap dot size.",
        default=1.0,
        min=0.1,
        max=10
    )

    snap_closestColor: bpy.props.FloatVectorProperty(
        name="Closest point color",
        description="The closest snap point color.",
        subtype='COLOR',
        default=[1.0, 1.0, 1.0, 1.0],
        size=4,
        min=0, max=1
    )

    snap_pointsColor: bpy.props.FloatVectorProperty(
        name="Poly point color",
        description="The snap points color.",
        subtype='COLOR',
        default=[1.0, 0.56, 0.0, 0.7],
        size=4,
        min=0, max=1
    )

    snap_gridpointsColor: bpy.props.FloatVectorProperty(
        name="Grid point color",
        description="The snapgrid points color.",
        subtype='COLOR',
        default=[0.12, 0.56, 1.0, 0.7],
        size=4,
        min=0, max=1
    )

    # Object settings #
    segs_int: bpy.props.IntProperty(
        name="Default segments",
        description="Default segments count for cylinder and sphere.",
        default=16,
        min=4,
        max=128
    )

    def draw(self, context):
        layout = self.layout
        # general settings
        general_box = layout.box()
        general_box.label(text="General settings")
        general_box.label(text="Active mouse button for the addon:")
        general_box.row().prop(self, "mouse_enum", expand=True)
        general_box.row().prop(self, "ishelp")
        general_box.row().prop(self, "axis_bool")
        general_box.row().prop(self, "object_ignorebehind", expand=True)
        general_box.row().prop(self, "text_size_int")
        general_box.row().prop(self, "header_color")
        general_box.row().prop(self, "text_color")
        general_box.row().prop(self, "hotkey_color")

        # wplane settings
        wplane_box = layout.box()
        wplane_box.label(text="Working Plane settings")
        wplane_box.row().prop(self, "grid_count")
        wplane_box.row().prop(self, "grid_color")

        # snap settings
        snap_box = layout.box()
        snap_box.label(text="Snap settings")
        snap_box.row().prop(self, "zsnaptoggle_bool")
        snap_box.row().prop(self, "snap_dist")
        snap_box.row().prop(self, "snap_dotsize")
        snap_box.row().prop(self, "snap_closestColor")
        snap_box.row().prop(self, "snap_pointsColor")
        snap_box.row().prop(self, "snap_gridpointsColor")

        # object settings
        object_box = layout.box()
        object_box.label(text="Object settings")
        object_box.row().prop(self, "segs_int", expand=True)


# add menu object mode
class VIEW3D_MT_qbtools(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_qbtools"
    bl_label = "QBlocker"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.box_create", text="Plane / Cube", icon='MESH_CUBE')
        layout.operator("object.cornercube_create", text="Corner Cube", icon='MESH_CUBE')
        layout.operator("object.cylinder_create", text="Circle / Cylinder", icon='MESH_CYLINDER')
        layout.operator("object.sphere_create", text="Sphere", icon='MESH_UVSPHERE')
        layout.operator("object.spherecube_create", text="SphereCube", icon='MESH_UVSPHERE')
        layout.operator("object.pyramid_create", text="Pyramid", icon='MESH_UVSPHERE')
        layout.operator("object.torus_create", text="Torus", icon='MESH_TORUS')
        layout.separator()
        # layout.operator("object.turn_to_cylinder", text="Turn into Cylinder", icon='MESH_UVSPHERE')
        layout.operator("object.convert_to_qblock", text="Convert to QBlock", icon='MESH_CUBE')
        # WIP
        layout.separator()
        layout.operator("object.qtransform", text="Transform object (WIP)", icon='MESH_CUBE')


def qblocker_menu(self, context):
    self.layout.menu("VIEW3D_MT_qbtools")
    self.layout.separator()


# add menu edit mode
class VIEW3D_MT_qbtools_edit(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_qbtools_edit"
    bl_label = "QBlocker"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.box_create", text="Plane / Cube", icon='MESH_CUBE')
        layout.operator("object.cornercube_create", text="Corner Cube", icon='MESH_CUBE')
        layout.operator("object.cylinder_create", text="Circle / Cylinder", icon='MESH_CYLINDER')
        layout.operator("object.sphere_create", text="Sphere", icon='MESH_UVSPHERE')
        layout.operator("object.spherecube_create", text="SphereCube", icon='MESH_UVSPHERE')
        layout.operator("object.pyramid_create", text="Pyramid", icon='MESH_UVSPHERE')
        layout.operator("object.torus_create", text="Torus", icon='MESH_TORUS')
        # layout.separator()
        # layout.operator("object.convert_to_qblock", text="Convert to QBlock", icon='MESH_CUBE')


def qblocker_edit_menu(self, context):
    self.layout.menu("VIEW3D_MT_qbtools_edit")
    self.layout.separator()


classes = (
    BoxCreateOperator,
    CornerCubeCreateOperator,
    CylinderCreateOperator,
    SphereCreateOperator,
    SphereCubeCreateOperator,
    PyramidCreateOperator,
    TorusCreateOperator,
    ConvertToQBlock,
    ObjectTransformOperator,
    VIEW3D_MT_qbtools,
    VIEW3D_MT_qbtools_edit,
    QBlockProperties,
    MESH_PT_QblockPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.types.VIEW3D_MT_object_context_menu.prepend(qblocker_menu)
    bpy.types.VIEW3D_MT_add.prepend(qblocker_menu)
    bpy.types.VIEW3D_MT_mesh_add.prepend(qblocker_edit_menu)
    bpy.utils.register_class(QBlockerAddonPreferences)
    bpy.types.Mesh.qblock_props = bpy.props.PointerProperty(type=QBlockProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    # bpy.types.VIEW3D_MT_object_context_menu.remove(qblocker_menu)
    bpy.types.VIEW3D_MT_add.remove(qblocker_menu)
    bpy.types.VIEW3D_MT_mesh_add.remove(qblocker_edit_menu)
    bpy.utils.unregister_class(QBlockerAddonPreferences)


if __name__ == "__main__":
    register()
