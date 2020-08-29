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


from .prefs import *
from .utils import *
from .uv_context import *
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty


class UVP2_OT_UvOperatorGeneric(bpy.types.Operator):

    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'


    def process_flags(self):
        
        return UvSelectionProcessFlags(selected=True, unselected=False)


    def require_selection(self):

        return True


    def execute(self, context):
        
        cancel = False

        self.prefs = get_prefs()
        self.scene_props = context.scene.uvp2_props
        self.uv_context = None

        reset_stats(self.prefs)
        
        try:
            start_time = time.time()
            process_flags = self.process_flags()

            if process_flags.enabled():     
                self.uv_context = UvContext(context, process_flags=process_flags)

                if self.require_selection() and self.uv_context.island_count() == 0:
                    self.report({'WARNING'}, 'No UV face selected')
                    return {'CANCELLED'}

            self.execute_specific()

            if in_debug_mode():
                print('UV operation time: ' + str(time.time() - start_time))

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, str(ex))
            cancel = True

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'Unexpected error')
            cancel = True

        if self.uv_context is not None:
            self.uv_context.update_meshes()

        return {'FINISHED'}


class UVP2_OT_SplitOverlappingIslands(UVP2_OT_UvOperatorGeneric):

    bl_idname = 'uvpackmaster2.split_overlapping_islands'
    bl_label = 'Split Overlapping Islands'
    bl_description = "Move all overlapping islands to the next tiles"

    def execute_specific(self):

        self.uv_context.detect_overlap_islands(0.0)
        islands_moved, undo_possible = self.uv_context.split_overlapping_islands()

        msg = "Done. Islands moved: {}".format(islands_moved)
        if not undo_possible:
            msg += ". Undo won't be possible (too many overlapping islands)"

        self.report({'INFO' if undo_possible else 'WARNING'}, msg)


class UVP2_OT_UndoIslandSplit(UVP2_OT_UvOperatorGeneric):

    bl_idname = 'uvpackmaster2.undo_island_split'
    bl_label = 'Undo Island Split'
    bl_description = "Undo island split operation"

    def execute_specific(self):

        islands_moved = self.uv_context.undo_island_split()
        self.report({'INFO'}, 'Done. Islands moved: {}'.format(islands_moved))


class UVP2_OT_AdjustScaleToUnselected(UVP2_OT_UvOperatorGeneric):

    bl_idname = 'uvpackmaster2.adjust_scale_to_unselected'
    bl_label = 'Adjust Scale To Unselected'
    bl_description = "Adjust scale of selected islands so it is uniform with scale of unselected islands"

    def process_flags(self):
        
        return UvSelectionProcessFlags(selected=True, unselected=True)


    def execute_specific(self):

        self.uv_context.adjust_scale_to_unselected()
        self.report({'INFO'}, 'Done')


class UVP2_OT_DebugIslands(UVP2_OT_UvOperatorGeneric):

    bl_idname = 'uvpackmaster2.debug_islands'
    bl_label = 'Debug Islands'
    bl_description = ""

    def process_flags(self):
        
        return UvSelectionProcessFlags(selected=True, unselected=False)


    def execute_specific(self):

        self.uv_context.debug_islands()
        self.report({'INFO'}, 'Done')


class UVP2_OT_TargetBoxUvOperator(UVP2_OT_UvOperatorGeneric):

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        return prefs.target_box_enable and super().poll(context)


    def require_selection(self):

        return False


class UVP2_OT_SelectIslandsInsideTargetBox(UVP2_OT_TargetBoxUvOperator):

    bl_idname = 'uvpackmaster2.select_islands_inside_target_gox'
    bl_label = 'Select Islands Inside Box'
    bl_description = ""

    select = BoolProperty(name="Select", default=True)

    def process_flags(self):
        
        return UvSelectionProcessFlags(selected=not self.select, unselected=self.select)


    def execute_specific(self):

        islands = self.uv_context.unsel_islands if self.select else self.uv_context.islands
        target_box = self.prefs.target_box(self.scene_props)

        islands_inside = self.uv_context.find_islands_inside_box(target_box, islands, fully_inside=self.scene_props.fully_inside)
        self.uv_context.select_islands(islands_inside, self.select)
        self.report({'INFO'}, 'Done')
        

class UVP2_OT_MoveTargetBoxTile(UVP2_OT_TargetBoxUvOperator):

    bl_idname = 'uvpackmaster2.move_target_box_tile'
    bl_label = 'Move Packing Box'
    bl_description = "Move the packing box to an adjacent tile"

    dir_x = IntProperty(
        name="Direction X",
        description='',
        default=0)

    dir_y = IntProperty(
        name="Direction Y",
        description='',
        default=0)

    
    def process_flags(self):
        
        return UvSelectionProcessFlags(selected=self.scene_props.move_islands, unselected=False)


    def execute_specific(self):

        tbox_width = abs(self.scene_props.target_box_p1_x - self.scene_props.target_box_p2_x)
        tbox_height = abs(self.scene_props.target_box_p1_y - self.scene_props.target_box_p2_y)

        delta_x = self.dir_x * tbox_width
        delta_y = self.dir_y * tbox_height

        if self.scene_props.move_islands:

            target_box = self.prefs.target_box(self.scene_props)

            islands_inside = self.uv_context.find_islands_inside_box(target_box, self.uv_context.islands, fully_inside=self.scene_props.fully_inside)

            for island in islands_inside:
                island.move((delta_x, delta_y))

        self.scene_props.target_box_p1_x += delta_x
        self.scene_props.target_box_p2_x += delta_x

        self.scene_props.target_box_p1_y += delta_y
        self.scene_props.target_box_p2_y += delta_y

        if self.scene_props.move_islands:
            msg = 'Moved (with {} islands)'.format(len(islands_inside))
        else:
            msg = 'Moved'

        self.report({'INFO'}, msg)
