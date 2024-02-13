import bpy
import bmesh
from mathutils import Vector
from bpy.types import Operator
from bpy.props import FloatProperty
from .._utils import get_prefs, is_tf_applied


def fit_to_grid(co, grid, rn):
    x, y, z = round(co[0] / grid) * grid, round(co[1] / grid) * grid, round(co[2] / grid) * grid
    return round(x, rn), round(y, rn), round(z, rn)


class KeFit2Grid(Operator):
    bl_idname = "view3d.ke_fit2grid"
    bl_label = "Fit2Grid"
    bl_description = "Quantization\n" \
                     "EDIT MODE: Snaps each vert in selected VERTS/EDGES/FACES to nearest set world grid value\n" \
                     "OBJECT MODE: Snaps Object Location to nearest Grid value"
    bl_options = {'REGISTER', 'UNDO'}

    set_grid: FloatProperty(
        name="Grid Value",
        min=0,
        description="Nearest Grid value in internal Blender Units / meters"
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        k = get_prefs()
        # Rounding nr / decimal steps - not forgetting to round the user fp value!
        rn = str(round(self.set_grid, 6))[::-1].find('.')

        if not self.set_grid:
            grid_setting = k.fit2grid
        else:
            grid_setting = self.set_grid

        obj = context.object

        if obj.type == 'MESH' and obj.data.is_editmode:
            print("Fit2Grid: %s" % obj.name)
            off_grid = []
            fp_rounding = 0
            tf_check = all(i for i in is_tf_applied(obj)[1:])

            od = obj.data
            bm = bmesh.from_edit_mesh(od)
            obj_mtx = obj.matrix_world.copy()

            verts = [v for v in bm.verts if v.select]

            if verts:
                vert_cos = [obj_mtx @ v.co for v in verts]
                for v, co in zip(verts, vert_cos):

                    old = tuple([round(i, 4) for i in co])
                    new = fit_to_grid(co, grid_setting, rn)

                    nv = obj_mtx.inverted() @ Vector(new)
                    nco = Vector((round(nv[0], rn), round(nv[1], rn), round(nv[2], rn)))
                    v.co = nco

                    if old == new:
                        fp_rounding += 1
                    else:
                        off_grid.append(v)

                bpy.ops.mesh.select_all(action='DESELECT')

                if off_grid:
                    for v in off_grid:
                        v.select = True

                bmesh.update_edit_mesh(od)
                # bm.free()
                bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.mode_set(mode='EDIT')

                tf_msg = ""
                if not tf_check:
                    tf_msg = "Rot/Scl NOT APPLIED"
                    print("Edit-Mode Note: Rotation or Scale not applied - "
                          "Results may be more inaccurate than micrometers!")

                if off_grid:
                    bpy.ops.mesh.select_mode(type="VERT")
                    self.report(
                        {"INFO"},
                        "Snapped %i vert(s) to grid. %s" % (len(off_grid), tf_msg)
                    )
                elif fp_rounding:
                    self.report(
                        {"INFO"},
                        "%i vert(s) on grid, FP-Rounding only. %s" % (fp_rounding, tf_msg)
                    )
                else:
                    # Will probably never be reached:
                    self.report({"INFO"}, "On grid - All good!")

            else:
                self.report({"INFO"}, "Nothing Selected?")

        elif context.mode == "OBJECT":
            print("Fit2Grid:")
            tf_not_applied = 0
            off_grid = []
            fp_rounded = []

            sel = list(context.selected_objects)
            if not sel:
                sel = [context.object]

            bpy.ops.object.select_all(action="DESELECT")

            for obj in sel:
                fp_rounding = False

                tf_check = is_tf_applied(obj)[2]
                tf_not_applied += int(not tf_check)

                old = tuple([round(i, 4) for i in obj.location])
                new = fit_to_grid(obj.location, grid_setting, rn)
                obj.location = new

                if old == new:
                    fp_rounding = True
                    fp_rounded.append(obj)
                else:
                    off_grid.append(obj)

                tf_msg = ""
                if not tf_check:
                    tf_msg = "Scale NOT APPLIED"

                if off_grid:
                    print("%s NOT on grid. %s" % (obj.name, tf_msg))

                elif fp_rounding:
                    print("%s ON grid, FP-Rounding only. %s" % (obj.name, tf_msg))

            if off_grid:
                for obj in off_grid:
                    obj.select_set(True)

            tf_txt = ""
            if tf_not_applied:
                tf_txt = "Scale NOT applied: %i" % tf_not_applied

            if off_grid:
                self.report({"INFO"}, "Snapped %i object(s) to grid. %s" % (len(off_grid), tf_txt))

            elif fp_rounded:
                self.report(
                    {"INFO"}, "%i object(s) on grid, FP-Rounding only. %s" % (len(fp_rounded), tf_txt))
            else:
                # Will probably never be reached:
                self.report({"INFO"}, "On grid - All good!")

        else:
            self.report({"INFO"}, "Invalid object type or mode - Aborted")

        return {'FINISHED'}
