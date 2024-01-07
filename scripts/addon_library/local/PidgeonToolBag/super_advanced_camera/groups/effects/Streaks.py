import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_streaks_group() -> NodeTree:

    # Create the group
    sac_streaks_group: NodeTree = bpy.data.node_groups.new(name=".SAC Streaks", type="CompositorNodeTree")

    input_node = sac_streaks_group.nodes.new("NodeGroupInput")
    output_node = sac_streaks_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_streaks_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_streaks_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    streaks_node_2 = sac_streaks_group.nodes.new("CompositorNodeGlare")
    streaks_node_2.name = "SAC Effects_Streaks"
    streaks_node_2.glare_type = "STREAKS"
    streaks_node_2.quality = "HIGH"
    streaks_node_2.mix = 1
    streaks_node_2.streaks = 6
    streaks_node_2.angle_offset = 0.1963495
    streaks_node_2.fade = 0.85

    color_mix_node_2 = sac_streaks_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node_2.name = "SAC Effects_StreaksStrength"
    color_mix_node_2.blend_type = "ADD"
    color_mix_node_2.inputs[0].default_value = 0

    # Create the links
    link_nodes(sac_streaks_group, input_node, 0, streaks_node_2, 0)
    link_nodes(sac_streaks_group, input_node, 0, color_mix_node_2, 1)
    link_nodes(sac_streaks_group, streaks_node_2, 0, color_mix_node_2, 2)
    link_nodes(sac_streaks_group, color_mix_node_2, 0, output_node, 0)

    return sac_streaks_group
