from math import degrees, radians
from bpy.props import FloatProperty
from bpy.types import Operator


class KeStraighten(Operator):
    bl_idname = "object.ke_straighten"
    bl_label = "Straighten"
    bl_description = "Snaps selected object(s) rotation to nearest set degree"
    bl_options = {'REGISTER', 'UNDO'}

    deg: FloatProperty(
        description="Degree Snap",
        default=90,
        min=0,
        max=90
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        for o in context.selected_objects:
            r = [radians((round(degrees(i) / self.deg) * self.deg)) for i in o.rotation_euler]
            o.rotation_euler[0] = r[0]
            o.rotation_euler[1] = r[1]
            o.rotation_euler[2] = r[2]

        return {"FINISHED"}
