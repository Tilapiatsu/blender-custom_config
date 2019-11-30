import bpy
import bmesh
import math


class AlignUVIsland(bpy.types.Operator):
    """Align Island to closest x or y axis by selected edge"""
    bl_idname = "uv.toolkit_align_island"
    bl_label = "Align UV Island (UVToolkit)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        if context.scene.tool_settings.use_uv_select_sync:
            self.report({'INFO'}, "Need to disable UV Sync")
            return {'CANCELLED'}
        cursor_loc_x = context.space_data.cursor_location[0]
        cursor_loc_y = context.space_data.cursor_location[1]
        active_object = context.view_layer.objects.active  # Store active object
        for obj in context.selected_editable_objects:
            context.view_layer.objects.active = obj

            uve = []
            uvee = []
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            uv_layer = bm.loops.layers.uv.verify()

            for f in bm.faces:
                for l in f.loops:
                    luv = l[uv_layer]
                    if luv.select:
                        uve.append(luv.uv)
                        uvee.append(luv)

            if len(uve) == 0 or len(uve) == 1:
                continue

            # Align Island: SpdB3d https://blenderartists.org/t/add-on-align-uv-island/697493
            ab = [uve[0].x - (uve[0].x + uve[1].x) / 2, uve[0].y - (uve[0].y + uve[1].y) / 2]
            ac = [uve[0].x - (uve[0].x + uve[1].x) / 2, 0]

            u_v = ab[0] * ac[0] + ab[1] * ac[1]

            _u_ = math.sqrt(ab[0]**2 + ab[1]**2)
            _v_ = math.sqrt(ac[0]**2 + ac[1]**2)

            _uv_ = _u_ * _v_

            i = 1
            while(_uv_ == 0 and i != len(uve)):
                ab = [uve[0].x - (uve[0].x + uve[i].x) / 2, uve[0].y - (uve[0].y + uve[i].y) / 2]
                ac = [uve[0].x - (uve[0].x + uve[i].x) / 2, 0]

                u_v = ab[0] * ac[0] + ab[1] * ac[1]

                _u_ = math.sqrt(ab[0]**2 + ab[1]**2)
                _v_ = math.sqrt(ac[0]**2 + ac[1]**2)

                _uv_ = _u_ * _v_

                i += 1

            if _uv_ == 0:
                angle = 0
            else:
                angle = math.degrees(math.acos(u_v / _uv_))

            ab = [uve[0].x - (uve[0].x + uve[1].x) / 2, uve[0].y - (uve[0].y + uve[1].y) / 2]
            ac = [0, uve[0].y - (uve[0].y + uve[1].y) / 2]

            u_v = ab[0] * ac[0] + ab[1] * ac[1]

            _u_ = math.sqrt(ab[0]**2 + ab[1]**2)
            _v_ = math.sqrt(ac[0]**2 + ac[1]**2)

            _uv_ = _u_ * _v_

            i = 1
            while(_uv_ == 0 and i != len(uve)):
                ab = [uve[0].x - (uve[0].x + uve[i].x) / 2, uve[0].y - (uve[0].y + uve[i].y) / 2]
                ac = [0, uve[0].y - (uve[0].y + uve[i].y) / 2]

                u_v = ab[0] * ac[0] + ab[1] * ac[1]

                _u_ = math.sqrt(ab[0]**2 + ab[1]**2)
                _v_ = math.sqrt(ac[0]**2 + ac[1]**2)

                _uv_ = _u_ * _v_

                i += 1

            if _uv_ == 0:
                angle2 = 0
            else:
                angle2 = math.degrees(math.acos(u_v / _uv_))

            if angle > angle2:
                angle = -angle2

            bpy.ops.uv.snap_cursor(target='SELECTED')

            pivot_ori = bpy.context.space_data.pivot_point

            bpy.context.space_data.pivot_point = 'CURSOR'

            bpy.ops.uv.select_linked()

            bpy.ops.transform.rotate(value=math.radians(angle))

            bpy.ops.uv.select_all(action='TOGGLE')

            uvee[0].select = True
            uvee[1].select = True

            ab = [uve[0].x - (uve[0].x + uve[1].x) / 2, uve[0].y - (uve[0].y + uve[1].y) / 2]
            ac = [uve[0].x - (uve[0].x + uve[1].x) / 2, 0]

            u_v = ab[0] * ac[0] + ab[1] * ac[1]

            _u_ = math.sqrt(ab[0]**2 + ab[1]**2)
            _v_ = math.sqrt(ac[0]**2 + ac[1]**2)

            _uv_ = _u_ * _v_

            i = 1
            while(_uv_ == 0 and i != len(uve)):
                ab = [uve[0].x - (uve[0].x + uve[i].x) / 2, uve[0].y - (uve[0].y + uve[i].y) / 2]
                ac = [uve[0].x - (uve[0].x + uve[i].x) / 2, 0]

                u_v = ab[0] * ac[0] + ab[1] * ac[1]

                _u_ = math.sqrt(ab[0]**2 + ab[1]**2)
                _v_ = math.sqrt(ac[0]**2 + ac[1]**2)

                _uv_ = _u_ * _v_

                i += 1

            if _uv_ == 0:
                aangle = 0
            else:
                aangle = math.degrees(math.acos(u_v / _uv_))

            ab = [uve[0].x - (uve[0].x + uve[1].x) / 2, uve[0].y - (uve[0].y + uve[1].y) / 2]
            ac = [0, uve[0].y - (uve[0].y + uve[1].y) / 2]

            u_v = ab[0] * ac[0] + ab[1] * ac[1]

            _u_ = math.sqrt(ab[0]**2 + ab[1]**2)
            _v_ = math.sqrt(ac[0]**2 + ac[1]**2)

            _uv_ = _u_ * _v_

            i = 1
            while(_uv_ == 0 and i != len(uve)):
                ab = [uve[0].x - (uve[0].x + uve[i].x) / 2, uve[0].y - (uve[0].y + uve[i].y) / 2]
                ac = [0, uve[0].y - (uve[0].y + uve[i].y) / 2]

                u_v = ab[0] * ac[0] + ab[1] * ac[1]

                _u_ = math.sqrt(ab[0]**2 + ab[1]**2)
                _v_ = math.sqrt(ac[0]**2 + ac[1]**2)

                _uv_ = _u_ * _v_

                i += 1

            if _uv_ == 0:
                aangle2 = 0
            else:
                aangle2 = math.degrees(math.acos(u_v / _uv_))

            if aangle == 0 or aangle2 == 0 or round(aangle) == 90 or round(aangle2) == 90:
                angle = 0
            elif aangle != 0 or aangle2 != 0:
                angle = angle * -2
            else:
                angle = 0

            bpy.ops.uv.select_linked()

            bpy.ops.transform.rotate(value=math.radians(angle))

            bpy.ops.uv.select_all(action='TOGGLE')

            bmesh.update_edit_mesh(me)

            bpy.context.space_data.pivot_point = pivot_ori

        context.view_layer.objects.active = active_object  # Restore active object
        context.space_data.cursor_location[0] = cursor_loc_x
        context.space_data.cursor_location[1] = cursor_loc_y
        return {'FINISHED'}
