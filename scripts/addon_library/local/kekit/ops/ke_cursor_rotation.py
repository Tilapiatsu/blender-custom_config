from math import radians

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from mathutils import Vector, Matrix
from .._utils import rotation_from_vector


class KeCursorRotation(Operator):
    bl_idname = "view3d.ke_cursor_rotation"
    bl_label = "Cursor Rotation"
    bl_options = {'REGISTER'}

    mode: EnumProperty(items=[
        ("STEP", "Step Rotate", "", 1),
        ("VIEW", "Align To View", "", 2),
        ("OBJECT", "Point To Object", "", 3),
        ("MATCH", "Match Object Rot", "", 4)],
        name="Mode", default="STEP", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "STEP":
            return "Rotate the cursor along chosen AXIS with either PRESET -or- CUSTOM degrees"
        elif properties.mode == "VIEW":
            return "Aligns the cursor Z axis to the view camera"
        elif properties.mode == "OBJECT":
            return "Rotate the cursor Z towards chosen object"
        else:
            return "Cursor uses chosen object's rotation"

    def execute(self, context):
        obj = bpy.data.objects.get(context.scene.kekit_cursor_obj)
        if not obj:
            obj = context.object
        cursor = context.scene.cursor
        qc = context.scene.cursor.matrix

        if self.mode == "VIEW":
            rv3d = context.space_data.region_3d
            cursor.rotation_euler = rv3d.view_rotation.to_euler()

        elif self.mode == "OBJECT":
            if obj:
                v = Vector(obj.location - cursor.location).normalized()
                if round(abs(v.dot(Vector((1, 0, 0)))), 3) == 1:
                    u = Vector((0, 0, 1))
                else:
                    u = Vector((-1, 0, 0))
                t = v.cross(u).normalized()
                rot_mtx = rotation_from_vector(v, t, rw=False)
                cursor.rotation_euler = rot_mtx.to_euler()
            else:
                self.report({"INFO"}, "No Object Selected")

        elif self.mode == "MATCH":
            if obj:
                cursor.rotation_euler = obj.rotation_euler
            else:
                self.report({"INFO"}, "No Object Selected")

        elif self.mode == "STEP":
            axis = context.scene.kekit_temp.kcm_axis
            custom_rot = context.scene.kekit_temp.kcm_custom_rot
            preset_rot = context.scene.kekit_temp.kcm_rot_preset
            if custom_rot != 0:
                rval = custom_rot
            else:
                rval = radians(int(preset_rot))
            rot_mtx = qc @ Matrix.Rotation(rval, 4, axis)
            cursor.rotation_euler = rot_mtx.to_euler()

        return {"FINISHED"}
