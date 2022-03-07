import bpy
import mathutils

from .WL_functions import *
from .WL_constants import GROUP_TYPES, TEMP_NAME


# Scene
def use_pinned_obj_update(self, context):
    if self.use_pinned_obj:
        self.pinned_obj = context.object
    else:
        None


# Object


def relink_layer_list_group(group, list):
    """Recalculates the links between all nodes in the chain. Takes the node group to relink,
    and the list (CollectionProperty) to take the length of."""
    nodes = group.nodes
    links = group.links

    group_input = nodes.get("Group Input")
    group_output = nodes.get("Group Output")
    wl_nodes = get_wl_group_nodes(group, [GROUP_TYPES["stack"], GROUP_TYPES["layer"]])

    for node in wl_nodes:
        try:
            index = int(node.name)
        except ValueError:
            raise ValueError(f"Node name '{node.name}' cannot be converted to int, aborting")
        prev_node, next_node = get_layer_neghbour_nodes(nodes, list, index)

        # geometry sockets
        if not prev_node:
            prev_node = group_input
        if not next_node:
            next_node = group_output

        if node.outputs["Geometry"].links:
            links.remove(node.outputs["Geometry"].links[0])

        links.new(prev_node.outputs["Geometry"], node.inputs["Geometry"])
        links.new(node.outputs["Geometry"], next_node.inputs["Geometry"])

        # data flow sockets
        result_socket = get_wl_socket(node.outputs, "result")
        for link in result_socket.links:
            links.remove(link)

        if index == 0:
            prev_result = None
        else:
            prev_result = get_wl_socket(prev_node.outputs, "result")

        if index == len(list) - 1:
            next_input = None
        else:
            next_input = get_wl_socket(next_node.inputs, "input")

        if next_input and next_input.links:
            links.remove(next_input.links[0])

        if prev_result:
            links.new(prev_result, get_wl_socket(node.inputs, "input"))

        if next_input:
            links.new(get_wl_socket(node.outputs, "result"), next_input)
        elif result_socket.links:
            links.remove(result_socket.links[0])


def new_layer_stack_slot(self):
    """Add a new layer stack slot"""
    stack_list = self.layer_stacks
    index = len(stack_list) - 1

    new_slot = stack_list.add()
    new_slot.name = "Layer stack " + str(index)
    self.g_index = len(self.layer_stacks) - 1

    if stack_list:
        self.relink_stack_group()
        self.organise_stack_list()

    return new_slot


def remove_layer_stack_slot(self, context, index):
    """Remove the layer stack slot at the given index"""
    stack_list = self.layer_stacks
    modifier = get_wl_mod_group(context, self.id_data, get_modifier=True)
    mod_group = modifier.node_group

    if len(stack_list) == 0:
        return

    stack_nodes = get_wl_group_nodes(mod_group, GROUP_TYPES["stack"])

    if len(stack_list) == 1:
        obj = modifier.id_data
        group = mod_group
        obj.modifiers.remove(modifier)
        if group:
            remove_node_group_references(group)
            bpy.data.node_groups.remove(group)

    else:
        stack_list[index].layer_stacks_enum = "NONE"

    stack_list.remove(index)
    if index == self.g_index:
        self.g_index = min(max(0, self.g_index - 1), len(stack_list) - 1)

    for node in stack_nodes:
        if int(node.name) > index:
            node.name = str(int(node.name) - 1)

    if stack_list:
        self.relink_stack_group()
        self.organise_stack_list()


def move_layer_stack_slot(self, context, from_idx, to_idx):
    """Move the layer stack slot at from_idx to to_idx"""
    mod_group = get_wl_mod_group(context, self.id_data)
    stack_list = self.layer_stacks
    to_idx = max(0, min(to_idx, len(stack_list) - 1))

    stack_list.move(to_idx, from_idx)
    self.g_index = to_idx

    if from_idx != to_idx:
        # rename nodes
        node = None
        if stack_list[to_idx].stack_group:
            node = mod_group.nodes[str(from_idx)]
            node.name = "temp"  # so replaced_node doesn't get .001 suffix
        if stack_list[from_idx].stack_group:
            replaced_node = mod_group.nodes[str(to_idx)]
            replaced_node.name = str(from_idx)
        if node:
            node.name = str(to_idx)

    if stack_list:
        self.relink_stack_group()
        self.organise_stack_list()


# Layer stacks


def new_layer_stack(self, context, name=""):
    """Add a new layer stack"""
    wl = self.id_data.weight_layers
    stack = wl.layer_stacks[wl.g_index]

    mod_group = get_wl_mod_group(context, self.id_data)
    group = append_node_group(GROUPS["stack"], new_instance=True)
    nodes = mod_group.nodes

    # remove previous stack node
    if stack.stack_group:
        prev_stack_node = [
            node for node in nodes if node.type == "GROUP" and node.node_tree.name == stack.stack_group.name
        ][0]
        nodes.remove(prev_stack_node)

    add_stack_group_node(nodes, group, wl)
    wl.relink_stack_group()

    name = name if name else "Layer Stack"
    i = 0
    while True:
        i += 1
        final_name = name + " " + str(i)
        try:
            _ = bpy.data.node_groups[get_stack_group(final_name, only_name=True)]
        except KeyError:
            break
    group.wl.name = final_name
    group.wl.color = get_random_rgb_from_hsv((0.66, 0.9, 0.75), h=0.09, s=0.1, v=0.25)  # blue
    # group.wl.color = colorsys.hsv_to_rgb(random.random(), 1, 1) # set random hue

    for node in group.nodes:
        if node.type == "GROUP" and node.node_tree:
            layer = stack.layers.add()
            node.name = node.name.split("_")[1] + "_" + stack.name
            layer.name = node.name
            layer.node_name = node.name
            layer.layer_group = node.node_tree
            node.node_tree.wl.type = GROUP_TYPES["layer"]

    group.wl.type = GROUP_TYPES["stack"]
    stack.stack_group = group
    stack.mute_remove_node = True

    wl.organise_stack_list()
    group.wl.organise_stack_group()

    # output layer
    layer_types = get_layer_cache()
    output_name = [t for t in layer_types if "-output-" in t.lower()][0]
    output_name = output_name.split("-")[1].upper()
    group.wl.new_layer(context, type=output_name)

    return group.wl


def remove_layer_stack(self, context, index):
    wl = self.id_data.weight_layers
    slot = wl.layer_stacks[index]
    group = slot.stack_group

    # remove layer groups as well
    layers = list(group.wl.layers)
    layers.reverse()
    for layer in layers:
        group.wl.remove_layer(context, index=layer.index)

    # we need to remove all references to the node group before removing it, otherwise it will cause a crash
    for obj in bpy.data.objects:
        for stack in obj.weight_layers.layer_stacks:
            if stack.stack_group and stack.stack_group == group:
                stack.layer_stacks_enum = "NONE"
                stack.stack_group = None

    for node in group.nodes:
        if node.type == "GROUP":
            if node.node_tree.users == 1:
                bpy.data.node_groups.remove(node.node_tree)
            else:
                group.nodes.remove(node)

    remove_node_group_references(group)

    bpy.data.node_groups.remove(group)


def relink_stack_list_group(group, list):
    """Recalculates the links between all nodes in the chain. Takes the node group to relink,
    and the list (CollectionProperty) to take the length of."""
    nodes = group.nodes
    links = group.links
    wl_nodes = get_wl_group_nodes(group, GROUP_TYPES["stack"])

    for node in wl_nodes:
        try:
            index = int(node.name)
        except ValueError:
            raise ValueError(f"Node name '{node.name}' cannot be converted to int, aborting")
        prev_node, next_node = get_stack_neighbour_nodes(nodes, list, index)

        links.new(prev_node.outputs[0], node.inputs[0])
        links.new(node.outputs[0], next_node.inputs[0])


def layer_stacks_enum_items(self, context):
    """Return enum of all layer group node groups"""
    items = [("NONE", "None", "No layer stack selected")]
    for group in bpy.data.node_groups:
        if group.type == "GEOMETRY" and group.wl.type == GROUP_TYPES["stack"]:
            item = (group.wl.name, group.wl.name, group.name)
            items.append(item)

    return items


def layer_stacks_enum_update(self, context):
    """Set the layer stack for the current slot"""
    # reset reference created by alpha trees
    self.vgroup = None
    if self.stack_group:
        for layer in self.stack_group.wl.layers:
            layer.layer_settings.on_remove_stack_instance(context)

    if self.layer_stacks_enum == "NONE":
        if self.stack_group:
            self.stack_group = None
        return

    if self.stack_group:
        if self.stack_group.name == get_stack_group(self.layer_stacks_enum, only_name=True):
            return
    self.stack_group = get_stack_group(self.layer_stacks_enum)


def stack_group_update(self, context):
    modifier = get_wl_mod_group(context, get_modifier=True)
    mod_group = modifier.node_group
    nodes = mod_group.nodes
    links = mod_group.links
    wl = self.id_data.weight_layers
    prev_node, next_node, = get_stack_neighbour_nodes(nodes, wl.layer_stacks, wl.g_index)
    old_node = nodes.get(str(wl.g_index))
    if old_node:
        nodes.remove(old_node)

    if not self.stack_group:
        links.new(prev_node.outputs[0], next_node.inputs[0])
        organise_stack_list(mod_group)
        return

    node = add_stack_group_node(nodes, self.stack_group, wl)
    links.new(prev_node.outputs[0], node.inputs[0])
    links.new(node.outputs[0], next_node.inputs[0])
    organise_stack_list(mod_group)

    for layer in self.stack_group.wl.layers:
        layer.layer_settings.on_new_stack_instance(context)


def stack_index_get(self):
    return list(self.id_data.weight_layers.layer_stacks).index(self)


def stack_name_get(self):
    # initialise if not already
    try:
        return self["stack_name"]
    except KeyError:
        self["stack_name"] = ""
        return ""


def stack_name_set(self, value):
    # This uses get() and set() to gain access to check that the previous value is not the same as the current one,
    # stopping infinite recursion
    if self["stack_name"] == value:
        return

    self["stack_name"] = value

    try:
        current_group = get_stack_group(self.name)
    except KeyError:
        current_group = None

    if current_group:
        input_name = self.name
        input_name = input_name + " " if not input_name.endswith(" ") else input_name

        i = 0
        while True:
            i += 1
            name = input_name + str(i)
            try:
                _ = get_stack_group(name)
            except KeyError:
                break

        self.name = name
    else:
        name = self.name

    group = self.id_data
    group.name = get_stack_group(name, only_name=True)

    for ng in bpy.data.node_groups:
        if ng.type == "GEOMETRY":
            for node in ng.nodes:
                if node.type == "GROUP" and node.node_tree == group:
                    node.label = group.wl.name


def organise_stack_list(group):
    """Sets position and size of all layer stack nodes in the chain"""
    nodes = group.nodes
    group_input = nodes.get("Group Input")
    group_output = nodes.get("Group Output")
    stack_nodes = get_wl_group_nodes(group, type=GROUP_TYPES["stack"])

    for node in stack_nodes:
        node.hide = True
        node.location = (0, 40 * -int(node.name))

    group_input.hide = group_output.hide = True
    group_input.width = group_output.width = 120
    group_input.location = (-group_input.width - 20, 0)
    group_output.location = (200, 0)


def manual_refresh_update(self, context):
    stack_node = get_wl_mod_group(context).nodes.get(str(self.index))
    if self.manual_refresh:
        self.bake_layer_stack()
        stack_node.mute = True
    else:
        stack_node.mute = False

    for layer in stack_node.node_tree.wl.layers:
        if hasattr(layer.layer_settings, "vgroup_name"):
            layer.layer_settings.vgroup_name = layer.layer_settings.vgroup_name


def bake_layer_stack(context, stack):
    bake_group = stack.stack_group
    obj = stack.id_data

    modifier = get_wl_mod_group(context, obj, get_modifier=True)
    idx = list(obj.modifiers).index(modifier) + 1
    bpy.ops.object.modifier_copy(modifier=modifier.name)
    mod = obj.modifiers[idx]
    temp_group = mod.node_group.copy()
    mod.node_group = temp_group
    group_output = temp_group.nodes.get("Group Output")

    for i, socket in enumerate(group_output.inputs[1:]):
        if socket.links:
            from_node = socket.links[0].from_node
            if from_node not in get_nodes_with_group(temp_group.nodes, bake_group, list=True):
                temp_group.outputs.remove(temp_group.outputs[i])

    for node in temp_group.nodes:
        node.mute = False

    for k in mod.keys():
        if k.startswith("Output") and mod[k].endswith(TEMP_NAME):
            mod[k] = mod[k][:-len(TEMP_NAME)]

    temp_group = mod.node_group

    orig_active = context.object
    context.view_layer.objects.active = obj

    bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    context.view_layer.objects.active = orig_active
    bpy.data.node_groups.remove(temp_group)


def vgroup_name_update(self, context, prev_name):
    """Changes all references to the previous vgroup name to the new one"""
    layers = self.layers
    for i in range(len(layers)):
        layer_node = self.id_data.nodes[str(i)]
        for socket in layer_node.inputs:
            if hasattr(socket, "default_value"):
                if socket.default_value == prev_name:
                    socket.default_value = self.vgroup.name


# Node groups


def node_group_type_items():
    items = []
    for t in GROUP_TYPES:
        t = GROUP_TYPES[t]
        items.append((t, t.capitalize(), t.capitalize()))
    return items


# Layers


def new_layer(self, context, type):
    """Add A new layer of the given type"""
    stack_group = self.id_data
    layers = stack_group.wl.layers
    layer_group = append_node_group(type, new_instance=True)
    layer_group.wl.type = GROUP_TYPES["layer"]
    nodes = list(layer_group.nodes)

    # Add metadata frames
    split = layer_group.wl.full_type.split("-")
    for i, name in zip([1, 3], ["type", "icon"]):
        node = get_wl_node(layer_group, name)
        if not node:
            name = NODES[name]
            node = layer_group.nodes.new("NodeFrame")
            node.name = name
            node.label = split[i]
            node.location = (node.width * i - node.width, min([n.location.y for n in nodes]) - 300)

    layer_info = get_layer_info(layer_group)
    if not layer_info["dont_use_mix"]:
        nodes = layer_group.nodes
        links = layer_group.links

        group_output = nodes.get("Group Output")
        group_input = nodes.get("Group Input")
        if not group_input or not group_output:
            self.report({"ERROR"}, "Could not find nodes named 'Group Input'/'Group Ouput'")
            return {"CANCELLED"}
        input_socket = get_wl_socket(group_input.outputs, "input")
        result_socket = get_wl_socket(group_output.inputs, "result")

        mix_node = nodes.new("ShaderNodeMixRGB")
        mix_node.name = mix_node.label = NODES["mix"]
        mix_node.blend_type = "ADD"
        mix_node.inputs[0].default_value = 1

        if not result_socket.links:
            self.report({"ERROR"}, "There is no node linket to the result socket of this layer group")
            return {"CANCELLED"}

        prev_output = result_socket.links[0].from_socket
        prev_node = prev_output.node
        mix_node.location = group_output.location = prev_node.location
        mix_node.location.x += prev_node.width + 20
        group_output.location.x += prev_node.width + mix_node.width + 40

        links.new(input_socket, mix_node.inputs[1])
        links.new(prev_output, mix_node.inputs[2])
        links.new(mix_node.outputs[0], result_socket)

    i = 0
    while True:
        i += 1
        name = GROUPS["layer"] + split[1] + "_" + str(i)
        try:
            _ = bpy.data.node_groups[name]
        except KeyError:
            break
    layer_group.name = name

    nodes = stack_group.nodes
    layer_node = nodes.new("GeometryNodeGroup")
    layer_node.node_tree = layer_group
    layer_node.name = str(len(layers))
    layer_node.use_custom_color = True
    layer_node.color = get_random_rgb_from_hsv((0.33, 0.9, 0.75), h=0.09, s=0.1, v=0.25)  # green

    layer = stack_group.wl.layers.add()
    layer.type = split[1]
    layer.name = split[1].capitalize().replace("_", " ")
    layer.layer_group = layer_group

    stack_group.wl.relink_stack_group()
    stack_group.wl.organise_stack_group()

    if len(layers) > 1 and layers[-2].type == "output":
        bpy.ops.weight_layer.layer_actions(action="MOVE_UP", index=-1)
        layer = layers[-2]

    layer.layer_settings.on_creation(context)

    return layer


def remove_layer(self, context, index):
    """Remove the layer at the given index"""

    layer = self.layers[index]
    layer.layer_settings.on_removal(bpy.context)
    group = layer.layer_group
    stack_group = self.id_data

    # remove adjustment layer groups as well
    for _ in layer.adjustments:
        bpy.ops.weight_layer.adjustment_actions(action="REMOVE", layer_index=index)

    self.layers.remove(index)
    remove_node_group_references(group)

    # rename all nodes that came after
    layer_nodes = get_wl_group_nodes(stack_group, GROUP_TYPES["layer"])
    layer_nodes.sort(key=lambda node: int(node.name))
    for node in layer_nodes:
        if int(node.name) > index:
            node.name = str(int(node.name) - 1)

    bpy.data.node_groups.remove(group)


def layer_types_items(self, context):
    items = []
    layer_types = get_layer_cache()
    for i, l in enumerate(layer_types):
        info = layer_types[l]
        items.append((info["name"].upper(), info["name"], info["category"], info["icon"], i))
    return items


def layer_index_get(self):
    return list(self.id_data.wl.layers).index(self)


def organise_layer_list(group):
    nodes = group.nodes

    input_frame = get_wl_node(group, "in_frame")
    output_frame = get_wl_node(group, "out_frame")

    l_nodes = get_wl_group_nodes(group, GROUP_TYPES["layer"])

    l_nodes.sort(key=lambda node: int(node.name))
    total_width = sum(n.width + 20 for n in l_nodes)

    xpos = -total_width / 2
    for node in l_nodes:
        node.location = (xpos, 0)
        xpos += node.width + 20

    # the position needs to be converted to local space within the frame
    in_nodes = [node for node in nodes if node.parent == input_frame]
    out_nodes = [node for node in nodes if node.parent == output_frame]

    in_pos = mathutils.Vector((min(n.location.x for n in in_nodes), max(n.location.y for n in in_nodes)))
    out_pos = mathutils.Vector((min(n.location.x for n in out_nodes), max(n.location.y for n in out_nodes)))

    for node in in_nodes:
        node.location = node.location - in_pos
    for node in out_nodes:
        node.location = node.location - out_pos

    input_frame.location = ((-total_width / 2) - input_frame.width, -30)
    output_frame.location = (total_width / 2 + 30, -30)
    return


def get_layer_adjustment_settings(self):
    try:
        return getattr(self.all_settings, self.type.lower())
    except AttributeError:
        return self.all_settings.default_settings


# adjustments


def adjustment_types_items(self, context):
    items = []
    layer_types = get_layer_cache()
    for i, l in enumerate(layer_types):
        info = layer_types[l]
        if info["type"] == ADJUSTMENT_NAME:
            items.append((info["name"].upper(), info["name"], info["category"], info["icon"], i))
    return items


def adjustment_index_get(self):
    layer_index = self.layer_index
    return list(self.id_data.wl.layers[int(layer_index)].adjustments).index(self)


def adjustment_layer_index_get(self):
    path = self.path_from_id()
    record = False
    layer_index = ""
    for ch in path:
        if ch == "[":
            record = True
            continue
        elif ch == "]":
            break
        if record:
            layer_index += ch
    return int(layer_index)


def relink_layer_group(group, list):
    nodes = group.nodes
    links = group.links

    adj_nodes = get_wl_group_nodes(group, GROUP_TYPES["adjustment"])
    adj_nodes.sort(key=lambda node: int(node.name))
    group_input = nodes.get("Group Input")
    group_output = nodes.get("Group Output")

    # print(adj_nodes)
    # if not adj_nodes:
    #     prev_socket = get_wl_socket(group_input.outputs, "ext_input")
    #     if prev_socket:
    #         mix_node = get_wl_node(group, "mix")
    #         links.new(prev_socket, mix_node.inputs[2])

    for node in adj_nodes:
        try:
            index = int(node.name)
        except ValueError:
            raise ValueError(f"Node name '{node.name}' cannot be converted to int, aborting")
        prev_node, next_node = get_adjustment_neighbour_nodes(nodes, list, index)

        # Geometry links
        prev_geo_node = prev_node
        if prev_node not in adj_nodes:
            prev_geo_node = group_input
        next_geo_node = next_node
        if next_node not in adj_nodes:
            next_geo_node = group_output

        links.new(prev_geo_node.outputs["Geometry"], node.inputs["Geometry"])
        links.new(node.outputs["Geometry"], next_geo_node.inputs["Geometry"])

        # data flow links
        prev_socket = get_wl_socket(prev_node.outputs, "result")
        next_socket = get_wl_socket(next_node.inputs, "input")

        if not prev_socket:
            for output in prev_node.outputs:
                if output.enabled:
                    prev_socket = output
                    break
        if not next_socket:
            next_socket = next_node.inputs[2]

        links.new(prev_socket, get_wl_socket(node.inputs, "input"))
        links.new(get_wl_socket(node.outputs, "result"), next_socket)


def organise_layer_group(group):
    nodes = group.nodes
    mix_node = get_wl_node(group, "mix")
    group_output = [node for node in nodes if node.type == "GROUP_OUTPUT"][0]
    adj_nodes = get_wl_group_nodes(group, GROUP_TYPES["adjustment"])
    adj_nodes.sort(key=lambda node: int(node.name))
    adj_nodes.append(get_wl_node(group, "mix"))
    adj_nodes.append(group_output)

    first_socket = get_wl_socket(adj_nodes[0].inputs, "input")
    first_socket = first_socket if first_socket else mix_node.inputs[2]
    prev_node = first_socket.links[0].from_node

    for node in adj_nodes:
        node.location = prev_node.location
        node.location.x += prev_node.width + 20
        prev_node = node


def active_adjustment_update(self, context):
    layer = self.id_data.wl.layers[self.layer_index]

    if self.active is True:
        for adj in layer.adjustments:
            if adj != self:
                adj.active = False
        layer.a_index = self.index
