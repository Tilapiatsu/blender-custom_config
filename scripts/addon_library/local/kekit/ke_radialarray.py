import bpy
import blf
from bpy.props import BoolProperty
from ._utils import get_selected, getset_transform, restore_transform, get_layer_collection, get_distance, \
    average_vector, set_status_text
from mathutils import Vector, Matrix
from math import radians


class KeRadialArray(bpy.types.Operator):
    bl_idname = "view3d.ke_radialarray"
    bl_label = "RadialArray"
    bl_description = "[Legacy] Modal circular setup for the Array Modifier\n" \
                     "Place CURSOR as array center (Cursor-Z = hub-axis) and select an OBJECT to use\n" \
                     "Auto-Arrange option ca be toggled in the Shortcut Editor"
    bl_options = {'REGISTER', 'UNDO'}

    auto_arrange: BoolProperty(
        name="Auto-Align",
        description="Automatically rotate Object towards center prior to radial",
        default=True
    )

    radial_count = 6
    og_radial_count = 2
    array = None
    loc = None
    loc_scl = 1
    loc_rotval = 60
    obj = None
    _handle = None
    screen_x = 100
    prev_mx = 100
    hcol = (1, 1, 1, 1)
    tcol = (1, 1, 1, 1)
    scol = (1, 1, 1, 1)
    fs = [64, 110, 120, 68, 20, 13, 98, 13, 45, 27, 9, 9, 30, 48, 10, 66, 80, 94, 12, 45]
    og = "WORLD"
    og_mtx = Matrix()
    adjust_mode = False
    snapval = 0.01
    help = False
    tot_off_rad = 0.0
    tot_off_z = 0.0
    tot_off_scl = 0.0
    array_input_mode = False
    _timer = None
    tick = 0
    tock = 0
    input_nrs = []
    new_mx = 0
    restore_coords = []
    adj_mode_rad = False
    adj_mode_scl = False
    adj_mode_z = False
    adj_val = 0

    numbers = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE')

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.object is not None and
                context.object.type == 'MESH' and
                not context.object.data.is_editmode)

    def draw(self, context):
        layout = self.layout

    def draw_callback_px(self, context, pos):
        val = self.radial_count
        hpos, vpos = self.fs[0], self.fs[1]
        if pos:
            hpos = pos - self.fs[2]
        if val:
            font_id = 0
            blf.enable(font_id, 4)
            blf.position(font_id, hpos, vpos + self.fs[3], 0)
            blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
            blf.size(font_id, self.fs[4], 72)
            blf.shadow(font_id, 5, 0, 0, 0, 1)
            blf.shadow_offset(font_id, 1, -1)
            blf.draw(font_id, "Radial Array: " + str(val))

            if self.array_input_mode or self.adj_mode_z or self.adj_mode_rad or self.adj_mode_scl:
                blf.size(font_id, self.fs[5], 72)
                blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
                blf.position(font_id, hpos, vpos + self.fs[6], 0)
                adjm = ""
                if self.adj_mode_rad:
                    adjm = "[ (X) Circle Radius Adjustment Mode ]"
                elif self.adj_mode_z:
                    adjm = "[ (Z) Depth Adjustment Mode ]"
                elif self.adj_mode_scl:
                    adjm = "[ (S) Scale Object Adjustment Mode ]"
                if self.array_input_mode:
                    blf.draw(font_id, "[ (A) Numerical Input Mode ] " + adjm)
                else:
                    blf.draw(font_id, adjm)
            if self.help:
                blf.size(font_id, self.fs[7], 72)
                blf.color(font_id, self.tcol[0], self.tcol[1], self.tcol[2], self.tcol[3])
                blf.position(font_id, hpos, vpos + self.fs[8], 0)
                blf.draw(font_id, "Count:       Mouse Wheel Up / Down")
                blf.position(font_id, hpos, vpos + self.fs[9], 0)
                blf.draw(font_id, "Radius:      (X) (or C)")
                blf.position(font_id, hpos, vpos + self.fs[10], 0)
                blf.draw(font_id, "Z Pos:       (Z)   Reset Z: (R)")
                blf.position(font_id, hpos, vpos - self.fs[11], 0)
                blf.draw(font_id, "Scale:       (S)")
                blf.position(font_id, hpos, vpos - self.fs[12], 0)
                blf.draw(font_id, "Adjustment Level: (1) Very Fine --> (5) Huge ")
                blf.position(font_id, hpos, vpos - self.fs[13], 0)
                blf.draw(font_id, "(A) Toggle Numerical Input Mode for Array Count")

                blf.size(font_id, self.fs[14], 72)
                blf.color(font_id, self.scol[0], self.scol[1], self.scol[2], self.scol[3])
                blf.position(font_id, hpos, vpos - self.fs[15], 0)
                blf.draw(font_id, "Apply: Enter/Spacebar/LMB  Cancel: Esc/RMB")
                blf.position(font_id, hpos, vpos - self.fs[16], 0)
                blf.draw(font_id, "Navigation: Blender (MMB's) + Ind.Std (Alt-MB's)")
        else:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.workspace.status_text_set(None)
            return {'CANCELLED'}

    def bmove(self, val):
        verts = self.obj.data.vertices
        coords = [0, 0, 0] * len(verts)
        verts.foreach_get('co', coords)
        for i in range(0, len(coords), 3):
            coords[i] += val[0]
            coords[i + 1] += val[1]
            coords[i + 2] += val[2]
        verts.foreach_set('co', coords)
        self.obj.data.update()

    def bscale(self, val):
        verts = self.obj.data.vertices
        coords = [0, 0, 0] * len(verts)
        verts.foreach_get('co', coords)
        # Calc mesh local center (origin is n/a)
        avg_co = []
        for i in range(0, len(coords), 3):
            avg_co.append(Vector((coords[i], coords[i + 1], coords[i + 2])))
        center = average_vector(avg_co)
        # Calc and apply vector from center to verts to scale
        for i in range(0, len(coords), 3):
            co = Vector((coords[i], coords[i + 1], coords[i + 2]))
            cvec = (co - center) * val
            coords[i] += cvec[0]
            coords[i + 1] += cvec[1]
            coords[i + 2] += cvec[2]
        verts.foreach_set('co', coords)
        self.obj.data.update()

    def update_rot(self):
        # Reset needed, and then re-rotate
        self.array.count = self.radial_count
        self.loc.rotation_euler = self.loc_rotval
        rot = radians(360 / self.radial_count)
        self.loc.rotation_euler.rotate_axis("Z", rot)

    def execute(self, context):
        # Check sel obj
        self.obj = get_selected(context, use_cat=True)
        if self.obj is not None:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        else:
            self.report({"INFO"}, "No valid Object selected?")
            return {'CANCELLED'}

        # Check object for existing components
        status = [False, False]
        for o in self.obj.children:
            if "RadialArrayEmpty" in o.name:
                self.loc = context.scene.objects[o.name]
                status[0] = True
                break
        for m in self.obj.modifiers:
            if "Radial Array" in m.name:
                self.array = m
                self.radial_count = int(self.array.count)
                self.og_radial_count = int(self.array.count)
                status[1] = True
                break

        if all(status):
            # Adjusting existing array (adjust_mode)
            self.adjust_mode = True
            self.og = getset_transform(o="LOCAL", p="INDIVIDUAL_ORIGINS", setglobal=True)
            # Reset array and empty, re-rotate
            self.array.count = 0
            self.loc.rotation_euler = self.obj.rotation_euler
            self.loc_rotval = self.loc.rotation_euler.copy()
            self.array.count = self.radial_count
            self.loc.rotation_euler.rotate_axis("Z", radians(360 / self.radial_count))

        elif any(status):
            self.report({"INFO"}, "Invalid Radial Array Object. Array/Empty removed/remain?")
            return {'CANCELLED'}

        # Setup
        self.screen_x = int(context.region.width * .5)
        self.prev_mx = self.screen_x
        k = context.preferences.addons[__package__].preferences
        self.hcol = k.modal_color_header
        self.tcol = k.modal_color_text
        self.scol = k.modal_color_subtext
        scale_factor = context.preferences.view.ui_scale * k.ui_scale
        self.fs = [int(round(n * scale_factor)) for n in self.fs]
        coords = []
        cpos = (0, 0, 0)

        if not self.adjust_mode:
            # setting active coll for empty creation - mess, should really be a one-liner:
            obj_collection = self.obj.users_collection[0]
            layer_collection = context.view_layer.layer_collection
            layer_coll = get_layer_collection(layer_collection, obj_collection.name)
            og_viewlayer = [context.view_layer.active_layer_collection]
            context.view_layer.active_layer_collection = layer_coll

            self.og = getset_transform(o="CURSOR", p="CURSOR", setglobal=True)
            self.og_mtx = self.obj.matrix_world.copy()

            if self.auto_arrange:
                # bpy.ops.view3d.ke_object_to_cursor('INVOKE_DEFAULT')
                cursor = context.scene.cursor
                c_loc = cursor.location
                c_rot = cursor.rotation_euler
                for obj in context.selected_objects:
                    obj.location = c_loc
                    og_rot_mode = str(obj.rotation_mode)
                    obj.rotation_mode = "XYZ"
                    obj.rotation_euler = c_rot
                    obj.rotation_mode = og_rot_mode

            # Backup vert coords for restore
            verts = self.obj.data.vertices
            self.restore_coords = [0, 0, 0] * len(verts)
            self.obj.data.vertices.foreach_get('co', self.restore_coords)

            # Initial radial offset using bbox diagonal
            bbmin, bbmax = self.obj.bound_box[0], self.obj.bound_box[-2]
            bb_diag = get_distance(Vector(bbmax), Vector(bbmin))
            if self.auto_arrange:
                self.bmove(Vector((bb_diag, 0.0, 0.0)))
                self.tot_off_rad = bb_diag

            # Set origin to center
            # bpy.ops.view3d.ke_origin_to_cursor('INVOKE_DEFAULT')
            context.scene.tool_settings.use_transform_data_origin = True
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), orient_type='CURSOR', mirror=True,
                                        use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                        proportional_size=1, use_proportional_connected=False,
                                        use_proportional_projected=False)
            context.scene.tool_settings.use_transform_data_origin = False
            bpy.ops.transform.select_orientation(orientation='LOCAL')

            # Make Empty (self.loc = locator)
            self.loc_scl = (bb_diag / 2, bb_diag / 2, bb_diag / 2)
            bpy.ops.object.empty_add(type='ARROWS', align='CURSOR', scale=self.loc_scl)
            context.object.name = self.obj.name + ".RadialArrayEmpty"
            self.loc = context.scene.objects[context.object.name]
            self.loc.empty_display_size = self.loc_scl[0]

            # Setup Empty & Parent
            self.obj.select_set(True)
            context.view_layer.objects.active = self.obj
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
            self.loc.select_set(False)
            self.loc.hide_viewport = True

            # Add Array
            self.array = self.obj.modifiers.new(name="Radial Array", type="ARRAY")
            self.array.use_relative_offset = False
            self.array.use_constant_offset = False
            self.array.use_object_offset = True
            self.array.offset_object = self.loc
            self.array.count = self.radial_count

            # initial Rotation
            self.loc_rotval = self.loc.rotation_euler.copy()
            self.loc.rotation_euler.rotate_axis("Z", radians(360 / self.radial_count))

            # Restoring the og active collection to avoid annoyances
            context.view_layer.active_layer_collection = og_viewlayer[0]

            # Adj Val - Calc mesh local center vs cursor loc for radius approx.
            verts = self.obj.data.vertices
            coords = [0, 0, 0] * len(verts)
            verts.foreach_get('co', coords)
            cpos = context.scene.cursor.location

        elif self.adjust_mode:
            # Backup vert coords for restore
            # + use for Adj Val - Calc mesh local center vs obj loc for radius approx.
            verts = self.obj.data.vertices
            self.restore_coords = [0, 0, 0] * len(verts)
            verts.foreach_get('co', self.restore_coords)
            cpos = self.obj.location

        # Set initial snap values from approx rad
        if not coords:
            coords = self.restore_coords

        avg_co = []
        for i in range(0, len(coords), 3):
            avg_co.append(Vector((coords[i], coords[i + 1], coords[i + 2])))

        objpos = self.obj.matrix_world @ average_vector(avg_co)
        self.adj_val = get_distance(objpos, cpos)

        if self.adj_val <= 0.1:
            self.snapval = 0.001

        elif self.adj_val < 2:
            self.snapval = 0.01

        elif self.adj_val > 2:
            self.snapval = 0.1

        # Run Modal
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)
        args = (context, self.screen_x)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        # UPDATE STATUS BAR
        status_help = [
            "[WHEEL] Count",
            "[A] Num.Input",
            "[X/C] Radius",
            "[Z/R] Z Offset/Reset",
            "[S] Scale",
            "[1-5] Adj.Level",
            "[X,Y,<,Z] Axis Lock",
            "[MMB, ALT-MBs] Navigation",
            "[ENTER/SPACEBAR/LMB] Apply",
            "[ESC/RMB] Cancel",
            "[H] Toggle Help"]
        set_status_text(context, status_help)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            self.new_mx = int(event.mouse_region_x)

        #
        # STEPVALUES OR NUMERICAL MODE
        #
        if event.type == 'A' and event.value == 'RELEASE':
            self.array_input_mode = not self.array_input_mode
            context.area.tag_redraw()

        if self.array_input_mode:
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

                    self.radial_count = val
                    self.update_rot()
                    self.input_nrs = []
                    context.area.tag_redraw()
        else:
            if event.type == 'ONE' and event.value == 'PRESS':
                self.snapval = 0.0001

            elif event.type == 'TWO' and event.value == 'PRESS':
                self.snapval = 0.001

            elif event.type == 'THREE' and event.value == 'PRESS':
                self.snapval = 0.01

            elif event.type == 'FOUR' and event.value == 'PRESS':
                self.snapval = 0.1

            elif event.type == 'FIVE' and event.value == 'PRESS':
                self.snapval = 1.0

        #
        # SET ADJUSTMENT MODE
        #
        if event.type in {'X', 'C'} and event.value == 'PRESS':
            if self.adj_mode_scl:
                self.adj_mode_scl = False
            elif self.adj_mode_z:
                self.adj_mode_z = False
            self.adj_mode_rad = not self.adj_mode_rad
            context.area.tag_redraw()

        elif event.type == 'Z' and event.value == 'PRESS':
            if self.adj_mode_rad:
                self.adj_mode_rad = False
            elif self.adj_mode_scl:
                self.adj_mode_scl = False
            self.adj_mode_z = not self.adj_mode_z
            context.area.tag_redraw()

        elif event.type == 'S' and event.value == 'PRESS':
            if self.adj_mode_rad:
                self.adj_mode_rad = False
            elif self.adj_mode_z:
                self.adj_mode_z = False
            self.adj_mode_scl = not self.adj_mode_scl
            context.area.tag_redraw()

        #
        # HELP
        #
        if event.type == 'H' and event.value == 'PRESS':
            self.help = not self.help
            context.area.tag_redraw()

        #
        # ADJUST ARRAY COUNT
        #
        elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            if event.type == 'WHEELDOWNMOUSE' and self.radial_count > 2:
                self.radial_count -= 1
            elif event.type == 'WHEELUPMOUSE':
                self.radial_count += 1
            self.update_rot()
            context.area.tag_redraw()

        #
        # ADJUST SCALE
        #
        if self.adj_mode_scl:
            val = None
            if self.new_mx > self.prev_mx:
                val = self.snapval + .01
            elif self.new_mx < self.prev_mx:
                val = (self.snapval + .01) * -1
            if val is not None:
                self.tot_off_scl += val
                self.bscale(val)
            self.prev_mx = self.new_mx
            # context.area.tag_redraw()

        #
        # ADJUST RADIUS
        #
        elif self.adj_mode_rad:
            val = None
            if self.new_mx > self.prev_mx:
                val = self.snapval * 1
            elif self.new_mx < self.prev_mx:
                val = (self.snapval * 1) * -1
            if val is not None:
                self.tot_off_rad += val
                self.bmove(Vector((val, 0.0, 0.0)))
            self.prev_mx = self.new_mx
            # context.area.tag_redraw()

        #
        # ADJUST Z POS
        #
        elif self.adj_mode_z:
            val = None
            if self.new_mx > self.prev_mx:
                val = self.snapval
            elif self.new_mx < self.prev_mx:
                val = self.snapval * -1
            if val is not None:
                self.tot_off_z += val
                self.bmove(Vector((0.0, 0.0, val)))
            self.prev_mx = self.new_mx
            # context.area.tag_redraw()

        # RESET Z POS
        elif event.type == 'R' and event.value == 'RELEASE':
            self.bmove(Vector((0.0, 0.0, self.tot_off_z * -1)))

        #
        # NAVIGATION
        #
        elif event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                event.alt and event.type == "RIGHTMOUSE" or \
                event.alt and event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}

        #
        # APPLY
        #
        if event.type in {'LEFTMOUSE', 'RET', 'SPACE'}:
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.area.tag_redraw()
            context.workspace.status_text_set(None)
            return {'FINISHED'}

        #
        # CANCEL
        #
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            # Restore offsets
            verts = self.obj.data.vertices
            verts.foreach_set('co', self.restore_coords)

            if self.adjust_mode:
                # Reset stored vals
                self.radial_count = self.og_radial_count
                self.update_rot()
            else:
                # Restore all the things
                self.loc.hide_viewport = False
                self.obj.modifiers.remove(self.array)
                self.obj.matrix_world = self.og_mtx
                self.obj.select_set(False)
                self.loc.select_set(True)
                bpy.ops.object.delete()
                self.obj.select_set(True)

            restore_transform(self.og)
            context.workspace.status_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


#
# CLASS REGISTRATION
#
def register():
    bpy.utils.register_class(KeRadialArray)


def unregister():
    bpy.utils.unregister_class(KeRadialArray)
