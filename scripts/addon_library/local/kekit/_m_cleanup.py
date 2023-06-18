import bpy
import bmesh
from bpy.types import Panel, Operator
from mathutils import Vector
from ._utils import average_vector, flattened


#
# MODULE UI
#
class UICleanUpToolsModule(Panel):
    bl_idname = "UI_PT_M_CLEANUPTOOLS"
    bl_label = "Clean-Up Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Macro Mesh Clean")
        row = col.row(align=True)
        row.operator('view3d.ke_clean', text="Select").select_only = True
        row.operator('view3d.ke_clean', text="Clean").select_only = False
        col.separator(factor=0.5)
        col.prop(k, "clean_doubles")
        col.prop(k, "clean_loose")
        col.prop(k, "clean_interior")
        col.prop(k, "clean_degenerate")
        col.prop(k, "clean_collinear")
        col.prop(k, "clean_tinyedge")
        col.prop(k, "clean_tinyedge_val")
        col = layout.column(align=True)
        col.label(text="Purge")
        boxrow = col.row(align=True)
        boxrow.operator('view3d.ke_purge', text="Mesh").block_type = "MESH"
        boxrow.operator('view3d.ke_purge', text="Material").block_type = "MATERIAL"
        boxrow.operator('view3d.ke_purge', text="Texture").block_type = "TEXTURE"
        boxrow.operator('view3d.ke_purge', text="Image").block_type = "IMAGE"
        col.operator('outliner.orphans_purge', text="Purge All Orphaned Data")
        col.label(text="Selection Tools")
        col.operator('mesh.ke_select_collinear')
        col.operator('mesh.ke_select_flipped_normal')
        col.label(text="Select Elements by Vert Count:")
        row = col.row(align=True)
        row.operator('view3d.ke_vert_count_select', text="0").sel_count = "0"
        row.operator('view3d.ke_vert_count_select', text="1").sel_count = "1"
        row.operator('view3d.ke_vert_count_select', text="2").sel_count = "2"
        row.operator('view3d.ke_vert_count_select', text="3").sel_count = "3"
        row.operator('view3d.ke_vert_count_select', text="4").sel_count = "4"
        row.operator('view3d.ke_vert_count_select', text="5+").sel_count = "5"


#
# MODULE OPERATORS (MISC)
#
def is_bmvert_collinear(v):
    le = v.link_edges
    if len(le) == 2:
        vec1 = Vector(v.co - le[0].other_vert(v).co)
        vec2 = Vector(v.co - le[1].other_vert(v).co)
        if vec1.length and vec2.length:
            if abs(vec1.angle(vec2)) >= 3.1415:
                return True
    return False


class KeClean(Operator):
    bl_idname = "view3d.ke_clean"
    bl_label = "Macro Mesh Cleaner"
    bl_description = "All the important cleaning operations in one click. Select or Clean.\n" \
                     "Note: Object mode (also multiple objects). Scale will be applied."
    bl_options = {'REGISTER', 'UNDO'}

    select_only: bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.mode == "OBJECT" and
                context.object.select_get() and
                context.object.type == 'MESH')

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        # props
        doubles = k.clean_doubles
        doubles_val = k.clean_doubles_val
        loose = k.clean_loose
        interior = k.clean_interior
        degenerate = k.clean_degenerate
        collinear = k.clean_collinear
        tinyedges = k.clean_tinyedge
        tinyedges_val = k.clean_tinyedge_val

        # PRESELECTION
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        if not sel_obj:
            return {"CANCELLED"}

        report = {}
        mes_found = ""

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action='DESELECT')

        for o in sel_obj:
            # SELECT
            o.select_set(state=True)
            context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.mode_set(mode="EDIT")

            sel_count = 0
            precount = int(len(o.data.vertices))

            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.select_mode(type='VERT')

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
                de = flattened([e.verts for e in bm.edges if e.calc_length() < doubles_val])
                df = flattened([f.verts for f in bm.faces if f.calc_area() < doubles_val])
                dv = list(set(de + df))
                bm_select.extend(dv)
                if not self.select_only and dv:
                    result = bmesh.ops.find_doubles(bm, verts=dv, dist=doubles_val)
                    verts = [i for i in result['targetmap'] if isinstance(i, bmesh.types.BMVert)]
                    if verts:
                        bmesh.ops.weld_verts(bm, targetmap=result['targetmap'])
                        bm.verts.ensure_lookup_table()
                    else:
                        bm_delete.extend(dv)

            if collinear:
                cvs = [v for v in bm.verts if is_bmvert_collinear(v)]
                bm_select.extend(cvs)
                bm_dissolve.extend(cvs)

            if tinyedges:
                mes = flattened([e.verts for e in bm.edges if e.calc_length() < tinyedges_val])
                bm_select.extend(mes)

            # PROCESS
            if not self.select_only:
                bm_dissolve = list(set(bm_dissolve))
                bmesh.ops.dissolve_verts(bm, verts=bm_dissolve)

                bm_delete = [v for v in bm_delete if v.is_valid]
                bm_delete = list(set(bm_delete))
                bmesh.ops.delete(bm, geom=bm_delete)
                if tinyedges:
                    mes = [v for v in mes if v.is_valid]
                    if len(mes) > 1:
                        mes_found = "-Tiny Edges (sel only) Found & Selected!-"
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
                print("Removed %s verts from %s" % ((precount - postcount), o.name))
                report[o.name] = vert_count
            if sel_count > 0:
                print("Found %s verts in %s" % (sel_count, o.name))
                report[o.name] = sel_count

            o.select_set(state=False)

        for o in sel_obj:
            o.select_set(state=True)

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


class KeVertCountSelect(Operator):
    bl_idname = "view3d.ke_vert_count_select"
    bl_label = "Vert Count Select"
    bl_description = " Select geo by vert count in selected Object(s) in Edit or Object Mode. (Note: Ngons are 5+)"
    bl_options = {'REGISTER', 'UNDO'}

    sel_count: bpy.props.EnumProperty(
        items=[("0", "Loose Vert", "", 1),
               ("1", "Loose Edge", "", 2),
               ("2", "2 Edges", "", 3),
               ("3", "Tri", "", 4),
               ("4", "Quad", "", 5),
               ("5", "Ngon", "", 6)],
        name="Select Geo by Vert Count",
        default="3")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        nr = int(self.sel_count)
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]

        if not sel_obj:
            self.report({"INFO"}, "Object must be selected!")
            return {"CANCELLED"}

        if context.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')

        for o in sel_obj:
            me = o.data
            bm = bmesh.from_edit_mesh(me)
            bm.verts.ensure_lookup_table()
            selection = []

            if nr <= 2:
                bm.select_mode = {'VERT'}
                for v in bm.verts:
                    le = len(v.link_edges)
                    if le == nr:
                        selection.append(v)

            elif nr >= 3:
                bm.select_mode = {'FACE'}
                for p in bm.faces:
                    pv = len(p.verts)
                    if nr == 5 and pv >= nr:
                        selection.append(p)
                    elif pv == nr:
                        selection.append(p)

            if selection:
                for v in selection:
                    v.select = True

            bm.select_flush_mode()
            bmesh.update_edit_mesh(o.data)

        if nr >= 3:
            context.tool_settings.mesh_select_mode = (False, False, True)
        else:
            context.tool_settings.mesh_select_mode = (True, False, False)

        return {'FINISHED'}


class KePurge(Operator):
    bl_idname = "view3d.ke_purge"
    bl_label = "Purge Unused Data"
    bl_description = "Purge specific unused data blocks\n" \
                     "Note: Deleted meshes will still 'use' materials: Purge meshes first"
    bl_options = {'REGISTER', 'UNDO'}

    block_type: bpy.props.EnumProperty(
        items=[("MESH", "Mesh", "", 1),
               ("MATERIAL", "Materials", "", 2),
               ("TEXTURE", "Textures", "", 3),
               ("IMAGE", "Images", "", 4)],
        name="Purge Data",
        default="MATERIAL")

    def execute(self, context):
        if self.block_type == "MESH":
            for block in bpy.data.meshes:
                if block.users == 0:
                    bpy.data.meshes.remove(block)
        elif self.block_type == "MATERIAL":
            for block in bpy.data.materials:
                if block.users == 0:
                    bpy.data.materials.remove(block)
        elif self.block_type == "TEXTURE":
            for block in bpy.data.textures:
                if block.users == 0:
                    bpy.data.textures.remove(block)
        elif self.block_type == "IMAGE":
            for block in bpy.data.images:
                if block.users == 0:
                    bpy.data.images.remove(block)

        return {'FINISHED'}


class KeSelectFlippedNormal(Operator):
    bl_idname = "mesh.ke_select_flipped_normal"
    bl_label = "Select Flipped Normal Faces"
    bl_description = "Selects flipped normal faces (the 'red' faces in 'face orientation' overlay)"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[("CONNECTED", "Connected", "", 1),
               ("AVERAGE", "Average", "", 2)
               ],
        name="Method", default="CONNECTED",
        description="Choose which method used to find flipped faces.\n"
                    "Average works better for (mostly flat) disconnected mesh islands.\n"
                    "Connected works best in most other cases.")
    invert : bpy.props.BoolProperty(name="Invert Selection", default=False)

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "mode", expand=True)
        layout.separator(factor=0.5)
        layout.prop(self, "invert", toggle=True)
        layout.separator(factor=0.5)

    def execute(self, context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        if self.mode == "AVERAGE":
            avg_normal = average_vector([f.normal for f in bm.faces])
            if self.invert:
                for f in bm.faces:
                    if avg_normal.dot(f.normal) > 0:
                        f.select_set(True)
            else:
                for f in bm.faces:
                    if avg_normal.dot(f.normal) < 0:
                        f.select_set(True)
        else:
            cbm = bm.copy()
            bmesh.ops.recalc_face_normals(cbm, faces=cbm.faces)
            if self.invert:
                for f, of in zip(cbm.faces, bm.faces):
                    if f.normal == of.normal:
                        of.select_set(True)
            else:
                for f, of in zip(cbm.faces, bm.faces):
                    if f.normal != of.normal:
                        of.select_set(True)
            cbm.free()
        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}


class KeSelectCollinear(Operator):
    bl_idname = "mesh.ke_select_collinear"
    bl_label = "Select Collinear Verts"
    bl_description = "Selects Collinear Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        obj = context.active_object
        if not obj:
            obj = sel_obj[0]

        og_mode = [b for b in context.tool_settings.mesh_select_mode]
        context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action='DESELECT')

        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        bm.select_mode = {'VERT'}

        count = 0
        for v in bm.verts:
            if is_bmvert_collinear(v):
                v.select = True
                count += 1

        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)

        if count > 0:
            self.report({"INFO"}, "Total Collinear Verts Found: %s" % count)
        else:
            context.tool_settings.mesh_select_mode = og_mode
            self.report({"INFO"}, "No Collinear Verts Found")

        return {"FINISHED"}


#
# MODULE REGISTRATION
#
classes = (
    UICleanUpToolsModule,
    KeClean,
    KeVertCountSelect,
    KePurge,
    KeSelectFlippedNormal,
    KeSelectCollinear
)

modules = (
)


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_cleanup:
        for c in classes:
            bpy.utils.register_class(c)
        
        for m in modules:
            m.register()


def unregister():
    if "bl_rna" in UICleanUpToolsModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
        
        for m in modules:
            m.unregister()


if __name__ == "__main__":
    register()
