import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
from mathutils import Matrix, Vector


def bbox_side(coords, mtx):
    x = [co[0] for co in coords]
    x.sort()
    y = [co[1] for co in coords]
    y.sort()
    z = [co[2] for co in coords]
    z.sort()
    return mtx @ Vector((x[0], y[0], z[0])), mtx @ Vector((x[-1], y[-1], z[-1]))


class KeVPFlip(Operator):
    bl_idname = "view3d.ke_vp_flip"
    bl_label = "VP Flip"
    bl_description = (
        "Link-Duplicate (option) & Rotate Object around -180° and place facing the original (slighly offset)\n"
        "Using Axis to closest Global axis to View port camera angle.\n"
        "(Similar to Mouse Mirror, but no scaling, just loc & rot)")
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    dupe: BoolProperty(name="Duplicate", default=True)
    link: BoolProperty(name="Linked", default=True)
    mouse_pos = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.space_data.type == "VIEW_3D" and context.mode == "OBJECT"

    def execute(self, context):
        obj = context.object
        new_pos = Vector(obj.location)

        rm = context.space_data.region_3d.view_matrix
        ot = "GLOBAL"
        tm = Matrix().to_3x3()

        v = tm.inverted() @ Vector(rm[2]).to_3d()
        x, y, z = abs(v[0]), abs(v[1]), abs(v[2])

        if x > y and x > z:
            axis = True, False, False
            oa = "X"
        elif y > x and y > z:
            axis = False, True, False
            oa = "Y"
        else:
            axis = False, False, True
            oa = "Z"

        bbcoords = []
        for b in obj.bound_box:
            bbcoords.append(b[:])

        bbmin, bbmax = bbox_side(bbcoords, obj.matrix_world)

        offset = Vector([0, 0, 0])
        axis_mask = [not i for i in axis]

        for a, i in enumerate(axis_mask):
            if a:
                offset[i] = (bbmax[i] - bbmin[i]) * -1
        new_pos -= offset

        if self.dupe:
            bpy.ops.object.duplicate(linked=self.link)
            new_obj = context.object
        else:
            new_obj = obj

        bpy.ops.transform.rotate(value=-3.14159, orient_axis=oa, orient_type=ot,
                                 orient_matrix=tm, orient_matrix_type=ot,
                                 constraint_axis=axis, mirror=False, use_proportional_edit=False,
                                 use_proportional_connected=False, use_proportional_projected=False, snap=False)

        new_obj.location = new_pos
        # Clean up rot
        r = new_obj.rotation_euler.to_quaternion().to_euler()
        new_obj.rotation_euler.x = round(r.x, 4)
        new_obj.rotation_euler.y = round(r.y, 4)
        new_obj.rotation_euler.z = round(r.z, 4)
        # Clean up loc
        new_obj.location.x = round(new_obj.location.x, 4)
        new_obj.location.y = round(new_obj.location.y, 4)
        new_obj.location.z = round(new_obj.location.z, 4)

        return {"FINISHED"}
