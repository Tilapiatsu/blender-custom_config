import bmesh
import bpy
from bpy.props import BoolVectorProperty, EnumProperty, FloatProperty, FloatVectorProperty, StringProperty
from bpy.types import Operator


# Blender Default Box Template (modified) - used by FitPrim et al.
def add_box(width, height, depth):
    verts = [(+1.0, +1.0, -1.0), (+1.0, -1.0, -1.0), (-1.0, -1.0, -1.0), (-1.0, +1.0, -1.0), (+1.0, +1.0, +1.0),
             (+1.0, -1.0, +1.0), (-1.0, -1.0, +1.0), (-1.0, +1.0, +1.0), ]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7), ]
    for i, v in enumerate(verts):
        verts[i] = v[0] * width, v[1] * depth, v[2] * height
    return verts, faces


class KePrimitiveBoxAdd(Operator):
    bl_idname = "mesh.ke_primitive_box_add"
    bl_label = "keBox"
    bl_description = "Creates a Box Primitive (from Blender Default Template)"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    width: FloatProperty(
        name="Width",
        description="Box Width",
        min=0.0001, max=10000.0,
        default=1.0,
    )
    height: FloatProperty(
        name="Height",
        description="Box Height",
        min=0.0001, max=10000.0,
        default=1.0,
    )
    depth: FloatProperty(
        name="Depth",
        description="Box Depth",
        min=0.0001, max=10000.0,
        default=1.0,
    )
    layers: BoolVectorProperty(
        name="Layers",
        description="Object Layers",
        size=20,
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    name: StringProperty(
        name="Name",
        description="Name",
        default="Box",
    )

    # generic transform props
    align_items = (
        ('WORLD', "World", "Align the new object to the world"),
        ('VIEW', "View", "Align the new object to the view"),
        ('CURSOR', "3D Cursor", "Use the 3D cursor orientation for the new object")
    )
    align: EnumProperty(
        name="Align",
        items=align_items,
        default='WORLD',
    )
    # update = AddObjectHelper.align_update_callback,
    location: FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
    )

    def execute(self, context):
        verts_loc, faces = add_box(self.width, self.height, self.depth)
        mesh = bpy.data.meshes.new(self.name)
        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()
        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])

        # Add Uv's (centered)
        uv_layer = bm.loops.layers.uv.verify()
        for face in bm.faces:
            for loop in face.loops:
                loop_uv = loop[uv_layer]
                loop_uv.uv[0] = loop.vert.co.x + 0.5
                loop_uv.uv[1] = loop.vert.co.y + 0.5

        for f in bm.faces:
            f.select = True

        bm.to_mesh(mesh)
        mesh.update()

        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)

        return {'FINISHED'}
