import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_vibrance_group() -> NodeTree:

    # Create the group
    sac_vibrance_group: NodeTree = bpy.data.node_groups.new(name=".SAC Vibrance", type="CompositorNodeTree")

    input_node = sac_vibrance_group.nodes.new("NodeGroupInput")
    output_node = sac_vibrance_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_vibrance_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_vibrance_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    separate_rgb_node = sac_vibrance_group.nodes.new("CompositorNodeSeparateColor")

    maximum_node_1 = sac_vibrance_group.nodes.new("CompositorNodeMath")
    maximum_node_1.operation = "MAXIMUM"
    maximum_node_2 = sac_vibrance_group.nodes.new("CompositorNodeMath")
    maximum_node_2.operation = "MAXIMUM"

    minimum_node_1 = sac_vibrance_group.nodes.new("CompositorNodeMath")
    minimum_node_1.operation = "MINIMUM"
    minimum_node_2 = sac_vibrance_group.nodes.new("CompositorNodeMath")
    minimum_node_2.operation = "MINIMUM"

    subtract_node_1 = sac_vibrance_group.nodes.new("CompositorNodeMath")
    subtract_node_1.operation = "SUBTRACT"
    subtract_node_2 = sac_vibrance_group.nodes.new("CompositorNodeMath")
    subtract_node_2.operation = "SUBTRACT"
    subtract_node_2.inputs[0].default_value = 1
    subtract_node_2.use_clamp = True

    divide_node = sac_vibrance_group.nodes.new("CompositorNodeMath")
    divide_node.operation = "DIVIDE"

    hsv_node = sac_vibrance_group.nodes.new("CompositorNodeHueSat")
    hsv_node.name = "SAC Colorgrade_Presets_Vibrance"

    # Create the links
    link_nodes(sac_vibrance_group, input_node, 0, separate_rgb_node, 0)
    link_nodes(sac_vibrance_group, separate_rgb_node, 0, maximum_node_1, 0)
    link_nodes(sac_vibrance_group, separate_rgb_node, 1, maximum_node_1, 1)
    link_nodes(sac_vibrance_group, maximum_node_1, 0, maximum_node_2, 0)
    link_nodes(sac_vibrance_group, separate_rgb_node, 2, maximum_node_2, 1)
    link_nodes(sac_vibrance_group, separate_rgb_node, 0, minimum_node_1, 0)
    link_nodes(sac_vibrance_group, separate_rgb_node, 1, minimum_node_1, 1)
    link_nodes(sac_vibrance_group, minimum_node_1, 0, minimum_node_2, 0)
    link_nodes(sac_vibrance_group, separate_rgb_node, 2, minimum_node_2, 1)
    link_nodes(sac_vibrance_group, maximum_node_2, 0, subtract_node_1, 0)
    link_nodes(sac_vibrance_group, minimum_node_2, 0, subtract_node_1, 1)
    link_nodes(sac_vibrance_group, maximum_node_2, 0, divide_node, 1)
    link_nodes(sac_vibrance_group, subtract_node_1, 0, divide_node, 0)
    link_nodes(sac_vibrance_group, divide_node, 0, subtract_node_2, 1)
    link_nodes(sac_vibrance_group, subtract_node_2, 0, hsv_node, 4)
    link_nodes(sac_vibrance_group, input_node, 0, hsv_node, 0)
    link_nodes(sac_vibrance_group, hsv_node, 0, output_node, 0)

    return sac_vibrance_group
