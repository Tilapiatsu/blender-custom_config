from bpy.types import Menu
from .._ui import pcoll
from .._utils import get_prefs


class KePieBookmarks(Menu):
    bl_label = "View & Cursor Bookmarks "
    bl_idname = "VIEW3D_MT_ke_pie_vcbookmarks"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_bookmarks

    def draw(self, context):
        b1 = pcoll['kekit']['ke_bm1'].icon_id
        b2 = pcoll['kekit']['ke_bm2'].icon_id
        b3 = pcoll['kekit']['ke_bm3'].icon_id
        b4 = pcoll['kekit']['ke_bm4'].icon_id
        b5 = pcoll['kekit']['ke_bm5'].icon_id
        b6 = pcoll['kekit']['ke_bm6'].icon_id
        c1 = pcoll['kekit']['ke_cursor1'].icon_id
        c2 = pcoll['kekit']['ke_cursor2'].icon_id
        c3 = pcoll['kekit']['ke_cursor3'].icon_id
        c4 = pcoll['kekit']['ke_cursor4'].icon_id
        c5 = pcoll['kekit']['ke_cursor5'].icon_id
        c6 = pcoll['kekit']['ke_cursor6'].icon_id
        k = context.scene.kekit_temp
        opv = 'view3d.ke_view_bookmark'
        opb = 'view3d.ke_cursor_bookmark'
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # VIEW BOOKMARKS
        box = pie.box()
        box.ui_units_x = 6.5
        box.label(text="View Bookmarks")
        row = box.grid_flow(row_major=True, columns=2, align=False)

        row.operator(opv, text="", icon="IMPORT").mode = "SET1"
        if sum(k.viewslot1) == 0:
            row.operator(opv, icon_value=b1, text="Use Slot 1", depress=False).mode = "USE1"
        else:
            row.operator(opv, icon_value=b1, text="Use Slot 1", depress=True).mode = "USE1"

        row.operator(opv, text="", icon="IMPORT").mode = "SET2"
        if sum(k.viewslot2) == 0:
            row.operator(opv, icon_value=b2, text="Use Slot 2", depress=False).mode = "USE2"
        else:
            row.operator(opv, icon_value=b2, text="Use Slot 2", depress=True).mode = "USE2"

        row.operator(opv, text="", icon="IMPORT").mode = "SET3"
        if sum(k.viewslot3) == 0:
            row.operator(opv, icon_value=b3, text="Use Slot 3", depress=False).mode = "USE3"
        else:
            row.operator(opv, icon_value=b3, text="Use Slot 3", depress=True).mode = "USE3"

        row.operator(opv, text="", icon="IMPORT").mode = "SET4"
        if sum(k.viewslot4) == 0:
            row.operator(opv, icon_value=b4, text="Use Slot 4", depress=False).mode = "USE4"
        else:
            row.operator(opv, icon_value=b4, text="Use Slot 4", depress=True).mode = "USE4"

        row.operator(opv, text="", icon="IMPORT").mode = "SET5"
        if sum(k.viewslot5) == 0:
            row.operator(opv, icon_value=b5, text="Use Slot 5", depress=False).mode = "USE5"
        else:
            row.operator(opv, icon_value=b5, text="Use Slot 5", depress=True).mode = "USE5"

        row.operator(opv, text="", icon="IMPORT").mode = "SET6"
        if sum(k.viewslot6) == 0:
            row.operator(opv, icon_value=b6, text="Use Slot 6", depress=False).mode = "USE6"
        else:
            row.operator(opv, icon_value=b6, text="Use Slot 6", depress=True).mode = "USE6"

        # CURSOR BOOKMARKS
        box = pie.box()
        box.ui_units_x = 6.5
        box.label(text="Cursor Bookmarks")
        row = box.grid_flow(row_major=True, columns=2, align=False)

        if sum(k.cursorslot1) == 0:
            row.operator(opb, icon_value=c1, text="Use Slot 1", depress=False).mode = "USE1"
        else:
            row.operator(opb, icon_value=c1, text="Use Slot 1", depress=True).mode = "USE1"
        row.operator(opb, text="", icon="IMPORT").mode = "SET1"

        if sum(k.cursorslot2) == 0:
            row.operator(opb, icon_value=c2, text="Use Slot 2", depress=False).mode = "USE2"
        else:
            row.operator(opb, icon_value=c2, text="Use Slot 2", depress=True).mode = "USE2"
        row.operator(opb, text="", icon="IMPORT").mode = "SET2"

        if sum(k.cursorslot3) == 0:
            row.operator(opb, icon_value=c3, text="Use Slot 3", depress=False).mode = "USE3"
        else:
            row.operator(opb, icon_value=c3, text="Use Slot 3", depress=True).mode = "USE3"
        row.operator(opb, text="", icon="IMPORT").mode = "SET3"

        if sum(k.cursorslot4) == 0:
            row.operator(opb, icon_value=c4,  text="Use Slot 4", depress=False).mode = "USE4"
        else:
            row.operator(opb, icon_value=c4,  text="Use Slot 4", depress=True).mode = "USE4"
        row.operator(opb, text="", icon="IMPORT").mode = "SET4"

        if sum(k.cursorslot5) == 0:
            row.operator(opb, icon_value=c5,  text="Use Slot 5", depress=False).mode = "USE5"
        else:
            row.operator(opb, icon_value=c5,  text="Use Slot 5", depress=True).mode = "USE5"
        row.operator(opb, text="", icon="IMPORT").mode = "SET5"

        if sum(k.cursorslot6) == 0:
            row.operator(opb, icon_value=c6,  text="Use Slot 6", depress=False).mode = "USE6"
        else:
            row.operator(opb, icon_value=c6,  text="Use Slot 6", depress=True).mode = "USE6"
        row.operator(opb, text="", icon="IMPORT").mode = "SET6"
