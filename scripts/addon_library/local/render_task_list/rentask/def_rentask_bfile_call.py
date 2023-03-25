import bpy, sys, subprocess
from ..utils import (
get_log_file_path,
get_bfile_run_path,
)


def bfile_subprocess_call(dic):
    # log_cmd = [sys.argv[0], "-b", "-P", get_bfile_run_path(), dic]
    cmd_l = [sys.argv[0], "-b", "-P", get_bfile_run_path(), "--factory-startup", "__rentask_split__", dic]
    # cmd_l = ["python", get_bfile_run_path(), "--factory-startup", "__rentask_split__", dic]
    subprocess.Popen(cmd_l)
