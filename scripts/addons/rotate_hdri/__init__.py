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
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}


import bpy
import blf
import math
import rna_keymap_ui
from bpy.props import IntProperty, FloatProperty, BoolProperty


def get_angle(context):
    shading = context.space_data.shading
    if shading.type == 'MATERIAL' and shading.use_scene_world is False:
        hdri_angle = shading.studiolight_rotate_z
        return hdri_angle
    else:
        mapping_node = get_world_mapping_node(context)
        if mapping_node:
            hdri_angle = mapping_node.rotation[2]
            return hdri_angle


def draw_callback_px(self, context):
    addon_prefs = context.preferences.addons["rotate_hdri"].preferences
    if addon_prefs.show_angle:

        width = context.area.width
        font_id = 0
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 3, 0, 0, 0, 0.7)
        blf.shadow_offset(font_id, 2, -2)
        blf.color(font_id, 1, 1, 1, 1)
        blf.position(font_id, width / 2, 60, 0)
        blf.size(font_id, 30, addon_prefs.text_size)
        blf.draw(font_id, str(int(math.degrees(get_angle(context)))) + "°")


def get_world_mapping_node(context):
    world = context.scene.world
    if world:
        world_nodes = world.node_tree.nodes
        mapping_node = world_nodes.get("Mapping")
        if mapping_node:
            return mapping_node


class RotateHDRI(bpy.types.Operator):
    bl_idname = "rotate.hdri"
    bl_label = "Rotate HDRI"

    first_mouse_x: IntProperty()
    first_value: FloatProperty()

    def modal(self, context, event):
        shading = context.space_data.shading
        mapping_node = get_world_mapping_node(context)
        if event.type == 'MOUSEMOVE':
            if shading.type == 'MATERIAL' and shading.use_scene_world is False:
                hdri_angle = shading.studiolight_rotate_z
                hdri_angle = self.first_value
                delta = self.first_mouse_x - event.mouse_x
                shading.studiolight_rotate_z = hdri_angle + delta * 0.01
            else:
                if mapping_node:
                    hdri_angle = mapping_node.rotation[2]
                    hdri_angle = self.first_value
                    delta = self.first_mouse_x - event.mouse_x
                    mapping_node.rotation[2] = hdri_angle + delta * 0.01
        if event.type == 'LEFTMOUSE' or 'RIGHTMOUSE' and event.value == "RELEASE":
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            shading = context.space_data.shading
            if shading.type == 'MATERIAL' and shading.use_scene_world is False:
                self.first_mouse_x = event.mouse_x
                self.first_value = shading.studiolight_rotate_z
            else:
                mapping_node = get_world_mapping_node(context)
                if mapping_node:
                    self.first_mouse_x = event.mouse_x
                    self.first_value = mapping_node.rotation[2]

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}


def get_hotkey_entry_item(km, kmi_name):
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            return km_item
    return None


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    show_angle: BoolProperty(
        name="Show angle",
        description="Show angle in Viewport",
        default=True,
    )

    text_size: IntProperty(
        soft_min=1,
        soft_max=2000,
        default=60,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.prop(self, "show_angle", text="Show angle in Viewport")
        row.prop(self, "text_size", text="Text size")

        wm = bpy.context.window_manager
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
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('rotate.hdri', 'LEFTMOUSE', 'PRESS', ctrl=True, alt=True)
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
