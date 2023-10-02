import addon_utils
from bpy.types import Menu
from .._utils import get_prefs


class KePieMisc(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_misc"
    bl_label = "ke.misc"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return (context.space_data.type == "VIEW_3D" and
                context.object and
                k.m_modeling and
                k.m_geo)

    def draw(self, context):
        # SEKALAISTA PIIRAKKA  ^ - ^
        k = get_prefs()
        mode = context.mode
        layout = self.layout
        pie = layout.menu_pie()
        f_val = 0.1

        looptools, quickpipe, meshtools = False, False, False
        looptools_c = addon_utils.check("mesh_looptools")
        quickpipe_c = addon_utils.check("quick_pipe")
        meshtools_c = addon_utils.check("mesh_tools")

        if looptools_c[0] and looptools_c[1]:
            looptools = True
        if quickpipe_c[0] and quickpipe_c[1]:
            quickpipe = True
        if meshtools_c[0] and meshtools_c[1]:
            meshtools = True

        # LÄNSI JA ITÄ
        if mode != "OBJECT":
            pie.operator('mesh.ke_activeslice', text="Active Slice")
            if looptools:
                pie.operator('mesh.looptools_circle', text="Circle      ")
            else:
                box = pie.box()
                box.enabled = False
                box.label(text="LoopTools N/A")
        elif mode == "OBJECT":
            pie.operator('view3d.ke_lineararray')
            pie.operator('view3d.ke_radialarray')

        # ETELÄ (LAATIKKO)
        col = pie.column()
        col.ui_units_x = 6
        col.separator(factor=1)
        fx_val = 0.5

        colbox = col.box()
        box = colbox.column(align=True)
        t = context.scene.tool_settings
        row = box.row(align=True)
        row.alignment = "CENTER"
        if mode == "OBJECT":
            row.prop(t, 'use_transform_data_origin', icon_only=True, icon="TRANSFORM_ORIGINS", toggle=True)
            row.separator(factor=fx_val)
            row.prop(t, 'use_transform_pivot_point_align', icon_only=True, icon="OBJECT_ORIGIN", toggle=True)
            row.separator(factor=fx_val)
            row.prop(t, 'use_transform_skip_children', icon_only=True, icon="CON_CHILDOF", toggle=True)
        else:
            row.prop(t, 'use_transform_correct_face_attributes', icon_only=True, icon="MOD_MESHDEFORM", toggle=True)
            if t.use_transform_correct_face_attributes:
                row.prop(t, 'use_transform_correct_keep_connected', icon_only=True, icon="SNAP_VERTEX", toggle=True)
            row.separator(factor=fx_val)
            row.prop(t, 'use_edge_path_live_unwrap', icon_only=True, icon="MOD_UVPROJECT", toggle=True)
            row.separator(factor=fx_val)
            row.prop(t, 'use_mesh_automerge', text="", toggle=True)
            if t.use_mesh_automerge:
                box.separator(factor=fx_val)
                row = box.row(align=True)
                row.alignment = "CENTER"
                if k.experimental:
                    row.prop(t, 'use_mesh_automerge_and_split', text="", toggle=True)
                    row.prop(t, 'double_threshold', text="", toggle=True)
                else:
                    row.enabled = False
                    row.label(text="N/A-Exp.Only")

        colbox = col.box()
        box = colbox.column(align=True)
        if mode == "EDIT_MESH":
            box.operator('wm.tool_set_by_id', text="Smooth      ").name = 'builtin.smooth'
            box.separator(factor=f_val)
            box.operator('wm.tool_set_by_id', text="Randomize").name = 'builtin.randomize'
            box.separator(factor=f_val)
            box.operator('wm.tool_set_by_id', text="Shrink/Fatten").name = 'builtin.shrink_fatten'
            box.separator(factor=f_val)
            box.operator('wm.tool_set_by_id', text="Shear").name = 'builtin.shear'
        else:
            box.operator('object.randomize_transform')
        box.separator(factor=f_val)
        box.operator('view3d.ke_fit2grid')
        box.separator(factor=f_val)
        box.operator('view3d.ke_collision').col_type = 'BOX'
        box.separator(factor=f_val)
        box.operator('transform.bend')
        box.separator(factor=f_val)
        box.operator('transform.push_pull')
        box.separator(factor=f_val)
        box.operator('transform.tosphere')

        # POHJOINEN
        pie.operator('view3d.ke_nice_project', text="Nice Project")

        # LUODE
        if mode != "OBJECT":
            if quickpipe:
                pie.operator('object.quickpipe')
            else:
                box = pie.box()
                box.enabled = False
                box.label(text="QuickPipe N/A")
        else:
            pie.operator('view3d.ke_quickmeasure').qm_start = "DEFAULT"

        # KOILINEN
        if mode != "OBJECT":
            pie.operator('mesh.ke_unbevel', text="Unbevel      ")
        else:
            pie.menu("VIEW3D_MT_object_convert")

        # LOUNAS
        pie.operator('view3d.ke_quick_origin_move')

        # KAAKKO
        if mode != "OBJECT":
            row = pie.row()
            row.separator(factor=1.5)
            p = row.column()
            p.separator(factor=22)
            p.ui_units_x = 6
            box = p.box()
            col = box.column(align=True)
            if looptools:
                col.operator('mesh.looptools_space', text="Space")
            else:
                row = col.row()
                row.enabled = False
                row.label(text="LoopTools N/A")
            col.separator(factor=0.5)
            if meshtools:
                col.menu_contents('VIEW3D_MT_ke_edit_mesh')
            else:
                row = col.row()
                row.enabled = False
                row.label(text="EditMesh Tools N/A")
                col.separator(factor=20)

        else:
            pie.operator('view3d.ke_zerolocal')


class KeMenuEditMesh(Menu):
    bl_idname = "VIEW3D_MT_ke_edit_mesh"
    bl_label = "MeshTools"

    def draw(self, context):
        layout = self.layout
        layout.operator('mesh.offset_edges', text="Offset Edges")
        layout.operator('mesh.vertex_chamfer', text="Vertex Chamfer")
        layout.operator('mesh.fillet_plus', text="Fillet Edges")
        layout.operator("mesh.face_inset_fillet", text="Face Inset Fillet")
        layout.operator("object.mextrude", text="Multi Extrude")
        layout.operator('mesh.split_solidify', text="Split Solidify")
        layout.operator("mesh.random_vertices", text="Random Vertices")
        layout.operator('object.mesh_edge_length_set', text="Set Edge Length")
        layout.operator('mesh.edges_floor_plan', text="Edges Floor Plan")
        layout.operator('mesh.edge_roundifier', text="Edge Roundify")
