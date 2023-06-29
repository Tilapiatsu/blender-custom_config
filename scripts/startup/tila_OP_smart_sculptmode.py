
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy

bl_info = {
    "name": "Tila : Smart sculpt Mode",
    "description": "Automatically switch to the proper sculpt mode",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (3, 60, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "category": "3D View"
}


class TILA_smart_sculptmode(bpy.types.Operator):
    bl_idname = "view3d.tila_smart_sculptmode"
    bl_label = "Smart Sculpt Mode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type in ['VIEW_3D']


    def execute(self, context):
                    
        if bpy.context.mode == 'OBJECT':
            if bpy.context.active_object is None:
                return {'CANCELLED'}
            if bpy.context.active_object.type == 'MESH':
                bpy.ops.sculpt.sculptmode_toggle()

            elif bpy.context.active_object.type == 'GPENCIL':
                bpy.ops.gpencil.sculptmode_toggle()

            elif bpy.context.active_object.type == 'CURVES':
                bpy.ops.curves.sculptmode_toggle()

            else:
                bpy.ops.object.editmode_toggle()

        elif bpy.context.mode in ['SCULPT', 'SCULPT_CURVES', 'SCULPT_GPENCIL']:
            bpy.ops.object.editmode_toggle()
        
        return {'FINISHED'}


classes = (
    TILA_smart_sculptmode,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
