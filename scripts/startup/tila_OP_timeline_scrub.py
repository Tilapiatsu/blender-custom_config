# SPDX-FileCopyrightText: 2021-2023 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

# Extracted from Grease Pencil Tools : 
# https://extensions.blender.org/add-ons/grease-pencil-tools/

'''Based on viewport_timeline_scrub standalone addon - Samuel Bernou'''

import numpy as np
import bpy
import gpu
import blf
from gpu_extras.batch import batch_for_shader

use_snap_ctrl = True
use_snap_shift = False
use_snap_alt = True
keycode = 'SPACE'

def nearest(array, value) -> int:
    '''
    Get a numpy array and a target value
    Return closest val found in array to passed value
    '''
    idx = (np.abs(array - value)).argmin()
    return int(array[idx])


def draw_callback_px(self, context):
    '''Draw callback use by modal to draw in viewport'''
    if context.area != self.current_area:
        return

    # text
    font_id = 0

    shader = gpu.shader.from_builtin('UNIFORM_COLOR') # initiate shader
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(1.0)

    # Draw HUD
    if self.use_hud_time_line:
        shader.bind()
        shader.uniform_float("color", self.color_timeline)
        self.batch_timeline.draw(shader)

    # Display keyframes
    if self.use_hud_keyframes and self.batch_keyframes:
        if self.keyframe_aspect == 'LINE':
            gpu.state.line_width_set(3.0)
            shader.bind()
            shader.uniform_float("color", self.color_timeline)
            self.batch_keyframes.draw(shader)
        else:
            gpu.state.line_width_set(1.0)
            shader.bind()
            shader.uniform_float("color", self.color_timeline)
            self.batch_keyframes.draw(shader)

    # Show current frame line
    gpu.state.line_width_set(1.0)
    if self.use_hud_playhead:
        playhead = [(self.cursor_x, self.my + self.playhead_size/2),
                    (self.cursor_x, self.my - self.playhead_size/2)]
        batch = batch_for_shader(shader, 'LINES', {"pos": playhead})
        shader.bind()
        shader.uniform_float("color", self.color_playhead)
        batch.draw(shader)

    # restore opengl defaults
    gpu.state.blend_set('NONE')

    # Display current frame text
    blf.color(font_id, *self.color_text)
    if self.use_hud_frame_current:
        blf.position(font_id, self.mouse[0]+10, self.mouse[1]+10, 0)
        blf.size(font_id, 30 * (self.dpi / 72.0))
        blf.draw(font_id, f'{self.new_frame:.0f}')

    # Display frame offset text
    if self.use_hud_frame_offset:
        blf.position(font_id, self.mouse[0]+10,
                     self.mouse[1]+(40*self.ui_scale), 0)
        blf.size(font_id, 16 * (self.dpi / 72.0))
        sign = '+' if self.offset > 0 else ''
        blf.draw(font_id, f'{sign}{self.offset:.0f}')


class GPTS_OT_time_scrub(bpy.types.Operator):
    bl_idname = "animation.tila_time_scrub"
    bl_label = "Time scrub"
    bl_description = "Quick time scrubbing with a shortcut"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type in ('VIEW_3D', 'SEQUENCE_EDITOR', 'CLIP_EDITOR')

    def invoke(self, context, event):

        self.current_area = context.area
        self.key = keycode
        self.evaluate_gp_obj_key = True
        self.always_snap = False
        self.rolling_mode = False

        self.dpi = context.preferences.system.dpi
        self.ui_scale = context.preferences.system.ui_scale
        # hud prefs
        self.color_timeline = [0.414041, 0.414041, 0.414041, 0.600000]
        self.color_playhead = [0.000774, 0.367247, 1.000000, 0.800000]
        self.color_text = [0.000774, 0.367247, 1.000000, 0.800000]
        self.use_hud_time_line = True
        self.use_hud_keyframes = True
        self.keyframe_aspect = 'LINE'
        self.use_hud_playhead = True
        self.use_hud_frame_current = True
        self.use_hud_frame_offset = True

        self.playhead_size = 100
        self.lines_size = 10

        self.px_step = 10
        self.snap_on = False
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.init_mouse_x = self.cursor_x = event.mouse_region_x

        # self.init_mouse_y = event.mouse_region_y # only to display init frame text
        self.cancel_frame = self.init_frame = self.new_frame = context.scene.frame_current
        self.lock_range = context.scene.lock_frame_selection_to_range
        if context.scene.use_preview_range:
            self.f_start = context.scene.frame_preview_start
            self.f_end = context.scene.frame_preview_end
        else:
            self.f_start = context.scene.frame_start
            self.f_end = context.scene.frame_end

        self.offset = 0
        self.pos = []

        # Snap control
        self.snap_ctrl = use_snap_ctrl
        self.snap_shift = use_snap_shift
        self.snap_alt = use_snap_alt
        self.snap_mouse_key = 'LEFTMOUSE' if self.key == 'RIGHTMOUSE' else 'RIGHTMOUSE'

        ob = context.object

        if context.space_data.type != 'VIEW_3D':
            ob = None  # do not consider any key

        if ob:  # condition to allow empty scrubing
            if ob.type != 'GPENCIL' or self.evaluate_gp_obj_key:
                # Get object keyframe position
                anim_data = ob.animation_data
                action = None

                if anim_data:
                    action = anim_data.action
                if action:
                    for fcu in action.fcurves:
                        for kf in fcu.keyframe_points:
                            if kf.co.x not in self.pos:
                                self.pos.append(kf.co.x)

            if ob.type == 'GPENCIL':
                # Get GP frame position
                gpl = ob.data.layers
                layer = gpl.active
                if layer:
                    for frame in layer.frames:
                        if frame.frame_number not in self.pos:
                            self.pos.append(frame.frame_number)

        if not ob or not self.pos:
            # Disable inverted behavior if no frame to snap
            self.always_snap = False
            if self.rolling_mode:
                self.report({'WARNING'}, 'No Keys to flip on')
                return {'CANCELLED'}

        if self.rolling_mode:
            # sorted and casted to int list since it's going to work with indexes
            self.pos = sorted([int(f) for f in self.pos])
            # find and make current frame the "starting" frame (force snap)
            active_pos = [i for i, num in enumerate(self.pos) if num <= self.init_frame]
            if active_pos:
                self.init_index = active_pos[-1]
                self.init_frame = self.new_frame = self.pos[self.init_index]
            else:
                self.init_index = 0
                self.init_frame = self.new_frame = self.pos[0]

            # del active_pos
            self.index_limit = len(self.pos) - 1

        # Also snap on play bounds (sliced off for keyframe display)
        self.pos += [self.f_start, self.f_end]

        # Disable Onion skin
        self.active_space_data = context.space_data
        self.onion_skin = None
        self.multi_frame = None
        if context.space_data.type == 'VIEW_3D':  # and 'GPENCIL' in context.mode
            self.onion_skin = self.active_space_data.overlay.use_gpencil_onion_skin
            self.active_space_data.overlay.use_gpencil_onion_skin = False

        if ob and ob.type == 'GPENCIL':
            if ob.data.use_multiedit:
                self.multi_frame = ob.data.use_multiedit
                ob.data.use_multiedit = False

        self.hud = True
        if not self.hud:
            ## Same as end settings when HUD is On
            if self.lock_range:
                self.pos = [i for i in self.pos if self.f_start <= i <= self.f_end]
            self.pos = np.asarray(self.pos)
            if self.rolling_mode:
                context.scene.frame_current = self.new_frame
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

        # - HUD params
        width = context.area.width
        right = int((width - self.init_mouse_x) / self.px_step)
        left = int(self.init_mouse_x / self.px_step)

        hud_pos_x = []
        for i in range(1, left):
            hud_pos_x.append(self.init_mouse_x - i*self.px_step)
        for i in range(1, right):
            hud_pos_x.append(self.init_mouse_x + i*self.px_step)

        # - list of double coords

        init_height = 60
        frame_height = self.lines_size
        key_height = 14
        bound_h = key_height + 19
        bound_bracket_l = self.px_step/2

        self.my = my = event.mouse_region_y

        self.hud_lines = []

        if not self.rolling_mode:
            # frame marks
            for x in hud_pos_x:
                self.hud_lines.append((x, my - (frame_height/2)))
                self.hud_lines.append((x, my + (frame_height/2)))

        # init frame mark
        self.hud_lines += [(self.init_mouse_x, my - (init_height/2)),
                           (self.init_mouse_x, my + (init_height/2))]

        if not self.rolling_mode:
            # Add start/end boundary bracket to HUD
            start_x = self.init_mouse_x + \
                (self.f_start - self.init_frame) * self.px_step
            end_x = self.init_mouse_x + \
                (self.f_end - self.init_frame) * self.px_step

            # start
            up = (start_x, my - (bound_h/2))
            dn = (start_x, my + (bound_h/2))
            self.hud_lines.append(up)
            self.hud_lines.append(dn)

            self.hud_lines.append(up)
            self.hud_lines.append((up[0] + bound_bracket_l, up[1]))
            self.hud_lines.append(dn)
            self.hud_lines.append((dn[0] + bound_bracket_l, dn[1]))

            # end
            up = (end_x, my - (bound_h/2))
            dn = (end_x, my + (bound_h/2))
            self.hud_lines.append(up)
            self.hud_lines.append(dn)

            self.hud_lines.append(up)
            self.hud_lines.append((up[0] - bound_bracket_l, up[1]))
            self.hud_lines.append(dn)
            self.hud_lines.append((dn[0] - bound_bracket_l, dn[1]))

        # Horizontal line
        self.hud_lines += [(0, my), (width, my)]

        # Prepare batchs to draw static parts
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')  # initiate shader
        self.batch_timeline = batch_for_shader(
            shader, 'LINES', {"pos": self.hud_lines})

        if self.rolling_mode:
            current_id = self.pos.index(self.new_frame)
            # Add init_frame to "cancel" it in later UI code
            ui_key_pos = [i - current_id + self.init_frame for i, _f in enumerate(self.pos[:-2])]
        else:
            ui_key_pos = self.pos[:-2]

        self.batch_keyframes = None # init if there are no keyframe to draw
        if ui_key_pos:
            if self.keyframe_aspect == 'LINE':
                key_lines = []
                # Slice off position of start/end frame added last (in list for snapping)
                for i in ui_key_pos:
                    key_lines.append(
                        (self.init_mouse_x + ((i-self.init_frame) * self.px_step), my - (key_height/2)))
                    key_lines.append(
                        (self.init_mouse_x + ((i-self.init_frame) * self.px_step), my + (key_height/2)))

                self.batch_keyframes = batch_for_shader(
                    shader, 'LINES', {"pos": key_lines})

            else:
                # diamond and square
                # keysize5 for square, 4 or 6 for diamond
                keysize = 6 if self.keyframe_aspect == 'DIAMOND' else 5
                upper = 0

                shaped_key = []
                indices = []
                idx_offset = 0
                for i in ui_key_pos:
                    center = self.init_mouse_x + ((i-self.init_frame)*self.px_step)
                    if self.keyframe_aspect == 'DIAMOND':
                        # +1 on x is to correct pixel alignment
                        shaped_key += [(center-keysize, my+upper),
                                    (center+1, my+keysize+upper),
                                    (center+keysize, my+upper),
                                    (center+1, my-keysize+upper)]

                    elif self.keyframe_aspect == 'SQUARE':
                        shaped_key += [(center-keysize+1, my-keysize+upper),
                                    (center-keysize+1, my+keysize+upper),
                                    (center+keysize, my+keysize+upper),
                                    (center+keysize, my-keysize+upper)]

                    indices += [(0+idx_offset, 1+idx_offset, 2+idx_offset),
                                (0+idx_offset, 2+idx_offset, 3+idx_offset)]
                    idx_offset += 4

                self.batch_keyframes = batch_for_shader(
                    shader, 'TRIS', {"pos": shaped_key}, indices=indices)

        # Trim snapping list of frame outside of frame range if range lock activated
        # (after drawing batch so those are still showed)
        if self.lock_range:
            self.pos = [i for i in self.pos if self.f_start <= i <= self.f_end]

        # convert frame list to array for numpy snap utility
        self.pos = np.asarray(self.pos)

        if self.rolling_mode:
            context.scene.frame_current = self.new_frame

        args = (self, context)
        self.viewtype = None
        self.spacetype = 'WINDOW'  # is PREVIEW for VSE, needed for handler remove

        if context.space_data.type == 'VIEW_3D':
            self.viewtype = bpy.types.SpaceView3D
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        elif context.space_data.type == 'SEQUENCE_EDITOR':
            self.viewtype = bpy.types.SpaceSequenceEditor
            self.spacetype = 'PREVIEW'
            self._handle = bpy.types.SpaceSequenceEditor.draw_handler_add(
                draw_callback_px, args, 'PREVIEW', 'POST_PIXEL')

        elif context.space_data.type == 'CLIP_EDITOR':
            self.viewtype = bpy.types.SpaceClipEditor
            self._handle = bpy.types.SpaceClipEditor.draw_handler_add(
                draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _exit_modal(self, context):
        if self.onion_skin is not None:
            self.active_space_data.overlay.use_gpencil_onion_skin = self.onion_skin
        if self.multi_frame:
            context.object.data.use_multiedit = self.multi_frame
        if self.hud and self.viewtype:
            self.viewtype.draw_handler_remove(self._handle, self.spacetype)
            context.area.tag_redraw()

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            # - calculate frame offset from pixel offset
            # - get mouse.x and add it to initial frame num
            self.mouse = (event.mouse_region_x, event.mouse_region_y)

            px_offset = (event.mouse_region_x - self.init_mouse_x)
            self.offset = int(px_offset / self.px_step)
            self.new_frame = self.init_frame + self.offset

            if self.rolling_mode:
                # Frame Flipping mode (equidistant scrub snap)
                self.index = self.init_index + self.offset
                # clamp to possible index range
                self.index = min(max(self.index, 0), self.index_limit)
                self.new_frame = self.pos[self.index]
                context.scene.frame_current = self.new_frame
                self.cursor_x = self.init_mouse_x + (self.offset * self.px_step)

            else:
                mod_snap = False
                if self.snap_ctrl and event.ctrl:
                    mod_snap = True
                if self.snap_shift and event.shift:
                    mod_snap = True
                if self.snap_alt and event.alt:
                    mod_snap = True

                ## Snapping
                if self.always_snap:
                    # inverted snapping behavior
                    if not self.snap_on and not mod_snap:
                        self.new_frame = nearest(self.pos, self.new_frame)
                else:
                    if self.snap_on or mod_snap:
                        self.new_frame = nearest(self.pos, self.new_frame)

                # frame range restriction
                if self.lock_range:
                    if self.new_frame < self.f_start:
                        self.new_frame = self.f_start
                    elif self.new_frame > self.f_end:
                        self.new_frame = self.f_end

                # context.scene.frame_set(self.new_frame)
                context.scene.frame_current = self.new_frame

                # - recalculate offset to snap cursor to frame
                self.offset = self.new_frame - self.init_frame

                # - calculate cursor pixel position from frame offset
                self.cursor_x = self.init_mouse_x + (self.offset * self.px_step)

        if event.type == 'ESC':
            # frame_set(self.init_frame) ?
            context.scene.frame_current = self.cancel_frame
            self._exit_modal(context)
            return {'CANCELLED'}

        # Snap if pressing NOT used mouse key (right or mid)
        if event.type == self.snap_mouse_key:
            if event.value == "PRESS":
                self.snap_on = True
            else:
                self.snap_on = False

        if event.type == self.key and event.value == 'RELEASE':
            self._exit_modal(context)
            return {'FINISHED'}

        return {"RUNNING_MODAL"}

# --- REGISTER ---

classes = (
    GPTS_OT_time_scrub,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
