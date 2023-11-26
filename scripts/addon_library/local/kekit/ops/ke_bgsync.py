import bpy
from bpy.types import Operator


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
