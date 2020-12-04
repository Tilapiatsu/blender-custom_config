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

# Author Stephen Leger

# Inspired by 2.79 snap api:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

import time

import bgl
import gpu
from mathutils import Vector, Matrix

from .bgl_ext import VoidBufValue
from .drawing import GPU_Indices, gpu_Indices_enable_state, gpu_Indices_restore_state
from .utils_projection import (
    region_2d_to_orig_and_view_vector as _get_ray,
    intersect_boundbox_threshold,
    intersect_ray_segment_fac,
    project_co_v3,
    )

# Same as slcad_snap
KNOT = 1
SEGS = 2
SEGS_CENTER = 16
SEGS_PERPENDICULAR = 32
SEGS_PARALLEL = 64
ORIGIN = 512


class _SnapObjectData:
    def __init__(self, data, omat):
        self.data = data
        self.mat = omat


class SnapContext:

    def __init__(self):
        self._exclude = set()
        self.freed = False
        self.snap_objects = []
        self.drawn_count = 0
        self._offset_cur = 1     # Starts with index 1

        self.proj_mat = Matrix.Identity(4)
        # self.depth_range = Vector((space.clip_start, space.clip_end))
        self.mval = Vector((0, 0))
        self._snap_mode = KNOT | SEGS

        self._dist_px = 2
        self._dist_px_sq = 4
        self.threshold = 5
        self._snap_buffer = None
        self.last_ray = None

        self.region = None
        self.rv3d = None
        self.depth_range = Vector((0, 1e64))

        self.set_pixel_dist(12)
        self._offscreen = None
        self._texture = None
        self.winsize = Vector((0, 0))

    def init_context(self, context):
        self.region = context.region
        self.rv3d = context.space_data.region_3d
        # self.depth_range = Vector((space.clip_start, space.clip_end))
        w, h = self.region.width, self.region.height
        self._offscreen = gpu.types.GPUOffScreen(w, h)
        self._texture = self._offscreen.color_texture
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._texture)
        NULL = VoidBufValue(0)
        bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_R32UI, w, h, 0,
                         bgl.GL_RED_INTEGER, bgl.GL_UNSIGNED_INT, NULL.buf)
        del NULL
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
        self.winsize = Vector((self._offscreen.width, self._offscreen.height))

    def _get_snap_obj_by_index(self, index):
        for snap_obj in self.snap_objects[:self.drawn_count]:
            data = snap_obj.data[1]
            if index < data.first_index + data.get_tot_elems():
                return snap_obj
        return None

    def _get_nearest_index(self):
        loc = [self._dist_px, self._dist_px]
        d = 1
        m = self.threshold
        maxi = 2 * m - 1
        offset = 1
        last_snap_obj = None
        r_value = 0
        while m < maxi:
            # axis x, y
            for i in range(2):
                while 2 * loc[i] * d < m:
                    raw = self._snap_buffer[loc[0]][loc[1]]
                    # S.L fix numerical issue..  int truncating to lower
                    value = int(round(raw, 0))
                    loc[i] += d

                    if value >= offset:
                        # print(raw, value)
                        r_value = value
                        snap_obj = self._get_snap_obj_by_index(r_value)
                        return snap_obj, r_value
            d = -d
            m += 4 * self._dist_px * d + 1

        return last_snap_obj, r_value

    def _max_pixel_dist(self, co):
        proj_co = project_co_v3(self, co)
        dpix = self.mval - proj_co
        return max([abs(i) for i in dpix[:]])

    def _get_loc(self, snap_obj, index):
        index -= snap_obj.data[1].first_index
        gpu_data = snap_obj.data[1]

        if gpu_data.draw_segs:
            if index < gpu_data.num_segs:

                seg_co = [snap_obj.mat @ Vector(v) for v in gpu_data.get_seg_co(index)]
                fac = intersect_ray_segment_fac(*seg_co, *self.last_ray)

                if (self._snap_mode & KNOT) and (fac < 0.25 or fac > 0.75):
                    co = seg_co[0] if fac < 0.5 else seg_co[1]
                    dist = self._max_pixel_dist(co)
                    if dist < self._dist_px:
                        return co, [co], dist, None, KNOT

                if (self._snap_mode & SEGS_CENTER) and (0.75 > fac > 0.25):
                    co = 0.5 * (seg_co[0] + seg_co[1])
                    dist = self._max_pixel_dist(co)
                    if dist < self._dist_px:
                        return co, [co, seg_co[0], seg_co[1]], dist, fac, SEGS

                if self._snap_mode & (SEGS | SEGS_PERPENDICULAR | SEGS_PARALLEL):
                    co = seg_co[0] + fac * (seg_co[1] - seg_co[0])
                    if fac <= 0.0:
                        co = seg_co[0]
                    elif fac >= 1.0:
                        co = seg_co[1]
                    dist = self._max_pixel_dist(co)
                    if dist < self._dist_px:
                        return co, [co, seg_co[0], seg_co[1]], dist, fac, SEGS

            index -= gpu_data.num_segs

        # use origin for isolated vertex as data structure is the same
        if gpu_data.draw_origin and ((self._snap_mode & ORIGIN) or (gpu_data.is_mesh and (self._snap_mode & KNOT))):
            if index < gpu_data.num_origins:
                co = Vector(gpu_data.get_origin_co(index))
                dist = self._max_pixel_dist(co)
                if dist < self._dist_px:
                    if gpu_data.is_mesh:
                        return co, [co], dist, None, KNOT
                    else:
                        return co, [co], dist, None, ORIGIN
            index -= gpu_data.num_origins

        return None

    def _get_snap_obj_by_obj(self, obj):
        for snap_obj in self.snap_objects:
            if obj == snap_obj.data[0]:
                return snap_obj

    def __del__(self):
        if not self.freed:
            self._offscreen.free()
            del self.snap_objects

    def update_all(self):
        self.drawn_count = 0
        self._offset_cur = 1
        bgl.glClearColor(0.0, 0.0, 0.0, 0.0)
        bgl.glClear(bgl.GL_COLOR_BUFFER_BIT | bgl.GL_DEPTH_BUFFER_BIT)

    def update_drawn_snap_object(self, snap_obj):
        if len(snap_obj.data) > 1:
            del snap_obj.data[1:]
            # self.update_all()
            # Update on next snap_get call #
            self.proj_mat = Matrix.Identity(4)

    def set_pixel_dist(self, dist_px):
        self._dist_px = int(dist_px)
        self._dist_px_sq = self._dist_px ** 2
        self.threshold = 2 * self._dist_px + 1
        self._snap_buffer = bgl.Buffer(bgl.GL_FLOAT, (self.threshold, self.threshold))

    def set_snap_mode(self, snap_mode):
        s = snap_mode & (KNOT | SEGS | SEGS_CENTER | SEGS_PERPENDICULAR | SEGS_PARALLEL | ORIGIN)
        if s != self._snap_mode:
            self._snap_mode = s
            self.update_all()

    def add_origins(self, context):
        # check isolate mode
        origins = [o.matrix_world.translation.copy()
                   for o in context.visible_objects
                ]
        origins.append(context.scene.cursor.location.copy())

        matrix = Matrix()
        self.snap_objects.append(_SnapObjectData([origins], matrix))

        return self.snap_objects[-1]

    def add_obj(self, obj):
        # print("gl_stack.add_obj %s" % obj.name)
        # Cannot freeze wrapped/owned data
        matrix = obj.matrix_world.copy()
        snap_obj = self._get_snap_obj_by_obj(obj)
        if not snap_obj:
            self.snap_objects.append(_SnapObjectData([obj], matrix))
        else:
            self.snap_objects.append(_SnapObjectData(snap_obj.data, matrix))

        return self.snap_objects[-1]

    def get_ray(self, mval):
        self.last_ray = _get_ray(self.region, self.rv3d, mval)
        return self.last_ray

    def draw(self):
        # For debug purposes
        gpu_Indices_enable_state()
        _offset_cur = 128
        proj_mat = self.rv3d.perspective_matrix.copy()

        multisample_enabled = bgl.glIsEnabled(bgl.GL_MULTISAMPLE)

        if multisample_enabled:
            bgl.glDisable(bgl.GL_MULTISAMPLE)

        dither_enabled = bgl.glIsEnabled(bgl.GL_DITHER)

        if dither_enabled:
            bgl.glDisable(bgl.GL_DITHER)

        # if self.proj_mat != proj_mat:
        GPU_Indices.set_ProjectionMatrix(proj_mat)
            # clear buffer
            # bgl.glClearColor(0.0, 0.0, 0.0, 0.0)
            # bgl.glClear(bgl.GL_COLOR_BUFFER_BIT | bgl.GL_DEPTH_BUFFER_BIT)

        for i, snap_obj in enumerate(self.snap_objects):

            obj = snap_obj.data[0]

            # create shader and data for detail analysis
            if len(snap_obj.data) == 1:
                # tim = time.time()
                snap_obj.data.append(
                    GPU_Indices(obj)
                )
                # print("create data %.4f" % (time.time() - tim))

            snap_obj.data[1].set_draw_mode(
                (self._snap_mode & (KNOT | SEGS | SEGS_CENTER | SEGS_PERPENDICULAR | SEGS_PARALLEL)) > 0,
                (self._snap_mode & ORIGIN) > 0
            )

            snap_obj.data[1].set_ModelViewMatrix(snap_obj.mat)
            snap_obj.data[1].draw(_offset_cur)

            _offset_cur += snap_obj.data[1].get_tot_elems()

        if dither_enabled:
            bgl.glEnable(bgl.GL_DITHER)  # dithering and AA break color coding, so disable #
        if multisample_enabled:
            bgl.glEnable(bgl.GL_MULTISAMPLE)

        gpu_Indices_restore_state()

    def snap(self, mval):
        t = time.time()

        ret = None
        self.mval[:] = mval

        gpu_Indices_enable_state()
        with self._offscreen.bind():

            multisample_enabled = bgl.glIsEnabled(bgl.GL_MULTISAMPLE)

            if multisample_enabled:
                bgl.glDisable(bgl.GL_MULTISAMPLE)

            dither_enabled = bgl.glIsEnabled(bgl.GL_DITHER)

            if dither_enabled:
                bgl.glDisable(bgl.GL_DITHER)

            proj_mat = self.rv3d.perspective_matrix.copy()

            if self.proj_mat != proj_mat:
                self.proj_mat = proj_mat
                GPU_Indices.set_ProjectionMatrix(self.proj_mat)
                self.update_all()

            ray_dir, ray_orig = self.get_ray(mval)
            for i, snap_obj in enumerate(self.snap_objects[self.drawn_count:], self.drawn_count):

                obj = snap_obj.data[0]

                # origins
                if obj.__class__.__name__ == 'list':
                    # filter by visibility
                    in_threshold = (self._snap_mode & ORIGIN)
                else:
                    # allow to hide some objects from snap, eg active object when moving
                    if obj is None or obj.name in self._exclude or not obj.visible_get():
                        # print("exclude %s" % obj.name)
                        continue

                    bbmin = Vector(obj.bound_box[0])
                    bbmax = Vector(obj.bound_box[6])

                    # check objects under ray using bound box
                    if bbmin != bbmax:
                        MVP = proj_mat @ snap_obj.mat
                        mat_inv = snap_obj.mat.inverted()
                        ray_orig_local = mat_inv @ ray_orig
                        ray_dir_local = ray_dir @ snap_obj.mat
                        in_threshold = intersect_boundbox_threshold(self, MVP, ray_orig_local, ray_dir_local, bbmin, bbmax)

                    else:
                        dist = self._max_pixel_dist(snap_obj.mat.translation)
                        in_threshold = dist < self._dist_px

                # print("ray_orig %s  ray_dir %s  %s in_threshold %s" % (ray_orig, ray_dir, obj.name, in_threshold))

                if in_threshold:

                    # create shader and data for detail analysis
                    if len(snap_obj.data) == 1:
                        # tim = time.time()

                        snap_obj.data.append(
                            GPU_Indices(obj)
                            )
                        # print("create data %.4f" % (time.time() - tim))

                    snap_obj.data[1].set_draw_mode(
                        (self._snap_mode & (KNOT | SEGS | SEGS_CENTER | SEGS_PERPENDICULAR | SEGS_PARALLEL)) > 0,
                        (self._snap_mode & ORIGIN) > 0
                    )
                    snap_obj.data[1].set_ModelViewMatrix(snap_obj.mat)
                    snap_obj.data[1].draw(self._offset_cur)

                    self._offset_cur += snap_obj.data[1].get_tot_elems()

                    self.snap_objects[self.drawn_count], self.snap_objects[i] = \
                        self.snap_objects[i], self.snap_objects[self.drawn_count]
                    self.drawn_count += 1

            bgl.glReadBuffer(bgl.GL_COLOR_ATTACHMENT0)
            bgl.glReadPixels(
                    int(self.mval[0]) - self._dist_px, int(self.mval[1]) - self._dist_px,
                    self.threshold, self.threshold, bgl.GL_RED_INTEGER, bgl.GL_UNSIGNED_INT, self._snap_buffer)
            bgl.glReadBuffer(bgl.GL_BACK)

            snap_obj, index = self._get_nearest_index()

            if snap_obj:
                ret = self._get_loc(snap_obj, index)

            # print(ret)
            # print(self._snap_buffer[:])
            if dither_enabled:
                bgl.glEnable(bgl.GL_DITHER)  # dithering and AA break color coding, so disable #
            if multisample_enabled:
                bgl.glEnable(bgl.GL_MULTISAMPLE)

        # self._offscreen.unbind()
        gpu_Indices_restore_state()

        # print("curve snap %s %.4f" % (len(self.snap_objects), time.time() - t))

        return snap_obj, ret

    def free(self):
        self.__del__()
        self.freed = True

