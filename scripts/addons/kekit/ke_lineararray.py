bl_info = {
    "name": "keLinearArray",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (2, 0, 2),
    "blender": (2, 80, 0),
}

import bpy
import blf
from .ke_utils import get_selected, get_distance
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import region_2d_to_location_3d


class VIEW3D_OT_ke_lineararray(bpy.types.Operator):
    bl_idname = "view3d.ke_lineararray"
    bl_label = "Linear Array"
    bl_description = "Creates an array in a line where instances are spaced automatically between start and end " \
                     "(where you point the mouse) using Object rotation. Scale will be applied."
    bl_options = {'REGISTER', 'UNDO'}

    _handle = None
    _handle_px = None
    _timer = None
    screen_x = 0
    region = None
    rv3d = None
    help = False
    set_pos = Vector((0,0,0))
    mouse_pos = Vector((0, 0))
    count = 2
    snap = False
    snapval = 0
    axis_lock = False
    imperial = []
    hcol = (1,1,1,1)
    tcol = (1,1,1,1)
    scol = (1,1,1,1)
    tm = Matrix().to_3x3()
    axis = True, False, True
    axis_int = 1
    start_v = Vector((0,1,0))
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

    numbers = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE')
    numpad = ('NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7',
              'NUMPAD_8', 'NUMPAD_9')

    @classmethod
    def poll(cls, context):
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
        return context.object is not None and context.object.type in cat and not context.object.data.is_editmode

    def draw_callback_px(self, context, pos):
        hpos, vpos = 64, 64
        if pos: hpos = pos - 10
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
            blf.position(font_id, hpos, vpos + 68, 0)
            blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
            blf.size(font_id, 20, 72)
            blf.shadow(font_id, 5, 0, 0, 0, 1)
            blf.shadow_offset(font_id, 1, -1)
            blf.draw(font_id, "Linear Array: " + str(self.count))
            blf.size(font_id, 13, 72)
            blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
            blf.position(font_id, hpos, vpos + 98, 0)
            if self.array_input_mode:
                blf.draw(font_id, title + " [(A) Numerical Input Mode]" )
            else:
                blf.draw(font_id, title)

            if self.help:
                blf.size(font_id, 13, 72)
                blf.color(font_id, self.tcol[0], self.tcol[1], self.tcol[2], self.tcol[3])
                blf.position(font_id, hpos, vpos + 45, 0)
                blf.draw(font_id, "Array Count: Mouse Wheel Up / Down")
                blf.position(font_id, hpos, vpos + 27, 0)
                if self.imperial:
                    blf.draw(font_id, "Grid Snap Steps: (1) feet, (2) inches, (3) thou, (4) mm")
                else:
                    blf.draw(font_id, "Grid Snap Steps: (1) m, (2) dm , (3) cm, (4) mm")
                blf.position(font_id, hpos, vpos + 9, 0)
                blf.draw(font_id, "Toggle Grid Snap: (1-4) or SHIFT-TAB")
                blf.position(font_id, hpos, vpos - 9, 0)
                blf.draw(font_id, "Manual Axis Lock: (X), (Y), (Z) and (C) to release Constraint")

                blf.size(font_id, 10, 72)
                blf.color(font_id, self.scol[0], self.scol[1], self.scol[2], self.scol[3])
                blf.position(font_id, hpos, vpos - 29, 0)
                blf.draw(font_id, "Apply: Enter/Spacebar/LMB  Cancel: Esc/RMB")
                blf.position(font_id, hpos, vpos - 40, 0)
                blf.draw(font_id, "Navigation: Blender (-MMB) or Ind.Std (Alt-MB's)")
            else:
                blf.size(font_id, 12, 72)
                blf.color(font_id, self.scol[0], self.scol[1], self.scol[2], self.scol[3])
                blf.position(font_id, hpos, vpos + 45, 0)
                blf.draw(font_id, "(H) Toggle Help")

        else:
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
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
        self.array.constant_offset_displace[self.axis_int] = self.dval / oc

    def set_snap(self, val):
        if self.snap and self.snapval == val:
            self.snap = False
        else:
            self.snapval = val
            self.snap = True


    def invoke(self, context, event):
        # INITIAL EVENT INFO & SETTINGS
        self.hcol = context.preferences.addons['kekit'].preferences.modal_color_header
        self.tcol = context.preferences.addons['kekit'].preferences.modal_color_text
        self.scol = context.preferences.addons['kekit'].preferences.modal_color_subtext

        self.imperial = bpy.context.scene.unit_settings.system
        self.unit_scale = bpy.context.scene.unit_settings.scale_length

        if self.imperial != 'IMPERIAL':
            self.imperial = []

        self.region = context.region
        self.rv3d = context.space_data.region_3d
        self.screen_x = int(self.region.width *.5)
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
        # initial mouse vector
        mp = region_2d_to_location_3d(self.region, self.rv3d, self.mouse_pos, self.set_pos)
        self.start_v = Vector((self.tm.inverted() @ self.set_pos) - (self.tm.inverted() @ mp)).normalized()

        # CHECK OBJECT FOR ADJUSTMENT MODE -------------------------------------------------------------------
        for m in self.obj.modifiers:
            if "Linear Array" in m.name:
                self.array = m
                self.count = int(self.array.count)
                self.og_count = int(self.array.count)
                self.og_spacing = self.array.constant_offset_displace[:]
                self.adjust_mode = True
                # spacing & axis will be instantly recalculated in modal
                break

        # NEW SETUP --------------------------------------------------------------------------------------------
        if not self.adjust_mode:
            # CREATE ARRAY MODIFIER
            self.array = self.obj.modifiers.new("Linear Array", 'ARRAY')
            self.array.use_relative_offset = False
            self.array.use_constant_offset = True
            self.array.constant_offset_displace = (0, 0, 0)
            self.array.count = 2

        # GO MODAL  --------------------------------------------------------------------------------------------
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)
        args = (context, self.screen_x)
        self._handle_px = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        # -------------------------------------------------------------------------------------------------
        # STEPVALUES OR NUMERICAL MODE
        # -------------------------------------------------------------------------------------------------
        if event.type == 'A' and event.value == 'PRESS':
            self.array_input_mode = not self.array_input_mode
            context.area.tag_redraw()

        if self.array_input_mode:
            if event.type == 'TIMER':
                self.tick += 1

            if event.type in (self.numbers + self.numpad) and event.value == 'PRESS':
                if event.type in self.numbers:
                    nr = self.numbers.index(event.type)
                else:
                    nr = self.index(event.type)

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
        else:
            if event.type == 'ONE' and event.value == 'PRESS':
                self.set_snap(0)

            elif event.type == 'TWO' and event.value == 'PRESS':
                self.set_snap(1)

            elif event.type == 'THREE' and event.value == 'PRESS':
                self.set_snap(2)

            elif event.type == 'FOUR' and event.value == 'PRESS':
                self.set_snap(3)

        # -------------------------------------------------------------------------------------------------
        # MAIN
        # -------------------------------------------------------------------------------------------------
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
                    self.array.constant_offset_displace = (0, 0, 0)

            # UPDATE OFFSET OBJ PO
            self.dval = get_distance(newpos, self.set_pos)
            if v1[self.axis_int] < v2[self.axis_int] :
                self.dval *= -1
            self.upd_array()

        # -------------------------------------------------------------------------------------------------
        # WHEEL COUNT UPDATE
        # -------------------------------------------------------------------------------------------------
        elif event.type == 'WHEELUPMOUSE':
            self.count += 1
            context.area.tag_redraw()
            self.upd_array()

        elif event.type == 'WHEELDOWNMOUSE' and self.count > 2:
            self.count -= 1
            context.area.tag_redraw()
            self.upd_array()

        # -------------------------------------------------------------------------------------------------
        # NAV
        # -------------------------------------------------------------------------------------------------
        if event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                event.alt and event.type == "RIGHTMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}

        # -------------------------------------------------------------------------------------------------
        # MISC HOTKEYS
        # -------------------------------------------------------------------------------------------------
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
            self.array.constant_offset_displace = (0, 0, 0)
            self.upd_array()

        elif event.type in {'Y', 'GRLESS'} and event.value == 'PRESS':
            self.axis_lock = True
            self.axis = True, False, True
            self.axis_int = 1
            context.area.tag_redraw()
            self.array.constant_offset_displace = (0, 0, 0)
            self.upd_array()

        elif event.type == 'Z' and event.value == 'PRESS':
            self.axis_lock = True
            self.axis = True, True, False
            self.axis_int = 2
            context.area.tag_redraw()
            self.array.constant_offset_displace = (0, 0, 0)
            self.upd_array()

        elif event.type == 'C' and event.value == 'PRESS':
            self.axis_lock = False
            context.area.tag_redraw()

        # -------------------------------------------------------------------------------------------------
        # APPLY
        # -------------------------------------------------------------------------------------------------
        elif event.type in {'RET', 'SPACE'} or event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            context.area.tag_redraw()
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            return {'FINISHED'}

        # -------------------------------------------------------------------------------------------------
        # CANCEL
        # -------------------------------------------------------------------------------------------------
        elif event.type == 'ESC' or event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            context.area.tag_redraw()
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            if not self.adjust_mode:
                bpy.ops.object.modifier_remove(modifier=self.array.name)
            else:
                self.array.count = self.og_count
                self.array.constant_offset_displace = self.og_spacing
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_OT_ke_lineararray)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_ke_lineararray)

if __name__ == "__main__":
    register()
