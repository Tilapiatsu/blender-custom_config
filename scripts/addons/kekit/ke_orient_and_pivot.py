bl_info = {
    "name": "ke Orient and Pivot",
    "author": "Kjell Emanuelsson 2019",
    "category": "Modeling",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
}

import bpy


class VIEW3D_OT_ke_opc(bpy.types.Operator):
    bl_idname = "view3d.ke_opc"
    bl_label = "Orientation and Pivot Combo"
    bl_description = "Orientation and Pivot Combo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    combo: bpy.props.EnumProperty(
        items=[("1", "OPC1", "", 1),
               ("2", "OPC2", "", 2),
               ("3", "OPC3", "", 3),
               ("4", "OPC4", "", 4)],
        name="Combo",
        default="1")

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        ctx_mode = bpy.context.mode
        orientation = "GLOBAL"
        pivot = "MEDIAN_POINT"

        if ctx_mode == "OBJECT":
            if self.combo == "1":
                orientation = bpy.context.scene.kekit.opc1_obj_o[1:]
                pivot = bpy.context.scene.kekit.opc1_obj_p[1:]
            elif self.combo == "2":
                orientation = bpy.context.scene.kekit.opc2_obj_o[1:]
                pivot = bpy.context.scene.kekit.opc2_obj_p[1:]
            elif self.combo == "3":
                orientation = bpy.context.scene.kekit.opc3_obj_o[1:]
                pivot = bpy.context.scene.kekit.opc3_obj_p[1:]
            elif self.combo == "4":
                orientation = bpy.context.scene.kekit.opc4_obj_o[1:]
                pivot = bpy.context.scene.kekit.opc4_obj_p[1:]

        elif ctx_mode == "EDIT_MESH":
            if self.combo == "1":
                orientation = bpy.context.scene.kekit.opc1_edit_o[1:]
                pivot = bpy.context.scene.kekit.opc1_edit_p[1:]
            elif self.combo == "2":
                orientation = bpy.context.scene.kekit.opc2_edit_o[1:]
                pivot = bpy.context.scene.kekit.opc2_edit_p[1:]
            elif self.combo == "3":
                orientation = bpy.context.scene.kekit.opc3_edit_o[1:]
                pivot = bpy.context.scene.kekit.opc3_edit_p[1:]
            elif self.combo == "4":
                orientation = bpy.context.scene.kekit.opc4_edit_o[1:]
                pivot = bpy.context.scene.kekit.opc4_edit_p[1:]

        bpy.ops.transform.select_orientation(orientation=orientation)
        bpy.context.tool_settings.transform_pivot_point = pivot

        return {'FINISHED'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_OT_ke_opc)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_ke_opc)

if __name__ == "__main__":
    register()
