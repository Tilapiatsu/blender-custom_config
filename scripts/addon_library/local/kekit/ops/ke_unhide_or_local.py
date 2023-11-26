import bpy
from bpy.types import Operator


class KeUnhideOrLocal(Operator):
    bl_idname = "view3d.ke_unhide_or_local"
    bl_label = "Unhide or Local Off"
    bl_description = "Unhides hidden items OR toggles Local mode OFF, if currently in Local mode" \
                     "\n(Compatible with Zero Local)"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        # fallback for deleting visible context object when hidden objects in scene
        if not context.object:
            hidden = []
            for o in context.scene.objects:
                if o.hide_viewport:
                    hidden.append(o)
            if hidden:
                for o in hidden:
                    o.select_set(True)

        if context.space_data.local_view:
            keys = []
            if context.object is not None:
                keys = context.object.keys()
            if "ZeroLocal" in keys:
                bpy.ops.view3d.ke_zerolocal()
            else:
                bpy.ops.view3d.localview(frame_selected=False)
        else:
            bpy.ops.object.hide_view_clear(select=False)
        return {"FINISHED"}
