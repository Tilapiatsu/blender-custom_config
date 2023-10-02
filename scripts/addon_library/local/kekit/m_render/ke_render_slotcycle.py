from sys import platform

import bpy
from bpy.app.handlers import persistent
from bpy.types import Operator
from .._utils import get_prefs


class KeRenderSlotCycle(Operator):
    bl_idname = "screen.ke_render_slotcycle"
    bl_label = "Render Image Slot Cycle"
    bl_description = "Render Image to the first empty render slot"
    bl_options = {'REGISTER'}

    @persistent
    def ke_init_render(self, scene, depsgraph):
        scene.kekit_temp.is_rendering = True
        # print("Render Starting")

    @persistent
    def ke_post_render(self, scene, depsgraph):
        scene.kekit_temp.is_rendering = False
        # print("Render Done")

    def execute(self, context):
        # Camera Check
        cam = [o for o in context.scene.objects if o.type == "CAMERA"]
        if not cam:
            self.report({'INFO'}, "No Cameras found?")
            return {"CANCELLED"}

        # Load Handlers
        handlers = [h.__name__ for h in bpy.app.handlers.render_post]
        handlers_active = True if [h == 'ke_post_render' for h in handlers] else False
        if not handlers_active:
            bpy.app.handlers.render_init.append(self.ke_init_render)
            bpy.app.handlers.render_post.append(self.ke_post_render)
            # print("keKit Render Handlers Loaded")

        # Check rendering status
        rendering = context.scene.kekit_temp.is_rendering

        if not rendering:
            k = get_prefs()
            full_wrap = bool(k.renderslotfullwrap)
            null = '/nul' if platform == 'win32' else '/dev/null'
            r = [i for i in bpy.data.images if i.name == 'Render Result']
            # Check & set active renderslot
            if r:
                r = r[0]
                if r.has_data:
                    # AFAICT Only possible hacky way to find 1st empty
                    current = int(r.render_slots.active_index)
                    total = len(r.render_slots)
                    step = 0
                    for i in range(total):
                        r.render_slots.active_index = step
                        try:
                            r.save_render(null)
                            step += 1
                        except RuntimeError:
                            break

                    if full_wrap and step == total:
                        if current < (total - 1):
                            r.render_slots.active_index = current + 1
                        else:
                            r.render_slots.active_index = 0
                            self.report({"INFO"}, "Render Slot Cycle FW: New cycle starting on slot 1")

                    else:
                        if step < total:
                            r.render_slots.active_index = step
                        else:
                            self.report({"WARNING"}, "Render Slot Cycle: All Render Slots are full!")
                            r.render_slots.active_index = current
                            return {"CANCELLED"}
                else:
                    r.render_slots.active_index = 0

            bpy.ops.render.render("INVOKE_DEFAULT", use_viewport=True)

        else:
            self.report({'INFO'}, "Not ready: Another render still in progress.")

        return {"FINISHED"}
