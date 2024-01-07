import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_perspectiveshift_group() -> NodeTree:

    # Create the group
    sac_perspectiveshift_group: NodeTree = bpy.data.node_groups.new(name=".SAC PerspectiveShift", type="CompositorNodeTree")

    input_node = sac_perspectiveshift_group.nodes.new("NodeGroupInput")
    output_node = sac_perspectiveshift_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_perspectiveshift_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_perspectiveshift_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    corner_pin_node = sac_perspectiveshift_group.nodes.new("CompositorNodeCornerPin")
    corner_pin_node.name = "SAC Effects_PerspectiveShift_CornerPin"

    scale_node = sac_perspectiveshift_group.nodes.new("CompositorNodeScale")
    scale_node.name = "SAC Effects_PerspectiveShift_Scale"
    scale_node.space = "RELATIVE"

    # Create the links
    link_nodes(sac_perspectiveshift_group, input_node, 0, corner_pin_node, 0)
    link_nodes(sac_perspectiveshift_group, corner_pin_node, 0, scale_node, 0)
    link_nodes(sac_perspectiveshift_group, scale_node, 0, output_node, 0)

    return sac_perspectiveshift_group
