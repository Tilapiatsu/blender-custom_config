import bpy

class TILA_SmartExtrudeOperator(bpy.types.Operator):
    bl_label = "Smart Extrude"
    bl_idname = "mesh.smart_extrude"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.mode == 'EDIT')

    def execute(self, context):
        if bpy.context.object.type == 'CURVE':
            bpy.ops.curve.extrude()
            bpy.ops.transform.translate('INVOKE_DEFAULT')
            return {'FINISHED'}

        mesh = context.object.data
        selface = mesh.total_face_sel
        seledge = mesh.total_edge_sel
        selvert = mesh.total_vert_sel

        if selvert == 0:
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.dupli_extrude_cursor('INVOKE_DEFAULT')
            return {'FINISHED'}
        if selvert > 0 and seledge == 0:
            bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')
            return {'FINISHED'}
        if seledge > 0 and selface == 0:
            bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')
            return {'FINISHED'}

        bpy.ops.mesh.extrude_region_move('EXEC_DEFAULT')

        if mesh.total_face_sel != selface:
            bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True)
            return {'FINISHED'}

        bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True)
        return {'FINISHED'}

classes = (TILA_SmartExtrudeOperator,)

def register():
	for cl in classes:
		bpy.utils.register_class(cl)

def unregister():
	for cl in classes:
		bpy.utils.unregister_class(cl)

if __name__ == "__main__":
	register()