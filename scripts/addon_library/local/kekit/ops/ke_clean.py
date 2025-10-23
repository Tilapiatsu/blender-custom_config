import bmesh
import bpy
from bpy.props import BoolProperty
from bpy.types import Operator
from .._utils import get_prefs, flattened, is_bmvert_collinear


class KeClean(Operator):
    bl_idname = "view3d.ke_clean"
    bl_label = "Macro Mesh Cleaner"
    bl_description = "All the important cleaning operations in one click. Select or Clean.\n" \
                     "Note: Object mode (also multiple objects). Scale will be applied."
    bl_options = {'REGISTER', 'UNDO'}

    select_only: BoolProperty(default=True, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.mode == "OBJECT" and
                context.object.select_get() and
                context.object.type == 'MESH')

    def execute(self, context):
        k = get_prefs()
        # props
        doubles = k.clean_doubles
        doubles_val = k.clean_doubles_val
        loose = k.clean_loose
        interior = k.clean_interior
        degenerate = k.clean_degenerate
        collinear = k.clean_collinear
        tinyedges = k.clean_tinyedge
        tinyedges_val = k.clean_tinyedge_val
        tv = 3.1415 - (k.clean_collinear_val * 0.0031415)
        set_edit_mode = False

        # PRESELECTION
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        if not sel_obj:
            return {"CANCELLED"}

        single_object = True if len(sel_obj) == 1 else False
        report = {}
        mes_found = ""

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action='DESELECT')

        for o in sel_obj:
            # SELECT
            set_edit_mode = False
            o.select_set(state=True)
            context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.mode_set(mode="EDIT")

            sel_count = 0
            precount = int(len(o.data.vertices))

            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action="DESELECT")
            # lame (but solid) update
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.editmode_toggle()

            bm_select = []
            bm_dissolve = []
            bm_delete = []
            mes = []

            if interior:
                bpy.ops.mesh.select_non_manifold(extend=True, use_wire=True, use_multi_face=True,
                                                 use_non_contiguous=True, use_verts=True, use_boundary=False)
                sel_count += len([v for v in o.data.vertices if v.select])
                if not self.select_only:
                    bpy.ops.mesh.delete(type='FACE')

            # And the rest in BMesh
            me = o.data
            bm = bmesh.from_edit_mesh(me)

            if doubles:
                result = bmesh.ops.find_doubles(bm, verts=bm.verts, dist=doubles_val)
                verts = [i for i in result['targetmap'] if isinstance(i, bmesh.types.BMVert)]
                bm_select.extend(verts)
                if not self.select_only:
                    bmesh.ops.weld_verts(bm, targetmap=result['targetmap'])
                    bm.verts.ensure_lookup_table()

            if loose:
                lv = [v for v in bm.verts if len(v.link_edges) <= 1]
                bm_select.extend(lv)
                bm_dissolve.extend(lv)

            if degenerate:
                degenerate_verts = set()
                for e in bm.edges:
                    if e.calc_length() < doubles_val:
                        for v in e.verts:
                            degenerate_verts.add(v)
                bm_select.extend(degenerate_verts)
                mes.extend(degenerate_verts)

            if collinear:
                cvs = [v for v in bm.verts if is_bmvert_collinear(v, tolerance=tv)]
                bm_select.extend(cvs)
                bm_dissolve.extend(cvs)

            if tinyedges:
                tmes = flattened([e.verts for e in bm.edges if e.calc_length() < tinyedges_val])
                mes.extend(tmes)
                bm_select.extend(tmes)

            # PROCESS
            if not self.select_only:
                bm_dissolve = list(set(bm_dissolve))
                bmesh.ops.dissolve_verts(bm, verts=bm_dissolve)

                bm_delete = [v for v in bm_delete if v.is_valid]
                bm_delete = list(set(bm_delete))
                bmesh.ops.delete(bm, geom=bm_delete)
                if mes:
                    mes = [v for v in bm_select if v.is_valid]
                    if len(mes) > 1:
                        mes_found = "Select Only Items: Tiny and/or Degenerate Edges Found & Selected!-"
                        for v in mes:
                            v.select_set(True)
            else:
                bm_select = list(set(bm_select))
                for v in bm_select:
                    v.select_set(True)

            bmesh.update_edit_mesh(me)
            bpy.ops.object.mode_set(mode="OBJECT")

            # TALLY
            sel_count += len(bm_select)
            postcount = int(len(o.data.vertices))
            vert_count = precount - postcount
            if vert_count > 0:
                print("### Removed %s verts from %s ###" % ((precount - postcount), o.name))
                report[o.name] = vert_count
            if sel_count > 0:
                print("### Found %s verts in %s ###" % (sel_count, o.name))
                report[o.name] = sel_count
                set_edit_mode = True

            if not set_edit_mode:
                o.select_set(state=False)
            else:
                o.select_set(state=True)

        if single_object and set_edit_mode:
            bpy.ops.object.mode_set(mode="EDIT")

        # bpy.ops.object.mode_set(mode=og_mode)
        if report:
            tot = "Total: " + str(sum(report.values()))
            final_report = str(report)
            if len(final_report) > 64:
                final_report = final_report[:62] + "..."
            if mes_found:
                tot = mes_found + tot
            self.report({"INFO"}, "%s, %s" % (tot, final_report))
        else:
            self.report({"INFO"}, "All Good!")

        return {"FINISHED"}
