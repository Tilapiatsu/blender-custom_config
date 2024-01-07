import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_pixelate_group() -> NodeTree:

    # Create the group
    sac_pixelate_group: NodeTree = bpy.data.node_groups.new(name=".SAC Pixelate", type="CompositorNodeTree")

    input_node = sac_pixelate_group.nodes.new("NodeGroupInput")
    output_node = sac_pixelate_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_pixelate_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_pixelate_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    math_add_node = sac_pixelate_group.nodes.new("CompositorNodeMath")
    math_add_node.operation = "ADD"
    math_add_node.name = "SAC Effects_Pixelate_Size"
    math_add_node.inputs[1].default_value = 1

    math_divide_node = sac_pixelate_group.nodes.new("CompositorNodeMath")
    math_divide_node.operation = "DIVIDE"
    math_divide_node.inputs[0].default_value = 1

    scale_node_1 = sac_pixelate_group.nodes.new("CompositorNodeScale")
    scale_node_1.space = "RELATIVE"
    scale_node_2 = sac_pixelate_group.nodes.new("CompositorNodeScale")
    scale_node_2.space = "RELATIVE"

    pixelate_node = sac_pixelate_group.nodes.new("CompositorNodePixelate")

    # Create the links
    link_nodes(sac_pixelate_group, input_node, 0, scale_node_1, 0)
    link_nodes(sac_pixelate_group, math_divide_node, 0, scale_node_1, 1)
    link_nodes(sac_pixelate_group, math_divide_node, 0, scale_node_1, 2)
    link_nodes(sac_pixelate_group, math_add_node, 0, math_divide_node, 1)
    link_nodes(sac_pixelate_group, scale_node_1, 0, pixelate_node, 0)
    link_nodes(sac_pixelate_group, pixelate_node, 0, scale_node_2, 0)
    link_nodes(sac_pixelate_group, math_add_node, 0, scale_node_2, 1)
    link_nodes(sac_pixelate_group, math_add_node, 0, scale_node_2, 2)
    link_nodes(sac_pixelate_group, scale_node_2, 0, output_node, 0)

    return sac_pixelate_group
