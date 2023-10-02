import bpy
from bpy.types import Operator
from mathutils import kdtree
from .._utils import mesh_world_coords, mesh_select_all, mesh_hide_all, dupe, shred


class KeSelectOccludedVerts(Operator):
    bl_idname = "view3d.ke_select_occluded_verts"
    bl_label = "Select Occluded Verts"
    bl_description = "Selects verts of selected object(s) that are occluded ('inside') the Active Object"
    bl_options = {'REGISTER', 'UNDO'}

    epsilon = 0.0001
    surface_offset = -0.001

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.object is not None and
                context.mode == "OBJECT")

    def execute(self, context):
        # CHECK MESH
        if len(context.selected_objects) < 2 or any([o for o in context.selected_objects if o.type != "MESH"]):
            self.report({"ERROR"}, "Select at least 2 Mesh Objects!")
            return {"CANCELLED"}

        # PREP OBJECTS & SELECTIONS
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target="MESH")

        og_active = context.object
        og_sel_obj = [o for o in context.selected_objects if o != og_active]

        for o in context.selected_objects:
            o.select_set(False)

        # TEMP-BOOL OCCLUDED INTERSECTION MESH & USE TO FIND MATCHING CO'S
        for obj in og_sel_obj:
            # CREATE TEMP DUPES FOR BOOLEAN
            o = dupe(obj)
            active = dupe(og_active)

            # SET SELECTIONS
            o.select_set(True)
            mesh_select_all(o, True)
            mesh_hide_all(o, False)
            context.view_layer.objects.active = active
            override = {"object": active}

            # SHRINK / ON-SURFACE OFFSET
            mod = active.modifiers.new("KeTempDisp", "DISPLACE")
            mod.show_viewport = False
            mod.strength = self.surface_offset
            bpy.ops.object.modifier_apply(override, modifier=mod.name)

            # INTERSECTION BOOLEAN
            mod = active.modifiers.new("KeTempBool", "BOOLEAN")
            mod.show_viewport = False
            mod.operation = "INTERSECT"
            mod.solver = 'EXACT'
            # mod.use_hole_tolerant = True
            mod.object = o
            bpy.ops.object.modifier_apply(override, modifier=mod.name)

            # FIND MATCHING CO'S
            imesh = context.object

            if len(imesh.data.vertices) != 0:
                mesh_select_all(obj, False)
                obj_cos = mesh_world_coords(obj)
                imesh_cos = mesh_world_coords(imesh)

                # SETUP K-DIMENSIONAL TREE SPACE-PARTITIONING DATA STRUCTURE
                size = len(imesh_cos)
                kd = kdtree.KDTree(size)
                for i, v in enumerate(imesh_cos):
                    kd.insert(v, i)
                kd.balance()

                # FIND MATCHING CO'S IN K-D TREE & SELECT VERTS
                sel_mask = [bool(kd.find_range(co, self.epsilon)) for co in obj_cos]
                obj.data.vertices.foreach_set("select", sel_mask)

            else:
                self.report({"ERROR"}, "%s - Failed to boolean intersection mesh!" % obj.name)

            # CLEANUP TEMP MESH
            shred(imesh)
            shred(o)

        # FINALIZE
        for o in og_sel_obj:
            o.select_set(True)

        context.view_layer.objects.active = og_sel_obj[0]
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

        return {"FINISHED"}
