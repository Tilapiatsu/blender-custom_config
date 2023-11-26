import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from .._utils import get_prefs


class KeOPC(Operator):
    bl_idname = "view3d.ke_opc"
    bl_label = "Orientation and Pivot Combo"
    bl_description = "Orientation and Pivot Combo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    combo: EnumProperty(
        items=[("1", "OPC1", "", 1),
               ("2", "OPC2", "", 2),
               ("3", "OPC3", "", 3),
               ("4", "OPC4", "", 4),
               ("5", "OPC5", "", 5),
               ("6", "OPC6", "", 6)],
        name="Combo",
        default="1")

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        ctx_mode = context.mode
        orientation = "GLOBAL"
        pivot = "MEDIAN_POINT"

        if ctx_mode == "OBJECT":
            if self.combo == "1":
                orientation = k.opc1_obj_o
                pivot = k.opc1_obj_p
            elif self.combo == "2":
                orientation = k.opc2_obj_o
                pivot = k.opc2_obj_p
            elif self.combo == "3":
                orientation = k.opc3_obj_o
                pivot = k.opc3_obj_p
            elif self.combo == "4":
                orientation = k.opc4_obj_o
                pivot = k.opc4_obj_p
            elif self.combo == "5":
                orientation = k.opc5_obj_o
                pivot = k.opc5_obj_p
            elif self.combo == "6":
                orientation = k.opc6_obj_o
                pivot = k.opc6_obj_p

        else:
            if self.combo == "1":
                orientation = k.opc1_edit_o
                pivot = k.opc1_edit_p
            elif self.combo == "2":
                orientation = k.opc2_edit_o
                pivot = k.opc2_edit_p
            elif self.combo == "3":
                orientation = k.opc3_edit_o
                pivot = k.opc3_edit_p
            elif self.combo == "4":
                orientation = k.opc4_edit_o
                pivot = k.opc4_edit_p
            elif self.combo == "5":
                orientation = k.opc5_edit_o
                pivot = k.opc5_edit_p
            elif self.combo == "6":
                orientation = k.opc6_edit_o
                pivot = k.opc6_edit_p

        bpy.ops.transform.select_orientation(orientation=orientation)
        context.tool_settings.transform_pivot_point = pivot
        return {'FINISHED'}
