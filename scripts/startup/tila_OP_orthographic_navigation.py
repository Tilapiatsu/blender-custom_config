
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import math, re
import bpy
bl_info = {
    "name": "Tila : Othographic navigation",
    "description": "This tool help you to navigate in the 3d view in a more easy way",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "category": "3D View"
}
# Need to add a mode to align Orthographic view based on the current face selection

bversion_string = bpy.app.version_string
bversion_reg = re.match("^(\d\.\d?\d)", bversion_string)
bversion = float(bversion_reg.group(0))

class TILA_OrthographicNavigation(bpy.types.Operator):
    bl_idname = "view3d.tila_orthographic_navigation"
    bl_label = "Othographic Navigation"

    direction : bpy.props.EnumProperty(name="direction", items=[("UP", "Up", ""), ("DOWN", "Doww", ""), ("LEFT", "Left", ""), ("RIGHT", "Right", "")])
    angle : bpy.props.FloatProperty(name="angle", default=90)
    move_threshold : bpy.props.FloatProperty(name='move_threshold', default=100)
    relative_to_selected_element : bpy.props.BoolProperty(name="relative", default=False)

    dir = {'UP': 'ORBITUP', 'DOWN': 'ORBITDOWN', 'LEFT': 'ORBITLEFT', 'RIGHT': 'ORBITRIGHT'}

    def get_release_condition(self, event):
        if bversion > 3.2:
            return event.value == 'RELEASE'
        else:
            return event.type in ['MOUSEMOVE', 'LEFTMOUSE', 'RIGHTMOUSE', 'WINDOW_DEACTIVATE'] and event.value in ['RELEASE', 'NOTHING']
    
    def get_run_condition(self, event) :
        if bversion < 3.2:
            return event.type == 'MOUSEMOVE' and event.value == 'PRESS'
        else:
            return event.type == event.type == 'MOUSEMOVE' and event.value == 'NOTHING'

    def set_initial_position(self, event):
        self.initial_mouseposition = event.mouse_x, event.mouse_y

    def need_switch_view(self, event):
        delta_x = event.mouse_x - self.initial_mouseposition[0]
        delta_y = event.mouse_y - self.initial_mouseposition[1]
        if delta_x > self.move_threshold:
            self.set_initial_position(event)
            return True, 'LEFT'
        elif delta_x < - self.move_threshold:
            self.set_initial_position(event)
            return True, 'RIGHT'
        elif delta_y > self.move_threshold:
            self.set_initial_position(event)
            return True, 'DOWN'
        elif delta_y < - self.move_threshold:
            self.set_initial_position(event)
            return True, 'UP'
        else:
            return False, 'NONE'

    def switch_view(self, event):
        try:
            need_switch, direction = self.need_switch_view(event)
            if need_switch:
                # need to check view_matrix to get better rotation for TOP and BOTTOM VIEW https://docs.blender.org/api/current/bpy.types.RegionView3D.html?highlight=orthographic#bpy.types.RegionView3D.is_orthographic_side_view
                if self.use_relatrive_to_selected_element:
                    bpy.ops.view3d.view_orbit(angle=self.angle, type=self.dir[direction])
                    bpy.ops.view3d.view_axis(type='FRONT', relative=True, align_active=True)
                else:
                    bpy.ops.view3d.view_orbit(angle=self.angle, type=self.dir[direction])
                    bpy.ops.view3d.view_axis(type='FRONT', relative=True)
        except RuntimeError as e:
            print('Runtime Error :\n{}'.format(e))

    def modal(self, context, event):
        if self.region.is_perspective:
            self.region.view_perspective = 'ORTHO'
            bpy.ops.view3d.view_axis(type='FRONT', relative=True)
        if self.get_run_condition(event):
            self.switch_view(event)
            return {'RUNNING_MODAL'}
        if event.type in {'ESC'}:  # Cancel
            return {'CANCELLED'}
        elif self.get_release_condition(event):
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.region = bpy.context.region_data
        self.object = bpy.context.object

        self.set_initial_position(event)
        return {'RUNNING_MODAL'}
    
    @property
    def use_relatrive_to_selected_element(self):
        return self.relative_to_selected_element and self.object and self.object.type == 'MESH' and self.object.data.is_editmode

classes = (
    TILA_OrthographicNavigation,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
