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
import gpu
from mathutils import Vector, Matrix

from .drawing import (
    GPU_Indices,
    TYP_OBJ,
    TYP_ORIGIN,
    TYP_BOUNDS,
    TYP_INSTANCE
)
from .utils_projection import (
    region_2d_to_orig_and_view_vector as _get_ray,
    intersect_boundbox_threshold,
    intersect_ray_segment_fac,
    intersect_ray_tri,
    project_co_v3,
    )

# Same as slcad_snap
KNOT = 1
SEGS = 2
SEGS_CENTER = 16
SEGS_PERPENDICULAR = 32
SEGS_PARALLEL = 64
FACE_CENTER = 128
FACE_NORMAL = 256
ORIGIN = 512
BOUNDS = 1024
INSTANCES = 2048

# display snap buffer as blender image
DEBUG_SNAP_BUFFER = False
DEBUG_COMARE_SNAP = False
DEBUG_DRAW_AS_IMAGE = False
USE_FRAMEBUFFER = True


class _SnapObjectData:
    def __init__(self, data, omat, typ=TYP_OBJ):
        self.data = data
        self.mat = omat
        self.typ = typ


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
        self.winsize = Vector((0, 0))

    def init_context(self, context):
        self.region = context.region
        self.rv3d = context.space_data.region_3d
        w, h = self.region.width, self.region.height
        self._offscreen = gpu.types.GPUOffScreen(w, h)
        self.winsize = Vector((w, h))

    def _get_snap_obj_by_index(self, index):
        for snap_obj in self.snap_objects[:self.drawn_count]:
            data = snap_obj.data[1]
            if index < data.first_index + data.get_tot_elems():
                return snap_obj
        return None

    def four_bytes_as_index(self, pixel):
        r, g, b, a = pixel
        idx = ((r * 255 + g) * 255 + b) * 255 + a
        return idx

    def _get_nearest_index(self):
        loc = [self._dist_px, self._dist_px]
        d = 1
        m = self.threshold
        maxi = 2 * m - 1
        offset = 1
        last_snap_obj = None
        r_value = 0

        if USE_FRAMEBUFFER:
            buf = self._snap_buffer.to_list()
        else:
            buf = self._snap_buffer

        while m < maxi:
            # axis x, y -> y, x in buffer
            for i in range(2):
                while 2 * loc[i] * d < m:
                    x, y = loc
                    raw = self.four_bytes_as_index(buf[y][x])
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
            if index < gpu_data.segs.num:

                seg_co = [snap_obj.mat @ Vector(v) for v in gpu_data.get_seg_co(index)]

                fac = intersect_ray_segment_fac(*seg_co, *self.last_ray)

                if (self._snap_mode & KNOT) and (not (0.75 > fac > 0.25) or not (self._snap_mode & SEGS_CENTER)):
                    co = seg_co[0] if fac < 0.5 else seg_co[1]
                    dist = self._max_pixel_dist(co)
                    if dist < self._dist_px:
                        return co, [co], dist, None, KNOT

                if (self._snap_mode & SEGS_CENTER) and ((0.75 > fac > 0.25) or not (self._snap_mode & KNOT)):
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

            index -= gpu_data.segs.num

        # use origin for isolated vertex as data structure is the same
        if gpu_data.draw_points:

            if index < gpu_data.points.num:
                co = Vector(gpu_data.get_points_co(index))
                dist = self._max_pixel_dist(co)
                if dist < self._dist_px:
                    if gpu_data.typ in {TYP_OBJ, TYP_INSTANCE}:
                        return co, [co], dist, None, KNOT
                    elif gpu_data.typ == TYP_ORIGIN:
                        return co, [co], dist, None, ORIGIN
                    elif gpu_data.typ == TYP_BOUNDS:
                        return co, [co], dist, None, BOUNDS
            index -= gpu_data.points.num

        if gpu_data.draw_tris:
            if index < gpu_data.tris.num:
                center, normal = [Vector(v) for v in gpu_data.get_face_normal_center(index)]
                co, normal = snap_obj.mat @ center, snap_obj.mat.to_3x3() @ normal
                if self._snap_mode & FACE_CENTER:
                    dist = self._max_pixel_dist(co)
                    if dist < self._dist_px:
                        return co, [co, normal], dist, None, FACE_CENTER
                if self._snap_mode & FACE_NORMAL:
                    tris_co = [snap_obj.mat @ Vector(v) for v in gpu_data.get_tris_co(index)]
                    intersect, co = intersect_ray_tri(*tris_co, *self.last_ray)
                    if intersect:
                        dist = self._max_pixel_dist(co)
                        if dist < self._dist_px:
                            return co, [co, normal], dist, None, FACE_NORMAL

            index -= gpu_data.tris.num

        return None

    def _get_snap_obj_by_typ(self, typ):
        for snap_obj in self.snap_objects:
            if snap_obj.typ == typ:
                self.snap_objects.append(_SnapObjectData(snap_obj.data, snap_obj.mat, typ))
                return True
        return False

    def _get_snap_obj_by_obj(self, obj):
        for snap_obj in self.snap_objects:
            if snap_obj.typ in {TYP_OBJ, TYP_INSTANCE} and obj == snap_obj.data[0]:
                return snap_obj

    def __del__(self):
        if not self.freed:
            self._offscreen.free()
            del self.snap_objects

    def update_all(self):
        self.drawn_count = 0
        self._offset_cur = 1
        self._offscreen.texture_color.clear(format='FLOAT', value=(0.0, 0.0, 0.0, 0.0))

    def set_pixel_dist(self, dist_px):
        self._dist_px = int(dist_px)
        self._dist_px_sq = self._dist_px ** 2
        self.threshold = 2 * self._dist_px + 1
        self._snap_buffer = None

    def set_snap_mode(self, snap_mode):
        s = snap_mode & (KNOT | SEGS | SEGS_CENTER | SEGS_PERPENDICULAR | SEGS_PARALLEL | ORIGIN | BOUNDS | INSTANCES)
        if s != self._snap_mode:
            self._snap_mode = s
            self.update_all()

    def add_bounds(self, context):

        if not self._get_snap_obj_by_typ(TYP_BOUNDS):
            bounds = []
            for o in context.visible_objects:
                tM = o.matrix_world
                bounds.extend([tM @  Vector(p) for p in o.bound_box])

            matrix = Matrix()
            self.snap_objects.append(_SnapObjectData([bounds], matrix, TYP_BOUNDS))

        return self.snap_objects[-1]

    def add_origins(self, context):
        # check isolate mode
        if not self._get_snap_obj_by_typ(TYP_ORIGIN):
            origins = [
                    o.matrix_world.translation.copy()
                    for o in context.visible_objects
                    ]
            # adds cursor to origins
            origins.append(context.scene.cursor.location.copy())

            matrix = Matrix()
            self.snap_objects.append(_SnapObjectData([origins], matrix, TYP_ORIGIN))

        return self.snap_objects[-1]

    def add_ghost(self, obj):

        snap_obj = self._get_snap_obj_by_obj(("ghost", obj))
        if not snap_obj:
            matrix = obj.matrix_world.copy()
            self.snap_objects.append(_SnapObjectData([("ghost", obj)], matrix, TYP_INSTANCE))
        else:
            self.snap_objects.append(_SnapObjectData(snap_obj.data, snap_obj.mat, TYP_INSTANCE))

        return self.snap_objects[-1]

    def add_instance(self, empty, obj):

        snap_obj = self._get_snap_obj_by_obj((empty, obj))
        if not snap_obj:
            matrix = empty.matrix_world @ obj.matrix_world
            self.snap_objects.append(_SnapObjectData([(empty, obj)], matrix, TYP_INSTANCE))
        else:
            self.snap_objects.append(_SnapObjectData(snap_obj.data, snap_obj.mat, TYP_INSTANCE))

        return self.snap_objects[-1]

    def add_obj(self, obj):
        # print("gl_stack.add_obj %s" % obj.name)
        # Cannot freeze wrapped/owned data
        snap_obj = self._get_snap_obj_by_obj(obj)
        if not snap_obj:
            matrix = obj.matrix_world.copy()
            self.snap_objects.append(_SnapObjectData([obj], matrix, TYP_OBJ))
        else:
            self.snap_objects.append(_SnapObjectData(snap_obj.data, snap_obj.mat, TYP_OBJ))

        return self.snap_objects[-1]

    def get_ray(self, mval):
        self.last_ray = _get_ray(self.region, self.rv3d, mval)
        return self.last_ray

    def draw(self):
        # For debug purposes
        # gpu_Indices_enable_state()
        _offset_cur = 0
        proj_mat = self.rv3d.perspective_matrix.copy()

        # multisample_enabled = bgl.glIsEnabled(bgl.GL_MULTISAMPLE)
        #
        # if multisample_enabled:
        #     bgl.glDisable(bgl.GL_MULTISAMPLE)
        #
        # dither_enabled = bgl.glIsEnabled(bgl.GL_DITHER)
        #
        # if dither_enabled:
        #     bgl.glDisable(bgl.GL_DITHER)

        # if self.proj_mat != proj_mat:
        # GPU_Indices.set_ProjectionMatrix(proj_mat)
            # clear buffer
            # bgl.glClearColor(0.0, 0.0, 0.0, 0.0)
            # bgl.glClear(bgl.GL_COLOR_BUFFER_BIT | bgl.GL_DEPTH_BUFFER_BIT)

        for i, snap_obj in enumerate(self.snap_objects):

            obj = snap_obj.data[0]

            # create shader and data for detail analysis
            if len(snap_obj.data) == 1:
                # tim = time.time()
                snap_obj.data.append(
                    GPU_Indices(obj, snap_obj.typ)
                )
                # print("create data %.4f" % (time.time() - tim))

            snap_obj.data[1].set_draw_mode(
                (self._snap_mode & ORIGIN) > 0,
                (self._snap_mode & BOUNDS) > 0,
                (self._snap_mode & (KNOT | SEGS | SEGS_CENTER | SEGS_PERPENDICULAR | SEGS_PARALLEL)) > 0,
                (self._snap_mode & (FACE_NORMAL | FACE_CENTER)) > 0
            )

            snap_obj.data[1].set_ModelViewMatrix(proj_mat @ snap_obj.mat)
            snap_obj.data[1].draw(_offset_cur)

            _offset_cur += snap_obj.data[1].get_tot_elems()

        # if dither_enabled:
        #     bgl.glEnable(bgl.GL_DITHER)  # dithering and AA break color coding, so disable #
        # if multisample_enabled:
        #     bgl.glEnable(bgl.GL_MULTISAMPLE)

        # gpu_Indices_restore_state()

    def read_texture(self, tex, x, y, w, h):
        pixels = tex.read()
        return gpu.types.Buffer("FLOAT", (h, w, 4), [pixels[y + j][x:x+w] for j in range(h)])

    def snap(self, mval):
        t = time.time()

        snap_obj = None

        ret = None
        self.mval[:] = mval

        with self._offscreen.bind():
            proj_mat = self.rv3d.perspective_matrix.copy()

            if self.proj_mat != proj_mat:
                self.proj_mat = proj_mat
                GPU_Indices.set_ProjectionMatrix(self.proj_mat)
                self.update_all()

            ray_dir, ray_orig = self.get_ray(mval)

            for i, snap_obj in enumerate(self.snap_objects[self.drawn_count:], self.drawn_count):

                obj = snap_obj.data[0]
                # origins
                if snap_obj.typ == TYP_ORIGIN:
                    # filter by visibility
                    in_threshold = (self._snap_mode & ORIGIN)

                elif snap_obj.typ == TYP_BOUNDS:
                    in_threshold = (self._snap_mode & BOUNDS)

                else:
                    # allow to hide some objects from snap, eg active object when moving
                    if obj is None or (snap_obj.typ != TYP_INSTANCE and (
                            obj.name in self._exclude or not obj.visible_get()
                            )):
                        # print("exclude %s" % obj.name)
                        continue

                    if snap_obj.typ == TYP_INSTANCE:
                        obj = obj[1]

                    bbmin = Vector(obj.bound_box[0])
                    bbmax = Vector(obj.bound_box[6])

                    # check objects under ray using bound box
                    if bbmin != bbmax:
                        MVP = proj_mat @ snap_obj.mat
                        mat_inv = snap_obj.mat.inverted()
                        ray_orig_local = mat_inv @ ray_orig
                        ray_dir_local = ray_dir @ snap_obj.mat
                        in_threshold = intersect_boundbox_threshold(
                            self, MVP, ray_orig_local, ray_dir_local, bbmin, bbmax
                        )

                    else:
                        dist = self._max_pixel_dist(snap_obj.mat.translation)
                        in_threshold = dist < self._dist_px

                # print("ray_orig %s  ray_dir %s  %s in_threshold %s" % (ray_orig, ray_dir, obj.name, in_threshold))

                if in_threshold:

                    # create shader and data for detail analysis
                    if len(snap_obj.data) == 1:
                        # tim = time.time()

                        snap_obj.data.append(
                            GPU_Indices(obj, snap_obj.typ)
                            )
                        # print("create data %.4f" % (time.time() - tim))

                    _sod =  snap_obj.data[1]

                    _sod.set_draw_mode(
                        (self._snap_mode & ORIGIN) > 0,
                        (self._snap_mode & BOUNDS) > 0,
                        (self._snap_mode & (KNOT | SEGS | SEGS_CENTER | SEGS_PERPENDICULAR | SEGS_PARALLEL)) > 0,
                        (self._snap_mode & (FACE_NORMAL | FACE_CENTER)) > 0
                    )

                    _sod.set_ModelViewMatrix(snap_obj.mat)
                    _sod.draw(self._offset_cur)

                    self._offset_cur += _sod.get_tot_elems()

                    # keep stack in growing offset order
                    self.snap_objects[self.drawn_count], self.snap_objects[i] = \
                        self.snap_objects[i], self.snap_objects[self.drawn_count]

                    self.drawn_count += 1

            w = h = self.threshold
            x = int(min(self.winsize.x - w, max(0, self.mval[0] - self._dist_px)))
            y = int(min(self.winsize.y - h, max(0, self.mval[1] - self._dist_px)))

            fb = gpu.state.active_framebuffer_get()

            if DEBUG_COMARE_SNAP:

                t = time.time()

                _test_buffer = fb.read_color(
                    x, y,
                    w, h,
                    4, 0, 'UBYTE'
                )
                t1 = time.time() - t

                t = time.time()
                self._snap_buffer = self.read_texture(
                    self._offscreen.texture_color,
                    x, y,
                    w, h
                )
                t2 = time.time() - t

                any_diff = any([
                    self.four_bytes_as_index(self._snap_buffer[i][j]) !=
                    self.four_bytes_as_index(_test_buffer[i][j])
                    for i in range(h)
                    for j in range(w)
                ])
                print(
                    "texture != frame_buffer",
                    any_diff,
                    "fb %.6f" % t1,
                    "tex %.6f" % t2
                )

                if any_diff:
                    for i in range(h):
                        for j in range(w):
                            if self.four_bytes_as_index(self._snap_buffer[i][j]) != \
                                    self.four_bytes_as_index(_test_buffer[i][j]):
                                print("diff", i, j, "tex", self._snap_buffer[i][j], "fb", _test_buffer[i][j])
                    raise Exception("Buffer != Texture")

            elif USE_FRAMEBUFFER:

                # 10x faster than reading from texture

                self._snap_buffer = fb.read_color(
                    x, y,
                    w, h,
                    4, 0, 'UBYTE'
                )
            else:
                self._snap_buffer = self.read_texture(
                    self._offscreen.texture_color,
                    x, y,
                    w, h
                )

            snap_obj, index = self._get_nearest_index()

            if snap_obj:
                ret = self._get_loc(snap_obj, index)

            if DEBUG_DRAW_AS_IMAGE:
                fb = gpu.state.active_framebuffer_get()
                self.as_image(
                    fb.read_color(0, 0, int(self.winsize.x), int(self.winsize.y), 4, 0, 'UBYTE'),
                    # self._offscreen.texture_color.read(),
                    int(self.winsize.x),
                    int(self.winsize.y),
                    "full_screen"
                )

            if DEBUG_SNAP_BUFFER:
                self.as_image(
                    self._snap_buffer,
                    w, h,
                    "snap_buffer"
                )

        # print("curve snap %s %.4f" % (len(self.snap_objects), time.time() - t))

        return snap_obj, ret

    def as_image(self, buffer, w, h, image_name):
        import bpy

        if image_name not in bpy.data.images:
            image = bpy.data.images.new(image_name,  w, h)
        else:
            image = bpy.data.images[image_name]
            image.scale(w, h)

        buffer.dimensions = w * h * 4
        image.pixels = [v *1000 for v in buffer]
        image.update()

    def free(self):
        self.__del__()
        self.freed = True


