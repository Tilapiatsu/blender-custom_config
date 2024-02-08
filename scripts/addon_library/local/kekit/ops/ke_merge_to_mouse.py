import bmesh
import bpy
from bpy.types import Operator
from mathutils import Vector
from .._utils import vertloops, get_vert_nearest_mouse, get_area_and_type, get_prefs


class KeMergeToMouse(Operator):
    bl_idname = "mesh.ke_merge_to_mouse"
    bl_label = "Merge to Mouse"
    bl_description = "Merge selected verts to the vert nearest the Mouse\n" \
                     "(Tip: You can point to merge (linked) unselected verts!)\n" \
                     "Edge Mode (C): Collapse selected edge rows to edge row nearest Mouse\n" \
                     "Note: In Quad Windows, Merge to Last is used instead"
    bl_options = {'REGISTER', 'UNDO'}

    mouse_pos = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        sel_mode = context.tool_settings.mesh_select_mode[:]

        # QUAD view? maybe later
        areatype = get_area_and_type()[1]
        if areatype == "QUAD":
            bpy.ops.mesh.merge(type='LAST')
            return {'FINISHED'}

        obj = context.object
        obj_mtx = obj.matrix_world.copy()
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        skip_linked = False

        # Sel check
        sel_verts = [v for v in bm.verts if v.select]
        if not sel_verts:
            print("Cancelled: Nothing Selected")
            return {"CANCELLED"}

        if sel_mode[1] and k.merge2mouse_ec:
            sel_edges = [e for e in bm.edges if e.select]

            if len(sel_edges) > 1:
                sedges = vertloops([e.verts for e in sel_edges])
                start_line = []

                close_vert_candidate = get_vert_nearest_mouse(context, self.mouse_pos, sel_verts, obj_mtx)
                for line in sedges:
                    if close_vert_candidate in line:
                        start_line = line

                if not start_line:
                    print("Cancelled: Target Edge Loop not found")
                    return {"CANCELLED"}

                le = []
                for v in sel_verts:
                    for e in v.link_edges:
                        if all(i in sel_verts for i in e.verts) and e not in sel_edges:
                            # Brute linkvert back & forth to cover Triangulation
                            skip = []
                            ce = []
                            for edge in sel_edges:
                                if v in edge.verts:
                                    ce = edge
                                    break
                            ov = e.other_vert(v)
                            skipmatch = [i for i in ce.verts if i != v]
                            for ove in ov.link_edges:
                                rov = ove.other_vert(ov)
                                if rov in skipmatch:
                                    skip.append(e)

                            if e not in skip:
                                le.append(e)

                collapse_rows = vertloops([e.verts for e in list(set(le))])

                if len(collapse_rows) >= 2:
                    for row in collapse_rows:
                        target = [i for i in row if i in start_line][0]
                        if not target:
                            target = row[0]
                        bmesh.ops.pointmerge(bm, verts=row, merge_co=target.co)

                    # Update & Finalize
                    bmesh.update_edit_mesh(mesh)
                    return {'FINISHED'}

        # ELSE VERT MODE MERGE
        context.tool_settings.mesh_select_mode = (True, False, False)
        if skip_linked:
            verts = sel_verts
        else:
            verts = []
            for v in sel_verts:
                for e in v.link_edges:
                    verts.append(e.other_vert(v))

            verts += sel_verts
            verts = list(set(verts))

        merge_point = get_vert_nearest_mouse(context, self.mouse_pos, verts, obj_mtx)

        if merge_point:
            if merge_point not in sel_verts:
                sel_verts.append(merge_point)
            bmesh.ops.pointmerge(bm, verts=sel_verts, merge_co=merge_point.co)
            bm.select_flush_mode()
            bmesh.update_edit_mesh(obj.data)

        context.tool_settings.mesh_select_mode = (sel_mode[0], sel_mode[1], sel_mode[2])

        return {'FINISHED'}
