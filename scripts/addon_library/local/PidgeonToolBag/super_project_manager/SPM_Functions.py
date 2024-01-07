#region import
import os
import bpy
import sys
import json
import time
import shutil
import typing

from ..pidgeon_tool_bag.PTB_Functions import (
    decode_json,
    encode_json,
    set_file_hidden
)

from .SPM_Settings import (
    AddonPreferences,
)

from bpy.types import (
    Context
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty
)

scene_prop = bpy.types.Scene

#endregion import

#region misc

BPS_DATA_FILE = os.path.join(
    os.path.expanduser("~"),
    "Blender Addons Data",
    "blender-project-starter",
    "BPS.json"
)

class Token():
    def __init__(self, value: str) -> None:
        self.value = value
        self.type = "STRING"

        if value == ">":
            self.type = "BRANCH_DOWN"

        if value == "(":
            self.type = "BRACKET_OPEN"

        if value == ")":
            self.type = "BRACKET_CLOSE"

        if value == "+":
            self.type = "ADD"

    def __str__(self) -> str:
        return self.value

    def __eq__(self, __value: 'Token') -> bool:
        return self.value == __value.value

    def is_string(self) -> bool:
        return self.type == "STRING"

    def is_branch_down(self) -> bool:
        return self.type == "BRANCH_DOWN"

    def is_bracket_open(self) -> bool:
        return self.type == "BRACKET_OPEN"

    def is_bracket_close(self) -> bool:
        return self.type == "BRACKET_CLOSE"

    def is_add(self) -> bool:
        return self.type == "ADD"

    def is_valid_closing_token(self) -> bool:
        return self.type in ["STRING", "BRACKET_CLOSE"]

#endregion misc

#region blenderdefender

def setup_addons_data():
    """Setup and validate the addon data."""
    default_addons_data = {
        "automatic_folders": {
            "Default Folder Set": [
                [0, "Blender Files"],
                [1,"Images>>Textures++References++Rendered Images"],
                [0,"Sounds"]
            ]
        },
        "unfinished_projects": [],
        "version": 140
    }

    addons_data_path = os.path.join(
        os.path.expanduser("~"),
        "Blender Addons Data",
        "blender-project-starter"
    )

    addons_data_file = os.path.join(addons_data_path, "BPS.json")

    if not os.path.isdir(addons_data_path):
        os.makedirs(addons_data_path)

    if "BPS.json" not in os.listdir(addons_data_path):
        encode_json(default_addons_data, addons_data_file)

    addons_data = ""
    try:
        addons_data = decode_json(addons_data_file)
    except Exception:
        pass

    if type(addons_data) != dict:
        shutil.move(addons_data_file, os.path.join(addons_data_path, f"BPS.{time.strftime('%Y-%m-%d')}.json"))
        encode_json(default_addons_data, addons_data_file)
        addons_data = default_addons_data

    if addons_data.get("version") < 130:
        encode_json(update_json(addons_data), addons_data_file)


def update_to_120(data):
    data["version"] = 120
    return data


def update_to_130(data):
    default_folders = []
    while data["automatic_folders"]:
        folder = data["automatic_folders"].pop(0)
        default_folders.append([False, folder])

    data["automatic_folders"] = {}
    data["automatic_folders"]["Default Folder Set"] = default_folders

    for i in range(len(data["unfinished_projects"])):
        data["unfinished_projects"][i] = [
            "project", data["unfinished_projects"][i]]

    data["version"] = 130

    return data


def update_json(data: dict) -> dict:
    version = data.get("version", 110)

    if version == 110:
        data = update_to_120(data)
        version = 120

    if version == 120:
        data = update_to_130(data)
        version = 130

    return data

#endregion blenderdefender

#region register

def register_properties():
    prefs: 'AddonPreferences' = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
    
    scene_prop.project_name = StringProperty(
        name="Project Name",
        description="Name of the Project Folder",
        subtype="NONE",
        default="My_Project"
    )

    scene_prop.project_location = StringProperty(
        name="Project Location",
        description="Saves the location of file",
        subtype="DIR_PATH",
        default=prefs.default_project_location
    )

    scene_prop.project_setup = EnumProperty(
        name="Project Setup",
        items=[
            ("Automatic_Setup", "Automatic Setup", "Automatic Project Setup "),
            ("Custom_Setup", "Custom Setup", "My Custom Setup")
        ],
        default="Automatic_Setup"
    )

    scene_prop.open_directory = BoolProperty(
        name="Open Directory",
        description="Open the Project Directory after the Project is created",
        default=True
    )

    scene_prop.add_new_project = BoolProperty(
        name="New unfinished project",
        description="Add a new unfinished project",
        default=False
    )

    scene_prop.save_blender_file = BoolProperty(
        name="Save Blender File",
        description="Save Blender File on build. If disabled, only the project folders are created",
        default=True
    )

    scene_prop.cut_or_copy = BoolProperty(
        name="Cut or Copy",
        description="Decide, if you want to cut or copy your file from the current folder to the project folder.",
    )

    scene_prop.save_file_with_new_name = BoolProperty(
        name="Save Blender File with another name",
        description="Save Blender File with another name",
    )

    scene_prop.save_blender_file_versioned = BoolProperty(
        name="Add Version Number",
        description="Add a Version Number if the File already exists",
    )

    scene_prop.save_file_name = StringProperty(
        name="Save File Name",
        description="Name of the Blender File",
        default="My Blend"
    )

    scene_prop.remap_relative = BoolProperty(
        name="Remap Relative",
        description="Remap the Relative Paths",
        default=True
    )

    scene_prop.compress_save = BoolProperty(
        name="Compress Save",
        description="Compress the File on Save.\nThis will make the File smaller, but it will take longer to save.\nThis will not compress images.",
        default=True
    )

    scene_prop.set_render_output = BoolProperty(
        name="Set the Render Output",
        description="Set the Render Output to the Project Folder",
    )

    scene_prop.project_rearrange_mode = BoolProperty(
        name="Switch to Rearrange Mode",
        description="Switch to Rearrange Mode",
    )

def register_automatic_folders(folders, folderset="Default Folder Set"):
    index = 0
    for folder in folders:
        folders.remove(index)

    data = decode_json(BPS_DATA_FILE)

    for folder in data["automatic_folders"][folderset]:
        f = folders.add()
        f["render_outputpath"] = folder[0]
        f["folder_name"] = folder[1]

def unregister_automatic_folders(folders, folderset="Default Folder Set"):
    data = []
    original_json = decode_json(BPS_DATA_FILE)

    for folder in folders:
        data.append([int(folder.render_outputpath),
                        folder.folder_name])

    original_json["automatic_folders"][folderset] = data

    encode_json(original_json, BPS_DATA_FILE)

def register_project_folders(project_folders, project_path):
    project_info: str = os.path.join(project_path, ".blender_pm")

    index = 0
    for folder in project_folders:
        project_folders.remove(index)

    project_metadata: dict = {}

    if os.path.exists(project_info):
        project_metadata: dict = decode_json(project_info)

    folders: list = project_metadata.get("displayed_project_folders", [])
    if len(folders) == 0:
        folders = [{"folder_path": f}
                   for f in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, f))]

    for folder in folders:
        f = project_folders.add()

        folder_name = os.path.basename(folder.get("folder_path", ""))
        full_path = os.path.join(project_path, folder.get("folder_path", ""))

        f["icon"] = folder.get("icon", "FILE_FOLDER")
        f["name"] = folder_name
        f["is_valid"] = os.path.exists(full_path)
        f["path"] = full_path

#endregion register

#region main

def generate_file_version_number(path):
    i = 1
    number = "0001"

    while os.path.exists("{}_v{}.blend".format(path, number)):
        i += 1
        number = str(i)
        number = "0" * (4 - len(number)) + number

    return "{}_v{}.blend".format(path, number)

def is_file_in_project_folder(context: Context, filepath):
    if filepath == "":
        return False

    filepath = os.path.normpath(filepath)
    project_folder = os.path.normpath(os.path.join(context.scene.project_location,context.scene.project_name))

    return filepath.startswith(project_folder)

def save_filepath(context: Context, filename, subfolder):
    path = os.path.join(context.scene.project_location, context.scene.project_name, subfolder, filename) + ".blend"

    return path

def structure_sets_enum(self, context: Context):
    tooltip = "Select a folder Structure Set."
    items = []

    for i in decode_json(BPS_DATA_FILE)["automatic_folders"]:
        items.append((i, i, tooltip))

    return items

def structure_sets_enum_update(self, context: Context):
    unregister_automatic_folders(self.automatic_folders, self.previous_set)
    register_automatic_folders(self.automatic_folders, self.folder_structure_sets)
    self.previous_set = self.folder_structure_sets

def active_project_enum(self, context: Context):
    tooltip = "Select a project you want to work with."
    items = []

    options = decode_json(BPS_DATA_FILE).get("filebrowser_panel_options", [])

    for el in options:
        items.append((el, os.path.basename(el), tooltip))

    return items

def active_project_enum_update(self: 'AddonPreferences', context: Context):
    register_project_folders(self.project_paths, self.active_project)

def add_unfinished_project(project_path):
    data = decode_json(BPS_DATA_FILE)

    if ["project", project_path] in data["unfinished_projects"]:
        return {'WARNING'}, f"The Project {os.path.basename(project_path)} already exists in the list of unfinished Projects!"

    data["unfinished_projects"].append(["project", project_path])
    encode_json(data, BPS_DATA_FILE)

    return {'INFO'}, f"Successfully added project {os.path.basename(project_path)} to the list of unfinished projects."

def finish_project(index):
    data = decode_json(BPS_DATA_FILE)

    data["unfinished_projects"].pop(index)
    encode_json(data, BPS_DATA_FILE)

def write_project_info(root_path, blend_file_path):
    if not blend_file_path.endswith(".blend"):
        return {"WARNING"}, "Can't create a Super Project Manager project! Please select a Blender file and try again."
    data = {
        "blender_files": {
            "main_file": None,
            "other_files": []
        },
    }
    project_info_path = os.path.join(root_path, ".blender_pm")
    if os.path.exists(project_info_path):
        data = decode_json(project_info_path)
        set_file_hidden(project_info_path, False)

    bfiles = data["blender_files"]
    if bfiles["main_file"] and bfiles["main_file"] != blend_file_path:
        bfiles["other_files"].append(bfiles["main_file"])
    bfiles["main_file"] = blend_file_path

    ct = time.localtime()  # Current time
    data["build_date"] = [ct.tm_year, ct.tm_mon,
                          ct.tm_mday, ct.tm_hour, ct.tm_min, ct.tm_sec]

    encode_json(data, project_info_path)

    set_file_hidden(project_info_path)

    return {"INFO"}, "Successfully created a Super Project Manager project!"

#endregion main

#region path generator

class Subfolders():
    def __init__(self, string: str, prefix: str = ""):
        self.prefix = prefix
        self.tree = {}
        self.warnings = []

        self._return_from_close_bracket = False

        self.tokens = self.tokenize(string)
        if len(self.tokens) == 0:
            return

        self.tree = self.parse_tree()

    def __str__(self) -> str:
        """Return a string representation of the folder tree."""
        return "/\n" + self.__to_string(self.tree)

    def __to_string(self, subtree: dict = None, row_prefix: str = "") -> str:
        """Recursive helper function for __str__()."""

        # Unicode characters for the tree represantation.
        UNICODE_RIGHT = "\u2514"
        UNICODE_VERTICAL_RIGHT = "\u251C"
        UNICODE_VERTICAL = "\u2502"

        return_string = ""

        folders = subtree.keys()

        for i, folder in enumerate(folders):
            unicode_prefix = UNICODE_VERTICAL_RIGHT + " "
            row_prefix_addition = UNICODE_VERTICAL + " "

            if i == len(folders) - 1:
                unicode_prefix = UNICODE_RIGHT + " "
                row_prefix_addition = "  "

            return_string += row_prefix + unicode_prefix + self.prefix + folder + "\n"

            return_string += self.__to_string(subtree.get(folder,{}), row_prefix + row_prefix_addition)

        return return_string

    def tokenize(self, string: str):
        """Tokenize a string with the syntax foo>>bar>>((spam>>eggs))++lorem++impsum
        Possible Tokens: String token, branch down token >>, brackets (( and )), add token ++
        Avoiding Regex. Instead, first envelope the tokens with the safe phrase ::safephrase.
        This phrase won't occur in the string, so it can be safely used for splitting in the next step.
        In the next step, the string is split up into all tokens by splitting up along ::safephrase
        Finally, all empty strings are removed to avoid errors."""

        string = string.replace(">>", "::safephrase>::safephrase")
        string = string.replace("++", "::safephrase+::safephrase")
        string = string.replace("((", "::safephrase(::safephrase")
        string = string.replace("))", "::safephrase)::safephrase")

        tokenized_string = string.split("::safephrase")
        if tokenized_string.count("(") != tokenized_string.count(")"):
            self.warnings.append("Unmatched Brackets detected! This might lead to unexpected behaviour when compiling paths!")

        tokens = [Token(el) for el in tokenized_string if el != ""]

        return tokens

    def parse_tree(self):
        """Parse tokens as tree of paths."""
        tree: dict = {}
        active_folder = ""

        if not self.tokens[-1].is_valid_closing_token():
            last_token = str(self.tokens.pop()) * 2
            self.warnings.append(f"A folder path should not end with '{last_token}'!")

        while self.tokens:
            if self._return_from_close_bracket:
                return tree

            token = self.tokens.pop(0)

            if token.is_string():
                tree[str(token)] = {}
                active_folder = str(token)
                continue

            if token.is_branch_down():
                if active_folder == "":
                    self.warnings.append(
                        "A '>>' can't be used until at least one Folder name is specified! This rule also applies for subfolders.")
                    continue

                tree[active_folder] = self.parse_tree()
                continue

            if token.is_bracket_open():
                tree.update(self.parse_tree())

                self._return_from_close_bracket = False
                continue

            if token.is_bracket_close():
                self._return_from_close_bracket = True
                return tree

        return tree

    def compile_paths(self, subpath: str = "", subtree: dict = None,) -> typing.List[str]:
        """Compile the Tree into a list of relative paths."""
        paths = []

        if subtree is None:
            subtree = self.tree

        for folder in subtree.keys():
            path = os.path.join(subpath, self.prefix + folder)
            paths.append(path)

            paths.extend(self.compile_paths(path, subtree.get(folder, {})))

        return paths

    def build_folders(self, project_dir: str) -> None:
        """Create the folders on the system."""
        for path in self.compile_paths(project_dir):

            if not os.path.isdir(path):
                os.makedirs(path)

def subfolder_enum(self, context: 'Context'):
    prefs: 'AddonPreferences' = context.preferences.addons[__package__.split(".")[0]].preferences

    tooltip = "Select Folder as target folder for your Blender File. Uses Folders from Automatic Setup."
    items = [(" ", "Root", tooltip)]

    folders = self.automatic_folders
    if context.scene.project_setup == "Custom_Setup":
        folders = self.custom_folders

    prefix = ""
    if prefs.prefix_with_project_name:
        prefix = context.scene.project_name + "_"

    try:
        for folder in folders:
            for subfolder in Subfolders(folder.folder_name, prefix).compile_paths():
                # subfolder = subfolder.replace(
                #     "/", ">>").replace("//", ">>").replace("\\", ">>")
                items.append((subfolder, subfolder.replace(prefix, ""), tooltip))
    except Exception as e:
        print("Exception in function subfolder_enum")
        print(e)

    return items

#endregion path generator

#region preferences

def get_active_project_path(self):
    active_directory = bpy.context.space_data.params.directory.decode(encoding="utf-8")

    for i, p in enumerate(self.project_paths):
        if os.path.normpath(p.path) == os.path.normpath(active_directory):
            return i

    return -1

def set_active_project_path(self, value):
    bpy.context.space_data.params.directory = self.project_paths[value].path.encode()

    # Custom setter logic
    self["active_project_path"] = value

#endregion preferences