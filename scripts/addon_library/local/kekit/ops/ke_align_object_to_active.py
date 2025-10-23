from bpy.props import EnumProperty
from bpy.types import Operator


class KeAlignObjectToActive(Operator):
    bl_idname = "view3d.ke_align_object_to_active"
    bl_label = "Align Object(s) to Active"
    bl_description = "Copy ACTIVE Object's Location, Rotation or Scale (or all) to all other SELECTED objects"
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    op: EnumProperty(
        items=[("LOC", "Location", "Copy ACTIVE Object's Location to all other SELECTED objects)", 1),
               ("ROT", "Rotation", "Copy ACTIVE Object's Rotation to all other SELECTED objects))", 2),
               ("SCL", "Scale", "Copy ACTIVE Object's Scale to all other SELECTED objects)", 3),
               ("ALL", "All", "Copy ACTIVE Object's Transforms to all other SELECTED objects)", 4)
               ],
        name="Align", default="ROT")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        column = layout.column()
        column.prop(self, "op", expand=True)

    @classmethod
    def poll(cls, context):
        return context.mode != "EDIT_MESH"

    def execute(self, context):
        sel = context.selected_objects
        active = context.active_object
        if not sel or not active:
            self.report({"WARNING"}, "Op Cancelled: Invalid Selection.")
            return {"CANCELLED"}

        if self.op == "LOC":
            for o in sel:
                o.location = active.location
        elif self.op == "ROT":
            for o in sel:
                o.rotation_euler = active.rotation_euler
        elif self.op == "SCL":
            for o in sel:
                o.scale = active.scale
        elif self.op == "ALL":
            for o in sel:
                o.location = active.location
                o.rotation_euler = active.rotation_euler
                o.scale = active.scale

        return {"FINISHED"}
