import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_hdr_group() -> NodeTree:

    # Create the group
    sac_hdr_group: NodeTree = bpy.data.node_groups.new(name=".SAC HDR", type="CompositorNodeTree")

    input_node = sac_hdr_group.nodes.new("NodeGroupInput")
    output_node = sac_hdr_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_hdr_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_hdr_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    hdrexposure_tree = hdrexposure_group()

    exposure_node = sac_hdr_group.nodes.new("CompositorNodeExposure")
    exposure_node.name = "SAC Effects_HDR_Exposure"
    exposure_node.inputs[1].default_value = -1.75

    hdr_exposure_under = sac_hdr_group.nodes.new("CompositorNodeGroup")
    hdr_exposure_under.node_tree = hdrexposure_tree
    hdr_exposure_under.name = "SAC Effects_HDR_Under"
    hdr_exposure_under.inputs["Exposure"].default_value = -2

    hdr_exposure_base = sac_hdr_group.nodes.new("CompositorNodeGroup")
    hdr_exposure_base.node_tree = hdrexposure_tree
    hdr_exposure_base.name = "SAC Effects_HDR_Base"

    hdr_exposure_over = sac_hdr_group.nodes.new("CompositorNodeGroup")
    hdr_exposure_over.node_tree = hdrexposure_tree
    hdr_exposure_over.name = "SAC Effects_HDR_Over"
    hdr_exposure_over.inputs["Exposure"].default_value = 2

    hdr_mix_node = sac_hdr_group.nodes.new("CompositorNodeMixRGB")
    hdr_mix_node.blend_type = "MIX"
    hdr_mix_node.name = "SAC Effects_HDR_Mix"

    math_multiply_node = sac_hdr_group.nodes.new("CompositorNodeMath")
    math_multiply_node.operation = "MULTIPLY"
    math_multiply_node.inputs[0].default_value = 0.1
    math_multiply_node.inputs[1].default_value = 2
    math_multiply_node.name = "SAC Effects_HDR_Sigma"

    math_power_node = sac_hdr_group.nodes.new("CompositorNodeMath")
    math_power_node.operation = "POWER"
    math_power_node.inputs[1].default_value = 2

    # Create the links
    link_nodes(sac_hdr_group, input_node, "Image", hdr_exposure_under, "Image")
    link_nodes(sac_hdr_group, input_node, "Image", hdr_exposure_base, "Image")
    link_nodes(sac_hdr_group, input_node, "Image", hdr_exposure_over, "Image")
    link_nodes(sac_hdr_group, hdr_exposure_under, "Image Add", hdr_exposure_base, "Image Val")
    link_nodes(sac_hdr_group, hdr_exposure_under, "Value Add", hdr_exposure_base, "Value Val")
    link_nodes(sac_hdr_group, hdr_exposure_base, "Image Add", hdr_exposure_over, "Image Val")
    link_nodes(sac_hdr_group, hdr_exposure_base, "Value Add", hdr_exposure_over, "Value Val")
    link_nodes(sac_hdr_group, input_node, "Image", hdr_mix_node, 1)
    link_nodes(sac_hdr_group, hdr_exposure_over, "Image Fin", exposure_node, 0)
    link_nodes(sac_hdr_group, exposure_node, 0, hdr_mix_node, 2)
    link_nodes(sac_hdr_group, math_multiply_node, 0, math_power_node, 0)
    link_nodes(sac_hdr_group, math_power_node, 0, hdr_exposure_under, "Sigma")
    link_nodes(sac_hdr_group, math_power_node, 0, hdr_exposure_base, "Sigma")
    link_nodes(sac_hdr_group, math_power_node, 0, hdr_exposure_over, "Sigma")
    link_nodes(sac_hdr_group, hdr_mix_node, 0, output_node, "Image")

    return sac_hdr_group

def hdrexposure_group() -> NodeTree:

    # Create the group
    hdr_exposure_group: NodeTree = bpy.data.node_groups.new(name=".SAC HDR Exposure", type="CompositorNodeTree")

    input_node = hdr_exposure_group.nodes.new("NodeGroupInput")
    output_node = hdr_exposure_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(hdr_exposure_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(hdr_exposure_group, "Image Val", "NodeSocketColor", "INPUT")
    create_socket(hdr_exposure_group, "Value Val", "NodeSocketFloat", "INPUT")
    create_socket(hdr_exposure_group, "Sigma", "NodeSocketFloat", "INPUT")
    create_socket(hdr_exposure_group, "Exposure", "NodeSocketFloat", "INPUT")
    create_socket(hdr_exposure_group, "Image Add", "NodeSocketColor", "OUTPUT")
    create_socket(hdr_exposure_group, "Value Add", "NodeSocketFloat", "OUTPUT")
    create_socket(hdr_exposure_group, "Image Fin", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    exposure_node = hdr_exposure_group.nodes.new("CompositorNodeExposure")

    map_range_node = hdr_exposure_group.nodes.new("CompositorNodeMapRange")
    map_range_node.inputs["From Min"].default_value = 0
    map_range_node.inputs["From Max"].default_value = 1
    map_range_node.inputs["To Min"].default_value = 0.1
    map_range_node.inputs["To Max"].default_value = 0.4

    math_subtract_node = hdr_exposure_group.nodes.new("CompositorNodeMath")
    math_subtract_node.operation = "SUBTRACT"

    math_power_node_1 = hdr_exposure_group.nodes.new("CompositorNodeMath")
    math_power_node_1.operation = "POWER"
    math_power_node_1.inputs[1].default_value = 2

    math_divide_node = hdr_exposure_group.nodes.new("CompositorNodeMath")
    math_divide_node.operation = "DIVIDE"
    math_divide_node.use_clamp = True

    math_multiply_node_1 = hdr_exposure_group.nodes.new("CompositorNodeMath")
    math_multiply_node_1.operation = "MULTIPLY"
    math_multiply_node_1.inputs[1].default_value = -1

    math_power_node_2 = hdr_exposure_group.nodes.new("CompositorNodeMath")
    math_power_node_2.operation = "POWER"
    math_power_node_2.inputs[0].default_value = 2.7182

    color_multiply_node = hdr_exposure_group.nodes.new("CompositorNodeMixRGB")
    color_multiply_node.blend_type = "MULTIPLY"

    color_add_node = hdr_exposure_group.nodes.new("CompositorNodeMixRGB")
    color_add_node.blend_type = "ADD"

    math_add_node = hdr_exposure_group.nodes.new("CompositorNodeMath")
    math_add_node.operation = "ADD"

    color_didivide_node = hdr_exposure_group.nodes.new("CompositorNodeMixRGB")
    color_didivide_node.blend_type = "DIVIDE"

    # Create the links
    link_nodes(hdr_exposure_group, input_node, "Image", map_range_node, 0)
    link_nodes(hdr_exposure_group, input_node, "Image", exposure_node, 0)
    link_nodes(hdr_exposure_group, input_node, "Exposure", exposure_node, 1)
    link_nodes(hdr_exposure_group, input_node, "Image Val", color_add_node, 2)
    link_nodes(hdr_exposure_group, input_node, "Value Val", math_add_node, 2)
    link_nodes(hdr_exposure_group, input_node, "Sigma", math_divide_node, 1)
    link_nodes(hdr_exposure_group, exposure_node, 0, math_subtract_node, 0)
    link_nodes(hdr_exposure_group, map_range_node, 0, math_subtract_node, 1)
    link_nodes(hdr_exposure_group, exposure_node, 0, color_multiply_node, 2)
    link_nodes(hdr_exposure_group, math_subtract_node, 0, math_power_node_1, 0)
    link_nodes(hdr_exposure_group, math_power_node_1, 0, math_divide_node, 0)
    link_nodes(hdr_exposure_group, math_divide_node, 0, math_multiply_node_1, 0)
    link_nodes(hdr_exposure_group, math_multiply_node_1, 0, math_power_node_2, 1)
    link_nodes(hdr_exposure_group, math_power_node_2, 0, color_multiply_node, 1)
    link_nodes(hdr_exposure_group, math_power_node_2, 0, math_add_node, 0)
    link_nodes(hdr_exposure_group, math_add_node, 0, output_node, "Value Add")
    link_nodes(hdr_exposure_group, color_multiply_node, 0, color_add_node, 1)
    link_nodes(hdr_exposure_group, color_add_node, 0, output_node, "Image Add")
    link_nodes(hdr_exposure_group, color_add_node, 0, color_didivide_node, 1)
    link_nodes(hdr_exposure_group, math_add_node, 0, color_didivide_node, 2)
    link_nodes(hdr_exposure_group, color_didivide_node, 0, output_node, "Image Fin")

    return hdr_exposure_group
