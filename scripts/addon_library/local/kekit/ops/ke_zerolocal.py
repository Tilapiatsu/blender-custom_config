from math import pi

import bpy
from bpy.types import Operator


class KeZeroLocal(Operator):
    bl_idname = "view3d.ke_zerolocal"
    bl_label = "Zero Local"
    bl_description = "Temporarily stores & zeroes Loc+Rot & sets Local View. " \
                     "\nRun ZeroLocal again to exit Local View & restore rotation" \
                     "\n+If no rot/loc -> just Local View"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D" and context.object

    def execute(self, context):
        obj = context.object
        in_local_view = bool(context.space_data.local_view)
        stored_rot = True if "ZeroLocalRot" in obj.keys() else False
        stored_loc = True if "ZeroLocalLoc" in obj.keys() else False

        if not in_local_view and any((stored_loc, stored_rot)):
            self.report({"INFO"}, "Not in Local View but has stored values: Copy/Remove manually (Custom Prop)")
            print("Zero Local: Likely exited Local View without using Zero Local"
                  "\nValues can be found in Object Properties / Custom Properties\nfor manual restoration/removal")
            return {"CANCELLED"}

        if not in_local_view:
            # Store Rotation
            rads = obj.rotation_euler
            pos = obj.location
            if sum(rads) != 0:
                # Store degs for easier manual fix (just copy-paste to rot) should something go wrong...
                degs = (rads[0] * 180 / pi, rads[1] * 180 / pi, rads[2] * 180 / pi)
                obj['ZeroLocalRot'] = degs
                obj.rotation_euler = (0, 0, 0)
            if sum(pos) != 0:
                obj['ZeroLocalLoc'] = pos
                obj.location = (0, 0, 0)

        elif in_local_view:
            if stored_rot:
                # Restore Rotation
                rads = obj['ZeroLocalRot']
                re_rads = (rads[0] * pi / 180, rads[1] * pi / 180, rads[2] * pi / 180)
                obj.rotation_euler = re_rads
                del obj['ZeroLocalRot']
            if stored_loc:
                obj.location = obj['ZeroLocalLoc']
                del obj['ZeroLocalLoc']

        bpy.ops.view3d.localview(frame_selected=False)

        return {"FINISHED"}
