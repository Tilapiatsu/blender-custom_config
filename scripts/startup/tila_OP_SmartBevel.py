import bpy
import bmesh

class TILA_SmartBevelOperator(bpy.types.Operator):
    bl_label = "Smart Bevel"         # display name in the interface.
    bl_idname = "mesh.smart_bevel"        # unique identifier for buttons and menu items to reference.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.mode == 'EDIT')

    def execute(self, context):
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        sel = []
        for v in bm.verts:
            if v.select:
                sel.append(v)

        if len(sel) == 0:
            self.report({'ERROR'}, 'Select at least one element')

        else:
            if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
                bpy.ops.mesh.bevel('INVOKE_DEFAULT',clamp_overlap=True,affect='VERTICES')
                return {'FINISHED'}
            elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
                bpy.ops.mesh.select_mode(type = 'EDGE')
                print('edge mode...')
                bpy.ops.mesh.region_to_loop('INVOKE_DEFAULT')
                print('selecting border...')
                me = bpy.context.object.data
                bm = bmesh.from_edit_mesh(me)
                sel = []
                for v in bm.verts:
                    if v.select:
                        sel.append(v)

                if len(sel) == 0:
                    bpy.ops.mesh.select_all(action='SELECT')

            bpy.ops.mesh.bevel('INVOKE_DEFAULT', clamp_overlap=True, miter_outer='ARC')
        bpy.ops.mesh.remove_doubles()

        return {'FINISHED'}

classes = (TILA_SmartBevelOperator,)

def register():
	for cl in classes:
		bpy.utils.register_class(cl)

def unregister():
	for cl in classes:
		bpy.utils.unregister_class(cl)

if __name__ == "__main__":
	register()