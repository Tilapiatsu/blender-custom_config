# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Rotate an HDRI",
    "description": "",
    "author": "Alexander Belyakov",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}

import math

import bpy
import blf
import rna_keymap_ui
from bpy.types import SpaceView3D, Operator, AddonPreferences
from bpy.props import (
    IntProperty,
    FloatProperty,
    BoolProperty,
    FloatVectorProperty
)


MAT_PREVIEW_LIMIT_POS = 3.1415927410125732
MAT_PREVIEW_LIMIT_NEG = -3.1415927410125732
MAPPING_NODE_LIMIT = 6.2831854820251465


def draw_callback_px(self, context):
    addon_prefs = context.preferences.addons["rotate_an_hdri"].preferences
    if addon_prefs.show_angle:
        r, g, b, a = addon_prefs.text_color
        angle = get_hdri_rotation_angle(context)
        width = context.area.width
        font_id = 0
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 3, 0, 0, 0, 0.7)
        blf.shadow_offset(font_id, 2, -2)
        blf.color(font_id, r, g, b, a)
        blf.position(font_id, width / 2, 60, 0)
        blf.size(font_id, 30, addon_prefs.text_size)
        blf.draw(font_id, f"{(math.degrees(angle)):.1f}°")


def get_hdri_rotation_angle(context):
    shading = context.space_data.shading
    hdri = get_hdri(context)
    hdri_angle = 0
    if hdri == 'MAT_PREVIEW':
        current_angle_z = shading.studiolight_rotate_z
        if current_angle_z > 0:
            hdri_angle = abs(MAT_PREVIEW_LIMIT_POS - current_angle_z)
        else:
            hdri_angle = abs(MAT_PREVIEW_LIMIT_NEG + current_angle_z)
    elif hdri == 'NODE':
        mapping_node = get_mapping_node(context)
        if mapping_node:
            if (2, 80) == bpy.app.version[:2]:
                current_angle_z = mapping_node.rotation[2]
            else:
                current_angle_z = mapping_node.inputs[2].default_value[2]
            hdri_angle = MAPPING_NODE_LIMIT - current_angle_z
    return hdri_angle


def get_hdri(context):
    shading = context.space_data.shading
    scene = context.scene
    hdri = None
    if scene.render.engine != 'BLENDER_WORKBENCH':
        if (2, 80) == bpy.app.version[:2]:
            if shading.type == 'MATERIAL' and shading.use_scene_world:
                hdri = 'NODE'
            elif shading.type == 'RENDERED':
                hdri = 'NODE'
            else:
                if shading.type == 'MATERIAL':
                    hdri = 'MAT_PREVIEW'
        else:
            if shading.type == 'MATERIAL' and shading.use_scene_world:
                hdri = 'NODE'
            elif shading.type == 'RENDERED' and shading.use_scene_world_render:
                hdri = 'NODE'
            elif shading.type == 'MATERIAL'and not shading.use_scene_world:
                hdri = 'MAT_PREVIEW'
            elif (shading.type == 'RENDERED'
                  and not shading.use_scene_world_render):
                hdri = 'MAT_PREVIEW'
    return hdri


def get_mapping_node(context):
    node_tree = context.scene.world.node_tree
    mapping_node = node_tree.nodes.get("Mapping")
    return mapping_node


class RotateHDRI(Operator):
    bl_idname = "rotate.hdri"
    bl_label = "Rotate HDRI"
    bl_options = {'INTERNAL'}

    first_mouse_x: IntProperty()
    first_value: FloatProperty()

    def modal(self, context, event):
        addon_prefs = context.preferences.addons["rotate_an_hdri"].preferences
        shading = context.space_data.shading
        if event.type == 'MOUSEMOVE':
            hdri = get_hdri(context)
            delta = self.first_mouse_x - event.mouse_x
            rotation_speed = 0.001 * addon_prefs.rotation_speed
            if hdri == 'MAT_PREVIEW':
                hdri_angle = self.first_value
                if shading.studiolight_rotate_z == MAT_PREVIEW_LIMIT_NEG:
                    self.first_value = MAT_PREVIEW_LIMIT_POS
                    self.first_mouse_x = event.mouse_x
                if shading.studiolight_rotate_z == MAT_PREVIEW_LIMIT_POS:
                    self.first_value = MAT_PREVIEW_LIMIT_NEG
                    self.first_mouse_x = event.mouse_x
                shading.studiolight_rotate_z = (
                    hdri_angle + delta * rotation_speed)
            elif hdri == 'NODE':
                mapping_node = get_mapping_node(context)
                if mapping_node:
                    hdri_angle = self.first_value
                    z = 2
                    if (2, 80) == bpy.app.version[:2]:
                        current_angle = mapping_node.rotation
                    else:
                        current_angle = mapping_node.inputs[2].default_value
                    if current_angle[z] < 0:
                        self.first_value = MAPPING_NODE_LIMIT
                        self.first_mouse_x = event.mouse_x
                    if current_angle[z] > MAPPING_NODE_LIMIT:
                        self.first_value = 0
                        self.first_mouse_x = event.mouse_x
                    current_angle[z] = hdri_angle + delta * rotation_speed

        if event.type == 'LEFTMOUSE':
            SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        if event.type == 'RIGHTMOUSE':
            SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        if event.type == 'ESC':
            SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        shading = context.space_data.shading
        hdri = get_hdri(context)
        self.first_mouse_x = event.mouse_x
        if hdri == 'MAT_PREVIEW':
            self.first_value = shading.studiolight_rotate_z
        elif hdri == 'NODE':
            mapping_node = get_mapping_node(context)
            if mapping_node:
                if (2, 80) == bpy.app.version[:2]:
                    current_angle_z = mapping_node.rotation[2]
                else:
                    current_angle_z = mapping_node.inputs[2].default_value[2]
                self.first_value = current_angle_z

        args = (self, context)
        self._handle = SpaceView3D.draw_handler_add(
            draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def get_hotkey_entry_item(km, kmi_name):
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            return km_item
    return None


class AddonPreferences(AddonPreferences):
    bl_idname = __name__

    show_angle: BoolProperty(
        name="Show rotation angle in viewport",
        default=True,
    )

    text_size: IntProperty(
        name="Size",
        soft_min=1,
        soft_max=1000,
        default=60,
    )

    rotation_speed: IntProperty(
        soft_min=1,
        soft_max=100,
        default=10,
    )

    text_color: FloatVectorProperty(
        name="Text Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1, 1, 1, 1)
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "show_angle")
        split = box.split()

        col = split.column()
        col.label(text="Text Size:")
        col.label(text="Text Color:")
        col.label(text="Rotation Speed:")

        col = split.column()
        col.prop(self, "text_size", text="", slider=True)
        col.prop(self, "text_color", text="")
        col.prop(self, "rotation_speed", text="", slider=True)

        wm = context.window_manager
        box = layout.box()
        split = box.split()
        col = split.column()
        col.label(text='Hotkey')
        col.separator()
        kc = wm.keyconfigs.user
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'rotate.hdri')
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)


addon_keymaps = []


def register():
    bpy.utils.register_class(RotateHDRI)
    bpy.utils.register_class(AddonPreferences)

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(
            name='3D View',
            space_type='VIEW_3D'
        )
        kmi = km.keymap_items.new(
            'rotate.hdri',
            'LEFTMOUSE',
            'PRESS',
            ctrl=True,
            alt=True
        )
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(RotateHDRI)
    bpy.utils.unregister_class(AddonPreferences)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
