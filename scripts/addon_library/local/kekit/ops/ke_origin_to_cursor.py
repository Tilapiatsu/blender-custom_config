import bpy
from bpy.props import EnumProperty
from bpy.types import Operator


class KeOriginToCursor(Operator):
    bl_idname = "view3d.ke_origin_to_cursor"
    bl_label = "Align Origin To Cursor"
    bl_description = "Aligns selected object(s) origin(s) to Cursor (Rotation,Location or both)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    align: EnumProperty(
        items=[("LOCATION", "Location Only", "", 1),
               ("ROTATION", "Rotation Only", "", 2),
               ("BOTH", "Location & Rotation", "", 3)
               ],
        name="Align",
        default="BOTH")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        column = layout.column()
        column.prop(self, "align", expand=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):

        if len(context.selected_objects) == 0:
            self.report({"INFO"}, "No object selected?")
            return {"CANCELLED"}

        # make sure the cursor euler values are not quaternion converted floating point garbage:
        og_cursor_setting = str(context.scene.cursor.rotation_mode)
        context.scene.cursor.rotation_mode = "XYZ"
        crot = context.scene.cursor.rotation_euler
        crot.x = round(crot.x, 4)
        crot.y = round(crot.y, 4)
        crot.z = round(crot.z, 4)

        if context.object.type == 'MESH':
            if context.object.data.is_editmode:
                bpy.ops.object.mode_set(mode="OBJECT")

        if self.align == "BOTH":
            context.scene.tool_settings.use_transform_data_origin = True
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), orient_type='CURSOR', mirror=True,
                                        use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                        proportional_size=1, use_proportional_connected=False,
                                        use_proportional_projected=False)
            context.scene.tool_settings.use_transform_data_origin = False

        else:
            cursor = context.scene.cursor
            ogloc = list(cursor.location)

            if self.align == 'LOCATION':
                context.scene.tool_settings.use_transform_data_origin = True
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                context.scene.tool_settings.use_transform_data_origin = False

            elif self.align == 'ROTATION':
                obj_loc = context.object.matrix_world.translation.copy()
                context.scene.tool_settings.use_transform_data_origin = True
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), orient_type='CURSOR', mirror=True,
                                            use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                            proportional_size=1, use_proportional_connected=False,
                                            use_proportional_projected=False)
                cursor.location = obj_loc
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                context.scene.tool_settings.use_transform_data_origin = False
                cursor.location = ogloc

        bpy.ops.transform.select_orientation(orientation='LOCAL')
        context.scene.cursor.rotation_mode = og_cursor_setting

        return {'FINISHED'}
