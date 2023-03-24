import bpy
import blf
from ._utils import getset_transform
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import region_2d_to_location_3d


class KeQuickOriginMove(bpy.types.Operator):
    bl_idname = "view3d.ke_quick_origin_move"
    bl_label = "Quick Origin Move"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        items=[("MOVE", "Move", "", 1),
               ("AUTOAXIS", "AutoAxisMove", "", 2)
               ],
        name="Mode",
        default="MOVE")

    init_vec = False
    mouse_pos = Vector((0, 0))
    startpos = Vector((0, 0, 0))
    tm = Matrix().to_3x3()
    ot = "LOCAL"
    axis = False, False, False
    og_loc = 0,0,0
    og_cursor = 0,0,0
    editmode = "OBJECT"
    _handle_px = None
    scol = (1,1,1,1)

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "MOVE":
            return "Move Object Origin (using Grab in modal, LMB/RMB to finish/cancel)"
        else:
            return "Move Object Origin with automatix axis lock based on mouse pos vs origin\n" \
                   "(using Grab in modal, LMB/RMB to finish/cancel)"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw_callback_px(self, context, pos):
        hpos, vpos = 64, 64
        if pos:
            hpos = pos - 10
        font_id = 0
        blf.enable(font_id, 4)
        blf.position(font_id, hpos, vpos - 25, 0)
        blf.color(font_id, self.scol[0], self.scol[1], self.scol[2], self.scol[3])
        blf.size(font_id, 13, 72)
        blf.shadow(font_id, 5, 0, 0, 0, 1)
        blf.shadow_offset(font_id, 1, -1)
        blf.draw(font_id, "[ Quick Origin Move ]")

    def invoke(self, context, event):
        self.og_loc = context.object.location[:]
        self.editmode = context.mode[:]
        self.scol = context.preferences.addons['kekit'].preferences.modal_color_subtext

        og_ot = getset_transform(setglobal=False)
        if og_ot[0] in {"GLOBAL", "LOCAL", "VIEW", "CURSOR", "GIMBAL"}:
            self.ot = og_ot[0]

        if self.editmode != "OBJECT":
            bpy.ops.object.mode_set(mode='OBJECT')

        # mouse track start
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)
        region = context.region
        rv3d = context.space_data.region_3d
        screen_x = int(region.width * .5)
        newpos = region_2d_to_location_3d(region, rv3d, self.mouse_pos, context.object.location)

        if self.mode == "AUTOAXIS":
            v = self.tm.inverted() @ Vector(context.object.location - newpos).normalized()
            start_v = Vector((0.5,0.5,0.5))
            if abs(v.dot(start_v)) > 0.3:
                x, y, z = abs(v[0]), abs(v[1]), abs(v[2])
                if x > y and x > z:
                    self.axis = True, False, False
                elif y > x and y > z:
                    self.axis = False, True, False
                else:
                    self.axis = False, False, True
            else:
                self.axis = False, False, True

        else:
            cursor = context.scene.cursor
            self.og_cursor = cursor.location[:]
            cursor.location = newpos
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            cursor.location = self.og_cursor

        context.window_manager.modal_handler_add(self)
        args = (context, screen_x)
        self._handle_px = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        context.scene.tool_settings.use_transform_data_origin = True

        bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type=self.ot, orient_matrix_type=self.ot,
                                    constraint_axis=self.axis, mirror=True, use_proportional_edit=False,
                                    proportional_edit_falloff='SMOOTH', proportional_size=1,
                                    use_proportional_connected=False, use_proportional_projected=False)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        # APPLY ------------------------------------------------------------------------------------------
        if event.type in {'RET', 'SPACE'} or event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            context.scene.tool_settings.use_transform_data_origin = False

            if self.editmode != "OBJECT" and self.mode == "MOVE":
                bpy.ops.object.mode_set(mode='EDIT')

            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            return {'FINISHED'}

        # CANCEL ------------------------------------------------------------------------------------------
        elif event.type == 'ESC' or event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            context.scene.tool_settings.use_transform_data_origin = False

            if self.mode == "MOVE":
                cursor = context.scene.cursor
                cursor.location = self.og_loc
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                cursor.location = self.og_cursor

                if self.editmode != "OBJECT":
                    bpy.ops.object.mode_set(mode='EDIT')

            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


#
# CLASS REGISTRATION
#
classes = (KeQuickOriginMove,)

modules = ()


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
