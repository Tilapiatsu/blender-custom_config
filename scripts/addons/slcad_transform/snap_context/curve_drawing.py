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
import gpu
import numpy as np
from .bgl_ext import VoidBufValue, np_array_as_bgl_Buffer


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

void main()
{
    gl_FragColor = vec4(offset + primitive_id_var, 0, 0, 0);
}
'''


def get_segs_array(curve):
    segs_index = []
    for i, spl in enumerate(curve.splines):
        if spl.type == 'POLY':
            pts = spl.points
        else:
            pts = spl.bezier_points
        n_edges = len(pts) - 1
        segs_index.extend([(i, j, j + 1) for j in range(n_edges)])
        if spl.use_cyclic_u:
            segs_index.append((i, 0, n_edges))

    if len(segs_index) > 0:
        return segs_index
    return None


def get_segs_co_array(curve, segs):
    if segs:
        edges_co = bgl.Buffer(bgl.GL_FLOAT, (len(segs), 2, 3))
        for i, (s, v0, v1) in enumerate(segs):
            if curve.splines[s].type == 'POLY':
                pts = curve.splines[s].points
            else:
                pts = curve.splines[s].bezier_points
            edges_co[i][0] = pts[v0].co.to_3d()
            edges_co[i][1] = pts[v1].co.to_3d()
        return edges_co
    return None


def get_knots_array(curve):
    knots_index = []
    for i, spl in enumerate(curve.splines):
        if spl.type == 'POLY':
            pts = spl.points
        else:
            pts = spl.bezier_points
        n_edges = len(pts)
        knots_index.extend([(i, j,) for j in range(n_edges)])
        # if spl.use_cyclic_u:
        #    knots_index.append((i, 0))
    if len(knots_index) > 0:
        return knots_index
    return None


def get_knots_co_array(curve, knots):
    if knots:
        knots_co = bgl.Buffer(bgl.GL_FLOAT, (len(knots), 3))
        for i, (s, j) in enumerate(knots):
            if curve.splines[s].type == 'POLY':
                p = curve.splines[s].points[j].co.to_3d()
            else:
                p = curve.splines[s].bezier_points[j].co.to_3d()
            knots_co[i] = p
        return knots_co  #bgl.Buffer(bgl.GL_FLOAT, (len(knots), 3), knots_co)
    return None


class _Curve_Arrays():
    def __init__(self, obj, create_segs, create_knots):

        self.curve_knots, self.curve_knots_co = None, None
        self.curve_segs, self.curve_segs_co = None, None

        if obj.type == 'CURVE':

            if create_segs:
                self.curve_segs = get_segs_array(obj.data)
                self.curve_segs_co = get_segs_co_array(obj.data, self.curve_segs)

            elif create_knots:
                self.curve_knots = get_knots_array(obj.data)
                self.curve_knots_co = get_knots_co_array(obj.data, self.curve_knots)

    def __del__(self):
        del self.curve_knots, self.curve_knots_co
        del self.curve_segs, self.curve_segs_co


class GPU_Indices_Curve:

    shader = gpu.types.GPUShader(vert_3d, primitive_id_frag)

    unif_MVP = bgl.glGetUniformLocation(shader.program, 'MVP')
    unif_offset = bgl.glGetUniformLocation(shader.program, 'offset')

    attr_pos = bgl.glGetAttribLocation(shader.program, 'pos')
    attr_primitive_id = bgl.glGetAttribLocation(shader.program, 'primitive_id')

    # returns of public API #
    knot_co = bgl.Buffer(bgl.GL_FLOAT, 3)
    seg_co = bgl.Buffer(bgl.GL_FLOAT, (2, 3))

    def __init__(self, obj, draw_segs, draw_knots):
        self._NULL = VoidBufValue(0)

        self.MVP = bgl.Buffer(bgl.GL_FLOAT, (4, 4))

        self.obj = obj
        self.draw_knots = draw_knots
        self.draw_segs = draw_segs

        self.vbo_knots = None
        self.vbo_knots_co = None

        self.vbo_segs = None
        self.vbo_segs_co = None
        
        ## Create VAO ##
        self.vao = bgl.Buffer(bgl.GL_INT, 1)
        bgl.glGenVertexArrays(1, self.vao)
        bgl.glBindVertexArray(self.vao[0])

        ## Init Array ##
        curve_arrays = _Curve_Arrays(obj, draw_segs, draw_knots)

        ## Create VBO for Knots ##
        if curve_arrays.curve_knots_co:
            self.vbo_knots_co = bgl.Buffer(bgl.GL_INT, 1)
            self.num_knots = len(curve_arrays.curve_knots_co)
            bgl.glGenBuffers(1, self.vbo_knots_co)
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_knots_co[0])
            bgl.glBufferData(
                bgl.GL_ARRAY_BUFFER,
                self.num_knots * 12,
                curve_arrays.curve_knots_co,
                bgl.GL_STATIC_DRAW
            )
            self.knots_index = curve_arrays.curve_knots
            self.vbo_knots = bgl.Buffer(bgl.GL_INT, 1)
            curve_knots = np.arange(self.num_knots, dtype='f4')
            bgl.glGenBuffers(1, self.vbo_knots)
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_knots[0])
            bgl.glBufferData(
                bgl.GL_ARRAY_BUFFER,
                self.num_knots * 4,
                np_array_as_bgl_Buffer(curve_knots),
                bgl.GL_STATIC_DRAW
            )
        else:
            self.knots_index = []
            self.num_knots = 0
            self.draw_knots = False

        ## Create VBO for Segs ##
        if curve_arrays.curve_segs_co:

            self.vbo_segs_co = bgl.Buffer(bgl.GL_INT, 1)
            self.num_segs = len(curve_arrays.curve_segs_co)
            bgl.glGenBuffers(1, self.vbo_segs_co)
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_segs_co[0])
            bgl.glBufferData(bgl.GL_ARRAY_BUFFER, self.num_segs * 24, curve_arrays.curve_segs_co, bgl.GL_STATIC_DRAW)

            self.segs_index = curve_arrays.curve_segs
            segs_indices = np.repeat(np.arange(self.num_segs, dtype = 'f4'), 2)
            self.vbo_segs = bgl.Buffer(bgl.GL_INT, 1)
            bgl.glGenBuffers(1, self.vbo_segs)
            bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_segs[0])
            bgl.glBufferData(bgl.GL_ARRAY_BUFFER, self.num_segs * 8, np_array_as_bgl_Buffer(segs_indices), bgl.GL_STATIC_DRAW)
            del segs_indices
        else:
            self.segs_index = []
            self.num_segs = 0
            self.draw_segs = False
            
        del curve_arrays

        bgl.glBindVertexArray(0)

    def get_tot_elems(self):
        tot = 0
        
        if self.draw_knots:
            tot += self.num_knots

        if self.draw_segs:
            tot += self.num_segs

        return tot

    def set_draw_mode(self, draw_segs, draw_knots):
        self.draw_knots = draw_knots and self.vbo_knots_co
        self.draw_segs = draw_segs and self.vbo_segs_co

    @classmethod
    def set_ProjectionMatrix(cls, P):
        cls.P = P

    def set_ModelViewMatrix(self, MV):
        self.MVP[:] = self.P @ MV

    def bind(self, co, id, offset):

        bgl.glUniform1f(self.unif_offset, float(offset))
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, co[0])
        bgl.glVertexAttribPointer(self.attr_pos, 3, bgl.GL_FLOAT, bgl.GL_FALSE, 0, self._NULL.buf)
        bgl.glEnableVertexAttribArray(self.attr_pos)
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, id[0])
        bgl.glVertexAttribPointer(self.attr_primitive_id, 1, bgl.GL_FLOAT, bgl.GL_FALSE, 0, self._NULL.buf)
        bgl.glEnableVertexAttribArray(self.attr_primitive_id)

    def Draw(self, index_offset):
        self.first_index = index_offset
        bgl.glUseProgram(self.shader.program)
        bgl.glBindVertexArray(self.vao[0])

        bgl.glUniformMatrix4fv(self.unif_MVP, 1, bgl.GL_TRUE, self.MVP)

        if self.draw_segs:
            self.bind(self.vbo_segs_co, self.vbo_segs, index_offset)
            bgl.glDrawArrays(bgl.GL_LINES, 0, self.num_segs * 2)
            index_offset += self.num_segs

        if self.draw_knots:
            self.bind(self.vbo_knots_co, self.vbo_knots, index_offset)
            bgl.glDrawArrays(bgl.GL_POINTS, 0, self.num_knots)
            index_offset += self.num_knots

        bgl.glDepthRange(0.0, 1.0)

    def get_knot_co(self, index):
        bgl.glBindVertexArray(self.vao[0])
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_knots_co[0])
        bgl.glGetBufferSubData(bgl.GL_ARRAY_BUFFER, index * 12, 12, self.knot_co)
        bgl.glBindVertexArray(0)
        return self.knot_co

    def get_knot_index(self, index):
        return self.knots_index[index]

    def get_seg_co(self, index):
        bgl.glBindVertexArray(self.vao[0])
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vbo_segs_co[0])
        bgl.glGetBufferSubData(bgl.GL_ARRAY_BUFFER, index * 24, 24, self.seg_co)
        bgl.glBindVertexArray(0)
        return self.seg_co

    def get_seg_index(self, index):
        return self.segs_index[index]

    def __del__(self):
        del self._NULL

        if self.vbo_knots_co:
            bgl.glDeleteBuffers(1, self.vbo_knots_co)
            bgl.glDeleteBuffers(1, self.vbo_knots)
            del self.knots_index
            
        if self.vbo_segs_co:
            bgl.glDeleteBuffers(1, self.vbo_segs_co)
            bgl.glDeleteBuffers(1, self.vbo_segs)
            del self.segs_index
        
        bgl.glDeleteVertexArrays(1, self.vao)
        
        
class PreviousGLState:
    buf = bgl.Buffer(bgl.GL_INT, (4, 1))
    cur_program = buf[0]
    cur_vao = buf[1]
    cur_vbo = buf[2]
    cur_ebo = buf[3]


def _store_current_shader_state(cls):
    bgl.glGetIntegerv(bgl.GL_CURRENT_PROGRAM, cls.cur_program)
    bgl.glGetIntegerv(bgl.GL_VERTEX_ARRAY_BINDING, cls.cur_vao)
    bgl.glGetIntegerv(bgl.GL_ARRAY_BUFFER_BINDING, cls.cur_vbo)
    bgl.glGetIntegerv(bgl.GL_ELEMENT_ARRAY_BUFFER_BINDING, cls.cur_ebo)


def _restore_shader_state(cls):
    bgl.glUseProgram(cls.cur_program[0])
    bgl.glBindVertexArray(cls.cur_vao[0])
    bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, cls.cur_vbo[0])
    bgl.glBindBuffer(bgl.GL_ELEMENT_ARRAY_BUFFER, cls.cur_ebo[0])


def gpu_Indices_enable_state():
    _store_current_shader_state(PreviousGLState)
    bgl.glUseProgram(GPU_Indices_Curve.shader.program)
    bgl.glEnableVertexAttribArray(GPU_Indices_Curve.attr_pos)
    bgl.glEnableVertexAttribArray(GPU_Indices_Curve.attr_primitive_id)


def gpu_Indices_restore_state():
    bgl.glDisableVertexAttribArray(GPU_Indices_Curve.attr_pos)
    bgl.glDisableVertexAttribArray(GPU_Indices_Curve.attr_primitive_id)
    bgl.glBindVertexArray(0)
    _restore_shader_state(PreviousGLState)
