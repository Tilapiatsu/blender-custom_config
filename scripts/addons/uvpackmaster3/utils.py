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
import json
import traceback
import sys
from collections import defaultdict

from .connection import *
# from .prefs import *
from .enums import *
from .os_iface import *
from .version import UvpmVersionInfo

import bpy
import bpy_types
import bmesh



def get_engine_path():
    return get_prefs().engine_path


def get_engine_execpath():
    engine_basename = 'uvpm'
    return os.path.join(get_engine_path(), os_exec_dirname(), engine_basename + os_exec_extension())


def in_debug_mode(debug_lvl = 1):
    return bpy.app.debug_value >= debug_lvl or bpy.app.debug


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
        

def print_backtrace(ex):
    _, _, trback = sys.exc_info()
    traceback.print_tb(trback)
    trbackDump = traceback.extract_tb(trback)
    filename, line, func, msg = trbackDump[-1]

    print('Line: {} Message: {}'.format(line, msg))
    print(str(ex))


def print_debug(debug_str):
    print('[UVPACKMASTER_DEBUG]: ' + debug_str)

def print_log(log_str):
    print('[UVPACKMASTER_LOG]: ' + log_str)

def print_error(error_str):
    print('[UVPACKMASTER_ERROR]: ' + error_str)

def print_warning(warning_str):
    print('[UVPACKMASTER_WARNING]: ' + warning_str)

def log_separator():
    return '-'*80

def rgb_to_rgba(rgb_color):

    return (rgb_color[0], rgb_color[1], rgb_color[2], 1.0)


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


def get_prop_type(collection, prop_id):
    return collection.bl_rna.properties[prop_id].type


def get_prop_name(collection, prop_id):
    return collection.bl_rna.properties[prop_id].name


def parse_json_file(json_file_path):
    with open(json_file_path) as f:
        try:
            data = json.load(f)
        except Exception as e:
            if in_debug_mode():
                print_backtrace(e)
            data = None
    return data


def unique_min_num(num_list, num_from=0):
    if not num_list:
        return num_from
    counter = num_from
    while True:
        counter += 1
        if counter in num_list:
            continue
        return counter


def unique_name(value, collection, instance=None):
    if collection.find(value) > -1:
        name_parts = value.rsplit(".", 1)
        base_name = name_parts[0]
        name_num_list = []
        found = 0
        same_found = 0
        for element in collection:
            if element == instance:
                continue

            if element.name.startswith(base_name):
                if element.name == value:
                    same_found += 1
                element_name_parts = element.name.rsplit(".", 1)
                if element_name_parts[0] != base_name:
                    continue
                found += 1
                if len(element_name_parts) < 2 or not element_name_parts[1].isnumeric():
                    continue
                name_num_list.append(int(element_name_parts[1]))

        if found > 0 and same_found > 0:
            return "{}.{:03d}".format(base_name, unique_min_num(name_num_list or [0]))
    return value


class ShadowedPropertyGroupMeta(bpy_types.RNAMetaPropGroup):
    def __new__(cls, name, bases, dct):
        shadow_cls = type(name, bases + (__ShadowPropertyGroup__,), dct)
        new_cls = super().__new__(cls, name, bases + (bpy.types.PropertyGroup,), dct)
        shadow_cls._real_cls = new_cls
        new_cls._shadow_cls = shadow_cls
        return new_cls


class __ShadowPropertyGroup__:
    def __getattr__(self, item):
        return getattr(self._real_cls, item)

    def cast_setattr(self, key, value):
        _types_func = {'BOOLEAN': bool, 'INT': int, 'FLOAT': float, 'STRING': str, 'ENUM': str}

        def _cast_value(_value, _type):
            _cast_func = _types_func.get(_type)
            if _cast_func is None:
                return _value
            return _cast_func(_value)

        prop_struct = self.bl_rna.properties.get(key, None)
        if prop_struct is not None and prop_struct.type in _types_func:
            prop_type = prop_struct.type
            is_array = getattr(prop_struct, 'is_array', False)
            if is_array:
                value = type(value)(_cast_value(v, prop_type) for v in value)
            else:
                value = _cast_value(value, prop_type)
        super().__setattr__(key, value)

    def property_unset(self, prop_name):
        prop_struct = self.bl_rna.properties[prop_name]
        is_array = getattr(prop_struct, 'is_array', False)
        if is_array and hasattr(prop_struct, 'default_array'):
            setattr(self, prop_name, prop_struct.default_array)
        elif hasattr(prop_struct, 'default'):
            setattr(self, prop_name, prop_struct.default)


class ShadowedPropertyGroup:
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "_shadow_cls"):
            return cls._shadow_cls(*args, **kwargs)
        return super().__new__(cls)


class ShadowedCollectionProperty:

    def __init__(self, elem_type):

        self.elem_type = elem_type
        self.collection = []

    def add(self):

        self.collection.append(self.elem_type())
        return self.collection[-1]

    def clear(self):

        self.collection.clear()

    def remove(self, idx):

        del self.collection[idx]

    def __len__(self):

        return len(self.collection)

    def __getitem__(self, idx):

            return self.collection[idx]

    def __iter__(self):

        return iter(self.collection)
        