from bpy.props import EnumProperty
from bpy.types import Operator


class KeAlignObjectToActive(Operator):
    bl_idname = "view3d.ke_align_object_to_active"
    bl_label = "Align Object(s) To Active"
    bl_description = "Align selected object(s) to the Active Objects Transforms. (You may want to apply scale)"
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    align: EnumProperty(
        items=[("LOCATION", "Location", "", 1),
               ("ROTATION", "Rotation", "", 2),
               ("BOTH", "Location & Rotation", "", 3)],
        name="Align", default="BOTH")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        column = layout.column()
        column.prop(self, "align", expand=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode != "EDIT_MESH"

    def execute(self, context):
        target_obj = None
        sel_obj = [o for o in context.selected_objects]
        if context.active_object:
            target_obj = context.active_object
        if target_obj is None and sel_obj:
            target_obj = sel_obj[-1]
        if not target_obj or len(sel_obj) < 2:
            print("Insufficent selection: Need at least 2 objects.")
            return {'CANCELLED'}

        sel_obj = [o for o in sel_obj if o != target_obj]

        for o in sel_obj:

            if self.align == "LOCATION":
                o.matrix_world.translation = target_obj.matrix_world.translation
            elif self.align == "ROTATION":
                og_pos = o.matrix_world.translation.copy()
                o.matrix_world = target_obj.matrix_world
                o.matrix_world.translation = og_pos
            elif self.align == "BOTH":
                o.matrix_world = target_obj.matrix_world

        target_obj.select_set(False)
        context.view_layer.objects.active = sel_obj[0]

        return {"FINISHED"}
