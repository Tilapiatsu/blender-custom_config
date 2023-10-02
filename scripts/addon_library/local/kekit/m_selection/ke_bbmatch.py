import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator


class KeBBMatch(Operator):
    bl_idname = "object.ke_bbmatch"
    bl_label = "Match Active Bounding Box"
    bl_description = "Scales selected object(s) to last selected object bounding box (along axis chosen in redo)\n" \
                     "Make sure origin(s) is properly placed beforehand\nScale will be auto-applied"
    bl_options = {'REGISTER', 'UNDO'}

    mode : EnumProperty(
        items=[("UNIT", "Longest Axis (Unit)", "", 1),
               ("ALL", "All Axis", "", 2),
               ("X", "X Only", "", 3),
               ("Y", "Y Only", "", 4),
               ("Z", "Z Only", "", 5),
               ],
        name="Scaling", default="UNIT",
        description="Choose which Bounding Box Axis to scale with")

    match_loc : BoolProperty(name="Location", default=False)
    match_rot : BoolProperty(name="Rotation", default=False)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "mode", expand=True)
        layout.separator(factor=0.5)
        row = layout.row()
        row.prop(self, "match_loc", toggle=True)
        row.prop(self, "match_rot", toggle=True)
        layout.separator(factor=0.5)

    def execute(self, context):
        sel_objects = [o for o in context.selected_objects]

        if not len(sel_objects) >= 2:
            self.report({"INFO"}, "Invalid Selection (2+ required)")
            return {"CANCELLED"}

        src_obj = context.object
        src_bb = src_obj.dimensions

        if self.mode == "UNIT":
            v = sorted(src_bb)[-1]
            src_bb = [v, v, v]
        elif self.mode == "X":
            v = src_bb[0]
            src_bb = [v, 1, 1]
        elif self.mode == "Y":
            v = src_bb[1]
            src_bb = [1, v, 1]
        elif self.mode == "Z":
            v = src_bb[2]
            src_bb = [1, 1, v]

        target_objects = [o for o in sel_objects if o != src_obj]

        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False, )

        for o in target_objects:

            bb = o.dimensions
            if self.mode == "UNIT":
                v = sorted(bb)[-1]
                bb = [v, v, v]
            elif self.mode == "X":
                v = bb[0]
                bb = [v, 1, 1]
            elif self.mode == "Y":
                v = bb[1]
                bb = [1, v, 1]
            elif self.mode == "Z":
                v = bb[2]
                bb = [1, 1, v]

            o.scale[0] *= (src_bb[0] / bb[0])
            o.scale[1] *= (src_bb[1] / bb[1])
            o.scale[2] *= (src_bb[2] / bb[2])

            if self.match_loc:
                o.location = src_obj.location
            if self.match_rot:
                o.rotation_euler = src_obj.rotation_euler

        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)

        return {"FINISHED"}
