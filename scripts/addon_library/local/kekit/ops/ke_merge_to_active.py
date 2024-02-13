import bmesh
import bpy
from bpy.types import Operator
from .._utils import vertloops


class KeMergeToActive(Operator):
    bl_idname = "mesh.ke_merge_to_active"
    bl_label = "MergeCollapse"
    bl_description = "VERT MODE: Merge selected verts to the Active vert (as 'Merge To Last')\n" \
                     "- if no Active Vert is in selection Collapse Average is used\n" \
                     "EDGE MODE: Merge selected edges to Active Edge (row) OR Collapse (if no Active edge)\n" \
                     "FACE MODE: Collapse (Average)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        use_collapse = False
        sel_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        # Sel check
        sel_verts = [v for v in bm.verts if v.select]
        if not sel_verts:
            print("Cancelled: Nothing Selected")
            return {"CANCELLED"}

        if sel_mode[1]:
            sel_edges = [e for e in bm.edges if e.select]

            if len(sel_edges) == 1:
                bpy.ops.mesh.merge("INVOKE_DEFAULT", type='COLLAPSE')

            elif len(sel_edges) > 1:
                sh = bm.select_history.active
                ae = sh if sh in sel_edges else []
                if not ae:
                    # print("Active Edge not found in selection - Using vanilla collapse")
                    bpy.ops.mesh.merge("INVOKE_DEFAULT", type='COLLAPSE')
                    return {"FINISHED"}

                sedges = vertloops([e.verts for e in sel_edges])
                start_line = []
                for line in sedges:
                    if ae.verts[0] in line:
                        start_line = line
                        break

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

                for row in collapse_rows:
                    target = [i for i in row if i in start_line][0]
                    if not target:
                        target = row[0]
                    bmesh.ops.pointmerge(bm, verts=row, merge_co=target.co)
                    bmesh.update_edit_mesh(mesh)

                mesh.update()
                # still don't trust blender to update the mesh w/o issue? toggle! ;P
                bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.mode_set(mode="EDIT")

        else:
            # Vert mode
            sh = bm.select_history.active
            ae = sh if sh in sel_verts else []
            if ae:
                bpy.ops.mesh.merge('INVOKE_DEFAULT', type='LAST')
            else:
                bpy.ops.mesh.merge('INVOKE_DEFAULT', type='COLLAPSE')

        return {'FINISHED'}
