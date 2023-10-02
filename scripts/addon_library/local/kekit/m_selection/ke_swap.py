from bpy.types import Operator


class KeSwap(Operator):
    bl_idname = "view3d.ke_swap"
    bl_label = "Swap Places"
    bl_description = "Swap places (transforms) for two objects. loc, rot & scale. (apply scale to avoid)"
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode != "EDIT_MESH"

    def execute(self, context):

        # CHECK SELECTION
        sel_obj = [o for o in context.selected_objects]
        if len(sel_obj) != 2:
            self.report({"INFO"}, "Incorrect Selection: Select 2 objects.")
            return {'CANCELLED'}

        # SWAP
        obj1 = sel_obj[0]
        obj2 = sel_obj[1]
        obj1_swap = obj2.matrix_world.copy()
        obj2_swap = obj1.matrix_world.copy()
        obj1.matrix_world = obj1_swap
        obj2.matrix_world = obj2_swap

        return {"FINISHED"}
