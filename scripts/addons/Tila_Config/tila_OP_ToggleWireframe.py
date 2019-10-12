import bpy
bl_info = {
    "name": "toggle_wireframe",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class ToggleXSymOperator(bpy.types.Operator):
    bl_idname = "view3d.toggle_wireframe"
    bl_label = "TILA: Toggle Wireframe"
    bl_options = {'REGISTER', 'UNDO'}

    selected : bpy.props.BoolProperty(name='selected', default=False)

    def execute(self, context):
        if self.selected:
            for o in context.selected_objects:
                context.view_layer.objects.active = o
                bpy.context.object.show_wire = not bpy.context.object.show_wire
        else:
            bpy.context.space_data.overlay.show_wireframes = not bpy.context.space_data.overlay.show_wireframes
        return {'FINISHED'}


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
