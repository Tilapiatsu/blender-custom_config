import bmesh
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator
from .._utils import average_vector


class KeSelectFlippedNormal(Operator):
    bl_idname = "mesh.ke_select_flipped_normal"
    bl_label = "Select Flipped Normal Faces"
    bl_description = "Selects flipped normal faces (the 'red' faces in 'face orientation' overlay)"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        items=[("CONNECTED", "Connected", "", 1),
               ("AVERAGE", "Average", "", 2)
               ],
        name="Method", default="CONNECTED",
        description="Choose which method used to find flipped faces.\n"
                    "Average works better for (mostly flat) disconnected mesh islands.\n"
                    "Connected works best in most other cases.")
    invert : BoolProperty(name="Invert Selection", default=False)

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "mode", expand=True)
        layout.separator(factor=0.5)
        layout.prop(self, "invert", toggle=True)
        layout.separator(factor=0.5)

    def execute(self, context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        if self.mode == "AVERAGE":
            avg_normal = average_vector([f.normal for f in bm.faces])
            if self.invert:
                for f in bm.faces:
                    if avg_normal.dot(f.normal) > 0:
                        f.select_set(True)
            else:
                for f in bm.faces:
                    if avg_normal.dot(f.normal) < 0:
                        f.select_set(True)
        else:
            cbm = bm.copy()
            bmesh.ops.recalc_face_normals(cbm, faces=cbm.faces)
            if self.invert:
                for f, of in zip(cbm.faces, bm.faces):
                    if f.normal == of.normal:
                        of.select_set(True)
            else:
                for f, of in zip(cbm.faces, bm.faces):
                    if f.normal != of.normal:
                        of.select_set(True)
            cbm.free()
        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}
