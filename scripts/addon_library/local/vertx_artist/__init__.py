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
    "name" : "VertX Artist",
    "author" : "Mahrkeenerh", 
    "description" : "Vertex coloring tool using Color Attributes",
    "blender" : (3, 4, 0),
    "version" : (2, 2, 5),
    "location" : "Edit Mode",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "Paint" 
}


import bpy
import bpy.utils.previews
import gpu
import gpu_extras
import mathutils
import blf
import os
import re
import colorsys
import subprocess
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ImportHelper, ExportHelper


addon_keymaps = {}
_icons = None
layers = {'sna_active_obj': None, }
layers_ui = {'sna_temp_layer_idx': 0, }
object_colors = {'sna_ignore_color_change': False, 'sna_active_color_selection': False, 'sna_prev_mode': '', }
vertx_panel = {'sna_popout_active': False, }
handler_BCC2E = []


def sna_update_name_94247(self, context):
    sna_updated_prop = self.name
    return_BDF88 = get_unique_transformation_name(name_list=eval("[i.name for i in bpy.context.view_layer.objects.active.sna_modification_stacks]"), name=sna_updated_prop)
    if (return_BDF88 == sna_updated_prop):
        pass
    else:
        self.name = return_BDF88


def sna_update_base_layer_C3B7B(self, context):
    sna_updated_prop = self.base_layer
    return_0ECDC = update_transformation(material=bpy.data.materials['display material vertx artist'], base_layer=sna_updated_prop)


def sna_update_factor_DCB8E(self, context):
    sna_updated_prop = self.factor
    return_9C95B = update_transformation(material=bpy.data.materials['display material vertx artist'], modification=self, factor=sna_updated_prop)


def sna_update_blend_color_81607(self, context):
    sna_updated_prop = self.blend_color
    return_C4E63 = update_transformation(material=bpy.data.materials['display material vertx artist'], modification=self, blend_color=sna_updated_prop)


def sna_update_sna_modification_stack_enum_42B47(self, context):
    sna_updated_prop = self.sna_modification_stack_enum
    material_0_dc6ab = sna_refresh_default_material_function_6E2E0()


def sna_update_blend_layer_3C8C9(self, context):
    sna_updated_prop = self.blend_layer
    return_61406 = update_transformation(material=bpy.data.materials['display material vertx artist'], modification=self, blend_layer=sna_updated_prop)


def sna_update_blend_type_4846E(self, context):
    sna_updated_prop = self.blend_type
    return_05A19 = update_transformation(material=bpy.data.materials['display material vertx artist'], modification=self, blend_type=sna_updated_prop)


def sna_update_include_0C1C2(self, context):
    sna_updated_prop = self.include
    material_0_7e880 = sna_refresh_default_material_function_6E2E0()


class SNA_UL_display_collection_list_5FDE3(bpy.types.UIList):

    def draw_item(self, context, layout, data, item_5FDE3, icon, active_data, active_propname, index_5FDE3):
        row = layout
        row_104C4 = layout.row(heading='', align=False)
        row_104C4.alert = False
        row_104C4.enabled = True
        row_104C4.active = True
        row_104C4.use_property_split = False
        row_104C4.use_property_decorate = False
        row_104C4.scale_x = 1.0
        row_104C4.scale_y = 1.0
        row_104C4.alignment = 'Left'.upper()
        if not True: row_104C4.operator_context = "EXEC_DEFAULT"
        op = row_104C4.operator('sna.toggle_color_transformation_visibility_fc89c', text='', icon_value=eval("254 if item_5FDE3.include else 253"), emboss=False, depress=False)
        op.sna_modification_index = index_5FDE3
        row_104C4.prop(item_5FDE3, 'blend_type', text='', icon_value=0, emboss=True)
        row_104C4.prop(item_5FDE3, 'blend_layer', text='', icon_value=0, emboss=True)
        if (item_5FDE3.blend_layer == 'flat color'):
            row_104C4.prop(item_5FDE3, 'blend_color', text='', icon_value=0, emboss=True)
        row_F7DCD = layout.row(heading='', align=False)
        row_F7DCD.alert = False
        row_F7DCD.enabled = True
        row_F7DCD.active = True
        row_F7DCD.use_property_split = False
        row_F7DCD.use_property_decorate = False
        row_F7DCD.scale_x = 1.0
        row_F7DCD.scale_y = 1.0
        row_F7DCD.alignment = 'Right'.upper()
        if not True: row_F7DCD.operator_context = "EXEC_DEFAULT"
        row_F7DCD.prop(item_5FDE3, 'factor', text='Fac', icon_value=0, emboss=True, slider=True)

    def filter_items(self, context, data, propname):
        flt_flags = []
        for item in getattr(data, propname):
            if not self.filter_name or self.filter_name.lower() in item.name.lower():
                if True:
                    flt_flags.append(self.bitflag_filter_item)
                else:
                    flt_flags.append(0)
            else:
                flt_flags.append(0)
        return flt_flags, []


_item_map = dict()


def sna_generate_dynamic_enum_86294_F2FB4(Prepend_List, List, Collection, Collection_Function, Description_List, Append_List):
    return_08E72 = new_enum_list = []
    return_5C2D3 = ([] if not Collection else [(Collection_Function if Collection_Function else lambda x: x.name)(i) for i in Collection])
    return_CE7BC = List if not return_5C2D3 else return_5C2D3
    return_241C4 = Prepend_List + return_CE7BC + Append_List
    for i_00465 in range(len(return_241C4)):
        return_C981A = new_enum_list.append([return_241C4[i_00465], return_241C4[i_00465], '' if len(Description_List) <= i_00465 else Description_List[i_00465], 0])
    return eval("new_enum_list")


_item_map = dict()


def sna_generate_dynamic_enum_86294_823FD(Prepend_List, List, Collection, Collection_Function, Description_List, Append_List):
    return_08E72 = new_enum_list = []
    return_5C2D3 = ([] if not Collection else [(Collection_Function if Collection_Function else lambda x: x.name)(i) for i in Collection])
    return_CE7BC = List if not return_5C2D3 else return_5C2D3
    return_241C4 = Prepend_List + return_CE7BC + Append_List
    for i_00465 in range(len(return_241C4)):
        return_C981A = new_enum_list.append([return_241C4[i_00465], return_241C4[i_00465], '' if len(Description_List) <= i_00465 else Description_List[i_00465], 0])
    return eval("new_enum_list")


_item_map = dict()


def make_enum_item(_id, name, descr, preview_id, uid):
    lookup = str(_id)+"\0"+str(name)+"\0"+str(descr)+"\0"+str(preview_id)+"\0"+str(uid)
    if not lookup in _item_map:
        _item_map[lookup] = (_id, name, descr, preview_id, uid)
    return _item_map[lookup]


def sna_generate_dynamic_enum_86294_9ADD2(Prepend_List, List, Collection, Collection_Function, Description_List, Append_List):
    return_08E72 = new_enum_list = []
    return_5C2D3 = ([] if not Collection else [(Collection_Function if Collection_Function else lambda x: x.name)(i) for i in Collection])
    return_CE7BC = List if not return_5C2D3 else return_5C2D3
    return_241C4 = Prepend_List + return_CE7BC + Append_List
    for i_00465 in range(len(return_241C4)):
        return_C981A = new_enum_list.append([return_241C4[i_00465], return_241C4[i_00465], '' if len(Description_List) <= i_00465 else Description_List[i_00465], 0])
    return eval("new_enum_list")


def property_exists(prop_path, glob, loc):
    try:
        eval(prop_path, glob, loc)
        return True
    except:
        return False


class SNA_UL_display_collection_list_CEEB3(bpy.types.UIList):

    def draw_item(self, context, layout, data, item_CEEB3, icon, active_data, active_propname, index_CEEB3):
        row = layout
        layout.prop(list(bpy.context.object.data.color_attributes)[index_CEEB3], 'name', text='', icon_value=202, emboss=False)
        row_20C09 = layout.row(heading='', align=False)
        row_20C09.alert = False
        row_20C09.enabled = bpy.context.view_layer.objects.active.sna_enable_editing
        row_20C09.active = True
        row_20C09.use_property_split = False
        row_20C09.use_property_decorate = False
        row_20C09.scale_x = 1.0
        row_20C09.scale_y = 1.0
        row_20C09.alignment = 'Right'.upper()
        if not True: row_20C09.operator_context = "EXEC_DEFAULT"
        if bpy.context.view_layer.objects.active.sna_enable_editing:
            row_20C09.prop(item_CEEB3, 'channels', text='', icon_value=0, emboss=True)
        else:
            row_20C09.label(text=item_CEEB3.channels, icon_value=0)
        if (index_CEEB3 == bpy.context.object.data.color_attributes.render_color_index):
            op = layout.operator('sna.toggle_render_color_layer_7a12b', text='', icon_value=258, emboss=False, depress=False)
            op.sna_layer_name = list(bpy.context.object.data.color_attributes)[index_CEEB3].name
        else:
            op = layout.operator('sna.toggle_render_color_layer_7a12b', text='', icon_value=257, emboss=False, depress=False)
            op.sna_layer_name = list(bpy.context.object.data.color_attributes)[index_CEEB3].name

    def filter_items(self, context, data, propname):
        flt_flags = []
        for item in getattr(data, propname):
            if not self.filter_name or self.filter_name.lower() in item.name.lower():
                if True:
                    flt_flags.append(self.bitflag_filter_item)
                else:
                    flt_flags.append(0)
            else:
                flt_flags.append(0)
        return flt_flags, []


def sna_update_sna_override_selection_color_C63F5(self, context):
    sna_updated_prop = self.sna_override_selection_color


def sna_update_color_E5CFB(self, context):
    sna_updated_prop = self.color
    if object_colors['sna_ignore_color_change']:
        pass
    else:
        return_D19EC = on_obj_color_change(obj_color=self, channels=list(bpy.context.view_layer.objects.active.sna_layers)[bpy.context.object.data.color_attributes.active_color_index].channels)


def display_collection_id(uid, vars):
    id = f"coll_{uid}"
    for var in vars.keys():
        if var.startswith("i_"):
            id += f"_{var}_{vars[var]}"
    return id


class SNA_UL_display_collection_list002_9846D(bpy.types.UIList):

    def draw_item(self, context, layout, data, item_9846D, icon, active_data, active_propname, index_9846D):
        row = layout
        layout.prop(item_9846D, 'name', text='', icon_value=0, emboss=False)
        row_EB758 = layout.row(heading='', align=True)
        row_EB758.alert = False
        row_EB758.enabled = True
        row_EB758.active = True
        row_EB758.use_property_split = False
        row_EB758.use_property_decorate = False
        row_EB758.scale_x = 1.0
        row_EB758.scale_y = 1.0
        row_EB758.alignment = 'Expand'.upper()
        if not True: row_EB758.operator_context = "EXEC_DEFAULT"
        row_EB758.prop(item_9846D, 'color', text='', icon_value=0, emboss=True)
        col_4DAE0 = row_EB758.column(heading='', align=True)
        col_4DAE0.alert = False
        col_4DAE0.enabled = ((bpy.context.object != None) and (((bpy.context.object.data.use_paint_mask or bpy.context.object.data.use_paint_mask_vertex) or 'EDIT_MESH'==bpy.context.mode) and (bpy.context.object.data.color_attributes.active_color != None)))
        col_4DAE0.active = True
        col_4DAE0.use_property_split = False
        col_4DAE0.use_property_decorate = False
        col_4DAE0.scale_x = 1.0
        col_4DAE0.scale_y = 1.0
        col_4DAE0.alignment = 'Expand'.upper()
        if not True: col_4DAE0.operator_context = "EXEC_DEFAULT"
        op = col_4DAE0.operator('sna.set_color_abbbf', text='', icon_value=36, emboss=True, depress=False)
        op.sna_new_color = item_9846D.color

    def filter_items(self, context, data, propname):
        flt_flags = []
        for item in getattr(data, propname):
            if not self.filter_name or self.filter_name.lower() in item.name.lower():
                if True:
                    flt_flags.append(self.bitflag_filter_item)
                else:
                    flt_flags.append(0)
            else:
                flt_flags.append(0)
        return flt_flags, []


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


def sna_draw_eyedropper_display_function_046A8(mouse_position, color_rgb, color_hex):
    quads = [[tuple((int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((-5.0, -5.0)))))[0]), int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((-5.0, -5.0)))))[1]))), tuple((int(int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((-5.0, -5.0)))))[0]) + 135), int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((-5.0, -5.0)))))[1]))), tuple((int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((-5.0, -5.0)))))[0]), int(int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((-5.0, -5.0)))))[1]) + 30))), tuple((int(int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((-5.0, -5.0)))))[0]) + 135), int(int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((-5.0, -5.0)))))[1]) + 30)))]]
    vertices = []
    indices = []
    for i_727C8, quad in enumerate(quads):
        vertices.extend(quad)
        indices.extend([(i_727C8 * 4, i_727C8 * 4 + 1, i_727C8 * 4 + 2), (i_727C8 * 4 + 2, i_727C8 * 4 + 1, i_727C8 * 4 + 3)])
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = gpu_extras.batch.batch_for_shader(shader, 'TRIS', {"pos": tuple(vertices)}, indices=tuple(indices))
    shader.bind()
    shader.uniform_float("color", (0.18397267162799835, 0.18397267162799835, 0.18397286534309387, 1.0))
    gpu.state.blend_set('ALPHA')
    batch.draw(shader)
    quads = [[tuple((int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))))[0]), int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))))[1]))), tuple((int(int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))))[0]) + 20), int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))))[1]))), tuple((int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))))[0]), int(int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))))[1]) + 20))), tuple((int(int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))))[0]) + 20), int(int(tuple(map(lambda v: int(v), tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))))[1]) + 20)))]]
    vertices = []
    indices = []
    for i_83E95, quad in enumerate(quads):
        vertices.extend(quad)
        indices.extend([(i_83E95 * 4, i_83E95 * 4 + 1, i_83E95 * 4 + 2), (i_83E95 * 4 + 2, i_83E95 * 4 + 1, i_83E95 * 4 + 3)])
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = gpu_extras.batch.batch_for_shader(shader, 'TRIS', {"pos": tuple(vertices)}, indices=tuple(indices))
    shader.bind()
    shader.uniform_float("color", eval("(*color_rgb, 1.0)"))
    gpu.state.blend_set('ALPHA')
    batch.draw(shader)
    font_id = 0
    if r'' and os.path.exists(r''):
        font_id = blf.load(r'')
    if font_id == -1:
        print("Couldn't load font!")
    else:
        x_AE6C4, y_AE6C4 = tuple(mathutils.Vector(tuple(mathutils.Vector(mouse_position) + mathutils.Vector((30.0, -1.0)))) + mathutils.Vector((30.0, 3.0)))
        blf.position(font_id, x_AE6C4, y_AE6C4, 0)
        if bpy.app.version >= (3, 4, 0):
            blf.size(font_id, 20.0)
        else:
            blf.size(font_id, 20.0, 72)
        clr = (1.0, 1.0, 1.0, 1.0)
        blf.color(font_id, clr[0], clr[1], clr[2], clr[3])
        if 0:
            blf.enable(font_id, blf.WORD_WRAP)
            blf.word_wrap(font_id, 0)
        if 0.0:
            blf.enable(font_id, blf.ROTATION)
            blf.rotation(font_id, 0.0)
        blf.enable(font_id, blf.WORD_WRAP)
        blf.draw(font_id, '#' + color_hex)
        blf.disable(font_id, blf.ROTATION)
        blf.disable(font_id, blf.WORD_WRAP)


_FE493_running = False
class SNA_OT_Vertx_Eyedropper_Fe493(bpy.types.Operator):
    bl_idname = "sna.vertx_eyedropper_fe493"
    bl_label = "VertX Eyedropper"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    cursor = "EYEDROPPER"
    _handle = None
    _event = {}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        if not False or context.area.spaces[0].bl_rna.identifier == 'SpaceNodeEditor':
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
        global _FE493_running
        _FE493_running = False
        context.window.cursor_set("DEFAULT")
        if handler_BCC2E:
            bpy.types.SpaceView3D.draw_handler_remove(handler_BCC2E[0], 'WINDOW')
            handler_BCC2E.pop(0)
            for a in bpy.context.screen.areas: a.tag_redraw()
        return_D7176 = set_clipboard()
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}

    def modal(self, context, event):
        global _FE493_running
        if not context.area or not _FE493_running:
            self.execute(context)
            return {'CANCELLED'}
        self.save_event(event)
        context.window.cursor_set('EYEDROPPER')
        try:
            return_41CCC = get_color(event=eval("event"))
            if (event.value == 'RELEASE'):
                if event.type in ['RIGHTMOUSE', 'ESC']:
                    self.execute(context)
                    return {'CANCELLED'}
                self.execute(context)
                return {"FINISHED"}
            else:
                if handler_BCC2E:
                    bpy.types.SpaceView3D.draw_handler_remove(handler_BCC2E[0], 'WINDOW')
                    handler_BCC2E.pop(0)
                    for a in bpy.context.screen.areas: a.tag_redraw()
                handler_BCC2E.append(bpy.types.SpaceView3D.draw_handler_add(sna_draw_eyedropper_display_function_046A8, ((event.mouse_region_x, event.mouse_region_y), return_41CCC[0], return_41CCC[1], ), 'WINDOW', 'POST_PIXEL'))
                for a in bpy.context.screen.areas: a.tag_redraw()
            bpy.context.scene.sna_static_color = return_41CCC[0]
        except Exception as error:
            print(error)
        if event.type in ['RIGHTMOUSE', 'ESC']:
            self.execute(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        global _FE493_running
        if _FE493_running:
            _FE493_running = False
            return {'FINISHED'}
        else:
            self.save_event(event)
            self.start_pos = (event.mouse_x, event.mouse_y)
            context.window.cursor_set('EYEDROPPER')
            return_41CCC = get_color(event=eval("event"))
            if (event.value == 'RELEASE'):
                if event.type in ['RIGHTMOUSE', 'ESC']:
                    self.execute(context)
                    return {'CANCELLED'}
                self.execute(context)
                return {"FINISHED"}
            else:
                if handler_BCC2E:
                    bpy.types.SpaceView3D.draw_handler_remove(handler_BCC2E[0], 'WINDOW')
                    handler_BCC2E.pop(0)
                    for a in bpy.context.screen.areas: a.tag_redraw()
                handler_BCC2E.append(bpy.types.SpaceView3D.draw_handler_add(sna_draw_eyedropper_display_function_046A8, ((event.mouse_region_x, event.mouse_region_y), return_41CCC[0], return_41CCC[1], ), 'WINDOW', 'POST_PIXEL'))
                for a in bpy.context.screen.areas: a.tag_redraw()
            bpy.context.scene.sna_static_color = return_41CCC[0]
            context.window_manager.modal_handler_add(self)
            _FE493_running = True
            return {'RUNNING_MODAL'}


def sna_extractbake_function_95836(layout_function, extract_name, bake_name):
    if ((bpy.context.object != None) and (bpy.context.object.data != None) and (bpy.context.object.data.color_attributes.active_color != None)):
        if (bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].channels == 'RGBA'):
            op = layout_function.operator('sna.extract_alpha_50ab0', text=extract_name, icon_value=598, emboss=True, depress=False)
    if ((bpy.context.object != None) and (bpy.context.object.data != None) and (bpy.context.object.data.color_attributes.active_color != None)):
        if (bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].channels == 'A'):
            op = layout_function.operator('sna.bake_alpha_a245b', text=bake_name, icon_value=599, emboss=True, depress=False)
            op.sna_layer_name = ''


class SNA_OT_Apply_Alpha_Gradient_72437(bpy.types.Operator):
    bl_idname = "sna.apply_alpha_gradient_72437"
    bl_label = "Apply Alpha Gradient"
    bl_description = "Apply alpha gradient to correct channel"
    bl_options = {"REGISTER", "UNDO"}
    sna_neg_axis: bpy.props.FloatProperty(name='neg_axis', description='', default=0.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=3)
    sna_pos_axis: bpy.props.FloatProperty(name='pos_axis', description='', default=0.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=3)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        return_591EF = apply_alpha_gradient(neg_axis=self.sna_neg_axis, pos_axis=self.sna_pos_axis)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_add_to_view3d_pt_tools_active_937B1(self, context):
    if not ((not ('OBJECT'==bpy.context.mode or 'EDIT_MESH'==bpy.context.mode))):
        layout = self.layout
        box_83E1C = layout.box()
        box_83E1C.alert = False
        box_83E1C.enabled = True
        box_83E1C.active = True
        box_83E1C.use_property_split = False
        box_83E1C.use_property_decorate = False
        box_83E1C.alignment = 'Expand'.upper()
        box_83E1C.scale_x = 1.0
        box_83E1C.scale_y = 1.0
        if not True: box_83E1C.operator_context = "EXEC_DEFAULT"
        box_83E1C.label(text='Alpha Gradients', icon_value=126)
        row_7232D = box_83E1C.row(heading='', align=False)
        row_7232D.alert = False
        row_7232D.enabled = True
        row_7232D.active = True
        row_7232D.use_property_split = False
        row_7232D.use_property_decorate = False
        row_7232D.scale_x = 1.0
        row_7232D.scale_y = 1.0
        row_7232D.alignment = 'Expand'.upper()
        if not True: row_7232D.operator_context = "EXEC_DEFAULT"
        row_7232D.prop(bpy.context.scene, 'sna_neg_axis', text='Negative', icon_value=0, emboss=True)
        row_7232D.prop(bpy.context.scene, 'sna_pos_axis', text='Positive', icon_value=0, emboss=True)
        row_05346 = box_83E1C.row(heading='', align=False)
        row_05346.alert = False
        row_05346.enabled = True
        row_05346.active = True
        row_05346.use_property_split = False
        row_05346.use_property_decorate = False
        row_05346.scale_x = 1.0
        row_05346.scale_y = 1.0
        row_05346.alignment = 'Expand'.upper()
        if not True: row_05346.operator_context = "EXEC_DEFAULT"
        op = row_05346.operator('sna.apply_alpha_gradient_72437', text='Apply Gradient', icon_value=0, emboss=True, depress=False)
        op.sna_neg_axis = bpy.context.scene.sna_neg_axis
        op.sna_pos_axis = bpy.context.scene.sna_pos_axis
        op = row_05346.operator('sna.apply_alpha_gradient_72437', text='Apply Positive', icon_value=0, emboss=True, depress=False)
        op.sna_neg_axis = bpy.context.scene.sna_pos_axis
        op.sna_pos_axis = bpy.context.scene.sna_pos_axis
        layout_function = box_83E1C
        sna_extractbake_function_95836(layout_function, 'Show Alpha', 'Hide Alpha')
        layout.separator(factor=2.0)


def sna_header_function_FB3F3(layout_function, ):
    box_6F92F = layout_function.box()
    box_6F92F.alert = False
    box_6F92F.enabled = True
    box_6F92F.active = True
    box_6F92F.use_property_split = False
    box_6F92F.use_property_decorate = False
    box_6F92F.alignment = 'Expand'.upper()
    box_6F92F.scale_x = 1.0
    box_6F92F.scale_y = 1.0
    if not True: box_6F92F.operator_context = "EXEC_DEFAULT"
    row_BF9F0 = box_6F92F.row(heading='', align=False)
    row_BF9F0.alert = False
    row_BF9F0.enabled = True
    row_BF9F0.active = True
    row_BF9F0.use_property_split = False
    row_BF9F0.use_property_decorate = False
    row_BF9F0.scale_x = 1.0
    row_BF9F0.scale_y = 1.0
    row_BF9F0.alignment = 'Expand'.upper()
    if not True: row_BF9F0.operator_context = "EXEC_DEFAULT"
    if vertx_panel['sna_popout_active']:
        row_BF9F0.template_icon(icon_value=77, scale=1.0)
    else:
        op = row_BF9F0.operator('sna.vertx_artist_popout_fa638', text='', icon_value=77, emboss=False, depress=False)
    row_BF9F0.label(text='VertX Artist', icon_value=0)
    row_BF9F0.popover('SNA_PT_PREFERENCES_1A5FD', text='', icon_value=233)
    row_C7980 = box_6F92F.row(heading='', align=True)
    row_C7980.alert = False
    row_C7980.enabled = True
    row_C7980.active = True
    row_C7980.use_property_split = False
    row_C7980.use_property_decorate = False
    row_C7980.scale_x = 1.0
    row_C7980.scale_y = 1.0
    row_C7980.alignment = 'Expand'.upper()
    if not True: row_C7980.operator_context = "EXEC_DEFAULT"
    row_C7980.prop(bpy.context.scene, 'sna_static_color', text='Set Color', icon_value=0, emboss=True)
    col_7B657 = row_C7980.column(heading='', align=True)
    col_7B657.alert = False
    col_7B657.enabled = ((bpy.context.object != None) and (((bpy.context.object.data.use_paint_mask or bpy.context.object.data.use_paint_mask_vertex) or 'EDIT_MESH'==bpy.context.mode) and (bpy.context.object.data.color_attributes.active_color != None)))
    col_7B657.active = True
    col_7B657.use_property_split = False
    col_7B657.use_property_decorate = False
    col_7B657.scale_x = 1.0
    col_7B657.scale_y = 1.0
    col_7B657.alignment = 'Expand'.upper()
    if not True: col_7B657.operator_context = "EXEC_DEFAULT"
    op = col_7B657.operator('sna.set_color_abbbf', text='', icon_value=36, emboss=True, depress=False)
    op.sna_new_color = bpy.context.scene.sna_static_color
    if ((bpy.context.object != None) and (bpy.context.object.data != None) and (bpy.context.object.data.color_attributes.active_color != None)):
        pass
    else:
        row_9CBB0 = box_6F92F.row(heading='', align=False)
        row_9CBB0.alert = True
        row_9CBB0.enabled = True
        row_9CBB0.active = True
        row_9CBB0.use_property_split = False
        row_9CBB0.use_property_decorate = False
        row_9CBB0.scale_x = 1.0
        row_9CBB0.scale_y = 1.0
        row_9CBB0.alignment = 'Expand'.upper()
        if not True: row_9CBB0.operator_context = "EXEC_DEFAULT"
        op = row_9CBB0.operator('sna.add_layer_af10a', text='Add Color Layer', icon_value=0, emboss=True, depress=False)


"""Vertex color script for blender."""


import math
import bmesh
# Gamma correction and inverse gamma correction may be reversed


def inverse_gamma(c: float):
    """Gamma uncorrection."""
    c = min(max(0, c), 1)
    c = c / 12.92 if c < 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)
    return c


def gamma_correct(c: float):
    """Gamma correction."""
    c = max(0.0, c * 12.92) if c < 0.0031308 else 1.055 * math.pow(c, 1.0 / 2.4) - 0.055
    c = max(min(int(c * 255 + 0.5), 255), 0)
    return c / 255


def inverse_gamma_color(rgb):
    """Gamma uncorrection."""
    # r = rgb[0] * 255
    # g = rgb[1] * 255
    # b = rgb[2] * 255
    # r = min(max(0, r), 255) / 255
    # g = min(max(0, g), 255) / 255
    # b = min(max(0, b), 255) / 255
    # r = r / 12.92 if r < 0.04045 else math.pow((r + 0.055) / 1.055, 2.4)
    # g = g / 12.92 if g < 0.04045 else math.pow((g + 0.055) / 1.055, 2.4)
    # b = b / 12.92 if b < 0.04045 else math.pow((b + 0.055) / 1.055, 2.4)
    # return r, g, b
    return inverse_gamma(rgb[0]), inverse_gamma(rgb[1]), inverse_gamma(rgb[2])


# possibly save color RGB, and then only update specific items
"""
{
    col_idx: {
        "obj": {
            vert_idx: [(
                corner_list_idx,
                corner_idx
            ), ...]
        }
    }


}
"""
color_corner_lookup = {}
"""
{
    ("obj", vert_idx, corner_idx): col_idx


}
"""
corner_color_lookup = {}


def set_restricted_color(color: tuple, new_color: tuple, channels: str):
    """Set color according to restrictions."""
    if bpy.context.mode != "EDIT_MESH":
        new_color = inverse_gamma_color(new_color)
    if "R" in channels:
        color[0] = new_color[0]
    if "G" in channels:
        color[1] = new_color[1]
    if "B" in channels:
        color[2] = new_color[2]
    if "A" == channels:
        hsv_color = colorsys.rgb_to_hsv(*new_color)
        for i in range(3):
            color[i] = hsv_color[2]


def set_color(color: tuple, channels: str):
    """Set color of active selection."""
    obj = bpy.context.object
    if obj is None:
        return None
    color_attribute = obj.data.color_attributes.active_color
    if color_attribute is None:
        return None
    # VERTEX PAINT MODE
    if bpy.context.mode == "PAINT_VERTEX":
        try:
            vert_mode = obj.data.use_paint_mask_vertex
            poly_mode = obj.data.use_paint_mask
        except AttributeError:
            return None
        if vert_mode:
            selected_vert_idx = []
            for vertex in obj.data.vertices:
                if vertex.select:
                    selected_vert_idx.append(vertex.index)
            for i, l in enumerate(obj.data.loops):
                if l.vertex_index not in selected_vert_idx:
                    continue
                set_restricted_color(
                    color_attribute.data[i].color,
                    color,
                    channels
                )
        # polygons
        if poly_mode:
            for polygon in obj.data.polygons:
                if polygon.select:
                    for i in polygon.loop_indices:
                        set_restricted_color(
                            color_attribute.data[i].color,
                            color,
                            channels
                        )
        return
    # EDIT MODE
    if bpy.context.mode == "EDIT_MESH":
        objs = bpy.context.selected_objects
        if not objs:
            objs = [obj]
        # new_color = None
        # changes = []
        # Ignore non-mesh objects
        objs = [x for x in objs if x.type == "MESH"]
        # obj_name_map = {x.name: x for x in objs}
        for obj in objs:
            mode = list(bpy.context.tool_settings.mesh_select_mode)
            bm = bmesh.from_edit_mesh(obj.data)
            active_layer = bm.loops.layers.color.get(color_attribute.name)
            # edge or vertex selection
            if mode[0] or mode[1]:
                for vert in bm.verts:
                    if vert.select:
                        for loop in vert.link_loops:
                            set_restricted_color(
                                loop[active_layer],
                                color,
                                channels
                            )
                            # changes.append((obj.name, vert.index, loop.index))
            # # faces
            if mode[2]:
                for face in bm.faces:
                    if face.select:
                        for loop in face.loops:
                            set_restricted_color(
                                loop[active_layer],
                                color,
                                channels
                            )
                            # changes.append((obj.name, loop.vert.index, loop.index))
            # if new_color is None:
            #     new_color = tuple(bm.verts[changes[-1][1]].link_loops[changes[-1][2]][active_layer])
            bmesh.update_edit_mesh(obj.data)
        # Update color corner lookup
        # for change in changes:
        #     corner_color_lookup[change] = color_attribute.index


def on_obj_color_change(obj_color, channels: str):
    """Update color of everything with same color."""
    color_idx = obj_color.index
    new_color = obj_color.color
    obj = bpy.context.object
    objs = bpy.context.selected_objects
    if not objs:
        if obj is None:
            return
        objs = [obj]
    # Ignore non-mesh objects
    objs = [x for x in objs if x.type == "MESH"]
    obj_name_map = {x.name: x for x in objs}
    for obj_name in color_corner_lookup[color_idx]:
        obj = obj_name_map[obj_name]        
        color_attribute = obj.data.color_attributes.active_color
        if color_attribute is None:
            continue
        bm = bmesh.from_edit_mesh(obj.data)
        active_layer = bm.loops.layers.color.get(color_attribute.name)
        for vert_idx in color_corner_lookup[color_idx][obj.name]:
            for corner_list_idx, corner_idx in color_corner_lookup[color_idx][obj.name][vert_idx]:
                set_restricted_color(
                    bm.verts[vert_idx].link_loops[corner_list_idx][active_layer],
                    new_color,
                    channels
                )
        bmesh.update_edit_mesh(obj.data)


def refresh_object_colors():
    """Return all colors of objects."""
    global color_corner_lookup, corner_color_lookup
    color_corner_lookup = {}
    corner_color_lookup = {}
    output_size = 2
    obj = bpy.context.object
    objs = bpy.context.selected_objects
    if not objs:
        if obj is None:
            return (None, ) * output_size
        objs = [obj]
    """
    colors = {
        (r, g, b): [idx, count],
    }
    """
    colors = {}
    # Ignore non-mesh objects
    objs = [x for x in objs if x.type == "MESH"]
    for obj in objs:
        color_attribute = obj.data.color_attributes.active_color
        if color_attribute is None:
            continue
        bm = bmesh.from_edit_mesh(obj.data)
        active_layer = bm.loops.layers.color.get(color_attribute.name)

        def get_color(corner_list_idx, c):
            color = tuple(corner[active_layer])[:-1]
            colors.setdefault(color, [len(colors), 0])[1] += c
            color_corner_lookup.setdefault(
                colors[color][0], {}
            ).setdefault(
                obj.name, {}
            ).setdefault(
                vert.index, []
            ).append(
                (corner_list_idx, corner.index)
            )
            # corner_color_lookup[(obj.name, vert.index, corner.index)] = colors[color][0]
        # vert or edge mode
        if bpy.context.tool_settings.mesh_select_mode[0] or bpy.context.tool_settings.mesh_select_mode[1]:
            for vert in bm.verts:
                for corner_idx, corner in enumerate(vert.link_loops):
                    get_color(corner_idx, int(vert.select))
        # faces
        if bpy.context.tool_settings.mesh_select_mode[2]:
            for face in bm.faces:

                def get_corner_idx():
                    corner_list_idx = 0
                    for i in range(len(corner.vert.link_loops)):
                        if corner.vert.link_loops[i].index == corner.index:
                            corner_list_idx = i
                            break
                    return corner_list_idx
                for corner in face.loops:
                    vert = corner.vert
                    get_color(get_corner_idx(), int(face.select))
    active_color_index = max(colors.values(), key=lambda x: x[1])[0] if len(colors) > 0 else None
    colors = [x for x in colors.keys()]
    return active_color_index, colors


def import_palette(path: str):
    """Import palette from file."""
    palette_name = os.path.basename(path).split(".")[0]
    palette_name = palette_name.replace("_", " ")
    file_extension = path.split(".")[-1]
    names = []
    colors = []
    if file_extension == "ccb":
        with open(path, "r", encoding="utf16") as f:
            contents = f.readlines()
        del contents[:25]
        for line in contents:
            line = line.strip().split(" ")
            r_raw = float(line[0])
            g_raw = float(line[1])
            b_raw = float(line[2])
            # colors.append(to_blender_color((r_raw, g_raw, b_raw)))
            colors.append((r_raw, g_raw, b_raw))
            names.append(line[4])
        return palette_name, names, colors
    if file_extension == "colors":
        with open(path, "r", encoding="us-ascii") as f:
            contents = f.read()
        colors_re = re.findall(r'(m_Color: {r: (.+), g: (.+), b: (.+), a: (.+)})', contents)
        names = re.findall(r'(- m_Name: (.*))', contents)
        for color in colors_re:
            r_raw = float(color[1])
            g_raw = float(color[2])
            b_raw = float(color[3])
            # colors.append(to_blender_color((r_raw, g_raw, b_raw)))
            colors.append((r_raw, g_raw, b_raw))
        names = [i[1] for i in names][9:]
        colors = colors[9:]
        return palette_name, names, colors
    if file_extension == "gpl":
        with open(path, "r", encoding="utf8") as f:
            contents = f.readlines()
        for line in contents:
            line = line.strip()
            if (
                line == "" or
                line.startswith("#") or
                line.startswith("GIMP Palette") or
                line.startswith("Name: ") or
                line.startswith("Columns: ")
            ):
                continue
            line = line.split()
            r_raw = float(line[0]) / 255
            g_raw = float(line[1]) / 255
            b_raw = float(line[2]) / 255
            name = " ".join(line[3:])
            # colors.append(to_blender_color((r_raw, g_raw, b_raw)))
            colors.append((r_raw, g_raw, b_raw))
            names.append(name)
        return palette_name, names, colors
    print("Unknown file extension: " + file_extension)
    return None, None, None


def export_palette(colors: list, path: str, ccb_header_path: str = None):
    """Export palette to file."""
    file_extension = path.split(".")[-1]
    if file_extension == "ccb":
        with open(ccb_header_path, "r", encoding="utf8") as f:
            contents = f.readlines()
        with open(path, "w", encoding="utf16") as out:
            out.writelines(contents)
            print(len(colors), file=out)
            for color in colors:
                # rgb = from_blender_color(tuple(color.color))
                rgb = tuple(color.color)
                print(
                    f"{rgb[0]:.6f}",
                    f"{rgb[1]:.6f}",
                    f"{rgb[2]:.6f}",
                    f"{1:.6f}",
                    color.name,
                    file=out
                )
        return
    if file_extension == "gpl":
        with open(path, "w", encoding="utf8") as out:
            print("GIMP Palette", file=out)
            print("Name:", os.path.basename(path).split(".")[0], file=out)
            print("Columns: 0", file=out)
            for color in colors:
                # rgb = from_blender_color(tuple(color.color))
                rgb = tuple(color.color)
                rgb_int = [int(x * 255) for x in rgb]
                print(
                    f"{rgb_int[0]}",
                    f"{rgb_int[1]}",
                    f"{rgb_int[2]}",
                    color.name,
                    file=out
                )
        return
    print("Unknown file extension: " + file_extension)
    return


def select_by_color(tolerance: float, color: tuple, color_idx: int, ignore_hsv: tuple):
    """Select all vertices/polygons with color within tolerance."""
    obj = bpy.context.object
    objs = bpy.context.selected_objects
    if not objs:
        if obj is None:
            return
        objs = [obj]
    # Ignore non-mesh objects
    objs = [x for x in objs if x.type == "MESH"]
    obj_name_map = {x.name: x for x in objs}
    # Deselect all
    if bpy.context.mode == "EDIT_MESH":
        bm = bmesh.from_edit_mesh(obj.data)
        for vert in bm.verts:
            vert.select = False
        for face in bm.faces:
            face.select = False
        for edge in bm.edges:
            edge.select = False
        bm.select_flush_mode()
    # vert mode or edge mode
    if bpy.context.tool_settings.mesh_select_mode[0] or bpy.context.tool_settings.mesh_select_mode[1]:
        for obj_name in color_corner_lookup[color_idx]:
            obj = obj_name_map[obj_name]
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            for vert_idx in color_corner_lookup[color_idx][obj_name]:
                if len(color_corner_lookup[color_idx][obj_name][vert_idx]) / len(bm.verts[vert_idx].link_loops) >= (1 - tolerance):
                    bm.verts[vert_idx].select = True
            # edge mode
            if bpy.context.tool_settings.mesh_select_mode[1]:
                for edge in bm.edges:
                    if edge.verts[0].select and edge.verts[1].select:
                        edge.select = True
            bmesh.update_edit_mesh(obj.data)
    # face mode
    if bpy.context.tool_settings.mesh_select_mode[2]:
        for obj_name in color_corner_lookup[color_idx]:
            obj = obj_name_map[obj_name]
            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()
            for face in bm.faces:
                loops_in_face = [x for x in face.loops if x.vert.index in color_corner_lookup[color_idx][obj_name]]
                if len(loops_in_face) / len(face.loops) >= (1 - tolerance):
                    face.select = True
            bmesh.update_edit_mesh(obj.data)


def combine_layers(
    channels: str,
    channels_list: list,
    channels_values: list,
    channels_gamma: list,
    layers: list


):
    """Assign color to active Color attribute from multiple channels."""
    obj = bpy.context.object
    if obj is None:
        return None
    color_attribute = obj.data.color_attributes.active_color
    if color_attribute is None:
        return None
    new_layer_name = color_attribute.name
    color_attributes = [None] * 4

    def combine_layers_bmesh():
        color_attribute = bm.loops.layers.color.get(new_layer_name)
        for channel in channels_list:
            for i in range(4):
                if channel == channels_list[i]:
                    color_attributes[i] = bm.loops.layers.color.get(channel)

        def color_map(corner, j: int):
            if color_attributes[j] is None:
                return channels_values[j]
            if j < 3:
                return corner[color_attributes[j]][j]
            if layers[channels_list[j]].channels == "A":
                obj_color = tuple(corner[color_attributes[j]])[:-1]
                obj_hsv_color = colorsys.rgb_to_hsv(*obj_color)
                return obj_hsv_color[2]
            if channels == "A":
                return corner[color_attributes[j]][3]
            return corner[color_attributes[j]][j]
        if channels == "A":
            for vert in bm.verts:
                for corner in vert.link_loops:
                    for j in range(3):
                        corner[color_attribute][j] = color_map(corner, 3)
            if channels_gamma[3] == "Gamma":
                for vert in bm.verts:
                    for corner in vert.link_loops:
                        for j in range(3):
                            corner[color_attribute][j] = gamma_correct(corner[color_attribute][j])
            if channels_gamma[3] == "Inverse":
                for vert in bm.verts:
                    for corner in vert.link_loops:
                        for j in range(3):
                            corner[color_attribute][j] = inverse_gamma(corner[color_attribute][j])
            return
        for vert in bm.verts:
            for corner in vert.link_loops:
                for j in range(4):
                    corner[color_attribute][j] = color_map(corner, j)
        for j in range(4):
            if channels_gamma[j] == "Gamma":
                for vert in bm.verts:
                    for corner in vert.link_loops:
                        corner[color_attribute][j] = gamma_correct(corner[color_attribute][j])
            if channels_gamma[j] == "Inverse":
                for vert in bm.verts:
                    for corner in vert.link_loops:
                        corner[color_attribute][j] = inverse_gamma(corner[color_attribute][j])

    def combine_layers_bpy():
        for col_attribute in obj.data.color_attributes:
            for i in range(4):
                if col_attribute.name == channels_list[i]:
                    color_attributes[i] = col_attribute

        def color_map(i: int, j: int):
            if color_attributes[j] is None:
                return channels_values[j]
            if j < 3:
                return color_attributes[j].data[i].color[j]
            if layers[color_attributes[j].name].channels == "A":
                obj_color = tuple(color_attributes[j].data[i].color)[:-1]
                obj_hsv_color = colorsys.rgb_to_hsv(*obj_color)
                return obj_hsv_color[2]
            if channels == "A":
                return color_attributes[j].data[i].color[3]
            return color_attributes[j].data[i].color[j]
        if channels == "A":
            for i, l in enumerate(obj.data.loops):
                for j in range(3):
                    color_attribute.data[i].color[j] = color_map(i, 3)
            if channels_gamma[3] == "Gamma":
                for i, l in enumerate(obj.data.loops):
                    for j in range(3):
                        color_attribute.data[i].color[j] = gamma_correct(color_attribute.data[i].color[j])
            if channels_gamma[3] == "Inverse":
                for i, l in enumerate(obj.data.loops):
                    for j in range(3):
                        color_attribute.data[i].color[j] = inverse_gamma(color_attribute.data[i].color[j])
            return
        for i, l in enumerate(obj.data.loops):
            for j in range(4):
                color_attribute.data[i].color[j] = color_map(i, j)
        for j in range(4):
            if channels_gamma[j] == "Gamma":
                for i, l in enumerate(obj.data.loops):
                    color_attribute.data[i].color[j] = gamma_correct(color_attribute.data[i].color[j])
            if channels_gamma[j] == "Inverse":
                for i, l in enumerate(obj.data.loops):
                    color_attribute.data[i].color[j] = inverse_gamma(color_attribute.data[i].color[j])
    if bpy.context.mode == "EDIT_MESH":
        bm = bmesh.from_edit_mesh(obj.data)
        combine_layers_bmesh()
        bmesh.update_edit_mesh(obj.data)
    else:
        combine_layers_bpy()


def calculate_alpha(neg_axis, pos_axis, min_z, max_z, z):
    """Calculate alpha value for vertex."""
    div = max_z - min_z if max_z - min_z != 0 else 1
    alpha = (z - min_z) / div * (pos_axis - neg_axis) + neg_axis
    return alpha


def apply_alpha_gradient(neg_axis: float, pos_axis: float):
    """Create alpha gradient on all selected objects"""
    active_obj = bpy.context.object
    objects = bpy.context.selected_objects
    if not objects:
        if active_obj is None:
            return None
        objects = [active_obj]
    for obj in objects:
        if obj.type != "MESH":
            continue
        if obj.data.color_attributes.active_color is None:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.geometry.color_attribute_add(name='Attribute', domain='CORNER', data_type='BYTE_COLOR')
    bpy.context.view_layer.objects.active = active_obj
    if bpy.context.mode == "OBJECT":
        obj_verts_coords = [obj.matrix_world @ v.co for obj in objects for v in obj.data.vertices]
    elif bpy.context.mode == "EDIT_MESH":
        obj_verts_coords = []
        for obj in objects:
            if obj.type != "MESH":
                continue
            bm = bmesh.from_edit_mesh(obj.data)
            obj_verts_coords.extend([obj.matrix_world @ v.co for v in bm.verts if v.select])
    if len(obj_verts_coords) == 0:
        return
    min_z = min(obj_verts_coords, key=lambda x: x[2])[2]
    max_z = max(obj_verts_coords, key=lambda x: x[2])[2]
    if bpy.context.mode == "EDIT_MESH":
        rolling_i = 0
        for i, obj in enumerate(objects):
            if obj.type != "MESH":
                continue
            bm = bmesh.from_edit_mesh(obj.data)
            active_name = obj.data.color_attributes.active_color.name
            channels = obj.sna_layers[active_name].channels
            color_attribute = bm.loops.layers.color.get(active_name)
            for vert in bm.verts:
                if not vert.select:
                    continue
                alpha = calculate_alpha(neg_axis, pos_axis, min_z, max_z, obj_verts_coords[rolling_i][2])
                rolling_i += 1
                for corner in vert.link_loops:
                    if channels == 'A':
                        corner[color_attribute][0] = alpha
                        corner[color_attribute][1] = alpha
                        corner[color_attribute][2] = alpha
                    else:
                        corner[color_attribute][3] = alpha
            bmesh.update_edit_mesh(obj.data)
    # Object mode
    else:
        rolling_i = 0
        for obj in objects:
            if obj.type != "MESH":
                continue
            channels = obj.sna_layers[obj.data.color_attributes.active_color.name].channels
            vert_corners = [[] for _ in range(len(obj.data.vertices))]
            for corner in obj.data.loops:
                vert_corners[corner.vertex_index].append(corner.index)
            for i in range(len(obj.data.vertices)):
                alpha = calculate_alpha(neg_axis, pos_axis, min_z, max_z, obj_verts_coords[rolling_i + i][2])
                for corner in vert_corners[i]:
                    if channels == 'A':
                        obj.data.color_attributes.active_color.data[corner].color[0] = alpha
                        obj.data.color_attributes.active_color.data[corner].color[1] = alpha
                        obj.data.color_attributes.active_color.data[corner].color[2] = alpha
                    else:
                        obj.data.color_attributes.active_color.data[corner].color[3] = alpha
            rolling_i += len(obj.data.vertices)


"""Script for layer modifications."""
blend_map = {
    "Mix": "MIX",
    "Darken": "DARKEN",
    "Multiply": "MULTIPLY",
    "Color Burn": "BURN",
    "Lighten": "LIGHTEN",
    "Screen": "SCREEN",
    "Color Dodge": "DODGE",
    "Add": "ADD",
    "Overlay": "OVERLAY",
    "Soft Light": "SOFT_LIGHT",
    "Linear Light": "LINEAR_LIGHT",
    "Difference": "DIFFERENCE",
    "Subtract": "SUBTRACT",
    "Divide": "DIVIDE",
    "Hue": "HUE",
    "Saturation": "SATURATION",
    "Color": "COLOR",
    "Value": "VALUE"


}


def create_material_connections(material, modifications, base_layer):
    """Create connections between nodes."""
    node_tree = material.node_tree
    material_output = node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    color_input = node_tree.nodes.new(type="ShaderNodeVertexColor")
    color_input.layer_name = base_layer
    color_input.location = (-200, 0)
    nodes = []
    if modifications is not None and len(modifications) > 0:
        for modification in modifications:
            if not modification.include:
                continue
            node = node_tree.nodes.new(type="ShaderNodeMixRGB")
            modification.node_name = node.name
            node.blend_type = blend_map[modification.blend_type]
            node.inputs[0].default_value = modification.factor
            node.location = (len(nodes) * 200, 0)
            if modification.blend_layer != "flat color":
                node_input = node_tree.nodes.new(type="ShaderNodeVertexColor")
                node_input.location = (len(nodes) * 200, -200)
                modification.input_node_name = node_input.name
                node_input.layer_name = modification.blend_layer
                node_tree.links.new(node_input.outputs[0], node.inputs[2])
            else:
                modification.input_node_name = ""
                node.inputs[2].default_value = (*modification.blend_color, 1)
            if not nodes:
                node_tree.links.new(color_input.outputs[0], node.inputs[1])
            else:
                node_tree.links.new(nodes[-1].outputs[0], node.inputs[1])
            nodes.append(node)
    if len(nodes) == 0:
        nodes.append(color_input)
    material_output.location = (len(nodes) * 200, 0)
    node_tree.links.new(nodes[-1].outputs[0], material_output.inputs[0])


# https://github.com/blender/blender/blob/57013e2a44e974d307f08f41793d810a49537f96/source/blender/blenkernel/intern/material.c#L1521


def mix_color(r_col, col, blend_type, fac):
    """Mix color with modification."""
    facm = 1 - fac
    match blend_type:
        case "Mix":
            r_col[0] = facm * r_col[0] + fac * col[0]
            r_col[1] = facm * r_col[1] + fac * col[1]
            r_col[2] = facm * r_col[2] + fac * col[2]
        case "Add":
            r_col[0] += fac * col[0]
            r_col[1] += fac * col[1]
            r_col[2] += fac * col[2]
        case "Multiply":
            r_col[0] *= (facm + fac * col[0])
            r_col[1] *= (facm + fac * col[1])
            r_col[2] *= (facm + fac * col[2])
        case "Screen":
            r_col[0] = 1 - (facm + fac * (1 - col[0])) * (1 - r_col[0])
            r_col[1] = 1 - (facm + fac * (1 - col[1])) * (1 - r_col[1])
            r_col[2] = 1 - (facm + fac * (1 - col[2])) * (1 - r_col[2])
        case "Overlay":
            if r_col[0] < 0.5:
                r_col[0] *= (facm + 2 * fac * col[0])
            else:
                r_col[0] = 1 - (facm + 2 * fac * (1 - col[0])) * (1 - r_col[0])
            if r_col[1] < 0.5:
                r_col[1] *= (facm + 2 * fac * col[1])
            else:
                r_col[1] = 1 - (facm + 2 * fac * (1 - col[1])) * (1 - r_col[1])
            if r_col[2] < 0.5:
                r_col[2] *= (facm + 2 * fac * col[2])
            else:
                r_col[2] = 1 - (facm + 2 * fac * (1 - col[2])) * (1 - r_col[2])
        case "Subtract":
            r_col[0] -= fac * col[0]
            r_col[1] -= fac * col[1]
            r_col[2] -= fac * col[2]
        case "Divide":
            if col[0] != 0:
                r_col[0] = facm * r_col[0] + fac * r_col[0] / col[0]
            if col[1] != 0:
                r_col[1] = facm * r_col[1] + fac * r_col[1] / col[1]
            if col[2] != 0:
                r_col[2] = facm * r_col[2] + fac * r_col[2] / col[2]
        case "Difference":
            r_col[0] = facm * r_col[0] + fac * abs(r_col[0] - col[0])
            r_col[1] = facm * r_col[1] + fac * abs(r_col[1] - col[1])
            r_col[2] = facm * r_col[2] + fac * abs(r_col[2] - col[2])
        case "Darken":
            r_col[0] = min(r_col[0], col[0]) * fac + r_col[0] * facm
            r_col[1] = min(r_col[1], col[1]) * fac + r_col[1] * facm
            r_col[2] = min(r_col[2], col[2]) * fac + r_col[2] * facm
        case "Lighten":
            tmp = fac * col[0]
            if tmp > r_col[0]:
                r_col[0] = tmp
            tmp = fac * col[1]
            if tmp > r_col[1]:
                r_col[1] = tmp
            tmp = fac * col[2]
            if tmp > r_col[2]:
                r_col[2] = tmp
        case "Color Dodge":
            if r_col[0] != 0:
                tmp = 1 - fac * col[0]
                if tmp <= 0:
                    r_col[0] = 1
                elif (tmp := r_col[0] / tmp) > 1:
                    r_col[0] = 1
                else:
                    r_col[0] = tmp
            if r_col[1] != 0:
                tmp = 1 - fac * col[1]
                if tmp <= 0:
                    r_col[1] = 1
                elif (tmp := r_col[1] / tmp) > 1:
                    r_col[1] = 1
                else:
                    r_col[1] = tmp
            if r_col[2] != 0:
                tmp = 1 - fac * col[2]
                if tmp <= 0:
                    r_col[2] = 1
                elif (tmp := r_col[2] / tmp) > 1:
                    r_col[2] = 1
                else:
                    r_col[2] = tmp
        case "Color Burn":
            tmp = facm + fac * col[0]
            if tmp <= 0:
                r_col[0] = 0
            elif (tmp := 1 - (1 - r_col[0]) / tmp) < 0:
                r_col[0] = 0
            elif tmp > 1:
                r_col[0] = 1
            else:
                r_col[0] = tmp
            tmp = facm + fac * col[1]
            if tmp <= 0:
                r_col[1] = 0
            elif (tmp := 1 - (1 - r_col[1]) / tmp) < 0:
                r_col[1] = 0
            elif tmp > 1:
                r_col[1] = 1
            else:
                r_col[1] = tmp
            tmp = facm + fac * col[2]
            if tmp <= 0:
                r_col[2] = 0
            elif (tmp := 1 - (1 - r_col[2]) / tmp) < 0:
                r_col[2] = 0
            elif tmp > 1:
                r_col[2] = 1
            else:
                r_col[2] = tmp
        case "Hue":
            col_h, col_s, col_v = colorsys.rgb_to_hsv(col[0], col[1], col[2])
            if col_s != 0:
                r_h, r_s, r_v = colorsys.rgb_to_hsv(r_col[0], r_col[1], r_col[2])
                tmp_r, tmp_g, tmp_b = colorsys.hsv_to_rgb(col_h, r_s, r_v)
                r_col[0] = facm * r_col[0] + fac * tmp_r
                r_col[1] = facm * r_col[1] + fac * tmp_g
                r_col[2] = facm * r_col[2] + fac * tmp_b
        case "Saturation":
            r_h, r_s, r_v = colorsys.rgb_to_hsv(r_col[0], r_col[1], r_col[2])
            if r_s != 0:
                col_h, col_s, col_v = colorsys.rgb_to_hsv(col[0], col[1], col[2])
                r_col[0], r_col[1], r_col[2] = colorsys.hsv_to_rgb(r_h, facm * r_s + fac * col_s, r_v)
        case "Value":
            r_h, r_s, r_v = colorsys.rgb_to_hsv(r_col[0], r_col[1], r_col[2])
            col_h, col_s, col_v = colorsys.rgb_to_hsv(col[0], col[1], col[2])
            r_col[0], r_col[1], r_col[2] = colorsys.hsv_to_rgb(r_h, r_s, facm * r_v + fac * col_v)
        case "Color":
            col_h, col_s, col_v = colorsys.rgb_to_hsv(col[0], col[1], col[2])
            if col_s != 0:
                r_h, r_s, r_v = colorsys.rgb_to_hsv(r_col[0], r_col[1], r_col[2])
                tmp_r, tmp_g, tmp_b = colorsys.hsv_to_rgb(col_h, col_s, r_v)
                r_col[0] = facm * r_col[0] + fac * tmp_r
                r_col[1] = facm * r_col[1] + fac * tmp_g
                r_col[2] = facm * r_col[2] + fac * tmp_b
        case "Soft Light":
            scr = 1 - (1 - col[0]) * (1 - r_col[0])
            scg = 1 - (1 - col[1]) * (1 - r_col[1])
            scb = 1 - (1 - col[2]) * (1 - r_col[2])
            r_col[0] = facm * r_col[0] + fac * ((1 - r_col[0]) * col[0] * r_col[0] + r_col[0] * scr)
            r_col[1] = facm * r_col[1] + fac * ((1 - r_col[1]) * col[1] * r_col[1] + r_col[1] * scg)
            r_col[2] = facm * r_col[2] + fac * ((1 - r_col[2]) * col[2] * r_col[2] + r_col[2] * scb)
        case "Linear Light":
            if col[0] > 0.5:
                r_col[0] += fac * (2 * (col[0] - 0.5))
            else:
                r_col[0] += fac * (2 * col[0] - 1)
            if col[1] > 0.5:
                r_col[1] += fac * (2 * (col[1] - 0.5))
            else:
                r_col[1] += fac * (2 * col[1] - 1)
            if col[2] > 0.5:
                r_col[2] += fac * (2 * (col[2] - 0.5))
            else:
                r_col[2] += fac * (2 * col[2] - 1)


def aplly_color_transformation_stack(modification_stack, only_visible):
    """Apply color transformation stack."""
    obj = bpy.context.object
    if obj is None:
        return "No object selected."
    color_attributes = obj.data.color_attributes
    base_layer = color_attributes.get(modification_stack.base_layer)
    if base_layer is None:
        return "Base layer not found."
    out_layer = color_attributes.active_color
    for i, l in enumerate(obj.data.loops):
        out_layer.data[i].color = base_layer.data[i].color
    for modification in modification_stack.modifications:
        if only_visible and not modification.include:
            continue
        if modification.blend_layer == "flat color":
            for i, l in enumerate(obj.data.loops):
                mix_color(
                    out_layer.data[i].color,
                    modification.blend_color,
                    modification.blend_type,
                    modification.factor
                )
        else:
            mix_layer = color_attributes.get(modification.blend_layer)
            for i, l in enumerate(obj.data.loops):
                mix_color(
                    out_layer.data[i].color,
                    mix_layer.data[i].color,
                    modification.blend_type,
                    modification.factor
                )


def update_transformation(
    material,
    modification = None,
    base_layer = None,
    blend_type = None,
    blend_layer = None,
    blend_color = None,
    factor = None


):
    """Update transformation."""
    node_tree = material.node_tree
    if base_layer is not None:
        input_node = node_tree.nodes.get("Color Attribute")
        input_node.layer_name = base_layer
        return
    if not modification.include:
        return
    node = node_tree.nodes.get(modification.node_name)
    if blend_type is not None:
        node.blend_type = blend_map[blend_type]
        return
    if blend_layer is not None:
        if blend_layer == "flat color":
            node.inputs[2].default_value = (*modification.blend_color, 1)
            node_tree.nodes.remove(node_tree.nodes.get(modification.input_node_name))
            modification.input_node_name = ""
        else:
            if modification.input_node_name == "":
                node_input = node_tree.nodes.new(type="ShaderNodeVertexColor")
                node_input.location = (node.location[0], node.location[1] - 200)
                modification.input_node_name = node_input.name
                node_tree.links.new(node_input.outputs[0], node.inputs[2])
            node_tree.nodes.get(modification.input_node_name).layer_name = blend_layer
        return
    if blend_color is not None:
        node.inputs[2].default_value = (*blend_color, 1)
        return
    if factor is not None:
        node.inputs[0].default_value = factor
        return


def get_unique_transformation_name(name_list, name):
    """Check, if name_list containst `name`. If so, return a unique name."""
    if name.lower() == "none":
        name = "New Transformation"
    if name_list.count(name) < 2:
        return name
    i = 1
    while True:
        new_name = f"{name} {i:03}"
        if new_name not in name_list:
            return new_name
        i += 1


import sys
last_hex_color = ''


def get_color(event):
    """Get color from mouse position"""
    global last_hex_color
    fb = gpu.state.active_framebuffer_get()
    screen_buffer = fb.read_color(event.mouse_x, event.mouse_y, 1, 1, 3, 0, 'FLOAT')
    color_rgb = screen_buffer.to_list()[0][0]
    color_hex = '%02x%02x%02x'.upper() % (round(color_rgb[0]*255), round(color_rgb[1]*255), round(color_rgb[2]*255))
    last_hex_color = color_hex
    return color_rgb, color_hex


def set_clipboard():
    """Copy color to clipboard"""
    if sys.platform == 'darwin':
        cmd = f'echo {last_hex_color}|pbcopy'
    elif sys.platform == 'win32':
        cmd = f'echo {last_hex_color}|clip'
    else:
        print(f'Sorry, "{sys.platform}" is not currently supported, report it, and I will add it.')
        return
    return subprocess.check_call(cmd, shell=True)


def sna_move_color_transform_function_2575A(value):
    bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications.move(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index, int(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index + value))
    item_30EFC = bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications[int(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index + value)]
    bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index = int(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index + value)
    return


class SNA_OT_Move_Transformation_Layer_Up_50685(bpy.types.Operator):
    bl_idname = "sna.move_transformation_layer_up_50685"
    bl_label = "Move Transformation Layer Up"
    bl_description = "Move Color Transformation Layer one step higher"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_move_color_transform_function_2575A(-1)
        material_0_a22c7 = sna_refresh_default_material_function_6E2E0()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Move_Transformation_Layer_Down_9A259(bpy.types.Operator):
    bl_idname = "sna.move_transformation_layer_down_9a259"
    bl_label = "Move Transformation Layer Down"
    bl_description = "Move Color Transformation Layer one step lower"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_move_color_transform_function_2575A(1)
        material_0_360f4 = sna_refresh_default_material_function_6E2E0()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Remove_Color_Transformation_Bf376(bpy.types.Operator):
    bl_idname = "sna.remove_color_transformation_bf376"
    bl_label = "Remove Color Transformation"
    bl_description = "Remove selected Color Transformation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        for i_96EA7 in range(len(bpy.context.view_layer.objects.active.sna_modification_stacks)):
            if bpy.context.view_layer.objects.active.sna_modification_stacks[i_96EA7] == bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum]:
                bpy.context.view_layer.objects.active.sna_modification_stacks.remove(i_96EA7)
                break
        bpy.context.view_layer.objects.active.sna_modification_stack_enum = 'None'
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Add_Color_Transformation_D7C6C(bpy.types.Operator):
    bl_idname = "sna.add_color_transformation_d7c6c"
    bl_label = "Add Color Transformation"
    bl_description = "Add new Color Transformation"
    bl_options = {"REGISTER", "UNDO"}
    sna_transformation_name: bpy.props.StringProperty(name='transformation_name', description='', default='New Transformation', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        item_604E4 = bpy.context.view_layer.objects.active.sna_modification_stacks.add()
        item_604E4.name = self.sna_transformation_name
        bpy.context.view_layer.objects.active.sna_modification_stack_enum = item_604E4.name
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Remove_Color_Transformation_Layer_Dac60(bpy.types.Operator):
    bl_idname = "sna.remove_color_transformation_layer_dac60"
    bl_label = "Remove Color Transformation Layer"
    bl_description = "Remove selected Color Transformation from the active Color Transformations Stack"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        if len(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications) > bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index:
            bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications.remove(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index)
        if (bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index == len(list(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications))):
            bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index = int(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index - 1.0)
        material_0_8a341 = sna_refresh_default_material_function_6E2E0()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Add_Color_Transformation_Layer_8A10C(bpy.types.Operator):
    bl_idname = "sna.add_color_transformation_layer_8a10c"
    bl_label = "Add Color Transformation Layer"
    bl_description = "Add new Color Transformation to the active Color Transformations Stack"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        item_9DDAD = bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications.add()
        material_0_331a1 = sna_refresh_default_material_function_6E2E0()
        bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index = int(len(list(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications)) - 1.0)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Refresh_Color_Transformation_View_3912B(bpy.types.Operator):
    bl_idname = "sna.refresh_color_transformation_view_3912b"
    bl_label = "Refresh Color Transformation View"
    bl_description = "Refresh render view of Color Transformation material"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        if bpy.context.preferences.addons['vertx_artist'].preferences.sna_hide_refresh_stack_warning:
            bpy.ops.sna.refresh_color_transformation_view_with_warning_d6f51()
        else:
            bpy.ops.sna.refresh_color_transformation_view_with_warning_d6f51('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Refresh_Color_Transformation_View_With_Warning_D6F51(bpy.types.Operator):
    bl_idname = "sna.refresh_color_transformation_view_with_warning_d6f51"
    bl_label = "Refresh Color Transformation View with Warning"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        if (len(list(bpy.context.object.material_slots)) != 1):
            for i_1AD2C in range(len(bpy.context.object.material_slots)):
                bpy.ops.object.material_slot_remove('INVOKE_DEFAULT', )
            bpy.ops.object.material_slot_add('INVOKE_DEFAULT', )
        material_0_a9ec6 = sna_refresh_default_material_function_6E2E0()
        bpy.context.object.material_slots[0].material = material_0_a9ec6
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text='Warning - refreshing view WILL remove and replace all your object materials.', icon_value=2)
        layout.prop(bpy.context.preferences.addons['vertx_artist'].preferences, 'sna_hide_refresh_stack_warning', text="Don't show again", icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)


def sna_refresh_default_material_function_6E2E0():
    if (property_exists("bpy.data.materials", globals(), locals()) and 'display material vertx artist' in bpy.data.materials):
        pass
    else:
        material_227CB = bpy.data.materials.new(name='display material vertx artist', )
        bpy.data.materials['display material vertx artist'].use_nodes = True
    bpy.data.materials['display material vertx artist'].node_tree.nodes.clear()
    return_88531 = create_material_connections(material=bpy.data.materials['display material vertx artist'], modifications=eval("bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications if bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].name != 'None' else None"), base_layer=bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].base_layer)
    return bpy.data.materials['display material vertx artist']


def sna_apply_stack_function_6A3CD(only_visible):
    bpy.ops.geometry.color_attribute_add(name=eval("f'{bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].base_layer} / {bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].name}'"), domain='CORNER', data_type='BYTE_COLOR')
    return_C78D3 = aplly_color_transformation_stack(modification_stack=bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum], only_visible=only_visible)
    if (return_C78D3 != None):
        self.report({'WARNING'}, message=return_C78D3)


class SNA_OT_Apply_Color_Transformation_Stack_969Ba(bpy.types.Operator):
    bl_idname = "sna.apply_color_transformation_stack_969ba"
    bl_label = "Apply Color Transformation Stack"
    bl_description = "Create a new Color Layer from base layer, and apply the whole Color Transformation Stack"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        if eval("all(i.include for i in bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications)"):
            sna_apply_stack_function_6A3CD(False)
        else:
            bpy.ops.sna.apply_color_transformation_stack_popup_050bc('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Apply_Color_Transformation_Stack_Popup_050Bc(bpy.types.Operator):
    bl_idname = "sna.apply_color_transformation_stack_popup_050bc"
    bl_label = "Apply Color Transformation Stack Popup"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_apply_stack_function_6A3CD(eval("bpy.context.scene.sna_transformations_visible_enum == 'Only Visible'"))
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(bpy.context.scene, 'sna_transformations_visible_enum', text='Apply', icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class SNA_PT_COLOR_TRANSFORMATIONS_0C04B(bpy.types.Panel):
    bl_label = 'Color Transformations'
    bl_idname = 'SNA_PT_COLOR_TRANSFORMATIONS_0C04B'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_category = 'Color Transformations - VertX Artist'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ((bpy.context.object == None))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row_EE927 = layout.row(heading='', align=False)
        row_EE927.alert = False
        row_EE927.enabled = True
        row_EE927.active = True
        row_EE927.use_property_split = False
        row_EE927.use_property_decorate = False
        row_EE927.scale_x = 1.0
        row_EE927.scale_y = 1.0
        row_EE927.alignment = 'Expand'.upper()
        if not True: row_EE927.operator_context = "EXEC_DEFAULT"
        if (bpy.context.view_layer.objects.active.sna_modification_stack_enum != 'None'):
            split_372C2 = row_EE927.split(factor=0.9300000071525574, align=True)
            split_372C2.alert = False
            split_372C2.enabled = True
            split_372C2.active = True
            split_372C2.use_property_split = True
            split_372C2.use_property_decorate = False
            split_372C2.scale_x = 1.0
            split_372C2.scale_y = 1.0
            split_372C2.alignment = 'Right'.upper()
            if not True: split_372C2.operator_context = "EXEC_DEFAULT"
            split_372C2.prop(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum], 'name', text='', icon_value=0, emboss=True)
            split_372C2.prop(bpy.context.view_layer.objects.active, 'sna_modification_stack_enum', text='', icon_value=0, emboss=True)
        else:
            row_EE927.prop(bpy.context.view_layer.objects.active, 'sna_modification_stack_enum', text='', icon_value=0, emboss=True)
        row_1641A = row_EE927.row(heading='', align=True)
        row_1641A.alert = False
        row_1641A.enabled = True
        row_1641A.active = True
        row_1641A.use_property_split = False
        row_1641A.use_property_decorate = False
        row_1641A.scale_x = 1.0
        row_1641A.scale_y = 1.0
        row_1641A.alignment = 'Expand'.upper()
        if not True: row_1641A.operator_context = "EXEC_DEFAULT"
        row_E6592 = row_1641A.row(heading='', align=True)
        row_E6592.alert = False
        row_E6592.enabled = True
        row_E6592.active = True
        row_E6592.use_property_split = False
        row_E6592.use_property_decorate = False
        row_E6592.scale_x = 1.0
        row_E6592.scale_y = 1.0
        row_E6592.alignment = 'Expand'.upper()
        if not True: row_E6592.operator_context = "EXEC_DEFAULT"
        op = row_E6592.operator('sna.add_color_transformation_d7c6c', text='', icon_value=31, emboss=True, depress=False)
        row_037ED = row_1641A.row(heading='', align=True)
        row_037ED.alert = False
        row_037ED.enabled = (bpy.context.view_layer.objects.active.sna_modification_stack_enum != 'None')
        row_037ED.active = True
        row_037ED.use_property_split = False
        row_037ED.use_property_decorate = False
        row_037ED.scale_x = 1.0
        row_037ED.scale_y = 1.0
        row_037ED.alignment = 'Expand'.upper()
        if not True: row_037ED.operator_context = "EXEC_DEFAULT"
        op = row_037ED.operator('sna.remove_color_transformation_bf376', text='', icon_value=32, emboss=True, depress=False)
        if (bpy.context.view_layer.objects.active.sna_modification_stack_enum != 'None'):
            col_4B399 = layout.column(heading='', align=False)
            col_4B399.alert = False
            col_4B399.enabled = True
            col_4B399.active = True
            col_4B399.use_property_split = False
            col_4B399.use_property_decorate = False
            col_4B399.scale_x = 1.0
            col_4B399.scale_y = 1.0
            col_4B399.alignment = 'Expand'.upper()
            if not True: col_4B399.operator_context = "EXEC_DEFAULT"
            col_4B399.prop(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum], 'base_layer', text='Base Layer', icon_value=0, emboss=True)
            row_0BFEC = col_4B399.row(heading='', align=False)
            row_0BFEC.alert = False
            row_0BFEC.enabled = True
            row_0BFEC.active = True
            row_0BFEC.use_property_split = False
            row_0BFEC.use_property_decorate = False
            row_0BFEC.scale_x = 1.0
            row_0BFEC.scale_y = 1.0
            row_0BFEC.alignment = 'Expand'.upper()
            if not True: row_0BFEC.operator_context = "EXEC_DEFAULT"
            coll_id = display_collection_id('5FDE3', locals())
            row_0BFEC.template_list('SNA_UL_display_collection_list_5FDE3', coll_id, bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum], 'modifications', bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum], 'index', rows=4)
            col_1E393 = row_0BFEC.column(heading='', align=False)
            col_1E393.alert = False
            col_1E393.enabled = True
            col_1E393.active = True
            col_1E393.use_property_split = False
            col_1E393.use_property_decorate = False
            col_1E393.scale_x = 1.0
            col_1E393.scale_y = 1.0
            col_1E393.alignment = 'Expand'.upper()
            if not True: col_1E393.operator_context = "EXEC_DEFAULT"
            col_1E393.separator(factor=0.5)
            col_FA5A0 = col_1E393.column(heading='', align=True)
            col_FA5A0.alert = False
            col_FA5A0.enabled = True
            col_FA5A0.active = True
            col_FA5A0.use_property_split = False
            col_FA5A0.use_property_decorate = False
            col_FA5A0.scale_x = 1.0
            col_FA5A0.scale_y = 1.0
            col_FA5A0.alignment = 'Expand'.upper()
            if not True: col_FA5A0.operator_context = "EXEC_DEFAULT"
            row_2D328 = col_FA5A0.row(heading='', align=True)
            row_2D328.alert = False
            row_2D328.enabled = True
            row_2D328.active = True
            row_2D328.use_property_split = False
            row_2D328.use_property_decorate = False
            row_2D328.scale_x = 1.0
            row_2D328.scale_y = 1.0
            row_2D328.alignment = 'Expand'.upper()
            if not True: row_2D328.operator_context = "EXEC_DEFAULT"
            op = row_2D328.operator('sna.add_color_transformation_layer_8a10c', text='', icon_value=31, emboss=True, depress=False)
            row_E1A7C = col_FA5A0.row(heading='', align=True)
            row_E1A7C.alert = False
            row_E1A7C.enabled = (len(list(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications)) != 0)
            row_E1A7C.active = True
            row_E1A7C.use_property_split = False
            row_E1A7C.use_property_decorate = False
            row_E1A7C.scale_x = 1.0
            row_E1A7C.scale_y = 1.0
            row_E1A7C.alignment = 'Expand'.upper()
            if not True: row_E1A7C.operator_context = "EXEC_DEFAULT"
            op = row_E1A7C.operator('sna.remove_color_transformation_layer_dac60', text='', icon_value=32, emboss=True, depress=False)
            col_1E393.separator(factor=0.25)
            col_8B142 = col_1E393.column(heading='', align=True)
            col_8B142.alert = False
            col_8B142.enabled = True
            col_8B142.active = True
            col_8B142.use_property_split = False
            col_8B142.use_property_decorate = False
            col_8B142.scale_x = 1.0
            col_8B142.scale_y = 1.0
            col_8B142.alignment = 'Expand'.upper()
            if not True: col_8B142.operator_context = "EXEC_DEFAULT"
            row_3D284 = col_8B142.row(heading='', align=True)
            row_3D284.alert = False
            row_3D284.enabled = ((len(list(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications)) != 0) and (bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index != 0))
            row_3D284.active = True
            row_3D284.use_property_split = False
            row_3D284.use_property_decorate = False
            row_3D284.scale_x = 1.0
            row_3D284.scale_y = 1.0
            row_3D284.alignment = 'Expand'.upper()
            if not True: row_3D284.operator_context = "EXEC_DEFAULT"
            op = row_3D284.operator('sna.move_transformation_layer_up_50685', text='', icon_value=7, emboss=True, depress=False)
            row_7DD54 = col_8B142.row(heading='', align=True)
            row_7DD54.alert = False
            row_7DD54.enabled = ((len(list(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications)) != 0) and (bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].index != int(len(list(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications)) - 1.0)))
            row_7DD54.active = True
            row_7DD54.use_property_split = False
            row_7DD54.use_property_decorate = False
            row_7DD54.scale_x = 1.0
            row_7DD54.scale_y = 1.0
            row_7DD54.alignment = 'Expand'.upper()
            if not True: row_7DD54.operator_context = "EXEC_DEFAULT"
            op = row_7DD54.operator('sna.move_transformation_layer_down_9a259', text='', icon_value=5, emboss=True, depress=False)
            col_4B399.separator(factor=0.0)
            row_27C66 = col_4B399.row(heading='', align=False)
            row_27C66.alert = False
            row_27C66.enabled = True
            row_27C66.active = True
            row_27C66.use_property_split = False
            row_27C66.use_property_decorate = False
            row_27C66.scale_x = 1.0
            row_27C66.scale_y = 1.0
            row_27C66.alignment = 'Expand'.upper()
            if not True: row_27C66.operator_context = "EXEC_DEFAULT"
            op = row_27C66.operator('sna.refresh_color_transformation_view_3912b', text='Refresh Material Preview', icon_value=692, emboss=True, depress=False)
            row_5BFE5 = row_27C66.row(heading='', align=False)
            row_5BFE5.alert = False
            row_5BFE5.enabled = (len(list(bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications)) != 0)
            row_5BFE5.active = True
            row_5BFE5.use_property_split = False
            row_5BFE5.use_property_decorate = False
            row_5BFE5.scale_x = 1.0
            row_5BFE5.scale_y = 1.0
            row_5BFE5.alignment = 'Expand'.upper()
            if not True: row_5BFE5.operator_context = "EXEC_DEFAULT"
            op = row_5BFE5.operator('sna.apply_color_transformation_stack_969ba', text='Apply Stack', icon_value=36, emboss=True, depress=False)


def sna_modification_blend_layer_enum_items(self, context):
    enum_items = sna_generate_dynamic_enum_86294_F2FB4(eval("['flat color']"), [], bpy.context.object.data.color_attributes, None, [], [])
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_modification_stack_base_layer_enum_items(self, context):
    enum_items = sna_generate_dynamic_enum_86294_823FD([], [], bpy.context.object.data.color_attributes, None, [], [])
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_modification_stack_enum_enum_items(self, context):
    enum_items = sna_generate_dynamic_enum_86294_9ADD2(eval("['None']"), [], bpy.context.view_layer.objects.active.sna_modification_stacks, None, [], [])
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


class SNA_OT_Toggle_Color_Transformation_Visibility_Fc89C(bpy.types.Operator):
    bl_idname = "sna.toggle_color_transformation_visibility_fc89c"
    bl_label = "Toggle Color Transformation Visibility"
    bl_description = "Change Color Transformation Visibility"
    bl_options = {"REGISTER", "UNDO"}
    sna_modification_index: bpy.props.IntProperty(name='modification_index', description='', default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications[self.sna_modification_index].include = (not bpy.context.view_layer.objects.active.sna_modification_stacks[bpy.context.view_layer.objects.active.sna_modification_stack_enum].modifications[self.sna_modification_index].include)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Synchronize_Layers_8B7E4(bpy.types.Operator):
    bl_idname = "sna.synchronize_layers_8b7e4"
    bl_label = "Synchronize Layers"
    bl_description = "Synchronize VertX Artist Color Layers with Color Attributes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_refresh_layers_function_5BF63()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


@persistent
def depsgraph_update_post_handler_25D07(dummy):
    sna_refresh_layers_function_5BF63()


def sna_refresh_layers_function_5BF63():
    if ((bpy.context.object != None) and property_exists("bpy.context.object.data.color_attributes", globals(), locals())):
        if (len(list(bpy.context.object.data.color_attributes)) == len(list(bpy.context.view_layer.objects.active.sna_layers))):
            for i_37784 in range(len(bpy.context.object.data.color_attributes)):
                if (property_exists("bpy.context.view_layer.objects.active.sna_layers", globals(), locals()) and bpy.context.object.data.color_attributes[i_37784].name in bpy.context.view_layer.objects.active.sna_layers):
                    pass
                else:
                    list(bpy.context.view_layer.objects.active.sna_layers)[i_37784].name = bpy.context.object.data.color_attributes[i_37784].name
        else:
            if (len(list(bpy.context.object.data.color_attributes)) > len(list(bpy.context.view_layer.objects.active.sna_layers))):
                for i_3724B in range(len(bpy.context.object.data.color_attributes)):
                    if (property_exists("bpy.context.view_layer.objects.active.sna_layers", globals(), locals()) and bpy.context.object.data.color_attributes[i_3724B].name in bpy.context.view_layer.objects.active.sna_layers):
                        pass
                    else:
                        item_B5B0B = bpy.context.view_layer.objects.active.sna_layers.add()
                        item_B5B0B.name = bpy.context.object.data.color_attributes[i_3724B].name
                        break
            else:
                for i_D9405 in range(len(bpy.context.view_layer.objects.active.sna_layers)):
                    if (property_exists("bpy.context.object.data.color_attributes", globals(), locals()) and bpy.context.view_layer.objects.active.sna_layers[i_D9405].name in bpy.context.object.data.color_attributes):
                        pass
                    else:
                        for i_2070B in range(len(bpy.context.view_layer.objects.active.sna_layers)):
                            if bpy.context.view_layer.objects.active.sna_layers[i_2070B] == bpy.context.view_layer.objects.active.sna_layers[i_D9405]:
                                bpy.context.view_layer.objects.active.sna_layers.remove(i_2070B)
                                break
                        break
        return


class SNA_OT_Add_Color_Layer_436C7(bpy.types.Operator):
    bl_idname = "sna.add_color_layer_436c7"
    bl_label = "Add Color Layer"
    bl_description = "Add new Color Layer"
    bl_options = {"REGISTER", "UNDO"}
    sna_name: bpy.props.StringProperty(name='name', description='', default='', subtype='NONE', maxlen=0, update=sna_update_name_94247)
    sna_new_color: bpy.props.FloatVectorProperty(name='new_color', description='', size=3, default=(0.0, 0.0, 0.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=6)

    def sna_channels_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_channels: bpy.props.EnumProperty(name='channels', description='', items=[('RGBA', 'RGBA', '', 0, 0), ('RGB', 'RGB', '', 0, 1), ('R', 'R', '', 0, 2), ('G', 'G', '', 0, 3), ('B', 'B', '', 0, 4), ('A', 'A', '', 0, 5), ('RG', 'RG', '', 0, 6), ('RB', 'RB', '', 0, 7), ('GB', 'GB', '', 0, 8)])

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        bpy.ops.geometry.color_attribute_add(name=self.sna_name, domain='CORNER', data_type='BYTE_COLOR', color=(self.sna_new_color[0], self.sna_new_color[1], self.sna_new_color[2], 1.0))
        bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color.name].channels = self.sna_channels
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        row_99816 = layout.row(heading='Layer Name', align=False)
        row_99816.alert = False
        row_99816.enabled = True
        row_99816.active = True
        row_99816.use_property_split = False
        row_99816.use_property_decorate = False
        row_99816.scale_x = 1.0
        row_99816.scale_y = 1.0
        row_99816.alignment = 'Expand'.upper()
        if not True: row_99816.operator_context = "EXEC_DEFAULT"
        row_99816.prop(self, 'sna_name', text='', icon_value=0, emboss=True)
        row_E1D31 = layout.row(heading='Base Color', align=False)
        row_E1D31.alert = False
        row_E1D31.enabled = True
        row_E1D31.active = True
        row_E1D31.use_property_split = False
        row_E1D31.use_property_decorate = False
        row_E1D31.scale_x = 1.0
        row_E1D31.scale_y = 1.0
        row_E1D31.alignment = 'Expand'.upper()
        if not True: row_E1D31.operator_context = "EXEC_DEFAULT"
        row_E1D31.prop(self, 'sna_new_color', text='', icon_value=0, emboss=True)
        row_EE37C = layout.row(heading='Channels', align=False)
        row_EE37C.alert = False
        row_EE37C.enabled = True
        row_EE37C.active = True
        row_EE37C.use_property_split = False
        row_EE37C.use_property_decorate = False
        row_EE37C.scale_x = 1.0
        row_EE37C.scale_y = 1.0
        row_EE37C.alignment = 'Expand'.upper()
        if not True: row_EE37C.operator_context = "EXEC_DEFAULT"
        row_EE37C.prop(self, 'sna_channels', text='', icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class SNA_OT_Select_Rgba_Layer_08766(bpy.types.Operator):
    bl_idname = "sna.select_rgba_layer_08766"
    bl_label = "Select RGBA Layer"
    bl_description = "Select RGBA layer to bake Alpha into"
    bl_options = {"REGISTER", "UNDO"}

    def sna_rgba_layers_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_rgba_layers: bpy.props.EnumProperty(name='rgba_layers', description='', items=sna_rgba_layers_enum_items)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_bake_alpha_function_B8766('')
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(None, 'None', text='', icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class SNA_OT_Extract_Alpha_50Ab0(bpy.types.Operator):
    bl_idname = "sna.extract_alpha_50ab0"
    bl_label = "Extract Alpha"
    bl_description = "Create a new alpha layer from the selected RGBA layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        layers['sna_active_obj'] = bpy.context.view_layer.objects.active
        for i_734E3 in range(len(bpy.context.view_layer.objects.selected)):
            bpy.context.view_layer.objects.active = bpy.context.view_layer.objects.selected[i_734E3]
            if (len(list(bpy.context.view_layer.objects.active.sna_layers)) == 0):
                bpy.ops.geometry.color_attribute_add(name='Attribute', domain='CORNER', data_type='BYTE_COLOR')
            if (bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].channels == 'RGBA'):
                bpy.ops.sna.add_layer_af10a(sna_layer_name=bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].name + '_alpha', sna_channels='A', sna_r_channel='None', sna_g_channel='None', sna_b_channel='None', sna_a_channel=bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].name, sna_r_channel_value=0.0, sna_g_channel_value=0.0, sna_b_channel_value=0.0, sna_a_channel_value=0.0, sna_r_gamma='None', sna_g_gamma='None', sna_b_gamma='None', sna_a_gamma='None')
        bpy.context.view_layer.objects.active = layers['sna_active_obj']
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Bake_Alpha_A245B(bpy.types.Operator):
    bl_idname = "sna.bake_alpha_a245b"
    bl_label = "Bake Alpha"
    bl_description = "Write the Alpha layer into the original RGBA layer. Will ask to select RGBA layer if it can't be detected automatically"
    bl_options = {"REGISTER", "UNDO"}
    sna_layer_name: bpy.props.StringProperty(name='layer_name', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        layers['sna_active_obj'] = bpy.context.view_layer.objects.active
        for i_DF0DA in range(len(bpy.context.view_layer.objects.selected)):
            bpy.context.view_layer.objects.active = bpy.context.view_layer.objects.selected[i_DF0DA]
            if (len(list(bpy.context.view_layer.objects.active.sna_layers)) == 0):
                bpy.ops.geometry.color_attribute_add(name='Attribute', domain='CORNER', data_type='BYTE_COLOR')
            if (bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].channels == 'A'):
                sna_bake_alpha_function_B8766(self.sna_layer_name)
        bpy.context.view_layer.objects.active = layers['sna_active_obj']
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_bake_alpha_function_B8766(layer_name):
    if (layer_name == 'None'):
        pass
    else:
        if (layer_name == ''):
            if ((property_exists("bpy.context.view_layer.objects.active.sna_layers", globals(), locals()) and eval("bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].name.split('_alpha')[0]") in bpy.context.view_layer.objects.active.sna_layers) and (bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].name != eval("bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].name.split('_alpha')[0]"))):
                sna_bake_alpha_function_B8766(eval("bpy.context.view_layer.objects.active.sna_layers[bpy.context.object.data.color_attributes.active_color_index].name.split('_alpha')[0]"))
            else:
                bpy.ops.sna.select_rgba_layer_08766('INVOKE_DEFAULT', sna_rgba_layers='NONE')
        else:
            layers_ui['sna_temp_layer_idx'] = bpy.context.object.data.color_attributes.active_color_index
            bpy.context.object.data.color_attributes.active_color_index = bpy.context.view_layer.objects.active.sna_layers.find(layer_name)
            return_1228E = combine_layers(channels='NONE', channels_list=[layer_name, layer_name, layer_name, bpy.context.view_layer.objects.active.sna_layers[layers_ui['sna_temp_layer_idx']].name], channels_values=[], channels_gamma=['None', 'None', 'None', 'None'], layers=bpy.context.view_layer.objects.active.sna_layers)
            bpy.context.object.data.color_attributes.active_color_index = layers_ui['sna_temp_layer_idx']
            bpy.ops.geometry.color_attribute_remove('INVOKE_DEFAULT', )
            bpy.context.object.data.color_attributes.active_color_index = bpy.context.view_layer.objects.active.sna_layers.find(layer_name)


def sna_generate_layers_enum_function_463EB(allowed_layers, channel_list):
    exp_D029D = channel_list = [['None', 'None', '', 0]]
    for i_093E9 in range(len(bpy.context.view_layer.objects.active.sna_layers)):
        if bpy.context.view_layer.objects.active.sna_layers[i_093E9].channels in list(allowed_layers):
            exp_A67C5 = channel_list.append([bpy.context.view_layer.objects.active.sna_layers[i_093E9].name, bpy.context.view_layer.objects.active.sna_layers[i_093E9].name, '', 0])
    return eval("channel_list")


def sna_g_channel_enum_items(self, context):
    enum_items = sna_generate_layers_enum_function_463EB({'RGB', 'GB', 'RG', 'RGBA', 'G'}, eval("g_channel_list"))
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


exec('r_channel_list = []')
exec('g_channel_list = []')
exec('b_channel_list = []')
exec('a_channel_list = []')
exec('rgba_channel_list = []')


def sna_a_channel_enum_items(self, context):
    enum_items = sna_generate_layers_enum_function_463EB({'RGBA', 'A'}, eval("a_channel_list"))
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_r_channel_enum_items(self, context):
    enum_items = sna_generate_layers_enum_function_463EB({'RGB', 'RG', 'RGBA', 'RB', 'R'}, eval("r_channel_list"))
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_b_channel_enum_items(self, context):
    enum_items = sna_generate_layers_enum_function_463EB({'RGB', 'GB', 'B', 'RGBA', 'RB'}, eval("b_channel_list"))
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


class SNA_PT_COLOR_LAYERS_B79C5(bpy.types.Panel):
    bl_label = 'Color Layers'
    bl_idname = 'SNA_PT_COLOR_LAYERS_B79C5'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_category = 'Color Layers - VertX Artist'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ((bpy.context.object == None))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        if ((bpy.context.object != None) and (bpy.context.object.data != None) and (bpy.context.object.data.color_attributes.active_color != None)):
            pass
        else:
            row_72BB1 = layout.row(heading='', align=False)
            row_72BB1.alert = True
            row_72BB1.enabled = True
            row_72BB1.active = True
            row_72BB1.use_property_split = False
            row_72BB1.use_property_decorate = False
            row_72BB1.scale_x = 1.0
            row_72BB1.scale_y = 1.0
            row_72BB1.alignment = 'Expand'.upper()
            if not True: row_72BB1.operator_context = "EXEC_DEFAULT"
            op = row_72BB1.operator('sna.add_layer_af10a', text='Add Color Layer', icon_value=31, emboss=True, depress=False)
            op.sna_r_gamma = 'None'
            op.sna_g_gamma = 'None'
            op.sna_b_gamma = 'None'
            op.sna_a_gamma = 'None'
        if (len(list(bpy.context.object.data.color_attributes)) == len(list(bpy.context.view_layer.objects.active.sna_layers))):
            pass
        else:
            row_88FB8 = layout.row(heading='', align=False)
            row_88FB8.alert = True
            row_88FB8.enabled = True
            row_88FB8.active = True
            row_88FB8.use_property_split = False
            row_88FB8.use_property_decorate = False
            row_88FB8.scale_x = 1.0
            row_88FB8.scale_y = 1.0
            row_88FB8.alignment = 'Expand'.upper()
            if not True: row_88FB8.operator_context = "EXEC_DEFAULT"
            op = row_88FB8.operator('sna.synchronize_layers_8b7e4', text='Refresh', icon_value=692, emboss=True, depress=False)
        row_791E5 = layout.row(heading='', align=False)
        row_791E5.alert = False
        row_791E5.enabled = True
        row_791E5.active = True
        row_791E5.use_property_split = False
        row_791E5.use_property_decorate = False
        row_791E5.scale_x = 1.0
        row_791E5.scale_y = 1.0
        row_791E5.alignment = 'Expand'.upper()
        if not True: row_791E5.operator_context = "EXEC_DEFAULT"
        coll_id = display_collection_id('CEEB3', locals())
        row_791E5.template_list('SNA_UL_display_collection_list_CEEB3', coll_id, bpy.context.view_layer.objects.active, 'sna_layers', bpy.context.object.data.color_attributes, 'active_color_index', rows=4)
        col_E9074 = row_791E5.column(heading='', align=False)
        col_E9074.alert = False
        col_E9074.enabled = True
        col_E9074.active = True
        col_E9074.use_property_split = False
        col_E9074.use_property_decorate = False
        col_E9074.scale_x = 1.0
        col_E9074.scale_y = 1.0
        col_E9074.alignment = 'Expand'.upper()
        if not True: col_E9074.operator_context = "EXEC_DEFAULT"
        col_9EEF1 = col_E9074.column(heading='', align=True)
        col_9EEF1.alert = False
        col_9EEF1.enabled = True
        col_9EEF1.active = True
        col_9EEF1.use_property_split = False
        col_9EEF1.use_property_decorate = False
        col_9EEF1.scale_x = 1.0
        col_9EEF1.scale_y = 1.0
        col_9EEF1.alignment = 'Expand'.upper()
        if not True: col_9EEF1.operator_context = "EXEC_DEFAULT"
        op = col_9EEF1.operator('sna.add_layer_af10a', text='', icon_value=31, emboss=True, depress=False)
        op.sna_r_gamma = 'None'
        op.sna_g_gamma = 'None'
        op.sna_b_gamma = 'None'
        op.sna_a_gamma = 'None'
        op = col_9EEF1.operator('geometry.color_attribute_remove', text='', icon_value=32, emboss=True, depress=False)
        col_E9074.separator(factor=0.25)
        op = col_E9074.operator('sna.toggle_layer_editing_17bff', text='', icon_value=197, emboss=True, depress=bpy.context.view_layer.objects.active.sna_enable_editing)
        layout_function = layout
        sna_extractbake_function_95836(layout_function, 'Extract Alpha', 'Bake Alpha')


class SNA_OT_Toggle_Render_Color_Layer_7A12B(bpy.types.Operator):
    bl_idname = "sna.toggle_render_color_layer_7a12b"
    bl_label = "Toggle Render Color Layer"
    bl_description = "Set Color Attribute used for rendering, and Color Transformation preview"
    bl_options = {"REGISTER", "UNDO"}
    sna_layer_name: bpy.props.StringProperty(name='layer_name', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        bpy.ops.geometry.color_attribute_render_set('INVOKE_DEFAULT', name=self.sna_layer_name)
        material_0_bba46 = sna_refresh_default_material_function_6E2E0()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Toggle_Layer_Editing_17Bff(bpy.types.Operator):
    bl_idname = "sna.toggle_layer_editing_17bff"
    bl_label = "Toggle Layer Editing"
    bl_description = "Enable or disable channels editing"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        if bpy.context.view_layer.objects.active.sna_enable_editing:
            bpy.ops.sna.toggle_layer_editing_with_warning_6b0ab()
        else:
            if bpy.context.preferences.addons['vertx_artist'].preferences.sna_hide_edit_warning:
                bpy.ops.sna.toggle_layer_editing_with_warning_6b0ab()
            else:
                bpy.ops.sna.toggle_layer_editing_with_warning_6b0ab('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Toggle_Layer_Editing_With_Warning_6B0Ab(bpy.types.Operator):
    bl_idname = "sna.toggle_layer_editing_with_warning_6b0ab"
    bl_label = "Toggle Layer Editing with Warning"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        bpy.context.view_layer.objects.active.sna_enable_editing = (not bpy.context.view_layer.objects.active.sna_enable_editing)
        if bpy.context and bpy.context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text='Warning - editing layer channels may result in unwanted behavior.', icon_value=2)
        layout.prop(bpy.context.preferences.addons['vertx_artist'].preferences, 'sna_hide_edit_warning', text="Don't show again", icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)


@persistent
def depsgraph_update_pre_handler_D69F3(dummy):
    pass


class SNA_OT_Refresh_Fe2A7(bpy.types.Operator):
    bl_idname = "sna.refresh_fe2a7"
    bl_label = "Refresh"
    bl_description = "Force refresh object colors"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        return_AC2E7 = refresh_object_colors()
        if (return_AC2E7[0] == None):
            pass
        else:
            object_colors['sna_ignore_color_change'] = True
            while (len(list(bpy.context.scene.sna_object_colors)) > len(return_AC2E7[1])):
                if len(bpy.context.scene.sna_object_colors) > int(len(list(bpy.context.scene.sna_object_colors)) - 1.0):
                    bpy.context.scene.sna_object_colors.remove(int(len(list(bpy.context.scene.sna_object_colors)) - 1.0))
            while (len(list(bpy.context.scene.sna_object_colors)) < len(return_AC2E7[1])):
                item_8A78A = bpy.context.scene.sna_object_colors.add()
                item_8A78A.index = int(len(list(bpy.context.scene.sna_object_colors)) - 1.0)
            bpy.context.scene.sna_active_color_index = return_AC2E7[0]
            for i_8A152 in range(len(return_AC2E7[1])):
                bpy.context.scene.sna_object_colors[i_8A152].color = return_AC2E7[1][i_8A152]
        object_colors['sna_ignore_color_change'] = False
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Showhide_Object_Colors_C831C(bpy.types.Operator):
    bl_idname = "sna.showhide_object_colors_c831c"
    bl_label = "Show/Hide Object Colors"
    bl_description = "Show or Hide Object colors"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        bpy.context.scene.sna_show_object_colors = (not bpy.context.scene.sna_show_object_colors)
        if (bpy.context.scene.sna_show_object_colors and 'EDIT_MESH'==bpy.context.mode):
            bpy.ops.sna.refresh_fe2a7('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Select_By_Color_Ee838(bpy.types.Operator):
    bl_idname = "sna.select_by_color_ee838"
    bl_label = "Select By Color"
    bl_description = "Select only the vertices/polygons with the specified color, depending on the selection tolerance"
    bl_options = {"REGISTER", "UNDO"}
    sna_selection_tolerance: bpy.props.FloatProperty(name='selection_tolerance', description='', default=0.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2)
    sna_select_color: bpy.props.FloatVectorProperty(name='select_color', description='', options={'HIDDEN'}, size=3, default=(0.0, 0.0, 0.0), subtype='COLOR_GAMMA', unit='NONE', min=0.0, max=1.0, step=3, precision=6)
    sna_select_color_idx: bpy.props.IntProperty(name='select_color_idx', description='', options={'HIDDEN'}, default=0, subtype='NONE')
    sna_ignore_hue: bpy.props.BoolProperty(name='ignore_hue', description='', default=False)
    sna_ignore_saturation: bpy.props.BoolProperty(name='ignore_saturation', description='', default=False)
    sna_ignore_value: bpy.props.BoolProperty(name='ignore_value', description='', default=False)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        return_198A2 = select_by_color(tolerance=self.sna_selection_tolerance, color=self.sna_select_color, color_idx=self.sna_select_color_idx, ignore_hsv=(self.sna_ignore_hue, self.sna_ignore_saturation, self.sna_ignore_value))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Checkpoint_1810D(bpy.types.Operator):
    bl_idname = "sna.checkpoint_1810d"
    bl_label = "Checkpoint"
    bl_description = "Create a checkpoint with an undo step"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_object_colors_function_C6050(layout_function, ):
    box_8F097 = layout_function.box()
    box_8F097.alert = False
    box_8F097.enabled = True
    box_8F097.active = True
    box_8F097.use_property_split = False
    box_8F097.use_property_decorate = False
    box_8F097.alignment = 'Expand'.upper()
    box_8F097.scale_x = 1.0
    box_8F097.scale_y = 1.0
    if not True: box_8F097.operator_context = "EXEC_DEFAULT"
    row_AFC4A = box_8F097.row(heading='', align=False)
    row_AFC4A.alert = False
    row_AFC4A.enabled = True
    row_AFC4A.active = True
    row_AFC4A.use_property_split = False
    row_AFC4A.use_property_decorate = False
    row_AFC4A.scale_x = 1.0
    row_AFC4A.scale_y = 1.0
    row_AFC4A.alignment = 'Expand'.upper()
    if not True: row_AFC4A.operator_context = "EXEC_DEFAULT"
    row_AFC4A.label(text='Adjust Object Colors', icon_value=202)
    op = row_AFC4A.operator('sna.showhide_object_colors_c831c', text='', icon_value=eval("254 if bpy.context.scene.sna_show_object_colors else 253"), emboss=False, depress=True)
    if bpy.context.scene.sna_show_object_colors:
        row_A5B7C = row_AFC4A.row(heading='', align=True)
        row_A5B7C.alert = False
        row_A5B7C.enabled = True
        row_A5B7C.active = True
        row_A5B7C.use_property_split = False
        row_A5B7C.use_property_decorate = False
        row_A5B7C.scale_x = 1.0
        row_A5B7C.scale_y = 1.0
        row_A5B7C.alignment = 'Expand'.upper()
        if not True: row_A5B7C.operator_context = "EXEC_DEFAULT"
        op = row_A5B7C.operator('sna.checkpoint_1810d', text='', icon_value=_icons['white_flag.png'].icon_id, emboss=True, depress=False)
        op = row_A5B7C.operator('sna.refresh_fe2a7', text='', icon_value=692, emboss=True, depress=False)
    if bpy.context.scene.sna_show_object_colors:
        split_5A9D3 = box_8F097.split(factor=0.5, align=False)
        split_5A9D3.alert = False
        split_5A9D3.enabled = True
        split_5A9D3.active = True
        split_5A9D3.use_property_split = False
        split_5A9D3.use_property_decorate = False
        split_5A9D3.scale_x = 1.0
        split_5A9D3.scale_y = 1.0
        split_5A9D3.alignment = 'Expand'.upper()
        if not True: split_5A9D3.operator_context = "EXEC_DEFAULT"
        split_5A9D3.label(text='Active Color:', icon_value=0)
        row_0850F = split_5A9D3.row(heading='', align=True)
        row_0850F.alert = False
        row_0850F.enabled = True
        row_0850F.active = True
        row_0850F.use_property_split = False
        row_0850F.use_property_decorate = False
        row_0850F.scale_x = 1.0
        row_0850F.scale_y = 1.0
        row_0850F.alignment = 'Expand'.upper()
        if not True: row_0850F.operator_context = "EXEC_DEFAULT"
        if (len(list(bpy.context.scene.sna_object_colors)) == 0):
            pass
        else:
            op = row_0850F.operator('sna.select_by_color_ee838', text='', icon_value=256, emboss=True, depress=False)
            op.sna_selection_tolerance = bpy.context.preferences.addons['vertx_artist'].preferences.sna_selection_tolerance
            op.sna_select_color = bpy.context.scene.sna_object_colors[bpy.context.scene.sna_active_color_index].color
            op.sna_select_color_idx = bpy.context.scene.sna_object_colors[bpy.context.scene.sna_active_color_index].index
            op.sna_ignore_hue = False
            op.sna_ignore_saturation = False
            op.sna_ignore_value = False
            row_0850F.prop(bpy.context.scene.sna_object_colors[bpy.context.scene.sna_active_color_index], 'color', text='', icon_value=0, emboss=True)
    if bpy.context.scene.sna_show_object_colors:
        box_8F097.label(text='Object Colors:', icon_value=251)
    if bpy.context.scene.sna_show_object_colors:
        grid_95E1F = box_8F097.grid_flow(columns=bpy.context.preferences.addons['vertx_artist'].preferences.sna_object_color_columns, row_major=True, even_columns=False, even_rows=False, align=False)
        grid_95E1F.enabled = True
        grid_95E1F.active = True
        grid_95E1F.use_property_split = False
        grid_95E1F.use_property_decorate = False
        grid_95E1F.alignment = 'Expand'.upper()
        grid_95E1F.scale_x = 1.0
        grid_95E1F.scale_y = 1.0
        if not True: grid_95E1F.operator_context = "EXEC_DEFAULT"
        for i_39762 in range(len(bpy.context.scene.sna_object_colors)):
            row_6B9B3 = grid_95E1F.row(heading='', align=True)
            row_6B9B3.alert = False
            row_6B9B3.enabled = True
            row_6B9B3.active = True
            row_6B9B3.use_property_split = False
            row_6B9B3.use_property_decorate = False
            row_6B9B3.scale_x = 1.0
            row_6B9B3.scale_y = 1.0
            row_6B9B3.alignment = 'Expand'.upper()
            if not True: row_6B9B3.operator_context = "EXEC_DEFAULT"
            op = row_6B9B3.operator('sna.select_by_color_ee838', text='', icon_value=256, emboss=True, depress=False)
            op.sna_selection_tolerance = bpy.context.preferences.addons['vertx_artist'].preferences.sna_selection_tolerance
            op.sna_select_color = bpy.context.scene.sna_object_colors[i_39762].color
            op.sna_select_color_idx = bpy.context.scene.sna_object_colors[i_39762].index
            op.sna_ignore_hue = False
            op.sna_ignore_saturation = False
            op.sna_ignore_value = False
            row_6B9B3.prop(bpy.context.scene.sna_object_colors[i_39762], 'color', text='', icon_value=0, emboss=True)


def sna_object_colors_object_mode_286C1(layout_function, ):
    box_10F49 = layout_function.box()
    box_10F49.alert = False
    box_10F49.enabled = True
    box_10F49.active = True
    box_10F49.use_property_split = False
    box_10F49.use_property_decorate = False
    box_10F49.alignment = 'Expand'.upper()
    box_10F49.scale_x = 1.0
    box_10F49.scale_y = 1.0
    if not True: box_10F49.operator_context = "EXEC_DEFAULT"
    row_CF32D = box_10F49.row(heading='', align=False)
    row_CF32D.alert = False
    row_CF32D.enabled = True
    row_CF32D.active = True
    row_CF32D.use_property_split = False
    row_CF32D.use_property_decorate = False
    row_CF32D.scale_x = 1.0
    row_CF32D.scale_y = 1.0
    row_CF32D.alignment = 'Expand'.upper()
    if not True: row_CF32D.operator_context = "EXEC_DEFAULT"
    row_CF32D.label(text='Adjust Object Colors', icon_value=202)
    op = row_CF32D.operator('sna.showhide_object_colors_c831c', text='', icon_value=eval("254 if bpy.context.scene.sna_show_object_colors else 253"), emboss=False, depress=True)


def sna_move_palette_color_function_797B4(palette_index, palette_color_index, value):
    list(bpy.context.scene.sna_palettes)[palette_index].palette_colors.move(palette_color_index, int(max(0.0, min(int(palette_color_index + value), int(len(list(list(bpy.context.scene.sna_palettes)[palette_index].palette_colors)) - 1.0)))))
    item_AE78F = list(bpy.context.scene.sna_palettes)[palette_index].palette_colors[int(max(0.0, min(int(palette_color_index + value), int(len(list(list(bpy.context.scene.sna_palettes)[palette_index].palette_colors)) - 1.0))))]
    list(bpy.context.scene.sna_palettes)[palette_index].index = int(max(0.0, min(int(palette_color_index + value), int(len(list(list(bpy.context.scene.sna_palettes)[palette_index].palette_colors)) - 1.0))))
    return


class SNA_OT_Remove_Palette_B653B(bpy.types.Operator):
    bl_idname = "sna.remove_palette_b653b"
    bl_label = "Remove Palette"
    bl_description = "Remove this palette"
    bl_options = {"REGISTER", "UNDO"}
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        if len(bpy.context.scene.sna_palettes) > self.sna_palette_index:
            bpy.context.scene.sna_palettes.remove(self.sna_palette_index)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Create_Palette_098Ec(bpy.types.Operator):
    bl_idname = "sna.create_palette_098ec"
    bl_label = "Create Palette"
    bl_description = "Create empty palette"
    bl_options = {"REGISTER", "UNDO"}
    sna_name: bpy.props.StringProperty(name='name', description='Name of the added palette', default='New Palette', subtype='NONE', maxlen=0, update=sna_update_name_94247)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        item_D3C96 = bpy.context.scene.sna_palettes.add()
        item_D3C96.name = self.sna_name
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Add_Palette_Color_631C1(bpy.types.Operator):
    bl_idname = "sna.add_palette_color_631c1"
    bl_label = "Add palette_color"
    bl_description = "Add single palette color into the palette"
    bl_options = {"REGISTER", "UNDO"}
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)
    sna_palette_color_index: bpy.props.IntProperty(name='palette_color_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)
    sna_color_name: bpy.props.StringProperty(name='color_name', description='', default='', subtype='NONE', maxlen=0)
    sna_new_color: bpy.props.FloatVectorProperty(name='new_color', description='', size=3, default=(0.0, 0.0, 0.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=6)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        item_A0D4B = list(bpy.context.scene.sna_palettes)[self.sna_palette_index].palette_colors.add()
        item_A0D4B.name = self.sna_color_name
        item_A0D4B.color = self.sna_new_color
        sna_move_palette_color_function_797B4(self.sna_palette_index, int(len(list(list(bpy.context.scene.sna_palettes)[self.sna_palette_index].palette_colors)) - 1.0), int(self.sna_palette_color_index + int(0.0 - -2.0 - len(list(list(bpy.context.scene.sna_palettes)[self.sna_palette_index].palette_colors)))))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Remove_Palette_Color_D6Fa3(bpy.types.Operator):
    bl_idname = "sna.remove_palette_color_d6fa3"
    bl_label = "Remove palette_color"
    bl_description = "Remove single palette color from the palette"
    bl_options = {"REGISTER", "UNDO"}
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)
    sna_palette_color_index: bpy.props.IntProperty(name='palette_color_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        if len(list(bpy.context.scene.sna_palettes)[self.sna_palette_index].palette_colors) > self.sna_palette_color_index:
            list(bpy.context.scene.sna_palettes)[self.sna_palette_index].palette_colors.remove(self.sna_palette_color_index)
        if (list(bpy.context.scene.sna_palettes)[self.sna_palette_index].index >= len(list(list(bpy.context.scene.sna_palettes)[self.sna_palette_index].palette_colors))):
            list(bpy.context.scene.sna_palettes)[self.sna_palette_index].index = int(len(list(list(bpy.context.scene.sna_palettes)[self.sna_palette_index].palette_colors)) - 1.0)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Move_Palette_Up_193F8(bpy.types.Operator):
    bl_idname = "sna.move_palette_up_193f8"
    bl_label = "Move palette Up"
    bl_description = "Move palette one step higher"
    bl_options = {"REGISTER", "UNDO"}
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_move_palette_function_DBA6A(self.sna_palette_index, -1)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_move_palette_function_DBA6A(palette_index, value):
    bpy.context.scene.sna_palettes.move(palette_index, int(palette_index + value))
    item_C749F = bpy.context.scene.sna_palettes[int(palette_index + value)]
    return


class SNA_OT_Move_Palette_Down_Cce25(bpy.types.Operator):
    bl_idname = "sna.move_palette_down_cce25"
    bl_label = "Move palette Down"
    bl_description = "Move palette one step lower"
    bl_options = {"REGISTER", "UNDO"}
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_move_palette_function_DBA6A(self.sna_palette_index, 1)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Move_Palette_Color_Down_00593(bpy.types.Operator):
    bl_idname = "sna.move_palette_color_down_00593"
    bl_label = "Move palette_color Down"
    bl_description = "Move palette color one step lower"
    bl_options = {"REGISTER", "UNDO"}
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)
    sna_palette_color_index: bpy.props.IntProperty(name='palette_color_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_move_palette_color_function_797B4(self.sna_palette_index, self.sna_palette_color_index, 1)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Move_Palette_Color_Up_1D220(bpy.types.Operator):
    bl_idname = "sna.move_palette_color_up_1d220"
    bl_label = "Move palette_color Up"
    bl_description = "Move palette color one step higher"
    bl_options = {"REGISTER", "UNDO"}
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)
    sna_palette_color_index: bpy.props.IntProperty(name='palette_color_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_move_palette_color_function_797B4(self.sna_palette_index, self.sna_palette_color_index, -1)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Import_Palette_26C39(bpy.types.Operator, ImportHelper):
    bl_idname = "sna.import_palette_26c39"
    bl_label = "Import Palette"
    bl_description = "Import a new palette and add it to the bottom"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty( default='*.ccb;*.colors;*.gpl', options={'HIDDEN'} )

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_import_palette_function_DEFBA(self.filepath)
        return {"FINISHED"}


class SNA_OT_Import_Replace_Palette_A4Fca(bpy.types.Operator, ImportHelper):
    bl_idname = "sna.import_replace_palette_a4fca"
    bl_label = "Import Replace Palette"
    bl_description = "Import a new palette to replace this one"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty( default='*.ccb;*.colors;*.gpl', options={'HIDDEN'} )
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        sna_import_palette_function_DEFBA(self.filepath)
        if len(bpy.context.scene.sna_palettes) > self.sna_palette_index:
            bpy.context.scene.sna_palettes.remove(self.sna_palette_index)
        bpy.context.scene.sna_palettes.move(int(len(list(bpy.context.scene.sna_palettes)) - 1.0), self.sna_palette_index)
        item_FB648 = bpy.context.scene.sna_palettes[self.sna_palette_index]
        return {"FINISHED"}


class SNA_OT_Export_Palettes_D17D2(bpy.types.Operator):
    bl_idname = "sna.export_palettes_d17d2"
    bl_label = "Export Palettes"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        op = layout.operator('sna.export_ccb_palette_e3da4', text='Export as .ccb', icon_value=707, emboss=True, depress=False)
        op.sna_palette_index = self.sna_palette_index
        op = layout.operator('sna.export_gpl_palette_b20a0', text='Export as .gpl', icon_value=707, emboss=True, depress=False)
        op.sna_palette_index = self.sna_palette_index

    def invoke(self, context, event):
        context.window_manager.invoke_props_popup(self, event)
        return self.execute(context)


class SNA_OT_Export_Ccb_Palette_E3Da4(bpy.types.Operator, ExportHelper):
    bl_idname = "sna.export_ccb_palette_e3da4"
    bl_label = "Export .ccb Palette"
    bl_description = "Export selected Palette as .ccb"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty( default='*.ccb;*.colors;*.gpl', options={'HIDDEN'} )
    filename_ext = '.ccb'
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        return_8B70B = export_palette(colors=bpy.context.scene.sna_palettes[self.sna_palette_index].palette_colors, path=self.filepath, ccb_header_path=os.path.join(os.path.dirname(__file__), 'assets', 'ccb_header.txt'))
        return {"FINISHED"}


class SNA_OT_Export_Gpl_Palette_B20A0(bpy.types.Operator, ExportHelper):
    bl_idname = "sna.export_gpl_palette_b20a0"
    bl_label = "Export .gpl Palette"
    bl_description = "Export selected Palette as .gpl"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty( default='*.ccb;*.colors;*.gpl', options={'HIDDEN'} )
    filename_ext = '.gpl'
    sna_palette_index: bpy.props.IntProperty(name='palette_index', description='', options={'HIDDEN'}, default=0, subtype='NONE', min=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        return_9F27A = export_palette(colors=bpy.context.scene.sna_palettes[self.sna_palette_index].palette_colors, path=self.filepath)
        return {"FINISHED"}


def sna_import_palette_function_DEFBA(Input):
    return_B500C = import_palette(path=Input)
    if (return_B500C[0] != None):
        item_4A115 = bpy.context.scene.sna_palettes.add()
        item_4A115.name = return_B500C[0]
        for i_E0D13 in range(len(return_B500C[1])):
            item_8115F = item_4A115.palette_colors.add()
            item_8115F.name = return_B500C[1][i_E0D13]
            item_8115F.color = return_B500C[2][i_E0D13]
        return


def sna_display_palettes_1AEAA(layout_function, ):
    grid_2E34D = layout_function.grid_flow(columns=bpy.context.preferences.addons['vertx_artist'].preferences.sna_palette_grid_columns, row_major=True, even_columns=False, even_rows=False, align=False)
    grid_2E34D.enabled = True
    grid_2E34D.active = True
    grid_2E34D.use_property_split = False
    grid_2E34D.use_property_decorate = False
    grid_2E34D.alignment = 'Expand'.upper()
    grid_2E34D.scale_x = 1.0
    grid_2E34D.scale_y = 1.0
    if not True: grid_2E34D.operator_context = "EXEC_DEFAULT"
    for i_0CF39 in range(len(bpy.context.scene.sna_palettes)):
        box_09C28 = grid_2E34D.box()
        box_09C28.alert = False
        box_09C28.enabled = True
        box_09C28.active = True
        box_09C28.use_property_split = False
        box_09C28.use_property_decorate = False
        box_09C28.alignment = 'Expand'.upper()
        box_09C28.scale_x = 1.0
        box_09C28.scale_y = 1.0
        if not True: box_09C28.operator_context = "EXEC_DEFAULT"
        box_09C28.prop(bpy.context.scene.sna_palettes[i_0CF39], 'name', text='', icon_value=54, emboss=True)
        if (bpy.context.preferences.addons['vertx_artist'].preferences.sna_color_grid_columns != 1):
            grid_203F1 = box_09C28.grid_flow(columns=bpy.context.preferences.addons['vertx_artist'].preferences.sna_color_grid_columns, row_major=True, even_columns=False, even_rows=False, align=False)
            grid_203F1.enabled = True
            grid_203F1.active = True
            grid_203F1.use_property_split = False
            grid_203F1.use_property_decorate = False
            grid_203F1.alignment = 'Expand'.upper()
            grid_203F1.scale_x = 1.0
            grid_203F1.scale_y = 1.0
            if not True: grid_203F1.operator_context = "EXEC_DEFAULT"
            for i_C8F0E in range(len(bpy.context.scene.sna_palettes[i_0CF39].palette_colors)):
                row_05D1F = grid_203F1.row(heading='', align=True)
                row_05D1F.alert = False
                row_05D1F.enabled = True
                row_05D1F.active = True
                row_05D1F.use_property_split = False
                row_05D1F.use_property_decorate = False
                row_05D1F.scale_x = 1.0
                row_05D1F.scale_y = 1.0
                row_05D1F.alignment = 'Expand'.upper()
                if not True: row_05D1F.operator_context = "EXEC_DEFAULT"
                row_05D1F.prop(bpy.context.scene.sna_palettes[i_0CF39].palette_colors[i_C8F0E], 'color', text='', icon_value=0, emboss=True)
                col_2061D = row_05D1F.column(heading='', align=True)
                col_2061D.alert = False
                col_2061D.enabled = ((bpy.context.object != None) and (((bpy.context.object.data.use_paint_mask or bpy.context.object.data.use_paint_mask_vertex) or 'EDIT_MESH'==bpy.context.mode) and (bpy.context.object.data.color_attributes.active_color != None)))
                col_2061D.active = True
                col_2061D.use_property_split = False
                col_2061D.use_property_decorate = False
                col_2061D.scale_x = 1.0
                col_2061D.scale_y = 1.0
                col_2061D.alignment = 'Expand'.upper()
                if not True: col_2061D.operator_context = "EXEC_DEFAULT"
                op = col_2061D.operator('sna.set_color_abbbf', text='', icon_value=36, emboss=True, depress=False)
                op.sna_new_color = bpy.context.scene.sna_palettes[i_0CF39].palette_colors[i_C8F0E].color
        else:
            row_EB1A0 = box_09C28.row(heading='', align=False)
            row_EB1A0.alert = False
            row_EB1A0.enabled = True
            row_EB1A0.active = True
            row_EB1A0.use_property_split = False
            row_EB1A0.use_property_decorate = False
            row_EB1A0.scale_x = 1.0
            row_EB1A0.scale_y = 1.0
            row_EB1A0.alignment = 'Expand'.upper()
            if not True: row_EB1A0.operator_context = "EXEC_DEFAULT"
            coll_id = display_collection_id('9846D', locals())
            row_EB1A0.template_list('SNA_UL_display_collection_list002_9846D', coll_id, bpy.context.scene.sna_palettes[i_0CF39], 'palette_colors', bpy.context.scene.sna_palettes[i_0CF39], 'index', rows=4)
            col_2228C = row_EB1A0.column(heading='', align=False)
            col_2228C.alert = False
            col_2228C.enabled = True
            col_2228C.active = True
            col_2228C.use_property_split = False
            col_2228C.use_property_decorate = False
            col_2228C.scale_x = 1.0
            col_2228C.scale_y = 1.0
            col_2228C.alignment = 'Expand'.upper()
            if not True: col_2228C.operator_context = "EXEC_DEFAULT"
            col_F7A0A = col_2228C.column(heading='', align=True)
            col_F7A0A.alert = False
            col_F7A0A.enabled = True
            col_F7A0A.active = True
            col_F7A0A.use_property_split = False
            col_F7A0A.use_property_decorate = False
            col_F7A0A.scale_x = 1.0
            col_F7A0A.scale_y = 1.0
            col_F7A0A.alignment = 'Expand'.upper()
            if not True: col_F7A0A.operator_context = "EXEC_DEFAULT"
            row_44371 = col_F7A0A.row(heading='', align=True)
            row_44371.alert = False
            row_44371.enabled = True
            row_44371.active = True
            row_44371.use_property_split = False
            row_44371.use_property_decorate = False
            row_44371.scale_x = 1.0
            row_44371.scale_y = 1.0
            row_44371.alignment = 'Expand'.upper()
            if not True: row_44371.operator_context = "EXEC_DEFAULT"
            op = row_44371.operator('sna.add_palette_color_631c1', text='', icon_value=31, emboss=True, depress=False)
            op.sna_palette_index = i_0CF39
            op.sna_palette_color_index = bpy.context.scene.sna_palettes[i_0CF39].index
            op.sna_color_name = 'Color'
            op.sna_new_color = (1.0, 1.0, 1.0)
            row_20930 = col_F7A0A.row(heading='', align=True)
            row_20930.alert = False
            row_20930.enabled = (len(list(bpy.context.scene.sna_palettes[i_0CF39].palette_colors)) != 0)
            row_20930.active = True
            row_20930.use_property_split = False
            row_20930.use_property_decorate = False
            row_20930.scale_x = 1.0
            row_20930.scale_y = 1.0
            row_20930.alignment = 'Expand'.upper()
            if not True: row_20930.operator_context = "EXEC_DEFAULT"
            op = row_20930.operator('sna.remove_palette_color_d6fa3', text='', icon_value=32, emboss=True, depress=False)
            op.sna_palette_index = i_0CF39
            op.sna_palette_color_index = bpy.context.scene.sna_palettes[i_0CF39].index
            col_2228C.separator(factor=0.25)
            col_67230 = col_2228C.column(heading='', align=True)
            col_67230.alert = False
            col_67230.enabled = True
            col_67230.active = True
            col_67230.use_property_split = False
            col_67230.use_property_decorate = False
            col_67230.scale_x = 1.0
            col_67230.scale_y = 1.0
            col_67230.alignment = 'Expand'.upper()
            if not True: col_67230.operator_context = "EXEC_DEFAULT"
            row_5D6DE = col_67230.row(heading='', align=True)
            row_5D6DE.alert = False
            row_5D6DE.enabled = ((len(list(bpy.context.scene.sna_palettes[i_0CF39].palette_colors)) != 0) and (bpy.context.scene.sna_palettes[i_0CF39].index != 0))
            row_5D6DE.active = True
            row_5D6DE.use_property_split = False
            row_5D6DE.use_property_decorate = False
            row_5D6DE.scale_x = 1.0
            row_5D6DE.scale_y = 1.0
            row_5D6DE.alignment = 'Expand'.upper()
            if not True: row_5D6DE.operator_context = "EXEC_DEFAULT"
            op = row_5D6DE.operator('sna.move_palette_color_up_1d220', text='', icon_value=7, emboss=True, depress=False)
            op.sna_palette_index = i_0CF39
            op.sna_palette_color_index = bpy.context.scene.sna_palettes[i_0CF39].index
            row_F62C9 = col_67230.row(heading='', align=True)
            row_F62C9.alert = False
            row_F62C9.enabled = ((len(list(bpy.context.scene.sna_palettes[i_0CF39].palette_colors)) != 0) and (bpy.context.scene.sna_palettes[i_0CF39].index != int(len(list(bpy.context.scene.sna_palettes[i_0CF39].palette_colors)) - 1.0)))
            row_F62C9.active = True
            row_F62C9.use_property_split = False
            row_F62C9.use_property_decorate = False
            row_F62C9.scale_x = 1.0
            row_F62C9.scale_y = 1.0
            row_F62C9.alignment = 'Expand'.upper()
            if not True: row_F62C9.operator_context = "EXEC_DEFAULT"
            op = row_F62C9.operator('sna.move_palette_color_down_00593', text='', icon_value=5, emboss=True, depress=False)
            op.sna_palette_index = i_0CF39
            op.sna_palette_color_index = bpy.context.scene.sna_palettes[i_0CF39].index
        row_D1E29 = box_09C28.row(heading='', align=True)
        row_D1E29.alert = False
        row_D1E29.enabled = True
        row_D1E29.active = True
        row_D1E29.use_property_split = False
        row_D1E29.use_property_decorate = False
        row_D1E29.scale_x = 1.0
        row_D1E29.scale_y = 1.0
        row_D1E29.alignment = 'Expand'.upper()
        if not True: row_D1E29.operator_context = "EXEC_DEFAULT"
        op = row_D1E29.operator('sna.import_replace_palette_a4fca', text='Import', icon_value=706, emboss=True, depress=False)
        op.sna_palette_index = i_0CF39
        row_A0363 = row_D1E29.row(heading='', align=True)
        row_A0363.alert = False
        row_A0363.enabled = (len(list(bpy.context.scene.sna_palettes[i_0CF39].palette_colors)) != 0)
        row_A0363.active = True
        row_A0363.use_property_split = False
        row_A0363.use_property_decorate = False
        row_A0363.scale_x = 1.0
        row_A0363.scale_y = 1.0
        row_A0363.alignment = 'Expand'.upper()
        if not True: row_A0363.operator_context = "EXEC_DEFAULT"
        op = row_A0363.operator('sna.export_palettes_d17d2', text='Export', icon_value=707, emboss=True, depress=False)
        op.sna_palette_index = i_0CF39
        op = row_D1E29.operator('sna.remove_palette_b653b', text='Remove', icon_value=21, emboss=True, depress=False)
        op.sna_palette_index = i_0CF39
        row_D1E29.separator(factor=0.25)
        row_1290D = row_D1E29.row(heading='', align=True)
        row_1290D.alert = False
        row_1290D.enabled = True
        row_1290D.active = True
        row_1290D.use_property_split = False
        row_1290D.use_property_decorate = False
        row_1290D.scale_x = 1.0
        row_1290D.scale_y = 1.0
        row_1290D.alignment = 'Expand'.upper()
        if not True: row_1290D.operator_context = "EXEC_DEFAULT"
        row_9FBC7 = row_1290D.row(heading='', align=True)
        row_9FBC7.alert = False
        row_9FBC7.enabled = (i_0CF39 != 0)
        row_9FBC7.active = True
        row_9FBC7.use_property_split = False
        row_9FBC7.use_property_decorate = False
        row_9FBC7.scale_x = 1.0
        row_9FBC7.scale_y = 1.0
        row_9FBC7.alignment = 'Expand'.upper()
        if not True: row_9FBC7.operator_context = "EXEC_DEFAULT"
        op = row_9FBC7.operator('sna.move_palette_up_193f8', text='', icon_value=7, emboss=True, depress=False)
        op.sna_palette_index = i_0CF39
        row_3AB45 = row_1290D.row(heading='', align=True)
        row_3AB45.alert = False
        row_3AB45.enabled = (i_0CF39 != int(len(list(bpy.context.scene.sna_palettes)) - 1.0))
        row_3AB45.active = True
        row_3AB45.use_property_split = False
        row_3AB45.use_property_decorate = False
        row_3AB45.scale_x = 1.0
        row_3AB45.scale_y = 1.0
        row_3AB45.alignment = 'Expand'.upper()
        if not True: row_3AB45.operator_context = "EXEC_DEFAULT"
        op = row_3AB45.operator('sna.move_palette_down_cce25', text='', icon_value=5, emboss=True, depress=False)
        op.sna_palette_index = i_0CF39


class SNA_PT_PREFERENCES_1A5FD(bpy.types.Panel):
    bl_label = 'Preferences'
    bl_idname = 'SNA_PT_PREFERENCES_1A5FD'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_context = ''
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.label(text='Preferences', icon_value=0)
        col_51439 = layout.column(heading='', align=True)
        col_51439.alert = False
        col_51439.enabled = True
        col_51439.active = True
        col_51439.use_property_split = False
        col_51439.use_property_decorate = False
        col_51439.scale_x = 1.0
        col_51439.scale_y = 1.0
        col_51439.alignment = 'Expand'.upper()
        if not True: col_51439.operator_context = "EXEC_DEFAULT"
        col_51439.prop(bpy.context.preferences.addons['vertx_artist'].preferences, 'sna_color_grid_columns', text='Color Grid Columns', icon_value=0, emboss=True)
        col_51439.prop(bpy.context.preferences.addons['vertx_artist'].preferences, 'sna_object_color_columns', text='Object Color Columns', icon_value=0, emboss=True)
        col_51439.prop(bpy.context.preferences.addons['vertx_artist'].preferences, 'sna_palette_grid_columns', text='Palette Columns', icon_value=0, emboss=True)
        layout.prop(bpy.context.preferences.addons['vertx_artist'].preferences, 'sna_selection_tolerance', text='Default Selection Tolerance', icon_value=0, emboss=True)
        box_2B6AF = layout.box()
        box_2B6AF.alert = False
        box_2B6AF.enabled = True
        box_2B6AF.active = True
        box_2B6AF.use_property_split = False
        box_2B6AF.use_property_decorate = False
        box_2B6AF.alignment = 'Expand'.upper()
        box_2B6AF.scale_x = 1.0
        box_2B6AF.scale_y = 1.0
        if not True: box_2B6AF.operator_context = "EXEC_DEFAULT"
        box_2B6AF.prop(bpy.context.preferences.addons['vertx_artist'].preferences, 'sna_hide_edit_warning', text='Hide Edit Warning', icon_value=0, emboss=True)
        box_2B6AF.prop(bpy.context.preferences.addons['vertx_artist'].preferences, 'sna_hide_refresh_stack_warning', text='Hide Refresh Stack Warning', icon_value=0, emboss=True)


class SNA_AddonPreferences_0446F(bpy.types.AddonPreferences):
    bl_idname = 'vertx_artist'
    sna_color_grid_columns: bpy.props.IntProperty(name='color_grid_columns', description='Number of columns to use for grid color display', default=1, subtype='NONE', min=1, max=100)
    sna_object_color_columns: bpy.props.IntProperty(name='object_color_columns', description='Number of columns to use for grid object color display', default=4, subtype='NONE', min=2, max=100)
    sna_palette_grid_columns: bpy.props.IntProperty(name='palette_grid_columns', description='Number of columns to use for palette grid display', default=1, subtype='NONE', min=1, max=100)
    sna_selection_tolerance: bpy.props.FloatProperty(name='selection_tolerance', description='How much can a vertex/face have other colors.', default=0.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2)
    sna_hide_edit_warning: bpy.props.BoolProperty(name='hide_edit_warning', description='Hide warning about editing layer channels', default=False)
    sna_hide_refresh_stack_warning: bpy.props.BoolProperty(name='hide_refresh_stack_warning', description='Hide warning about refreshing color transformatin stack', default=False)

    def sna_override_selection_color_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_override_selection_color: bpy.props.EnumProperty(name='override_selection_color', description='', items=[('None', 'None', '', 0, 0), ('White Override', 'White Override', '', 0, 1), ('Full Override', 'Full Override', '', 0, 2)], update=sna_update_sna_override_selection_color_C63F5)
    sna_selection_color: bpy.props.FloatVectorProperty(name='selection_color', description='', size=4, default=(0.9058823585510254, 0.6078431606292725, 0.250980406999588, 0.5), subtype='COLOR_GAMMA', unit='NONE', min=0.0, max=1.0, step=3, precision=6)

    def draw(self, context):
        if not (False):
            layout = self.layout 
            layout.prop(find_user_keyconfig('5F569'), 'type', text='Panel Popout', full_event=True)
            layout.prop(find_user_keyconfig('1C102'), 'type', text='Quick Access Menu', full_event=True)
            layout.prop(find_user_keyconfig('38BF8'), 'type', text='Color Eyedropper', full_event=True)
            layout.prop(find_user_keyconfig('34B58'), 'type', text='Set Color', full_event=True)


class SNA_MT_ED3E4(bpy.types.Menu):
    bl_idname = "SNA_MT_ED3E4"
    bl_label = "VertXArtist: Quick Access"

    @classmethod
    def poll(cls, context):
        return not ((not 'PAINT_VERTEX'==bpy.context.mode))

    def draw(self, context):
        layout = self.layout.menu_pie()
        layout.prop(bpy.context.object.data, 'use_paint_mask_vertex', text='', icon_value=0, emboss=True)
        layout.prop(bpy.context.object.data, 'use_paint_mask', text='', icon_value=0, emboss=True)
        op = layout.operator('sna.checkpoint_1810d', text='Checkpoint', icon_value=_icons['white_flag.png'].icon_id, emboss=True, depress=False)
        op = layout.operator('sna.select_by_color_ee838', text='Active Select', icon_value=256, emboss=True, depress=False)
        op.sna_selection_tolerance = bpy.context.preferences.addons['vertx_artist'].preferences.sna_selection_tolerance
        op.sna_select_color = (1.0, 1.0, 1.0)
        op.sna_select_color_idx = 0
        op.sna_ignore_hue = False
        op.sna_ignore_saturation = False
        op.sna_ignore_value = False


class SNA_OT_Set_Color_Static_3018B(bpy.types.Operator):
    bl_idname = "sna.set_color_static_3018b"
    bl_label = "Set Color Static"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not  not ('PAINT_VERTEX'==bpy.context.mode or 'EDIT_MESH'==bpy.context.mode)

    def execute(self, context):
        bpy.ops.sna.set_color_abbbf('INVOKE_DEFAULT', sna_new_color=bpy.context.scene.sna_static_color)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Set_Color_Abbbf(bpy.types.Operator):
    bl_idname = "sna.set_color_abbbf"
    bl_label = "Set Color"
    bl_description = "Apply color to selection"
    bl_options = {"REGISTER", "UNDO"}
    sna_new_color: bpy.props.FloatVectorProperty(name='new_color', description='Color to apply to selection', size=3, default=(0.0, 0.0, 0.0), subtype='COLOR_GAMMA', unit='NONE', min=0.0, max=1.0, step=3, precision=6)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        if ((bpy.context.object != None) and (((bpy.context.object.data.use_paint_mask or bpy.context.object.data.use_paint_mask_vertex) or 'EDIT_MESH'==bpy.context.mode) and (bpy.context.object.data.color_attributes.active_color != None))):
            return_EFB53 = set_color(color=self.sna_new_color, channels=list(bpy.context.view_layer.objects.active.sna_layers)[bpy.context.object.data.color_attributes.active_color_index].channels)
            if (bpy.context.scene.sna_show_object_colors and 'EDIT_MESH'==bpy.context.mode):
                bpy.ops.sna.refresh_fe2a7('INVOKE_DEFAULT', )
        else:
            self.report({'WARNING'}, message="Can't set color")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Vertx_Artist_Restore_Panel_F0746(bpy.types.Operator):
    bl_idname = "sna.vertx_artist_restore_panel_f0746"
    bl_label = "VertX Artist Restore Panel"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        vertx_panel['sna_popout_active'] = False
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Vertx_Artist_Popout_Fa638(bpy.types.Operator):
    bl_idname = "sna.vertx_artist_popout_fa638"
    bl_label = "VertX Artist Popout"
    bl_description = "Pop the VertX Artist panel out"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not  not ('PAINT_VERTEX'==bpy.context.mode or 'EDIT_MESH'==bpy.context.mode)

    def execute(self, context):
        vertx_panel['sna_popout_active'] = False
        if bpy.context and bpy.context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout_function = layout
        sna_vertx_artist_main_panel_function_372CE(layout_function, )

    def invoke(self, context, event):
        vertx_panel['sna_popout_active'] = True
        if bpy.context and bpy.context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
        return context.window_manager.invoke_props_dialog(self, width=300)


def sna_vertx_artist_main_panel_function_372CE(layout_function, ):
    layout_function = layout_function
    sna_header_function_FB3F3(layout_function, )
    layout_function = layout_function
    sna_display_palettes_1AEAA(layout_function, )
    row_F4D60 = layout_function.row(heading='', align=True)
    row_F4D60.alert = False
    row_F4D60.enabled = True
    row_F4D60.active = True
    row_F4D60.use_property_split = False
    row_F4D60.use_property_decorate = False
    row_F4D60.scale_x = 1.0
    row_F4D60.scale_y = 1.0
    row_F4D60.alignment = 'Expand'.upper()
    if not True: row_F4D60.operator_context = "EXEC_DEFAULT"
    op = row_F4D60.operator('sna.import_palette_26c39', text='Import Palette', icon_value=706, emboss=True, depress=False)
    op = row_F4D60.operator('sna.create_palette_098ec', text='Create Palette', icon_value=31, emboss=True, depress=False)
    if 'EDIT_MESH'==bpy.context.mode:
        if ((bpy.context.object != None) and (bpy.context.object.data != None) and (bpy.context.object.data.color_attributes.active_color != None)):
            layout_function.separator(factor=1.0)
            layout_function = layout_function
            sna_object_colors_function_C6050(layout_function, )
    else:
        layout_function.separator(factor=0.5)
        split_D60DC = layout_function.split(factor=0.5, align=True)
        split_D60DC.alert = False
        split_D60DC.enabled = 'PAINT_VERTEX'==bpy.context.mode
        split_D60DC.active = True
        split_D60DC.use_property_split = False
        split_D60DC.use_property_decorate = False
        split_D60DC.scale_x = 1.0
        split_D60DC.scale_y = 1.0
        split_D60DC.alignment = 'Expand'.upper()
        if not True: split_D60DC.operator_context = "EXEC_DEFAULT"
        split_A0FA8 = split_D60DC.split(factor=0.5, align=True)
        split_A0FA8.alert = False
        split_A0FA8.enabled = True
        split_A0FA8.active = True
        split_A0FA8.use_property_split = False
        split_A0FA8.use_property_decorate = False
        split_A0FA8.scale_x = 1.0
        split_A0FA8.scale_y = 1.0
        split_A0FA8.alignment = 'Expand'.upper()
        if not True: split_A0FA8.operator_context = "EXEC_DEFAULT"
        op = split_A0FA8.operator('paint.vertex_color_brightness_contrast', text='Bri/Con', icon_value=0, emboss=True, depress=False)
        op = split_A0FA8.operator('paint.vertex_color_hsv', text='HSV', icon_value=0, emboss=True, depress=False)
        split_24752 = split_D60DC.split(factor=0.5, align=True)
        split_24752.alert = False
        split_24752.enabled = True
        split_24752.active = True
        split_24752.use_property_split = False
        split_24752.use_property_decorate = False
        split_24752.scale_x = 1.0
        split_24752.scale_y = 1.0
        split_24752.alignment = 'Expand'.upper()
        if not True: split_24752.operator_context = "EXEC_DEFAULT"
        op = split_24752.operator('paint.vertex_color_smooth', text='Smooth', icon_value=0, emboss=True, depress=False)
        op = split_24752.operator('paint.vertex_color_dirt', text='Dirt', icon_value=0, emboss=True, depress=False)


def sna_add_to_view3d_pt_tools_active_DB2BC(self, context):
    if not ( not ('PAINT_VERTEX'==bpy.context.mode or 'EDIT_MESH'==bpy.context.mode)):
        layout = self.layout
        if vertx_panel['sna_popout_active']:
            op = layout.operator('sna.vertx_artist_restore_panel_f0746', text='VertX Artist Reset', icon_value=77, emboss=True, depress=False)
        else:
            layout_function = layout
            sna_vertx_artist_main_panel_function_372CE(layout_function, )
            layout.separator(factor=0.5)


def sna_add_to_view3d_pt_tools_active_722B0(self, context):
    if not ((not 'OBJECT'==bpy.context.mode)):
        layout = self.layout
        layout_function = layout
        sna_object_colors_object_mode_286C1(layout_function, )
        layout.separator(factor=0.5)


class SNA_OT_Add_Layer_Af10A(bpy.types.Operator):
    bl_idname = "sna.add_layer_af10a"
    bl_label = "Add Layer"
    bl_description = "Add new layer, or combine channels from other layers"
    bl_options = {"REGISTER", "UNDO"}
    sna_layer_name: bpy.props.StringProperty(name='layer_name', description='', default='Attribute', subtype='NONE', maxlen=0)

    def sna_channels_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_channels: bpy.props.EnumProperty(name='channels', description='', items=[('RGBA', 'RGBA', '', 0, 0), ('RGB', 'RGB', '', 0, 1), ('R', 'R', '', 0, 2), ('G', 'G', '', 0, 3), ('B', 'B', '', 0, 4), ('A', 'A', '', 0, 5), ('RG', 'RG', '', 0, 6), ('RB', 'RB', '', 0, 7), ('GB', 'GB', '', 0, 8)])
    sna_r_channel: bpy.props.EnumProperty(name='r_channel', description='', items=sna_r_channel_enum_items)
    sna_g_channel: bpy.props.EnumProperty(name='g_channel', description='', items=sna_g_channel_enum_items)
    sna_b_channel: bpy.props.EnumProperty(name='b_channel', description='', items=sna_b_channel_enum_items)
    sna_a_channel: bpy.props.EnumProperty(name='a_channel', description='', items=sna_a_channel_enum_items)
    sna_r_channel_value: bpy.props.FloatProperty(name='r_channel_value', description='', default=0.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2)
    sna_g_channel_value: bpy.props.FloatProperty(name='g_channel_value', description='', default=0.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2)
    sna_b_channel_value: bpy.props.FloatProperty(name='b_channel_value', description='', default=0.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2)
    sna_a_channel_value: bpy.props.FloatProperty(name='a_channel_value', description='', default=1.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2)

    def sna_r_gamma_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_r_gamma: bpy.props.EnumProperty(name='r_gamma', description='', items=[('None', 'None', '', 0, 0), ('Gamma', 'Gamma', '', 0, 1), ('Inverse', 'Inverse', '', 0, 2)])

    def sna_g_gamma_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_g_gamma: bpy.props.EnumProperty(name='g_gamma', description='', items=[('None', 'None', '', 0, 0), ('Gamma', 'Gamma', '', 0, 1), ('Inverse', 'Inverse', '', 0, 2)])

    def sna_b_gamma_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_b_gamma: bpy.props.EnumProperty(name='b_gamma', description='', items=[('None', 'None', '', 0, 0), ('Gamma', 'Gamma', '', 0, 1), ('Inverse', 'Inverse', '', 0, 2)])

    def sna_a_gamma_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_a_gamma: bpy.props.EnumProperty(name='a_gamma', description='', items=[('None', 'None', '', 0, 0), ('Gamma', 'Gamma', '', 0, 1), ('Inverse', 'Inverse', '', 0, 2)])

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and False:
            cls.poll_message_set()
        return not False

    def execute(self, context):
        bpy.ops.sna.add_color_layer_436c7(sna_name=self.sna_layer_name, sna_channels=self.sna_channels)
        return_B9B37 = combine_layers(channels=self.sna_channels, channels_list=[self.sna_r_channel, self.sna_g_channel, self.sna_b_channel, self.sna_a_channel], channels_values=[self.sna_r_channel_value, self.sna_g_channel_value, self.sna_b_channel_value, self.sna_a_channel_value], channels_gamma=[self.sna_r_gamma, self.sna_g_gamma, self.sna_b_gamma, self.sna_a_gamma], layers=bpy.context.view_layer.objects.active.sna_layers)
        self.sna_r_channel = 'None'
        self.sna_g_channel = 'None'
        self.sna_b_channel = 'None'
        self.sna_a_channel = 'None'
        self.sna_layer_name = 'Attribute'
        self.sna_channels = 'RGBA'
        self.sna_r_channel_value = 0.0
        self.sna_g_channel_value = 0.0
        self.sna_b_channel_value = 0.0
        self.sna_a_channel_value = 1.0
        self.sna_r_gamma = 'None'
        self.sna_g_gamma = 'None'
        self.sna_b_gamma = 'None'
        self.sna_a_gamma = 'None'
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        row_0D298 = layout.row(heading='Layer Name', align=False)
        row_0D298.alert = False
        row_0D298.enabled = True
        row_0D298.active = True
        row_0D298.use_property_split = False
        row_0D298.use_property_decorate = False
        row_0D298.scale_x = 1.0
        row_0D298.scale_y = 1.0
        row_0D298.alignment = 'Expand'.upper()
        if not True: row_0D298.operator_context = "EXEC_DEFAULT"
        row_0D298.prop(self, 'sna_layer_name', text='', icon_value=0, emboss=True)
        row_6A1BF = layout.row(heading='Channels', align=False)
        row_6A1BF.alert = False
        row_6A1BF.enabled = True
        row_6A1BF.active = True
        row_6A1BF.use_property_split = False
        row_6A1BF.use_property_decorate = False
        row_6A1BF.scale_x = 1.0
        row_6A1BF.scale_y = 1.0
        row_6A1BF.alignment = 'Expand'.upper()
        if not True: row_6A1BF.operator_context = "EXEC_DEFAULT"
        row_6A1BF.prop(self, 'sna_channels', text='', icon_value=0, emboss=True)
        layout.separator(factor=0.5)
        row_0FB12 = layout.row(heading='Layer Name', align=False)
        row_0FB12.alert = False
        row_0FB12.enabled = True
        row_0FB12.active = True
        row_0FB12.use_property_split = False
        row_0FB12.use_property_decorate = False
        row_0FB12.scale_x = 1.0
        row_0FB12.scale_y = 1.0
        row_0FB12.alignment = 'Expand'.upper()
        if not True: row_0FB12.operator_context = "EXEC_DEFAULT"
        row_0FB12.label(text='', icon_value=0)
        row_0FB12.label(text='Color Layer', icon_value=0)
        row_0FB12.label(text='Flat Value', icon_value=0)
        row_0FB12.label(text='Correction', icon_value=0)
        if 'R' in self.sna_channels:
            row_D2F51 = layout.row(heading='R channel', align=False)
            row_D2F51.alert = False
            row_D2F51.enabled = True
            row_D2F51.active = True
            row_D2F51.use_property_split = False
            row_D2F51.use_property_decorate = False
            row_D2F51.scale_x = 1.0
            row_D2F51.scale_y = 1.0
            row_D2F51.alignment = 'Expand'.upper()
            if not True: row_D2F51.operator_context = "EXEC_DEFAULT"
            row_D2F51.prop(self, 'sna_r_channel', text='', icon_value=0, emboss=True)
            row_86B13 = row_D2F51.row(heading='', align=False)
            row_86B13.alert = False
            row_86B13.enabled = (self.sna_r_channel == 'None')
            row_86B13.active = True
            row_86B13.use_property_split = False
            row_86B13.use_property_decorate = False
            row_86B13.scale_x = 1.0
            row_86B13.scale_y = 1.0
            row_86B13.alignment = 'Expand'.upper()
            if not True: row_86B13.operator_context = "EXEC_DEFAULT"
            row_86B13.prop(self, 'sna_r_channel_value', text='', icon_value=0, emboss=True)
            row_D2F51.prop(self, 'sna_r_gamma', text='', icon_value=0, emboss=True)
        if 'G' in self.sna_channels:
            row_2D2B7 = layout.row(heading='G channel', align=False)
            row_2D2B7.alert = False
            row_2D2B7.enabled = True
            row_2D2B7.active = True
            row_2D2B7.use_property_split = False
            row_2D2B7.use_property_decorate = False
            row_2D2B7.scale_x = 1.0
            row_2D2B7.scale_y = 1.0
            row_2D2B7.alignment = 'Expand'.upper()
            if not True: row_2D2B7.operator_context = "EXEC_DEFAULT"
            row_2D2B7.prop(self, 'sna_g_channel', text='', icon_value=0, emboss=True)
            row_DCD4F = row_2D2B7.row(heading='', align=False)
            row_DCD4F.alert = False
            row_DCD4F.enabled = (self.sna_g_channel == 'None')
            row_DCD4F.active = True
            row_DCD4F.use_property_split = False
            row_DCD4F.use_property_decorate = False
            row_DCD4F.scale_x = 1.0
            row_DCD4F.scale_y = 1.0
            row_DCD4F.alignment = 'Expand'.upper()
            if not True: row_DCD4F.operator_context = "EXEC_DEFAULT"
            row_DCD4F.prop(self, 'sna_g_channel_value', text='', icon_value=0, emboss=True)
            row_2D2B7.prop(self, 'sna_g_gamma', text='', icon_value=0, emboss=True)
        if 'B' in self.sna_channels:
            row_CD92D = layout.row(heading='B channel', align=False)
            row_CD92D.alert = False
            row_CD92D.enabled = True
            row_CD92D.active = True
            row_CD92D.use_property_split = False
            row_CD92D.use_property_decorate = False
            row_CD92D.scale_x = 1.0
            row_CD92D.scale_y = 1.0
            row_CD92D.alignment = 'Expand'.upper()
            if not True: row_CD92D.operator_context = "EXEC_DEFAULT"
            row_CD92D.prop(self, 'sna_b_channel', text='', icon_value=0, emboss=True)
            row_65049 = row_CD92D.row(heading='', align=False)
            row_65049.alert = False
            row_65049.enabled = (self.sna_b_channel == 'None')
            row_65049.active = True
            row_65049.use_property_split = False
            row_65049.use_property_decorate = False
            row_65049.scale_x = 1.0
            row_65049.scale_y = 1.0
            row_65049.alignment = 'Expand'.upper()
            if not True: row_65049.operator_context = "EXEC_DEFAULT"
            row_65049.prop(self, 'sna_b_channel_value', text='', icon_value=0, emboss=True)
            row_CD92D.prop(self, 'sna_b_gamma', text='', icon_value=0, emboss=True)
        if 'A' in self.sna_channels:
            row_57FC2 = layout.row(heading='A channel', align=False)
            row_57FC2.alert = False
            row_57FC2.enabled = True
            row_57FC2.active = True
            row_57FC2.use_property_split = False
            row_57FC2.use_property_decorate = False
            row_57FC2.scale_x = 1.0
            row_57FC2.scale_y = 1.0
            row_57FC2.alignment = 'Expand'.upper()
            if not True: row_57FC2.operator_context = "EXEC_DEFAULT"
            row_57FC2.prop(self, 'sna_a_channel', text='', icon_value=0, emboss=True)
            row_97476 = row_57FC2.row(heading='', align=False)
            row_97476.alert = False
            row_97476.enabled = (self.sna_a_channel == 'None')
            row_97476.active = True
            row_97476.use_property_split = False
            row_97476.use_property_decorate = False
            row_97476.scale_x = 1.0
            row_97476.scale_y = 1.0
            row_97476.alignment = 'Expand'.upper()
            if not True: row_97476.operator_context = "EXEC_DEFAULT"
            row_97476.prop(self, 'sna_a_channel_value', text='', icon_value=0, emboss=True)
            row_57FC2.prop(self, 'sna_a_gamma', text='', icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)


class SNA_GROUP_sna_palette_color(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='name', description='Palette_color name', default='Color', subtype='NONE', maxlen=0, update=sna_update_name_94247)
    color: bpy.props.FloatVectorProperty(name='color', description='Palette_color color', size=3, default=(0.0, 0.0, 0.0), subtype='COLOR_GAMMA', unit='NONE', min=0.0, max=1.0, step=3, precision=6, update=sna_update_color_E5CFB)


class SNA_GROUP_sna_object_color(bpy.types.PropertyGroup):
    color: bpy.props.FloatVectorProperty(name='color', description='Object color to dynamically change', size=3, default=(0.0, 0.0, 0.0), subtype='COLOR_GAMMA', unit='NONE', min=0.0, max=1.0, step=3, precision=6, update=sna_update_color_E5CFB)
    index: bpy.props.IntProperty(name='index', description='', default=0, subtype='NONE')


class SNA_GROUP_sna_layer(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='name', description='', default='', subtype='NONE', maxlen=0, update=sna_update_name_94247)
    channels: bpy.props.EnumProperty(name='channels', description='', items=[('RGBA', 'RGBA', '', 0, 0), ('RGB', 'RGB', '', 0, 1), ('R', 'R', '', 0, 2), ('G', 'G', '', 0, 3), ('B', 'B', '', 0, 4), ('A', 'A', '', 0, 5), ('RG', 'RG', '', 0, 6), ('RB', 'RB', '', 0, 7), ('GB', 'GB', '', 0, 8)])


class SNA_GROUP_sna_modification(bpy.types.PropertyGroup):
    node_name: bpy.props.StringProperty(name='node_name', description='', default='', subtype='NONE', maxlen=0)
    input_node_name: bpy.props.StringProperty(name='input_node_name', description='', default='', subtype='NONE', maxlen=0)
    include: bpy.props.BoolProperty(name='include', description='', default=True, update=sna_update_include_0C1C2)
    blend_type: bpy.props.EnumProperty(name='blend_type', description='', items=[('Mix', 'Mix', '', 0, 0), ('Darken', 'Darken', '', 0, 1), ('Multiply', 'Multiply', '', 0, 2), ('Color Burn', 'Color Burn', '', 0, 3), ('Lighten', 'Lighten', '', 0, 4), ('Screen', 'Screen', '', 0, 5), ('Color Dodge', 'Color Dodge', '', 0, 6), ('Add', 'Add', '', 0, 7), ('Overlay', 'Overlay', '', 0, 8), ('Soft Light', 'Soft Light', '', 0, 9), ('Linear Light', 'Linear Light', '', 0, 10), ('Difference', 'Difference', '', 0, 11), ('Subtract', 'Subtract', '', 0, 12), ('Divide', 'Divide', '', 0, 13), ('Hue', 'Hue', '', 0, 14), ('Saturation', 'Saturation', '', 0, 15), ('Color', 'Color', '', 0, 16), ('Value', 'Value', '', 0, 17)], update=sna_update_blend_type_4846E)
    blend_layer: bpy.props.EnumProperty(name='blend_layer', description='', items=sna_modification_blend_layer_enum_items, update=sna_update_blend_layer_3C8C9)
    blend_color: bpy.props.FloatVectorProperty(name='blend_color', description='', size=3, default=(1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=6, update=sna_update_blend_color_81607)
    factor: bpy.props.FloatProperty(name='factor', description='', default=0.5, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2, update=sna_update_factor_DCB8E)


class SNA_GROUP_sna_palette(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='name', description='Palette name', default='', subtype='NONE', maxlen=0, update=sna_update_name_94247)
    palette_colors: bpy.props.CollectionProperty(name='palette_colors', description='', type=SNA_GROUP_sna_palette_color)
    index: bpy.props.IntProperty(name='index', description='Palette index', default=0, subtype='NONE', min=0)


class SNA_GROUP_sna_modification_stack(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='name', description='', default='', subtype='NONE', maxlen=0, update=sna_update_name_94247)
    modifications: bpy.props.CollectionProperty(name='modifications', description='', type=SNA_GROUP_sna_modification)
    base_layer: bpy.props.EnumProperty(name='base_layer', description='', items=sna_modification_stack_base_layer_enum_items, update=sna_update_base_layer_C3B7B)
    index: bpy.props.IntProperty(name='index', description='', default=0, subtype='NONE', min=0)


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.utils.register_class(SNA_GROUP_sna_palette_color)
    bpy.utils.register_class(SNA_GROUP_sna_object_color)
    bpy.utils.register_class(SNA_GROUP_sna_layer)
    bpy.utils.register_class(SNA_GROUP_sna_modification)
    bpy.utils.register_class(SNA_GROUP_sna_palette)
    bpy.utils.register_class(SNA_GROUP_sna_modification_stack)
    bpy.types.Scene.sna_static_color = bpy.props.FloatVectorProperty(name='static_color', description='Color to apply to selection', size=3, default=(0.0, 0.0, 0.0), subtype='COLOR_GAMMA', unit='NONE', min=0.0, max=1.0, step=3, precision=6)
    bpy.types.Scene.sna_palettes = bpy.props.CollectionProperty(name='palettes', description='', type=SNA_GROUP_sna_palette)
    bpy.types.Scene.sna_active_color_index = bpy.props.IntProperty(name='active_color_index', description='', default=0, subtype='NONE')
    bpy.types.Scene.sna_object_colors = bpy.props.CollectionProperty(name='object_colors', description='', type=SNA_GROUP_sna_object_color)
    bpy.types.Scene.sna_object_colors_index = bpy.props.IntProperty(name='object_colors_index', description='Object_color index', default=0, subtype='NONE', min=0)
    bpy.types.Object.sna_layers = bpy.props.CollectionProperty(name='layers', description='', type=SNA_GROUP_sna_layer)
    bpy.types.Object.sna_enable_editing = bpy.props.BoolProperty(name='enable_editing', description='', default=False)
    bpy.types.Object.sna_modification_stack_enum = bpy.props.EnumProperty(name='modification_stack_enum', description='', items=sna_modification_stack_enum_enum_items, update=sna_update_sna_modification_stack_enum_42B47)
    bpy.types.Object.sna_modification_stacks = bpy.props.CollectionProperty(name='modification_stacks', description='', type=SNA_GROUP_sna_modification_stack)
    bpy.types.Scene.sna_transformations_visible_enum = bpy.props.EnumProperty(name='transformations_visible_enum', description='', items=[('All', 'All', '', 0, 0), ('Only Visible', 'Only Visible', '', 0, 1)])
    bpy.types.Scene.sna_neg_axis = bpy.props.FloatProperty(name='neg_axis', description='', default=0.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2)
    bpy.types.Scene.sna_pos_axis = bpy.props.FloatProperty(name='pos_axis', description='', default=1.0, subtype='NONE', unit='NONE', min=0.0, max=1.0, step=3, precision=2)
    bpy.types.Scene.sna_show_object_colors = bpy.props.BoolProperty(name='show_object_colors', description='', default=True)
    bpy.utils.register_class(SNA_OT_Vertx_Eyedropper_Fe493)
    bpy.utils.register_class(SNA_OT_Apply_Alpha_Gradient_72437)
    bpy.types.VIEW3D_PT_tools_active.prepend(sna_add_to_view3d_pt_tools_active_937B1)
    bpy.utils.register_class(SNA_OT_Move_Transformation_Layer_Up_50685)
    bpy.utils.register_class(SNA_OT_Move_Transformation_Layer_Down_9A259)
    bpy.utils.register_class(SNA_OT_Remove_Color_Transformation_Bf376)
    bpy.utils.register_class(SNA_OT_Add_Color_Transformation_D7C6C)
    bpy.utils.register_class(SNA_OT_Remove_Color_Transformation_Layer_Dac60)
    bpy.utils.register_class(SNA_OT_Add_Color_Transformation_Layer_8A10C)
    bpy.utils.register_class(SNA_OT_Refresh_Color_Transformation_View_3912B)
    bpy.utils.register_class(SNA_OT_Refresh_Color_Transformation_View_With_Warning_D6F51)
    bpy.utils.register_class(SNA_OT_Apply_Color_Transformation_Stack_969Ba)
    bpy.utils.register_class(SNA_OT_Apply_Color_Transformation_Stack_Popup_050Bc)
    bpy.utils.register_class(SNA_PT_COLOR_TRANSFORMATIONS_0C04B)
    bpy.utils.register_class(SNA_UL_display_collection_list_5FDE3)
    bpy.utils.register_class(SNA_OT_Toggle_Color_Transformation_Visibility_Fc89C)
    bpy.utils.register_class(SNA_OT_Synchronize_Layers_8B7E4)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post_handler_25D07)
    bpy.utils.register_class(SNA_OT_Add_Color_Layer_436C7)
    bpy.utils.register_class(SNA_OT_Select_Rgba_Layer_08766)
    bpy.utils.register_class(SNA_OT_Extract_Alpha_50Ab0)
    bpy.utils.register_class(SNA_OT_Bake_Alpha_A245B)
    bpy.utils.register_class(SNA_PT_COLOR_LAYERS_B79C5)
    bpy.utils.register_class(SNA_UL_display_collection_list_CEEB3)
    bpy.utils.register_class(SNA_OT_Toggle_Render_Color_Layer_7A12B)
    bpy.utils.register_class(SNA_OT_Toggle_Layer_Editing_17Bff)
    bpy.utils.register_class(SNA_OT_Toggle_Layer_Editing_With_Warning_6B0Ab)
    bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_pre_handler_D69F3)
    bpy.utils.register_class(SNA_OT_Refresh_Fe2A7)
    bpy.utils.register_class(SNA_OT_Showhide_Object_Colors_C831C)
    bpy.utils.register_class(SNA_OT_Select_By_Color_Ee838)
    bpy.utils.register_class(SNA_OT_Checkpoint_1810D)
    if not 'white_flag.png' in _icons: _icons.load('white_flag.png', os.path.join(os.path.dirname(__file__), 'icons', 'white_flag.png'), "IMAGE")
    bpy.utils.register_class(SNA_OT_Remove_Palette_B653B)
    bpy.utils.register_class(SNA_OT_Create_Palette_098Ec)
    bpy.utils.register_class(SNA_OT_Add_Palette_Color_631C1)
    bpy.utils.register_class(SNA_OT_Remove_Palette_Color_D6Fa3)
    bpy.utils.register_class(SNA_OT_Move_Palette_Up_193F8)
    bpy.utils.register_class(SNA_OT_Move_Palette_Down_Cce25)
    bpy.utils.register_class(SNA_OT_Move_Palette_Color_Down_00593)
    bpy.utils.register_class(SNA_OT_Move_Palette_Color_Up_1D220)
    bpy.utils.register_class(SNA_OT_Import_Palette_26C39)
    bpy.utils.register_class(SNA_OT_Import_Replace_Palette_A4Fca)
    bpy.utils.register_class(SNA_OT_Export_Palettes_D17D2)
    bpy.utils.register_class(SNA_OT_Export_Ccb_Palette_E3Da4)
    bpy.utils.register_class(SNA_OT_Export_Gpl_Palette_B20A0)
    bpy.utils.register_class(SNA_UL_display_collection_list002_9846D)
    bpy.utils.register_class(SNA_PT_PREFERENCES_1A5FD)
    bpy.utils.register_class(SNA_AddonPreferences_0446F)
    bpy.utils.register_class(SNA_MT_ED3E4)
    if not 'white_flag.png' in _icons: _icons.load('white_flag.png', os.path.join(os.path.dirname(__file__), 'icons', 'white_flag.png'), "IMAGE")
    bpy.utils.register_class(SNA_OT_Set_Color_Static_3018B)
    bpy.utils.register_class(SNA_OT_Set_Color_Abbbf)
    bpy.utils.register_class(SNA_OT_Vertx_Artist_Restore_Panel_F0746)
    bpy.utils.register_class(SNA_OT_Vertx_Artist_Popout_Fa638)
    bpy.types.VIEW3D_PT_tools_active.prepend(sna_add_to_view3d_pt_tools_active_DB2BC)
    bpy.types.VIEW3D_PT_tools_active.prepend(sna_add_to_view3d_pt_tools_active_722B0)
    bpy.utils.register_class(SNA_OT_Add_Layer_Af10A)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('sna.vertx_eyedropper_fe493', 'S', 'PRESS',
        ctrl=False, alt=True, shift=True, repeat=False)
    addon_keymaps['38BF8'] = (km, kmi)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'V', 'PRESS',
        ctrl=False, alt=False, shift=False, repeat=False)
    kmi.properties.name = 'SNA_MT_ED3E4'
    addon_keymaps['1C102'] = (km, kmi)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('sna.set_color_static_3018b', 'K', 'PRESS',
        ctrl=False, alt=True, shift=True, repeat=False)
    addon_keymaps['34B58'] = (km, kmi)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('sna.vertx_artist_popout_fa638', 'V', 'PRESS',
        ctrl=False, alt=False, shift=True, repeat=False)
    addon_keymaps['5F569'] = (km, kmi)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.sna_show_object_colors
    del bpy.types.Scene.sna_pos_axis
    del bpy.types.Scene.sna_neg_axis
    del bpy.types.Scene.sna_transformations_visible_enum
    del bpy.types.Object.sna_modification_stacks
    del bpy.types.Object.sna_modification_stack_enum
    del bpy.types.Object.sna_enable_editing
    del bpy.types.Object.sna_layers
    del bpy.types.Scene.sna_object_colors_index
    del bpy.types.Scene.sna_object_colors
    del bpy.types.Scene.sna_active_color_index
    del bpy.types.Scene.sna_palettes
    del bpy.types.Scene.sna_static_color
    bpy.utils.unregister_class(SNA_GROUP_sna_modification_stack)
    bpy.utils.unregister_class(SNA_GROUP_sna_palette)
    bpy.utils.unregister_class(SNA_GROUP_sna_modification)
    bpy.utils.unregister_class(SNA_GROUP_sna_layer)
    bpy.utils.unregister_class(SNA_GROUP_sna_object_color)
    bpy.utils.unregister_class(SNA_GROUP_sna_palette_color)
    bpy.utils.unregister_class(SNA_OT_Vertx_Eyedropper_Fe493)
    if handler_BCC2E:
        bpy.types.SpaceView3D.draw_handler_remove(handler_BCC2E[0], 'WINDOW')
        handler_BCC2E.pop(0)
    bpy.utils.unregister_class(SNA_OT_Apply_Alpha_Gradient_72437)
    bpy.types.VIEW3D_PT_tools_active.remove(sna_add_to_view3d_pt_tools_active_937B1)
    bpy.utils.unregister_class(SNA_OT_Move_Transformation_Layer_Up_50685)
    bpy.utils.unregister_class(SNA_OT_Move_Transformation_Layer_Down_9A259)
    bpy.utils.unregister_class(SNA_OT_Remove_Color_Transformation_Bf376)
    bpy.utils.unregister_class(SNA_OT_Add_Color_Transformation_D7C6C)
    bpy.utils.unregister_class(SNA_OT_Remove_Color_Transformation_Layer_Dac60)
    bpy.utils.unregister_class(SNA_OT_Add_Color_Transformation_Layer_8A10C)
    bpy.utils.unregister_class(SNA_OT_Refresh_Color_Transformation_View_3912B)
    bpy.utils.unregister_class(SNA_OT_Refresh_Color_Transformation_View_With_Warning_D6F51)
    bpy.utils.unregister_class(SNA_OT_Apply_Color_Transformation_Stack_969Ba)
    bpy.utils.unregister_class(SNA_OT_Apply_Color_Transformation_Stack_Popup_050Bc)
    bpy.utils.unregister_class(SNA_PT_COLOR_TRANSFORMATIONS_0C04B)
    bpy.utils.unregister_class(SNA_UL_display_collection_list_5FDE3)
    bpy.utils.unregister_class(SNA_OT_Toggle_Color_Transformation_Visibility_Fc89C)
    bpy.utils.unregister_class(SNA_OT_Synchronize_Layers_8B7E4)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post_handler_25D07)
    bpy.utils.unregister_class(SNA_OT_Add_Color_Layer_436C7)
    bpy.utils.unregister_class(SNA_OT_Select_Rgba_Layer_08766)
    bpy.utils.unregister_class(SNA_OT_Extract_Alpha_50Ab0)
    bpy.utils.unregister_class(SNA_OT_Bake_Alpha_A245B)
    bpy.utils.unregister_class(SNA_PT_COLOR_LAYERS_B79C5)
    bpy.utils.unregister_class(SNA_UL_display_collection_list_CEEB3)
    bpy.utils.unregister_class(SNA_OT_Toggle_Render_Color_Layer_7A12B)
    bpy.utils.unregister_class(SNA_OT_Toggle_Layer_Editing_17Bff)
    bpy.utils.unregister_class(SNA_OT_Toggle_Layer_Editing_With_Warning_6B0Ab)
    bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_pre_handler_D69F3)
    bpy.utils.unregister_class(SNA_OT_Refresh_Fe2A7)
    bpy.utils.unregister_class(SNA_OT_Showhide_Object_Colors_C831C)
    bpy.utils.unregister_class(SNA_OT_Select_By_Color_Ee838)
    bpy.utils.unregister_class(SNA_OT_Checkpoint_1810D)
    bpy.utils.unregister_class(SNA_OT_Remove_Palette_B653B)
    bpy.utils.unregister_class(SNA_OT_Create_Palette_098Ec)
    bpy.utils.unregister_class(SNA_OT_Add_Palette_Color_631C1)
    bpy.utils.unregister_class(SNA_OT_Remove_Palette_Color_D6Fa3)
    bpy.utils.unregister_class(SNA_OT_Move_Palette_Up_193F8)
    bpy.utils.unregister_class(SNA_OT_Move_Palette_Down_Cce25)
    bpy.utils.unregister_class(SNA_OT_Move_Palette_Color_Down_00593)
    bpy.utils.unregister_class(SNA_OT_Move_Palette_Color_Up_1D220)
    bpy.utils.unregister_class(SNA_OT_Import_Palette_26C39)
    bpy.utils.unregister_class(SNA_OT_Import_Replace_Palette_A4Fca)
    bpy.utils.unregister_class(SNA_OT_Export_Palettes_D17D2)
    bpy.utils.unregister_class(SNA_OT_Export_Ccb_Palette_E3Da4)
    bpy.utils.unregister_class(SNA_OT_Export_Gpl_Palette_B20A0)
    bpy.utils.unregister_class(SNA_UL_display_collection_list002_9846D)
    bpy.utils.unregister_class(SNA_PT_PREFERENCES_1A5FD)
    bpy.utils.unregister_class(SNA_AddonPreferences_0446F)
    bpy.utils.unregister_class(SNA_MT_ED3E4)
    bpy.utils.unregister_class(SNA_OT_Set_Color_Static_3018B)
    bpy.utils.unregister_class(SNA_OT_Set_Color_Abbbf)
    bpy.utils.unregister_class(SNA_OT_Vertx_Artist_Restore_Panel_F0746)
    bpy.utils.unregister_class(SNA_OT_Vertx_Artist_Popout_Fa638)
    bpy.types.VIEW3D_PT_tools_active.remove(sna_add_to_view3d_pt_tools_active_DB2BC)
    bpy.types.VIEW3D_PT_tools_active.remove(sna_add_to_view3d_pt_tools_active_722B0)
    bpy.utils.unregister_class(SNA_OT_Add_Layer_Af10A)
