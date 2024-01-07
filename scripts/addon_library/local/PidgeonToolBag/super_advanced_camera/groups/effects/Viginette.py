import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_viginette_group() -> NodeTree:

    # Create the group
    sac_viginette_group: NodeTree = bpy.data.node_groups.new(name=".SAC Viginette", type="CompositorNodeTree")

    input_node = sac_viginette_group.nodes.new("NodeGroupInput")
    output_node = sac_viginette_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_viginette_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_viginette_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    roundness_map_range_node = sac_viginette_group.nodes.new("CompositorNodeMapRange")
    roundness_map_range_node.name = "SAC Effects_Viginette_Roundness"
    roundness_map_range_node.inputs[0].default_value = 0
    roundness_map_range_node.inputs[1].default_value = -1
    roundness_map_range_node.inputs[2].default_value = 1
    roundness_map_range_node.inputs[3].default_value = 0
    roundness_map_range_node.inputs[4].default_value = 1

    intensity_map_range_node = sac_viginette_group.nodes.new("CompositorNodeMapRange")
    intensity_map_range_node.name = "SAC Effects_Viginette_Intensity"
    intensity_map_range_node.inputs[0].default_value = 0
    intensity_map_range_node.inputs[1].default_value = -1
    intensity_map_range_node.inputs[2].default_value = 1
    intensity_map_range_node.inputs[3].default_value = 0
    intensity_map_range_node.inputs[4].default_value = 1

    midpoint_map_range_node = sac_viginette_group.nodes.new("CompositorNodeMapRange")
    midpoint_map_range_node.name = "SAC Effects_Viginette_Midpoint"
    midpoint_map_range_node.inputs[0].default_value = 0
    midpoint_map_range_node.inputs[1].default_value = -0.999
    midpoint_map_range_node.inputs[2].default_value = 1
    midpoint_map_range_node.inputs[3].default_value = 0
    midpoint_map_range_node.inputs[4].default_value = 2

    midpoint_add_node = sac_viginette_group.nodes.new("CompositorNodeMath")
    midpoint_add_node.operation = "ADD"
    midpoint_add_node.inputs[1].default_value = (0.25/4)
    midpoint_add_node.name = "SAC Effects_Viginette_Midpoint_Add"

    whiten_node = sac_viginette_group.nodes.new("CompositorNodeMath")
    whiten_node.operation = "ADD"
    whiten_node.inputs[1].default_value = 1
    whiten_node.use_clamp = True

    lense_distortion_node = sac_viginette_group.nodes.new("CompositorNodeLensdist")

    scale_node = sac_viginette_group.nodes.new("CompositorNodeScale")
    scale_node.space = "RELATIVE"

    multiply_node = sac_viginette_group.nodes.new("CompositorNodeMath")
    multiply_node.operation = "MULTIPLY"

    pingpong_node = sac_viginette_group.nodes.new("CompositorNodeMath")
    pingpong_node.operation = "PINGPONG"
    pingpong_node.inputs[1].default_value = 0.5

    multiply_node2 = sac_viginette_group.nodes.new("CompositorNodeMath")
    multiply_node2.operation = "MULTIPLY"
    multiply_node2.inputs[1].default_value = 2
    multiply_node2.use_clamp = True

    greater_than_node = sac_viginette_group.nodes.new("CompositorNodeMath")
    greater_than_node.operation = "GREATER_THAN"
    greater_than_node.inputs[1].default_value = 0.5
    greater_than_node.use_clamp = True

    add_node = sac_viginette_group.nodes.new("CompositorNodeMath")
    add_node.operation = "ADD"
    add_node.use_clamp = True

    directional_blur_node = sac_viginette_group.nodes.new("CompositorNodeDBlur")
    directional_blur_node.iterations = 6
    directional_blur_node.zoom = 0.25
    directional_blur_node.name = "SAC Effects_Viginette_Directional_Blur"

    color_mix_node = sac_viginette_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node.blend_type = "MIX"

    # Create the links
    link_nodes(sac_viginette_group, input_node, 0, whiten_node, 0)
    link_nodes(sac_viginette_group, whiten_node, 0, lense_distortion_node, 0)
    link_nodes(sac_viginette_group, roundness_map_range_node, 0, lense_distortion_node, 1)
    link_nodes(sac_viginette_group, lense_distortion_node, 0, scale_node, 0)
    link_nodes(sac_viginette_group, midpoint_map_range_node, 0, midpoint_add_node, 1)
    link_nodes(sac_viginette_group, midpoint_add_node, 0, scale_node, 1)
    link_nodes(sac_viginette_group, midpoint_add_node, 0, scale_node, 2)
    link_nodes(sac_viginette_group, scale_node, 0, multiply_node, 1)
    link_nodes(sac_viginette_group, whiten_node, 0, multiply_node, 0)
    link_nodes(sac_viginette_group, multiply_node, 0, directional_blur_node, 0)
    link_nodes(sac_viginette_group, intensity_map_range_node, 0, pingpong_node, 0)
    link_nodes(sac_viginette_group, pingpong_node, 0, multiply_node2, 0)
    link_nodes(sac_viginette_group, multiply_node2, 0, add_node, 0)
    link_nodes(sac_viginette_group, directional_blur_node, 0, add_node, 1)
    link_nodes(sac_viginette_group, add_node, 0, color_mix_node, 0)
    link_nodes(sac_viginette_group, intensity_map_range_node, 0, greater_than_node, 0)
    link_nodes(sac_viginette_group, greater_than_node, 0, color_mix_node, 1)
    link_nodes(sac_viginette_group, input_node, 0, color_mix_node, 2)
    link_nodes(sac_viginette_group, color_mix_node, 0, output_node, 0)

    return sac_viginette_group
