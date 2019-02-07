
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy
bl_info = {
    "name": "Select Through",
    "description": "Select through a mesh",
    "author": ("Tilapiatsu"),
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}


class TILA_select_through(bpy.types.Operator):
    bl_idname = "view3d.tila_select_through"
    bl_label = "Select Through"

    mode = bpy.props.StringProperty(name="mode", default='SET')
    type = bpy.props.StringProperty(name="type", default='BORDER')

    def modal(self, context, event):
        bpy.context.space_data.shading.show_xray = True
        if event.type == 'MOUSEMOVE' and event.value == 'PRESS':
            print(self.type, self.mode)
            if self.type == 'BORDER':
                bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode, wait_for_input=False)
            if self.type == 'LASSO':
                bpy.ops.view3d.select_lasso(mode=self.mode)
            return {'RUNNING_MODAL'}
        if event.type in {'ESC'}:  # Cancel
            bpy.context.space_data.shading.show_xray = False
            return {'CANCELLED'}
        elif event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
            bpy.context.space_data.shading.show_xray = False
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if bpy.context.space_data.shading.show_xray == True:
            if self.type == 'BORDER':
                bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode, wait_for_input=False)
            if self.type == 'LASSO':
                bpy.ops.view3d.select_lasso(mode=self.mode)
        else:
            context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
 
classes = (
    TILA_select_through
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
