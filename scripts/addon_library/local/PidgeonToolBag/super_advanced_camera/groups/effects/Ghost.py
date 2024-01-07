import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_ghost_group() -> NodeTree:

    # Create the group
    sac_ghost_group: NodeTree = bpy.data.node_groups.new(name=".SAC Ghost", type="CompositorNodeTree")

    input_node = sac_ghost_group.nodes.new("NodeGroupInput")
    output_node = sac_ghost_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_ghost_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_ghost_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    ghost_node_3 = sac_ghost_group.nodes.new("CompositorNodeGlare")
    ghost_node_3.name = "SAC Effects_Ghosts"
    ghost_node_3.glare_type = "GHOSTS"
    ghost_node_3.quality = "HIGH"
    ghost_node_3.mix = 1

    color_mix_node_3 = sac_ghost_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node_3.name = "SAC Effects_GhostsStrength"
    color_mix_node_3.blend_type = "ADD"
    color_mix_node_3.inputs[0].default_value = 0

    # Create the links
    link_nodes(sac_ghost_group, input_node, 0, ghost_node_3, 0)
    link_nodes(sac_ghost_group, input_node, 0, color_mix_node_3, 1)
    link_nodes(sac_ghost_group, ghost_node_3, 0, color_mix_node_3, 2)
    link_nodes(sac_ghost_group, color_mix_node_3, 0, output_node, 0)

    # return
    return sac_ghost_group
