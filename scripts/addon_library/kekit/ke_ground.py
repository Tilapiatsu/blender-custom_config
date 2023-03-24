import bpy
from bpy_types import Operator
from ._utils import point_axis_raycast


def zmove(value, zonly=True):
    if zonly:
        values = (0, 0, value)
    else:
        values = value
    bpy.ops.transform.translate(value=values, orient_type='GLOBAL',
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                proportional_size=1, use_proportional_connected=False,
                                use_proportional_projected=False, release_confirm=True)


class KeGround(Operator):
    bl_idname = "view3d.ke_ground"
    bl_label = "Ground (or Center)"
    bl_description = "Ground (or Center) selected Object(s), or selected elements (snap to world Z0 only)"
    bl_options = {'REGISTER', 'UNDO'}

    op: bpy.props.EnumProperty(
        items=[("GROUND", "Ground to Z0", "", 1),
               ("CENTER", "Ground & Center on Z", "", 2),
               ("CENTER_ALL", "Center XYZ", "", 3),
               ("CENTER_GROUND", "Center XY & Ground Z", "", 4),
               ("UNDER", "(Under)Ground to Z0", "", 5),
               ("CUSTOM", "Ground to custom Z", "", 6),
               ("CUSTOM_CENTER", "Center to custom Z", "", 7)],
        name="Operation",
        default="GROUND")

    custom_z: bpy.props.FloatProperty(
        name="Custom Z Value", description="Set custom value on Z axis", default=0)

    group: bpy.props.BoolProperty(
        name="Group", description="Treat all selected objects as one item", default=False)

    raycast: bpy.props.BoolProperty(
        name="Raycast", description="Stops on obstructions on the way down (Nothing: Z0)", default=True)

    ignore_selected: bpy.props.BoolProperty(
        name="Ignore Selected", description="Ignore selected Objects when raycasting", default=False)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects]
        if not sel_obj:
            self.report({"INFO"}, "Ground: Selection Error?")
            return {'CANCELLED'}

        offset = 0
        if context.object.type == "MESH":
            editmode = bool(context.object.data.is_editmode)
        else:
            editmode = False

        group_vc = [(0, 0, 0)]
        group_zs = [0.0]
        if self.group:
            low_z = []
            for o in sel_obj:
                if o.type == 'MESH':
                    low_z.extend([o.matrix_world @ v.co for v in o.data.vertices])
                else:
                    low_z.append(o.location)
            group_vc = sorted(low_z, key=lambda z: z[2])
            group_zs = [p[2] for p in group_vc]

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action="DESELECT")

        if self.ignore_selected:
            for o in sel_obj:
                o.hide_set(True)

        for o in sel_obj:
            if self.ignore_selected:
                o.hide_set(False)

            o.select_set(True)
            context.view_layer.objects.active = o

            if o.type == 'MESH':
                if self.group:
                    vc = [group_vc[0], group_vc[-1]]
                    zs = [group_zs[0], group_zs[-1]]
                else:
                    if editmode:
                        vc = [o.matrix_world @ v.co for v in o.data.vertices if v.select]
                    else:
                        vc = [o.matrix_world @ v.co for v in o.data.vertices]
                    vz = []
                    for co in vc:
                        vz.append(co[2])
                    zs = sorted(vz)
            else:
                vc = [o.location, o.location]
                zs = [vc[0][2], vc[1][2]]

            if self.raycast and vc:
                if self.group:
                    coords = [vc[0]]
                    point = vc[0]
                else:
                    coords = sorted(vc, key=lambda z: z[2])
                    point = coords[0]

                point[2] -= 0.0001  # hack so it doesn't trace itself...
                raycast = point_axis_raycast(context, vec_point=point, axis=2)
                if raycast[1] is not None:
                    hit = raycast[1]
                    hit[2] -= 0.0001  # meh
                    dist = coords[0][2] - hit[2]
                    zs[-1] = dist + (zs[-1] - zs[0])
                    zs[0] = dist

                    if zs[0] == 0:
                        print("Ground: Raycast error. Aborting.")
                        for ob in sel_obj:
                            ob.select_set(True)
                        if self.ignore_selected:
                            for obj in sel_obj:
                                obj.hide_set(False)
                        return {"CANCELLED"}

            if editmode:
                bpy.ops.object.mode_set(mode='EDIT')

            if vc:
                if self.group:
                    vc = group_vc
                    zs = group_zs

                if self.op == "GROUND":
                    offset = round(zs[0], 6) * -1

                elif self.op == "CENTER":
                    offset = round(zs[0] + ((zs[-1] - zs[0]) / 2), 6) * -1

                elif self.op == "CENTER_ALL":
                    zx = sorted([c[0] for c in vc])
                    zy = sorted([c[1] for c in vc])
                    xo = round(zx[0] + ((zx[-1] - zx[0]) / 2), 6) * -1
                    yo = round(zy[0] + ((zy[-1] - zy[0]) / 2), 6) * -1
                    zo = round(zs[0] + ((zs[-1] - zs[0]) / 2), 6) * -1
                    zmove((xo, yo, zo), zonly=False)

                elif self.op == "CENTER_GROUND":
                    zx = sorted([c[0] for c in vc])
                    zy = sorted([c[1] for c in vc])
                    xo = round(zx[0] + ((zx[-1] - zx[0]) / 2), 6) * -1
                    yo = round(zy[0] + ((zy[-1] - zy[0]) / 2), 6) * -1
                    zo = round(zs[0], 6) * -1
                    zmove((xo, yo, zo), zonly=False)

                elif self.op == "UNDER":
                    offset = round(zs[-1], 6) * -1

                elif self.op == "CUSTOM":
                    offset = (round(zs[0], 6) - self.custom_z) * -1

                elif self.op == "CUSTOM_CENTER":
                    offset = (round(zs[0] + ((zs[-1] - zs[0]) / 2), 6) - self.custom_z) * -1

                if offset and self.op != "CENTER_ALL":
                    zmove(offset)

            bpy.ops.object.mode_set(mode='OBJECT')
            o.select_set(False)
            if self.ignore_selected:
                o.hide_set(True)

        if self.ignore_selected:
            for o in sel_obj:
                o.hide_set(False)

        for ob in sel_obj:
            ob.select_set(True)

        if editmode:
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


#
# CLASS REGISTRATION
#
classes = (KeGround,)

modules = ()


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
