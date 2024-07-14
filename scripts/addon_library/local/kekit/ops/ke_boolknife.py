import bmesh
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from .._utils import mesh_select_all, dupe, shred


class KeBoolKnife(Operator):
    bl_idname = "view3d.ke_boolknife"
    bl_label = "Bool Knife"
    bl_description = "Object Mode: Cuts the ACTIVE object with other SELECTED object(s)\n"\
                     "Edit Mode: Selected mesh cuts unselected mesh (faces)\n"\
                     "='Face/Intersect (knife)' + object mode support & cutter handling (redo panel)"
    bl_options = {'REGISTER', 'UNDO'}

    post_op: EnumProperty(
        items=[("HIDE", "Keep & Hide", "", 1),
               ("VISIBLE", "Keep & Visible", "", 2),
               ("DELETE", "Delete", "", 3)],
        name="Obj.Mode Cutter",
        description="Pick how to handle the 'cutter' object(s) post-operation",
        default="VISIBLE")

    post_op_edit: EnumProperty(
        items=[("HIDE", "Keep & Hide", "", 1),
               ("SELECTED", "Keep & Select", "", 2),
               ("DELETE", "Delete", "", 3)],
        name="Edit M. Cutter",
        description="Pick how to handle the 'cutter' mesh post-operation",
        default="SELECTED")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == "MESH")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        # row = col.row()
        col.prop(self, "post_op", expand=True)
        col.separator(factor=0.5)
        col.prop(self, "post_op_edit", expand=True)
        layout.separator(factor=1)

    def execute(self, context):
        objmode = True if context.mode == "OBJECT" else False
        # SETUP
        if objmode:
            active = context.active_object
            if not active:
                self.report({"INFO"}, "No objects selected to use as cutter?")
                return {"CANCELLED"}

            mesh_select_all(active, False)
            og_cutters = [o for o in context.selected_objects if o != active]

            for obj in og_cutters:
                cutter = dupe(obj)
                obj.select_set(False)
                if self.post_op == "HIDE":
                    obj.hide_set(True)
                elif self.post_op == "DELETE":
                    shred(obj)
                cutter.select_set(True)
                mesh_select_all(cutter, True)

            bpy.ops.object.join()
            context.view_layer.objects.active = active
            bpy.ops.object.editmode_toggle()
        else:
            active = context.object

        # CUT UNSELECTED MESH
        bm = bmesh.from_edit_mesh(active.data)
        og_sel, og_verts = [], []
        if not objmode:
            og_sel = [f for f in bm.faces if f.select]
            if not og_sel:
                self.report({"INFO"}, "No elements selected to use as cutter?")
                return {"CANCELLED"}
            og_verts = [v for v in bm.verts if v.select]
            bpy.ops.mesh.duplicate()
            # Hiding the faces to avoid "cutting the cutter" is not enough
            # --> just moving 'em out of the way - probably ;)  (alt. extract/merge, meh)
            for v in og_verts:
                v.co.z -= 100000

        sel = [f for f in bm.faces if f.select]
        # return {"FINISHED"}
        bpy.ops.mesh.intersect(mode="SELECT_UNSELECT", separate_mode="CUT")

        # SELECT REMAINING CONNECTED TENP-CUTTER MESH
        remains = [i for i in sel if i.is_valid]
        if not remains:
            self.report({"ERROR"}, "Mesh Intersect Failed")
            return {"CANCELLED"}

        # DELETE TENP-CUTTER MESH
        for f in remains:
            f.select_set(True)
        bpy.ops.mesh.select_linked(delimit=set())
        new_sel = [f for f in bm.faces if f.select]
        if og_sel:
            bmesh.ops.delete(bm, geom=new_sel, context="FACES")
            for f in og_sel:
                f.select_set(True)
            for v in og_verts:
                v.co.z += 100000

        # PROCESS CUTTER MESH
        if objmode or self.post_op_edit == "DELETE":
            bmesh.ops.delete(bm, geom=new_sel, context="FACES")
        elif not objmode and self.post_op_edit == "HIDE":
            for f in new_sel:
                f.select_set(False)
                f.hide_set(True)

        bmesh.update_edit_mesh(active.data)

        if objmode:
            bpy.ops.object.editmode_toggle()
            context.space_data.overlay.show_wireframes = True

        return {"FINISHED"}
