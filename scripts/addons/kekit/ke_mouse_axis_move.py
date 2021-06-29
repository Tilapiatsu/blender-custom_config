bl_info = {
    "name": "keMouseAxisMove",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 1, 2),
    "blender": (2, 80, 0),
}

import bpy
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import region_2d_to_location_3d
from .ke_utils import getset_transform, restore_transform, average_vector


class VIEW3D_OT_ke_mouse_axis_move(bpy.types.Operator):
    bl_idname = "view3d.ke_mouse_axis_move"
    bl_label = "Mouse Axis Move"
    bl_description = "Runs Grab with Axis auto-locked based on your mouse movement (or viewport when rot) using recalculated orientation " \
                     "based on the selected Orientation type."
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[("MOVE", "Move", "", 1),
               ("DUPE", "Duplicate", "", 2),
               ("ROT", "Rotate", "", 3),
               ("SCL", "Resize", "", 4),
               ("CURSOR", "Cursor", "", 5)
               ],
        name="Mode",
        default="MOVE")

    mouse_pos = Vector((0, 0))
    startpos = Vector((0, 0, 0))
    tm = Matrix().to_3x3()
    rv = None
    ot = "GLOBAL"
    obj = None
    obj_loc = None
    em_types = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "DUPE":
            return "Duplicates mesh/object before running Mouse Axis Move"
        elif properties.mode == "CURSOR":
            return "Mouse Axis Move for the Cursor. Global orientation or Cursor orientation (used in all modes except Global)"
        else:
            return "Runs Grab, Rotate or Resize with Axis auto-locked based on your mouse movement (or viewport when Rot) " \
                   "using recalculated orientation based on the selected Orientation type."

    # @classmethod
    # def poll(cls, context):
    #     return context.object is not None

    @classmethod
    def get_mpos(cls, context, coord, pos):
        region = context.region
        rv3d = context.region_data
        return region_2d_to_location_3d(region, rv3d, coord, pos)

    def invoke(self, context, event):
        sel_obj = [o for o in context.selected_objects]
        if sel_obj:
            if len(sel_obj) > 1:
                self.obj_loc = average_vector([o.location for o in sel_obj])
            else:
                self.obj_loc = sel_obj[0].location
        else:
            self.report({"INFO"}, " No objects selected ")
            return {'CANCELLED'}

        if sel_obj and context.object is None:
            self.obj = sel_obj[0]
            for o in sel_obj:
                if o.type in self.em_types:
                    self.obj = o
                    break

        elif context.object is not None:
            self.obj = context.object
        else:
            self.report({"INFO"}, " No valid objects selected ")
            return {'CANCELLED'}


        # mouse track start
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)

        # Mouse vec start
        if self.mode != "ROT":
            self.startpos = self.get_mpos(context, self.mouse_pos, self.obj_loc)

        # get rotation vectors
        og = getset_transform(setglobal=False)
        self.ot = og[0]

        if self.mode == "CURSOR":
            if og[0] == "GLOBAL":
                pass
            else:
                og[0] = "CURSOR"
                self.tm = context.scene.cursor.matrix.to_3x3()

        else:
            # check type
            if self.obj.type in self.em_types and bool(self.obj.data.is_editmode):
                em = True
            else:
                em = "OBJECT"

            if og[0] == "GLOBAL":
                pass

            elif og[0] == "CURSOR":
                self.tm = context.scene.cursor.matrix.to_3x3()

            elif og[0] == "LOCAL" or og[0] == "NORMAL" and not em:
                self.tm = self.obj.matrix_world.to_3x3()

            elif og[0] == "VIEW":
                self.tm = context.space_data.region_3d.view_matrix.inverted().to_3x3()

            elif og[0] == "GIMBAL":
                self.report({"INFO"}, "Gimbal Orientation not supported")
                return {'CANCELLED'}

            # NORMAL / SELECTION
            elif em != "OBJECT":
                self.obj.update_from_editmode()
                sel = [v for v in self.obj.data.vertices if v.select]
                if sel:
                    try:
                        bpy.ops.transform.create_orientation(name='keTF', use_view=False, use=True, overwrite=True)
                        self.tm = context.scene.transform_orientation_slots[0].custom_orientation.matrix.copy()
                        bpy.ops.transform.delete_orientation()
                        restore_transform(og)
                    except RuntimeError:
                        print("Fallback: Invalid selection for Orientation - Using Local")
                        # Normal O. with a entire cube selected will fail create_o.
                        bpy.ops.transform.select_orientation(orientation='LOCAL')
                        self.tm = self.obj.matrix_world.to_3x3()
                else:
                    self.report({"INFO"}, " No elements selected ")
                    return {'CANCELLED'}
            else:
                self.report({"INFO"}, "Unsupported Orientation Mode")
                return {'CANCELLED'}

            if self.mode == "DUPE":
                if em != "OBJECT":
                    bpy.ops.mesh.duplicate('INVOKE_DEFAULT')
                else:
                    if bpy.context.scene.kekit.tt_linkdupe:
                        bpy.ops.object.duplicate('INVOKE_DEFAULT', linked=True)
                    else:
                        bpy.ops.object.duplicate('INVOKE_DEFAULT', linked=False)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            # mouse track end candidate
            new_mouse_pos = Vector((int(event.mouse_region_x), int(event.mouse_region_y)))
            t1 = abs(new_mouse_pos[0] - self.mouse_pos[0])
            t2 = abs(new_mouse_pos[1] - self.mouse_pos[1])

            if t1 > 10 or t2 > 10 or self.mode == "ROT":

                if self.mode == "ROT":
                    # no need to track mouse vec
                    rm = context.space_data.region_3d.view_matrix
                    v = self.tm.inverted() @ Vector(rm[2]).to_3d()
                    x, y, z = abs(v[0]), abs(v[1]), abs(v[2])

                else:
                    # mouse vec end
                    newpos = self.get_mpos(context, new_mouse_pos, self.obj_loc)
                    v = self.tm.inverted() @ Vector(self.startpos - newpos).normalized()
                    x, y, z = abs(v[0]), abs(v[1]), abs(v[2])

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

                elif self.mode == "CURSOR":
                    bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type=self.ot, orient_matrix_type=self.ot,
                                                constraint_axis=axis, mirror=True, use_proportional_edit=False,
                                                proportional_edit_falloff='SMOOTH', cursor_transform=True,
                                                use_proportional_connected=False, use_proportional_projected=False)
                else:
                    bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type=self.ot, orient_matrix_type=self.ot,
                                                constraint_axis=axis, mirror=True, use_proportional_edit=False,
                                                proportional_edit_falloff='SMOOTH', proportional_size=1,
                                                use_proportional_connected=False, use_proportional_projected=False)

                return {'FINISHED'}

        elif event.type == 'ESC':
            # Justincase
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_OT_ke_mouse_axis_move)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_ke_mouse_axis_move)

if __name__ == "__main__":
    register()
