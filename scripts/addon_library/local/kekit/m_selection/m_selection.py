import bpy
from bpy.types import Panel

from .ke_align_object_to_active import KeAlignObjectToActive
from .ke_align_origin_to_selected import KeAlignOriginToSelected
from .ke_bbmatch import KeBBMatch
from .ke_cursor_clear_rot import KeCursorClearRot
from .ke_cursor_fit_and_align import KeCursorFitAlign
from .ke_frame_all_or_selected import KeFrameView
from .ke_mouse_side_of_active import KeMouseSideofActive
from .ke_object_to_cursor import KeObjectToCursor
from .ke_origin_to_cursor import KeOriginToCursor
from .ke_origin_to_selected import KeOriginToSelected
from .ke_quick_origin_move import KeQuickOriginMove
from .ke_select_boundary import KeSelectBoundary
from .ke_select_by_displaytype import KeSelectByDisplayType
from .ke_select_invert_linked import KeSelectInvertLinked
from .ke_select_objects_by_vertselection import KeVertObjectSelect
from .ke_selected_to_origin import KeSelectedToOrigin
from .ke_set_active_collection import KeSetActiveCollection
from .ke_show_in_outliner import KeShowInOutliner
from .ke_straighten import KeStraighten
from .ke_swap import KeSwap
from .ke_view_align import KeViewAlign
from .ke_view_align_snap import KeViewAlignSnap
from .ke_view_align_toggle import KeViewAlignToggle
from .ke_vp_step_rotate import KeStepRotate
from .ke_lock import KeLock

from .._utils import get_prefs
from .._ui import pcoll


class UISelectionModule(Panel):
    bl_idname = "UI_PT_M_SELECTION"
    bl_label = "Select & Align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)

        # ALIGN (leaning)
        row = col.row(align=True)
        row.operator("view3d.cursor_fit_selected_and_orient", text="Cursor Fit & Align")
        split = row.row(align=True)
        split.alignment = "RIGHT"
        if k.cursorfit:
            split.prop(k, "cursorfit", text="", icon="CHECKMARK", toggle=True)
        else:
            split.prop(k, "cursorfit", text="", icon_value=pcoll['kekit']['ke_uncheck'].icon_id, toggle=True)

        row = col.row(align=True)
        row.operator("view3d.ke_vp_step_rotate", text="StepRotate 90").rot = 90
        row.operator("view3d.ke_vp_step_rotate", text="StepRotate -90").rot = -90

        col.label(text="Align View To")
        row = col.row(align=True)
        row.operator('view3d.ke_view_align_toggle', text="Cursor").mode = 'CURSOR'
        row.operator('view3d.ke_view_align_toggle', text="Selected").mode = 'SELECTION'
        row.operator('view3d.ke_view_align_snap', text="OrthoSnap").contextual = False

        row = col.row(align=True)
        row.operator("screen.ke_frame_view", text="Frame All or Selected")
        split = row.row(align=True)
        split.alignment = "RIGHT"
        if k.frame_mo:
            split.prop(k, "frame_mo", text="", icon="CHECKMARK", toggle=True)
        else:
            split.prop(k, "frame_mo", text="", icon_value=pcoll['kekit']['ke_uncheck'].icon_id, toggle=True)

        col.label(text="Align Origin(s) To")
        row = col.row(align=True)
        row.operator('view3d.ke_origin_to_cursor', text="Cursor")
        row.operator('view3d.align_origin_to_selected', text="Selection")
        row.operator('view3d.origin_to_selected', text="Sel.Loc")

        row = col.row(align=True)
        row.operator("view3d.ke_quick_origin_move", icon="TRANSFORM_ORIGINS").mode = "MOVE"
        split = row.row(align=True)
        split.alignment = "RIGHT"
        split.operator("view3d.ke_quick_origin_move", icon="TRANSFORM_ORIGINS", text="AutoAxis").mode = "AUTOAXIS"

        col.label(text="Align Object(s) To")
        row = col.row(align=True)
        row.operator('view3d.ke_object_to_cursor', text="Cursor")
        row.operator('view3d.ke_align_object_to_active', text="Active Object").align = "BOTH"
        row.operator('view3d.selected_to_origin', text="Origin")
        col.operator('object.ke_bbmatch')

        col.separator(factor=0.5)
        col.operator('object.ke_straighten', icon="CON_ROTLIMIT")
        col.operator('view3d.ke_swap', text="Swap Places", icon="CON_TRANSLIKE")

        # SELECT (leaning)
        col.label(text="Select")
        row = col.row(align=True)
        row.operator('view3d.ke_lock', icon="RESTRICT_SELECT_ON", text="Lock").mode = "LOCK"
        row.operator('view3d.ke_lock', icon="RESTRICT_SELECT_ON", text="L.Unsel").mode = "LOCK_UNSELECTED"
        row.operator('view3d.ke_lock', icon="RESTRICT_SELECT_OFF", text="Unlock").mode = "UNLOCK"
        col.operator("mesh.ke_select_boundary", text="Select Boundary (+Active)")
        col.operator('view3d.ke_select_invert_linked')
        col.operator('mesh.ke_mouse_side_of_active', icon="MOUSE_MOVE")
        col.operator('view3d.ke_show_in_outliner')
        col.operator('view3d.ke_set_active_collection')
        col.operator('object.ke_select_objects_by_vertselection')


class UISelectByDisplayType(Panel):
    bl_idname = "UI_PT_ke_select_by_display_type"
    bl_label = "Select by Display Type"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_SELECTION"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        layout = layout.column(align=True)
        layout.prop(k, "sel_type_coll", toggle=True)
        layout.label(text="Select Objects with Display Type:")
        layout.operator('object.ke_select_by_displaytype', text="Textured").dt = "TEXTURED"
        layout.operator('object.ke_select_by_displaytype', text="Solid").dt = "SOLID"
        layout.operator('object.ke_select_by_displaytype', text="Wire").dt = "WIRE"
        layout.operator('object.ke_select_by_displaytype', text="Bounds").dt = "BOUNDS"
        layout.separator(factor=0.5)
        layout.label(text="Specific Bounds Display Type:")
        layout.operator('object.ke_select_by_displaytype', text="Capsule").dt = "CAPSULE"
        layout.operator('object.ke_select_by_displaytype', text="Cone").dt = "CONE"
        layout.operator('object.ke_select_by_displaytype', text="Cylinder").dt = "CYLINDER"
        layout.operator('object.ke_select_by_displaytype', text="Sphere").dt = "SPHERE"
        layout.operator('object.ke_select_by_displaytype', text="Box").dt = "BOX"


def menu_show_in_outliner(self, context):
    self.layout.operator(KeShowInOutliner.bl_idname, text=KeShowInOutliner.bl_label)


def menu_set_active_collection(self, context):
    self.layout.operator(KeSetActiveCollection.bl_idname, text=KeSetActiveCollection.bl_label)


classes = (
    UISelectionModule,
    UISelectByDisplayType,
    KeCursorClearRot,
    KeOriginToCursor,
    KeAlignOriginToSelected,
    KeOriginToSelected,
    KeObjectToCursor,
    KeAlignObjectToActive,
    KeSelectedToOrigin,
    KeStraighten,
    KeSwap,
    KeSelectBoundary,
    KeShowInOutliner,
    KeSetActiveCollection,
    KeSelectInvertLinked,
    KeSelectByDisplayType,
    KeBBMatch,
    KeVertObjectSelect,
    KeStepRotate,
    KeCursorFitAlign,
    KeFrameView,
    KeMouseSideofActive,
    KeQuickOriginMove,
    KeViewAlign,
    KeViewAlignSnap,
    KeViewAlignToggle,
    KeLock,
)


def register():
    k = get_prefs()
    if k.m_selection:
        for c in classes:
            bpy.utils.register_class(c)

        bpy.types.VIEW3D_MT_object_context_menu.append(menu_set_active_collection)
        bpy.types.VIEW3D_MT_object_context_menu.append(menu_show_in_outliner)
        bpy.types.Scene.kekit_cursor_obj = bpy.props.StringProperty()


def unregister():
    if "bl_rna" in UISelectionModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)

        bpy.types.VIEW3D_MT_object_context_menu.remove(menu_set_active_collection)
        bpy.types.VIEW3D_MT_object_context_menu.remove(menu_show_in_outliner)
        try:
            del bpy.types.Scene.kekit_cursor_obj
        except Exception as e:
            print('unregister fail:\n', e)
            pass
