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

from .graphicgems_ray_box import ray_box
from mathutils import Vector


def depth_get(co, ray_start, ray_dir):
    dvec = co - ray_start
    return dvec.dot(ray_dir)


def region_2d_to_orig_and_view_vector(region, rv3d, coord):
    viewinv = rv3d.view_matrix.inverted()
    persinv = rv3d.perspective_matrix.inverted()

    x, y = region.width, region.height

    dx = (2.0 * coord[0] / x) - 1.0
    dy = (2.0 * coord[1] / y) - 1.0
    # print("region size", x, y, dx, dy, persinv[3].xyz.length)

    if rv3d.is_perspective:
        origin_start = viewinv.translation.copy()

        out = Vector((dx, dy, -0.5))

        w = out.dot(persinv[3].xyz) + persinv[3][3]

        view_vector = ((persinv @ out) / w) - origin_start
    else:
        view_vector = -viewinv.col[2].xyz

        origin_start = ((persinv.col[0].xyz * dx) +
                        (persinv.col[1].xyz * dy) +
                        persinv.translation)

        if rv3d.view_perspective != 'CAMERA':
            # S.L in ortho view, origin may be plain wrong so add arbitrary distance ..
            origin_start -= view_vector * 1000

    view_vector.normalize()
    return view_vector, origin_start


def project_co_v3(sctx, co):
    proj_co = sctx.proj_mat @ co.to_4d()
    proj_co.xy /= proj_co.w

    win_half = sctx.winsize * 0.5
    proj_co[0] = (proj_co[0] + 1.0) * win_half[0]
    proj_co[1] = (proj_co[1] + 1.0) * win_half[1]

    return proj_co.xy


def intersect_ray_segment_fac(v0, v1, ray_direction, ray_origin):
    a = v1 - v0
    t = v0 - ray_origin
    n = a.cross(ray_direction)
    nlen = n.length_squared

    # if (nlen == 0.0f) the lines are parallel, has no nearest point, only distance squared.*/
    if nlen == 0.0:
        # Calculate the distance to the nearest point to origin then #
        return a.dot(ray_direction) < 0
    else:
        c = n - t
        cray = c.cross(ray_direction)
        return cray.dot(n) / nlen


def intersect_boundbox_threshold(sctx, MVP, ray_origin_local, ray_direction_local, bbmin, bbmax):
    # fix issue with axis aligned curve
    threshold = Vector((0.1, 0.1, 0.1))
    return ray_box(ray_origin_local, ray_direction_local, bbmin - threshold, bbmax + threshold)

