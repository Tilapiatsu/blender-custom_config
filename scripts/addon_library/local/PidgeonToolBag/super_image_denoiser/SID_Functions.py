import bpy
import os
from math import ceil
from bpy.types import Node, NodeTree
from ..pidgeon_tool_bag.PTB_Functions import bcolors, link_nodes, create_socket
from ..presets.FFmpeg import *

# region Node Tools

def create_panel(tree: NodeTree, panel_name: str):
    return (tree.interface.new_panel(name=panel_name, default_closed=True))
# endregion Node Tools

# region SID Node Groups


def create_denoiser_skip_group() -> NodeTree:

    # check if a node tree with the name ".SID Skip Denoiser" already exists
    denoiser_skip_tree = bpy.data.node_groups.get(".SID Skip Denoiser")
    if not denoiser_skip_tree is None:
        return denoiser_skip_tree

    # create the group
    denoiser_skip_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID Skip Denoiser")
    input_node = denoiser_skip_tree.nodes.new("NodeGroupInput")
    output_node = denoiser_skip_tree.nodes.new("NodeGroupOutput")

    # create the inputs and outputs
    create_socket(denoiser_skip_tree, "Direct", "NodeSocketColor", "INPUT")
    create_socket(denoiser_skip_tree, "Indirect", "NodeSocketColor", "INPUT")
    create_socket(denoiser_skip_tree, "Color", "NodeSocketColor", "INPUT")
    create_socket(denoiser_skip_tree, "Denoising Normal", "NodeSocketVector", "INPUT")
    create_socket(denoiser_skip_tree, "Denoising Albedo", "NodeSocketColor", "INPUT")
    create_socket(denoiser_skip_tree, "Image", "NodeSocketColor", "OUTPUT")
    create_socket(denoiser_skip_tree, "Direct", "NodeSocketColor", "OUTPUT")
    create_socket(denoiser_skip_tree, "Indirect", "NodeSocketColor", "OUTPUT")

    denoiser_skip_tree.interface.items_tree["Color"].default_value = (1, 1, 1, 1)

    # create the nodes
    add_color_node = denoiser_skip_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node.blend_type = "ADD"
    multiply_color_node = denoiser_skip_tree.nodes.new("CompositorNodeMixRGB")
    multiply_color_node.blend_type = "MULTIPLY"

    # link the nodes
    link_nodes(denoiser_skip_tree, input_node, "Direct", add_color_node, 1)
    link_nodes(denoiser_skip_tree, input_node, "Indirect", add_color_node, 2)
    link_nodes(denoiser_skip_tree, add_color_node, 0, multiply_color_node, 1)
    link_nodes(denoiser_skip_tree, input_node, "Color", multiply_color_node, 2)
    link_nodes(denoiser_skip_tree, multiply_color_node, 0, output_node, "Image")
    link_nodes(denoiser_skip_tree, input_node, "Direct", output_node, "Direct")
    link_nodes(denoiser_skip_tree, input_node, "Indirect", output_node, "Indirect")

    return denoiser_skip_tree


def create_denoiser_super_group() -> NodeTree:

    # check if a node tree with the name ".SID Super Denoiser" already exists
    denoiser_super_tree = bpy.data.node_groups.get(".SID Super Denoiser")
    if not denoiser_super_tree is None:
        return denoiser_super_tree

    # create the group
    denoiser_super_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID Super Denoiser")
    input_node = denoiser_super_tree.nodes.new("NodeGroupInput")
    output_node = denoiser_super_tree.nodes.new("NodeGroupOutput")

    # create the inputs and outputs
    create_socket(denoiser_super_tree, "Direct", "NodeSocketColor", "INPUT")
    create_socket(denoiser_super_tree, "Indirect", "NodeSocketColor", "INPUT")
    create_socket(denoiser_super_tree, "Color", "NodeSocketColor", "INPUT")
    create_socket(denoiser_super_tree, "Denoising Normal", "NodeSocketVector", "INPUT")
    create_socket(denoiser_super_tree, "Denoising Albedo", "NodeSocketColor", "INPUT")
    create_socket(denoiser_super_tree, "Image", "NodeSocketColor", "OUTPUT")
    create_socket(denoiser_super_tree, "Direct", "NodeSocketColor", "OUTPUT")
    create_socket(denoiser_super_tree, "Indirect", "NodeSocketColor", "OUTPUT")

    denoiser_super_tree.interface.items_tree["Color"].default_value = (1, 1, 1, 1)

    # create the nodes
    denoise_node_direct = denoiser_super_tree.nodes.new("CompositorNodeDenoise")
    denoise_node_direct.prefilter = "ACCURATE"
    denoise_node_direct.use_hdr = True

    denoise_node_indirect = denoiser_super_tree.nodes.new("CompositorNodeDenoise")
    denoise_node_indirect.prefilter = "ACCURATE"
    denoise_node_indirect.use_hdr = True

    add_color_node = denoiser_super_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node.blend_type = "ADD"

    multiply_color_node = denoiser_super_tree.nodes.new("CompositorNodeMixRGB")
    multiply_color_node.blend_type = "MULTIPLY"

    # link the nodes
    link_nodes(denoiser_super_tree, input_node, "Direct", denoise_node_direct, 0)
    link_nodes(denoiser_super_tree, input_node, "Denoising Normal", denoise_node_direct, 1)
    link_nodes(denoiser_super_tree, input_node, "Denoising Albedo", denoise_node_direct, 2)
    link_nodes(denoiser_super_tree, input_node, "Indirect", denoise_node_indirect, 0)
    link_nodes(denoiser_super_tree, input_node, "Denoising Normal", denoise_node_indirect, 1)
    link_nodes(denoiser_super_tree, input_node, "Denoising Albedo", denoise_node_indirect, 2)
    link_nodes(denoiser_super_tree, denoise_node_direct, 0, add_color_node, 1)
    link_nodes(denoiser_super_tree, denoise_node_indirect, 0, add_color_node, 2)
    link_nodes(denoiser_super_tree, add_color_node, 0, multiply_color_node, 1)
    link_nodes(denoiser_super_tree, input_node, "Color", multiply_color_node, 2)
    link_nodes(denoiser_super_tree, multiply_color_node, 0, output_node, "Image")
    link_nodes(denoiser_super_tree, denoise_node_direct, 0, output_node, "Direct")
    link_nodes(denoiser_super_tree, denoise_node_indirect, 0, output_node, "Indirect")

    return denoiser_super_tree


def create_super_group() -> NodeTree:
    settings = bpy.context.scene.sid_settings

    # check if a node tree with the name ".SID Super" already exists
    super_tree = bpy.data.node_groups.get(".SID Super")
    if not super_tree is None:
        return super_tree

    denoiser_super_tree = create_denoiser_super_group()
    skip_denoiser_tree = create_denoiser_skip_group()

    # create the group
    super_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID Super")
    input_node = super_tree.nodes.new("NodeGroupInput")
    output_node = super_tree.nodes.new("NodeGroupOutput")

    # create the inputs and outputs
    diffuse_panel = create_panel(super_tree, "Diffuse")
    create_socket(super_tree, "DiffDir", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(super_tree, "DiffInd", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(super_tree, "DiffCol", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(super_tree, "DiffDir", "NodeSocketColor", "OUTPUT", diffuse_panel)
    create_socket(super_tree, "DiffInd", "NodeSocketColor", "OUTPUT", diffuse_panel)

    glossy_panel = create_panel(super_tree, "Glossy")
    create_socket(super_tree, "GlossDir", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(super_tree, "GlossInd", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(super_tree, "GlossCol", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(super_tree, "GlossDir", "NodeSocketColor", "OUTPUT", glossy_panel)
    create_socket(super_tree, "GlossInd", "NodeSocketColor", "OUTPUT", glossy_panel)

    transmission_panel = create_panel(super_tree, "Transmission")
    create_socket(super_tree, "TransDir", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(super_tree, "TransInd", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(super_tree, "TransCol", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(super_tree, "TransDir", "NodeSocketColor", "OUTPUT", transmission_panel)
    create_socket(super_tree, "TransInd", "NodeSocketColor", "OUTPUT", transmission_panel)

    volume_panel = create_panel(super_tree, "Volume")
    create_socket(super_tree, "VolumeDir", "NodeSocketColor", "INPUT", volume_panel)
    create_socket(super_tree, "VolumeInd", "NodeSocketColor", "INPUT", volume_panel)
    create_socket(super_tree, "VolumeDir", "NodeSocketColor", "OUTPUT", volume_panel)
    create_socket(super_tree, "VolumeInd", "NodeSocketColor", "OUTPUT", volume_panel)

    emission_panel = create_panel(super_tree, "Emit")
    create_socket(super_tree, "Emit", "NodeSocketColor", "INPUT", emission_panel)
    create_socket(super_tree, "Emit", "NodeSocketColor", "OUTPUT", emission_panel)

    environment_panel = create_panel(super_tree, "Env")
    create_socket(super_tree, "Env", "NodeSocketColor", "INPUT", environment_panel)
    create_socket(super_tree, "Env", "NodeSocketColor", "OUTPUT", environment_panel)

    create_socket(super_tree, "Denoising Normal", "NodeSocketVector", "INPUT")
    create_socket(super_tree, "Denoising Albedo", "NodeSocketColor", "INPUT")
    create_socket(super_tree, "Image", "NodeSocketColor", "OUTPUT")

    # create the nodes
    diffuse_node_group = super_tree.nodes.new("CompositorNodeGroup")
    diffuse_node_group.node_tree = denoiser_super_tree if settings.diffuse else skip_denoiser_tree
    diffuse_node_group.name = "Diffuse Denoiser"

    glossy_node_group = super_tree.nodes.new("CompositorNodeGroup")
    glossy_node_group.node_tree = denoiser_super_tree if settings.glossy else skip_denoiser_tree
    glossy_node_group.name = "Glossy Denoiser"

    transmission_node_group = super_tree.nodes.new("CompositorNodeGroup")
    transmission_node_group.node_tree = denoiser_super_tree if settings.transmission else skip_denoiser_tree
    transmission_node_group.name = "Transmission Denoiser"

    volume_node_group = super_tree.nodes.new("CompositorNodeGroup")
    volume_node_group.node_tree = denoiser_super_tree if settings.volume else skip_denoiser_tree
    volume_node_group.name = "Volume Denoiser"

    emission_denoiser_node = super_tree.nodes.new("CompositorNodeDenoise")
    emission_denoiser_node.prefilter = "ACCURATE"
    emission_denoiser_node.use_hdr = True
    emission_denoiser_node.name = "Emission Denoiser"
    emission_denoiser_node.mute = not settings.emission

    environment_denoiser_node = super_tree.nodes.new("CompositorNodeDenoise")
    environment_denoiser_node.prefilter = "ACCURATE"
    environment_denoiser_node.use_hdr = True
    environment_denoiser_node.name = "Environment Denoiser"
    environment_denoiser_node.mute = not settings.environment

    add_color_node_1 = super_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_1.blend_type = "ADD"
    add_color_node_2 = super_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_2.blend_type = "ADD"
    add_color_node_3 = super_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_3.blend_type = "ADD"
    add_color_node_4 = super_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_4.blend_type = "ADD"
    add_color_node_5 = super_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_5.blend_type = "ADD"

    # link the nodes
    link_nodes(super_tree, input_node, "DiffDir", diffuse_node_group, "Direct")
    link_nodes(super_tree, input_node, "DiffInd", diffuse_node_group, "Indirect")
    link_nodes(super_tree, input_node, "DiffCol", diffuse_node_group, "Color")
    link_nodes(super_tree, input_node, "Denoising Normal", diffuse_node_group, "Denoising Normal")
    link_nodes(super_tree, input_node, "Denoising Albedo", diffuse_node_group, "Denoising Albedo")
    link_nodes(super_tree, input_node, "GlossDir", glossy_node_group, "Direct")
    link_nodes(super_tree, input_node, "GlossInd", glossy_node_group, "Indirect")
    link_nodes(super_tree, input_node, "GlossCol", glossy_node_group, "Color")
    link_nodes(super_tree, input_node, "Denoising Normal", glossy_node_group, "Denoising Normal")
    link_nodes(super_tree, input_node, "Denoising Albedo", glossy_node_group, "Denoising Albedo")
    link_nodes(super_tree, input_node, "TransDir", transmission_node_group, "Direct")
    link_nodes(super_tree, input_node, "TransInd", transmission_node_group, "Indirect")
    link_nodes(super_tree, input_node, "TransCol", transmission_node_group, "Color")
    link_nodes(super_tree, input_node, "Denoising Normal", transmission_node_group, "Denoising Normal")
    link_nodes(super_tree, input_node, "Denoising Albedo", transmission_node_group, "Denoising Albedo")
    link_nodes(super_tree, input_node, "VolumeDir", volume_node_group, "Direct")
    link_nodes(super_tree, input_node, "VolumeInd", volume_node_group, "Indirect")
    link_nodes(super_tree, input_node, "Denoising Normal", volume_node_group, "Denoising Normal")
    link_nodes(super_tree, input_node, "Denoising Albedo", volume_node_group, "Denoising Albedo")
    link_nodes(super_tree, input_node, "Emit", emission_denoiser_node, 0)
    link_nodes(super_tree, input_node, "Denoising Normal", emission_denoiser_node, 1)
    link_nodes(super_tree, input_node, "Denoising Albedo", emission_denoiser_node, 2)
    link_nodes(super_tree, input_node, "Env", environment_denoiser_node, 0)
    link_nodes(super_tree, input_node, "Denoising Normal", environment_denoiser_node, 1)
    link_nodes(super_tree, input_node, "Denoising Albedo", environment_denoiser_node, 2)
    link_nodes(super_tree, diffuse_node_group, "Image", add_color_node_1, 1)
    link_nodes(super_tree, glossy_node_group, "Image", add_color_node_1, 2)
    link_nodes(super_tree, add_color_node_1, 0, add_color_node_2, 1)
    link_nodes(super_tree, transmission_node_group, "Image", add_color_node_2, 2)
    link_nodes(super_tree, add_color_node_2, 0, add_color_node_3, 1)
    link_nodes(super_tree, volume_node_group, "Image", add_color_node_3, 2)
    link_nodes(super_tree, add_color_node_3, 0, add_color_node_4, 1)
    link_nodes(super_tree, emission_denoiser_node, 0, add_color_node_4, 2)
    link_nodes(super_tree, add_color_node_4, 0, add_color_node_5, 1)
    link_nodes(super_tree, environment_denoiser_node, 0, add_color_node_5, 2)
    link_nodes(super_tree, add_color_node_5, 0, output_node, "Image")
    link_nodes(super_tree, diffuse_node_group, "Direct", output_node, "DiffDir")
    link_nodes(super_tree, diffuse_node_group, "Indirect", output_node, "DiffInd")
    link_nodes(super_tree, glossy_node_group, "Direct", output_node, "GlossDir")
    link_nodes(super_tree, glossy_node_group, "Indirect", output_node, "GlossInd")
    link_nodes(super_tree, transmission_node_group, "Direct", output_node, "TransDir")
    link_nodes(super_tree, transmission_node_group, "Indirect", output_node, "TransInd")
    link_nodes(super_tree, volume_node_group, "Direct", output_node, "VolumeDir")
    link_nodes(super_tree, volume_node_group, "Indirect", output_node, "VolumeInd")
    link_nodes(super_tree, emission_denoiser_node, 0, output_node, "Emit")
    link_nodes(super_tree, environment_denoiser_node, 0, output_node, "Env")

    return super_tree


def create_denoiser_high_group() -> NodeTree:

    # check if a node tree with the name ".SID High Denoiser" already exists
    denoiser_high_tree = bpy.data.node_groups.get(".SID High Denoiser")
    if not denoiser_high_tree is None:
        return denoiser_high_tree

    # create the group
    denoiser_high_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID High Denoiser")
    input_node = denoiser_high_tree.nodes.new("NodeGroupInput")
    output_node = denoiser_high_tree.nodes.new("NodeGroupOutput")

    # create the inputs and outputs
    create_socket(denoiser_high_tree, "Direct", "NodeSocketColor", "INPUT")
    create_socket(denoiser_high_tree, "Indirect", "NodeSocketColor", "INPUT")
    create_socket(denoiser_high_tree, "Color", "NodeSocketColor", "INPUT")
    create_socket(denoiser_high_tree, "Denoising Normal", "NodeSocketVector", "INPUT")
    create_socket(denoiser_high_tree, "Denoising Albedo", "NodeSocketColor", "INPUT")
    create_socket(denoiser_high_tree, "Image", "NodeSocketColor", "OUTPUT")

    denoiser_high_tree.interface.items_tree["Color"].default_value = (1, 1, 1, 1)

    # create the nodes
    add_color_node = denoiser_high_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node.blend_type = "ADD"

    multiply_color_node = denoiser_high_tree.nodes.new("CompositorNodeMixRGB")
    multiply_color_node.blend_type = "MULTIPLY"

    denoise_node = denoiser_high_tree.nodes.new("CompositorNodeDenoise")
    denoise_node.prefilter = "FAST"
    denoise_node.use_hdr = True

    # link the nodes
    link_nodes(denoiser_high_tree, input_node, "Direct", add_color_node, 1)
    link_nodes(denoiser_high_tree, input_node, "Indirect", add_color_node, 2)
    link_nodes(denoiser_high_tree, add_color_node, 0, multiply_color_node, 1)
    link_nodes(denoiser_high_tree, input_node, "Color", multiply_color_node, 2)
    link_nodes(denoiser_high_tree, multiply_color_node, 0, denoise_node, 0)
    link_nodes(denoiser_high_tree, input_node, "Denoising Normal", denoise_node, 1)
    link_nodes(denoiser_high_tree, input_node, "Denoising Albedo", denoise_node, 2)
    link_nodes(denoiser_high_tree, denoise_node, 0, output_node, "Image")

    return denoiser_high_tree


def create_high_group() -> NodeTree:
    settings = bpy.context.scene.sid_settings

    # check if a node tree with the name ".SID High" already exists
    high_tree = bpy.data.node_groups.get(".SID High")
    if not high_tree is None:
        return high_tree

    denoiser_high_tree = create_denoiser_high_group()
    skip_denoiser_tree = create_denoiser_skip_group()

    # create the group
    high_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID High")
    input_node = high_tree.nodes.new("NodeGroupInput")
    output_node = high_tree.nodes.new("NodeGroupOutput")

    # create the inputs and outputs
    diffuse_panel = create_panel(high_tree, "Diffuse")
    create_socket(high_tree, "DiffDir", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(high_tree, "DiffInd", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(high_tree, "DiffCol", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(high_tree, "Diffuse", "NodeSocketColor", "OUTPUT", diffuse_panel)

    glossy_panel = create_panel(high_tree, "Glossy")
    create_socket(high_tree, "GlossDir", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(high_tree, "GlossInd", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(high_tree, "GlossCol", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(high_tree, "Glossy", "NodeSocketColor", "OUTPUT", glossy_panel)

    transmission_panel = create_panel(high_tree, "Transmission")
    create_socket(high_tree, "TransDir", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(high_tree, "TransInd", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(high_tree, "TransCol", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(high_tree, "Transmission", "NodeSocketColor", "OUTPUT", transmission_panel)

    volume_panel = create_panel(high_tree, "Volume")
    create_socket(high_tree, "VolumeDir", "NodeSocketColor", "INPUT", volume_panel)
    create_socket(high_tree, "VolumeInd", "NodeSocketColor", "INPUT", volume_panel)
    create_socket(high_tree, "Volume", "NodeSocketColor", "OUTPUT", volume_panel)

    emission_panel = create_panel(high_tree, "Emit")
    create_socket(high_tree, "Emit", "NodeSocketColor", "INPUT", emission_panel)
    create_socket(high_tree, "Emit", "NodeSocketColor", "OUTPUT", emission_panel)

    environment_panel = create_panel(high_tree, "Env")
    create_socket(high_tree, "Env", "NodeSocketColor", "INPUT", environment_panel)
    create_socket(high_tree, "Env", "NodeSocketColor", "OUTPUT", environment_panel)

    create_socket(high_tree, "Denoising Normal", "NodeSocketVector", "INPUT")
    create_socket(high_tree, "Denoising Albedo", "NodeSocketColor", "INPUT")
    create_socket(high_tree, "Image", "NodeSocketColor", "OUTPUT")

    # create the nodes
    diffuse_denoiser_node = high_tree.nodes.new("CompositorNodeGroup")
    diffuse_denoiser_node.node_tree = denoiser_high_tree if settings.diffuse else skip_denoiser_tree
    diffuse_denoiser_node.name = "Diffuse Denoiser"

    glossy_denoiser_node = high_tree.nodes.new("CompositorNodeGroup")
    glossy_denoiser_node.node_tree = denoiser_high_tree if settings.glossy else skip_denoiser_tree
    glossy_denoiser_node.name = "Glossy Denoiser"

    transmission_denoiser_node = high_tree.nodes.new("CompositorNodeGroup")
    transmission_denoiser_node.node_tree = denoiser_high_tree if settings.transmission else skip_denoiser_tree
    transmission_denoiser_node.name = "Transmission Denoiser"

    volume_denoiser_node = high_tree.nodes.new("CompositorNodeGroup")
    volume_denoiser_node.node_tree = denoiser_high_tree if settings.volume else skip_denoiser_tree
    volume_denoiser_node.name = "Volume Denoiser"

    emission_denoiser_node = high_tree.nodes.new("CompositorNodeDenoise")
    emission_denoiser_node.prefilter = "FAST"
    emission_denoiser_node.use_hdr = True
    emission_denoiser_node.name = "Emission Denoiser"

    environment_denoiser_node = high_tree.nodes.new("CompositorNodeDenoise")
    environment_denoiser_node.prefilter = "FAST"
    environment_denoiser_node.use_hdr = True
    environment_denoiser_node.name = "Environment Denoiser"

    add_color_node_1 = high_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_1.blend_type = "ADD"
    add_color_node_2 = high_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_2.blend_type = "ADD"
    add_color_node_3 = high_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_3.blend_type = "ADD"
    add_color_node_4 = high_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_4.blend_type = "ADD"
    add_color_node_5 = high_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_5.blend_type = "ADD"

    # link the nodes
    link_nodes(high_tree, input_node, "DiffDir", diffuse_denoiser_node, "Direct")
    link_nodes(high_tree, input_node, "DiffInd", diffuse_denoiser_node, "Indirect")
    link_nodes(high_tree, input_node, "DiffCol", diffuse_denoiser_node, "Color")
    link_nodes(high_tree, input_node, "Denoising Normal", diffuse_denoiser_node, "Denoising Normal")
    link_nodes(high_tree, input_node, "Denoising Albedo", diffuse_denoiser_node, "Denoising Albedo")
    link_nodes(high_tree, input_node, "GlossDir", glossy_denoiser_node, "Direct")
    link_nodes(high_tree, input_node, "GlossInd", glossy_denoiser_node, "Indirect")
    link_nodes(high_tree, input_node, "GlossCol", glossy_denoiser_node, "Color")
    link_nodes(high_tree, input_node, "Denoising Normal", glossy_denoiser_node, "Denoising Normal")
    link_nodes(high_tree, input_node, "Denoising Albedo", glossy_denoiser_node, "Denoising Albedo")
    link_nodes(high_tree, input_node, "TransDir", transmission_denoiser_node, "Direct")
    link_nodes(high_tree, input_node, "TransInd", transmission_denoiser_node, "Indirect")
    link_nodes(high_tree, input_node, "TransCol", transmission_denoiser_node, "Color")
    link_nodes(high_tree, input_node, "Denoising Normal", transmission_denoiser_node, "Denoising Normal")
    link_nodes(high_tree, input_node, "Denoising Albedo", transmission_denoiser_node, "Denoising Albedo")
    link_nodes(high_tree, input_node, "VolumeDir", volume_denoiser_node, "Direct")
    link_nodes(high_tree, input_node, "VolumeInd", volume_denoiser_node, "Indirect")
    link_nodes(high_tree, input_node, "Denoising Normal", volume_denoiser_node, "Denoising Normal")
    link_nodes(high_tree, input_node, "Denoising Albedo", volume_denoiser_node, "Denoising Albedo")
    link_nodes(high_tree, input_node, "Emit", emission_denoiser_node, 0)
    link_nodes(high_tree, input_node, "Denoising Normal", emission_denoiser_node, 1)
    link_nodes(high_tree, input_node, "Denoising Albedo", emission_denoiser_node, 2)
    link_nodes(high_tree, input_node, "Env", environment_denoiser_node, 0)
    link_nodes(high_tree, input_node, "Denoising Normal", environment_denoiser_node, 1)
    link_nodes(high_tree, input_node, "Denoising Albedo", environment_denoiser_node, 2)
    link_nodes(high_tree, diffuse_denoiser_node, "Image", add_color_node_1, 1)
    link_nodes(high_tree, glossy_denoiser_node, "Image", add_color_node_1, 2)
    link_nodes(high_tree, add_color_node_1, 0, add_color_node_2, 1)
    link_nodes(high_tree, transmission_denoiser_node, "Image", add_color_node_2, 2)
    link_nodes(high_tree, add_color_node_2, 0, add_color_node_3, 1)
    link_nodes(high_tree, volume_denoiser_node, "Image", add_color_node_3, 2)
    link_nodes(high_tree, add_color_node_3, 0, add_color_node_4, 1)
    link_nodes(high_tree, emission_denoiser_node, 0, add_color_node_4, 2)
    link_nodes(high_tree, add_color_node_4, 0, add_color_node_5, 1)
    link_nodes(high_tree, environment_denoiser_node, 0, add_color_node_5, 2)
    link_nodes(high_tree, add_color_node_5, 0, output_node, "Image")
    link_nodes(high_tree, diffuse_denoiser_node, "Image", output_node, "Diffuse")
    link_nodes(high_tree, glossy_denoiser_node, "Image", output_node, "Glossy")
    link_nodes(high_tree, transmission_denoiser_node, "Image", output_node, "Transmission")
    link_nodes(high_tree, volume_denoiser_node, "Image", output_node, "Volume")
    link_nodes(high_tree, emission_denoiser_node, 0, output_node, "Emit")
    link_nodes(high_tree, environment_denoiser_node, 0, output_node, "Env")

    return high_tree


def create_standard_group() -> NodeTree:

    # check if a node tree with the name ".SID Standard" already exists
    standard_tree = bpy.data.node_groups.get(".SID Standard")
    if not standard_tree is None:
        return standard_tree

    # create the group
    standard_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID Standard")
    input_node = standard_tree.nodes.new("NodeGroupInput")
    output_node = standard_tree.nodes.new("NodeGroupOutput")

    # create the inputs and outputs
    create_socket(standard_tree, "Image", "NodeSocketColor", "INPUT")
    create_socket(standard_tree, "Denoising Normal", "NodeSocketVector", "INPUT")
    create_socket(standard_tree, "Denoising Albedo", "NodeSocketColor", "INPUT")
    create_socket(standard_tree, "Image", "NodeSocketColor", "OUTPUT")

    # create the nodes
    denoise_node = standard_tree.nodes.new("CompositorNodeDenoise")
    denoise_node.prefilter = "FAST"
    denoise_node.use_hdr = True

    # link the nodes
    link_nodes(standard_tree, input_node, "Image", denoise_node, 0)
    link_nodes(standard_tree, input_node, "Denoising Normal", denoise_node, 1)
    link_nodes(standard_tree, input_node, "Denoising Albedo", denoise_node, 2)
    link_nodes(standard_tree, denoise_node, 0, output_node, "Image")

    return standard_tree


def create_temporal_albedo_node() -> NodeTree:

    # Check if a node tree with the name ".SID Temporal Albedo" already exists
    temporal_albedo_tree = bpy.data.node_groups.get(".SID Temporal Albedo")
    if not temporal_albedo_tree is None:
        return temporal_albedo_tree

    # Create the group
    temporal_albedo_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID Temporal Albedo")
    input_node = temporal_albedo_tree.nodes.new("NodeGroupInput")
    output_node = temporal_albedo_tree.nodes.new("NodeGroupOutput")

    # Create the inputs and outputs
    create_socket(temporal_albedo_tree, "DiffCol", "NodeSocketColor", "INPUT")
    create_socket(temporal_albedo_tree, "GlossCol", "NodeSocketColor", "INPUT")
    create_socket(temporal_albedo_tree, "TransCol", "NodeSocketColor", "INPUT")
    create_socket(temporal_albedo_tree, "Emit", "NodeSocketColor", "INPUT")
    create_socket(temporal_albedo_tree, "Env", "NodeSocketColor", "INPUT")
    create_socket(temporal_albedo_tree, "Temporal Albedo", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    add_color_node_1 = temporal_albedo_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_1.blend_type = "ADD"
    add_color_node_2 = temporal_albedo_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_2.blend_type = "ADD"
    add_color_node_3 = temporal_albedo_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_3.blend_type = "ADD"
    add_color_node_4 = temporal_albedo_tree.nodes.new("CompositorNodeMixRGB")
    add_color_node_4.blend_type = "ADD"

    # Link the nodes
    link_nodes(temporal_albedo_tree, input_node, "DiffCol", add_color_node_1, 1)
    link_nodes(temporal_albedo_tree, input_node, "GlossCol", add_color_node_1, 2)
    link_nodes(temporal_albedo_tree, add_color_node_1, 0, add_color_node_2, 1)
    link_nodes(temporal_albedo_tree, input_node, "TransCol", add_color_node_2, 2)
    link_nodes(temporal_albedo_tree, add_color_node_2, 0, add_color_node_3, 1)
    link_nodes(temporal_albedo_tree, input_node, "Emit", add_color_node_3, 2)
    link_nodes(temporal_albedo_tree, add_color_node_3, 0, add_color_node_4, 1)
    link_nodes(temporal_albedo_tree, input_node, "Env", add_color_node_4, 2)
    link_nodes(temporal_albedo_tree, add_color_node_4, 0, output_node, "Temporal Albedo")

    return temporal_albedo_tree


def create_super_image_denoiser_group() -> NodeTree:

    # check if a node tree with the name ".SID Super Image Denoiser" already exists
    super_image_denoiser_tree = bpy.data.node_groups.get(".Super Image Denoiser")
    if not super_image_denoiser_tree is None:
        return super_image_denoiser_tree

    # create the group
    super_image_denoiser_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Super Image Denoiser")
    input_node = super_image_denoiser_tree.nodes.new("NodeGroupInput")
    output_node = super_image_denoiser_tree.nodes.new("NodeGroupOutput")

    # create the inputs and outputs
    denoiser_types = create_panel(super_image_denoiser_tree, "Denoiser Types")
    create_socket(super_image_denoiser_tree, "Super", "NodeSocketColor", "OUTPUT", denoiser_types)
    create_socket(super_image_denoiser_tree, "High", "NodeSocketColor", "OUTPUT", denoiser_types)
    create_socket(super_image_denoiser_tree, "Standard", "NodeSocketColor", "OUTPUT", denoiser_types)

    diffuse_panel = create_panel(super_image_denoiser_tree, "Diffuse")
    create_socket(super_image_denoiser_tree, "DiffDir", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(super_image_denoiser_tree, "DiffInd", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(super_image_denoiser_tree, "DiffCol", "NodeSocketColor", "INPUT", diffuse_panel)
    create_socket(super_image_denoiser_tree, "DiffDir", "NodeSocketColor", "OUTPUT", diffuse_panel)
    create_socket(super_image_denoiser_tree, "DiffInd", "NodeSocketColor", "OUTPUT", diffuse_panel)
    create_socket(super_image_denoiser_tree, "DiffCol", "NodeSocketColor", "OUTPUT", diffuse_panel)
    create_socket(super_image_denoiser_tree, "Diffuse", "NodeSocketColor", "OUTPUT", diffuse_panel)

    glossy_panel = create_panel(super_image_denoiser_tree, "Glossy")
    create_socket(super_image_denoiser_tree, "GlossDir", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(super_image_denoiser_tree, "GlossInd", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(super_image_denoiser_tree, "GlossCol", "NodeSocketColor", "INPUT", glossy_panel)
    create_socket(super_image_denoiser_tree, "GlossDir", "NodeSocketColor", "OUTPUT", glossy_panel)
    create_socket(super_image_denoiser_tree, "GlossInd", "NodeSocketColor", "OUTPUT", glossy_panel)
    create_socket(super_image_denoiser_tree, "GlossCol", "NodeSocketColor", "OUTPUT", glossy_panel)
    create_socket(super_image_denoiser_tree, "Glossy", "NodeSocketColor", "OUTPUT", glossy_panel)

    transmission_panel = create_panel(super_image_denoiser_tree, "Transmission")
    create_socket(super_image_denoiser_tree, "TransDir", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(super_image_denoiser_tree, "TransInd", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(super_image_denoiser_tree, "TransCol", "NodeSocketColor", "INPUT", transmission_panel)
    create_socket(super_image_denoiser_tree, "TransDir", "NodeSocketColor", "OUTPUT", transmission_panel)
    create_socket(super_image_denoiser_tree, "TransInd", "NodeSocketColor", "OUTPUT", transmission_panel)
    create_socket(super_image_denoiser_tree, "TransCol", "NodeSocketColor", "OUTPUT", transmission_panel)
    create_socket(super_image_denoiser_tree, "Transmission", "NodeSocketColor", "OUTPUT", transmission_panel)

    volume_panel = create_panel(super_image_denoiser_tree, "Volume")
    create_socket(super_image_denoiser_tree, "VolumeDir", "NodeSocketColor", "INPUT", volume_panel)
    create_socket(super_image_denoiser_tree, "VolumeInd", "NodeSocketColor", "INPUT", volume_panel)
    create_socket(super_image_denoiser_tree, "VolumeDir", "NodeSocketColor", "OUTPUT", volume_panel)
    create_socket(super_image_denoiser_tree, "VolumeInd", "NodeSocketColor", "OUTPUT", volume_panel)
    create_socket(super_image_denoiser_tree, "Volume", "NodeSocketColor", "OUTPUT", volume_panel)

    emission_panel = create_panel(super_image_denoiser_tree, "Emit")
    create_socket(super_image_denoiser_tree, "Emit", "NodeSocketColor", "INPUT", emission_panel)
    create_socket(super_image_denoiser_tree, "Emit", "NodeSocketColor", "OUTPUT", emission_panel)

    environment_panel = create_panel(super_image_denoiser_tree, "Env")
    create_socket(super_image_denoiser_tree, "Env", "NodeSocketColor", "INPUT", environment_panel)
    create_socket(super_image_denoiser_tree, "Env", "NodeSocketColor", "OUTPUT", environment_panel)

    technical_panel = create_panel(super_image_denoiser_tree, "Technical")
    create_socket(super_image_denoiser_tree, "Image", "NodeSocketColor", "INPUT")
    create_socket(super_image_denoiser_tree, "Alpha", "NodeSocketFloat", "INPUT", technical_panel)
    create_socket(super_image_denoiser_tree, "Denoising Normal", "NodeSocketVector", "INPUT", technical_panel)
    create_socket(super_image_denoiser_tree, "Denoising Albedo", "NodeSocketColor", "INPUT", technical_panel)
    create_socket(super_image_denoiser_tree, "Temporal Albedo", "NodeSocketColor", "OUTPUT", technical_panel)

    # create the nodes
    super_image_denoiser_node = super_image_denoiser_tree.nodes.new("CompositorNodeGroup")
    super_image_denoiser_node.node_tree = create_super_group()
    high_image_denoiser_node = super_image_denoiser_tree.nodes.new("CompositorNodeGroup")
    high_image_denoiser_node.node_tree = create_high_group()
    standard_denoiser_node = super_image_denoiser_tree.nodes.new("CompositorNodeGroup")
    standard_denoiser_node.node_tree = create_standard_group()
    temporal_albedo_node = super_image_denoiser_tree.nodes.new("CompositorNodeGroup")
    temporal_albedo_node.node_tree = create_temporal_albedo_node()
    set_alpha_node_super = super_image_denoiser_tree.nodes.new("CompositorNodeSetAlpha")
    set_alpha_node_super.mode = "REPLACE_ALPHA"
    set_alpha_node_high = super_image_denoiser_tree.nodes.new("CompositorNodeSetAlpha")
    set_alpha_node_high.mode = "REPLACE_ALPHA"

    # link the nodes
    link_nodes(super_image_denoiser_tree, input_node, "Alpha", set_alpha_node_super, "Alpha")
    link_nodes(super_image_denoiser_tree, input_node, "Alpha", set_alpha_node_high, "Alpha")

    link_nodes(super_image_denoiser_tree, input_node, "DiffDir", super_image_denoiser_node, "DiffDir")
    link_nodes(super_image_denoiser_tree, input_node, "DiffInd", super_image_denoiser_node, "DiffInd")
    link_nodes(super_image_denoiser_tree, input_node, "DiffCol", super_image_denoiser_node, "DiffCol")
    link_nodes(super_image_denoiser_tree, input_node, "GlossDir", super_image_denoiser_node, "GlossDir")
    link_nodes(super_image_denoiser_tree, input_node, "GlossInd", super_image_denoiser_node, "GlossInd")
    link_nodes(super_image_denoiser_tree, input_node, "GlossCol", super_image_denoiser_node, "GlossCol")
    link_nodes(super_image_denoiser_tree, input_node, "TransDir", super_image_denoiser_node, "TransDir")
    link_nodes(super_image_denoiser_tree, input_node, "TransInd", super_image_denoiser_node, "TransInd")
    link_nodes(super_image_denoiser_tree, input_node, "TransCol", super_image_denoiser_node, "TransCol")
    link_nodes(super_image_denoiser_tree, input_node, "VolumeDir", super_image_denoiser_node, "VolumeDir")
    link_nodes(super_image_denoiser_tree, input_node, "VolumeInd", super_image_denoiser_node, "VolumeInd")
    link_nodes(super_image_denoiser_tree, input_node, "Emit", super_image_denoiser_node, "Emit")
    link_nodes(super_image_denoiser_tree, input_node, "Env", super_image_denoiser_node, "Env")
    link_nodes(super_image_denoiser_tree, input_node, "Denoising Normal", super_image_denoiser_node, "Denoising Normal")
    link_nodes(super_image_denoiser_tree, input_node, "Denoising Albedo", super_image_denoiser_node, "Denoising Albedo")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "Image", set_alpha_node_super, 0)

    link_nodes(super_image_denoiser_tree, input_node, "DiffDir", high_image_denoiser_node, "DiffDir")
    link_nodes(super_image_denoiser_tree, input_node, "DiffInd", high_image_denoiser_node, "DiffInd")
    link_nodes(super_image_denoiser_tree, input_node, "DiffCol", high_image_denoiser_node, "DiffCol")
    link_nodes(super_image_denoiser_tree, input_node, "GlossDir", high_image_denoiser_node, "GlossDir")
    link_nodes(super_image_denoiser_tree, input_node, "GlossInd", high_image_denoiser_node, "GlossInd")
    link_nodes(super_image_denoiser_tree, input_node, "GlossCol", high_image_denoiser_node, "GlossCol")
    link_nodes(super_image_denoiser_tree, input_node, "TransDir", high_image_denoiser_node, "TransDir")
    link_nodes(super_image_denoiser_tree, input_node, "TransInd", high_image_denoiser_node, "TransInd")
    link_nodes(super_image_denoiser_tree, input_node, "TransCol", high_image_denoiser_node, "TransCol")
    link_nodes(super_image_denoiser_tree, input_node, "VolumeDir", high_image_denoiser_node, "VolumeDir")
    link_nodes(super_image_denoiser_tree, input_node, "VolumeInd", high_image_denoiser_node, "VolumeInd")
    link_nodes(super_image_denoiser_tree, input_node, "Emit", high_image_denoiser_node, "Emit")
    link_nodes(super_image_denoiser_tree, input_node, "Env", high_image_denoiser_node, "Env")
    link_nodes(super_image_denoiser_tree, input_node, "Denoising Normal", high_image_denoiser_node, "Denoising Normal")
    link_nodes(super_image_denoiser_tree, input_node, "Denoising Albedo", high_image_denoiser_node, "Denoising Albedo")
    link_nodes(super_image_denoiser_tree, high_image_denoiser_node, "Image", set_alpha_node_high, 0)

    link_nodes(super_image_denoiser_tree, input_node, "Image", standard_denoiser_node, "Image")
    link_nodes(super_image_denoiser_tree, input_node, "Denoising Normal", standard_denoiser_node, "Denoising Normal")
    link_nodes(super_image_denoiser_tree, input_node, "Denoising Albedo", standard_denoiser_node, "Denoising Albedo")

    link_nodes(super_image_denoiser_tree, set_alpha_node_super, "Image", output_node, "Super")
    link_nodes(super_image_denoiser_tree, set_alpha_node_high, "Image", output_node, "High")
    link_nodes(super_image_denoiser_tree, standard_denoiser_node, "Image", output_node, "Standard")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "DiffDir", output_node, "DiffDir")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "DiffInd", output_node, "DiffInd")
    link_nodes(super_image_denoiser_tree, input_node, "DiffCol", output_node, "DiffCol")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "GlossDir", output_node, "GlossDir")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "GlossInd", output_node, "GlossInd")
    link_nodes(super_image_denoiser_tree, input_node, "GlossCol", output_node, "GlossCol")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "TransDir", output_node, "TransDir")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "TransInd", output_node, "TransInd")
    link_nodes(super_image_denoiser_tree, input_node, "TransCol", output_node, "TransCol")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "VolumeDir", output_node, "VolumeDir")
    link_nodes(super_image_denoiser_tree, super_image_denoiser_node, "VolumeInd", output_node, "VolumeInd")
    link_nodes(super_image_denoiser_tree, high_image_denoiser_node, "Diffuse", output_node, "Diffuse")
    link_nodes(super_image_denoiser_tree, high_image_denoiser_node, "Glossy", output_node, "Glossy")
    link_nodes(super_image_denoiser_tree, high_image_denoiser_node, "Transmission", output_node, "Transmission")
    link_nodes(super_image_denoiser_tree, high_image_denoiser_node, "Volume", output_node, "Volume")
    link_nodes(super_image_denoiser_tree, high_image_denoiser_node, "Emit", output_node, "Emit")
    link_nodes(super_image_denoiser_tree, high_image_denoiser_node, "Env", output_node, "Env")

    link_nodes(super_image_denoiser_tree, input_node, "DiffCol", temporal_albedo_node, "DiffCol")
    link_nodes(super_image_denoiser_tree, input_node, "GlossCol", temporal_albedo_node, "GlossCol")
    link_nodes(super_image_denoiser_tree, input_node, "TransCol", temporal_albedo_node, "TransCol")
    link_nodes(super_image_denoiser_tree, input_node, "Emit", temporal_albedo_node, "Emit")
    link_nodes(super_image_denoiser_tree, input_node, "Env", temporal_albedo_node, "Env")
    link_nodes(super_image_denoiser_tree, temporal_albedo_node, "Temporal Albedo", output_node, "Temporal Albedo")

    return super_image_denoiser_tree


def enable_passes():
    for layer in bpy.context.scene.view_layers:
        layer.use_pass_combined = True
        layer.cycles.denoising_store_passes = True
        layer.use_pass_diffuse_direct = True
        layer.use_pass_diffuse_indirect = True
        layer.use_pass_diffuse_color = True
        layer.use_pass_glossy_direct = True
        layer.use_pass_glossy_indirect = True
        layer.use_pass_glossy_color = True
        layer.use_pass_transmission_direct = True
        layer.use_pass_transmission_indirect = True
        layer.use_pass_transmission_color = True
        layer.cycles.use_pass_volume_direct = True
        layer.cycles.use_pass_volume_indirect = True
        layer.use_pass_emit = True
        layer.use_pass_environment = True
        layer.use_pass_vector = False if bpy.context.scene.sid_settings.denoiser_type == "SID" else True


def connect_render_layers_to_sid():
    settings = bpy.context.scene.sid_settings
    # Get the main node tree
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    # Define a list of passes
    passes = [
        "Image", "Alpha", "DiffDir", "DiffInd", "DiffCol",
        "GlossDir", "GlossInd", "GlossCol", "TransDir",
        "TransInd", "TransCol", "VolumeDir", "VolumeInd",
        "Emit", "Env", "Denoising Normal", "Denoising Albedo"
    ]

    skip_passes = ["Alpha"]

    index = 0

    # For every R_LAYERS node in the node tree
    for render_layer_node in [node for node in tree.nodes if node.type == 'R_LAYERS']:

        # Enable passes for this view layer
        bpy.context.scene.view_layers[render_layer_node.layer].use = True
        enable_passes()

        # Check if this render_layer_node already has a SID node connected
        sid_already_connected = any(
            link.to_node.type == 'GROUP' and link.to_node.node_tree.name.startswith(".Super Image Denoiser")
            for link in tree.links if link.from_node == render_layer_node
        )

        if sid_already_connected:
            continue

        # Create a new SID node group for this render_layer_node
        sid_node = tree.nodes.new("CompositorNodeGroup")
        sid_node.location = render_layer_node.location[0] + 300, render_layer_node.location[1]
        sid_node.node_tree = create_super_image_denoiser_group()

        # Check if both nodes are present
        if render_layer_node and sid_node:
            # Connect passes
            for pass_name in passes:
                if (pass_name in render_layer_node.outputs) and (pass_name in sid_node.inputs):
                    # Find the connections from the render layer node for this pass
                    for link in tree.links:
                        if (link.from_node == render_layer_node) and (link.from_socket.name == pass_name):
                            # If the pass is "Image", remove the existing link and create a new link to the SID node
                            if pass_name == "Image":
                                link_nodes(tree, sid_node, settings.quality, link.to_node, link.to_socket.name)
                            elif pass_name in skip_passes:
                                pass
                            else:
                                link_nodes(tree, sid_node, pass_name, link.to_node, link.to_socket)

                    # Connect every pass from the render layer node to the SID node
                    link_nodes(tree, render_layer_node, pass_name, sid_node, pass_name)


def cleanup_temporal_output_node():
    for node in bpy.context.scene.node_tree.nodes:
        if node.type == "OUTPUT_FILE" and node.name.startswith("SID Temporal Output"):
            bpy.context.scene.node_tree.nodes.remove(node)


def create_temporal_output_node():
    settings = bpy.context.scene.sid_settings
    cleanup_temporal_output_node()

    index = 0
    bpy.context.scene.render.use_motion_blur = False
    bpy.context.scene.view_layers[0].use_pass_vector = True

    for node in bpy.context.scene.node_tree.nodes:
        if node.type == "GROUP" and node.node_tree.name.startswith(".Super Image Denoiser"):

            output_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeOutputFile")
            output_node.name = "SID Temporal Output"
            output_node.format.file_format = "OPEN_EXR_MULTILAYER"
            output_node.format.exr_codec = "PIZ"
            output_node.format.color_depth = "16" if settings.smaller_exr_files else "32"
            output_node.base_path = os.path.join(settings.working_directory, "processing", str(index), settings.custom_name + "######")
            output_node.location = node.location[0] + 300, node.location[1] - 300

            # get the render layer node that SID is connected to
            render_layer_node = None
            for link in bpy.context.scene.node_tree.links:
                if link.to_node == node and link.from_node.type == "R_LAYERS":
                    render_layer_node = link.from_node

            # link the node
            link_nodes(bpy.context.scene.node_tree, node, settings.quality, output_node, 0)
            output_node.file_slots.new("Vector")
            link_nodes(bpy.context.scene.node_tree, render_layer_node, "Vector", output_node, "Vector")
            output_node.file_slots.new("Depth")
            link_nodes(bpy.context.scene.node_tree, render_layer_node, "Denoising Depth", output_node, "Depth")
            output_node.file_slots.new("Temporal Albedo")
            link_nodes(bpy.context.scene.node_tree, node, "Temporal Albedo", output_node, "Temporal Albedo")

            index += 1


# endregion SID Node Groups

# region SID Settings


def update_diffuse(self, context):
    try:
        super_node_group = bpy.data.node_groups.get(".SID Super").nodes.get("Diffuse Denoiser")
        high_node_group = bpy.data.node_groups.get(".SID High").nodes.get("Diffuse Denoiser")
    except:
        return

    if self.diffuse:
        super_node_group.node_tree = create_denoiser_super_group()
        high_node_group.node_tree = create_denoiser_high_group()
    else:
        super_node_group.node_tree = create_denoiser_skip_group()
        high_node_group.node_tree = create_denoiser_skip_group()


def update_glossy(self, context):
    try:
        super_node_group = bpy.data.node_groups.get(".SID Super").nodes.get("Glossy Denoiser")
        high_node_group = bpy.data.node_groups.get(".SID High").nodes.get("Glossy Denoiser")
    except:
        return

    if self.glossy:
        super_node_group.node_tree = create_denoiser_super_group()
        high_node_group.node_tree = create_denoiser_high_group()
    else:
        super_node_group.node_tree = create_denoiser_skip_group()
        high_node_group.node_tree = create_denoiser_skip_group()


def update_transmission(self, context):
    try:
        super_node_group = bpy.data.node_groups.get(".SID Super").nodes.get("Transmission Denoiser")
        high_node_group = bpy.data.node_groups.get(".SID High").nodes.get("Transmission Denoiser")
    except:
        return

    if self.transmission:
        super_node_group.node_tree = create_denoiser_super_group()
        high_node_group.node_tree = create_denoiser_high_group()
    else:
        super_node_group.node_tree = create_denoiser_skip_group()
        high_node_group.node_tree = create_denoiser_skip_group()


def update_volume(self, context):
    try:
        super_node_group = bpy.data.node_groups.get(".SID Super").nodes.get("Volume Denoiser")
        high_node_group = bpy.data.node_groups.get(".SID High").nodes.get("Volume Denoiser")
    except:
        return

    if self.volume:
        super_node_group.node_tree = create_denoiser_super_group()
        high_node_group.node_tree = create_denoiser_high_group()
    else:
        super_node_group.node_tree = create_denoiser_skip_group()
        high_node_group.node_tree = create_denoiser_skip_group()


def update_emission(self, context):
    try:
        bpy.data.node_groups.get(".SID Super").nodes.get("Emission Denoiser").mute = not self.emission
        bpy.data.node_groups.get(".SID High").nodes.get("Emission Denoiser").mute = not self.emission
    except:
        return


def update_environment(self, context):
    try:
        bpy.data.node_groups.get(".SID Super").nodes.get("Environment Denoiser").mute = not self.environment
        bpy.data.node_groups.get(".SID High").nodes.get("Environment Denoiser").mute = not self.environment
    except:
        return


def update_multilayer_exr(self, context):
    compositor = bpy.context.scene.node_tree
    if self.multilayer_exr:
        for node in compositor.nodes:
            if node.type == "OUTPUT_FILE" and node.label.startswith("SID Output"):
                # remove the node
                compositor.nodes.remove(node)

        index = 0
        for node in compositor.nodes:
            if node.type == "GROUP" and node.node_tree.name == ".Super Image Denoiser":
                output_node = compositor.nodes.new("CompositorNodeOutputFile")
                output_node.name = "SID Output"
                output_node.format.file_format = "OPEN_EXR_MULTILAYER"
                output_node.base_path = self.multilayer_exr_path + str(index) + "/"
                link_nodes(compositor, node, self.quality, output_node, 0)
                if self.quality == "Super":
                    # add new slot
                    output_node.file_slots.new("DiffDir")
                    link_nodes(compositor, node, "DiffDir", output_node, "DiffDir")
                    output_node.file_slots.new("DiffInd")
                    link_nodes(compositor, node, "DiffInd", output_node, "DiffInd")
                    output_node.file_slots.new("DiffCol")
                    link_nodes(compositor, node, "DiffCol", output_node, "DiffCol")
                    output_node.file_slots.new("GlossDir")
                    link_nodes(compositor, node, "GlossDir", output_node, "GlossDir")
                    output_node.file_slots.new("GlossInd")
                    link_nodes(compositor, node, "GlossInd", output_node, "GlossInd")
                    output_node.file_slots.new("GlossCol")
                    link_nodes(compositor, node, "GlossCol", output_node, "GlossCol")
                    output_node.file_slots.new("TransDir")
                    link_nodes(compositor, node, "TransDir", output_node, "TransDir")
                    output_node.file_slots.new("TransInd")
                    link_nodes(compositor, node, "TransInd", output_node, "TransInd")
                    output_node.file_slots.new("TransCol")
                    link_nodes(compositor, node, "TransCol", output_node, "TransCol")
                    output_node.file_slots.new("VolumeDir")
                    link_nodes(compositor, node, "VolumeDir", output_node, "VolumeDir")
                    output_node.file_slots.new("VolumeInd")
                    link_nodes(compositor, node, "VolumeInd", output_node, "VolumeInd")
                    output_node.file_slots.new("Emit")
                    link_nodes(compositor, node, "Emit", output_node, "Emit")
                    output_node.file_slots.new("Env")
                    link_nodes(compositor, node, "Env", output_node, "Env")
                elif self.quality == "High":
                    output_node.file_slots.new("Diffuse")
                    link_nodes(compositor, node, "Diffuse", output_node, "Diffuse")
                    output_node.file_slots.new("Glossy")
                    link_nodes(compositor, node, "Glossy", output_node, "Glossy")
                    output_node.file_slots.new("Transmission")
                    link_nodes(compositor, node, "Transmission", output_node, "Transmission")
                    output_node.file_slots.new("Volume")
                    link_nodes(compositor, node, "Volume", output_node, "Volume")
                    output_node.file_slots.new("Emit")
                    link_nodes(compositor, node, "Emit", output_node, "Emit")
                    output_node.file_slots.new("Env")
                    link_nodes(compositor, node, "Env", output_node, "Env")

                output_node.location = node.location[0] + 300, node.location[1]

                index += 1

    else:
        for node in compositor.nodes:
            if node.type == "OUTPUT_FILE" and node.name.startswith("SID Output"):
                # remove the node
                compositor.nodes.remove(node)

# endregion SID Settings

# region Other Tools

def create_temporal_median(minimum: bool) -> NodeTree:

    if minimum:
        min_max = "MINIMUM"
        median_name = ".SID Temporal MedianMin"
    else:
        min_max = "MAXIMUM"
        median_name = ".SID Temporal MedianMax"

    # check if a node tree with the name ".SID Temporal MedianMin" already exists
    if bpy.data.node_groups.get(median_name):
        return bpy.data.node_groups.get(median_name)
    
    # create the group
    temporal_median_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=median_name)
    input_node = temporal_median_tree.nodes.new("NodeGroupInput")
    output_node = temporal_median_tree.nodes.new("NodeGroupOutput")

    # create the sockets
    create_socket(temporal_median_tree, "a", "NodeSocketColor", "INPUT")
    create_socket(temporal_median_tree, "b", "NodeSocketColor", "INPUT")
    create_socket(temporal_median_tree, "median image", "NodeSocketColor", "OUTPUT")

    # create the nodes
    separate_color_0 = temporal_median_tree.nodes.new("CompositorNodeSeparateColor")
    separate_color_1 = temporal_median_tree.nodes.new("CompositorNodeSeparateColor")
    median_r = temporal_median_tree.nodes.new("CompositorNodeMath")
    median_r.operation = min_max
    median_g = temporal_median_tree.nodes.new("CompositorNodeMath")
    median_g.operation = min_max
    median_b = temporal_median_tree.nodes.new("CompositorNodeMath")
    median_b.operation = min_max
    median_a = temporal_median_tree.nodes.new("CompositorNodeMath")
    median_a.operation = min_max

    combine_color = temporal_median_tree.nodes.new("CompositorNodeCombineColor")

    # link the nodes
    link_nodes(temporal_median_tree, input_node, "a", separate_color_0, 0)
    link_nodes(temporal_median_tree, input_node, "b", separate_color_1, 0)

    link_nodes(temporal_median_tree, separate_color_0, 0, median_r, 0)
    link_nodes(temporal_median_tree, separate_color_0, 1, median_g, 0)
    link_nodes(temporal_median_tree, separate_color_0, 2, median_b, 0)
    link_nodes(temporal_median_tree, separate_color_0, 3, median_a, 0)

    link_nodes(temporal_median_tree, separate_color_1, 0, median_r, 1)
    link_nodes(temporal_median_tree, separate_color_1, 1, median_g, 1)
    link_nodes(temporal_median_tree, separate_color_1, 2, median_b, 1)
    link_nodes(temporal_median_tree, separate_color_1, 3, median_a, 1)

    link_nodes(temporal_median_tree, median_r, 0, combine_color, 0)
    link_nodes(temporal_median_tree, median_g, 0, combine_color, 1)
    link_nodes(temporal_median_tree, median_b, 0, combine_color, 2)
    link_nodes(temporal_median_tree, median_a, 0, combine_color, 3)

    link_nodes(temporal_median_tree, combine_color, 0, output_node, "median image")

    return temporal_median_tree

def create_temporal_crop() -> NodeTree:

    # Check if a node tree with the name ".SID Temporal Crop" already exists
    if bpy.data.node_groups.get(".SID Temporal Crop"):
        return bpy.data.node_groups.get(".SID Temporal Crop")

    render = bpy.context.scene.render
    settings = bpy.context.scene.sid_settings

    # create the tree
    crop_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID Temporal Crop")

    # create the sockets
    create_socket(crop_tree, "Image", "NodeSocketColor", "INPUT")
    create_socket(crop_tree, "Image", "NodeSocketColor", "OUTPUT")

    # create the nodes
    input_node = crop_tree.nodes.new("NodeGroupInput")
    output_node = crop_tree.nodes.new("NodeGroupOutput")

    overscan_percentage = ceil(render.resolution_percentage * (100 + settings.overscan) / 100)
    crop_aspect = (1 - (render.resolution_x * render.resolution_percentage / 100) / (render.resolution_x * overscan_percentage / 100)) / 2

    crop_node = crop_tree.nodes.new(type="CompositorNodeCrop")
    crop_node.use_crop_size = True
    crop_node.relative = True
    crop_node.rel_min_x = crop_aspect
    crop_node.rel_max_x = 1 - crop_aspect
    crop_node.rel_min_y = crop_node.rel_min_x
    crop_node.rel_max_y = crop_node.rel_max_x

    scale_node = crop_tree.nodes.new(type="CompositorNodeScale")
    scale_node.space = "ABSOLUTE"
    scale_node.inputs[1].default_value = render.resolution_x * render.resolution_percentage / 100
    scale_node.inputs[2].default_value = render.resolution_y * render.resolution_percentage / 100
    
    link_nodes(crop_tree, input_node, 0, crop_node, 0)
    link_nodes(crop_tree, crop_node, 0, scale_node, 0)
    link_nodes(crop_tree, scale_node, 0, output_node, 0)

    return crop_tree

def create_temporal_align() -> NodeTree:
    settings = bpy.context.scene.sid_settings

    # check if a node tree with the name ".SID Align" already exists
    if bpy.data.node_groups.get(".SID Temporal Align"):
        return bpy.data.node_groups.get(".SID Temporal Align")

    # create the group
    temporal_align_tree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".SID Temporal Align")
    input_node = temporal_align_tree.nodes.new("NodeGroupInput")
    output_node = temporal_align_tree.nodes.new("NodeGroupOutput")

    # create the sockets
    frame_0_panel = create_panel(temporal_align_tree, "0")
    create_socket(temporal_align_tree, "Frame + 0", "NodeSocketColor", "INPUT", frame_0_panel)
    create_socket(temporal_align_tree, "Albedo + 0", "NodeSocketColor", "INPUT", frame_0_panel)
    create_socket(temporal_align_tree, "Vector + 0", "NodeSocketColor", "INPUT", frame_0_panel)

    frame_1_panel = create_panel(temporal_align_tree, "1")
    create_socket(temporal_align_tree, "Frame + 1", "NodeSocketColor", "INPUT", frame_1_panel)
    create_socket(temporal_align_tree, "Albedo + 1", "NodeSocketColor", "INPUT", frame_1_panel)
    create_socket(temporal_align_tree, "Vector + 1", "NodeSocketColor", "INPUT", frame_1_panel)
    create_socket(temporal_align_tree, "Depth + 1", "NodeSocketColor", "INPUT", frame_1_panel)

    frame_2_panel = create_panel(temporal_align_tree, "2")
    create_socket(temporal_align_tree, "Frame + 2", "NodeSocketColor", "INPUT", frame_2_panel)
    create_socket(temporal_align_tree, "Albedo + 2", "NodeSocketColor", "INPUT", frame_2_panel)
    create_socket(temporal_align_tree, "Vector + 2", "NodeSocketColor", "INPUT", frame_2_panel)

    create_socket(temporal_align_tree, "Temporal Aligned", "NodeSocketColor", "OUTPUT")

    # create the nodes
    displace_frame_0 = temporal_align_tree.nodes.new("CompositorNodeDisplace")
    displace_frame_0.inputs["X Scale"].default_value = -1
    displace_frame_0.inputs["Y Scale"].default_value = -1
    
    displace_frame_0_ta = temporal_align_tree.nodes.new(type="CompositorNodeDisplace")
    displace_frame_0_ta.inputs["X Scale"].default_value = -1
    displace_frame_0_ta.inputs["Y Scale"].default_value = -1

    displace_frame_2 = temporal_align_tree.nodes.new(type="CompositorNodeDisplace")
    displace_frame_2.inputs["X Scale"].default_value = 1
    displace_frame_2.inputs["Y Scale"].default_value = 1

    displace_frame_2_ta = temporal_align_tree.nodes.new(type="CompositorNodeDisplace")
    displace_frame_2_ta.inputs["X Scale"].default_value = 1
    displace_frame_2_ta.inputs["Y Scale"].default_value = 1

    median_max_0 = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    median_max_0.node_tree = create_temporal_median(False)
    median_max_0_ta = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    median_max_0_ta.node_tree = create_temporal_median(False)

    median_min_0 = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    median_min_0.node_tree = create_temporal_median(True)
    median_min_0_ta = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    median_min_0_ta.node_tree = create_temporal_median(True)

    median_max_1 = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    median_max_1.node_tree = create_temporal_median(False)
    median_max_1_ta = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    median_max_1_ta.node_tree = create_temporal_median(False)

    median_min_1 = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    median_min_1.node_tree = create_temporal_median(True)
    median_min_1_ta = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    median_min_1_ta.node_tree = create_temporal_median(True)

    alpha_over = temporal_align_tree.nodes.new(type="CompositorNodeAlphaOver")
    alpha_over_ta = temporal_align_tree.nodes.new(type="CompositorNodeAlphaOver")

    ta_difference = temporal_align_tree.nodes.new(type="CompositorNodeMixRGB")
    ta_difference.blend_type = "DIFFERENCE"
    ta_difference.use_clamp = True

    ta_multiply = temporal_align_tree.nodes.new(type="CompositorNodeMath")
    ta_multiply.operation = "MULTIPLY"
    ta_multiply.use_clamp = True
    ta_multiply.inputs[1].default_value = settings.ted_threshold

    ta_dialate = temporal_align_tree.nodes.new(type="CompositorNodeDilateErode")
    ta_dialate.mode = "FEATHER"
    ta_dialate.distance = settings.ted_radius
    ta_dialate.falloff = "SPHERE"

    ta_mix = temporal_align_tree.nodes.new(type="CompositorNodeMixRGB")
    ta_mix.blend_type = "MIX"

    vector_blur = temporal_align_tree.nodes.new(type="CompositorNodeVecBlur")
    vector_blur.mute = not settings.motion_blur
    vector_blur.samples = settings.motion_blur_samples
    vector_blur.factor = settings.motion_blur_shutter_speed
    vector_blur.speed_min = settings.motion_blur_min_speed
    vector_blur.speed_max = settings.motion_blur_max_speed
    vector_blur.use_curved = settings.motion_blur_curved_interpolation

    crop_node = temporal_align_tree.nodes.new(type="CompositorNodeGroup")
    crop_node.node_tree = create_temporal_crop()
    
    # link the nodes
    link_nodes(temporal_align_tree, input_node, "Frame + 0", displace_frame_0, 0)
    link_nodes(temporal_align_tree, input_node, "Vector + 0", displace_frame_0, 1)
    link_nodes(temporal_align_tree, input_node, "Albedo + 0", displace_frame_0_ta, 0)
    link_nodes(temporal_align_tree, input_node, "Vector + 0", displace_frame_0_ta, 1)

    link_nodes(temporal_align_tree, input_node, "Frame + 2", displace_frame_2, 0)
    link_nodes(temporal_align_tree, input_node, "Vector + 2", displace_frame_2, 1)
    link_nodes(temporal_align_tree, input_node, "Albedo + 2", displace_frame_2_ta, 0)
    link_nodes(temporal_align_tree, input_node, "Vector + 2", displace_frame_2_ta, 1)

    link_nodes(temporal_align_tree, input_node, "Frame + 1", median_max_0, 0)
    link_nodes(temporal_align_tree, displace_frame_2, 0, median_max_0, 1)
    link_nodes(temporal_align_tree, input_node, "Albedo + 1", median_max_0_ta, 0)
    link_nodes(temporal_align_tree, displace_frame_2_ta, 0, median_max_0_ta, 1)

    link_nodes(temporal_align_tree, input_node, "Frame + 1", median_min_0, 0)
    link_nodes(temporal_align_tree, displace_frame_2, 0, median_min_0, 1)
    link_nodes(temporal_align_tree, input_node, "Albedo + 1", median_min_0_ta, 0)
    link_nodes(temporal_align_tree, displace_frame_2_ta, 0, median_min_0_ta, 1)

    link_nodes(temporal_align_tree, median_max_0, 0, median_min_1, 0)
    link_nodes(temporal_align_tree, displace_frame_0, 0, median_min_1, 1)
    link_nodes(temporal_align_tree, median_max_0_ta, 0, median_min_1_ta, 0)
    link_nodes(temporal_align_tree, displace_frame_0_ta, 0, median_min_1_ta, 1)

    link_nodes(temporal_align_tree, median_min_1, 0, median_max_1, 0)
    link_nodes(temporal_align_tree, median_min_0, 0, median_max_1, 1)
    link_nodes(temporal_align_tree, median_min_1_ta, 0, median_max_1_ta, 0)
    link_nodes(temporal_align_tree, median_min_0_ta, 0, median_max_1_ta, 1)

    link_nodes(temporal_align_tree, input_node, "Frame + 1", alpha_over, 1)
    link_nodes(temporal_align_tree, median_max_1, 0, alpha_over, 2)
    link_nodes(temporal_align_tree, input_node, "Frame + 1", alpha_over_ta, 1)
    link_nodes(temporal_align_tree, median_max_1_ta, 0, alpha_over_ta, 2)

    link_nodes(temporal_align_tree, alpha_over_ta, 0, ta_difference, 1)
    link_nodes(temporal_align_tree, input_node, "Albedo + 1", ta_difference, 2)

    link_nodes(temporal_align_tree, ta_difference, 0 , ta_multiply, 0)
    link_nodes(temporal_align_tree, ta_multiply, 0, ta_dialate, 0)
    link_nodes(temporal_align_tree, ta_dialate, 0, ta_mix, 0)
    link_nodes(temporal_align_tree, alpha_over, 0, ta_mix, 1)
    link_nodes(temporal_align_tree, input_node, "Frame + 1", ta_mix, 2)

    link_nodes(temporal_align_tree, ta_mix, 0, vector_blur, 0)
    link_nodes(temporal_align_tree, input_node, "Depth + 1", vector_blur, 1)
    link_nodes(temporal_align_tree, input_node, "Vector + 1", vector_blur, 2)

    link_nodes(temporal_align_tree, vector_blur, 0, crop_node, 0)
    link_nodes(temporal_align_tree, crop_node, 0, output_node, "Temporal Aligned")

    if settings.overscan == 0:
        crop_node.mute = True

    return temporal_align_tree

def output_format(setting):
    settings = bpy.context.scene.sid_settings
    setting.file_format = settings.file_format
    # PNG
    if settings.file_format == "PNG":
        setting.color_mode = 'RGBA'
        setting.color_depth = '8'
        setting.compression = 0
    # JPEG
    elif settings.file_format == "JPEG":
        setting.color_mode = 'RGB'
        setting.quality = 90
    # EXR
    elif settings.file_format == "OPEN_EXR":

        setting.color_mode = 'RGBA'
        setting.color_depth = '32'
        setting.exr_codec = 'PIZ'
    # TIFF
    elif settings.file_format == "TIFF":
        setting.color_mode = 'RGBA'
        setting.color_depth = '16'
        setting.tiff_codec = 'NONE'

def create_temporal_setup(scene, view_layer_id: int):
    settings = bpy.context.scene.sid_settings

    frames = 0
    # count all files in the folder
    for file in os.listdir(os.path.join(bpy.path.abspath(settings.working_directory), "processing", str(view_layer_id))):
        if file.endswith(".exr"):
            frames += 1
    
    if frames < 4:
        print(bcolors.WARNING + "Not enough frames to denoise, needs at least 4, skipping..."+ bcolors.ENDC)
        return

    pre_denoise_info = f"Starting to denoise animation // Layers: {view_layer_id} // Frames: {frames}"
    print(bcolors.OKBLUE + pre_denoise_info+ bcolors.ENDC, "\n")

    compositor = scene.node_tree
    path_processing = os.path.join(bpy.path.abspath(settings.working_directory), "processing", str(view_layer_id))
    path_completed = os.path.join(bpy.path.abspath(settings.working_directory), "completed", str(view_layer_id))
    
    for node in compositor.nodes: compositor.nodes.remove(node)

    old_frame_start = scene.frame_start
    scene.frame_start = 2
    scene.frame_end = frames - 2
    scene.frame_current = 2

    # create nodes
    def load_processing_image(image_offset: str):

        image_path = os.path.join(path_processing, settings.custom_name + str(image_offset).zfill(6) + ".exr")
        image_name = os.path.basename(image_path)

        if image_name in bpy.data.images:
            return bpy.data.images.get(image_name)

        image = bpy.data.images.load(image_path)
        image.source = "SEQUENCE"

        return image
    
    def unload_processing_image(image_offset: str):
        image_path = os.path.join(path_processing, settings.custom_name + str(image_offset).zfill(6) + ".exr")
        image_name = os.path.basename(image_path)

        if image_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images.get(image_name))

    def create_temporal_image_nodes(offset) -> Node:
        image_node = compositor.nodes.new("CompositorNodeImage")
        image_node.image = load_processing_image(str(old_frame_start))
        image_node.frame_duration = frames
        image_node.frame_start = 1
        image_node.frame_offset = offset + old_frame_start - 1
        image_node.label = "SID Image"
        return image_node

    frame_0 = create_temporal_image_nodes(0)
    frame_1 = create_temporal_image_nodes(1)
    frame_2 = create_temporal_image_nodes(2)

    def link_to_temporal_node(input_node, layer, output_node):

        link_nodes(compositor, frame_0, layer, input_node, "Frame + 0")
        link_nodes(compositor, frame_0, "Vector", input_node, "Vector + 0")
        link_nodes(compositor, frame_0, settings.ted_source, input_node, "Albedo + 0")

        link_nodes(compositor, frame_1, layer, input_node, "Frame + 1")
        link_nodes(compositor, frame_1, "Vector", input_node, "Vector + 1")
        link_nodes(compositor, frame_1, settings.ted_source, input_node, "Albedo + 1")
        link_nodes(compositor, frame_1, "Depth", input_node, "Depth + 1")

        link_nodes(compositor, frame_2, layer, input_node, "Frame + 2")
        link_nodes(compositor, frame_2, "Vector", input_node, "Vector + 2")
        link_nodes(compositor, frame_2, settings.ted_source, input_node, "Albedo + 2")

        link_nodes(compositor, input_node, 0, output_node, layer)

    temporal_align = compositor.nodes.new("CompositorNodeGroup")
    temporal_align.node_tree = create_temporal_align()

    output_node = compositor.nodes.new("CompositorNodeComposite")

    link_to_temporal_node(temporal_align, "Image", output_node)

    if settings.use_sac:
        sac_tree = bpy.data.node_groups.get("Super Advanced Camera")
        sac_node_group = compositor.nodes.new("CompositorNodeGroup")
        sac_node_group.node_tree = sac_tree

        link_nodes(compositor, temporal_align, 0, sac_node_group, 0)
        link_nodes(compositor, sac_node_group, 0, output_node, "Image")

    scene.render.filepath = os.path.join(path_completed, settings.custom_name + "######")

    output_format(scene.render.image_settings)


    bpy.ops.render.render(animation = True, scene = scene.name)
    unload_processing_image(str(old_frame_start))

    if not settings.frame_compensation:
        return

    first_frame_int = 0
    last_frame = 0

    for file in os.listdir(path_processing):
        if file.endswith(".exr"):
            if first_frame_int == 0:
                first_frame_int = int((file.split(".")[0]).replace(settings.custom_name, ""))
            last_frame_int = int((file.split(".")[0]).replace(settings.custom_name, ""))

    first_frame = str(first_frame_int).zfill(6)
    last1_frame = str(last_frame_int - 1).zfill(6)
    last_frame = str(last_frame_int).zfill(6)

    # add the first frame as an image node connected to an output file node with the path to the completed folder

    def create_temporal_image_nodes_comp(offset) -> Node:
        image_node = compositor.nodes.new("CompositorNodeImage")
        image_node.image = bpy.data.images.load(os.path.join(path_processing, settings.custom_name + offset + ".exr"))
        image_node.frame_duration = frames
        image_node.frame_start = 1
        image_node.frame_offset = int(offset) + int(old_frame_start) - 1
        image_node.label = "SID Image"
        return image_node
    
    first_frame_node = create_temporal_image_nodes_comp(first_frame)
    last_frame_node1 = create_temporal_image_nodes_comp(last1_frame)
    last_frame_node2 = create_temporal_image_nodes_comp(last_frame)

    crop_tree = create_temporal_crop()

    crop_node_group1 = compositor.nodes.new("CompositorNodeGroup")
    crop_node_group1.node_tree = crop_tree
    crop_node_group2 = compositor.nodes.new("CompositorNodeGroup")
    crop_node_group2.node_tree = crop_tree
    crop_node_group3 = compositor.nodes.new("CompositorNodeGroup")
    crop_node_group3.node_tree = crop_tree

    output_node = compositor.nodes.new("CompositorNodeOutputFile")
    output_node.base_path = path_completed
    
    output_format(output_node.format)

    output_node.file_slots.remove(output_node.inputs[0])

    first_frame_out = settings.custom_name + str(first_frame_int).zfill(6)
    last1_frame_out = settings.custom_name + str(last_frame_int-1).zfill(6)
    last_frame_out = settings.custom_name + str(last_frame_int).zfill(6)

    output_names = [first_frame_out, last1_frame_out, last_frame_out]
    for name in output_names:
        output_node.file_slots.new(name)
        output_node.file_slots[name].path = name


    link_nodes(compositor, first_frame_node, "Image", crop_node_group1, 0)
    link_nodes(compositor, last_frame_node1, "Image", crop_node_group2, 0)
    link_nodes(compositor, last_frame_node2, "Image", crop_node_group3, 0)

    if settings.use_sac:
        sac_node_group1 = compositor.nodes.new("CompositorNodeGroup")
        sac_node_group1.node_tree = sac_tree
        sac_node_group2 = compositor.nodes.new("CompositorNodeGroup")
        sac_node_group2.node_tree = sac_tree
        sac_node_group3 = compositor.nodes.new("CompositorNodeGroup")
        sac_node_group3.node_tree = sac_tree

        link_nodes(compositor, crop_node_group1, 0, sac_node_group1, 0)
        link_nodes(compositor, sac_node_group1, 0, output_node, first_frame_out)

        link_nodes(compositor, crop_node_group2, 0, sac_node_group2, 0)
        link_nodes(compositor, sac_node_group2, 0, output_node, last1_frame_out)

        link_nodes(compositor, crop_node_group3, 0, sac_node_group3, 0)
        link_nodes(compositor, sac_node_group3, 0, output_node, last_frame_out)
    
    else:
        link_nodes(compositor, crop_node_group1, 0, output_node, first_frame_out)
        link_nodes(compositor, crop_node_group2, 0, output_node, last1_frame_out)
        link_nodes(compositor, crop_node_group3, 0, output_node, last_frame_out)
        
    scene.frame_start = 1
    bpy.ops.render.render(animation = False, scene = scene.name, write_still = False)
    unload_processing_image(first_frame)
    unload_processing_image(last1_frame)
    unload_processing_image(last_frame)

    # search the completed folder for files with 10 digits and rename them to first 6 digits, so that 1234567890.png becomes 123456.png
    length = len(settings.custom_name) + 6
    for file in os.listdir(path_completed):
        if len(file.split(".")[0]) > length:
            try:
                os.rename(os.path.join(path_completed, file), os.path.join(path_completed, file.split(".")[0][0:length] + "." + file.split(".")[1]))
            except Exception as e:
                print(bcolors.WARNING + "Error while renaming file:", e+ bcolors.ENDC)

    return

def create_combine_setup(scene, view_layer_id: int):
    settings = bpy.context.scene.sid_settings

    if settings.file_format == "PNG":
        ends_with = ".png"
    elif settings.file_format == "JPEG":
        ends_with = ".jpg"
    elif settings.file_format == "OPEN_EXR":
        ends_with = ".exr"
    elif settings.file_format == "TIFF":
        ends_with = ".tiff"
    
    frames = 0
    # count all files in the folder
    for file in os.listdir(os.path.join(bpy.path.abspath(settings.working_directory), "completed", str(view_layer_id))):
        if file.endswith(ends_with):
            frames += 1

    pre_combine_info = f"Starting to combine frames into animation // Layers: {view_layer_id} // Frames: {frames}"
    print(bcolors.OKBLUE + pre_combine_info+ bcolors.ENDC, "\n")

    compositor = scene.node_tree
    path_completed = os.path.join(bpy.path.abspath(settings.working_directory), "completed", str(view_layer_id))
    path_combined = os.path.join(bpy.path.abspath(settings.working_directory), "combined", str(view_layer_id))
    
    for node in compositor.nodes: compositor.nodes.remove(node)

    scene.frame_start = 1
    scene.frame_end = frames
    scene.frame_current = 1

    # create nodes
    def load_processing_image():

        image_path = os.path.join(path_completed, settings.custom_name + str(scene.frame_start).zfill(6) + ends_with)
        image_name = os.path.basename(image_path)

        if image_name in bpy.data.images:
            return bpy.data.images.get(image_name)

        image = bpy.data.images.load(image_path)
        image.source = "SEQUENCE"

        return image
    
    def unload_processing_image():
        image_path = os.path.join(path_completed, settings.custom_name + str(scene.frame_start).zfill(6) + ends_with)
        image_name = os.path.basename(image_path)

        if image_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images.get(image_name))

    image_node = compositor.nodes.new("CompositorNodeImage")
    image_node.image = load_processing_image()
    image_node.frame_duration = frames
    image_node.frame_start = 1
    image_node.frame_offset = -1
    image_node.label = "SID Image"

    output_node = compositor.nodes.new("CompositorNodeComposite")

    # link the nodes
    link_nodes(compositor, image_node, "Image", output_node, 0)

    scene.render.filepath = os.path.join(path_combined, settings.custom_name + "######")

    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.image_settings.color_mode = 'RGB'

    if settings.file_format_video == "H264_in_MP4": H264_in_MP4(scene)
    elif settings.file_format_video == "Xvid": Xvid(scene)
    elif settings.file_format_video == "WebM_VP9": WebM_VP9(scene)
    elif settings.file_format_video == "Ogg_Theora": Ogg_Theora(scene)
    elif settings.file_format_video == "H264_in_Matroska": H264_in_Matroska(scene)
    elif settings.file_format_video == "H264_in_Matroska_for_scrubbing": H264_in_Matroska_for_scrubbing(scene)

    bpy.ops.render.render(animation = True, scene = scene.name)
    unload_processing_image()

    

# endregion Other Tools