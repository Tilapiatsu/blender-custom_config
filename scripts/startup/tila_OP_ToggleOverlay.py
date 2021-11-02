import bpy
bl_info = {
    "name": "toggle_overlay",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "View3D",
}


class TILA_ToggleOverlay(bpy.types.Operator):
    bl_idname = "view3d.toggle_overlay"
    bl_label = "TILA: Toggle overlay"
    bl_options = {'REGISTER', 'UNDO'}

    mode : bpy.props.EnumProperty(items=[("TOGGLE", "Toggle", ""), ("SOFT", "Soft", "")])

    soft_parameters=['show_annotation',
                     'show_extras',
                     'show_bones',
                     'show_relationship_lines',
                     'show_motion_paths',
                     'show_outline_selected',
                     'show_object_origins',
                     'show_floor',
                     'show_axis_x',
                     'show_axis_y',
                     'show_face_orientation']

    def toggle_state(self, state=None):
        if state is None:
            self.enabled = not (self.enabled)
        else:
            self.enabled = state

    def toggle_soft(self, state=None):
        if state is None:
            return
        else:
            for p in self.soft_parameters:
                if p in dir(bpy.context.space_data.overlay):
                    setattr(bpy.context.space_data.overlay, p, state)
    
    def is_enable(self):
        if self.mode == 'TOGGLE':
            return bpy.context.space_data.overlay
        elif self.mode == 'SOFT':
            return self.enabled
    
    def get_state(self):
        if self.mode == 'TOGGLE':
            self.enabled = self.is_enable()
        elif self.mode == 'SOFT':
            state = True
            for p in self.soft_parameters:
                if p in dir(bpy.context.space_data.overlay):
                    state =  state and getattr(bpy.context.space_data.overlay, p)

            self.enabled = state

    def execute(self, context):
        self.get_state()
        if self.mode == 'TOGGLE':
            bpy.ops.wm.context_toggle(data_path='space_data.overlay.show_overlays')
            
            if self.is_enable:
                self.toggle_state(state=False)
            else:
                self.toggle_state(state=True)

        elif self.mode == 'SOFT':
            spaces = context.area.spaces
            for s in spaces:
                if s.type =='VIEW_3D':
                    self.toggle_soft(not self.enabled)
                    self.toggle_state()
        
        return {'FINISHED'}

classes = (TILA_ToggleOverlay,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
