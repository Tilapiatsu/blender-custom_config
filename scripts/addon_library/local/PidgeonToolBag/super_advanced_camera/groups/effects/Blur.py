import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_blur_group() -> NodeTree:

    # Create the group
    sac_blur_group: NodeTree = bpy.data.node_groups.new(name=".SAC Blur", type="CompositorNodeTree")

    input_node = sac_blur_group.nodes.new("NodeGroupInput")
    output_node = sac_blur_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_blur_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_blur_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    blur_node = sac_blur_group.nodes.new("CompositorNodeBlur")
    blur_node.name = "SAC Effects_Blur"

    # Create the links
    link_nodes(sac_blur_group, input_node, 0, blur_node, 0)
    link_nodes(sac_blur_group, blur_node, 0, output_node, 0)

    # return
    return sac_blur_group
