import bpy

from . import non_id_prop, get_set_prop, dict_prop
from typing import Callable, Any


def DictProperty(get=None, set=None, update=None):
    return dict_prop.DictProperty(get, set, update).prop


def GetSetProperty(
    get: Callable[[bpy.types.PropertyGroup], Any] = None,
    set: Callable[[bpy.types.PropertyGroup, Any], None] = None,
) -> property:
    """
    A simple property that uses only the provided get and set functions.
    If set is not provided, property will be read-only.

    Args:
        get (Callable[[bpy.types.PropertyGroup], Any], optional): A function that is called when the property is read.\
            It's return value is what is given when the property is accessed.
        set (Callable[[bpy.types.PropertyGroup, Any], None], optional): A function that is called\
            when the property is set.

    Returns:
        property: A property that returns the result of the provided get function when it is read,
        And calls the provided set function when the value is modified.
    """

    return get_set_prop.GetSetProperty(get, set).prop


def NonIDProperty(
    name: str,
    subtype: str,
    get: Callable[[bpy.types.PropertyGroup], Any] = None,
    set: Callable[[bpy.types.PropertyGroup, Any], None] = None,
    update: Callable[[bpy.types.PropertyGroup, bpy.types.Context], None] = None,
    name_update: Callable[[bpy.types.PropertyGroup, bpy.types.Context, str], None] = None,
) -> property:
    """Returns a property that can hold a reference to a blender property that is not a subclass of bpy.types.ID,
    even if that properties name is changed in the UI.

    Limitations:
        * The name argument must be the same as the name of the variable the property is being assigned to.

    Example usage:
        bpy.types.Object.vgroup = NonIDProperty(name="vgroup", subtype="vertex_groups")

    Args:
        name (str): THIS MUST BE THE SAME AS THE NAME OF THE VARIABLE THIS IS ASSIGNED TO.
        subtype (str): This is the path from the ID data block that this is currently registered to,
            to the non ID property you want to assign it to.
        get (function[self] -> Any): Function that is called when the property is returned
        set (function[self, value] -> None): Function that is called when the property is set
        update (function): Function that is called when the property is updated
        name_update(function): Function that is called when the name of the current property is changed

    Returns:
        property: a property that will still reference the item it is assigned to,
            even when the name of the item is changed
    """
    return non_id_prop.NonIDProperty(name, subtype, get, set, update, name_update).prop


modules = [non_id_prop]


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()
