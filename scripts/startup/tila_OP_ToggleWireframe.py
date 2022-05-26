import bpy
bl_info = {
    "name": "toggle_wireframe",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class TILA_ToggleWireframe(bpy.types.Operator):
    bl_idname = "view3d.toggle_wireframe"
    bl_label = "TILA: Toggle Wireframe"
    bl_options = {'REGISTER', 'UNDO'}

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
            xray_props = bpy.context.scene.xray_props
            if self.selected:
                pass
            else:
                if xray_props.draw_xray_mode == 'ENABLED':
                    xray_props.draw_xray_mode = 'DISABLED'
                    context.space_data.overlay.show_occlude_wire = False
                else:
                    xray_props.draw_xray_mode = 'ENABLED'
                    context.space_data.overlay.show_occlude_wire = True
                xray_props.draw_offset = 0.02
                xray_props.polygon_opacity = 1.0
                xray_props.edge_opacity = 1.0
                xray_props.face_color = (0.008, 0.111, 0.566, 0.5)
                xray_props.highlight_color = (0.381, 1.0, 0.915, 0.25)


        return {'FINISHED'}

classes = (TILA_ToggleWireframe,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
