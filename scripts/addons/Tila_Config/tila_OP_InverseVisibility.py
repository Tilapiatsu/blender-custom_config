import bpy
bl_info = {
    "name": "inverse_visibility",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class ToggleXSymOperator(bpy.types.Operator):
    bl_idname = "view3d.inverse_visibility"
    bl_label = "TILA: Inverse Visibility"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Store initial mode
        initial_mode = context.mode

        if initial_mode in ['EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_TEXT', 'EDIT_ARMATURE', 'EDIT_METABALL', 'EDIT_LATTICE']:
            initial_mode = 'EDIT'

        # Switch to EDIT_MESH if needed
        if initial_mode not in ['EDIT']:
            bpy.ops.object.editmode_toggle()

        # Inverse Visibility
        self.invese()

        # Revert to initial mode
        bpy.ops.object.mode_set(mode = initial_mode)

        return {'FINISHED'}

    def invese(self):
        bpy.ops.mesh.reveal(select=True)
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.hide(unselected=False)

def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
