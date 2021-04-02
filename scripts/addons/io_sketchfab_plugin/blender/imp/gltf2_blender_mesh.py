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
import bmesh

from .gltf2_blender_primitive import *
from .gltf2_blender_skin import *
from ..com.gltf2_blender_conversion import *

class BlenderMesh():

    @staticmethod
    def create(gltf, mesh_idx, node_idx, parent):
        pymesh = gltf.data.meshes[mesh_idx]
        pynode = gltf.data.nodes[node_idx]

        # Geometry
        if pymesh.name:
            mesh_name = pymesh.name
        else:
            mesh_name = "Mesh_" + str(mesh_idx)

        mesh = bpy.data.meshes.new(mesh_name)
        verts = []
        edges = []
        faces = []
        for prim in pymesh.primitives:
            verts, edges, faces = BlenderPrimitive.create(gltf, prim, verts, edges, faces)

        mesh.from_pydata(verts, edges, faces)
        mesh.validate()

        return mesh

    @staticmethod
    def set_mesh(gltf, pymesh, mesh, obj):
        # Normals
        offset = 0
        for prim in pymesh.primitives:
            offset = BlenderPrimitive.set_normals(gltf, prim, mesh, offset)

        mesh.update()

        # manage UV
        offset = 0
        for prim in pymesh.primitives:
            offset = BlenderPrimitive.set_UV(gltf, prim, obj, mesh, offset)

        mesh.update()

        # Object and UV are now created, we can set UVMap into material
        for prim in pymesh.primitives:
            BlenderPrimitive.set_UV_in_mat(gltf, prim, obj)

        # Assign materials to mesh
        offset = 0
        cpt_index_mat = 0
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        for prim in pymesh.primitives:
            offset, cpt_index_mat = BlenderPrimitive.assign_material(gltf, prim, obj, bm, offset, cpt_index_mat)

        bm.to_mesh(obj.data)
        bm.free()

        # Create shapekeys if needed
        max_shape_to_create = 0
        for prim in pymesh.primitives:
            if prim.targets:
                if len(prim.targets) > max_shape_to_create:
                    max_shape_to_create = len(prim.targets)

        # Create basis shape key
        if max_shape_to_create > 0:
            obj.shape_key_add(name = "Basis")

        for i in range(max_shape_to_create):

            obj.shape_key_add(name="target_" + str(i))

            offset_idx = 0
            for prim in pymesh.primitives:
                if prim.targets is None:
                    continue
                if i >= len(prim.targets):
                    continue

                bm = bmesh.new()
                bm.from_mesh(mesh)

                shape_layer = bm.verts.layers.shape[i+1]

                pos = BinaryData.get_data_from_accessor(gltf, prim.targets[i]['POSITION'])

                for vert in bm.verts:
                    if not vert.index in range(offset_idx, offset_idx + prim.vertices_length):
                        continue

                    shape = vert[shape_layer]

                    co = Conversion.loc_gltf_to_blender(list(pos[vert.index - offset_idx]))
                    shape.x = obj.data.vertices[vert.index].co.x + co[0]
                    shape.y = obj.data.vertices[vert.index].co.y + co[1]
                    shape.z = obj.data.vertices[vert.index].co.z + co[2]

                bm.to_mesh(obj.data)
                bm.free()
                offset_idx += prim.vertices_length

        # set default weights for shape keys, and names
        if pymesh.weights is not None:
            for i in range(max_shape_to_create):
                if i < len(pymesh.weights):
                    obj.data.shape_keys.key_blocks[i+1].value = pymesh.weights[i]
                    if gltf.data.accessors[pymesh.primitives[0].targets[i]['POSITION']].name is not None:
                       obj.data.shape_keys.key_blocks[i+1].name  = gltf.data.accessors[pymesh.primitives[0].targets[i]['POSITION']].name


        # Apply vertex color.
        vertex_color = None
        offset = 0
        for prim in pymesh.primitives:
            if 'COLOR_0' in prim.attributes.keys():
                # Create vertex color, once only per object
                if vertex_color is None:
                    vertex_color = obj.data.vertex_colors.new(name="COLOR_0")

                color_data = BinaryData.get_data_from_accessor(gltf, prim.attributes['COLOR_0'])

                for poly in mesh.polygons:
                    for loop_idx in range(poly.loop_start, poly.loop_start + poly.loop_total):
                        vert_idx = mesh.loops[loop_idx].vertex_index
                        if vert_idx in range(offset, offset + prim.vertices_length):
                            cpt_idx = vert_idx - offset
                            if bpy.app.version < (2, 80, 0):
                                vertex_color.data[loop_idx].color = tuple(list(color_data[cpt_idx][0:3]))
                            else:
                                vertex_color.data[loop_idx].color = tuple(list(color_data[cpt_idx][0:3]) + [1.0])

            offset = offset + prim.vertices_length
