from bpy.types import Operator
from mathutils import Vector


class KeSyncviewportMaterial(Operator):
    bl_idname = "view3d.ke_syncvpmaterial"
    bl_label = "Sync to Viewport Display"
    bl_description = "Synd BSDF Color (and Roughness & Metallic, if applicable) to Viewport Display"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        # Get Active Material / Node
        am = context.object.active_material
        shader = None
        if am.use_nodes:
            for n in am.node_tree.nodes:
                if n.type != "OUTPUT_MATERIAL":
                    shader = n
                    break

        # Grab Active Material values
        if shader is not None:
            am_node_c, am_node_m, am_node_r = None, None, None
            st = shader.type
            am_node_c = Vector(shader.inputs[0].default_value)
            if st == "BSDF_PRINCIPLED":
                am_node_m = float(shader.inputs[6].default_value)
                am_node_r = float(shader.inputs[9].default_value)
            elif st in {"BSDF_GLASS", "BSDF_ANISOTROPIC", "BSDF_DIFFUSE", "BSDF_GLOSSY", "BSDF_REFRACTION"}:
                am_node_r = float(shader.inputs[1].default_value)
            elif st == "EEVEE_SPECULAR":
                am_node_r = float(shader.inputs[2].default_value)

            # Apply to Viewport shading
            if am_node_c is not None:
                am.diffuse_color = am_node_c
            if am_node_m is not None:
                am.metallic = am_node_m
            if am_node_r is not None:
                am.roughness = am_node_r

        return {"FINISHED"}
