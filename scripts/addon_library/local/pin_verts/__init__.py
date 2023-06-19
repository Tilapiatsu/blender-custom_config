# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Pin Verts",
    "author" : "Corza", 
    "description" : "",
    "blender" : (3, 0, 0),
    "version" : (2, 0, 0),
    "location" : "",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "3D View" 
}


import bpy
import bpy.utils.previews
from mathutils import Vector
import gpu
import gpu_extras


addon_keymaps = {}
_icons = None
handler_FD27A = []


def find_user_keyconfig(key):
    km, kmi = addon_keymaps[key]
    for item in bpy.context.window_manager.keyconfigs.user.keymaps[km.name].keymap_items:
        found_item = False
        if kmi.idname == item.idname:
            found_item = True
            for name in dir(kmi.properties):
                if not name in ["bl_rna", "rna_type"] and not name[0] == "_":
                    if name in kmi.properties and name in item.properties and not kmi.properties[name] == item.properties[name]:
                        found_item = False
        if found_item:
            return item
    print(f"Couldn't find keymap item for {key}, using addon keymap instead. This won't be saved across sessions!")
    return kmi


_5F468_running = False
class SNA_OT_Modal_Operator_5F468(bpy.types.Operator):
    bl_idname = "sna.modal_operator_5f468"
    bl_label = "Modal Operator"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    cursor = "CROSSHAIR"
    _handle = None
    _event = {}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        if not False or context.area.spaces[0].bl_rna.identifier == 'SpaceView3D':
            return not False
        return False

    def save_event(self, event):
        event_options = ["type", "value", "alt", "shift", "ctrl", "oskey", "mouse_region_x", "mouse_region_y", "mouse_x", "mouse_y", "pressure", "tilt"]
        if bpy.app.version >= (3, 2, 1):
            event_options += ["type_prev", "value_prev"]
        for option in event_options: self._event[option] = getattr(event, option)

    def draw_callback_px(self, context):
        event = self._event
        if event.keys():
            event = dotdict(event)
            try:
                pass
            except Exception as error:
                print(error)

    def execute(self, context):
        global _5F468_running
        _5F468_running = False
        context.window.cursor_set("DEFAULT")
        bpy.context.scene.tool_settings.use_proportional_edit = False
        bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='OBJECT')
        bpy.ops.object.origin_set('INVOKE_DEFAULT', type='ORIGIN_GEOMETRY')
        if handler_FD27A:
            bpy.types.SpaceView3D.draw_handler_remove(handler_FD27A[0], 'WINDOW')
            handler_FD27A.pop(0)
            for a in bpy.context.screen.areas: a.tag_redraw()
        bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='OBJECT')
        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
        for i_B6383 in range(len(bpy.context.active_object.vertex_groups)-1,-1,-1):
            bpy.context.active_object.vertex_groups.remove(group=bpy.context.active_object.vertex_groups[i_B6383], )
        bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='EDIT')
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}

    def modal(self, context, event):
        global _5F468_running
        if not context.area or not _5F468_running:
            self.execute(context)
            return {'CANCELLED'}
        self.save_event(event)
        context.window.cursor_set('CROSSHAIR')
        try:
            if (not 'EDIT_MESH'==bpy.context.mode):
                self.execute(context)
                return {"FINISHED"}
        except Exception as error:
            print(error)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        global _5F468_running
        if _5F468_running:
            _5F468_running = False
            return {'FINISHED'}
        else:
            self.save_event(event)
            self.start_pos = (event.mouse_x, event.mouse_y)
            out_coords = None
            import bmesh
            # Get the active object (assumed to be a mesh object)
            obj = bpy.context.active_object
            # Switch to edit mode
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            # Get the edit-mode BMesh
            bm = bmesh.from_edit_mesh(obj.data)
            world_matrix = obj.matrix_world
            unselected_vertices = [(v.index, (world_matrix @ Vector((v.co[0], v.co[1], v.co[2], 1.0)))[:3]) for v in bm.verts if not v.select]
            out_coords = []
            # Print the index and location of the selected vertices
            for vertex in unselected_vertices:
                index, location = vertex
                #print(f"Index: {index}, Location: {location}")
                out_coords.append(location)
            handler_FD27A.append(bpy.types.SpaceView3D.draw_handler_add(sna_function_execute_F1DF2, (out_coords, ), 'WINDOW', 'POST_VIEW'))
            for a in bpy.context.screen.areas: a.tag_redraw()
            bpy.ops.object.vertex_group_add('INVOKE_DEFAULT', )
            bpy.ops.object.vertex_group_assign('INVOKE_DEFAULT', )
            bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='OBJECT')
            bpy.ops.object.shape_key_add('INVOKE_DEFAULT', )
            bpy.ops.object.shape_key_add('INVOKE_DEFAULT', )
            bpy.context.active_object.active_shape_key.vertex_group = bpy.context.active_object.vertex_groups['Group'].name
            bpy.context.active_object.active_shape_key.value = 1.0
            bpy.context.view_layer.objects.active.use_shape_key_edit_mode = True
            bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='EDIT')
            bpy.ops.mesh.select_all('INVOKE_DEFAULT', action='DESELECT')
            if bpy.context.scene.sna_auto_enabledisable_falloff:
                bpy.context.scene.tool_settings.use_proportional_edit = True
            context.window_manager.modal_handler_add(self)
            _5F468_running = True
            return {'RUNNING_MODAL'}


def sna_function_execute_F1DF2(Input):
    coords = tuple(Input)
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = gpu_extras.batch.batch_for_shader(shader, 'POINTS', {"pos": coords})
    shader.bind()
    shader.uniform_float("color", (1.0, 0.0, 0.0005912857595831156, 0.4283650517463684))
    gpu.state.point_size_set(18.43000030517578)
    gpu.state.depth_test_set('LESS')
    gpu.state.depth_mask_set(True)
    gpu.state.blend_set('ALPHA')
    batch.draw(shader)


class SNA_AddonPreferences_B8AF5(bpy.types.AddonPreferences):
    bl_idname = 'pin_verts'

    def draw(self, context):
        if not (False):
            layout = self.layout 
            layout.prop(find_user_keyconfig('ED993'), 'type', text='Shortcut', full_event=True)
            layout.prop(bpy.context.scene, 'sna_auto_enabledisable_falloff', text='Auto Enable/Disable Proportional Editing', icon_value=0, emboss=True)
            layout.prop(bpy.context.scene, 'sna_show_header_button_editmode', text='Show Buttin in Header (Editmode)', icon_value=0, emboss=True)


def sna_add_to_view3d_ht_tool_header_8CF9B(self, context):
    if not (False):
        layout = self.layout
        if bpy.context.scene.sna_show_header_button_editmode:
            if 'EDIT_MESH'==bpy.context.mode:
                op = layout.operator('sna.modal_operator_5f468', text='Pin Unselected Vertices', icon_value=43, emboss=True, depress=False)


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.types.Scene.sna_auto_enabledisable_falloff = bpy.props.BoolProperty(name='auto_enabledisable_falloff', description='', default=True)
    bpy.types.Scene.sna_show_header_button_editmode = bpy.props.BoolProperty(name='show_header_button_editmode', description='', default=True)
    bpy.utils.register_class(SNA_OT_Modal_Operator_5F468)
    bpy.utils.register_class(SNA_AddonPreferences_B8AF5)
    bpy.types.VIEW3D_HT_tool_header.append(sna_add_to_view3d_ht_tool_header_8CF9B)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new('sna.modal_operator_5f468', 'P', 'PRESS',
        ctrl=False, alt=False, shift=True, repeat=False)
    addon_keymaps['ED993'] = (km, kmi)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.sna_show_header_button_editmode
    del bpy.types.Scene.sna_auto_enabledisable_falloff
    bpy.utils.unregister_class(SNA_OT_Modal_Operator_5F468)
    if handler_FD27A:
        bpy.types.SpaceView3D.draw_handler_remove(handler_FD27A[0], 'WINDOW')
        handler_FD27A.pop(0)
    bpy.utils.unregister_class(SNA_AddonPreferences_B8AF5)
    bpy.types.VIEW3D_HT_tool_header.remove(sna_add_to_view3d_ht_tool_header_8CF9B)
