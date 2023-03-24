import bpy
from random import uniform
from colorsys import hsv_to_rgb

import os

from .WL_constants import BLEND_PATH, CUSTOM_DRAW_PATH, WL_MOD_NAME, GROUPS, NODES, SOCKETS, LAYER_NAME,\
    ADJUSTMENT_NAME, GROUP_TYPES, ICONS
from . import WL_icons

# UI


def draw_ui_list(
    layout,
    list,
    list_class,
    actions_operator,
    list_name,
    data,
    list_setting,
    index_data,
    index_name,
    menu="",
    rows=3,
):
    """Draw a UI list with the standard button configuration (+, -, up, down, menu),
    returns the button column"""

    row = layout.row(align=True)
    list_str = list_class.bl_rna.identifier

    row.template_list(list_str, list_name, data, list_setting, index_data, index_name, rows=rows)
    column = row.column()
    col = column.column(align=True)
    actions_name = actions_operator.bl_idname
    col.operator(actions_name, text="", icon="ADD").action = "ADD"
    row = col.row(align=True)

    if not list:
        row.enabled = False
    row.operator(actions_name, text="", icon="REMOVE").action = "REMOVE"

    if list:
        if len(list) >= 2:
            col = column.column(align=True)
            col.operator(actions_name, text="", icon="TRIA_UP").action = "UP"
            col.operator(actions_name, text="", icon="TRIA_DOWN").action = "DOWN"

    if menu:
        col = column.column(align=True)
        col.menu(menu, text="", icon="DOWNARROW_HLT")

    return col


def draw_headers(self, context):
    """Draws the pinned icon at the top of the Weight Layers panel,
    and the Trees panel when installed with AT"""

    wl = context.scene.weight_layers
    layout = self.layout
    row = layout.row()
    row.active = wl.use_pinned_obj
    row.prop(wl, "use_pinned_obj", text="", emboss=False, icon="PINNED" if wl.use_pinned_obj else "UNPINNED")
    layout.separator(factor=0.5)


def get_random_rgb_from_hsv(input_hsv, h=0.1, s=0.1, v=0.1):
    """takes an hsv value and randomises the value of each component by the value passed in the parameters h, s and v"""
    color = input_hsv
    h = uniform(color[0] - h, color[0] + h)
    s = uniform(color[1] - s, color[1] + s)
    v = uniform(color[2] - v, color[2] + v)
    color = hsv_to_rgb(h, s, v)
    return color


# General


def get_wl_prefs(context):
    return context.preferences.addons[__package__.split(".")[0]].preferences


def get_wl_icon(name):
    name = ICONS[name]
    return WL_icons.icon_groups["wl_icons"][name].icon_id


def append_node_group(name: str, new_instance: bool):
    """Returns the node group of the given name. If new_instance is True,
    the returned node group will not have any other users, but if it is False,
    the node group may be used in multiple places"""

    instances = len([ng for ng in bpy.data.node_groups if name in ng.name])
    path = BLEND_PATH
    with bpy.data.libraries.load(path) as (data_from, data_to):
        for ng in data_from.node_groups:
            if name in ng.upper():
                data_to.node_groups.append(ng)
                break
        else:
            raise KeyError(f"Could not find node with name: {name} from: {path}")
    node_group = data_to.node_groups[0]

    if new_instance is True and instances > 0:
        node_group = node_group.copy()

    node_group.wl.full_type = ng
    node_group.name = name + "_" + str(instances + 1)

    return node_group


def get_wl_vars(context):
    """Returns: object.weight_layers, layer_stack, layers
    or None if it doesn't exist."""
    wl = get_wl_obj(context).weight_layers
    if wl.layer_stacks:
        stack = wl.layer_stacks[wl.g_index]
        layers = stack.stack_group.wl.layers if stack.stack_group else None
    else:
        stack = layers = None

    return wl, stack, layers


def get_nodes_with_group(source_nodes, group, list=False):
    """returns all group nodes in the node tree that have the specified group as their node trees.
    returns a list if there are more than one."""

    nodes = [n for n in source_nodes if n.type == "GROUP" and n.node_tree == group]
    if len(nodes) == 0:
        raise KeyError(f"No nodes with group '{group.name}' as their node tree")
    elif len(nodes) > 0 and not list:
        nodes = nodes[0]

    return nodes


def get_wl_node(group, name):
    """Get the node in the given node tree that has the name definied in the NODES dictionary in WL_constants.
    returns None if no node is found"""
    nodes = group.nodes if isinstance(group, bpy.types.GeometryNodeTree) else group
    return nodes.get(NODES[name])


def get_wl_socket(sockets, name):
    """Get the socket in the given list of sockets that has the name definied in the SOCKETS dictionary in WL_constants.
    returns None if no socket is found"""
    return sockets.get(SOCKETS[name])


def remove_node_group_references(group):
    """Remove all nodes that use this group and reconnect sockets after"""
    for ng in bpy.data.node_groups:
        if ng.type == "GEOMETRY":
            for node in ng.nodes:
                if node.type == "GROUP" and node.node_tree == group:
                    for link in node.internal_links:
                        from_socket = link.from_socket
                        to_socket = link.to_socket
                        if from_socket.links and to_socket.links:
                            from_socket = from_socket.links[0].from_socket
                            to_socket = to_socket.links[0].to_socket
                            ng.links.new(from_socket, to_socket)

                    ng.nodes.remove(node)


# WL


def get_wl_obj(context):
    """Returns the either context.object or the pinned object (weight_layers.pinned_obj)
    depending on weight_layers.use_pinned_obj"""
    wl = context.scene.weight_layers
    obj = wl.pinned_obj if wl.use_pinned_obj else context.object
    return obj


def get_wl_mod_group(context, obj=None, get_modifier=False):
    """Return the modifier node group for this object.
    This houses the layer stack, and is object specific"""

    obj = get_wl_obj(context) if not obj else obj
    modifiers = obj.modifiers
    # convert to list to be able to access the index
    mods = list(modifiers)

    index = -1
    for mod in mods:
        if mod.type == "NODES":
            if mod.node_group:
                if mod.node_group.wl.type == GROUP_TYPES["stack_list"]:
                    break
                else:
                    index = mods.index(mod) - 1
    else:
        mod = modifiers.new(WL_MOD_NAME, type="NODES")
        prev_obj = context.object
        group = mod.node_group
        group.wl.type = GROUP_TYPES["stack_list"]
        group.name = GROUPS["stack_list"] + obj.name

        context.view_layer.objects.active = obj
        bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=index)
        context.view_layer.objects.active = prev_obj

    # create new instance if object has been duplicated
    mod_group = mod.node_group
    if mod_group.users > 1:
        # check to see if being called from ui (can't modify blend data while drawing)
        update_name = True
        try:
            mod_group.name = mod_group.name
        except AttributeError:
            update_name = False
        if update_name:
            mod_group = mod.node_group.copy()
            mod_group.name = GROUPS["stack_list"] + obj.name
            mod.node_group = mod_group

    return mod if get_modifier else mod.node_group


def get_wl_group_nodes(group, type):
    """returns all of the group nodes where node.group.wl.type is equal to the type provided"""
    if isinstance(type, str):
        type = [type]

    if isinstance(group, bpy.types.GeometryNodeTree):
        nodes = group.nodes
    else:
        nodes = group
    layer_nodes = []
    for node in nodes:
        if node.type == "GROUP" and node.node_tree and node.node_tree.wl.type in type:
            layer_nodes.append(node)
    return layer_nodes


# Layer Stacks


def get_layer_neghbour_nodes(nodes, list, index):
    """get the nodes that come before and after the current node in the chain"""

    prev_node = next_node = None

    offset = 1
    while not prev_node or not next_node:
        prev_node = nodes.get(str(index - offset)) if not prev_node else prev_node
        next_node = nodes.get(str(index + offset)) if not next_node else next_node

        if offset > len(list) - 1:
            break

        offset += 1

    return prev_node, next_node


def get_stack_neighbour_nodes(nodes, list, index):
    input_node = nodes.get("Group Input")
    output_node = nodes.get("Group Output")

    prev_node = next_node = None
    if index == 0:
        prev_node = input_node
    if index == len(list) - 1:
        next_node = output_node

    offset = 1
    while not prev_node or not next_node:
        prev_node = nodes.get(str(index - offset)) if not prev_node else prev_node
        next_node = nodes.get(str(index + offset)) if not next_node else next_node

        if offset > len(list) - 1:
            prev_node = input_node if not prev_node else prev_node
            next_node = output_node if not next_node else next_node
            break

        offset += 1

    return prev_node, next_node


def get_stack_group(name, only_name=False):
    """returns the node group for a given name, KeyError if it doesn't exist.
    if only_name, only returns the name of the node group, even if it doesn't exist"""
    name = GROUPS["stack"] + "_" + name
    return name if only_name else bpy.data.node_groups[name]


def add_stack_group_node(nodes, group, wl):
    """Adds a group to the object's modifier group that will house the layers"""
    stack_node = nodes.new("GeometryNodeGroup")
    stack_node.name = str(wl.g_index)
    stack_node.label = group.wl.name
    stack_node.node_tree = group
    stack_node.use_custom_color = True
    stack_node.color = group.wl.color
    stack_node.hide = True
    stack_node.width = 180
    stack_node.select = False
    nodes.active = stack_node
    wl.organise_stack_list()
    return stack_node


# Layers


def get_layer_info(layer_group):
    info = {
        "type": get_wl_node(layer_group, "type"),
        "icon": get_wl_node(layer_group, "icon"),
        "dont_use_mix": get_wl_node(layer_group, "dont_use_mix")
    }
    for i in info:
        info[i] = info[i].label if info[i] else ""
        if info[i] in ["True", "False"]:
            info[i] = eval(info[i])
    return info


def check_node_script_exists(type):
    path = CUSTOM_DRAW_PATH
    type = type.lower()
    for file in os.listdir(path):
        if file == LAYER_NAME + "_" + type + ".py":
            return LAYER_NAME + "_" + type
        elif file == ADJUSTMENT_NAME + "_" + type + ".py":
            return ADJUSTMENT_NAME + "_" + type
    else:
        return False


# Idea shamelessly taken from the Erindale Toolkit addon by Campbell Barton (very worth it!):
# https://erindale.gumroad.com/l/erintools


def get_layer_cache(*, reload=False):
    """returns a list of all layer nodes in the base resources.blend file, as a tuple of:
    full name, layer name, category, icon."""

    node_cache = get_layer_cache._node_cache
    if reload or not node_cache:
        node_cache = {}
        with bpy.data.libraries.load(BLEND_PATH) as (data_from, data_to):
            for ng in data_from.node_groups:
                if ng.startswith(LAYER_NAME) or ng.startswith(ADJUSTMENT_NAME):
                    # name format is "WLAYER/WLADJUST-name-category-icon"
                    split = ng.split("-")
                    layer = ng.startswith(LAYER_NAME)
                    icon = split[3].upper()
                    icon = icon if icon else "RENDERLAYERS"
                    try:
                        node_cache[ng] = {
                            "type": split[0],
                            "name": split[1].capitalize(),
                            "category": split[2].capitalize() if layer else "Adjustments",
                            "icon": icon
                        }
                    except IndexError as e:
                        node_cache[ng] = {
                            "type": "ERROR",
                            "name": split[1].capitalize() + "_NAME_ERROR",
                            "category": "ERROR",
                            "icon": "ERROR",
                        }

                        print(str(e) + " for node: " + split[1])

    get_layer_cache._node_cache = node_cache
    return node_cache


get_layer_cache._node_cache = {}

# adjustments


def get_adjustment_neighbour_nodes(nodes, list, index):
    mix_node = get_wl_node(nodes, "mix")
    adj_nodes = get_wl_group_nodes(nodes, GROUP_TYPES["adjustment"])
    adj_nodes.sort(key=lambda node: int(node.name))

    node = nodes.get(str(index))
    is_connected = bool(get_wl_socket(node.inputs, "input").links) or bool(get_wl_socket(node.outputs, "result").links)
    prev_node = nodes.get(str(index - 1))
    next_node = nodes.get(str(index + 1))

    if not next_node:
        next_node = mix_node

    if not prev_node:
        if index == 0 and is_connected:
            prev_node = get_wl_socket(node.inputs, "input").links[0].from_node
        else:
            socket = get_wl_socket(next_node.inputs, "input")
            socket = socket if socket else next_node.inputs[2]  # mix node
            prev_node = socket.links[0].from_node

    return prev_node, next_node
