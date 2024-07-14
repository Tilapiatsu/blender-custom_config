import numpy as np
from bpy.props import BoolProperty
from bpy.types import Operator
from mathutils import Vector
from .._utils import get_override_by_type

def travel_back_nodes(node_in):
    found = []

    def recur(n):
        for n_inputs in n.inputs:
            for node_links in n_inputs.links:
                found.append(node_links.from_node)
                recur(node_links.from_node)

    recur(node_in)
    return found


def has_rgb_img(nodes):
    for n in nodes:
        if "ShaderNodeTexImage" in str(type(n)):
            if n.image is not None:
                if n.image.colorspace_settings.name == "sRGB":
                    return n.image


def find_texture_average(c):
    # Find RGB Texture (if used in node tree)
    first = c.links[0].from_node
    img = has_rgb_img([first])
    if img is None:
        nodes = travel_back_nodes(first)
        img = has_rgb_img(nodes)
    if img is not None:
        x, y = img.size[0], img.size[1]
        if x > 32:
            step = int(x / 32)
        else:
            step = x
        alpha_tolerance = 0.95
        vsn = 0.000001
        # GRAB PIXEL DATA
        src = np.empty(x * y * 4, dtype=np.float32)
        img.pixels.foreach_get(src)
        src = np.reshape(src, (x, y, 4))
        # Very fast (& rough!) integer downscale
        src = src[::step, ::step]
        # ONLY USE PIXELS *WITH* ALPHA (0-alpha colors usually "bad" average)
        rgba = np.reshape(src, (-1, 4))
        alpha_mask = np.where(rgba[:, 3] > alpha_tolerance, 1, 0)
        rgba = rgba[alpha_mask == 1]
        rgb = rgba[:, :-1]
        avg = np.average(rgb, axis=0)
        # sRGB Gamma haxxors & add an alpha element for vp col
        avg = [(((i * i) + vsn) / 0.4546) * 0.4546 for i in avg] + [1.0]
        return avg


def update_vpshading(m):
    shader = None
    is_set = False
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type != "OUTPUT_MATERIAL":
                shader = n
                break
    # Grab Active Material values
    if shader is not None:
        m_node_c, m_node_m, m_node_r = None, None, None
        m_node_c = Vector(shader.inputs[0].default_value)
        # Check if sRGB texture is used
        c = shader.inputs[0]
        if c.is_linked:
            avgc = find_texture_average(c)
            if avgc is not None:
                m_node_c = avgc
        # Check rgb box values
        st = shader.type
        if st == "BSDF_PRINCIPLED":
            m_node_m = float(shader.inputs[6].default_value)
            m_node_r = float(shader.inputs[9].default_value)
        elif st in {"BSDF_GLASS", "BSDF_ANISOTROPIC", "BSDF_DIFFUSE", "BSDF_GLOSSY", "BSDF_REFRACTION"}:
            m_node_r = float(shader.inputs[1].default_value)
        elif st == "EEVEE_SPECULAR":
            m_node_r = float(shader.inputs[2].default_value)
        # Apply to Viewport shading
        if m_node_c is not None:
            m.diffuse_color = m_node_c
            is_set = True
        if m_node_m is not None:
            m.metallic = m_node_m
        if m_node_r is not None:
            m.roughness = m_node_r
    return is_set


class KeSyncviewportMaterial(Operator):
    bl_idname = "view3d.ke_syncvpmaterial"
    bl_label = "Sync Material & Viewport"
    bl_description = "Synd BSDF Color (and Roughness & Metallic, if applicable) to Viewport Display"
    bl_options = {'REGISTER', 'UNDO'}

    active_only: BoolProperty(default=True, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_material

    def execute(self, context):
        context.object.select_set(True)
        context.view_layer.objects.active = context.object
        vp_set = False

        if self.active_only:
            vp_set = update_vpshading(context.object.active_material)
        else:
            sel_obj = context.selected_objects
            for obj in sel_obj:
                for slot in obj.material_slots:
                    vp_set = update_vpshading(slot.material)

        if vp_set:
            w, a, r = get_override_by_type()
            with context.temp_override(window=w, area=a, region=r):
                context.space_data.shading.color_type = 'MATERIAL'

        return {"FINISHED"}
