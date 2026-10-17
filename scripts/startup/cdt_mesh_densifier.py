bl_info = {
    "name": "CDT Mesh Densifier",
    "author": "OpenAI",
    "version": (0, 7, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Item > CDT Densifier",
    "description": "Duplicate a mesh and densify selected triangles while preserving shared boundaries",
    "category": "Mesh",
}

import math
import os
import random
import re
from array import array

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

# -----------------------------------------------------------------------------
# 2D geometry helpers
# -----------------------------------------------------------------------------


def cross2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def point_in_triangle_2d(p, a, b, c, eps=1e-10):
    c1 = cross2(a, b, p)
    c2 = cross2(b, c, p)
    c3 = cross2(c, a, p)
    return (c1 >= -eps and c2 >= -eps and c3 >= -eps) or (c1 <= eps and c2 <= eps and c3 <= eps)


def _projected_intervals_overlap(poly, axis, rect):
    p_values = [p[0] * axis[0] + p[1] * axis[1] for p in poly]
    r_values = [p[0] * axis[0] + p[1] * axis[1] for p in rect]
    return max(p_values) >= min(r_values) - 1e-12 and max(r_values) >= min(p_values) - 1e-12


def triangle_intersects_rect(tri, xmin, ymin, xmax, ymax):
    """Separating-axis test: does a UV triangle intersect a texel rectangle?"""
    rect = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    axes = [(1.0, 0.0), (0.0, 1.0)]
    for i in range(3):
        a, b = tri[i], tri[(i + 1) % 3]
        dx, dy = b[0] - a[0], b[1] - a[1]
        axes.append((-dy, dx))
    return all(_projected_intervals_overlap(tri, axis, rect) for axis in axes)


def _mask_pixel_value(rgba, channel):
    r, g, b, a = rgba
    if channel == "RED":
        return r
    if channel == "GREEN":
        return g
    if channel == "BLUE":
        return b
    if channel == "ALPHA":
        return a
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


class ImageMask:
    """Cached UV-space image mask, including per-tile UDIM pixel buffers.

    For UDIM images, each tile is read through Blender's active-tile image
    buffer. Missing tiles are treated as inactive. UV coordinates are mapped
    to tile numbers using the standard UDIM formula.
    """

    def __init__(self, image, threshold=0.0, channel="LUMINANCE"):
        if image is None:
            raise ValueError("No mask image was supplied.")
        self.image = image
        self.threshold = float(threshold)
        self.channel = channel
        self.is_tiled = image.source == "TILED"
        self.tiles = {}
        # Lazily computed active-pixel bounds make black/mostly-empty masks
        # inexpensive to query across meshes with many triangles.
        self.active_bounds = {}

        if self.is_tiled:
            tile_numbers = [int(tile.number) for tile in image.tiles]
            if not tile_numbers:
                raise ValueError(f"UDIM image '{image.name}' has no tiles.")

            # Important Blender API limitation: image.pixels.foreach_get() reads
            # tile 1001 even when tiles.active_index points at another tile.
            # Therefore, load each file-backed tile as a temporary ordinary image
            # instead of pretending active_index changes the pixel buffer.
            image_path = bpy.path.abspath(image.filepath) if image.filepath else ""
            has_udim_token = "<UDIM>" in image_path.upper()
            for tile in image.tiles:
                number = int(tile.number)
                tile_pixels = None
                width = height = 0

                # Generated UDIM tiles have a uniform generated color; preserve
                # that color without trying to access a nonexistent pixel buffer.
                if getattr(tile, "is_generated_tile", False):
                    width, height = map(int, tile.size[:2])
                    if width < 1 or height < 1:
                        width = int(getattr(tile, "generated_width", 0) or image.size[0])
                        height = int(getattr(tile, "generated_height", 0) or image.size[1])
                    if width > 0 and height > 0:
                        rgba = tuple(float(c) for c in tile.generated_color)
                        tile_pixels = array("f", rgba) * (width * height)

                # External UDIM image sets use a filename token such as
                # texture.<UDIM>.png. Load each concrete file independently.
                if tile_pixels is None and has_udim_token:
                    concrete_path = re.sub(r"<UDIM>", str(number), image_path, flags=re.IGNORECASE)
                    if os.path.isfile(concrete_path):
                        temp_image = None
                        try:
                            temp_image = bpy.data.images.load(concrete_path, check_existing=False)
                            width, height = map(int, temp_image.size[:2])
                            if width > 0 and height > 0:
                                tile_pixels = array("f", [0.0]) * (width * height * 4)
                                temp_image.pixels.foreach_get(tile_pixels)
                        finally:
                            if temp_image is not None:
                                bpy.data.images.remove(temp_image)

                # Packed or otherwise non-file-backed tile 1001 can still be read
                # from the image datablock. Blender's public Python pixel buffer
                # does not expose packed non-1001 tile buffers independently.
                if tile_pixels is None and number == 1001:
                    width, height = map(int, image.size[:2])
                    if width > 0 and height > 0:
                        tile_pixels = array("f", [0.0]) * (width * height * 4)
                        image.pixels.foreach_get(tile_pixels)

                if tile_pixels is not None and width > 0 and height > 0:
                    self.tiles[number] = (width, height, tile_pixels)

            if not self.tiles:
                raise ValueError(
                    f"UDIM image '{image.name}' has no readable tile pixels. "
                    "For file-backed UDIMs, use a filepath containing <UDIM>."
                )
            missing = sorted(set(tile_numbers) - set(self.tiles))
            if missing:
                raise ValueError(
                    f"Could not read UDIM tile(s) {', '.join(map(str, missing))} from '{image.name}'. "
                    "Blender's Python image.pixels API only exposes tile 1001 directly; "
                    "make sure each tile exists as a separate file matching the <UDIM> filepath."
                )
        else:
            width, height = map(int, image.size[:2])
            if width < 1 or height < 1:
                raise ValueError(f"Mask image '{image.name}' has no pixel data.")
            pixels = array("f", [0.0]) * (width * height * 4)
            image.pixels.foreach_get(pixels)
            self.tiles[1001] = (width, height, pixels)

    @staticmethod
    def _tile_for_uv(u, v):
        """Return (UDIM number, local U, local V), or None for negative UVs."""
        if u < 0.0 or v < 0.0:
            return None
        tile_u = int(math.floor(u))
        tile_v = int(math.floor(v))
        return 1001 + tile_u + 10 * tile_v, u - tile_u, v - tile_v

    def value_at_uv(self, uv):
        u, v = float(uv.x), float(uv.y)
        mapped = self._tile_for_uv(u, v)
        if mapped is None:
            return 0.0
        tile_number, local_u, local_v = mapped
        if not self.is_tiled and tile_number != 1001:
            return 0.0
        tile_data = self.tiles.get(tile_number)
        if tile_data is None:
            return 0.0
        width, height, pixels = tile_data
        # Avoid treating an exact tile boundary as the last texel of the
        # previous tile; floor() maps it to the tile on the positive side.
        x = min(width - 1, max(0, int(math.floor(local_u * width))))
        y = min(height - 1, max(0, int(math.floor(local_v * height))))
        idx = (y * width + x) * 4
        return _mask_pixel_value(pixels[idx : idx + 4], self.channel)

    def uv_is_active(self, uv):
        return self.value_at_uv(uv) > self.threshold

    def triangle_active_fraction(self, uv_triangle):
        """Estimate active coverage from interior samples, across UDIM tiles.

        This intentionally avoids the old 'any active texel touched' rule,
        which caused a large UV triangle to be selected by a tiny active texel.
        It remains a triangle-level approximation, not exact mask clipping.
        """
        a, b, c = [Vector((float(uv.x), float(uv.y))) for uv in uv_triangle]
        samples = (
            (a + b + c) / 3.0,
            a * 0.6 + b * 0.2 + c * 0.2,
            a * 0.2 + b * 0.6 + c * 0.2,
            a * 0.2 + b * 0.2 + c * 0.6,
            (a + b) * 0.5,
            (b + c) * 0.5,
            (c + a) * 0.5,
        )
        active = sum(self.uv_is_active(uv) for uv in samples)
        return active / len(samples)

    def _tile_uv_origin(self, tile_number):
        index = int(tile_number) - 1001
        return float(index % 10), float(index // 10)

    def _active_pixel_bounds(self, tile_number):
        if tile_number in self.active_bounds:
            return self.active_bounds[tile_number]
        width, height, pixels = self.tiles[tile_number]
        min_x, min_y, max_x, max_y = width, height, -1, -1
        for y in range(height):
            row = y * width * 4
            for x in range(width):
                idx = row + x * 4
                if _mask_pixel_value(pixels[idx : idx + 4], self.channel) > self.threshold:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        bounds = None if max_x < 0 else (min_x, min_y, max_x, max_y)
        self.active_bounds[tile_number] = bounds
        return bounds

    def triangle_has_nonzero_texel(self, uv_triangle):
        """Return True if any active texel intersects the UV triangle.

        Unlike triangle_active_fraction(), this is a precise *selection test*:
        it detects small strokes even when they occupy much less than half of a
        large triangle. It does not mean the whole triangle will be densely
        sampled; interior points are filtered against the mask separately.
        """
        tri = [(float(uv.x), float(uv.y)) for uv in uv_triangle]
        tri_min_u = min(p[0] for p in tri)
        tri_max_u = max(p[0] for p in tri)
        tri_min_v = min(p[1] for p in tri)
        tri_max_v = max(p[1] for p in tri)

        for tile_number, (width, height, pixels) in self.tiles.items():
            tile_u, tile_v = self._tile_uv_origin(tile_number)
            if not self.is_tiled and tile_number != 1001:
                continue
            active_bounds = self._active_pixel_bounds(tile_number)
            if active_bounds is None:
                continue
            active_x0, active_y0, active_x1, active_y1 = active_bounds
            min_u = max(tri_min_u, tile_u)
            max_u = min(tri_max_u, tile_u + 1.0)
            min_v = max(tri_min_v, tile_v)
            max_v = min(tri_max_v, tile_v + 1.0)
            if min_u > max_u or min_v > max_v:
                continue

            x0 = max(active_x0, 0, min(width - 1, int(math.floor((min_u - tile_u) * width))))
            x1 = min(active_x1, width - 1, max(0, int(math.floor((max_u - tile_u) * width))))
            y0 = max(active_y0, 0, min(height - 1, int(math.floor((min_v - tile_v) * height))))
            y1 = min(active_y1, height - 1, max(0, int(math.floor((max_v - tile_v) * height))))
            if x0 > x1 or y0 > y1:
                continue

            for y in range(y0, y1 + 1):
                py0 = tile_v + y / height
                py1 = tile_v + (y + 1) / height
                row = y * width * 4
                for x in range(x0, x1 + 1):
                    idx = row + x * 4
                    rgba = pixels[idx : idx + 4]
                    if _mask_pixel_value(rgba, self.channel) <= self.threshold:
                        continue
                    px0 = tile_u + x / width
                    px1 = tile_u + (x + 1) / width
                    if triangle_intersects_rect(tri, px0, py0, px1, py1):
                        return True
        return False

    def active_edge_parameters(self, uv_a, uv_b, world_length, spacing):
        """Return edge parameters to split only painted portions of a UV edge.

        The edge is sampled at half-texel intervals. Each contiguous run of
        active samples is split independently, so a painted stroke does not
        cause the unpainted remainder of the same mesh edge to be subdivided.
        Returned values are normalized parameters in the open interval (0, 1).
        """
        a = Vector((float(uv_a.x), float(uv_a.y)))
        b = Vector((float(uv_b.x), float(uv_b.y)))
        max_steps = 1
        for width, height, _pixels in self.tiles.values():
            max_steps = max(max_steps, int(math.ceil(max(abs(b.x - a.x) * width, abs(b.y - a.y) * height) * 2.0)))
        max_steps = min(max_steps, 200000)
        active = [self.uv_is_active(a.lerp(b, i / max_steps)) for i in range(max_steps + 1)]
        params = set()
        i = 0
        while i <= max_steps:
            if not active[i]:
                i += 1
                continue
            start = i
            while i + 1 <= max_steps and active[i + 1]:
                i += 1
            end = i
            t0 = start / max_steps
            t1 = end / max_steps
            if 0.0 < t0 < 1.0:
                params.add(t0)
            if 0.0 < t1 < 1.0:
                params.add(t1)
            run_length = max(0.0, (t1 - t0) * world_length)
            segments = max(1, int(math.ceil(run_length / spacing)))
            for j in range(1, segments):
                t = t0 + (t1 - t0) * (j / segments)
                if 0.0 < t < 1.0:
                    params.add(t)
            i += 1
        return sorted(params)

    def active_texel_centers_in_triangle(self, uv_triangle, limit=5000):
        """Return active texel-center UVs inside a triangle, with bounded memory.

        Used as a fallback when random world-space samples miss a thin brush
        stroke. The scan is restricted to the triangle's UV bounding box.
        """
        tri = [(float(uv.x), float(uv.y)) for uv in uv_triangle]
        tri_min_u = min(p[0] for p in tri)
        tri_max_u = max(p[0] for p in tri)
        tri_min_v = min(p[1] for p in tri)
        tri_max_v = max(p[1] for p in tri)
        found = []
        seen = 0
        for tile_number, (width, height, pixels) in self.tiles.items():
            tile_u, tile_v = self._tile_uv_origin(tile_number)
            active_bounds = self._active_pixel_bounds(tile_number)
            if active_bounds is None:
                continue
            active_x0, active_y0, active_x1, active_y1 = active_bounds
            min_u = max(tri_min_u, tile_u)
            max_u = min(tri_max_u, tile_u + 1.0)
            min_v = max(tri_min_v, tile_v)
            max_v = min(tri_max_v, tile_v + 1.0)
            if min_u > max_u or min_v > max_v:
                continue
            x0 = max(active_x0, 0, min(width - 1, int(math.floor((min_u - tile_u) * width))))
            x1 = min(active_x1, width - 1, max(0, int(math.floor((max_u - tile_u) * width))))
            y0 = max(active_y0, 0, min(height - 1, int(math.floor((min_v - tile_v) * height))))
            y1 = min(active_y1, height - 1, max(0, int(math.floor((max_v - tile_v) * height))))
            if x0 > x1 or y0 > y1:
                continue
            for y in range(y0, y1 + 1):
                row = y * width * 4
                v = tile_v + (y + 0.5) / height
                for x in range(x0, x1 + 1):
                    idx = row + x * 4
                    if _mask_pixel_value(pixels[idx : idx + 4], self.channel) <= self.threshold:
                        continue
                    u = tile_u + (x + 0.5) / width
                    if not point_in_triangle_2d((u, v), *tri):
                        continue
                    seen += 1
                    # Reservoir sampling prevents a solid/large mask from
                    # biasing the fallback toward the first scanlines.
                    uv = Vector((u, v))
                    if len(found) < limit:
                        found.append(uv)
                    else:
                        j = self._reservoir_index(seen)
                        if j < limit:
                            found[j] = uv
        return found

    @staticmethod
    def _reservoir_index(seen):
        return random.randrange(seen)


# -----------------------------------------------------------------------------
# Sampling and local coordinate helpers
# -----------------------------------------------------------------------------


def triangle_basis(p0, p1, p2):
    e1 = p1 - p0
    if e1.length_squared < 1e-20:
        return None
    normal = e1.cross(p2 - p0)
    if normal.length_squared < 1e-20:
        return None
    x_axis = e1.normalized()
    normal.normalize()
    y_axis = normal.cross(x_axis).normalized()

    def project(p):
        d = p - p0
        return (d.dot(x_axis), d.dot(y_axis))

    def unproject(p2d):
        return p0 + x_axis * p2d[0] + y_axis * p2d[1]

    return project, unproject


def sample_triangle(a, b, c, spacing, rng, max_samples):
    """Bounded Poisson-like rejection sampling inside a triangle."""
    if max_samples <= 0 or spacing <= 0:
        return []
    area = 0.5 * (b - a).cross(c - a).length
    if area <= 1e-14:
        return []

    target = max(0, int(area / (0.866025403784 * spacing * spacing)))
    target = min(target, max_samples)
    if target == 0:
        return []

    ab, bc, ca = (b - a).length, (c - b).length, (a - c).length
    samples = []
    min_dist_sq = (spacing * 0.82) ** 2
    max_attempts = max(100, target * 30)

    for _ in range(max_attempts):
        if len(samples) >= target:
            break
        u, v = rng.random(), rng.random()
        if u + v > 1.0:
            u, v = 1.0 - u, 1.0 - v
        p = a + (b - a) * u + (c - a) * v
        margin = min(
            (p - a).cross(b - a).length / max(ab, 1e-12),
            (p - b).cross(c - b).length / max(bc, 1e-12),
            (p - c).cross(a - c).length / max(ca, 1e-12),
        )
        # Leave space near constrained edges; edge vertices are fixed separately.
        if margin < spacing * 0.12:
            continue
        if all((p - q).length_squared >= min_dist_sq for q in samples):
            samples.append(p)
    return samples


def barycentric_weights_2d(p, a, b, c):
    denom = cross2(a, b, c)
    if abs(denom) < 1e-15:
        return (1.0, 0.0, 0.0)
    w0 = cross2(p, b, c) / denom
    w1 = cross2(a, p, c) / denom
    w2 = cross2(a, b, p) / denom
    return w0, w1, w2


def sample_masked_triangle(p0, p1, p2, uv0, uv1, uv2, spacing, rng, max_samples, mask):
    """Generate interior points only where the image mask is active.

    Random world-space candidates provide spacing-aware coverage. If a narrow
    stroke is missed (or under-sampled), active texel centers provide fallback
    candidates. CDT still triangulates the complete source triangle, so the
    unpainted area remains coarse instead of being densely sampled everywhere.
    """
    if max_samples <= 0:
        return []
    uv_tri = [Vector(uv0), Vector(uv1), Vector(uv2)]
    basis = triangle_basis(p0, p1, p2)
    if basis is None:
        return []
    project, _unproject = basis
    tri2 = [project(p0), project(p1), project(p2)]
    denom = cross2(*tri2)
    if abs(denom) < 1e-15:
        return []

    area = 0.5 * (p1 - p0).cross(p2 - p0).length
    target = min(max_samples, max(1, int(area / (0.866025403784 * spacing * spacing))))
    # Oversample modestly so painted areas smaller than the triangle have a
    # chance to receive points, but cap attempts to keep the operation bounded.
    raw = sample_triangle(p0, p1, p2, spacing, rng, min(max_samples, max(target * 4, 32)))
    candidates = []
    for point in raw:
        q = project(point)
        weights = barycentric_weights_2d(q, *tri2)
        uv = uv_tri[0] * weights[0] + uv_tri[1] * weights[1] + uv_tri[2] * weights[2]
        if mask.uv_is_active(uv):
            candidates.append(point)

    # Only perform the more expensive texel scan when random sampling did not
    # provide enough points. This is what makes tiny strokes inside huge faces
    # discoverable without scanning every pixel for every triangle.
    if len(candidates) < min(max(1, int(target * 0.25)), 32):
        uv_centers = mask.active_texel_centers_in_triangle(uv_tri, limit=min(5000, max(256, target * 8)))
        for uv in uv_centers:
            weights = barycentric_weights_2d((uv.x, uv.y), *[(q.x, q.y) for q in uv_tri])
            point = p0 * weights[0] + p1 * weights[1] + p2 * weights[2]
            candidates.append(point)

    rng.shuffle(candidates)
    accepted = []
    min_dist_sq = (spacing * 0.82) ** 2
    for point in candidates:
        if all((point - existing).length_squared >= min_dist_sq for existing in accepted):
            accepted.append(point)
            if len(accepted) >= target:
                break
    return accepted


# -----------------------------------------------------------------------------
# Main densifier
# -----------------------------------------------------------------------------


class CDTMeshDensifier:
    """Create a triangulated duplicate while keeping original vertices fixed.

    For image masks, edges are split only within sampled painted runs along
    their UVs. Triangles intersecting painted texels are processed, but interior
    points are added only at masked UV positions. This supports small strokes in
    the middle of large polygons while leaving unpainted areas comparatively
    coarse. UDIM mask sampling supports tile-number lookup (1001 + U + 10*V).
    """

    def __init__(
        self,
        obj,
        spacing_cm=10.0,
        max_vertices=500_000,
        seed=1,
        mask_image=None,
        mask_threshold=0.0,
        mask_channel="LUMINANCE",
        mask_attribute_name="MaskValue",
        preserve_custom_normals=True,
    ):
        if obj is None or obj.type != "MESH":
            raise TypeError("Active object must be a mesh object.")
        if spacing_cm <= 0:
            raise ValueError("Spacing must be greater than zero.")
        if max_vertices < len(obj.data.vertices):
            raise ValueError("Vertex limit is lower than the number of original vertices.")

        self.obj = obj
        self.mesh = obj.data
        unit_scale = bpy.context.scene.unit_settings.scale_length or 1.0
        self.spacing_world = (spacing_cm * 0.01) / unit_scale
        self.max_vertices = int(max_vertices)
        self.seed = int(seed)
        self.rng = random.Random(seed)
        self.mask_image = mask_image
        self.mask_threshold = mask_threshold
        self.mask_channel = mask_channel
        self.mask_attribute_name = (mask_attribute_name or "MaskValue").strip() or "MaskValue"
        self.preserve_custom_normals = preserve_custom_normals

    def build(self):
        src = self.mesh
        src.calc_loop_triangles()
        matrix_world = self.obj.matrix_world.copy()
        inverse_world = matrix_world.inverted_safe()
        original_local = [v.co.copy() for v in src.vertices]
        original_world = [matrix_world @ co for co in original_local]

        try:
            src_corner_normals = [loop.normal.copy() for loop in src.loops]
        except Exception:
            src_corner_normals = [Vector((0.0, 0.0, 1.0)) for _ in src.loops]

        source_uv_layers = list(src.uv_layers)
        uv_layer = src.uv_layers.active if self.mask_image else None
        if self.mask_image and uv_layer is None:
            raise ValueError("A UV map is required when an image mask is supplied.")
        mask = ImageMask(self.mask_image, self.mask_threshold, self.mask_channel) if self.mask_image else None

        triangles = list(src.loop_triangles)
        if not triangles:
            raise ValueError("The input mesh has no triangulatable faces.")

        # Select triangles that actually intersect at least one active texel.
        # This detects tiny brush strokes even when their coverage is far below
        # 50% of a large source triangle. Interior samples are mask-filtered later.
        triangle_uvs = []
        selected_triangles = set()
        for ti, tri in enumerate(triangles):
            uv_tri = [uv_layer.data[li].uv.copy() for li in tri.loops] if mask else None
            triangle_uvs.append(uv_tri)
            selected = mask is None or mask.triangle_has_nonzero_texel(uv_tri)
            if selected:
                selected_triangles.add(ti)

        # Build a shared edge graph from the triangulated surface, including
        # virtual diagonals. Store each triangle's UV edge so only painted edges
        # are split in mask mode; an interior stroke must not force every outer
        # edge of a large polygon to subdivide.
        edge_to_triangles = {}
        edge_uv_by_triangle = {}
        for ti, tri in enumerate(triangles):
            vids = list(tri.vertices)
            loops = list(tri.loops)
            for side in range(3):
                a, b = vids[side], vids[(side + 1) % 3]
                key = (min(a, b), max(a, b))
                edge_to_triangles.setdefault(key, []).append(ti)
                if mask is not None:
                    edge_uv_by_triangle[(ti, key)] = (
                        uv_layer.data[loops[side]].uv.copy(),
                        uv_layer.data[loops[(side + 1) % 3]].uv.copy(),
                    )

        # In mask mode compute split positions only inside painted runs along
        # each UV edge. Shared mesh edges use the union of incident UV-side
        # positions, preserving connectivity even when the UVs are split.
        edge_parameters = {}
        required_vertices = len(src.vertices)
        for key, incident in edge_to_triangles.items():
            a, b = key
            length = (original_world[b] - original_world[a]).length
            if mask is None:
                segments = max(1, int(math.ceil(length / self.spacing_world)))
                params = [step / segments for step in range(1, segments)]
            else:
                param_set = set()
                for ti in incident:
                    uv_a, uv_b = edge_uv_by_triangle[(ti, key)]
                    tri_vids = list(triangles[ti].vertices)
                    side_direction = None
                    for side in range(3):
                        va, vb = tri_vids[side], tri_vids[(side + 1) % 3]
                        if (min(va, vb), max(va, vb)) == key:
                            side_direction = (va, vb)
                            break
                    local_params = mask.active_edge_parameters(uv_a, uv_b, length, self.spacing_world)
                    if side_direction is not None and side_direction[0] != a:
                        local_params = [1.0 - t for t in local_params]
                    param_set.update(t for t in local_params if 0.0 < t < 1.0)
                params = sorted(param_set)
            edge_parameters[key] = params
            required_vertices += len(params)

        # Loose original edges are split in full-mesh mode only. They do not
        # belong to a surface/UV region, so a mask cannot select them reliably.
        triangle_edge_keys = set(edge_to_triangles)
        loose_edge_keys = []
        for edge in src.edges:
            a, b = edge.vertices
            key = (min(a, b), max(a, b))
            if key not in triangle_edge_keys:
                loose_edge_keys.append(key)
                if mask is None:
                    length = (original_world[key[1]] - original_world[key[0]]).length
                    segs = max(1, int(math.ceil(length / self.spacing_world)))
                    edge_parameters[key] = [step / segs for step in range(1, segs)]
                    required_vertices += segs - 1
                else:
                    edge_parameters[key] = []

        if required_vertices > self.max_vertices:
            raise RuntimeError(
                f"Splitting surface edges requires at least {required_vertices:,} vertices, "
                f"exceeding the limit of {self.max_vertices:,}. Increase the limit or use a larger spacing."
            )

        # Allocate all shared edge-chain vertices once, in deterministic order.
        out_local = [co.copy() for co in original_local]
        edge_chains = {}
        for key, params in edge_parameters.items():
            a, b = key  # chain is always stored low vertex index -> high index
            chain = [a]
            for t in params:
                world_co = original_world[a].lerp(original_world[b], t)
                chain.append(len(out_local))
                out_local.append(inverse_world @ world_co)
            chain.append(b)
            edge_chains[key] = chain

        out_faces = []
        out_face_materials = []
        out_face_smooth = []
        # Whether each output face belongs to the active (subdivided) mask
        # region. This is face-local rather than vertex-local so a shared
        # boundary vertex can have different values on either side.
        out_face_mask_active = []
        out_corner_normals = []
        out_uvs = {layer.name: [] for layer in source_uv_layers}
        interior_budget = self.max_vertices - len(out_local)

        # To avoid point-cloud edges crossing the constrained boundary, every
        # triangle is triangulated independently with all boundary subsegments
        # supplied as constraints. Adjacent triangles share the exact same
        # boundary vertex IDs through edge_chains.
        for ti, tri in enumerate(triangles):
            vids = list(tri.vertices)
            loop_ids = list(tri.loops)
            p0, p1, p2 = [original_world[i] for i in vids]
            basis = triangle_basis(p0, p1, p2)
            if basis is None:
                continue
            project, unproject = basis
            tri_2d = [project(p0), project(p1), project(p2)]
            if cross2(*tri_2d) < 0:
                vids[1], vids[2] = vids[2], vids[1]
                loop_ids[1], loop_ids[2] = loop_ids[2], loop_ids[1]
                p0, p1, p2 = [original_world[i] for i in vids]
                basis = triangle_basis(p0, p1, p2)
                if basis is None:
                    continue
                project, unproject = basis
                tri_2d = [project(p0), project(p1), project(p2)]

            selected = ti in selected_triangles
            boundary_ids = []
            for side in range(3):
                va, vb = vids[side], vids[(side + 1) % 3]
                chain = edge_chains[(min(va, vb), max(va, vb))]
                if chain[0] != va:
                    chain = list(reversed(chain))
                # omit endpoint vb; it starts the next side's chain
                boundary_ids.extend(chain[:-1])

            # An inactive triangle with no split edge stays exactly as one
            # triangle. If a neighbour forced edge splits, retriangulate it to
            # maintain shared connectivity, but add no interior samples.
            has_split_boundary = any(
                bool(edge_parameters[(min(vids[i], vids[(i + 1) % 3]), max(vids[i], vids[(i + 1) % 3]))])
                for i in range(3)
            )
            if not selected and not has_split_boundary:
                out_faces.append(list(vids))
                out_face_mask_active.append(False)
                poly = src.polygons[tri.polygon_index]
                out_face_materials.append(poly.material_index)
                out_face_smooth.append(poly.use_smooth)
                for li in loop_ids:
                    out_corner_normals.append(src_corner_normals[li].copy())
                    for layer in source_uv_layers:
                        out_uvs[layer.name].append(layer.data[li].uv.copy())
                continue

            # Generate samples only at active UV positions. In mask mode this
            # means a small stroke in a huge polygon receives points without
            # filling the unpainted parts of that polygon with random vertices.
            samples_world = []
            if selected and interior_budget > 0:
                if mask is None:
                    samples_world = sample_triangle(p0, p1, p2, self.spacing_world, self.rng, interior_budget)
                else:
                    # Match UV corners to the possibly winding-corrected
                    # vertex/loop order used for p0, p1, p2 above.
                    uv_tri = [uv_layer.data[li].uv.copy() for li in loop_ids]
                    samples_world = sample_masked_triangle(
                        p0,
                        p1,
                        p2,
                        uv_tri[0],
                        uv_tri[1],
                        uv_tri[2],
                        self.spacing_world,
                        self.rng,
                        interior_budget,
                        mask,
                    )
                interior_budget -= len(samples_world)

            # CDT inputs are unique boundary vertices followed by interior points.
            input_global_ids = list(boundary_ids)
            points_2d = [project(matrix_world @ out_local[gid]) for gid in boundary_ids]
            for point in samples_world:
                gid = len(out_local)
                out_local.append(inverse_world @ point)
                input_global_ids.append(gid)
                points_2d.append(project(point))

            boundary_count = len(boundary_ids)
            if boundary_count < 3:
                continue
            constraints = [(i, (i + 1) % boundary_count) for i in range(boundary_count)]
            boundary_face = [tuple(range(boundary_count))]
            try:
                cdt_verts, _cdt_edges, cdt_faces, orig_verts, _orig_edges, _orig_faces = delaunay_2d_cdt(
                    [Vector((float(p[0]), float(p[1]))) for p in points_2d],
                    constraints,
                    boundary_face,
                    1,  # triangulate inside boundary
                    1e-10,
                    True,
                )
            except Exception as exc:
                raise RuntimeError(f"CDT failed for source triangle {tuple(tri.vertices)}: {exc}") from exc

            # Map CDT points back to the input vertices. If the CDT merged an
            # input point, choose the first provenance index; for this input,
            # distinct boundary/sample points should not normally be merged.
            cdt_to_global = {}
            for oi, provenance in enumerate(orig_verts):
                if not provenance:
                    # CDT may introduce a point only for intersections. There
                    # should be none for a triangle plus interior samples.
                    co2 = Vector(cdt_verts[oi])
                    nearest = min(range(len(points_2d)), key=lambda j: (co2 - Vector(points_2d[j])).length_squared)
                    if (co2 - Vector(points_2d[nearest])).length_squared > 1e-12:
                        raise RuntimeError(
                            "CDT introduced an unmapped vertex; refusing to create potentially non-manifold output."
                        )
                    provenance = [nearest]
                cdt_to_global[oi] = input_global_ids[provenance[0]]

            source_normals = [src_corner_normals[li].copy() for li in loop_ids]
            source_uv_triangles = {
                layer.name: [layer.data[li].uv.copy() for li in loop_ids] for layer in source_uv_layers
            }
            a2, b2, c2 = tri_2d
            denom = cross2(a2, b2, c2)
            poly = src.polygons[tri.polygon_index]

            for cdt_face_indices in cdt_faces:
                if len(cdt_face_indices) < 3:
                    continue
                # CDT normally returns triangles for this mode. If a polygon is
                # returned, fan-triangulate it around its first vertex.
                local_tris = []
                if len(cdt_face_indices) == 3:
                    local_tris.append(tuple(cdt_face_indices))
                else:
                    for k in range(1, len(cdt_face_indices) - 1):
                        local_tris.append((cdt_face_indices[0], cdt_face_indices[k], cdt_face_indices[k + 1]))

                for cdt_tri in local_tris:
                    face = [cdt_to_global[i] for i in cdt_tri]
                    if len(set(face)) != 3:
                        continue
                    q0, q1, q2 = [Vector(cdt_verts[i]) for i in cdt_tri]
                    area2 = cross2(q0, q1, q2)
                    if abs(area2) < 1e-12:
                        continue
                    # Match the source triangle's winding. This avoids flipped
                    # faces and helps ensure a consistent manifold surface.
                    if area2 * denom < 0:
                        face[1], face[2] = face[2], face[1]
                        cdt_tri = (cdt_tri[0], cdt_tri[2], cdt_tri[1])
                    out_faces.append(face)
                    out_face_materials.append(poly.material_index)
                    out_face_smooth.append(poly.use_smooth)
                    if mask is not None:
                        # Classify the FACE by its interior, not by its corner
                        # vertices. A boundary vertex can be shared by an
                        # active face and an inactive face, and corner-domain
                        # data must be allowed to differ on those two sides.
                        centroid_2d = (q0 + q1 + q2) / 3.0
                        centroid_weights = barycentric_weights_2d(centroid_2d, a2, b2, c2)
                        centroid_uv = (
                            source_uv_triangles[uv_layer.name][0] * centroid_weights[0]
                            + source_uv_triangles[uv_layer.name][1] * centroid_weights[1]
                            + source_uv_triangles[uv_layer.name][2] * centroid_weights[2]
                        )
                        out_face_mask_active.append(mask.value_at_uv(centroid_uv) > self.mask_threshold)
                    else:
                        out_face_mask_active.append(False)

                    for cdt_vi in cdt_tri:
                        q = Vector(cdt_verts[cdt_vi])
                        weights = barycentric_weights_2d(q, a2, b2, c2)
                        normal = (
                            source_normals[0] * weights[0]
                            + source_normals[1] * weights[1]
                            + source_normals[2] * weights[2]
                        )
                        if normal.length_squared > 1e-20:
                            normal.normalize()
                        else:
                            normal = source_normals[0].copy()
                        out_corner_normals.append(normal)
                        for name, uv_tri in source_uv_triangles.items():
                            out_uvs[name].append(
                                uv_tri[0] * weights[0] + uv_tri[1] * weights[1] + uv_tri[2] * weights[2]
                            )

        # Split loose edges in full-mesh mode and preserve them as edge chains.
        loose_edges = []
        for key in loose_edge_keys:
            chain = edge_chains[key]
            loose_edges.extend((chain[i], chain[i + 1]) for i in range(len(chain) - 1))

        # Final defensive checks: no duplicate-index faces and no duplicate faces.
        clean_faces = []
        clean_mats = []
        clean_smooth = []
        clean_face_mask_active = []
        clean_normals = []
        clean_uvs = {layer.name: [] for layer in source_uv_layers}
        seen_faces = set()
        loop_cursor = 0
        for fi, face in enumerate(out_faces):
            # All generated output faces should be triangles.
            if len(face) != 3 or len(set(face)) != 3:
                loop_cursor += len(face)
                continue
            canonical = tuple(sorted(face))
            if canonical in seen_faces:
                loop_cursor += len(face)
                continue
            seen_faces.add(canonical)
            clean_faces.append(face)
            clean_mats.append(out_face_materials[fi])
            clean_smooth.append(out_face_smooth[fi])
            clean_face_mask_active.append(out_face_mask_active[fi])
            clean_normals.extend(out_corner_normals[loop_cursor : loop_cursor + 3])
            for name in clean_uvs:
                clean_uvs[name].extend(out_uvs[name][loop_cursor : loop_cursor + 3])
            loop_cursor += len(face)

        if len(out_local) > self.max_vertices:
            raise RuntimeError(f"Vertex limit exceeded ({len(out_local):,} > {self.max_vertices:,}).")

        new_mesh = bpy.data.meshes.new(f"{src.name}_Densified")
        new_mesh.from_pydata(out_local, loose_edges, clean_faces)
        new_mesh.update(calc_edges=True)

        for i, poly in enumerate(new_mesh.polygons):
            if i < len(clean_mats):
                poly.material_index = clean_mats[i]
                poly.use_smooth = clean_smooth[i]
        for material in src.materials:
            new_mesh.materials.append(material)

        for src_uv in source_uv_layers:
            dst_uv = new_mesh.uv_layers.new(name=src_uv.name)
            values = clean_uvs[src_uv.name]
            if len(values) == len(dst_uv.data):
                for i, uv in enumerate(values):
                    dst_uv.data[i].uv = uv

        # Store mask values on the CORNER domain. Initialize every corner to
        # zero, then write sampled image values only for corners belonging to
        # faces classified as inside the subdivided region. This is important
        # at the boundary: the same mesh vertex may have a nonzero corner on
        # the active face and zero on the adjacent inactive face.
        if mask is not None and uv_layer is not None:
            mask_uvs = clean_uvs.get(uv_layer.name, [])
            if len(mask_uvs) == len(new_mesh.loops) and len(clean_face_mask_active) == len(new_mesh.polygons):
                attr = new_mesh.attributes.get(self.mask_attribute_name)
                if attr is not None:
                    raise ValueError(
                        f"Corner attribute name '{self.mask_attribute_name}' conflicts "
                        "with an existing output attribute (for example a UV map). "
                        "Choose a different name."
                    )
                attr = new_mesh.attributes.new(
                    name=self.mask_attribute_name,
                    type="FLOAT",
                    domain="CORNER",
                )
                # Explicit initialization documents and guarantees the outside
                # region remains zero regardless of image values at its edges.
                for item in attr.data:
                    item.value = 0.0
                loop_start = 0
                for poly_index, poly in enumerate(new_mesh.polygons):
                    if clean_face_mask_active[poly_index]:
                        for loop_index in range(loop_start, loop_start + poly.loop_total):
                            attr.data[loop_index].value = mask.value_at_uv(mask_uvs[loop_index])
                    loop_start += poly.loop_total

        if self.preserve_custom_normals and len(clean_normals) == len(new_mesh.loops):
            try:
                new_mesh.normals_split_custom_set(clean_normals)
            except Exception:
                pass

        # Copy polygon-relevant object settings via object.copy(); source data is untouched.
        new_obj = self.obj.copy()
        new_obj.data = new_mesh
        new_obj.name = f"{self.obj.name}_Densified"
        new_obj.matrix_world = matrix_world
        new_obj.animation_data_clear()
        for collection in self.obj.users_collection:
            collection.objects.link(new_obj)
        return new_obj


# -----------------------------------------------------------------------------
# Blender UI
# -----------------------------------------------------------------------------


class CDT_DENSIFIER_Props(bpy.types.PropertyGroup):
    spacing_cm: FloatProperty(
        name="Spacing (cm)",
        description="Target maximum segment length for original edges and target spacing for interior points",
        default=10.0,
        min=0.01,
        soft_max=100.0,
        precision=2,
    )
    max_vertices: IntProperty(
        name="Vertex Limit",
        description="Hard limit for total output vertices; operation aborts if edge splits alone exceed it",
        default=500_000,
        min=3,
        max=100_000_000,
    )
    seed: IntProperty(name="Random Seed", default=1, min=0, max=2147483647)
    mask_image: PointerProperty(
        name="Mask Image",
        description="Optional UV-space image mask. Interior points and edge splits are restricted to painted regions",
        type=bpy.types.Image,
    )
    mask_threshold: FloatProperty(
        name="Mask Threshold",
        description="A texel is active when its selected channel is greater than this value",
        default=0.0,
        min=0.0,
        max=1.0,
        precision=3,
    )
    mask_channel: EnumProperty(
        name="Mask Channel",
        items=[
            ("LUMINANCE", "Luminance", "Use weighted RGB luminance"),
            ("RED", "Red", "Use the red channel"),
            ("GREEN", "Green", "Use the green channel"),
            ("BLUE", "Blue", "Use the blue channel"),
            ("ALPHA", "Alpha", "Use the alpha channel"),
        ],
        default="LUMINANCE",
    )
    mask_attribute_name: StringProperty(
        name="Corner Attribute",
        description="Name of the FLOAT face-corner attribute that stores the sampled mask value",
        default="MaskValue",
    )
    preserve_custom_normals: BoolProperty(
        name="Preserve / Interpolate Normals",
        description="Attempt to transfer per-corner shading normals from the source triangles",
        default=True,
    )


class MESH_OT_cdt_densify_duplicate(bpy.types.Operator):
    bl_idname = "mesh.cdt_densify_duplicate"
    bl_label = "Create Densified Duplicate"
    bl_description = "Duplicate the active mesh, evenly split its original edges, and densify masked regions"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        obj = context.active_object
        props = context.scene.cdt_densifier_props
        try:
            densifier = CDTMeshDensifier(
                obj,
                spacing_cm=props.spacing_cm,
                max_vertices=props.max_vertices,
                seed=props.seed,
                mask_image=props.mask_image,
                mask_threshold=props.mask_threshold,
                mask_channel=props.mask_channel,
                mask_attribute_name=props.mask_attribute_name,
                preserve_custom_normals=props.preserve_custom_normals,
            )
            result = densifier.build()
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        bpy.ops.object.select_all(action="DESELECT")
        result.select_set(True)
        context.view_layer.objects.active = result
        self.report(
            {"INFO"},
            f"Created {result.name}: {len(result.data.vertices):,} vertices, {len(result.data.polygons):,} triangles",
        )
        return {"FINISHED"}


class VIEW3D_PT_cdt_densifier(bpy.types.Panel):
    bl_label = "CDT Densifier"
    bl_idname = "VIEW3D_PT_cdt_densifier"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def draw(self, context):
        layout = self.layout
        props = context.scene.cdt_densifier_props
        layout.prop(props, "spacing_cm")
        layout.prop(props, "max_vertices")
        layout.prop(props, "seed")
        layout.separator()
        layout.label(text="Optional UV Image Mask")
        layout.label(text="Only interior points inside painted mask regions are added")
        layout.label(text="UDIM tiles are supported when pixel buffers are readable")
        layout.prop(props, "mask_image")
        if props.mask_image:
            layout.prop(props, "mask_channel")
            layout.prop(props, "mask_threshold")
            layout.prop(props, "mask_attribute_name")
        layout.prop(props, "preserve_custom_normals")
        layout.operator("mesh.cdt_densify_duplicate", icon="MOD_TRIANGULATE")


classes = (
    CDT_DENSIFIER_Props,
    MESH_OT_cdt_densify_duplicate,
    VIEW3D_PT_cdt_densifier,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cdt_densifier_props = PointerProperty(type=CDT_DENSIFIER_Props)


def unregister():
    del bpy.types.Scene.cdt_densifier_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
