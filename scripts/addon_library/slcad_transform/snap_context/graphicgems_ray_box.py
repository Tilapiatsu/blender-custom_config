# -*- coding:utf-8 -*-

# Pure python port of GraphicGems ray_box()

# source : https://github.com/erich666/GraphicsGems/blob/master/gems/RayBox.c
#
# LICENSE
#
# This code repository predates the concept of Open Source, and predates most licenses along such lines.
# As such, the official license truly is:
#
# EULA: The Graphics Gems code is copyright-protected.
# In other words, you cannot claim the text of the code as your own and resell it.
# Using the code is permitted in any program, product, or library,
# non-commercial or commercial. Giving credit is not required, though is a nice gesture.
# The code comes as-is, and if there are any flaws or problems with any Gems code,
# nobody involved with Gems - authors, editors, publishers, or webmasters - are to be held responsible.
# Basically, don't be a jerk, and remember that anything free comes with no guarantee.


from mathutils import Vector


RIGHT = 0
LEFT = 1
MIDDLE = 2


def ray_box(ray_origin_local, ray_direction_local, bbmin, bbmax):
    inside = True
    dims = 3
    quadrant = [0] * dims
    whichPlane = 0
    maxT = Vector()
    candidatePlane = [0] * dims
    coord = Vector()
    # Find candidate planes; this loop can be avoided if
    # rays cast all from the eye(assume perpsective view) */

    for i in range(dims):
        if ray_origin_local[i] < bbmin[i]:
            quadrant[i] = LEFT
            candidatePlane[i] = bbmin[i]
            inside = False
        elif ray_origin_local[i] > bbmax[i]:
            quadrant[i] = RIGHT
            candidatePlane[i] = bbmax[i]
            inside = False
        else:
            quadrant[i] = MIDDLE

    # Ray origin inside bounding box */
    if inside:
        # coord = ray_origin_local
        return True

    # Calculate T distances to candidate planes */
    for i in range(dims):
        if quadrant[i] != MIDDLE and ray_direction_local[i] != 0:
            maxT[i] = (candidatePlane[i] - ray_origin_local[i]) / ray_direction_local[i]
        else:
            maxT[i] = -1

    # Get largest of the maxT's for final choice of intersection */
    for i in range(dims):
        if maxT[whichPlane] < maxT[i]:
            whichPlane = i

    # Check final candidate actually inside box * /
    if maxT[whichPlane] < 0:
        return False

    for i in range(dims):
        if whichPlane != i:
            coord[i] = ray_origin_local[i] + maxT[whichPlane] * ray_direction_local[i]
            if coord[i] < bbmin[i] or coord[i] > bbmax[i]:
                return False
        else:
            coord[i] = candidatePlane[i]

    return True  # ray hits box

