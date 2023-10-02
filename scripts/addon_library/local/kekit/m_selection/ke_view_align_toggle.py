import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from mathutils import Vector, Quaternion


class KeViewAlignToggle(Operator):
    bl_idname = "view3d.ke_view_align_toggle"
    bl_label = "View Align Selected Toggle"
    bl_options = {'REGISTER'}

    mode: EnumProperty(
        items=[("SELECTION", "", "", 1),
               ("CURSOR", "", "", 2)],
        name="View Align Mode",
        default="SELECTION",
        options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "SELECTION":
            return "Align View to Active Face OR 3 Vertices OR 2 Edges (or, in Object-mode: Obj's Z axis)\n" \
                   "Toggle (run again) to restore view from before alignment"
        else:
            return "Align View to Cursor Z-Axis Orientation\n" \
                   "Toggle (run again) to restore view from before alignment"

    def execute(self, context):
        rv3d = context.space_data.region_3d
        v = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        slot = context.scene.kekit_temp.viewtoggle
        # SET
        if sum(slot) == 0:
            p = [int(rv3d.is_perspective)]
            d = [rv3d.view_distance]
            loc = [i for i in rv3d.view_location]
            rot = [i for i in rv3d.view_rotation]
            v = p + d + loc + rot
            slot[0] = v[0]
            slot[1] = v[1]
            slot[2] = v[2]
            slot[3] = v[3]
            slot[4] = v[4]
            slot[5] = v[5]
            slot[6] = v[6]
            slot[7] = v[7]
            slot[8] = v[8]

            if self.mode == "SELECTION":
                if context.object.mode == "EDIT":
                    bpy.ops.view3d.ke_view_align()
                else:
                    bpy.ops.view3d.view_axis(type='TOP', align_active=True)
                bpy.ops.view3d.view_selected(use_all_regions=False)

            elif self.mode == "CURSOR":
                q = context.scene.cursor.rotation_euler.to_quaternion()
                rv3d.view_rotation = q
                bpy.ops.view3d.view_center_cursor()

            if rv3d.is_perspective:
                bpy.ops.view3d.view_persportho()
        else:
            v[0] = slot[0]
            v[1] = slot[1]
            v[2] = slot[2]
            v[3] = slot[3]
            v[4] = slot[4]
            v[5] = slot[5]
            v[6] = slot[6]
            v[7] = slot[7]
            v[8] = slot[8]

            if not rv3d.is_perspective and bool(v[0]):
                bpy.ops.view3d.view_persportho()
            rv3d.view_distance = v[1]
            rv3d.view_location = Vector(v[2:5])
            rv3d.view_rotation = Quaternion(v[5:9])

            slot[0] = 0
            slot[1] = 0
            slot[2] = 0
            slot[3] = 0
            slot[4] = 0
            slot[5] = 0
            slot[6] = 0
            slot[7] = 0
            slot[8] = 0

        return {"FINISHED"}
