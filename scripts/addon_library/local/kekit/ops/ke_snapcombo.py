import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from .._utils import get_prefs

# >= 4.2 ref lists
snap_elements = [
    'INCREMENT', 'GRID', 'VOLUME', 'FACE_NEAREST', 'FACE', 'EDGE_PERPENDICULAR', 'EDGE_MIDPOINT', 'FACE_PROJECT',
    'VERTEX', 'EDGE'
]
snap_target = ['ACTIVE', 'CENTER', 'CLOSEST', 'MEDIAN']

snap_floats = [
    'snap_angle_increment_2d',
    'snap_angle_increment_2d_precision',
    'snap_angle_increment_3d',
    'snap_angle_increment_3d_precision',
]
snap_ints = [
    'snap_face_nearest_steps',
]
snap_sets = [
    'snap_elements',
]
snap_strings = [
    'snap_target',
]
snap_bools = [
    'use_snap_align_rotation',
    'use_snap_backface_culling',
    'use_snap_edit',
    'use_snap_nonedit',
    'use_snap_peel_object',
    'use_snap_rotate',
    'use_snap_scale',
    'use_snap_selectable',
    'use_snap_self',
    'use_snap_to_same_target',
    'use_snap_translate',
]


# old  (< 4.2) funcs
def get_snap_settings(context):
    ts = context.scene.tool_settings
    s1 = ""
    s4 = ""
    if bpy.app.version < (4, 0):
        for i in ts.snap_elements:
            s1 = s1 + str(i) + ','
        s1 = s1[:-1]
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
              bool(ts.use_snap_project),  # 3.6 LTS
              False,  # placeholders
              False,
              ]
        s2 = str(ts.snap_target)
    else:
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
              False,  # placeholders
              False,
              False,
              ]
    return s1, s2, s3, s4


def set_snap_settings(context, s1, s2, s3, s4):
    ts = context.scene.tool_settings
    if bpy.app.version < (4, 0):
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
        ts.use_snap_project = s3[11]  # 3.6 LTS, changed in 4.0

    else:
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

        if bpy.app.version >= (4, 2):
            # Storing all values as floats (for simpler prop storage)
            # to use as-is, or bool'd against element-lists, or just bool'd
            kprop = k.__getattribute__("snap_combo" + str(slot))
            ts = context.scene.tool_settings

            if mode == "GET":
                # Store Nrs
                offset = 0
                for idx, item in enumerate(snap_floats + snap_ints):
                    kprop[idx] = float(ts.__getattribute__(item))
                    offset += 1

                # Store sets
                next_offset = 0
                for idx, item in enumerate(snap_elements):
                    idx += offset
                    if item in list(ts.snap_elements):
                        kprop[idx] = 1.0
                    else:
                        kprop[idx] = 0.0
                    next_offset += 1

                offset += next_offset

                # Store string (enum)
                next_offset = 0
                for idx, item in enumerate(snap_target):
                    idx += offset
                    if ts.snap_target == item:
                        kprop[idx] = 1.0
                    else:
                        kprop[idx] = 0.0
                    next_offset += 1

                offset += next_offset

                # Store bools
                for idx, item in enumerate(snap_bools):
                    idx += offset
                    kprop[idx] = float(ts.__getattribute__(item))

                # Prevent data loss! :
                bpy.ops.wm.save_userpref()

            elif mode == "SET":
                # Store Nrs
                floats_vals = kprop[:4]
                int_val = int(kprop[4])
                # bool remaining
                bool_defaults = [bool(int(e)) for e in kprop]
                elements_comp = bool_defaults[5:15]
                target_comp = bool_defaults[15:19]
                bool_comp = bool_defaults[19:]

                # RECONSTRUCT & COMPARE THINGS
                # Nrs:
                for val, i in zip(floats_vals, snap_floats):
                    ts.__setattr__(i, val)
                ts.__setattr__(snap_ints[0], int_val)

                # Element-Sets
                restored_set = set()
                for b, i in zip(elements_comp, snap_elements):
                    if b:
                        restored_set.add(i)
                ts.__setattr__(snap_sets[0], restored_set)

                # Target Enum-String
                restored_str = "ACTIVE"
                for b, i in zip(target_comp, snap_target):
                    if b:
                        restored_str = i
                ts.__setattr__(snap_strings[0], restored_str)

                # Bools
                for b, i in zip(bool_comp, snap_bools):
                    ts.__setattr__(i, b)

        else:
            # These are the old (pre 4.2) methods, kept for backwards-compatibility

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
                # need to save here...
                bpy.ops.wm.save_userpref()

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
