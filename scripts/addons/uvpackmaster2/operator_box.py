
from .utils import *
# from .pack_context import *
from .prefs import *
from .register import reset_target_box_params
# from .operator import UVP2_OT_PackOperatorGeneric

import bmesh
import bpy
import bgl
import blf

if is_blender28():
    import gpu
    from gpu_extras.batch import batch_for_shader



def bgl_set_color(font_id, color):

    if is_blender28():
        blf.color(font_id, *color)
    else:
        bgl.glColor4f(*color)

def editor_draw_msg(color, msg):
    font_id = 0
    blf.size(font_id, 15, 72)
    bgl_set_color(font_id, color)

    x_coord = 10
    y_coord = 35 if is_blender28() else 10

    blf.position(font_id, x_coord, y_coord, 0)
    blf.draw(font_id, msg)

    bgl_set_color(font_id, (0, 0, 0, 1))



def target_box_draw_callback_b28(self, context):

    try:

        self.shader.bind()
        self.shader.uniform_float("color", self.box_color)
        self.batch.draw(self.shader)

    except Exception as ex:
        if in_debug_mode(debug_lvl=2):
            print_backtrace(ex)


def target_box_draw_callback_b27(self, context):

    try:

        bgl.glColor4f(*self.box_color)
        bgl.glLineWidth(1.0)
        bgl.glBegin(bgl.GL_LINES)

        for coords in self.coords:
            bgl.glVertex2f(*coords)

        bgl.glEnd()
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    except Exception as ex:
        if in_debug_mode(debug_lvl=2):
            print_backtrace(ex)


def target_box_draw_callback_text(self, context):

    try:

        if not self.prefs.target_box_draw_enable:
            return

        editor_draw_msg(self.box_color, 'Click and hold RMB in the UV area to start drawing packing box. Press ESC to cancel')

    except Exception as ex:
        if in_debug_mode(debug_lvl=2):
            print_backtrace(ex)


class UVP2_OT_EnableTargetBox(bpy.types.Operator):

    bl_idname = 'uvpackmaster2.enable_target_box'
    bl_label = 'Enable Packing Box'
    bl_description = "Enable the packing box functionality"

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        return prefs.FEATURE_target_box and (not prefs.target_box_enable)

    def __init__(self):
        self.__draw_handler = None

    def finish(self, context):

        try:
            if self.__draw_handler_box is not None:
                bpy.types.SpaceImageEditor.draw_handler_remove(self.__draw_handler, 'WINDOW')

            if self.__draw_handler_text is not None:
                bpy.types.SpaceImageEditor.draw_handler_remove(self.__draw_handler_text, 'WINDOW')
        except:
            pass

        if context.area is not None:
            context.area.tag_redraw()

        reset_target_box_params(self.prefs)

    def modal(self, context, event):
        finish = False
        force_redraw = False

        try:
            if not self.prefs.target_box_enable or context.area is None:
                self.finish(context)
                return {'FINISHED'}

            if self.prefs.target_box_draw_enable:

                if not self.target_box_draw_after_click:

                    if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
                        view_coords = self.context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)

                        self.scene_props.target_box_p1_x = view_coords[0]
                        self.scene_props.target_box_p1_y = view_coords[1]

                        self.scene_props.target_box_p2_x = view_coords[0]
                        self.scene_props.target_box_p2_y = view_coords[1]

                        self.target_box_draw_after_click = True

                    elif event.type == 'ESC':
                        self.prefs.target_box_draw_enable = False
                        force_redraw = True

                else:

                    exit_draw_mode = event.type == 'RIGHTMOUSE' and event.value == 'RELEASE'

                    if event.type == 'MOUSEMOVE' or exit_draw_mode:
                        view_coords = self.context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)

                        self.scene_props.target_box_p2_x = view_coords[0]
                        self.scene_props.target_box_p2_y = view_coords[1]

                        if exit_draw_mode:
                            try:
                                validate_target_box(self.scene_props)
                            except:
                                reset_target_box(self.scene_props)
                                self.report({'ERROR'}, 'Drawn packig box was too small - it was reset to the default value')

                            self.target_box_draw_after_click = False
                            self.prefs.target_box_draw_enable = False

                        self.update_coords()
                        force_redraw = True
                        

                if force_redraw:
                    self.context.area.tag_redraw()

                return {'RUNNING_MODAL'}

            self.update_coords()

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, str(ex))
            finish = True

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'Unexpected error')
            finish = True

        if finish:
            self.finish(context)
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def update_coords(self):

        p1 = (self.scene_props.target_box_p1_x, self.scene_props.target_box_p1_y)
        p2 = (self.scene_props.target_box_p1_x, self.scene_props.target_box_p2_y)
        p3 = (self.scene_props.target_box_p2_x, self.scene_props.target_box_p2_y)
        p4 = (self.scene_props.target_box_p2_x, self.scene_props.target_box_p1_y)

        new_coords = [
            p1, p2,
            p2, p3,
            p3, p4,
            p4, p1
        ]

        if new_coords != self.coords:
            self.coords = new_coords

            if is_blender28():
                self.batch = batch_for_shader(self.shader, 'LINES', {"pos": self.coords})

            self.context.area.tag_redraw()

    def execute(self, context):

        self.context = context
        self.scene_props = context.scene.uvp2_props
        self.prefs = get_prefs()

        self.prefs.target_box_enable = True
        self.prefs.target_box_draw_enable = False
        self.target_box_draw_after_click = False

        self.box_color = (1, 1, 0, 1)

        if is_blender28():
            self.shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

        self.coords = None
        self.update_coords()

        handler_args = (self, context)
        target_box_draw_callback = target_box_draw_callback_b28 if is_blender28() else target_box_draw_callback_b27

        self.__draw_handler = bpy.types.SpaceImageEditor.draw_handler_add(target_box_draw_callback, handler_args, 'WINDOW', 'POST_VIEW')
        self.__draw_handler_text = bpy.types.SpaceImageEditor.draw_handler_add(target_box_draw_callback_text, handler_args, 'WINDOW', 'POST_PIXEL')

        wm = context.window_manager
        # self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    # def invoke(self, context, event):

    #     self.scene_props = context.scene.uvp2_props
    #     self.prefs = get_prefs()

    #     return self.execute(context)


class UVP2_OT_DisableTargetBox(bpy.types.Operator):

    bl_idname = 'uvpackmaster2.disable_target_box'
    bl_label = 'Disable Packing Box'
    bl_description = "Disable the packing box funcionality"

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        return prefs.target_box_enable

    def execute(self, context):

        self.prefs = get_prefs()
        self.prefs.target_box_enable = False

        context.area.tag_redraw()

        return {'FINISHED'}


class UVP2_OT_DrawTargetBox(bpy.types.Operator):

    bl_idname = 'uvpackmaster2.draw_target_box'
    bl_label = 'Draw Packing Box'
    bl_description = "Draw packing box manually using the mouse coursor"

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        return prefs.target_box_enable and not prefs.target_box_draw_enable

    def execute(self, context):

        self.prefs = get_prefs()
        self.prefs.target_box_draw_enable = True

        context.area.tag_redraw()

        return {'FINISHED'}

class UVP2_OT_SetTargetBoxTile(bpy.types.Operator):

    bl_idname = 'uvpackmaster2.set_target_box_tile'
    bl_label = 'Set Tile'
    bl_description = "Set packing box to a UDIM tile as defined by the 'Tile (X)' and 'Tile (Y)' parameters"

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        return prefs.target_box_enable

    def execute(self, context):

        self.scene_props = context.scene.uvp2_props

        self.scene_props.target_box_p1_x = self.scene_props.target_box_tile_x
        self.scene_props.target_box_p1_y = self.scene_props.target_box_tile_y

        self.scene_props.target_box_p2_x = self.scene_props.target_box_tile_x + 1
        self.scene_props.target_box_p2_y = self.scene_props.target_box_tile_y + 1

        return {'FINISHED'}