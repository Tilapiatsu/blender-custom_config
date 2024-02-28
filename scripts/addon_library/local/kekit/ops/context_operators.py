import bmesh
import bpy
from bpy.types import Operator
from .._utils import find_parents, get_prefs


# BASIC / SIMPLE CONTEXT OPERATORS

class KeContextBevel(Operator):
    bl_idname = "mesh.ke_contextbevel"
    bl_label = "Context Bevel"
    bl_description = "Vert Mode: Vertex Bevel Tool\nEdge Mode: Edge Bevel Tool\nFace Mode: Inset Faces Tool"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and context.object.data.is_editmode)

    def execute(self, context):
        k = get_prefs()
        sel_mode = context.tool_settings.mesh_select_mode[:]
        if k.apply_scale and context.object.library is None and context.object.data.users == 1:
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.editmode_toggle()
            bpy.ops.ed.undo_push()
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
        # k = get_prefs()
        k = context.preferences.addons['kekit'].preferences
        if k.m_tt:
            use_tt = k.tt_extrude
        else:
            use_tt = False

        sel_mode = context.tool_settings.mesh_select_mode[:]

        if context.object.type == 'MESH':
            if sel_mode[0]:
                if use_tt:
                    am = bool(context.scene.tool_settings.use_mesh_automerge)
                    if am:
                        context.scene.tool_settings.use_mesh_automerge = False
                    bpy.ops.mesh.extrude_vertices_move(MESH_OT_extrude_verts_indiv=None, TRANSFORM_OT_translate=None)
                    bpy.ops.ed.undo_push()
                    if am:
                        context.scene.tool_settings.use_mesh_automerge = True
                    bpy.ops.view3d.ke_tt('INVOKE_DEFAULT', True, mode="MOVE")
                else:
                    bpy.ops.mesh.extrude_vertices_move('INVOKE_DEFAULT', True)

            elif sel_mode[1]:
                if use_tt:
                    am = bool(context.scene.tool_settings.use_mesh_automerge)
                    if am:
                        context.scene.tool_settings.use_mesh_automerge = False
                    bpy.ops.mesh.extrude_edges_move(MESH_OT_extrude_edges_indiv=None, TRANSFORM_OT_translate=None)
                    bpy.ops.ed.undo_push()
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
        return context.selected_objects

    def execute(self, context):
        if context.active_object not in context.selected_objects:
            context.view_layer.objects.active = context.selected_objects[0]
        k = get_prefs()
        has_dm = k.m_geo
        if has_dm:
            pluscut = k.cd_pluscut
        else:
            pluscut = False

        smart = bool(k.cd_smart)

        ctx_mode = context.mode
        if ctx_mode == "EDIT_MESH":
            sel_mode = context.tool_settings.mesh_select_mode

            # VERTS
            if sel_mode[0]:
                if smart:
                    bm = bmesh.from_edit_mesh(context.object.data)
                    floaters = [i for i in bm.verts if i.select and len(i.link_edges) < 2]
                    if floaters:
                        bmesh.ops.delete(bm, geom=floaters)
                        bmesh.update_edit_mesh(context.object.data)
                    else:
                        bpy.ops.mesh.ke_contextdissolve('INVOKE_DEFAULT', True)
                else:
                    bpy.ops.mesh.delete(type='VERT')

            # EDGES
            elif sel_mode[1]:
                if smart:
                    bm = bmesh.from_edit_mesh(context.object.data)
                    floaters = [i for i in bm.edges if i.select and len(i.link_faces) < 2]
                    if floaters:
                        bpy.ops.mesh.delete(type='EDGE')
                    else:
                        bpy.ops.mesh.ke_contextdissolve('INVOKE_DEFAULT', True)
                else:
                    bpy.ops.mesh.delete(type='EDGE')

            # FACES
            elif sel_mode[2]:
                if has_dm and pluscut:
                    bpy.ops.view3d.ke_copyplus('INVOKE_DEFAULT', True, mode="CUT")
                else:
                    bpy.ops.mesh.delete(type='FACE')

        elif ctx_mode == "OBJECT":
            sel = list(context.selected_objects)
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
    bl_description = "EDGES: loop select, POLYS: Linked select, VERTS: (linked) Border edges\n" \
                     "OBJECT: Hierarchy select with children. Run again to include parents\n" \
                     "Intended for *Double-click select* (Assign in prefs)"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        k = get_prefs()
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
    bl_description = "Extends Context Select. Intended for Shift-Double-click LMB\n" \
                     "(You have to assign dbl-click in preferences)"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        k = get_prefs()
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
    bl_description = "Subtracts Context Select. Intended for Ctrl-Double-click LMB\n" \
                     "(You have to assign dbl-click in preferences)"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        k = get_prefs()
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
