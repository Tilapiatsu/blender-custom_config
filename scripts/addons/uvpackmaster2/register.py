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


import platform
import multiprocessing
import subprocess

from .prefs import *
from .version import UvpVersionInfo
from .os_iface import *

from .enums import *
from .utils import *
from .connection import *

from bpy.props import StringProperty
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper
        )



def platform_check():
    unsupported_msg = 'Unsupported platform detected. Supported platforms are Linux 64 bit, Windows 64 bit, MacOS 64 bit'

    sys = platform.system()
    if sys != 'Linux' and sys != 'Windows' and sys != 'Darwin':
        raise RuntimeError(unsupported_msg)

    is_64bit = platform.machine().endswith('64')
    if not is_64bit:
        raise RuntimeError(unsupported_msg)

    os_platform_check(get_uvp_execpath())


def get_uvp_version():
    uvp_args = [get_uvp_execpath(), '-E', '-o', str(UvPackerOpcode.REPORT_VERSION)]
    uvp_proc = subprocess.Popen(uvp_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    send_finish_confirmation(uvp_proc)

    try:
        uvp_proc.wait(5)
    except:
        uvp_proc.terminate()
        raise

    in_stream = uvp_proc.stdout

    version_msg = None
    while True:
        msg = connection_rcv_message(in_stream)
        msg_code = force_read_int(msg)

        if msg_code == UvPackMessageCode.VERSION:
            version_msg = msg
            break

    if version_msg is None:
        raise RuntimeError('Could not read the UVP version')

    # TODO: make sure this won't block
    version_major = force_read_int(version_msg)
    version_minor = force_read_int(version_msg)
    version_patch = force_read_int(version_msg)
    version_suffix = struct.unpack('c', version_msg.read(1))[0].decode('ascii')

    feature_cnt = struct.unpack('i', version_msg.read(4))[0]
    feature_codes = []

    for i in range(feature_cnt):
        feature_codes.append(force_read_int(version_msg))

    dev_cnt = force_read_int(version_msg)
    devices = []

    for i in range(dev_cnt):
        id_length = force_read_int(version_msg)
        id = version_msg.read(id_length).decode('ascii')

        name_length = force_read_int(version_msg)
        name = version_msg.read(name_length).decode('ascii')

        dev_flags = force_read_int(version_msg)
        devices.append((id, name, dev_flags))

    uvp_version = (version_major, version_minor, version_patch)
    return uvp_version, version_suffix, feature_codes, devices


def parse_feature_codes(feature_codes):
    prefs = get_prefs()

    prefs.FEATURE_demo = False
    prefs.FEATURE_island_rotation = False
    prefs.FEATURE_overlap_check = False
    prefs.FEATURE_packing_depth = False
    prefs.FEATURE_heuristic_search = False
    prefs.FEATURE_pack_ratio = False
    prefs.FEATURE_pack_to_others = False
    prefs.FEATURE_grouping = False
    prefs.FEATURE_lock_overlapping = False
    prefs.FEATURE_advanced_heuristic = False
    prefs.FEATURE_self_intersect_processing = False
    prefs.FEATURE_validation = False
    prefs.FEATURE_multi_device_pack = False
    prefs.FEATURE_target_box = False
    prefs.FEATURE_island_rotation_step = False
    prefs.FEATURE_pack_to_tiles = False

    for code in feature_codes:
        int_code = code
        if int_code == UvPackerFeatureCode.DEMO:
            prefs.FEATURE_demo = True
        elif int_code == UvPackerFeatureCode.ISLAND_ROTATION:
            prefs.FEATURE_island_rotation = True
        elif int_code == UvPackerFeatureCode.OVERLAP_CHECK:
            prefs.FEATURE_overlap_check = True
        elif int_code == UvPackerFeatureCode.PACKING_DEPTH:
            prefs.FEATURE_packing_depth = True
        elif int_code == UvPackerFeatureCode.HEURISTIC_SEARCH:
            prefs.FEATURE_heuristic_search = True
        elif int_code == UvPackerFeatureCode.PACK_RATIO:
            prefs.FEATURE_pack_ratio = True
        elif int_code == UvPackerFeatureCode.PACK_TO_OTHERS:
            prefs.FEATURE_pack_to_others = True
        elif int_code == UvPackerFeatureCode.GROUPING:
            prefs.FEATURE_grouping = True
        elif int_code == UvPackerFeatureCode.LOCK_OVERLAPPING:
            prefs.FEATURE_lock_overlapping = True
        elif int_code == UvPackerFeatureCode.ADVANCED_HEURISTIC:
            prefs.FEATURE_advanced_heuristic = True
        elif int_code == UvPackerFeatureCode.SELF_INTERSECT_PROCESSING:
            prefs.FEATURE_self_intersect_processing = True
        elif int_code == UvPackerFeatureCode.VALIDATION:
            prefs.FEATURE_validation = True
        elif int_code == UvPackerFeatureCode.MULTI_DEVICE_PACK:
            prefs.FEATURE_multi_device_pack = True
        elif int_code == UvPackerFeatureCode.TARGET_BOX:
            prefs.FEATURE_target_box = True
        elif int_code == UvPackerFeatureCode.ISLAND_ROTATION_STEP:
            prefs.FEATURE_island_rotation_step = True
        elif int_code == UvPackerFeatureCode.PACK_TO_TILES:
            prefs.FEATURE_pack_to_tiles = True

@bpy.app.handlers.persistent
def load_post_handler(scene):
    reset_target_box_params(get_prefs())
    return None

def reset_target_box_params(prefs):
    prefs.target_box_enable = False
    prefs.target_box_draw_enable = False
    prefs.target_box_draw_after_click = False

def reset_debug_params(prefs):
    prefs.write_to_file = False
    prefs.seed = 0


def reset_feature_codes(prefs):
    prefs.FEATURE_demo = False
    prefs.FEATURE_island_rotation = True
    prefs.FEATURE_overlap_check = True
    prefs.FEATURE_packing_depth = True
    prefs.FEATURE_heuristic_search = True
    prefs.FEATURE_pack_ratio = True
    prefs.FEATURE_pack_to_others = True
    prefs.FEATURE_grouping = True
    prefs.FEATURE_lock_overlapping = True
    prefs.FEATURE_advanced_heuristic = True
    prefs.FEATURE_self_intersect_processing = True
    prefs.FEATURE_validation = True
    prefs.FEATURE_multi_device_pack = True
    prefs.FEATURE_target_box = True
    prefs.FEATURE_island_rotation_step = True
    prefs.FEATURE_pack_to_tiles = True


def register_specific(bl_info):

    bpy.app.handlers.load_post.append(load_post_handler)

    addon_uvp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uvp')
    paths_to_check = [get_prefs().uvp_path, os_uvp_path(), addon_uvp_path]

    for path in paths_to_check:

        if path is None:
            continue

        try:
            register_uvp(path)
        except:
            continue

        break


def check_uvp():
    uvp_release_filepath = os.path.join(get_uvp_path(), 'release-{}.uvpini'.format(UvpVersionInfo.uvp_version_string()))
    return os.path.isfile(uvp_release_filepath)


def unregister_uvp():
    prefs = get_prefs()
    prefs.uvp_initialized = False
    prefs.label_message = 'UVP engine {} not detected, press the button for help:'.format(UvpVersionInfo.uvp_version_string())
    prefs.uvp_path = 'Select a path to the UVP engine'

    prefs.sel_dev_idx = -1
    prefs.dev_array.clear()


def register_uvp(uvp_path):

    try:
        prefs = get_prefs()
        prefs.uvp_path = uvp_path
        prefs.enabled = True
        prefs.uvp_initialized = False
        prefs.label_message = ''
        prefs.thread_count = multiprocessing.cpu_count()
        prefs.dev_array.clear()
        
        reset_stats(prefs)
        reset_target_box_params(prefs)
        reset_debug_params(prefs)
        reset_feature_codes(prefs)

        if not check_uvp():
            raise RuntimeError('Engine version {} required'.format(UvpVersionInfo.uvp_version_string()))

        if not os.path.isfile(get_uvp_execpath()):
            raise RuntimeError('Engine installation broken')

        platform_check()

        uvp_version, version_suffix, feature_codes, devices = get_uvp_version()

        if uvp_version != UvpVersionInfo.uvp_version_tuple():
            raise RuntimeError('Unexpected error')

        edition_array = UvpVersionInfo.uvp_edition_array()
        edition_array_tmp = [edition_info for edition_info in edition_array if edition_info.suffix == version_suffix]
        if len(edition_array_tmp) != 1:
            raise RuntimeError('Unexpected error')

        edition_long_name = edition_array_tmp[0].long_name

        parse_feature_codes(feature_codes)

        if len(devices) == 0 or devices[0][0] != 'cpu':
            raise RuntimeError('Unexpected error')

        prefs.supported_dev_count = 0

        for dev in devices:
            dev_prop = prefs.dev_array.add()
            dev_prop.id = dev[0]
            dev_prop.name = dev[1]

            dev_flags = dev[2]
            dev_prop.supported = (dev_flags & UvDeviceFlags.SUPPORTED) > 0
            dev_prop.supports_groups_together = (dev_flags & UvDeviceFlags.SUPPORTS_GROUPS_TOGETHER) > 0

            if dev_prop.supported:
                prefs.supported_dev_count += 1

        if prefs.sel_dev_idx >= len(devices) or prefs.sel_dev_idx < 0:
            prefs.sel_dev_idx = 0

        prefs.label_message = 'UVP engine: {} ({})'.format(UvpVersionInfo.uvp_version_string(), edition_long_name)
        prefs.uvp_initialized = True

    except Exception as ex:
        if in_debug_mode():
            print_backtrace(ex)

        unregister_uvp()
        raise
    except:
        unregister_uvp()
        raise


class UVP2_OT_SelectUvpEngine(bpy.types.Operator, ImportHelper):

    bl_idname = 'uvpackmaster2.select_uvp_engine'
    bl_label = 'Select UVP Engine'
    bl_description = 'Select a path to the UVP engine'

    filename_ext = ".uvpini"
    filter_glob : StringProperty(
        default="*.uvpini",
        options={'HIDDEN'},
        )
    
    def execute(self, context):

        try:
            uvp_path = os.path.abspath(os.path.dirname(self.filepath))
            register_uvp(uvp_path)
            self.report({'INFO'}, 'UVP initialized. Save Blender preferences to make the path permanent')

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'UVP initialization failed: ' + str(ex))

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'UVP initialization failed: Unexpected error')

        redraw_ui(context)

        return {'FINISHED'}
    
    def draw(self, context):
        pass

    def post_op(self):
        pass