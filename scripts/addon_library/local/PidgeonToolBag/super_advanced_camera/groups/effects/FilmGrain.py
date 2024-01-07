import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_filmgrain_group() -> NodeTree:

    # Create the group
    sac_filmgrain_group: NodeTree = bpy.data.node_groups.new(name=".SAC FilmGrain", type="CompositorNodeTree")

    input_node = sac_filmgrain_group.nodes.new("NodeGroupInput")
    output_node = sac_filmgrain_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_filmgrain_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_filmgrain_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    add_node = sac_filmgrain_group.nodes.new("CompositorNodeMath")
    add_node.operation = "ADD"
    add_node.use_clamp = True
    add_node.inputs[1].default_value = 1

    lens_distortion_node = sac_filmgrain_group.nodes.new("CompositorNodeLensdist")
    lens_distortion_node.use_jitter = True
    lens_distortion_node.inputs[1].default_value = 0.00001

    rgb_to_bw_node = sac_filmgrain_group.nodes.new("CompositorNodeRGBToBW")

    math_subtract_node = sac_filmgrain_group.nodes.new("CompositorNodeMath")
    math_subtract_node.operation = "SUBTRACT"
    math_subtract_node.use_clamp = True
    math_subtract_node.inputs[0].default_value = 1

    bilateral_blur_node = sac_filmgrain_group.nodes.new("CompositorNodeBilateralblur")
    bilateral_blur_node.iterations = 5
    bilateral_blur_node.sigma_color = 0.4
    bilateral_blur_node.sigma_space = 1
    bilateral_blur_node.name = "SAC Effects_FilmGrain_Blur"

    color_screen_node = sac_filmgrain_group.nodes.new("CompositorNodeMixRGB")
    color_screen_node.blend_type = "SCREEN"
    color_screen_node.name = "SAC Effects_FilmGrain_Strength"
    color_screen_node.inputs[0].default_value = 0

    # Create the links
    link_nodes(sac_filmgrain_group, input_node, 0, add_node, 0)
    link_nodes(sac_filmgrain_group, add_node, 0, lens_distortion_node, 0)
    link_nodes(sac_filmgrain_group, lens_distortion_node, 0, rgb_to_bw_node, 0)
    link_nodes(sac_filmgrain_group, rgb_to_bw_node, 0, math_subtract_node, 1)
    link_nodes(sac_filmgrain_group, math_subtract_node, 0, bilateral_blur_node, 0)
    link_nodes(sac_filmgrain_group, math_subtract_node, 0, bilateral_blur_node, 1)
    link_nodes(sac_filmgrain_group, bilateral_blur_node, 0, color_screen_node, 2)
    link_nodes(sac_filmgrain_group, input_node, 0, color_screen_node, 1)
    link_nodes(sac_filmgrain_group, color_screen_node, 0, output_node, 0)

    # return
    return sac_filmgrain_group
