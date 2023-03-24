import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector
from ._utils import get_distance, get_midpoint, get_scene_unit, chunk, set_status_text


def bb(self, context):
    self.stat = []
    self.sizes = []
    x, y, z = [], [], []
    for i in self.vpos:
        x.append(i[0])
        y.append(i[1])
        z.append(i[2])
    x, y, z = sorted(x), sorted(y), sorted(z)

    if len(x) > 1:  # any coords
        # XY, XZ, YZ
        if self.area_mode[1]:
            unit = get_scene_unit((x[-1] - x[0]) * (z[-1] - z[0]), nearest=True)
            am = "Area XZ:"
        elif self.area_mode[2]:
            unit = get_scene_unit((y[-1] - y[0]) * (z[-1] - z[0]), nearest=True)
            am = "Area YZ:"
        else:
            unit = get_scene_unit((x[-1] - x[0]) * (y[-1] - y[0]), nearest=True)
            am = "Area XY:"
        self.area = am + str(round(unit[1], 2)) + unit[0] + "\u00b2"

    self.lines = [
        ((x[0], y[0], z[0]), (x[0], y[0], z[-1])),
        ((x[0], y[0], z[0]), (x[-1], y[0], z[0])),
        ((x[0], y[0], z[0]), (x[0], y[-1], z[0]))
    ]
    self.bb_lines = [
        ((x[-1], y[-1], z[-1]), (x[-1], y[-1], z[0])),
        ((x[-1], y[-1], z[-1]), (x[0], y[-1], z[-1])),
        ((x[-1], y[-1], z[-1]), (x[-1], y[0], z[-1])),
        ((x[0], y[0], z[-1]), (x[0], y[-1], z[-1])),
        ((x[0], y[-1], z[0]), (x[0], y[-1], z[-1])),
        ((x[-1], y[0], z[0]), (x[-1], y[0], z[-1])),
        ((x[0], y[0], z[-1]), (x[-1], y[0], z[-1])),
        ((x[0], y[-1], z[0]), (x[-1], y[-1], z[0])),
        ((x[-1], y[-1], z[0]), (x[-1], y[0], z[0])),
    ]
    for i in self.lines:
        d = get_distance(i[0], i[1])
        self.sizes.append(d)
        unit = get_scene_unit(d, nearest=True)
        value = str(round(unit[1], 4)) + unit[0]
        self.stat.append(value)


def sel_check(self, context, sel_save_check=False):
    self.edit_mode = context.tool_settings.mesh_select_mode[:]
    self.vpos = []
    self.lines = []
    self.stat = []
    self.bb_lines = []
    if context.mode == "OBJECT":
        self.obj_mode = True
    else:
        self.obj_mode = False

    # grab each mesh object (and maybe store in sel_save_obj) ------------------------------------------------------
    if self.sel_save_mode and not sel_save_check:
        sel_obj = self.sel_save_obj
    elif sel_save_check:
        sel_obj = [obj for obj in context.selected_objects if obj.type == "MESH"]
        self.sel_save_obj = sel_obj
    else:
        sel_obj = [obj for obj in context.selected_objects if obj.type == "MESH"]

    if sel_obj:
        self.snapobj = sel_obj[0]

    # store one list of vert indices per obj in sel_save -----------------------------------------------------------
    sel_verts = []
    obj_precalc = False

    if not self.sel_save_mode or sel_save_check:
        # just using the bounds for object mode calc, for speed.
        if self.obj_mode:
            for obj in sel_obj:
                self.vpos.extend([obj.matrix_world @ Vector(co) for co in obj.bound_box])
                obj_precalc = True
        else:
            for obj in sel_obj:
                obj.update_from_editmode()
                if self.edit_mode[1]:  # to ensure correct vert pairs for edge mode
                    verts = []
                    edges = [e for e in obj.data.edges if e.select]
                    if edges:
                        for e in edges:
                            verts.extend([v for v in e.vertices])
                else:
                    verts = [v.index for v in obj.data.vertices if v.select]
                sel_verts.append(verts)

    if sel_save_check:
        self.sel_save = sel_verts

    if self.sel_save_mode or obj_precalc:
        sel_verts = self.sel_save
        if self.obj_mode:
            for obj in sel_obj:
                self.vpos.extend([obj.matrix_world @ Vector(co) for co in obj.bound_box])
            if self.vpos:
                obj_precalc = True

    # Process indices for coordinates --------------------------------------------------------------------
    if sel_verts and not obj_precalc:
        for indices, obj in zip(sel_verts, sel_obj):
            obj.update_from_editmode()
            self.vpos.extend([obj.matrix_world @ obj.data.vertices[v].co for v in indices])

    if context.mode == "EDIT_MESH" and self.vpos:
        convert_stats = False
        if self.edit_mode[0] and sel_verts:

            if self.sel_save_mode and self.vertmode == "Distance" and len(self.vpos) > 1:
                self.stat = [round(get_distance(self.vpos[0], self.vpos[1]), 4)]
                self.lines = [(self.vpos[0], self.vpos[1])]
                convert_stats = True

            elif not self.sel_save_mode and self.vertmode == "Distance":
                if len(self.vpos) > 0:
                    if len(self.vpos) == 1:
                        new = self.vpos
                    else:
                        new = [pos for pos in self.vpos if pos not in self.vert_history[1:]]
                    self.vert_history.extend(new)
                else:
                    self.vert_history = []

                if self.vertmode == "Distance" and len(self.vert_history) > 1:
                    vl = self.vert_history

                    if len(vl) % 2 != 0:
                        exv = vl[-2]
                        vl.insert(-2, exv)

                    vps = chunk(vl, 2)
                    self.lines = vps
                    for vp in vps:
                        d = round(get_distance(vp[0], vp[1]), 4)
                        self.stat.append(d)

                    convert_stats = True
                else:
                    self.lines = None

            elif self.vertmode == "BBox" and len(self.vpos) > 1:
                bb(self, context)
            else:
                self.lines = None

        elif self.edit_mode[1]:
            convert_stats = True
            self.vert_history = []
            vps = chunk(self.vpos, 2)
            self.lines = vps
            for vp in vps:
                d = round(get_distance(vp[0], vp[1]), 4)
                self.stat.append(d)

        elif self.edit_mode[2]:
            self.vert_history = []
            if len(self.vpos) < 3:
                self.lines = None
            else:
                bb(self, context)

        if convert_stats:
            # Total distance calc
            unit, value = get_scene_unit(sum(self.stat), nearest=True)
            self.dtot = str(value) + unit

            # unit conversion
            conv = []
            for s in self.stat:
                u, v = get_scene_unit(s, nearest=True)
                conv.append(str(v) + u)
            self.stat = conv

    else:  # OBJECT MODE
        if self.vpos:
            bb(self, context)


def txt_calc(self, context):
    upd = []
    for i in self.lines:
        line_mid = get_midpoint(i[0], i[1])
        tpos = location_3d_to_region_2d(context.region, context.space_data.region_3d, line_mid)
        upd.append(tpos)
    self.txt_pos = upd


def draw_callback_view(self, context):
    if self.lines:
        glines = []
        bblines = []
        if self.edit_mode[2] or self.obj_mode or self.vertmode == "BBox":
            for i in self.bb_lines:
                bblines.extend((i[0], i[1]))

        for i in self.lines:
            if bblines:
                glines.append((i[0], i[1]))
            else:
                glines.extend((i[0], i[1]))

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        gpu.state.line_width_set(3)
        gpu.state.blend_set("ALPHA")

        if bblines:
            z = batch_for_shader(shader, 'LINES', {"pos": glines[0]})
            shader.bind()
            shader.uniform_float("color", (0.12, 0.43, 0.76, 1))
            z.draw(shader)

            x = batch_for_shader(shader, 'LINES', {"pos": glines[1]})
            shader.bind()
            shader.uniform_float("color", (0.83, 0.05, 0.17, 1))
            x.draw(shader)

            y = batch_for_shader(shader, 'LINES', {"pos": glines[2]})
            shader.bind()
            shader.uniform_float("color", (0.45, 0.61, 0.27, 1))
            y.draw(shader)

            batch = batch_for_shader(shader, 'LINES', {"pos": bblines})
            shader.bind()
            shader.uniform_float("color", (0.65, 0.65, 0.65, .4))
            batch.draw(shader)

        else:
            batch = batch_for_shader(shader, 'LINES', {"pos": glines})
            shader.bind()
            shader.uniform_float("color", (0.3, 0.79, 0.74, 1))
            batch.draw(shader)


def draw_callback_px(self, context):
    font_id = 0
    if self.user_axis == 1:
        ua = "Y"
    elif self.user_axis == 0:
        ua = "X"
    else:
        ua = "Z"

    if self.lines and self.txt_pos and self.stat:
        # draw stats
        count = 0
        blf.enable(font_id, 4)
        blf.size(font_id, self.ui[0], 72)
        blf.color(font_id, 0.9, 0.9, 0.9, 1)
        blf.shadow(font_id, 3, 0, 0, 0, 1)
        blf.shadow_offset(font_id, 1, -1)

        for t, s in zip(self.txt_pos, self.stat):
            if t is not None:
                blf.position(font_id, t[0], t[1], 0)

                if self.obj_mode:
                    if count == 0:
                        axis = "z:"
                    elif count == 1:
                        axis = "x:"
                    else:
                        axis = "y:"
                    s = axis + str(s)
                    blf.draw(font_id, s)

                elif not self.obj_mode:
                    if self.edit_mode[0] and self.vertmode == "BBox" or self.edit_mode[2]:
                        if count == 0:
                            axis = "z:"
                        elif count == 1:
                            axis = "x:"
                        else:
                            axis = "y:"
                        s = axis + str(s)
                        blf.draw(font_id, s)

                    elif self.edit_mode[0] and self.vertmode == "Distance" or self.edit_mode[1]:
                        blf.draw(font_id, s)
                else:
                    blf.draw(font_id, str(s))

                count += 1

    # Selection Info
    hpos, vpos = self.screen_x - self.ui[18], self.ui[19]
    blf.shadow(font_id, 5, 0, 0, 0, 1)
    blf.shadow_offset(font_id, 1, -1)

    if not self.help_mode:
        hoff = self.ui[1]
    else:
        hoff = 0

    if self.edit_mode[0] and not self.obj_mode:
        vmode = self.vertmode
    else:
        vmode = ""

    if not self.lines:
        blf.color(font_id, self.scol[0], self.scol[1], self.scol[2], self.scol[3])
        blf.size(font_id, self.ui[2], 72)
        blf.position(font_id, hpos, vpos + self.ui[3] - hoff, 0)
        blf.draw(font_id, "[ Invalid Selection ] %s" % vmode)
    else:
        if self.sel_save_mode:
            blf.color(font_id, self.scol[0], self.scol[1], self.scol[2], self.scol[3])
            blf.size(font_id, self.ui[4], 72)
            blf.position(font_id, hpos, vpos + self.ui[5] - hoff, 0)
            blf.draw(font_id, "[ --- Using Saved Selection (F)--- ] %s" % vmode)

        blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
        blf.size(font_id, self.ui[6], 72)
        blf.position(font_id, hpos, vpos + self.ui[7] - hoff, 0)
        if self.edit_mode[1] and not self.obj_mode:
            blf.draw(font_id, "Quick Measure [Total: %s]" % self.dtot)
        elif self.edit_mode[0] and not self.obj_mode:
            if self.vertmode == "Distance":
                blf.draw(font_id, "Quick Measure Mode (V): %s ['C' to Clear Selection] [Total: %s]"
                         % (self.vertmode, self.dtot))
            else:
                blf.draw(font_id, "Quick Measure Mode (V): %s [%s]" % (self.vertmode, self.area))
        else:
            blf.draw(font_id, "Quick Measure [%s]" % self.area)

    # Instructions
    blf.color(font_id, self.tcol[0], self.tcol[1], self.tcol[2], self.tcol[3])
    blf.size(font_id, self.ui[8], 72)

    if self.help_mode:
        blf.position(font_id, hpos, vpos + self.ui[9], 0)
        blf.draw(font_id, "Change / Update Mode: (1)Verts, (2)Edges, (3)Faces, (4)Objects")
        blf.position(font_id, hpos, vpos + self.ui[10], 0)
        if self.edit_mode[0]:
            blf.draw(font_id, "Stop: (Esc), (Enter), (Spacebar). Toggle Vert Mode: (V)  Clear Sel: (C) or space-click")
        else:
            blf.draw(font_id, "Stop: (Esc), (Enter), (Spacebar)")

        blf.position(font_id, hpos, vpos + self.ui[11], 0)
        blf.draw(font_id, "(W/G)rab, (R)otate, (S)cale")
        blf.position(font_id, hpos, vpos + self.ui[12], 0)
        blf.draw(font_id, "Freeze Selection: (F) Toggle    Area: (A) Cycle")
        blf.position(font_id, hpos, vpos - self.ui[13], 0)
        blf.draw(font_id, "Round-Snap: (T) By %s-Axis(M). Unit-scale:%s(N). Round-Snap All Axis (B)."
                 % (ua, self.unit_size))

        blf.color(font_id, self.scol[0], self.scol[1], self.scol[2], self.scol[3])
        blf.size(font_id, self.ui[14], 72)
        blf.position(font_id, hpos, vpos - self.ui[15], 0)
        blf.draw(font_id, "Navigation: Blender(MMB) or Ind.Std(Alt-) & (TAB) toggles mode. (H) Toggle Help")


def snapscale(self, context, all_axis=False):
    if self.edit_mode[2]:
        temp_emode = False
        # re-order the sizes because im apparently making things needlessly convoluted...
        z = self.sizes.pop(0)
        self.sizes.append(z)

        other_axis = [0, 1, 2]
        other_axis.pop(self.user_axis)

        # calculate rounded values
        if not all_axis:
            size = self.sizes[self.user_axis]
            user_value = round(size, 2)
        else:
            user_value = (round(self.sizes[0], 2), round(self.sizes[1], 2), round(self.sizes[2], 2))

        if context.mode == "OBJECT":  # QnD indeed...
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            temp_emode = True

        if all_axis:
            nx = user_value[0] / self.sizes[0]
            ny = user_value[1] / self.sizes[1]
            nz = user_value[2] / self.sizes[2]
            new_dimensions = (nx, ny, nz)
        else:
            edit_val = user_value / self.sizes[self.user_axis]
            new_dimensions = [edit_val, edit_val, edit_val]

            if not self.unit_size:
                new_dimensions[other_axis[0]] = 1
                new_dimensions[other_axis[1]] = 1

        bpy.ops.transform.resize(value=new_dimensions, orient_type='GLOBAL', orient_matrix_type='GLOBAL',
                                 constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False,
                                 use_proportional_connected=False, use_proportional_projected=False, snap=False,
                                 gpencil_strokes=False, texture_space=False, remove_on_cancel=False,
                                 release_confirm=False)
        if temp_emode:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode="OBJECT")


class KeQuickMeasure(bpy.types.Operator):
    bl_idname = "view3d.ke_quickmeasure"
    bl_label = "Quick Measure"
    bl_description = "Contextual measurement types by mesh selection (Obj & Edit modes).\n" \
                     "*QM FreezeMode* starts in freeze mode."

    qm_start: bpy.props.EnumProperty(
        items=[("DEFAULT", "Default Mode", "", "DEFAULT", 1),
               ("SEL_SAVE", "Selection Save Mode", "", "SEL_SAVE", 2),
               ], name="Start Mode", default="DEFAULT")

    @classmethod
    def poll(cls, context):
        return (context.preferences.addons[__package__].preferences.qm_running is False
                and context.object is not None
                and context.object.type == 'MESH')

    _handle = None
    _handle_px = None
    _timer = None
    lines = None
    bb_lines = None
    txt_pos = []
    vpos = None
    vpairs = None
    edit_mode = None
    obj_mode = False
    stat = "Stat Info"
    dtot = ""
    screen_x = 64
    vertmode = "Distance"
    area = "N/A"
    area_mode = [True, False, False]  # XY, XZ, YZ
    auto_update = True
    sel_upd = False
    sel_save_mode = False
    sel_save = []
    sel_save_obj = []
    help_mode = False
    vert_history = []

    unit_size = False
    user_axis = 2
    sizes = []
    snapobj = []

    hcol = (1, 1, 1, 1)
    tcol = (1, 1, 1, 1)
    scol = (1, 1, 1, 1)
    ui = [14, 72, 15, 106, 15, 134, 20, 106, 15, 78, 56, 36, 16, 4, 12, 24, 15, 78, 100, 64]

    def invoke(self, context, event):
        k = context.preferences.addons[__package__].preferences
        self.hcol = k.modal_color_header
        self.tcol = k.modal_color_text
        self.scol = k.modal_color_subtext
        scale_factor = context.preferences.view.ui_scale * k.ui_scale
        self.ui = [int(round(n * scale_factor)) for n in self.ui]
        self.auto_update = k.quickmeasure

        bpy.ops.wm.tool_set_by_id(name="builtin.select")
        active_obj = context.active_object
        sel_obj = [obj for obj in context.selected_objects if obj.type == "MESH"]

        # Make sure active obj is selected
        if len(sel_obj) == 0 and active_obj:
            if active_obj.type == "MESH":
                active_obj.select_set(state=True)
                sel_obj = active_obj

        if not sel_obj:
            self.report({'WARNING'}, "No mesh object selected.")
            print("Cancelled: No mesh object selected.")
            return {'CANCELLED'}

        bpy.app.handlers.frame_change_post.clear()
        sel_check(self, context, sel_save_check=True)

        if context.area.type == 'VIEW_3D':
            if self.qm_start == "SEL_SAVE":
                self.sel_save_mode = True

            self.screen_x = int(context.region.width * .5)

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_view, args, 'WINDOW', 'POST_VIEW')
            self._handle_px = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            wm = context.window_manager
            self._timer = wm.event_timer_add(time_step=0.02, window=context.window)
            wm.modal_handler_add(self)

            context.area.tag_redraw()
            k.qm_running = True

            # UPDATE STATUS BAR
            status_help = [
                "[1,2,3,4] Change/Update ElementMode",
                "[W/G, R, S] Grab, Rotate, Scale",
                "[F] Toggle Sel.Freeze",
                "[A] Area Cycle",
                "[V] Toggle VertMode",
                "[C] Clear Selection",
                "[MMB, ALT-MBs] Navigation",
                "[ESC/ENTER/SPACEBAR] Finish",
                "[H] Toggle Help"]
            set_status_text(context, status_help)
            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            print("Cancelled: No suitable viewport found")
            k.qm_running = False
            return {'CANCELLED'}

    def modal(self, context, event):
        if event.type in {'ONE', 'TWO', 'THREE'} and event.value == 'RELEASE':
            if context.mode == "OBJECT":
                bpy.ops.object.editmode_toggle()
            if event.type == "ONE":
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                bpy.ops.view3d.select(deselect_all=True)
            elif event.type == "TWO":
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            elif event.type == "THREE":
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            self.vert_history = []
            sel_check(self, context)
            context.area.tag_redraw()

        elif event.type in {'FOUR', 'TAB'} and event.value == 'RELEASE':
            bpy.ops.object.editmode_toggle()
            sel_check(self, context)
            context.area.tag_redraw()

        if event.type == 'V' and event.value == 'RELEASE':
            if self.vertmode == "Distance":
                self.vertmode = "BBox"
            else:
                self.vertmode = "Distance"
            self.vert_history = []
            sel_check(self, context)
            context.area.tag_redraw()

        elif event.type == 'C' and event.value == 'RELEASE':
            bpy.ops.view3d.select(deselect_all=True)
            self.vert_history = []
            sel_check(self, context)

        if context.area and self.sel_upd:
            if self.auto_update:
                sel_check(self, context)
            elif context.mode == "OBJECT":
                sel_check(self, context)
            if not self.sel_save_mode:
                self.sel_upd = False
            context.area.tag_redraw()

        if self.lines and context.area and event.type == 'TIMER':
            if self.sel_save_mode:
                sel_check(self, context)
            txt_calc(self, context)
            context.area.tag_redraw()

        if event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                event.alt and event.type == "RIGHTMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}

        elif event.ctrl and event.type == "Z":
            return {'RUNNING_MODAL'}

        elif event.type == 'F' and event.value == 'RELEASE':
            self.sel_save_mode = not self.sel_save_mode
            if self.sel_save_mode:
                sel_check(self, context, sel_save_check=True)
            context.area.tag_redraw()

        elif event.type == 'H' and event.value == 'RELEASE':
            self.help_mode = not self.help_mode
            context.area.tag_redraw()

        elif event.type in {'ESC', 'RETURN', 'SPACE'}:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            context.area.tag_redraw()
            context.preferences.addons['kekit'].preferences.qm_running = False
            context.workspace.status_text_set(None)
            return {'FINISHED'}

        elif event.type == "LEFTMOUSE" or event.type == "RIGHTMOUSE":
            self.sel_upd = True
            return {'PASS_THROUGH'}

        elif event.ctrl or event.alt:
            return {'PASS_THROUGH'}

        elif event.shift and not self.edit_mode[0] and not self.obj_mode and self.vertmode != "Distance":
            return {'PASS_THROUGH'}

        elif event.type == 'G' or event.type == 'W':
            bpy.ops.transform.translate('INVOKE_DEFAULT')

        elif event.type == 'R':
            bpy.ops.transform.rotate('INVOKE_DEFAULT')

        elif event.type == 'S':
            bpy.ops.transform.resize('INVOKE_DEFAULT')

        elif event.type in {'X', 'Y', 'Z', 'GRLESS'}:
            return {'PASS_THROUGH'}

        elif event.type == 'A' and event.value == 'RELEASE':
            if self.area_mode[0]:
                self.area_mode[0], self.area_mode[1], self.area_mode[2] = False, True, False
            elif self.area_mode[1]:
                self.area_mode[0], self.area_mode[1], self.area_mode[2] = False, False, True
            elif self.area_mode[2]:
                self.area_mode[0], self.area_mode[1], self.area_mode[2] = True, False, False
            sel_check(self, context)
            context.area.tag_redraw()

        elif event.type in {'NUMPAD_PLUS', 'NUMPAD_MINUS', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5',
                            'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        elif event.type == 'T' and event.value == 'RELEASE':
            snapscale(self, context, all_axis=False)
            sel_check(self, context)

        elif event.type == 'N' and event.value == 'RELEASE':
            self.unit_size = not self.unit_size

        elif event.type == 'B' and event.value == 'RELEASE':
            snapscale(self, context, all_axis=True)
            sel_check(self, context)

        elif event.type == 'M' and event.value == 'RELEASE':
            if self.user_axis == 0:
                self.user_axis = 1
            elif self.user_axis == 1:
                self.user_axis = 2
            elif self.user_axis == 2:
                self.user_axis = 0

        else:
            self.sel_upd = False

        return {'RUNNING_MODAL'}


#
# CLASS REGISTRATION
#
classes = (KeQuickMeasure,)

modules = ()


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
