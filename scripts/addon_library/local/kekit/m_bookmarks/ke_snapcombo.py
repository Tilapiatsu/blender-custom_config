from bpy.props import StringProperty
from bpy.types import Operator
from .._utils import get_prefs


def get_snap_settings(context):
    ct = context.scene.tool_settings
    s1 = ""
    for i in ct.snap_elements:
        s1 = s1 + str(i) + ','
    s1 = s1[:-1]
    s2 = str(ct.snap_target)
    s3 = [bool(ct.use_snap_grid_absolute),
          bool(ct.use_snap_backface_culling),
          bool(ct.use_snap_align_rotation),
          bool(ct.use_snap_self),
          bool(ct.use_snap_project),
          bool(ct.use_snap_peel_object),
          bool(ct.use_snap_translate),
          bool(ct.use_snap_rotate),
          bool(ct.use_snap_scale)]
    return s1, s2, s3


def set_snap_settings(context, s1, s2, s3):
    ct = context.scene.tool_settings
    ct.snap_elements = s1
    ct.snap_target = s2
    ct.use_snap_grid_absolute = s3[0]
    ct.use_snap_backface_culling = s3[1]
    ct.use_snap_align_rotation = s3[2]
    ct.use_snap_self = s3[3]
    ct.use_snap_project = s3[4]
    ct.use_snap_peel_object = s3[5]
    ct.use_snap_translate = s3[6]
    ct.use_snap_rotate = s3[7]
    ct.use_snap_scale = s3[8]


class KeSnapCombo(Operator):
    bl_idname = "view3d.ke_snap_combo"
    bl_label = "Snapping Setting Combos"
    bl_description = "Store & Restore snapping settings. (Custom naming in keKit panel)"
    bl_options = {'REGISTER', "UNDO"}

    mode: StringProperty(default="SET1", options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        if "SET" in properties.mode:
            return "Recall stored snapping settings from slot" + properties.mode[-1]
        else:
            return "Store current snapping settings in slot %s" % properties.mode[-1]

    def execute(self, context):
        k = get_prefs()
        mode = self.mode[:3]
        slot = int(self.mode[3:])

        if mode == "GET":
            s1, s2, s3 = get_snap_settings(context)
            if slot == 1:
                k.snap_elements1 = s1
                k.snap_targets1 = s2
                k.snap_bools1 = s3
            elif slot == 2:
                k.snap_elements2 = s1
                k.snap_targets2 = s2
                k.snap_bools2 = s3
            elif slot == 3:
                k.snap_elements3 = s1
                k.snap_targets3 = s2
                k.snap_bools3 = s3
            elif slot == 4:
                k.snap_elements4 = s1
                k.snap_targets4 = s2
                k.snap_bools4 = s3
            elif slot == 5:
                k.snap_elements5 = s1
                k.snap_targets5 = s2
                k.snap_bools5 = s3
            else:
                k.snap_elements6 = s1
                k.snap_targets6 = s2
                k.snap_bools6 = s3

        elif mode == "SET":
            if slot == 1:
                c = k.snap_elements1
                s1 = set(c.split(","))
                s2 = k.snap_targets1
                s3 = k.snap_bools1
            elif slot == 2:
                c = k.snap_elements2
                s1 = set(c.split(","))
                s2 = k.snap_targets2
                s3 = k.snap_bools2
            elif slot == 3:
                c = k.snap_elements3
                s1 = set(c.split(","))
                s2 = k.snap_targets3
                s3 = k.snap_bools3
            elif slot == 4:
                c = k.snap_elements4
                s1 = set(c.split(","))
                s2 = k.snap_targets4
                s3 = k.snap_bools4
            elif slot == 5:
                c = k.snap_elements5
                s1 = set(c.split(","))
                s2 = k.snap_targets5
                s3 = k.snap_bools5
            else:
                c = k.snap_elements6
                s1 = set(c.split(","))
                s2 = k.snap_targets6
                s3 = k.snap_bools6

            set_snap_settings(context, s1, s2, s3)

            if k.combo_autosnap:
                context.scene.tool_settings.use_snap = True

        return {'FINISHED'}
