bl_info = {
    "name": "keFrameView",
    "author": "Kjell Emanuelsson",
    "version": (0, 0, 1),
    "blender": (2, 9, 0),
    "description": "Frame All or Selected",
}

import bpy


class SCREEN_OT_ke_frame_view(bpy.types.Operator):
    bl_idname = "screen.ke_frame_view"
    bl_label = "Frame All or Selected"
    bl_description = "Frame Selection, or everything if nothing is selected."
    bl_options = {'REGISTER'}

    # for now
    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):

        # print("Current Space:", context.space_data.type)
        # todo: Rework for all the contexts
        # GRAPH_EDITOR, DOPESHEET_EDITOR, VIEW_3D, NODE_EDITOR

        sel_mode = bpy.context.mode
        sel_obj =  [o for o in context.selected_objects]
        active = [context.active_object]

        if sel_mode == "OBJECT":
            if active and sel_obj:
                bpy.ops.view3d.view_selected('INVOKE_DEFAULT', use_all_regions=False)
            else:
                bpy.ops.view3d.view_all('INVOKE_DEFAULT', center=True)

        elif sel_mode == "POSE":
            if context.selected_bones or context.selected_pose_bones_from_active_object:
                bpy.ops.view3d.view_selected('INVOKE_DEFAULT', use_all_regions=False)
            else:
                bpy.ops.view3d.view_all('INVOKE_DEFAULT', center=True)

        elif sel_mode in {"EDIT_MESH", "EDIT_CURVE", "EDIT_SURFACE"}:
            if not sel_obj and active:
                sel_obj = active

            sel_check = False

            for o in sel_obj:
                o.update_from_editmode()

                if o.type == "MESH":
                    for v in o.data.vertices:
                        if v.select:
                            sel_check = True
                            break

                elif o.type == "CURVE":
                    for sp in o.data.splines:
                        for cp in sp.bezier_points:
                            if cp.select_control_point:
                                sel_check = True
                                break

                elif o.type == "SURFACE":
                    for sp in o.data.splines:
                        for cp in sp.points:
                            if cp.select:
                                sel_check = True
                                break

            if sel_check:
                bpy.ops.view3d.view_selected('INVOKE_DEFAULT', use_all_regions=False)
            else:
                bpy.ops.view3d.view_all('INVOKE_DEFAULT', center=True)

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
def register():
    bpy.utils.register_class(SCREEN_OT_ke_frame_view)

def unregister():
    bpy.utils.unregister_class(SCREEN_OT_ke_frame_view)

if __name__ == "__main__":
    register()
