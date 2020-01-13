import bpy
from bpy.types import Menu, Operator

# -------------------------------------------------------------------------------------------------
# Operators
# -------------------------------------------------------------------------------------------------

class VIEW3D_OT_ke_snap_target(Operator):
    bl_idname = "ke.snap_target"
    bl_label = "Snap Target"
    bl_options = {'REGISTER', 'UNDO'}

    ke_snaptarget: bpy.props.EnumProperty(
        items=[("CLOSEST", "Closest", "Closest", "", 1),
               ("CENTER", "Center", "Center", "", 2),
               ("MEDIAN", "Median", "Median", "", 3),
               ("ACTIVE", "Active", "Active", "", 4),
               ("PROJECT", "Project Self", "Project Self", "", 5),
               ("ALIGN", "Align Rotation", "Align Rotation", "", 6)],
        name="Snap Target",
        default="CLOSEST")

    def execute(self, context):
        ct = bpy.context.scene.tool_settings
        if self.ke_snaptarget == 'PROJECT':
            ct.use_snap_self = not ct.use_snap_self
        elif self.ke_snaptarget == 'ALIGN':
            ct.use_snap_align_rotation = not ct.use_snap_align_rotation
        else:
            ct.snap_target = self.ke_snaptarget
        return {'FINISHED'}


class VIEW3D_OT_ke_snap_element(Operator):
    bl_idname = "ke.snap_element"
    bl_label = "Snap Element"
    bl_options = {'REGISTER', 'UNDO'}

    ke_snapelement: bpy.props.EnumProperty(
        items=[("INCREMENT", "Increment", "", "SNAP_INCREMENT", 1),
               ("VERTEX", "Vertex", "", "SNAP_VERTEX", 2),
               ("EDGE", "Edge", "", "SNAP_EDGE", 3),
               ("FACE", "Face", "", "SNAP_FACE", 4),
               ("VOLUME", "Volume", "", "SNAP_VOLUME", 5),
               ("MIX", "Element Mix", "", "SNAP_MIX", 6)],
        name="Snap Element",
        default="INCREMENT")


    def execute(self, context):
        ct = bpy.context.scene.tool_settings
        ct.use_snap = True

        if self.ke_snapelement == "MIX":
            ct.snap_elements = {'VERTEX', 'EDGE', 'EDGE_MIDPOINT', 'FACE'}

        elif self.ke_snapelement == "EDGE":
            ct.snap_elements = {'EDGE', 'EDGE_MIDPOINT'}

        elif self.ke_snapelement == "INCREMENT":
            ct.snap_elements = {'INCREMENT'}
            ctx_mode = bpy.context.mode
            if ctx_mode == "OBJECT":
                ct.use_snap_grid_absolute = True
            else:
                ct.use_snap_grid_absolute = False
        else:
            ct.snap_elements = {self.ke_snapelement}

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Custom Pie Menus
# -------------------------------------------------------------------------------------------------

class VIEW3D_MT_PIE_ke_snapping(Menu):
    bl_label = "keSnapping"
    bl_idname = "VIEW3D_MT_ke_pie_snapping"

    def draw(self, context):
        ct = bpy.context.scene.tool_settings
        layout = self.layout

        pie = layout.menu_pie()
        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3
        if not ct.use_snap_self:
            cbox.operator("ke.snap_target", text="Project Self", icon="PROP_PROJECTED",depress=False).ke_snaptarget = "PROJECT"
        else:
            cbox.operator("ke.snap_target", text="Project Self", icon="PROP_PROJECTED",depress=True).ke_snaptarget = "PROJECT"

        if not ct.use_snap_align_rotation:
            cbox.operator("ke.snap_target", text="Align Rotation", icon="ORIENTATION_NORMAL", depress=False).ke_snaptarget = "ALIGN"
        else:
            cbox.operator("ke.snap_target", text="Align Rotation", icon="ORIENTATION_NORMAL", depress=True).ke_snaptarget = "ALIGN"

        cbox.separator()

        if not ct.snap_target == "MEDIAN":
            cbox.operator("ke.snap_target", text="Median", icon="PIVOT_MEDIAN", depress=False).ke_snaptarget = "MEDIAN"
        else:
            cbox.operator("ke.snap_target", text="Median", icon="PIVOT_MEDIAN", depress=True).ke_snaptarget = "MEDIAN"

        if not ct.snap_target == "ACTIVE":
            cbox.operator("ke.snap_target", text="Active", icon="PIVOT_ACTIVE", depress=False).ke_snaptarget = "ACTIVE"
        else:
            cbox.operator("ke.snap_target", text="Active", icon="PIVOT_ACTIVE", depress=True).ke_snaptarget = "ACTIVE"

        if not ct.snap_target == "CLOSEST":
            cbox.operator("ke.snap_target", text="Closest", icon="NORMALS_VERTEX_FACE", depress=False).ke_snaptarget = "CLOSEST"
        else:
            cbox.operator("ke.snap_target", text="Closest", icon="NORMALS_VERTEX_FACE", depress=True).ke_snaptarget = "CLOSEST"

        # gap = pie.column()
        # gap.scale_y = 7

        pie = layout.menu_pie()
        pie.operator("ke.snap_element", text="Vertex", icon="SNAP_VERTEX").ke_snapelement = "VERTEX"
        pie.operator("ke.snap_element", text="Element Mix", icon="SNAP_ON").ke_snapelement = "MIX"
        pie.operator("ke.snap_element", text="Increment/Grid", icon="SNAP_GRID").ke_snapelement = "INCREMENT"
        pie.separator()
        pie.operator("ke.snap_element", text="Edge", icon="SNAP_EDGE").ke_snapelement = "EDGE"
        pie.separator()
        pie.operator("ke.snap_element", text="Face", icon="SNAP_FACE").ke_snapelement = "FACE"

        pie = layout.menu_pie()
        c = pie.column()
        cbox = c.box().column()



# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    VIEW3D_OT_ke_snap_element,
    VIEW3D_OT_ke_snap_target,
    VIEW3D_MT_PIE_ke_snapping,
    )

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
