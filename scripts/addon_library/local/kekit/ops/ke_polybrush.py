import blf
import bmesh
import bpy
from addon_utils import check
from bpy.types import Operator
from mathutils.geometry import intersect_line_line
from .._utils import set_status_text, get_prefs, is_bmvert_collinear


def draw_callback_px(self, context):

    txt = "[ PolyBrush ] : " + self.txt
    bs = "\u2003" * 2  # 'blank space' spacer
    help_txt = "[SHIFT-LMB] Add Stroke %s [MMB] Close Stroke %s [RMB] Clear Strokes" % (bs, bs)

    bs = "\u2003" * 1
    if self.boolapply:
        help_txt2 = "[1-4, E, C] Tools %s [ENTER] Apply %s [SPACE] Apply & Bool %s [ESC] Cancel" % (bs, bs, bs)
    else:
        help_txt2 = "[1-4, E, C] Tools %s [ENTER] Apply %s [ESC] Cancel" % (bs, bs)

    blf.enable(self.font_id, 4)
    blf.color(self.font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
    blf.size(self.font_id, self.fontsize)
    blf.shadow(self.font_id, 3, 0, 0, 0, 1)
    blf.shadow_offset(self.font_id, 2, -2)

    # Main title line
    d = blf.dimensions(self.font_id, txt)
    hpos = self.screen_x - (int(d[0] * 0.5)) + self.fontsize
    blf.position(self.font_id, hpos, self.fontsize * 6, 0)
    blf.draw(self.font_id, txt)

    # Help line 1
    blf.color(self.font_id, self.hcol[0] * 0.85, self.hcol[1] * 0.85, self.hcol[2] * 0.85, self.hcol[3] * 0.85)
    blf.size(self.font_id, self.sm_font)
    d = blf.dimensions(self.font_id, help_txt)
    hpos = self.screen_x - (int(d[0] * 0.5)) + self.sm_font
    blf.position(self.font_id, hpos, (self.fontsize * 6) - (self.fontsize * 2), 0)
    blf.draw(self.font_id, help_txt)

    # Help line 2
    d = blf.dimensions(self.font_id, help_txt2)
    hpos = self.screen_x - (int(d[0] * 0.5)) + self.sm_font
    blf.position(self.font_id, hpos, (self.fontsize * 6) - (self.fontsize * 3.5), 0)
    blf.draw(self.font_id, help_txt2)


class KePolyBrush(Operator):
    bl_idname = "object.ke_polybrush"
    bl_label = "PolyBrush"
    bl_description = "A new version  of BoolTool PolyBrush - Requires the Bool Tool add-on\n" \
                     "Please read INSTRUCTIONS in the modal STATUS BAR & on-screen text (or wiki)"
    bl_options = {'REGISTER', 'UNDO'}

    ctx = None
    gp_obj = None
    gp_layer = None
    frame = None
    temp = []
    stage_two = False
    sel_obj = None
    new_obj = None
    restore_toolbar = False
    restore_sidebar = False
    restore_brush = []
    collection = None
    solidify_d = 1
    merge_d = 0.001
    hcol = (1, 1, 1, 1)
    fontsize = 16
    sm_font = 12
    font_id = 0
    txt = ""
    _handle_px = None
    screen_x = 64
    boolapply = False
    skip_opt = False

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D" and context.mode == "OBJECT"

    def set_draw_mode(self, activate):
        if activate:
            # Hide the ui to avoid some confusion (not usable in the modal)
            if self.ctx.space_data.show_region_toolbar:
                bpy.ops.wm.context_toggle(data_path="space_data.show_region_toolbar")
                self.restore_toolbar = True
            if self.ctx.space_data.show_region_ui:
                bpy.ops.wm.context_toggle(data_path="space_data.show_region_ui")
                self.restore_sidebar = True

            # Set Draw Mode Defaults:
            bpy.ops.object.mode_set(mode='PAINT_GPENCIL')
            self.ctx.scene.tool_settings.use_gpencil_automerge_strokes = True
            self.ctx.scene.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'
            self.ctx.scene.tool_settings.gpencil_sculpt.lock_axis = 'VIEW'
            bpy.ops.wm.tool_set_by_id(name="builtin.polyline")
            self.txt = "GPencil PolyLine (1)"
            self.skip_opt = False

            # Set (& save to restore later) brush settings
            brush = self.ctx.scene.tool_settings.gpencil_paint.brush
            self.restore_brush = [brush.size, brush.gpencil_settings.pen_strength]
            brush.size = 4
            brush.gpencil_settings.pen_strength = 1.0

        else:
            if self.restore_toolbar:
                bpy.ops.wm.context_toggle(data_path="space_data.show_region_toolbar")
            if self.restore_sidebar:
                bpy.ops.wm.context_toggle(data_path="space_data.show_region_ui")
            bpy.ops.object.mode_set(mode='OBJECT')

    def set_status_help(self, activate):
        # STATUS BAR HELP / INSTRUCTIONS
        if activate:
            spacer_val = 4
            w = self.ctx.window.width
            if w <= 1280:
                # Useful in (2560x1440) half-screen blender use
                spacer_val = 1
            elif w <= 1920:
                # "Minimum" monitor res, and 4k half-screen res
                spacer_val = 2
            status_help = [
                "[SHIFT-LMB] Add Stroke",
                "[MMB] Close Stroke",
                "[RMB] Clear Strokes",
                "[1-4] PolyLine, Box, Circle, Draw",
                "[E,C] Eraser,Cutter",
                "[ESC] Cancel",
                "[ENTER] Apply",
            ]
            if self.sel_obj is not None:
                status_help += [
                    "[SPACE] Apply +BT Diff",
                    "[ALT-SPACE] +Intrs",
                    "[SHIFT-SPACE] +Union",
                    "[CTRL-SPACE] +Slice",
                ]
            set_status_text(self.ctx, status_help, spacing=spacer_val, kb="")
        else:
            self.ctx.workspace.status_text_set(None)

    def remove_gp(self):
        # Restore brush settings
        brush = self.ctx.scene.tool_settings.gpencil_paint.brush
        brush.size = self.restore_brush[0]
        brush.gpencil_settings.pen_strength = self.restore_brush[1]
        # Remove temp gp
        self.frame.clear()
        data = self.gp_obj.data
        bpy.data.objects.remove(self.gp_obj, do_unlink=True)
        bpy.data.grease_pencils.remove(data)

    def add_gp(self):
        # Cleanup (to avoid any "left-over" issues)
        # PB is always reset/temporary to keep things (more) predictable
        if "PolyBrush" in bpy.data.grease_pencils.keys():
            bpy.data.grease_pencils.remove(bpy.data.grease_pencils["PolyBrush"])

        # Create GP & Link
        gp_data = bpy.data.grease_pencils.new("PolyBrush")
        gp_data.pixel_factor = 1
        gp_data.stroke_thickness_space = "SCREENSPACE"
        gp_data.zdepth_offset = 0.001

        self.gp_layer = gp_data.layers.new("PolyBrush", set_active=True)
        self.gp_layer.tint_color = (0, 1, 0.5)
        self.gp_layer.color = (0, 1, 0.5)
        self.gp_layer.opacity = 1
        self.gp_layer.tint_factor = 1
        self.gp_layer.line_change = 0

        self.gp_obj = bpy.data.objects.new("PolyBrush", gp_data)
        self.gp_obj.show_in_front = True
        self.ctx.scene.collection.objects.link(self.gp_obj)
        self.frame = self.gp_layer.frames.new(bpy.context.scene.frame_current)

        # Preserve Local View - edge case QoL?
        if self.ctx.space_data.local_view:
            self.gp_obj.local_view_set(self.ctx.space_data, True)

        # Set selections
        for o in self.ctx.selected_objects:
            o.select_set(False)
        self.ctx.view_layer.objects.active = self.gp_obj
        self.gp_obj.select_set(True)

    def get_sizes(self, vcos):
        x = sorted([co[0] for co in vcos])
        y = sorted([co[1] for co in vcos])
        z = sorted([co[2] for co in vcos])
        dims = sorted([x[-1] - x[0], y[-1] - y[0], z[-1] - z[0]])
        self.solidify_d = dims[1]  # = short side dim in 2d
        self.merge_d = dims[-1] * 0.0125

    def convert_to_mesh(self):
        bpy.ops.object.mode_set(mode="OBJECT")

        # New Object Data (Temp GP = only 1 layer & 1 frame)
        new_mesh = bpy.data.meshes.new(name="PixelBrushData")
        verts, edges = [], []
        for stroke in self.frame.strokes:
            for i, point in enumerate(stroke.points):
                verts.append(point.co)
                if i > 0:
                    edges.append((len(verts) - 1, len(verts) - 2))
        if not verts:
            self.report({"WARNING"}, "No GPencil data to convert - Cancelled")
            return {"CANCELLED"}
        new_mesh.from_pydata(verts, edges, ())

        # Cleanup with bmesh
        bm = bmesh.new()
        bm.from_mesh(new_mesh)

        if not self.skip_opt:
            # Remove redundant collinear verts
            to_delete = [v for v in bm.verts if is_bmvert_collinear(v, tolerance=3)]
            bmesh.ops.dissolve_verts(bm, verts=to_delete)
            bm.verts.ensure_lookup_table()
            # For easier polyline "shape-closing" - just overlap last two gpencil lines, & we sort it out here:
            x = intersect_line_line(bm.verts[1].co, bm.verts[0].co, bm.verts[-2].co, bm.verts[-1].co)
            if x:
                bm.verts[0].co = x[0]
                bm.verts[-1].co = x[1]

        # Grab sizes for solidify & remove doubles merge distance
        self.get_sizes([v.co for v in bm.verts])

        # Cleanup/simplify and create face
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=self.merge_d)
        bmesh.ops.contextual_create(bm, geom=bm.verts[:] + bm.edges[:], mat_nr=0, use_smooth=False)

        # Finalize
        bm.to_mesh(new_mesh)
        bm.free()

        # Assign obj & link to scene
        self.new_obj = bpy.data.objects.new(name="PixelBrush", object_data=new_mesh)
        self.collection.objects.link(self.new_obj)
        self.new_obj.select_set(True)
        self.ctx.view_layer.objects.active = self.new_obj
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

    def add_solidify(self, is_slice):
        mod = self.new_obj.modifiers.new("PB-Solidify", "SOLIDIFY")
        mod.offset = 0
        mod.thickness = self.solidify_d
        if is_slice:
            override = {"object": self.new_obj}
            with self.ctx.temp_override(**override):
                bpy.ops.object.modifier_apply(modifier=mod.name)

    def finalize(self, boolprep, is_slice):
        self.convert_to_mesh()
        self.set_draw_mode(False)
        self.set_status_help(False)
        self.remove_gp()
        self.add_solidify(is_slice)
        self.ctx.workspace.status_text_set(None)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
        self.ctx.area.tag_redraw()
        if boolprep:
            self.sel_obj.select_set(True)
            self.ctx.view_layer.objects.active = self.sel_obj

    def reselect_brush(self):
        bpy.ops.object.select_all(action="DESELECT")
        self.new_obj.select_set(True)
        self.ctx.view_layer.objects.active = self.new_obj

    def invoke(self, context, event):
        bt_installed = False
        if all(check("object_boolean_tools")) or all(check("bl_ext.blender_org.bool_tool")):
            bt_installed = True

        if not bt_installed:
            self.report({"INFO"}, "Cancelled: BoolTool Add-on not activated")
            return {"CANCELLED"}

        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        self.hcol = k.modal_color_header
        scale_factor = context.preferences.view.ui_scale * k.ui_scale
        self.fontsize = int(round(self.fontsize * scale_factor))
        self.sm_font = self.fontsize * 0.85
        self.screen_x = int(context.region.width * .5)
        self.temp = []
        self.ctx = context

        self.sel_obj = None
        if context.active_object:
            if context.active_object.type == "MESH":
                self.sel_obj = context.active_object

        if self.sel_obj is not None:
            self.collection = self.sel_obj.users_collection[0]
            self.boolapply = True
        else:
            self.collection = context.scene.collection
            self.boolapply = False

        self.add_gp()
        self.set_draw_mode(True)
        self.set_status_help(True)
        args = (self, context)
        self._handle_px = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        # Needs to catch CTRL-Z early, or it will crash Blender during Gpencil op.
        if event.type == "ESC" or event.ctrl and event.type == "Z":
            self.set_status_help(False)
            self.set_draw_mode(False)
            self.remove_gp()
            self.report({"INFO"}, "Poly Brush: Operation Cancelled by User")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            self.ctx.area.tag_redraw()
            return {"CANCELLED"}

        if event.type == "ONE" and event.value == "RELEASE":
            bpy.ops.wm.tool_set_by_id(name="builtin.polyline")
            self.txt = "GPencil PolyLine (1)"

            self.ctx.area.tag_redraw()

        elif event.type == "TWO" and event.value == "RELEASE":
            bpy.ops.wm.tool_set_by_id(name="builtin.box")
            self.txt = "GPencil Box (2)"
            self.ctx.area.tag_redraw()

        elif event.type == "THREE" and event.value == "RELEASE":
            bpy.ops.wm.tool_set_by_id(name="builtin.circle")
            self.txt = "Pencil Circle (3)"
            self.skip_opt = True
            self.ctx.area.tag_redraw()

        elif event.type == "FOUR" and event.value == "RELEASE":
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.Draw")
            self.txt = "GPencil Draw (4)"
            self.skip_opt = True
            self.ctx.area.tag_redraw()

        elif event.type == "E" and event.value == "RELEASE":
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.Erase")
            self.txt = "GPencil Eraser (E)"
            self.ctx.area.tag_redraw()

        elif event.type == "C" and event.value == "RELEASE":
            bpy.ops.wm.tool_set_by_id(name="builtin.cutter")
            self.txt = "GPencil Cutter (C)"
            self.ctx.area.tag_redraw()

        if event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE":
            return {"PASS_THROUGH"}

        elif event.type == "RIGHTMOUSE":
            self.frame.clear()

        if event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                event.alt and event.type == "RIGHTMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE":
            return {"PASS_THROUGH"}

        if event.type in {"RET", "NUMPAD_ENTER"}:
            self.finalize(boolprep=False, is_slice=False)
            return {"FINISHED"}

        if self.boolapply:
            # This layout seems best at catching the input variants
            if event.type == "SPACE" and event.value == "RELEASE":

                if event.alt:
                    self.finalize(boolprep=True, is_slice=False)
                    bpy.ops.btool.boolean_inters('INVOKE_DEFAULT')
                    self.reselect_brush()
                    return {"FINISHED"}

                elif event.shift:
                    self.finalize(boolprep=True, is_slice=False)
                    bpy.ops.btool.boolean_union('INVOKE_DEFAULT')
                    self.reselect_brush()
                    return {"FINISHED"}

                elif event.ctrl:
                    self.finalize(boolprep=True, is_slice=True)
                    bpy.ops.btool.boolean_slice('INVOKE_DEFAULT')
                    self.reselect_brush()
                    return {"FINISHED"}

                else:
                    self.finalize(boolprep=True, is_slice=False)
                    bpy.ops.btool.boolean_diff('INVOKE_DEFAULT')
                    self.reselect_brush()
                    return {"FINISHED"}
        else:
            if event.type == "SPACE" and event.value == "RELEASE":
                self.finalize(boolprep=False, is_slice=False)
                return {"FINISHED"}

        return {"RUNNING_MODAL"}