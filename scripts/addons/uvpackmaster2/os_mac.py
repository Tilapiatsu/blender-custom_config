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
from ctypes.util import find_library


def os_exec_extension():
    return ''

def os_exec_dirname():
    return 'mac'

def os_uvp_creation_flags():
    return None

def os_cancel_sig():
    return signal.SIGQUIT

def os_uvp_path():
    return None

def os_platform_check(uvp_execpath):
    cmd_line = 'chmod u+x "{}"'.format(uvp_execpath)
    proc = subprocess.Popen(cmd_line, shell=True)

    err_msg = ''
    try:
        proc.wait(5)
        if proc.returncode != 0:
            raise Exception()
    except:
        raise RuntimeError('Could not set the executable flag on the engine binary')