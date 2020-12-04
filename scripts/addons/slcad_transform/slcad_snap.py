# -*- coding:utf-8 -*-

# #
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
# 
# <pep8 compliant>

# ----------------------------------------------------------
# Author: Stephen Leger (s-leger)
#
# ----------------------------------------------------------

import time
import logging
from math import pi, cos, sin
from mathutils import Matrix, Vector
import bpy

try:
    from .snap_context import SnapContext
    USE_GL = True
except ImportError:
    print("Snap to curves will be disabled")
    USE_GL = False
    pass

# Draw gl stack
DEBUG_GL = False # bpy.app.version >= (2,91,0)

logger = logging.getLogger(__package__)

X_AXIS = Vector((1, 0, 0))
Y_AXIS = Vector((0, 1, 0))
Z_AXIS = Vector((0, 0, 1))
VECTOR3 = Vector()

# Snap modes flags
VERT = 1
EDGE = 2
FACE = 4
GRID = 8
EDGE_CENTER = 16
EDGE_PERPENDICULAR = 32
EDGE_PARALLEL = 64
FACE_CENTER = 128
FACE_NORMAL = 256
ORIGIN = 512

SNAP_TO_ISOLATED_MESH = True
SNAP_TO_BASE_MESH = True


def debug_typ(typ):
    s = []
    if typ & VERT:
        s.append("VERT")
    if typ & EDGE:
        s.append("EDGE")
    if typ & FACE:
        s.append("FACE")
    if typ & ORIGIN:
        s.append("ORIGIN")
    return " ".join(s)


class SlCadSnapTarget:

    def __init__(self, typ, obj, dist, pts, normal, z=0, t=None, ray_depth=0, face_index=0, vertex_index=-1):
        self.typ = typ

        # not really usefull here
        self.o = obj

        # distance from mouse pointer in pixels
        self.d = dist

        # points, 0 = snap point in world coordsys 1&2 p0 p1 of edge and more for faces

        self._pts = pts
        # hint index of object component
        self.n = normal

        # distance from origin
        self.z = z

        # t of snap point along segment
        self.t = t

        self.ray_depth = ray_depth

        self._face_index = face_index
        self._vertex_index = vertex_index

    def __str__(self):
        return "%s f:%s d:%.3f z:%.3f t:%s coord:%s" % (
            debug_typ(self.typ),
            self._face_index,
            # self._vertex_index,
            self.d,
            self.z,
            self.t,
            self.p
        )

    @property
    def p(self):
        return self._pts[0]

    @property
    def p0(self):
        if len(self._pts) > 1:
            return self._pts[1]
        return None

    @property
    def p1(self):
        if len(self._pts) > 2:
            return self._pts[2]
        return None

    @property
    def closest_p(self):
        # closest point of snapped edge
        p0, p1 = self.p0, self.p1
        if p1 is not None:
            if self.t > 0.5:
                p1, p0 = p0, p1
            p = p0
        else:
            p = p0
        return p

    def constraint(self, constraint):
        p0, p1 = self.p0, self.p1
        if p1 is not None:
            if self.t > 0.5:
                p1, p0 = p0, p1
            v = p1 - p0
            p = p0
        else:
            v = X_AXIS
            p = p0
        constraint.origin = p
        constraint.direction = v


class SlCadSnap:

    def __init__(self):
        # max search radius in pixels
        self._snap_radius = 30
        self._max_attempts = 3
        # search samples around mouse center
        self._cast_samples = 6
        # distance from polygon for next cast
        self._cast_threshold = 0.001
        # clipping
        self._near_clip = 0
        self._far_clip = 1e32

        # limit to nth intersection of ray cast
        self._max_depth = 100
        self._back_faces = True
        # flag
        self._active = False
        self._is_snapping = False
        # exclude objects by name
        self._exclude = set()

        self.ray_origin = Vector()
        self.ray_direction = Vector()

        self._skip_selected_faces = False

        # snap raw object
        self._snap_loc = Vector()
        self._snap_raw = None
        self.snap_mode = VERT
        self._x_ray = False
        self._center = Vector((0, 0))
        self._rv3d = None
        self._region = None
        self._win_half = Vector((0, 0))

        self.gl_stack = None
        # snap final location with constraints
        self.snap_to = Vector()

    @property
    def x_ray(self):
        return self._x_ray

    @x_ray.setter
    def x_ray(self, mode):
        self._x_ray = mode

    def start(self, context, snap_to_loose):

        self._region = context.region
        self._rv3d = context.space_data.region_3d
        if USE_GL:
            self.gl_stack = SnapContext()
            self.gl_stack.set_pixel_dist(self._snap_radius)
            self.gl_stack.init_context(context)
            self.update_gl_snap()
            for o in context.visible_objects:
                if o.type == "CURVE":
                    if any([x == 0 for x in o.scale]):
                        continue
                    self.gl_stack.add_obj(o)
                elif o.type == "MESH" and snap_to_loose:
                    self.gl_stack.add_obj(o)
            self.gl_stack.add_origins(context)

    def exit(self):
        # cleanup exclude
        self.clear_exclude()
        self._skip_selected_faces = False
        if self.gl_stack is not None:
            self.gl_stack.snap_objects.clear()

    def minimum_blender_version(self, major, minor, rev):
        return bpy.app.version >= (major, minor, rev)

    def _scene_ray_cast(self, context, orig, vec):
        if self.minimum_blender_version(2, 91, 0):
            return context.scene.ray_cast(
                depsgraph=context.view_layer.depsgraph,
                origin=orig,
                direction=vec)
        else:
            return context.scene.ray_cast(
                view_layer=context.view_layer,
                origin=orig,
                direction=vec)

    def _event_pixel_coord(self, event):
        return Vector((event.mouse_region_x, event.mouse_region_y))

    def _region_2d_to_orig_and_vect(self, coord):
        viewinv = self._rv3d.view_matrix.inverted()
        persinv = self._rv3d.perspective_matrix.inverted()
        dx = (2.0 * coord[0] / self._region.width) - 1.0
        dy = (2.0 * coord[1] / self._region.height) - 1.0
        if self._rv3d.is_perspective:
            origin_start = viewinv.translation.copy()
            out = Vector((dx, dy, -0.5))
            w = out.dot(persinv[3].xyz) + persinv[3][3]
            view_vector = ((persinv @ out) / w) - origin_start
        else:
            view_vector = -viewinv.col[2].xyz

            origin_start = ((persinv.col[0].xyz * dx) +
                            (persinv.col[1].xyz * dy) +
                            viewinv.translation)

        view_vector.normalize()
        return origin_start, view_vector

    def _deep_cast(self, context, screen_pixel_coord, hits, deep_cast):
        """ Find objects below mouse
        :param context:
        :param screen_pixel_coord:
        :param hits:
        :param deep_cast:
        :return:
        """
        origin, direction = self._region_2d_to_orig_and_vect(screen_pixel_coord)
        hit = True
        ray_depth = 0
        far_clip = self._far_clip
        dist = self._near_clip
        orig = origin + (direction * dist)
        if deep_cast:
            max_depth = self._max_depth
        else:
            max_depth = 1
        # ray cast origin may be too close in ortho mode ..
        if not self._rv3d.is_perspective:
            far_clip += 100000
            orig -= direction * 100000

        while hit and dist < far_clip and ray_depth < max_depth:
            hit, pos, normal, face_index, o, matrix_world = self._scene_ray_cast(
                context,
                orig,
                direction
            )
            if hit:
                dist = (orig - pos).length
                orig += direction * (dist + self._cast_threshold)
                if o.name not in self._exclude and o.visible_get():
                    # normal -> vec are opposites, when facing length is 0 when opposite length is 2
                    # if self._back_faces or (matrix_world.to_quaternion() @ normal + direction).length < 1:
                    if o not in hits:
                        hits[o] = {}
                    # we only store one hit by face index
                    if face_index not in hits[o]:
                        hits[o][face_index] = tuple([pos, normal, matrix_world, (origin - pos).length, ray_depth])

                    ray_depth += 1

    def lerp(self, p0, p1, t):
        return p0 + t * (p1 - p0)

    def is_not_on_screen(self, pt):
        x, y = self._screen_location_from_3d(pt)
        wx, wy = self._region.width, self._region.height
        return not (wx > x > 0 and wy > y > 0)

    def _point_segment_t(self, v0, v1, pt):
        """Return t param of nearest point over segment
        :param v0:
        :param v1:
        :param pt:
        :return:
        """
        d = v1 - v0
        a = pt - v0
        dl = d.length_squared
        if dl == 0:
            return 0
        return a.dot(d) / dl

    def _ray_segment_t(self, v0, v1, ray_origin, ray_direction):
        """ param t on segment of nearest point ray-segment 
        :param v0: 
        :param v1: 
        :param ray_origin: 
        :param ray_direction: 
        :return: 
        """
        a = v1 - v0
        t = v0 - ray_origin
        n = a.cross(ray_direction)
        nlen = n.length_squared
        # if (nlen == 0.0f) the lines are parallel, has no nearest point, only distance squared.*/
        if nlen == 0.0:
            return None
        else:
            c = n - t
            cray = c.cross(ray_direction)
            return cray.dot(n) / nlen

    def _min_edge_dist(self, p0, p1, origin, direction):
        t = self._ray_segment_t(p0, p1, origin, direction)
        if t is None:
            p = p0
            t = 0
        else:
            # print("_ray_segment_t", t)
            p = self.lerp(p0, p1, t)
        d = self._pixel_dist(p)
        if t <= 0:
            t, p = 0, p0
        elif t >= 1:
            t, p = 1, p1
        return t, p, d

    def _pixel_dist(self, p):
        dpix = self._center - self._screen_location_from_3d(p)
        return dpix.length  # max([abs(i) for i in dpix[:]]) #

    def _closest_mesh_vert(self, o, me, origin, hits, closest):
        for face_index, hit in hits.items():
            if face_index < len(me.polygons):
                pos, normal, matrix_world, z, ray_depth = hit

                if self._skip_selected_faces and me.polygons[face_index].select:
                    continue

                # TODO: handle "visible" state
                verts = [
                    (i, matrix_world @ me.vertices[i].co)
                    for i in me.polygons[face_index].vertices
                ]
                # n = matrix_world.to_quaternion() @ normal
                for i, co in verts:

                    if self._skip_selected_faces and me.vertices[i].select:
                        continue

                    dist = self._pixel_dist(co)
                    if dist < self._snap_radius:
                        closest.append(
                            SlCadSnapTarget(
                                VERT, o, dist, [co], normal,
                                z=(co - origin).length,
                                ray_depth=ray_depth,
                                face_index=face_index
                            )
                        )

    def _closest_subs(self, origin, direction, p0, p1, snap_radius, s0, s1):
        t, p, d = self._min_edge_dist(p0, p1, origin, direction)
        found = False
        dist = 1e32
        typ = None
        res = None
        fac = 0
        z = 1e32
        radius = snap_radius
        if (self.snap_mode & VERT) and (t < 0.3 or t > 0.7):
            ps = p0
            skip = s0
            if t > 0.5:
                ps = p1
                skip = s1
            if not skip:
                dpix = self._pixel_dist(ps)
                if dpix < radius:
                    typ = VERT
                    res = [ps]
                    fac = None
                    found = True
                    dist = d
                    radius = dpix
                    z = (ps - origin).length

        if (self.snap_mode & EDGE_CENTER) and (0.75 > t > 0.25):
            if not (s0 or s1):
                ps = 0.5 * (p0 + p1)
                dpix = self._pixel_dist(ps)
                if dpix < radius:
                    typ = EDGE
                    res = [ps, p0, p1]
                    fac = t
                    found = True
                    dist = d
                    radius = dpix
                    z = (ps - origin).length

        if not found and (self.snap_mode & (EDGE | EDGE_PERPENDICULAR | EDGE_PARALLEL)):

            if not (s0 or s1):

                if d < radius:
                    typ = EDGE
                    res = [p, p0, p1]
                    fac = t
                    found = True
                    dist = d
                    radius = d
                    z = (p - origin).length

        return found, (radius, typ, dist, res, fac, z)

    def _closest_mesh_face(self, o, me, origin, direction, hits, closest, skip_face):
        snap_radius = self._snap_radius
        seek_radius = snap_radius

        for face_index, hit in hits.items():
            if face_index < len(me.polygons):

                # Find closest item start by verts, then edges / center, face center if closest
                # and fallback to face if nothing else is found in radius

                if self._skip_selected_faces and me.polygons[face_index].select:
                    # skip selected face in edit mode when snapping to normal
                    continue

                # TODO: handle "visible" state
                pos, normal, matrix_world, z, ray_depth = hit
                dist = 1e32
                verts = [
                    (self._skip_selected_faces and me.vertices[v].select, matrix_world @ me.vertices[v].co)
                    for v in me.polygons[face_index].vertices
                ]
                res = None
                fac = None
                typ = FACE

                if self.snap_mode & (VERT | EDGE | EDGE_CENTER | EDGE_PERPENDICULAR | EDGE_PARALLEL):
                    for i, (s1, p1) in enumerate(verts):
                        s0, p0 = verts[i - 1]
                        found, ret = self._closest_subs(
                            origin, direction, p0, p1, snap_radius, s0, s1
                        )
                        if found:
                            _snap_radius, _typ, dpix, _res, _fac, _z = ret
                            if dpix < seek_radius:
                                seek_radius = dpix
                                _snap_radius, typ, dist, res, fac, z = ret

                if self.snap_mode & FACE_CENTER:
                    ps = matrix_world @ me.polygons[face_index].center
                    dpix = self._pixel_dist(ps)
                    if dpix < seek_radius:
                        typ = FACE
                        res = [ps] + [v[1] for v in verts]
                        dist = dpix
                        z = (ps - origin).length
                        fac = None

                if res is None and (self.snap_mode & (FACE | FACE_NORMAL)):
                    # nothing else found, skip face if something was found in curve
                    if skip_face:
                        continue
                    res = [pos] + [v[1] for v in verts]
                    dist = self._pixel_dist(pos)

                if res is not None:
                    closest.append(
                        SlCadSnapTarget(
                            typ, o, dist, res, normal,
                            z=z, t=fac, ray_depth=ray_depth, face_index=face_index
                        )
                    )

    def _closest_mesh_edge(self, o, me, origin, direction, hits, closest):
        snap_radius = self._snap_radius
        seek_radius = snap_radius
        for face_index, hit in hits.items():
            if face_index < len(me.polygons):

                if self._skip_selected_faces and me.polygons[face_index].select:
                    continue

                # TODO: handle "visible" state
                pos, normal, matrix_world, z, ray_depth = hit
                verts = [
                    (self._skip_selected_faces and me.vertices[v].select, matrix_world @ me.vertices[v].co)
                    for v in me.polygons[face_index].vertices
                ]
                dist = 1e32
                typ = None
                fac = None
                res = []
                for i, (s1, p1) in enumerate(verts):
                    s0, p0 = verts[i - 1]
                    found, ret = self._closest_subs(
                        origin, direction, p0, p1, snap_radius, s0, s1
                    )
                    if found:
                        _snap_radius, _typ, _dist, _res, _fac, _z = ret
                        if _dist < seek_radius:
                            seek_radius = _dist
                            _snap_radius, typ, dist, res, fac, z = ret

                if typ is not None:
                    closest.append(
                        SlCadSnapTarget(
                            typ, o, dist, res, normal,
                            z=z, t=fac, ray_depth=ray_depth, face_index=face_index
                        )
                    )
            else:
                logger.debug("_closest_mesh_edge face_index > n polys %s > %s" % (face_index, len(me.polygons)))

    def _closest_geometry(self, context, origin, direction, hits_dict, closest, skip_face):
        t = time.time()
        # TODO: handle "visible" state at object's level, including "isolated" state

        depsgraph = context.evaluated_depsgraph_get()
        for o, hits in hits_dict.items():
            if o.type == "MESH":

                if len(o.modifiers) > 0:
                    me = o.evaluated_get(depsgraph).to_mesh()
                else:
                    me = o.data

                if self.snap_mode & (FACE | FACE_CENTER | FACE_NORMAL):
                    self._closest_mesh_face(o, me, origin, direction, hits, closest, skip_face)

                elif self.snap_mode & (EDGE | EDGE_CENTER | EDGE_PERPENDICULAR | EDGE_PARALLEL):
                    self._closest_mesh_edge(o, me, origin, direction, hits, closest)

                elif self.snap_mode & VERT:
                    self._closest_mesh_vert(o, me, origin, hits, closest)

        # print("_closest_geometry %.4f" % (time.time() - t))

    def _cast(self, context, hits, radius, use_center, deep_cast):
        t = time.time()

        # allow multiple attempts if nothing is found on radius
        n_hits, n_faces, max_depth = 0, 0, 0

        if use_center:
            self._deep_cast(context, self._center, hits, deep_cast)

        # when hit a face in edge / face / normal / origin modes, closest is under mouse cursor
        if len(hits) == 0 or (self.snap_mode & (VERT | EDGE_CENTER | FACE_CENTER)):
            cx, cy = self._center[0:2]
            da = 2 * pi / self._cast_samples
            for i in range(self._cast_samples):
                # cast multiple rays around radius
                a = i * da
                self._deep_cast(context, (cx + radius * cos(a), cy + radius * sin(a)), hits, deep_cast)

        n_hits, max_depth, n_faces = len(hits), 0, 0
        if n_hits > 0:
            _hits = [len(hit) for hit in hits.values()]
            max_depth = max(_hits)
            n_faces = sum(_hits)

        # print("_cast objects:%s faces:%s depth:%s  %.4f" % (n_hits, n_faces, max_depth, time.time() - t))

    @staticmethod
    def _isect_vec_plane(origin, u, p_co, p_no, epsilon=1e-6):
        """
        p0, vec: define the line
        p_co, p_no: define the plane:
            p_co is a point on the plane (plane coordinate).
            p_no is a normal vector defining the plane direction;
                 (does not need to be normalized).
        return a Vector or None (when the intersection can't be found).
        """
        d = p_no.dot(u)
        if abs(d) > epsilon:
            w = origin - p_co
            t = -p_no.dot(w) / d
            return origin + t * u
        else:
            # The segment is parallel to plane
            return None

    def _mouse_to_plane(self, p_co=Vector((0, 0, 0)), p_no=Z_AXIS):
        """
            convert mouse pos to 3d point over plane defined by origin and normal
            return None if the point is behind camera view
        """
        origin, direction = self.ray_origin, self.ray_direction

        pt = self._isect_vec_plane(origin, direction, p_co, p_no)

        # fix issue with parallel plane (front or left ortho view)
        if pt is None:
            pt = self._isect_vec_plane(origin, direction, p_co, Y_AXIS)

        if pt is None:
            pt = self._isect_vec_plane(origin, direction, p_co, X_AXIS)

        if pt is None:
            pt = self._isect_vec_plane(origin, direction, p_co, Z_AXIS)

        if pt is None:
            # fallback to a null vector
            pt = Vector()

        # if is_perspective:
        #     # Check if point is behind point of view (mouse over horizon)
        #     res = self._view_matrix_inverted(origin, direction) @ pt
        #     if res.z < 0:
        #         print("not behind camera")

        return pt

    def _screen_location_from_3d(self, co):
        proj_co = self._rv3d.perspective_matrix @ co.to_4d()
        proj_co.xy /= proj_co.w
        proj_co[0] = (proj_co[0] + 1.0) * self._win_half[0]
        proj_co[1] = (proj_co[1] + 1.0) * self._win_half[1]
        return proj_co.xy

    def set_snap_mode(self, snap_mode):
        if snap_mode != self.snap_mode:
            self.snap_mode = snap_mode

    def update_gl_snap(self):
        if self.gl_stack is not None:
            self.gl_stack.set_snap_mode(self.snap_mode)

    def toggle_snap_mode(self, snap_to_xx):
        if self.snap_mode & snap_to_xx:
            self.snap_mode &= ~snap_to_xx
        else:
            self.snap_mode |= snap_to_xx
        self.update_gl_snap()

    @property
    def view_x(self):
        return -self._rv3d.view_matrix.row[0].xyz

    @property
    def view_y(self):
        return -self._rv3d.view_matrix.row[1].xyz

    @property
    def view_z(self):
        return -self._rv3d.view_matrix.row[2].xyz

    def event_origin_and_direction(self, event):
        self._center = self._event_pixel_coord(event)
        self.ray_origin, self.ray_direction = self._region_2d_to_orig_and_vect(self._center)
        return self._center, self.ray_origin, self.ray_direction

    @property
    def is_snapping_to_vert(self):
        return self._is_snapping and (self._snap_raw.typ & VERT)

    @property
    def is_snapping_to_edge(self):
        return self._is_snapping and (self._snap_raw.typ & EDGE)

    @property
    def is_snapping_to_face(self):
        return self._is_snapping and (self._snap_raw.typ & FACE)

    @property
    def is_snapping_to_normal(self):
        return self._is_snapping and (self.snap_mode & FACE_NORMAL)

    @property
    def is_snapping_to_perpendicular(self):
        return self.is_snapping_to_edge and (self.snap_mode & EDGE_PERPENDICULAR)

    @property
    def is_snapping_to_parallel(self):
        return self.is_snapping_to_edge and (self.snap_mode & EDGE_PARALLEL)

    @property
    def is_snapping_to_origin(self):
        return self._is_snapping and (self._snap_raw.typ & ORIGIN)

    @property
    def edge_points(self):
        p0, p1 = self._snap_raw.p0, self._snap_raw.p1
        if self._snap_raw.t > 0.5:
            p0, p1 = p1, p0
        return p0, p1

    @property
    def is_snapping(self):
        '''
        :return: Snapping state boolean, True when snapping to something
        '''
        return self._is_snapping

    @property
    def snap_target(self):
        '''
        :return: Active snap target SlCadSnapTarget or None
        '''
        if self._is_snapping:
            return self._snap_raw
        return None

    @property
    def snap_location(self):
        '''
        :return: Active snap location Vector or None
        '''
        if self._is_snapping:
            return self._snap_loc
        return None

    def snap(self, context, event, grid_matrix=None):
        """ Update _snap_raw, _snap_loc and _is_snapping state
        :param context: blender's context
        :param event: blender's mouse event
        :param grid_matrix: optional Matrix for grid snap plane and scale
        :return:
        """

        # flag to prevent overflow
        # a modal may call faster than time to compute
        if self._active:
            return

        self._win_half = 0.5 * Vector((context.region.width, context.region.height))

        self._is_snapping = False
        self._active = True

        hits = {}
        closest_curve = []

        center, origin, direction = self.event_origin_and_direction(event)

        t = time.time()

        # when geometry is found (origin or curve), skip face snap
        skip_face = False

        if self.gl_stack is not None and (self.snap_mode & (
                VERT | EDGE | EDGE_CENTER | EDGE_PERPENDICULAR | EDGE_PARALLEL | ORIGIN)
        ):
            # if DEBUG_GL:
            #    self.gl_stack.draw()

            # fallback to gl for curves, origin, cursor, isolated verts / edges, limited to knots and straight segments
            target, ret = self.gl_stack.snap(center)

            if target is not None and ret is not None:
                loc, pts, dist, fac, typ = ret
                # print("snap gl_stack.snap(): data:%s loc:%s idx:%s  %.4f" %
                #  (target.data[0].name, loc, idx, time.time() - t))
                if loc is not None:
                    # if self.snap_mode & ORIGIN:
                    #     pos = target.data[0].matrix_world.translation
                    #     z = (pos - origin).length
                    #     closest_curve.append(
                    #         SlCadSnapTarget(ORIGIN, target.data[0], 0, [pos], Z_AXIS, z=z, t=None)
                    #     )
                    # else:
                    #
                    #     typ = EDGE
                    #     if fac is None:
                    #         typ = VERT
                    # logger.debug("found %s  %s" % (typ, dist))
                    z = (pts[0] - origin).length
                    closest_curve.append(
                        SlCadSnapTarget(typ, target.data[0], dist, pts, Z_AXIS, z=z, t=fac)
                    )
                    skip_face = True

        # Snap to geometry, use ray under mouse only on first attempt
        use_center = True

        attempts = self._max_attempts
        # Progressive grow snap radius by attempts
        snap_radius_px = int(self._snap_radius / attempts)
        radius = 0

        # Deep cast for x_ray and when snapping to normal in edit mode to skip selected faces
        sort_by_ray_depth = (context.mode == "EDIT_MESH" and (self.snap_mode & FACE_NORMAL))
        deep_cast = self.x_ray or sort_by_ray_depth

        while attempts > 0:

            closest = closest_curve[:]
            attempts -= 1
            radius += snap_radius_px

            if (self.snap_mode & (
                    VERT | EDGE | EDGE_CENTER | EDGE_PERPENDICULAR | EDGE_PARALLEL | FACE | FACE_CENTER | FACE_NORMAL
            )):

                self._cast(context, hits, radius, use_center, deep_cast)

                use_center = False
                if len(hits) > 0:
                    self._closest_geometry(context, origin, direction, hits, closest, skip_face)

            if self.snap_mode & GRID and grid_matrix is not None:
                # Snap to grid
                p0 = self._mouse_to_plane(p_co=grid_matrix.translation, p_no=grid_matrix.col[2].to_3d())
                if p0 is not None:
                    x, y, z = grid_matrix.inverted_safe() @ p0
                    p1 = grid_matrix @ Vector((round(x, 1), round(y, 1), round(z, 1)))
                    closest.append(
                        SlCadSnapTarget(GRID, None, self._pixel_dist(p1), [p1], Z_AXIS)
                    )

            if len(closest) > 0:

                # when snapping to normal use ray depth to sort items, as a back face may be closest than anything else
                if sort_by_ray_depth:
                    closest.sort(key=lambda i: (i.ray_depth, i.d, i.z))
                else:
                    # prefer closest z items when pixel distance is the same
                    closest.sort(key=lambda i: (i.d, i.z))

                snap_raw = closest[0]

                # for i in closest:
                #    print(i)

                # snap proximity with mouse pointer
                if snap_raw.d < self._snap_radius:
                    self._snap_loc = snap_raw.p
                    self._snap_raw = snap_raw
                    self._is_snapping = True
                    break

        # print("snap: %.4f" % (time.time() - t))

        self._active = False

    def exclude_selected_face(self):
        self._skip_selected_faces = True  # (self.snap_mode & FACE_NORMAL)

    def exclude_from_snap(self, objs):
        self._exclude = set([o.name for o in objs])
        if self.gl_stack is not None:
            self.gl_stack._exclude = self._exclude
        self._is_snapping = False

    def clear_exclude(self):
        self._exclude.clear()
        if self.gl_stack is not None:
            self.gl_stack._exclude.clear()
