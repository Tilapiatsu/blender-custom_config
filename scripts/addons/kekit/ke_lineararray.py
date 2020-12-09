bl_info = {
    "name": "keLinearArray",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 2),
    "blender": (2, 80, 0),
}

import bpy
import blf
from .ke_utils import get_selected
from mathutils import Vector
from bpy_extras.view3d_utils import region_2d_to_location_3d


def draw_callback_px(self, context, pos):
    hpos, vpos = 64, 64
    if pos: hpos = pos - 10
    title = ""

    if self.axis_lock is not None:
        if self.axis_lock == 2:
            title += "[Z]"
        elif self.axis_lock == 1:
            title += "[Y]"
        else :
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
        blf.color(font_id, 0.796, 0.7488, 0.6435, 1)
        blf.size(font_id, 20, 72)
        blf.shadow(font_id, 5, 0, 0, 0, 1)
        blf.shadow_offset(font_id, 1, -1)
        blf.draw(font_id, "Linear Array: " + str(self.count))
        blf.size(font_id, 13, 72)
        blf.color(font_id, 0.85, 0.85, 0.85, 1)
        blf.position(font_id, hpos, vpos + 98, 0)
        blf.draw(font_id, title)

        if self.help:
            blf.size(font_id, 13, 72)
            blf.color(font_id, 0.85, 0.85, 0.85, 1)
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
            blf.color(font_id, 0.5, 0.5, 0.5, 1)
            blf.position(font_id, hpos, vpos - 29, 0)
            blf.draw(font_id, "Exit: RMB, Esc, Enter or Spacebar")
            blf.position(font_id, hpos, vpos - 40, 0)
            blf.draw(font_id, "Navigation: Blender (-MMB) or Ind.Std (Alt-MB's)")
        else:
            blf.size(font_id, 12, 72)
            blf.color(font_id, 0.5, 0.5, 0.5, 1)
            blf.position(font_id, hpos, vpos + 45, 0)
            blf.draw(font_id, "(H) Toggle Help")

    else:
        return {'CANCELLED'}


def to_imperial(values, mode):
    unit_scale = bpy.context.scene.unit_settings.scale_length
    values = [i * unit_scale for i in values]
    if mode == 0:
        # FEET
        return '\u0027', [(v // 0.3048) * 0.3048 for v in values]
    elif mode == 1:
        # INCHES
        return '\u0022', [(v // 0.0254) * 0.0254 for v in values]
    elif mode == 2:
        # THOU
        return 'thou', [(v // 0.000025) * 0.000025 for v in values]
    else:
        return 'bu', values


class VIEW3D_OT_ke_lineararray(bpy.types.Operator):
    bl_idname = "view3d.ke_lineararray"
    bl_label = "Linear Array"
    bl_description = "Creates an array in a line where instances are spaced automatically between start and end " \
                     "(where you point the mouse)."
    bl_options = {'REGISTER', 'UNDO'}

    _handle = None
    _handle_px = None
    screen_x = 0
    region = None
    rv3d = None
    help = False
    set_pos = Vector((0,0,0))
    set_rot = Vector((0,0,0))
    count = 2
    oname = ""
    mouse_pos = Vector((0, 0))
    prev = 0
    snap = False
    snapval = 0
    axis_lock = None
    imperial = []

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.type == 'MESH' and not context.object.data.is_editmode)

    def upd_array(self, context, event):
        # Get Mouse Pos for end-point
        cpos = self.set_pos
        pos = region_2d_to_location_3d(self.region, self.rv3d, (event.mouse_region_x, event.mouse_region_y), cpos)
        # Snapping
        if self.snap:
            if self.imperial:
                conv = to_imperial(pos, self.snapval)
                if conv[0] == "bu":
                    pos = Vector((round(pos[0], self.snapval), round(pos[1], self.snapval), round(pos[2], self.snapval)))
                else:
                    pos = conv[1]
            else:
                pos = Vector((round(pos[0], self.snapval), round(pos[1], self.snapval), round(pos[2], self.snapval)))

        # Find Axis Direction & Distance (if not axis locked)
        dx = abs(pos[0] - self.set_pos[0])
        dy = abs(pos[1] - self.set_pos[1])
        dz = abs(pos[2] - self.set_pos[2])

        dic = {0: dx, 1: dy, 2: dz}

        if self.axis_lock is not None:
            axis = self.axis_lock
        else:
            axis = sorted(dic, key=dic.get)[-1]

        # Set Values
        axis_val = dic[axis]

        ola = context.scene.objects[self.oname].modifiers[-1]
        ola.count = self.count
        oc = self.count - 1

        # Reset if Axis shifts
        if axis != self.prev:
            pos = self.set_pos
            ola.constant_offset_displace = (0, 0, 0)
            context.object.location = self.set_pos

        if pos[axis] < self.set_pos[axis]:
            axis_val *= -1

        context.object.location[axis] = pos[axis]
        ola.constant_offset_displace[axis] = axis_val / oc

        # Store for axis shift (reset)
        self.prev = axis


    def invoke(self, context, event):
        self.imperial = bpy.context.scene.unit_settings.system
        if self.imperial != 'IMPERIAL':
            self.imperial = []
        self.region = context.region
        self.rv3d = context.space_data.region_3d
        self.screen_x = int(self.region.width *.5)
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)

        obj = get_selected(context)

        if obj:
            # PRESETS
            bpy.ops.wm.tool_set_by_id(name="builtin.select")
            self.set_pos = obj.location
            self.set_rot = obj.rotation_euler
            self.oname = obj.name
            # Since it will just be borked without scaled applied anyway - we auto apply.
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            # CREATE ARRAY MODIFIER
            bpy.ops.object.modifier_add(type='ARRAY')
            ola = bpy.context.scene.objects[self.oname].modifiers[-1]
            ola.name = "LineArray"
            ola.use_relative_offset = False
            ola.use_constant_offset = True

            # CREATE TEMP EMPTY LOCATOR
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=self.set_pos,
                                     rotation=self.set_rot)
            context.object.name = "keLineArrayLocator"
            context.object.hide_viewport = True

            # RUN MODAL
            context.window_manager.modal_handler_add(self)
            args = (self, context, self.screen_x)
            self._handle_px = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            return {'RUNNING_MODAL'}

        return {'CANCELLED'}


    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            self.upd_array(context, event)

        elif event.type == 'WHEELUPMOUSE':
            self.count += 1
            context.area.tag_redraw()
            self.upd_array(context, event)

        elif event.type == 'WHEELDOWNMOUSE' and self.count > 2:
            self.count -= 1
            context.area.tag_redraw()
            self.upd_array(context, event)

        elif event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                event.alt and event.type == "RIGHTMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}

        elif event.type == 'ONE' and event.value == 'PRESS':
            if self.snap and self.snapval == 0:
                self.snap = False
            else:
                self.snapval = 0
                self.snap = True
            self.upd_array(context, event)

        elif event.type == 'TWO' and event.value == 'PRESS':
            if self.snap and self.snapval == 1:
                self.snap = False
            else:
                self.snapval = 1
                self.snap = True
            self.upd_array(context, event)

        elif event.type == 'THREE' and event.value == 'PRESS':
            if self.snap and self.snapval == 2:
                self.snap = False
            else:
                self.snapval = 2
                self.snap = True
            self.upd_array(context, event)

        elif event.type == 'FOUR' and event.value == 'PRESS':
            if self.snap and self.snapval == 3:
                self.snap = False
            else:
                self.snapval = 3
                self.snap = True
            self.upd_array(context, event)

        elif event.shift and event.type == 'TAB' and event.value == 'PRESS':
            self.snap = not self.snap

        elif event.type == 'H' and event.value == 'PRESS':
            self.help = not self.help
            context.area.tag_redraw()

        elif event.type == 'X' and event.value == 'PRESS':
            self.axis_lock = 0
            context.area.tag_redraw()

        elif event.type in {'Y', 'GRLESS'} and event.value == 'PRESS':
            self.axis_lock = 1
            context.area.tag_redraw()

        elif event.type == 'Z' and event.value == 'PRESS':
            self.axis_lock = 2
            context.area.tag_redraw()

        elif event.type == 'C' and event.value == 'PRESS':
            self.axis_lock = None
            context.area.tag_redraw()

        elif event.type in {'ESC', 'RET', 'SPACE'} or event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            context.area.tag_redraw()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            context.object.hide_viewport = False
            context.object.select_set(True)
            bpy.ops.object.delete(use_global=True, confirm=False)
            context.scene.objects[self.oname].select_set(True)
            context.view_layer.objects.active = context.scene.objects[self.oname]
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (VIEW3D_OT_ke_lineararray,
           )

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
