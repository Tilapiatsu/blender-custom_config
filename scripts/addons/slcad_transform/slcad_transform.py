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

import bpy
import os
import bmesh
import time
import logging
from logging import config
from bpy.types import Operator, WorkSpaceTool, AddonPreferences, PropertyGroup, Panel
from bpy.props import (
    EnumProperty, BoolProperty, StringProperty, IntProperty, FloatProperty,
    CollectionProperty, FloatVectorProperty, BoolVectorProperty
)

from . import __version__, bl_info

from bpy.utils import register_class, unregister_class, register_tool, unregister_tool, previews
from mathutils import Vector, Matrix
from math import atan2, radians, degrees, sin, cos, ceil, log2, log10
from .utils.gpu_draw import (
    GPU_3d_ArcFill, GPU_2d_Circle, GPU_3d_Line, GPU_3d_Circle, GPU_3d_PolyLine, BLF_Text,
    TEXT_CENTER, TEXT_MIDDLE
)
from .slcad_snap import (
    SlCadSnap,
    VERT,
    EDGE,
    EDGE_CENTER,
    EDGE_PERPENDICULAR,
    EDGE_PARALLEL,
    FACE,
    FACE_CENTER,
    GRID,
    FACE_NORMAL,
    ORIGIN,
    X_AXIS, Y_AXIS, Z_AXIS
)

ZERO = Vector()

DEBUG_DRAW_GL = False  # bpy.app.version >= (2, 91, 0)


logger = logging.getLogger(__package__)

# logging.addLevelName( logging.WARNING, "\033[1;31m%8s\033[1;0m" % logging.getLevelName(logging.WARNING))
# logging.addLevelName( logging.ERROR, "\033[1;41m%8s\033[1;0m" % logging.getLevelName(logging.ERROR))

config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)-15s %(levelname)8s %(filename)s %(lineno)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stderr',
        }
    },
    'loggers': {
        __package__: {'level': 'INFO'}
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['console'],
    }
})

slcadsnap = SlCadSnap()

# draw flags
DRAW_SNAP = 1
DRAW_EDGE = 2
DRAW_PIVOT = 4
DRAW_ROTATE = 8
DRAW_CONSTRAINT = 16
DRAW_PREVIEW = 32  # Snap constraint preview
DRAW_MOVE = 64
DRAW_PERPENDICULAR = 128
DRAW_FACE = 256
DRAW_SCALE = 512
DRAW_NORMAL = 1024
DRAW_GRID = 2048
DRAW_EDGE_AXIS = 4096

# actions
KEYBOARD = 1
ROTATE = 2
MOVE = 4
SCALE = 8
PIVOT = 16
FREEMOVE = 32
CONSTRAINT = 64
MOVE_SNAP_FROM = 128
MOVE_SNAP_TO = 256
DUPLICATE = 512

# constraint axis or plane
X = 1
Y = 2
Z = 4
AXIS = 8

# constraint flags
C_LOCAL = 1
C_GLOBAL = 2
C_USER = 4
C_EDGE = 8
C_NORMAL = 16
C_SCREEN = 32


class IconsManager:

    def __del__(self):
        if self._icons is not None:
            self.cleanup()

    def __init__(self):
        self._icons = None

    @property
    def icons(self):
        self.load()
        return self._icons

    def load(self):
        if self._icons is None:
            self._icons = previews.new()
            folder = os.path.join(os.path.dirname(__file__), "icons")
            files = os.listdir(folder)
            for file in files:
                name, ext = os.path.splitext(file)
                if ext == ".png":
                    self._icons.load(
                        name,
                        os.path.join(folder, file),
                        'IMAGE',
                        force_reload=False
                    )

    def cleanup(self):
        previews.remove(self._icons)
        self._icons = None


icon_man = IconsManager()

_running = False

# Default keymap, to init preferences
default_keymap = {
    # name,     key, label,         tip,    ctrl, alt, shift
    "VERT": ("V", "Vertex"),
    "EDGE": ("E", "Edge"),
    "EDGE_CENTER": ("E", "Edge Center", False, False, True),
    "FACE": ("F", "Face"),
    "FACE_CENTER": ("F", "Face Center", False, False, True),
    "GRID": ("G", "Grid"),
    "EDGE_PERPENDICULAR": ("P", "Perpendicular"),
    "EDGE_PARALLEL": ("P", "Parallel", False, False, True),
    "FACE_NORMAL": ("N", "Normal"),
    "ORIGIN": ("O", "Origin"),
    "X": ("X", "Axis X"),
    "Y": ("Y", "Axis Y"),
    "Z": ("Z", "Axis Z"),
    "YZ": ("X", "Plane YZ", False, False, True),
    "XZ": ("Y", "Plane XZ", False, False, True),
    "XY": ("Z", "Plane XY", False, False, True),
    "AVERAGE": ("A", "Average"),
    "AVERAGE_CLEAR": ("A", "Clear", False, False, True),
    "CONSTRAINT": ("C", "Constraint (Move)"),
    "X_RAY": ("H", "X ray"),
    "SCALE_DIMENSIONS": ("TAB", "Scale dimensions"),
    "CLEAR_SNAP": ("SPACE", "Clear all snap"),
    "INVERT_CONSTRAINT": ("I", "Invert constraint direction"),
    "DUPLICATE": ("D", "Duplicate"),
    "WORLD_CONSTRAINT": ("C", "Constraint world", False, False, True)
    # it is still not possible to define actions shortcuts
    # "MOVE": ("G", "Move"),
    # "ROTATE": ("R", "Rotate"),
    # "SCALE": ("S", "Scale")
}


class context_override:
    """ Override context in object mode
    """

    def area(self, context, ctx):
        # take care of context switching
        # when call from outside of 3d view
        # on subsequent calls those vars are set
        try:
            if context.space_data is None or context.space_data.type != 'VIEW_3D':
                for window in context.window_manager.windows:
                    screen = window.screen
                    for area in screen.areas:
                        if area.type == 'VIEW_3D':
                            ctx['area'] = area
                            for region in area.regions:
                                if region.type == 'WINDOW':
                                    ctx['region'] = region
                            break
        except AttributeError:
            pass

    def id_data(self, context, ctx, act, sel):
        """ Set id data based context variables
        :param act:
        :param sel:
        :param context:
        :param ctx:
        :return:
        """
        act_id_data = act.id_data
        sel_id_data = [o.id_data for o in sel]
        all_id_data = context.scene.objects
        ctx['selected_objects'] = sel_id_data
        ctx['selectable_objects'] = all_id_data
        ctx['visible_objects'] = all_id_data
        ctx['objects_in_mode'] = [act_id_data]
        # parent child relationship operators
        ctx['editable_objects'] = sel_id_data
        ctx['selected_editable_objects'] = sel_id_data
        ctx['objects_in_mode_unique_data'] = [act_id_data]
        # looks like snap use editable bases.. no more exposed in context ???
        # view_layer->basact;
        # for (Base * base = view_layer->object_bases.first ...

    def __init__(self, context, act, sel):
        if act not in sel:
            sel.append(act)
        ctx = context.copy()
        # area override
        self.area(context, ctx)
        # view_layer <bpy_struct, ViewLayer("View Layer")>
        # active_operator  <bpy_struct, Operator>
        # collection  <bpy_struct, Collection()>
        # layer_collection <bpy_struct, LayerCollection()>
        # <Struct Object()>
        ctx['object'] = act
        ctx['active_object'] = act

        # bpy.data objects
        self.id_data(context, ctx, act, sel)

        # override context
        self._ctx = ctx

    def __enter__(self):
        return self._ctx

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def debug_constraint(constraint):
    s = []
    if constraint & C_LOCAL:
        s.append("C_LOCAL")
    if constraint & C_GLOBAL:
        s.append("C_GLOBAL")
    if constraint & C_USER:
        s.append("C_USER")
    if constraint & C_EDGE:
        s.append("C_EDGE")
    if constraint & C_NORMAL:
        s.append("C_NORMAL")
    if constraint & C_SCREEN:
        s.append("C_SCREEN")
    return " | ".join(s)


def debug_action(action):
    s = []
    if action & KEYBOARD:
        s.append("KEYBOARD")
    if action & MOVE:
        s.append("MOVE")
    if action & ROTATE:
        s.append("ROTATE")
    if action & SCALE:
        s.append("SCALE")
    if action & PIVOT:
        s.append("PIVOT")
    if action & FREEMOVE:
        s.append("FREEMOVE")
    if action & CONSTRAINT:
        s.append("CONSTRAINT")
    return " | ".join(s)


def debug_axis(axis):
    s = []
    if axis & AXIS:
        if axis & X:
            s.append("X")
        if axis & Y:
            s.append("Y")
        if axis & Z:
            s.append("Z")
    else:
        if axis & X:
            s.append("YZ")
        if axis & Y:
            s.append("XZ")
        if axis & Z:
            s.append("XY")
    return " ".join(s)


class SlCadGridWidget:

    def __init__(self, color1, color2, axis_x, axis_y, line_width):
        self._axis_x = GPU_3d_PolyLine(axis_x, 2.0 * line_width)
        self._axis_y = GPU_3d_PolyLine(axis_y, 2.0 * line_width)
        self._axis_x.set_coords([(-1000, 0, 0), (1000, 0, 0)], indices=[(0, 1)])
        self._axis_y.set_coords([(0, -1000, 0), (0, 1000, 0)], indices=[(0, 1)])
        self._line = GPU_3d_PolyLine(color1, line_width)
        coords = []
        for i in range(42):
            if i < 21:
                x0, x1 = -10, 10
                y0 = y1 = i - 10
            else:
                x0 = x1 = i - 31
                y0, y1 = -10, 10
            coords.extend([(x0, y0, 0), (x1, y1, 0)])

        self._line.set_coords(coords, indices=[(i, i + 1) for i in range(0, 84, 2)])

        self._subline = GPU_3d_PolyLine(color2, line_width)
        coords = []
        for i in range(402):
            if i < 201:
                if i % 10 == 0:
                    continue
                x0, x1 = -10, 10
                y0 = y1 = (i / 10) - 10
            else:
                if i % 10 == 1:
                    continue
                x0 = x1 = ((i - 201) / 10) - 10
                y0, y1 = -10, 10
            coords.extend([(x0, y0, 0), (x1, y1, 0)])
        self._subline.set_coords(coords, indices=[(i, i + 1) for i in range(0, 804, 2)])

    def set_world_matrix(self, tM, tM_axis):
        self._line.set_world_matrix(tM)
        self._subline.set_world_matrix(tM)
        self._axis_x.set_world_matrix(tM_axis)
        self._axis_y.set_world_matrix(tM_axis)

    def set_color(self, color1, color2):
        self._line._color = color1
        self._subline._color = color2

    def draw(self, context):
        self._line.draw(context)
        self._subline.draw(context)
        self._axis_x.draw(context)
        self._axis_y.draw(context)


class SlCadRotateWidget:

    def __init__(self, radius, thickness, line_width, color, text_color, font_size=16):
        self._txt = BLF_Text(font_size, text_color, align=TEXT_MIDDLE)
        self._amt = GPU_3d_ArcFill(0.80 * radius, 0.15 * radius, color=color)
        self._c = GPU_3d_Circle(radius, segments=72, color=color, width=line_width)

        self._line0 = GPU_3d_PolyLine(color, 0.25 * line_width)
        self._line1 = GPU_3d_PolyLine(color, 0.5 * line_width)
        self._line2 = GPU_3d_PolyLine(color, line_width)
        self._radius = radius + thickness
        da = radians(5)
        ri = 0.84 * radius - 0.25 * thickness
        r0, r1, r2, r3 = \
            radius + 0.05 * thickness, \
            radius + 0.25 * thickness, \
            radius + 0.5 * thickness, \
            radius + thickness

        coords = [[],[],[]]
        for i in range(72):
            if (i % 9) == 0:
                r = r3
                j = 2
            elif (i % 3) == 0:
                r = r2
                j = 1
            else:
                r = r1
                j = 0
            x, y = cos(da * i), sin(da * i)
            coords[j].extend([(ri * x, ri * y, 0), (r * x, r * y, 0)])
            ri = r0

        self._line0.set_coords(coords[0], indices=[(i, i + 1) for i in range(0, len(coords[0]), 2)])
        self._line1.set_coords(coords[1], indices=[(i, i + 1) for i in range(0, len(coords[1]), 2)])
        self._line2.set_coords(coords[2], indices=[(i, i + 1) for i in range(0, len(coords[2]), 2)])

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
        self._line0.set_world_matrix(tM)
        self._line1.set_world_matrix(tM)
        self._line2.set_world_matrix(tM)

    def set_color(self, color):
        r, g, b, a = color
        self._amt._color = (r, g, b, 0.3)
        self._c._color = color
        self._line0._color = color
        self._line1._color = color
        self._line2._color = color

    def draw(self, context):
        self._amt.draw(context)
        self._c.draw(context)
        self._line0.draw(context)
        self._line1.draw(context)
        self._line2.draw(context)

        a = self.angle
        r = self._radius * 1.2
        text_pos = slcadsnap._screen_location_from_3d(self._amt._matrix @ Vector((r * cos(a), r * sin(a), 0)))
        self._txt.draw(context, "%.2f" % degrees(self.angle), text_pos)


class SlCadMoveWidget:

    def __init__(self, marker_size, width, color, text_color, font_size=16):
        self._txt = BLF_Text(font_size, text_color, align=TEXT_MIDDLE)
        self._amt = GPU_3d_Line(width=width, color=color)
        self._to = GPU_3d_Line(width=width, color=color)
        self._lines = [GPU_3d_Line() for i in range(100)]
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
            n_lines = 1 + min(99, int(100 * dist / pow(10, ceil(log10(dist)))))
            for i in range(n_lines):
                self._lines[i].draw(context)
            self._to.draw(context)
        us = context.scene.unit_settings
        # how to round properly ?
        d = dist * us.scale_length
        txt = bpy.utils.units.to_string(
            us.system,
            'LENGTH',
            d,
            precision=5,
            split_unit=us.use_separate,
            compatible_unit=False
        )
        text_pos = slcadsnap._screen_location_from_3d(self._to._matrix @ Vector((1, 0, 0)))
        self._txt.draw(context, "   %s" % txt, text_pos)


class SlCadScaleWidget:

    def __init__(self, marker_size, width, color, text_color, font_size=16):
        self._txt = BLF_Text(font_size, text_color, align=TEXT_MIDDLE)
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
            us = context.scene.unit_settings
            txt = bpy.utils.units.to_string(
                us.system,
                'LENGTH',
                round(dist * us.scale_length, 5),
                precision=5,
                split_unit=us.use_separate,
                compatible_unit=False
            )
            text_pos = slcadsnap._screen_location_from_3d(self._to._matrix @ Vector((1, 0, 0)))
            self._txt.draw(context, "   %.2f%s  ( %s )" % (100 * dist / self.ref, "%", txt), text_pos)


class SlCadEdgeWidget:

    def __init__(self, radius, line_width, colour):
        self._c = GPU_2d_Circle(radius, color=colour, line_width=line_width)
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


class SlCadNormalWidget:

    def __init__(self, radius, line_width, colour):
        self._c = GPU_2d_Circle(radius, color=colour, line_width=line_width)
        self._normal = GPU_3d_Line(color=colour, width=line_width)
        self._normal.set_coords([(0, 0, 0), (0, 0, 1)])

    def draw(self, context):
        self._normal.draw(context)
        self._c.c = slcadsnap._screen_location_from_3d(self._normal._matrix.translation)
        self._c.draw(context)

    def set_world_matrix(self, tM):
        self._normal.set_world_matrix(tM)


class SlCadFaceWidget:

    def __init__(self, radius, line_width, colour):
        self._c = GPU_2d_Circle(radius, color=colour, line_width=line_width)
        self._edges = GPU_3d_PolyLine(color=colour, width=line_width)
        self._pos = Vector()

    def draw(self, context):
        self._edges.draw(context)
        self._c.c = slcadsnap._screen_location_from_3d(self._pos)
        self._c.draw(context)

    def set_coords(self, coords):
        self._pos = coords[0]
        self._edges.set_coords(coords[1:] + [coords[1]])


class SlCadPerpendicularWidget:

    def __init__(self, line_width, colour):
        self._constraint = GPU_3d_PolyLine(color=colour, width=line_width)
        # near constraint                                             near edge
        self._constraint.set_coords([
            (1, 0, 0), (0, 0, 0), (0, 0, 0.11),
            (0, 0, 0.22), (0, 0, 0.33), (0, 0, 0.44), (0, 0, 0.55), (0, 0, 0.66), (0, 0, 0.77),
            (0, 0, 0.88), (0, 0, 1), (0, 1, 1)
        ], indices=[
            (0, 1), (1, 2),
            (3, 4), (5, 6), (7, 8),
            (9, 10), (10, 11)
        ])

    def draw(self, context):
        self._constraint.draw(context)

    def set_world_matrix(self, tM):
        self._constraint.set_world_matrix(tM)


class SlCadConstraintWidget:

    def __init__(self, line_width, x_color, y_color, z_color):
        self._x = GPU_3d_Line(color=x_color, width=line_width)
        self._y = GPU_3d_Line(color=y_color, width=line_width)
        self._z = GPU_3d_Line(color=z_color, width=line_width)
        self._x.set_coords([(0, 0, 0), (1, 0, 0)])
        self._y.set_coords([(0, 0, 0), (0, 1, 0)])
        self._z.set_coords([(0, 0, 0), (0, 0, 1)])
        self._axis = (X | Y | Z)

    def draw(self, context):
        self._x.draw(context)
        self._y.draw(context)
        self._z.draw(context)

    def set_axis_color(self, line, active):
        r, g, b, a = line._color
        if active:
            a = 0.8
        else:
            a = 0.5
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


class SlCadConstraint:
    changeAxesDict = {
        ("X", "Z"): lambda x, y, z: (z, -y, x),
        ("X", "Y"): lambda x, y, z: (z, x, y),
        ("Y", "Z"): lambda x, y, z: (y, z, x),
        ("Y", "X"): lambda x, y, z: (x, z, -y),

        ("Z", "X"): lambda x, y, z: (x, y, z),
        ("Z", "Y"): lambda x, y, z: (-y, x, z),
        ("-X", "Z"): lambda x, y, z: (-z, y, x),
        ("-X", "Y"): lambda x, y, z: (-z, x, -y),

        ("-Y", "Z"): lambda x, y, z: (-y, -z, x),
        ("-Y", "X"): lambda x, y, z: (x, -z, y),
        ("-Z", "X"): lambda x, y, z: (x, -y, -z),
        ("-Z", "Y"): lambda x, y, z: (y, x, -z),
    }

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

        elif cls == "Vector" and direction is not None:
            self._init_by_origin_and_direction(origin, direction, z)

        elif cls == "SlCadConstraint":
            self._mat = origin._mat.copy()
            self._project_x = origin._project_x
            self.set_project_normal(origin._project_z)

        else:
            self._update_matrix(Vector(), X_AXIS, Y_AXIS, Z_AXIS)

    @property
    def _project_y(self):
        return 3 - (self._project_x + self._project_z)

    @classmethod
    def safe_vectors(cls, direction, guide, main_axis="X", guide_axis="Z"):
        """
        :param direction: Vector, main axis, will be preserved if guide is not perpendicular
        :param guide: Vector or None, may change if not perpendicular to main axis
        :param main_axis: ("X", "Y", "Z", "-X", "-Y", "-Z")
        :param guide_axis: ("X", "Y", "Z")
        :return: 3 non null Vectors as x, y, z axis for orthogonal Matrix
         where direction is on main_axis, guide is on guide_axis
        """
        if guide_axis[-1:] == main_axis[-1:]:
            return X_AXIS, Y_AXIS, Z_AXIS

        if direction == ZERO:
            z = Z_AXIS
        else:
            z = direction.normalized()

        # skip invalid guide
        if guide is None:
            y = ZERO
        else:
            y = z.cross(guide.normalized())

        if y.length < 0.5:
            if guide_axis == "X":
                y = z.cross(X_AXIS)
                if y.length < 0.5:
                    y = Z_AXIS
            elif guide_axis == "Y":
                y = z.cross(Y_AXIS)
                if y.length < 0.5:
                    y = Z_AXIS
            elif guide_axis == "Z":
                y = z.cross(Z_AXIS)
                if y.length < 0.5:
                    y = Y_AXIS

        x = y.cross(z)

        unsafe = [v.length < 0.0001 for v in [x, y, z]]

        if any(unsafe):
            raise ValueError("Null vector found %s %s / %s %s %s  %s" % (direction, guide, x, y, z, unsafe))

        return cls.changeAxesDict[(main_axis, guide_axis)](x, y, z)

    def negate(self):
        ''' Recerse axis
        :return:
        '''
        self._mat.col[0] = -Vector(self._mat.col[0])
        self._mat.col[1] = -Vector(self._mat.col[1])
        self._mat.col[2] = -Vector(self._mat.col[2])
        self._update_project_matrix()

    def __copy__(self):
        return SlCadConstraint(origin=self)

    def _init_by_matrix(self, tm):
        self._mat = tm
        self._update_project_matrix()

    def _init_by_origin_and_direction(self, o, x, z):
        xl = x.length
        vx, vy, vz = self.safe_vectors(x, z)
        if xl > 0.0001:
            vx = xl * vx
        self._update_matrix(o, vx, vy, vz)

    def _update_project_matrix(self):
        x = self._axis(self._project_x).normalized()
        z = self._axis(self._project_z).normalized()
        y = z.cross(x)
        self._project_matrix = self._make_matrix(self.origin, x, y, z)

    @classmethod
    def safe_matrix(cls, o, x, z, main_axis="X", guide_axis="Z"):
        vx, vy, vz = cls.safe_vectors(x, z, main_axis, guide_axis)
        return cls._make_matrix(o, vx, vy, vz)

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
        xl = x.length
        zl = z.length
        vx, vy, vz = cls.safe_vectors(x, z)
        if xl > 0.0001:
            vx = xl * vx
        if zl > 0.0001:
            vz = zl * vz
        return cls._make_matrix(o, vx, vy, vz)

    @classmethod
    def _matrix_from_normal(cls, o, z):
        return cls.safe_matrix(o, z, Z_AXIS, "Z", "Y")

    @classmethod
    def _matrix_from_view(cls, o, z):
        dz = abs(z.dot(Z_AXIS))
        if dz == 1:
            y = Y_AXIS
        else:
            y = Z_AXIS
        return cls.safe_matrix(o, z, y, "Z", "Y")

    def set_matrix_from_view(self, o, z):
        self._mat = self._matrix_from_view(o, z)
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
        xl = x.length
        if xl < 0.0001:
            x = X_AXIS
            xl = 1
        vx, vy, vz = self.safe_vectors(x, Z_AXIS)
        vx = xl * vx
        self._update_matrix(self.origin, vx, vy, vz)

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
        if abs(d) < epsilon:
            # print("d: %.6f" % d)
            # The segment is parallel to plane
            return None
        else:
            w = origin - self.origin
            t = -p_no.dot(w) / d
            return origin + t * direction

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


def update_debug_level(self, context):
    logger.setLevel(self.debug_level)


class SlCadTextEval:
    text = ""


def header_text(self, context):
    layout = self.layout
    prefs = context.preferences.addons[__package__].preferences
    layout.label(text=SlCadTextEval.text)
    layout.label(text="Confirm", icon="EVENT_RETURN")
    layout.label(text="Cancel", icon="EVENT_ESC")

    for i, short in enumerate(prefs.keymap[10:13]):
        short.draw(layout, use_row=False, icon_only=True)
    layout.label(text="Confirm and change axis")


def header_draw(self, context):
    prefs = context.preferences.addons[__package__].preferences
    layout = self.layout
    for i, short in enumerate(prefs.keymap[:-3]):
        short.draw(layout, use_row=False)
    layout.label(text="Disable snap", icon="EVENT_CTRL")
    layout.label(text="Round", icon="EVENT_ALT")
    layout.label(text="", icon="EVENT_ALT")
    layout.label(text="Round small", icon="EVENT_SHIFT")


def draw_settings(context, layout, tool):
    prefs = context.preferences.addons[__package__].preferences
    km = context.window_manager.keyconfigs['blender addon'].keymaps['3D View Tool: Cad Transform'].keymap_items
    props = tool.operator_properties("slcad.translate")
    is_panel = context.region.type in {'UI', 'WINDOW'}

    row = layout.row()
    row.use_property_split = False
    row.prop(props, "snap_elements", text="", expand=True, icon_only=True)
    row.prop(props, "x_ray", text="", emboss=True, icon='XRAY')

    if is_panel:
        layout.separator()
        icon = "DISCLOSURE_TRI_RIGHT"
        if prefs.display_shortcuts:
            icon = "DISCLOSURE_TRI_DOWN"
        row = layout.row(align=True)
        row.use_property_split = False
        row.prop(prefs, "display_shortcuts", icon=icon, emboss=True, toggle=False)

    if prefs.display_shortcuts or not is_panel:
        layout.separator()
        layout.label(text="Tools:")
        # prefs.keymap.get("MOVE").draw(layout, use_row=True)
        # prefs.keymap.get("ROTATE").draw(layout, use_row=True)
        # prefs.keymap.get("SCALE").draw(layout, use_row=True)
        # @TODO WARNING ! this fails with numerical keys
        layout.label(text="Move", icon="EVENT_%s" % km['slcad.translate'].type)
        layout.label(text="Rotate", icon="EVENT_%s" % km['slcad.rotate'].type)
        layout.label(text="Scale", icon="EVENT_%s" % km['slcad.scale'].type)

        if is_panel:
            layout.separator()
            layout.label(text="Snap modes:")
            for i, short in enumerate(prefs.keymap):
                if i == 10:
                    layout.separator()
                    layout.label(text="Constraint:")
                elif i == 16:
                    layout.separator()
                    layout.label(text="Options")
                short.draw(layout, use_row=True)

            layout.label(text="Disable snap (hold)", icon="EVENT_CTRL")
            layout.label(text="Round (hold)", icon="EVENT_ALT")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_ALT")
            row.label(text="Round small (hold)", icon="EVENT_SHIFT")


class SLCAD_main:
    bl_idname = 'slcad.transform'
    bl_label = 'CAD Transform'
    bl_options = {'UNDO'}

    snap_elements: EnumProperty(
        name="snap_elements",
        items=(
            ('VERT', "Vertex", "Vertex", 'SNAP_VERTEX', VERT),
            ('EDGE', "Edge", "Edge", 'SNAP_EDGE', EDGE),
            ('FACE', "Face", "Face", 'SNAP_FACE', FACE),
            ('GRID', "Grid", "Grid", 'SNAP_GRID', GRID),
            ('EDGE_CENTER', "Edge Center", "Edge Center", 'SNAP_MIDPOINT', EDGE_CENTER),
            ('EDGE_PERPENDICULAR', "Edge Perpendicular", "Perpendicular", 'SNAP_PERPENDICULAR', EDGE_PERPENDICULAR),
            ('EDGE_PARALLEL', "Edge Parallel", "Edge Parallel", icon_man.icons["EDGE_PARALLEL"].icon_id, EDGE_PARALLEL),
            ('FACE_CENTER', "Face Center", "Face Center", 'SNAP_FACE_CENTER', FACE_CENTER),
            ('FACE_NORMAL', "Face Normal", "Face Normal", 'SNAP_NORMAL', FACE_NORMAL),
            ('ORIGIN', "Object origin / cursor", "Object origin / cursor", 'OBJECT_ORIGIN', ORIGIN),
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
    _copy = 0
    _duplicates = []
    _last_run = 0
    _action = 0
    _snap_average = []
    snap_from = Vector()
    _handle = None

    _draw_flags = 0
    _flags_axis = 0
    _constraint_flag = 0
    _absolute_scale = False
    _scale_dimensions = 1

    _constraint_user = None
    _constraint_local = None
    _constraint_global = None
    _constraint_edge = None
    _constraint_normal = None
    _constraint_screen = None

    _snap_widget = None
    _average_widget = None
    _average_preview_widget = None
    _preview_widget = None
    _constraint_widget = None
    _perpendicular_widget = None
    _edge_axis_widget = None
    _edge_widget = None
    _face_widget = None
    _normal_widget = None
    _grid_widget = None

    _scale_widget = None
    _move_widget = None
    _rotate_widget = None

    _matrix_world = {}
    _delta_rotation = {}
    _undo_edit = {}
    _undo = {}
    # _modifiers = {}
    _disable_snap = False
    _dirty = False

    _release_confirm = False
    _confirm_exit = True
    _real_time = False

    _default_action = MOVE
    _show_origins = False, False
    _show_grid = False, False, False, False
    _header_draw_backup = None
    _header_text_backup = None
    _pass_through_event = 'PASS_THROUGH'

    # keyboard related
    line_entered = ""
    line_pos = 0
    _units = {
        "METERS": "m",
        "CENTIMETERS": "cm",
        "MILLIMETERS": "mm",
        "KILOMETERS": "km",
        "ADAPTIVE": None,
        "MILES": "mi",
        "FEET": "'",
        "INCHES": "\"",
        "THOU": "thou"  # not supported
    }

    _keyboard_ascii = {
        ".", ",", "-", "+", "1", "2", "3",
        "4", "5", "6", "7", "8", "9", "0",
        "c", "m", "d", "k", "f", "t", "i", "n",
        " ", "/", "*", "'", "\"", "°"
        # "="
    }
    _keyboard_type = {
        'BACK_SPACE', 'DEL',
        'LEFT_ARROW', 'RIGHT_ARROW', 'RET', 'NUMPAD_ENTER'
    }

    @property
    def constraint(self):

        if self._constraint_flag & C_LOCAL:
            return self._constraint_local

        elif self._constraint_flag & C_GLOBAL:
            return self._constraint_global

        elif self._constraint_flag & C_EDGE:
            return self._constraint_edge

        elif self._constraint_flag & C_NORMAL:
            return self._constraint_normal

        elif self._constraint_flag & C_USER and self._constraint_user is not None:
            return self._constraint_user

        else:
            return self._constraint_screen

    def exit(self, context, event):

        logger.debug("exit()")

        self.change_header_draw(self._header_draw_backup)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.window.cursor_set("DEFAULT")
        overlay = context.space_data.overlay
        overlay.show_floor, overlay.show_axis_x, overlay.show_axis_y, overlay.show_ortho_grid = self._show_grid
        overlay.show_object_origins_all, overlay.show_object_origins = self._show_origins
        self._handle = None
        self._undo_edit.clear()
        self._undo.clear()
        slcadsnap.exit()
        self._apply_edit_mode_changes(context)
        global _running
        _running = False

        # self.restore_modifiers(context.active_object)
        # self._modifiers.clear()

    # def hide_modifiers(self, o):
    #     # hide modifiers from snap ..
    #     self._modifiers[o] = []
    #     for mod in o.modifiers:
    #         self._modifiers[o].append(mod.show_viewport)
    #         mod.show_viewport = False
    #
    # def restore_modifiers(self, o):
    #     if o in self._modifiers:
    #         for mod, show in zip(o.modifiers, self._modifiers[o]):
    #             mod.show_viewport = show

    def change_header_draw(self, fun):
        logger.debug("change_header_draw()")
        last = bpy.types.STATUSBAR_HT_header.draw
        bpy.types.STATUSBAR_HT_header.draw = fun
        return last

    def gl_draw(self, context):

        logger.debug("gl_draw()")

        if len(self._snap_average) > 1:
            for p in self._snap_average[1:]:
                self._average_widget.c = slcadsnap._screen_location_from_3d(p)
                self._average_widget.draw(context)
            self._average_preview_widget.c = slcadsnap._screen_location_from_3d(self.snap_average)
            self._average_preview_widget.draw(context)

        if self._draw_flags & DRAW_CONSTRAINT:
            self._constraint_widget.draw(context)

        if self._draw_flags & DRAW_PERPENDICULAR:
            self._perpendicular_widget.draw(context)

        if self._draw_flags & DRAW_PREVIEW:
            loc = self.apply_constraint(slcadsnap._snap_loc)
            self._preview_widget.c = slcadsnap._screen_location_from_3d(loc)
            self._preview_widget.draw(context)

        if self._draw_flags & DRAW_EDGE:
            self._edge_widget.draw(context)

        if self._draw_flags & DRAW_NORMAL:
            self._normal_widget.draw(context)

        if self._draw_flags & DRAW_FACE:
            self._face_widget.draw(context)

        if self._draw_flags & DRAW_GRID:
            # compute grid size and color on the fly
            self.update_grid_widget(context)
            self._grid_widget.draw(context)

        if self._draw_flags & DRAW_ROTATE:
            self._rotate_widget.draw(context)

        if self._draw_flags & DRAW_MOVE:
            self._move_widget.draw(context)

        if self._draw_flags & DRAW_SCALE:
            self._scale_widget.draw(context)

        if self._draw_flags & DRAW_EDGE_AXIS:
            self._edge_axis_widget.draw(context)

        if self._draw_flags & DRAW_SNAP:
            self._snap_widget.c = slcadsnap._screen_location_from_3d(slcadsnap._snap_loc)
            self._snap_widget.draw(context)

        if DEBUG_DRAW_GL:
            slcadsnap.gl_stack.draw()

    def set_constraint_origin(self, origin):
        self._constraint_global.origin = origin
        self._constraint_local.origin = origin
        self._constraint_screen.origin = origin

    def update_edge_constraint(self):
        self._constraint_flag = (C_USER | C_EDGE)
        if slcadsnap.snap_mode & (EDGE | EDGE_PARALLEL):
            self._flags_axis = (X | AXIS)
        elif slcadsnap.snap_mode & EDGE_PERPENDICULAR:
            self._flags_axis = (Y | AXIS)
        p0, p1 = slcadsnap.edge_points
        tM = SlCadConstraint._matrix_from_up_and_direction(p0, p1 - p0, Z_AXIS)
        self._constraint_edge._init_by_matrix(tM)
        self.set_constraint_origin(p0)
        self.snap_from = p0

    def update_normal_constraint(self):
        self._flags_axis = Z
        self._constraint_flag = (C_USER | C_NORMAL)
        p0 = slcadsnap._snap_raw.p
        tM = SlCadConstraint._matrix_from_normal(p0, slcadsnap._snap_raw.n)
        self._constraint_normal._init_by_matrix(tM)
        self.set_constraint_origin(p0)
        self.snap_from = p0

    def keyboard_event(self, context, event):
        """
        :param context:
        :param event:
        :return: True to continue, False to exit modal
        """
        k = event.type
        prefs = context.preferences.addons[__package__].preferences

        signature = (event.alt, event.ctrl, event.shift, event.type, event.value)

        if event.value == "PRESS":

            if prefs.match("DUPLICATE", signature):
                self._action |= DUPLICATE
                self._copy = 0

            if prefs.match("AVERAGE", signature):
                # average snap points
                if slcadsnap._is_snapping:
                    # 2 cases: snap from / snap to
                    pt = self.apply_constraint(slcadsnap._snap_raw.p)
                    self.push_average(pt)
                return True

            elif prefs.match("AVERAGE_CLEAR", signature):
                curr = self._snap_average[0]
                self.clear_average()
                self._snap_average[0] = curr
                return True

            elif prefs.match("SCALE_DIMENSIONS", signature):
                self._scale_dimensions = (self._scale_dimensions + 1) % 3

            elif prefs.match("SCALE_DIMENSIONS", (event.alt, event.ctrl, False, event.type, event.value)):
                # use shift to go down
                self._scale_dimensions -= 1
                if self._scale_dimensions < 0:
                    self._scale_dimensions = 2

            elif not (self._action & KEYBOARD):

                if prefs.match("WORLD_CONSTRAINT", signature):
                    self._action &= ~PIVOT
                    self._constraint_flag = C_GLOBAL
                    self.constraint._mat = Matrix()
                    self.constraint._update_project_matrix()
                    self.update_constraint(context)

                elif prefs.match("CONSTRAINT", signature) and (self._action & MOVE):

                    self._action |= PIVOT
                    self._draw_flags |= DRAW_CONSTRAINT

                    # User defined constraint axis
                    if slcadsnap.is_snapping_to_edge and (
                            slcadsnap.snap_mode & (EDGE | EDGE_PERPENDICULAR | EDGE_PARALLEL)
                    ):
                        self.update_edge_constraint()
                        self.confirm(context, event, None)

                    elif slcadsnap.is_snapping_to_normal:
                        self.update_normal_constraint()
                        self.confirm(context, event, None)

                    else:
                        # Allow snap
                        slcadsnap.clear_exclude()

                        # Clear constraint
                        self._flags_axis = 0
                        self._constraint_user = None

                        if self._constraint_flag & C_USER:
                            # Clear pivot action and constraint
                            self._action &= ~PIVOT
                            self._draw_flags &= ~DRAW_CONSTRAINT

                        else:
                            # Start pivot action
                            self._action &= ~FREEMOVE

                        self._constraint_flag = C_SCREEN

                        # update axis and widget
                        self.update_constraint(context)

                elif prefs.match("X_RAY", signature):
                    slcadsnap.x_ray = not slcadsnap.x_ray

                elif prefs.match("CLEAR_SNAP", signature):
                    slcadsnap.snap_mode = 0

                elif prefs.match("EDGE", signature):
                    slcadsnap.toggle_snap_mode(EDGE)

                elif prefs.match("EDGE_CENTER", signature):
                    slcadsnap.toggle_snap_mode(EDGE_CENTER)

                elif prefs.match("FACE_CENTER", signature):
                    slcadsnap.toggle_snap_mode(FACE_CENTER)

                elif prefs.match("FACE", signature):
                    slcadsnap.toggle_snap_mode(FACE)

                elif prefs.match("GRID", signature):
                    slcadsnap.toggle_snap_mode(GRID)
                    # self.update_grid_widget(context)

                elif prefs.match("FACE_NORMAL", signature):
                    slcadsnap.toggle_snap_mode(FACE_NORMAL)

                elif prefs.match("ORIGIN", signature):
                    slcadsnap.toggle_snap_mode(ORIGIN)

                elif prefs.match("EDGE_PERPENDICULAR", signature):
                    # Toggle exclusive
                    if slcadsnap.snap_mode & EDGE_PERPENDICULAR:
                        slcadsnap.snap_mode &= ~EDGE_PERPENDICULAR
                        slcadsnap.snap_mode |= EDGE_PARALLEL
                    elif slcadsnap.snap_mode & EDGE_PARALLEL:
                        slcadsnap.snap_mode &= ~EDGE_PARALLEL
                    else:
                        slcadsnap.snap_mode &= ~EDGE_PARALLEL
                        slcadsnap.snap_mode |= EDGE_PERPENDICULAR

                elif prefs.match("EDGE_PARALLEL", signature):
                    # Toggle exclusive
                    if slcadsnap.snap_mode & EDGE_PARALLEL:
                        slcadsnap.snap_mode &= ~EDGE_PARALLEL
                        slcadsnap.snap_mode |= EDGE_PERPENDICULAR
                    elif slcadsnap.snap_mode & EDGE_PERPENDICULAR:
                        slcadsnap.snap_mode &= ~EDGE_PERPENDICULAR
                    else:
                        slcadsnap.snap_mode &= ~EDGE_PERPENDICULAR
                        slcadsnap.snap_mode |= EDGE_PARALLEL

                elif prefs.match("VERT", signature):
                    slcadsnap.toggle_snap_mode(VERT)

                elif prefs.match("INVERT_CONSTRAINT", signature):
                    # set opposite direction for main constraint axis
                    self.constraint.negate()
                    # update transform
                    self._free_move(context, event)

                elif prefs.match("X,Y,Z,XY,XZ,YZ", signature):

                    self._change_constraint_axis(context, signature)

                    # Clear pivot flag to allow keyboard entry at call time for rotate and scale
                    if (self._action & (ROTATE | SCALE)) and not (self._action & FREEMOVE):

                        self._action &= ~PIVOT
                        self._action |= FREEMOVE

                        if self._action & ROTATE:
                            self._draw_flags |= DRAW_ROTATE

                        elif self._action & SCALE:
                            self._draw_flags |= DRAW_SCALE

                        # prevent snap to itself unless we move origin only
                        if context.mode == "OBJECT" and not context.scene.tool_settings.use_transform_data_origin:
                            slcadsnap.exclude_from_snap(context.selected_objects)

                        elif context.mode == "EDIT_MESH":
                            slcadsnap.exclude_selected_face()

                    # update transform
                    self._free_move(context, event)

                elif event.value in {"RET", "NUMPAD_ENTER"}:
                    snap_loc = self.get_snap_loc(context, event)
                    self.confirm(context, event, snap_loc)
                    return False

                elif event.ascii in self._keyboard_ascii and not (self._action & PIVOT):

                    # enter in keyboard mode only with valid ascii chars
                    self._header_text_backup = self.change_header_draw(header_text)
                    # self._constraint_backup = self.constraint.__copy__()
                    context.window.cursor_set('TEXT')

                    self._action |= KEYBOARD

            if self._action & KEYBOARD:

                # Validate entry and change axis for next one
                if prefs.match("X,Y,Z", signature):
                    confirm = (
                            ((self._flags_axis & X) and not prefs.match("X", signature)) or
                            ((self._flags_axis & Y) and not prefs.match("Y", signature)) or
                            ((self._flags_axis & Z) and not prefs.match("Z", signature))
                    )
                    self._eval_keyboard_entry(context, event, confirm)
                    self._change_constraint_axis(context, signature)
                    return True


                c = event.ascii

                if c in self._keyboard_ascii:
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

                confirm = k in {"RET", "NUMPAD_ENTER"}

                if (self._action & DUPLICATE):

                    key = prefs.key("DUPLICATE")
                    try:
                        if self.line_entered.startswith(key):
                            self._copy = max(0, int(self.line_entered[1:]) - 1)
                        else:
                            dups = self.line_entered.split(key)
                            if len(dups) == 2:
                                line_entered, ncopy = dups
                                self._copy = max(0, int(ncopy) - 1)

                        if confirm:
                            self.line_entered = ""
                            SlCadTextEval.text = ""
                            self.line_pos = 0
                            self._action &= ~KEYBOARD
                            self._action &= ~ DUPLICATE
                            context.window.cursor_set("CROSSHAIR")
                            self.change_header_draw(self._header_text_backup)

                        snap_loc = self.get_snap_loc(context, event)
                        self.transform(context, event, snap_loc)

                    except:
                        pass

                else:
                    return self._eval_keyboard_entry(context, event, confirm)

        return True

    def _change_constraint_axis(self, context, signature):
        prefs = context.preferences.addons[__package__].preferences
        # enable + toggle local global
        if prefs.match("X,YZ", signature):
            axis = X
        elif prefs.match("Y,XZ", signature):
            axis = Y
        else:
            axis = Z

        # Rotate never constraint to plane
        if self._action & ROTATE:
            constraint_to_plane = False
            same_constraint = True
        else:
            constraint_to_plane = prefs.match("XY,XZ,YZ", signature)
            # mode change from plane to axis
            same_constraint = constraint_to_plane != (self._flags_axis & AXIS)

        # toggle when same axis is set
        if (self._flags_axis & axis) and same_constraint:

            # 2 toggle local / global / disable
            if self._constraint_flag & C_USER:
                # toggle to local / global
                self._constraint_flag &= ~C_USER
                # in plane mode skip local
                if self._flags_axis & AXIS:
                    self._constraint_flag |= self._primary_constraint
                else:
                    self._constraint_flag |= self._secondary_constraint

            elif self._constraint_flag & self._primary_constraint:
                # toggle local to global
                self._constraint_flag &= ~self._primary_constraint
                self._constraint_flag |= self._secondary_constraint

            else:
                # Rotate / Scale always have a constraint
                if self._action & (ROTATE | SCALE):

                    self._constraint_flag &= ~self._secondary_constraint

                    if self._constraint_user is None:
                        self._constraint_flag |= self._primary_constraint
                    else:
                        self._constraint_flag |= C_USER
                else:
                    # Free constraint for move action
                    self._flags_axis = 0

        else:

            self._constraint_flag &= ~C_SCREEN
            # in move action last toggle state is global
            self._constraint_flag &= ~self._secondary_constraint
            self._flags_axis = axis

            if constraint_to_plane:
                self._flags_axis &= ~AXIS
            else:
                self._flags_axis |= AXIS

            # if there is a no user constraint use local one
            if self._constraint_user is None and not (self._constraint_flag & (C_EDGE | C_NORMAL)):
                self._constraint_flag |= self._primary_constraint
            else:
                self._constraint_flag |= C_USER

        self.update_constraint(context)
        # self.update_grid_widget(context)

    def _eval_keyboard_entry(self, context, event, confirm):

        if self._action & SCALE:
            value_type = "NONE"
            # use absolute scale when unit is specified
            if any([c in self.line_entered for c in "cmkdftin'\""]):
                value_type = "LENGTH"

        elif self._action & ROTATE:
            value_type = "ROTATION"

        else:
            value_type = "LENGTH"

        value = 0
        valid = False
        line_entered = self.line_entered

        try:
            # move - to first position when found at last one
            if len(line_entered) > 0:
                if line_entered[-1] == "-":
                    line_entered = "-" + line_entered[:-1]
            else:
                # use 0 on empty line, this is the best way to refresh header
                line_entered = "0"

            us = context.scene.unit_settings

            # Use custom unit when set by user
            if value_type == "LENGTH" and us.system in {"METRIC", "IMPERIAL"} and us.length_unit in self._units:
                ref_unit = self._units[us.length_unit]
            else:
                ref_unit = None

            value = bpy.utils.units.to_value(
                us.system, value_type, line_entered, str_ref_unit=ref_unit
            )

            if value_type == "LENGTH":
                value /= us.scale_length
            valid = True

        except Exception as ex:  # ValueError:
            logger.debug("%s" % ex)
            logger.debug("%s" % self.line_entered)
            pass

        SlCadTextEval.text = line_entered

        if valid:

            # Compute new snap_loc

            snap_loc = Vector()
            vl = 0
            p0, v = Vector(), Vector()

            # Move snap point along edge / normal
            if slcadsnap.is_snapping_to_edge:
                p0, p1 = slcadsnap.edge_points
                v = p1 - p0
                vl = v.length
                logger.debug("keyboard is_snapping_to_edge %s" % vl)

            elif slcadsnap.is_snapping_to_normal:
                p0, v = slcadsnap._snap_raw.p, slcadsnap._snap_raw.n
                vl = v.length
                logger.debug("keyboard is_snapping_to_normal %s" % vl)

            if vl > 0:

                pt = p0 + (value / vl * v)

                # Before current action
                # if (self._action & MOVE_SNAP_FROM) or not (self._action & FREEMOVE):
                #     # move Snap from
                #     self.snap_from = pt
                #     self.constraint.origin = pt
                #     self._action |= MOVE_SNAP_FROM
                #
                # else:
                #     # Snap to
                if self._action & PIVOT:
                    self.constraint.p1 = pt
                    self._constraint_widget.set_world_matrix(self.constraint._mat)

                elif slcadsnap.is_snapping_to_normal:
                    snap_loc = pt
                else:
                    snap_loc = self.apply_constraint(pt)

            else:

                # Compute absolute values for snap point
                if self._action & PIVOT:
                    self.constraint.move(value)
                    self._constraint_widget.set_world_matrix(self.constraint._mat)

                elif self._action & SCALE:
                    snap_loc = self.get_snap_loc(context, event)
                    p0 = self.constraint.p0
                    curr = snap_loc - p0
                    axis = curr.normalized()

                    if self._absolute_scale or value_type == "LENGTH":
                        ref = 1
                        # negative value offset from current
                        if value < 0:
                            value = curr.length + value
                    else:
                        ref = self.constraint._axis(0).length
                        # negative value offset from current
                        if value < 0:
                            value = (curr.length / ref) + value

                    logger.debug("keyboard axis %s" % axis)
                    snap_loc = p0 + value * ref * axis

                elif self._action & ROTATE:
                    snap_loc = self.constraint.project_matrix @ Vector((cos(value), sin(value), 0))

                elif self._action & MOVE:
                    p0 = self.snap_from
                    snap_loc = self.get_snap_loc(context, event)
                    snap_loc = p0 + value * (snap_loc - p0).normalized()

            self.transform(context, event, snap_loc, confirm)

            if confirm:

                self.line_entered = ""
                SlCadTextEval.text = ""
                self.line_pos = 0
                self._action &= ~KEYBOARD
                context.window.cursor_set("CROSSHAIR")
                self.change_header_draw(self._header_text_backup)
                if self._action & (PIVOT | MOVE_SNAP_FROM):
                    return True

                elif self._action & (MOVE | ROTATE | SCALE):
                    # apply scale
                    if (self._action & SCALE) and context.mode == "OBJECT":
                        self._transform_restore_rotation(context)

                    self.store_matrix_world(context)
                    return False

        return True

    def store_matrix_world(self, context):
        self._matrix_world = {o: o.matrix_world.copy() for o in context.selected_objects}

    def undo(self, context, event):
        tm = Matrix()
        for o in self._matrix_world.keys():
            self._transform(context, event, o, tm, confirm=True)

    def update_constraint(self, context):

        axis = self._flags_axis & (X | Y | Z)

        if axis > 0:
            self._draw_flags |= DRAW_CONSTRAINT
        else:
            self._draw_flags &= ~DRAW_CONSTRAINT

        if axis > 0:

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

            self.constraint.set_project_axis(direction)
            self.constraint.set_project_normal(normal)

        # setup color and axis
        if self._action & ROTATE:
            self.update_rotate_widget(context)

        elif self._action & MOVE:
            self.update_move_widget(context)

        elif self._action & SCALE:
            self.update_scale_widget(context)

        self._constraint_widget.set_world_matrix(self.constraint._mat)
        self._constraint_widget.set_display_axis(self._flags_axis)

    def apply_constraint(self, pt):

        is_edge = slcadsnap.is_snapping_to_edge and (slcadsnap.snap_mode & EDGE)
        use_axis = (self._flags_axis & AXIS) and not (self._action & ROTATE)

        if slcadsnap.is_snapping_to_perpendicular:
            # perpendicular to edge
            p0, p1 = slcadsnap.edge_points
            t = slcadsnap._ray_segment_t(p0, p1, self.constraint.origin, self.constraint.project_normal)
            if t is None:
                # edge is parallel to constraint, there are infinite solutions
                logger.debug("perpendicular: parallel, degrade to closest point on constraint axis")
                pt = self.constraint.project_to_axis(pt)
            else:
                pt = slcadsnap.lerp(p0, p1, t)
            # will only constraint to a plane
            is_edge = False
            use_axis = False

        elif slcadsnap.is_snapping_to_parallel:
            # parallel to edge
            p0, p1 = slcadsnap.edge_points
            v = p1 - p0
            p0, p1 = self.constraint.origin, self.constraint.origin + v
            t = slcadsnap._point_segment_t(p0, p1, pt)
            # parallel bypass constraint
            return slcadsnap.lerp(p0, p1, t)

        elif slcadsnap.is_snapping_to_normal:
            # normal bypass any constraint
            return pt

        if self._flags_axis & (X | Y | Z):

            if self._constraint_flag & C_USER:
                c = self.constraint
            else:
                c = self.constraint.__copy__()
                c.origin = self.snap_from

            if is_edge and use_axis:
                # Intersection of constraint axis and edge
                p0, p1 = slcadsnap.edge_points
                # are parallel ?
                # in scale mode, always use the x axis of the source constraint
                t = slcadsnap._ray_segment_t(p0, p1, c.origin, c.project_axis)

                # print("is_edge and use_axis t:", t)

                if t is None:
                    logger.debug("edge: parallel, degrade to closest point on constraint axis")

                else:
                    pt = slcadsnap.lerp(p0, p1, t)

                pt = c.project_to_axis(pt)

            elif use_axis:  # and not (self._action & ROTATE):
                pit = None

                if slcadsnap.is_snapping_to_face:
                    # face plane by matrix
                    tm = SlCadConstraint._matrix_from_normal(slcadsnap._snap_raw.p0, slcadsnap._snap_raw.n)
                    cf = SlCadConstraint(tm)
                    pit = cf.intersect(self.constraint.origin, self.constraint.project_axis)

                if pit is None:
                    # nearest point on constraint axis, perpendicular to constraint axis
                    # fallback to nearest point on constraint plane
                    pt = c.project_to_axis(pt)
                else:
                    pt = pit

            elif is_edge and (self._action & ROTATE):
                # intersection of edge and plane
                p0, p1 = slcadsnap.edge_points
                pit = c.intersect(p0, p1 - p0)
                if pit is None:
                    # fallback to nearest point on constraint plane
                    pt = c.project_to_plane(pt)
                else:
                    pt = pit
            else:
                # nearest point on constraint plane
                pt = c.project_to_plane(pt)

        return pt

    def get_snap_loc(self, context, event):
        """
        Compute snap location update snap widgets and apply constraints
        :param context:
        :param event:
        :return: Vector
        """
        self._draw_flags &= ~DRAW_EDGE
        self._draw_flags &= ~DRAW_FACE
        self._draw_flags &= ~DRAW_NORMAL
        self._draw_flags &= ~DRAW_PREVIEW

        overlay = context.space_data.overlay

        if slcadsnap.snap_mode & GRID:
            # limit to plane mode ?
            overlay.show_floor, overlay.show_axis_x, overlay.show_axis_y, overlay.show_ortho_grid = \
                False, False, False, False
            self._draw_flags |= DRAW_GRID
        else:
            overlay.show_floor, overlay.show_axis_x, overlay.show_axis_y, overlay.show_ortho_grid = self._show_grid
            self._draw_flags &= ~DRAW_GRID

        if slcadsnap.snap_mode & ORIGIN:
            overlay.show_object_origins_all, overlay.show_object_origins = True, True
        else:
            overlay.show_object_origins_all, overlay.show_object_origins = self._show_origins

        if slcadsnap._is_snapping:

            # Display snap point
            snap_loc = slcadsnap._snap_loc
            self._draw_flags |= DRAW_SNAP

            # Display snap preview
            if self._flags_axis & (X | Y | Z):
                self._draw_flags |= DRAW_PREVIEW

            # Display edge overlay
            if slcadsnap.is_snapping_to_edge:
                p0, p1 = slcadsnap.edge_points
                tM = SlCadConstraint._matrix_from_up_and_direction(p0, p1 - p0, -slcadsnap.ray_direction)
                self._edge_widget.set_world_matrix(tM)
                self._draw_flags |= DRAW_EDGE

            # Display face overlay
            if slcadsnap.is_snapping_to_face:
                self._face_widget.set_coords(slcadsnap._snap_raw._pts)
                self._draw_flags |= DRAW_FACE

            if slcadsnap.is_snapping_to_normal:
                tM = SlCadConstraint._matrix_from_normal(slcadsnap._snap_raw.p, slcadsnap._snap_raw.n)
                self._normal_widget.set_world_matrix(tM)
                self._draw_flags |= DRAW_NORMAL

        else:
            # project view ray over constraint plane

            if self._flags_axis & (X | Y | Z):

                c = self.constraint

                p0 = c.origin

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
                    if snap_loc is None:
                        snap_loc = p0

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
                        if t is None:
                            # parallel segments
                            logger.debug("behind view, ray parallel to view")
                            t = 0
                        snap_loc = p0 + t * v

            else:

                # use a plane perpendicular to view
                self._constraint_screen.set_matrix_from_view(self.snap_from, -slcadsnap.ray_direction)
                p_co, p_no = self._constraint_screen.p0, self._constraint_screen.project_normal
                snap_loc = slcadsnap._mouse_to_plane(p_co=p_co, p_no=p_no)

            self._draw_flags &= ~DRAW_SNAP

        if slcadsnap.is_snapping_to_parallel:
            p0, p1 = slcadsnap.edge_points
            snap_loc = self.constraint.origin + p1 - p0

        pt = self.apply_constraint(snap_loc)

        self._draw_flags &= ~DRAW_EDGE_AXIS
        self._draw_flags &= ~DRAW_PERPENDICULAR

        # compute perpendicular widget matrix
        if slcadsnap.is_snapping_to_perpendicular:
            # p is along snapped edge
            p0, p1 = slcadsnap.edge_points
            c = self.constraint.__copy__()
            c.origin = p0
            p1 = c.project_to_plane(p1)
            t = slcadsnap._ray_segment_t(p0, p1, self.constraint.origin, self.constraint.project_normal)

            if t is None or abs(t) > 10000:
                logger.debug("perpendicular, segment parallel to constraint project_to_axis")
                p = c.project_to_plane(pt)

            else:
                p = slcadsnap.lerp(p0, p1, t)

            # pt is p projected on constraint plane
            x = self.constraint.origin - pt
            y = p0 - p
            z = p - pt
            tM = SlCadConstraint._make_matrix(pt, x, y, z)
            self._perpendicular_widget.set_world_matrix(tM)
            self._draw_flags |= DRAW_PERPENDICULAR

        elif slcadsnap.is_snapping_to_parallel or (self._action & ROTATE):
            # skip edge axis widget
            pass

        elif slcadsnap.is_snapping_to_edge and (self._flags_axis & AXIS):
            # compute edge axis widget matrix

            p0, p1 = slcadsnap.edge_points
            t = slcadsnap._ray_segment_t(p0, p1, self.constraint.origin, self.constraint.project_axis)
            if t is None or abs(t) > 10000:
                logger.debug("edge, segment parallel to constraint project_to_axis")
                p = self.constraint.project_to_axis(pt)
                pt = p
                p0 = snap_loc
            else:
                p = slcadsnap.lerp(p0, p1, t)
                pt = self.constraint.project_to_axis(p)

            # pt is p projected on constraint axis
            x = self.constraint.origin - pt
            y = p0 - p
            z = p - pt
            tM = SlCadConstraint._make_matrix(pt, x, y, z)
            self._edge_axis_widget.set_world_matrix(tM)
            self._draw_flags |= DRAW_EDGE_AXIS

        return pt

    def confirm(self, context, event, snap_loc):
        # Constraint so snap target is predictable for rotation and scale
        logger.debug("confirm %s  c: %s  axis: %s" % (
            debug_action(self._action),
            debug_constraint(self._constraint_flag),
            debug_axis(self._flags_axis)
        ))

        if self._action & PIVOT:

            self._action &= ~PIVOT

            if snap_loc is not None:
                self.constraint.p1 = snap_loc

            if not (self._constraint_flag & (C_EDGE | C_NORMAL)):
                self._flags_axis = AXIS

                if self._action & ROTATE:
                    self._flags_axis |= Z

                elif self._action & SCALE:
                    self._flags_axis |= X

            if self._action & ROTATE:
                self._draw_flags |= DRAW_ROTATE

            elif self._action & SCALE:
                self._draw_flags |= DRAW_SCALE

            # update constraint widget and axis
            self.update_constraint(context)

            if (self._action & MOVE) and not (self._constraint_flag & (C_EDGE | C_NORMAL)):
                # MOVE wait for a snap_from to start unless an edge or normal constraint are set
                self._action &= ~FREEMOVE

            elif context.mode == "OBJECT":
                # ROTATE and SCALE start right here
                # MOVE wait a new click to start

                if self._action & SCALE:
                    # apply object's rotation to match constraint axis
                    self._transform_apply_rotation_and_scale(context)
                    self.store_matrix_world(context)
                    logger.debug("_transform_apply_rotation_and_scale %s" % len(self._delta_rotation))

                # exclude by click in modal for MOVE
                # prevent snap to itself unless we move origin only
                if self._action & (ROTATE | SCALE) and not context.scene.tool_settings.use_transform_data_origin:
                    slcadsnap.exclude_from_snap(context.selected_objects)

            if self._action & (ROTATE | SCALE) and context.mode == "EDIT_MESH":
                slcadsnap.exclude_selected_face()

            return False

        elif self._action & (MOVE | ROTATE | SCALE):
            self.transform(context, event, snap_loc)
            # reset rotation for objects in scale mode
            logger.debug("_transform_restore_rotation %s" % len(self._delta_rotation))

        if self._action & SCALE:  # and context.mode == "OBJECT":
            self._transform_restore_rotation(context)

        slcadsnap.clear_exclude()

        self.snap_from = Vector()
        # Keep last action ?
        self._draw_flags = 0
        self._flags_axis = 0
        self._constraint_flag = 0
        self._action = 0
        self._duplicates.clear()

        return self._confirm_exit

    def update_grid_widget(self, context):

        tm = self.constraint.project_matrix

        if slcadsnap.snap_mode & GRID:
            # region = context.region
            v3d = context.space_data
            r3d = v3d.region_3d
            viewinv = r3d.view_matrix.inverted()
            if r3d.is_perspective:
                ray_origin = viewinv.translation.copy()
            else:
                persinv = r3d.perspective_matrix.inverted()

                ray_origin = (persinv.col[0].xyz +
                              persinv.col[1].xyz +
                              viewinv.translation)

            view_z = r3d.view_matrix.row[2].xyz
            d = 0
            if r3d.is_perspective:
                pt = self.constraint.intersect(ray_origin, view_z)
                if pt is None:
                    pt = self._constraint_screen.origin
                d = (pt - ray_origin).length

            if d == 0:
                d = abs(r3d.view_distance)

            largeur = max(0.0001, 2 * d / v3d.lens * 36)

            grid_size = 1e32
            while grid_size > largeur:
                grid_size /= 10

            # snap depends on precise grid size, remove rounding error
            grid_size = round(grid_size, 5)

            logger.debug("grid_size:%s screen:%.2f distance:%.2f" % (grid_size, largeur, d))

            sm = Matrix.Scale(grid_size, 4)
            tm_axis = tm = tm @ sm
            # is center on screen ?
            if slcadsnap.is_not_on_screen(tm.translation):
                pt = self.constraint.intersect(ray_origin, view_z)
                if pt is not None:
                    pt = self.constraint.project_matrix.inverted() @ pt
                    offset = Vector([round(v / grid_size, 0) for v in pt]) * grid_size
                    logger.debug("center: %s   offset: %s" % (pt, offset))
                    tm = self.constraint.project_matrix @ Matrix.Translation(offset) @ sm

            r, g, b, a = context.preferences.themes[0].view_3d.grid[0:4]
            # grid size is lower than view, but size of grid is 10
            a0, a1 = a, min(a, 2 * a * grid_size / largeur)
            # print(a0, a1)
            self._grid_widget.set_world_matrix(tm, tm_axis)
            self._grid_widget.set_color((r, g, b, a0), (r, g, b, a1))

        return tm

    def modal(self, context, event):

        if context.area is not None:
            context.area.tag_redraw()

        t = time.time()

        # fix issue #3
        # Events may fire faster than modal is able to consume
        # stacked events continue to fire past user action
        if (t - self._last_run) < 0.005:
            # do not skip important events
            if not (
                    event.type in {'LEFTMOUSE', 'ESC', 'RIGHTMOUSE'} or
                    event.type in self._keyboard_type or
                    event.ascii in self._keyboard_ascii
            ):
                logger.debug("Modal skip event to prevent overflow  %s %s" % (event.type, event.value))
                # allow events to bubble up eg view navigation using alt + middle mouse
                return {'PASS_THROUGH'}

        prefs = context.preferences.addons[__package__].preferences

        logger.debug("Modal body start  %s %s" % (event.type, event.value))

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == "PRESS":

            if self._action & KEYBOARD:

                if self._action & PIVOT:
                    # escape from user constraint
                    self._constraint_flag &= ~C_USER
                    self._constraint_flag |= C_GLOBAL
                    self._constraint_user = None
                    self.update_constraint(context)

                self.line_entered = ""
                self.line_pos = 0

                if self._action & DUPLICATE:
                    self._copy = 0

                else:
                    self._eval_keyboard_entry(context, event, False)

                self.change_header_draw(self._header_text_backup)
                self._action &= ~KEYBOARD
                self._action &= ~ DUPLICATE
                context.window.cursor_set("CROSSHAIR")
                self._last_run = time.time()
                return {'RUNNING_MODAL'}

            elif not (self._action & PIVOT):
                slcadsnap.clear_exclude()
                self.undo(context, event)

            if self._action & SCALE:  # and context.mode == "OBJECT":
                self._transform_restore_rotation(context)

            self.exit(context, event)
            return {'FINISHED'}

        elif context.region_data is None:
            logger.debug("Region_data is none")

        elif context.active_object is None:
            logger.debug("Active_object is none")

        elif event.type in self._keyboard_type or event.ascii in self._keyboard_ascii:

            if prefs.use_numpad_for_navigation and "NUMPAD_" in event.type:
                return {'PASS_THROUGH'}

            logger.debug("Keyboard_event %s %s" % (event.type, event.value))
            if self.keyboard_event(context, event):
                self._last_run = time.time()
                return {'RUNNING_MODAL'}

            elif self._confirm_exit:
                self.exit(context, event)
                return {'FINISHED'}

        elif event.type in {'LEFTMOUSE'}:

            if self._action == 0:
                # should never occur
                logger.debug("Action == 0")

            else:

                snap_loc = self.get_snap_loc(context, event)
                snap_loc = self.temp_average(snap_loc)

                if snap_loc is None:
                    logger.debug("Snap_loc is None")

                else:

                    if event.value == "PRESS":

                        if not (self._action & FREEMOVE):
                            # click/release cycle 1

                            if self._action & PIVOT:

                                self._constraint_flag &= ~C_SCREEN

                                if self._action & MOVE_SNAP_FROM:
                                    snap_loc = self.snap_from

                                # confirm will bypass step2
                                if slcadsnap.is_snapping_to_edge and (
                                        slcadsnap.snap_mode & (EDGE | EDGE_PERPENDICULAR | EDGE_PARALLEL)
                                ):
                                    self.update_edge_constraint()
                                    self.confirm(context, event, None)

                                elif slcadsnap.is_snapping_to_normal:
                                    self.update_normal_constraint()
                                    self.confirm(context, event, None)

                                else:
                                    # Create a user constraint
                                    self._constraint_flag |= C_USER
                                    self._constraint_user = SlCadConstraint(
                                        context.active_object.matrix_world.normalized()
                                    )
                                    # setup constraint origin
                                    self._constraint_user.origin = snap_loc
                                    self.set_constraint_origin(snap_loc)
                                    # update axis and widget
                                    self.update_constraint(context)

                                self._draw_flags |= DRAW_CONSTRAINT

                            else:
                                # only MOVE reach this point
                                # prevent snap to itself unless we move origin only
                                if context.mode == "OBJECT" and \
                                        not context.scene.tool_settings.use_transform_data_origin:
                                    slcadsnap.exclude_from_snap(context.selected_objects)

                                elif context.mode == "EDIT_MESH":
                                    # print("exclude_selected_face")
                                    slcadsnap.exclude_selected_face()

                                # set constraint origins (all but C_USER)
                                if not (self._constraint_flag & C_USER):
                                    self.set_constraint_origin(snap_loc)

                            # Store initial state
                            self.store_matrix_world(context)

                            # snap from is constraint origin for rotate and scale
                            self.snap_from = snap_loc

                            self.clear_average()
                            self._action &= ~MOVE_SNAP_FROM
                            self._action |= FREEMOVE

                        elif not self._release_confirm:
                            # click to confirm
                            if self.confirm(context, event, snap_loc):
                                self.exit(context, event)
                                return {'FINISHED'}

                    elif event.value == "RELEASE" and self._release_confirm:

                        if self._action & FREEMOVE:
                            # release to confirm
                            if self.confirm(context, event, snap_loc):
                                self.exit(context, event)
                                return {'FINISHED'}

                    self._last_run = time.time()
                    return {'RUNNING_MODAL'}

        elif event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            # when keyboard is active disallow mouse input
            if not (self._action & KEYBOARD):
                self._free_move(context, event)

        elif (event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} and event.ctrl) or \
              event.type in {'UP_ARROW', 'DOWN_ARROW'} and event.value == "PRESS":
            offset = -1
            if "UP" in event.type:
                offset = 1
            self._copy = max(0, self._copy + offset)

            if self._action & (MOVE | ROTATE | SCALE):
                snap_loc = self.get_snap_loc(context, event)
                self.transform(context, event, snap_loc)

        self._last_run = time.time()
        logger.info("Modal body end %.4f" % (self._last_run - t))

        return {'PASS_THROUGH'}

    def push_average(self, snap_loc):
        if snap_loc is not None:
            self._snap_average.append(snap_loc)

    def temp_average(self, snap_loc):
        if snap_loc is not None:
            self._snap_average[0] = snap_loc
        return self.snap_average

    def clear_average(self):
        self._snap_average = [Vector()]

    @property
    def snap_average(self):
        v = self._snap_average[0].copy()
        for p in self._snap_average[1:]:
            v += p
        return v / len(self._snap_average)

    def _free_move(self, context, event):

        if event.ctrl or self._disable_snap:
            slcadsnap._is_snapping = False
            # refresh view origin and direction
            logger.debug("slcadsnap.event_origin_and_direction")
            slcadsnap.event_origin_and_direction(event)

        else:
            logger.debug("slcadsnap.snap")
            grid_matrix = self.update_grid_widget(context)
            slcadsnap.snap(context, event, grid_matrix)

        snap_loc = self.get_snap_loc(context, event)
        snap_loc = self.temp_average(snap_loc)

        if (self._action & FREEMOVE) and snap_loc is not None:

            if self._action & PIVOT:
                # set pivot direction on free move after 1 st press/release cycle
                self.constraint.p1 = snap_loc
                self._constraint_widget.set_world_matrix(self.constraint._mat)
                # start drawing pivot
                self._draw_flags |= DRAW_CONSTRAINT

            else:

                # use screen as constraint
                if self._constraint_flag & C_SCREEN:
                    self._constraint_screen.set_matrix_from_view(self.snap_from, -slcadsnap.ray_direction)

                self.transform(context, event, snap_loc, confirm=False)

    def transform(self, context, event, snap_loc, confirm=True):

        logger.debug("transform %s  c: %s  axis: %s" % (
            debug_action(self._action),
            debug_constraint(self._constraint_flag),
            debug_axis(self._flags_axis)
        ))

        if self._action & MOVE:
            if slcadsnap.is_snapping_to_normal:
                delta = snap_loc
            else:
                delta = snap_loc - self.snap_from

            self._move(context, event, delta, confirm)

        elif self._action & ROTATE:
            loc = self.constraint.project_matrix.inverted() @ snap_loc
            angle = atan2(loc.y, loc.x)
            self._rotate(context, event, angle, confirm)

        elif self._action & SCALE:
            ref = self.constraint._axis(0).length
            if ref > 0:
                delta = snap_loc - self.constraint.origin
                self._scale(context, event, delta, confirm)

    def color_by_axis(self, context, axis, alpha):
        theme = context.preferences.themes[0].user_interface
        r, g, b = theme.axis_z
        if axis == 0:
            r, g, b = theme.axis_x
        elif axis == 1:
            r, g, b = theme.axis_y
        return r, g, b, alpha

    def update_move_widget(self, context):
        # Display move widget
        if self._flags_axis & AXIS and self._flags_axis & (X | Y | Z):
            axis = self.constraint._project_x
            color = self.color_by_axis(context, axis, 0.7)
        else:
            color = (0, 0, 0, 0.7)
        self._move_widget.set_color(color)

    def update_scale_widget(self, context):
        # Display move widget
        if self._flags_axis & AXIS and self._flags_axis & (X | Y | Z):
            axis = self.constraint._project_x
            color = self.color_by_axis(context, axis, 0.7)
        else:
            color = (0, 0, 0, 0.7)
        self._scale_widget.set_color(color)
        self._scale_widget.ref = self.constraint.direction.length

        tM = SlCadConstraint._matrix_from_up_and_direction(
            self.snap_from,
            self.constraint.direction,
            -slcadsnap.ray_direction
        )
        self._scale_widget.set_world_matrix(tM)

    def update_rotate_widget(self, context):
        axis = self.constraint._project_z
        color = self.color_by_axis(context, axis, 0.7)
        tM = self.constraint.project_matrix @ Matrix.Scale(self.constraint.direction.length, 4)
        self._rotate_widget.set_world_matrix(tM)
        self._rotate_widget.set_color(color)

    def sign(self, value, positive):
        if positive:
            return abs(value)
        else:
            return -abs(value)

    def _move(self, context, event, delta, confirm):

        dist = delta.length

        # Rounding
        if event.alt and dist > 0:
            slog = ceil(log10(dist))
            sfac = pow(10, slog)
            if event.shift:
                step = 0.01 * sfac
            else:
                step = 0.05 * sfac
            dist = dist - (dist % step)
            delta = dist * delta.normalized()

        if slcadsnap.is_snapping_to_normal:

            logger.debug("move: normal")

            tm = self.constraint.project_matrix

            if not confirm:
                # move slightly over target so snap will not skip coplanar faces
                delta += 2 * slcadsnap._cast_threshold * slcadsnap._snap_raw.n

            if self._flags_axis & Y:
                up = -Z_AXIS
            else:
                up = Z_AXIS

            x, y, z = SlCadConstraint.safe_vectors(slcadsnap._snap_raw.n, up, "Z", "Y")
            trs = tm.inverted() @ SlCadConstraint._make_matrix(delta, x, y, z).normalized()

            # align with normal
            delta = delta - self.snap_from

        else:
            t, r, s = self.constraint.project_matrix.decompose()
            rm = r.to_matrix().normalized().to_4x4()
            trs = Matrix.Translation(rm.inverted() @ delta)

        tM = SlCadConstraint._matrix_from_up_and_direction(self.snap_from, delta, -slcadsnap.ray_direction)
        self._move_widget.set_world_matrix(tM)

        if dist > 0:
            self._draw_flags |= DRAW_MOVE
        else:
            self._draw_flags &= ~DRAW_MOVE

        if self._real_time or confirm:
            # absolute move in constraint space
            for o, tm in self._matrix_world.items():
                self._transform(context, event, o, trs, confirm)

    def _rotate(self, context, event, a, confirm):
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

        if self._real_time or confirm:

            # if "EDIT" in context.mode: # == "EDIT_MESH":
            # Absolute rotation in constraint space
            trs = Matrix.Rotation(angle, 4, "Z")
            for o, tm in self._matrix_world.items():
                self._transform(context, event, o, trs, confirm)

    def _scale(self, context, event, delta, confirm):
        """Scale, in object mode mimic edit mode scaling, keep final objects scale at 1 (apply scale)
        :param context:
        :param event:
        :param delta:
        :param confirm:
        :return:
        """
        prefs = context.preferences.addons[__package__].preferences

        origin = self.constraint.origin
        ref = self.constraint._axis(0).length

        dist = delta.length

        if ref == 0 or dist == 0:
            return

        # scale diff from 1
        fac = (dist - ref) / ref

        if fac == 0:
            return

        direction = delta.normalized()

        if event.alt:
            if prefs.absolute_scale:
                if dist > 0:
                    slog = ceil(log10(dist))
                    sfac = pow(10, slog)
                    if event.shift:
                        step = 0.01 * sfac
                    else:
                        step = 0.05 * sfac
                    dist = dist - (dist % step)
                    fac = (dist - ref) / ref

            else:
                if event.shift:
                    step = 0.01
                else:
                    step = 0.05
                fac = fac - (fac % step)

        if fac == 0:
            return

        tM = SlCadConstraint._matrix_from_up_and_direction(
            origin,
            ref * (1 + fac) * direction,
            -slcadsnap.ray_direction
        )

        self._scale_widget.set_world_matrix(tM)

        if self._real_time or confirm:
            # from world to pivot
            pivot = self.constraint.project_matrix
            # pivot_inverse = pivot.inverted()
            # delta vector in world space
            axis = fac * direction

            # Absolute scale in constraint space, disallow negative scale
            t, rq, s = pivot.decompose()
            rm = rq.to_matrix().normalized().to_4x4()
            x, y, z = [(1 + self.sign(j, fac >= 0)) for j in rm.inverted() @ axis]

            if self._scale_dimensions == 0:
                y, z = 1, 1

            elif self._scale_dimensions == 1:
                y, z = x, 1

            elif self._scale_dimensions == 2:
                y, z = x, x

            trs = Matrix([
                [x, 0, 0, 0],
                [0, y, 0, 0],
                [0, 0, z, 0],
                [0, 0, 0, 1]
            ])
            for o, tm in self._matrix_world.items():
                self._transform(context, event, o, trs, confirm)

    def _store_children_transform(self, o):
        return [child.matrix_world.copy() for child in o.children]

    def _reset_children_transform(self, o, ct):
        if len(ct) > 0:
            for tm, child in zip(ct, o.children):
                child.matrix_world = tm

    def _transform(self, context, event, o, tm, confirm):
        ts = context.scene.tool_settings
        if o.mode == "OBJECT" and context.mode == "OBJECT":
            # tm is absolute about constraint
            space = self.constraint.project_matrix
            trs = space @ tm @ space.inverted() @ self._matrix_world[o]

            # Transform in object mode
            _ct = []
            if ts.use_transform_skip_children:
                # transform only parent
                _ct = self._store_children_transform(o)

            if ts.use_transform_data_origin:
                # transform origin
                self._make_unique_obdata(o)
                if self._action & ROTATE:
                    # origin_set does not respect rotation ..
                    self._rec_align_rotation(o, trs)

                loc = context.scene.cursor.location
                context.scene.cursor.location = trs.translation
                with context_override(context, o, [o]) as ctx:
                    bpy.ops.object.origin_set(ctx, type='ORIGIN_CURSOR')
                context.scene.cursor.location = loc

            elif ts.use_transform_pivot_point_align:
                # translate only pivot
                o.matrix_world.translation = trs.translation

            else:
                # regular transform
                o.matrix_world = trs
                # Instance trs, lerp work for translation only
                # Lerp and instance objects
                dups = self._duplicate_object(o)
                # neutral
                _tm = Matrix()
                for i, new_o in enumerate(dups):
                    # o goes to 1, other from [0 .. -1]
                    fac = i / self._copy
                    new_o.matrix_world = space @ _tm.lerp(tm, fac) @ space.inverted() @ self._matrix_world[o]

            self._reset_children_transform(o, _ct)

        elif o.mode == "EDIT":
            # Transform in edit mode
            # tm in constraint space

            if o in self._undo_edit:
                undo = self._undo_edit[o]
            else:
                undo = Matrix()

            # Pre-transform in object's space
            space = o.matrix_world.inverted() @ self.constraint.project_matrix
            trs = space @ tm @ space.inverted()
            self._undo_edit[o] = trs.inverted()

            trs = trs @ undo

            logger.debug("%s %s %s" % (context.mode, o.type, o.mode))

            if context.mode == "EDIT_MESH" and o.type == "MESH":

                bm = bmesh.from_edit_mesh(o.data)
                verts = [v for v in bm.verts if v.select]

                if len(verts) > 0:
                    bmesh.ops.transform(bm, matrix=trs, space=Matrix(), verts=verts)

                    # destructive, enable only on confirm
                    if confirm and ts.use_mesh_automerge:
                        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=ts.double_threshold)

                bmesh.update_edit_mesh(o.data, loop_triangles=True, destructive=ts.use_mesh_automerge)
                o.update_from_editmode()

            elif context.mode == "EDIT_CURVE" and o.type == "CURVE":

                for spline in o.data.splines:
                    # fix issue #9
                    if spline.type in {'POLY', 'NURBS'}:
                        for p in spline.points:
                            if p.select:
                                p.co = (trs @ p.co.to_3d()).to_4d()

                    elif spline.type == "BEZIER":
                        for p in spline.bezier_points:
                            if p.select_control_point:
                                p.co = trs @ p.co
                            if p.select_left_handle:
                                p.handle_left = trs @ p.handle_left
                            if p.select_right_handle:
                                p.handle_right = trs @ p.handle_right

    def _clean_datablock(self, o, d):
        if d and d.users == 1:
            getattr(bpy.data, o.type.lower()).remove(d)

    def _duplicate_object(self, o):
        dups = len(self._duplicates)
        for i in range(self._copy, dups):
            if self._duplicates:
                new_o = self._duplicates.pop()
                for coll in new_o.users_collection:
                    coll.objects.unlink(new_o)
                self._clean_datablock(new_o, new_o.data)
                bpy.data.objects.remove(new_o)

        if self._copy > 0:
            for i in range(dups, self._copy):
                new_o = o.copy()
                if self._action & (MOVE | ROTATE):
                    # in move mode we may create instances
                    d = new_o.data
                    new_o.data = o.data
                    self._clean_datablock(new_o, d)
                for coll in o.users_collection:
                    if new_o.name not in coll:
                        coll.objects.link(new_o)
                self._duplicates.append(new_o)
        return self._duplicates

    def _make_unique_obdata(self, o):
        """Make object unique as we can't apply object's transform on shared data
        :param context:
        :param o:
        :return:
        """
        if o.data is not None and o.data.users > 1:
            o.data = o.data.copy()
            try:
                o.data.update_flag()
            except:
                pass

    def _rotate_only_parent(self, o, rot):
        _ct = self._store_children_transform(o)
        o.matrix_world = rot @ o.matrix_world
        self._reset_children_transform(o, _ct)

    def _apply_transform_to_curve(self, o, tm):
        for spline in o.data.splines:
            # fix issue #9
            if spline.type in {'POLY', 'NURBS'}:
                for p in spline.points:
                    p.co = (tm @ p.co.to_3d()).to_4d()
            elif spline.type == "BEZIER":
                for p in spline.bezier_points:
                    p.co = tm @ p.co
                    p.handle_left = tm @ p.handle_left
                    p.handle_right = tm @ p.handle_right

    def _apply_transform_to_mesh(self, o, tm):
        if o.mode == "EDIT":
            bm = bmesh.from_edit_mesh(o.data)
        else:
            bm = bmesh.new(use_operators=True)
            bm.from_mesh(o.data)
        # apply both rotation and scale
        bmesh.ops.transform(bm, matrix=tm, space=Matrix(), verts=bm.verts[:])
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bm.normal_update()
        if o.mode == "EDIT":
            bmesh.update_edit_mesh(o.data, loop_triangles=False, destructive=False)
        else:
            bm.to_mesh(o.data)
            bm.free()

    def _apply_transform(self, o, tm):
        if o.type == "MESH":
            self._apply_transform_to_mesh(o, tm)
        elif o.type == "CURVE":
            self._apply_transform_to_curve(o, tm)
        elif o.type =="EMPTY" and o.empty_display_type == "IMAGE":
            # apply scale to reference image size, use x axis as reference
            o.empty_display_size *= tm.to_scale().x

    def _rec_apply_scale(self, o):
        """Apply scale part to mesh including hierarchy, preserve rotation
        """
        self._make_unique_obdata(o)
        tm = o.matrix_world
        cm = [self._rec_apply_scale(c) for c in o.children]
        rot = tm.to_quaternion().to_matrix().to_4x4()
        trs = Matrix.Translation(tm.translation)
        self._apply_transform(o, rot.inverted() @ trs.inverted() @ tm)
        trx = trs @ tm.normalized().to_quaternion().to_matrix().to_4x4()
        o.matrix_world = trx.copy()
        self._reset_children_transform(o, cm)
        return trx

    def _rec_align_rotation(self, o, rm):
        cm = [self._rec_align_rotation(c, rm) for c in o.children]
        tm = o.matrix_world
        itm = tm.inverted().normalized()
        r = (itm @ rm).to_3x3().normalized().to_4x4()
        self._apply_transform(o, r.inverted())
        trx = tm @ r
        o.matrix_world = trx.copy()
        self._delta_rotation[o] = (itm @ trx).to_3x3().normalized().to_4x4()
        self._reset_children_transform(o, cm)
        return trx

    def _transform_restore_rotation(self, context):
        """Apply object scale and restore rotation
        :param context:
        :return:
        """
        context.view_layer.update()

        for o in context.selected_objects:
            self._rec_apply_scale(o)

        context.view_layer.update()

        for o, rot in self._delta_rotation.items():
            cm = self._store_children_transform(o)
            self._apply_transform(o, rot)
            o.matrix_world = o.matrix_world @ rot.inverted()
            self._reset_children_transform(o, cm)

        self._delta_rotation.clear()

    def _transform_apply_scale(self, context):
        # sanity check, fix zero scale preserve hierarchy
        update_matrix = False
        for o in context.scene.objects:
            if any([x == 0 for x in o.scale]):
                update_matrix = True
                self._rec_apply_scale(o)
        if update_matrix:
            context.view_layer.update()

    def _transform_apply_rotation_and_scale(self, context):
        """Apply object rotation + scale so axis match with constraint
        :param context:
        :return:
        """
        for o in context.selected_objects:
            self._rec_apply_scale(o)

        # update matrix_world..
        context.view_layer.update()

        tm = self.constraint.project_matrix
        self._delta_rotation = {}

        for o in context.selected_objects:
            self._rec_align_rotation(o, tm)

        # update matrix_world..
        context.view_layer.update()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def _apply_edit_mode_changes(self, context):
        # update object data from change so snap can see them
        if context.mode == "EDIT_MESH":
            for o in context.selected_objects:
                if o.mode == "EDIT":
                    o.update_from_editmode()

    def init_prefs(self, context, prefs):

        self._keyboard_type = {
            'BACK_SPACE', 'DEL',
            'LEFT_ARROW', 'RIGHT_ARROW', 'RET', 'NUMPAD_ENTER'
        }

        for k in prefs.keymap:
            self._keyboard_type.add(k.key)

        self._release_confirm = prefs.release_confirm
        self._real_time = True  # prefs.real_time
        self._absolute_scale = prefs.absolute_scale
        self._scale_dimensions = prefs.scale_dimensions
        self._primary_constraint = {'C_LOCAL':C_LOCAL, 'C_GLOBAL': C_GLOBAL}[prefs.constraint_order]
        self._secondary_constraint = {'C_LOCAL': C_GLOBAL, 'C_GLOBAL':C_LOCAL}[prefs.constraint_order]
        slcadsnap._snap_radius = prefs.snap_radius

    def init(self, context):
        global slcadsnap

        self._flags_axis = 0
        self._constraint_flag = C_LOCAL
        self._duplicates.clear()

        self._apply_edit_mode_changes(context)
        prefs = context.preferences.addons[__package__].preferences
        # sanity check, fix zero scale preserve hierarchy
        if prefs.apply_scale:
            self._transform_apply_scale(context)

        logger.debug("slcadsnap.start(context)")
        slcadsnap.start(context, prefs.snap_to_loose)

        local = context.active_object.matrix_world.normalized()
        world = Matrix.Translation(local.translation)
        self._constraint_global = SlCadConstraint(world)
        self._constraint_local = SlCadConstraint(local)
        self.store_matrix_world(context)
        self.clear_average()

    def invoke(self, context, event):

        if not self.poll(context):
            self.report({'WARNING'}, "CAD Transform require an active object")
            return {'CANCELLED'}

        global _running
        if _running:
            # finished "consume" event
            return {'FINISHED'}

        if context.area.type == 'VIEW_3D':
            _running = True
            logger.debug("invoke start")

            context.window.cursor_set("CROSSHAIR")
            # draw status
            self._header_draw_backup = self.change_header_draw(header_draw)
            # apply prefs
            prefs = context.preferences.addons[__package__].preferences
            self.init_prefs(context, prefs)
            update_debug_level(prefs, context)

            overlay = context.space_data.overlay
            self._show_grid = overlay.show_floor, overlay.show_axis_x, overlay.show_axis_y, overlay.show_ortho_grid
            self._show_origins = overlay.show_object_origins_all, overlay.show_object_origins

            if context.active_object is not None:
                self.snap_from = context.active_object.location.copy()

            self._delta_rotation = {}

            # self._view_plane = SlCadConstraint()
            self._constraint_user = None
            self._constraint_edge = SlCadConstraint()
            self._constraint_normal = SlCadConstraint()
            self._constraint_screen = SlCadConstraint()

            # self._modifiers = {}
            # self.hide_modifiers(context.active_object)
            theme = context.preferences.themes[0].user_interface
            axis_x = self.color_by_axis(context, 0, 0.5)
            axis_y = self.color_by_axis(context, 1, 0.5)
            axis_z = self.color_by_axis(context, 2, 0.5)

            logger.debug("invoke create gl widgets")
            radius = prefs.widget_size
            line_width = prefs.line_width
            ruler_width = prefs.ruler_width
            # setup gl widgets
            self._snap_widget = GPU_2d_Circle(radius, color=prefs.snap_color, line_width=line_width)
            self._average_widget = GPU_2d_Circle(radius, color=prefs.average_color, line_width=line_width)
            self._average_preview_widget = GPU_2d_Circle(
                radius, color=prefs.average_preview_color, line_width=line_width
            )
            # preview snap target with constraint
            self._preview_widget = GPU_2d_Circle(radius, color=prefs.preview_color, line_width=line_width)

            self._grid_widget = SlCadGridWidget((0, 0, 0, 0.5), (0, 0, 0, 0.5), axis_x, axis_y, prefs.grid_width)

            self._edge_widget = SlCadEdgeWidget(0.6 * radius, line_width, prefs.snap_high_color)
            self._face_widget = SlCadFaceWidget(0.6 * radius, line_width, prefs.snap_high_color)
            self._normal_widget = SlCadNormalWidget(0.6 * radius, line_width, prefs.snap_high_color)
            r, g, b = theme.gizmo_secondary[0:3]
            self._perpendicular_widget = SlCadPerpendicularWidget(line_width, (r, g, b, 0.5))
            self._edge_axis_widget = SlCadPerpendicularWidget(line_width, (b, g, r, 0.5))
            self._constraint_widget = SlCadConstraintWidget(line_width, axis_x, axis_y, axis_z)
            self._move_widget = SlCadMoveWidget(
                0.1, ruler_width, (0, 0, 0, 0.7), prefs.text_color, prefs.font_size
            )
            self._rotate_widget = SlCadRotateWidget(
                0.5, 0.15, ruler_width, (0, 1, 0, 0.2), prefs.text_color, prefs.font_size
            )
            self._scale_widget = SlCadScaleWidget(
                0.1, ruler_width, (0, 0, 0, 0.7), prefs.text_color, prefs.font_size
            )

            logger.debug("invoke init(context)")
            self.init(context)

            self._action = self._default_action

            logger.debug("invoke draw handler")
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                self.gl_draw, (context,), 'WINDOW', 'POST_PIXEL'   #,'POST_VIEW' #
            )

            logger.debug("invoke modal handler")
            wm = context.window_manager
            wm.modal_handler_add(self)

            return {'RUNNING_MODAL'}

        else:

            self.report({'WARNING'}, "CAD Transform require 3d view")
            return {'CANCELLED'}


class SLCAD_OT_translate(SLCAD_main, Operator):
    bl_idname = 'slcad.translate'
    bl_label = 'CAD Translate'

    _default_action = MOVE


class SLCAD_OT_rotate(SLCAD_main, Operator):
    bl_idname = 'slcad.rotate'
    bl_label = 'CAD Rotate'

    _default_action = ROTATE | PIVOT


class SLCAD_OT_scale(SLCAD_main, Operator):
    bl_idname = 'slcad.scale'
    bl_label = 'CAD Scale'

    _default_action = SCALE | PIVOT


def update_shortcut(self, context):
    if False and self.name in {'MOVE', 'ROTATE', 'SCALE'}:
        keymap = context.preferences.addons[__package__].preferences.keymap
        g = keymap.get("MOVE")
        r = keymap.get("ROTATE")
        s = keymap.get("SCALE")
        if any([i is None for i in [g, r, s]]):
            return
        SLCAD_transform.bl_keymap = (
            ("slcad.translate", {"type": g.key, "value": 'PRESS'}, None),  # , "ctrl": True},
            ("slcad.rotate", {"type": r.key, "value": 'PRESS'}, None),
            ("slcad.scale", {"type": s.key, "value": 'PRESS'}, None),
        )
        unregisterKeymaps()
        registerKeymaps()


class SLCAD_keymap(PropertyGroup):
    # event names for regular keyboard entry
    _keyboard_numbers = {
        "ZERO",
        "ONE",
        "TWO",
        "THREE",
        "FOUR",
        "FIVE",
        "SIX",
        "SEVEN",
        "EIGHT",
        "NINE"
    }

    name: StringProperty(name="name", default="event")
    label: StringProperty(name="label", default="Event")
    key: EnumProperty(
        name="key",
        default="A",
        items=(
            ('A', 'A', 'A', 'EVENT_A', 0),
            ('B', 'B', 'B', 'EVENT_B', 1),
            ('C', 'C', 'C', 'EVENT_C', 2),
            ('D', 'D', 'D', 'EVENT_D', 3),
            ('E', 'E', 'E', 'EVENT_E', 4),
            ('F', 'F', 'F', 'EVENT_F', 5),
            ('G', 'G', 'G', 'EVENT_G', 6),
            ('H', 'H', 'H', 'EVENT_H', 7),
            ('I', 'I', 'I', 'EVENT_I', 8),
            ('J', 'J', 'J', 'EVENT_J', 9),
            ('K', 'K', 'K', 'EVENT_K', 10),
            ('L', 'L', 'L', 'EVENT_L', 11),
            ('M', 'M', 'M', 'EVENT_M', 12),
            ('N', 'N', 'N', 'EVENT_N', 13),
            ('O', 'O', 'O', 'EVENT_O', 14),
            ('P', 'P', 'P', 'EVENT_P', 15),
            ('Q', 'Q', 'Q', 'EVENT_Q', 16),
            ('R', 'R', 'R', 'EVENT_R', 17),
            ('S', 'S', 'S', 'EVENT_S', 18),
            ('T', 'T', 'T', 'EVENT_T', 19),
            ('U', 'U', 'U', 'EVENT_U', 20),
            ('V', 'V', 'V', 'EVENT_V', 21),
            ('W', 'W', 'W', 'EVENT_W', 22),
            ('X', 'X', 'X', 'EVENT_X', 23),
            ('Y', 'Y', 'Y', 'EVENT_Y', 24),
            ('Z', 'Z', 'Z', 'EVENT_Z', 25),
            ('F1', 'F1', 'F1', 'EVENT_F1', 26),
            ('F2', 'F2', 'F2', 'EVENT_F2', 27),
            ('F3', 'F3', 'F3', 'EVENT_F3', 28),
            ('F4', 'F4', 'F4', 'EVENT_F4', 29),
            ('F5', 'F5', 'F5', 'EVENT_F5', 30),
            ('F6', 'F6', 'F6', 'EVENT_F6', 31),
            ('F7', 'F7', 'F7', 'EVENT_F7', 32),
            ('F8', 'F8', 'F8', 'EVENT_F8', 33),
            ('F9', 'F9', 'F9', 'EVENT_F9', 34),
            ('F10', 'F10', 'F10', 'EVENT_F10', 35),
            ('F11', 'F11', 'F11', 'EVENT_F11', 36),
            ('F12', 'F12', 'F12', 'EVENT_F12', 37),
            ('ZERO', '0', '0', icon_man.icons['KEY_0'].icon_id, 38),
            ('ONE', '1', '1', icon_man.icons['KEY_1'].icon_id, 39),
            ('TWO', '2', '2', icon_man.icons['KEY_2'].icon_id, 40),
            ('THREE', '3', '3', icon_man.icons['KEY_3'].icon_id, 41),
            ('FOUR', '4', '4', icon_man.icons['KEY_4'].icon_id, 42),
            ('FIVE', '5', '5', icon_man.icons['KEY_5'].icon_id, 43),
            ('SIX', '6', '6', icon_man.icons['KEY_6'].icon_id, 44),
            ('SEVEN', '7', '7', icon_man.icons['KEY_7'].icon_id, 45),
            ('EIGHT', '8', '8', icon_man.icons['KEY_8'].icon_id, 46),
            ('NINE', '9', '9', icon_man.icons['KEY_9'].icon_id, 47),
            ('TAB', 'TAB', 'TAB', 'EVENT_TAB', 48),
            ('SPACE', 'SPACE', 'SPACE', 'EVENT_SPACEKEY', 49)
        ),
        update=update_shortcut
    )
    alt: BoolProperty(default=False, name="alt")
    shift: BoolProperty(default=False, name="shift")
    ctrl: BoolProperty(default=False, name="ctrl")

    @property
    def has_icon(self):
        return self.key not in self._keyboard_numbers

    def draw_pref(self, layout):
        row = layout.row(align=True)
        split = row.split(factor=0.5)
        col = split.column()
        row = col.row(align=True)
        row.prop(self, "label", text="")
        col = split.column()
        row = col.row()
        row.prop(self, "key", text="", icon_only=True)
        row.prop(self, "ctrl", icon="EVENT_CTRL")
        row.prop(self, "alt", icon="EVENT_ALT")
        row.prop(self, "shift", icon="EVENT_SHIFT")

    def draw(self, layout, use_row=True, icon_only=False):
        row = layout
        global icon_man
        if any([self.ctrl, self.alt, self.shift]):
            if use_row:
                row = layout.row(align=True)
            if self.ctrl:
                row.label(text="", icon="EVENT_CTRL")
            if self.alt:
                row.label(text="", icon="EVENT_ALT")
            if self.shift:
                row.label(text="", icon="EVENT_SHIFT")

        if icon_only:
            text = ""
        else:
            text = self.label

        icon = self.bl_rna.properties['key'].enum_items[self.key].icon

        if self.has_icon:
            row.label(text=text, icon=icon)
        else:
            row.label(text=text, icon_value=icon)

    def __str__(self):
        key = ""
        if self.ctrl:
            key += 'CTRL+'
        if self.alt:
            key += 'ALT+'
        if self.shift:
            key += 'SHIFT+'
        return "%s (%s%s)" % (self.label, key, self.key)

    def match(self, signature, value="PRESS"):
        return (self.alt, self.ctrl, self.shift, self.key, value) == signature


class SLCAD_PT_tools_options:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_label = "CAD Transform"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__package__].preferences
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(prefs, "absolute_scale", text="Absolute scale")


class SLCAD_PT_tools_options_object(SLCAD_PT_tools_options, Panel):
    bl_parent_id = "VIEW3D_PT_tools_object_options"
    bl_context = ".objectmode"


class SLCAD_PT_tools_options_mesh(SLCAD_PT_tools_options, Panel):
    bl_parent_id = "VIEW3D_PT_tools_meshedit_options"
    bl_context = ".mesh_edit"


class SLCAD_PT_tools_options_curve(SLCAD_PT_tools_options, Panel):
    bl_context = ".curve_edit"


def register_shorcut(prefs, name, shortcut):
    short = prefs.get(name)
    if short is None:
        short = prefs.add()
    else:
        return
    slen = len(shortcut)
    short.name = name
    short.label = shortcut[1]
    short.ctrl = slen > 2 and shortcut[2]
    short.alt = slen > 3 and shortcut[3]
    short.shift = slen > 4 and shortcut[4]
    short.key = shortcut[0]


def register_shortcuts():
    keymap = bpy.context.preferences.addons[__package__].preferences.keymap
    # keyconfigs = bpy.context.window_manager.keyconfigs
    # km = keyconfigs['blender'].keymaps['3D View']
    # default_keymap['MOVE'] = (find_key_by_idname_and_map_type(km, "transform.translate", "KEYBOARD", "G"), "Move")
    # default_keymap['ROTATE'] = (find_key_by_idname_and_map_type(km, "transform.rotate", "KEYBOARD", "R"), "Rotate")
    # default_keymap['SCALE'] = (find_key_by_idname_and_map_type(km, "transform.scale", "KEYBOARD", "S"), "Scale")

    for name, shortcut in default_keymap.items():
        register_shorcut(keymap, name, shortcut)


class SLCAD_AddonPreferences(AddonPreferences):
    bl_idname = __package__

    release_confirm: BoolProperty(name="Release confirm", description="Confirm on mouse release", default=False)
    # real_time: BoolProperty(name="Real time", description="Transform in real-time", default=True)
    # confirm_exit: BoolProperty(name="Exit on confirm", description="Exit tool on confirm", default=True)
    absolute_scale: BoolProperty(
        name="Absolute scale", description="Use absolute values for scale when using keyboard", default=False
    )
    apply_scale: BoolProperty(
        name="Apply scale", description="Ensure object does not have any scale axis at 0", default=True
    )
    display_shortcuts: BoolProperty(
        name="Shortcuts", description="Display shortcuts", default=True
    )
    snap_to_loose: BoolProperty(
        name="Snap to loose geometry", description="Snap to isolated vertex and edges", default=True
    )
    snap_radius: IntProperty(
        name="Snap radius (pixel)",
        description="Snap radius in pixels, default 30",
        min=10,
        max=50,
        default=30
    )

    text_color: FloatVectorProperty(
        name="Text",
        description="Text color",
        subtype='COLOR_GAMMA',
        default=(0.95, 0.95, 0.95, 1.0),
        size=4,
        min=0, max=1
    )
    average_color: FloatVectorProperty(
        name="Average",
        description="Average circle color",
        subtype='COLOR_GAMMA',
        default=(0, 0.5, 1, 0.3),
        size=4,
        min=0, max=1
    )
    average_preview_color: FloatVectorProperty(
        name="Average preview",
        description="Average preview circle color",
        subtype='COLOR_GAMMA',
        default=(1, 0, 0.5, 0.3),
        size=4,
        min=0, max=1
    )
    snap_color: FloatVectorProperty(
        name="Snap",
        description="Snap circle color",
        subtype='COLOR_GAMMA',
        default=(1, 0.5, 0, 0.7),
        size=4,
        min=0, max=1
    )
    snap_high_color: FloatVectorProperty(
        name="Snap highlight",
        description="Snap highlight color",
        subtype='COLOR_GAMMA',
        default=(1, 0, 0, 0.8),
        size=4,
        min=0, max=1
    )
    preview_color: FloatVectorProperty(
        name="Preview",
        description="Preview circle color",
        subtype='COLOR_GAMMA',
        default=(0, 0, 1, 0.7),
        size=4,
        min=0, max=1
    )
    widget_size: FloatProperty(name="Circle widgets radius (pixel)", min=0.2, default=5)
    line_width: FloatProperty(name="Snap widgets lines thickness (pixel)", min=0.1, default=1)
    ruler_width: FloatProperty(name="Rulers lines thickness (pixel)", min=0.1, default=2)
    grid_width: FloatProperty(name="Grid lines thickness (pixel)", min=0.1, default=1)

    font_size: IntProperty(name="Font size", min=8, default=16)
    constraint_order: EnumProperty(
        name="Constraint toggle",
        description="Order of constraint toggle",
        items=(
            ('C_GLOBAL', "Global then local", "Use global then local axis for constraint"),
            ('C_LOCAL', "Local then global", "Use local then global axis for constraint")
        ),
        default='C_LOCAL'
    )
    debug_level: EnumProperty(
        name="Debug level",
        description="Set debug log level",
        items=(
            ('ERROR', "Error", "Enable error only, this is the less verbose option"),
            ('WARNING', "Warning", "Enable warning log, less verbose than info"),
            ('INFO', 'Info', 'Enable info log, this is default option'),
            ('DEBUG', 'Debug', 'Enable debug log, this is the most verbose option')
        ),
        default='WARNING',
        update=update_debug_level
    )
    # ('0', 'Non uniform 1D / 2D', 'Scale non uniform in 1 / 2 dimensions'),
    default_scale_dimensions: EnumProperty(
        name="Scale default",
        description="Scale in 1D / 2D / 3D by default",
        items=(
            ('0', 'Scale 1D', 'Scale along 1 dimension'),
            ('1', 'Uniform 2D', 'Uniform scale in 2 dimensions'),
            ('2', 'Uniform 3D', 'Uniform scale in 3 dimensions'),
        ),
        default='0'
    )

    @property
    def scale_dimensions(self):
        return int(self.default_scale_dimensions)

    use_numpad_for_navigation: BoolProperty(
        name="Use numpad for navigation",
        description="When enabled, numerical entry done on numpad are kept for viewport navigation",
        default=False
    )

    keymap: CollectionProperty(type=SLCAD_keymap)

    def key(self, name):
        k = self.keymap.get(name)
        if k:
            return k.key.lower()
        return ""

    def match(self, name, signature, value="PRESS"):
        shorts = name.split(",")
        for sname in shorts:
            short = self.keymap.get(sname)
            if short is not None and short.match(signature, value):
                return True
        return False

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Interaction")
        box.prop(self, "use_numpad_for_navigation")
        box.prop(self, "release_confirm")
        box.prop(self, "snap_radius")

        box = layout.box()
        box.label(text="Operators options")
        box.prop(self, "snap_to_loose")
        box.prop(self, "absolute_scale")
        box.prop(self, "default_scale_dimensions")
        box.prop(self, "constraint_order")

        box = layout.box()
        box.label(text="Sanity check")
        box.prop(self, "apply_scale")

        box = layout.box()
        box.label(text="Theme")

        row = box.row()
        col = row.column()
        col.label(text="Text")
        col = row.column()
        col.prop(self, "text_color", text="")
        box.prop(self, "font_size")

        row = box.row()
        col = row.column()
        col.label(text="Snap highlight")
        col = row.column()
        col.prop(self, "snap_high_color", text="")

        row = box.row()
        col = row.column()
        col.label(text="Snap circle")
        col = row.column()
        col.prop(self, "snap_color", text="")

        row = box.row()
        col = row.column()
        col.label(text="Preview circle")
        col = row.column()
        col.prop(self, "preview_color", text="")

        row = box.row()
        col = row.column()
        col.label(text="Average circle")
        col = row.column()
        col.prop(self, "average_color", text="")
        row = box.row()
        col = row.column()
        col.label(text="Average preview circle")
        col = row.column()
        col.prop(self, "average_preview_color", text="")

        box.prop(self, "widget_size")
        box.prop(self, "line_width")
        box.prop(self, "ruler_width")
        box.prop(self, "grid_width")

        box = layout.box()
        box.label(text="Keymap")
        # layout.prop(self, "confirm_exit")
        box.label(text="Snap modes:")
        for key in self.keymap[0:10]:
            key.draw_pref(box)
        box.label(text="Constraint:")
        for key in self.keymap[10:16]:
            key.draw_pref(box)
        box.label(text="Options:")
        for key in self.keymap[16:]:
            key.draw_pref(box)
        box = layout.box()
        box.label(text="Debug")
        box.prop(self, "debug_level")


class SLCAD_transform(WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "slcad.transform"
    bl_label = "CAD Transform %s" % __version__
    bl_description = "Precise transforms operations\nShortcuts: G / R / S"
    bl_icon = os.path.join(os.path.dirname(__file__), "icons", "ops.transform.cad")
    bl_widget = None
    bl_keymap = (
        ("slcad.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("slcad.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("slcad.scale", {"type": 'S', "value": 'PRESS'}, None),
    )

    draw_settings = draw_settings


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


def find_key_by_idname_and_map_type(keymap, idname, map_type, default=""):
    for k in keymap.keymap_items:
        if k.idname == idname and k.map_type == map_type:
            return k.type
    return default


@ToolDef.from_fn
def toolCadTransform():
    return dict(idname=SLCAD_transform.bl_idname,
                label=SLCAD_transform.bl_label,
                description=SLCAD_transform.bl_description,
                icon=SLCAD_transform.bl_icon,
                widget=None,
                keymap=kmTool,
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
    addonmap = keyconfigs.get("blender addon").keymaps

    for km_name, km_args, km_content in [keymap]:
        km = addonmap.find(km_name, **km_args)
        if km is not None:
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


def registerTools(mode):
    tools = getToolList('VIEW_3D', mode)
    tools += None, toolCadTransform
    del tools


def unregisterTools(mode):
    tools = getToolList('VIEW_3D', mode)
    index = tools.index(toolCadTransform) - 1  # None
    tools.pop(index)
    tools.remove(toolCadTransform)
    del tools


def register():
    global icon_man
    icon_man.load()

    if bpy.app.background:
        print("{} {} : not loaded in background instance".format(bl_info['name'], __version__))
        return

    try:
        register_class(SLCAD_keymap)
        register_class(SLCAD_AddonPreferences)
        register_shortcuts()
        # register_class(SLCAD_OT_transform)
        register_class(SLCAD_OT_translate)
        register_class(SLCAD_OT_rotate)
        register_class(SLCAD_OT_scale)
        register_class(SLCAD_PT_tools_options_object)
        register_class(SLCAD_PT_tools_options_mesh)
        register_class(SLCAD_PT_tools_options_curve)
        registerTools('OBJECT')
        registerTools('EDIT_MESH')
        registerTools('EDIT_CURVE')
        registerKeymaps()
        # register_tool(SLCAD_transform, after={"builtin.transform"}, separator=True) #, group=True)
    except Exception as ex:
        print("{} {} : error while loading\n{}".format(bl_info['name'], __version__, ex))
        raise

    print("{} {} : ready".format(bl_info['name'], __version__))


def unregister():
    if bpy.app.background:
        return

    unregisterKeymaps()
    # unregister_tool(SLCAD_transform)
    unregisterTools('OBJECT')
    unregisterTools('EDIT_MESH')
    unregisterTools('EDIT_CURVE')
    unregister_class(SLCAD_PT_tools_options_object)
    unregister_class(SLCAD_PT_tools_options_mesh)
    unregister_class(SLCAD_PT_tools_options_curve)
    # unregister_class(SLCAD_OT_transform)
    unregister_class(SLCAD_OT_translate)
    unregister_class(SLCAD_OT_rotate)
    unregister_class(SLCAD_OT_scale)
    unregister_class(SLCAD_AddonPreferences)
    unregister_class(SLCAD_keymap)
    print("%s %s successfully disabled" % (bl_info['name'], __version__))

    global icon_man
    icon_man.cleanup()
