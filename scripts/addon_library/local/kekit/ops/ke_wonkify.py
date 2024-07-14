import bpy
import random
from math import radians
from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator
from mathutils import Matrix, Vector
from .._utils import get_vertex_islands, is_tf_applied


class KeWonkify(Operator):
    bl_idname = "view3d.ke_wonkify"
    bl_label = "Wonkify"
    bl_description = ("OBJECT MODE: Applies minor random transform per VERT, PART or OBJECT - adding a SHAPE KEY\n"
                      "EDIT MODE: Uses Edges/Faces SELECTION Island(s) similar to 'Part' operation")
    bl_options = {'REGISTER', 'UNDO'}

    op: EnumProperty(
        items=[("OBJECT", "Per Object", "Random transform applied per Object as Shape Key", 1),
               ("PART", "Per Part", "Random transform applied per Part (per object) as Shape Key", 2),
               ("VERT", "Per Vert", "Random transform applied per Vert (per object) as Shape Key", 3)],
        name="Operation", default="PART")
    value: FloatProperty(name="Shape Key Value", default=1, min=0, max=10,
                         description="The Wonkify Shape Key Value (same as in Properties/Data panel)")
    override: FloatProperty(
        default=0, min=0, max=10, name="Override Wonk-factor",
        description="If not 0: Replaces the default automatic Wonk-factor (that's based on shortest edge %)")
    loc: BoolProperty(name="Translate", default=False)
    rot: BoolProperty(name="Rotate", default=True)
    scl: BoolProperty(name="Scale", default=False)
    replace_sk: BoolProperty(
        name="Replace Wonkify SK",
        default=True,
        description="ON: Overwrites Wonkify Shape Key (if already in use)\n"
                    "OFF: Will add more Wonkify Shape Keys"
    )
    delta_tf: BoolProperty(name="Use Delta TF", default=False,
                           description="Non-mesh Objects: Use Delta Transform instead of regular Tf")
    nonmesh_val: FloatProperty(
        default=0.25, min=0, max=10, name="Wonk Factor",
        description="Set Wonk-factor for non-mesh objects")

    ov = 0.0
    random_mtx = Matrix()
    non_mesh_mode = False
    em = False

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        if not self.non_mesh_mode:
            col = layout.column()
            col.prop(self, "op", expand=True)
            if self.em:
                col.enabled = False
            layout.prop(self, "value")
            layout.prop(self, "override")
            layout.prop(self, "replace_sk")
        else:
            layout.label(text="Non-Mesh Mode:")
            layout.prop(self, "nonmesh_val")
            layout.prop(self, "delta_tf")
        row = layout.row()
        row.prop(self, "loc", text="Move", toggle=True)
        row.prop(self, "rot", text="Rotate", toggle=True)
        row.prop(self, "scl", text="Scale", toggle=True)
        layout.separator(factor=1)

    def calc_random_mtx(self):
        self.random_mtx = Matrix()
        x = random.uniform(-self.ov, self.ov)
        y = random.uniform(-self.ov, self.ov)
        z = random.uniform(-self.ov, self.ov)
        if self.loc:
            self.random_mtx @= Matrix.Translation((x * 0.1, y * 0.1, z * 0.1))
        if self.rot:
            m_rotx = Matrix.Rotation(radians(x), 4, 'X')
            m_roty = Matrix.Rotation(radians(y), 4, 'Y')
            m_rotz = Matrix.Rotation(radians(z), 4, 'Z')
            self.random_mtx = self.random_mtx @ m_rotx @ m_roty @ m_rotz
        if self.scl:
            m_sclx = Matrix.Scale(1 + (x / 1 * 0.01), 4, Vector((1, 0, 0)))
            m_scly = Matrix.Scale(1 + (y / 1 * 0.01), 4, Vector((0, 1, 0)))
            m_sclz = Matrix.Scale(1 + (z / 1 * 0.01), 4, Vector((0, 0, 1)))
            self.random_mtx = self.random_mtx @ m_sclx @ m_scly @ m_sclz

    def execute(self, context):
        sel_obj = context.selected_objects
        if not sel_obj and context.object:
            sel_obj = [context.object]

        self.non_mesh_mode = True if any(bool(o.type != "MESH") for o in sel_obj) else False
        if self.non_mesh_mode:
            # Directly affect object transform - No Shape Keys, (Loc/Scl is hacky)
            self.ov = self.nonmesh_val
            for o in sel_obj:
                self.calc_random_mtx()
                if self.delta_tf:
                    loc, rot, scl = self.random_mtx.decompose()
                    o.delta_location = loc
                    o.delta_rotation_euler = rot.to_euler()
                    if self.scl:
                        o.delta_scale = scl
                else:
                    loc, rot, scl = self.random_mtx.decompose()
                    o.location += loc
                    rot.rotate(o.rotation_euler)
                    o.rotation_euler = rot.to_euler("XYZ", o.rotation_euler)
                    if self.scl:
                        o.scale = scl

            return {"FINISHED"}

        # ELSE, SHAPE KEY MESH MODE
        for o in sel_obj:
            # Check Edit Mode
            self.em = False
            if o.mode != "OBJECT":
                o.update_from_editmode()
                self.em = True
            # Always process in Objmode
            bpy.ops.object.mode_set(mode="OBJECT")
            if self.scl:
                # Non-normalized scale auto-apply
                if not is_tf_applied(o)[2]:
                    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)

            basis = None
            wonk = None

            if not o.data.shape_keys:
                basis = o.shape_key_add(name="Basis", from_mix=False)
                wonk = o.shape_key_add(name="Wonkify", from_mix=False)
            else:
                for s in o.data.shape_keys.key_blocks:
                    if s.name == "Basis":
                        basis = s
                    elif s.name == "Wonkify" and self.replace_sk:
                        o.shape_key_remove(s)
                if basis:
                    wonk = o.shape_key_add(name="Wonkify", from_mix=False)
                    # bpy.ops.object.shape_key_add(from_mix=False)

            if basis is None or wonk is None:
                print("Invalid Basis SK: Could not set-up 'Basis' shape")
                return {"CANCELLED"}

            # Set active SK
            idx = o.data.shape_keys.key_blocks.find('Wonkify')
            if idx != -1:
                o.active_shape_key_index = idx

            verts = o.data.vertices
            edges = o.data.edges

            if self.em:
                o.use_shape_key_edit_mode = True
                self.op = "PART"

            wonk.interpolation = "KEY_LINEAR"
            wonk.relative_key = basis
            wonk.slider_max = 10
            wonk.value = self.value
            wonk.name = "Wonkify"

            # USE SMALLEST EDGE AS LIMITER (TO AVOID CRAZY ROTATIONS)
            elens = []
            for e in edges:
                v1 = verts[e.vertices[0]]
                v2 = verts[e.vertices[1]]
                elens.append((v1.co - v2.co).length)
            elens.sort()
            # TF Offset Value
            self.ov = elens[0]
            if self.override != 0:
                self.ov = self.override

            if self.op == "PART":
                # MESH ISLANDS MODE
                if self.em:
                    sel_verts = [v for v in verts if v.select]
                    sel_edges = [v for v in edges if v.select]
                    islands = get_vertex_islands(sel_verts, sel_edges, is_bm=False)
                else:
                    islands = get_vertex_islands(verts, edges, is_bm=False)
                for island in islands:
                    self.calc_random_mtx()
                    for v in island:
                        wonk.data[v.index].co = self.random_mtx @ v.co

            elif self.op == "VERT":
                # EVERY VERT MODE
                for (vert, sk) in zip(verts, wonk.data):
                    self.calc_random_mtx()
                    sk.co = self.random_mtx @ vert.co

            else:
                # ENTIRE MESH OBJECT MODE
                self.calc_random_mtx()
                for (vert, sk) in zip(verts, wonk.data):
                    sk.co = self.random_mtx @ vert.co

            if self.em:
                bpy.ops.object.editmode_toggle()

        return {"FINISHED"}
