import bpy
from mathutils import *

bl_info = {
	"name": "Tila : Remove End Bones",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Armature",
}

class TILA_RemoveEndBonesOperator(bpy.types.Operator):
    bl_idname = "object.tila_remove_end_bones"
    bl_label = "TILA: Remove End Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.active_object is None or bpy.context.active_object.type != 'ARMATURE':
            return {'CANCELLED'}
        
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'OBJECT':
                bpy.ops.object.editmode_toggle()
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.object.select_pattern(pattern="*_end")
                bpy.ops.armature.delete()
                bpy.ops.object.editmode_toggle()
                
            elif context.mode == 'EDIT':
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.object.select_pattern(pattern="*_end")
                bpy.ops.armature.delete()
                

        return {'FINISHED'}


addon_keymaps = []

classes = (TILA_RemoveEndBonesOperator,)

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
