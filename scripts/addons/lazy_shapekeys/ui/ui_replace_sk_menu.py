import bpy,re
from bpy.props import *
from bpy.types import Panel, UIList
from ..utils import preference


#
class LAZYSHAPEKEYS_UL_replace_menu(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        addon_prefs = preference()
        # assert(isinstance(item, bpy.types.ShapeKey))
        obj = active_data
        # key = data
        key_block = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.66, align=False)
            row = split.row(align=True)
            use_folder_l = [sk for i,sk in enumerate(obj.data.shape_keys.key_blocks) if re.findall("^%s" % addon_prefs.folder_token,sk.name)]
            if use_folder_l:
                if not re.findall("^%s" % addon_prefs.folder_token,item.name):
                    row.label(text="",icon="BLANK1")
                    row.prop(key_block, "name", text="", emboss=False, icon_value=icon)
                else:
                    row.prop(key_block, "name", text="", emboss=False,icon="FILE_FOLDER")
            else:
                row.prop(key_block, "name", text="", emboss=False, icon_value=icon)


            row = split.row(align=True)
            if addon_prefs.sk_menu_use_slider:
                row.emboss = "NORMAL"
            else:
                row.emboss = 'NONE_OR_STATUS'
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                row.active = False
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="")
            elif index > 0:
                row.prop(key_block, "value", text="",slider=addon_prefs.sk_menu_use_slider)
            else:
                row.label(text="")
            row.prop(key_block, "mute", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)






# class MeshButtonsPanel:
#     bl_space_type = 'PROPERTIES'
#     bl_region_type = 'WINDOW'
#     bl_context = "data"
#
#     @classmethod
#     def poll(cls, context):
#         engine = context.engine
#         return context.mesh and (engine in cls.COMPAT_ENGINES)
#
#
# class LAZYSHAPEKEYS_PT_shape_keys(MeshButtonsPanel, Panel):
#     bl_label = "Shape Keys"
#     COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
#
#     @classmethod
#     def poll(cls, context):
#         engine = context.engine
#         obj = context.object
#         return (obj and obj.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'} and (engine in cls.COMPAT_ENGINES))

def LAZYSHAPEKEYS_PT_shape_keys(self, context):
    layout = self.layout

    ob = context.object
    key = ob.data.shape_keys
    kb = ob.active_shape_key

    enable_edit = ob.mode != 'EDIT'
    enable_edit_value = False
    enable_pin = False

    if enable_edit or (ob.use_shape_key_edit_mode and ob.type == 'MESH'):
        enable_pin = True
        if ob.show_only_shape_key is False:
            enable_edit_value = True

    row = layout.row()

    rows = 3
    if kb:
        rows = 5

    # row.template_list("MESH_UL_shape_keys", "", key, "key_blocks", ob, "active_shape_key_index", rows=rows)
    row.template_list("LAZYSHAPEKEYS_UL_replace_menu", "", key, "key_blocks", ob, "active_shape_key_index", rows=rows)

    col = row.column(align=True)

    col.operator("object.shape_key_add", icon='ADD', text="").from_mix = False
    col.operator("object.shape_key_remove", icon='REMOVE', text="").all = False

    col.separator()

    col.menu("MESH_MT_shape_key_context_menu", icon='DOWNARROW_HLT', text="")

    if kb:
        col.separator()

        sub = col.column(align=True)
        sub.operator("object.shape_key_move", icon='TRIA_UP', text="").type = 'UP'
        sub.operator("object.shape_key_move", icon='TRIA_DOWN', text="").type = 'DOWN'

        split = layout.split(factor=0.4)
        row = split.row()
        row.enabled = enable_edit
        row.prop(key, "use_relative")

        row = split.row()
        row.alignment = 'RIGHT'

        sub = row.row(align=True)
        sub.label()  # XXX, for alignment only
        subsub = sub.row(align=True)
        subsub.active = enable_pin
        subsub.prop(ob, "show_only_shape_key", text="")
        sub.prop(ob, "use_shape_key_edit_mode", text="")

        sub = row.row()
        if key.use_relative:
            sub.operator("object.shape_key_clear", icon='X', text="")
        else:
            sub.operator("object.shape_key_retime", icon='RECOVER_LAST', text="")

        layout.use_property_split = True
        if key.use_relative:
            if ob.active_shape_key_index != 0:
                row = layout.row()
                row.active = enable_edit_value
                row.prop(kb, "value")

                col = layout.column()
                sub.active = enable_edit_value
                sub = col.column(align=True)
                sub.prop(kb, "slider_min", text="Range Min")
                sub.prop(kb, "slider_max", text="Max")

                col.prop_search(kb, "vertex_group", ob, "vertex_groups", text="Vertex Group")
                col.prop_search(kb, "relative_key", key, "key_blocks", text="Relative To")

        else:
            layout.prop(kb, "interpolation")
            row = layout.column()
            row.active = enable_edit_value
            row.prop(key, "eval_time")
