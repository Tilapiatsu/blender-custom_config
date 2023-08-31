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

def get_prefs():
    return bpy.context.preferences.addons['pin_verts'].preferences

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
    # cursor = "CROSSHAIR"
    _handle = None
    _event = {}
    unselected = True

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
        if handler_FD27A:
            bpy.types.SpaceView3D.draw_handler_remove(handler_FD27A[0], 'WINDOW')
            handler_FD27A.pop(0)
            for a in bpy.context.screen.areas: a.tag_redraw()

        bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='EDIT')
        bpy.ops.mesh.reveal(select=False)
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
            self.preferences = get_prefs()
            if self.preferences.sna_auto_enabledisable_falloff:
                bpy.context.scene.tool_settings.use_proportional_edit = True
            self.hide_only_verts()
            bpy.ops.mesh.select_all('INVOKE_DEFAULT', action='DESELECT')
            context.window_manager.modal_handler_add(self)
            _5F468_running = True
            return {'RUNNING_MODAL'}
        
    def hide_only_verts(self):
        act_obj = bpy.context.object
        old_mode = act_obj.mode

        bpy.ops.object.mode_set(mode="OBJECT")

        sel_l = bpy.context.selected_objects
        if not act_obj in sel_l:
            sel_l += act_obj

        for obj in sel_l:
            me = obj.data
            if not obj.type == act_obj.type: # 同じオブジェクトタイプのみ
                continue

            # メッシュ
            if obj.type == "MESH":
                for vert in me.vertices:
                    if self.unselected:
                        if not vert.select:
                            vert.hide = True
                    else:
                        if vert.select:
                            vert.hide = True

            # カーブ
            elif obj.type == "CURVE":
                for sp in me.splines:
                    if sp.type == "BEZIER":
                        for pt in sp.bezier_points:
                            if self.unselected:
                                if not pt.select_control_point:
                                    pt.hide = True
                            else:
                                if pt.select_control_point:
                                    pt.hide = True
                    else:
                        for pt in sp.points:
                            if self.unselected:
                                if not pt.select:
                                    pt.hide = True
                            else:
                                if pt.select:
                                    pt.hide = True

            # サーフェス
            elif obj.type == "SURFACE":
                for sp in me.splines:
                    for pt in sp.points:
                        if pt.select:
                            pt.hide = True


        bpy.ops.object.mode_set(mode=old_mode)

vs_uni = '''
    uniform mat4 ModelViewProjectionMatrix;
    uniform float offset;
    in vec3 pos;

    vec4 project = ModelViewProjectionMatrix * vec4(pos, 1.0);
    vec4 vecOffset = vec4(0.0,0.0,offset,0.0);

    void main() {
        gl_Position = project + vecOffset;
    }
'''

fs_uni = '''
    uniform vec4 color;
    out vec4 fragColor;

    void main()
    {
        fragColor = vec4(color.xyz, color.w);
    }

'''

shader_uni = gpu.types.GPUShader(vs_uni, fs_uni)

def sna_function_execute_F1DF2(Input):
    coords = tuple(Input)
    # shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    shader = shader_uni
    batch = gpu_extras.batch.batch_for_shader(shader, 'POINTS', {"pos": coords})
    shader.bind()
    shader.uniform_float("color", (1.0, 0.0, 0.0, 0.43))
    retopo_offset = bpy.context.space_data.overlay.retopology_offset * bpy.context.space_data.overlay.show_retopology 

    shader.uniform_float("offset", -0.001 - retopo_offset/10)
    gpu.state.point_size_set(5.0)
    gpu.state.depth_test_set('LESS')
    gpu.state.depth_mask_set(True)
    gpu.state.blend_set('ALPHA')
    batch.draw(shader)


class SNA_AddonPreferences_B8AF5(bpy.types.AddonPreferences):
    bl_idname = 'pin_verts'
    sna_auto_enabledisable_falloff : bpy.props.BoolProperty(name='auto_enabledisable_falloff', description='', default=True)
    sna_show_header_button_editmode : bpy.props.BoolProperty(name='show_header_button_editmode', description='', default=True)

    def draw(self, context):
        if not (False):
            layout = self.layout 
            layout.prop(find_user_keyconfig('ED993'), 'type', text='Shortcut', full_event=True)
            layout.prop(self, 'sna_auto_enabledisable_falloff', text='Auto Enable/Disable Proportional Editing', icon_value=0, emboss=True)
            layout.prop(self, 'sna_show_header_button_editmode', text='Show Buttin in Header (Editmode)', icon_value=0, emboss=True)


def sna_add_to_view3d_ht_tool_header_8CF9B(self, context):
    if not (False):
        layout = self.layout
        if get_prefs().sna_show_header_button_editmode:
            if 'EDIT_MESH'==bpy.context.mode:
                op = layout.operator('sna.modal_operator_5f468', text='Pin Unselected Vertices', icon_value=43, emboss=True, depress=False)


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    
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
    bpy.utils.unregister_class(SNA_OT_Modal_Operator_5F468)
    if handler_FD27A:
        bpy.types.SpaceView3D.draw_handler_remove(handler_FD27A[0], 'WINDOW')
        handler_FD27A.pop(0)
    bpy.utils.unregister_class(SNA_AddonPreferences_B8AF5)
    bpy.types.VIEW3D_HT_tool_header.remove(sna_add_to_view3d_ht_tool_header_8CF9B)
