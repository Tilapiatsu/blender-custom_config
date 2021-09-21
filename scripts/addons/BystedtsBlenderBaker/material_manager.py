import bpy

def get_material_output_node(context, material):

    node_tree = material.node_tree
    for node in node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL' and node.is_active_output:
            return node



def get_shader_connected_to_material_output(context, material, material_output_node = None):

    if material_output_node == None:
        material_output_node = get_material_output_node(context, material)
    
    return material_output_node.inputs['Surface'].links[0].from_node

def connect_emission_to_material_output(context, material, material_output_node = None):

    if material_output_node == None:
        material_output_node = get_material_output_node(context, material)

    node_tree = material.node_tree
    emission_node = node_tree.nodes.new(type="ShaderNodeEmission")
    node_tree.links.new(emission_node.outputs['Emission'], material_output_node.inputs['Surface'])

    return emission_node

def get_nodes_of_type(context, material, node_type):
    
    return_nodes = []

    for node in  material.node_tree.nodes:
        if node.type == node_type:
            return_nodes.append(node)

    return return_nodes