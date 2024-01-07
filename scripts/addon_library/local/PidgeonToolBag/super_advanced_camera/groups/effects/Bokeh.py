import bpy
import os
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_bokeh_group() -> NodeTree:

    # Create the group
    sac_bokeh_group: NodeTree = bpy.data.node_groups.new(name=".SAC Bokeh", type="CompositorNodeTree")

    input_node = sac_bokeh_group.nodes.new("NodeGroupInput")
    output_node = sac_bokeh_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_bokeh_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_bokeh_group, "Depth", "NodeSocketFloat", "INPUT")
    create_socket(sac_bokeh_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    normalize_node = sac_bokeh_group.nodes.new("CompositorNodeNormalize")

    add_node = sac_bokeh_group.nodes.new("CompositorNodeMath")
    add_node.operation = "ADD"
    add_node.inputs[1].default_value = 0
    add_node.name = "SAC Effects_Bokeh_Offset"

    multiply_node = sac_bokeh_group.nodes.new("CompositorNodeMath")
    multiply_node.operation = "MULTIPLY"
    multiply_node.inputs[1].default_value = 1
    multiply_node.name = "SAC Effects_Bokeh_Range"

    absolute_node = sac_bokeh_group.nodes.new("CompositorNodeMath")
    absolute_node.operation = "ABSOLUTE"

    image_node = sac_bokeh_group.nodes.new("CompositorNodeImage")
    image_node.name = "SAC Effects_Bokeh_Image"

    custom_node = sac_bokeh_group.nodes.new("CompositorNodeImage")
    custom_node.name = "SAC Effects_Bokeh_Custom_Image"

    bokeh_image_node = sac_bokeh_group.nodes.new("CompositorNodeBokehImage")
    bokeh_image_node.name = "SAC Effects_Bokeh_Procedural"

    switch_node = sac_bokeh_group.nodes.new("CompositorNodeSwitch")
    switch_node.name = "SAC Effects_Bokeh_Switch"

    switch_image_node = sac_bokeh_group.nodes.new("CompositorNodeSwitch")
    switch_image_node.name = "SAC Effects_Bokeh_ImageSwitch"

    rotate_node = sac_bokeh_group.nodes.new("CompositorNodeRotate")
    rotate_node.name = "SAC Effects_Bokeh_Rotation"

    bokeh_blur_node = sac_bokeh_group.nodes.new("CompositorNodeBokehBlur")
    bokeh_blur_node.name = "SAC Effects_Bokeh_Blur"
    bokeh_blur_node.use_variable_size = True

    # Create the links
    link_nodes(sac_bokeh_group, input_node, 1, normalize_node, 0)
    link_nodes(sac_bokeh_group, normalize_node, 0, add_node, 0)
    link_nodes(sac_bokeh_group, add_node, 0, multiply_node, 0)
    link_nodes(sac_bokeh_group, multiply_node, 0, absolute_node, 0)
    link_nodes(sac_bokeh_group, absolute_node, 0, bokeh_blur_node, 2)
    link_nodes(sac_bokeh_group, input_node, 0, bokeh_blur_node, 0)
    link_nodes(sac_bokeh_group, image_node, 0, switch_image_node, 0)
    link_nodes(sac_bokeh_group, custom_node, 0, switch_image_node, 1)
    link_nodes(sac_bokeh_group, switch_image_node, 0, rotate_node, 0)
    link_nodes(sac_bokeh_group, rotate_node, 0, switch_node, 0)
    link_nodes(sac_bokeh_group, bokeh_image_node, 0, switch_node, 1)
    link_nodes(sac_bokeh_group, switch_node, 0, bokeh_blur_node, 1)
    link_nodes(sac_bokeh_group, bokeh_blur_node, 0, output_node, 0)

    return sac_bokeh_group
