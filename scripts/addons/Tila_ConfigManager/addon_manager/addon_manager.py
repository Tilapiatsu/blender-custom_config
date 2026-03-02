from __future__ import annotations
import os
import sys
import json
import shutil
import subprocess
import stat
import platform
from typing import Optional
import bpy
import addon_utils
import importlib
from pathlib import Path
from os import path
from . import admin
from ..config import keymaps, settings
from ..logger import LOG
from ..preferences.ui.log_list import TILA_Config_Log as log_list

root_folder: Path = Path(bpy.utils.script_path_user()).parent

dependencies = ["gitpython"]

create_symbolic_link_file = path.join(path.dirname(path.realpath(__file__)), "create_symbolic_link.py")


def get_installed_addons():
    addons_fake_modules = {}
    addon_utils.modules(module_cache=addons_fake_modules, refresh=False)
    return addons_fake_modules.keys()


def install_dependencies():
    current_dir = Path(path.realpath(__file__)).parent
    dependencies_path = current_dir / "dependencies"
    LOG.debug("Dependency folder : " + str(dependencies_path))
    if dependencies_path not in sys.path:
        sys.path.append(str(dependencies_path))

    if not dependencies_path.exists():
        dependencies_path.mkdir(parents=True, exist_ok=True)
        install = True
    else:
        install = False
        dependency_subfolder = list(dependencies_path.iterdir())

        for d in dependencies:
            found = False
            for s in dependency_subfolder:
                if d.lower() in str(s).lower():
                    found = True

            if not found:
                install = True
                break

    if not install:
        return
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            *dependencies,
            "--target",
            dependencies_path,
        ]
    )


def enable_addon(addon_name):
    if addon_name is None:
        return False

    log_progress = log_list(
        bpy.context.window_manager.tila_config_log_list,
        "tila_config_log_list_idx",
        "ENABLE_ADDON",
    )
    if addon_name in bpy.context.preferences.addons:
        log_progress.warning(f"Addon already Enabled : {addon_name}, skipping")
        log_progress.separator(add_to_satus=True)
        return False
    elif addon_name in get_installed_addons():
        log_progress.start(f"Addon not Installed : {addon_name}")
        return False

    log_progress.start(f"Enabling Addon : {addon_name}")
    try:
        bpy.ops.preferences.addon_enable(module=addon_name)
    except RuntimeError:
        log_progress.error(f"Addon {addon_name} is not loaded, skipping")
    bpy.context.window_manager.keyconfigs.update()
    log_progress.done("Enable Done!")
    log_progress.separator(add_to_satus=True)

    return True


def disable_addon(addon_name):
    log_progress = log_list(
        bpy.context.window_manager.tila_config_log_list,
        "tila_config_log_list_idx",
        "DISABLE_ADDON",
    )
    if addon_name not in bpy.context.preferences.addons:
        log_progress.start(f"Addon already Disabled : {addon_name}")
        return False

    log_progress.start(f"Disabling Addon : {addon_name}")
    bpy.ops.preferences.addon_disable(module=addon_name)
    bpy.context.window_manager.keyconfigs.update()
    log_progress.done("Disable Done!")
    log_progress.separator(add_to_satus=True)

    return True


def file_acces_handler(func, path, exc_info):
    LOG.debug("Handling Error for file ", path)
    LOG.debug(exc_info)
    # Check if file access issue
    if not os.access(path, os.W_OK):
        # Try to change the permision of file
        os.chmod(path, stat.S_IWUSR)
        # call the calling function again
        func(path)


try:
    import git
except (ModuleNotFoundError, ImportError) as e:
    LOG.error(e, store_failure=False)
    install_dependencies()
    import git


class File:
    def __init__(self, path):
        self.log = LOG
        self.path = path
        self._name = None
        self._file = None
        self._ext = None
        self._is_compatible_ext = None
        self._compatible_format = None

    @property
    def name(self):
        if self._name is None:
            self._name = path.basename(path.splitext(self.path)[0])

        return self._name

    @property
    def file(self):
        if self._file is None:
            self._file = path.basename(self.path)

        return self._file

    @property
    def ext(self):
        if self._ext is None:
            self._ext = path.splitext(self.file)[1].lower()

        return self._ext

    @property
    def dirname(self):
        return path.dirname(self.path)

    @property
    def is_compatible_ext(self):
        if self._is_compatible_ext is None:
            self._is_compatible_ext = self.ext in self.compatible_formats.keys()

        return self._is_compatible_ext

    @property
    def compatible_format(self):
        if self._compatible_format is None:
            if self._is_compatible_ext:
                self._compatible_format = self.compatible_formats[self.ext]
            else:
                self._compatible_format = False

        return self._compatible_format

    @property
    def compatible_formats(self):
        return {}


class Json(File):
    def __init__(self, json_path):
        super(Json, self).__init__(json_path)
        self.log = LOG
        self._json_data = None

    # Properties
    @property
    def is_valid(self):
        return path.isfile(self.path)

    @property
    def json_data(self):
        self._json_data = self.get_json_data()

        return self._json_data

    def get_json_attr(self, attr):
        if not self.json_data:
            return ""
        else:
            if attr in self.json_data:
                return self.json_data[attr]
            else:
                self.log.warning('Attribute "{}" doesn\'t exist in json data'.format(attr))
                return ""

    def get_json_data(self):
        json_data = {}
        if not self.is_valid:
            return False

        with open(self.path, "r", encoding="utf-8-sig") as json_file:
            data = json.load(json_file)
            json_data = data

        return json_data

    def save(self, json_dict):
        # Serializing json
        json_object = json.dumps(json_dict, indent=4)

        # Writing to output file
        with open(self.path, "w") as outfile:
            outfile.write(json_object)


class PathAM:
    def __init__(self, path: Optional[Path] = None):
        self._path = path
        self._is_set = True

        if not self.is_set:
            self._is_set = False
            self._path = Path()

        self.log_progress = log_list(
            bpy.context.window_manager.tila_config_log_list,
            "tila_config_log_list_idx",
            "PATH",
        )

    def __str__(self) -> str:
        return str(self._path) if self._path is not None else ""

    @property
    def is_set(self) -> bool:
        if self._is_set:
            return self._path is not None
        return self._is_set

    @property
    def path(self) -> Path:
        return Path(str(self._path).replace("#", str(root_folder)))

    @property
    def exists(self) -> bool:
        if self.is_set:
            return self.path.exists()
        return False

    @property
    def is_file(self) -> bool:
        if self.is_set:
            return self.path.is_file()
        return False

    @property
    def is_dir(self) -> bool:
        if self.is_set:
            return self.path.is_dir()
        return False

    def remove(self) -> None:
        target = "undefined"
        if self.is_file:
            target = "File"
        elif self.is_dir:
            target = "Directory"

        if path.islink(self.path):
            self.log_progress.start(f"Unlink {target} {self.path}")
            self.path.unlink()
        else:
            self.log_progress.start(f"Remove {target} {self.path}")
            if self.is_file:
                os.remove(self.path)
            elif self.is_dir:
                shutil.rmtree(self.path, onexc=file_acces_handler)


class PathElementAM:
    def __init__(self, path_dict, local_path: PathAM):
        self._path_dict = path_dict
        self.local_path = local_path
        self.log_progress = log_list(
            bpy.context.window_manager.tila_config_log_list,
            "tila_config_log_list_idx",
            "PATH_ELEMENT",
        )

    @property
    def is_enable(self):
        return self._path_dict["is_enable"]

    @property
    def local_subpath(self):
        return "" if self._path_dict["local_subpath"] is None else self._path_dict["local_subpath"]

    @property
    def local_subpath_resolved(self):
        if self._path_dict["local_subpath"] is None:
            return self.local_path
        else:
            return PathAM(self.local_path.path / Path(self._path_dict["local_subpath"]))

    @property
    def destination_path(self):
        if self._path_dict["destination_path"] is None:
            return PathAM()
        return PathAM(Path(self._path_dict["destination_path"]))

    def clean(self, force=False):
        if self.destination_path.exists:
            if not force and self.is_enable:
                return

            self.destination_path.remove()
            self.log_progress.done("Clean Done!")

    def link(self, overwrite=False, force=False, as_string=True):
        if not force and not self.is_enable:
            return None

        if self.local_subpath_resolved.path is None or self.destination_path.path is None:
            return None

        if self.destination_path.exists:
            if overwrite:
                self.destination_path.remove()
            else:
                self.log_progress.warning(f"Path Already Exists : Skipping {self.destination_path.path}")
                return None

        self.log_progress.start(f"Linking {self.local_subpath_resolved.path} -> {self.destination_path.path}")

        result = [
            self.local_subpath_resolved.path,
            self.destination_path.path,
            self.local_subpath_resolved.is_dir,
        ]

        return str(result) if as_string else result

    def enable(self, force=False):
        if not force and not self.is_enable:
            return
        if not self.destination_path.is_set:
            return
        elif self.destination_path.is_file:
            addon_name = path.splitext(path.basename(self.destination_path.path))[0]

            if not enable_addon(addon_name):
                return
        elif self.destination_path.is_dir:
            addon_name = path.basename(self.destination_path.path)

            if not enable_addon(addon_name):
                return

    def disable(self, force=False):
        if not force:
            if self.is_enable:
                return
        if not self.destination_path.is_set:
            return

        addon_name = path.splitext(path.basename(self.destination_path.path))[0]

        if not disable_addon(addon_name):
            return


class ElementAM:
    def __init__(self, element_dict, name):
        self.element_dict = element_dict
        self.name = name
        self.root_folder = root_folder
        self.log_progress = log_list(
            bpy.context.window_manager.tila_config_log_list,
            "tila_config_log_list_idx",
            "ELEMENT",
        )

    def __str__(self):
        LOG.debug(self.name)
        s = ""
        s += f"----------------------------------------{self.name}----------------------------------------\n"
        s += f"is_enable = {self.is_enable}\n"
        s += f"is_sync = {self.is_sync}\n"
        s += f"is_submodule = {self.is_submodule}\n"
        s += f"local_path = {self.local_path.path}\n"
        s += f"online_url = {self.online_url}\n"
        s += f"repository_url = {self.repository_url}\n"
        for i, p in enumerate(self.paths):
            s += "--------------------------------------------------------------------------------\n"
            s += f"path {i}\n"
            s += "--------------------------------------------------------------------------------\n"
            s += f"paths.is_enable = {p.is_enable}\n"
            s += f"paths.local_subpath_resolved = {p.local_subpath_resolved.path}\n"
            s += f"paths.destination_path = {p.destination_path.path}\n"
            s += ""

        return s

    @property
    def safe_name(self):
        return self.extension_id if self.is_extension else self.name.replace(" ", "_")

    @property
    def is_sync(self):
        return self.element_dict["is_sync"]

    @property
    def is_enable(self):
        return self.element_dict["is_enable"]

    @property
    def is_extension(self):
        return self.element_dict["is_extension"] and self.extension_id is not None

    @property
    def is_repository(self):
        return self.repository_url is not None

    @property
    def extension_id(self):
        return self.element_dict["extension_id"]

    @property
    def branch(self):
        return self.element_dict["branch"]

    @property
    def is_submodule(self):
        return self.element_dict["is_submodule"]

    @property
    def online_url(self):
        return self.element_dict["online_url"]

    @property
    def repository_url(self):
        return (
            self.element_dict["repository_url"]
            if (not self.is_extension or (self.is_extension and self.element_dict["repository_url"] is not None))
            else "blender_org"
        )

    @property
    def module(self):
        return ("bl_ext." + self.repository_url + "." + self.extension_id) if self.is_extension else self.name

    @property
    def windows_drive(self) -> Path:
        p = self.element_dict["windows_drive"]
        return Path(p) if p is not None else Path("")

    @property
    def linux_drive(self) -> Path:
        p = self.element_dict["linux_drive"]
        return Path(p) if p is not None else Path("")

    @property
    def os_drive(self) -> Path:
        match platform.system():
            case "Windows":
                return self.windows_drive
            case "Linux":
                return self.linux_drive
            case _:
                return Path("")

    @property
    def local_path(self):
        local_path = self.element_dict["local_path"]
        if local_path is None:
            return PathAM()

        return PathAM(self.os_drive.joinpath(Path(self.element_dict["local_path"])))

    @property
    def keymaps(self):
        return self.element_dict["keymaps"]

    @property
    def settings(self):
        return self.module in settings.settings.keys()

    @property
    def paths(self):
        if self.element_dict["paths"] is None:
            return []
        else:
            return [PathElementAM(x, self.local_path) for x in self.element_dict["paths"]]

    def ensure_repo_init(self):
        if not self.local_path.is_set:
            return

        subdir = list(self.local_path.path.iterdir())
        subdir = [str(s.stem) for s in subdir]

        if ".git" not in subdir:
            self.log_progress.start("Init Submodule")
            repo = git.Repo(root_folder)
            repo.git.submodule("update", "--init")

    def clean(self, force=False, clean_cloned=False):
        for p in self.paths:
            p.clean(force=force)

        if self.is_extension:
            self.log_progress.done(f"Uninstalling Extension : {self.extension_id}")
            bpy.ops.extensions.package_uninstall(repo_index=0, pkg_id=self.extension_id)

        if not clean_cloned:
            return

        if force and self.is_sync and not self.is_submodule:
            if self.local_path.exists:
                self.local_path.remove()
                self.log_progress.done("Clean Done!")
                self.log_progress.separator(add_to_satus=True)

    def sync(self, overwrite=False, force=False):
        if not force and not self.is_sync:
            return

        if self.is_extension:
            self.log_progress.start(f"Installing Extension {self.extension_id}")
            # print(os.listdir(bpy.context.preferences.extensions.repos[0].directory))
            bpy.ops.extensions.package_install(repo_index=0, pkg_id=self.extension_id, enable_on_install=False)
            # print(os.listdir(bpy.context.preferences.extensions.repos[0].directory))
            self.log_progress.done("Extension Installtion Done!")
            self.log_progress.separator(add_to_satus=True)
            return

        if self.repository_url is None or not self.local_path.is_set:
            return

        if self.local_path.exists and not self.is_submodule:
            if overwrite:
                self.local_path.remove()
            else:
                # print(f'Path Already Exists : Skipping {self.local_path.path}')
                return

        self.log_progress.start(f"Syncing {self.name} to {self.local_path.path}")

        if self.is_submodule:
            self.ensure_repo_init()
            repo = git.Repo(str(self.local_path.path))
            repo.git.submodule("update", "--init")
            if self.branch is not None:
                message = f"Cheking out branch : {self.branch}"
                self.log_progress.start(message)
                repo.git.checkout(self.branch)
            message = "Pull from origin"
            self.log_progress.start(message)
            # o = repo.remotes
            # o.origin.pull()
        else:
            kwargs = {"branch": self.branch} if self.branch is not None else {}
            # if self.branch is not None:
            try:
                git.Repo.clone_from(self.repository_url, str(self.local_path.path), **kwargs)
            except Exception as e:
                print(e)
                self.log_progress.done("Syncing Failed!")
                self.log_progress.separator(add_to_satus=True)
                return

        self.log_progress.done("Syncing Done!")
        self.log_progress.separator(add_to_satus=True)

    def link(self, overwrite=False, force=False, as_string=True):
        if not self.local_path.is_set or self.is_extension:
            return []

        link_commands = []
        for p in self.paths:
            command = p.link(overwrite=overwrite, force=force, as_string=as_string)
            if command is None:
                continue
            link_commands.append(command)

        return link_commands

    def enable(self, force=False):
        if not force and not self.is_enable:
            return

        if self.is_extension:
            enable_addon(self.module)
            return

        if len(self.paths) == 0:
            enable_addon(self.module)
        else:
            for p in self.paths:
                p.enable(force=force)

    def disable(self, force=False):
        if not force and self.is_enable:
            return

        if not len(self.paths):
            disable_addon(self.name)
        else:
            for p in self.paths:
                p.disable(force=force)

    def set_keymaps(self, restore=False, all=False):
        if self.keymaps:
            try:
                importlib.reload(keymaps)
                km = keymaps.keymaps[self.module].TILA_Config_Keymaps
                keymap_instance = km()
                if restore:
                    keymap_instance.keymap_restore(all=all)
                keymap_instance.set_keymaps()
                self.log_progress.separator(add_to_satus=True)
            except AttributeError as e:
                self.log_progress.warning(f"{self.name} Addon was not assigned properly \n {e}")
                LOG.error(f"{e}")

    def set_settings(self):
        try:
            addon_settings = settings.settings[self.module].TILA_Config_Settings
            setting_instance = addon_settings()
            setting_instance.set_settings()
            self.log_progress.separator(add_to_satus=True)

        except AttributeError as e:
            self.log_progress.warning(f"{self.safe_name} : {e}")


class AddonManager:
    def __init__(self, json_path):
        self._json_path = json_path
        self.json = Json(json_path)
        self.processing = False
        self.queue_list = []
        self.log_progress = log_list(
            bpy.context.window_manager.tila_config_log_list,
            "tila_config_log_list_idx",
            "ADDON_MANAGER",
        )

    @property
    def elements(self):
        return {k: ElementAM(v, k) for k, v in self.json.json_data.items() if k[0] != "_"}

    def save_json(self, json_dict):
        self.json.save(json_dict)

    def queue_clean(self, element_name=None, force=False, clean_cloned=False):
        if element_name is None:
            for e in self.elements.values():
                self.queue(
                    [
                        self.clean,
                        {
                            "element_name": e.name,
                            "force": force,
                            "clean_cloned": clean_cloned,
                        },
                    ]
                )
        elif element_name in self.elements.keys():
            self.queue(
                [
                    self.clean,
                    {
                        "element_name": element_name,
                        "force": force,
                        "clean_cloned": clean_cloned,
                    },
                ]
            )

    def clean(self, element_name=None, force=False, clean_cloned=False):
        self.processing = True

        if element_name is None:
            for e in self.elements.values():
                e.clean(force=force, clean_cloned=clean_cloned)
        elif element_name in self.elements.keys():
            self.elements[element_name].clean(force=force, clean_cloned=clean_cloned)

        self.processing = False

    def queue_sync(self, element_name=None, overwrite=False, force=False):
        if element_name is None:
            for e in self.elements.values():
                self.queue(
                    [
                        self.sync,
                        {
                            "element_name": e.name,
                            "overwrite": overwrite,
                            "force": force,
                        },
                    ]
                )
        elif element_name in self.elements.keys():
            self.queue(
                [
                    self.sync,
                    {
                        "element_name": element_name,
                        "overwrite": overwrite,
                        "force": force,
                    },
                ]
            )

    def sync(self, element_name=None, overwrite=False, force=False):
        self.processing = True

        if element_name is None:
            for e in self.elements.values():
                e.sync(overwrite=overwrite, force=force)
        elif element_name in self.elements.keys():
            self.elements[element_name].sync(overwrite=overwrite, force=force)

        self.processing = False

    def queue_link(self, element_name=None, overwrite=False):
        if element_name is None:
            for e in self.elements.values():
                self.queue([self.link, {"element_name": e.name, "overwrite": overwrite}])
        elif element_name in self.elements.keys():
            self.queue([self.link, {"element_name": element_name, "overwrite": overwrite}])

    def link(self, element_name=None, overwrite=False, force=False):
        self.processing = True

        link_command = []
        if element_name is None:
            for e in self.elements.values():
                command = e.link(
                    overwrite=overwrite,
                    force=force,
                    as_string=platform.system() == "Windows",
                )
                if not len(command):
                    continue
                link_command += command
        elif element_name in self.elements.keys():
            command = self.elements[element_name].link(
                overwrite=overwrite,
                force=force,
                as_string=platform.system() == "Windows",
            )
            if not len(command):
                return
            link_command = command

        sp_command = [create_symbolic_link_file, "--", "--file_to_link", *link_command]
        match platform.system():
            case "Windows":
                admin.elevate(sp_command)
            case "Linux":
                for command in link_command:
                    os.symlink(command[0], command[1], target_is_directory=command[2])

        self.processing = False

    def queue_enable(self, element_name=None, force=False):
        if element_name is None:
            for e in self.elements.values():
                self.queue([self.enable, {"element_name": e.name, "force": force}])
        elif element_name in self.elements.keys():
            self.queue([self.enable, {"element_name": element_name, "force": force}])

    def enable(self, element_name=None, force=False):
        self.processing = True

        if element_name is None:
            for e in self.elements.values():
                e.enable(force=force)
        elif element_name in self.elements.keys():
            self.elements[element_name].enable(force=force)

        self.processing = False

    def queue_disable(self, element_name=None, force=False):
        if element_name is None:
            for e in self.elements.values():
                self.queue([self.disable, {"element_name": e.name, "force": force}])
        elif element_name in self.elements.keys():
            self.queue([self.disable, {"element_name": element_name, "force": force}])

    def disable(self, element_name=None, force=False):
        self.processing = True

        if element_name is None:
            for e in self.elements.values():
                e.disable(force=force)
        elif element_name in self.elements.keys():
            self.elements[element_name].disable(force=force)

        self.processing = False

    def queue_set_keymaps(self, element_name=None, restore=False):
        if element_name is None:
            for e in self.elements.values():
                if not e.keymaps:
                    continue

                self.queue([self.set_keymaps, {"element_name": e.name, "restore": restore}])

        elif element_name in self.elements.keys():
            if not self.elements[element_name].keymaps:
                return

            self.queue([self.set_keymaps, {"element_name": element_name, "restore": restore}])

    def set_keymaps(self, element_name=None, restore=False):
        self.processing = True

        if element_name is None:
            for e in self.elements.values():
                e.set_keymaps(restore=restore)
        elif element_name in self.elements.keys():
            self.elements[element_name].set_keymaps(restore=restore, all=True)

        self.processing = False

    def queue_set_settings(self, element_name=None):
        if element_name is None:
            for e in self.elements.values():
                if not e.settings:
                    continue

                self.queue([self.set_settings, {"element_name": e.name}])

        elif element_name in self.elements.keys():
            if not self.elements[element_name].settings:
                return

            self.queue([self.set_settings, {"element_name": element_name}])

    def set_settings(self, element_name=None):
        self.processing = True

        if element_name is None:
            for e in self.elements.values():
                e.set_settings()
        elif element_name in self.elements.keys():
            self.elements[element_name].set_settings()

        self.processing = False

    def queue(self, action):
        self.queue_list.append(action)

    def flush_queue(self):
        self.queue_list = []

    def next_action(self):
        if len(self.queue_list) == 0:
            self.log_progress.done("Queue Done !")
            return

        action = self.queue_list.pop(0)

        action[0](**action[1])

    def __str__(self):
        s = ""
        for _, v in self.elements.items():
            s += f"{v}\n"

        return s
