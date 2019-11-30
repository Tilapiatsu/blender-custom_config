
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


def print_backtrace(ex):
    _, _, trback = sys.exc_info()
    traceback.print_tb(trback)
    trbackDump = traceback.extract_tb(trback)
    filename, line, func, msg = trbackDump[-1]

    print('Line: {} Message: {}'.format(line, msg))
    print(str(ex))

class IslandSolution:
    island_idx = None
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

        float_array = force_read_floats(pack_solution_msg, 8)

        i_solution.angle = float_array[0]
        i_solution.pivot = mathutils.Vector(
            (float_array[1], float_array[2],
             0.0))
        i_solution.offset = mathutils.Vector(
            (float_array[3], float_array[4],
             0.0))

        i_solution.scale = float_array[5]

        i_solution.post_scale_offset = mathutils.Vector(
            (float_array[6], float_array[7],
             0.0))

        pack_solution.island_solutions.append(i_solution)

    return pack_solution

def to_uvp_group_method(group_method):
    if group_method in {UvGroupingMethod.MATERIAL.code, UvGroupingMethod.MESH.code, UvGroupingMethod.OBJECT.code}:

        return UvGroupingMethodUvp.EXTERNAL

    elif group_method == UvGroupingMethod.SIMILARITY.code:

        return UvGroupingMethodUvp.SIMILARITY

    raise RuntimeError('Unexpected grouping method encountered')


def handle_invalid_islands(p_context, invalid_islands):
    p_context.select_all_faces(False)

    for idx, island_faces in enumerate(p_context.uv_island_faces_list):
        if idx in invalid_islands:
            p_context.select_island_faces(idx, island_faces, True)

def handle_island_flags(p_context, uv_island_faces_list, island_flags):
    overlap_indicies = []
    for i in range(len(island_flags)):
        overlaps = island_flags[i] & UvPackerIslandFlags.OVERLAPS
        if overlaps > 0:
            overlap_indicies.append(i)

    overlap_detected = len(overlap_indicies) > 0
    if overlap_detected:
        for idx, island_faces in enumerate(uv_island_faces_list):
            if idx not in overlap_indicies:
                p_context.select_island_faces(idx, island_faces, False)
            else:
                p_context.select_island_faces(idx, island_faces, True)

    return overlap_detected


def get_active_image_size(context):
    img = None
    for area in context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            img = area.spaces.active.image

    if img is None:
        raise RuntimeError("'Use Texture Ratio' option is on, but no active texture was found")

    if img.size[0] == 0 or img.size[1] == 0:
        raise RuntimeError("'Use Texture Ratio' option is on, but a texture with invalid dimensions was found in the UV editor")

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

def reset_target_box(scene_props):

    scene_props.target_box_p1_x = 0.0
    scene_props.target_box_p1_y = 0.0

    scene_props.target_box_p2_x = 1.0
    scene_props.target_box_p2_y = 1.0
    

def validate_target_box(scene_props):
    tbox_dim_limit = 0.05
    tbox_width = abs(scene_props.target_box_p1_x - scene_props.target_box_p2_x)
    tbox_height = abs(scene_props.target_box_p1_y - scene_props.target_box_p2_y)

    if tbox_width < tbox_dim_limit:
        raise RuntimeError('Packing box width must be larger than ' + tbox_dim_limit)

    if tbox_height < tbox_dim_limit:
        raise RuntimeError('Packing box height must be larger than ' + tbox_dim_limit)
