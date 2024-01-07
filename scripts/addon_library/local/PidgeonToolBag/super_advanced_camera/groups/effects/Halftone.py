import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket

def create_halftone_group() -> NodeTree:

    # Create the group
    sac_halftone_group: NodeTree = bpy.data.node_groups.new(name=".SAC Halftone", type="CompositorNodeTree")

    input_node = sac_halftone_group.nodes.new("NodeGroupInput")
    output_node = sac_halftone_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_halftone_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_halftone_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    value_node = sac_halftone_group.nodes.new("CompositorNodeValue")
    value_node.name = "SAC Effects_Halftone_SizeSave"

    separate_rgb_node = sac_halftone_group.nodes.new("CompositorNodeSeparateColor")

    rgb_to_bw_node = sac_halftone_group.nodes.new("CompositorNodeRGBToBW")

    switch_node = sac_halftone_group.nodes.new("CompositorNodeSwitch")
    switch_node.name = "SAC Effects_Halftone_Switch"

    texture_node = sac_halftone_group.nodes.new("CompositorNodeTexture")
    texture = bpy.data.textures.get(".SAC Dot Screen")
    texture_node.texture = texture
    texture_node.inputs[1].default_value[0] = 96.0
    texture_node.inputs[1].default_value[1] = 54.0
    texture_node.name = "SAC Effects_Halftone_Texture"

    halftone_part = halftonepart_group()

    halftone_part_group_node_c = sac_halftone_group.nodes.new("CompositorNodeGroup")
    halftone_part_group_node_c.node_tree = halftone_part

    halftone_part_group_node_r = sac_halftone_group.nodes.new("CompositorNodeGroup")
    halftone_part_group_node_r.node_tree = halftone_part

    halftone_part_group_node_g = sac_halftone_group.nodes.new("CompositorNodeGroup")
    halftone_part_group_node_g.node_tree = halftone_part

    halftone_part_group_node_b = sac_halftone_group.nodes.new("CompositorNodeGroup")
    halftone_part_group_node_b.node_tree = halftone_part

    combine_rgb_node = sac_halftone_group.nodes.new("CompositorNodeCombineColor")

    value_node = sac_halftone_group.nodes.new("CompositorNodeValue")
    value_node.name = "SAC Effects_Halftone_Value"
    value_node.outputs[0].default_value = -0.2

    delta_node = sac_halftone_group.nodes.new("CompositorNodeValue")
    delta_node.name = "SAC Effects_Halftone_Delta"
    delta_node.outputs[0].default_value = 0.2

    # Create the links
    link_nodes(sac_halftone_group, input_node, 0, separate_rgb_node, 0)
    link_nodes(sac_halftone_group, input_node, 0, rgb_to_bw_node, 0)
    link_nodes(sac_halftone_group, rgb_to_bw_node, 0, halftone_part_group_node_c, "Image")
    link_nodes(sac_halftone_group, separate_rgb_node, 0, halftone_part_group_node_r, "Image")
    link_nodes(sac_halftone_group, separate_rgb_node, 1, halftone_part_group_node_g, "Image")
    link_nodes(sac_halftone_group, separate_rgb_node, 2, halftone_part_group_node_b, "Image")
    link_nodes(sac_halftone_group, texture_node, 0, halftone_part_group_node_c, "Dots")
    link_nodes(sac_halftone_group, texture_node, 0, halftone_part_group_node_r, "Dots")
    link_nodes(sac_halftone_group, texture_node, 0, halftone_part_group_node_g, "Dots")
    link_nodes(sac_halftone_group, texture_node, 0, halftone_part_group_node_b, "Dots")
    link_nodes(sac_halftone_group, value_node, 0, halftone_part_group_node_c, "Value")
    link_nodes(sac_halftone_group, value_node, 0, halftone_part_group_node_r, "Value")
    link_nodes(sac_halftone_group, value_node, 0, halftone_part_group_node_g, "Value")
    link_nodes(sac_halftone_group, value_node, 0, halftone_part_group_node_b, "Value")
    link_nodes(sac_halftone_group, delta_node, 0, halftone_part_group_node_c, "Delta")
    link_nodes(sac_halftone_group, delta_node, 0, halftone_part_group_node_r, "Delta")
    link_nodes(sac_halftone_group, delta_node, 0, halftone_part_group_node_g, "Delta")
    link_nodes(sac_halftone_group, delta_node, 0, halftone_part_group_node_b, "Delta")
    link_nodes(sac_halftone_group, halftone_part_group_node_r, "Image", combine_rgb_node, 0)
    link_nodes(sac_halftone_group, halftone_part_group_node_g, "Image", combine_rgb_node, 1)
    link_nodes(sac_halftone_group, halftone_part_group_node_b, "Image", combine_rgb_node, 2)
    link_nodes(sac_halftone_group, separate_rgb_node, 3, combine_rgb_node, 3)
    link_nodes(sac_halftone_group, halftone_part_group_node_c, "Image", switch_node, 0)
    link_nodes(sac_halftone_group, combine_rgb_node, 0, switch_node, 1)
    link_nodes(sac_halftone_group, switch_node, 0, output_node, 0)

    return sac_halftone_group


def halftonepart_group() -> NodeTree:

    # Create the group
    halftone_part_group: NodeTree = bpy.data.node_groups.new(name=".SAC Halftone part", type="CompositorNodeTree")

    input_node = halftone_part_group.nodes.new("NodeGroupInput")
    output_node = halftone_part_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(halftone_part_group, "Image", "NodeSocketFloat", "INPUT")
    create_socket(halftone_part_group, "Dots", "NodeSocketFloat", "INPUT")
    create_socket(halftone_part_group, "Value", "NodeSocketFloat", "INPUT")
    create_socket(halftone_part_group, "Delta", "NodeSocketFloat", "INPUT")
    create_socket(halftone_part_group, "Image", "NodeSocketFloat", "OUTPUT")

    # Create the nodes
    color_ramp_node_1 = halftone_part_group.nodes.new("CompositorNodeValToRGB")
    color_ramp_node_1.color_ramp.elements[0].position = 0.085

    math_multiply_node = halftone_part_group.nodes.new("CompositorNodeMath")
    math_multiply_node.operation = "MULTIPLY"

    math_add_node_1 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_add_node_1.operation = "ADD"

    math_add_node_2 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_add_node_2.operation = "ADD"

    math_add_node_3 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_add_node_3.operation = "ADD"

    math_add_node_4 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_add_node_4.operation = "ADD"

    math_greater_than_node_1 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_greater_than_node_1.operation = "GREATER_THAN"
    math_greater_than_node_1.inputs[1].default_value = 0

    math_greater_than_node_2 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_greater_than_node_2.operation = "GREATER_THAN"

    math_greater_than_node_3 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_greater_than_node_3.operation = "GREATER_THAN"

    math_greater_than_node_4 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_greater_than_node_4.operation = "GREATER_THAN"

    math_greater_than_node_5 = halftone_part_group.nodes.new("CompositorNodeMath")
    math_greater_than_node_5.operation = "GREATER_THAN"

    color_mix_node_1 = halftone_part_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node_1.blend_type = "MIX"
    color_mix_node_1.inputs[1].default_value = (0, 0, 0, 1)

    color_mix_node_2 = halftone_part_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node_2.blend_type = "MIX"

    color_mix_node_3 = halftone_part_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node_3.blend_type = "MIX"

    color_mix_node_4 = halftone_part_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node_4.blend_type = "MIX"

    color_mix_node_5 = halftone_part_group.nodes.new("CompositorNodeMixRGB")
    color_mix_node_5.blend_type = "MIX"
    color_mix_node_5.inputs[2].default_value = (1, 1, 1, 1)

    dialate_erode_node_1 = halftone_part_group.nodes.new("CompositorNodeDilateErode")
    dialate_erode_node_1.mode = "DISTANCE"
    dialate_erode_node_1.distance = -2

    dialate_erode_node_2 = halftone_part_group.nodes.new("CompositorNodeDilateErode")
    dialate_erode_node_2.mode = "DISTANCE"
    dialate_erode_node_2.distance = -1

    dialate_erode_node_4 = halftone_part_group.nodes.new("CompositorNodeDilateErode")
    dialate_erode_node_4.mode = "DISTANCE"
    dialate_erode_node_4.distance = 1

    filter_soften_node = halftone_part_group.nodes.new("CompositorNodeFilter")
    filter_soften_node.filter_type = "SOFTEN"

    greater_than_node = halftone_part_group.nodes.new("CompositorNodeMath")
    greater_than_node.operation = "GREATER_THAN"
    greater_than_node.inputs[1].default_value = 0.018

    # Create the links
    link_nodes(halftone_part_group, input_node, "Image", color_ramp_node_1, 0)
    link_nodes(halftone_part_group, color_ramp_node_1, 0, math_multiply_node, 0)
    link_nodes(halftone_part_group, input_node, "Dots", math_multiply_node, 1)
    link_nodes(halftone_part_group, input_node, "Value", math_add_node_1, 0)
    link_nodes(halftone_part_group, input_node, "Delta", math_add_node_1, 1)
    link_nodes(halftone_part_group, input_node, "Delta", math_add_node_2, 1)
    link_nodes(halftone_part_group, input_node, "Delta", math_add_node_3, 1)
    link_nodes(halftone_part_group, input_node, "Delta", math_add_node_4, 1)
    link_nodes(halftone_part_group, math_add_node_1, 0, math_add_node_2, 0)
    link_nodes(halftone_part_group, math_add_node_2, 0, math_add_node_3, 0)
    link_nodes(halftone_part_group, math_add_node_3, 0, math_add_node_4, 0)
    link_nodes(halftone_part_group, math_add_node_1, 0, math_greater_than_node_2, 1)
    link_nodes(halftone_part_group, math_add_node_2, 0, math_greater_than_node_3, 1)
    link_nodes(halftone_part_group, math_add_node_3, 0, math_greater_than_node_4, 1)
    link_nodes(halftone_part_group, math_add_node_4, 0, math_greater_than_node_5, 1)
    link_nodes(halftone_part_group, color_ramp_node_1, 0, math_greater_than_node_1, 0)
    link_nodes(halftone_part_group, color_ramp_node_1, 0, math_greater_than_node_2, 0)
    link_nodes(halftone_part_group, color_ramp_node_1, 0, math_greater_than_node_3, 0)
    link_nodes(halftone_part_group, color_ramp_node_1, 0, math_greater_than_node_4, 0)
    link_nodes(halftone_part_group, color_ramp_node_1, 0, math_greater_than_node_5, 0)
    link_nodes(halftone_part_group, math_greater_than_node_1, 0, color_mix_node_1, 0)
    link_nodes(halftone_part_group, math_greater_than_node_2, 0, color_mix_node_2, 0)
    link_nodes(halftone_part_group, math_greater_than_node_3, 0, color_mix_node_3, 0)
    link_nodes(halftone_part_group, math_greater_than_node_4, 0, color_mix_node_4, 0)
    link_nodes(halftone_part_group, math_greater_than_node_5, 0, color_mix_node_5, 0)
    link_nodes(halftone_part_group, math_multiply_node, 0, dialate_erode_node_1, 0)
    link_nodes(halftone_part_group, math_multiply_node, 0, dialate_erode_node_2, 0)
    link_nodes(halftone_part_group, math_multiply_node, 0, dialate_erode_node_4, 0)
    link_nodes(halftone_part_group, dialate_erode_node_1, 0, color_mix_node_1, 2)
    link_nodes(halftone_part_group, dialate_erode_node_2, 0, color_mix_node_2, 2)
    link_nodes(halftone_part_group, math_multiply_node, 0, color_mix_node_3, 2)
    link_nodes(halftone_part_group, dialate_erode_node_4, 0, color_mix_node_4, 2)
    link_nodes(halftone_part_group, color_mix_node_1, 0, color_mix_node_2, 1)
    link_nodes(halftone_part_group, color_mix_node_2, 0, color_mix_node_3, 1)
    link_nodes(halftone_part_group, color_mix_node_3, 0, color_mix_node_4, 1)
    link_nodes(halftone_part_group, color_mix_node_4, 0, color_mix_node_5, 1)
    link_nodes(halftone_part_group, color_mix_node_5, 0, filter_soften_node, 1)
    link_nodes(halftone_part_group, filter_soften_node, 0, greater_than_node, 0)
    link_nodes(halftone_part_group, greater_than_node, 0, output_node, 0)

    return halftone_part_group
