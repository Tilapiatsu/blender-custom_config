import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket

def create_whitelevel_group() -> NodeTree:

    # Create the group
    sac_whitelevel_group: NodeTree = bpy.data.node_groups.new(name=".SAC WhiteLevel", type="CompositorNodeTree")

    input_node = sac_whitelevel_group.nodes.new("NodeGroupInput")
    output_node = sac_whitelevel_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_whitelevel_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_whitelevel_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    rgb_curves_node = sac_whitelevel_group.nodes.new("CompositorNodeCurveRGB")
    rgb_curves_node.name = "SAC Colorgrade_Color_WhiteLevel"

    # Create the links
    link_nodes(sac_whitelevel_group, input_node, 0, rgb_curves_node, 1)
    link_nodes(sac_whitelevel_group, rgb_curves_node, 0, output_node, 0)

    return sac_whitelevel_group
