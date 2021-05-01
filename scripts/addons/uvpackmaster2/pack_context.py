# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


from .enums import *
from .prefs import *
from .utils import *
from .island_params import *
from .prefs import is_blender28

import time
import struct 

from mathutils import Vector, Matrix
import bmesh



class PackContext:
    # b_context = None
    # bm = None
    # uv_layer = None

    def __init__(self, _context):
        self.context = _context

        if is_blender28():
            self.objs = []

            for obj in self.context.selected_objects:

                if obj.type != 'MESH':
                    continue

                already_added = False
                for obj2 in self.objs:
                    if obj.data == obj2.data:
                        already_added = True
                        break

                if not already_added:
                    self.objs.append(obj)


            if self.context.active_object.type == 'MESH':
                active_added = False

                for obj2 in self.objs:
                    if self.context.active_object.data == obj2.data:
                        active_added = True
                        break

                if not active_added:
                    self.objs.append(self.context.active_object)

        else:
            self.objs = [self.context.active_object]

        self.bms = []
        self.uv_layers = []
        self.face_idx_offsets = []
        self.vert_idx_offsets = []

        self.island_bm_map = dict()
        self.uv_island_faces_list = None
        self.solution_matrices = None

        next_face_idx_offset = 0
        next_vert_idx_offset = 0

        for obj in self.objs:
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            self.bms.append(bm)
            self.uv_layers.append(bm.loops.layers.uv.verify())

            self.face_idx_offsets.append(next_face_idx_offset)
            next_face_idx_offset += len(bm.faces)

            self.vert_idx_offsets.append(next_vert_idx_offset)
            next_vert_idx_offset += len(bm.verts)

    def serialize_uv_maps(self, send_unselected, send_groups, send_rot_step, send_lock_groups, send_verts_3d, group_method=None):
        serialize_start = time.time()
        serialized_maps = bytes()
        selected_cnt = 0
        unselected_cnt = 0

        face_id_len_array = []
        uv_coord_array = []
        vert_idx_array = []
    
        serialization_flags = 0

        if send_unselected:
            serialization_flags |= UvMapSerializationFlags.CONTAINS_FLAGS
            face_flags_array = []

        if send_groups:
            serialization_flags |= UvMapSerializationFlags.CONTAINS_GROUPS
            self.get_face_group_method = self.init_grouping(group_method)
            face_groups_array = []

        if send_rot_step:
            serialization_flags |= UvMapSerializationFlags.CONTAINS_ROT_STEP

            rot_step_array = []
            rot_step_layers = []
            for bm in self.bms:
                rot_step_layers.append(self.get_or_create_vcolor_layer(bm, RotStepIslandParamInfo))

        if send_lock_groups:
            serialization_flags |= UvMapSerializationFlags.CONTAINS_LOCK_GROUPS

            lock_group_array = []
            lock_group_layers = []
            for bm in self.bms:
                lock_group_layers.append(self.get_or_create_vcolor_layer(bm, LockGroupIslandParamInfo))

        if send_verts_3d:

            serialization_flags |= UvMapSerializationFlags.CONTAINS_VERTS_3D
            verts_3d_array = []


        for bm_idx, bm in enumerate(self.bms):
            obj = self.objs[bm_idx]
            uv_layer = self.uv_layers[bm_idx]
            faces = self.get_visible_faces(bm) if send_unselected else self.get_selected_faces(bm, uv_layer)
            
            for face in faces:
                face_id_len_array.append(face.index + self.face_idx_offsets[bm_idx])
                face_id_len_array.append(len(face.verts))

                face_selected = True

                if send_unselected:
                    face_selected = self.face_is_selected(bm, uv_layer, face)
                    face_flags = 0

                    if face_selected:
                        face_flags |= UvFaceInputFlags.SELECTED
                        selected_cnt += 1
                    else:
                        unselected_cnt += 1

                    face_flags_array.append(face_flags)
                else:
                    selected_cnt += 1

                if send_groups:
                    face_groups_array.append(self.get_face_group_method(bm_idx, obj, face, face_selected))

                if send_rot_step:
                    rot_step_array.append(self.get_param(RotStepIslandParamInfo, rot_step_layers[bm_idx], face))

                if send_lock_groups:
                    lock_group_array.append(self.get_param(LockGroupIslandParamInfo, lock_group_layers[bm_idx], face))

                for loop in face.loops:
                    uv_tuple = loop[uv_layer].uv.to_tuple(5)
                    uv_coord_array.append(uv_tuple[0])
                    uv_coord_array.append(uv_tuple[1])
                    vert_idx_array.append(loop.vert.index + self.vert_idx_offsets[bm_idx])

                    if send_verts_3d:
                        verts_3d_array.append(loop.vert.co.x)
                        verts_3d_array.append(loop.vert.co.y)
                        verts_3d_array.append(loop.vert.co.z)

        serialized_maps += struct.pack('i', serialization_flags)
        serialized_maps += struct.pack('i', int(len(face_id_len_array) / 2))
        serialized_maps += struct.pack('i' * len(face_id_len_array), *face_id_len_array)
        serialized_maps += struct.pack('i', len(vert_idx_array))
        serialized_maps += struct.pack('f' * len(uv_coord_array), *uv_coord_array)
        serialized_maps += struct.pack('i' * len(vert_idx_array), *vert_idx_array)

        if (serialization_flags & UvMapSerializationFlags.CONTAINS_VERTS_3D) > 0:
            serialized_maps += struct.pack('f' * len(verts_3d_array), *verts_3d_array)

        if (serialization_flags & UvMapSerializationFlags.CONTAINS_FLAGS) > 0:
            serialized_maps += struct.pack('i' * len(face_flags_array), *face_flags_array)

        if (serialization_flags & UvMapSerializationFlags.CONTAINS_GROUPS) > 0:
            serialized_maps += struct.pack('i' * len(face_groups_array), *face_groups_array)

        if (serialization_flags & UvMapSerializationFlags.CONTAINS_ROT_STEP) > 0:
            serialized_maps += struct.pack('i' * len(rot_step_array), *rot_step_array)

        if (serialization_flags & UvMapSerializationFlags.CONTAINS_LOCK_GROUPS) > 0:
            serialized_maps += struct.pack('i' * len(lock_group_array), *lock_group_array)

        if in_debug_mode():
            print('UV serialization time: ' + str(time.time() - serialize_start))

        self.serialized_maps = serialized_maps
        return selected_cnt, unselected_cnt

    def calc_island_bbox(self, island_idx):

        x_coords = []
        y_coords = []

        bm_idx = self.island_bm_map[island_idx]
        bm = self.bms[bm_idx]
        face_idx_offset = self.face_idx_offsets[bm_idx]
        uv_layer = self.uv_layers[bm_idx]

        for face_idx in self.uv_island_faces_list[island_idx]:
            orig_face_idx = face_idx - face_idx_offset

            face = bm.faces[orig_face_idx]
            for loop in face.loops:
                x_coords.append(loop[uv_layer].uv[0])
                y_coords.append(loop[uv_layer].uv[1])

        return [Vector((min(x_coords), min(y_coords))), Vector((max(x_coords), max(y_coords)))]

    def islands_received(self):

        return self.uv_island_faces_list is not None

    def set_islands(self, selected_count, islands):
        if selected_count > len(islands):
            raise RuntimeError('Unexpected output from the UVP process')

        self.uv_island_faces_list = islands
        self.solution_matrices = [None] * len(islands)

        curr_bm_idx = 0
        for island_idx in range(selected_count):
            island = islands[island_idx]

            next_bm_idx = curr_bm_idx + 1
            while next_bm_idx < len(self.face_idx_offsets) and self.face_idx_offsets[next_bm_idx] <= island[0]:
                curr_bm_idx = next_bm_idx
                next_bm_idx += 1

            self.island_bm_map[island_idx] = curr_bm_idx

        curr_bm_idx = 0
        for island_idx in range(selected_count, len(islands)):
            island = islands[island_idx]

            next_bm_idx = curr_bm_idx + 1
            while next_bm_idx < len(self.face_idx_offsets) and self.face_idx_offsets[next_bm_idx] <= island[0]:
                curr_bm_idx = next_bm_idx
                next_bm_idx += 1

            self.island_bm_map[island_idx] = curr_bm_idx


    def get_face_group_material(self, bm_idx, obj, face, face_selected):

        mat_idx = face.material_index

        if not (mat_idx >= 0 and mat_idx < len(obj.material_slots)):
            raise RuntimeError('Grouping by material error: invalid material id')

        mat = obj.material_slots[mat_idx]

        if mat is None:
            raise RuntimeError('Grouping by material error: some faces belong to an empty material slot')

        return self.material_map[mat.name]

    def get_face_group_mesh(self, bm_idx, obj, face, face_selected):

        return self.mesh_map[bm_idx][face.index]

    def get_face_group_object(self, bm_idx, obj, face, face_selected):

        return bm_idx

    def get_face_group_tile(self, bm_idx, obj, face, face_selected):

        if not face_selected:
            return -1

        uv_layer = self.uv_layers[bm_idx]
        uvs = face.loops[0][uv_layer].uv

        if uvs[0] < 0.0 or uvs[1] < 0.0:
            raise RuntimeError("Grouping method '{}' requires all UV coordinates to be greater than 0".format(UvGroupingMethod.TILE.name))

        if uvs[0] >= UVP2_Preferences.MAX_TILES_IN_ROW:
            raise RuntimeError("Grouping method '{}' requires all UV X coordinates to be lower than {}".format(UvGroupingMethod.TILE.name, UVP2_Preferences.MAX_TILES_IN_ROW))

        return int(uvs[0]) + int(uvs[1]) * UVP2_Preferences.MAX_TILES_IN_ROW

    def get_face_group_manual(self, bm_idx, obj, face, face_selected):

        return self.get_param(GroupIslandParamInfo, self.manual_group_layers[bm_idx], face)

    def create_material_map(self):
        self.material_map = dict()

        next_mat_exid = 0

        for bm_idx in range(len(self.bms)):
            # bm_idx = self.island_bm_map[idx]
            bm = self.bms[bm_idx]
            obj = self.objs[bm_idx]

            if len(obj.material_slots) == 0:
                raise RuntimeError('Grouping by material error: object does not have a material assigned')

            for mat in obj.material_slots:
                if mat is None:
                    continue

                if mat.name not in self.material_map:
                    self.material_map[mat.name] = next_mat_exid
                    next_mat_exid += 1

        return len(self.material_map)

    def create_mesh_map(self):

        self.mesh_map = []
        curr_group_id = 0

        for bm_idx in range(len(self.bms)):

            mesh_map = dict()
            bm = self.bms[bm_idx]

            faces_left = set(range(len(bm.faces)))

            while len(faces_left) > 0:
                face_idx = list(faces_left)[0]
                faces_left.remove(face_idx)

                faces_to_process = []
                faces_to_process.append(face_idx)

                while len(faces_to_process) > 0:
                    new_face_idx = faces_to_process[0]
                    del faces_to_process[0]

                    mesh_map[new_face_idx] = curr_group_id
                    new_face = bm.faces[new_face_idx]

                    for vert in new_face.verts:
                        for face in vert.link_faces:
                            if face.index not in faces_left:
                                continue

                            faces_to_process.append(face.index)
                            faces_left.remove(face.index)

                curr_group_id += 1

            self.mesh_map.append(mesh_map)


    def init_grouping(self, group_method):
        if group_method == UvGroupingMethod.MATERIAL.code:
            self.create_material_map()
            return self.get_face_group_material
            
        if group_method == UvGroupingMethod.MESH.code:
            self.create_mesh_map()
            return self.get_face_group_mesh

        if group_method == UvGroupingMethod.OBJECT.code:
            return self.get_face_group_object

        if group_method == UvGroupingMethod.MANUAL.code:
            self.manual_group_layers = []
            for bm in self.bms:
                self.manual_group_layers.append(self.get_or_create_vcolor_layer(bm, GroupIslandParamInfo))

            return self.get_face_group_manual

        if group_method == UvGroupingMethod.TILE.code:
            return self.get_face_group_tile

        raise RuntimeError('Unexpected grouping method encountered')


    def update_meshes(self):
        for obj in self.objs:
            bmesh.update_edit_mesh(obj.data)

    def face_is_selected(self, bm, uv_layer, f):
        if self.context.tool_settings.use_uv_select_sync:
            return f.select
        else:
            if not f.select:
                return False

            face_selected = True

            for loop in f.loops:
                if not loop[uv_layer].select:
                    face_selected = False
                    break

            return face_selected

    def get_visible_faces(self, bm):
        if self.context.tool_settings.use_uv_select_sync:
            return [f for f in bm.faces if not f.hide]
        else:
            return [f for f in bm.faces if f.select]

    def get_selected_faces(self, bm, uv_layer):
        if self.context.tool_settings.use_uv_select_sync:
            return [f for f in bm.faces if f.select]
        else:
            face_list = []
            for face in bm.faces:
                if not face.select:
                    continue

                face_selected = True

                for loop in face.loops:
                    if not loop[uv_layer].select:
                        face_selected = False
                        break

                if face_selected:
                    face_list.append(face)

            return face_list

    def select_face(self, face, select):
        for v in face.verts:
            v.select = select

        face.select = select

    def select_faces(self, island_faces, select):
        island_faces.sort()

        curr_bm_idx = 0
        curr_bm = self.bms[0]
        curr_uv_layer = self.uv_layers[0]
        curr_face_idx_offset = 0
        next_face_idx_offset = len(self.bms[0].faces)

        for face_idx in island_faces:
            while face_idx >= next_face_idx_offset:
                curr_bm_idx += 1
                next_face_idx_offset += len(self.bms[curr_bm_idx].faces)
                curr_bm = self.bms[curr_bm_idx]
                curr_uv_layer = self.uv_layers[curr_bm_idx]
                curr_face_idx_offset = self.face_idx_offsets[curr_bm_idx]

            orig_face_idx = face_idx - curr_face_idx_offset
            face = curr_bm.faces[orig_face_idx]

            if self.context.tool_settings.use_uv_select_sync:
                self.select_face(face, select)
            else:
                for loop in face.loops:
                    loop[curr_uv_layer].select = select

    def select_island_faces(self, island_idx, island_faces, select):
        bm_idx = self.island_bm_map[island_idx]
        bm = self.bms[bm_idx]
        uv_layer = self.uv_layers[bm_idx]
        face_idx_offset = self.face_idx_offsets[bm_idx]

        if self.context.tool_settings.use_uv_select_sync:
            for face_idx in island_faces:
                orig_face_idx = face_idx - face_idx_offset
                face = bm.faces[orig_face_idx]
                self.select_face(face, select)
        else:
            for face_idx in island_faces:
                orig_face_idx = face_idx - face_idx_offset
                face = bm.faces[orig_face_idx]

                for loop in face.loops:
                    loop[uv_layer].select = select

    def select_island(self, island_idx, select):

        self.select_island_faces(island_idx, self.uv_island_faces_list[island_idx], select)
        
    def select_all_faces(self, select):
        for bm_idx in range(len(self.bms)):
            bm = self.bms[bm_idx]
            uv_layer = self.uv_layers[bm_idx]

            if self.context.tool_settings.use_uv_select_sync:
                for face in bm.faces:
                    self.select_face(face, select)
            else:
                for face in bm.faces:
                    for loop in face.loops:
                        loop[uv_layer].select = select

    def scale_selected_faces(self, scale_factors):
        sx = scale_factors[0]
        sy = scale_factors[1]

        if sx == 1.0 and sy == 1.0:
            return

        for bm_idx in range(len(self.bms)):
            bm = self.bms[bm_idx]
            uv_layer = self.uv_layers[bm_idx]

            selected_faces = self.get_selected_faces(bm, uv_layer)
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv_layer].uv = (loop[uv_layer].uv[0] * sx, loop[uv_layer].uv[1] * sy)

    def transform_island(self, island_idx, matrix):

        bm_idx = self.island_bm_map[island_idx]
        bm = self.bms[bm_idx]
        uv_layer = self.uv_layers[bm_idx]
        face_idx_offset = self.face_idx_offsets[bm_idx]

        island_faces = self.uv_island_faces_list[island_idx]

        for face_idx in island_faces:
            orig_face_idx = face_idx - face_idx_offset
            face = bm.faces[orig_face_idx]
            for loop in face.loops:
                uv = loop[uv_layer].uv
                transformed_uv = matrix @ Vector((uv[0], uv[1], 0.0))
                loop[uv_layer].uv = (transformed_uv[0], transformed_uv[1])

    def apply_pack_solution(self, pack_ratio, pack_solution):

        new_solution_matrices = [None] * len(self.uv_island_faces_list)

        for i_solution in pack_solution.island_solutions:
            
            i_solution.post_scale_offset.x /= pack_ratio
            matrix = Matrix.Translation(i_solution.post_scale_offset)
            matrix = matrix @ Matrix.Scale(1 / i_solution.scale / pack_ratio, 4, (1.0, 0.0, 0.0))
            matrix = matrix @ Matrix.Scale(1 / i_solution.scale, 4, (0.0, 1.0, 0.0))
            matrix = matrix @ Matrix.Translation(i_solution.offset)
            matrix = matrix @ Matrix.Translation(i_solution.pivot)
            matrix = matrix @ Matrix.Rotation(i_solution.angle, 4, 'Z')
            matrix = matrix @ Matrix.Translation(-i_solution.pivot)
            matrix = matrix @ Matrix.Scale(i_solution.pre_scale, 4, (0.0, 1.0, 0.0))
            matrix = matrix @ Matrix.Scale(i_solution.pre_scale, 4, (1.0, 0.0, 0.0))
            matrix = matrix @ Matrix.Scale(pack_ratio, 4, (1.0, 0.0, 0.0))

            new_solution_matrices[i_solution.island_idx] = matrix

            if self.solution_matrices[i_solution.island_idx] is not None:
                matrix = matrix @ self.solution_matrices[i_solution.island_idx].inverted()

            self.solution_matrices[i_solution.island_idx] = None
            self.transform_island(i_solution.island_idx, matrix)

        for island_idx in range(len(self.uv_island_faces_list)):

            if self.solution_matrices[island_idx] is None:
                continue

            self.transform_island(island_idx, self.solution_matrices[island_idx].inverted())

        self.solution_matrices = new_solution_matrices
        self.update_meshes()

    def get_or_create_vcolor_layer(self, bm, param_info):
        
        vcolor_chname = param_info.get_vcolor_chname()
        default_value = param_info.get_default_vcolor()

        if vcolor_chname not in bm.loops.layers.color:
            vcolor_layer = bm.loops.layers.color.new(vcolor_chname)

            for face in bm.faces:
                for loop in face.loops:
                    loop[vcolor_layer] = default_value

        else:
            vcolor_layer = bm.loops.layers.color[vcolor_chname]

        return vcolor_layer

    def set_vcolor(self, param_info, value):

        for bm_idx in range(len(self.bms)):
            bm = self.bms[bm_idx]
            uv_layer = self.uv_layers[bm_idx]

            vcolor_layer = self.get_or_create_vcolor_layer(bm, param_info)

            selected_faces = self.get_selected_faces(bm, uv_layer)
            for face in selected_faces:
                for loop in face.loops:
                    loop[vcolor_layer] = value

    def get_vcolor(self, vcolor_layer, face):

        return face.loops[0][vcolor_layer]

    def set_param(self, param_info, param_value):

        self.set_vcolor(param_info, param_info.param_to_vcolor(param_value))

    def get_param(self, param_info, vcolor_layer, face):

        return param_info.vcolor_to_param(self.get_vcolor(vcolor_layer, face))

    def get_all_param_values(self, param_info):

        output = set()
    
        for bm_idx in range(len(self.bms)):
            bm = self.bms[bm_idx]
            uv_layer = self.uv_layers[bm_idx]

            vcolor_layer = self.get_or_create_vcolor_layer(bm, param_info)

            faces = bm.faces[:]
            for face in faces:
                output.add(self.get_param(param_info, vcolor_layer, face))

        return list(output)

    def handle_invalid_islands(self, invalid_islands):

        self.select_all_faces(False)

        for idx, island_faces in enumerate(self.uv_island_faces_list):
            if idx in invalid_islands:
                self.select_island_faces(idx, island_faces, True)

    def handle_island_flags(self, island_flags):

        overlap_indicies = []
        outside_indicies = []

        for i in range(len(island_flags)):
            overlaps = island_flags[i] & UvPackerIslandFlags.OVERLAPS
            if overlaps > 0:
                overlap_indicies.append(i)

            outside = island_flags[i] & UvPackerIslandFlags.OUTSIDE_TARGET_BOX
            if outside > 0:
                outside_indicies.append(i)

        overlap_detected = len(overlap_indicies) > 0
        outside_detected = len(outside_indicies) > 0

        invalid_detected = overlap_detected or outside_detected
        invalid_indicies = set(overlap_indicies).union(set(outside_indicies))

        if invalid_detected:
            for idx, island_faces in enumerate(self.uv_island_faces_list):
                if idx not in invalid_indicies:
                    self.select_island_faces(idx, island_faces, False)
                else:
                    self.select_island_faces(idx, island_faces, True)

        return overlap_detected, outside_detected