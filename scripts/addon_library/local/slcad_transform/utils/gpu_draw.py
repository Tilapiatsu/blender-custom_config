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
import bpy
import gpu

import blf
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector


TEXT_LEFT = 1
TEXT_CENTER = 2
TEXT_RIGHT = 4
TEXT_MIDDLE = 8


vertex_3d = '''
uniform mat4 MVP;

in vec3 position;

void main()
{
    gl_Position = MVP * vec4(position, 1.0);
}
'''


if bpy.app.version >= (2,83,0):
    # 2.83+ color correction, see https://developer.blender.org/T79788
    fragment_flat_color = '''
    uniform vec4 color;

    out vec4 fragColor;

    void main()
    {
        fragColor = blender_srgb_to_framebuffer_space(color);
    }
    '''
else:
    fragment_flat_color = '''
    uniform vec4 color;
    
    out vec4 fragColor;
    
    void main()
    {
        fragColor = color;
    }
    '''


def get_shader(builtin_typ=None):
    import bpy
    if bpy.app.background:
        return None
    if builtin_typ is not None:
        return gpu.shader.from_builtin(builtin_typ)
    else:
        return gpu.types.GPUShader(vertex_3d, fragment_flat_color)


class Segment:
    _shader = None

    def __init__(self):
        self._coords = [
            self.dim(co) for co in [
                (0, 0, 0), (1, 0, 0)
            ]
        ]

    @property
    def p0(self):
        return self._coords[0]

    @p0.setter
    def p0(self, pos):
        p0 = self.dim(pos)
        if p0 != self.p0:
            self._coords[0] = p0
            self._batch = None

    @property
    def p1(self):
        return self._coords[1]

    @p1.setter
    def p1(self, pos):
        p1 = self.dim(pos)
        if p1 != self.p1:
            self._coords[1] = p1
            self._batch = None


class Rectangle:

    def __init__(self, width=0, height=0):
        w, h = 0.5 * width, 0.5 * height
        self._coords = [
            self.dim(co) for co in [
                (-w, -h, 0), (-w, h, 0), (w, -h, 0), (w, h, 0)
            ]
        ]

    @property
    def width(self):
        return self._coords[2][0] - self._coords[0][0]

    @width.setter
    def width(self, value):
        if value != self.width:
            w = 0.5 * value
            for i, co in enumerate(self._coords):
                if i < 2:
                    co[0] = -w
                else:
                    co[0] = w
            self._batch = None

    @property
    def height(self):
        return self._coords[1][1] - self._coords[0][1]

    @height.setter
    def height(self, value):
        if value != self.height:
            h = 0.5 * value
            for i, co in enumerate(self._coords):
                if i % 2 == 0:
                    co[1] = -h
                else:
                    co[1] = h
            self._batch = None


class Arc:

    def __init__(self, start_angle=0, delta_angle=0):
        self._start_angle = start_angle
        self._delta_angle = delta_angle

    def _enabled(self):
        return self._delta_angle != 0

    @property
    def start_angle(self):
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        if value != self._start_angle:
            self._start_angle = value
            self._batch = None

    @property
    def angle(self):
        return self._delta_angle

    @angle.setter
    def angle(self, value):
        if value != self._delta_angle:
            self._delta_angle = value
            self._batch = None


class GPU_Line:

    def __init__(self, width):
        self._width = width

    def _gl_enable(self):
        gpu.state.line_width_set(self._width)
        gpu.state.blend_set('ALPHA')
        
    def _gl_disable(self):
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')
        

class GPU_Polygon:

    def _gl_enable(self):
        gpu.state.blend_set('ALPHA')

    def _gl_disable(self):
        gpu.state.blend_set('NONE')
        

class BLF_Text:
    def __init__(self, font_size, color=(1, 1, 1, 1), align=TEXT_LEFT):
        self._color = color
        self._font_size = font_size
        self._align = align

    def draw(self, context, txt, text_pos):
        dpi, font_id = context.preferences.system.dpi, 0
        blf.size(font_id, self._font_size, dpi)
        x, y = text_pos
        if self._align != TEXT_LEFT:
            text_size = blf.dimensions(font_id, txt)
            if self._align & TEXT_CENTER:
                x -= 0.5 * text_size[0]
            elif self._align & TEXT_LEFT:
                x -= text_size[0]
            if self._align & TEXT_MIDDLE:
                y -= text_size[1]
        blf.color(0, *self._color)
        blf.position(font_id, x, y, 0)
        blf.draw(font_id, txt)

    def size(self, context, txt):
        dpi, font_id = context.preferences.system.dpi, 0
        blf.size(font_id, self._font_size, dpi)
        return blf.dimensions(font_id, txt)


class GPU_Draw:
    _shader = None

    def __init__(self, color=(1, 1, 0, 1), dims=3):
        self._batch = None
        self._dims = dims
        self._color = color
        self._coords = []
        self._indices = None

    def dim(self, coord):
        return Vector(coord[0:self._dims])

    @property
    def coords(self):
        return self._coords, self._indices

    def _enabled(self):
        return True

    def _batch_for_shader(self):
        raise NotImplementedError

    def _gl_enable(self):
        gpu.state.blend_set('ALPHA')
        
    def _gl_disable(self):
        gpu.state.blend_set('NONE')
        
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

    _shader = get_shader()

    def __init__(self, color, batch_type):
        GPU_Draw.__init__(self, color, dims=3)
        self._matrix = Matrix()
        self._format = gpu.types.GPUVertFormat()
        self._pos = self._format.attr_add(
            id="position",
            comp_type="F32",
            len=3,
            fetch_mode="FLOAT"
        )
        self._vbo = None
        self._ebo = None
        # batch_type in "LINE_STRIP", "TRI_STRIP" ..
        self._batch_type = batch_type

    def _batch_for_shader(self):
        coords, indices = self.coords

        self._vbo = gpu.types.GPUVertBuf(len=len(coords), format=self._format)
        self._vbo.attr_fill(id=self._pos, data=coords)
        if indices is not None:
            self._ebo = gpu.types.GPUIndexBuf(type=self._batch_type, seq=indices)
            self._batch = gpu.types.GPUBatch(type=self._batch_type, buf=self._vbo, elem=self._ebo)
        else:
            self._batch = gpu.types.GPUBatch(type=self._batch_type, buf=self._vbo)

    def set_world_matrix(self, matrix):
        # by default axis is 2 (Z axis)
        self._matrix = matrix

    def draw(self, context):
        if not self._enabled():
            return

        if self._batch is None:
            self._batch_for_shader()

        self._shader.bind()
        self._shader.uniform_float("MVP", context.region_data.perspective_matrix @ self._matrix)
        self._shader.uniform_float("color", self._color)

        self._gl_enable()
        self._batch.draw(self._shader)
        self._gl_disable()


class GPU_3d_PolyLine(GPU_Line, GPU_3d_uniform):

    def __init__(self, color=(1, 1, 0, 1), width=2.0):
        GPU_3d_uniform.__init__(self, color, "LINE_STRIP")
        GPU_Line.__init__(self, width)

    def set_coords(self, coords, indices=None):
        if indices is not None:
            self._batch_type = "LINES"
        else:
            self._batch_type = "LINE_STRIP"
        self._coords = coords
        self._indices = indices
        self._batch = None


class GPU_3d_Circle(GPU_Line, GPU_3d_uniform):

    def __init__(self, radius, segments=32, color=(1, 1, 0, 1), width=2.0):
        GPU_3d_uniform.__init__(self, color, "LINE_STRIP")
        GPU_Line.__init__(self, width)
        da = 2 * pi / (segments - 1)
        r = radius
        self._coords = [
               (r * cos(da * i), r * sin(da * i), 0)
               for i in range(segments)
        ]


class GPU_3d_Line(GPU_3d_PolyLine, Segment):

    def __init__(self, color=(1, 1, 0, 1), width=2.0):
        GPU_3d_PolyLine.__init__(self, color, width)
        Segment.__init__(self)


class GPU_3d_ArcFill(GPU_Polygon, GPU_3d_uniform, Arc):

    def __init__(self, radius, thickness, segments=32, color=(1, 1, 0, 1)):
        GPU_3d_uniform.__init__(self, color, "TRI_STRIP")
        GPU_Polygon.__init__(self)
        Arc.__init__(self)
        self._radius = radius
        self._segments = segments
        self._thickness = thickness

    def _compute_coords(self):
        a, da = self._start_angle, self._delta_angle / (self._segments - 1)
        r, dr = self._radius, self._thickness
        return [
            ((r + j * dr) * cos(a + da * i), (r + j * dr) * sin(a + da * i), 0)
            for i in range(self._segments)
            for j in range(2)
        ]

    @property
    def coords(self):
        if self._batch is None:
            self._coords = self._compute_coords()
        return self._coords, None


class GPU_2d_uniform(GPU_Draw):
    _shader = get_shader('UNIFORM_COLOR')

    def __init__(self, color, batch_type):
        GPU_Draw.__init__(self, color, dims=2)
        self._batch_type = batch_type

    def _batch_for_shader(self):
        coords, indices = self.coords
        self._batch = batch_for_shader(self._shader, self._batch_type, {"pos": coords}, indices=indices)


class GPU_2d_Circle(GPU_Line, GPU_2d_uniform):

    def __init__(self, radius, segments=32, color=(1, 1, 0, 1), line_width=2):
        GPU_2d_uniform.__init__(self, color, "LINE_STRIP")
        GPU_Line.__init__(self, line_width)
        self._radius = radius
        self._segments = segments
        self._center = Vector((0, 0))

    def _compute_coords(self):
        x, y = self._center[0:2]
        da = 2 * pi / (self._segments - 1)
        r = self._radius
        return [(x + r * cos(da * i), y + r * sin(da * i)) for i in range(self._segments)]

    @property
    def coords(self):
        if self._batch is None:
            self._coords = self._compute_coords()
        return self._coords, None

    @property
    def c(self):
        return self._center

    @c.setter
    def c(self, pix):
        center = self.dim(pix)
        if center != self._center:
            self._center = center
            self._batch = None
