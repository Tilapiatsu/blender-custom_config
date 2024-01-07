import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_iso_group() -> NodeTree:

    # Create the group
    sac_iso_group: NodeTree = bpy.data.node_groups.new(name=".SAC ISO", type="CompositorNodeTree")

    input_node = sac_iso_group.nodes.new("NodeGroupInput")
    output_node = sac_iso_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_iso_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_iso_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    add_node = sac_iso_group.nodes.new("CompositorNodeMath")
    add_node.operation = "ADD"
    add_node.use_clamp = True
    add_node.inputs[1].default_value = 1

    lens_distortion_node = sac_iso_group.nodes.new("CompositorNodeLensdist")
    lens_distortion_node.use_jitter = True
    lens_distortion_node.inputs[1].default_value = 0.000001

    color_subtract_node = sac_iso_group.nodes.new("CompositorNodeMixRGB")
    color_subtract_node.blend_type = "SUBTRACT"
    color_subtract_node.use_clamp = True

    math_less_than_node = sac_iso_group.nodes.new("CompositorNodeMath")
    math_less_than_node.operation = "LESS_THAN"
    math_less_than_node.inputs[1].default_value = 0.03

    color_mix_node = sac_iso_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node.blend_type = "MIX"
    color_mix_node.inputs[2].default_value = (0, 0.2, 0, 1)

    despeckle_node = sac_iso_group.nodes.new("CompositorNodeDespeckle")
    despeckle_node.threshold = 0
    despeckle_node.threshold_neighbor = 0
    despeckle_node.name = "SAC Effects_ISO_Despeckle"

    color_add_node = sac_iso_group.nodes.new("CompositorNodeMixRGB")
    color_add_node.blend_type = "ADD"
    color_add_node.name = "SAC Effects_ISO_Add"
    color_add_node.inputs[0].default_value = 0

    # Create the links
    link_nodes(sac_iso_group, input_node, 0, add_node, 0)
    link_nodes(sac_iso_group, add_node, 0, lens_distortion_node, 0)
    link_nodes(sac_iso_group, lens_distortion_node, 0, color_subtract_node, 1)
    link_nodes(sac_iso_group, color_subtract_node, 0, math_less_than_node, 0)
    link_nodes(sac_iso_group, math_less_than_node, 0, color_mix_node, 0)
    link_nodes(sac_iso_group, color_subtract_node, 0, color_mix_node, 1)
    link_nodes(sac_iso_group, color_mix_node, 0, despeckle_node, 1)
    link_nodes(sac_iso_group, despeckle_node, 0, color_add_node, 2)
    link_nodes(sac_iso_group, input_node, 0, color_add_node, 1)
    link_nodes(sac_iso_group, color_add_node, 0, output_node, 0)

    return sac_iso_group
