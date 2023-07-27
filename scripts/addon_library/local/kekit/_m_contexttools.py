import bpy
from bpy_types import Panel, Operator
import addon_utils
import bmesh
from ._utils import vertloops, find_parents
from . import ke_contextconnect


class UIContextToolsModule(Panel):
    bl_idname = "UI_PT_M_CONTEXTTOOLS"
    bl_label = "Context Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = ""
    bl_parent_id = "UI_PT_M_MODELING"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        split = row.split(factor=.6, align=True)
        split.operator('mesh.ke_contextbevel')
        row2 = split.row(align=True)
        row2.prop(k, "apply_scale", toggle=True)
        row2.prop(k, "korean", text="K/F", toggle=True)

        row = col.row(align=True)
        row.operator('mesh.ke_contextextrude')
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        row2.prop(k, "tt_extrude", text="TT", toggle=True)

        row = col.row(align=True)
        split = row.split(factor=.6, align=True)
        split.operator('view3d.ke_contextdelete')
        split2 = split.row(align=True)
        split2.prop(k, "cd_smart", text="S", toggle=True)
        split2.prop(k, "h_delete", text="H", toggle=True)
        split2.prop(k, "cd_pluscut", text="+", toggle=True)
        col.operator('mesh.ke_contextdissolve')

        col.separator(factor=0.5)
        row = col.row(align=True)
        split = row.split(factor=.5, align=True)
        split.label(text=" C.Select:")
        row2 = split.row(align=True)
        row2.prop(k, "context_select_h", toggle=True)
        row2.prop(k, "context_select_b", toggle=True)
        row2.prop(k, "context_select_c", toggle=True)
        col.operator('view3d.ke_contextselect')
        col.operator('view3d.ke_contextselect_extend')
        col.operator('view3d.ke_contextselect_subtract')

        col.separator(factor=0.5)
        col.operator('mesh.ke_bridge_or_fill', text="Bridge or Fill")
        col.operator('mesh.ke_context_connect', text="Context Connect")
        col.operator('mesh.ke_triple_connect_spin', text="Triple Connect Spin")
        col.operator('mesh.ke_contextslide')


class KeContextBevel(Operator):
    bl_idname = "mesh.ke_contextbevel"
    bl_label = "Context Bevel"
    bl_description = "Vert Mode: Vertex Bevel Tool\nEdge Mode: Edge Bevel Tool\nFace Mode: Inset Faces Tool"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and context.object.data.is_editmode)

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        sel_mode = context.tool_settings.mesh_select_mode[:]
        if k.apply_scale and context.object.library is None and context.object.data.users == 1:
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.editmode_toggle()
        if sel_mode[0]:
            bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='VERTICES')
        elif sel_mode[1]:
            if k.korean:
                bpy.ops.mesh.bevel('INVOKE_DEFAULT', segments=2, profile=1, affect='EDGES')
            else:
                bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='EDGES')
        elif sel_mode[2]:
            bpy.ops.mesh.inset('INVOKE_DEFAULT', use_outset=False)
        return {'FINISHED'}


class KeContextExtrude(Operator):
    bl_idname = "mesh.ke_contextextrude"
    bl_label = "Context Extrude"
    bl_description = "Vert Mode: Vertex Extrude\nEdge Mode: Edge Extrude\nFace Mode: Face Extrude Normal (Region)"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.mode != "OBJECT")

    def execute(self, context):
        use_tt = context.preferences.addons[__package__].preferences.tt_extrude
        sel_mode = context.tool_settings.mesh_select_mode[:]

        if context.object.type == 'MESH':
            if sel_mode[0]:
                if use_tt:
                    am = bool(context.scene.tool_settings.use_mesh_automerge)
                    if am:
                        context.scene.tool_settings.use_mesh_automerge = False
                    bpy.ops.mesh.extrude_vertices_move(MESH_OT_extrude_verts_indiv=None, TRANSFORM_OT_translate=None)
                    if am:
                        context.scene.tool_settings.use_mesh_automerge = True
                    bpy.ops.view3d.ke_tt('INVOKE_DEFAULT', True, mode="MOVE")
                else:
                    bpy.ops.mesh.extrude_vertices_move('INVOKE_DEFAULT', True)

            elif sel_mode[1]:
                # bpy.ops.mesh.ke_offset_edges('EXEC_DEFAULT', True)  # todo: make Modal to completely replace built-in
                if use_tt:
                    am = bool(context.scene.tool_settings.use_mesh_automerge)
                    if am:
                        context.scene.tool_settings.use_mesh_automerge = False
                    bpy.ops.mesh.extrude_edges_move(MESH_OT_extrude_edges_indiv=None, TRANSFORM_OT_translate=None)
                    if am:
                        context.scene.tool_settings.use_mesh_automerge = True
                    bpy.ops.view3d.ke_tt('INVOKE_DEFAULT', mode="MOVE")
                else:
                    bpy.ops.mesh.extrude_edges_move('INVOKE_DEFAULT')

            elif sel_mode[2]:
                bpy.ops.view3d.edit_mesh_extrude_move_normal('INVOKE_DEFAULT', True)

        elif context.object.type == 'CURVE':
            if use_tt:
                bpy.ops.curve.extrude()
                bpy.ops.view3d.ke_tt('INVOKE_DEFAULT', mode="MOVE")
            else:
                bpy.ops.curve.extrude_move('INVOKE_DEFAULT')
        elif context.object.type == "GPENCIL":
            if use_tt:
                bpy.ops.gpencil.extrude()
                bpy.ops.view3d.ke_tt('INVOKE_DEFAULT', mode="MOVE")
            else:
                bpy.ops.gpencil.extrude_move('INVOKE_DEFAULT')

        return {'FINISHED'}


class KeContextDelete(Operator):
    bl_idname = "view3d.ke_contextdelete"
    bl_label = "Context Delete"
    bl_description = "Deletes selection by selection mode (VERTEX, EDGE, FACE or OBJECT)"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        has_dm = k.m_dupe
        pluscut = k.cd_pluscut
        smart = bool(k.cd_smart)

        ctx_mode = context.mode
        if ctx_mode == "EDIT_MESH":
            if smart:
                bm = bmesh.from_edit_mesh(context.object.data)
                floaters = [i for i in bm.verts if i.select and not i.link_faces]
                if floaters:
                    for v in floaters:
                        bm.verts.remove(v)
                    bmesh.update_edit_mesh(context.object.data)
            sel_mode = context.tool_settings.mesh_select_mode
            if sel_mode[0]:
                if smart:
                    bpy.ops.mesh.ke_contextdissolve('INVOKE_DEFAULT', True)
                else:
                    bpy.ops.mesh.delete(type='VERT')
            elif sel_mode[1]:
                if smart:
                    bpy.ops.mesh.ke_contextdissolve('INVOKE_DEFAULT', True)
                else:
                    bpy.ops.mesh.delete(type='EDGE')
            elif sel_mode[2]:
                if has_dm and pluscut:
                    bpy.ops.view3d.ke_copyplus('INVOKE_DEFAULT', True, mode="CUT")
                else:
                    bpy.ops.mesh.delete(type='FACE')

        elif ctx_mode == "OBJECT":
            sel = context.selected_objects[:]
            if k.h_delete:
                for o in sel:
                    for child in o.children:
                        sel.append(child)
            sel = list(set(sel))

            if has_dm and pluscut:
                for item in sel:
                    item.select_set(True)
                bpy.ops.view3d.ke_copyplus('INVOKE_DEFAULT', True, mode="CUT")
            else:
                for item in sel:
                    bpy.data.objects.remove(item, do_unlink=True)

        elif context.object.type == "GPENCIL" and ctx_mode != "OBJECT":
            bpy.ops.gpencil.delete(type='POINTS')

        elif context.object.type == "CURVE" and ctx_mode != "OBJECT":
            bpy.ops.curve.delete(type='VERT')

        return {'FINISHED'}


class KeContextDissolve(Operator):
    bl_idname = "mesh.ke_contextdissolve"
    bl_label = "Context Dissolve"
    bl_description = "Dissolves selection by selection mode (VERTEX, EDGE or POLY)"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.mode != "OBJECT")

    def execute(self, context):
        if context.object.type == 'MESH':
            sel_mode = context.tool_settings.mesh_select_mode[:]
            if sel_mode[0]:
                bpy.ops.mesh.dissolve_verts('INVOKE_DEFAULT', True)
            elif sel_mode[1]:
                bpy.ops.mesh.dissolve_edges('INVOKE_DEFAULT', True)
            elif sel_mode[2]:
                bpy.ops.mesh.dissolve_faces('INVOKE_DEFAULT', True)

        elif context.object.type == 'GPENCIL':
            bpy.ops.gpencil.dissolve(type='POINTS')

        elif context.object.type == 'CURVE':
            bpy.ops.curve.dissolve_verts()

        return {'FINISHED'}


class KeContextSelect(Operator):
    bl_idname = "view3d.ke_contextselect"
    bl_label = "Context Select"
    bl_description = "EDGES: loop select, POLYS: Linked select, VERTS: (linked) Border edges" \
                     "OBJECT: Hierarchy select with children. Run again to include parents" \
                     "Intended for Double-click select. (Assign in prefs)"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        if context.mode == "EDIT_MESH":
            sel_mode = context.tool_settings.mesh_select_mode

            if sel_mode[0]:
                if k.context_select_b:
                    bm = bmesh.from_edit_mesh(context.active_object.data)
                    og = [v for v in bm.verts if v.select]
                    bpy.ops.mesh.select_linked(delimit=set())
                    bpy.ops.mesh.region_to_loop()
                    bpy.ops.ed.undo_push()
                    sel_verts = [v for v in bm.verts if v.select]
                    if sel_verts:
                        pass
                        # bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                    else:
                        context.tool_settings.mesh_select_mode = (True, False, False)
                        for v in og:
                            v.select = True
                        bpy.ops.mesh.select_linked(delimit=set())
                else:
                    bpy.ops.mesh.select_linked(delimit=set())
                bpy.ops.ed.undo_push()

            elif sel_mode[1]:
                bpy.ops.mesh.loop_multi_select(True, ring=False)
                bpy.ops.ed.undo_push()

            elif sel_mode[2]:
                bpy.ops.mesh.select_linked(delimit=set())
                bpy.ops.ed.undo_push()

        elif context.mode == "OBJECT":
            children = context.object.children_recursive
            select = children
            if k.context_select_h:
                select += find_parents(context.object)
            if k.context_select_c:
                bpy.ops.object.select_grouped(type='COLLECTION')
            for o in select:
                o.select_set(True)

        return {'FINISHED'}


class KeContextSelectExtend(Operator):
    bl_idname = "view3d.ke_contextselect_extend"
    bl_label = "Context Select Extend"
    bl_description = "Extends Context Select. Intended for Shift-Double-click LMB" \
                     "(You have to assign dbl-click in preferences)"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        if context.mode == "EDIT_MESH":
            sel_mode = context.tool_settings.mesh_select_mode

            if sel_mode[0]:
                bpy.ops.mesh.select_linked(delimit=set())
                if k.context_select_b:
                    bpy.ops.mesh.region_to_loop()
                    # bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.ed.undo_push()

            elif sel_mode[1]:
                bpy.ops.mesh.loop_multi_select(ring=False)
                bpy.ops.ed.undo_push()

            elif sel_mode[2]:
                bpy.ops.mesh.select_linked(delimit=set())
                bpy.ops.ed.undo_push()

        elif context.mode == "OBJECT":
            fh = k.context_select_h
            children = context.object.children_recursive
            select = children
            if fh:
                for o in context.selected_objects:
                    select += o.children_recursive
                    select += find_parents(o)
                select = list(set(select))
            for o in select:
                o.select_set(True)

        return {'FINISHED'}


class KeContextSelectSubtract(Operator):
    bl_idname = "view3d.ke_contextselect_subtract"
    bl_label = "Context Select Subtract"
    bl_description = "Subtracts Context Select. Intended for Ctrl-Double-click LMB" \
                     "(You have to assign dbl-click in preferences)"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        if context.mode == "EDIT_MESH":
            sel_mode = context.tool_settings.mesh_select_mode

            if sel_mode[0]:
                if k.context_select_b:
                    bpy.ops.mesh.select_linked(delimit=set())
                    bpy.ops.mesh.region_to_loop()
                    # bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                else:
                    bpy.ops.mesh.select_linked_pick('INVOKE_DEFAULT', deselect=True)
                bpy.ops.ed.undo_push()

            elif sel_mode[1]:
                bpy.ops.mesh.loop_select('INVOKE_DEFAULT', deselect=True)
                bpy.ops.ed.undo_push()
            elif sel_mode[2]:
                bpy.ops.mesh.select_linked_pick('INVOKE_DEFAULT', deselect=True)
                bpy.ops.ed.undo_push()

        elif context.mode == "OBJECT":
            fh = k.context_select_h
            children = context.object.children_recursive
            select = children
            if fh:
                select += find_parents(context.object)
            for o in select:
                o.select_set(False)

        return {'FINISHED'}


class KeBridgeOrFill(Operator):
    bl_idname = "mesh.ke_bridge_or_fill"
    bl_label = "Bridge or Fill"
    bl_description = "Bridge edge selection, except when ONE continous border edge-loop is selected: Grid Fill\n" \
                     "F2 mode with 1 EDGE or 1 VERT selected\n" \
                     "FACE ADD with two edges (sharing a vert) or 3+ verts in vert mode."

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode[:]

        obj = context.active_object
        mesh = obj.data
        obj.update_from_editmode()

        if sel_mode[0]:
            sel_verts = [v for v in mesh.vertices if v.select]
            if len(sel_verts) == 1:
                try:
                    bpy.ops.mesh.f2('INVOKE_DEFAULT')
                except Exception as e:
                    print("F2 aborted - using Mesh Fill:\n", e)
                    bpy.ops.mesh.fill('INVOKE_DEFAULT')
            elif len(sel_verts) > 2:
                bpy.ops.mesh.edge_face_add()

        if sel_mode[1]:
            vert_pairs = []
            sel_edges = [e for e in mesh.edges if e.select]
            for e in sel_edges:
                vp = [v for v in e.vertices]
                vert_pairs.append(vp)

            if len(sel_edges) == 1:
                try:
                    bpy.ops.mesh.f2('INVOKE_DEFAULT')
                except Exception as e:
                    print("F2 aborted - using Mesh Fill:\n", e)
                    bpy.ops.mesh.fill('INVOKE_DEFAULT')

            elif vert_pairs:
                if len(sel_edges) == 2:
                    tri_check = len(list(set(vert_pairs[0] + vert_pairs[1])))
                    if tri_check < 4:
                        bm = bmesh.from_edit_mesh(mesh)
                        bm.verts.ensure_lookup_table()
                        sel_verts = [v for v in bm.verts if v.select]
                        new = bm.faces.new([bm.verts[i.index] for i in sel_verts])
                        uv_layer = bm.loops.layers.uv.verify()
                        for loop in new.loops:
                            loop_uv = loop[uv_layer]
                            loop_uv.uv[0] = loop.vert.co.x + 0.5
                            loop_uv.uv[1] = loop.vert.co.y + 0.5
                        bmesh.update_edit_mesh(mesh)

                check_loops = vertloops(vert_pairs)
                if len(check_loops) == 1 and check_loops[0][0] == check_loops[-1][-1] and len(sel_edges) % 2 == 0:
                    try:
                        bpy.ops.mesh.fill_grid('INVOKE_DEFAULT', True)
                    except Exception as e:
                        print("Fill Grid aborted - using F2 or Mesh Fill:\n", e)
                        try:
                            bpy.ops.mesh.f2('INVOKE_DEFAULT')
                        except Exception as e:
                            print("F2 aborted - using Mesh Fill:\n", e)
                            bpy.ops.mesh.fill('INVOKE_DEFAULT')
                else:
                    if len(sel_edges) % 2 != 0:
                        bpy.ops.mesh.fill('INVOKE_DEFAULT')
                    else:
                        try:
                            bpy.ops.mesh.bridge_edge_loops('INVOKE_DEFAULT', True)
                        except Exception as e:
                            print("Bridge Edge Loops aborted: \n", e)

        return {'FINISHED'}


class KeTripleConnectSpin(Operator):
    bl_idname = "mesh.ke_triple_connect_spin"
    bl_label = "TripleConnectSpin"
    bl_description = "VERTS: Connect Verts, EDGE(s): Spin, FACE(s): Triangulate"
    bl_options = {'REGISTER', 'UNDO'}

    connect_mode: bpy.props.EnumProperty(
        items=[("PATH", "Vertex Path", "", 1),
               ("PAIR", "Vertex Pair", "", 2),
               ("ACTIVE", "Selected To Active", "", 3)],
        name="Vertex Connect",
        default="PATH")

    spin_mode: bpy.props.EnumProperty(
        items=[("CW", "Clockwise", "", 1),
               ("CCW", "Counter Clockwise", "", 2)],
        name="Edge Spin",
        default="CW")

    triple_mode: bpy.props.EnumProperty(
        items=[("BEAUTY", "Beauty Method", "", 1),
               ("FIXED", "Fixed/Clip Method", "", 2)],
        name="Face Triangulation",
        default="BEAUTY")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        selection = False

        bpy.ops.object.mode_set(mode='OBJECT')
        for v in context.object.data.vertices:
            if v.select:
                selection = True
                break
        bpy.ops.object.mode_set(mode='EDIT')

        if selection:
            sel_mode = context.tool_settings.mesh_select_mode[:]

            if sel_mode[0]:
                if self.connect_mode == 'PATH':
                    try:
                        bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
                    except Exception as e:
                        print("Connect Path fail: Using Vert Connect instead", e)
                        bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')

                elif self.connect_mode == 'PAIR':
                    bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')

                elif self.connect_mode == 'ACTIVE':
                    # (Modified) contribution by: Wahyu Nugraha
                    obj = context.object
                    me = obj.data
                    bm = bmesh.from_edit_mesh(me)
                    sel_verts = [v for v in bm.verts if v.select]
                    active = bm.select_history.active

                    if len(sel_verts) < 2 or not active:
                        self.report({"INFO"}, "Invalid selection")
                        return {'CANCELLED'}

                    for v in sel_verts:
                        v.select_set(False)

                    sel_verts = [v for v in sel_verts if v != active]
                    for v in sel_verts:
                        pair = [v, active]
                        bmesh.ops.connect_verts(bm, verts=pair)

                    bmesh.update_edit_mesh(me)

            elif sel_mode[1]:
                try:
                    if self.spin_mode == 'CW':
                        bpy.ops.mesh.edge_rotate(use_ccw=False)
                    elif self.spin_mode == 'CCW':
                        bpy.ops.mesh.edge_rotate(use_ccw=True)
                except Exception as e:
                    self.report({"INFO"}, "TripleConnectSpin: Invalid Edge Selection?")
                    print(e)
                    return {'CANCELLED'}

            elif sel_mode[2]:
                if self.triple_mode == 'BEAUTY':
                    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
                elif self.triple_mode == 'FIXED':
                    bpy.ops.mesh.quads_convert_to_tris(quad_method='FIXED', ngon_method='CLIP')
        else:
            return {'CANCELLED'}

        return {'FINISHED'}


class KeContextSlide(Operator):
    bl_idname = "mesh.ke_contextslide"
    bl_label = "Context Slide"
    bl_description = "Alternative one-click for double-G slide."

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode
        if sel_mode[0]:
            bpy.ops.transform.vert_slide("INVOKE_DEFAULT")
        else:
            bpy.ops.transform.edge_slide("INVOKE_DEFAULT")

        return {'FINISHED'}


classes = (
    UIContextToolsModule,
    KeContextBevel,
    KeContextExtrude,
    KeContextDelete,
    KeContextDissolve,
    KeContextSelect,
    KeContextSelectExtend,
    KeContextSelectSubtract,
    KeBridgeOrFill,
    KeTripleConnectSpin,
    KeContextSlide
)

modules = (
    ke_contextconnect,
)


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_contexttools:
        try:
            if not bpy.context.preferences.addons[__package__].preferences.m_modeling:
                UIContextToolsModule.bl_category = __package__
                UIContextToolsModule.bl_parent_id = ""
            else:
                UIContextToolsModule.bl_category = ""
                UIContextToolsModule.bl_parent_id = "UI_PT_M_MODELING"
        except Exception as e:
            print("\nkeKit Multicut Panel Error:\n", e)
            pass

        for c in classes:
            bpy.utils.register_class(c)

        for m in modules:
            m.register()


def unregister():
    if "bl_rna" in UIContextToolsModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)

        for m in modules:
            m.unregister()


if __name__ == "__main__":
    register()
