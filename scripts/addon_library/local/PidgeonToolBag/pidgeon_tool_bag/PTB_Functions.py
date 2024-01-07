import bpy
import time
import sys
import os
import contextlib
import subprocess
import importlib
import json
import typing
from collections import namedtuple
from .PTB_Functions import *
from bpy.types import (
    Object,
    NodeTree,
    Node,
)
from mathutils import Vector


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[104m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    SUCCESS = '\033[42m'
    WARNING = '\033[93m'
    ABORT = '\033[103m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


#region dependencies

from sys import platform
if platform == "linux" or platform == "linux2":
    index_url = "https://download.pytorch.org/whl/cpu"
elif platform == "win32":
    index_url = "https://download.pytorch.org/whl/cu118"
elif platform == "darwin":
    index_url = None

dependency = namedtuple("dependency", ["module", "package", "name", "index_url", "skip_import", "required_for"])

all_dependencies = (
    dependency(module="cv2", package="opencv-python", name="cv2", index_url=None, skip_import=False, required_for=["sfr", "siu"]),
    dependency(module="cv2", package="opencv-contrib-python", name="cv2", index_url=None, skip_import=False, required_for=["sfr", "siu"]),
    dependency(module="matplotlib", package="matplotlib", name="matplotlib", index_url=None, skip_import=False, required_for=["sfr"]),
    dependency(module="torch", package="torch", name="torch", index_url=index_url, skip_import=False, required_for=["siu"]),
    dependency(module="torchvision", package="torchvision", name="torchvision", index_url=index_url, skip_import=False, required_for=["siu"]),
    dependency(module="torchaudio", package="torchaudio", name="torchaudio", index_url=index_url, skip_import=False, required_for=["siu"]),
    dependency(module="glob2", package="glob2", name="glob2", index_url=None, skip_import=False, required_for=["siu"]),
)

def import_module(module_name, global_name=None):
    if global_name is None:
        global_name = module_name

    if global_name in globals():
        importlib.reload(globals()[global_name])
    else:
        globals()[global_name] = importlib.import_module(module_name)

def install_pip():
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        import ensurepip

        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)

def install_module(module_name, package_name=None, index_url=None):
    from pathlib import Path

    if package_name is None:
        package_name = module_name

    # Attempt to import the module first
    try:
        importlib.import_module(module_name)
        print(f"{module_name} is already installed.")
        return  # Skip installation as module is already installed
    except ImportError:
        # Module not installed, proceed with installation
        pass

    environ_dict = dict(os.environ)
    module_path = Path.joinpath(Path(os.path.dirname(__file__)).parent, Path("python_modules"))
    if not module_path.exists():
        module_path.mkdir()
    if index_url is None:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name, "-t", module_path, "--upgrade"], check=True, env=environ_dict)
    else:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name, "-t", module_path, "--index-url", index_url, "--upgrade"], check=True, env=environ_dict)
    print(f"{module_name} has been successfully installed.")


class dependencies_check_singleton(object):
    def __init__(self):
        self._checked = {}  # Now a dictionary
        self._needs_install = {}  # Now a dictionary
        self._error = False
        self._success = False

    def checked(self, context):
        return self._checked.get(context, False)

    def needs_install(self, context):
        return self._needs_install.get(context, False)

    def check_dependencies(self, contexts):
        if not isinstance(contexts, list):
            contexts = [contexts]

        for context in contexts:
            self._checked[context] = False
            self._needs_install[context] = False
            missing_dependencies = []

            for dependency in all_dependencies:
                if dependency.skip_import or context not in dependency.required_for: 
                    continue
                try:
                    print(f"Checking for {dependency.module}...")
                    import_module(dependency.module, dependency.name)
                    print(f"Found {dependency.module}.")
                except ModuleNotFoundError:
                    print(f"{dependency.module} is missing.")
                    missing_dependencies.append(dependency)

            critical_missing = any(dep for dep in missing_dependencies)
            self._needs_install[context] = critical_missing
            self._checked[context] = True

            if missing_dependencies:
                missing_deps_names = [dep.module for dep in missing_dependencies]
                print(f"Missing dependencies for {context}: {', '.join(missing_deps_names)}")
            else:
                print(f"All dependencies are present for {context}.")

    def install_dependencies(self, context):
        self._error = False
        self._success = False
        # Update pip
        print("Ensuring pip is installed...")
        install_pip()

        context_dependencies = [dep for dep in all_dependencies if any(ctx in dep.required_for for ctx in context)]

        for dep in all_dependencies:
            print(context, "AND", dep.required_for)

        print(context_dependencies)

        for dependency in context_dependencies:
            package_name = dependency.package if dependency.package is not None else dependency.module
            print(f"Installing {package_name}...")
            try:
                install_module(module_name=dependency.module, package_name=dependency.package, index_url=dependency.index_url)
            except (subprocess.CalledProcessError, ImportError) as err:
                self._error = True
                print(f"Error installing {package_name}!")
                print(str(err))
                raise ValueError(package_name)

        self._success = True
        self.check_dependencies(context)


dependencies = dependencies_check_singleton()

#endregion dependencies

#region version check

def version_to_float(s, truncated=False):
    """versioning is very dumb in this plugin, it sometimes use string format, sometimes blender use a list format ect.. ultimately in order to """
    # Thanks, Geo-Scatter Team!
    if isinstance(s, (list, tuple, set)):
        s = '.'.join(map(str, s))
    # remove unwanted substrings
    for sub in ["Beta", "Alpha", "Release", "Candidate", " "]:
        s = s.replace(sub, "")
    # split on dot and rejoin the first two parts with a dot, concatenate the rest
    parts = s.split('.')
    s = '.'.join(parts[:2]) + ''.join(parts[2:])
    # convert to float
    s = float(s)
    # truncate to only essential version?
    if (truncated):
        s = int(s*10)/10

    return s

notifications = []

def notification_check():
    # reset any previous notifications
    global notifications
    notifications = [
        n for n in notifications if n[0] not in (
            "OLD_BLENDER_VERSION",
            "NEW_BLENDER_VERSION",
            "EXP_BLENDER_VERSION",
        )
    ]

    # current addon version
    from .. __init__ import bl_info
    user_addon_version = version_to_float(".".join(map(str,bl_info['blender'])), truncated=True)
    user_blender_version = version_to_float(bpy.app.version_string, truncated=True)

    # check if the user uses an old blender version
    if (user_blender_version < user_addon_version):
        print(f"{bcolors.WARNING}Blender version too old for plugin{bcolors.ENDC}")
        notifications.append(("OLD_BLENDER_VERSION", user_blender_version, user_addon_version))

    # check if the user uses a newer blender version
    if (user_blender_version > user_addon_version):
        print(f"{bcolors.WARNING}Blender version newer than tested{bcolors.ENDC}")
        notifications.append(("NEW_BLENDER_VERSION", user_blender_version, user_addon_version))

    # check if the user uses experimental builds
    if (("Beta" in bpy.app.version_string) or ("Alpha" in bpy.app.version_string) or ("Candidate" in bpy.app.version_string)):
        print(f"{bcolors.WARNING}Blender version is experimental{bcolors.ENDC}")
        notifications.append(("EXP_BLENDER_VERSION"))

    return None

def draw_notification(layout):
    col = layout.column().box().column()

    for n in notifications:
        n_type = n[0]

        # Old Blender Version
        if n_type == "OLD_BLENDER_VERSION":
            col.label(text="You are using an old version of Blender. Some features may not work properly.", icon="ERROR")
            col.label(text="Please update Blender to the latest supported version.", icon="BLANK1")
            col.separator(factor=0.5)

        # New Blender Version
        elif n_type == "NEW_BLENDER_VERSION":
            col.label(text="You are using a new version of Blender.", icon="ERROR")
            col.label(text="Some features may not work properly. Please update the plugin.", icon="BLANK1")
            col.label(text="If you already have the latest version, please test it, and report any bugs you may find.", icon="BLANK1")
            col.label(text="You can report bugs in our Discord server.", icon="BLANK1")
            col.operator("wm.url_open", text="Join Discord", icon="URL").url = "https://discord.gg/cnFdGQP"
            col.separator(factor=0.5)

        # Experimental Blender Version
        elif n_type == "EXP_BLENDER_VERSION":
            col.label(text="You are using an experimental version of Blender.", icon="ERROR")
            col.label(text="Some features may not work properly.", icon="BLANK1")
            col.separator(factor=0.5)
        
        return None
        
    col.label(text="You are using a supported version of Blender.", icon="INFO")
    col.separator(factor=0.5)
    
#endregion version check

@contextlib.contextmanager
def suppress_stdout():
    """ A context manager to suppress standard output. """
    original_stdout = sys.stdout  # Save a reference to the original standard output

    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull  # Redirect stdout to the null device
        try:
            yield
        finally:
            sys.stdout = original_stdout  # Restore stdout to the original standard output

def word_wrap(string="", layout=None, alignment="CENTER", max_char=70):
    
    def wrap(string,max_char):

        newstring = ""
        
        while (len(string) > max_char):

            # find position of nearest whitespace char to the left of "width"
            marker = max_char - 1
            while (not string[marker].isspace()):
                marker = marker - 1

            # remove line from original string and add it to the new string
            newline = string[0:marker] + "\n"
            newstring = newstring + newline
            string = string[marker + 1:]
        
        return newstring + string
    
    #Multiline string? 
    if ("\n" in string):
        wrapped = "\n".join([wrap(l,max_char) for l in string.split("\n")])
    else:
        wrapped = wrap(string,max_char)

    #UI Layout Draw? 

    if (layout is not None):

        lbl = layout.column()
        lbl.active = False 

        for l in wrapped.split("\n"):

            line = lbl.row()
            line.alignment = alignment
            line.label(text=l)
            continue 
        
    return wrapped

def template_boxtitle(settings, col, option, text, icon):
    boxcoltitle = col.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_" + option, emboss=False, text=text, icon=icon)


def format_time(seconds_float):
    # Convert float to integer to avoid decimal places
    total_seconds = int(seconds_float)

    # Calculate hours, minutes, and seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Format the time into a string
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def render_image(file_path, mode='EXEC_DEFAULT'):
    """ Render the current scene to the specified file path and return the render time. """
    bpy.context.scene.render.filepath = file_path
    start_time = time.time()
    with suppress_stdout():
        bpy.ops.render.render(mode, write_still=True)
    render_time = time.time() - start_time
    return render_time

def get_subframes(subframes):
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end
    step_size = (end - start) / (subframes +1)
    frame_values = [round(start + i * step_size) for i in range(subframes + 2)]
    return frame_values

def deselect_all(self, context):
    for obj in context.view_layer.objects.selected:
        obj: Object
        obj.select_set(False)

def calculate_object_distance(selected_object_loc: Vector, active_camera_loc):
    return(selected_object_loc - active_camera_loc).length
   
def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value


def decode_json(path: str) -> typing.Union[dict, list]:
    with open(path) as f:
        j = json.load(f)
    return j


def encode_json(j: typing.Union[dict, list], path: str) -> typing.Union[dict, list]:
    with open(path, "w+") as f:
        json.dump(j, f, indent=4)
    return j

def set_file_hidden(f, hide_file=True):
    if sys.platform != "win32":
        return

    hide_flag = "+h" if hide_file else "-h"
    subprocess.call(f'attrib {hide_flag} "{f}"', shell=True)

def link_nodes(tree: NodeTree, output: Node, output_socket, input: Node, input_socket) -> None:
    if isinstance(input_socket, bpy.types.NodeSocket):
        tree.links.new(output.outputs[output_socket], input_socket)
        return
    tree.links.new(output.outputs[output_socket], input.inputs[input_socket])

def create_socket(tree: NodeTree, socket_name: str, socket_type: str, socket_in_out: str, socket_parent=None) -> None:
    tree.interface.new_socket(name=socket_name, in_out=socket_in_out, socket_type=socket_type, parent=socket_parent)