import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_contrast_group() -> NodeTree:

    # Create the group
    sac_contrast_group: NodeTree = bpy.data.node_groups.new(name=".SAC Contrast", type="CompositorNodeTree")

    input_node = sac_contrast_group.nodes.new("NodeGroupInput")
    output_node = sac_contrast_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_contrast_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_contrast_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    contrast_node = sac_contrast_group.nodes.new("CompositorNodeBrightContrast")
    contrast_node.name = "SAC Colorgrade_Light_Contrast"

    # Create the links
    link_nodes(sac_contrast_group, input_node, 0, contrast_node, 0)
    link_nodes(sac_contrast_group, contrast_node, 0, output_node, 0)

    return sac_contrast_group
