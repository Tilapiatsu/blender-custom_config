bl_info = {
    "name": "CDT Mesh Densifier",
    "author": "OpenAI",
    "version": (0, 4, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Item > CDT Densifier",
    "description": "Duplicate a mesh and densify selected triangles while preserving shared boundaries",
    "category": "Mesh",
}

import bpy
import math
import random
from array import array
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    PointerProperty,
    EnumProperty,
)


# -----------------------------------------------------------------------------
# 2D geometry helpers
# -----------------------------------------------------------------------------

def cross2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def point_in_triangle_2d(p, a, b, c, eps=1e-10):
    c1 = cross2(a, b, p)
    c2 = cross2(b, c, p)
    c3 = cross2(c, a, p)
    return (c1 >= -eps and c2 >= -eps and c3 >= -eps) or (
        c1 <= eps and c2 <= eps and c3 <= eps
    )


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
    if channel == 'RED':
        return r
    if channel == 'GREEN':
        return g
    if channel == 'BLUE':
        return b
    if channel == 'ALPHA':
        return a
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


class ImageMask:
    """Cached UV-space image mask, sampled from Blender's image datablock."""

    def __init__(self, image, threshold=0.0, channel='LUMINANCE'):
        if image is None:
            raise ValueError("No mask image was supplied.")
        if image.source == 'TILED':
            raise ValueError("UDIM/tiled mask images are not supported by this prototype yet.")
        self.image = image
        self.width, self.height = image.size[:]
        if self.width < 1 or self.height < 1:
            raise ValueError(f"Mask image '{image.name}' has no pixel data.")
        self.threshold = threshold
        self.channel = channel
        self.pixels = array('f', [0.0]) * (self.width * self.height * 4)
        image.pixels.foreach_get(self.pixels)

    def value_at_uv(self, uv):
        """Read the nearest texel at UV coordinates. UVs outside 0..1 are inactive."""
        u, v = float(uv.x), float(uv.y)
        if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
            return 0.0
        x = min(self.width - 1, max(0, int(math.floor(u * self.width))))
        y = min(self.height - 1, max(0, int(math.floor(v * self.height))))
        idx = (y * self.width + x) * 4
        return _mask_pixel_value(self.pixels[idx:idx + 4], self.channel)

    def uv_is_active(self, uv):
        return self.value_at_uv(uv) > self.threshold

    def triangle_has_nonzero_texel(self, uv_triangle):
        tri = [(float(uv.x), float(uv.y)) for uv in uv_triangle]
        min_u = max(0.0, min(p[0] for p in tri))
        max_u = min(1.0, max(p[0] for p in tri))
        min_v = max(0.0, min(p[1] for p in tri))
        max_v = min(1.0, max(p[1] for p in tri))
        if min_u > max_u or min_v > max_v:
            return False

        x0 = max(0, min(self.width - 1, int(math.floor(min_u * self.width))))
        x1 = max(0, min(self.width - 1, int(math.floor(max_u * self.width))))
        y0 = max(0, min(self.height - 1, int(math.floor(min_v * self.height))))
        y1 = max(0, min(self.height - 1, int(math.floor(max_v * self.height))))

        for y in range(y0, y1 + 1):
            py0, py1 = y / self.height, (y + 1) / self.height
            for x in range(x0, x1 + 1):
                px0, px1 = x / self.width, (x + 1) / self.width
                if not triangle_intersects_rect(tri, px0, py0, px1, py1):
                    continue
                idx = (y * self.width + x) * 4
                rgba = self.pixels[idx:idx + 4]
                if _mask_pixel_value(rgba, self.channel) > self.threshold:
                    return True
        return False


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


# -----------------------------------------------------------------------------
# Main densifier
# -----------------------------------------------------------------------------

class CDTMeshDensifier:
    """Create a triangulated duplicate while keeping original vertices fixed.

    Original edges belonging to selected triangles are divided into equal-length
    segments. Edges shared with unselected triangles are split as needed to avoid
    cracks. Interior sampling is limited to selected triangles. A triangle is
    selected when it intersects at least one active mask texel. This is a
    triangle-level mask approximation, not exact clipping to individual texels.
    """

    def __init__(
        self,
        obj,
        spacing_cm=10.0,
        max_vertices=500_000,
        seed=1,
        mask_image=None,
        mask_threshold=0.0,
        mask_channel='LUMINANCE',
        preserve_custom_normals=True,
    ):
        if obj is None or obj.type != 'MESH':
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

        # Select triangles in UV space. Use texel/triangle intersection rather
        # than centroid sampling so small active mask regions are not missed.
        selected_triangles = set()
        for ti, tri in enumerate(triangles):
            selected = True
            if mask is not None:
                uv_tri = [uv_layer.data[li].uv.copy() for li in tri.loops]
                selected = mask.triangle_has_nonzero_texel(uv_tri)
            if selected:
                selected_triangles.add(ti)

        # Build a shared edge graph from the *triangulated surface*, not just
        # Mesh.edges. This includes virtual diagonals introduced when an ngon
        # or quad is represented by loop_triangles. A key is an unordered pair
        # of original vertex indices, so adjacent triangles reuse the same chain.
        edge_to_triangles = {}
        for ti, tri in enumerate(triangles):
            vids = list(tri.vertices)
            for side in range(3):
                a, b = vids[side], vids[(side + 1) % 3]
                key = (min(a, b), max(a, b))
                edge_to_triangles.setdefault(key, []).append(ti)

        # An edge is split if any incident triangle is selected. This also
        # splits the shared side on the inactive neighbour to avoid cracks.
        edge_segments = {}
        required_vertices = len(src.vertices)
        for key, incident in edge_to_triangles.items():
            should_split = any(ti in selected_triangles for ti in incident)
            if should_split:
                a, b = key
                length = (original_world[b] - original_world[a]).length
                segments = max(1, int(math.ceil(length / self.spacing_world)))
            else:
                segments = 1
            edge_segments[key] = segments
            required_vertices += segments - 1

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
                    edge_segments[key] = segs
                    required_vertices += segs - 1
                else:
                    edge_segments[key] = 1

        if required_vertices > self.max_vertices:
            raise RuntimeError(
                f"Splitting surface edges requires at least {required_vertices:,} vertices, "
                f"exceeding the limit of {self.max_vertices:,}. Increase the limit or use a larger spacing."
            )

        # Allocate all shared edge-chain vertices once, in deterministic order.
        out_local = [co.copy() for co in original_local]
        edge_chains = {}
        for key, segments in edge_segments.items():
            a, b = key  # chain is always stored low vertex index -> high index
            chain = [a]
            for step in range(1, segments):
                t = step / segments
                world_co = original_world[a].lerp(original_world[b], t)
                chain.append(len(out_local))
                out_local.append(inverse_world @ world_co)
            chain.append(b)
            edge_chains[key] = chain

        out_faces = []
        out_face_materials = []
        out_face_smooth = []
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
                edge_segments[(min(vids[i], vids[(i + 1) % 3]), max(vids[i], vids[(i + 1) % 3]))] > 1
                for i in range(3)
            )
            if not selected and not has_split_boundary:
                out_faces.append(list(vids))
                poly = src.polygons[tri.polygon_index]
                out_face_materials.append(poly.material_index)
                out_face_smooth.append(poly.use_smooth)
                for li in loop_ids:
                    out_corner_normals.append(src_corner_normals[li].copy())
                    for layer in source_uv_layers:
                        out_uvs[layer.name].append(layer.data[li].uv.copy())
                continue

            # Interior sampling is only done for selected triangles. The sampler
            # is bounded by the remaining vertex budget.
            samples_world = []
            if selected and interior_budget > 0:
                samples_world = sample_triangle(
                    p0, p1, p2, self.spacing_world, self.rng, interior_budget
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
                    1,       # triangulate inside boundary
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
                        raise RuntimeError("CDT introduced an unmapped vertex; refusing to create potentially non-manifold output.")
                    provenance = [nearest]
                cdt_to_global[oi] = input_global_ids[provenance[0]]

            source_normals = [src_corner_normals[li].copy() for li in loop_ids]
            source_uv_triangles = {
                layer.name: [layer.data[li].uv.copy() for li in loop_ids]
                for layer in source_uv_layers
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

                    for cdt_vi in cdt_tri:
                        q = Vector(cdt_verts[cdt_vi])
                        weights = barycentric_weights_2d(q, a2, b2, c2)
                        normal = source_normals[0] * weights[0] + source_normals[1] * weights[1] + source_normals[2] * weights[2]
                        if normal.length_squared > 1e-20:
                            normal.normalize()
                        else:
                            normal = source_normals[0].copy()
                        out_corner_normals.append(normal)
                        for name, uv_tri in source_uv_triangles.items():
                            out_uvs[name].append(uv_tri[0] * weights[0] + uv_tri[1] * weights[1] + uv_tri[2] * weights[2])

        # Split loose edges in full-mesh mode and preserve them as edge chains.
        loose_edges = []
        for key in loose_edge_keys:
            chain = edge_chains[key]
            loose_edges.extend((chain[i], chain[i + 1]) for i in range(len(chain) - 1))

        # Final defensive checks: no duplicate-index faces and no duplicate faces.
        clean_faces = []
        clean_mats = []
        clean_smooth = []
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
            clean_normals.extend(out_corner_normals[loop_cursor:loop_cursor + 3])
            for name in clean_uvs:
                clean_uvs[name].extend(out_uvs[name][loop_cursor:loop_cursor + 3])
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
        description="Optional UV-space image mask. Only selected triangles are densified; shared boundary edges may split",
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
            ('LUMINANCE', "Luminance", "Use weighted RGB luminance"),
            ('RED', "Red", "Use the red channel"),
            ('GREEN', "Green", "Use the green channel"),
            ('BLUE', "Blue", "Use the blue channel"),
            ('ALPHA', "Alpha", "Use the alpha channel"),
        ],
        default='LUMINANCE',
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
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

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
                preserve_custom_normals=props.preserve_custom_normals,
            )
            result = densifier.build()
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        result.select_set(True)
        context.view_layer.objects.active = result
        self.report({ 'INFO' }, f"Created {result.name}: {len(result.data.vertices):,} vertices, {len(result.data.polygons):,} triangles")
        return {'FINISHED'}


class VIEW3D_PT_cdt_densifier(bpy.types.Panel):
    bl_label = "CDT Densifier"
    bl_idname = "VIEW3D_PT_cdt_densifier"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        props = context.scene.cdt_densifier_props
        layout.prop(props, "spacing_cm")
        layout.prop(props, "max_vertices")
        layout.prop(props, "seed")
        layout.separator()
        layout.label(text="Optional UV Image Mask")
        layout.label(text="Mask selects triangles touching active texels")
        layout.prop(props, "mask_image")
        if props.mask_image:
            layout.prop(props, "mask_channel")
            layout.prop(props, "mask_threshold")
        layout.prop(props, "preserve_custom_normals")
        layout.operator("mesh.cdt_densify_duplicate", icon='MOD_TRIANGULATE')


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
