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
            retopo_mode = bpy.context.scene.ps_set_
            prefs = context.preferences.addons['Poly_Source'].preferences
            if self.selected:
                pass
            else:
                if retopo_mode.PS_retopology:
                    retopo_mode.PS_retopology = False
                    context.space_data.overlay.show_occlude_wire = False
                    bpy.context.space_data.overlay.show_fade_inactive = False


                else:
                    retopo_mode.PS_retopology = True
                    context.space_data.overlay.show_occlude_wire = True
                    bpy.context.space_data.overlay.show_fade_inactive = True
                    bpy.context.space_data.overlay.fade_inactive_alpha = 0.5

                prefs.z_bias = 0.02
                prefs.opacity = 0.15
                prefs.verts_size = 1
                prefs.edge_width = 1

        return {'FINISHED'}

classes = (TILA_ToggleWireframe,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
