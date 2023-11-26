import bpy
from addon_utils import check
from bpy.types import Panel, Menu
from .ops.pie_operators import KePieOps, KeCallPie, KeObjectOp, KeOverlays
from ._utils import get_prefs, is_registered
from ._ui import pcoll


class UIPieMenusModule(Panel):
    bl_idname = "UI_PT_M_PIEMENUS_KEKIT"
    bl_label = "Pie Menus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        m_modeling = k.m_modeling
        m_selection = k.m_selection
        m_bookmarks = k.m_bookmarks
        m_render = k.m_render

        layout = self.layout
        pie = layout.column()
        pie.operator("ke.call_pie", text="keShading", icon="DOT").name = "KE_MT_shading_pie"

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="keSnapping", icon="DOT").name = "VIEW3D_MT_ke_pie_snapping"
        else:
            row.enabled = False
            row.label(text="keSnapping N/A")

        row = pie.row(align=True)
        if m_selection:
            row.operator("wm.call_menu_pie", text="keStepRotate", icon="DOT").name = "VIEW3D_MT_ke_pie_step_rotate"
        else:
            row.enabled = False
            row.label(text="keStepRotate N/A")

        row = pie.row(align=True)
        if m_modeling:
            row.operator("wm.call_menu_pie", text="keFit2Grid", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid"
            row.operator("wm.call_menu_pie", text="F2G Micro", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid_micro"
        else:
            row.enabled = False
            row.label(text="keFit2Grid N/A")

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="keOrientPivot", icon="DOT").name = "VIEW3D_MT_ke_pie_orientpivot"
        else:
            row.enabled = False
            row.label(text="keOrientPivot N/A")

        pie.operator("wm.call_menu_pie", text="keOverlays", icon="DOT").name = "VIEW3D_MT_ke_pie_overlays"

        row = pie.row(align=True)
        if m_modeling and m_selection:
            row.operator("wm.call_menu_pie", text="keSnapAlign", icon="DOT").name = "VIEW3D_MT_ke_pie_align"
        else:
            row.enabled = False
            row.label(text="keSnapAlign N/A")

        row = pie.row(align=True)
        if m_modeling:
            row.operator("wm.call_menu_pie", text="keFitPrim", icon="DOT").name = "VIEW3D_MT_ke_pie_fitprim"
            row.operator("wm.call_menu_pie", text="+Add", icon="DOT").name = "VIEW3D_MT_ke_pie_fitprim_add"
        else:
            row.enabled = False
            row.label(text="keFitPrim N/A")

        pie.operator("wm.call_menu_pie", text="keSubd", icon="DOT").name = "VIEW3D_MT_ke_pie_subd"

        row = pie.row(align=True)
        if m_render:
            row.operator("wm.call_menu_pie", text="keMaterials", icon="DOT").name = "VIEW3D_MT_PIE_ke_materials"
        else:
            row.enabled = False
            row.label(text="keMaterials N/A")

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="View&CursorBookmarks",
                         icon="DOT").name = "VIEW3D_MT_ke_pie_vcbookmarks"
        else:
            row.enabled = False
            row.label(text="View&CursorBookmarks N/A")

        row = pie.row(align=True)
        if m_modeling:
            row.operator("wm.call_menu_pie", text="keMultiCut", icon="DOT").name = "VIEW3D_MT_ke_pie_multicut"
        else:
            row.enabled = False
            row.label(text="keMultiCut N/A")

        row = pie.row(align=True)
        row.operator("wm.call_menu_pie", text="keMisc", icon="DOT").name = "VIEW3D_MT_ke_pie_misc"

        row = pie.row(align=True)
        row.operator("wm.call_menu_pie", text="Bool Tool", icon="DOT").name = "VIEW3D_MT_ke_pie_booltool"


class UIPieMenusBlender(Panel):
    bl_idname = "UI_PT_M_PIEMENUS_BLENDER"
    bl_label = "Blender Default Pie Menus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_PIEMENUS_KEKIT"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie().column()
        pie.operator("wm.call_menu_pie", text="Falloffs Pie",
                     icon="DOT").name = "VIEW3D_MT_proportional_editing_falloff_pie"
        pie.operator("wm.call_menu_pie", text="View Pie", icon="DOT").name = "VIEW3D_MT_view_pie"
        pie.operator("wm.call_menu_pie", text="Pivot Pie", icon="DOT").name = "VIEW3D_MT_pivot_pie"
        pie.operator("wm.call_menu_pie", text="Orientation Pie", icon="DOT").name = "VIEW3D_MT_orientations_pie"
        pie.operator("wm.call_menu_pie", text="Shading Pie", icon="DOT").name = "VIEW3D_MT_shading_pie"
        pie.operator("wm.call_menu_pie", text="Snap Pie", icon="DOT").name = "VIEW3D_MT_snap_pie"
        pie.operator("wm.call_menu_pie", text="UV: Snap Pie", icon="DOT").name = "IMAGE_MT_uvs_snap_pie"
        pie.separator()
        pie.operator("wm.call_menu_pie", text="Clip: Tracking", icon="DOT").name = "CLIP_MT_tracking_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Solving", icon="DOT").name = "CLIP_MT_solving_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Marker", icon="DOT").name = "CLIP_MT_marker_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Reconstruction", icon="DOT").name = "CLIP_MT_reconstruction_pie"


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


def is_canvas(_obj):
    try:
        if _obj["BoolToolRoot"]:
            return True
    except KeyError:
        return False


def is_brush(_obj):
    try:
        if _obj["BoolToolBrush"]:
            return True
    except KeyError:
        return False


def is_fast_transform():
    preferences = bpy.context.preferences
    addons = preferences.addons
    addon_prefs = addons["object_boolean_tools"].preferences
    if addon_prefs.fast_transform:
        return True
    else:
        return False


class KePieBoolTool(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_booltool"
    bl_label = "BoolTool"

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.active_object)

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        obj = context.active_object

        s1 = " \u2002"  # "auto", aka "destructive": default symbol = just invisible spacer
        s2 = " \u2699"  # modifier, default symbol = cog icon

        if not all(check("object_boolean_tools")):
            pie.label(text="BoolTool Add-on not activated")
        else:
            # W
            pie.operator('object.booltool_auto_difference', text="Difference" + s1, icon="SELECT_SUBTRACT")
            # E
            pie.operator('btool.boolean_diff', text="Difference" + s2, icon="SELECT_SUBTRACT")

            # S - Big bottom menu
            col = pie.column()
            col.ui_units_x = 9
            srow = col.row()
            srow.separator(factor=2)
            box = srow.box()
            scol = box.column(align=True)
            scol.operator('object.booltool_auto_intersect', text="Intersect" + s1, icon="SELECT_INTERSECT")
            scol.operator('btool.boolean_inters', text="Intersect" + s2, icon="SELECT_INTERSECT")

            srow.separator(factor=2)
            col.separator(factor=1)
            # srow.separator(factor=2)

            if is_canvas(obj) or is_brush(obj):
                srow = col.row()
                # srow.separator(factor=2)
                box = srow.box()

                if is_canvas(obj):
                    subcol = box.row(align=True)
                    subcol.prop(context.scene, "BoolHide", text="All", icon="RESTRICT_VIEW_OFF")
                    # subcol.separator()
                    subcol.operator('btool.to_mesh', icon="IMPORT", text="All")
                    Rem = subcol.operator('btool.remove', icon="X", text="All")
                    Rem.thisObj = ""
                    Rem.Prop = "CANVAS"

                # srow.separator(factor=2)

                if is_canvas(obj):
                    # col.separator(factor=1)
                    box = col.box()

                    for mod in obj.modifiers:
                        row = box.row(align=True)

                        if "BTool_" in mod.name:
                            op = mod.operation

                            if op == "DIFFERENCE":
                                icon = "SELECT_SUBTRACT"
                            elif op == "UNION":
                                icon = "SELECT_EXTEND"
                            elif op == "INTERSECT":
                                icon = "SELECT_INTERSECT"
                            else:
                                # Fallback: SLICE will always have the same icon as subtract as there is no "slice" op
                                icon = "SELECT_DIFFERENCE"

                            objSelect = row.operator("btool.find_brush", text=mod.object.name, icon=icon, emboss=False)
                            objSelect.obj = mod.object.name

                            EnableIcon = "RESTRICT_VIEW_ON"
                            if mod.show_viewport:
                                EnableIcon = "RESTRICT_VIEW_OFF"
                            Enable = row.operator('btool.enable_brush', icon=EnableIcon, emboss=False)
                            Enable.thisObj = mod.object.name

                            Remove = row.operator("btool.remove", text="", icon="X", emboss=False)
                            Remove.thisObj = mod.object.name
                            Remove.Prop = "THIS"

                        else:
                            row.label(text=mod.name)

                        Up = row.operator("btool.move_stack", icon="TRIA_UP", emboss=False)
                        Up.modif = mod.name
                        Up.direction = "UP"

                        Dw = row.operator("btool.move_stack", icon="TRIA_DOWN", emboss=False)
                        Dw.modif = mod.name
                        Dw.direction = "DOWN"

                elif is_brush(obj):
                    col = box.column(align=False)
                    btype = obj["BoolToolBrush"]

                    if btype == "DIFFERENCE":
                        icon = "SELECT_SUBTRACT"
                    elif btype == "UNION":
                        icon = "SELECT_EXTEND"
                    elif btype == "INTERSECT":
                        icon = "SELECT_INTERSECT"
                    elif btype == "SLICE":
                        icon = "SELECT_DIFFERENCE"
                    else:
                        icon = "NONE"

                    col.label(text=btype, icon=icon)

                    row = col.row(align=True)
                    row.operator('view3d.ke_solo_cutter', text="Solo").mode = "ALL"
                    row.operator('view3d.ke_solo_cutter', text="SoloP").mode = "PRE"
                    row.operator('object.ke_showcuttermod', text="ShowMod")

                    if obj["BoolTool_FTransform"] == "True":
                        ft_icon = "PMARKER_ACT"
                    else:
                        ft_icon = "PMARKER"

                    srow = col.row(align=True)
                    # split = row.split(align=True, factor=0.7)
                    # row = split.row(align=True)
                    if not is_fast_transform():
                        srow.enabled = False
                    srow.operator('btool.enable_ftransf', text="Use FastTf", icon=ft_icon)
                    # row = split.row()
                    row = col.row(align=True)
                    row.operator('btool.enable_this_brush', text="Hide", icon="HIDE_OFF")
                    row.operator('btool.brush_to_mesh', icon="IMPORT", text="Apply")
                    Rem = row.operator('btool.remove', icon="X", text="Del")
                    Rem.thisObj = ""
                    Rem.Prop = "BRUSH"

            # N
            pie.operator('object.ke_polybrush')
            # NW
            pie.operator('object.booltool_auto_difference', text="Slice" + s1, icon="SELECT_DIFFERENCE")
            # NE
            pie.operator('btool.boolean_slice', text="Slice" + s2, icon="SELECT_DIFFERENCE")
            # SW
            pie.operator('object.booltool_auto_union', text="Union" + s1, icon="SELECT_EXTEND")
            # SE
            pie.operator('btool.boolean_union', text="Union" + s2, icon="SELECT_EXTEND")


class KePieFit2Grid(Menu):
    bl_label = "keFit2Grid"
    bl_idname = "VIEW3D_MT_ke_pie_fit2grid"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_modeling

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fit2grid", text="50cm").set_grid = 0.5
        pie.operator("view3d.ke_fit2grid", text="5cm").set_grid = 0.05
        pie.operator("view3d.ke_fit2grid", text="15cm").set_grid = 0.15
        pie.operator("view3d.ke_fit2grid", text="1cm").set_grid = 0.01
        pie.operator("view3d.ke_fit2grid", text="1m").set_grid = 1.0
        pie.operator("view3d.ke_fit2grid", text="2.5cm").set_grid = 0.025
        pie.operator("view3d.ke_fit2grid", text="25cm").set_grid = 0.25
        pie.operator("view3d.ke_fit2grid", text="10cm").set_grid = 0.1


class KePieFit2GridMicro(Menu):
    bl_label = "keFit2Grid_micro"
    bl_idname = "VIEW3D_MT_ke_pie_fit2grid_micro"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_modeling

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fit2grid", text="5mm").set_grid = 0.005
        pie.operator("view3d.ke_fit2grid", text="5µm").set_grid = 0.0005
        pie.operator("view3d.ke_fit2grid", text="1.5mm").set_grid = 0.0015
        pie.operator("view3d.ke_fit2grid", text="1µm").set_grid = 0.0001
        pie.operator("view3d.ke_fit2grid", text="1cm").set_grid = 0.01
        pie.operator("view3d.ke_fit2grid", text="2.5µm").set_grid = 0.00025
        pie.operator("view3d.ke_fit2grid", text="5µm").set_grid = 0.0005
        pie.operator("view3d.ke_fit2grid", text="1mm").set_grid = 0.001


class KePieFitPrim(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_fitprim"
    bl_label = "ke.fit_prim"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_geo

    def draw(self, context):
        cm = context.mode
        layout = self.layout
        pie = layout.menu_pie()

        if cm == "EDIT_MESH":

            w = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            w.ke_fitprim_option = "CYL"
            w.ke_fitprim_pieslot = "W"

            e = pie.operator("view3d.ke_fitprim", text="Cylinder Obj", icon='MESH_CYLINDER')
            e.ke_fitprim_option = "CYL"
            e.ke_fitprim_pieslot = "E"
            e.ke_fitprim_itemize = True

            s = pie.operator("view3d.ke_fitprim", text="Cube", icon='CUBE')
            s.ke_fitprim_option = "BOX"
            s.ke_fitprim_pieslot = "S"

            n = pie.operator("view3d.ke_fitprim", text="Cube Obj", icon='MESH_CUBE')
            n.ke_fitprim_option = "BOX"
            n.ke_fitprim_pieslot = "N"
            n.ke_fitprim_itemize = True

            col = pie.box().column()
            nw = col.operator("view3d.ke_fitprim", text="Sphere", icon='SPHERE')
            nw.ke_fitprim_option = "SPHERE"
            nw.ke_fitprim_pieslot = "NW"
            nw2 = col.operator("view3d.ke_fitprim", text="QuadSphere", icon='SPHERE')
            nw2.ke_fitprim_option = "QUADSPHERE"
            nw2.ke_fitprim_pieslot = "NW"

            col = pie.box().column()
            ne = col.operator("view3d.ke_fitprim", text="Sphere Obj", icon='MESH_UVSPHERE')
            ne.ke_fitprim_option = "SPHERE"
            ne.ke_fitprim_pieslot = "NE"
            ne.ke_fitprim_itemize = True
            ne2 = col.operator("view3d.ke_fitprim", text="QuadSphere Obj", icon='MESH_UVSPHERE')
            ne2.ke_fitprim_option = "QUADSPHERE"
            ne2.ke_fitprim_pieslot = "NE"
            ne2.ke_fitprim_itemize = True

            sw = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            sw.ke_fitprim_option = "PLANE"
            sw.ke_fitprim_pieslot = "SW"

            se = pie.operator("view3d.ke_fitprim", text="Plane Obj", icon='MESH_PLANE')
            se.ke_fitprim_option = "PLANE"
            se.ke_fitprim_pieslot = "SE"
            se.ke_fitprim_itemize = True

        if cm == "OBJECT":
            # W
            pie.separator()

            e = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            e.ke_fitprim_option = "CYL"
            e.ke_fitprim_pieslot = "E"

            # S
            pie.separator()

            n = pie.operator("view3d.ke_fitprim", text="Cube", icon='MESH_CUBE')
            n.ke_fitprim_option = "BOX"
            n.ke_fitprim_pieslot = "N"

            nw2 = pie.operator("view3d.ke_fitprim", text="QuadSphere", icon='MESH_UVSPHERE')
            nw2.ke_fitprim_option = "QUADSPHERE"
            nw2.ke_fitprim_pieslot = "NW"

            ne = pie.operator("view3d.ke_fitprim", text="Sphere", icon='MESH_UVSPHERE')
            ne.ke_fitprim_option = "SPHERE"
            ne.ke_fitprim_pieslot = "NE"

            # SW
            pie.separator()

            se = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            se.ke_fitprim_option = "PLANE"
            se.ke_fitprim_pieslot = "SE"


class KePieFitPrimAdd(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_fitprim_add"
    bl_label = "ke.fit_prim_add"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_geo

    def draw(self, context):
        cm = context.mode
        layout = self.layout
        pie = layout.menu_pie()

        if cm == "EDIT_MESH":

            w = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            w.ke_fitprim_option = "CYL"
            w.ke_fitprim_pieslot = "W"

            e = pie.operator("view3d.ke_fitprim", text="Cylinder Obj", icon='MESH_CYLINDER')
            e.ke_fitprim_option = "CYL"
            e.ke_fitprim_pieslot = "E"
            e.ke_fitprim_itemize = True

            s = pie.operator("view3d.ke_fitprim", text="Cube", icon='CUBE')
            s.ke_fitprim_option = "BOX"
            s.ke_fitprim_pieslot = "S"

            n = pie.operator("view3d.ke_fitprim", text="Cube Obj", icon='MESH_CUBE')
            n.ke_fitprim_option = "BOX"
            n.ke_fitprim_pieslot = "N"
            n.ke_fitprim_itemize = True

            col = pie.box().column()
            nw = col.operator("view3d.ke_fitprim", text="Sphere", icon='SPHERE')
            nw.ke_fitprim_option = "SPHERE"
            nw.ke_fitprim_pieslot = "NW"
            nw2 = col.operator("view3d.ke_fitprim", text="QuadSphere", icon='SPHERE')
            nw2.ke_fitprim_option = "QUADSPHERE"
            nw2.ke_fitprim_pieslot = "NW"

            col = pie.box().column()
            ne = col.operator("view3d.ke_fitprim", text="Sphere Obj", icon='MESH_UVSPHERE')
            ne.ke_fitprim_option = "SPHERE"
            ne.ke_fitprim_pieslot = "NE"
            ne.ke_fitprim_itemize = True
            ne2 = col.operator("view3d.ke_fitprim", text="QuadSphere Obj", icon='MESH_UVSPHERE')
            ne2.ke_fitprim_option = "QUADSPHERE"
            ne2.ke_fitprim_pieslot = "NE"
            ne2.ke_fitprim_itemize = True

            sw = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            sw.ke_fitprim_option = "PLANE"
            sw.ke_fitprim_pieslot = "SW"

            se = pie.operator("view3d.ke_fitprim", text="Plane Obj", icon='MESH_PLANE')
            se.ke_fitprim_option = "PLANE"
            se.ke_fitprim_pieslot = "SE"
            se.ke_fitprim_itemize = True

        if cm == "OBJECT":
            # WEST
            op = pie.operator("view3d.ke_fitprim", text="Cylinder", icon='MESH_CYLINDER')
            op.ke_fitprim_option = "CYL"
            op.ke_fitprim_pieslot = "W"

            # EAST
            c = pie.row()
            s = c.column()
            s.separator(factor=27)
            box = s.box()
            box.emboss = "PULLDOWN_MENU"
            col = box.grid_flow(columns=2, even_columns=True, align=True)
            col.scale_x = 1.5
            col.scale_y = 0.9
            col.operator('object.empty_add', icon='EMPTY_AXIS').type = "PLAIN_AXES"
            col.menu_contents("VIEW3D_MT_mesh_add")
            col.menu_contents("VIEW3D_MT_add")

            # SOUTH
            op = pie.operator("view3d.ke_fitprim", text="Plane", icon='MESH_PLANE')
            op.ke_fitprim_option = "PLANE"
            op.ke_fitprim_pieslot = "S"

            # NORTH
            op = pie.operator("view3d.ke_fitprim", text="Cube", icon='MESH_CUBE')
            op.ke_fitprim_option = "BOX"
            op.ke_fitprim_pieslot = "N"

            # NORTHWEST
            op = pie.operator("view3d.ke_fitprim", text="Sphere", icon='MESH_UVSPHERE')
            op.ke_fitprim_option = "SPHERE"
            op.ke_fitprim_pieslot = "NW"

            # NORTHEAST
            pie.separator()

            # SOUTHWEST
            op = pie.operator("view3d.ke_fitprim", text="QuadSphere", icon='MESH_UVSPHERE')
            op.ke_fitprim_option = "QUADSPHERE"
            op.ke_fitprim_pieslot = "SW"
            # SOUTHEAST - BLANK


class KePieMaterials(Menu):
    bl_label = "keMaterials"
    bl_idname = "VIEW3D_MT_PIE_ke_materials"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_render

    def draw(self, context):
        c = all(check("materials_utils"))
        k = get_prefs()
        op = "view3d.ke_id_material"
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        box = pie.box()
        box.ui_units_x = 7
        col = box.column(align=True)
        col.label(text="Assign ID Material")
        row = col.row(align=True)
        row.template_node_socket(color=k.idm01)
        row.operator(op, text=k.idm01_name).m_id = 1
        row = col.row(align=True)
        row.template_node_socket(color=k.idm02)
        row.operator(op, text=k.idm02_name).m_id = 2
        row = col.row(align=True)
        row.template_node_socket(color=k.idm03)
        row.operator(op, text=k.idm03_name).m_id = 3
        row = col.row(align=True)
        row.template_node_socket(color=k.idm04)
        row.operator(op, text=k.idm04_name).m_id = 4
        row = col.row(align=True)
        row.template_node_socket(color=k.idm05)
        row.operator(op, text=k.idm05_name).m_id = 5
        row = col.row(align=True)
        row.template_node_socket(color=k.idm06)
        row.operator(op, text=k.idm06_name).m_id = 6
        row = col.row(align=True)
        row.template_node_socket(color=k.idm07)
        row.operator(op, text=k.idm07_name).m_id = 7
        row = col.row(align=True)
        row.template_node_socket(color=k.idm08)
        row.operator(op, text=k.idm08_name).m_id = 8
        row = col.row(align=True)
        row.template_node_socket(color=k.idm09)
        row.operator(op, text=k.idm09_name).m_id = 9
        row = col.row(align=True)
        row.template_node_socket(color=k.idm10)
        row.operator(op, text=k.idm10_name).m_id = 10
        row = col.row(align=True)
        row.template_node_socket(color=k.idm11)
        row.operator(op, text=k.idm11_name).m_id = 11
        row = col.row(align=True)
        row.template_node_socket(color=k.idm12)
        row.operator(op, text=k.idm12_name).m_id = 12

        if c:
            # obj = context.object
            mu_prefs = context.preferences.addons["materials_utils"].preferences
            limit = mu_prefs.search_show_limit
            if limit == 0:
                limit = "Inf."
            mat_count = len(bpy.data.materials)
            split_count = 32 if mat_count > 64 else 11
            col_count = round((mat_count / split_count))

            # ASSIGN MATERIALS BOX - RIGHT -------------------------------------------------
            box = pie.box()
            if col_count < 2:
                box.ui_units_x = 7.5
            box.label(text="Assign Material  [%s / %s]" % (mat_count, limit))
            col = box.column_flow(align=False, columns=col_count)
            col.ui_units_x = 6 * col_count
            col.menu_contents("VIEW3D_MT_materialutilities_assign_material")

            # MATERIALS UTILS MAIN BOX - BOTTOM --------------------------------------------
            main = pie.column()
            main.separator(factor=4)
            box = main.box()
            box.ui_units_x = 8
            col = box.column(align=True)
            # col.menu_contents("VIEW3D_MT_materialutilities_main")
            col.menu('VIEW3D_MT_materialutilities_select_by_material',
                     icon='VIEWZOOM')
            col.separator()
            col.operator('VIEW3D_OT_materialutilities_copy_material_to_others',
                         text='Copy Active to Others',
                         icon='COPY_ID')
            col.separator()
            col.menu('VIEW3D_MT_materialutilities_clean_slots',
                     icon='NODE_MATERIAL')
            col.separator()
            col.operator('VIEW3D_OT_materialutilities_replace_material',
                         text='Replace Material',
                         icon='OVERLAY')
            op = col.operator('VIEW3D_OT_materialutilities_fake_user_set',
                              text='Set Fake User',
                              icon='FAKE_USER_OFF')
            op.fake_user = mu_prefs.fake_user
            op.affect = mu_prefs.fake_user_affect
            op = col.operator('VIEW3D_OT_materialutilities_change_material_link',
                              text='Change Material Link',
                              icon='LINKED')
            op.link_to = mu_prefs.link_to
            op.affect = mu_prefs.link_to_affect
            col.separator()
            col.prop(mu_prefs, "search_show_limit")
            col.menu('VIEW3D_MT_materialutilities_specials',
                     icon='SOLO_ON')
        else:
            pie.label(text="Material Utils Add-on Not Enabled")


class KePieMisc(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_misc"
    bl_label = "ke.misc"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return (context.space_data.type == "VIEW_3D" and
                context.object and
                k.m_modeling and
                k.m_geo)

    def draw(self, context):
        # SEKALAISTA PIIRAKKA  ^ - ^
        k = get_prefs()
        mode = context.mode
        layout = self.layout
        pie = layout.menu_pie()
        f_val = 0.1

        looptools = all(check("mesh_looptools"))
        quickpipe = all(check("quick_pipe"))
        meshtools = all(check("mesh_tools"))

        # LÄNSI JA ITÄ
        if mode != "OBJECT":
            if looptools:
                pie.operator('mesh.looptools_space', text="Space       ")
                pie.operator('mesh.looptools_circle', text="Circle      ")
            else:
                box = pie.box()
                box.enabled = False
                box.label(text="LoopTools N/A")
                box = pie.box()
                box.enabled = False
                box.label(text="LoopTools N/A")
        elif mode == "OBJECT":
            pie.operator('view3d.ke_lineararray')
            pie.operator('view3d.ke_radialarray')

        # ETELÄ (LAATIKKO)
        col = pie.column()
        col.ui_units_x = 6
        col.separator(factor=1)
        fx_val = 0.5

        colbox = col.box()
        box = colbox.column(align=True)
        t = context.scene.tool_settings
        row = box.row(align=True)
        row.alignment = "CENTER"
        if mode == "OBJECT":
            row.prop(t, 'use_transform_data_origin', icon_only=True, icon="TRANSFORM_ORIGINS", toggle=True)
            row.separator(factor=fx_val)
            row.prop(t, 'use_transform_pivot_point_align', icon_only=True, icon="OBJECT_ORIGIN", toggle=True)
            row.separator(factor=fx_val)
            row.prop(t, 'use_transform_skip_children', icon_only=True, icon="CON_CHILDOF", toggle=True)
        else:
            row.prop(t, 'use_transform_correct_face_attributes', icon_only=True, icon="MOD_MESHDEFORM", toggle=True)
            if t.use_transform_correct_face_attributes:
                row.prop(t, 'use_transform_correct_keep_connected', icon_only=True, icon="SNAP_VERTEX", toggle=True)
            row.separator(factor=fx_val)
            row.prop(t, 'use_edge_path_live_unwrap', icon_only=True, icon="MOD_UVPROJECT", toggle=True)
            row.separator(factor=fx_val)
            row.prop(t, 'use_mesh_automerge', text="", toggle=True)
            if t.use_mesh_automerge:
                box.separator(factor=fx_val)
                row = box.row(align=True)
                row.alignment = "CENTER"
                if k.experimental:
                    row.prop(t, 'use_mesh_automerge_and_split', text="", toggle=True)
                    row.prop(t, 'double_threshold', text="", toggle=True)
                else:
                    row.enabled = False
                    row.label(text="N/A-Exp.Only")

        colbox = col.box()
        box = colbox.column(align=True)
        if mode == "EDIT_MESH":
            box.operator('wm.tool_set_by_id', text="Smooth      ").name = 'builtin.smooth'
            box.separator(factor=f_val)
            box.operator('wm.tool_set_by_id', text="Randomize").name = 'builtin.randomize'
            box.separator(factor=f_val)
            box.operator('wm.tool_set_by_id', text="Shrink/Fatten").name = 'builtin.shrink_fatten'
            box.separator(factor=f_val)
            box.operator('wm.tool_set_by_id', text="Shear").name = 'builtin.shear'
        else:
            box.operator('object.randomize_transform')
        box.separator(factor=f_val)
        box.operator('view3d.ke_fit2grid')
        box.separator(factor=f_val)
        box.operator('view3d.ke_collision').col_type = 'BOX'
        box.separator(factor=f_val)
        box.operator('transform.bend')
        box.separator(factor=f_val)
        box.operator('transform.push_pull')
        box.separator(factor=f_val)
        box.operator('transform.tosphere')

        # POHJOINEN
        pie.operator('view3d.ke_nice_project', text="Nice Project")

        # LUODE
        if mode != "OBJECT":
            if quickpipe:
                pie.operator('object.quickpipe')
            else:
                box = pie.box()
                box.enabled = False
                box.label(text="QuickPipe N/A")
        else:
            pie.operator('view3d.ke_quickmeasure').qm_start = "DEFAULT"

        # KOILINEN
        if mode != "OBJECT":
            pie.operator('mesh.ke_unbevel', text="Unbevel      ")
        else:
            pie.menu("VIEW3D_MT_object_convert")

        # LOUNAS
        pie.operator('view3d.ke_quick_origin_move')

        # KAAKKO
        if mode != "OBJECT":
            row = pie.row()
            row.separator(factor=1.5)
            p = row.column()
            p.separator(factor=22)
            p.ui_units_x = 6
            box = p.box()
            col = box.column(align=True)
            col.operator('mesh.ke_activeslice', text="Active Slice")
            col.separator(factor=0.5)
            if meshtools:
                col.menu_contents('VIEW3D_MT_ke_edit_mesh')
            else:
                row = col.row()
                row.enabled = False
                row.label(text="EditMesh Tools N/A")
                col.separator(factor=20)

        else:
            pie.operator('view3d.ke_zerolocal')


class KeMenuEditMesh(Menu):
    bl_idname = "VIEW3D_MT_ke_edit_mesh"
    bl_label = "MeshTools"

    def draw(self, context):
        layout = self.layout
        layout.operator('mesh.offset_edges', text="Offset Edges").geometry_mode = "extrude"
        layout.operator('mesh.vertex_chamfer', text="Vertex Chamfer")
        layout.operator('mesh.fillet_plus', text="Fillet Edges")
        layout.operator("mesh.face_inset_fillet", text="Face Inset Fillet")
        layout.operator("object.mextrude", text="Multi Extrude")
        layout.operator('mesh.split_solidify', text="Split Solidify")
        layout.operator("mesh.random_vertices", text="Random Vertices")
        layout.operator('object.mesh_edge_length_set', text="Set Edge Length")
        layout.operator('mesh.edges_floor_plan', text="Edges Floor Plan")
        layout.operator('mesh.edge_roundifier', text="Edge Roundify")


def get_props(p, preset="0"):
    v1, v2, v3, v4 = 0, 0, 0, 0
    if preset == "0":
        v1, v2, v3, v4 = p[0], p[1], p[2], p[3]
    elif preset == "1":
        v1, v2, v3, v4 = p[4], p[5], p[6], p[7]
    elif preset == "2":
        v1, v2, v3, v4 = p[8], p[9], p[10], p[11]
    elif preset == "3":
        v1, v2, v3, v4 = p[12], p[13], p[14], p[15]
    elif preset == "4":
        v1, v2, v3, v4 = p[16], p[17], p[18], p[19]
    elif preset == "5":
        v1, v2, v3, v4 = p[20], p[21], p[22], p[23]
    elif preset == "6":
        v1, v2, v3, v4 = p[24], p[25], p[26], p[27]
    elif preset == "7":
        v1, v2, v3, v4 = p[28], p[29], p[30], p[31]
    return v1, str(int(v2)), v3, bool(v4)


class KePieMultiCut(Menu):
    bl_label = "keMultiCut"
    bl_idname = "VIEW3D_MT_ke_pie_multicut"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_modeling

    def draw(self, context):
        k = get_prefs()
        p = k.mc_prefs[:]
        mc = 'mesh.ke_multicut'
        layout = self.layout
        pie = layout.menu_pie()

        op = pie.operator(mc, text="%s" % k.mc_name0)
        v1, v2, v3, v4 = get_props(p, preset="0")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name1)
        v1, v2, v3, v4 = get_props(p, preset="1")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name2)
        v1, v2, v3, v4 = get_props(p, preset="2")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name3)
        v1, v2, v3, v4 = get_props(p, preset="3")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name4)
        v1, v2, v3, v4 = get_props(p, preset="4")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name5)
        v1, v2, v3, v4 = get_props(p, preset="5")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name6)
        v1, v2, v3, v4 = get_props(p, preset="6")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"

        op = pie.operator(mc, text="%s" % k.mc_name7)
        v1, v2, v3, v4 = get_props(p, preset="7")
        op.o_relative = v1
        op.o_center = v2
        op.o_fixed = v3
        op.using_fixed = v4
        op.preset = "SET"


class KePieOrientPivot(Menu):
    bl_label = "keOrientPivot"
    bl_idname = "VIEW3D_MT_ke_pie_orientpivot"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_bookmarks

    def draw(self, context):
        k = get_prefs()
        ct = context.scene.tool_settings
        name1 = k.opc1_name
        name2 = k.opc2_name
        name3 = k.opc3_name
        name4 = k.opc4_name
        name5 = k.opc5_name
        name6 = k.opc6_name

        mode = context.mode
        obj = context.active_object
        extmode = False
        if (obj is None) or (mode in {'OBJECT', 'POSE', 'WEIGHT_PAINT'}):
            extmode = True

        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_opc", text="%s" % name5, icon_value=pcoll['kekit']['ke_opc5'].icon_id).combo = "5"
        pie.operator("view3d.ke_opc", text="%s" % name3, icon_value=pcoll['kekit']['ke_opc3'].icon_id).combo = "3"
        pie.operator("view3d.ke_opc", text="%s" % name4, icon_value=pcoll['kekit']['ke_opc4'].icon_id).combo = "4"
        pie.operator("view3d.ke_opc", text="%s" % name1, icon_value=pcoll['kekit']['ke_opc1'].icon_id).combo = "1"
        pie.operator("view3d.ke_opc", text="%s" % name6, icon_value=pcoll['kekit']['ke_opc6'].icon_id).combo = "6"
        pie.operator("view3d.ke_opc", text="%s" % name2, icon_value=pcoll['kekit']['ke_opc2'].icon_id).combo = "2"

        c = pie.column()
        c.separator(factor=13)
        cbox = c.box().column(align=True)
        cbox.scale_y = 1.2
        cbox.ui_units_x = 6.25
        cbox.prop(context.scene.transform_orientation_slots[0], "type", expand=True)

        c = pie.column()
        c.separator(factor=12.5)
        cbox = c.box().column(align=True)
        cbox.ui_units_x = 6.5
        cbox.scale_y = 1.3
        cbox.prop_enum(ct, "transform_pivot_point", value='BOUNDING_BOX_CENTER')
        cbox.prop_enum(ct, "transform_pivot_point", value='CURSOR')
        cbox.prop_enum(ct, "transform_pivot_point", value='INDIVIDUAL_ORIGINS')
        cbox.prop_enum(ct, "transform_pivot_point", value='MEDIAN_POINT')
        cbox.prop_enum(ct, "transform_pivot_point", value='ACTIVE_ELEMENT')
        if extmode:
            cbox = c.box().column(align=True)
            cbox.prop(ct, "use_transform_pivot_point_align")
        else:
            c.separator(factor=3)


class KePieOverlays(Menu):
    bl_label = "keOverlays"
    bl_idname = "VIEW3D_MT_ke_pie_overlays"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        o = context.space_data.overlay
        s = context.space_data.shading
        cm = context.mode
        op = "view3d.ke_overlays"

        layout = self.layout
        pie = layout.menu_pie()

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.15
        cbox.ui_units_x = 7

        if s.show_backface_culling:
            cbox.operator(op, text="Backface Culling", icon="XRAY", depress=True).overlay = "BACKFACE"
        else:
            cbox.operator(op, text="Backface Culling", icon="XRAY",
                          depress=False).overlay = "BACKFACE"

        cbox.separator(factor=0.25)

        row = cbox.row(align=True)
        if o.show_floor:
            row.operator(op, text="Floor", depress=True).overlay = "GRID"
        else:
            row.operator(op, text="Floor", depress=False).overlay = "GRID"

        if o.show_ortho_grid:
            row.operator(op, text="Grid", depress=True).overlay = "GRID_ORTHO"
        else:
            row.operator(op, text="Grid", depress=False).overlay = "GRID_ORTHO"

        row.operator(op, text="Both").overlay = "GRID_BOTH"

        cbox.separator(factor=0.25)

        if o.show_extras:
            cbox.operator(op, text="Extras", icon="LIGHT_SUN", depress=True).overlay = "EXTRAS"
        else:
            cbox.operator(op, text="Extras", icon="LIGHT_SUN", depress=False).overlay = "EXTRAS"

        if o.show_cursor:
            cbox.operator(op, text="Cursor", icon="CURSOR", depress=True).overlay = "CURSOR"
        else:
            cbox.operator(op, text="Cursor", icon="CURSOR", depress=False).overlay = "CURSOR"

        if o.show_object_origins:
            cbox.operator(op, text="Origins", icon="OBJECT_ORIGIN", depress=True).overlay = "ORIGINS"
        else:
            cbox.operator(op, text="Origins", icon="OBJECT_ORIGIN", depress=False).overlay = "ORIGINS"

        if o.show_bones:
            cbox.operator(op, text="Bones", icon="BONE_DATA", depress=True).overlay = "BONES"
        else:
            cbox.operator(op, text="Bones", icon="BONE_DATA", depress=False).overlay = "BONES"

        if o.show_relationship_lines:
            cbox.operator(op, text="Relationship Lines", icon="CON_TRACKTO",
                          depress=True).overlay = "LINES"
        else:
            cbox.operator(op, text="Relationship Lines", icon="CON_TRACKTO",
                          depress=False).overlay = "LINES"

        cbox.separator(factor=0.25)

        if o.show_wireframes:
            cbox.operator(op, text="Object Wireframes", icon="MOD_WIREFRAME",
                          depress=True).overlay = "WIREFRAMES"
        else:
            cbox.operator(op, text="Object Wireframes", icon="MOD_WIREFRAME",
                          depress=False).overlay = "WIREFRAMES"

        if o.show_outline_selected:
            cbox.operator(op, text="Select Outline", icon="MESH_CIRCLE",
                          depress=True).overlay = "OUTLINE"
        else:
            cbox.operator(op, text="Select Outline", icon="MESH_CIRCLE",
                          depress=False).overlay = "OUTLINE"

        if s.show_object_outline:
            cbox.operator(op, text="Object Outline", icon="MESH_CIRCLE",
                          depress=True).overlay = "OBJ_OUTLINE"
        else:
            cbox.operator(op, text="Object Outline", icon="MESH_CIRCLE",
                          depress=False).overlay = "OBJ_OUTLINE"

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.15
        cbox.ui_units_x = 7
        if cm == "OBJECT":
            cbox.enabled = False

        if o.show_edge_seams:
            cbox.operator(op, text="Edge Seams", icon="UV_ISLANDSEL", depress=True).overlay = "SEAMS"
        else:
            cbox.operator(op, text="Edge Seams", icon="UV_ISLANDSEL", depress=False).overlay = "SEAMS"

        if o.show_edge_sharp:
            cbox.operator(op, text="Edge Sharp", icon="MESH_CUBE", depress=True).overlay = "SHARP"
        else:
            cbox.operator(op, text="Edge Sharp", icon="MESH_CUBE", depress=False).overlay = "SHARP"

        if o.show_edge_crease:
            cbox.operator(op, text="Edge Crease", icon="META_CUBE", depress=True).overlay = "CREASE"
        else:
            cbox.operator(op, text="Edge Crease", icon="META_CUBE", depress=False).overlay = "CREASE"

        if o.show_edge_bevel_weight:
            cbox.operator(op, text="Edge Bevel Weight", icon="MOD_BEVEL",
                          depress=True).overlay = "BEVEL"
        else:
            cbox.operator(op, text="Edge Bevel Weight", icon="MOD_BEVEL",
                          depress=False).overlay = "BEVEL"

        cbox.separator(factor=0.25)

        if o.show_vertex_normals:
            cbox.operator(op, text="Vertex Normals", icon="NORMALS_VERTEX",
                          depress=True).overlay = "VN"
        else:
            cbox.operator(op, text="Vertex Normals", icon="NORMALS_VERTEX",
                          depress=False).overlay = "VN"

        if o.show_split_normals:
            cbox.operator(op, text="Split Normals", icon="NORMALS_VERTEX_FACE",
                          depress=True).overlay = "SN"
        else:
            cbox.operator(op, text="Split Normals", icon="NORMALS_VERTEX_FACE",
                          depress=False).overlay = "SN"

        if o.show_face_normals:
            cbox.operator(op, text="Face Normals", icon="NORMALS_FACE", depress=True).overlay = "FN"
        else:
            cbox.operator(op, text="Face Normals", icon="NORMALS_FACE", depress=False).overlay = "FN"

        cbox.separator(factor=0.25)

        if o.show_face_orientation:
            cbox.operator(op, text="Face Orientation", icon="FACESEL",
                          depress=True).overlay = "FACEORIENT"
        else:
            cbox.operator(op, text="Face Orientation", icon="FACESEL",
                          depress=False).overlay = "FACEORIENT"

        if o.show_weight:
            cbox.operator(op, text="Vertex Weights", icon="GROUP_VERTEX",
                          depress=True).overlay = "WEIGHT"
        else:
            cbox.operator(op, text="Vertex Weights", icon="GROUP_VERTEX",
                          depress=False).overlay = "WEIGHT"

        cbox.separator(factor=0.25)

        row = cbox.row(align=True)
        if o.show_extra_indices:
            row.operator(op, text="Indices", depress=True).overlay = "INDICES"
        else:
            row.operator(op, text="Indices",
                         depress=False).overlay = "INDICES"

        row.separator(factor=0.1)

        if o.show_extra_edge_length:
            row.operator(op, text="Edge Lengths", depress=True).overlay = "LENGTHS"
        else:
            row.operator(op, text="Edge Lengths",
                         depress=False).overlay = "LENGTHS"

        c = pie.column()
        c.separator(factor=4)
        cbox = c.box().column()
        cbox.scale_y = 1.15
        cbox.ui_units_x = 7
        cbox.use_property_split = False

        obj = context.object
        if obj:
            obj_type = obj.type
            is_geometry = (obj_type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME', 'HAIR', 'POINTCLOUD'})
            has_bounds = (is_geometry or obj_type in {'LATTICE', 'ARMATURE'})
            is_wire = (obj_type in {'CAMERA', 'EMPTY'})
            is_dupli = (obj.instance_type != 'NONE')

            col = cbox.column(align=True)
            row = col.row()
            if o.show_stats:
                row.operator(op, text="Stats", icon="LINENUMBERS_ON", depress=True).overlay = "STATS"
            else:
                row.operator(op, text="Stats", icon="LINENUMBERS_ON", depress=False).overlay = "STATS"
            row = col.row()
            row.scale_y = 0.8
            row.enabled = False
            row.label(text="Show Active Object:")
            col.prop(obj, "show_name", text="Name")
            col.prop(obj, "show_axis", text="Axis")

            if is_geometry or is_dupli:
                col.prop(obj, "show_wire", text="Wireframe")
            if obj_type == 'MESH' or is_dupli:
                col.prop(obj, "show_all_edges", text="All Edges")
            if is_geometry:
                col.prop(obj, "show_texture_space", text="Texture Space")
                col.prop(obj.display, "show_shadows", text="Shadow")
            col.prop(obj, "show_in_front", text="In Front")

            if has_bounds:
                col.prop(obj, "show_bounds")

            sub = col.row(align=True)
            if is_wire:
                # wire objects only use the max. display type for duplis
                sub.active = is_dupli

            if has_bounds:
                sub.prop(obj, "display_bounds_type", text="")
            sub.prop(obj, "display_type", text="")
        else:
            col = cbox.column()
            col.enabled = False
            col.label(text="No Active Object")

        c = pie.column()
        cbox = c.box().row(align=True)
        cbox.scale_y = 1.2
        cbox.operator(op, text="All Overlays", icon="OVERLAY").overlay = "ALL"
        cbox.operator(op, text="All Edge Overlays", icon="UV_EDGESEL").overlay = "ALLEDIT"
        c.separator(factor=7)


class KePieShading(Menu):
    bl_label = "keShading"
    bl_idname = "KE_MT_shading_pie"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        k = get_prefs()
        xp = k.experimental
        layout = self.layout
        shading = None
        view = context.space_data
        if view.type == 'VIEW_3D':
            shading = view.shading
        if shading is None:
            print("Pie Menu not drawn: Incorrect Context Fallback")
            return {'CANCELLED'}

        pie = layout.menu_pie()

        # SLOT
        pie.prop(shading, "type", expand=True)

        # SLOT
        if shading.type == 'RENDERED':
            c = pie.row()
            b = c.column()
            col = b.box().column()
            col.scale_y = 0.9
            col.prop(shading, "use_scene_lights_render")
            col.prop(shading, "use_scene_world_render")
            if is_registered("VIEW3D_OT_ke_bg_sync"):
                col.operator("view3d.ke_bg_sync", icon="SHADING_TEXTURE")
            else:
                col.label(text="BG sync N/A")
            # col.separator(factor=1.2)

            row = col.row()
            row.prop(shading, "render_pass", text="")
            row.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
            c.separator(factor=2.5)
            b.separator(factor=3.5)
        else:
            pie.separator()

        # SLOT
        if shading.type == 'SOLID' and shading.light != 'FLAT':
            spacer = pie.row()
            spacer.label(text="")

            col = spacer.box().column()
            sub = col.row()

            if shading.light == 'STUDIO':
                prefs = context.preferences
                system = prefs.system

                if not system.use_studio_light_edit:
                    sub.scale_y = 0.6
                    sub.scale_x = .738
                    sub.template_icon_view(shading, "studio_light", scale_popup=3.0)
                else:
                    sub.prop(
                        system,
                        "use_studio_light_edit",
                        text="Disable Studio Light Edit",
                        icon='NONE',
                        toggle=True,
                    )
                sub2 = sub.column()
                sub2.scale_x = 1.3
                sub2.scale_y = 1.8
                p = sub2.column(align=False)
                p.prop(shading, "use_world_space_lighting", text="World Space Lighting", icon='WORLD', toggle=True)
                p.operator("preferences.studiolight_show", text="Preferences", emboss=False, icon='PREFERENCES')
                p.separator(factor=0.3)
                if xp:
                    p.prop(shading, "studiolight_rotate_z", text="RotateZ")
                else:
                    p.label(text="Rot Disabled")

            elif shading.light == 'MATCAP':
                sub.scale_y = 0.6
                sub.scale_x = .7
                sub.template_icon_view(shading, "studio_light", scale_popup=3.0)

                sub = sub.column()
                sub.scale_y = 1.8
                sub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
                sub.operator("view3d.toggle_matcap_flip", emboss=False, text="", icon='ARROW_LEFTRIGHT')

        elif shading.type == 'RENDERED' and not shading.use_scene_world_render:
            b = pie.row()
            c = b.column()

            col = b.box().column()
            col.scale_y = 0.65
            col.scale_x = 0.7
            sub = col.row()
            sub.template_icon_view(shading, "studio_light", scale_popup=3)

            sub2 = sub.column()
            sub2.scale_y = 1.4
            sub2.scale_x = 1.1
            if xp:
                sub2.prop(shading, "studiolight_rotate_z", text="RotateZ")
            else:
                sub2.label(text="Rot Disabled")
            sub2.prop(shading, "studiolight_intensity", text="Intensity")
            sub2.prop(shading, "studiolight_background_alpha", text="Alpha")
            sub2.prop(shading, "studiolight_background_blur", text="Blur")
            b.separator(factor=13.5)
            c.separator(factor=2.5)

        else:
            pie.separator()

        # SLOT
        if shading.type == 'MATERIAL':
            r = pie.row()
            c = r.column()
            c.separator(factor=16)
            col = c.box().column()
            col.scale_y = 0.9
            col.prop(shading, "use_scene_lights")
            col.prop(shading, "use_scene_world")
            col.operator("view3d.ke_bg_sync", icon="SHADING_TEXTURE")
            # col.separator(factor=1.2)
            row = col.row()
            row.prop(shading, "render_pass", text="")
            row.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
            r.separator(factor=2.4)

        else:
            pie.separator()

        # SLOT
        r = pie.row()
        r.separator(factor=2.4)
        c = r.column()

        if shading.type == 'SOLID':
            c.separator(factor=3)
            col = c.box().column()
            col.ui_units_x = 12
            lights = col.row()
            lights.prop(shading, "light", expand=True)
            col.separator(factor=0.5)
            col.grid_flow(columns=3, align=True).prop(shading, "color_type", expand=True)

            obj = context.object
            if shading.color_type == 'SINGLE':
                col.column().prop(shading, "single_color", text="")

            elif obj and shading.color_type == "OBJECT":
                obj_type = obj.type
                is_geometry = (obj_type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME', 'HAIR',
                                            'POINTCLOUD'})
                is_empty_image = (obj_type == 'EMPTY' and obj.empty_display_type == 'IMAGE')
                is_dupli = (obj.instance_type != 'NONE')
                is_gpencil = (obj_type == 'GPENCIL')
                if is_geometry or is_dupli or is_empty_image or is_gpencil:
                    col.column().prop(obj, "color", text="")

            col.separator(factor=0.5)
            opt = col.row(align=True)
            opt.alignment = "CENTER"
            opt.prop(shading, "show_shadows", text="Shadows", toggle=True)
            opt.prop(shading, "show_cavity", text="Cavity", toggle=True)
            opt.prop(shading, "show_specular_highlight", text="Specular", toggle=True)

        elif shading.type == 'MATERIAL':
            if not shading.use_scene_world:
                c.separator(factor=16)
                col = c.box().column()
                sub = col.row()
                sub.scale_y = 0.65
                sub.scale_x = 0.7
                sub.template_icon_view(shading, "studio_light", scale_popup=3)

                sub2 = sub.column()
                sub2.scale_y = 1.4
                sub2.scale_x = 1.1
                if xp:
                    sub2.prop(shading, "studiolight_rotate_z", text="RotateZ")
                else:
                    sub2.label(text="Rot Disabled")
                sub2.prop(shading, "studiolight_intensity", text="Intensity")
                sub2.prop(shading, "studiolight_background_alpha", text="Alpha")
                sub2.prop(shading, "studiolight_background_blur", text="Blur")


class KePieSnapAlign(Menu):
    bl_label = "keSnapAlign"
    bl_idname = "VIEW3D_MT_ke_pie_align"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_modeling and k.m_selection

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.cursor_fit_selected_and_orient", text="Cursor Fit&Align", icon="ORIENTATION_CURSOR")

        pie.operator("mesh.ke_zeroscale", text="ZeroScale H", icon="NODE_SIDE").screen_axis = 0

        pie.operator("mesh.ke_zeroscale", text="ZeroScale Cursor", icon="CURSOR").orient_type = "CURSOR"

        pie.operator("mesh.ke_zeroscale", text="ZeroScale V", icon="NODE_TOP").screen_axis = 1

        c = pie.row()
        main = c.column()
        selbox = main.box().column()
        selbox.operator("view3d.snap_selected_to_grid", text="Selection to Grid", icon='RESTRICT_SELECT_OFF')
        selbox.operator("view3d.snap_selected_to_cursor", text="Selection to Cursor",
                        icon='RESTRICT_SELECT_OFF').use_offset = False
        selbox.operator("view3d.snap_selected_to_cursor", text="Sel.to Cursor w.Offset",
                        icon='RESTRICT_SELECT_OFF').use_offset = True
        selbox.operator("view3d.snap_selected_to_active", text="Selection to Active", icon='RESTRICT_SELECT_OFF')
        selbox.operator("view3d.selected_to_origin", text="Sel.to Origin (Set Origin)", icon='RESTRICT_SELECT_OFF')
        spacer = c.column()
        spacer.label(text="")
        main.label(text="")
        main.label(text="")

        pie.operator("mesh.ke_zeroscale", text="ZeroScale Normal", icon="NORMALS_FACE").orient_type = "NORMAL"

        c = pie.row()
        main = c.column()
        main.label(text="")
        main.label(text="")
        cbox = main.box().column()
        cbox.operator("view3d.snap_cursor_to_center", text="Cursor to World Origin", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_selected", text="Cursor to Selected", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_active", text="Cursor to Active", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_grid", text="Cursor to Grid", icon='CURSOR')
        cbox.operator("view3d.ke_cursor_clear_rot", icon='CURSOR')
        spacer = c.column()
        spacer.label(text="")

        spacer = pie.row()
        spacer.label(text="")
        vbox = spacer.column()
        vbox.label(text="")
        vbox.label(text="")
        vbox = vbox.box().column()
        vbox.operator('view3d.align_origin_to_selected', text="Align Origin To Selected", icon="OBJECT_ORIGIN")
        vbox.operator('view3d.ke_origin_to_cursor', text="Align Origin(s) To Cursor", icon="PIVOT_CURSOR")
        vbox.operator('view3d.ke_object_to_cursor', text="Align Object(s) to Cursor", icon="CURSOR")
        vbox.operator('view3d.ke_align_object_to_active', text="Align Object(s) to Active", icon="CON_LOCLIKE")
        vbox.operator('view3d.ke_swap', text="Swap Places", icon="CON_TRANSLIKE")


class KePieSnapping(Menu):
    bl_label = "keSnapping"
    bl_idname = "VIEW3D_MT_ke_pie_snapping"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_bookmarks

    def draw(self, context):
        k = get_prefs()
        ct = context.scene.tool_settings
        name1 = k.snap_name1
        name2 = k.snap_name2
        name3 = k.snap_name3
        name4 = k.snap_name4
        name5 = k.snap_name5
        name6 = k.snap_name6
        s1 = pcoll['kekit']['ke_snap1'].icon_id
        s2 = pcoll['kekit']['ke_snap2'].icon_id
        s3 = pcoll['kekit']['ke_snap3'].icon_id
        s4 = pcoll['kekit']['ke_snap4'].icon_id
        s5 = pcoll['kekit']['ke_snap5'].icon_id
        s6 = pcoll['kekit']['ke_snap6'].icon_id

        layout = self.layout
        pie = layout.menu_pie()

        # W
        pie.operator("view3d.ke_snap_combo", icon_value=s5, text="%s" % name5).mode = "SET5"
        # E
        pie.operator("view3d.ke_snap_combo", icon_value=s3, text="%s" % name3).mode = "SET3"
        # S
        pie.operator("view3d.ke_snap_combo", icon_value=s4, text="%s" % name4).mode = "SET4"
        # N
        pie.operator("view3d.ke_snap_combo", icon_value=s1, text="%s" % name1).mode = "SET1"
        # NW
        pie.operator("view3d.ke_snap_combo", icon_value=s6, text="%s" % name6).mode = "SET6"
        # NE
        pie.operator("view3d.ke_snap_combo", icon_value=s2, text="%s" % name2).mode = "SET2"

        # SW
        c = pie.column()
        c.separator(factor=28)
        c.ui_units_x = 9
        c.scale_y = 1.15
        cr = c.row()
        cbox = cr.box().column(align=True)
        cbox.prop(ct, 'snap_elements', expand=True)
        # cbox.prop(ct, 'snap_elements_individual', expand=True)
        cbox.separator(factor=1)
        crow = cbox.grid_flow(align=True)
        crow.prop(ct, 'snap_target', expand=True)
        cr.separator(factor=2.5)

        # SE
        c = pie.row()
        c.separator(factor=2.5)
        c.ui_units_x = 9
        c.scale_y = 1.15
        r = c.column()
        r.separator(factor=29)
        cbox = r.box().row(align=True)
        cbox.prop(ct, 'use_snap', text="Snapping")
        cbox.prop(k, "combo_autosnap", text="Auto")
        r.separator(factor=0.5)
        cbox = r.box().column()
        cbox.scale_y = 1.05
        col = cbox.column(align=True)
        if not ct.use_snap_grid_absolute:
            col.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=False).op = "GRID"
        else:
            col.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=True).op = "GRID"
        col.prop(ct, 'use_snap_align_rotation', text="Align Rotation")
        col.prop(ct, 'use_snap_backface_culling', text="Backface Culling")
        col.prop(ct, 'use_snap_peel_object', text="Peel Object")
        # cbox.separator(factor=0.5)
        col = cbox.column(align=True)
        if context.mode == "OBJECT":
            col.enabled = False
        col.prop(ct, 'use_snap_self')
        col.prop(ct, 'use_snap_edit')
        col.prop(ct, 'use_snap_nonedit')
        cbox.prop(ct, 'use_snap_selectable')
        # cbox.separator(factor=0.5)
        row = cbox.row(align=True)
        row.prop(ct, 'use_snap_translate', text="T")
        row.prop(ct, 'use_snap_rotate', text="R")
        row.prop(ct, 'use_snap_scale', text="S")


class KePieStepRotate(Menu):
    bl_label = "keVPStepRotate"
    bl_idname = "VIEW3D_MT_ke_pie_step_rotate"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_selection

    def draw(self, context):
        k = get_prefs()
        xp = k.experimental
        op = "view3d.ke_vp_step_rotate"
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator(op, text="-90", icon="LOOP_BACK").rot = -90
        pie.operator(op, text="90", icon="LOOP_FORWARDS").rot = 90

        s = pie.column()
        s.separator(factor=2.5)
        s.scale_x = 0.85
        row = s.row(align=True)
        # row.scale_x = 0.5
        # row.scale_y = 1.2
        row.label(text=" ")
        row.label(text=" ")
        row.operator("object.location_clear", text="LOC").clear_delta = False
        row.operator("object.scale_clear", text="SCL").clear_delta = False
        row.operator("object.ke_object_op", text="CLR").cmd = "CLEAR_LR"
        row.label(text=" ")
        row.label(text=" ")

        box = s.box()
        box.scale_y = 1.1
        row = box.row(align=True)
        # Removing due to "unsupported RNA type 2" errors, solution TBD
        split = row
        if xp:
            split = row.split(factor=0.4, align=True)
            row = split.column(align=True)
        row.operator("object.ke_object_op", text="X Clear").cmd = "ROT_CLEAR_X"
        row.operator("object.ke_object_op", text="Y Clear").cmd = "ROT_CLEAR_Y"
        row.operator("object.ke_object_op", text="Z Clear").cmd = "ROT_CLEAR_Z"
        if xp:
            row = split.column(align=True)
            row.prop(context.object, "rotation_euler", text="")

        box = s.column(align=True)
        box.operator("object.ke_straighten", text="Straighten Object", icon="CON_ROTLIMIT").deg = 90

        pie.operator("object.rotation_clear", text="Rotation (Clear)").clear_delta = False
        pie.operator(op, text="-45", icon="LOOP_BACK").rot = -45
        pie.operator(op, text=" 45", icon="LOOP_FORWARDS").rot = 45
        pie.operator(op, text="-180", icon="LOOP_BACK").rot = -180
        pie.operator(op, text=" 180", icon="LOOP_FORWARDS").rot = 180


class KePieSubd(Menu):
    bl_idname = "VIEW3D_MT_ke_pie_subd"
    bl_label = "keSubd"

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.active_object)

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        k = get_prefs()

        if k.experimental:
            # Check existing modifiers
            bevel_mods = []
            mirror_mods = []
            solidify_mods = []
            subd_mods = []
            wn_mods = []
            vgicon = "GROUP_VERTEX"

            cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
            active = context.active_object

            if active and active.type in cat:
                for m in active.modifiers:
                    if m.type == "BEVEL":
                        bevel_mods.append(m)
                    elif m.type == "MIRROR":
                        mirror_mods.append(m)
                    elif m.type == "SOLIDIFY":
                        solidify_mods.append(m)
                    elif m.type == "SUBSURF":
                        subd_mods.append(m)
                    elif m.type == "WEIGHTED_NORMAL":
                        wn_mods.append(m)

            vertex_groups = [i for i in active.vertex_groups if i.name[:3] == "V_G"]

            # Bevel Weights
            pie.operator("ke.pieops", text="Bevel Weight -1").op = "BWEIGHTS_OFF"
            pie.operator("ke.pieops", text="Bevel Weight 1").op = "BWEIGHTS_ON"

            # MAIN BOX
            vg = pie.column()
            vg.ui_units_x = 24.5

            # VERTEX GROUPS ASSIGNMENT
            if vertex_groups:
                box = vg.box()
                row = box.row(align=True)
                split = row.split(factor=1, align=True)
                split.operator("ke.pieops", text="Clear").op = "CLEAR_VG"
                row.separator(factor=1)

                n = vertex_groups[0].name
                row.operator("ke.pieops", text=n, icon=vgicon).op = "ADD_VG¤" + n

                if len(vertex_groups) > 1:
                    for group in vertex_groups[1:]:
                        gn = group.name[-3:]
                        row.operator("ke.pieops", text=gn, icon=vgicon).op = "ADD_VG¤" + group.name

                row.separator(factor=1)
                row.operator("ke.pieops", text="New").op = "ADD_VG"
            else:
                row = vg.row()
                split = row.split()
                split.separator(factor=1)
                split.operator("ke.pieops", text="New Bevel VGroup", icon=vgicon).op = "ADD_VG"
                split.separator(factor=1)

            vg.separator()
            main = vg.row(align=True)
            main.alignment = "LEFT"

            # MIRROR & LATTICE
            c = main.column(align=False)
            c.ui_units_x = 9
            c.scale_y = 0.9

            if mirror_mods:
                for m in mirror_mods:
                    col = c.box().column()
                    menu = col.row(align=True)
                    menu.label(text=m.name, icon="MOD_MIRROR")
                    menu.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    menu.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)
                    col.separator(factor=0.5)
                    col.scale_y = 0.8
                    sub = col.row(align=True)
                    sub.label(text="Mirror XYZ")
                    sub.prop(m, "use_axis", icon_only=True)
                    sub = col.row(align=True)
                    sub.label(text="Bisect XYZ")
                    sub.prop(m, "use_bisect_axis", icon_only=True)
                    sub = col.row(align=True)
                    sub.label(text="Flip XYZ")
                    sub.prop(m, "use_bisect_flip_axis", icon_only=True)
                    col.separator(factor=0.5)
                    sub = col.row(align=True)
                    sub.label(text="Use World Origo")
                    mop = sub.operator("ke.pieops", text="", icon="ORIENTATION_GLOBAL")
                    mop.op = "MIRROR_W"
                    mop.mname = m.name
                    xmop = sub.operator("ke.pieops", text="", icon="X")
                    xmop.op = "REM_MIRROR_W"
                    xmop.mname = m.name
                    c.separator(factor=0.7)
            else:
                sub = c.box().column(align=True)
                c.scale_y = 1.0
                sub.label(text="Add Mirror [+Bisect]", icon="MOD_MIRROR")
                row = sub.row(align=True)
                row.operator("ke.pieops", text="X").op = "MIRROR_X"
                row.operator("ke.pieops", text="", icon="EVENT_B").op = "SYM_X"
                row.separator(factor=0.3)
                row.operator("ke.pieops", text="Y").op = "MIRROR_Y"
                row.operator("ke.pieops", text="", icon="EVENT_B").op = "SYM_Y"
                row.separator(factor=0.3)
                row.operator("ke.pieops", text="Z").op = "MIRROR_Z"
                row.operator("ke.pieops", text="", icon="EVENT_B").op = "SYM_Z"
                c.separator(factor=0.7)

            # VG Selection & Removal
            if vertex_groups:
                col = c.box().column()
                for group in vertex_groups:
                    gn = group.name[-3:]
                    row = col.row(align=True)
                    split = row.split(factor=0.4)
                    split.label(text=gn, icon=vgicon)
                    sub = split.row(align=True)
                    sub.operator("ke.pieops", text="", icon="ADD").op = "OPVG¤SEL¤" + gn
                    sub.operator("ke.pieops", text="", icon="REMOVE").op = "OPVG¤DSEL¤" + gn
                    sub.operator("ke.pieops", text="", icon="LOOP_BACK").op = "OPVG¤REM¤" + gn
                    sub.operator("ke.pieops", text="", icon="PANEL_CLOSE").op = "OPVG¤DEL¤" + gn

            # MAIN BOX MENU
            main.separator(factor=1)
            c = main.column(align=True)
            c.ui_units_x = 8

            if subd_mods:
                for m in subd_mods:
                    s = c.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_SUBSURF")
                    s.separator(factor=0.3)
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)
                    s.separator(factor=0.5)
                    s.prop(m, "uv_smooth", text="")
                    s.prop(m, "boundary_smooth", text="")
                    sub = s.row(align=True)
                    sub.prop(m, "use_creases", text="Crease", toggle=True)
                    sub.prop(m, "show_on_cage", text="OnCage", toggle=True)
                    c.separator(factor=0.5)
            else:
                s = c.box().column()
                if is_registered("VIEW3D_OT_ke_subd"):
                    s.operator('view3d.ke_subd', text="SubD Toggle").level_mode = "TOGGLE"
                else:
                    s.enabled = False
                    s.label(text="Subd Toggle N/A")

                c.separator(factor=0.7)

            if solidify_mods:
                for m in solidify_mods:
                    s = c.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_SOLIDIFY")
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)
                    s.separator(factor=0.5)
                    s.prop(m, "thickness", text="Thickness")
                    s.prop(m, "offset", text="Offset")
                    c.separator(factor=0.7)
                    row = s.row(align=True)
                    row.prop(m, "use_even_offset", text="Even", toggle=False)
                    row.prop(m, "use_rim", text="Rim", toggle=False)
                    row.prop(m, "use_rim_only", text="Only Rim", toggle=False)
            else:
                c.separator(factor=0.7)
                c.operator("ke.pieops", text="Add Solidify").op = "SOLIDIFY"

            c.separator(factor=0.7)

            if wn_mods:
                for m in wn_mods:
                    s = c.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_NORMALEDIT")
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)
                    s.separator(factor=0.5)
                    s.prop(m, "mode", text="")
                    s.prop(m, "thresh")
                    c.separator(factor=0.7)
                    row = s.row(align=True)
                    row.prop(m, "keep_sharp", toggle=False)
                    row.prop(m, "use_face_influence", toggle=False)
            else:
                c.separator(factor=0.7)
                c.operator("ke.pieops", text="Add Weighted Normal").op = "WEIGHTED_NORMAL"

            # BEVEL MODS
            main.separator(factor=1)
            b = main.column(align=True)
            b.ui_units_x = 9
            b.scale_y = 0.9

            if bevel_mods:
                bevm = [m for m in bevel_mods if m.limit_method == "WEIGHT"]
                for m in bevm:
                    s = b.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_BEVEL")
                    s.separator(factor=0.5)
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)

                    split = s.split(factor=0.65, align=True)
                    row = split.row(align=True)
                    row.prop_menu_enum(m, "offset_type", text="", icon="DOT")
                    row.prop(m, "width", text="")
                    split.prop(m, "segments", text="")

                    row = s.row(align=True)
                    row.prop(m, "use_clamp_overlap", text="", toggle=False)
                    row.separator(factor=0.3)
                    row.prop(m, "profile")

                    s.separator(factor=0.3)
                    row = s.row(align=True)
                    row.prop(m, "miter_outer", text="")
                    row.prop(m, "miter_inner", text="")
                    b.separator(factor=0.7)

                if not bevm:
                    b.operator("ke.pieops", text="Add Weight Bevel", icon="MOD_BEVEL").op = "W_BEVEL"
                    b.separator(factor=0.7)
            else:
                b.operator("ke.pieops", text="Add Weight Bevel", icon="MOD_BEVEL").op = "W_BEVEL"
                b.separator(factor=0.7)

            b.separator(factor=0.7)
            if bevel_mods:
                bevm = [m for m in bevel_mods if m.limit_method == "ANGLE"]
                for m in bevm:
                    s = b.box().column(align=True)
                    sub = s.row(align=True)
                    sub.label(text=m.name, icon="MOD_BEVEL")
                    s.separator(factor=0.5)
                    sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                    sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)

                    split = s.split(factor=0.65, align=True)
                    row = split.row(align=True)
                    row.prop_menu_enum(m, "offset_type", text="", icon="DOT")
                    row.prop(m, "width", text="")
                    split.prop(m, "segments", text="")

                    row = s.row(align=True)
                    row.prop(m, "use_clamp_overlap", text="", toggle=False)
                    row.separator(factor=0.3)
                    row.prop(m, "profile", text="")
                    row.prop(m, "angle_limit", text="")

                    s.separator(factor=0.3)
                    row = s.row(align=True)
                    row.prop(m, "miter_outer", text="")
                    row.prop(m, "miter_inner", text="")
                    b.separator(factor=0.7)

                if not bevm:
                    b.operator("ke.pieops", text="Add Angle Bevel", icon="MOD_BEVEL").op = "ANGLE_BEVEL"
                    b.separator(factor=0.7)
            else:
                b.operator("ke.pieops", text="Add Angle Bevel", icon="MOD_BEVEL").op = "ANGLE_BEVEL"
                b.separator(factor=0.7)

            if vertex_groups:
                used = []

                if bevel_mods:
                    bevm = [m for m in bevel_mods if m.limit_method == "VGROUP"]
                    for m in bevm:
                        s = b.box().column(align=True)
                        sub = s.row(align=True)
                        sub.label(text=m.name, icon="MOD_BEVEL")
                        s.separator(factor=0.5)
                        sub.operator("ke.pieops", text="", icon="CHECKMARK").op = "APPLY¤" + str(m.name)
                        sub.operator("ke.pieops", text="", icon="X").op = "DELETE¤" + str(m.name)

                        split = s.split(factor=0.65, align=True)
                        row = split.row(align=True)
                        row.prop_menu_enum(m, "offset_type", text="", icon="DOT")
                        row.prop(m, "width", text="")
                        split.prop(m, "segments", text="")

                        row = s.row(align=True)
                        row.prop(m, "use_clamp_overlap", text="", toggle=False)
                        row.prop(m, "profile")

                        s.separator(factor=0.3)
                        row = s.row(align=True)
                        row.prop(m, "miter_outer", text="")
                        row.prop(m, "miter_inner", text="")
                        b.separator(factor=0.7)
                        used.append(m.name)

                for group in vertex_groups:
                    n = group.name
                    if n[:3] == "V_G" and n not in used:
                        b.operator("ke.pieops", text="Add " + group.name + " Bevel",
                                   icon="MOD_BEVEL").op = "VG_BEVEL¤" + n
                        b.separator(factor=0.7)

            # TOP
            m = pie.column(align=True)
            m.ui_units_x = 7.5
            top = m.box().column(align=True)
            row = top.row(align=True)
            row.operator("ke.pieops", text="S", icon="EDITMODE_HLT").op = "SUBD_EDIT_VIS"
            row.operator("ke.pieops", text="E", icon="EDITMODE_HLT").op = "MOD_EDIT_VIS"
            row.operator("ke.pieops", text="V", icon="RESTRICT_VIEW_OFF").op = "MOD_VIS"
            top.separator(factor=0.3)
            top.prop(k, "korean", text="Korean Bevels")
            row = top.row(align=True)
            row.operator("ke.pieops", text="Flat").op = "SHADE_FLAT"
            row.operator("ke.pieops", text="Smooth").op = "SHADE_SMOOTH"

            split = top.split(align=True, factor=0.65)
            split.prop(active.data, "use_auto_smooth", text="AutoSmth", toggle=True)
            split.prop(active.data, "auto_smooth_angle", text="")

            row = top.row(align=True)
            row.operator("object.ke_object_op", text="30").cmd = "AS_30"
            row.operator("object.ke_object_op", text="45").cmd = "AS_45"
            row.operator("object.ke_object_op", text="60").cmd = "AS_60"
            row.operator("object.ke_object_op", text="180").cmd = "AS_180"
            top.separator(factor=0.3)

            row = top.row(align=True)
            if is_registered("VIEW3D_OT_ke_solo_cutter"):
                row.operator('view3d.ke_solo_cutter', text="SoloC").mode = "ALL"
                row.operator('view3d.ke_solo_cutter', text="SoloP").mode = "PRE"
            if is_registered("OBJECT_OT_ke_showcuttermod"):
                row.operator('object.ke_showcuttermod', text="SCM")

            spacer = m.column()
            spacer.label(text="")

            # Crease
            pie.operator("ke.pieops", text="Crease Weight -1").op = "CREASE_OFF"
            pie.operator("ke.pieops", text="Crease Weight 1").op = "CREASE_ON"

            # blanking SW & SE
            # pie.separator()
            # pie.separator()
        else:
            pie.separator()
            pie.separator()
            box = pie.box()
            box.label(text="[ Disabled: Requires keKit Experimental Mode ]")


classes = (
    KeCallPie,
    KeMenuEditMesh,
    KeObjectOp,
    KeOverlays,
    KePieBookmarks,
    KePieBoolTool,
    KePieFit2Grid,
    KePieFit2GridMicro,
    KePieFitPrim,
    KePieFitPrimAdd,
    KePieMaterials,
    KePieMisc,
    KePieMultiCut,
    KePieOps,
    KePieOrientPivot,
    KePieOverlays,
    KePieShading,
    KePieSnapAlign,
    KePieSnapping,
    KePieStepRotate,
    KePieSubd,
    UIPieMenusModule,
    UIPieMenusBlender,
)


addon_keymaps = []


def register():
    k = get_prefs()
    if k.m_piemenus:
        for c in classes:
            bpy.utils.register_class(c)

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if kc:
            km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
            kmi = km.keymap_items.new(idname="ke.call_pie", type='ZERO', value='PRESS', ctrl=True, alt=True, shift=True)
            kmi.properties.name = "KE_MT_shading_pie"
            addon_keymaps.append((km, kmi))


def unregister():
    if "bl_rna" in UIPieMenusModule.__dict__:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()

        for c in reversed(classes):
            bpy.utils.unregister_class(c)
