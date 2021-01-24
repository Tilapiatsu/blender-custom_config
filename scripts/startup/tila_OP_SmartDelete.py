import bpy
bl_info = {
    "name": "Smart Delete",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Object",
}


class TILA_SmartDeleteOperator(bpy.types.Operator):
    bl_idname = "object.tila_smartdelete"
    bl_label = "TILA: Smart Delete"
    bl_options = {'REGISTER', 'UNDO'}

    menu: bpy.props.BoolProperty(name='call_menu', default=False)

    def execute(self, context):
        if context.space_data.type == 'VIEW_3D':
            if self.menu:
                if context.mode == 'EDIT_MESH':
                    bpy.ops.wm.call_menu(name='VIEW3D_MT_edit_mesh_delete')
                elif context.mode == 'EDIT_CURVE':
                    bpy.ops.wm.call_menu(name='VIEW3D_MT_edit_curve_delete')
            else:
                if context.mode == 'EDIT_MESH':
                    current_mesh_mode = context.tool_settings.mesh_select_mode[:]
                    # if vertex mode on
                    if current_mesh_mode[0]:
                        bpy.ops.mesh.dissolve_verts()

                    # if vertex mode on
                    if current_mesh_mode[1]:
                        bpy.ops.mesh.dissolve_edges(use_verts=True)

                    # if vertex mode on
                    if current_mesh_mode[2]:
                        bpy.ops.mesh.delete(type='FACE')
                elif context.mode == 'EDIT_CURVE':
                    bpy.ops.curve.delete(type='VERT')

                elif context.mode == 'EDIT_GPENCIL':
                    try:
                        bpy.ops.gpencil.delete(type='POINTS')
                    except Exception as e:
                        print("Warning: %r" % e)
            
                elif context.mode == 'OBJECT':
                    bpy.ops.object.delete(use_global=False, confirm=False)

        elif context.space_data.type == 'OUTLINER':
            bpy.ops.outliner.delete()

        elif context.space_data.type == 'FILE_BROWSER':
            bpy.ops.file.delete()
        # elif context.space_data.type == 'IMAGE_EDITOR':
        #     layout.label("No Context! image editor")
        return {'FINISHED'}


addon_keymaps = []

classes = (TILA_SmartDeleteOperator,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
