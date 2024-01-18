from bpy.props import StringProperty
from bpy.types import Operator
from .._utils import get_prefs


def get_snap_settings(context):
    ts = context.scene.tool_settings
    s1 = ""
    s4 = ""
    for i in ts.snap_elements_base:
        s1 += str(i) + ','
    s1 = s1[:-1]
    for i in ts.snap_elements_individual:
        s4 += str(i) + ','
    if not s4:
        s4 = "NONE"
    s2 = str(ts.snap_target)
    s3 = [bool(ts.use_snap_grid_absolute),
          bool(ts.use_snap_backface_culling),
          bool(ts.use_snap_align_rotation),
          bool(ts.use_snap_peel_object),
          bool(ts.use_snap_self),
          bool(ts.use_snap_edit),
          bool(ts.use_snap_nonedit),
          bool(ts.use_snap_selectable),
          bool(ts.use_snap_translate),
          bool(ts.use_snap_rotate),
          bool(ts.use_snap_scale),
          ]
    return s1, s2, s3, s4


def set_snap_settings(context, s1, s2, s3, s4):
    ts = context.scene.tool_settings
    if list(s4)[0] != "NONE":
        # set other set first (to whatever) to 'clear' ind-set...tbd: better method
        ts.snap_elements = {"INCREMENT"}
        if s4:
            ts.snap_elements_individual = set(s4)
    ts.snap_elements = s1
    ts.snap_target = s2
    ts.use_snap_grid_absolute = s3[0]
    ts.use_snap_backface_culling = s3[1]
    ts.use_snap_align_rotation = s3[2]
    ts.use_snap_peel_object = s3[3]
    ts.use_snap_self = s3[4]
    ts.use_snap_edit = s3[5]
    ts.use_snap_nonedit = s3[6]
    ts.use_snap_selectable = s3[7]
    ts.use_snap_translate = s3[8]
    ts.use_snap_rotate = s3[9]
    ts.use_snap_scale = s3[10]


def clean_set(prop):
    s = set(prop.split(","))
    if s:
        ns = []
        for i in s:
            if i:
                ns.append(i)
        s = set(ns)
    return s


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
            s1, s2, s3, s4 = get_snap_settings(context)
            if slot == 1:
                k.snap_elements1 = s1
                k.snap_elements_ind1 = s4
                k.snap_targets1 = s2
                k.snap_bools1 = s3
            elif slot == 2:
                k.snap_elements2 = s1
                k.snap_elements_ind2 = s4
                k.snap_targets2 = s2
                k.snap_bools2 = s3
            elif slot == 3:
                k.snap_elements3 = s1
                k.snap_elements_ind3 = s4
                k.snap_targets3 = s2
                k.snap_bools3 = s3
            elif slot == 4:
                k.snap_elements4 = s1
                k.snap_elements_ind4 = s4
                k.snap_targets4 = s2
                k.snap_bools4 = s3
            elif slot == 5:
                k.snap_elements5 = s1
                k.snap_elements_ind5 = s4
                k.snap_targets5 = s2
                k.snap_bools5 = s3
            else:
                k.snap_elements6 = s1
                k.snap_elements_ind6 = s4
                k.snap_targets6 = s2
                k.snap_bools6 = s3

        elif mode == "SET":
            if slot == 1:
                s1 = clean_set(k.snap_elements1)
                s4 = clean_set(k.snap_elements_ind1)
                s2 = k.snap_targets1
                s3 = k.snap_bools1
            elif slot == 2:
                s1 = clean_set(k.snap_elements2)
                s4 = clean_set(k.snap_elements_ind2)
                s2 = k.snap_targets2
                s3 = k.snap_bools2
            elif slot == 3:
                s1 = clean_set(k.snap_elements3)
                s4 = clean_set(k.snap_elements_ind3)
                s2 = k.snap_targets3
                s3 = k.snap_bools3
            elif slot == 4:
                s1 = clean_set(k.snap_elements4)
                s4 = clean_set(k.snap_elements_ind4)
                s2 = k.snap_targets4
                s3 = k.snap_bools4
            elif slot == 5:
                s1 = clean_set(k.snap_elements5)
                s4 = clean_set(k.snap_elements_ind5)
                s2 = k.snap_targets5
                s3 = k.snap_bools5
            else:
                s1 = clean_set(k.snap_elements6)
                s4 = clean_set(k.snap_elements_ind6)
                s2 = k.snap_targets6
                s3 = k.snap_bools6

            set_snap_settings(context, s1, s2, s3, s4)

            if k.combo_autosnap:
                context.scene.tool_settings.use_snap = True

        return {'FINISHED'}
