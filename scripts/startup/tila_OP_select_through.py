
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy, re
bl_info = {
    "name": "Select Through",
    "description": "Select through a mesh",
    "author": ("Tilapiatsu"),
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "category": "3D View"
}

bversion_string = bpy.app.version_string
bversion_reg = re.match("^(\d\.\d?\d)", bversion_string)
bversion = float(bversion_reg.group(0))

class TILA_select_through(bpy.types.Operator):
    bl_idname = "view3d.tila_select_through"
    bl_label = "TILA: Select Through"

    mode : bpy.props.StringProperty(name="mode", default='SET')
    type : bpy.props.StringProperty(name="type", default='BORDER')

    compatible_modes = ['EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_METABALL', 'EDIT_LATTICE', 'OBJECT', 'PAINT_WEIGHT', 'PAINT_VERTEX', 'PARTICLE']
    bypass_modes = ['EDIT_GPENCIL', 'PAINT_GPENCIL', 'SCULPT_GPENCIL']

    def get_release_condition(self, event):
        if bversion < 3.2:
            return event.type == 'MOUSEMOVE' and event.value == 'RELEASE'
        else:
            return event.type in ['MOUSEMOVE', 'LEFTMOUSE', 'RIGHTMOUSE', 'WINDOW_DEACTIVATE'] and event.value in ['RELEASE', 'NOTHING'] and self.run
    
    def get_run_condition(self, event) :
        if bversion < 3.2:
            return event.type == 'MOUSEMOVE' and event.value == 'PRESS'
        else:
            return event.type == 'MOUSEMOVE' and event.value == 'NOTHING' and not self.run

    def run_tool(self):
        try:
            if self.type == 'BORDER':
                self.run = True
                bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode, wait_for_input=False)
            if self.type == 'LASSO':
                self.run = True
                bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)
        except RuntimeError as e:
            print('Runtime Error :\n{}'.format(e))

    def modal(self, context, event):
        bpy.context.space_data.shading.show_xray = True
        # print(event.type, event.value)
        if self.get_release_condition(event):
            self.run = False
            bpy.context.space_data.shading.show_xray = False
            return {'CANCELLED'}
        elif self.get_run_condition(event):
            self.run_tool()
            return {'RUNNING_MODAL'}
        elif event.type in {'ESC'}:  # Cancel
            bpy.context.space_data.shading.show_xray = False
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.run = False
        if bpy.context.mode in self.compatible_modes:
            if bpy.context.space_data.shading.show_xray is True:
                self.run_tool()
            else:
                context.window_manager.modal_handler_add(self)
        elif bpy.context.mode in self.bypass_modes:
            self.run_tool()
            return{'FINISHED'}
        return {'RUNNING_MODAL'}


classes = (
    TILA_select_through,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
