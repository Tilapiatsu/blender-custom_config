import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_exposure_group() -> NodeTree:

    # Create the group
    sac_exposure_group: NodeTree = bpy.data.node_groups.new(name=".SAC Exposure", type="CompositorNodeTree")

    input_node = sac_exposure_group.nodes.new("NodeGroupInput")
    output_node = sac_exposure_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_exposure_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_exposure_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    exposure_node = sac_exposure_group.nodes.new("CompositorNodeExposure")
    exposure_node.name = "SAC Colorgrade_Light_Exposure"

    # Create the links
    link_nodes(sac_exposure_group, input_node, 0, exposure_node, 0)
    link_nodes(sac_exposure_group, exposure_node, 0, output_node, 0)

    return sac_exposure_group
