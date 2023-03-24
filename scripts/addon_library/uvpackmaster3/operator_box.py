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


from .overlay import OverlayManager
from .utils import *
# from .prefs import *
from .grouping_scheme import GroupingSchemeAccess
from .box import UVPM3_Box
from .box_utils import BoxRenderInfo, BoxRenderer, BoxRenderAccess, CustomTargetBoxAccess, TextChunk, disable_box_rendering
from .operator import UVPM3_OT_Engine
from .prefs_scripted_utils import ScriptParams

from bpy.props import IntProperty, BoolProperty
import bpy


class RenderBoxMode:
    IDLE = 0
    DRAW = 1
    RESIZE = 2


class RenderBoxesOverlayManager(OverlayManager):

    FINISH_PROMPT_MSG = 'Press ESC to finish'
    CANCEL_PROMPT_MSG = 'Press ESC to cancel'
    SNAP_PROMPT_MSG = 'Hold CTRL to snap to tile of other box boundaries'

    IDLE_HEADER_MSG = '[BOX EDITING]'
    IDLE_SELECT_ACTIVE_PROMPT_MSG = 'Press LMB inside a box to make it active'
    IDLE_DRAW_PROMPT_MSG = 'Press D to start drawing the active box'

    DRAW_HEADER_MSG = '[BOX DRAWING]'
    DRAW_START_PROMPT_MSG = 'Press and hold RMB in the UV area to start drawing'

    RESIZE_HEADER_MSG = '[BOX RESIZING]'


    def __init__(self, op, context):
        self.op = op
        self.mode_to_msg_array = {
            RenderBoxMode.IDLE : self.idle_overlay_msg_array,
            RenderBoxMode.DRAW : self.draw_overlay_msg_array,
            RenderBoxMode.RESIZE : self.resize_overlapy_msg_array
        }

        super().__init__(context, render_boxes_overlay_manager_draw_callback)

    def idle_overlay_msg_array(self):
        msg_array = []
        msg_array.append(self.IDLE_HEADER_MSG)

        if len(self.op.box_info_array) > 1:
            msg_array.append(self.IDLE_SELECT_ACTIVE_PROMPT_MSG)

        msg_array.append(self.IDLE_DRAW_PROMPT_MSG)
        msg_array.append(self.FINISH_PROMPT_MSG)
        return msg_array

    def draw_overlay_msg_array(self):
        msg_array = []
        msg_array.append(self.DRAW_HEADER_MSG)
        msg_array.append(self.DRAW_START_PROMPT_MSG)
        msg_array.append(self.SNAP_PROMPT_MSG)
        msg_array.append(self.CANCEL_PROMPT_MSG)
        return msg_array

    def resize_overlapy_msg_array(self):
        msg_array = []
        msg_array.append(self.RESIZE_HEADER_MSG)
        msg_array.append(self.SNAP_PROMPT_MSG)
        msg_array.append(self.CANCEL_PROMPT_MSG)
        return msg_array

    def overlay_msg_array(self):
        return self.mode_to_msg_array[self.op.render_mode]()

def render_boxes_overlay_manager_draw_callback(self, context):

    try:
        self.callback_begin()
        msg_array = self.overlay_msg_array()

        for msg in reversed(msg_array):
            self.print_text_inline(msg)

    except Exception as ex:
        if in_debug_mode(debug_lvl=2):
            print_backtrace(ex)


class UVPM3_OT_RenderBoxesGeneric(bpy.types.Operator):

    SNAP_DISTANCE = 0.1
    RESIZE_THICKNESS = 0.1
    DEFAULT_CURSOR_ID = 'DEFAULT'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        return not prefs.box_rendering

    def is_alive(self):
        return True

    def appy_box_transformation(self, drawn_box):
        try:
            drawn_box.validate()
        except:
            self.report({'ERROR'}, 'The box was too small - operation undone')

        else:
            self.active_box_stored.copy_from(drawn_box)
        self.active_box_info.box = self.active_box_stored
        self.reset_render_variables()

    def apply_snapping(self, points, mask=(True, True, True, True)):
        snap_points_list = [tuple(round(p) for p in points)]
        if self.box_info_array is not None:
            for box_info in self.box_info_array:
                if box_info != self.active_box_info:
                    snap_points_list.append(box_info.box.coords_tuple())

        for snap_points in snap_points_list:
            for idx, snap_point in enumerate(snap_points):
                if not mask[idx]:
                    continue

                check_points = (snap_point, snap_points[(idx+2) % len(snap_points)])
                for check_point in check_points:
                    if abs(check_point - points[idx]) < self.SNAP_DISTANCE:
                        points[idx] = check_point
                        break
        return points

    def handle_draw(self, event):

        if self.active_box_info is None:
            return

        if self.render_mode not in (RenderBoxMode.IDLE, RenderBoxMode.DRAW):
            return

        if event.type == 'D' and event.value == 'PRESS':
            self.redraw_needed = True
            self.render_mode = RenderBoxMode.DRAW

        if self.render_mode != RenderBoxMode.DRAW:
            return

        exit_draw_mode = False

        if self.draw_begin is None:

            if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
                view_coords = self.context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)

                self.active_box_stored = self.active_box_info.box
                self.draw_begin = view_coords
                self.draw_end = view_coords

        else:

            exit_draw_mode = event.type == 'RIGHTMOUSE' and event.value == 'RELEASE'

            if event.type == 'MOUSEMOVE' or exit_draw_mode:
                view_coords = self.context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)

                self.draw_end = view_coords
                self.prefs.boxes_dirty = True

        if self.draw_begin is not None and self.draw_end is not None:
            draw_coords = list(self.draw_begin + self.draw_end)

            if self.snap_enable:
                draw_coords = self.apply_snapping(draw_coords)

            self.active_box_info.box = UVPM3_Box(*draw_coords)

        if exit_draw_mode:

            drawn_box = self.active_box_info.box
            self.appy_box_transformation(drawn_box)
            self.redraw_needed = True

    def impl_box_info_array(self):

        return self.box_info_array, self.active_box_info

    def reset_render_variables(self):

        self.render_mode = RenderBoxMode.IDLE
        self.resize_edges = None
        # self.cursor_id = self.DEFAULT_CURSOR_ID
        self.draw_begin = None
        self.draw_end = None
        self.snap_enable = False
        self.active_box_stored = None

    def handle_box_selection(self, event):

        if self.render_mode != RenderBoxMode.IDLE:
            return

        if self.box_info_array is None:
            return

        if not (event.type == 'LEFTMOUSE' and event.value == 'PRESS'):
            return

        view_coords = self.context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)

        box_to_select = None
        min_history_val = float('inf')

        for box_info in self.box_info_array:
            if box_info.box.point_inside(view_coords):

                history_val = self.sel_history.get(box_info.glob_idx)
                if history_val is None:
                    box_to_select = box_info
                    break

                if history_val < min_history_val:
                    box_to_select = box_info
                    min_history_val = history_val

        if box_to_select is None:
            return

        self.force_block_event = True
        self.sel_history[box_to_select.glob_idx] = self.next_sel_history_val
        self.next_sel_history_val += 1
        self.box_access.impl_select_box(box_to_select)

    def handle_resize(self, event):

        if self.render_mode not in (RenderBoxMode.IDLE, RenderBoxMode.RESIZE):
            return

        if self.active_box_info is None:
            return

        view_coords = self.context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)

        if self.render_mode == RenderBoxMode.RESIZE:
            drawn_box = self.active_box_info.box

            if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                self.appy_box_transformation(drawn_box)
                self.force_block_event = False
                self.prefs.boxes_dirty = True

            elif event.type == 'MOUSEMOVE':
                new_coords = [drawn_box.p1_x, drawn_box.p1_y, drawn_box.p2_x, drawn_box.p2_y]

                if self.resize_edges[0]:
                    new_coords[0] = view_coords[0]
                elif self.resize_edges[2]:
                    new_coords[2] = view_coords[0]

                if self.resize_edges[1]:
                    new_coords[3] = view_coords[1]
                elif self.resize_edges[3]:
                    new_coords[1] = view_coords[1]

                if self.snap_enable:
                    snap_mask = (
                        self.resize_edges[0],
                        self.resize_edges[3],
                        self.resize_edges[2],
                        self.resize_edges[1],
                    )
                    new_coords = self.apply_snapping(new_coords, snap_mask)

                self.active_box_info.box = UVPM3_Box(*new_coords)
                self.prefs.boxes_dirty = True
            return

        on_edges = self.active_box_info.box.point_on_edges(view_coords, self.RESIZE_THICKNESS)
        on_edges_count = sum(on_edges)
        on_left, on_top, on_right, on_bottom = on_edges

        if on_edges_count > 1:
            self.cursor_id = "CROSSHAIR"
        elif on_top or on_bottom:
            self.cursor_id = "MOVE_Y"
        elif on_left or on_right:
            self.cursor_id = "MOVE_X"

        if on_edges_count > 0 and event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.render_mode = RenderBoxMode.RESIZE
            self.resize_edges = on_edges
            self.force_block_event = True
            self.active_box_stored = self.active_box_info.box

    def update_text(self, box_info):

        if len(box_info.text_chunks) == 0:
            return

        if box_info is self.active_box_info:
            
            outline_color = box_info.outline_color if self.box_access.ACTIVE_OUTLINE_COLOR is None else self.box_access.ACTIVE_OUTLINE_COLOR
            new_text_chunks = []
            new_text_chunks.append(TextChunk('[ ', outline_color))
            new_text_chunks += box_info.text_chunks
            new_text_chunks.append(TextChunk(' ]', outline_color))

            box_info.text_chunks = new_text_chunks

    def udpate_colors(self, box_info):

        col_multiplier = self.box_access.NON_ACTIVE_COLOR_MULTIPLIER
        color = box_info.color
        outline_color = box_info.outline_color
        text_color = None

        if box_info is self.active_box_info:

            if self.box_access.ACTIVE_COLOR is not None:
                color = self.box_access.ACTIVE_COLOR
                
            if self.box_access.ACTIVE_OUTLINE_COLOR is not None:
                outline_color = self.box_access.ACTIVE_OUTLINE_COLOR

            if self.box_access.ACTIVE_TEXT_COLOR is not None:
                text_color = self.box_access.ACTIVE_TEXT_COLOR
                
            col_multiplier = self.box_access.ACTIVE_COLOR_MULTIPLIER

        box_info.color = tuple(col_multiplier * x for x in color)
        box_info.outline_color = tuple(col_multiplier * x for x in outline_color)

        for t_chunk in box_info.text_chunks:
            t_color = text_color if text_color is not None else t_chunk.color
            t_chunk.color = tuple(col_multiplier * x for x in t_color)

    def udpate_z_coord(self, box_info):

        if self.box_access.ACTIVE_Z_COORD is not None and box_info is self.active_box_info:
            box_info.z_coord = self.box_access.ACTIVE_Z_COORD

    def update_box_info_array(self):

        if self.render_mode != RenderBoxMode.IDLE:
            return

        self.box_info_array = None
        box_info_array, self.active_box_info = self.box_access.impl_box_info_array()

        for box_info in box_info_array:
            self.update_text(box_info)
            self.udpate_colors(box_info)
            self.udpate_z_coord(box_info)

        self.box_info_array = box_info_array

    def coords_update_needed(self, event):
        return self.prefs.boxes_dirty or self.box_renderer.coords_update_needed(event) or event.type == 'ESC'

    def cursor_set(self, context, cursor_id):
        context.window.cursor_set(cursor_id)

    def modal(self, context, event):

        try:
            self.force_block_event = False
            self.snap_enable = event.ctrl

            if not self.prefs.box_rendering or (context.area is None):
                raise OpFinishedException()

            elif event.type == 'ESC' and event.value == 'PRESS':
                if self.render_mode != RenderBoxMode.IDLE:
                    self.reset_render_variables()
                    self.redraw_needed = True
                else:
                    raise OpFinishedException()

            if event.type != 'TIMER':
                if self.render_mode == RenderBoxMode.IDLE:
                    self.cursor_id = self.DEFAULT_CURSOR_ID

                self.handle_resize(event)
                self.handle_draw(event)

                self.handle_box_selection(event)
                self.cursor_set(self.context, self.cursor_id)

            if self.coords_update_needed(event):
                self.update_box_info_array()
                self.box_renderer.update_coords()
                self.redraw_needed = True

            if self.redraw_needed:
                self.context.area.tag_redraw()
                self.redraw_needed = False

            exit_code = 'RUNNING_MODAL' if self.force_block_event or self.render_mode != RenderBoxMode.IDLE else 'PASS_THROUGH'
            return {exit_code}


        except OpFinishedException:
            pass

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, str(ex))

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'Unexpected error')

        self.finish(context)
        return {'FINISHED'}

    def finish(self, context):

        if self._timer is not None:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        self.ov_manager.finish()
        self.box_renderer.finish()

        self.cursor_set(context, self.DEFAULT_CURSOR_ID)

        if context.area is not None:
            context.area.tag_redraw()

        self.prefs.box_rendering = False
        self.post_render()

    def pre_render(self):
        pass

    def post_render(self):
        pass

    def execute(self, context):

        self.box_access = self.get_box_access()

        if not self.box_access.init_access(context):
            return {'CANCELLED'}

        self._timer = None
        self.sel_history = dict()
        self.next_sel_history_val = 0

        self.box_info_array = None
        self.active_box_info = None
        self.context = context
        self.prefs = get_prefs()
        self.prefs.box_rendering = True
        self.redraw_needed = False
        self.force_block_event = False

        self.reset_render_variables()

        self.ov_manager = RenderBoxesOverlayManager(self, context)
        self.box_renderer = BoxRenderer(context, self)

        wm = context.window_manager
        wm.modal_handler_add(self)

        self.pre_render()

        MODAL_INTERVAL_S = 0.2
        wm = context.window_manager
        self._timer = wm.event_timer_add(MODAL_INTERVAL_S, window=context.window)

        return {'RUNNING_MODAL'}


class UVPM3_OT_FinishBoxRendering(bpy.types.Operator):

    bl_idname = 'uvpackmaster3.finish_box_rendering'
    bl_label = 'Finish Box Editing'
    bl_description = ''

    def execute(self, context):

        disable_box_rendering(None, context)
        return {'FINISHED'}


class GroupingSchemeRenderAccess(BoxRenderAccess):

    def init_access(self, g_scheme):

        self.g_scheme = g_scheme
        return self.g_scheme is not None

    def impl_render_group(self, group):

        return True

    def impl_box_info_array(self):

        box_info_array = []
        active_box_info = None

        class IntWrapper:
            def __init__(self):
                self.val = 0
        text_line_dict = defaultdict(IntWrapper)

        for group_idx, group in enumerate(self.g_scheme.groups):

            if not self.impl_render_group(group):
                continue

            z_coord = 1.0 if group_idx == self.g_scheme.active_group_idx else 0.0

            for box_idx, box in enumerate(group.target_boxes):

                text_line_num = text_line_dict[box]

                box_info = BoxRenderInfo(len(box_info_array), box, rgb_to_rgba(group.color), "{} (Box {})".format(group.name, box_idx), text_line_num.val, z_coord)
                box_info.group_idx = group_idx
                box_info.box_idx = box_idx

                text_line_num.val += 1

                if group_idx == self.g_scheme.active_group_idx and box_idx == group.active_target_box_idx:
                    active_box_info = box_info

                box_info_array.append(box_info)

        return box_info_array, active_box_info

    def impl_select_box(self, box_info):

        group_idx = box_info.group_idx

        if group_idx < 0 or group_idx >= len(self.g_scheme.groups):
            return

        group = self.g_scheme.groups[group_idx]
        box_idx = box_info.box_idx

        if box_idx < 0 or box_idx >= len(group.target_boxes):
            return

        self.g_scheme.active_group_idx = group_idx
        group.active_target_box_idx = box_idx



class ActiveGroupingSchemeRenderAccess(GroupingSchemeRenderAccess, GroupingSchemeAccess):

    ACTIVE_Z_COORD = 10.0
    # NON_ACTIVE_COLOR_MULTIPLIER = 0.5
    # ACTIVE_COLOR_MULTIPLIER = 0.0

    def init_access(self, context):
        GroupingSchemeAccess.init_access(self, context)
        return GroupingSchemeRenderAccess.init_access(self, self.active_g_scheme)

    def impl_render_group(self, group):

        return not self.active_g_scheme.is_complementary_group(group)

        

class UVPM3_OT_RenderGroupingSchemeBoxes(UVPM3_OT_RenderBoxesGeneric):

    bl_idname = 'uvpackmaster3.render_grouping_scheme_boxes'
    bl_label = 'Edit Scheme Target Boxes'
    bl_description = ''

    def pre_render(self):
        
        self.prefs.group_scheme_boxes_editing = True

    def post_render(self):
        
        self.prefs.group_scheme_boxes_editing = False

    def get_box_access(self):

        return ActiveGroupingSchemeRenderAccess()


class UVPM3_OT_ModifyTargetBox(bpy.types.Operator):

    def execute(self, context):

        self.init_access(context)

        self.scene_props = context.scene.uvpm3_props
        active_box = self.impl_active_box()

        if active_box is None:
            return {'CANCELLED'}

        self.modify_impl(active_box)
        return {'FINISHED'}


class UVPM3_OT_SetTargetBoxToTile(UVPM3_OT_ModifyTargetBox):

    bl_label = 'Set Box To Tile'
    bl_description = "Set a target box to a UDIM tile as defined by the 'Tile (X)' and 'Tile (Y)' parameters"

    tile_x : IntProperty(
        name=Labels.TILE_X_NAME,
        description=Labels.TILE_X_DESC,
        default=0)

    tile_y : IntProperty(
        name=Labels.TILE_Y_NAME,
        description=Labels.TILE_Y_DESC,
        default=0)

    def modify_impl(self, active_box):

        active_box.p1_x = self.tile_x
        active_box.p1_y = self.tile_y
        active_box.p2_x = self.tile_x + 1
        active_box.p2_y = self.tile_y + 1

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):

        col = self.layout.column(align=True)
        col.prop(self, 'tile_x')
        col.prop(self, 'tile_y')


class MoveTargetBoxProperties:

    dir_x : IntProperty(
        name="Direction X",
        description='',
        default=0)

    dir_y : IntProperty(
        name="Direction Y",
        description='',
        default=0)



class UVPM3_OT_SetGroupingSchemeBoxToTile(UVPM3_OT_SetTargetBoxToTile, GroupingSchemeAccess):

    bl_idname = 'uvpackmaster3.set_grouping_scheme_box_to_tile'


class UVPM3_OT_SetCustomTargetBoxToTile(UVPM3_OT_SetTargetBoxToTile, CustomTargetBoxAccess):

    bl_idname = 'uvpackmaster3.set_main_target_box_to_tile'


class UVPM3_OT_MoveTargetBox(UVPM3_OT_ModifyTargetBox):

    bl_label = 'Move Target Box'
    bl_description = "Move a target box to an adjacent tile"

    def modify_impl(self, active_box):

        width = active_box.width
        height = active_box.height

        delta_x = self.dir_x * width
        delta_y = self.dir_y * height

        active_box.offset((delta_x, delta_y))


class UVPM3_OT_MoveGroupingSchemeBox(UVPM3_OT_MoveTargetBox, MoveTargetBoxProperties, GroupingSchemeAccess):

    bl_idname = 'uvpackmaster3.move_grouping_scheme_box'


class UVPM3_OT_MoveCustomTargetBox(UVPM3_OT_MoveTargetBox, MoveTargetBoxProperties, CustomTargetBoxAccess):

    bl_idname = 'uvpackmaster3.move_main_target_box'
    


class UVPM3_OT_RenderCustomTargetBox(UVPM3_OT_RenderBoxesGeneric):

    bl_idname = 'uvpackmaster3.render_main_target_box'
    bl_label = 'Edit Target Box'
    bl_description = ''

    def pre_render(self):
        
        self.prefs.custom_target_box_editing = True

    def post_render(self):
        
        self.prefs.custom_target_box_editing = False

    def get_box_access(self):

        return CustomTargetBoxAccess()


class UVPM3_OT_ModifyTargetBoxEngine(UVPM3_OT_Engine):

    SCENARIO_ID = 'hidden.modify_box_with_islands'

    # def skip_topology_parsing(self):
    #     return True

    def isolated_execution(self):
        return True

    def pre_main(self):
        self.init_access(self.context)

        self.active_box = self.impl_active_box()
        self.modified_box = self.active_box.copy()
        self.modify_impl(self.modified_box)

    def post_main(self):
        self.active_box.copy_from(self.modified_box)

    def get_scenario_id(self):
        if self.scene_props.move_islands:
            return self.SCENARIO_ID

        return None

    def setup_script_params(self):
        
        script_params = ScriptParams()
        script_params.add_param('fully_inside', self.scene_props.fully_inside)
        script_params.add_param('orig_box', self.active_box.coords_tuple())
        script_params.add_param('modified_box', self.modified_box.coords_tuple())

        return script_params

    def check_engine_retcode(self, retcode):
        if retcode in {UvpmRetCode.SUCCESS}:
            return

        if retcode == UvpmRetCode.INVALID_ISLANDS:
            error_suffix = 'invalid island topology'
        else:
            error_suffix = 'engine process returned an error'

        raise RuntimeError('Box could not be modified: {}'.format(error_suffix))
    

class UVPM3_OT_MoveTargetBoxEngine(UVPM3_OT_ModifyTargetBoxEngine):

    bl_label = 'Move Target Box'
    bl_description = "Move a target box to an adjacent tile"

    def modify_impl(self, active_box):

        width = active_box.width
        height = active_box.height

        delta_x = self.dir_x * width
        delta_y = self.dir_y * height

        active_box.offset((delta_x, delta_y))



class UVPM3_OT_SelectIslandsInBox(UVPM3_OT_Engine):

    bl_label = 'Select Islands In Box'
    bl_description = 'Select/deselect islands in the active box'
    SCENARIO_ID = 'hidden.select_islands_in_box'


    def isolated_execution(self):
        return True

    def require_selection(self):
        return not self.select

    def send_unselected_islands(self):
        return self.select

    def pre_main(self):
        self.init_access(self.context)
        self.active_box = self.impl_active_box()

    def setup_script_params(self):
        
        script_params = ScriptParams()
        script_params.add_param('fully_inside', self.scene_props.fully_inside)
        script_params.add_param('active_box', self.active_box.coords_tuple())
        script_params.add_param('select', self.select)

        return script_params

    def check_engine_retcode(self, retcode):
        if retcode in {UvpmRetCode.SUCCESS}:
            return

        if retcode == UvpmRetCode.INVALID_ISLANDS:
            error_suffix = 'invalid island topology'
        else:
            error_suffix = 'engine process returned an error'

        raise RuntimeError('Could not select islands: {}'.format(error_suffix))


class SelectIslandsInBoxProperties:

    select : BoolProperty(name='Select', default=False)


class UVPM3_OT_SelectIslandsInGroupingSchemeBox(UVPM3_OT_SelectIslandsInBox, SelectIslandsInBoxProperties, GroupingSchemeAccess):

    bl_idname = 'uvpackmaster3.select_islands_in_grouping_scheme_box'


class UVPM3_OT_SelectIslandsInCustomTargetBox(UVPM3_OT_SelectIslandsInBox, SelectIslandsInBoxProperties, CustomTargetBoxAccess):

    bl_idname = 'uvpackmaster3.select_islands_in_custom_target_box'
    
