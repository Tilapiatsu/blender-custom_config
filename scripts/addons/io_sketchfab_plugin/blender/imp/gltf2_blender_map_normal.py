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

class BlenderNormalMap():

    @staticmethod
    def create(gltf, material_idx):
        engine = bpy.context.scene.render.engine
        if engine == Version.ENGINE:
            BlenderNormalMap.create_cycles(gltf, material_idx)
        else:
            pass #TODO for internal / Eevee in future 2.8

    def create_cycles(gltf, material_idx):

        pymaterial = gltf.data.materials[material_idx]

        material = bpy.data.materials[pymaterial.blender_material]
        node_tree = material.node_tree

        BlenderTextureInfo.create(gltf, pymaterial.normal_texture.index)

        # retrieve principled node and output node
        principled = None
        diffuse   = None
        glossy    = None
        if len([node for node in node_tree.nodes if node.type == "BSDF_PRINCIPLED"]) != 0:
            principled = [node for node in node_tree.nodes if node.type == "BSDF_PRINCIPLED"][0]
        else:
            #No principled, we are probably coming from extension
            diffuse = [node for node in node_tree.nodes if node.type == "BSDF_DIFFUSE"][0]
            glossy  = [node for node in node_tree.nodes if node.type == "BSDF_GLOSSY"][0]

        # add nodes
        mapping = node_tree.nodes.new('ShaderNodeMapping')
        mapping.location = -1000,-500
        uvmap = node_tree.nodes.new('ShaderNodeUVMap')
        uvmap.location = -1500, -500
        if pymaterial.normal_texture.tex_coord is not None:
            uvmap["gltf2_texcoord"] = pymaterial.normal_texture.tex_coord # Set custom flag to retrieve TexCoord
        else:
            uvmap["gltf2_texcoord"] = 0 #TODO set in pre_compute instead of here

        text  = BlenderTextureNode.create(gltf, pymaterial.normal_texture.index, node_tree, 'NORMALMAP')
        Version.set_colorspace(text)
        text.location = -500, -500

        normalmap_node = node_tree.nodes.new('ShaderNodeNormalMap')
        normalmap_node.location = -250,-500
        if pymaterial.normal_texture.tex_coord is not None:
            normalmap_node["gltf2_texcoord"] = pymaterial.normal_texture.tex_coord # Set custom flag to retrieve TexCoord
        else:
            normalmap_node["gltf2_texcoord"] = 0 #TODO set in pre_compute instead of here


        # create links
        node_tree.links.new(mapping.inputs[0], uvmap.outputs[0])
        node_tree.links.new(text.inputs[0], mapping.outputs[0])
        node_tree.links.new(normalmap_node.inputs[1], text.outputs[0])

        # following  links will modify PBR node tree
        if principled:
            node_tree.links.new(principled.inputs["Normal"], normalmap_node.outputs[0])
        if diffuse:
            node_tree.links.new(diffuse.inputs[2], normalmap_node.outputs[0])
        if glossy:
            node_tree.links.new(glossy.inputs[2], normalmap_node.outputs[0])
