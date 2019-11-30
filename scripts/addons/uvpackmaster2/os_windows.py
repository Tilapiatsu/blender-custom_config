
import os
import signal
import subprocess
from ctypes.util import find_library

def os_exec_extension():
    return '.exe'

def os_exec_dirname():
    return 'win'

def os_uvp_creation_flags():
    return subprocess.CREATE_NEW_PROCESS_GROUP

def os_cancel_sig():
    return signal.CTRL_BREAK_EVENT
    
def os_platform_check(uvp_execpath):
    if find_library('MSVCP140.dll') is None:
        return False, 'Install Visual C++ 2017 Redistributable and restart Blender'
        
    return True, ''
    