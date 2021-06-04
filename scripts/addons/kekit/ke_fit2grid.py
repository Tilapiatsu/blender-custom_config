bl_info = {
    "name": "ke_fit2grid",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 2),
    "blender": (2, 80, 0),
}
import bpy
import bmesh
from .ke_utils import get_loops, correct_normal, average_vector
from mathutils import Vector, Matrix


def fit_to_grid(co, grid):
    x, y, z = round(co[0] / grid) * grid, round(co[1] / grid) * grid, round(co[2] / grid) * grid
    return round(x, 5), round(y, 5), round(z, 5)


class VIEW3D_OT_ke_fit2grid(bpy.types.Operator):
    bl_idname = "view3d.ke_fit2grid"
    bl_label = "Fit2Grid"
    bl_description = "EDIT: Snaps verts of selected VERTS/EDGES/FACES to nearest set world grid step."
    bl_options = {'REGISTER', 'UNDO'}

    set_grid: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        if not self.set_grid:
            grid_setting = bpy.context.scene.kekit.fit2grid
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

                for v,co in zip(verts, vert_cos):
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
                bm.free()
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
            self.report({"INFO"}, "Fit2Grid: Invalid object/mode - Aborted")

        return {'FINISHED'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_OT_ke_fit2grid)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_ke_fit2grid)

if __name__ == "__main__":
    register()
