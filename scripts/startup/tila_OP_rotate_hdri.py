import bpy
import bmesh
bl_info = {
    "name": "Tila : Rotate HDI",
    "description": "Use the proper Rotate HDRI depending on the render mode",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "category": "3D View"
}



class TILA_RotateHDRI(bpy.types.Operator):
    bl_idname = "view3d.tila_rotate_hdri"
    bl_label = "Rotate HDRI"
    bl_options = {'REGISTER', 'UNDO'}

    rotate_command = {  'RENDERED':['EASYHDR_OT_rotate_hdri', 'bpy.ops.easyhdr.rotate_hdri'],
                        'MATERIAL':['ROTATE_OT_hdri', 'bpy.ops.rotate.hdri']}
    
    def invoke(self, context, event):
        if bpy.context.space_data.shading.type not in ['RENDERED', 'MATERIAL']:
            return {'CANCELLED'}

        if self.rotate_command[bpy.context.space_data.shading.type][0] not in dir(bpy.types):
            return  {'CANCELLED'}
        
        self.command = f'{self.rotate_command[bpy.context.space_data.shading.type][1]}("INVOKE_DEFAULT")'
        eval(self.command)
        return {'FINISHED'}



classes = (
    TILA_RotateHDRI,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
