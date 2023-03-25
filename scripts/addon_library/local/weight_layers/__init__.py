# Copyright (C) 2021  Andrew Stevenson
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This addon is designed to work both on its own, and also as a part of the Alpha Trees addon (https://blenderartists.org/t/alpha-trees-wip-nature-addon)
# This means that there are a few functions that are only used once is this addon, but that are accessed by Alpha Trees addon when it is bundeled with it.

import bpy
import addon_utils
import importlib
import os
import sys

# from . import WL_ui, WL_settings, WL_preferences, WL_callbacks, WL_functions, WL_operators, WL_constants, WL_icons
# from .layer_scripts import *
from . import WL_constants

bl_info = {
    "name": "Weight Layers 2.0",
    "author": "Andrew Stevenson",
    "description": "Create realtime procedural weight maps",
    "blender": (3, 0, 0),
    "version": (2, 0, 0),
    "location": "N panel > Weight layers",
    # "tracker_url": "https://blenderartists.org/t/alpha-trees-wip-nature-addon",
    "support": "COMMUNITY",
    "category": "3D View"
}

# modules = [
#     WL_constants,
#     WL_icons,
#     WL_ui,
#     WL_functions,
#     WL_callbacks,
#     WL_settings,
#     WL_operators,
#     WL_preferences,
#     ]

# modules = [
#     WL_icons,
#     WL_ui,
#     WL_settings,
#     WL_operators,
#     WL_preferences,
# ]


def get_current_level_modules(file, package):
    """Gets all modules on the current level with a return function
    :rtype: list[modules]
    """
    # get names of modules from files
    top_level = []
    dir_name = os.path.dirname(file)
    for f in os.listdir(dir_name):
        path = os.path.join(dir_name, f)
        if os.path.isdir(path) and not f.startswith("."):
            if "__init__.py" in os.listdir(path):
                top_level.append(package + "." + f)

        elif f.endswith(".py") and "__" not in f:
            top_level.append(package + "." + f.replace(".py", ""))

    # import needed modules if not present
    for f in top_level:
        try:
            _ = sys.modules[f]
        except KeyError:
            importlib.import_module(f, package)

    # filter for those with a register function
    with_register = [sys.modules[m] for m in top_level if hasattr(sys.modules[m], "register")]
    return with_register


if "bpy" in locals():
    # get all modules that are part of the addon
    wl_modules = [sys.modules[m] for m in sys.modules.keys() if __package__ in m]
    for m in wl_modules:
        importlib.reload(m)

modules = get_current_level_modules(__file__, __package__)


def register():
    # check if another version of Weight Layers is installed (as standalone, or part of Alpha Trees)
    # If standalone, will concede to Alpha Trees, if Alpha Trees, will disable standalone.
    importlib.reload(WL_constants)
    if WL_constants.ALREADY_INSTALLED:
        if WL_constants.IS_AT:
            # if part of alpha trees
            for addon in bpy.context.preferences.addons.keys():
                if "weight" in addon.lower() and "layers" in addon.lower():
                    addon_utils.disable(addon, default_set=True, handle_error=None)
        else:
            # if standalone
            print(
                "Weight Layers is already installed as part of Alpha Trees. If you want to update it, please download the latest version of Alpha Trees."
            )
            addon_utils.disable(__package__, default_set=True, handle_error=None)
            return

    for module in modules:
        module.register()


def unregister():
    for module in modules:
        try:
            module.unregister()
        except ValueError:
            continue
