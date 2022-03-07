import bpy, re
from bpy.props import *
from bpy.types import Panel
from ..utils import preference


class LAZYSHAPEKEYS_PT_main(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Addons'
    bl_label = "Lazy Shapekeys"
    bl_options = {'DEFAULT_CLOSED'}


    # @classmethod
    # def poll(cls, context):
    #     if bpy.context.object:
    #         obj = bpy.context.object
    #         if obj.type in {"MESH", "CURVE", "SURFACE", "META", "FONT","LATTICE"}:
    #             return True


    def draw(self, context):
        layout = self.layout
        # addon_prefs = preference()
        props = bpy.context.scene.lazy_shapekeys
        colle = bpy.context.scene.lazy_shapekeys_colle

        layout.operator("lazy_shapekeys.shape_keys_sync_update",icon="NONE")
        layout.prop(props,"tgt_colle")

        layout.separator()
        # if colle:
        #     box = layout.box()
        # for item in colle:
        #     row = box.row()
        #     row.prop(item,"mute",text="",icon="CHECKBOX_DEHLT" if item.mute else "CHECKBOX_HLT",emboss=False)
        #     row.prop(item,"value",text=item.name,slider=True)


        layout.template_list("LAZYSHAPEKEYS_UL_sync_list", "", bpy.context.scene, "lazy_shapekeys_colle", props, "sync_colle_index", rows=5)


        # obj = bpy.context.object
        # if not obj.data.shape_keys:
        #     return
        #
        # col_main = layout.column(align=True)
        # is_space = False
        # for i,sk in enumerate(obj.data.shape_keys.key_blocks):
        #     if sk.name == "Basis":
        #         continue
        #     if re.findall("^@",sk.name):
        #         col_main.separator()
        #         col_main.prop(sk,"name",text="",emboss=False)
        #         is_space = True
        #         continue
        #     row = col_main.row(align=True)
        #     if is_space:
        #         row.label(text="",icon="BLANK1")
        #     row.prop(sk,"mute",text="",icon="CHECKBOX_HLT",emboss=False)
        #     rows = row.row(align=True)
        #     if sk.mute:
        #         rows.active = False
        #     rows.prop(sk,"value",text=sk.name,slider=True)
