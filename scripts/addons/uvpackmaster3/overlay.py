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


from .enums import OperationStatus, UvpmLogType
from .utils import in_debug_mode, print_backtrace


class TextOverlay:

    def __init__(self, text, color):
        self.coords = None
        self.text = text
        self.color = color

    def set_coords(self, coords):
        self.coords = coords

    def draw(self, ov_manager):
        if self.coords is None:
            return

        blf.color(ov_manager.font_id, *self.color)
        region_coord = ov_manager.context.region.view2d.view_to_region(self.coords[0], self.coords[1])
        blf.position(ov_manager.font_id, region_coord[0], region_coord[1], 0)
        blf.draw(ov_manager.font_id, self.text)



class OverlayManager:

    LINE_X_COORD = 10
    LINE_Y_COORD = 35
    LINE_DISTANCE = 25
    LINE_TEXT_COLOR = (1, 1, 1, 1)

    TEXT_SIZE = 15
    TEXT_OVERLAY_SIZE = 20

    def __init__(self, context, callback):

        self.font_id = 0
        self.context = context

        handler_args = (self, context)
        self.__draw_handler = bpy.types.SpaceImageEditor.draw_handler_add(callback, handler_args, 'WINDOW', 'POST_PIXEL')

    def finish(self):

        if self.__draw_handler is not None:
            bpy.types.SpaceImageEditor.draw_handler_remove(self.__draw_handler, 'WINDOW')

    def print_text(self, coords, text, color, z_coord=0.0):

        blf.size(self.font_id, self.TEXT_SIZE, 72)
        blf.color(self.font_id, *color)

        blf.position(self.font_id, coords[0], coords[1], z_coord)
        blf.draw(self.font_id, text)

        blf.color(self.font_id, *(0, 0, 0, 1))

    def __print_text_inline(self, line_num, text, color):

        x_coord = self.LINE_X_COORD
        y_coord = self.LINE_Y_COORD + line_num * self.LINE_DISTANCE
        self.print_text((x_coord, y_coord), text, color)

    def print_text_inline(self, text, color=LINE_TEXT_COLOR):
        self.__print_text_inline(self.next_line_num, text, color)
        self.next_line_num += 1

    def callback_begin(self):

        self.next_line_num = 0



class EngineOverlayManager(OverlayManager):

    WARNING_COLOR = (1, 0.4, 0, 1)
    ERROR_COLOR = (1, 0, 0, 1)
    DISABLED_DEVICE_COLOR_MULTIPLIER = 0.7

    INTEND_STR = '  '

    OPSTATUS_TO_COLOR = {
        OperationStatus.ERROR : ERROR_COLOR,
        OperationStatus.WARNING : WARNING_COLOR,
        OperationStatus.CORRECT : OverlayManager.LINE_TEXT_COLOR
    }

    def __init__(self, op, dev_array):
        super().__init__(op.p_context.context, engine_overlay_manager_draw_callback)
        
        self.op = op
        self.dev_array = dev_array
        self.print_dev_progress = True
        self.p_context = op.p_context
        self.log_manager = op.log_manager

        self.font_id = 0


    def print_dev_array(self):
        if self.dev_array is None:
            return

        for dev in reversed(self.dev_array):
            dev_color = self.LINE_TEXT_COLOR

            if self.print_dev_progress:
                progress_str = "{}% ".format(dev.bench_entry.progress)
            else:
                progress_str = ''

            if dev.settings.enabled:
                dev_status = "{}(iterations: {})".format(progress_str, dev.bench_entry.iter_count)
            else:
                dev_status = 'disabled'
                dev_color = tuple(self.DISABLED_DEVICE_COLOR_MULTIPLIER * c for c in dev_color)

            self.print_text_inline("{}{}: {}".format(self.INTEND_STR, dev.name, dev_status), color=dev_color)

        self.print_text_inline("[PACKING DEVICES]:")

    def print_list(self, header, list, color):
        for elem in reversed(list):
            self.print_text_inline("{}* {}".format(self.INTEND_STR, elem), color=color)

        self.print_text_inline("[{}]:".format(header), color=color)


def engine_overlay_manager_draw_callback(self, context):

    try:
        self.callback_begin()

        status_str = self.log_manager.last_log(UvpmLogType.STATUS)
        if status_str is None:
            status_str = ''

        status_color = self.OPSTATUS_TO_COLOR[self.log_manager.operation_status()]
        hint_str = self.log_manager.last_log(UvpmLogType.HINT)

        if hint_str:
            status_str = "{} ({})".format(status_str, hint_str)

        self.print_text_inline('[STATUS]: ' + status_str, color=status_color)
        self.print_dev_array()

        log_print_metadata = (\
            (UvpmLogType.INFO,   'INFO'),
            (UvpmLogType.WARNING,'WARNINGS'),
            (UvpmLogType.ERROR,  'ERRORS')
        )

        for log_type, header in log_print_metadata:
            op_status = self.log_manager.LOGTYPE_TO_OPSTATUS[log_type]
            color = self.OPSTATUS_TO_COLOR[op_status]
            
            log_list = self.log_manager.log_list(log_type)
            if len(log_list) > 0:
                self.print_list(header, log_list, color)


        blf.size(self.font_id, self.TEXT_OVERLAY_SIZE, 72)

        if self.p_context.p_islands is not None:
            for p_island in self.p_context.p_islands:
                overlay = p_island.overlay()
                if overlay is not None:
                    overlay.draw(self)

    except Exception as ex:
        if in_debug_mode():
            print_backtrace(ex)
