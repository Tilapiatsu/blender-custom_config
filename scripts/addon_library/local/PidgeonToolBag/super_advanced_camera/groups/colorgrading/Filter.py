import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket
from ...SAC_Functions import get_filter


def create_max_group() -> NodeTree:

    # Create the group
    sac_max_group: NodeTree = bpy.data.node_groups.new(name=".SAC Three Max", type="CompositorNodeTree")

    input_node = sac_max_group.nodes.new("NodeGroupInput")
    output_node = sac_max_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_max_group, "A", "NodeSocketFloat", "INPUT")
    create_socket(sac_max_group, "B", "NodeSocketFloat", "INPUT")
    create_socket(sac_max_group, "C", "NodeSocketFloat", "INPUT")
    create_socket(sac_max_group, "Value", "NodeSocketFloat", "OUTPUT")

    # Create the nodes
    math_max_1 = sac_max_group.nodes.new("CompositorNodeMath")
    math_max_1.operation = "MAXIMUM"

    math_max_2 = sac_max_group.nodes.new("CompositorNodeMath")
    math_max_2.operation = "MAXIMUM"

    # Create the links
    link_nodes(sac_max_group, input_node, 0, math_max_1, 0)
    link_nodes(sac_max_group, input_node, 1, math_max_1, 1)
    link_nodes(sac_max_group, math_max_1, 0, math_max_2, 0)
    link_nodes(sac_max_group, input_node, 2, math_max_2, 1)
    link_nodes(sac_max_group, math_max_2, 0, output_node, 0)

    return sac_max_group


def create_combine_group() -> NodeTree:

    if ".SAC Three Max" not in bpy.data.node_groups:
        sac_max = create_max_group()
    else:
        sac_max = bpy.data.node_groups[".SAC Three Max"]

    # Create the group
    sac_combine_group: NodeTree = bpy.data.node_groups.new(name=".SAC Combine", type="CompositorNodeTree")

    input_node = sac_combine_group.nodes.new("NodeGroupInput")
    output_node = sac_combine_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_combine_group, "R", "NodeSocketColor", "INPUT")
    create_socket(sac_combine_group, "G", "NodeSocketColor", "INPUT")
    create_socket(sac_combine_group, "B", "NodeSocketColor", "INPUT")
    create_socket(sac_combine_group, "A", "NodeSocketFloat", "INPUT")
    create_socket(sac_combine_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    separate_rgb_1 = sac_combine_group.nodes.new("CompositorNodeSeparateColor")
    separate_rgb_2 = sac_combine_group.nodes.new("CompositorNodeSeparateColor")
    separate_rgb_3 = sac_combine_group.nodes.new("CompositorNodeSeparateColor")

    max_group_1 = sac_combine_group.nodes.new("CompositorNodeGroup")
    max_group_1.node_tree = sac_max
    max_group_2 = sac_combine_group.nodes.new("CompositorNodeGroup")
    max_group_2.node_tree = sac_max
    max_group_3 = sac_combine_group.nodes.new("CompositorNodeGroup")
    max_group_3.node_tree = sac_max

    combine_rgb = sac_combine_group.nodes.new("CompositorNodeCombineColor")

    # Create the links
    link_nodes(sac_combine_group, input_node, 0, separate_rgb_1, 0)
    link_nodes(sac_combine_group, input_node, 1, separate_rgb_2, 0)
    link_nodes(sac_combine_group, input_node, 2, separate_rgb_3, 0)
    link_nodes(sac_combine_group, separate_rgb_1, 0, max_group_1, "A")
    link_nodes(sac_combine_group, separate_rgb_2, 0, max_group_1, "B")
    link_nodes(sac_combine_group, separate_rgb_3, 0, max_group_1, "C")
    link_nodes(sac_combine_group, separate_rgb_1, 1, max_group_2, "A")
    link_nodes(sac_combine_group, separate_rgb_2, 1, max_group_2, "B")
    link_nodes(sac_combine_group, separate_rgb_3, 1, max_group_2, "C")
    link_nodes(sac_combine_group, separate_rgb_1, 2, max_group_3, "A")
    link_nodes(sac_combine_group, separate_rgb_2, 2, max_group_3, "B")
    link_nodes(sac_combine_group, separate_rgb_3, 2, max_group_3, "C")
    link_nodes(sac_combine_group, max_group_1, 0, combine_rgb, 0)
    link_nodes(sac_combine_group, max_group_2, 0, combine_rgb, 1)
    link_nodes(sac_combine_group, max_group_3, 0, combine_rgb, 2)
    link_nodes(sac_combine_group, input_node, 3, combine_rgb, 3)
    link_nodes(sac_combine_group, combine_rgb, 0, output_node, 0)

    return sac_combine_group


def create_filter_group() -> NodeTree:

    # Create the groups once
    if ".SAC Combine" not in bpy.data.node_groups:
        sac_combine = create_combine_group()
    else:
        sac_combine = bpy.data.node_groups[".SAC Combine"]

    # Create the group
    sac_filter_group: NodeTree = bpy.data.node_groups.new(name=".SAC Filter", type="CompositorNodeTree")

    input_node = sac_filter_group.nodes.new("NodeGroupInput")
    output_node = sac_filter_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_filter_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_filter_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    separate_rgb = sac_filter_group.nodes.new("CompositorNodeSeparateColor")

    red_channel = sac_filter_group.nodes.new("CompositorNodeCurveRGB")
    red_channel.name = "SAC Colorgrade_Filter_Red"
    red_channel.mapping.extend = "HORIZONTAL"
    green_channel = sac_filter_group.nodes.new("CompositorNodeCurveRGB")
    green_channel.name = "SAC Colorgrade_Filter_Green"
    green_channel.mapping.extend = "HORIZONTAL"
    blue_channel = sac_filter_group.nodes.new("CompositorNodeCurveRGB")
    blue_channel.name = "SAC Colorgrade_Filter_Blue"
    blue_channel.mapping.extend = "HORIZONTAL"

    filter_channels = get_filter("Default")
    channels = [red_channel, green_channel, blue_channel]

    for channel, filter_channel in enumerate(filter_channels):
        channel_node = channels[channel]
        for curve, filter_curve in enumerate(filter_channel):
            channel_mapping = channel_node.mapping.curves[curve]
            for point, filter_point in enumerate(reversed(filter_curve)):
                if (point == len(filter_curve)-1) or (point == 0):
                    continue
                channel_mapping.points.new(point/(len(filter_curve)-1), filter_point)
        channel_node.mapping.update()

    combine_group = sac_filter_group.nodes.new("CompositorNodeGroup")
    combine_group.node_tree = sac_combine

    mix_node = sac_filter_group.nodes.new("CompositorNodeMixRGB")
    mix_node.blend_type = "MIX"
    mix_node.inputs[0].default_value = 0.5
    mix_node.name = "SAC Colorgrade_Filter_Mix"

    # Create the links
    link_nodes(sac_filter_group, input_node, 0, separate_rgb, 0)
    link_nodes(sac_filter_group, separate_rgb, 0, red_channel, 1)
    link_nodes(sac_filter_group, separate_rgb, 1, green_channel, 1)
    link_nodes(sac_filter_group, separate_rgb, 2, blue_channel, 1)
    link_nodes(sac_filter_group, red_channel, 0, combine_group, "R")
    link_nodes(sac_filter_group, green_channel, 0, combine_group, "G")
    link_nodes(sac_filter_group, blue_channel, 0, combine_group, "B")
    link_nodes(sac_filter_group, separate_rgb, 3, combine_group, "A")
    link_nodes(sac_filter_group, combine_group, 0, mix_node, 2)
    link_nodes(sac_filter_group, input_node, 0, mix_node, 1)
    link_nodes(sac_filter_group, mix_node, 0, output_node, 0)

    return sac_filter_group
