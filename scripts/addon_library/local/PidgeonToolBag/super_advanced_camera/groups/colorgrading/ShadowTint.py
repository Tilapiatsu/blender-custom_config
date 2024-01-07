import bpy
from bpy.types import NodeTree
from ....pidgeon_tool_bag.PTB_Functions import link_nodes, create_socket


def create_shadowtint_group() -> NodeTree:

    # Create the group
    sac_shadowtint_group: NodeTree = bpy.data.node_groups.new(name=".SAC ShadowTint", type="CompositorNodeTree")

    input_node = sac_shadowtint_group.nodes.new("NodeGroupInput")
    output_node = sac_shadowtint_group.nodes.new("NodeGroupOutput")

    # Create the sockets
    create_socket(sac_shadowtint_group, "Image", "NodeSocketColor", "INPUT")
    create_socket(sac_shadowtint_group, "Image", "NodeSocketColor", "OUTPUT")

    # Create the nodes
    subtract_node = sac_shadowtint_group.nodes.new("CompositorNodeMath")
    subtract_node.operation = "SUBTRACT"
    subtract_node.inputs[0].default_value = 1
    subtract_node.use_clamp = True

    mixrgb_node = sac_shadowtint_group.nodes.new("CompositorNodeMixRGB")
    mixrgb_node.blend_type = "COLOR"
    mixrgb_node.name = "SAC Colorgrade_Presets_ShadowTint"

    # Create the links
    link_nodes(sac_shadowtint_group, input_node, 0, subtract_node, 1)
    link_nodes(sac_shadowtint_group, input_node, 0, mixrgb_node, 1)
    link_nodes(sac_shadowtint_group, subtract_node, 0, mixrgb_node, 0)
    link_nodes(sac_shadowtint_group, mixrgb_node, 0, output_node, 0)

    return sac_shadowtint_group
