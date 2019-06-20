import bpy

class SeparateAndSelect(bpy.types.Operator):
    bl_idname = "mesh.separate_and_select"        # unique identifier for buttons and menu items to reference.
    bl_label = "Separate and Select"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):

        base = bpy.context.active_object
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.editmode_toggle()
        base.select_set(state=False)
        selected = bpy.context.selected_objects
        for sel in selected:
            bpy.context.view_layer.objects.active = sel
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        return {'FINISHED'}

def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()