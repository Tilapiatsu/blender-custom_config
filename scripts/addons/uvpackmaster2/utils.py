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


import os
import platform
import traceback
import sys
import mathutils
from collections import defaultdict

from .connection import *
from .prefs import *
from .enums import *
from .os_iface import *
from .version import UvpVersionInfo

import bpy
import bmesh


def get_uvp_path():
    return get_prefs().uvp_path


def get_uvp_execpath():
    uvp_basename = 'uvp'
    return os.path.join(get_uvp_path(), os_exec_dirname(), uvp_basename + os_exec_extension())


def in_debug_mode(debug_lvl = 1):
    return bpy.app.debug_value >= debug_lvl


def split_by_chars(str, cnt):
    str_split = str.split()

    array = []
    curr_str = ''
    curr_cnt = 0

    for word in str_split:
        curr_str += ' ' + word
        curr_cnt += len(word)

        if curr_cnt > cnt:
            array.append((curr_str))
            curr_str = ''
            curr_cnt = 0

    if curr_str != '':
        array.append((curr_str))

    return array
        

def reset_stats(prefs):

    prefs.stats_area = -1.0
    prefs.stats_array.clear()
    prefs['op_status'] = ''
    prefs['op_warnings'] = []


def print_backtrace(ex):
    _, _, trback = sys.exc_info()
    traceback.print_tb(trback)
    trbackDump = traceback.extract_tb(trback)
    filename, line, func, msg = trbackDump[-1]

    print('Line: {} Message: {}'.format(line, msg))
    print(str(ex))

class IslandSolution:
    island_idx = None
    pre_scale = None
    angle = None
    pivot = None
    offset = None
    scale = None
    post_scale_offset = None

class PackSolution:
    island_solutions = None

def read_pack_solution(pack_solution_msg):

    pack_solution = PackSolution()

    solution_island_count = force_read_int(pack_solution_msg)
    pack_solution.island_solutions = []

    for i in range(solution_island_count):
        i_solution = IslandSolution()
        i_solution.island_idx = force_read_int(pack_solution_msg)

        float_array = force_read_floats(pack_solution_msg, 9)

        i_solution.pre_scale = float_array[0]
        i_solution.angle = float_array[1]
        i_solution.pivot = mathutils.Vector(
            (float_array[2], float_array[3],
             0.0))
        i_solution.offset = mathutils.Vector(
            (float_array[4], float_array[5],
             0.0))

        i_solution.scale = float_array[6]

        i_solution.post_scale_offset = mathutils.Vector(
            (float_array[7], float_array[8],
             0.0))

        pack_solution.island_solutions.append(i_solution)

    return pack_solution


def to_uvp_group_method(group_method):

    if group_method in {UvGroupingMethod.MATERIAL.code, UvGroupingMethod.MESH.code, UvGroupingMethod.OBJECT.code, UvGroupingMethod.MANUAL.code}:

        return UvGroupingMethodUvp.EXTERNAL

    elif group_method == UvGroupingMethod.SIMILARITY.code:

        return UvGroupingMethodUvp.SIMILARITY

    raise RuntimeError('Unexpected grouping method encountered')


def redraw_ui(context):

    for area in context.screen.areas:
        if area is not None:
            area.tag_redraw()


def get_active_image_size(context):

    img = None
    for area in context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            img = area.spaces.active.image

    if img is None:
        raise RuntimeError("Active texture in the UV editor required for the operation")

    if img.size[0] == 0 or img.size[1] == 0:
        raise RuntimeError("Active texture in the UV editor has invalid dimensions")

    return (img.size[0], img.size[1])


def get_active_image_ratio(context):

    img_size = get_active_image_size(context)

    return float(img_size[0]) / float(img_size[1])


def pixel_to_unit(context, pixel_value):

    prefs = get_prefs()
    scene_props = context.scene.uvp2_props

    if prefs.pack_ratio_enabled(scene_props):
        img_size = get_active_image_size(context)
        tex_size = img_size[1]
    else:
        tex_size = scene_props.pixel_margin_tex_size

    return float(pixel_value) / tex_size


def get_pixel_margin(context):

    return pixel_to_unit(context, context.scene.uvp2_props.pixel_margin)


def get_pixel_padding(context):
    
    return pixel_to_unit(context, context.scene.uvp2_props.pixel_padding)


def validate_target_box(scene_props):
    
    tbox_dim_limit = 0.05
    tbox_width = abs(scene_props.target_box_p1_x - scene_props.target_box_p2_x)
    tbox_height = abs(scene_props.target_box_p1_y - scene_props.target_box_p2_y)

    if tbox_width < tbox_dim_limit:
        raise RuntimeError('Packing box width must be larger than ' + tbox_dim_limit)

    if tbox_height < tbox_dim_limit:
        raise RuntimeError('Packing box height must be larger than ' + tbox_dim_limit)
