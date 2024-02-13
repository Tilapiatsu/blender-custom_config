import numpy as np
import blf
import bpy
import gpu
from bpy.props import EnumProperty
from bpy.types import Operator
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader
from .._utils import (
    get_prefs,
    get_distance,
    shift_list,
    get_scene_unit,
    get_midpoint,
    set_status_text
)
from mathutils import Vector

# Todo: Rewrite the whole thing with smarter history etc. with for_each + numpy


def mesh_world_coords(obj):
    n = len(obj.data.vertices)
    coords = np.empty((n * 3), dtype=float)
    obj.data.vertices.foreach_get("co", coords)
    # magic mtx apply
    coords = np.reshape(coords, (n, 3))
    coords4d = np.empty(shape=(n, 4), dtype=float)
    coords4d[::-1] = 1
    coords4d[:, :-1] = coords
    bb = np.einsum('ij,aj->ai', obj.matrix_world,  coords4d)[:, :-1]
    # sort bb for extremes
    bb_x = np.sort(bb[:, 0])
    bb_y = np.sort(bb[:, 1])
    bb_z = np.sort(bb[:, 2])
    return (bb_x[0], bb_y[0], bb_z[0]), (bb_x[-1], bb_y[-1], bb_z[-1])


def draw_callback_view(self, context):

    gpu.state.line_width_set(4)
    gpu.state.blend_set("ALPHA")

    if self.history:
        if self.bb_lines and self.bb_graylines and self.display[0] != "DISTANCE":
            x = batch_for_shader(self.shader, 'LINES', {"pos": self.bb_lines[0]})
            self.shader.uniform_float("color", (0.76, 0.05, 0.17, 1))
            x.draw(self.shader)

            y = batch_for_shader(self.shader, 'LINES', {"pos": self.bb_lines[1]})
            self.shader.uniform_float("color", (0.45, 0.61, 0.27, 1))
            y.draw(self.shader)

            z = batch_for_shader(self.shader, 'LINES', {"pos": self.bb_lines[2]})
            self.shader.uniform_float("color", (0.12, 0.43, 0.76, 1))
            z.draw(self.shader)

            bb = batch_for_shader(self.shader, 'LINES', {"pos": self.bb_graylines})
            self.shader.uniform_float("color", (0.65, 0.65, 0.65, .35))
            bb.draw(self.shader)

        if self.lines and self.display[0] != "BBOX":
            flat = []
            for i in self.lines:
                flat.extend((i[0], i[1]))
            batch = batch_for_shader(self.shader, 'LINES', {"pos": flat})
            self.shader.uniform_float("color", (0.3, 0.79, 0.74, 1))
            batch.draw(self.shader)


def draw_callback_px(self, context):
    # Initial offset from bottom of the screen:
    self.txt_vspace = self.fontsize[0] * 2
    lineheight = 20
    padding = 8

    def draw_textline(rgba, size, msg):
        # Centering + increasing vspacing each time
        blf.color(self.font_id, rgba[0], rgba[1], rgba[2], rgba[3])
        blf.size(self.font_id, size)
        d = blf.dimensions(self.font_id, msg)
        self.txt_vspace += (d[1] + padding)
        vpos = self.txt_vspace + lineheight
        hpos = self.screen_x - int(d[0] * 0.5) + 8
        blf.position(self.font_id, hpos, vpos, 0)
        blf.draw(self.font_id, msg)

    blf.enable(self.font_id, 4)
    blf.color(self.font_id, 0.9, 0.9, 0.9, 1)
    blf.size(self.font_id, self.fontsize[0])
    blf.shadow(self.font_id, 3, 0, 0, 0, 1)
    blf.shadow_offset(self.font_id, 2, -2)

    # Draw line stats
    if self.history:
        if self.bb_mpos and self.display[0] != "DISTANCE":
            for t, s in zip(self.bb_mpos, self.bb_lines_dist):
                if t and s:
                    blf.position(self.font_id, t[0] - self.txt_vspace * 2, t[1] - self.txt_vspace, 0)
                    blf.draw(self.font_id, s)

        if self.lines_mpos and self.display[0] != "BBOX":
            for t, s in zip(self.lines_mpos, self.lines_dist):
                if t and s:
                    blf.position(self.font_id, t[0], t[1], 0)
                    blf.draw(self.font_id, s)

    # Assemble UI txt
    ui_entries = []

    if not self.history:
        ui_entries.append((self.scol, self.fontsize[0], "[ Invalid Selection ]"))
        ui_entries.append((self.scol, self.fontsize[1], ""))
    else:
        if self.sel_freeze:
            ui_entries.append((self.scol, self.fontsize[0], "[ Freeze: Using Saved Selection (F) ]"))
            ui_entries.append((self.scol, self.fontsize[1], ""))
        if self.display[0] == "DISTANCE":
            ui_entries.append((self.hcol, self.fontsize[0], "QM - Distance Total: %s" % self.lines_tot))
        else:
            ui_entries.append((self.hcol, self.fontsize[0],
                               "QM - %s, %s, %s - Area (M) %s" % (
                                   self.bb_lines_dist[0], self.bb_lines_dist[1], self.bb_lines_dist[2], self.area)))

        ui_entries.append((self.tcol, self.fontsize[1], "Display (D): %s" % self.display[0]))
        if self.fast_calc and self.mode == "OBJECT":
            ui_entries.append((self.scol, self.fontsize[1], "[ Fast Bounds Calc Active (B) ]"))

    if self.help_mode:
        ui_help_entries = [
            (self.scol, self.fontsize[0], " "),
            (self.scol, self.fontsize[2], "Help:"),
            (self.scol, self.fontsize[2], "Change / Update Mode: (1)Verts, (2)Edges, (3)Faces, (4/TAB)Objects"),
            (self.scol, self.fontsize[2], "Stop: (Esc), (Enter), (Spacebar). Clear Sel: (C) or space-click"),
            (self.scol, self.fontsize[2], "(W/G)rab, (R)otate, (S)cale"),
            (self.scol, self.fontsize[2], "Freeze Selection: (F),  Cycle Area Modes: (M),  Cycle Display Modes: (D)"),
            (self.scol, self.fontsize[2], "Fast Object Mode Bounds Calculation Mode: (B)"),
            (self.scol, self.fontsize[2], "Note: Modifiers, (A, X, Y, Z, <) and NUMPAD are passed through"),
            (self.scol, self.fontsize[2], "Navigation: Blender(MMB) or Ind.Std(Alt-)  (H) Toggle Help")
        ]
    else:
        ui_help_entries = [
            (self.scol, self.fontsize[0], " "),
            (self.scol, self.fontsize[2], "Help (H)")
        ]
    ui_entries.extend(ui_help_entries)

    # Draw UI txt - starts from bottom with flexible "height", just reverse to keep it intuitive:
    ui_entries.reverse()
    for t in ui_entries:
        draw_textline(t[0], t[1], t[2])


class KeQuickMeasure(Operator):
    bl_idname = "view3d.ke_quickmeasure"
    bl_label = "Quick Measure"
    bl_description = "Contextual measurement types by mesh selection (Obj & Edit modes).\n" \
                     "*QM FreezeMode* starts in freeze mode."

    qm_start: EnumProperty(items=[
        ("DEFAULT", "Default Mode", "", "DEFAULT", 1),
        ("SEL_SAVE", "Selection Save Mode", "", "SEL_SAVE", 2)],
        name="Start Mode", default="DEFAULT")

    ctx = None
    sel_freeze = False
    sel_upd = False
    non_mesh = False
    mode = "OBJECT"
    component = (True, False, False)
    history = [["", []]]
    sel_edges = {}
    bb_lines = []
    bb_lines_dist = []
    bb_mpos = []
    bb_graylines = []
    lines = []
    lines_mpos = []
    lines_dist = []
    lines_tot = []
    display = ["BBOX + DISTANCE", "BBOX", "DISTANCE"]
    hcol = (1, 1, 1, 1)
    tcol = (1, 1, 1, 1)
    scol = (1, 1, 1, 1)
    fontsize = [16, 14, 12]
    txt_vspace = 0
    _handle_view = None
    _handle_px = None
    _timer = None
    screen_x = 64
    area_mode = ["XY", "XZ", "YZ"]
    area = "N/A"
    auto_update = True
    help_mode = False
    shader = None
    font_id = 0
    first_run = 0
    fast_calc = False
    rounding = 3

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return (k.qm_running is False
                and context.object is not None and context.area.type == 'VIEW_3D')

    def quit_qm(self):
        wm = self.ctx.window_manager
        wm.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle_view, 'WINDOW')
        bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
        self.ctx.area.tag_redraw()
        self.ctx.preferences.addons['kekit'].preferences.qm_running = False
        self.ctx.workspace.status_text_set(None)
        # Final Report
        print("")
        if self.bb_lines_dist:
            s = ', '.join(self.bb_lines_dist)
            print("QM Bounding Box : %s" % s)
        if self.lines_dist:
            s = ', '.join(self.lines_dist)
            print("QM Lines        : %s" % s)
            print("QM Lines Total  : %s" % self.lines_tot)

    def get_modes(self):
        self.mode = self.ctx.mode
        self.component = self.ctx.tool_settings.mesh_select_mode[:]
        # Face mode
        if self.mode != "OBJECT" and self.component[2]:
            if self.display[0] == "DISTANCE":
                self.display = shift_list(self.display, -1)

    def get_selection(self):
        sel_obj = self.ctx.selected_objects
        self.sel_edges = {}
        sel = []

        if not sel_obj:
            return sel, sel_obj

        for o in self.ctx.selected_objects:
            if self.mode == "OBJECT" or o.type != "MESH":
                sel.append([o.name, []])
            else:
                o.update_from_editmode()
                sel.append([o.name, [v.index for v in o.data.vertices if v.select]])
                self.sel_edges[o.name] = [e.index for e in o.data.edges if e.select]

        return sel, [o.name for o in sel_obj]

    def check_selection(self):
        sel, sel_obj = self.get_selection()
        # Clear old sel empty objs / selections
        clear_obj = [s[0] for s in sel if not s[1]]
        for entry in self.history:
            if entry[0] not in sel_obj:
                self.history.remove(entry)
            elif entry[0] in clear_obj:
                entry[1] = []
            else:
                newsel = [s[1] for s in sel if s[0] == entry[0]]
                if newsel:
                    for n in newsel:
                        reselected = [i for i in entry[1] if i in n]
                        if reselected:
                            entry[1] = reselected
                        else:
                            entry[1] = []

        # Create history dict for ref
        old_entries = {}
        for entry in self.history:
            if entry[0] in old_entries:
                upd = list(set(old_entries[entry[0]] + entry[1]))
                old_entries[entry[0]] = upd
            else:
                old_entries[entry[0]] = entry[1]

        # Update selection history
        for entry in sel:
            if entry[0] in old_entries:
                old = old_entries[entry[0]]
                new = [i for i in entry[1] if i not in old]
                if new:
                    self.history.append([entry[0], new])
            else:
                self.history.append(entry)

    def calc_values(self):
        self.lines, self.lines_dist, self.lines_tot = [], [], []
        # Get Coordinates
        cos, bb, = [], []

        if self.mode == "OBJECT":
            for h in self.history:
                # obj = bpy.data.objects[h[0]]
                obj = self.ctx.scene.objects[h[0]]
                if obj.type == "MESH":
                    if not self.fast_calc:
                        bb.extend(mesh_world_coords(obj))
                    else:
                        mtx = obj.matrix_world
                        for corner in obj.bound_box:
                            bb.append(mtx @ Vector(corner))
                else:
                    bb.append(obj.location)
                # for Object-2-Object Distances lines
                cos.append(obj.location)

        elif self.mode == "EDIT_MESH":
            # Verts (+ bb)
            for h in self.history:
                if h[1]:
                    obj = self.ctx.scene.objects[h[0]]
                    obj.update_from_editmode()
                    mtx = obj.matrix_world
                    for i in h[1]:
                        cos.append(mtx @ obj.data.vertices[i].co)

            bb.extend(cos)

            # Edges
            if self.component[1]:
                # Dict: No history needed for edges for QM
                for key in self.sel_edges:
                    obj = self.ctx.scene.objects[key]
                    mtx = obj.matrix_world
                    for e in self.sel_edges[key]:
                        edge = obj.data.edges[e]
                        co = []
                        for i in edge.vertices:
                            co.append(mtx @ obj.data.vertices[i].co)
                        self.lines.append(co)
        else:
            self.history = []
            self.report({"INFO"}, "Unsupported Mode")

        # Calc Bounding Box
        self.bb_calc(bb)

        # Vert pairing (line vectors) for vertex & object mode
        pairup = True
        if not self.component[0] and not self.mode == "OBJECT":
            pairup = False

        if pairup:
            if len(cos) > 1:
                # make sure lines are in pairs
                for i, j in zip(cos, cos[1:]):
                    self.lines.append([i, j])
            else:
                self.lines = []

        # Finalize for draw with unit conversion and rounding
        tot = 0
        for pair in self.lines:
            d = get_distance(pair[0], pair[1])
            tot += d
            unit = get_scene_unit(d, nearest=True)
            value = str(round(unit[1], self.rounding)) + unit[0]
            self.lines_dist.append(value)

        unit = get_scene_unit(tot, nearest=True)
        self.lines_tot = str(round(unit[1], self.rounding - 1)) + unit[0]

    def txt_calc(self, lines):
        upd = []
        if lines:
            for i in lines:
                line_mid = get_midpoint(i[0], i[1])
                tpos = location_3d_to_region_2d(self.ctx.region, self.ctx.space_data.region_3d, line_mid)
                upd.append(tpos)
        return upd

    def bb_calc(self, bb):
        # np bother
        if isinstance(bb, list):
            if not bb:
                self.bb_lines, self.bb_lines_dist, self.bb_graylines = [], [], []
                return
        elif isinstance(bb, np.ndarray):
            if not bb.any():
                self.bb_lines, self.bb_lines_dist, self.bb_graylines = [], [], []
                return

        x, y, z = [], [], []
        for i in bb:
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])
        x, y, z = sorted(x), sorted(y), sorted(z)

        self.bb_lines = [
            ((x[0], y[0], z[0]), (x[-1], y[0], z[0])),
            ((x[0], y[0], z[0]), (x[0], y[-1], z[0])),
            ((x[0], y[0], z[0]), (x[0], y[0], z[-1]))
        ]
        self.bb_graylines = [
            (x[-1], y[-1], z[-1]), (x[-1], y[-1], z[0]),
            (x[-1], y[-1], z[-1]), (x[0], y[-1], z[-1]),
            (x[-1], y[-1], z[-1]), (x[-1], y[0], z[-1]),
            (x[0], y[0], z[-1]), (x[0], y[-1], z[-1]),
            (x[0], y[-1], z[0]), (x[0], y[-1], z[-1]),
            (x[-1], y[0], z[0]), (x[-1], y[0], z[-1]),
            (x[0], y[0], z[-1]), (x[-1], y[0], z[-1]),
            (x[0], y[-1], z[0]), (x[-1], y[-1], z[0]),
            (x[-1], y[-1], z[0]), (x[-1], y[0], z[0]),
        ]
        # Area Calc & format txt
        if self.area_mode[0] == "XZ":
            unit = get_scene_unit((x[-1] - x[0]) * (z[-1] - z[0]), nearest=True)
            am = "XZ: "
        elif self.area_mode[0] == "YZ":
            unit = get_scene_unit((y[-1] - y[0]) * (z[-1] - z[0]), nearest=True)
            am = "YZ: "
        else:
            unit = get_scene_unit((x[-1] - x[0]) * (y[-1] - y[0]), nearest=True)
            am = "XY: "
        self.area = am + str(round(unit[1], self.rounding-1)) + unit[0] + "\u00b2"

        # Format bb values
        self.bb_lines_dist = []
        for i, j in zip(self.bb_lines, ("x:", "y:", "z:")):
            d = get_distance(i[0], i[1])
            unit = get_scene_unit(d, nearest=True)
            self.bb_lines_dist.append(j + str(round(unit[1], self.rounding)) + unit[0])

    def intial_update(self):
        self.get_modes()
        if len([i for i in self.component if i]) > 1:
            print("QM: More than one component mode is active: QM may not work as intended.\n"
                  "    Please use EITHER Vertex, Edge, Face (or Object mode)")
        if self.component[0] and self.mode == "EDIT_MESH":
            tot = 0
            for o in self.ctx.selected_objects:
                o.update_from_editmode()
                tot += len([v.index for v in o.data.vertices if v.select])
            if tot > 2:
                print("QM: Vertex mode selection starting with more than 2 verts cleared "
                      "to avoid garbage line results\n"
                      "    QM has vert selection history, Blender doesn't!")
                bpy.ops.view3d.select(deselect_all=True)
        self.modal_update()

    def modal_update(self):
        self.get_modes()
        self.check_selection()
        self.calc_values()
        self.ctx.area.tag_redraw()

    def invoke(self, context, event):
        k = get_prefs()
        self.hcol = k.modal_color_header
        self.tcol = k.modal_color_text
        self.scol = k.modal_color_subtext
        scale_factor = context.preferences.view.ui_scale * k.ui_scale
        self.fontsize = [int(round(n * scale_factor)) for n in self.fontsize]
        self.screen_x = int(context.region.width * .5)
        self.ctx = context
        self.history = [["", []]]

        if self.qm_start == "SEL_SAVE":
            self.sel_freeze = True

        # Auto-Set appropriate tool for selection
        bpy.ops.wm.tool_set_by_id(name="builtin.select")

        # Prep for GPU draw & run Modal
        self.shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        bpy.app.handlers.frame_change_post.clear()

        args = (self, context)
        self._handle_view = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_view, args, 'WINDOW', 'POST_VIEW')
        self._handle_px = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step=0.004, window=context.window)
        wm.modal_handler_add(self)

        self.intial_update()

        # Preset start modes
        if (self.component[0] or self.component[1]) and self.mode != "OBJECT":
            self.display = ["DISTANCE", "BBOX + DISTANCE", "BBOX"]
        else:
            # self.display = ["BBOX + DISTANCE", "BBOX", "DISTANCE"]
            self.display = ["BBOX", "DISTANCE", "BBOX + DISTANCE"]

        # UPDATE STATUS BAR
        # spacing "autodetect" skipping unicode "icons" due to text amount
        spacer_val = 4
        w = self.ctx.window.width
        if w <= 1280:
            # Some utility For 2560x1440ish half-screen blender use and lowres
            spacer_val = 1
        elif w <= 1920:
            # "Minimum" monitor res, and 4k half-screen res
            spacer_val = 2

        status_help = [
            "[1,2,3,4/TAB] Change/Update ElementMode",
            "[W/G, R, S] Grab, Rotate, Scale",
            "[F] Toggle Sel.Freeze",
            "[A] Cycle Area Mode",
            "[M] Cycle Display Mode",
            "[C] Clear Selection",
            "[B] Fast Bounds Calc Mode",
            "[H] Toggle Help",
            "[ESC/ENTER/SPACEBAR] Finish",
            "[MMB, ALT-MBs] Navigation",
        ]

        set_status_text(self.ctx, text_list=status_help, spacing=spacer_val, mb="", kb="")

        k.qm_running = True

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        #
        # Modes
        #
        if event.type in {'ONE', 'TWO', 'THREE'} and event.value == 'RELEASE':
            self.history = []
            if context.mode == "OBJECT":
                if self.sel_freeze:
                    self.sel_freeze = False
                bpy.ops.object.editmode_toggle()
            if event.type == "ONE":
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            elif event.type == "TWO":
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            elif event.type == "THREE":
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            bpy.ops.view3d.select(deselect_all=True)
            self.modal_update()

        elif event.type in {'FOUR', 'TAB'} and event.value == 'RELEASE':
            if self.sel_freeze:
                self.sel_freeze = False
            self.history = []
            bpy.ops.object.editmode_toggle()
            bpy.ops.view3d.select(deselect_all=True)
            self.modal_update()

        if self.first_run > 1:
            if event.type == 'D' and event.value == 'RELEASE':
                self.display = shift_list(self.display, -1)
                context.area.tag_redraw()

            elif event.type == 'F' and event.value == 'RELEASE':
                self.sel_freeze = not self.sel_freeze
                self.modal_update()

            elif event.type == 'H' and event.value == 'RELEASE':
                self.help_mode = not self.help_mode
                context.area.tag_redraw()

            elif event.type == 'M' and event.value == 'RELEASE':
                self.area_mode = shift_list(self.area_mode, -1)
                self.calc_values()
                context.area.tag_redraw()

            elif event.type == 'B' and event.value == 'RELEASE':
                self.fast_calc = not self.fast_calc
                self.calc_values()
                context.area.tag_redraw()
        #
        # Update
        #
        if context.area and event.type == 'TIMER':
            if context.mode not in {"OBJECT", "EDIT_MESH"}:
                self.report({"WARNING"}, "QM Cancelled: Unsupported Mode - Use 'Object' or 'Edit Mesh'")
                self.quit_qm()
                return {'FINISHED'}

            if self.history:
                # if self.sel_freeze: # calc-limit yields no noticable perf gain
                self.calc_values()
                self.ctx.area.tag_redraw()

                self.screen_x = int(self.ctx.region.width * .5)
                self.lines_mpos = self.txt_calc(self.lines)
                self.bb_mpos = self.txt_calc(self.bb_lines)

            context.area.tag_redraw()
            # silly delay for mode inputs (in case QM shortcut is also on the mode keys...)
            if self.first_run < 1:
                self.first_run += 0.1

        if context.area and self.sel_upd:
            if self.sel_freeze:
                self.calc_values()
                self.ctx.area.tag_redraw()
            else:
                self.modal_update()
            self.sel_upd = False
        #
        # Inputs
        #
        if event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                event.alt and event.type == "RIGHTMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}

        if event.type in {"LEFTMOUSE", "RIGHTMOUSE"} :
            self.sel_upd = True
            return {'PASS_THROUGH'}

        elif event.ctrl or event.alt or event.shift:
            return {'PASS_THROUGH'}

        elif event.type == 'C' and event.value == 'RELEASE':
            self.history = []
            bpy.ops.view3d.select(deselect_all=True)
            self.modal_update()

        elif event.ctrl and event.type == "Z":
            return {'RUNNING_MODAL'}

        elif event.type in {'ESC', 'RETURN', 'SPACE'}:
            self.quit_qm()
            return {'FINISHED'}

        elif event.type == 'G' or event.type == 'W':
            bpy.ops.transform.translate('INVOKE_DEFAULT')

        elif event.type == 'R':
            bpy.ops.transform.rotate('INVOKE_DEFAULT')

        elif event.type == 'S':
            bpy.ops.transform.resize('INVOKE_DEFAULT')

        elif event.type in {'X', 'Y', 'Z', 'GRLESS'}:
            return {'PASS_THROUGH'}

        elif event.type == 'A':
            self.modal_update()
            return {'PASS_THROUGH'}

        elif event.type in {'NUMPAD_PLUS', 'NUMPAD_MINUS', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4',
                            'NUMPAD_5',
                            'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        else:
            self.sel_upd = False

        return {'RUNNING_MODAL'}
