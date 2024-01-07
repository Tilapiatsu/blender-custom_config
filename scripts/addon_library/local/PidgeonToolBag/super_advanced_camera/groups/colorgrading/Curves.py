import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_curves_group() -> NodeTree:

    # Create the group
    sac_curves_group: NodeTree = bpy.data.node_groups.new(name=".SAC Curves", type="CompositorNodeTree")

    input_node = sac_curves_group.nodes.new("NodeGroupInput")
    output_node = sac_curves_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_curves_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_curves_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    rgb_curves_node = sac_curves_group.nodes.new("CompositorNodeCurveRGB")
    rgb_curves_node.name = "SAC Colorgrade_Curves_RGB"
    rgb_curves_node.inputs[0].default_value = 0

    hsv_curves_node = sac_curves_group.nodes.new("CompositorNodeHueCorrect")
    hsv_curves_node.name = "SAC Colorgrade_Curves_HSV"
    hsv_curves_node.inputs[0].default_value = 0

    # Create the links
    link_nodes(sac_curves_group, input_node, 0, rgb_curves_node, 1)
    link_nodes(sac_curves_group, rgb_curves_node, 0, hsv_curves_node, 1)
    link_nodes(sac_curves_group, hsv_curves_node, 0, output_node, 0)

    return sac_curves_group
