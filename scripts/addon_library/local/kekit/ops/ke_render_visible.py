import bpy
from bpy.app.handlers import persistent
from bpy.types import Operator
from .._utils import get_prefs


class KeRenderVisible(Operator):
    bl_idname = "screen.ke_render_visible"
    bl_label = "Render Visible"
    bl_description = "Render only what is currently visible in the viewport - Regardless of outliner settings"
    bl_options = {'REGISTER'}

    _timer = None
    stop = False
    objects = []
    og_states = []
    cycle = False

    @persistent
    def ke_init_render(self, scene, depsgraph):
        bpy.context.window_manager.kekit_temp_session.qm_running = True
        # print("Render Starting")

    @persistent
    def ke_post_render(self, scene, depsgraph):
        bpy.context.window_manager.kekit_temp_session.qm_running = False
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
        rendering = context.window_manager.kekit_temp_session.qm_running

        if not rendering:
            # Grab visibility states & setup
            cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL',
                   'VOLUME', 'ARMATURE', 'EMPTY', 'LIGHT', 'LIGHT_PROBE'}
            self.objects = [o for o in context.scene.objects if o.type in cat]
            visible = [o for o in context.visible_objects if o.type in cat]
            self.og_states = [s.hide_render for s in self.objects]

            k = get_prefs()
            self.cycle = k.renderslotcycle

            for o in self.objects:
                o.hide_render = True
            for o in visible:
                o.hide_render = False

            # # Running Modal timer hack, so we can see render progress...
            self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            return {"CANCELLED"}

    def modal(self, context, event):
        if event.type == 'TIMER':
            print(context.window_manager.kekit_temp_session.qm_running)
            if self.stop or event.type == "ESC":
                if not context.window_manager.kekit_temp_session.qm_running:
                    # remove timer
                    context.window_manager.event_timer_remove(self._timer)
                    # restore visibility states
                    for o, s in zip(self.objects, self.og_states):
                        o.hide_render = s
                    return {"FINISHED"}

            elif not self.stop:
                if self.cycle:
                    status = bpy.ops.screen.ke_render_slotcycle("INVOKE_DEFAULT")
                    if status == {"CANCELLED"}:
                        self.report({"WARNING"}, "SC: All Render Slots are full!")
                else:
                    bpy.ops.render.render("INVOKE_DEFAULT")
                self.stop = True

        return {"PASS_THROUGH"}
