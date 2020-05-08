# -*- coding:utf-8 -*-

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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110- 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# ----------------------------------------------------------
# Author: Stephen Leger (s-leger)
#
# ----------------------------------------------------------

from math import pi, cos, sin
import gpu
import bgl
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector


vertex_3d = '''
uniform mat4 MVP;

in vec3 position;

void main()
{
    gl_Position = MVP * vec4(position, 1.0);
}
'''


fragment_flat_color = '''
uniform vec4 color;

out vec4 fragColor;

void main()
{
    fragColor = color;
}
'''


class Segment:
    _shader = None

    def __init__(self, dims=3):
        self._dims = dims
        self.set_coords([(0,0,0), (1,0,0)])

    def set_coords(self, coords):
        self._coords = [Vector(co[0:self._dims]) for co in coords]
        self._batch = None

    @property
    def p0(self):
        return self._coords[0]

    @p0.setter
    def p0(self, pos):
        self.set_coords([pos, self._coords[1]])

    @property
    def p1(self):
        return self._coords[1]

    @p1.setter
    def p1(self, pos):
        self.set_coords([self._coords[0], pos])



class Rectangle:

    def __init__(self, width=0, height=0):
        self._batch = None
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._batch = None

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self._batch = None

class Arc:

    def __init__(self, start_angle=0, delta_angle=0):
        self._batch = None
        self._start_angle = start_angle
        self._delta_angle = delta_angle

    def _enabled(self):
        return self._delta_angle != 0

    @property
    def start_angle(self):
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value
        self._batch = None

    @property
    def angle(self):
        return self._delta_angle

    @angle.setter
    def angle(self, value):
        self._delta_angle = value
        self._batch = None


class BGL_Line:

    def __init__(self, width):
        self._width = width

    def _gl_enable(self):
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(self._width)

    def _gl_disable(self):
        bgl.glLineWidth(1.0)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glDisable(bgl.GL_LINE_SMOOTH)


class BGL_Polygon:

    def _gl_enable(self):
        bgl.glEnable(bgl.GL_POLYGON_SMOOTH)
        bgl.glEnable(bgl.GL_BLEND)

    def _gl_disable(self):
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glDisable(bgl.GL_POLYGON_SMOOTH)


class GPU_Draw:
    _shader = None

    def __init__(self, color=(1, 1, 0, 1)):
        self._color = color
        self._batch = None

    def _get_coords(self):
        return []

    def _enabled(self):
        return True

    def _batch_for_shader(self):
        raise NotImplementedError

    def _gl_enable(self):
        bgl.glEnable(bgl.GL_BLEND)

    def _gl_disable(self):
        bgl.glDisable(bgl.GL_BLEND)

    def draw(self, context):
        if not self._enabled():
            return

        if self._batch is None:
            self._batch_for_shader()

        self._shader.bind()
        self._shader.uniform_float("color", self._color)

        self._gl_enable()
        self._batch.draw(self._shader)
        self._gl_disable()


class GPU_3d_uniform(GPU_Draw):

    _shader = gpu.types.GPUShader(vertex_3d, fragment_flat_color)

    def __init__(self, color, batch_type):
        GPU_Draw.__init__(self, color)
        self._matrix = Matrix()
        self._format = gpu.types.GPUVertFormat()
        self._pos = self._format.attr_add(
            id="position",
            comp_type="F32",
            len=3,
            fetch_mode="FLOAT"
        )
        self._vbo = None
        # batch_type in "LINE_STRIP", "TRI_STRIP" ..
        self._batch_type = batch_type

    def _batch_for_shader(self):
        coords = self._get_coords()

        self._vbo = gpu.types.GPUVertBuf(len=len(coords), format=self._format)
        self._vbo.attr_fill(id=self._pos, data=coords)
        self._batch = gpu.types.GPUBatch(type=self._batch_type, buf=self._vbo)

    # _shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    #
    # def __init__(self, color, batch_type):
    #     GPU_Draw.__init__(self, color)
    #     self._matrix = Matrix()
    #     # batch_type in "LINE_STRIP", "TRI_STRIP" ..
    #     self._batch_type = batch_type
    #
    # def _batch_for_shader(self):
    #     coords = self._get_coords()
    #     self._batch = batch_for_shader(self._shader, self._batch_type, {"pos": coords})

    def set_world_matrix(self, matrix):
        # by default axis is 2 (Z axis)
        self._matrix = matrix

    def draw(self, context):
        if not self._enabled():
            return

        if self._batch is None:
            self._batch_for_shader()

        self._shader.bind()
        # self._shader.uniform_float("ModelMatrix", self._matrix)
        self._shader.uniform_float("MVP", context.region_data.perspective_matrix @ self._matrix)
        self._shader.uniform_float("color", self._color)

        self._gl_enable()
        self._batch.draw(self._shader)
        self._gl_disable()


class GPU_3d_PolyLine(BGL_Line, GPU_3d_uniform):

    def __init__(self, color=(1, 1, 0, 1), width=2.0):
        GPU_3d_uniform.__init__(self, color, "LINE_STRIP")
        BGL_Line.__init__(self, width)
        self._coords = []

    def _get_coords(self):
        return self._coords

    def set_coords(self, coords):
        self._coords = [Vector(co) for co in coords]
        self._batch = None


class GPU_3d_Circle(BGL_Line, GPU_3d_uniform):

    def __init__(self, radius, segments=32, color=(1, 1, 0, 1), width=2.0):
        GPU_3d_uniform.__init__(self, color, "LINE_STRIP")
        BGL_Line.__init__(self, width)
        self._radius = radius
        self._segments = segments

    def _get_coords(self):
        da = 2 * pi / (self._segments - 1)
        r = self._radius
        return [
            (r * cos(da * i), r * sin(da * i), 0)
            for i in range(self._segments)
        ]


class GPU_3d_Line(GPU_3d_PolyLine, Segment):

    def __init__(self, color=(1, 1, 0, 1), width=2.0):
        GPU_3d_PolyLine.__init__(self, color, width)
        Segment.__init__(self, dims=3)


class GPU_3d_Rectangle(BGL_Line, GPU_3d_uniform, Rectangle):

    def __init__(self, width, height, color=(1, 1, 0, 1)):
        GPU_3d_uniform.__init__(self, color, "TRI_STRIP")
        BGL_Line.__init__(self, width)
        Rectangle.__init__(self, width, height)

    def _get_coords(self):
        w, h = 0.5 * self._width, 0.5 * self._height
        return [
            (-w, -h, 0), (-w, h, 0), (w, -h, 0), (w, h, 0)
        ]


class GPU_3d_RectangleFill(BGL_Polygon, GPU_3d_uniform, Rectangle):

    def __init__(self, width, height, color=(1, 1, 0, 1)):
        GPU_3d_uniform.__init__(self, color, "TRI_STRIP")
        BGL_Polygon.__init__(self)
        Rectangle.__init__(self, width, height)

    def _get_coords(self):
        w, h = 0.5 * self._width, 0.5 * self._height
        return [
            (-w, -h, 0), (-w, h, 0), (w, -h, 0), (w, h, 0)
        ]

class GPU_3d_ArcFill(BGL_Polygon, GPU_3d_uniform, Arc):

    def __init__(self, radius, thickness, segments=32, color=(1, 1, 0, 1)):
        GPU_3d_uniform.__init__(self, color, "TRI_STRIP")
        BGL_Polygon.__init__(self)
        Arc.__init__(self)
        self._radius = radius
        self._segments = segments
        self._thickness = thickness

    def _get_coords(self):
        a, da = self._start_angle, self._delta_angle / (self._segments - 1)
        r, dr = self._radius, self._thickness
        return [
            ((r + j * dr) * cos(a + da * i), (r + j * dr) * sin(a + da * i), 0)
            for i in range(self._segments)
            for j in range(2)
        ]

class GPU_2d_uniform(GPU_Draw):
    _shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

    def __init__(self, color, batch_type):
        GPU_Draw.__init__(self, color)
        self._batch_type = batch_type

    def _batch_for_shader(self):
        coords = self._get_coords()
        self._batch = batch_for_shader(self._shader, self._batch_type, {"pos": coords})


class GPU_2d_Polyline(BGL_Line, GPU_2d_uniform):

    def __init__(self, color=(1, 1, 0, 1), width=2):
        GPU_2d_uniform.__init__(self, color, "LINE_STRIP")
        BGL_Line.__init__(self, width)
        self._coords = []

    def _get_coords(self):
        return self._coords

    def set_coords(self, coords):
        self._coords = [Vector(co[0:2]) for co in coords]
        self._batch = None


class GPU_2d_Line(GPU_2d_Polyline, Segment):

    def __init__(self, color=(1, 1, 0, 1), width=2):
        GPU_2d_Polyline.__init__(self, color, width)
        Segment.__init__(self, dims=2)


class GPU_2d_Circle(BGL_Line, GPU_2d_uniform):

    def __init__(self, radius, segments=32, color=(1, 1, 0, 1), line_width=2):
        GPU_2d_uniform.__init__(self, color, "LINE_STRIP")
        BGL_Line.__init__(self, line_width)
        self._radius = radius
        self._segments = segments
        self._center = Vector((0, 0))

    def _get_coords(self):
        x, y = self._center[0:2]
        da = 2 * pi / (self._segments - 1)
        r = self._radius
        return [(x + r * cos(da * i), y + r * sin(da * i)) for i in range(self._segments)]

    @property
    def c(self):
        return self._center

    @c.setter
    def c(self, pix):
        self._center = Vector(pix[0:2])
        self._batch = None


class GPU_2d_Rectangle(BGL_Line, GPU_2d_uniform, Rectangle):

    def __init__(self, width, height, color=(1, 1, 0, 1), line_width=2):
        GPU_2d_uniform.__init__(self, color, "TRI_STRIP")
        BGL_Line.__init__(self, line_width)
        Rectangle.__init__(self, width, height)
        self._center = Vector((0, 0))

    def _get_coords(self):
        w, h = 0.5 * self._width, 0.5 * self._height
        x, y = self._center[0:2]
        return [
            (x - w, y - h, 0), (x - w, y + h, 0), (x + w, y - h, 0), (x + w, y - h, 0)
        ]

    @property
    def c(self):
        return self._center

    @c.setter
    def c(self, pix):
        self._center = Vector(pix[0:2])
        self._batch = None


class GPU_2d_RectangleFill(GPU_2d_uniform, Rectangle):

    def __init__(self, width, height, color=(1, 1, 0, 1)):
        GPU_2d_uniform.__init__(self, color, "TRI_STRIP")
        Rectangle.__init__(self, width, height)
        self._center = Vector((0, 0))
        
    def _get_coords(self):
        w, h = 0.5 * self._width, 0.5 * self._height
        x, y = self._center[0:2]
        return [
            (x - w, y - h, 0), (x - w, y + h, 0), (x + w, y - h, 0), (x + w, y - h, 0)
        ]

    @property
    def c(self):
        return self._center

    @c.setter
    def c(self, pix):
        self._center = Vector(pix[0:2])
        self._batch = None
