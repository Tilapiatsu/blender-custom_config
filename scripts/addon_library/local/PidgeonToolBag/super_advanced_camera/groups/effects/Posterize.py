import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_posterize_group() -> NodeTree:

    # Create the group
    sac_posterize_group: NodeTree = bpy.data.node_groups.new(name=".SAC Posterize", type="CompositorNodeTree")

    input_node = sac_posterize_group.nodes.new("NodeGroupInput")
    output_node = sac_posterize_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_posterize_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_posterize_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    posterize_node = sac_posterize_group.nodes.new("CompositorNodePosterize")
    posterize_node.name = "SAC Effects_Posterize"
    posterize_node.inputs[1].default_value = 128

    # Create the links
    link_nodes(sac_posterize_group, input_node, 0, posterize_node, 0)
    link_nodes(sac_posterize_group, posterize_node, 0, output_node, 0)

    return sac_posterize_group
