import bpy

bl_info = {
    "name": "Tila : Toggle Wireframe",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class TILA_ToggleWireframe(bpy.types.Operator):
    bl_idname = "view3d.toggle_wireframe"
    bl_label = "TILA: Toggle Wireframe"
    bl_options = {'REGISTER'}

    mode: bpy.props.EnumProperty(items=[("SET", "Set", ""), ("OVERLAY", "Overlay", ""), ("RETOPO", "Retopology", "")])
    selected : bpy.props.BoolProperty(name='selected', default=False)

    def execute(self, context):
        if self.mode == 'OVERLAY':
            if self.selected:
                for o in context.selected_objects:
                    context.view_layer.objects.active = o
                    bpy.context.object.show_wire = not bpy.context.object.show_wire
            else:
                bpy.context.space_data.overlay.show_wireframes = not bpy.context.space_data.overlay.show_wireframes
        elif self.mode == 'SET':
            if self.selected:
                for o in context.selected_objects:
                    context.view_layer.objects.active = o
                    
                    if bpy.context.object.display_type != "WIRE":
                        bpy.context.object.display_type = "WIRE"
                    else:
                        bpy.context.object.display_type = "TEXTURED"
                        
            else:
                bpy.ops.view3d.toggle_shading(type='WIREFRAME')
        
        elif self.mode == "RETOPO":
            if self.selected:
                pass
            else:
                if context.space_data.overlay.show_retopology:
                    context.space_data.overlay.show_retopology = False
                    # context.space_data.overlay.show_occlude_wire = False
                    context.space_data.overlay.show_fade_inactive = False


                else:
                    context.space_data.overlay.show_retopology = True
                    # context.space_data.overlay.show_occlude_wire = True
                    context.space_data.overlay.show_fade_inactive = True
                    context.space_data.overlay.fade_inactive_alpha = 0.5

        return {'FINISHED'}

classes = (TILA_ToggleWireframe,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
