import bpy
import bmesh


class RipFaces(bpy.types.Operator):
    bl_idname = "uv.toolkit_rip_faces"
    bl_label = "Rip Faces (UVToolkit)"
    bl_description = "Rip Faces"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        if context.scene.tool_settings.use_uv_select_sync:
            self.report({'INFO'}, "Need to disable UV Sync")
            return {'CANCELLED'}

        active_object = context.view_layer.objects.active  # Store active object
        for obj in context.selected_editable_objects:
            context.view_layer.objects.active = obj
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            uv_layer = bm.loops.layers.uv.verify()

            selected_uvloops = []

            # Radivarig: Rip Uv Faces https://github.com/Radivarig/UvSquares/blob/master/uv_squares.py
            for f in bm.faces:
                for l in f.loops:
                    luv = l[uv_layer]
                    if luv.select:
                        selected_uvloops.append(luv)

            if selected_uvloops == []:
                continue

            selFaces = []

            for f in bm.faces:
                isFaceSel = True
                for l in f.loops:
                    luv = l[uv_layer]
                    if luv.select is False:
                        isFaceSel = False
                        break

                if isFaceSel:
                    selFaces.append(f)

            if len(selFaces) == 0:
                target = None
                for f in bm.faces:
                    for l in f.loops:
                        luv = l[uv_layer]
                        if luv.select:
                            target = luv
                            break
                    if target is not None: break

                for f in bm.faces:
                    for l in f.loops:
                        luv = l[uv_layer]
                        luv.select = False

                target.select = True

            bpy.ops.uv.select_all(action='DESELECT')

            for sf in selFaces:
                for l in sf.loops:
                    luv = l[uv_layer]
                    luv.select = True

        context.view_layer.objects.active = active_object  # Restore active object
        return {'FINISHED'}


class RipFacesMove(bpy.types.Macro):
    bl_idname = "uv.toolkit_rip_faces_move"
    bl_label = "Rip Faces Move (UVToolkit)"
