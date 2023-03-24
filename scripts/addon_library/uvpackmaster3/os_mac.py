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


import subprocess
import signal
import os
from ctypes.util import find_library


def os_exec_extension():
    return ''

def os_exec_dirname():
    return 'mac'

def os_engine_creation_flags():
    return None

def os_cancel_sig():
    return signal.SIGQUIT

def os_engine_path():
    return os.path.join('/Applications', 'UVPackmaster', 'engine3')

def os_platform_check(engine_execpath):
    pass

def os_get_userdata_path():
    home_path = os.getenv("HOME")
    if not home_path:
        raise RuntimeError('Could not get the home path')

    return os.path.join(home_path, 'Library', 'Application Support', 'UVPackmaster')

def os_simulate_esc_event():
    # Not implemented
    pass