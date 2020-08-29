
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


from .prefs import is_blender28
from .utils import *
from .island_params import *

from mathutils import Vector, Matrix, bvhtree
import bmesh

import time
from collections import defaultdict
from math import sqrt, floor, ceil


def box_collide(box1, box2):
    return not ( box2[0].x > box1[1].x or box2[1].x < box1[0].x or box2[1].y < box1[0].y or box2[0].y > box1[1].y)

def box_center(box):
    return ((box[0].x + box[1].x) / 2.0, (box[0].y + box[1].y) / 2.0)

def box_width(box):
    return abs(box[0].x - box[1].x)

def box_height(box):
    return abs(box[0].y - box[1].y)

def box_contains_box(box_outer, box_inner):
    return\
        box_outer[0].x <= box_inner[0].x and\
        box_outer[0].y <= box_inner[0].y and\
        box_outer[1].x >= box_inner[1].x and\
        box_outer[1].y >= box_inner[1].y

def box_equal(box1, box2):
    eps = 0.0001
    return (box1[0] - box2[0]).length < eps and (box1[1] - box2[1]).length < eps 


class UvIsland:

    NEXT_ISLAND_NUM = 0

    uv_obj = None
    faces = None
    island_num = None
    uv_bm_simple = None
    uv_bm = None
    bvh = None
    overlapping = None
    split_offset = None
    bbox = None
    area = None
    area_3d = None
    param_map = None

    def __init__(self, uv_obj, faces):
        self.uv_obj = uv_obj
        self.faces = faces
        self.param_map = dict()

        self.island_num = UvIsland.NEXT_ISLAND_NUM
        UvIsland.NEXT_ISLAND_NUM += 1


    def create_uv_bm(self, simple):

        if simple:
            if self.uv_bm_simple is not None:
                return

            self.uv_bm_simple = bmesh.new()
            target_bm = self.uv_bm_simple
        else:
            if self.uv_bm is not None:
                return

            self.uv_bm = bmesh.new()
            target_bm = self.uv_bm

        vertlvl_to_bmvert = dict()

        uv_bm_verts = target_bm.verts
        uv_bm_faces = target_bm.faces

        def vertlvl_key(vert_id, lvl):
            return (vert_id, lvl)

        def lvl_to_Z(lvl):
            return 100.0 * float(lvl) + self.island_num * 0.005

        def cantor_pairing(num1, num2):
            sum = num1 + num2
            return (sum + 1) * sum // 2 + num2

        lvl_count = 1 if simple else 2

        if not simple:
            delta = (self.island_num % 5) * 0.00001
            bbox = self.calc_bbox()
            bbox_center = box_center(bbox)
            bbox_center = Vector((bbox_center[0], bbox_center[1], 0.0))

            bbox_width = box_width(bbox)
            bbox_height = box_height(bbox)
            eps = 0.001
            width_multiplier = bbox_width if bbox_width > eps else 1.0
            height_multiplier = bbox_height if bbox_height > eps else 1.0

            matrix = Matrix.Translation(bbox_center)
            matrix = matrix @ Matrix.Scale(1.0 + delta / width_multiplier, 4, (1.0, 0.0, 0.0)) 
            matrix = matrix @ Matrix.Scale(1.0 + delta / height_multiplier, 4, (0.0, 1.0, 0.0)) 
            matrix = matrix @ Matrix.Translation(-bbox_center)

        for face_id in self.faces:
            uv_face = self.uv_obj.face_to_verts[face_id]

            for vert_id in uv_face:

                for lvl in range(lvl_count):
                    key = vertlvl_key(vert_id, lvl)
                    # uv_offset = [0.0, 0.0]

                    if vertlvl_to_bmvert.get(key) is None:

                        # if lvl > 0:
                        #     delta = 1e-6
                        #     hash = cantor_pairing(self.island_num, vert_id) % 4
                        #     axis = hash // 2
                        #     sign = 2*(hash % 2) - 1
                        #     uv_offset[axis] = sign * delta

                        uv = self.uv_obj.uv_tuples[vert_id][0]

                        if not simple:
                            uv = Vector((uv[0], uv[1], 0.0))
                            uv = matrix @ uv

                        uv_bm_verts.new((uv[0], uv[1], lvl_to_Z(lvl)))
                        vertlvl_to_bmvert[key] = len(uv_bm_verts)-1


        uv_bm_verts.ensure_lookup_table()

        def create_bm_face(vid1, vid2):
            bm_face_verts = [
                uv_bm_verts[vertlvl_to_bmvert[vertlvl_key(vid1, 0)]],
                uv_bm_verts[vertlvl_to_bmvert[vertlvl_key(vid2, 0)]],
                uv_bm_verts[vertlvl_to_bmvert[vertlvl_key(vid2, 1)]],
                uv_bm_verts[vertlvl_to_bmvert[vertlvl_key(vid1, 1)]] ]

            try:
                uv_bm_faces.new(bm_face_verts)
            except:
                pass

        for face_id in self.faces:
            uv_face = self.uv_obj.face_to_verts[face_id]

            hori_face_verts1 = []
            hori_face_verts2 = []

            for i in range(len(uv_face)-1):
                vid1 = uv_face[i]
                hori_face_verts1.append(uv_bm_verts[vertlvl_to_bmvert[vertlvl_key(vid1, 0)]])

                if not simple:
                    vid2 = uv_face[i+1]
                    create_bm_face(vid1, vid2)

                    hori_face_verts2.append(uv_bm_verts[vertlvl_to_bmvert[vertlvl_key(vid1, 1)]])

            hori_face_verts1.append(uv_bm_verts[vertlvl_to_bmvert[vertlvl_key(uv_face[-1], 0)]])
            uv_bm_faces.new(hori_face_verts1)

            if not simple:
                create_bm_face(uv_face[0], uv_face[-1])
                hori_face_verts2.append(uv_bm_verts[vertlvl_to_bmvert[vertlvl_key(uv_face[-1], 1)]])
                uv_bm_faces.new(hori_face_verts2)           


    def create_bvh(self, eps):

        if self.bvh is not None:
            return

        self.create_uv_bm(simple=False)

        self.bvh = bvhtree.BVHTree.FromBMesh(self.uv_bm, epsilon=eps)
        self.overlapping = []


    def check_overlap(self, other_island):

        if self == other_island:
            return False

        # if not bbox_collide(self.calc_bbox(), other_island.calc_bbox()):
        #     return False

        if box_equal(self.calc_bbox(), other_island.calc_bbox()):
            return True

        return len(self.bvh.overlap(other_island.bvh)) > 0


    def move(self, offset):

        for face_id in self.faces:
            face = self.uv_obj.bm.faces[face_id]

            for loop in face.loops:
                uv = loop[self.uv_obj.uv_layer].uv
                uv.x += offset[0]
                uv.y += offset[1]


    def scale(self, pivot, scale):
        
        pivot = Vector((pivot[0], pivot[1], 0.0))

        matrix = Matrix.Translation(pivot)
        matrix = matrix @ Matrix.Scale(scale, 4)
        matrix = matrix @ Matrix.Translation(-pivot)

        for face_id in self.faces:
            face = self.uv_obj.bm.faces[face_id]

            for loop in face.loops:
                uv = loop[self.uv_obj.uv_layer].uv
                transformed_uv = matrix @ Vector((uv[0], uv[1], 0.0))
                loop[self.uv_obj.uv_layer].uv = (transformed_uv[0], transformed_uv[1])


    def calc_bbox(self):

        if self.bbox is None:
            x_coords = []
            y_coords = []

            for face_id in self.faces:
                face = self.uv_obj.bm.faces[face_id]
                for loop in face.loops:
                    x_coords.append(loop[self.uv_obj.uv_layer].uv[0])
                    y_coords.append(loop[self.uv_obj.uv_layer].uv[1])

            self.bbox = [Vector((min(x_coords), min(y_coords))), Vector((max(x_coords), max(y_coords)))]

        return self.bbox


    def calc_area(self):

        if self.area is None:

            if self.uv_bm_simple is None:
                self.create_uv_bm(simple=True)

            area = 0.0
            self.uv_bm_simple.faces.ensure_lookup_table()
            
            for face in self.uv_bm_simple.faces:
                area += face.calc_area()

            self.area = area

        return self.area


    def calc_area_3d(self):

        if self.area_3d is None:

            area_3d = 0.0
            faces_3d = self.uv_obj.bm.faces
            faces_3d.ensure_lookup_table()

            for face_id in self.faces:
                area_3d += faces_3d[face_id].calc_area()

            self.area_3d = area_3d

        return self.area_3d


    def calc_border_length(self):

        return self.uv_obj.calc_faces_border_length(self.faces)


    def select(self, select):
        self.uv_obj.select_faces(self.faces, select)


    def get_param(self, param_info):

        param_val = self.param_map.get(param_info.NAME)

        if param_val is None:
            param_val = self.uv_obj.get_param_from_faces(param_info, self.faces)
            self.param_map[param_info.NAME] = param_val


        return param_val
            

    def set_param(self, param_info, param_val):

        self.uv_obj.set_param_to_faces(param_info, self.faces, param_val)
        self.param_map[param_info.NAME] = param_val



class UvObject:

    obj = None
    uv_context = None
    bm = None
    uv_layer = None
    sel_faces = None
    unsel_faces = None
    # face_idx_offset = None
    # vert_idx_offset = None
    islands = None
    unsel_islands = None
    face_to_verts = None
    vert_to_faces = None
    # vert_to_loops = None
    uv_tuples = None


    def __init__(self, uv_context, process_flags, obj=None, bm=None):

        self.obj = obj
        self.uv_context = uv_context
        self.bm = bm if obj is None else bmesh.from_edit_mesh(obj.data)
        self.bm.verts.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()

        self.uv_layer = self.bm.loops.layers.uv.verify()

        self.extract_islands(process_flags)

        # self.face_idx_offset = next_face_idx_offset
        # self.vert_idx_offset = next_vert_idx_offset


    # def next_offsets(self):

    #     next_face_idx_offset = self.face_idx_offset + len(self.bm.faces)
    #     next_vert_idx_offset = self.vert_idx_offset + len(self.bm.verts)

    #     return next_face_idx_offset, next_vert_idx_offset

    def has_islands(self):

        return (self.islands is not None and len(self.islands) > 0) or (self.unsel_islands is not None and len(self.unsel_islands) > 0) 


    def get_visible_faces(self):

        if self.uv_context.context.tool_settings.use_uv_select_sync:
            return [f for f in self.bm.faces if not f.hide]
        else:
            return [f for f in self.bm.faces if f.select]


    def update_faces(self):

        self.sel_faces = []
        self.unsel_faces = []

        visible_faces = self.get_visible_faces()

        for face in visible_faces:

            if self.uv_context.context.tool_settings.use_uv_select_sync:
                face_selected = face.select
            else:
                face_selected = True

                for loop in face.loops:
                    if not loop[self.uv_layer].select:
                        face_selected = False
                        break

            if face_selected:
                self.sel_faces.append(face)
            else:
                self.unsel_faces.append(face)


    def extract_island(self, face_id, faces_left, island_faces):

        faces_left.remove(face_id)
        faces_to_process = [face_id]

        while len(faces_to_process) > 0:
            new_face_id = faces_to_process.pop(0)
            island_faces.add(new_face_id)

            for v in self.face_to_verts[new_face_id]:

                connected_faces = self.vert_to_faces[v]
                if connected_faces:
                    for cf in connected_faces:
                        if cf in faces_left:
                            faces_left.remove(cf)
                            faces_to_process.append(cf)


    def extract_islands_from_faces(self, faces):

        extract_start_time = time.time()

        def get_uv_tuple_from_loop(l):
            return (l[self.uv_layer].uv.to_tuple(5), l.vert.index)

        uv_tuple_to_vert_id = dict()
        faces_left = set()

        for f in faces:
            faces_left.add(f.index)
            
            for l_idx, l in enumerate(f.loops):
                uv_tuple = get_uv_tuple_from_loop(l)
                vert_id = uv_tuple_to_vert_id.get(uv_tuple)

                if vert_id is None:
                    self.vert_to_faces.append(set())
                    # self.vert_to_loops.append(list())
                    self.uv_tuples.append(uv_tuple)

                    vert_id = len(self.vert_to_faces) - 1
                    uv_tuple_to_vert_id[uv_tuple] = vert_id

                self.face_to_verts[f.index].append(vert_id)
                self.vert_to_faces[vert_id].add(f.index)
                # self.vert_to_loops[vert_id].append(l)

        islands = []
        
        while len(faces_left) > 0:
            current_island_faces = set()

            face_id = list(faces_left)[0]
            self.extract_island(face_id, faces_left, current_island_faces)
            islands.append(UvIsland(self, current_island_faces))

        if in_debug_mode():
            print('Island extracting time: ' + str(time.time() - extract_start_time))

        return islands
      

    def extract_islands(self, process_flags):

        self.update_faces()

        self.face_to_verts = defaultdict(list)
        self.vert_to_faces = []
        # self.vert_to_loops = []
        self.uv_tuples = []

        if process_flags.selected:
            self.islands = self.extract_islands_from_faces(self.sel_faces)

        if process_flags.unselected:
            self.unsel_islands = self.extract_islands_from_faces(self.unsel_faces)


    def coord_minmax(self, coord):

        coords = [uv_tuple[0][coord] for uv_tuple in self.uv_tuples]
        return (min(coords), max(coords))


    def calc_faces_border_length(self, faces):

        edge_face_count = defaultdict(lambda: 0)

        for face_id in faces:
            uv_face = self.face_to_verts[face_id]

            for i in range(len(uv_face)-1):
                vid1 = uv_face[i]
                vid2 = uv_face[i+1]

                v_pair = (min(vid1, vid2), max(vid1, vid2))
                edge_face_count[v_pair] += 1

            vid1 = uv_face[0]
            vid2 = uv_face[-1]

            v_pair = (min(vid1, vid2), max(vid1, vid2))
            edge_face_count[v_pair] += 1

        result = 0.0
        for v_pair, face_count in edge_face_count.items():
            if face_count == 1:
                uv_tuple1 = self.uv_tuples[v_pair[0]]
                uv_tuple2 = self.uv_tuples[v_pair[1]]
                result += (Vector((uv_tuple1[0][0], uv_tuple1[0][1])) - Vector((uv_tuple2[0][0], uv_tuple2[0][1]))).length

        return result


    def select_face(self, face, select):

        if self.uv_context.context.tool_settings.use_uv_select_sync:
            for v in face.verts:
                v.select = select

            face.select = select
        else:
            for loop in face.loops:
                loop[self.uv_layer].select = select


    def select_faces(self, faces, select):

        self.bm.faces.ensure_lookup_table()

        for face_id in faces:
            face = self.bm.faces[face_id]
            self.select_face(face, select)


    def set_vcolor_to_face(self, param_layer, face, vcolor_val):

        for loop in face.loops:
            loop[param_layer] = vcolor_val


    def get_vcolor_from_face(self, param_layer, face):

        return face.loops[0][param_layer]


    def get_param_layer(self, param_info, create=False):
        
        if param_info.get_vcolor_chname() in self.bm.loops.layers.color:
            return self.bm.loops.layers.color[param_info.get_vcolor_chname()]

        if not create:
            raise IslandParamError('Invalid param requested')

        param_layer = self.bm.loops.layers.color.new(param_info.get_vcolor_chname())
        default_vcolor = param_info.get_default_vcolor()

        for face in self.bm.faces:
            self.set_vcolor_to_face(param_layer, face, default_vcolor)

        return param_layer


    def get_param_from_faces(self, param_info, faces):

        param_layer = self.get_param_layer(param_info)

        self.bm.faces.ensure_lookup_table()
        vcolor_val = self.get_vcolor_from_face(param_layer, self.bm.faces[next(iter(faces))])

        for face_id in faces:
            face = self.bm.faces[face_id]

            if vcolor_val != self.get_vcolor_from_face(param_layer, face):
                raise IslandParamError('Inconsistent island param value')

        return param_info.vcolor_to_param(vcolor_val)


    def set_param_to_faces(self, param_info, faces, param_val):

        param_layer = self.get_param_layer(param_info, create=True)
        vcolor_val = param_info.param_to_vcolor(param_val)

        self.bm.faces.ensure_lookup_table()
        for face_id in faces:
            face = self.bm.faces[face_id]

            self.set_vcolor_to_face(param_layer, face, vcolor_val)


class UvSelectionProcessFlags:

    selected = None
    unselected = None

    def __init__(self, selected=True, unselected=False):
        self.selected = selected
        self.unselected = unselected

    def enabled(self):
        return self.selected or self.unselected


class UvContext:

    context = None
    uv_objects = None
    islands = None
    unsel_islands = None
    overlap_groups = None
    next_overlap_group_num = None

    def __init__(self, context, process_flags):
        self.context = context

        if is_blender28():
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

        else:
            objs = [self.context.active_object]

        self.uv_objects = []

        for obj in objs:
            uv_obj = UvObject(self, process_flags, obj=obj)

            if uv_obj.has_islands():
                self.uv_objects.append(uv_obj)

        # Collect islands
        if process_flags.selected:
            self.islands = []
            for uv_obj in self.uv_objects:
                self.islands += uv_obj.islands

        if process_flags.unselected:
            self.unsel_islands = []

            for uv_obj in self.uv_objects:
                self.unsel_islands += uv_obj.unsel_islands


    def uv_obj_from_box(self, box):

        bm = bmesh.new()

        verts = []
        verts.append(bm.verts.new((0.0, 0.0, 0.0)))
        verts.append(bm.verts.new((1.0, 0.0, 0.0)))
        verts.append(bm.verts.new((1.0, 1.0, 0.0)))
        verts.append(bm.verts.new((0.0, 1.0, 0.0)))

        bm.verts.ensure_lookup_table()

        for vert in verts:
            vert.select = True

        bm.faces.new(verts)

        bm.faces.ensure_lookup_table()
        face = bm.faces[0]
        face.select = True

        uv_layer = bm.loops.layers.uv.new('tmpUV')
        uv_verts = []
        uv_verts.append(box[0])
        uv_verts.append((box[0].x, box[1].y))
        uv_verts.append(box[1])
        uv_verts.append((box[1].x, box[0].y))

        for idx, loop in enumerate(face.loops):
            loop[uv_layer].uv = uv_verts[idx]
            loop[uv_layer].select = True

        uv_obj = UvObject(self, UvSelectionProcessFlags(), obj=None, bm=bm)
        uv_obj.islands[0].bbox = box

        return uv_obj


    # def extract_islands(self):
        
    #     for uv_obj in self.uv_objects:
    #         uv_obj.extract_islands()


    def update_meshes(self):
        for uv_obj in self.uv_objects:
            bmesh.update_edit_mesh(uv_obj.obj.data)


    def island_count(self):
        return len(self.islands)


    def coord_minmax(self, coord):

        minmax_array = [uv_obj.coord_minmax(coord) for uv_obj in self.uv_objects]
        return (min([minmax[0] for minmax in minmax_array]), max([minmax[1] for minmax in minmax_array]))


    def handle_overlapping_islands(self, island1, island2):

        island1.overlapping.append(island2)
        island2.overlapping.append(island1)


    def detect_overlap_islands(self, eps):

        for island in self.islands:
            island.create_bvh(eps)

        for i in range(len(self.islands)):
            island = self.islands[i]

            for j in range(i+1, len(self.islands)):
                other_island = self.islands[j]
                
                if island.check_overlap(other_island):
                    self.handle_overlapping_islands(island, other_island)


    def split_overlapping_islands(self):
        
        # Get x coords
        x_minmax = self.coord_minmax(0)
        offset_step = max(int(ceil(x_minmax[1])) - int(floor(x_minmax[0])), 1)

        islands_moved = 0
        max_offset = 0

        islands_sorted = self.islands[:]
        islands_sorted.sort(key=lambda island: len(island.overlapping))

        for island in islands_sorted:

            free_offset = None
            offset_to_check = 0

            while free_offset is None:

                offset_found = True

                for other_island in island.overlapping:
                    if other_island.split_offset is not None and other_island.split_offset == offset_to_check:
                        offset_found = False
                        break

                if offset_found:
                    free_offset = offset_to_check
                else:
                    offset_to_check += offset_step

            max_offset = max(max_offset, free_offset)
            island.split_offset = free_offset

            if island.split_offset != 0:
                island.move((island.split_offset, 0.0))
                islands_moved += 1

        if max_offset <= SplitOffsetParamInfo.MAX_VALUE:
            undo_possible = True
            for island in self.islands:
                island.set_param(SplitOffsetParamInfo, island.split_offset)

        else:
            undo_possible = False
            for island in self.islands:
                island.set_param(SplitOffsetParamInfo, SplitOffsetParamInfo.INVALID_VALUE)

        return (islands_moved, undo_possible)


    def undo_island_split(self):

        try:
            for island in self.islands:
                split_offset = island.get_param(SplitOffsetParamInfo)

                if split_offset == SplitOffsetParamInfo.INVALID_VALUE:
                    raise IslandParamError('Invalid value found')

        except IslandParamError:
            raise RuntimeError('Undo not possible (split data not found)')
        except:
            raise

        islands_moved = 0

        for island in self.islands:

            split_offset = island.get_param(SplitOffsetParamInfo)
            if split_offset != 0:
                island.move((-split_offset, 0.0))
                islands_moved += 1

            island.set_param(SplitOffsetParamInfo, SplitOffsetParamInfo.INVALID_VALUE)

        return islands_moved


    def adjust_scale_to_unselected(self):

        eps = 0.0001
        avg_scale_ratio = 0.0

        valid_count = 0

        for island in self.unsel_islands:
            area = island.calc_area()
            area_3d = island.calc_area_3d()

            if area < eps or area_3d < eps:
                continue

            ratio = area_3d / area
            avg_scale_ratio += ratio

            valid_count += 1

        if valid_count == 0:
            raise RuntimeError('No valid unselected island found')

        avg_scale_ratio /= valid_count

        for island in self.islands:
            area = island.calc_area()
            area_3d = island.calc_area_3d()

            if area < eps or area_3d < eps:
                continue

            scale = sqrt(area_3d / avg_scale_ratio / area)
            island.scale(box_center(island.calc_bbox()), scale)


    def debug_islands(self):

        bbox_dims = [box_width(island.calc_bbox()) for island in self.islands]
        bbox_dims += [box_height(island.calc_bbox()) for island in self.islands]

        max_bbox_dim = max(bbox_dims)

        border_len = 0.0
        for island in self.islands:
            border_len += island.calc_border_length()

        print('[DEBUG ISLANDS]:')
        print('Max bbox dimension: ' + str(max_bbox_dim))
        print('Border length: ' + str(border_len))
        print('[DEBUG ISLAND END]')


    def find_islands_inside_box(self, box, islands, fully_inside):

        output = []
        not_fully_inside = []

        for island in islands:
            if box_contains_box(box, island.calc_bbox()):
                output.append(island)
            else:
                not_fully_inside.append(island)

        if not fully_inside:

            box_obj = self.uv_obj_from_box(box)
            box_island = box_obj.islands[0]
            box_island.create_bvh(0.0)

            for island in not_fully_inside:
                island.create_bvh(0.0)

                if box_island.check_overlap(island):
                    output.append(island)

        return output


    def select_islands(self, islands, select):

        for island in islands:
            island.select(select)
