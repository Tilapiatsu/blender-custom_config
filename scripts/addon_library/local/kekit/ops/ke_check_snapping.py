import numpy as np

import bpy
from bpy.props import FloatProperty
from bpy.types import Operator
from mathutils import kdtree
from .._utils import mesh_world_coords, mesh_select_all


class KeCheckSnapping(Operator):
    bl_idname = "view3d.ke_check_snapping"
    bl_label = "Check Snapping"
    bl_description = "Selects (2+) mesh objects verts that (are supposed to) share coords (='Snapped')"
    bl_options = {'REGISTER', 'UNDO'}

    epsilon : FloatProperty(
        precision=6,
        min=0.000001,
        default=0.00001,
        name="Threshold",
        description="Distance tolerance for coordinates (or floating point rounding)"
    )

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.selected_objects)

    def execute(self, context):
        # CHECK MESH
        if len(context.selected_objects) < 2 or any([o for o in context.selected_objects if o.type != "MESH"]):
            self.report({"ERROR"}, "Select at least 2 Mesh Objects!")
            return {"CANCELLED"}

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        # GET 'OBJECT AND COORDS' LOOP PAIRS
        oac = []
        for obj in context.selected_objects:
            wcos = mesh_world_coords(obj)
            oac.append([obj, wcos])
            mesh_select_all(obj, False)

        # FIND MATCHING CO'S
        count = 0
        for obj, coords in oac:
            # SETUP K-DIMENSIONAL TREE SPACE-PARTITIONING DATA STRUCTURE
            cmp_co = np.concatenate([i[1] for i in oac if i[0].name != obj.name])
            size = len(cmp_co)
            kd = kdtree.KDTree(size)
            for i, v in enumerate(cmp_co):
                kd.insert(v, i)
            kd.balance()

            # FIND MATCHING CO'S IN K-D TREE & SELECT
            sel_mask = [bool(kd.find_range(co, self.epsilon)) for co in coords]
            obj.data.vertices.foreach_set("select", sel_mask)
            count += sum(sel_mask)

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        if count:
            self.report({"INFO"}, "Snapped: %i verts share coords" % count)
        else:
            self.report({"INFO"}, "Not Snapped: No verts share coords")

        return {"FINISHED"}
