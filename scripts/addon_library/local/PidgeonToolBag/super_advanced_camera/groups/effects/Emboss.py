import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_emboss_group() -> NodeTree:

    # Create the group
    sac_emboss_group: NodeTree = bpy.data.node_groups.new(name=".SAC Emboss", type="CompositorNodeTree")

    input_node = sac_emboss_group.nodes.new("NodeGroupInput")
    output_node = sac_emboss_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_emboss_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_emboss_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    emboss_node = sac_emboss_group.nodes.new("CompositorNodeFilter")
    emboss_node.filter_type = "SHADOW"
    emboss_node.name = "SAC Effects_Emboss"
    emboss_node.inputs[0].default_value = 0

    # Create the links
    link_nodes(sac_emboss_group, input_node, 0, emboss_node, 1)
    link_nodes(sac_emboss_group, emboss_node, 0, output_node, 0)

    # return
    return sac_emboss_group
