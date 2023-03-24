import bpy
import bmesh
from ._utils import override_by_active_view3d


class KeFrameView(bpy.types.Operator):
    bl_idname = "screen.ke_frame_view"
    bl_label = "Frame All or Selected"
    bl_description = "Frame Selection, or everything if nothing is selected."
    bl_options = {'REGISTER'}

    mpx = 0
    mpy = 0

    @classmethod
    def poll(cls, context):
        spaces = {"GRAPH_EDITOR", "DOPESHEET_EDITOR", "VIEW_3D", "NODE_EDITOR", "IMAGE_EDITOR"}
        return context.space_data.type in spaces

    def invoke(self, context, event):
        self.mpx = int(event.mouse_x)
        self.mpy = int(event.mouse_y)
        return self.execute(context)

    def execute(self, context):
        mesh_only = context.preferences.addons[__package__].preferences.frame_mo
        cat = {'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER', 'EMPTY', 'LATTICE', 'VOLUME'}
        space = context.space_data.type
        if space == "VIEW_3D":
            ctx = override_by_active_view3d(context, self.mpx, self.mpy)
            sel_mode = context.mode
            sel_obj = [o for o in context.selected_objects]
            active = context.active_object

            temp_hide = []
            if mesh_only and not sel_obj:
                for o in context.scene.objects:
                    if o.type in cat and not o.hide_viewport:
                        temp_hide.append(o)
                        o.hide_viewport = True

            # Not sure when 'paint' changed order, including both...
            if sel_mode in {'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'PARTICLE_EDIT',
                            'SCULPT_GPENCIL', 'PAINT_GPENCIL', 'WEIGHT_GPENCIL', 'VERTEX_GPENCIL',
                            'PAINT_VERTEX', 'PAINT_WEIGHT', 'PAINT_TEXTURE'}:
                # Framing object in these modes
                sel_mode = "OBJECT"

            if sel_mode == "OBJECT":
                if active and sel_obj:
                    bpy.ops.view3d.view_selected(ctx, 'INVOKE_DEFAULT')
                else:
                    bpy.ops.view3d.view_all(ctx, 'INVOKE_DEFAULT')

            elif sel_mode == "POSE":
                if context.selected_bones or context.selected_pose_bones_from_active_object:
                    bpy.ops.view3d.view_selected(ctx, 'INVOKE_DEFAULT')
                else:
                    bpy.ops.view3d.view_all(ctx, 'INVOKE_DEFAULT')

            elif sel_mode in {"EDIT_MESH", "EDIT_CURVE", "EDIT_SURFACE", "EDIT_LATTICE", "EDIT_GPENCIL",
                              "EDIT_ARMATURE", "POSE"}:

                if not sel_obj and active:
                    sel_obj = [active]

                if not sel_obj:
                    return {"CANCELLED"}

                sel_check = False

                for o in sel_obj:
                    o.update_from_editmode()
                    if o.type == "MESH":
                        for v in o.data.vertices:
                            if v.select:
                                sel_check = True
                                break

                    elif o.type == "CURVE":
                        for sp in o.data.splines:
                            for cp in sp.bezier_points:
                                if cp.select_control_point:
                                    sel_check = True
                                    break

                    elif o.type == "SURFACE":
                        for sp in o.data.splines:
                            for cp in sp.points:
                                if cp.select:
                                    sel_check = True
                                    break

                    elif o.type == "LATTICE":
                        for p in o.data.points:
                            if p.select:
                                sel_check = True
                                break

                    elif o.type == "GPENCIL":
                        stroke = o.data.layers.active.active_frame.strokes[0]
                        if any(p.select for p in stroke.points):
                            sel_check = True
                            break

                    elif o.type == "ARMATURE":
                        if sel_mode == "POSE":
                            sel = context.selected_pose_bones
                        else:
                            sel = context.selected_editable_bones
                        if sel:
                            sel_check = True

                if sel_check:
                    bpy.ops.view3d.view_selected(ctx, 'INVOKE_DEFAULT')

                else:
                    if mesh_only and not temp_hide:
                        for o in context.scene.objects:
                            if o.type in cat and not o.hide_viewport:
                                temp_hide.append(o)
                                o.hide_viewport = True

                    # bpy.ops.view3d.view_all(ctx, 'INVOKE_DEFAULT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.view3d.view_selected(ctx, 'INVOKE_DEFAULT')
                    bpy.ops.mesh.select_all(action='DESELECT')

            if mesh_only and temp_hide:
                for o in temp_hide:
                    o.hide_viewport = False

        elif space == "GRAPH_EDITOR":
            sel = []
            for c in context.selected_visible_fcurves:
                for kp in c.keyframe_points:
                    if kp.select_control_point:
                        sel.append(kp)
            if sel:
                bpy.ops.graph.view_selected('INVOKE_DEFAULT')
            else:
                bpy.ops.graph.view_all('INVOKE_DEFAULT')

        elif space == "DOPESHEET_EDITOR":
            obj = context.object
            action = obj.animation_data.action
            sel = []
            for fcurve in action.fcurves:
                for kp in fcurve.keyframe_points:
                    if kp.select_control_point:
                        sel.append(kp)
            if sel:
                bpy.ops.action.view_selected('INVOKE_DEFAULT')
            else:
                bpy.ops.action.view_all('INVOKE_DEFAULT')

        elif space == "NODE_EDITOR":
            sel = context.selected_nodes[:]
            if sel:
                bpy.ops.node.view_selected('INVOKE_DEFAULT')
            else:
                if bpy.ops.node.view_all.poll():
                    bpy.ops.node.view_all('INVOKE_DEFAULT')

        elif space == "IMAGE_EDITOR":
            # AKA UV Editor...
            sel = False
            if context.object.data.is_editmode:

                sel_sync = bool(context.scene.tool_settings.use_uv_select_sync)
                bm = bmesh.from_edit_mesh(context.active_object.data)
                uv_layer = bm.loops.layers.uv.verify()

                for face in bm.faces:
                    for loop in face.loops:
                        uv = loop[uv_layer]
                        if sel_sync:
                            if loop.vert.select:
                                sel = True
                                break
                        else:
                            if uv.select:
                                sel = True
                                break
                if sel:
                    bpy.ops.image.view_selected('INVOKE_DEFAULT')
                elif not sel and uv_layer:
                    bpy.ops.uv.select_all(action='SELECT')
                    bpy.ops.image.view_selected('INVOKE_DEFAULT')
                    bpy.ops.uv.select_all(action='DESELECT')
                else:
                    # only frames 0-1 as "all"
                    bpy.ops.image.view_all('INVOKE_DEFAULT')

        return {'FINISHED'}


#
# CLASS REGISTRATION
#
classes = (KeFrameView,)

modules = ()


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
