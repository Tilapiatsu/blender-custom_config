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
from math import pi, cos, sin
from mathutils import Matrix, Vector
from .snap_context import SnapContext


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
FACE_CENTER = 64
FACE_NORMAL = 128


class SlCadSnapTarget:
    def __init__(self, typ, obj, dist, pts, normal, priority=0, t=None, face_index=0, vertex_index=-1):
        self.typ = typ
        #
        self.o = obj
        # distance from pointer in world units
        self.d = dist
        # points, 0 = snap point in world coordsys 1&2 p0 p1 of edge and more for faces

        self._pts = pts
        # hint index of object component
        self.n = normal
        #
        self.priority = priority
        # t of snap point along segment
        self.t = t

        self._face_index = face_index
        self._vertex_index = vertex_index

    def __str__(self):
        return "face:%s vert:%s dpix:%s t:%s coord:%s" % (self._face_index, self._vertex_index, self.d, self.t, self.p)

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
        self._max_depth = 1
        self._back_faces = True
        # flag
        self._active = False
        self._is_snapping = False
        # exclude objects by name
        self._exclude = set()

        self.ray_origin = Vector()
        self.ray_direction = Vector()

        # snap raw object
        self._snap_loc = Vector()
        self._snap_raw = None
        self.snap_mode = 0

        self._rv3d = None
        self._region = None
        self._win_half = Vector((0, 0))

        self.gl_stack = None
        # snap final location with constraints
        self.snap_to = Vector()

    @property
    def x_ray(self):
        return self._max_depth > 1

    @x_ray.setter
    def x_ray(self, mode):
        if mode:
            self._max_depth = 100
        else:
            self._max_depth = 1

    def start(self, context):

        self._region = context.region
        self._rv3d = context.space_data.region_3d

        # setup gl stack
        # if self.gl_stack is None:
        self.gl_stack = SnapContext()
        self.gl_stack.set_pixel_dist(self._snap_radius)
        self.gl_stack.init_context(context.region, context.space_data)
        self.update_gl_snap()

        for o in context.visible_objects:
            if o.type == "CURVE":
                self.gl_stack.add_obj(o, o.matrix_world)

    def exit(self):
        # cleanup exclude
        self.clear_exclude()
        self.gl_stack.snap_objects.clear()

    def _scene_ray_cast(self, context, origin, direction):
        return context.scene.ray_cast(
            view_layer=context.view_layer,
            origin=origin,
            direction=direction)

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

    def _deep_cast(self, context, priority, screen_pixel_coord, hits):
        """ Find objects below mouse
        :param context:
        :param screen_pixel_coord:
        :param max_dist:
        :param max_depth:
        :return:
        """
        origin, direction = self._region_2d_to_orig_and_vect(screen_pixel_coord)
        hit = True
        depth = 0
        far_clip = self._far_clip
        dist = self._near_clip
        orig = origin + (direction * dist)

        # ray cast origin may be too close in ortho mode ..
        if not self._rv3d.is_perspective:
            far_clip += 100000
            orig -= direction * 100000

        while hit and dist < far_clip and depth < self._max_depth:
            hit, pos, normal, face_index, o, matrix_world = self._scene_ray_cast(
                context,
                orig,
                direction
            )
            if hit:
                dist = (orig - pos).length
                orig += direction * (dist + self._cast_threshold)
                if o.name not in self._exclude:
                    # normal -> vec are opposites, when facing length is 0 when opposite length is 2
                    # if self._back_faces or (matrix_world.to_quaternion() @ normal + direction).length < 1:
                    if o not in hits:
                        hits[o] = {}
                    # we only store one hit by face index
                    if face_index not in hits[o]:
                        hits[o][face_index] = tuple([pos, normal, matrix_world, priority])

                    depth += 1


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
            return 0
        else:
            c = n - t
            cray = c.cross(ray_direction)
            return cray.dot(n) / nlen

    def _min_edge_dist(self, p0, p1, origin, direction):
        t = self._ray_segment_t(p0, p1, origin, direction)
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
        return dpix.length  #max([abs(i) for i in dpix[:]]) #

    def _closest_mesh_vert(self, o, me, hits, closest):
        for face_index, hit in hits.items():
            if face_index < len(me.polygons):
                pos, normal, matrix_world, priority = hit
                verts = [(i, matrix_world @ me.vertices[i].co) for i in me.polygons[face_index].vertices]
                # n = matrix_world.to_quaternion() @ normal
                for i, co in verts:
                    dist = self._pixel_dist(co)
                    if dist < self._snap_radius:
                        closest.append(
                            SlCadSnapTarget(VERT, o, priority + dist, [co], normal, vertex_index=i, face_index=face_index)
                        )

    def _closest_subs(self, origin, direction, p0, p1, snap_radius):
        t, p, d = self._min_edge_dist(p0, p1, origin, direction)
        found = False
        dist = 1e32
        typ = None
        res = None
        fac = 0
        radius = snap_radius
        if (self.snap_mode & VERT) and (t < 0.3 or t > 0.7):
            ps = p0
            if t > 0.5:
                ps = p1
            dpix = self._pixel_dist(ps)
            if dpix < radius:
                typ = VERT
                res = [ps]
                fac = None
                found = True
                dist = d
                radius = dpix

        if (self.snap_mode & EDGE_CENTER) and (0.75 > t > 0.25):
            ps = 0.5 * (p0 + p1)
            dpix = self._pixel_dist(ps)
            if dpix < radius:
                typ = EDGE
                res = [ps, p0, p1]
                fac = t
                found = True
                dist = d
                radius = dpix

        if not found and (self.snap_mode & EDGE):
            if d < radius:
                typ = EDGE
                res = [p, p0, p1]
                fac = t
                found = True
                dist = d
                radius = d

        return found, (radius, typ, dist, res, fac)

    def _closest_mesh_face(self, o, me, origin, direction, hits, closest):
        snap_radius = self._snap_radius
        for face_index, hit in hits.items():
            if face_index < len(me.polygons):
                pos, normal, matrix_world, priority = hit
                dist = 1e32
                verts = [matrix_world @ me.vertices[v].co for v in me.polygons[face_index].vertices]
                res = [pos] + verts
                fac = None
                typ = FACE
                seek_radius = snap_radius
                if (self.snap_mode & (VERT | EDGE | EDGE_CENTER)):
                    for i, p1 in enumerate(verts):
                        p0 = verts[i - 1]
                        found, ret = self._closest_subs(
                            origin, direction, p0, p1, snap_radius
                        )
                        if found:
                            _snap_radius, typ, dist, res, fac = ret
                            if dist < seek_radius:
                                seek_radius = dist

                if (self.snap_mode & FACE_CENTER):
                    ps = matrix_world @ me.polygons[face_index].center
                    dpix = self._pixel_dist(ps)
                    if dpix < seek_radius:
                        typ = FACE
                        res = [ps] + verts
                        pos = ps

                if typ == FACE:
                    dist = self._pixel_dist(pos)
                    fac = None

                closest.append(
                    SlCadSnapTarget(typ, o, dist + priority, res, normal, t=fac)
                )

    def _closest_mesh_edge(self, o, me, origin, direction, hits, closest):
        snap_radius = self._snap_radius
        for face_index, hit in hits.items():
            if face_index < len(me.polygons):
                pos, normal, matrix_world, priority = hit
                verts = [matrix_world @ me.vertices[v].co for v in me.polygons[face_index].vertices]
                dist = 1e32
                typ = None
                fac = None
                res = []
                for i, p1 in enumerate(verts):
                    p0 = verts[i - 1]
                    found, ret = self._closest_subs(
                        origin, direction, p0, p1, snap_radius
                    )
                    if found:
                        _snap_radius, typ, dist, res, fac = ret

                if typ is not None:
                    closest.append(
                        SlCadSnapTarget(typ, o, dist + priority, res, normal, t=fac)
                    )
            else:
                print("_closest_mesh_edge face_index > n polys %s > %s" % (face_index, len(me.polygons)))

    def _closest_geometry(self, context, origin, direction, hits_dict, closest):
        t = time.time()
        depsgraph = context.evaluated_depsgraph_get()
        for o, hits in hits_dict.items():
            if o.type == "MESH":

                if len(o.modifiers) > 0:
                    me = o.evaluated_get(depsgraph).to_mesh()
                else:
                    me = o.data

                if (self.snap_mode & (FACE | FACE_CENTER)):
                    self._closest_mesh_face(o, me, origin, direction, hits, closest)

                elif (self.snap_mode & (EDGE | EDGE_CENTER)):
                    self._closest_mesh_edge(o, me, origin, direction, hits, closest)

                elif (self.snap_mode & VERT):
                    self._closest_mesh_vert(o, me, hits, closest)

        # print("_closest_geometry %.4f" % (time.time() - t))

    def _cast(self, context, hits, radius, use_center=True):
        t = time.time()
        
        cx, cy = self._center[0:2]
        da = 2 * pi / self._cast_samples
        # allow multiple attempts if nothing is found on radius
        n_hits, n_faces, max_depth = 0, 0, 0

        if use_center:
            self._deep_cast(context, 0, self._center, hits)

        for i in range(self._cast_samples):
            # cast multiple rays around radius
            a = i * da
            self._deep_cast(context, 0.00001, (cx + radius * cos(a), cy + radius * sin(a)), hits)
        n_hits, max_depth, n_faces = len(hits), 0, 0
        if n_hits > 0:
            _hits = [len(hit) for hit in hits.values()]
            max_depth = max(_hits)
            n_faces = sum(_hits)

        print("_cast objects:%s faces:%s depth:%s  %.4f" % (n_hits, n_faces, max_depth, time.time() - t))

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
            self.gl_stack.set_snap_mode(
                (self.snap_mode & VERT) != 0,
                (self.snap_mode & EDGE) != 0,
                (self.snap_mode & EDGE_CENTER) != 0
            )

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

    def snap(self, context, event):

        # flag to prevent overflow
        if self._active:
            return

        self._win_half = 0.5 * Vector((context.region.width, context.region.height))

        self._is_snapping = False
        self._active = True

        hits = {}
        closest_curve = []

        center, origin, direction = self.event_origin_and_direction(event)

        t = time.time()

        # fallback to gl for curves only, limited to knots and straight segments
        target, ret = self.gl_stack.snap(center)
        if target is not None and ret is not None:
            loc, pts, dist, fac = ret

            # print("snap gl_stack.snap(): data:%s loc:%s idx:%s  %.4f" % (target.data[0].name, loc, idx, time.time() - t))
            if loc is not None:
                typ = EDGE
                if fac is None:
                    typ = VERT
                closest_curve.append(
                    SlCadSnapTarget(typ, target.data[0], dist, pts, Z_AXIS, t=fac)
                )

        # snap to geometry
        use_center = True

        attempts = self._max_attempts
        # progressive grow of radius by attempts
        snap_radius_px = int(self._snap_radius / attempts)
        radius = 0
        while attempts > 0:

            closest = closest_curve[:]
            attempts -= 1
            radius += snap_radius_px

            if self.snap_mode & (VERT | EDGE | EDGE_CENTER | FACE):
                # Mesh snap rely on scene.ray_cast
                self._cast(context, hits, radius, use_center)

                use_center = False
                if len(hits) > 0:
                    self._closest_geometry(context, origin, direction, hits, closest)

            if self.snap_mode & GRID:
                # Snap to grid
                p0 = self._mouse_to_plane()
                if p0 is not None:
                    x, y, z = p0
                    p1 = Vector((round(x, 0), round(y, 0), round(z, 0)))
                    closest.append(
                        SlCadSnapTarget(GRID, None, self._pixel_dist(p1), [p1], Z_AXIS)
                    )

            if len(closest) > 0:

                closest.sort(key=lambda i: i.d)
                snap_raw = closest[0]

                for c in closest:
                    print(c)

                # snap proximity with mouse pointer
                if snap_raw.d < self._snap_radius:
                    self._snap_loc = snap_raw.p
                    self._snap_raw = snap_raw
                    self._is_snapping = True
                    break

        # print("snap: %.4f" % (time.time() - t))

        self._active = False

    def exclude_from_snap(self, objs):
        self._exclude = set([o.name for o in objs])
        self.gl_stack._exclude = self._exclude

    def clear_exclude(self):
        self._exclude.clear()
        self.gl_stack._exclude.clear()

