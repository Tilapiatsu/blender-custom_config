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
import signal
import subprocess
from ctypes.util import find_library
from ctypes import windll

import winreg


def os_exec_extension():
    return '.exe'

def os_exec_dirname():
    return 'win'

def os_engine_creation_flags():
    return subprocess.CREATE_NEW_PROCESS_GROUP

def os_cancel_sig():
    return signal.CTRL_BREAK_EVENT
   
def os_read_registry(reg_path, reg_name):

    try:

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
        val, _not_used = winreg.QueryValueEx(key, reg_name)
        winreg.CloseKey(key)
 
    except WindowsError:
        return None
    
    return val

def os_engine_path():
    
    return os_read_registry(r"Software\UVPackmaster", "Engine3InstallPath")

def os_platform_check(engine_execpath):
    if find_library('MSVCP140.dll') is None:
        return False, 'Install Visual C++ 2017 Redistributable and restart Blender'
        
    return True, ''

def os_get_userdata_path():
    appdata_path = os.getenv('APPDATA')
    if not appdata_path:
        raise RuntimeError('Could not get the appdata path')

    return os.path.join(appdata_path, 'UVPackmaster')

def os_simulate_esc_event():
    windll.user32.keybd_event(0x1B, 0, 0, 0)
    windll.user32.keybd_event(0x1B, 0, 0x0002, 0)