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

# from .prefs import *
from .version import UvpmVersionInfo
from .os_iface import *

from .enums import *
from .utils import *
from .connection import *

from bpy.props import StringProperty
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper
        )


class BenchmarkEntry:
    # progress : IntProperty(name="", default=0)
    # iter_count : IntProperty(name="", default=0)
    # total_time : IntProperty(name="", default=0)
    # avg_time : IntProperty(name="", default=0)

    def __init__(self):
        self.reset()

    def reset(self):
        self.progress = 0
        self.iter_count = 0
        self.total_time = 0
        self.avg_time = 0

    def decode(self, benchmark_msg):
        self.progress = force_read_int(benchmark_msg)
        self.iter_count = force_read_int(benchmark_msg)
        self.total_time = force_read_int(benchmark_msg)
        self.avg_time = -1 if self.iter_count == 0 else int(float(self.total_time) / self.iter_count)

class DeviceDesc:
    # id : StringProperty(name="", default="")
    # name : StringProperty(name="", default="")
    # supported : BoolProperty(name="", default=False)
    # supports_groups_together : BoolProperty(name="", default=False)
    # bench_entry : PointerProperty(type=UVPM3_BenchmarkEntry)
    # settings : PointerProperty(type=UVPM3_DeviceSettings)

    def __init__(self, id, name, supported, supports_groups_together, settings):
        self.id = id
        self.name = name
        self.supported = supported
        self.supports_groups_together = supports_groups_together
        self.settings = settings
        self.bench_entry = BenchmarkEntry()

    def reset(self):
        self.bench_entry.reset()



def platform_check():
    unsupported_msg = 'Unsupported platform detected. Supported platforms are Linux 64 bit, Windows 64 bit, MacOS 64 bit'

    sys = platform.system()
    if sys != 'Linux' and sys != 'Windows' and sys != 'Darwin':
        raise RuntimeError(unsupported_msg)

    is_64bit = platform.machine().endswith('64')
    if not is_64bit:
        raise RuntimeError(unsupported_msg)

    os_platform_check(get_engine_execpath())


def get_engine_version():
    engine_args = [get_engine_execpath(), '-E', '-o', str(UvpmOpcode.REPORT_VERSION)]
    engine_proc = subprocess.Popen(engine_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    send_finish_confirmation(engine_proc)

    try:
        engine_proc.wait(5)
    except:
        engine_proc.terminate()
        raise

    in_stream = engine_proc.stdout

    version_msg = None
    while True:
        msg = connection_rcv_message(in_stream)
        msg_code = force_read_int(msg)

        if msg_code == UvpmMessageCode.VERSION:
            version_msg = msg
            break

    if version_msg is None:
        raise RuntimeError('Could not read the UVPM version')

    # TODO: make sure this won't block
    version_major = force_read_int(version_msg)
    version_minor = force_read_int(version_msg)
    version_patch = force_read_int(version_msg)
    version_suffix = decode_string(version_msg, str_len=1) # struct.unpack('c', version_msg.read(1))[0].decode('ascii')

    feature_cnt = struct.unpack('i', version_msg.read(4))[0]
    feature_codes = []

    for i in range(feature_cnt):
        feature_codes.append(force_read_int(version_msg))

    dev_cnt = force_read_int(version_msg)
    devices = []

    for i in range(dev_cnt):
        id = decode_string(version_msg)
        name = decode_string(version_msg)

        dev_flags = force_read_int(version_msg)
        devices.append((id, name, dev_flags))

    engine_version = (version_major, version_minor, version_patch)
    return engine_version, version_suffix, feature_codes, devices


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
        if int_code == UvpmFeatureCode.DEMO:
            prefs.FEATURE_demo = True
        elif int_code == UvpmFeatureCode.ISLAND_ROTATION:
            prefs.FEATURE_island_rotation = True
        elif int_code == UvpmFeatureCode.OVERLAP_CHECK:
            prefs.FEATURE_overlap_check = True
        elif int_code == UvpmFeatureCode.PACKING_DEPTH:
            prefs.FEATURE_packing_depth = True
        elif int_code == UvpmFeatureCode.HEURISTIC_SEARCH:
            prefs.FEATURE_heuristic_search = True
        elif int_code == UvpmFeatureCode.PACK_RATIO:
            prefs.FEATURE_pack_ratio = True
        elif int_code == UvpmFeatureCode.PACK_TO_OTHERS:
            prefs.FEATURE_pack_to_others = True
        elif int_code == UvpmFeatureCode.GROUPING:
            prefs.FEATURE_grouping = True
        elif int_code == UvpmFeatureCode.LOCK_OVERLAPPING:
            prefs.FEATURE_lock_overlapping = True
        elif int_code == UvpmFeatureCode.ADVANCED_HEURISTIC:
            prefs.FEATURE_advanced_heuristic = True
        elif int_code == UvpmFeatureCode.SELF_INTERSECT_PROCESSING:
            prefs.FEATURE_self_intersect_processing = True
        elif int_code == UvpmFeatureCode.VALIDATION:
            prefs.FEATURE_validation = True
        elif int_code == UvpmFeatureCode.MULTI_DEVICE_PACK:
            prefs.FEATURE_multi_device_pack = True
        elif int_code == UvpmFeatureCode.TARGET_BOX:
            prefs.FEATURE_target_box = True
        elif int_code == UvpmFeatureCode.ISLAND_ROTATION_STEP:
            prefs.FEATURE_island_rotation_step = True
        elif int_code == UvpmFeatureCode.PACK_TO_TILES:
            prefs.FEATURE_pack_to_tiles = True

@bpy.app.handlers.persistent
def load_post_handler(scene):
    get_prefs().reset_box_params()
    return None


def register_specific(bl_info):

    bpy.app.handlers.load_post.append(load_post_handler)

    addon_engine_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uvpm')
    paths_to_check = [get_prefs().engine_path, os_engine_path(), addon_engine_path]

    for path in paths_to_check:

        if path is None:
            continue

        try:
            register_engine(path)
        except:
            continue

        break


def check_engine():
    engine_release_filepath = os.path.join(get_engine_path(), 'release-{}.uvpmi'.format(UvpmVersionInfo.engine_version_string()))
    return os.path.isfile(engine_release_filepath)


def unregister_engine():
    prefs = get_prefs()
    prefs.engine_initialized = False
    prefs.engine_status_msg = 'UVPackmaster engine {} not detected'.format(UvpmVersionInfo.engine_version_string())
    prefs.engine_path = 'Engine not detected'

    prefs.reset_device_array()


def register_engine(engine_path):

    try:
        prefs = get_prefs()
        prefs.reset()
        prefs.engine_path = engine_path

        if not check_engine():
            raise RuntimeError('Engine version {} required'.format(UvpmVersionInfo.engine_version_string()))

        if not os.path.isfile(get_engine_execpath()):
            raise RuntimeError('Engine installation broken')

        platform_check()

        engine_version, version_suffix, feature_codes, devices = get_engine_version()

        if engine_version != UvpmVersionInfo.engine_version_tuple():
            raise RuntimeError('Unexpected error')

        edition_array = UvpmVersionInfo.uvpm_edition_array()
        edition_array_tmp = [edition_info for edition_info in edition_array if edition_info.suffix == version_suffix]
        if len(edition_array_tmp) != 1:
            raise RuntimeError('Unexpected error')

        edition_long_name = edition_array_tmp[0].long_name

        parse_feature_codes(feature_codes)

        if len(devices) == 0 or devices[0][0] != 'cpu':
            raise RuntimeError('Unexpected error')

        register_devices(prefs, devices)

        prefs.engine_status_msg = 'UVPackmaster Engine: {} {}'.format(UvpmVersionInfo.engine_version_string(), edition_long_name)
        prefs.engine_initialized = True

    except Exception as ex:
        if in_debug_mode():
            print_backtrace(ex)

        unregister_engine()
        raise
    except:
        unregister_engine()
        raise


def register_devices(prefs, devices):

    dev_array = []

    for dev in devices:
        dev_id = dev[0]
        dev_name = dev[1]
        dev_flags = dev[2]

        # Search for saved device settings
        dev_saved_settings = None
        for saved_settins in prefs.saved_dev_settings:
            if saved_settins.dev_id == dev_id:
                dev_saved_settings = saved_settins
                break

        if dev_saved_settings is None:
            dev_saved_settings = prefs.saved_dev_settings.add()
            dev_saved_settings.dev_id = dev_id

        dev_desc = DeviceDesc(\
            dev_id,
            dev_name,
            supported=(dev_flags & UvpmDeviceFlags.SUPPORTED) > 0,
            supports_groups_together=(dev_flags & UvpmDeviceFlags.SUPPORTS_GROUPS_TOGETHER) > 0,
            settings=dev_saved_settings.settings)

        dev_array.append(dev_desc)

    type(prefs).dev_array = dev_array


def register_modes(modes_classes):
    from collections import defaultdict
    mode_type__mode_id_cls_pair = defaultdict(list)
    modes_ids = []

    for mode_cls in modes_classes:
        if mode_cls.MODE_ID in modes_ids:
            raise RuntimeError("The '{}' mode is duplicated".format(mode_cls.MODE_ID))

        modes_ids.append(mode_cls)
        mode_type__mode_id_cls_pair[mode_cls.MODE_TYPE].append((mode_cls.MODE_ID, mode_cls))

    prefs_type = type(get_prefs())
    prefs_type.modes_dict = dict(mode_type__mode_id_cls_pair)


class UVPM3_OT_SetEnginePath(bpy.types.Operator, ImportHelper):

    bl_idname = 'uvpackmaster3.set_engine_path'
    bl_label = 'Set Engine Path'
    bl_description = 'Set a path to the UVPM engine'

    filename_ext = ".uvpmi"
    filter_glob : StringProperty(
        default="*.uvpmi",
        options={'HIDDEN'},
        )
    
    def execute(self, context):

        try:
            engine_path = os.path.abspath(os.path.dirname(self.filepath))
            register_engine(engine_path)
            self.report({'INFO'}, 'UVPM engine initialized. Save Blender preferences to make the path permanent')

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'UVPM engine initialization failed: ' + str(ex))

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'UVPM initialization failed: Unexpected error')

        redraw_ui(context)

        return {'FINISHED'}
    
    def draw(self, context):
        pass

    def post_op(self):
        pass