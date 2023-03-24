import bpy
import bmesh
from bpy.props import BoolProperty, FloatProperty
from ._utils import get_distance


class KeExEx(bpy.types.Operator):
    bl_idname = "mesh.ke_exex"
    bl_label = "Extract & Extrude"
    bl_description = "Extract & Extrude\nExtract, Offset and Extrude with adjustable values in the redo-panel"
    bl_options = {'REGISTER', 'UNDO'}

    depth_override: FloatProperty(
        name="Override Depth",
        default=0.0,
        min=0.0,
        description="Override depth - instead of edge length - if not zero",
    )
    offset_override: FloatProperty(
        name="Override Offset",
        default=0.0,
        min=0.0,
        description="Override offset distance from source mesh - instead of edge length - if not zero",
    )
    open: BoolProperty(name="Open Borders", description="Does not cap the 'bottom' faces", default=False)
    use_long: BoolProperty(name="Longest Edge", description="Uses shortest edge by default", default=False)
    select: BoolProperty(name="Select Result", description="Selects new geo", default=True)
    separate: BoolProperty(name="Make New Object", description="Dupe & separate geo to a new Object", default=False)

    @classmethod
    def poll(cls, context):
        return context.object is not None and \
            context.mode != "OBJECT" and \
            context.object.type == "MESH"

    def execute(self, context):
        if self.separate:
            bpy.ops.mesh.ke_extract_and_edit(dupe=True, objmode=False, expand=False, itemize=False)

        obj = context.object
        od = obj.data
        bm = bmesh.from_edit_mesh(od)
        epsilon = 0.0000001
        use_offset_override = False
        og_sep_faces = []

        sel_faces = [f for f in bm.faces if f.select]
        if not sel_faces:
            self.report({"INFO"}, "Select faces")
            return {"CANCELLED"}

        if self.separate:
            og_sep_faces = sel_faces.copy()

        # Offset Calc
        vps = [get_distance(e.verts[0].co, e.verts[1].co) for e in bm.edges if e.select]
        vps.sort()
        if self.use_long:
            d = vps[-1]
        else:
            d = vps[0]

        if self.depth_override > epsilon:
            d = self.depth_override

        if self.offset_override > epsilon:
            use_offset_override = True

        # Macro time!
        if use_offset_override:
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.inset(thickness=0, depth=self.offset_override, use_outset=False)
            nf = [f for f in bm.faces if f.select]
            bpy.ops.mesh.select_more()
            for f in nf:
                f.select_set(False)
            bpy.ops.mesh.delete(type='FACE')
            for f in nf:
                f.select_set(True)

        if self.open:
            if use_offset_override:
                bpy.ops.mesh.inset(thickness=0, depth=d, use_outset=False)
            else:
                bpy.ops.mesh.duplicate()
                bpy.ops.mesh.inset(thickness=0, depth=d, use_outset=False)
            bpy.ops.mesh.select_more()
            new_verts = [v for v in bm.verts if v.select]
        else:
            if not use_offset_override:
                bpy.ops.mesh.duplicate()
            bpy.ops.mesh.flip_normals()
            verts1 = [v for v in bm.verts if v.select]
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.flip_normals()
            bpy.ops.mesh.inset(thickness=0, depth=d, use_outset=False)
            bpy.ops.mesh.select_more()
            verts2 = [v for v in bm.verts if v.select]
            new_verts = list(set(verts1 + verts2))

        bmesh.ops.remove_doubles(bm, verts=new_verts, dist=0.00001)

        if self.separate and og_sep_faces:
            bmesh.ops.delete(bm, geom=og_sep_faces, context="FACES")

        if self.select:
            bpy.ops.mesh.select_linked(delimit=set())
        else:
            bpy.ops.mesh.select_all(action='DESELECT')

        bmesh.update_edit_mesh(od)

        return {'FINISHED'}


#
# CLASS REGISTRATION
#
def register():
    bpy.utils.register_class(KeExEx)


def unregister():
    bpy.utils.unregister_class(KeExEx)
