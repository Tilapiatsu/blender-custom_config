bl_info = {
    "name": "keQuickScale",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
}
import bpy


class VIEW3D_OT_ke_quickscale(bpy.types.Operator):
    bl_idname = "view3d.ke_quickscale"
    bl_label = "Quick Scale"
    bl_description = "Set dimension (in current scene unit). Unit sized from chosen axis. Obj & Edit mode (selection)"
    bl_options = {'REGISTER'}

    user_axis : bpy.props.IntProperty(default=2)

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        user_value = bpy.context.scene.kekit.qs_user_value
        unit_size = bpy.context.scene.kekit.qs_unit_size
        other_axis = [0 ,1 ,2]
        other_axis.pop(self.user_axis)
        sel_verts = []
        vpos = []

        # Check selections
        sel_obj = [obj for obj in context.selected_objects if obj.type == "MESH"][0]

        if context.mode != "OBJECT":
            sel_obj.update_from_editmode()
            sel_verts = [v.index for v in sel_obj.data.vertices if v.select]

        else:  # Object Mode
            sel_verts = [v.index for v in sel_obj.data.vertices]

        if not sel_verts:
            self.report({'WARNING'}, "No vertices found/selected")
            print("Cancelled: No vertices found/selected")
            return {'CANCELLED'}

        vpos.extend([sel_obj.matrix_world @ sel_obj.data.vertices[v].co for v in sel_verts])

        # Calc dimension values
        x, y, z = [], [], []
        for i in vpos:
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])
        x, y, z = sorted(x), sorted(y), sorted(z)
        dimension = x[-1] - x[0], y[-1] - y[0], z[-1] - z[0]

        # Resize
        if context.mode == "OBJECT":
            obj_val = user_value / (dimension[self.user_axis] / sel_obj.scale[self.user_axis])
            factor = obj_val / sel_obj.scale[self.user_axis]

            new_scale = [1, 1, 1]
            if unit_size:
                new_scale[self.user_axis] = obj_val
                new_scale[other_axis[0]] = factor * sel_obj.scale[other_axis[0]]
                new_scale[other_axis[1]] = factor * sel_obj.scale[other_axis[1]]
                sel_obj.scale = (new_scale[0], new_scale[1], new_scale[2])
            else:
                sel_obj.scale[self.user_axis] = obj_val

        else:
            edit_val =  user_value / dimension[self.user_axis]
            new_dimensions = [edit_val, edit_val, edit_val]

            if not unit_size:
                new_dimensions[other_axis[0]] = 1
                new_dimensions[other_axis[1]] = 1

            bpy.ops.transform.resize(value=new_dimensions, orient_type='GLOBAL', orient_matrix_type='GLOBAL',
                                     constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False,
                                     use_proportional_connected=False, use_proportional_projected=False, snap=False,
                                     gpencil_strokes=False, texture_space=False, remove_on_cancel=False,
                                     release_confirm=False)

        return {'FINISHED'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    VIEW3D_OT_ke_quickscale,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
