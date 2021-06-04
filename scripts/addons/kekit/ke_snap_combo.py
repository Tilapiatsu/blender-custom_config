bl_info = {
    "name": "kekit_snapcombo",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 3),
    "blender": (2, 80, 0),
}
import bpy
from bpy.types import Operator


class VIEW3D_OT_ke_snap_combo(Operator):
    bl_idname = "view3d.ke_snap_combo"
    bl_label = "Snapping Setting Combos"
    bl_description = "Store & Restore snapping settings. (Custom naming in keKit panel) Save kekit prefs!"
    bl_options = {'REGISTER', "UNDO"}

    mode: bpy.props.StringProperty(default="SET1", options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        if "SET" in properties.mode:
            return "Recall stored snapping settings from slot " + properties.mode[-1]
        else:
            return "Store current snapping settings in slot %s \n(Save kekit prefs!)" % properties.mode[-1]

    def get_snap_settings(self, context):
        s1 = ""
        for i in context.scene.tool_settings.snap_elements:
            s1 = s1 + str(i) + ','
        s1 = s1[:-1]
        s2 = str(context.scene.tool_settings.snap_target)
        s3 = [bool(context.scene.tool_settings.use_snap_grid_absolute),
              bool(context.scene.tool_settings.use_snap_backface_culling),
              bool(context.scene.tool_settings.use_snap_align_rotation),
              bool(context.scene.tool_settings.use_snap_self),
              bool(context.scene.tool_settings.use_snap_project),
              bool(context.scene.tool_settings.use_snap_peel_object),
              bool(context.scene.tool_settings.use_snap_translate),
              bool(context.scene.tool_settings.use_snap_rotate),
              bool(context.scene.tool_settings.use_snap_scale)]
        return s1, s2, s3

    def set_snap_settings(self, context, s1, s2, s3):
        context.scene.tool_settings.snap_elements = s1
        context.scene.tool_settings.snap_target = s2
        context.scene.tool_settings.use_snap_grid_absolute = s3[0]
        context.scene.tool_settings.use_snap_backface_culling = s3[1]
        context.scene.tool_settings.use_snap_align_rotation = s3[2]
        context.scene.tool_settings.use_snap_self = s3[3]
        context.scene.tool_settings.use_snap_project = s3[4]
        context.scene.tool_settings.use_snap_peel_object = s3[5]
        context.scene.tool_settings.use_snap_translate = s3[6]
        context.scene.tool_settings.use_snap_rotate = s3[7]
        context.scene.tool_settings.use_snap_scale = s3[8]

    def execute(self, context):
        mode = self.mode[:3]
        slot = int(self.mode[3:])

        if mode == "GET":
            s1, s2, s3 = self.get_snap_settings(context)
            if slot == 1:
                bpy.context.scene.kekit.snap_elements1 = s1
                bpy.context.scene.kekit.snap_targets1 = s2
                bpy.context.scene.kekit.snap_bools1 = s3
            elif slot == 2:
                bpy.context.scene.kekit.snap_elements2 = s1
                bpy.context.scene.kekit.snap_targets2 = s2
                bpy.context.scene.kekit.snap_bools2 = s3
            elif slot == 3:
                bpy.context.scene.kekit.snap_elements3 = s1
                bpy.context.scene.kekit.snap_targets3 = s2
                bpy.context.scene.kekit.snap_bools3 = s3
            elif slot == 4:
                bpy.context.scene.kekit.snap_elements4 = s1
                bpy.context.scene.kekit.snap_targets4 = s2
                bpy.context.scene.kekit.snap_bools4 = s3

        elif mode == "SET":
            if slot == 1:
                c = bpy.context.scene.kekit.snap_elements1
                s1 = set(c.split(","))
                s2 = bpy.context.scene.kekit.snap_targets1
                s3 = bpy.context.scene.kekit.snap_bools1
            elif slot == 2:
                c = bpy.context.scene.kekit.snap_elements2
                s1 = set(c.split(","))
                s2 = bpy.context.scene.kekit.snap_targets2
                s3 = bpy.context.scene.kekit.snap_bools2
            elif slot == 3:
                c = bpy.context.scene.kekit.snap_elements3
                s1 = set(c.split(","))
                s2 = bpy.context.scene.kekit.snap_targets3
                s3 = bpy.context.scene.kekit.snap_bools3
            elif slot == 4:
                c = bpy.context.scene.kekit.snap_elements4
                s1 = set(c.split(","))
                s2 = bpy.context.scene.kekit.snap_targets4
                s3 = bpy.context.scene.kekit.snap_bools4

            self.set_snap_settings(context, s1, s2, s3)

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_OT_ke_snap_combo)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_ke_snap_combo)

if __name__ == "__main__":
    register()
