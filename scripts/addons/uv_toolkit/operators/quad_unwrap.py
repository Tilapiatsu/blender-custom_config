import bpy
import bmesh
from mathutils import Vector


class QuadUnwrap(bpy.types.Operator):
    """Unwrap selection from to contiguous uniform quad layout"""
    bl_idname = "uv.toolkit_quad_unwrap"
    bl_label = "Quad Unwrap  (UVToolkit)"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        if context.scene.tool_settings.use_uv_select_sync:
            self.report({'INFO'}, "Need to disable UV Sync")
            return {'FINISHED'}

        active_object = context.view_layer.objects.active  # Store active object
        current_mesh_select_mode = tuple(context.tool_settings.mesh_select_mode)

        for obj in context.selected_objects:
            context.view_layer.objects.active = obj

            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            uv_layer = bm.loops.layers.uv.verify()

            selected_verts = []
            selected_uv_loops = []

            for f in bm.faces:
                for l in f.loops:
                    luv = l[uv_layer]
                    if luv.select:
                        selected_uv_loops.append(luv)
                        selected_verts.append(l.vert)

            if selected_uv_loops == []:
                continue

            context.scene.tool_settings.use_uv_select_sync = True
            bpy.ops.uv.select_all(action='DESELECT')
            context.tool_settings.mesh_select_mode = False, False, True

            for v in selected_verts:
                v.select = True

            # convert selected vetices to single face
            context.tool_settings.mesh_select_mode = True, False, False
            context.tool_settings.mesh_select_mode = False, False, True

            f = bm.faces.active

            if f is None:
                continue

            selected_vertices = [v for v in f.verts if v.select]
            if len(selected_vertices) != 4:
                continue

            bpy.ops.uv.select_linked()

            # Keith (http://wahooney.net) Boshoff 'Quad Unwrap'

            # get uvs and average edge lengths
            luv1 = f.loops[0][uv_layer]
            luv2 = f.loops[1][uv_layer]
            luv3 = f.loops[2][uv_layer]
            luv4 = f.loops[3][uv_layer]

            l1 = ((f.verts[0].co - f.verts[1].co).length + (f.verts[2].co - f.verts[3].co).length) / 2
            l2 = ((f.verts[1].co - f.verts[2].co).length + (f.verts[3].co - f.verts[0].co).length) / 2

            # Try to fit into old coords
            u = ((luv1.uv - luv2.uv).length + (luv3.uv - luv4.uv).length) / 2
            v = ((luv2.uv - luv3.uv).length + (luv4.uv - luv1.uv).length) / 2

            c = (luv1.uv + luv2.uv + luv3.uv + luv4.uv) / 4

            if l1 < l2:
                u = v * (l1 / l2)
            else:
                v = u * (l2 / l1)

            # try to fit into old coords
            luv1.uv = c + Vector((-u, -v)) / 2
            luv2.uv = c + Vector((u, -v)) / 2
            luv3.uv = c + Vector((u, v)) / 2
            luv4.uv = c + Vector((-u, v)) / 2
            bmesh.update_edit_mesh(me)

            bpy.ops.uv.follow_active_quads(mode='LENGTH_AVERAGE')

        bpy.ops.mesh.select_all(action='SELECT')
        context.scene.tool_settings.use_uv_select_sync = False
        context.view_layer.objects.active = active_object  # Restore active object
        context.tool_settings.mesh_select_mode = current_mesh_select_mode
        return {'FINISHED'}
