import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_saturation_group(NodeName, GroupName) -> NodeTree:

    # Create the group
    sac_saturation_group: NodeTree = bpy.data.node_groups.new(name=GroupName, type="CompositorNodeTree")

    input_node = sac_saturation_group.nodes.new("NodeGroupInput")
    output_node = sac_saturation_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_saturation_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_saturation_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    hsv_node = sac_saturation_group.nodes.new("CompositorNodeHueSat")
    hsv_node.name = NodeName

    # Create the links
    link_nodes(sac_saturation_group, input_node, 0, hsv_node, 0)
    link_nodes(sac_saturation_group, hsv_node, 0, output_node, 0)

    return sac_saturation_group
