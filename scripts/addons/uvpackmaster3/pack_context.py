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
from .utils import *

import time
import struct 


from mathutils import Vector, Matrix
import bmesh


class UvMod:

    def __init__(self, p_island):

        self.p_island = p_island

    def restore_orig_uvs(self):

        if self.p_island._transform_stored is not None:
            tranform_stored_inverted = self.p_island._transform_stored.inverted()
            self.p_island.transform(tranform_stored_inverted)
            self.p_island._transform_stored = None

    def pre_apply(self):
        pass

    def post_apply(self):
        pass


class UvModTransform(UvMod):

    def __init__(self, p_island, transform):
        super().__init__(p_island)

        self.orig_transform = transform
        self.transform = transform

    def restore_orig_uvs(self):
        pass

    def pre_apply(self):

        if self.p_island._transform_stored is not None:
            tranform_stored_inverted = self.p_island._transform_stored.inverted()
            self.transform = self.transform @ tranform_stored_inverted

    def apply(self):

        self.p_island.transform(self.transform)

    def post_apply(self):

        self.p_island._transform_stored = self.orig_transform
    

class UvModVerticesGeneric(UvMod):

    # def __init__(self, p_island):
    #     super().__init__(p_island)

    def pre_apply(self):
        
        self.p_island.orig_vert_map() # Force saving orig vert map before modification

    def post_apply(self):
        
        self.p_island._vert_modified = True


class UvModVertexMap(UvModVerticesGeneric):

    def __init__(self, p_island, vert_map):
        super().__init__(p_island)

        self.vert_map = vert_map

    def apply(self):

        self.p_island.apply_vert_map(self.vert_map)

        
class UvModOutVertices(UvModVerticesGeneric):

    def __init__(self, p_island, face_order, vertices):
        super().__init__(p_island)

        self.face_order = face_order
        self.vertices = vertices

    def apply(self):

        loc_face_order = self.p_island.to_loc_face_indices(self.face_order)

        v_idx = 0
        for face_idx in loc_face_order:
            face = self.p_island.p_obj.bm.faces[face_idx]

            for loop in face.loops:
                loop[self.p_island.p_obj.uv_layer].uv = (self.vertices[v_idx][0], self.vertices[v_idx][1])
                v_idx += 1

        assert(v_idx == len(self.vertices))



class PackIsland:

    p_obj = None
    face_indices = None
    faces = None
    iparam_values = None
    __overlay = None
    __bbox = None

    __orig_vert_map = None
    _vert_modified = False
    _transform_stored = None

    flags = 0

    def __init__(self, p_obj, face_indices, selected):
        self.p_obj = p_obj
        self.flags = UvpmIslandFlags.SELECTED if selected else 0

        self.face_indices = self.to_loc_face_indices(face_indices)
        self.faces = [self.p_obj.bm.faces[face_idx] for face_idx in self.face_indices]

    def to_loc_face_indices(self, face_indices):
        return self.p_obj.to_loc_face_indices(face_indices)

    def calc_bbox(self):

        x_coords = []
        y_coords = []

        for face_idx in self.face_indices:
            face = self.p_obj.bm.faces[face_idx]
            for loop in face.loops:
                x_coords.append(loop[self.p_obj.uv_layer].uv[0])
                y_coords.append(loop[self.p_obj.uv_layer].uv[1])

        return [Vector((min(x_coords), min(y_coords))), Vector((max(x_coords), max(y_coords)))]

    def bbox(self):

        if self.__bbox is None:
            self.__bbox = self.calc_bbox()

        return self.__bbox

    def register_overlay(self, overlay):

        self.__overlay = overlay

    def overlay(self):

        if self.__overlay is not None:
            bbox = self.bbox()
            self.__overlay.set_coords((bbox[0] + bbox[1]) / 2.0)
        
        return self.__overlay

    def iparam_value(self, iparam_info):

        return self.iparam_values[iparam_info.index()]

    def save_iparam(self, iparam_info):

        self.p_obj.save_iparam(iparam_info, self.iparam_value(iparam_info), self.faces)

    def select_faces(self, island_faces, select):

        if self.p_obj.p_context.context.tool_settings.use_uv_select_sync:
            for face_idx in island_faces:
                face = self.p_obj.bm.faces[face_idx]
                PackContext.select_face(face, select)
        else:
            for face_idx in island_faces:
                face = self.p_obj.bm.faces[face_idx]

                for loop in face.loops:
                    loop[self.p_obj.uv_layer].select = select

    def select(self, select):

        self.select_faces(self.face_indices, select)

    def transform(self, matrix):

        for face_idx in self.face_indices:
            face = self.p_obj.bm.faces[face_idx]
            for loop in face.loops:
                uv = loop[self.p_obj.uv_layer].uv
                transformed_uv = matrix @ Vector((uv[0], uv[1], 1.0))
                loop[self.p_obj.uv_layer].uv = (transformed_uv[0] / transformed_uv[2], transformed_uv[1] / transformed_uv[2])

    def apply_vert_map(self, vert_map):

        for face_idx, verts in vert_map.items():
            face = self.p_obj.bm.faces[face_idx]
            assert(len(face.loops) == len(vert_map))

            loop_idx = 0
            for loop in face.loops:
                loop[self.p_obj.uv_layer].uv = (verts[loop_idx][0], verts[loop_idx][1])

    def orig_vert_map(self):

        if self.__orig_vert_map is not None:
            return self.__orig_vert_map

        assert(not self._vert_modified)
        assert(self._transform_stored is None)

        __orig_vert_map = dict()
        for face_idx in self.face_indices:
            verts = []

            face = self.p_obj.bm.faces[face_idx]
            for loop in face.loops:
                uv = loop[self.p_obj.uv_layer].uv
                verts.append((uv[0], uv[1]))

            __orig_vert_map[face_idx] = verts

        self.__orig_vert_map = __orig_vert_map
        return self.__orig_vert_map

    def restore_orig_uvs(self, uv_mod):

        if self._vert_modified:
            assert(self._transform_stored is None)
            self.apply_vert_map(self.orig_vert_map())
            self._vert_modified = False
            return

        uv_mod.restore_orig_uvs()

    def modify_uvs(self, uv_mod):

        assert(self is uv_mod.p_island)
        self.restore_orig_uvs(uv_mod)

        uv_mod.pre_apply()
        uv_mod.apply()
        uv_mod.post_apply()

        self.__bbox = None

    def apply_out_island(self, out_island):

        if out_island.transform is not None:
            self.modify_uvs(UvModTransform(self, out_island.transform))

        if out_island.iparam_values is not None:
            self.iparam_values = out_island.iparam_values

        if out_island.flags is not None:
            old_flags = self.flags
            new_flags = out_island.flags

            old_selected = (old_flags & UvpmIslandFlags.SELECTED) > 0
            new_selected = (new_flags & UvpmIslandFlags.SELECTED) > 0

            if old_selected != new_selected:
                self.select(new_selected)

            self.flags = new_flags

        if out_island.vertices is not None:
            assert(out_island.face_order is not None)

            self.modify_uvs(UvModOutVertices(self, out_island.face_order, out_island.vertices))




class PackObject:

    obj = None
    bm = None
    uv_layer = None
    face_idx_offset = None
    vert_idx_offset = None

    def __init__(self, p_context, obj, next_face_idx_offset, next_vert_idx_offset):
        self.p_context = p_context
        self.obj = obj
        self.bm = bmesh.from_edit_mesh(self.obj.data)
        self.bm.verts.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()

        self.uv_layer = self.bm.loops.layers.uv.verify()

        self.face_idx_offset = self.next_face_idx_offset = next_face_idx_offset
        self.vert_idx_offset = self.next_vert_idx_offset = next_vert_idx_offset

        self.next_face_idx_offset += len(self.bm.faces)
        self.next_vert_idx_offset += len(self.bm.verts)

    def to_loc_face_idx(self, glob_face_idx):
        return glob_face_idx - self.face_idx_offset

    def to_loc_face_indices(self, face_indices):
        return [self.to_loc_face_idx(glob_face_idx) for glob_face_idx in face_indices]

    def to_glob_face_idx(self, loc_face_idx):
        return loc_face_idx + self.face_idx_offset

    def get_selected_faces(self):
        if self.p_context.context.tool_settings.use_uv_select_sync:
            return [f for f in self.bm.faces if f.select]
        else:
            face_list = []
            for face in self.bm.faces:
                if not face.select:
                    continue

                face_selected = True

                for loop in face.loops:
                    if not loop[self.uv_layer].select:
                        face_selected = False
                        break

                if face_selected:
                    face_list.append(face)

            return face_list

    def get_visible_faces(self):
        if self.p_context.context.tool_settings.use_uv_select_sync:
            return [f for f in self.bm.faces if not f.hide]
        else:
            return [f for f in self.bm.faces if f.select]

    def face_is_selected(self, f):
        if self.p_context.context.tool_settings.use_uv_select_sync:
            return f.select
        else:
            if not f.select:
                return False

            face_selected = True

            for loop in f.loops:
                if not loop[self.uv_layer].select:
                    face_selected = False
                    break

            return face_selected

    def get_or_create_vcolor_layer(self, iparam_info):
        
        # MUSTDO: implement layer caching
        vcolor_chname = iparam_info.get_vcolor_chname()
        default_value = iparam_info.get_default_vcolor()

        layer_container = PackContext.get_vcolor_layer_container(self.bm)
        if vcolor_chname not in layer_container:
            vcolor_layer = layer_container.new(vcolor_chname)

            for face in self.bm.faces:
                PackContext.set_vcolor(vcolor_layer, face, default_value)

        else:
            vcolor_layer = layer_container[vcolor_chname]

        return vcolor_layer

    # def set_vcolor(self, iparam_info, value, faces=None):

    #     vcolor_layer = self.get_or_create_vcolor_layer(iparam_info)

    #     if faces is None:
    #         faces = self.get_selected_faces()
    #     for face in faces:
    #         for loop in face.loops:
    #             loop[vcolor_layer] = value

    def save_iparam(self, iparam_info, iparam_value, faces=None):

        vcolor_layer = self.get_or_create_vcolor_layer(iparam_info)
        value = iparam_info.param_to_vcolor(iparam_value)
        
        if faces is None:
            faces = self.get_selected_faces()

        for face in faces:
            PackContext.set_vcolor(vcolor_layer, face, value)

    def load_all_iparam_values(self, iparam_info):

        output = set()

        vcolor_layer = self.get_or_create_vcolor_layer(iparam_info)
        faces = self.bm.faces[:]

        for face in faces:
            output.add(PackContext.load_iparam(iparam_info, vcolor_layer, face))

        return output


class PackContext:

    @classmethod
    def get_vcolor_layer_container(cls, bm):
        return bm.loops.layers.color

    @classmethod
    def get_vcolor(cls, vcolor_layer, face):

        return face.loops[0][vcolor_layer]

    @classmethod
    def set_vcolor(cls, vcolor_layer, face, value):

        for loop in face.loops:
            loop[vcolor_layer] = value

    @classmethod
    def load_iparam(cls, iparam_info, vcolor_layer, face):

        return iparam_info.vcolor_to_param(cls.get_vcolor(vcolor_layer, face))

    @classmethod
    def select_face(cls, face, select):
        for v in face.verts:
            v.select = select

        face.select = select

    def __init__(self, _context):

        self.iparam_array = [None] * UvpmIslandIntParams.MAX_COUNT
        self.iparam_name_to_index = dict()

        self.context = _context

        objs = []

        for obj in self.context.selected_objects:

            if obj.type != 'MESH':
                continue

            already_added = False
            for obj2 in objs:
                if obj.data == obj2.data:
                    already_added = True
                    break

            if not already_added:
                objs.append(obj)


        if self.context.active_object.type == 'MESH':
            active_added = False

            for obj2 in objs:
                if self.context.active_object.data == obj2.data:
                    active_added = True
                    break

            if not active_added:
                objs.append(self.context.active_object)

        next_face_idx_offset = 0
        next_vert_idx_offset = 0
        self.p_objects = []

        for obj in objs:
            p_obj = PackObject(self, obj, next_face_idx_offset, next_vert_idx_offset)
            next_face_idx_offset = p_obj.next_face_idx_offset
            next_vert_idx_offset = p_obj.next_vert_idx_offset
            self.p_objects.append(p_obj)

        self.total_face_count = next_face_idx_offset
        self.p_islands = None

    def register_iparam(self, iparam_info, param_index=None):

        old_index = self.iparam_name_to_index.get(iparam_info.script_name)

        if old_index is not None:
            if param_index is not None and old_index != param_index:
                raise ValueError()

            iparam_info.INDEX = old_index
            return

        if param_index is not None:
            if self.iparam_array[param_index] is not None:
                raise ValueError()
        else:
            try:
                param_index = next(idx for idx, entry in enumerate(self.iparam_array) if entry is None)
            except StopIteration:
                raise RuntimeError('Maximal number of island parameters exceeded')

        assert(self.iparam_array[param_index] is None)
        self.iparam_array[param_index] = iparam_info
        self.iparam_name_to_index[iparam_info.script_name] = param_index
        iparam_info.INDEX = param_index

    def get_iparam_info(self, param_index):

        iparam_info = self.iparam_array[param_index]
        if iparam_info is None:
            raise ValueError()

        assert(iparam_info.index() == param_index)
        return iparam_info

    def serialize_uv_maps(self, send_unselected, send_verts_3d, iparam_serializers):

        serialize_start = time.time()
        serialized_maps = bytes()
        selected_cnt = 0
        unselected_cnt = 0

        face_id_len_array = []
        uv_coord_array = []
        vert_idx_array = []
    
        serialization_flags = 0

        if send_unselected:
            serialization_flags |= UvpmMapSerializationFlags.CONTAINS_FLAGS
            face_flags_array = []

        if send_verts_3d:

            serialization_flags |= UvpmMapSerializationFlags.CONTAINS_VERTS_3D
            verts_3d_array = []

        for idx, ip_serializer in enumerate(iparam_serializers):

            ip_serializer.init_context(self)
            assert(ip_serializer.iparam_info.index() == idx)

        for p_obj_idx, p_obj in enumerate(self.p_objects):
            faces = p_obj.get_visible_faces() if send_unselected else p_obj.get_selected_faces()
            
            for face in faces:
                face_id_len_array.append(face.index + p_obj.face_idx_offset)
                face_id_len_array.append(len(face.verts))

                face_selected = True

                if send_unselected:
                    face_selected = p_obj.face_is_selected(face)
                    face_flags = 0

                    if face_selected:
                        face_flags |= UvpmFaceInputFlags.SELECTED
                        selected_cnt += 1
                    else:
                        unselected_cnt += 1

                    face_flags_array.append(face_flags)
                else:
                    selected_cnt += 1

                for ip_serializer in iparam_serializers:

                    ip_serializer.serialize_iparam(p_obj_idx, p_obj, face)


                for loop in face.loops:
                    uv = loop[p_obj.uv_layer].uv.to_tuple(5)
                    uv_coord_array.append(uv[0])
                    uv_coord_array.append(uv[1])
                    vert_idx_array.append(loop.vert.index + p_obj.vert_idx_offset)

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

        if (serialization_flags & UvpmMapSerializationFlags.CONTAINS_VERTS_3D) > 0:
            serialized_maps += struct.pack('f' * len(verts_3d_array), *verts_3d_array)

        if (serialization_flags & UvpmMapSerializationFlags.CONTAINS_FLAGS) > 0:
            serialized_maps += struct.pack('i' * len(face_flags_array), *face_flags_array)

        serialized_maps += struct.pack('i', len(iparam_serializers))

        from .island_params import IParamInfo

        for idx, ip_serializer in enumerate(iparam_serializers):
            serialized_maps += ip_serializer.iparam_info.serialize()
            iparam_values = ip_serializer.iparam_values
            serialized_maps += struct.pack(IParamInfo.PARAM_TYPE_MARK * len(iparam_values), *iparam_values)

        if in_debug_mode():
            print('UVPM serialization time: ' + str(time.time() - serialize_start))

        return serialized_maps, selected_cnt, unselected_cnt

    def islands_received(self):

        return self.p_islands is not None

    def set_islands(self, selected_count, islands):
        if selected_count > len(islands):
            raise RuntimeError('Unexpected output from the UVPM process')

        p_islands = []
        curr_obj_idx = 0

        for island_idx in range(selected_count):
            island_faces = islands[island_idx]

            next_obj_idx = curr_obj_idx + 1
            while next_obj_idx < len(self.p_objects) and self.p_objects[next_obj_idx].face_idx_offset <= island_faces[0]:
                curr_obj_idx = next_obj_idx
                next_obj_idx += 1

            p_islands.append(PackIsland(self.p_objects[curr_obj_idx], island_faces, selected=True))

        curr_obj_idx = 0
        for island_idx in range(selected_count, len(islands)):
            island_faces = islands[island_idx]

            next_obj_idx = curr_obj_idx + 1
            while next_obj_idx < len(self.p_objects) and self.p_objects[next_obj_idx].face_idx_offset <= island_faces[0]:
                curr_obj_idx = next_obj_idx
                next_obj_idx += 1

            p_islands.append(PackIsland(self.p_objects[curr_obj_idx], island_faces, selected=False))

        self.p_islands = p_islands

    def update_meshes(self):

        if self.context.mode != 'EDIT_MESH':
            return

        for p_obj in self.p_objects:
            bmesh.update_edit_mesh(p_obj.obj.data)
        
    def select_all_faces(self, select):

        for p_obj in self.p_objects:

            # MUSTDO: refactor this
            if self.context.tool_settings.use_uv_select_sync:
                for face in p_obj.bm.faces:
                    PackContext.select_face(face, select)
            else:
                for face in p_obj.bm.faces:
                    for loop in face.loops:
                        loop[p_obj.uv_layer].select = select

    def scale_selected_faces(self, scale_factors):

        sx = scale_factors[0]
        sy = scale_factors[1]

        if sx == 1.0 and sy == 1.0:
            return

        for p_obj in self.p_objects:

            selected_faces = p_obj.get_selected_faces()
            for face in selected_faces:
                for loop in face.loops:
                    loop[p_obj.uv_layer].uv = (loop[p_obj.uv_layer].uv[0] * sx, loop[p_obj.uv_layer].uv[1] * sy)

    def apply_out_islands(self, out_islands):

        dirty_iparams = [self.get_iparam_info(param_index) for param_index in out_islands.dirty_iparam_indices]

        for out_island in out_islands.islands:
            p_island = self.p_islands[out_island.idx]
            p_island.apply_out_island(out_island)

            for iparam_info in dirty_iparams:
                p_island.save_iparam(iparam_info)


    # def set_vcolor(self, iparam_info, value):

    #     for p_obj in self.p_objects:
    #         p_obj.set_vcolor(iparam_info, value)

    def save_iparam(self, iparam_info, iparam_value):

        # self.set_vcolor(iparam_info, iparam_info.param_to_vcolor(iparam_value))
        for p_obj in self.p_objects:
            p_obj.save_iparam(iparam_info, iparam_value)

    def load_all_iparam_values(self, iparam_info):

        output = set()
    
        for p_obj in self.p_objects:
            output = output.union(p_obj.load_all_iparam_values(iparam_info))

        return list(output)
