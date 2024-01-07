import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_negative_group() -> NodeTree:

    # Create the group
    sac_negative_group: NodeTree = bpy.data.node_groups.new(name=".SAC Negative", type="CompositorNodeTree")

    input_node = sac_negative_group.nodes.new("NodeGroupInput")
    output_node = sac_negative_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_negative_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_negative_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    negative_node = sac_negative_group.nodes.new("CompositorNodeInvert")
    negative_node.inputs[0].default_value = 0
    negative_node.name = "SAC Effects_Negative"

    # Create the links
    link_nodes(sac_negative_group, input_node, 0, negative_node, 1)
    link_nodes(sac_negative_group, negative_node, 0, output_node, 0)

    # return
    return sac_negative_group
