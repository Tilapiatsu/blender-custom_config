import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_infrared_group() -> NodeTree:

    # Create the group
    sac_infrared_group: NodeTree = bpy.data.node_groups.new(name=".SAC Infrared", type="CompositorNodeTree")

    input_node = sac_infrared_group.nodes.new("NodeGroupInput")
    output_node = sac_infrared_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_infrared_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_infrared_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    add_node = sac_infrared_group.nodes.new("CompositorNodeMath")
    add_node.operation = "ADD"
    add_node.inputs[1].default_value = 0
    add_node.name = "SAC Effects_Infrared_Add"

    color_ramp_node = sac_infrared_group.nodes.new("CompositorNodeValToRGB")
    color_ramp_node.color_ramp.elements[0].color = (1, 0.122138, 0.715693, 1)
    color_ramp_node.color_ramp.elements[0].position = 0.05
    color_ramp_node.color_ramp.elements[1].color = (0.048172, 0.05286, 0.434154, 1)
    color_ramp_node.color_ramp.elements[1].position = 0.25
    color_ramp_node.color_ramp.elements.new(0.4)
    color_ramp_node.color_ramp.elements[2].color = (0, 1, 0.921582, 1)
    color_ramp_node.color_ramp.elements.new(0.55)
    color_ramp_node.color_ramp.elements[3].color = (0, 0.62396, 0.052861, 1)
    color_ramp_node.color_ramp.elements.new(0.75)
    color_ramp_node.color_ramp.elements[4].color = (1, 0.973445, 0, 1)
    color_ramp_node.color_ramp.elements.new(0.85)
    color_ramp_node.color_ramp.elements[5].color = (1, 0, 0, 1)
    color_ramp_node.color_ramp.elements.new(1)
    color_ramp_node.color_ramp.elements[6].color = (1, 1, 1, 1)

    color_mix_node = sac_infrared_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node.blend_type = "MIX"
    color_mix_node.inputs[0].default_value = 0
    color_mix_node.name = "SAC Effects_Infrared_Mix"

    # Create the links
    link_nodes(sac_infrared_group, input_node, 0, add_node, 0)
    link_nodes(sac_infrared_group, add_node, 0, color_ramp_node, 0)
    link_nodes(sac_infrared_group, color_ramp_node, 0, color_mix_node, 2)
    link_nodes(sac_infrared_group, input_node, 0, color_mix_node, 1)
    link_nodes(sac_infrared_group, color_mix_node, 0, output_node, 0)

    return sac_infrared_group
