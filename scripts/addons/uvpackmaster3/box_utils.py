# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
import blf
import bgl
import gpu
from gpu_extras.batch import batch_for_shader

from .box import UVPM3_Box
from .utils import get_prefs, in_debug_mode, print_backtrace
from .overlay import OverlayManager


def disable_box_rendering(self, context):

    prefs = get_prefs()
    prefs.box_rendering = False



class TextChunk:

    def __init__(self, text, color):

        self.text = text
        self.color = color


class BoxRenderInfo:

    def __init__(self, glob_idx, box, color, text, text_line_num=0, z_coord=0.0):

        self.glob_idx = glob_idx
        self.box = box
        self.color = color
        self.outline_color = color

        self.text_chunks = []
        if text is not None:
            self.text_chunks.append(TextChunk(text, color))

        self.text_line_num = text_line_num
        self.z_coord = z_coord


class BoxRenderer(OverlayManager):

    LINE_WIDTH = 4.0

    def __init__(self, context, box_access):
    
        self.last_pixel_viewsize = None
        self.__draw_handler = None
        self.prefs = get_prefs()
        self.context = context
        self.box_access =  box_access

        self.box_info_array = None
        self.active_box_info = None

        self.shader = gpu.shader.from_builtin('3D_FLAT_COLOR')
        self.batch = None
        self.line_batch = None
        self.update_coords()

        handler_args = (self, context)
        self.__draw_handler = bpy.types.SpaceImageEditor.draw_handler_add(render_boxes_draw_callback, handler_args, 'WINDOW', 'POST_VIEW')
        super().__init__(context, render_boxes_draw_text_callback)

    def finish(self):

        if self.__draw_handler is not None:
            bpy.types.SpaceImageEditor.draw_handler_remove(self.__draw_handler, 'WINDOW')

        super().finish()

    def get_pixel_viewsize(self):

        tmp_coords0 = self.context.region.view2d.region_to_view(0, 0)
        tmp_coords1 = self.context.region.view2d.region_to_view(1, 1)
        return abs(tmp_coords0[0] - tmp_coords1[0])

    def coords_update_needed(self, event):

        pixel_viewsize_changed = self.last_pixel_viewsize is None or (self.last_pixel_viewsize != self.get_pixel_viewsize())
        # print(ret_value)
        return pixel_viewsize_changed

        # return (event.type in {'WHEELDOWNMOUSE', 'WHEELUPMOUSE'}) or (event.type == 'MIDDLEMOUSE' and event.ctrl)
        # return event.type != 'MOUSEMOVE'

    def update_box_info_array(self):

        self.box_info_array = None
        box_info_array, self.active_box_info = self.box_access.impl_box_info_array()

        if box_info_array is None:
            return

        # MUSTDO: workaround for text drawing order. Can we avoid this?
        self.box_info_array = sorted(box_info_array, key=lambda box_info: box_info.z_coord)

    def update_coords(self):

        self.prefs.boxes_dirty = False
        self.update_box_info_array()

        if self.box_info_array is None:
            return
            
        self.batch = None
        self.line_batch = None

        batch_coords = []
        batch_colors = []

        def append_box_to_batch(box, z_coord, color):

            p1 = (box.p1_x, box.p1_y)
            p2 = (box.p2_x, box.p2_y)

            coords = [
                (p1[0], p1[1], z_coord),
                (p1[0], p2[1], z_coord),
                (p2[0], p2[1], z_coord),

                (p1[0], p1[1], z_coord),
                (p2[0], p1[1], z_coord),
                (p2[0], p2[1], z_coord)
            ]
            
            nonlocal batch_coords
            nonlocal batch_colors

            batch_coords += coords
            batch_colors += [color] * len(coords)

        def append_line_to_batch(p1, p2, fixed_coord, offset, z_coord, color):

            nonlocal append_box_to_batch

            p2 = [p2[0], p2[1]]
            p2[fixed_coord] += offset

            append_box_to_batch(UVPM3_Box(p1[0], p1[1], p2[0], p2[1]), z_coord, color)

        
        self.last_pixel_viewsize = self.get_pixel_viewsize()
        line_width = self.LINE_WIDTH * self.last_pixel_viewsize

        for box_info in self.box_info_array:

            min_coords = box_info.box.min_corner
            max_coords = box_info.box.max_corner
            # max_coords = tuple(max(min_coords[i], max_coords[i]-pixel_viewsize[i]) for i in range(2))

            z_coord = box_info.z_coord
            color = box_info.color

            p1 = (min_coords[0], min_coords[1])
            p2 = (min_coords[0], max_coords[1])
            p3 = (max_coords[0], max_coords[1])
            p4 = (max_coords[0], min_coords[1])

            append_line_to_batch(p1, p2, 0,  line_width, z_coord, color)
            append_line_to_batch(p2, p3, 1, -line_width, z_coord, color)
            append_line_to_batch(p3, p4, 0, -line_width, z_coord, color)
            append_line_to_batch(p4, p1, 1,  line_width, z_coord, color)
            
            
        self.batch = batch_for_shader(self.shader, 'TRIS', {"pos": batch_coords, "color": batch_colors})

        if self.active_box_info is not None:

            min_coords = self.active_box_info.box.min_corner
            max_coords = self.active_box_info.box.max_corner
            z_coord = self.active_box_info.z_coord

            p1 = (min_coords[0], min_coords[1], z_coord)
            p2 = (min_coords[0], max_coords[1], z_coord)
            p3 = (max_coords[0], max_coords[1], z_coord)
            p4 = (max_coords[0], min_coords[1], z_coord)

            line_coords = [
                p1, p2,
                p2, p3,
                p3, p4,
                p4, p1
            ]

            line_colors = [self.active_box_info.outline_color] * len(line_coords)
            self.line_batch = batch_for_shader(self.shader, 'LINES', {"pos": line_coords, "color": line_colors})

        self.context.area.tag_redraw()


def render_boxes_draw_callback(self, context):

    try:
        self.box_access.is_alive()

        self.shader.bind()
        # bgl.glLineWidth(self.LINE_WIDTH)
        bgl.glEnable(bgl.GL_DEPTH_TEST)

        if self.batch is not None:
            self.batch.draw(self.shader)

        bgl.glDisable(bgl.GL_DEPTH_TEST)

        if self.line_batch is not None:
            bgl.glLineWidth(1.0)
            self.line_batch.draw(self.shader)

    except Exception as ex:
        if in_debug_mode(debug_lvl=2):
            print_backtrace(ex)


def render_boxes_draw_text_callback(self, context):

    try:
        self.box_access.is_alive()
        self.callback_begin()

        # box_info_array, active_box_info = self.box_access.impl_box_info_array()

        if self.box_info_array is None:
            return

        # bgl.glEnable(bgl.GL_DEPTH_TEST)
        # blf.shadow(self.font_id, 0, 1, 1, 1, 1)
        # blf.enable(self.font_id, blf.SHADOW)

        for box_info in self.box_info_array:

            if len(box_info.text_chunks) == 0:
                continue

            # min_corner = box.min_corner
            text_view_coords = box_info.box.min_corner

            COORD_OFFSET = 0.05
            text_view_coords = (text_view_coords[0] + COORD_OFFSET, text_view_coords[1] + COORD_OFFSET)

            # if box_info is self.active_box_info:
            #     text = "[ {} ]".format(box_info.text)
            # else:
            #     text = box_info.text

            text_region_coords = self.context.region.view2d.view_to_region(text_view_coords[0], text_view_coords[1], clip=False)
            text_region_coords = [text_region_coords[0], text_region_coords[1] + self.LINE_DISTANCE * box_info.text_line_num]

            for t_chunk in box_info.text_chunks:
                self.print_text(text_region_coords, t_chunk.text, t_chunk.color, box_info.z_coord)
                text_region_coords[0] += blf.dimensions(self.font_id, t_chunk.text)[0]

        bgl.glDisable(bgl.GL_DEPTH_TEST)

    except Exception as ex:
        if in_debug_mode(debug_lvl=2):
            print_backtrace(ex)




class BoxRenderAccess:

    ACTIVE_COLOR = None
    ACTIVE_COLOR_MULTIPLIER = 1.0
    ACTIVE_Z_COORD = None
    ACTIVE_OUTLINE_COLOR = (1,0.25,0,1)
    ACTIVE_TEXT_COLOR = None # (1,1,1,1)

    NON_ACTIVE_COLOR_MULTIPLIER = 1.0

    def is_alive(self):
        return True


class BoxArrayAccess:

    def init_access(self, box_array, color, active_idx=-1):

        assert(len(box_array) > 0)
        self.box_array = box_array
        self.color = color
        self.active_idx = active_idx

        return True

    def impl_active_box(self):

        if self.active_idx < 0:
            return None
        
        return self.box_array[self.active_idx]


class BoxArrayRenderAccess(BoxArrayAccess, BoxRenderAccess):

    def impl_box_info_array(self):

        box_info_array = [BoxRenderInfo(glob_idx, box, self.color, None) for glob_idx, box in enumerate(self.box_array)]

        active_box_info = None if self.active_idx < 0 else box_info_array[self.active_idx]
        return box_info_array, active_box_info

    def impl_select_box(self, box_info):
        
        self.active_idx = box_info.glob_idx


class CustomTargetBoxAccess(BoxArrayRenderAccess):

    MAIN_TARGET_BOX_COLOR = (1, 1, 0, 1)

    def init_access(self, context, ui_drawing=False):

        return super().init_access([context.scene.uvpm3_props.custom_target_box], self.MAIN_TARGET_BOX_COLOR, active_idx=0)
