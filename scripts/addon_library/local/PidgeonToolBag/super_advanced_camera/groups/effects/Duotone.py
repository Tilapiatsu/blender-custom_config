import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_duotone_group() -> NodeTree:

    # Create the group
    sac_duotone_group: NodeTree = bpy.data.node_groups.new(name=".SAC Duotone", type="CompositorNodeTree")

    input_node = sac_duotone_group.nodes.new("NodeGroupInput")
    output_node = sac_duotone_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_duotone_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_duotone_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    mix_node_1 = sac_duotone_group.nodes.new("CompositorNodeMixRGB")
    mix_node_1.name = "SAC Effects_Duotone_Colors"
    mix_node_1.inputs[1].default_value = (0.01, 0.01, 0.17, 1)
    mix_node_1.inputs[2].default_value = (1, 0.56, 0.06, 1)

    map_range_node = sac_duotone_group.nodes.new("CompositorNodeMapRange")
    map_range_node.name = "SAC Effects_Duotone_MapRange"
    map_range_node.inputs[1].default_value = 0.1
    map_range_node.inputs[2].default_value = 0.5
    map_range_node.inputs[3].default_value = 0
    map_range_node.inputs[4].default_value = 1
    map_range_node.use_clamp = True

    mix_node_2 = sac_duotone_group.nodes.new("CompositorNodeMixRGB")
    mix_node_2.name = "SAC Effects_Duotone_Blend"
    mix_node_2.inputs[0].default_value = 0

    # Create the links
    link_nodes(sac_duotone_group, input_node, 0, map_range_node, 0)
    link_nodes(sac_duotone_group, map_range_node, 0, mix_node_1, 0)
    link_nodes(sac_duotone_group, mix_node_1, 0, mix_node_2, 2)
    link_nodes(sac_duotone_group, input_node, 0, mix_node_2, 1)
    link_nodes(sac_duotone_group, mix_node_2, 0, output_node, 0)

    # return
    return sac_duotone_group
