import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from mathutils import Vector, Quaternion


class KeViewPos(Operator):
    bl_idname = "view3d.ke_viewpos"
    bl_label = "Get & Set Viewpos"
    bl_description = "Get & Set Viewpos"
    bl_options = {'REGISTER', 'UNDO'}

    mode : EnumProperty(
        items=[("GET", "Get Viewpos", "", "GET", 1),
               ("SET", "Set Viewpos", "", "SET", 2),
               ],
        name="Viewpos", options={"HIDDEN"},
        default="SET")

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "GET":
            return "Get Viewport placement values"
        else:
            return "Set Viewport placement values"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        rv3d = context.space_data.region_3d

        if self.mode == "GET":
            p = [int(rv3d.is_perspective)]
            d = [rv3d.view_distance]
            loc = [i for i in rv3d.view_location]
            rot = [i for i in rv3d.view_rotation]
            v = p + d + loc + rot
            v = str(v)
            context.scene.kekit_temp.view_query = v

        else:
            try:
                q = str(context.scene.kekit_temp.view_query)[1:-1]
                qs = q.split(",")
                v = [float(i) for i in qs]
            except Exception as e:
                print("\n", e, "\n Incorrect values. Aborting.")
                return {'CANCELLED'}

            if len(v) == 9:
                if not rv3d.is_perspective and bool(v[0]):
                    bpy.ops.view3d.view_persportho()
                rv3d.view_distance = v[1]
                rv3d.view_location = Vector(v[2:5])
                rv3d.view_rotation = Quaternion(v[5:9])

        return {'FINISHED'}
