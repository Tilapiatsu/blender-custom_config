import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_warp_group() -> NodeTree:

    # Create the group
    sac_warp_group: NodeTree = bpy.data.node_groups.new(name=".SAC Warp", type="CompositorNodeTree")

    input_node = sac_warp_group.nodes.new("NodeGroupInput")
    output_node = sac_warp_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_warp_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_warp_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    directional_blur_node = sac_warp_group.nodes.new("CompositorNodeDBlur")
    directional_blur_node.name = "SAC Effects_Warp"

    # Create the links
    link_nodes(sac_warp_group, input_node, 0, directional_blur_node, 0)
    link_nodes(sac_warp_group, directional_blur_node, 0, output_node, 0)

    return sac_warp_group
