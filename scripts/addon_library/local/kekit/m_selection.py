import bpy
from bpy.types import Panel, Operator

from ._ui import pcoll
from ._utils import get_prefs, set_active_collection
from .ops.ke_align_object_to_active import KeAlignObjectToActive
from .ops.ke_align_origin_to_selected import KeAlignOriginToSelected
from .ops.ke_bbmatch import KeBBMatch
from .ops.ke_cursor_align_rot import KeCursorAlignRot
from .ops.ke_cursor_fit_and_align import KeCursorFitAlign
from .ops.ke_cursor_ortho_snap import KeCursorOrthoSnap
from .ops.ke_cursor_rotation import KeCursorRotation
from .ops.ke_emptyparent import KeEmptyParent
from .ops.ke_frame_all_or_selected import KeFrameView
from .ops.ke_lock import KeLock
from .ops.ke_mouse_side_of_active import KeMouseSideofActive, KeMouseSelectMirror
from .ops.ke_object_to_cursor import KeObjectToCursor
from .ops.ke_origin_to_cursor import KeOriginToCursor
from .ops.ke_origin_to_selected import KeOriginToSelected
from .ops.ke_ortho_snap import KeOrthoSnap
from .ops.ke_quick_origin_move import KeQuickOriginMove
from .ops.ke_select_boundary import KeSelectBoundary
from .ops.ke_select_by_displaytype import KeSelectByDisplayType
from .ops.ke_select_invert_linked import KeSelectInvertLinked
from .ops.ke_select_objects_by_vertselection import KeVertObjectSelect
from .ops.ke_selected_to_origin import KeSelectedToOrigin
from .ops.ke_straighten import KeStraighten
from .ops.ke_swap import KeSwap
from .ops.ke_view_align import KeViewAlign
from .ops.ke_view_align_toggle import KeViewAlignToggle
from .ops.ke_vp_flip import KeVPFlip
from .ops.ke_vp_step_rotate import KeStepRotate


class UISelectionModule(Panel):
    bl_idname = "UI_PT_M_SELECTION"
    bl_label = "Select & Align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        u = pcoll['kekit']['ke_uncheck'].icon_id
        c = pcoll['kekit']['ke_check'].icon_id
        layout = self.layout
        col = layout.column(align=True)

        # ALIGN (leaning)
        row = col.row(align=True)
        row.operator(KeCursorFitAlign.bl_idname, text="Cursor Fit & Align", icon="CURSOR")
        row.prop(k, "cursorfit", text="", toggle=True, icon_value=c if k.cursorfit else u)
        row.prop(k, "cursor_gizmo", text="", icon="EMPTY_DATA")
        row = col.row(align=True)
        row.operator(KeCursorAlignRot.bl_idname, icon="MOUSE_MOVE")
        row.prop(k, "cursorfit", text="", toggle=True, icon_value=c if k.cursorfit else u)
        row = col.row(align=True)
        row.operator(KeStepRotate.bl_idname, text="StepRotate 90").rot = 90
        row.operator(KeStepRotate.bl_idname, text="StepRotate -90").rot = -90
        col.separator(factor=0.5)

        row = col.row(align=True).split(factor=0.9, align=True)
        row.operator(KeViewAlignToggle.bl_idname).mode = 'SELECTION'
        row.operator(KeViewAlignToggle.bl_idname, icon="CURSOR", text="View Align Toggle Cursor").mode = 'CURSOR'
        col.operator(KeOrthoSnap.bl_idname)
        row = col.row(align=True)
        row.operator(KeFrameView.bl_idname, text="Frame All or Selected")
        row.prop(k, "frame_mo", text="", toggle=True, icon_value=c if k.frame_mo else u)
        col.separator(factor=0.5)

        row = col.row(align=True).split(factor=0.9, align=True)
        row.operator(KeAlignOriginToSelected.bl_idname)
        row.operator(KeOriginToCursor.bl_idname, icon="CURSOR")
        col.operator(KeOriginToSelected.bl_idname)
        col.separator(factor=0.5)

        row = col.row(align=False).split(factor=0.9, align=True)
        row.operator(KeQuickOriginMove.bl_idname, icon="TRANSFORM_ORIGINS").mode = "MOVE"
        row.operator(KeQuickOriginMove.bl_idname, icon="TRANSFORM_ORIGINS", text="QOM AutoAxis").mode = "AUTOAXIS"
        col.separator(factor=0.5)

        col.operator(KeObjectToCursor.bl_idname)
        col.operator(KeAlignObjectToActive.bl_idname)
        col.operator(KeSelectedToOrigin.bl_idname)
        col.operator(KeBBMatch.bl_idname)

        col.separator(factor=0.5)
        row = col.row(align=True)
        row.operator(KeStraighten.bl_idname, icon="CON_ROTLIMIT")
        row.operator(KeSwap.bl_idname, text="Swap Places", icon="CON_TRANSLIKE")
        col.operator(KeEmptyParent.bl_idname)

        # SELECT (leaning)
        col.label(text="Select")
        row = col.row(align=True)
        row.operator(KeLock.bl_idname, icon="RESTRICT_SELECT_ON", text="Lock").mode = "LOCK"
        row.operator(KeLock.bl_idname, icon="RESTRICT_SELECT_ON", text="L.Unsel").mode = "LOCK_UNSELECTED"
        row.operator(KeLock.bl_idname, icon="RESTRICT_SELECT_OFF", text="Unlock").mode = "UNLOCK"
        col.operator(KeSelectBoundary.bl_idname, text="Select Boundary (+Active)")
        col.operator(KeSelectInvertLinked.bl_idname)
        col.operator(KeMouseSideofActive.bl_idname, icon="MOUSE_MOVE")
        col.operator(KeMouseSelectMirror.bl_idname, icon="MOUSE_MOVE")
        col.operator(KeShowInOutliner.bl_idname)
        col.operator(KeSetActiveCollection.bl_idname)
        col.operator(KeVertObjectSelect.bl_idname)


class UIxSelectByDisplayType(Panel):
    bl_idname = "UI_PT_ke_select_by_display_type"
    bl_label = "Select by Display Type"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_SELECTION"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        op = KeSelectByDisplayType.bl_idname
        layout = self.layout
        layout = layout.column(align=True)
        layout.prop(k, "sel_type_coll", toggle=True)
        layout.label(text="Select Objects with Display Type:")
        layout.operator(op, text="Textured").dt = "TEXTURED"
        layout.operator(op, text="Solid").dt = "SOLID"
        layout.operator(op, text="Wire").dt = "WIRE"
        layout.operator(op, text="Bounds").dt = "BOUNDS"
        layout.separator(factor=0.5)
        layout.label(text="Specific Bounds Display Type:")
        layout.operator(op, text="Capsule").dt = "CAPSULE"
        layout.operator(op, text="Cone").dt = "CONE"
        layout.operator(op, text="Cylinder").dt = "CYLINDER"
        layout.operator(op, text="Sphere").dt = "SPHERE"
        layout.operator(op, text="Box").dt = "BOX"


#
# Utility Operators
#
class KeSetActiveCollection(Operator):
    bl_idname = "view3d.ke_set_active_collection"
    bl_label = "Set Active Collection"
    bl_description = "[keKit] Set selected object's parent collection as Active (also in Object Context Menu)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        set_active_collection(context, context.object)
        return {"FINISHED"}


class KeShowInOutliner(Operator):
    bl_idname = "view3d.ke_show_in_outliner"
    bl_label = "Show in Outliner"
    bl_description = "[keKit] Locate the selected object(s) in the outliner (& set parent Collection as Active)\n" \
                     "(in Object Context Menu)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        sel_objects = [o for o in context.selected_objects]

        override = None
        for area in context.screen.areas:
            if 'OUTLINER' in area.type:
                for region in area.regions:
                    if 'WINDOW' in region.type:
                        override = context.temp_override(area=area, region=region)
                        break
                break

        if not sel_objects or override is None:
            self.report({"INFO"}, "Nothing selected? / Outliner not found?")
            return {"CANCELLED"}

        for obj in sel_objects:
            context.view_layer.objects.active = obj
            with override:
                bpy.ops.outliner.show_active()

        return {"FINISHED"}


class KeCursorClearRot(Operator):
    bl_idname = "view3d.ke_cursor_clear_rot"
    bl_label = "Clear Cursor Rotation"
    bl_description = "Clear the cursor's rotation (only)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        c = context.scene.cursor
        if c.rotation_mode == "QUATERNION":
            c.rotation_quaternion = 1, 0, 0, 0
        elif c.rotation_mode == "AXIS_ANGLE":
            c.rotation_axis_angle = 0, 0, 1, 0
        else:
            c.rotation_euler = 0, 0, 0
        return {'FINISHED'}


classes = (
    KeAlignObjectToActive,
    KeAlignOriginToSelected,
    KeBBMatch,
    KeCursorAlignRot,
    KeCursorClearRot,
    KeCursorFitAlign,
    KeCursorOrthoSnap,
    KeCursorRotation,
    KeEmptyParent,
    KeFrameView,
    KeLock,
    KeMouseSelectMirror,
    KeMouseSideofActive,
    KeObjectToCursor,
    KeOriginToCursor,
    KeOriginToSelected,
    KeOrthoSnap,
    KeQuickOriginMove,
    KeSelectBoundary,
    KeSelectByDisplayType,
    KeSelectInvertLinked,
    KeSelectedToOrigin,
    KeSetActiveCollection,
    KeShowInOutliner,
    KeStepRotate,
    KeStraighten,
    KeSwap,
    KeVPFlip,
    KeVertObjectSelect,
    KeViewAlign,
    KeViewAlignToggle,
    UISelectionModule,
    UIxSelectByDisplayType,
)


def register():
    k = get_prefs()
    if k.m_selection:
        for c in classes:
            bpy.utils.register_class(c)

        bpy.types.Scene.kekit_cursor_obj = bpy.props.StringProperty()


def unregister():
    if "bl_rna" in UISelectionModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)

        try:
            del bpy.types.Scene.kekit_cursor_obj
        except Exception as e:
            print('unregister fail:\n', e)
            pass
