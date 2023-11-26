import bpy
import bmesh
from mathutils import Vector
from bpy.types import Operator
from bpy.props import FloatProperty
from .._utils import get_prefs


def fit_to_grid(co, grid):
    x, y, z = round(co[0] / grid) * grid, round(co[1] / grid) * grid, round(co[2] / grid) * grid
    return round(x, 5), round(y, 5), round(z, 5)


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
        description="Nearest Grid value in internal BU(Metric)"
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        k = get_prefs()
        if not self.set_grid:
            grid_setting = k.fit2grid
        else:
            grid_setting = self.set_grid

        obj = context.object

        if obj.type == 'MESH' and obj.data.is_editmode:
            od = obj.data
            bm = bmesh.from_edit_mesh(od)
            obj_mtx = obj.matrix_world.copy()

            verts = [v for v in bm.verts if v.select]

            if verts:
                vert_cos = [obj_mtx @ v.co for v in verts]
                modified = []

                for v, co in zip(verts, vert_cos):
                    new_coords = fit_to_grid(co, grid_setting)
                    old_coords = tuple([round(i, 5) for i in co])

                    if new_coords != old_coords:
                        new_coords = new_coords
                        v.co = obj_mtx.inverted() @ Vector(new_coords)
                        modified.append(v)

                bpy.ops.mesh.select_all(action='DESELECT')

                if modified:
                    for v in modified:
                        v.select = True

                bmesh.update_edit_mesh(od)
                # bm.free()
                bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.mode_set(mode='EDIT')

                if modified:
                    bpy.ops.mesh.select_mode(type="VERT")
                    self.report({"INFO"}, "Fit2Grid: %i vert(s) not on grid" % len(modified))
                else:
                    self.report({"INFO"}, "Fit2Grid: On grid - All good!")

            else:
                self.report({"INFO"}, "Fit2Grid: Nothing Selected?")

        elif context.mode == "OBJECT":
            new_loc = fit_to_grid(obj.location, grid_setting)
            obj.location = new_loc

        else:
            self.report({"INFO"}, "Fit2Grid: Invalid object type or mode - Aborted")

        return {'FINISHED'}
