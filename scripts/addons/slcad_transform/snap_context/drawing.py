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

import bgl
import bpy
import gpu
import numpy as np
from .bgl_ext import VoidBufValue, np_array_as_bgl_Buffer
from mathutils.geometry import interpolate_bezier
import bmesh
import time

TYP_OBJ = 1
TYP_ORIGIN = 2
TYP_BOUNDS = 4


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

void main()
{
    FragColor = vec4(offset + primitive_id_var, 0, 0, 0);
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
    looseedges = [i.verts for i in bm.edges if i.is_wire]
    edges_co = None
    if len(looseedges) > 0:
        edges_co = bgl.Buffer(bgl.GL_FLOAT, (len(looseedges), 2, 3))
        for i, (v0, v1) in enumerate(looseedges):
            edges_co[i][0] = v0.co
            edges_co[i][1] = v1.co
    return edges_co


def get_bmesh_loose_verts(bm):
    # TODO: handle "visible" state
    pos = [v.co for v in bm.verts if not v.link_edges]
    if len(pos) < 1:
        return None
    return bgl.Buffer(bgl.GL_FLOAT, (len(pos), 3), pos)


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
    edges_co = bgl.Buffer(bgl.GL_FLOAT, (len(segs), 2, 3))
    for i, (v0, v1) in enumerate(segs):
        edges_co[i][0] = pos[v0]
        edges_co[i][1] = pos[v1]
    # print("get_curve_arrays %.4f  (%s) segs" % (time.time() - t, len(edges_co)))
    return edges_co


class _Object_Arrays:

    def __init__(self, obj, typ):

        self.segs_co = None
        self.origin_co = None
        self.bounds_co = None
        self.is_mesh = False

        if typ == TYP_ORIGIN:
            self.origin_co = bgl.Buffer(bgl.GL_FLOAT, (len(obj), 3), obj)

        elif typ == TYP_BOUNDS:
            self.bounds_co = bgl.Buffer(bgl.GL_FLOAT, (len(obj), 3), obj)

        elif obj.type == 'CURVE':
            self.segs_co = get_curve_arrays(obj.data)
        
        elif obj.type == 'MESH':
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
            self.origin_co = get_bmesh_loose_verts(bm)
            self.segs_co = get_bmesh_loose_edges(bm)

            self.is_mesh = True

            if obj.mode != "EDIT":
                bm.free()

    def __del__(self):
        del self.segs_co
        del self.origin_co
        del self.bounds_co


def check_error(msg):
    err = bgl.glGetError()
    if err != bgl.GL_NO_ERROR:
        print ("slcad_snap GL Error: %s %s" % (msg, err))


class GPU_Indices:

    #
    if bpy.app.version >= (2, 91, 0):
        shader = gpu.types.GPUShader(vert_3d, primitive_id_frag)
        unif_MVP = shader.uniform_from_name("MVP")
        unif_offset = shader.uniform_from_name("offset")
        attr_pos = shader.attr_from_name('pos')
        attr_primitive_id = shader.attr_from_name('primitive_id')
    else:
        from .utils_shader import Shader
        shader = Shader(gl_version + vert_3d, None, gl_version + primitive_id_frag)
        unif_MVP = bgl.glGetUniformLocation(shader.program, 'MVP')
        unif_offset = bgl.glGetUniformLocation(shader.program, 'offset')
        attr_pos = bgl.glGetAttribLocation(shader.program, 'pos')
        attr_primitive_id = bgl.glGetAttribLocation(shader.program, 'primitive_id')

    # returns of public API #

    # knot_co = bgl.Buffer(bgl.GL_FLOAT, 3)
    seg_co = bgl.Buffer(bgl.GL_FLOAT, (2, 3))
    origin_co = bgl.Buffer(bgl.GL_FLOAT, 3)
    bounds_co = bgl.Buffer(bgl.GL_FLOAT, 3)

    def __init__(self, obj, typ):

        self._NULL = VoidBufValue(0)

        self.MVP = bgl.Buffer(bgl.GL_FLOAT, (4, 4))

        # self.obj = obj
        self.first_index = 0

        self.vbo_segs = None
        self.vbo_segs_co = None

        self.vbo_origin = None
        self.vbo_origin_co = None

        self.vbo_bounds = None
        self.vbo_bounds_co = None

        self.num_segs = 0
        self.num_origins = 0
        self.num_bounds = 0

        self._draw_segs = False
        self._draw_origins = False
        self._draw_bounds = False
        self.is_mesh = False

        self.snap_mode = 0

        self.vao = bgl.Buffer(bgl.GL_INT, 1)

        bgl.glGenVertexArrays(1, self.vao)
        check_error("glGenVertexArrays(1, self.vao)")
        bgl.glBindVertexArray(self.vao[0])
        check_error("glBindVertexArray(self.vao[0])")

        _arrays = _Object_Arrays(obj, typ)

        if _arrays.segs_co:

            self.vbo_segs_co = bgl.Buffer(bgl.GL_INT, 1)
            self.num_segs = len(_arrays.segs_co)
            bgl.glGenBuffers(1, self.vbo_segs_co)
            check_error("glGenBuffers")
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_segs_co[0])
            check_error("glBindBuffer")
            bgl.glBufferData(bgl.GL_ARRAY_BUFFER, self.num_segs * 24, _arrays.segs_co, bgl.GL_STATIC_DRAW)
            check_error("glBufferData")

            segs_indices = np.repeat(np.arange(self.num_segs, dtype='f4'), 2)
            self.vbo_segs = bgl.Buffer(bgl.GL_INT, 1)
            bgl.glGenBuffers(1, self.vbo_segs)
            check_error("glGenBuffers")
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_segs[0])
            check_error("glBindBuffer")
            bgl.glBufferData(
                bgl.GL_ARRAY_BUFFER, self.num_segs * 8, np_array_as_bgl_Buffer(segs_indices), bgl.GL_STATIC_DRAW
            )
            check_error("glBufferData")
            del segs_indices
            self._draw_segs = True

        # objects origin
        if _arrays.origin_co:

            self.vbo_origin_co = bgl.Buffer(bgl.GL_INT, 1)
            self.num_origins = len(_arrays.origin_co)
            bgl.glGenBuffers(1, self.vbo_origin_co)
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_origin_co[0])
            check_error("glBindBuffer")
            bgl.glBufferData(bgl.GL_ARRAY_BUFFER, self.num_origins * 12, _arrays.origin_co, bgl.GL_STATIC_DRAW)
            check_error("glBufferData")

            orig_indices = np.arange(self.num_origins, dtype='f4')
            self.vbo_origin = bgl.Buffer(bgl.GL_INT, 1)
            bgl.glGenBuffers(1, self.vbo_origin)
            check_error("glGenBuffers")

            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_origin[0])
            check_error("glBindBuffer")
            bgl.glBufferData(
                bgl.GL_ARRAY_BUFFER, self.num_origins * 4, np_array_as_bgl_Buffer(orig_indices), bgl.GL_STATIC_DRAW
            )
            check_error("glBufferData")
            del orig_indices
            self.is_mesh = _arrays.is_mesh
            self._draw_origins = True

        # objects bound box
        if _arrays.bounds_co:
            self.vbo_bounds_co = bgl.Buffer(bgl.GL_INT, 1)

            self.num_bounds = len(_arrays.bounds_co)
            bgl.glGenBuffers(1, self.vbo_bounds_co)
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_bounds_co[0])
            bgl.glBufferData(bgl.GL_ARRAY_BUFFER, self.num_bounds * 12, _arrays.bounds_co, bgl.GL_STATIC_DRAW)

            bounds_indices = np.arange(self.num_bounds, dtype='f4')
            self.vbo_bounds = bgl.Buffer(bgl.GL_INT, 1)
            bgl.glGenBuffers(1, self.vbo_bounds)
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_bounds[0])
            bgl.glBufferData(
                bgl.GL_ARRAY_BUFFER, self.num_bounds * 4, np_array_as_bgl_Buffer(bounds_indices), bgl.GL_STATIC_DRAW
            )
            del bounds_indices
            self._draw_bounds = True

        del _arrays

        bgl.glBindVertexArray(0)
        check_error("glBindVertexArray(0)")

    def get_tot_elems(self):
        tot = 0
        if self.draw_segs:
            tot += self.num_segs
        if self.draw_origin:
            tot += self.num_origins
        if self.draw_bounds:
            tot += self.num_bounds
        return tot
    
    @property
    def draw_segs(self):
        return self._draw_segs and self.vbo_segs is not None

    @property
    def draw_bounds(self):
        return self._draw_bounds and self.vbo_bounds is not None

    @property
    def draw_origin(self):
        # origins and isolated vertices
        return (self._draw_origins or (self._draw_segs and self.is_mesh)) and self.vbo_origin is not None

    def set_snap_mode(self, snap_mode):
        self.snap_mode = snap_mode

    def set_draw_mode(self, draw_segs, draw_origin, draw_bounds):
        self._draw_segs = draw_segs
        self._draw_origins = draw_origin
        self._draw_bounds = draw_bounds

    @classmethod
    def set_ProjectionMatrix(cls, P):
        cls.P = P

    def set_ModelViewMatrix(self, MV):
        self.MVP[:] = self.P @ MV

    def bind(self, co, buf_id, offset):
        bgl.glUniform1f(self.unif_offset, float(offset))
        check_error("glUniform1f")
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, co[0])
        check_error("glBindBuffer")
        bgl.glVertexAttribPointer(self.attr_pos, 3, bgl.GL_FLOAT, bgl.GL_FALSE, 0, self._NULL.buf)
        check_error("glVertexAttribPointer")
        bgl.glEnableVertexAttribArray(self.attr_pos)
        check_error("glEnableVertexAttribArray")
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, buf_id[0])
        check_error("glBindBuffer")
        bgl.glVertexAttribPointer(self.attr_primitive_id, 1, bgl.GL_FLOAT, bgl.GL_FALSE, 0, self._NULL.buf)
        check_error("glVertexAttribPointer")
        bgl.glEnableVertexAttribArray(self.attr_primitive_id)
        check_error("glEnableVertexAttribArray")

    def draw(self, index_offset):

        self.first_index = index_offset

        bgl.glUseProgram(self.shader.program)
        check_error("glUseProgram")

        bgl.glBindVertexArray(self.vao[0])
        check_error("glBindVertexArray(self.vao[0])")
        bgl.glUniformMatrix4fv(self.unif_MVP, 1, bgl.GL_TRUE, self.MVP)
        check_error("glUniformMatrix4fv")
        # 2.91 - require sequence of floats
        # self.shader.uniform_float("MVP", np.reshape(self.MVP, 16))

        if self.draw_segs:
            self.bind(self.vbo_segs_co, self.vbo_segs, index_offset)
            check_error("draw_segs bind")
            # 2.91
            # self.shader.uniform_float("offset", float(index_offset))
            bgl.glDrawArrays(bgl.GL_LINES, 0, self.num_segs * 2)
            check_error("draw_segs glDrawArrays")
            index_offset += self.num_segs

        if self.draw_origin:
            self.bind(self.vbo_origin_co, self.vbo_origin, index_offset)
            check_error("draw_origin bind")
            # 2.91
            # self.shader.uniform_float("offset", float(index_offset))
            bgl.glDrawArrays(bgl.GL_POINTS, 0, self.num_origins)
            check_error("draw_origin glDrawArrays")
            index_offset += self.num_origins

        if self.draw_bounds:
            self.bind(self.vbo_bounds_co, self.vbo_bounds, index_offset)
            check_error("draw_bounds bind")
            # 2.91
            # self.shader.uniform_float("offset", float(index_offset))
            bgl.glDrawArrays(bgl.GL_POINTS, 0, self.num_bounds)
            check_error("draw_bounds glDrawArrays")
            index_offset += self.num_bounds

        bgl.glBindVertexArray(0)
        check_error("glBindVertexArray(0)")

            
    def get_seg_co(self, index):
        bgl.glBindVertexArray(self.vao[0])
        check_error("glBindVertexArray(self.vao[0])")
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_segs_co[0])
        check_error("glBindBuffer")
        bgl.glGetBufferSubData(bgl.GL_ARRAY_BUFFER, index * 24, 24, self.seg_co)
        check_error("glGetBufferSubData")
        bgl.glBindVertexArray(0)
        check_error("glBindVertexArray(0)")
        return self.seg_co

    def get_origin_co(self, index):
        bgl.glBindVertexArray(self.vao[0])
        check_error("glBindVertexArray(self.vao[0])")
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_origin_co[0])
        check_error("glBindBuffer")
        bgl.glGetBufferSubData(bgl.GL_ARRAY_BUFFER, index * 12, 12, self.origin_co)
        check_error("glGetBufferSubData")
        bgl.glBindVertexArray(0)
        check_error("glBindVertexArray(0)")
        return self.origin_co

    def get_bounds_co(self, index):
        bgl.glBindVertexArray(self.vao[0])
        check_error("glBindVertexArray(self.vao[0])")
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_bounds_co[0])
        check_error("glBindBuffer")
        bgl.glGetBufferSubData(bgl.GL_ARRAY_BUFFER, index * 12, 12, self.bounds_co)
        check_error("glGetBufferSubData")
        bgl.glBindVertexArray(0)
        check_error("glBindVertexArray(0)")
        return self.bounds_co

    def __del__(self):
        del self._NULL

        if self.vbo_segs_co:
            bgl.glDeleteBuffers(1, self.vbo_segs_co)
            bgl.glDeleteBuffers(1, self.vbo_segs)

        if self.vbo_origin_co:
            bgl.glDeleteBuffers(1, self.vbo_origin_co)
            bgl.glDeleteBuffers(1, self.vbo_origin)

        if self.vbo_bounds_co:
            bgl.glDeleteBuffers(1, self.vbo_bounds_co)
            bgl.glDeleteBuffers(1, self.vbo_bounds)

        bgl.glDeleteVertexArrays(1, self.vao)
        
#