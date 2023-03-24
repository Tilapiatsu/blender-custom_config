import bpy
from bpy.app.handlers import persistent
from sys import platform
from bpy.types import Panel, Operator
from ._prefs import pcoll


#
# MODULE UI
#
class UIRenderModule(Panel):
    bl_idname = "UI_PT_M_RENDER"
    bl_label = "Render"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_category = __package__
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        col = layout.column(align=True)
        hrow = col.row(align=True)
        hrow.scale_y = 0.25
        hrow.enabled = False
        hrow.label(text="Render")
        col.separator(factor=0.5)

        row = col.row(align=True)
        row.operator('screen.ke_render_visible', icon="RENDER_STILL", text="Render Visible")
        if k.renderslotcycle:
            row.prop(k, "renderslotcycle", text="", toggle=True, icon="CHECKMARK")
        else:
            row.prop(k, "renderslotcycle", text="", toggle=True, icon_value=pcoll['kekit']['ke_uncheck'].icon_id)

        row = col.row(align=True)
        row.operator('screen.ke_render_slotcycle', icon="RENDER_STILL", text="Render Slot Cycle")
        if k.renderslotfullwrap:
            row.prop(k, "renderslotfullwrap", text="", toggle=True, icon="CHECKMARK")
        else:
            row.prop(k, "renderslotfullwrap", text="", toggle=True, icon_value=pcoll['kekit']['ke_uncheck'].icon_id)

        row = col.row(align=True)
        row.operator('view3d.ke_bg_sync', icon="SHADING_TEXTURE")


#
# MODULE OPERATORS (MISC)
#
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
            # Grab visibility states & setup
            cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL',
                   'VOLUME', 'ARMATURE', 'EMPTY', 'LIGHT', 'LIGHT_PROBE'}
            self.objects = [o for o in context.scene.objects if o.type in cat]
            visible = [o for o in context.visible_objects if o.type in cat]
            self.og_states = [s.hide_render for s in self.objects]
            self.cycle = context.preferences.addons[__package__].preferences.renderslotcycle

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
            if self.stop or event.type == "ESC":
                if not context.scene.kekit_temp.is_rendering:
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
            full_wrap = bool(context.preferences.addons[__package__].preferences.renderslotfullwrap)
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


class KeBgSync(Operator):
    bl_idname = "view3d.ke_bg_sync"
    bl_label = "BG Sync"
    bl_description = "Set Viewport Preview Background EXR to Render Background EXR\n" \
                     "with rotation & strength values from VP"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        # prep
        using_bg, vp_is_bg, render_toggle = False, False, False
        n_in, n_out, zrot, strength, env_vector_in = None, None, None, None, None
        zrot_label = "ke_BG_ENV_ZRot"
        tc_label = "ke_BG_ENV_TC"

        #
        # CHECK VP
        #
        s_type = context.space_data.shading.type
        wr = context.space_data.shading.use_scene_world_render

        if s_type == 'RENDERED' and wr:
            s_type = 'MATERIAL'
            render_toggle = True

        if s_type == 'MATERIAL' or not wr:
            shading = context.space_data.shading
            vp_img = shading.studio_light
            vp_img_path = context.preferences.studio_lights[vp_img].path
            zrot = shading.studiolight_rotate_z
            strength = shading.studiolight_intensity
        else:
            self.report({"INFO"}, "BG Sync: Viewport not in Preview or Rendered mode")
            return {'CANCELLED'}

        #
        # CHECK CURRENT BG
        #
        if not context.scene.world.use_nodes:
            context.scene.world.use_nodes = True

        sw = context.scene.world
        nt = bpy.data.worlds[sw.name].node_tree
        n_in = nt.nodes['Background'].inputs['Color']

        bg = [n.from_node for n in n_in.links]
        if bg:
            using_bg = True
            if bg[0].image.name == vp_img:
                vp_is_bg = True
                env_vector_in = bg[0].inputs['Vector']
                if not bg[0].image.has_data:
                    bg[0].image.filepath = vp_img_path
                    bg[0].image.reload()
                # print("Env already connected!") # Update strength and rot only

        #
        # CHECK IF ENV IS LOADED
        #

        # 1st Check Unconnected Nodes
        if using_bg and not vp_is_bg:
            env_images = [n for n in nt.nodes if "ShaderNodeTexEnvironment" in n.bl_idname]
            if env_images:
                for e in env_images:
                    if e.image.name == vp_img:
                        n_out = e.outputs['Color']
                        env_vector_in = e.inputs['Vector']
                        if not e.image.has_data:
                            e.image.filepath = vp_img_path
                            e.image.reload()
                        break

        # 2nd, Check orphaned images
        if n_out is None and not vp_is_bg:
            n = []
            for i in bpy.data.images:
                if i.name == vp_img:
                    vp_img_path = i.name

                    if not i.has_data:
                        i.reload()

                    n = nt.nodes.new("ShaderNodeTexEnvironment")
                    n.image = i
                    n.image.filepath = vp_img_path
                    break

            # Or, 3rd load from disk
            if not n:
                n = nt.nodes.new("ShaderNodeTexEnvironment")
                n.image = bpy.data.images.load(vp_img_path)

            # Get links
            n_out = n.outputs['Color']
            env_vector_in = n.inputs['Vector']

        #
        # CHECK ZROT & TC NODE
        #
        zrot_node = [n for n in nt.nodes if "VectorRotate" in n.bl_idname and n.label == zrot_label]

        if not zrot_node:
            zrot_node = nt.nodes.new("ShaderNodeVectorRotate")
            zrot_node.label = zrot_label
        else:
            zrot_node = zrot_node[0]

        tc_node = [n for n in nt.nodes if "ShaderNodeTexCoord" in n.bl_idname and n.label == tc_label]

        if not tc_node:
            tc_node = nt.nodes.new("ShaderNodeTexCoord")
            tc_node.label = tc_label
        else:
            tc_node = tc_node[0]

        #
        # CONNECT LINKS & SET VALUES
        #
        if not vp_is_bg:
            # ENV link
            nt.links.new(n_out, n_in)

        # Zrot & tc links (Always, justincase)
        nt.links.new(tc_node.outputs['Generated'], zrot_node.inputs['Vector'])
        nt.links.new(zrot_node.outputs['Vector'], env_vector_in)

        # ADJUST STRENGTH AND ROT
        zrot_node.inputs["Angle"].default_value = zrot
        nt.nodes['Background'].inputs['Strength'].default_value = strength

        #
        # TIDY UP
        #
        offset_x = int(nt.nodes['Background'].location.x - 360)
        offset_y = int(nt.nodes['Background'].location.y)

        # Place env
        active_env = [n.from_node for n in n_in.links][0]
        active_env.location.x = offset_x
        active_env.location.y = offset_y

        # Removing unused env nodes (less purple issues)
        other_envs = [e for e in nt.nodes if "ShaderNodeTexEnvironment" in e.bl_idname and e != active_env]
        for e in other_envs:
            nt.nodes.remove(e)

        # Line up zrot & tc
        zrot_node.location.y = offset_y
        zrot_node.location.x = offset_x - 256
        tc_node.location.y = offset_y
        tc_node.location.x = offset_x - 460

        # "Excessively orderly"
        wo = [n for n in nt.nodes if "ShaderNodeOutputWorld" in n.bl_idname]
        if wo:
            wo[0].location.y = offset_y

        if render_toggle:
            context.space_data.shading.type = 'RENDERED'
        return {"FINISHED"}


#
# MODULE REGISTRATION
#
classes = (
    UIRenderModule,
    KeRenderVisible,
    KeRenderSlotCycle,
    KeBgSync,
)

modules = ()


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_render:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():
    if "bl_rna" in UIRenderModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
