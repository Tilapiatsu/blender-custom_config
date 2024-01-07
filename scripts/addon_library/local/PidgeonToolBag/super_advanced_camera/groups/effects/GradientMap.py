import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_gradientmap_group() -> NodeTree:

    # Create the group
    sac_gradientmap_group: NodeTree = bpy.data.node_groups.new(name=".SAC GradientMap", type="CompositorNodeTree")

    input_node = sac_gradientmap_group.nodes.new("NodeGroupInput")
    output_node = sac_gradientmap_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_gradientmap_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_gradientmap_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    gradientmap_node = sac_gradientmap_group.nodes.new("CompositorNodeValToRGB")
    gradientmap_node.name = "SAC Effects_GradientMap"

    colormix_node = sac_gradientmap_group.nodes.new("CompositorNodeMixRGB")
    colormix_node.name = "SAC Effects_GradientMap_Mix"
    colormix_node.inputs[0].default_value = 0

    # Create the links
    link_nodes(sac_gradientmap_group, input_node, 0, gradientmap_node, 0)
    link_nodes(sac_gradientmap_group, gradientmap_node, 0, colormix_node, 2)
    link_nodes(sac_gradientmap_group, input_node, 0, colormix_node, 1)
    link_nodes(sac_gradientmap_group, colormix_node, 0, output_node, 0)

    # return
    return sac_gradientmap_group
