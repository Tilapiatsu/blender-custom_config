bl_info = {
    "name": "keMouseAxisMove",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 2),
    "blender": (2, 80, 0),
}

import bpy
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import region_2d_to_location_3d
from .ke_utils import getset_transform, restore_transform


class VIEW3D_OT_ke_mouse_axis_move(bpy.types.Operator):
    bl_idname = "view3d.ke_mouse_axis_move"
    bl_label = "Mouse Axis Move"
    bl_description = "Runs Grab with Axis auto-locked based on your mouse movement (or viewport when rot) using recalculated orientation " \
                     "based on the selected Orientation type."
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[("MOVE", "Move", "", "MOVE", 1),
               ("DUPE", "Duplicate", "", "DUPE", 2),
               ("ROT", "Rotate", "", "ROT", 3),
               ("SCL", "Resize", "", "SCL", 4)
               ],
        name="Mode",
        default="MOVE")

    mouse_pos = Vector((0, 0))
    startpos = Vector((0, 0, 0))
    tm = Matrix().to_3x3()
    rv = None
    ot = "GLOBAL"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    @classmethod
    def get_mpos(cls, context, coord, pos):
        region = context.region
        rv3d = context.region_data
        return region_2d_to_location_3d(region, rv3d, coord, pos)

    def invoke(self, context, event):
        # mouse track start
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)
        # Mouse vec start
        if self.mode != "ROT":
            self.startpos = self.get_mpos(context, self.mouse_pos, context.object.location)

        # get rotation vectors
        og = getset_transform(setglobal=False)
        self.ot = og[0]

        #check type
        if context.object.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}:
            em = bool(context.object.data.is_editmode)
        else:
            em = "OBJECT"

        if og[0] == "GLOBAL":
            self.rv = self.tm[0].to_3d(), self.tm[1].to_3d(), self.tm[2].to_3d()

        elif og[0] == "CURSOR":
            cm = context.scene.cursor.matrix.to_3x3()
            self.rv = cm[0], cm[1], cm[2]

        elif og[0] == "LOCAL" or og[0] == "NORMAL" and not em :
            self.tm = context.object.matrix_world.to_3x3()
            self.rv = self.tm[0].to_3d(), self.tm[1].to_3d(), self.tm[2].to_3d()

        elif og[0] == "VIEW":
            vm = context.space_data.region_3d.view_matrix.to_3x3()
            self.rv = vm[0], vm[1], vm[2]

        elif og[0] == "GIMBAL":
            self.report({"INFO"}, "Gimbal Orientation not supported")
            return {'CANCELLED'}

        # NORMAL / SELECTION
        elif em:
            context.object.update_from_editmode()
            sel = [v for v in context.object.data.vertices if v.select]
            if sel:
                try:
                    bpy.ops.transform.create_orientation(name='keTF', use_view=False, use=True, overwrite=True)
                    self.tm = context.scene.transform_orientation_slots[0].custom_orientation.matrix.copy()
                    bpy.ops.transform.delete_orientation()
                    restore_transform(og)
                    self.rv = self.tm[0].to_3d(), self.tm[1].to_3d(), self.tm[2].to_3d()
                except RuntimeError:
                    print("Fallback: Invalid selection for Orientation - Using Local")
                    # Normal O. with a entire cube selected will fail create_o.
                    bpy.ops.transform.select_orientation(orientation='LOCAL')
                    self.tm = context.object.matrix_world.to_3x3()
                    self.rv = self.tm[0].to_3d(), self.tm[1].to_3d(), self.tm[2].to_3d()
            else:
                self.report({"INFO"}, " No elements selected ")
                return {'CANCELLED'}
        else:
            self.report({"INFO"}, "Unsupported Orientation Mode")
            return {'CANCELLED'}

        if self.rv is not None:
            # abs-ahoy - just need the axis, no direction. there prob is a more optimal way for all this...
            self.rv = [Vector((abs(self.rv[0][0]), abs(self.rv[0][1]), abs(self.rv[0][2]))).normalized(), \
                      Vector((abs(self.rv[1][0]), abs(self.rv[1][1]), abs(self.rv[1][2]))).normalized(), \
                      Vector((abs(self.rv[2][0]), abs(self.rv[2][1]), abs(self.rv[2][2]))).normalized()]
        else:
            self.report({"INFO"}, "Aborted: Unexpected state") # justincase
            return {'CANCELLED'}

        if self.mode == "DUPE":
            if em:
                bpy.ops.mesh.duplicate('INVOKE_DEFAULT')
            else:
                bpy.ops.object.duplicate('INVOKE_DEFAULT')

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            # mouse track end candidate
            new_mouse_pos = Vector((int(event.mouse_region_x), int(event.mouse_region_y)))
            t1 = abs(new_mouse_pos[0] - self.mouse_pos[0])
            t2 = abs(new_mouse_pos[1] - self.mouse_pos[1])

            if t1 > 10 or t2 > 10:

                if self.mode == "ROT":
                    # doesnt really need the modal mouse mode, but meh.
                    rm = context.space_data.region_3d.view_matrix
                    v = Vector(rm[2]).to_3d()
                else:
                    # mouse vec end
                    newpos = self.get_mpos(context, new_mouse_pos, context.object.location)
                    v = Vector(newpos - self.startpos).normalized()

                v = Vector((abs(v[0]), abs(v[1]), abs(v[2])))

                # compare mouse vec to rotation vecs and pick axis to lock
                x = v.dot(self.rv[0].normalized())
                y = v.dot(self.rv[1].normalized())
                z = v.dot(self.rv[2].normalized())

                if x > y and x > z:
                    axis = True, False, False
                    oa = "X"
                elif y > x and y > z:
                    axis = False, True, False
                    oa = "Y"
                else:
                    axis = False, False, True
                    oa = "Z"

                if self.mode == "ROT":
                    bpy.ops.transform.rotate('INVOKE_DEFAULT', orient_axis=oa, orient_type=self.ot,
                                             orient_matrix=self.tm, orient_matrix_type=self.ot,
                                             constraint_axis=axis, mirror=True, use_proportional_edit=False,
                                             proportional_edit_falloff='SMOOTH', proportional_size=1,
                                             use_proportional_connected=False, use_proportional_projected=False)
                elif self.mode == "SCL":
                    bpy.ops.transform.resize('INVOKE_DEFAULT', orient_type=self.ot,
                                             orient_matrix=self.tm, orient_matrix_type=self.ot,
                                             constraint_axis=axis, mirror=True, use_proportional_edit=False,
                                             proportional_edit_falloff='SMOOTH', proportional_size=1,
                                             use_proportional_connected=False, use_proportional_projected=False)
                else:
                    bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=axis)

                return {'FINISHED'}

        elif event.type == 'ESC':
            # Justincase
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (VIEW3D_OT_ke_mouse_axis_move,
           )

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
