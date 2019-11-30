import bpy


class DisableSelectedCheckerMaps(bpy.types.Operator):
    bl_idname = "uv.toolkit_disable_selected_checker_materials"
    bl_label = "Disable selected Materials (UVToolkit)"
    bl_description = "Disable selected checker materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.selected_objects == []:
            self.report({'WARNING'}, 'No Objects Selected')
            return {'CANCELLED'}
        else:
            active_object = context.view_layer.objects.active  # Store active object
            current_mode = context.object.mode  # Store object mode
            for obj in context.selected_objects:
                context.view_layer.objects.active = obj
                context.active_object.select_set(state=True)
                if context.active_object.active_material is not None:
                    if bpy.data.materials[0].name.startswith("checker_material"):
                        context.object.active_material_index = 0
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.material_slot_remove()
            bpy.ops.object.mode_set(mode=current_mode)  # Restore object mode
            context.view_layer.objects.active = active_object  # Restore active object
            return{'FINISHED'}
