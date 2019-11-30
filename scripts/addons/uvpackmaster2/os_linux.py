import os
import subprocess
import signal

def os_exec_extension():
    return ''

def os_exec_dirname():
    return 'lin'

def os_uvp_creation_flags():
    return None

def os_cancel_sig():
    return signal.SIGQUIT

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
