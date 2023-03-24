"""
 * ***** BEGIN GPL LICENSE BLOCK *****
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * Contributor(s): Julien Duroure.
 *
 * ***** END GPL LICENSE BLOCK *****
 """

import bpy
from .gltf2_blender_texture import *

# Version management
from ..blender_version import Version

class BlenderPbr():

    def create(gltf, pypbr, mat_name, vertex_color):
        engine = bpy.context.scene.render.engine
        if engine == Version.ENGINE:
            BlenderPbr.create_cycles(gltf, pypbr, mat_name, vertex_color)
        else:
            pass #TODO for internal / Eevee in future 2.8

    def create_cycles(gltf, pypbr, mat_name, vertex_color):
        material = bpy.data.materials[mat_name]
        material.use_nodes = True
        node_tree = material.node_tree

        # delete all nodes except output
        for node in list(node_tree.nodes):
            if not node.type == 'OUTPUT_MATERIAL':
                node_tree.nodes.remove(node)

        output_node = node_tree.nodes[0]
        output_node.location = 1250,0

        # create PBR node
        principled = node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        principled.location = 0,0

        if pypbr.color_type == gltf.SIMPLE:

            if not vertex_color:

                # change input values
                principled.inputs[0].default_value = pypbr.base_color_factor
                principled.inputs[5].default_value = pypbr.metallic_factor #TODO : currently set metallic & specular in same way
                principled.inputs[7].default_value = pypbr.roughness_factor

            else:
                # Create attribute node to get COLOR_0 data
                attribute_node = node_tree.nodes.new('ShaderNodeAttribute')
                attribute_node.attribute_name = 'COLOR_0'
                attribute_node.location = -500,0

                principled.inputs[5].default_value = pypbr.metallic_factor #TODO : currently set metallic & specular in same way
                principled.inputs[7].default_value = pypbr.roughness_factor

                # links
                rgb_node = node_tree.nodes.new('ShaderNodeMixRGB')
                rgb_node.blend_type = 'MULTIPLY'
                rgb_node.inputs['Fac'].default_value = 1.0
                rgb_node.inputs['Color1'].default_value = pypbr.base_color_factor
                node_tree.links.new(rgb_node.inputs['Color2'], attribute_node.outputs[0])
                node_tree.links.new(principled.inputs[0], rgb_node.outputs[0])

        elif pypbr.color_type == gltf.TEXTURE_FACTOR:

            #TODO alpha ?
            if vertex_color:
                # TODO tree locations
                # Create attribute / separate / math nodes
                attribute_node = node_tree.nodes.new('ShaderNodeAttribute')
                attribute_node.attribute_name = 'COLOR_0'

                separate_vertex_color = node_tree.nodes.new('ShaderNodeSeparateRGB')
                math_vc_R = node_tree.nodes.new('ShaderNodeMath')
                math_vc_R.operation = 'MULTIPLY'

                math_vc_G = node_tree.nodes.new('ShaderNodeMath')
                math_vc_G.operation = 'MULTIPLY'

                math_vc_B = node_tree.nodes.new('ShaderNodeMath')
                math_vc_B.operation = 'MULTIPLY'

            BlenderTextureInfo.create(gltf, pypbr.base_color_texture.index)

            # create UV Map / Mapping / Texture nodes / separate & math and combine
            text_node = BlenderTextureNode.create(gltf, pypbr.base_color_texture.index, node_tree, 'BASE COLOR')
            text_node.location = -1000,500

            combine = node_tree.nodes.new('ShaderNodeCombineRGB')
            combine.location = -250,500

            math_R  = node_tree.nodes.new('ShaderNodeMath')
            math_R.location = -500, 750
            math_R.operation = 'MULTIPLY'
            math_R.inputs[1].default_value = pypbr.base_color_factor[0]

            math_G  = node_tree.nodes.new('ShaderNodeMath')
            math_G.location = -500, 500
            math_G.operation = 'MULTIPLY'
            math_G.inputs[1].default_value = pypbr.base_color_factor[1]

            math_B  = node_tree.nodes.new('ShaderNodeMath')
            math_B.location = -500, 250
            math_B.operation = 'MULTIPLY'
            math_B.inputs[1].default_value = pypbr.base_color_factor[2]

            separate = node_tree.nodes.new('ShaderNodeSeparateRGB')
            separate.location = -750, 500

            mapping = node_tree.nodes.new('ShaderNodeMapping')
            mapping.location = -1500, 500

            uvmap = node_tree.nodes.new('ShaderNodeUVMap')
            uvmap.location = -2000, 500
            if pypbr.base_color_texture.tex_coord is not None:
                uvmap["gltf2_texcoord"] = pypbr.base_color_texture.tex_coord # Set custom flag to retrieve TexCoord
            else:
                uvmap["gltf2_texcoord"] = 0 #TODO set in pre_compute instead of here
            # UV Map will be set after object/UVMap creation

            # Create links
            if vertex_color:
                node_tree.links.new(separate_vertex_color.inputs[0], attribute_node.outputs[0])
                node_tree.links.new(math_vc_R.inputs[1], separate_vertex_color.outputs[0])
                node_tree.links.new(math_vc_G.inputs[1], separate_vertex_color.outputs[1])
                node_tree.links.new(math_vc_B.inputs[1], separate_vertex_color.outputs[2])
                node_tree.links.new(math_vc_R.inputs[0], math_R.outputs[0])
                node_tree.links.new(math_vc_G.inputs[0], math_G.outputs[0])
                node_tree.links.new(math_vc_B.inputs[0], math_B.outputs[0])
                node_tree.links.new(combine.inputs[0], math_vc_R.outputs[0])
                node_tree.links.new(combine.inputs[1], math_vc_G.outputs[0])
                node_tree.links.new(combine.inputs[2], math_vc_B.outputs[0])

            else:
                node_tree.links.new(combine.inputs[0], math_R.outputs[0])
                node_tree.links.new(combine.inputs[1], math_G.outputs[0])
                node_tree.links.new(combine.inputs[2], math_B.outputs[0])

            # Common for both mode (non vertex color / vertex color)
            node_tree.links.new(math_R.inputs[0], separate.outputs[0])
            node_tree.links.new(math_G.inputs[0], separate.outputs[1])
            node_tree.links.new(math_B.inputs[0], separate.outputs[2])

            node_tree.links.new(mapping.inputs[0], uvmap.outputs[0])
            node_tree.links.new(text_node.inputs[0], mapping.outputs[0])
            node_tree.links.new(separate.inputs[0], text_node.outputs[0])


            node_tree.links.new(principled.inputs[0], combine.outputs[0])

        elif pypbr.color_type == gltf.TEXTURE:

            BlenderTextureInfo.create(gltf, pypbr.base_color_texture.index)

            #TODO alpha ?
            if vertex_color:
                # Create attribute / separate / math nodes
                attribute_node = node_tree.nodes.new('ShaderNodeAttribute')
                attribute_node.attribute_name = 'COLOR_0'
                attribute_node.location = -2000,250

                separate_vertex_color = node_tree.nodes.new('ShaderNodeSeparateRGB')
                separate_vertex_color.location = -1500, 250

                math_vc_R = node_tree.nodes.new('ShaderNodeMath')
                math_vc_R.operation = 'MULTIPLY'
                math_vc_R.location = -1000,750

                math_vc_G = node_tree.nodes.new('ShaderNodeMath')
                math_vc_G.operation = 'MULTIPLY'
                math_vc_G.location = -1000,500

                math_vc_B = node_tree.nodes.new('ShaderNodeMath')
                math_vc_B.operation = 'MULTIPLY'
                math_vc_B.location = -1000,250


                combine = node_tree.nodes.new('ShaderNodeCombineRGB')
                combine.location = -500,500

                separate = node_tree.nodes.new('ShaderNodeSeparateRGB')
                separate.location = -1500, 500

            # create UV Map / Mapping / Texture nodes / separate & math and combine
            text_node = node_tree.nodes.new('ShaderNodeTexImage')
            text_node = BlenderTextureNode.create(gltf, pypbr.base_color_texture.index, node_tree, 'BASE COLOR')

            if vertex_color:
                text_node.location = -2000,500
            else:
                text_node.location = -500,500

            mapping = node_tree.nodes.new('ShaderNodeMapping')
            if vertex_color:
                mapping.location = -2500,500
            else:
                mapping.location = -1500,500

            uvmap = node_tree.nodes.new('ShaderNodeUVMap')
            if vertex_color:
                uvmap.location = -3000,500
            else:
                uvmap.location = -2000,500
            if pypbr.base_color_texture.tex_coord is not None:
                uvmap["gltf2_texcoord"] = pypbr.base_color_texture.tex_coord # Set custom flag to retrieve TexCoord
            else:
                uvmap["gltf2_texcoord"] = 0 #TODO set in pre_compute instead of here
            # UV Map will be set after object/UVMap creation

            # Create links
            if vertex_color:
                node_tree.links.new(separate_vertex_color.inputs[0], attribute_node.outputs[0])

                node_tree.links.new(math_vc_R.inputs[1], separate_vertex_color.outputs[0])
                node_tree.links.new(math_vc_G.inputs[1], separate_vertex_color.outputs[1])
                node_tree.links.new(math_vc_B.inputs[1], separate_vertex_color.outputs[2])

                node_tree.links.new(combine.inputs[0], math_vc_R.outputs[0])
                node_tree.links.new(combine.inputs[1], math_vc_G.outputs[0])
                node_tree.links.new(combine.inputs[2], math_vc_B.outputs[0])

                node_tree.links.new(separate.inputs[0], text_node.outputs[0])

                node_tree.links.new(principled.inputs[0], combine.outputs[0])

                node_tree.links.new(math_vc_R.inputs[0], separate.outputs[0])
                node_tree.links.new(math_vc_G.inputs[0], separate.outputs[1])
                node_tree.links.new(math_vc_B.inputs[0], separate.outputs[2])

            else:
                node_tree.links.new(principled.inputs[0], text_node.outputs[0])

            # Common for both mode (non vertex color / vertex color)

            node_tree.links.new(mapping.inputs[0], uvmap.outputs[0])
            node_tree.links.new(text_node.inputs[0], mapping.outputs[0])


        # Says metallic, but it means metallic & Roughness values
        if pypbr.metallic_type == gltf.SIMPLE:
            principled.inputs[4].default_value = pypbr.metallic_factor
            principled.inputs[7].default_value = pypbr.roughness_factor

        elif pypbr.metallic_type == gltf.TEXTURE:
            BlenderTextureInfo.create(gltf, pypbr.metallic_roughness_texture.index)
            metallic_text = BlenderTextureNode.create(gltf, pypbr.metallic_roughness_texture.index, node_tree, 'METALLIC ROUGHNESS')
            Version.set_colorspace(metallic_text)
            metallic_text.location = -500,0

            metallic_separate = node_tree.nodes.new('ShaderNodeSeparateRGB')
            metallic_separate.location = -250,0

            metallic_mapping = node_tree.nodes.new('ShaderNodeMapping')
            metallic_mapping.location = -1000,0

            metallic_uvmap = node_tree.nodes.new('ShaderNodeUVMap')
            metallic_uvmap.location = -1500,0
            if pypbr.metallic_roughness_texture.tex_coord is not None:
                metallic_uvmap["gltf2_texcoord"] = pypbr.metallic_roughness_texture.tex_coord # Set custom flag to retrieve TexCoord
            else:
                metallic_uvmap["gltf2_texcoord"] = 0 #TODO set in pre_compute instead of here

            # links
            node_tree.links.new(metallic_separate.inputs[0], metallic_text.outputs[0])
            node_tree.links.new(principled.inputs[4], metallic_separate.outputs[2]) # metallic
            node_tree.links.new(principled.inputs[7], metallic_separate.outputs[1]) # Roughness

            node_tree.links.new(metallic_mapping.inputs[0], metallic_uvmap.outputs[0])
            node_tree.links.new(metallic_text.inputs[0], metallic_mapping.outputs[0])

        elif pypbr.metallic_type == gltf.TEXTURE_FACTOR:

            BlenderTextureInfo.create(gltf, pypbr.metallic_roughness_texture.index)
            metallic_text = BlenderTextureNode.create(gltf, pypbr.metallic_roughness_texture.index, node_tree, 'METALLIC ROUGHNESS')
            Version.set_colorspace(metallic_text)
            metallic_text.location = -1000,0

            metallic_separate = node_tree.nodes.new('ShaderNodeSeparateRGB')
            metallic_separate.location = -500,0

            metallic_math     = node_tree.nodes.new('ShaderNodeMath')
            metallic_math.operation = 'MULTIPLY'
            metallic_math.inputs[1].default_value = pypbr.metallic_factor
            metallic_math.location = -250,100

            roughness_math = node_tree.nodes.new('ShaderNodeMath')
            roughness_math.operation = 'MULTIPLY'
            roughness_math.inputs[1].default_value = pypbr.roughness_factor
            roughness_math.location = -250,-100

            metallic_mapping = node_tree.nodes.new('ShaderNodeMapping')
            metallic_mapping.location = -1000,0

            metallic_uvmap = node_tree.nodes.new('ShaderNodeUVMap')
            metallic_uvmap.location = -1500,0
            if pypbr.metallic_roughness_texture.tex_coord is not None:
                metallic_uvmap["gltf2_texcoord"] = pypbr.metallic_roughness_texture.tex_coord # Set custom flag to retrieve TexCoord
            else:
                metallic_uvmap["gltf2_texcoord"] = 0 #TODO set in pre_compute instead of here


            # links
            node_tree.links.new(metallic_separate.inputs[0], metallic_text.outputs[0])

            # metallic
            node_tree.links.new(metallic_math.inputs[0], metallic_separate.outputs[2])
            node_tree.links.new(principled.inputs[4], metallic_math.outputs[0])

            # roughness
            node_tree.links.new(roughness_math.inputs[0], metallic_separate.outputs[1])
            node_tree.links.new(principled.inputs[7], roughness_math.outputs[0])

            node_tree.links.new(metallic_mapping.inputs[0], metallic_uvmap.outputs[0])
            node_tree.links.new(metallic_text.inputs[0], metallic_mapping.outputs[0])

        # link node to output
        node_tree.links.new(output_node.inputs[0], principled.outputs[0])
