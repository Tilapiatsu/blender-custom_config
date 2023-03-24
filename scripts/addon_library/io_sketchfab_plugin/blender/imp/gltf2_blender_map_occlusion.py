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

class BlenderOcclusionMap():

    @staticmethod
    def create(gltf, material_idx):
        engine = bpy.context.scene.render.engine
        if engine == Version.ENGINE:
            BlenderOcclusionMap.create_cycles(gltf, material_idx)
        else:
            pass #TODO for internal / Eevee in future 2.8

    def create_cycles(gltf, material_idx):

        pymaterial = gltf.data.materials[material_idx]

        BlenderTextureInfo.create(gltf, pymaterial.occlusion_texture.index)

        # Pack texture, but doesn't use it for now. Occlusion is calculated from Cycles.
        bpy.data.images[gltf.data.images[gltf.data.textures[pymaterial.occlusion_texture.index].source].blender_image_name].use_fake_user = True
