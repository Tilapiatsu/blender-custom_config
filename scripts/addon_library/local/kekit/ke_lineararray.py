import bpy
import blf
from bpy.props import BoolProperty
from ._utils import get_selected, get_distance, set_status_text
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import region_2d_to_location_3d


class KeLinearArray(bpy.types.Operator):
    bl_idname = "view3d.ke_lineararray"
    bl_label = "LinearArray"
    bl_description = "Creates an Array (modifier) in a line. Instances are spaced automatically between start & end\n" \
                     "(where you point the mouse) using Object rotation.\n" \
                     "Instances: Apply-Converts to link-duplicates (no modifier) - also available in modal as shortcut"
    bl_options = {'REGISTER', 'UNDO'}

    convert : BoolProperty(
        name="Convert to Instances",
        description="Applies modifier and makes array linked mesh objects automatically",
        default=False)

    _handle = None
    _handle_px = None
    _timer = None
    screen_x = 0
    region = None
    rv3d = None
    help = False
    set_pos = Vector((0, 0, 0))
    mouse_pos = Vector((0, 0))
    count = 2
    snap = False
    snapval = 0
    axis_lock = False
    imperial = []
    hcol = (1, 1, 1, 1)
    tcol = (1, 1, 1, 1)
    scol = (1, 1, 1, 1)
    fs = [64, 64, 10, 68, 20, 13, 98, 13, 45, 27, 9, 9, 10, 29, 40, 12, 45]
    tm = Matrix().to_3x3()
    axis = True, False, True
    axis_int = 1
    start_v = Vector((0, 1, 0))
    adjust_mode = False
    array = None
    obj = None
    dval = 1
    unit_scale = 1
    og_count = 2
    og_spacing = 1
    array_input_mode = False
    tick = 0
    tock = 0
    input_nrs = []
    is_gpencil = False
    offset = (0, 0, 0)
    grless_hack = False

    numbers = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE')

    def draw(self, context):
        layout = self.layout

    @classmethod
    def poll(cls, context):
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
        return context.object is not None and context.object.type in cat and context.mode == "OBJECT"

    def draw_callback_px(self, context, pos):
        hpos, vpos = self.fs[0], self.fs[1]
        if pos:
            hpos = pos - self.fs[2]
        title = ""

        if self.axis_lock:
            if self.axis_int == 2:
                title += "[Z]"
            elif self.axis_int == 1:
                title += "[Y]"
            else:
                title += "[X]"

        if self.snap:
            title += " "
            if self.snapval == 0:
                if self.imperial:
                    title += "[ft]"
                else:
                    title += "[m]"
            elif self.snapval == 1:
                if self.imperial:
                    title += "[in]"
                else:
                    title += "[dm]"
            elif self.snapval == 2:
                if self.imperial:
                    title += "[thou]"
                else:
                    title += "[cm]"
            elif self.snapval == 3:
                title += "[mm]"

        if self.count:
            font_id = 0
            blf.enable(font_id, 4)
            blf.position(font_id, hpos, vpos + self.fs[3], 0)
            blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
            blf.size(font_id, self.fs[4], 72)
            blf.shadow(font_id, 5, 0, 0, 0, 1)
            blf.shadow_offset(font_id, 1, -1)
            blf.draw(font_id, "Linear Array: " + str(self.count))
            blf.size(font_id, self.fs[5], 72)
            blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
            blf.position(font_id, hpos, vpos + self.fs[6], 0)
            blf.draw(font_id, title)
            if self.help:
                blf.size(font_id, self.fs[7], 72)
                blf.color(font_id, self.tcol[0], self.tcol[1], self.tcol[2], self.tcol[3])
                blf.position(font_id, hpos, vpos + self.fs[8], 0)
                blf.draw(font_id, "Array Count: Mouse Wheel or (0-9) Numerical Input")
                blf.position(font_id, hpos, vpos + self.fs[9], 0)
                if self.imperial:
                    blf.draw(font_id, "Grid Snap Steps: (Q) feet, (W) inches, (E) thou, (R) mm")
                else:
                    blf.draw(font_id, "Grid Snap Steps: (Q) m, (W) dm , (E) cm, (R) mm")
                blf.position(font_id, hpos, vpos + self.fs[10], 0)
                blf.draw(font_id, "Toggle Grid Snap: (Q,W,E,R) or SHIFT-TAB")
                blf.position(font_id, hpos, vpos - self.fs[11], 0)
                blf.draw(font_id, "Manual Axis Lock: (X), (Y), (Z) and (C) to release Constraint")

                blf.size(font_id, self.fs[12], 72)
                blf.color(font_id, self.scol[0], self.scol[1], self.scol[2], self.scol[3])
                blf.position(font_id, hpos, vpos - self.fs[13], 0)
                blf.draw(font_id, "Apply: Enter/Spacebar/LMB  Cancel: Esc/RMB  Instances:F")
                blf.position(font_id, hpos, vpos - self.fs[14], 0)
                blf.draw(font_id, "Navigation: Blender (-MMB) or Ind.Std (Alt-MB's)")
        else:
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            context.workspace.status_text_set(None)
            return {'CANCELLED'}

    def to_imperial(self, values):
        values = [i * self.unit_scale for i in values]
        if self.snapval == 0:
            # FEET
            return '\u0027', [(v // 0.3048) * 0.3048 for v in values]
        elif self.snapval == 1:
            # INCHES
            return '\u0022', [(v // 0.0254) * 0.0254 for v in values]
        elif self.snapval == 2:
            # THOU
            return 'thou', [(v // 0.000025) * 0.000025 for v in values]
        else:
            return 'bu', values

    def upd_array(self):
        self.array.count = self.count
        oc = self.count - 1
        if self.is_gpencil:
            self.array.constant_offset[self.axis_int] = self.dval / oc
        else:
            self.array.constant_offset_displace[self.axis_int] = self.dval / oc

    def set_snap(self, val):
        if self.snap and self.snapval == val:
            self.snap = False
        else:
            self.snapval = val
            self.snap = True

    def remove_modal(self, context):
        context.area.tag_redraw()
        context.window_manager.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
        context.workspace.status_text_set(None)

    def to_instances(self):
        count = self.count - 1
        if count:
            offsetval = Vector(self.array.constant_offset_displace)
            mtx = self.obj.matrix_world.to_3x3()
            bpy.ops.object.modifier_remove(modifier=self.array.name)
            for i in range(1, self.count):
                bpy.ops.object.duplicate_move_linked(
                    OBJECT_OT_duplicate={"linked": True, "mode": 'TRANSLATION'},
                    TRANSFORM_OT_translate={"value": offsetval,
                                            "orient_type": 'LOCAL',
                                            "orient_matrix": mtx,
                                            "orient_matrix_type": 'LOCAL',
                                            "mirror": False, "use_proportional_edit": False})

    def invoke(self, context, event):
        # INITIAL EVENT INFO & SETTINGS
        k = context.preferences.addons[__package__].preferences
        self.hcol = k.modal_color_header
        self.tcol = k.modal_color_text
        self.scol = k.modal_color_subtext

        scale_factor = context.preferences.view.ui_scale * k.ui_scale
        self.fs = [int(round(n * scale_factor)) for n in self.fs]

        self.imperial = bpy.context.scene.unit_settings.system
        self.unit_scale = bpy.context.scene.unit_settings.scale_length

        if self.imperial != 'IMPERIAL':
            self.imperial = []

        self.region = context.region
        self.rv3d = context.space_data.region_3d
        self.screen_x = int(self.region.width * 0.5)
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)

        return self.execute(context)

    def execute(self, context):
        # SELECTION
        self.obj = get_selected(context, use_cat=True)
        if not self.obj:
            self.report({"INFO"}, "No valid Object selected?")
            return {'CANCELLED'}

        # SETUP
        bpy.ops.wm.tool_set_by_id(name="builtin.select")
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        self.set_pos = self.obj.location.copy()
        self.tm = self.obj.matrix_world.copy()
        if self.obj.type == "GPENCIL":
            self.is_gpencil = True
        # initial mouse vector
        mp = region_2d_to_location_3d(self.region, self.rv3d, self.mouse_pos, self.set_pos)
        self.start_v = Vector((self.tm.inverted() @ self.set_pos) - (self.tm.inverted() @ mp)).normalized()

        # CHECK OBJECT FOR ADJUSTMENT MODE
        if self.is_gpencil:
            mods = self.obj.grease_pencil_modifiers
        else:
            mods = self.obj.modifiers

        for m in mods:
            if "Linear Array" in m.name:
                self.array = m
                self.count = int(self.array.count)
                self.og_count = int(self.array.count)
                if not self.is_gpencil:
                    self.og_spacing = self.array.constant_offset_displace[:]
                else:
                    self.og_spacing = self.array.constant_offset[:]
                self.adjust_mode = True
                # spacing & axis will be instantly recalculated in modal
                break

        # NEW SETUP
        if not self.adjust_mode:
            # CREATE ARRAY MODIFIER
            if self.is_gpencil:
                self.array = self.obj.grease_pencil_modifiers.new("Linear Array", 'GP_ARRAY')
            else:
                self.array = self.obj.modifiers.new("Linear Array", 'ARRAY')

            self.offset = (0, 0, 0)
            self.array.use_relative_offset = False
            self.array.use_constant_offset = True
            self.array.count = 2

        if not self.array:
            print("Linear Array: No Array Found")
            return {"CANCELLED"}

        # GO MODAL
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)
        args = (context, self.screen_x)
        self._handle_px = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        # UPDATE STATUS BAR
        status_help = [
            "[WHEEL] Count",
            "[0-9] Num.Input",
            "[Q,W,E,R] Toggle/Grid Snap Lvl",
            "[X,Y/<,Z] Axis Lock",
            "[F] Convert to Instances",
            "[C] Release lock",
            "[MMB, ALT-MB] Blender or Ind.Std Nav",
            "[ENTER/SPACEBAR/LMB] Apply",
            "[ESC/RMB] Cancel",
            "[H] Toggle Help"]
        set_status_text(context, status_help)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # LINUX GRLESS HACK (will use ANY "unrecognized" key as grless)
        if not event.type:
            self.grless_hack = True
        #
        # STEPVALUES OR NUMERICAL MODE
        #
        if event.type == 'TIMER':
            self.tick += 1

        if event.type in self.numbers and event.value == 'PRESS':
            nr = self.numbers.index(event.type)
            self.input_nrs.append(nr)
            self.tock = int(self.tick)

        if self.tick - self.tock >= 1:
            nrs = len(self.input_nrs)
            if nrs != 0:
                if nrs == 3:
                    val = (self.input_nrs[0] * 100) + (self.input_nrs[1] * 10) + self.input_nrs[2]
                elif nrs == 2:
                    val = (self.input_nrs[0] * 10) + self.input_nrs[1]
                else:
                    val = self.input_nrs[0]

                if val < 2:
                    val = 2
                self.count = val
                self.upd_array()
                self.input_nrs = []
                context.area.tag_redraw()

        if event.type == 'Q' and event.value == 'PRESS':
            self.set_snap(0)

        elif event.type == 'W' and event.value == 'PRESS':
            self.set_snap(1)

        elif event.type == 'E' and event.value == 'PRESS':
            self.set_snap(2)

        elif event.type == 'R' and event.value == 'PRESS':
            self.set_snap(3)

        #
        # MAIN
        #
        if event.type == 'MOUSEMOVE':
            new_mouse_pos = Vector((int(event.mouse_region_x), int(event.mouse_region_y)))
            newpos = region_2d_to_location_3d(self.region, self.rv3d, new_mouse_pos, self.set_pos)

            if self.snap:
                if self.imperial:
                    newpos = self.to_imperial(newpos, self.snapval, self.unit_scale)[1]
                else:
                    newpos = Vector(
                        (round(newpos[0], self.snapval),
                         round(newpos[1], self.snapval),
                         round(newpos[2], self.snapval)))

            # CHECK AXIS VECTOR CHANGE
            v1, v2 = self.tm.inverted() @ newpos, self.tm.inverted() @ self.set_pos

            if not self.axis_lock:
                v = Vector((v2 - v1)).normalized()

                if abs(v.dot(self.start_v)) > 0.3:
                    x, y, z = abs(v[0]), abs(v[1]), abs(v[2])
                    if x > y and x > z:
                        self.axis = False, True, True
                        self.axis_int = 0
                    elif y > x and y > z:
                        self.axis = True, False, True
                        self.axis_int = 1
                    else:
                        self.axis = True, True, False
                        self.axis_int = 2

                    # Reset for update constraint axis
                    if self.is_gpencil:
                        self.array.constant_offset = (0, 0, 0)
                    else:
                        self.array.constant_offset_displace = (0, 0, 0)

            # UPDATE OFFSET OBJ PO
            self.dval = get_distance(newpos, self.set_pos)
            if v1[self.axis_int] < v2[self.axis_int] :
                self.dval *= -1
            self.upd_array()

        #
        # WHEEL COUNT UPDATE
        #
        elif event.type == 'WHEELUPMOUSE':
            self.count += 1
            context.area.tag_redraw()
            self.upd_array()

        elif event.type == 'WHEELDOWNMOUSE' and self.count > 2:
            self.count -= 1
            context.area.tag_redraw()
            self.upd_array()

        #
        # NAV
        #
        if event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                event.alt and event.type == "RIGHTMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}

        #
        # MISC HOTKEYS
        #
        elif event.shift and event.type == 'TAB' and event.value == 'PRESS':
            self.snap = not self.snap

        elif event.type == 'H' and event.value == 'PRESS':
            self.help = not self.help
            context.area.tag_redraw()

        elif event.type == 'X' and event.value == 'PRESS':
            self.axis_lock = True
            self.axis = False, True, True
            self.axis_int = 0
            context.area.tag_redraw()
            self.offset = (0, 0, 0)
            self.upd_array()

        elif self.grless_hack or event.type in {'Y', 'GRLESS'} and event.value == 'PRESS':
            self.grless_hack = False
            self.axis_lock = True
            self.axis = True, False, True
            self.axis_int = 1
            context.area.tag_redraw()
            self.offset = (0, 0, 0)
            self.upd_array()

        elif event.type == 'Z' and event.value == 'PRESS':
            self.axis_lock = True
            self.axis = True, True, False
            self.axis_int = 2
            context.area.tag_redraw()
            if self.is_gpencil:
                self.array.constant_offset = (0, 0, 0)
            else:
                self.array.constant_offset_displace = (0, 0, 0)
            self.upd_array()

        elif event.type == 'C' and event.value == 'PRESS':
            self.axis_lock = False
            context.area.tag_redraw()

        #
        # APPLY
        #
        elif event.type in {'RET', 'SPACE'} or event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.remove_modal(context)
            if self.convert:
                self.to_instances()
            return {'FINISHED'}

        elif event.type == "F" and event.value == 'PRESS':
            self.remove_modal(context)
            self.to_instances()
            return {"FINISHED"}
        #
        # CANCEL
        #
        elif event.type == 'ESC' or event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            self.remove_modal(context)
            if not self.adjust_mode:
                bpy.ops.object.modifier_remove(modifier=self.array.name)
            else:
                self.array.count = self.og_count
                if self.is_gpencil:
                    self.array.constant_offset = (0, 0, 0)
                else:
                    self.array.constant_offset_displace = (0, 0, 0)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


#
# CLASS REGISTRATION
#
def register():
    bpy.utils.register_class(KeLinearArray)


def unregister():
    bpy.utils.unregister_class(KeLinearArray)
