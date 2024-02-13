import numpy as np

import bpy
from bpy.props import FloatProperty
from bpy.types import Operator
from mathutils import kdtree
from .._utils import mesh_world_coords, mesh_select_all, get_linked_objects


class KeCheckSnapping(Operator):
    bl_idname = "view3d.ke_check_snapping"
    bl_label = "Check Snapping"
    bl_description = ("Selects (2+) mesh objects verts that (are supposed to) share coords (='Snapped')\n"
                      "If there are Linked Objects selected, it will not select verts, only objects")
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
        ao = None
        oac = []
        linked = 0
        for obj in context.selected_objects:
            if len(get_linked_objects(obj)) > 1:
                linked += 1
            mesh_select_all(obj, False)
            wcos = mesh_world_coords(obj)
            oac.append([obj, wcos])

        if linked:
            if context.active_object in context.selected_objects:
                ao = context.active_object

        # FIND MATCHING CO'S
        obj_to_select = []
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
            mcount = sum(sel_mask)
            count += mcount
            if mcount:
                obj_to_select.append(obj)
            if not linked or obj == ao:
                obj.data.vertices.foreach_set("select", sel_mask)

        bpy.ops.object.select_all(action="DESELECT")
        if ao:
            obj_to_select = [ao]
        for o in obj_to_select:
            o.select_set(True)

        linktxt = ""
        if linked:
            linktxt = "[Linked Object(s)]"
            print("Note: Linked Object(s) selected - Active Object selection only")

        if ao or not linked:
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

        if count:
            self.report({"INFO"}, "Snapped - %i verts. %s" % (count, linktxt))
        else:
            self.report({"INFO"}, "Not Snapped. %s" % linktxt)

        return {"FINISHED"}
