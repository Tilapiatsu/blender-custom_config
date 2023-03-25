from mathutils import Quaternion, Vector
import bpy
import re


def copy_settings(froms, to):
    for prop in froms.bl_rna.properties:
        if prop.is_readonly:
            continue
        if prop.identifier == 'type':
            continue
        if prop.identifier == 'show_locked_time':
            continue
        if re.match('^show_region_', prop.identifier):
            continue
        val = getattr(froms, prop.identifier)
        setattr(to, prop.identifier, val)


def setView(area, rotation):
    backVec = Vector((0.0, 0.0, -1.0))
    backVec = rotation @ backVec

    # rightVec = mathutils.Vector((1.0, 0.0, 0.0))
    # rightVec = rotation @ rightVec

    context = bpy.context.copy()
    context['area'] = area
    for region in area.regions:
        if region.type == "WINDOW":
            break
    context['region'] = region
    context['space_data'] = area.spaces[0]

    axis = "FRONT"
    if backVec.y > 0.9:
        axis = "FRONT"
    if backVec.y < -0.9:
        axis = "BACK"
    if backVec.x > 0.9:
        axis = "LEFT"
    if backVec.x < -0.9:
        axis = "RIGHT"
    if backVec.z > 0.9:
        axis = "BOTTOM"
    if backVec.z < -0.9:
        axis = "TOP"
    # TODO no way to set 90 180 -90 views:
    #  x:1 => TOP Def ; y:-1 => TOP90 x:-1 => TOP180 y:1 => TOP-90
    #  x:1 => Bottom Def y:1 => Bottom90 x:-1 => Bottom180 y:-1 => Bottom-90

    bpy.ops.view3d.view_axis(context, type=axis)
