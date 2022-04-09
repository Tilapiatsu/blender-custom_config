

from .operator_box import *
from .utils import get_prefs

class BoxEditUI:

    def __init__(self, context, scene_props):

        self.prefs = get_prefs()
        self.init_access(context, ui_drawing=True)
        self.context = context
        self.scene_props = scene_props

    def impl_force_show_coords(self):

        return False

    def draw(self, layout):

        col = layout.column(align=True)
        edit_enable = self.impl_edit_enable()
        active_box = self.impl_active_box()
        draw_box_coords = active_box is not None and (edit_enable or self.impl_force_show_coords())

        if edit_enable or draw_box_coords:
            edit_box = col.box()
            edit_col = edit_box.column(align=True)
            # edit_col.enabled = edit_enable

        if draw_box_coords:
            edit_col.label(text='Box coordinates:')

            coord_c = edit_col.column(align=True)

            row = coord_c.row(align=True)
            row.prop(active_box, "p1_x")

            row = coord_c.row(align=True)
            row.prop(active_box, "p1_y")

            row = coord_c.row(align=True)
            row.prop(active_box, "p2_x")

            row = coord_c.row(align=True)
            row.prop(active_box, "p2_y")

            edit_col.separator()

        if edit_enable:
            edit_box = col.box()
            edit_col = edit_box.column(align=True)
            
            row = edit_col.row(align=True)
            row.operator(self.impl_set_to_tile_operator().bl_idname)

            edit_col.separator()
            edit_col.label(text='Islands inside the box:')

            select_op = self.impl_select_islands_in_box_operator()
            row = edit_col.row(align=True)
            row.operator(select_op.bl_idname, text="Select").select = True
            row.operator(select_op.bl_idname, text="Deselect").select = False

            box = edit_col.box()
            box.prop(self.scene_props, "fully_inside")

            edit_col.separator()
            edit_col.label(text='Move the box to an adjacent tile:')

            row = edit_col.row(align=True)

            move_op = self.impl_move_box_operator()

            col3 = row.column(align=True)
            op = col3.operator(move_op.bl_idname, text="↖")
            op.dir_x = -1
            op.dir_y = 1
            op = col3.operator(move_op.bl_idname, text="←")
            op.dir_x = -1
            op.dir_y = 0
            op = col3.operator(move_op.bl_idname, text="↙")
            op.dir_x = -1
            op.dir_y = -1

            col3 = row.column(align=True)
            op = col3.operator(move_op.bl_idname, text="↑")
            op.dir_x = 0
            op.dir_y = 1
            col3.label(text="")
            op = col3.operator(move_op.bl_idname, text="↓")
            op.dir_x = 0
            op.dir_y = -1

            col3 = row.column(align=True)
            op = col3.operator(move_op.bl_idname, text="↗")
            op.dir_x = 1
            op.dir_y = 1
            op = col3.operator(move_op.bl_idname, text="→")
            op.dir_x = 1
            op.dir_y = 0
            op = col3.operator(move_op.bl_idname, text="↘")
            op.dir_x = 1
            op.dir_y = -1

            # box = edit_col.box()
            # box.prop(self.scene_props, "move_islands")

            edit_col.separator()

        op_type = UVPM3_OT_FinishBoxRendering if edit_enable else self.impl_render_boxes_operator()
        col.operator(op_type.bl_idname)


class GroupingSchemeBoxesEditUI(BoxEditUI, GroupingSchemeAccess):

    def impl_edit_enable(self):

        return self.prefs.group_scheme_boxes_editing

    def impl_set_to_tile_operator(self):

        return UVPM3_OT_SetGroupingSchemeBoxToTile

    def impl_render_boxes_operator(self):

        return UVPM3_OT_RenderGroupingSchemeBoxes

    def impl_move_box_operator(self):

        return UVPM3_OT_MoveGroupingSchemeBox

    def impl_select_islands_in_box_operator(self):

        return UVPM3_OT_SelectIslandsInGroupingSchemeBox



class CustomTargetBoxEditUI(BoxEditUI, CustomTargetBoxAccess):

    def impl_force_show_coords(self):

        return True

    def impl_edit_enable(self):

        return self.prefs.custom_target_box_editing

    def impl_set_to_tile_operator(self):

        return UVPM3_OT_SetCustomTargetBoxToTile

    def impl_render_boxes_operator(self):

        return UVPM3_OT_RenderCustomTargetBox

    def impl_move_box_operator(self):

        return UVPM3_OT_MoveCustomTargetBox

    def impl_select_islands_in_box_operator(self):

        return UVPM3_OT_SelectIslandsInCustomTargetBox
