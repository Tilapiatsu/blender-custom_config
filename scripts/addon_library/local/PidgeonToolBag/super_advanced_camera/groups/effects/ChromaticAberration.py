import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_chromatic_group() -> NodeTree:

    # Create the group
    sac_chromatic_group: NodeTree = bpy.data.node_groups.new(name=".SAC ChromaticAberration", type="CompositorNodeTree")

    input_node = sac_chromatic_group.nodes.new("NodeGroupInput")
    output_node = sac_chromatic_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_chromatic_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_chromatic_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    chromatic_node = sac_chromatic_group.nodes.new("CompositorNodeLensdist")
    chromatic_node.use_fit = True
    chromatic_node.name = "SAC Effects_ChromaticAberration"

    # Create the links
    link_nodes(sac_chromatic_group, input_node, 0, chromatic_node, 0)
    link_nodes(sac_chromatic_group, chromatic_node, 0, output_node, 0)

    # return
    return sac_chromatic_group
