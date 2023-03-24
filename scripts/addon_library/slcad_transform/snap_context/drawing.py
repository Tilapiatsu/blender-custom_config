# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact for more information about the Addon:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

# import bgl
import gpu
import numpy as np
from mathutils.geometry import interpolate_bezier
from mathutils import Matrix
import bmesh
import time

# Mesh / curve
TYP_OBJ = 1
TYP_ORIGIN = 2
TYP_BOUNDS = 4
TYP_INSTANCE = 8

USE_PRIMITIVE_BUFFER = True

vert_3d = '''
uniform mat4 MVP;

in vec3 pos;
in float primitive_id;
out float primitive_id_var;

void main()
{
    
    primitive_id_var = primitive_id;
    gl_Position = MVP * vec4(pos, 1.0);
    
}
'''

primitive_id_frag = '''
uniform float offset;

in float primitive_id_var;
out vec4 FragColor;

vec4 cast_to_4_bytes(float f){
    vec4 color;
    color.a = float(int(f)%256);
    color.b = float(int(f/256)%256); 
    color.g = float(int(f/65536)%256);
    color.r = float(int(f/16581376)%256);
    return color / 255.0;
}

void main()
{
    FragColor = cast_to_4_bytes(offset + primitive_id_var);
}
'''

gl_version = '''
#version 330
'''

def interp_bezier(p0, p1, segs, resolution):
    """
     Bezier curve approximation
    """
    if (resolution == 0 or
            (p0.handle_right_type == 'VECTOR' and
             p1.handle_left_type == 'VECTOR')):
        segs.append(p0.co[0:3])

    else:
        seg = interpolate_bezier(p0.co,
                                 p0.handle_right,
                                 p1.handle_left,
                                 p1.co,
                                 resolution + 1)
        segs.extend([p[0:3] for p in seg[:-2]])


def get_bmesh_loose_edges(bm):
    # TODO: handle "visible" state
    edges_co = []
    for ed in bm.edges:
        if ed.is_wire:
            edges_co.extend([ed.verts[0].co, ed.verts[1].co])
    if len(edges_co) > 0:
        return edges_co
    return None

def get_bmesh_loose_verts(bm):
    # TODO: handle "visible" state
    pos = [v.co for v in bm.verts if v.is_wire]
    if len(pos) > 0:
        return pos
    return None


def get_bmesh_edges(bm):
    edges_co = [v.co for v in bm.verts]
    edges_indexes = [[ed.verts[0].index, ed.verts[1].index] for ed in bm.edges]
    if len(edges_co) > 0:
        return edges_co, edges_indexes
    return None, None


def get_bmesh_verts(bm):
    pos = [v.co for v in bm.verts]
    if len(pos) > 0:
        return pos
    return None


def get_bmesh_faces(bm):
    # must triangulate !
    faces = bm.calc_loop_triangles()
    # each face is a triangle, with a ref to source face
    faces_tris = {f.index: [[]] for f in bm.faces}
    faces_center_normal = []
    for loop in faces:
        for l in loop:
            i = l.face.index
            if len(faces_tris[i][-1]) == 3:
                faces_tris[i].append([])
            if (faces_tris[i][-1]) == 0:
                faces_center_normal.append(l.face.center)
                faces_center_normal.append(l.face.normal)
            faces_tris[i][-1].append(l.vert.index)

    # same as vertex cos
    faces_co = [v.co for v in bm.verts]
    # array of array of tris for each face
    faces_indexes = [[tri for tri in faces_tris[f.index]] for f in bm.faces]
    # provide index for each triangle ?
    # primitive_ids = [[f.index for tri in faces_tris[f.index]] for f in bm.faces]
    # provide index for each vertex ??
    # primitive_ids = [[f.index] * 3 for f in bm.faces for tri in faces_tris[f.index]]
    if len(faces_co) > 0:
        return faces_co, faces_indexes, faces_center_normal
    return None, None, None


def get_curve_arrays(curve):
    # ~0.1s / 100k pts on POLY
    t = time.time()
    segs = []
    pos = []
    k0 = 0
    for i, spl in enumerate(curve.splines):
        # limited support for nurbs
        if spl.type in {'POLY', 'NURBS'}:
            if len(spl.points) < 2:
                continue
            pos.extend([p.co[0:3] for p in spl.points])
        elif spl.type == 'BEZIER':
            pts = spl.bezier_points
            # limit resolution on huge curves
            if len(pts) < 2:
                continue
            elif len(pts) > 500:
                resolution = 0
            else:
                resolution = curve.resolution_u
            for j, p1 in enumerate(pts[1:]):
                interp_bezier(pts[j], p1, pos, resolution)
            if spl.use_cyclic_u:
                interp_bezier(pts[-1], pts[0], pos, resolution)
            else:
                pos.append(pts[-1].co[0:3])
        else:
            # fix issue #9 Nurbs curve crash blender
            continue
        k1 = len(pos)
        segs.extend([(j, j + 1) for j in range(k0, k1 - 1)])
        if spl.use_cyclic_u:
            segs.append((k1 - 1, k0))
        k0 = k1
    if len(segs) < 1:
        return None

    edges_co = []
    for i, (v0, v1) in enumerate(segs):
        edges_co.extend([pos[v0], pos[v1]])
    return edges_co


class _Object_Arrays:

    def __init__(self, obj, typ):

        self.points_co = None
        self.segs_co = None

        self.tris_co = None
        self.faces_indexes = None
        self.faces_center_normal = None

        self.is_mesh = False

        if typ == TYP_ORIGIN:

            self.points_co = obj

        elif typ == TYP_BOUNDS:

            self.points_co = obj

        elif typ == TYP_INSTANCE:
            if obj.type == "MESH":
                print(obj.name, typ)

                # @TODO: properly store isolated verts
                if obj.mode == "EDIT":
                    bm = bmesh.from_edit_mesh(obj.data)
                else:
                    bm = bmesh.new(use_operators=True)
                    bm.from_mesh(obj.data)

                # apply both rotation and scale
                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()

                self.segs_co = get_bmesh_edges(bm)
                self.tris_co, self.faces_indexes, self.faces_center_normal = get_bmesh_faces(bm)
                self.points_co = get_bmesh_loose_verts(bm)

                if obj.mode != "EDIT":
                    bm.free()

            elif obj.type == "CURVE":
                self.segs_co = get_curve_arrays(obj.data)

        elif obj.type == 'CURVE':
            self.segs_co = get_curve_arrays(obj.data)
        
        elif obj.type == 'MESH':

            # print(obj.name, typ)

            # @TODO: properly store isolated verts
            if obj.mode == "EDIT":
                bm = bmesh.from_edit_mesh(obj.data)
            else:
                bm = bmesh.new(use_operators=True)
                bm.from_mesh(obj.data)

            # apply both rotation and scale
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
            self.points_co = get_bmesh_loose_verts(bm)
            self.segs_co = get_bmesh_loose_edges(bm)

            if obj.mode != "EDIT":
                bm.free()

    def __del__(self):
        del self.segs_co
        del self.points_co
        del self.tris_co


class SnapBuffer:
    def __init__(self, num, vbo, ebo, batch):
        self.num = num
        self.vbo = vbo
        self.ebo = ebo
        self.batch = batch

    def __del__(self):
        del self.batch
        del self.ebo
        del self.vbo


class GPU_Indices:

    shader = gpu.types.GPUShader(vert_3d, primitive_id_frag)
    fmt = gpu.types.GPUVertFormat()
    fmt.attr_add(id="pos", comp_type='F32', len=3, fetch_mode='FLOAT')

    if USE_PRIMITIVE_BUFFER:
        fmt.attr_add(id="primitive_id", comp_type='F32', len=1, fetch_mode='FLOAT')

    P = Matrix()

    def create_buffers(self, co, batch_type, indices=None):
        _len = len(co)

        # print("create_buffers",_len, self.fmt, batch_type, co, indices)
        _indices = indices
        if _indices is None:
            if batch_type == 'POINTS':
                _indices = np.arange(_len, dtype='i')
            elif batch_type == 'LINES':
                _indices = [(i, i + 1) for i in range(0, _len, 2)]
            else:
                _indices = [(i, i + 1, i + 2) for i in range(0, _len, 3)]

        vbo = gpu.types.GPUVertBuf(len=_len, format=self.fmt)
        vbo.attr_fill(id="pos", data=co)

        n_indices = len(_indices)

        if USE_PRIMITIVE_BUFFER:

            if batch_type == 'POINTS':
                primitive_id = np.arange(_len, dtype='f4')
            elif batch_type == 'LINES':
                primitive_id = np.repeat(np.arange(n_indices, dtype='f4'), 2)
            else:
                primitive_id = np.repeat(np.arange(n_indices, dtype='f4'), 3)

            vbo.attr_fill(id="primitive_id", data=primitive_id)
            del primitive_id

        ebo = gpu.types.GPUIndexBuf(type=batch_type, seq=_indices)
        batch = gpu.types.GPUBatch(type=batch_type, buf=vbo, elem=ebo)

        del indices
        del _indices

        return SnapBuffer(n_indices, vbo, ebo, batch)

    def __init__(self, obj, typ):

        self.MVP = Matrix()

        self.first_index = 0

        self.segs = None
        self.tris = None
        self.points = None
        self.typ = typ
        self._draw_points = False
        self._draw_segs = False
        self._draw_tris = False

        _arrays = _Object_Arrays(obj, typ)

        if _arrays.segs_co:
            self.segs = self.create_buffers(_arrays.segs_co, "LINES")

        if _arrays.points_co:
            self.points =  self.create_buffers(_arrays.points_co, "POINTS")

        if _arrays.tris_co:
            self.tris = self.create_buffers(_arrays.tris_co, "TRIS", indices=_arrays.faces_indexes)

        self._arrays = _arrays

    def get_tot_elems(self):
        tot = 0
        if self.draw_segs:
            tot += self.segs.num
        if self.draw_points:
            tot += self.points.num
        if self.draw_tris:
            tot += self.tris.num
        return tot
    
    @property
    def draw_segs(self):
        return self._draw_segs and self.segs is not None

    @property
    def draw_points(self):
        return self._draw_points and self.points is not None

    @property
    def draw_tris(self):
        return self._draw_tris and self.tris is not None

    def set_draw_mode(self, draw_origins, draw_bounds, draw_segs, draw_tris):
        # Knots / segs / isolated edges
        self._draw_segs = draw_segs
        # origin / isolated verts / bounds / cursor
        self._draw_points = (
            ((self.typ & (TYP_OBJ | TYP_INSTANCE)) > 0 and draw_segs) or
            (self.typ == TYP_BOUNDS and draw_bounds) or
            (self.typ == TYP_ORIGIN and draw_origins)
        )
        # snap to faces of instances / ghost
        self._draw_tris = draw_tris

    @classmethod
    def set_ProjectionMatrix(cls, P):
        cls.P = P

    def set_ModelViewMatrix(self, MV):
        self.MVP = self.P @ MV

    def draw(self, index_offset):

        self.first_index = index_offset

        self.shader.bind()
        self.shader.uniform_float("MVP", self.MVP)

        gpu.state.depth_mask_set(False)
        gpu.state.blend_set('NONE')
        gpu.state.line_width_set(1.0)

        if self.draw_segs:
            self.shader.uniform_float("offset", float(index_offset))
            self.segs.batch.draw(self.shader)
            # if USE_PRIMITIVE_BUFFER:
            #    index_offset += int(self.segs.num / 2)
            # else:
            index_offset += self.segs.num

        if self.draw_points:
            self.shader.uniform_float("offset", float(index_offset))
            self.points.batch.draw(self.shader)
            index_offset += self.points.num

        if self.draw_tris:
            self.shader.uniform_float("offset", float(index_offset))
            self.tris.batch.draw(self.shader)
            # if USE_PRIMITIVE_BUFFER:
            #    index_offset += int(self.tris.num / 3)
            # else:
            index_offset += self.tris.num

    def get_seg_co(self, index):

        # if USE_PRIMITIVE_BUFFER:
        i = index * 2
        # else:
        # i = 2 * int(index / 2)

        if index + 2 > self.segs.num:
            print("index", i, ">", self.segs.num)
            i = 2 * self.segs.num - 2

        return self._arrays.segs_co[i:i + 2]

    def get_points_co(self, index):
        return self._arrays.points_co[index]

    def get_tris_co(self, index):

        # if USE_PRIMITIVE_BUFFER:
        i = index * 3
        # else:
        #    i = 3 * int(index / 3)

        if index + 3 > self.tris.num:
            print("index", i, ">", self.tris.num)
            i = self.tris.num - 3

        return self._arrays.tris_co[i:i + 3]

    def get_faces_center_normal(self, index):

        if USE_PRIMITIVE_BUFFER:
            i = index * 2
        else:
            i = 2 * int(index / 2)

        return self._arrays.faces_center_normal[i: i + 2]

    def __del__(self):
        del self._arrays
        pass
