import bpy

from bpy.props import IntProperty


class UvToolkitProperties(bpy.types.PropertyGroup):
    checker_map_width: IntProperty(name="Width", min=0)
    checker_map_height: IntProperty(name="Height", min=0)
