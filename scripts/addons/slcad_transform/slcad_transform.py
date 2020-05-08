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
import blf
import bpy
import os
from bpy.types import Operator, WorkSpaceTool, AddonPreferences, PropertyGroup
from bpy.props import EnumProperty, BoolProperty, StringProperty, CollectionProperty
from bpy.utils import register_class, unregister_class, register_tool, unregister_tool

from mathutils import Vector, Matrix
from math import atan2, radians, degrees, sin, cos, ceil, log2, log10
from .utils.gpu_draw import (
    GPU_3d_ArcFill, GPU_2d_Circle, GPU_3d_Line, GPU_3d_Circle, GPU_3d_PolyLine
)
from .slcad_snap import (
    SlCadSnap,
    VERT,
    EDGE,
    EDGE_CENTER,
    EDGE_PERPENDICULAR,
    FACE,
    FACE_CENTER,
    GRID,
    FACE_NORMAL,
    X_AXIS, Y_AXIS, Z_AXIS
)

slcadsnap = SlCadSnap()

# draw flags
DRAW_SNAP = 1
DRAW_EDGE = 2
DRAW_PIVOT = 4
DRAW_ROTATE = 8
DRAW_CONSTRAINT = 16
DRAW_PREVIEW = 32       # Snap constraint preview
DRAW_MOVE = 64
DRAW_PERPENDICULAR = 128
DRAW_FACE = 256
DRAW_SCALE = 512

# actions
KEYBOARD = 1
ROTATE = 2
MOVE = 4
SCALE = 8
PIVOT = 16   # use modal press + release to setup constraint axis
FREEMOVE = 32
CONSTRAINT = 64
MOVE_SNAP_FROM = 128
MOVE_SNAP_TO = 256

# constraint flags
X = 1
Y = 2
Z = 4
AXIS = 8


LOCAL = 1
GLOBAL = 2
USER = 4
# axis or plane



class SlCadRotateWidget:

    def __init__(self, radius, thickness, line_width, color, font_size=16):
        self._font_size = font_size
        self._amt = GPU_3d_ArcFill(0.84 * radius, 0.15 * radius, color=color)
        self._c = GPU_3d_Circle(radius, segments=72, color=color, width=line_width)
        self._lines = [
            GPU_3d_Line()
            for i in range(72)
        ]
        da = radians(5)
        ri = 0.84 * radius - 0.25 * thickness
        r0, r1, r2, r3 = \
            radius + 0.05 * thickness, \
            radius + 0.25 * thickness, \
            radius + 0.5 * thickness, \
            radius + thickness
        w1 = 0.25 * line_width
        w2 = 0.5 * line_width
        w3 = line_width
        for i, line in enumerate(self._lines):
            if (i % 9) == 0:
                r = r3
                w = w3
            elif (i % 3) == 0:
                r = r2
                w = w2
            else:
                r = r1
                w = w1
            x, y = cos(da * i), sin(da * i)
            line.set_coords([(ri * x, ri * y, 0), (r * x, r * y, 0)])
            line._width = w
            ri = r0
        self.set_color(color)

    @property
    def angle(self):
        return self._amt.angle

    @angle.setter
    def angle(self, value):
        self._amt.angle = value

    def set_world_matrix(self, tM):
        self._amt.set_world_matrix(tM)
        self._c.set_world_matrix(tM)
        for line in self._lines:
            line.set_world_matrix(tM)

    def set_color(self, color):
        r, g, b, a = color
        self._amt._color = (r, g, b, 0.3)
        self._c._color = color
        for line in self._lines:
            line._color = color

    def draw(self, context):
        self._amt.draw(context)
        self._c.draw(context)
        for line in self._lines:
            line.draw(context)

        text_pos = slcadsnap._screen_location_from_3d(self._amt._matrix @ Vector((0, -0.25, 0)))
        dpi, font_id = context.preferences.system.dpi, 0
        txt = "%.2f" % degrees(self.angle)
        text_size = blf.dimensions(font_id, txt)
        blf.color(0, *self._c._color)
        blf.size(font_id, self._font_size, dpi)
        blf.position(font_id, text_pos.x - 0.5 * text_size[0], text_pos.y, 0)
        blf.draw(font_id, txt)


class SlCadMoveWidget:

    def __init__(self, marker_size, radius, width, color, font_size=16):
        self._font_size = font_size
        self._amt = GPU_3d_Line(width=width, color=color)
        self._to = GPU_3d_Line(width=width, color=color)
        self._lines = [
            GPU_3d_Line()
            for i in range(100)
        ]
        y0 = -marker_size
        y1 = 0.3 * marker_size
        y2 = 0.6 * marker_size
        y3 = marker_size
        for i, line in enumerate(self._lines):
            if i == 0:
                w = width
                y = -y0
            elif (i % 10) == 0:
                w = width
                y = y3
            elif (i % 5) == 0:
                w = 0.6 * width
                y = y2
            else:
                w = 0.3 * width
                y = y1
            x = i / 100
            line.set_coords([(x, y0, 0), (x, y, 0)])
            line._width = w
            y0 = 0
        self._to.set_coords([(1.0, -marker_size, 0), (1.0, marker_size, 0)])
        self._to._width = width
        self.set_color(color)

    @property
    def distance(self):
        return self._amt._matrix.col[0].to_3d().length

    def set_world_matrix(self, tM):
        self._amt.set_world_matrix(tM)
        dist = self.distance
        if dist > 0:
            slog = ceil(log10(dist))
            x_scale = pow(10, slog)
            y_scale = pow(2, slog)
            sM = tM @ Matrix.Scale(x_scale / dist, 4, X_AXIS) @ Matrix.Scale(y_scale, 4, Y_AXIS)
            for line in self._lines:
                line.set_world_matrix(sM)
            self._to.set_world_matrix(tM @ Matrix.Scale(y_scale, 4, Y_AXIS))

    def set_color(self, color):
        self._amt._color = color
        self._to._color = color
        for line in self._lines:
            line._color = color

    def draw(self, context):
        dist = self.distance
        if dist > 0:
            self._amt.draw(context)
            n_lines = 1 + min(100, int(100 * dist / pow(10, ceil(log10(dist)))))
            for i in range(n_lines):
                self._lines[i].draw(context)
            self._to.draw(context)

        pix0 = slcadsnap._screen_location_from_3d(self._amt._matrix @ Vector((0.5, 0, 0)))
        dpi, font_id = context.preferences.system.dpi, 0

        blf.color(0, *self._to._color)
        blf.size(font_id, self._font_size, dpi)
        blf.position(font_id, pix0.x, pix0.y + 0.5 * self._font_size, 0)
        blf.draw(font_id, "%.2f" % dist)


class SlCadScaleWidget:

    def __init__(self, marker_size, width, color, font_size=16):
        self._font_size = font_size
        self._amt = GPU_3d_Line(width=width, color=color)
        self._to = GPU_3d_Line(width=width, color=color)
        self._from = GPU_3d_Line(width=width, color=color)
        self._to.set_coords([(1.0, -marker_size, 0), (1.0, marker_size, 0)])
        self._from.set_coords([(0, -marker_size, 0), (0, marker_size, 0)])
        self.set_color(color)
        self.ref = 0

    @property
    def distance(self):
        return self._amt._matrix.col[0].to_3d().length

    def set_world_matrix(self, tM):
        self._amt.set_world_matrix(tM)
        dist = self.distance
        if dist > 0:
            slog = ceil(log10(dist))
            y_scale = pow(2, slog)
            self._to.set_world_matrix(tM @ Matrix.Scale(y_scale, 4, Y_AXIS))
            self._from.set_world_matrix(tM @ Matrix.Scale(y_scale, 4, Y_AXIS))

    def set_color(self, color):
        self._amt._color = color
        self._to._color = color
        self._from._color = color

    def draw(self, context):
        dist = self.distance
        if dist > 0:
            self._amt.draw(context)
            self._to.draw(context)
            self._from.draw(context)

        if self.ref > 0:
            pix0 = slcadsnap._screen_location_from_3d(self._amt._matrix @ Vector((0.5, 0, 0)))
            dpi, font_id = context.preferences.system.dpi, 0

            blf.color(0, *self._to._color)
            blf.size(font_id, self._font_size, dpi)
            blf.position(font_id, pix0.x, pix0.y + 0.5 * self._font_size, 0)
            blf.draw(font_id, "%.1f%s" % (100 * dist / self.ref, "%"))


class SlCadEdgeWidget:

    def __init__(self, radius, line_width, colour):
        self._c = GPU_2d_Circle(radius, color=colour)
        self._edge = GPU_3d_Line(color=colour, width=line_width)
        self._mid = GPU_3d_Line(color=colour, width=line_width)
        self._edge.set_coords([(0, 0, 0), (1, 0, 0)])
        self._mid.set_coords([(0.5, -0.5, 0), (0.5, 0.5, 0)])
        
    def draw(self, context):
        self._edge.draw(context)
        self._mid.draw(context)
        self._c.c = slcadsnap._screen_location_from_3d(self._edge._matrix.translation)
        self._c.draw(context)

    def set_world_matrix(self, tM):
        y_scale = 0.05 * tM.col[0].to_3d().length
        self._edge.set_world_matrix(tM)
        self._mid.set_world_matrix(tM @ Matrix.Scale(y_scale, 4, Y_AXIS))


class SlCadFaceWidget:

    def __init__(self, radius, line_width, colour):
        self._c = GPU_2d_Circle(radius, color=colour)
        self._edges = GPU_3d_PolyLine(color=colour, width=line_width)
        self._pos = Vector()

    def draw(self, context):
        self._edges.draw(context)
        self._c.c = slcadsnap._screen_location_from_3d(self._pos)
        self._c.draw(context)

    def set_coords(self, coords):
        self._pos = coords[0]
        self._edges.set_coords(coords[1:] + [coords[1]])


class SlCadPerpendiculatWidget:

    def __init__(self, line_width, colour):
        self._constraint = GPU_3d_Line(color=colour, width=line_width)
        self._target = GPU_3d_Line(color=colour, width=line_width)

        self._constraint.set_coords([(0, 0, 0), (1, 0, 0)])
        self._target.set_coords([(0, 0, 0), (0, 1, 0)])

    def draw(self, context):
        self._constraint.draw(context)
        self._target.draw(context)

    def set_world_matrix(self, tM):
        self._constraint.set_world_matrix(tM)
        self._target.set_world_matrix(tM)


class SlCadConstraintWidget:

    def __init__(self, radius, line_width, colour):
        self._c = GPU_2d_Circle(radius, color=colour)
        self._x = GPU_3d_Line(color=(1,0,0,0.8), width=line_width)
        self._y = GPU_3d_Line(color=(0,1,0,0.8), width=line_width)
        self._z = GPU_3d_Line(color=(0,0,1,0.8), width=line_width)
        self._x.set_coords([(0, 0, 0), (1, 0, 0)])
        self._y.set_coords([(0, 0, 0), (0, 1, 0)])
        self._z.set_coords([(0, 0, 0), (0, 0, 1)])
        self._axis = (X | Y | Z)

    def draw(self, context):
        self._x.draw(context)
        self._y.draw(context)
        self._z.draw(context)
        self._c.c = slcadsnap._screen_location_from_3d(self._x._matrix.translation)
        self._c.draw(context)

    def set_axis_color(self, line, active):
        r, g, b, a = line._color
        if active:
            a = 0.8
        else:
            a = 0.3
        line._color = (r, g, b, a)

    def set_display_axis(self, flags):
        if flags & AXIS:
            axis = flags
        else:
            axis = ~flags
        self.set_axis_color(self._x, axis & X)
        self.set_axis_color(self._y, axis & Y)
        self.set_axis_color(self._z, axis & Z)

    def set_world_matrix(self, tM):
        self._x.set_world_matrix(tM)
        self._y.set_world_matrix(tM)
        self._z.set_world_matrix(tM)


def debug_action(action):
    s = []
    if action & KEYBOARD: s.append("KEYBOARD")
    if action & MOVE: s.append("MOVE")
    if action & ROTATE: s.append("ROTATE")
    if action & SCALE: s.append("SCALE")
    if action & PIVOT: s.append("PIVOT")
    if action & FREEMOVE: s.append("FREEMOVE")
    if action & CONSTRAINT: s.append("CONSTRAINT")
    return " | ".join(s)


class SlCadConstraint:

    def __init__(self, origin=None, direction=None, z=None):
        """
        :param origin: Origin
        :param direction: x Axis
        :param z: z axis
        """
        self._project_x = 0
        self._project_z = 2
        self._project_matrix = None

        cls = origin.__class__.__name__
        if cls == "Matrix":
            self._mat = origin.copy()
            self._update_project_matrix()

        elif cls == "Ray":
            o = origin.origin.copy()
            x = origin.direction.copy()
            self._init_by_origin_and_direction(o, x, z)

        elif cls == "Vector" and direction is not None:
            o = origin
            x = direction
            self._init_by_origin_and_direction(o, x, z)

        elif cls == "SlCadConstraint":
            self._mat = origin._mat.copy()
            self._project_x = origin._project_x
            self.set_project_normal(origin._project_z)

        else:
            o = Vector()
            x, y, z = X_AXIS, Y_AXIS, Z_AXIS
            self._update_matrix(o, x, y, z)

    def __copy__(self):
        return SlCadConstraint(origin=self)

    def _init_by_matrix(self, tm):
        self._mat = tm
        self._update_project_matrix()

    def _init_by_origin_and_direction(self, o, x, z):
        self.origin = o
        y = z.cross(x.normalized())
        self._update_matrix(o, x, y, z)

    def _update_project_matrix(self):
        x = self._axis(self._project_x).normalized()
        z = self._axis(self._project_z).normalized()
        y = z.cross(x)
        self._project_matrix = self._make_matrix(self.origin, x, y, z)

    @classmethod
    def _make_matrix(cls, o, x, y, z):
        return Matrix([
            [x.x, y.x, z.x, o.x],
            [x.y, y.y, z.y, o.y],
            [x.z, y.z, z.z, o.z],
            [0, 0, 0, 1]
        ])

    @classmethod
    def _matrix_from_up_and_direction(cls, o, x, z):
        xn = x.normalized()
        zn = z.normalized()
        zl = z.length
        y = zn.cross(xn)
        z = zl * xn.cross(y)
        return cls._make_matrix(o, x, y, z)

    def set_matrix_from_view(self, o, z):
        dz = abs(z.dot(Z_AXIS))
        if dz == 1:
            y = Y_AXIS
        else:
            y = Z_AXIS
        x = y.cross(z)
        y = z.cross(x)
        self._mat = self._make_matrix(o, x, y, z)
        self.set_project_axis(0)
        self.set_project_normal(2)

    def _update_matrix(self, o, x, y, z):
        self._mat = self._make_matrix(o, x, y, z)
        self._update_project_matrix()

    @property
    def origin(self):
        return self._mat.translation

    @origin.setter
    def origin(self, o):
        self._mat.translation = o
        self._project_matrix.translation = o

    @property
    def direction(self):
        return self._axis(0)

    @direction.setter
    def direction(self, x):
        # try to prevent "roll"
        if x.length < 0.0001:
            x, y, z = X_AXIS, Y_AXIS, Z_AXIS
        else:
            xn = x.normalized()
            xz = abs(xn.dot(Z_AXIS))
            if xz == 1:
                z = X_AXIS
            else:
                z = Z_AXIS
            y = z.cross(xn)
            z = xn.cross(y)
        self._update_matrix(self.origin, x, y, z)

    def _col(self, axis, value):
        self._mat.col[axis][0:3] = value[0:3]

    def _axis(self, axis):
        return self._mat.col[axis].to_3d()

    def set_project_axis(self, axis):
        self._project_x = axis

    def set_project_normal(self, axis):
        self._project_z = axis
        self._update_project_matrix()

    @property
    def project_matrix(self):
        return self._project_matrix

    @property
    def project_normal(self):
        return self._axis(self._project_z).normalized()

    @property
    def project_axis(self):
        return self._axis(self._project_x).normalized()

    @property
    def project_side(self):
        project_y = 3 - (self._project_z + self._project_x)
        return self._axis(project_y).normalized()

    def project_to_axis(self, p):
        o, d = self.origin, self.project_axis
        a = p - o
        t = d.dot(a)
        return o + t * d

    def project_to_plane(self, p):
        tM = self._project_matrix
        pos = tM.inverted() @ p
        pos.z = 0
        return tM @ pos

    def intersect(self, origin, direction, epsilon=1e-6):
        """
        origin, direction: define the line
        return a Vector or None (when the intersection can't be found).
        """
        p_no = self.project_normal
        d = p_no.dot(direction)
        if abs(d) > epsilon:
            w = origin - self.origin
            t = -p_no.dot(w) / d
            return origin + t * direction
        else:
            # The segment is parallel to plane
            return None

    @property
    def p0(self):
        return self.origin

    @p0.setter
    def p0(self, value):
        self.origin = value

    @property
    def p1(self):
        return self.origin + self.direction

    @p1.setter
    def p1(self, value):
        self.direction = value - self.origin

    def move(self, amt):
        self.origin += amt * self.project_axis


def get_xray_ex(self):
    return slcadsnap.x_ray


def set_xray_ex(self, mode):
    slcadsnap.x_ray = mode
    return None


def get_snap_mode_ex(self):
    return slcadsnap.snap_mode


def set_snap_mode_ex(self, snap_mode):
    slcadsnap.set_snap_mode(snap_mode)
    return None


def update_snap_mode_ex(self, context):
    slcadsnap.update_gl_snap()
    return None


#
def header_draw(self, context):
    layout = self.layout
    layout.label(text="Vertex", icon="EVENT_V")
    layout.label(text="Edge", icon="EVENT_E")
    layout.label(text="", icon="EVENT_SHIFT")
    layout.label(text="Edge center", icon="EVENT_E")
    layout.label(text="Face", icon="EVENT_F")
    layout.label(text="", icon="EVENT_SHIFT")
    layout.label(text="Face center", icon="EVENT_F")
    layout.label(text="Grid", icon="EVENT_G")
    layout.label(text="Edge perpendicular", icon="EVENT_P")
    layout.label(text="Constraint:")
    layout.label(text="", icon="EVENT_X")
    layout.label(text="", icon="EVENT_Y")
    layout.label(text="", icon="EVENT_Z")
    layout.label(text="Options:")
    layout.label(text="X ray", icon="EVENT_H")
    layout.label(text="Disable snap", icon="EVENT_CTRL")
    layout.label(text="Round", icon="EVENT_ALT")
    layout.label(text="", icon="EVENT_ALT")
    layout.label(text="Round (small)", icon="EVENT_SHIFT")


class SlCadTextEval:
    text = ""


def header_text(self, context):
    layout = self.layout
    layout.label(text=SlCadTextEval.text)
    layout.label(text="Confirm", icon="EVENT_RETURN")
    layout.label(text="Cancel", icon="EVENT_ESC")


class SLCAD_OT_transform:
    
    bl_idname = 'slcad.transform'
    bl_label = 'CAD Transform'

    snap_elements: EnumProperty(
        name="snap_elements",
        items=(
            ('VERT', "Vertex", "(V) Vertex", 'SNAP_VERTEX', VERT),
            ('EDGE', "Edge", "(E) Edge", 'SNAP_EDGE', EDGE),
            ('FACE', "Face", "(F) Face", 'SNAP_FACE', FACE),
            ('GRID', "Grid", "(G) Grid", 'SNAP_GRID', GRID),
            ('EDGE_CENTER', "Edge Center", "(SHIFT+E) Edge Center", 'SNAP_MIDPOINT', EDGE_CENTER),
            ('EDGE_PERPENDICULAR', "Edge Perpendicular", "(P) Edge Perpendicular", 'SNAP_PERPENDICULAR', EDGE_PERPENDICULAR),
            ('FACE_CENTER', "Face Center", "(SHIFT+F) Face Center", 'SNAP_FACE_CENTER', FACE_CENTER)
        ),
        options={'ENUM_FLAG'},
        get=get_snap_mode_ex,
        set=set_snap_mode_ex,
        update=update_snap_mode_ex
        )
    x_ray: BoolProperty(
        name="Xray",
        description="Snap across geometry",
        default=False,
        get=get_xray_ex,
        set=set_xray_ex
    )
    bl_options = {'UNDO'}

    _draw_flags = 0
    _action = 0

    _handle = None

    _flags_axis = 0
    _constraint_flag = 0
    _constraint = None
    _edge_constraint = None
    _constraint_user = None

    _snap_widget = None
    _preview_widget = None
    _constraint_widget = None
    _perpendicular_widget = None
    # constraint preview for edge
    _edge_widget = None
    _face_widget = None
    _rotate_widget = None

    # keyboard related
    line_entered = ""
    line_pos = 0
    _constraint_backup = None

    _release_confirm = False
    _confirm_exit = False
    _default_action = MOVE

    _header_draw_backup = None
    _header_text_backup = None

    _undo = []
    _keyboard_ascii = {
        ".", ",", "-", "+", "1", "2", "3",
        "4", "5", "6", "7", "8", "9", "0",
        "c", "m", "d", "k", "h", "a",
        " ", "/", "*", "'", "\""
        # "="
    }
    _keyboard_type = {
        'E', 'F', 'P', 'V', 'H',
        'C', 'G', 'R', 'S',
        'X', 'Y', 'Z',
        'BACK_SPACE', 'DEL',
        'LEFT_ARROW', 'RIGHT_ARROW', 'RET', 'NUMPAD_ENTER'
    }

    def exit(self, context):
        self.change_header_draw(self._header_draw_backup)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.window.cursor_set("DEFAULT")
        self._handle = None
        slcadsnap.exit()

    def change_header_draw(self, fun):
        last = bpy.types.STATUSBAR_HT_header.draw
        bpy.types.STATUSBAR_HT_header.draw = fun
        return last

    def gl_draw(self, context):

        if (self._draw_flags & DRAW_CONSTRAINT):
            self._constraint_widget.draw(context)

        if (self._draw_flags & DRAW_PERPENDICULAR):
            self._perpendicular_widget.draw(context)

        if (self._draw_flags & DRAW_PREVIEW):
            loc = self.apply_constraint(slcadsnap._snap_loc)
            self._preview_widget.c = slcadsnap._screen_location_from_3d(loc)
            self._preview_widget.draw(context)

        if (self._draw_flags & DRAW_EDGE):
            self._edge_widget.draw(context)

        if (self._draw_flags & DRAW_FACE):
            self._face_widget.draw(context)

        if (self._draw_flags & DRAW_ROTATE):
            self._rotate_widget.draw(context)
    
        if (self._draw_flags & DRAW_MOVE):
            self._move_widget.draw(context)

        if (self._draw_flags & DRAW_SCALE):
            self._scale_widget.draw(context)

        if (self._draw_flags & DRAW_SNAP):
            self._snap_widget.c = slcadsnap._screen_location_from_3d(slcadsnap._snap_loc)
            self._snap_widget.draw(context)

    def keyboard_event(self, context, event):

        k = event.type

        if self._confirm_exit and k in {"R", "S"}:
            return True

        if event.value == "PRESS":

            if k == "C":

                # User defined constraint axis
                if slcadsnap._is_snapping and (slcadsnap._snap_raw.typ & EDGE):
                    self._constraint = self._edge_constraint.__copy__()
                    self._draw_flags |= DRAW_CONSTRAINT
                    self._flags_axis = (X | AXIS)
                    self._constraint_widget.set_world_matrix(self._constraint._mat)
                    self._constraint_widget.set_display_axis(self._flags_axis)
                else:
                    self._flags_axis = 0
                    self._constraint_flag = 0
                    self._draw_flags &= ~DRAW_CONSTRAINT
                    self._action |= CONSTRAINT

            elif k == "E":
                if event.shift:
                    slcadsnap.toggle_snap_mode(EDGE_CENTER)
                else:
                    slcadsnap.toggle_snap_mode(EDGE)

            elif k == "F":
                if event.shift:
                    slcadsnap.toggle_snap_mode(FACE_CENTER)
                else:
                    slcadsnap.toggle_snap_mode(FACE)

            elif k == "G":

                if self._action > 0:
                    slcadsnap.toggle_snap_mode(GRID)
                else:
                    self._action = MOVE

            elif k == "H":

                slcadsnap.x_ray = not slcadsnap.x_ray

            elif k == "P":
                slcadsnap.toggle_snap_mode(EDGE_PERPENDICULAR)

            elif k == "R":
                self._action = ROTATE
                self._action |= PIVOT

            elif k == "S":
                self._action = SCALE
                self._action |= PIVOT

            elif k == "V":
                slcadsnap.toggle_snap_mode(VERT)

            elif k in "XYZ":

                # enable + toggle local global
                if k == "X":
                    axis = X
                elif k == "Y":
                    axis = Y
                else:
                    axis = Z

                constraint_to_plane = event.shift and not (self._action & ROTATE)
                # mode change from plane to axis
                same_constraint = constraint_to_plane != (self._flags_axis & AXIS)

                # toggle when same axis is set
                if (self._flags_axis & axis) and same_constraint:
                    # 2 toggle local / global / disable
                    if self._constraint_flag & USER:
                        tM = context.active_object.matrix_world.copy()
                        tM.translation = self.snap_from
                        self._constraint_flag &= ~USER
                        # in plane mode skip local
                        if self._flags_axis & AXIS:
                            self._constraint_flag |= LOCAL
                        else:
                            self._constraint_flag |= GLOBAL

                    elif self._constraint_flag & LOCAL:
                        tM = Matrix.Translation(self.snap_from)
                        self._constraint_flag &= ~LOCAL
                        self._constraint_flag |= GLOBAL

                    else:
                        self._constraint_flag &= ~GLOBAL

                        if self._action & (ROTATE | SCALE):
                            if self._constraint_user is None:
                                tM = context.active_object.matrix_world.copy()
                                tM.translation = self.snap_from
                                self._constraint_flag |= LOCAL
                            else:
                                tM = self._constraint_user._mat
                                self._constraint_flag |= USER
                        else:
                            self._flags_axis = 0

                else:

                    self._flags_axis = axis

                    if constraint_to_plane:
                        self._flags_axis &= ~AXIS
                    else:
                        self._flags_axis |= AXIS

                    # if there is a no user constraint set a local one
                    if self._constraint_user is None:
                        tM = context.active_object.matrix_world.copy()
                        tM.translation = self.snap_from
                        self._constraint_flag |= LOCAL

                    else:
                        tM = self._constraint_user._mat
                        self._constraint_flag |= USER

                if (self._flags_axis & (X | Y | Z)):
                    self._constraint._init_by_matrix(tM)
                    self._draw_flags |= DRAW_CONSTRAINT
                    self._draw_flags |= DRAW_PREVIEW
                else:
                    self._draw_flags &= ~DRAW_CONSTRAINT
                    self._draw_flags &= ~DRAW_PREVIEW

                self.set_constraint_axis(axis)
                # setup color and axis
                if (self._action & ROTATE):
                    self.update_rotate_widget()
                elif (self._action & MOVE):
                    self.update_move_widget()
                elif (self._action & SCALE):
                    self.update_scale_widget()

            else:

                if not (self._action & KEYBOARD):
                    self._header_text_backup = self.change_header_draw(header_text)
                    self._constraint_backup = self._constraint.__copy__()


                self._action |= KEYBOARD

                c = event.ascii
                if c:
                    if c == ",":
                        c = "."
                    self.line_entered = self.line_entered[:self.line_pos] + c + self.line_entered[self.line_pos:]
                    self.line_pos += 1


                if self.line_entered:
                    if k == 'BACK_SPACE':
                        self.line_entered = self.line_entered[:self.line_pos - 1] + self.line_entered[self.line_pos:]
                        self.line_pos -= 1

                    elif k == 'DEL':
                        self.line_entered = self.line_entered[:self.line_pos] + self.line_entered[self.line_pos + 1:]

                    elif k == 'LEFT_ARROW':
                        self.line_pos = (self.line_pos - 1) % (len(self.line_entered) + 1)

                    elif k == 'RIGHT_ARROW':
                        self.line_pos = (self.line_pos + 1) % (len(self.line_entered) + 1)

                if (self._action & SCALE):
                    value_type = "NONE"

                elif (self._action & ROTATE):
                    value_type = "ROTATION"

                else:
                    value_type = "LENGTH"

                confirm = k in {"RET", "NUMPAD_ENTER"}

                valid = False
                value = 0

                SlCadTextEval.text = self.line_entered

                try:

                    value = bpy.utils.units.to_value(
                        context.scene.unit_settings.system, value_type, self.line_entered
                    )
                    valid = True

                except Exception as ex:  # ValueError:
                    print(ex)
                    print(self.line_entered)
                    #self.line_entered = ""
                    #self.line_pos = 0
                    pass


                if valid:

                    not_edge = True

                    # Move snap point along edge
                    if slcadsnap._is_snapping and (slcadsnap._snap_raw.typ & EDGE):

                        p0, p1 = self._edge_constraint.p0, self._edge_constraint.p1
                        v = p1 - p0
                        vl = v.length

                        if abs(value) > 0 and vl > 0:
                            pt = p0 + (value / vl * v)
                            if not (self._action & FREEMOVE) or (self._action & MOVE_SNAP_FROM):
                                # Snap from
                                self.snap_from = pt

                                self._action |= MOVE_SNAP_FROM
                                not_edge = False

                            else:
                                # Snap to
                                if (self._action & (PIVOT | CONSTRAINT)):
                                    self._constraint.p1 = pt
                                    self._constraint_widget.set_world_matrix(self._constraint._mat)
                                    not_edge = False

                                elif (self._action & MOVE):
                                    self._move(context, event, pt - self.snap_from, confirm)
                                    not_edge = False

                    if not_edge:
                        # print("value", value)
                        if (self._action & PIVOT):
                            pivot = self._constraint_backup.__copy__()
                            pivot.move(value)
                            self._constraint = pivot
                            self._constraint_widget.set_world_matrix(self._constraint._mat)

                        elif (self._action & SCALE):
                            snap_loc = self.get_snap_loc(event)
                            delta = value * (snap_loc - self._constraint.p0).normalized()
                            self._scale(context, event, delta, confirm)

                        elif (self._action & ROTATE):
                            self._rotate(context, event, value, confirm)

                        elif (self._action & MOVE):
                            snap_loc = self.get_snap_loc(event)
                            delta = value * (snap_loc - self.snap_from).normalized()
                            self._move(context, event, delta, confirm)

                    if confirm:
                        self.line_entered = ""
                        SlCadTextEval.text = ""
                        self.line_pos = 0
                        self._action &= ~KEYBOARD
                        self.change_header_draw(self._header_text_backup)
                        if self._action & (PIVOT | CONSTRAINT | MOVE_SNAP_FROM):
                            return True

                        elif self._action & (MOVE | ROTATE | SCALE):
                            return not self._confirm_exit

        #elif event.value == "REALEASE":
        #    self._constraint_flag &= ~GLOBAL

        return True

    def set_constraint_axis(self, axis):

        axis_index = int(log2(axis))

        if self._flags_axis & AXIS and not (self._action & ROTATE):
            # single axis, rotate use normal as axis
            direction = axis_index
            normal = 2
            if axis == Z:
                normal = 1
        else:
            normal = axis_index
            direction = 0
            if axis == X:
                direction = 1

        self._constraint.set_project_axis(direction)
        self._constraint.set_project_normal(normal)
        self._constraint_widget.set_world_matrix(self._constraint._mat)
        self._constraint_widget.set_display_axis(self._flags_axis)

    def get_constraint_axis(self):
        return self._constraint._project_x

    def apply_constraint(self, pt):

        is_edge = slcadsnap._is_snapping and slcadsnap._snap_raw.typ & EDGE
        use_axis = (self._flags_axis & AXIS) and not (self._action & ROTATE)

        if is_edge and (slcadsnap.snap_mode & EDGE_PERPENDICULAR):
            # perpendicular to edge
            p0, p1 = slcadsnap._snap_raw.p0, slcadsnap._snap_raw.p1
            t = slcadsnap._point_segment_t(p0, p1, self.snap_from)
            pt = slcadsnap.lerp(p0, p1, t)

        elif (self._flags_axis & (X|Y|Z)):

            if is_edge and use_axis:
                # intersection of constraint axis and edge
                p0, p1 = slcadsnap._snap_raw.p0, slcadsnap._snap_raw.p1
                c = self._constraint.__copy__()
                c.origin = self.snap_from
                # in scale mode, always use the x axis of the source constraint
                t = slcadsnap._ray_segment_t(p0, p1, c.origin, c.project_axis)
                pt = slcadsnap.lerp(p0, p1, t)
                pt = c.project_to_axis(pt)

            elif use_axis and not (self._action & ROTATE):
                # nearest point on constraint axis, perpendicular to constraint axis
                pt = self._constraint.project_to_axis(pt)

            elif is_edge and (self._action & ROTATE):
                # intersection of edge and plane
                p0, p1 = slcadsnap._snap_raw.p0, slcadsnap._snap_raw.p1
                pit = self._constraint.intersect(p0, p1 - p0)
                if pit is None:
                    # fallback to nearest point on constraint plane
                    pt = self._constraint.project_to_plane(pt)
                else:
                    pt = pit
            else:
                # nearest point on constraint plane
                pt = self._constraint.project_to_plane(pt)

        return pt

    def get_snap_loc(self, event):

        self._draw_flags &= ~DRAW_EDGE
        self._draw_flags &= ~DRAW_FACE

        if slcadsnap._is_snapping:

            snap_loc = slcadsnap._snap_loc
            self._draw_flags |= DRAW_SNAP

            if self._flags_axis & (X | Y | Z):
                self._draw_flags |= DRAW_PREVIEW

            # Display edge overlay
            if (slcadsnap._snap_raw.typ & EDGE) and \
                 (slcadsnap.snap_mode & (EDGE | EDGE_CENTER | EDGE_PERPENDICULAR)):

                p0, p1 = slcadsnap._snap_raw.p0, slcadsnap._snap_raw.p1

                if slcadsnap._snap_raw.t > 0.5:
                    p1, p0 = p0, p1

                self._edge_constraint.p0, self._edge_constraint.p1 = p0, p1

                tM = SlCadConstraint._matrix_from_up_and_direction(p0, p1 - p0, -slcadsnap.ray_direction)
                self._edge_widget.set_world_matrix(tM)
                self._draw_flags |= DRAW_EDGE

            # display face overlay
            if (slcadsnap._snap_raw.typ & FACE) and \
                 (slcadsnap.snap_mode & (FACE | FACE_CENTER)):
                self._face_widget.set_coords(slcadsnap._snap_raw._pts)
                self._draw_flags |= DRAW_FACE
        else:
            # project view ray over constraint plane

            c = self._constraint
            p0 = c.origin

            if (self._flags_axis & (X|Y|Z)):
                snap_loc = None
                # rotate require a plane eval
                if (self._flags_axis & AXIS) and not (self._action & ROTATE):

                    # use closest point between constraint axis and view ray
                    v = c.project_axis

                    # "scan line"

                    # compute intersection of a plane parallel to view_vector and constraint axis
                    p_co = slcadsnap.ray_origin
                    p_no = slcadsnap.ray_direction.cross(slcadsnap.view_y)
                    # 0.1 was not always ideal in ortho view..
                    # use a plane relative to center of view / constraint ??
                    if abs(c.project_axis.dot(p_no)) < 0.5:
                        p_no = slcadsnap.ray_direction.cross(slcadsnap.view_x)

                    snap_loc = slcadsnap._isect_vec_plane(p0, v, p_co, p_no, epsilon=1e-6)

                else:
                    # project over plane
                    d = slcadsnap.view_z.dot(c.project_normal)

                    if abs(d) > 0.02:
                        snap_loc = slcadsnap._mouse_to_plane(p_co=p0, p_no=c.project_normal)

                    # limit to axis when point is behind view or plane is near parallel to view
                    if snap_loc is None or slcadsnap.is_not_on_screen(snap_loc):
                        v = slcadsnap.view_z.cross(c.project_normal)
                        p1 = p0 + v
                        t = slcadsnap._ray_segment_t(p0, p1, slcadsnap.ray_origin, slcadsnap.ray_direction)
                        snap_loc = p0 + t * v

            else:
                # use a plane perpendicular to view
                # self._view_plane._matrix_from_up_and_direction(p0, p1 - p0, -slcadsnap.ray_direction)
                self._view_plane.set_matrix_from_view(p0, -slcadsnap.ray_direction)
                #p_co, p_no = self._constraint.p0, self._constraint.project_normal
                p_co, p_no = self._view_plane.p0, self._view_plane.project_normal
                snap_loc = slcadsnap._mouse_to_plane(p_co=p_co, p_no=p_no)

            self._draw_flags &= ~DRAW_SNAP
            self._draw_flags &= ~DRAW_PREVIEW

        # apply constraint
        pt = self.apply_constraint(snap_loc)

        # compute perpendicular widget matrix
        if slcadsnap._is_snapping and \
                (slcadsnap._snap_raw.typ & EDGE) and \
                (slcadsnap.snap_mode & (EDGE_PERPENDICULAR)):
            x = self._constraint.origin - pt
            y = self._edge_constraint.origin - pt
            z = self._constraint.project_normal
            tM = SlCadConstraint._make_matrix(pt, x, y, z)
            self._perpendicular_widget.set_world_matrix(tM)
            self._draw_flags |= DRAW_PERPENDICULAR
        else:
            self._draw_flags &= ~DRAW_PERPENDICULAR

        return pt

    def confirm(self, context, event, snap_loc):

        # Constraint so snap target is predictable for rotation and scale
        print("confirm", debug_action(self._action))

        if (self._action & PIVOT):
            self._constraint.p1 = snap_loc
            self._constraint.set_project_axis(0)
            self._constraint.set_project_normal(2)
            self._constraint_user = self._constraint.__copy__()
            if (self._action & SCALE):
                self._flags_axis = X
                self._flags_axis |= AXIS
                self.update_scale_widget()
                self._draw_flags |= DRAW_SCALE
            else:
                self._flags_axis = Z
                self._flags_axis |= AXIS
                self.update_rotate_widget()
                self._draw_flags |= DRAW_ROTATE

            self._constraint_widget.set_display_axis(self._flags_axis)
            # keep freemove state to start rotate/scale without click
            self._action &= ~PIVOT
            slcadsnap.exclude_from_snap(context.selected_objects)
            return False

        elif (self._action & CONSTRAINT):
            self._constraint.p1 = snap_loc
            self._constraint_user = self._constraint.__copy__()
            self._flags_axis = X
            self._flags_axis |= AXIS
            self._constraint_widget.set_world_matrix(self._constraint._mat)
            self._constraint_widget.set_display_axis(self._flags_axis)

            self._action &= ~CONSTRAINT
            self._action &= ~FREEMOVE
            return False

        elif (self._action & (MOVE|ROTATE|SCALE)):
            # same than freemove
            self.mouse_freemove(context, event, snap_loc)

        slcadsnap.clear_exclude()
        self.snap_from = Vector()
        # Keep last action ?
        self._draw_flags = 0
        self._flags_axis = 0
        self._constraint_flag = 0
        self._action = 0

        return self._confirm_exit

    def modal(self, context, event):

        if context.area is not None:
            context.area.tag_redraw()

        print(event.type)

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == "PRESS":

            if (self._action & KEYBOARD):

                if self._action & (PIVOT | CONSTRAINT):
                    self._constraint = self._constraint_backup.__copy__()
                SlCadTextEval.text = ""
                self.line_entered = ""
                self.line_pos = 0
                self.change_header_draw(self._header_text_backup)
                self._action &= ~KEYBOARD
                return {'RUNNING_MODAL'}

            elif not (self._action & PIVOT):
                slcadsnap.clear_exclude()
                for o, tm in zip(context.selected_objects, self._undo):
                    o.matrix_world = tm

            self.exit(context)
            return {'FINISHED'}

        elif context.region_data is None:
            return {'PASS_THROUGH'}

        elif context.active_object is None:
            return {'PASS_THROUGH'}

        elif event.type in self._keyboard_type or event.ascii in self._keyboard_ascii:

            print("keyboard_event", event.type, event.value)
            if self.keyboard_event(context, event):
                return {'RUNNING_MODAL'}
            else:
                self.exit(context)
                return {'FINISHED'}

        elif event.type in {'LEFTMOUSE'}:

            if self._action == 0:
                print("left mouse %s without action" % event.value)
                return {'PASS_THROUGH'}

            snap_loc = self.get_snap_loc(event)

            if snap_loc is None:
                print("left mouse %s snap_loc is None" % event.value)
                return {'PASS_THROUGH'}

            if event.value == "PRESS":

                if not (self._action & FREEMOVE):
                    # clic/release cycle 1
                    # context.window.cursor_set("SCROLL_XY")

                    if (self._action & CONSTRAINT):
                        # set constraint
                        if (self._action & MOVE_SNAP_FROM):
                            snap_loc = self.snap_from
                        self._constraint.p0 = snap_loc
                        self._constraint_widget.set_world_matrix(self._constraint._mat)

                    else:
                        if (self._action & PIVOT):
                            # set pivot
                            if (self._action & MOVE_SNAP_FROM):
                                snap_loc = self.snap_from
                            self._constraint.p0 = snap_loc
                            self._constraint_widget.set_world_matrix(self._constraint._mat)
                        else:

                            slcadsnap.exclude_from_snap(context.selected_objects)

                            # Rotate and scale draw start at pivot confirm
                            if (self._action & MOVE):

                                self.update_move_widget()

                        # move / rotate / scale action: store initial state
                        self._undo = [o.matrix_world.copy() for o in context.selected_objects]
                        self.snap_from = snap_loc

                    self._action &= ~MOVE_SNAP_FROM
                    self._action |= FREEMOVE

                elif not self._release_confirm:
                    # click to confirm
                    if self.confirm(context, event, snap_loc):
                        self.exit(context)
                        return {'FINISHED'}

            elif event.value == "RELEASE" and self._release_confirm:
                if (self._action & FREEMOVE):
                    if self.confirm(context, event, snap_loc):
                        self.exit(context)
                        return {'FINISHED'}

            print("left mouse %s action" % event.value, debug_action(self._action))

            return {'RUNNING_MODAL'}

        elif event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:

            if event.ctrl:
                slcadsnap._is_snapping = False
                # refresh view origin and direction
                slcadsnap.event_origin_and_direction(event)

            else:
                slcadsnap.snap(context, event)
                print(slcadsnap._is_snapping)

            snap_loc = self.get_snap_loc(event)


            if (self._action & FREEMOVE) and snap_loc is not None:
                if (self._action & (CONSTRAINT | PIVOT)):
                    # set pivot direction on free move after 1 st press/release cycle
                    self._constraint.p1 = snap_loc
                    self._constraint_widget.set_world_matrix(self._constraint._mat)
                    # start drawing pivot
                    self._draw_flags |= DRAW_CONSTRAINT
                else:

                    # use screen as constraint
                    if self._flags_axis == 0:
                        self._constraint.set_matrix_from_view(self.snap_from, -slcadsnap.ray_direction)

                    self.mouse_freemove(context, event, snap_loc)

        return {'PASS_THROUGH'}

    def mouse_freemove(self, context, event, snap_loc):

        if (self._action & MOVE):
            delta = snap_loc - self.snap_from
            self._move(context, event, delta, store=False)

        elif (self._action & ROTATE):
            loc = self._constraint.project_matrix.inverted() @ snap_loc
            angle = atan2(loc.y, loc.x)
            self._rotate(context, event, angle, store=False)

        elif (self._action & SCALE):
            ref = self._constraint.direction.length
            if ref > 0:
                delta = snap_loc - self._constraint.p0
                self._scale(context, event, delta, store=False)

    def _move(self, context, event, delta, store=True):

        # Rounding
        if event.alt:
            dist = delta.length
            if dist > 0:
                slog = ceil(log10(dist))
                sfac = pow(10, slog)
                if event.shift:
                    step = 0.01 * sfac
                else:
                    step = 0.05 * sfac
                dist = dist - (dist % step)
                delta = dist * delta.normalized()

        tM = SlCadConstraint._matrix_from_up_and_direction(self.snap_from, delta, -slcadsnap.ray_direction)
        self._move_widget.set_world_matrix(tM)
        self._draw_flags |= DRAW_MOVE

        for i, (o, tm) in enumerate(zip(context.selected_objects, self._undo)):
            tm = tm.copy()
            tm.translation += delta
            o.matrix_world = tm
            if store:
                self._undo[i] = tm

    def update_move_widget(self):
        # Display move widget
        if self._flags_axis & AXIS and self._flags_axis & (X | Y | Z):
            axis_index = self._constraint._project_x
            color = (0, 0, 1, 0.7)
            if axis_index == 0:
                color = (1, 0, 0, 0.7)
            elif axis_index == 1:
                color = (0, 1, 0, 0.7)
        else:
            color = (0, 0, 0, 0.7)
        self._move_widget.set_color(color)

    def update_scale_widget(self):
        # Display move widget
        if self._flags_axis & AXIS and self._flags_axis & (X | Y | Z):
            axis_index = self._constraint._project_x
            color = (0, 0, 1, 0.7)
            if axis_index == 0:
                color = (1, 0, 0, 0.7)
            elif axis_index == 1:
                color = (0, 1, 0, 0.7)
        else:
            color = (0, 0, 0, 0.7)
        self._scale_widget.set_color(color)
        self._scale_widget.ref = self._constraint.direction.length
        tM = SlCadConstraint._matrix_from_up_and_direction(
            self.snap_from,
            self._constraint.direction,
            -slcadsnap.ray_direction
        )
        self._scale_widget.set_world_matrix(tM)

    def update_rotate_widget(self):
        axis = self._constraint._project_z
        color = (0, 0, 1, 0.7)
        if axis == 0:
            color = (1, 0, 0, 0.7)
        elif axis == 1:
            color = (0, 1, 0, 0.7)

        tM = self._constraint.project_matrix @ Matrix.Scale(self._constraint.direction.length, 4)
        self._rotate_widget.set_world_matrix(tM)
        self._rotate_widget.set_color(color)

    def _rotate(self, context, event, a, store=True):
        # Rounding
        angle = a
        if event.alt:
            if event.shift:
                step = 1.0
            else:
                step = 5.0
            angle = radians(step * round(degrees(a) / step, 0))

        # update rotate widget
        self._rotate_widget.angle = angle

        # Apply rotation
        pivot = Matrix.Translation(self._constraint.p0)
        rot = Matrix.Rotation(angle, 4, self._constraint.project_normal)
        trs = pivot @ rot @ pivot.inverted()
        for i, (o, tm) in enumerate(zip(context.selected_objects, self._undo)):
            o.matrix_world = tm = trs @ tm
            if store:
                self._undo[i] = tm

    def sign(self, value, positive):
        if positive:
            return abs(value)
        else:
            return -abs(value)

    def _scale(self, context, event, delta, store=True):
        ref = self._constraint.direction.length
        if ref == 0:
            return
        fac = (delta.length - ref) / ref
        if fac == 0:
            return

        if event.alt:

            if event.shift:
                step = 0.1
            else:
                step = 0.5
            fac = fac - (fac % step)

        tM = SlCadConstraint._matrix_from_up_and_direction(
            self.snap_from,
            ref * (1 + fac) * delta.normalized(),
            -slcadsnap.ray_direction
        )
        self._scale_widget.set_world_matrix(tM)

        pivot = Matrix.Translation(self.snap_from)
        pivot_inverse = pivot.inverted()
        axis = fac * delta.normalized()

        for i, (o, tm) in enumerate(zip(context.selected_objects, self._undo)):
            t, rq, s = tm.decompose()
            rm = rq.to_matrix().to_4x4()
            # offset pivot to local, apply scale to offset local
            t_local = Vector([i * (1 + j) for i, j in zip(pivot_inverse @ t, axis)])
            world = pivot @ Matrix.Translation(t_local)
            # preserve negative scale
            x, y, z = [self.sign(i * (1 + self.sign(j, fac >= 0)), i >= 0) for i, j in zip(s, rm.inverted() @ axis)]
            o.matrix_world = tm = world @ rm @ Matrix([
                [x, 0, 0, 0],
                [0, y, 0, 0],
                [0, 0, z, 0],
                [0, 0, 0, 1]
            ])
            if store:
                self._undo[i] = tm

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window.cursor_set("CROSSHAIR")
            # draw status
            self._header_draw_backup = self.change_header_draw(header_draw)

            # apply prefs
            prefs = context.preferences.addons[__package__].preferences
            self._release_confirm = prefs.release_confirm
            # self._confirm_exit = prefs.confirm_exit
            global slcadsnap
            slcadsnap.start(context)

            self._flags_axis = 0
            self._constraint_flag = 0
            self.snap_from = Vector()
            # backup to be able to toggle between local / global / user
            self._constraint_user = None
            self._view_plane = SlCadConstraint()
            self._constraint = SlCadConstraint()
            self._edge_constraint = SlCadConstraint()
            self._undo = []

            self._action = self._default_action

            # setup gl widgets
            self._snap_widget = GPU_2d_Circle(5, color=(1, 0.5, 0, 0.7))
            # preview snap target with constraint
            self._preview_widget = GPU_2d_Circle(5, color=(0, 0, 1, 0.7))

            self._edge_widget = SlCadEdgeWidget(3, 2.0, (1, 0, 0, 0.5))
            self._face_widget = SlCadFaceWidget(3, 2.0, (1, 0, 0, 0.5))

            self._perpendicular_widget = SlCadPerpendiculatWidget(1.0, (0, 1, 1, 0.5))
            self._constraint_widget = SlCadConstraintWidget(5, 2.0, (0, 1, 0, 0.7))

            self._move_widget = SlCadMoveWidget(0.1, 5, 2.0, (0, 0, 0, 0.7))
            self._rotate_widget = SlCadRotateWidget(0.5, 0.15, 2.0, color=(0, 1, 0, 0.2))
            self._scale_widget = SlCadScaleWidget(0.1, 2.0, (0, 0, 0, 0.7))

            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                self.gl_draw, (context,), 'WINDOW', 'POST_PIXEL'
            )

            wm = context.window_manager
            wm.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'FINISHED'}


class SLCAD_OT_translate(SLCAD_OT_transform, Operator):
    bl_idname = 'slcad.translate'
    bl_label = 'CAD Translate'

    _default_action = MOVE
    _confirm_exit = True


class SLCAD_OT_rotate(SLCAD_OT_transform, Operator):
    bl_idname = 'slcad.rotate'
    bl_label = 'CAD Rotate'

    _default_action = ROTATE | PIVOT
    _confirm_exit = True


class SLCAD_OT_scale(SLCAD_OT_transform, Operator):
    bl_idname = 'slcad.scale'
    bl_label = 'CAD Scale'

    _default_action = SCALE | PIVOT
    _confirm_exit = True


class SLCAD_AddonPreferences(AddonPreferences):

    bl_idname = __package__

    release_confirm: BoolProperty(name="Release confirm", description="Confirm on mouse release", default=False)
    # confirm_exit: BoolProperty(name="Exit on confirm", description="Exit tool on confirm", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "release_confirm")
        # layout.prop(self, "confirm_exit")


class SLCAD_transform(WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "slcad.transform"
    bl_label = "CAD Transform"
    bl_description = "Precise transforms operations\nShortcuts: G / R / S"
    bl_icon = os.path.join(os.path.dirname(__file__), "icons", "ops.transform.cad")
    bl_widget = None
    bl_keymap = (
        ("slcad.translate", {"type": 'G', "value": 'PRESS'}, {"properties": [("snap_elements", {'VERT'})]}), #, "ctrl": True},
        ("slcad.rotate", {"type": 'R', "value": 'PRESS'},  {"properties": [("snap_elements", {'VERT'})]}),
        ("slcad.scale", {"type": 'S', "value": 'PRESS'}, {"properties": [("snap_elements", {'VERT'})]})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("slcad.translate")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "snap_elements", text="", expand=True, icon_only=True)
        row.prop(props, "x_ray", text="", emboss=True, icon='XRAY')
        layout.separator()
        layout.label(text="Tools:")
        layout.label(text="Move", icon="EVENT_G")
        layout.label(text="Rotate", icon="EVENT_R")
        layout.label(text="Scale", icon="EVENT_S")

        if context.region.type in {'UI', 'WINDOW'}:
            layout.separator()
            layout.label(text="Snap modes")
            layout.label(text="Vertex", icon="EVENT_V")
            layout.label(text="Edge", icon="EVENT_E")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Edge center", icon="EVENT_E")
            layout.label(text="Face", icon="EVENT_F")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Face center", icon="EVENT_F")
            layout.label(text="Grid", icon="EVENT_G")
            layout.label(text="Edge perpendicular", icon="EVENT_P")
            layout.separator()
            layout.label(text="Constraint")
            layout.label(text="User Constraint", icon="EVENT_C")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_X")
            row.label(text="", icon="EVENT_Y")
            row.label(text="", icon="EVENT_Z")
            row.label(text="Axis user / local / global")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_X")
            row.label(text="", icon="EVENT_Y")
            row.label(text="", icon="EVENT_Z")
            row.label(text="Plane", icon="EVENT_SHIFT")
            layout.separator()
            layout.label(text="Options")
            layout.label(text="X ray", icon="EVENT_H")
            layout.label(text="Disable snap", icon="EVENT_CTRL")
            layout.label(text="X ray", icon="EVENT_D")
            layout.label(text="Round", icon="EVENT_ALT")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_ALT")
            row.label(text="Round (small)", icon="EVENT_SHIFT")



# Temporary Workaround for Tool Not working on restart (T60766)
from bpy.utils.toolsystem import ToolDef

kmTool = "3D View Tool: Cad Transform"
keymap = (
        kmTool,
        {"space_type": SLCAD_transform.bl_space_type, "region_type": 'WINDOW'},
        {"items": list(SLCAD_transform.bl_keymap)},
        )

emptyKeymap = (kmTool,
        {"space_type": SLCAD_transform.bl_space_type, "region_type": 'WINDOW'},
        {"items": []},)



@ToolDef.from_fn
def toolCadTransform():

    return dict(idname = SLCAD_transform.bl_idname,
        label = SLCAD_transform.bl_label,
        description = SLCAD_transform.bl_description,
        icon = SLCAD_transform.bl_icon,
        widget = None,
        keymap = kmTool,
        draw_settings=SLCAD_transform.draw_settings
        )


def registerKeymaps():
    keyconfigs = bpy.context.window_manager.keyconfigs
    kc_defaultconf = keyconfigs.default
    kc_addonconf = keyconfigs.addon

    from bl_keymap_utils.io import keyconfig_init_from_data
    keyconfig_init_from_data(kc_defaultconf, [keymap])
    keyconfig_init_from_data(kc_addonconf, [keymap])


def unregisterKeymaps():
    keyconfigs = bpy.context.window_manager.keyconfigs
    defaultmap = keyconfigs.get("blender").keymaps
    addonmap   = keyconfigs.get("blender addon").keymaps

    for km_name, km_args, km_content in [keymap]:
        km = addonmap.find(km_name, **km_args)
        keymap_items = km.keymap_items
        for item in km_content['items']:
            item_id = keymap_items.find(item[0])
            if item_id != -1:
                keymap_items.remove(keymap_items[item_id])
        addonmap.remove(km)
        defaultmap.remove(defaultmap.find(km_name, **km_args))


def getToolList(spaceType, contextMode):
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    cls = ToolSelectPanelHelper._tool_class_from_space_type(spaceType)
    return cls._tools[contextMode]


def registerTools():
    tools = getToolList('VIEW_3D', 'OBJECT')
    tools += None, toolCadTransform
    del tools


def unregisterTools():
    tools = getToolList('VIEW_3D', 'OBJECT')
    index = tools.index(toolCadTransform) - 1 #None
    tools.pop(index)
    tools.remove(toolCadTransform)
    del tools


def register():
    # register_class(slcad_shortcut)
    register_class(SLCAD_AddonPreferences)
    # register_shortcuts(bpy.context)
    register_class(SLCAD_OT_translate)
    register_class(SLCAD_OT_rotate)
    register_class(SLCAD_OT_scale)
    registerTools()
    # register_tool(SLCAD_transform, after={"builtin.transform"}, separator=True) #, group=True)
    registerKeymaps()
    print("SLCAD register")


def unregister():
    unregisterKeymaps()
    # unregister_tool(SLCAD_transform)
    unregisterTools()
    unregister_class(SLCAD_OT_translate)
    unregister_class(SLCAD_OT_rotate)
    unregister_class(SLCAD_OT_scale)
    unregister_class(SLCAD_AddonPreferences)
    #unregister_class(slcad_shortcut)
    print("SLCAD unregister")

