import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_overlay_group() -> NodeTree:

    # Create the group
    sac_overlay_group: NodeTree = bpy.data.node_groups.new(name=".SAC Overlay", type="CompositorNodeTree")

    input_node = sac_overlay_group.nodes.new("NodeGroupInput")
    output_node = sac_overlay_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_overlay_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_overlay_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    mix_node = sac_overlay_group.nodes.new("CompositorNodeMixRGB")
    mix_node.blend_type = "OVERLAY"
    mix_node.name = "SAC Effects_Overlay"
    mix_node.inputs[0].default_value = 0

    texture_node = sac_overlay_group.nodes.new("CompositorNodeImage")
    texture_node.name = "SAC Effects_Overlay_Texture"

    # Create the links
    link_nodes(sac_overlay_group, input_node, 0, mix_node, 1)
    link_nodes(sac_overlay_group, texture_node, 0, mix_node, 2)
    link_nodes(sac_overlay_group, mix_node, 0, output_node, 0)

    return sac_overlay_group
