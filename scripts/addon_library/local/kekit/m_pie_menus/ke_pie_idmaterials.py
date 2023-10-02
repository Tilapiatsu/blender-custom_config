from math import ceil

import addon_utils
import bpy
from bpy.types import Menu
from .._utils import get_prefs


class KePieMaterials(Menu):
    bl_label = "keMaterials"
    bl_idname = "VIEW3D_MT_PIE_ke_materials"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_render

    def draw(self, context):
        c = addon_utils.check("materials_utils")
        k = get_prefs()
        op = "view3d.ke_id_material"
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        box = pie.box()
        box.ui_units_x = 7
        col = box.column(align=True)
        col.label(text="Assign ID Material")
        row = col.row(align=True)
        row.template_node_socket(color=k.idm01)
        row.operator(op, text=k.idm01_name).m_id = 1
        row = col.row(align=True)
        row.template_node_socket(color=k.idm02)
        row.operator(op, text=k.idm02_name).m_id = 2
        row = col.row(align=True)
        row.template_node_socket(color=k.idm03)
        row.operator(op, text=k.idm03_name).m_id = 3
        row = col.row(align=True)
        row.template_node_socket(color=k.idm04)
        row.operator(op, text=k.idm04_name).m_id = 4
        row = col.row(align=True)
        row.template_node_socket(color=k.idm05)
        row.operator(op, text=k.idm05_name).m_id = 5
        row = col.row(align=True)
        row.template_node_socket(color=k.idm06)
        row.operator(op, text=k.idm06_name).m_id = 6
        row = col.row(align=True)
        row.template_node_socket(color=k.idm07)
        row.operator(op, text=k.idm07_name).m_id = 7
        row = col.row(align=True)
        row.template_node_socket(color=k.idm08)
        row.operator(op, text=k.idm08_name).m_id = 8
        row = col.row(align=True)
        row.template_node_socket(color=k.idm09)
        row.operator(op, text=k.idm09_name).m_id = 9
        row = col.row(align=True)
        row.template_node_socket(color=k.idm10)
        row.operator(op, text=k.idm10_name).m_id = 10
        row = col.row(align=True)
        row.template_node_socket(color=k.idm11)
        row.operator(op, text=k.idm11_name).m_id = 11
        row = col.row(align=True)
        row.template_node_socket(color=k.idm12)
        row.operator(op, text=k.idm12_name).m_id = 12

        if c[0] and c[1]:
            # obj = context.object
            mu_prefs = context.preferences.addons["materials_utils"].preferences
            limit = mu_prefs.search_show_limit
            if limit == 0:
                limit = "Inf."
            mat_count = len(bpy.data.materials)
            split_count = 32 if mat_count > 64 else 11
            col_count = ceil((mat_count / split_count))

            # ASSIGN MATERIALS BOX - RIGHT -------------------------------------------------
            box = pie.box()
            if col_count < 2:
                box.ui_units_x = 7.5
            box.label(text="Assign Material  [%s / %s]" % (mat_count, limit))
            col = box.column_flow(align=False, columns=col_count)
            col.ui_units_x = 6 * col_count
            col.menu_contents("VIEW3D_MT_materialutilities_assign_material")

            # MATERIALS UTILS MAIN BOX - BOTTOM --------------------------------------------
            main = pie.column()
            main.separator(factor=4)
            box = main.box()
            box.ui_units_x = 8
            col = box.column(align=True)
            # col.menu_contents("VIEW3D_MT_materialutilities_main")
            col.menu('VIEW3D_MT_materialutilities_select_by_material',
                     icon='VIEWZOOM')
            col.separator()
            col.operator('VIEW3D_OT_materialutilities_copy_material_to_others',
                         text='Copy Active to Others',
                         icon='COPY_ID')
            col.separator()
            col.menu('VIEW3D_MT_materialutilities_clean_slots',
                     icon='NODE_MATERIAL')
            col.separator()
            col.operator('VIEW3D_OT_materialutilities_replace_material',
                         text='Replace Material',
                         icon='OVERLAY')
            op = col.operator('VIEW3D_OT_materialutilities_fake_user_set',
                              text='Set Fake User',
                              icon='FAKE_USER_OFF')
            op.fake_user = mu_prefs.fake_user
            op.affect = mu_prefs.fake_user_affect
            op = col.operator('VIEW3D_OT_materialutilities_change_material_link',
                              text='Change Material Link',
                              icon='LINKED')
            op.link_to = mu_prefs.link_to
            op.affect = mu_prefs.link_to_affect
            col.separator()
            col.prop(mu_prefs, "search_show_limit")
            col.menu('VIEW3D_MT_materialutilities_specials',
                     icon='SOLO_ON')
        else:
            pie.label(text="Material Utils Add-on Not Enabled")
