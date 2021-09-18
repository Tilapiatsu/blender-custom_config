bl_info = {
    "name": "keClean",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 3, 4),
    "blender": (2, 80, 0),
}
import bpy
import bmesh
from mathutils import Vector


class VIEW3D_OT_ke_clean(bpy.types.Operator):
    bl_idname = "view3d.ke_clean"
    bl_label = "Macro Mesh Cleaner"
    bl_description = "All the important cleaning operations in one click. Customize options. " \
                     "Note: Edit or Object mode (also multiple objects)."
    bl_options = {'REGISTER', 'UNDO'}

    doubles = True
    doubles_val = 0.0001
    loose = True
    interior = True
    degenerate = True
    degenerate_val = 0.0001
    collinear = True

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def is_bmvert_collinear(self, v):
        le = v.link_edges
        if len(le) == 2:
            vec1 = Vector(v.co - le[0].other_vert(v).co)
            vec2 = Vector(v.co - le[1].other_vert(v).co)
            if abs(vec1.angle(vec2)) >= 3.1415:
                return True
        return False

    def select_collinear(self, obj):
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        bm.select_mode = {'VERT'}

        for v in bm.verts:
            if self.is_bmvert_collinear(v):
                v.select = True

        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)


    def execute(self, context):
        # VARIABLES  ---Todo: Custom values are not behaving. Meh.
        self.doubles = bpy.context.scene.kekit.clean_doubles
        # self.doubles_val = bpy.context.scene.kekit.clean_doubles_val
        self.loose = bpy.context.scene.kekit.clean_loose
        self.interior = bpy.context.scene.kekit.clean_interior
        self.degenerate = bpy.context.scene.kekit.clean_degenerate
        # self.degenerate_val = bpy.context.scene.kekit.clean_degenerate_val
        self.collinear = bpy.context.scene.kekit.clean_collinear

        # PRESELECTION
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        active_obj = context.active_object
        if not active_obj:
            active_obj = sel_obj[0]

        og_mode = str(context.mode)
        if og_mode == "EDIT_MESH":
            og_mode = "EDIT"

        vert_count = 0

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode="EDIT")

        for o in sel_obj:
            # SELECT
            o.select_set(state=True)
            precount = int(len(o.data.vertices))
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')

            # REMOVE DOUBLES
            if self.doubles:
                bpy.ops.mesh.remove_doubles(threshold=self.degenerate_val)

            # REMOVE LOOSE NON-MANIFOLD
            if self.loose:
                bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)

            # REMOVE INTERIOR FACES
            if self.interior:
                bpy.ops.mesh.select_non_manifold(extend=True, use_wire=True, use_multi_face=True, use_non_contiguous=True,
                                             use_verts=True, use_boundary=False)
                bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.mesh.delete(type='FACE')

            # REMOVE DEGENERATE
            if self.degenerate:
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.dissolve_degenerate(threshold=self.degenerate_val)
                bpy.ops.mesh.select_all(action='DESELECT')

            # REMOVE COLLINEAR
            if self.collinear:
                self.select_collinear(o)
                bpy.ops.mesh.dissolve_verts(use_face_split=False, use_boundary_tear=False)

            # TALLY
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")
            postcount = int(len(o.data.vertices))
            vert_count += precount - postcount
            print("Removed %s verts from %s" %((precount - postcount), o.name ))

            bpy.ops.object.mode_set(mode="OBJECT")
            o.select_set(state=False)

        for o in sel_obj:
            o.select_set(state=True)

        bpy.ops.object.mode_set(mode=og_mode)
        if vert_count > 0:
            self.report({"INFO"}, "Total verts removed: %s" %vert_count )
        else:
            self.report({"INFO"}, "All Good!")

        return {"FINISHED"}


class VIEW3D_OT_ke_vert_count_select(bpy.types.Operator):
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
            nr = int(self.sel_count)

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
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)
        else:
            bpy.context.tool_settings.mesh_select_mode = (True, False, False)

        return {'FINISHED'}


class VIEW3D_OT_ke_purge(bpy.types.Operator):
    bl_idname = "view3d.ke_purge"
    bl_label = "Purge Unused Data"
    bl_description = "Purge specific unused data blocks\nNote: Deleted meshes will still 'use' materials: Purge meshes first"
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


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (VIEW3D_OT_ke_clean,
           VIEW3D_OT_ke_vert_count_select,
           VIEW3D_OT_ke_purge,
           )


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
