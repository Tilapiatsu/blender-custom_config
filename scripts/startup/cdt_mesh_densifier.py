bl_info = {
    "name": "CDT Mesh Densifier",
    "author": "OpenAI",
    "version": (0, 2, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Item > CDT Densifier",
    "description": "Duplicate a mesh, evenly split original edges, and densify selected surface regions",
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
    """Cached image mask. A UV triangle is selected if it intersects any nonzero texel."""

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

    Every original edge is divided into equal-length segments based on the
    requested spacing. Interior sampling is limited to triangles selected by an
    optional UV image mask. A triangle is selected when it intersects at least
    one nonzero mask texel.
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

        # Blender stores shading normals per loop/corner, allowing hard edges to
        # retain distinct normals on their two sides.
        try:
            src_corner_normals = [loop.normal.copy() for loop in src.loops]
        except Exception:
            src_corner_normals = [Vector((0, 0, 1)) for _ in src.loops]

        uv_layer = src.uv_layers.active if self.mask_image else None
        if self.mask_image and uv_layer is None:
            raise ValueError("A UV map is required when a mask image is supplied.")
        mask = ImageMask(self.mask_image, self.mask_threshold, self.mask_channel) if self.mask_image else None

        # Preflight the required edge vertices before allocating the output.
        edge_segments = {}
        required_vertices = len(src.vertices)
        for edge in src.edges:
            a, b = edge.vertices
            length = (original_world[b] - original_world[a]).length
            segments = max(1, int(math.ceil(length / self.spacing_world)))
            edge_segments[edge.index] = segments
            required_vertices += segments - 1
        if required_vertices > self.max_vertices:
            raise RuntimeError(
                f"Evenly splitting original edges requires at least {required_vertices:,} vertices, "
                f"exceeding the limit of {self.max_vertices:,}. Increase the limit or use a larger spacing."
            )

        # Original vertices retain their original indices and local coordinates.
        out_local = [co.copy() for co in original_local]
        edge_vertex_ids = {}
        for edge in src.edges:
            a, b = edge.vertices
            segments = edge_segments[edge.index]
            ids = [a]
            for step in range(1, segments):
                t = step / segments
                world_co = original_world[a].lerp(original_world[b], t)
                local_co = inverse_world @ world_co
                ids.append(len(out_local))
                out_local.append(local_co)
            ids.append(b)
            edge_vertex_ids[edge.index] = ids

        # Map undirected endpoint pair to original edge index.
        edge_lookup = {}
        for edge in src.edges:
            a, b = edge.vertices
            edge_lookup[(min(a, b), max(a, b))] = edge.index

        out_faces = []
        out_face_materials = []
        out_face_smooth = []
        out_corner_normals = []
        out_uvs = {layer.name: [] for layer in src.uv_layers}
        source_uv_layers = list(src.uv_layers)
        interior_budget = self.max_vertices - len(out_local)

        for tri in src.loop_triangles:
            v_ids = list(tri.vertices)
            loop_ids = list(tri.loops)
            p0, p1, p2 = [original_world[i] for i in v_ids]
            basis = triangle_basis(p0, p1, p2)
            if basis is None:
                continue
            project, unproject = basis

            tri_2d = [project(p0), project(p1), project(p2)]
            if cross2(*tri_2d) < 0:
                v_ids[1], v_ids[2] = v_ids[2], v_ids[1]
                loop_ids[1], loop_ids[2] = loop_ids[2], loop_ids[1]
                p0, p1, p2 = [original_world[i] for i in v_ids]
                project, unproject = triangle_basis(p0, p1, p2)
                tri_2d = [project(p0), project(p1), project(p2)]

            # Select this triangle by UV mask. A triangle is selected if any
            # nonzero image texel intersects its UV triangle, not merely its centroid.
            selected = True
            tri_uvs = None
            if mask:
                tri_uvs = [uv_layer.data[i].uv.copy() for i in loop_ids]
                selected = mask.triangle_has_nonzero_texel(tri_uvs)

            # Build ordered boundary chain: original corners plus evenly spaced
            # samples along each of the triangle's three original mesh edges.
            boundary_global_ids = []
            for side in range(3):
                va = v_ids[side]
                vb = v_ids[(side + 1) % 3]
                edge_key = (min(va, vb), max(va, vb))
                edge_index = edge_lookup.get(edge_key)
                if edge_index is None:
                    # Defensive fallback for malformed/non-manifold input.
                    boundary_global_ids.append(va)
                    continue
                chain = edge_vertex_ids[edge_index]
                if chain[0] == va:
                    ordered_chain = chain[:-1]
                else:
                    ordered_chain = list(reversed(chain))[ :-1]
                boundary_global_ids.extend(ordered_chain)

            # Unique boundary ids in perimeter order.
            compact_boundary = []
            for idx in boundary_global_ids:
                if not compact_boundary or compact_boundary[-1] != idx:
                    compact_boundary.append(idx)
            if len(compact_boundary) > 1 and compact_boundary[0] == compact_boundary[-1]:
                compact_boundary.pop()
            if len(compact_boundary) < 3:
                continue

            # Add interior points only to triangles intersecting nonzero mask texels.
            samples_world = []
            if selected and interior_budget > 0:
                # Reserve some budget for later triangles by bounding each triangle's
                # requested sample count to the remaining global budget.
                samples_world = sample_triangle(
                    p0, p1, p2, self.spacing_world, self.rng, interior_budget
                )
                interior_budget -= len(samples_world)

            # CDT input consists of boundary vertices first, then interior samples.
            cdt_input_global_ids = list(compact_boundary)
            cdt_points_2d = []
            for global_id in compact_boundary:
                cdt_points_2d.append(project(matrix_world @ out_local[global_id]))
            for point in samples_world:
                global_id = len(out_local)
                out_local.append(inverse_world @ point)
                cdt_input_global_ids.append(global_id)
                cdt_points_2d.append(project(point))

            # Constraints preserve every segment along the original triangle boundary.
            boundary_count = len(compact_boundary)
            cdt_edges = [(i, (i + 1) % boundary_count) for i in range(boundary_count)]
            cdt_face = [tuple(range(boundary_count))]
            try:
                cdt_verts, _cdt_edges, cdt_faces, orig_verts, _orig_edges, _orig_faces = (
                    delaunay_2d_cdt(
                        [Vector((p[0], p[1])) for p in cdt_points_2d],
                        cdt_edges,
                        cdt_face,
                        1,       # triangulate inside the constrained boundary
                        1e-9,
                        True,
                    )
                )
            except Exception as exc:
                raise RuntimeError(
                    f"Constrained triangulation failed for source triangle {tuple(tri.vertices)}: {exc}"
                ) from exc

            # The input vertices are all retained in this setup. Use CDT's
            # original-vertex map instead of matching positions by floating point.
            output_to_global = {}
            for out_i in range(len(cdt_verts)):
                source_indices = orig_verts[out_i] if out_i < len(orig_verts) else []
                if not source_indices:
                    raise RuntimeError("CDT returned a vertex without an input-vertex mapping.")
                output_to_global[out_i] = cdt_input_global_ids[source_indices[0]]

            # Per-loop source normals and UVs follow the source triangle's corner order.
            source_normals = [src_corner_normals[i].copy() for i in loop_ids]
            source_uv_triangles = {
                layer.name: [layer.data[i].uv.copy() for i in loop_ids]
                for layer in source_uv_layers
            }
            a2, b2, c2 = tri_2d
            material_index = src.polygons[tri.polygon_index].material_index
            smooth = src.polygons[tri.polygon_index].use_smooth

            for cdt_face_indices in cdt_faces:
                if len(cdt_face_indices) != 3:
                    continue
                face = [output_to_global[i] for i in cdt_face_indices]
                if len(set(face)) != 3:
                    continue
                q0, q1, q2 = [Vector(cdt_verts[i]) for i in cdt_face_indices]
                if abs(cross2(q0, q1, q2)) < 1e-12:
                    continue
                out_faces.append(face)
                out_face_materials.append(material_index)
                out_face_smooth.append(smooth)

                for cdt_vertex_index in cdt_face_indices:
                    q = Vector(cdt_verts[cdt_vertex_index])
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

                    for layer_name, uv_tri in source_uv_triangles.items():
                        uv = uv_tri[0] * weights[0] + uv_tri[1] * weights[1] + uv_tri[2] * weights[2]
                        out_uvs[layer_name].append(uv)

        # Include loose edges not represented by faces, retaining original endpoints.
        face_edge_keys = set()
        for face in out_faces:
            for i, a in enumerate(face):
                b = face[(i + 1) % len(face)]
                face_edge_keys.add((min(a, b), max(a, b)))
        loose_edges = []
        for edge in src.edges:
            a, b = edge.vertices
            key = (min(a, b), max(a, b))
            if key not in face_edge_keys:
                loose_edges.extend((edge_vertex_ids[edge.index][i], edge_vertex_ids[edge.index][i + 1])
                                    for i in range(len(edge_vertex_ids[edge.index]) - 1))

        new_mesh = bpy.data.meshes.new(f"{src.name}_Densified")
        new_mesh.from_pydata(out_local, loose_edges, out_faces)
        new_mesh.update()

        for i, poly in enumerate(new_mesh.polygons):
            if i < len(out_face_materials):
                poly.material_index = out_face_materials[i]
                poly.use_smooth = out_face_smooth[i]
        for material in src.materials:
            new_mesh.materials.append(material)

        # UV coordinates are transferred per output loop, preserving seams.
        for src_uv in source_uv_layers:
            dst_uv = new_mesh.uv_layers.new(name=src_uv.name)
            values = out_uvs[src_uv.name]
            if len(values) == len(dst_uv.data):
                for i, uv in enumerate(values):
                    dst_uv.data[i].uv = uv

        if self.preserve_custom_normals and len(out_corner_normals) == len(new_mesh.loops):
            try:
                new_mesh.normals_split_custom_set(out_corner_normals)
            except Exception:
                # Some Blender builds/mesh states may reject custom-normal writes.
                pass

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
        description="Optional UV-space image mask. Triangles touching nonzero texels are densified",
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
