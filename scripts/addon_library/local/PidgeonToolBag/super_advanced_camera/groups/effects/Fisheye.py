import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_fisheye_group() -> NodeTree:

    # Create the group
    sac_fisheye_group: NodeTree = bpy.data.node_groups.new(name=".SAC Fisheye", type="CompositorNodeTree")

    input_node = sac_fisheye_group.nodes.new("NodeGroupInput")
    output_node = sac_fisheye_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_fisheye_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_fisheye_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    lens_distortion_node = sac_fisheye_group.nodes.new("CompositorNodeLensdist")
    lens_distortion_node.name = "SAC Effects_Fisheye"
    lens_distortion_node.use_fit = True

    # Create the links
    link_nodes(sac_fisheye_group, input_node, 0, lens_distortion_node, 0)
    link_nodes(sac_fisheye_group, lens_distortion_node, 0, output_node, 0)

    # return
    return sac_fisheye_group
