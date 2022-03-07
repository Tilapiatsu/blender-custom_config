from pathlib import PurePath
import bpy

# noqa

# Check if inside alpha trees, or if it is a standalone addon
path = PurePath(__file__).parent
# print(str(path))
IS_AT = "addons" != str(path.parts[-2])
ALREADY_INSTALLED = hasattr(bpy.types.Object, "weight_layers")
AT_ADDON_NAME = path.parts[-2] if IS_AT else ""  # get the name of the alpha trees folder

SCRIPT_PATH = str(path)
CUSTOM_DRAW_PATH = str(path / "layer_scripts")
CUSTOM_ICON_PATH = str(path / "resources" / "custom_icons")
BLEND_PATH = str(path / "resources" / "WL_nodes.blend")
# print(IS_AT, AT_ADDON_NAME, SCRIPT_PATH, BLEND_PATH)

ICONS = {"weight_layers": "weight_layers.png"}

LAYER_NAME = "WLAYER"
ADJUSTMENT_NAME = "WLADJUST"
TEMP_NAME = "_temp"

WL_MOD_NAME = "WL_GEO_NODES"
GROUP_TYPES = {
    "none": "NONE",
    "stack_list": "STACK_LIST",
    "stack": "STACK",
    "layer": "LAYER",
    "adjustment": "ADJUSTMENT",
}

LAYER_TYPES = {
    "input": "input",
    "output": "output",
}

GROUPS = {
    "stack_list": "WL_STACK_LIST_",
    "stack": "WL_LAYER_STACK",
    "layer": "WLAYER_",
}

NODES = {
    "in_frame": "_input_frame_",
    "out_frame": "_output_frame_",
    "info": "_info_frame_",
    "type": "_type_frame_",
    "icon": "_icon_frame_",
    "dont_use_mix": "_dont_use_mix_frame_",
    "mix": "_output_mix_",
}

SOCKETS = {
    "input": "_input_",
    "result": "_result_",
    "ext_input": "_external_input_",
    "ext_output": "_output_",
}
