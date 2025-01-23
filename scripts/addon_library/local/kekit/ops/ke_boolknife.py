import bmesh
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from .._utils import mesh_select_all, dupe, shred


def remove_temp_cutter(bm, temp_cutter_verts):
    rem = set()
    for v in temp_cutter_verts:
        for f in bm.faces:
            if any(v for v in f.verts if v in temp_cutter_verts):
                for fv in f.verts:
                    rem.add(fv)
                continue
    for v in rem:
        bm.verts.remove(v)


class KeBoolKnife(Operator):
    bl_idname = "view3d.ke_boolknife"
    bl_label = "Bool Knife"
    bl_description = (
        "Simple Boolean Slice Operation:\n"
        "Object Mode: Cuts the ACTIVE object with other SELECTED object(s)\n"
        "Edit Mode: SELECTED mesh cuts UNSELECTED mesh (faces)\n"
        "='Face/Intersect (knife)' + object mode support & cutter handling (redo panel)"
    )
    bl_options = {'REGISTER', 'UNDO'}

    post_op: EnumProperty(
        items=[("HIDE", "Keep & Hide", "", 1),
               ("SELECTED", "Keep & Visible", "", 2),
               ("DELETE", "Delete", "", 3)],
        name="Cutter Handling",
        description="Pick how to handle the 'cutter' object(s) post-operation",
        default="SELECTED")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == "MESH")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        col.prop(self, "post_op", expand=True)
        col.separator(factor=0.5)

    def execute(self, context):
        objmode = True if context.mode == "OBJECT" else False
        if objmode and len(context.selected_objects) != 2:
            self.report({"INFO"}, "Need 2 objects selected!")
            return {"CANCELLED"}

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
            active = context.object
            bm = bmesh.from_edit_mesh(active.data)
            temp_cutter_verts = [v for v in bm.verts if v.select]

            bpy.ops.mesh.intersect(mode="SELECT_UNSELECT", separate_mode="CUT")

            # Remove temp-cutter
            remove_temp_cutter(bm, temp_cutter_verts)
            bmesh.update_edit_mesh(active.data)

            bpy.ops.object.editmode_toggle()
            context.space_data.overlay.show_wireframes = True
            if self.post_op == "SELECTED":
                for obj in og_cutters:
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                active.select_set(False)

            return {'FINISHED'}

        # EDIT MODE
        active = context.object
        bm = bmesh.from_edit_mesh(active.data)

        # if not objmode:  # should always be edit mode?!
        # Storing selecteds and og state refs
        og_sel = [f for f in bm.faces if f.select]
        if not og_sel:
            self.report({"INFO"}, "No face elements selected to use as cutter?")
            return {"CANCELLED"}

        og_sel_verts = [v for v in bm.verts if v.select]
        og_verts = set(bm.verts)

        # Create temp-cutter
        bpy.ops.mesh.duplicate()
        temp_cutter_verts = [v for v in bm.verts if v.select]

        # Hiding faces to avoid "cutting the cutter" is not enough:
        # --> just moving 'em out of the way - temporarliy ;)  (alt. TBD)
        temp_offset = 2
        for v in og_sel_verts:
            v.co.z -= temp_offset

        bpy.ops.mesh.intersect(mode="SELECT_UNSELECT", separate_mode="CUT")

        for v in og_sel_verts:
            v.co.z += temp_offset

        # Remove temp-cutter
        remove_temp_cutter(bm, temp_cutter_verts)

        # POST OP HANDLING (for editmode, obj mode already handled)
        if self.post_op == "DELETE":
            for f in og_sel:
                bm.faces.remove(f)
        elif self.post_op == "HIDE":
            for f in og_sel:
                f.hide_set(True)
        elif self.post_op == "SELECTED":
            for f in og_sel:
                f.select_set(True)

        bmesh.update_edit_mesh(active.data)

        return {'FINISHED'}
