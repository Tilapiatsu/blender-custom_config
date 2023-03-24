import bpy
import blf
from bpy.props import BoolProperty, IntProperty, FloatProperty, EnumProperty
from ._utils import set_status_text, vector_from_matrix, refresh_ui, find_parents, apply_transform, getset_transform, \
    unparent, restore_transform
from mathutils import Vector, Matrix
from math import radians, sqrt


def get_axis(mtx, vec):
    v = mtx @ vec
    x, y, z = abs(v[0]), abs(v[1]), abs(v[2])
    if x > y and x > z:
        axis = 0
    elif y > x and y > z:
        axis = 1
    else:
        axis = 2
    return axis


def planarize(v1, v2):
    n_norm = sqrt(sum(v2 * v2))
    try:
        new = v1 - ((v1.dot(v2) / (n_norm * n_norm)) * v2)
    except ZeroDivisionError:
        print("RI: Divide By Zero")
        return v1
    return new


def angle_check_first(cand1, cand2, idx, nrm):
    c1 = vector_from_matrix(cand1, axis=idx).dot(nrm)
    c2 = vector_from_matrix(cand2, axis=idx).dot(nrm)
    if c1 > c2:
        return True
    else:
        return False


class KeRadialInstances(bpy.types.Operator):
    bl_idname = "view3d.ke_radial_instances"
    bl_label = "Radial Instances"
    bl_description = "Modal circular linked-duplication with re-activation feature\n" \
                     "Place CURSOR as center. 'Hub' axis is the SELECTED OBJECT axis facing you/view"
    bl_options = {'REGISTER', 'UNDO'}

    count: IntProperty(
        name="Count",
        description="Initial nr of linked duplicates",
        default=8,
        min=2, max=9999,
        options={'SKIP_SAVE'}
    )
    degrees: FloatProperty(
        name="Degrees",
        description="Full circle (360) or limit to set degrees\n"
                    "(Also adjustable while modal)",
        default=360,
        min=0.1, max=360,
        subtype="ANGLE",
        options={'SKIP_SAVE'},
    )
    step_degrees: FloatProperty(
        name="Step Degrees",
        description="Step to increase/decrease degrees limit in modal",
        default=15, min=0.1, max=180,
        subtype="ANGLE",
        options={'SKIP_SAVE'},
    )
    align: BoolProperty(
        name="Auto-Align",
        description="Automatically rotate Object towards cursor\n"
                    "(Also available as a toggle while modal)",
        default=True,
        options={'SKIP_SAVE'},
    )
    empty_parent: BoolProperty(
        name="Empty-Parent",
        description="Parent instances to an Empty as center-hub group control where the Cursor is placed\n"
                    "NOTE: 'Adjustment Mode' is NOT possible without the Empty",
        default=True
    )
    selection: EnumProperty(
        items=[("EMPTY", "Objects & Empty Active", "", 1),
               ("OBJECTS", "Objects Only", "", 2),
               ("NONE", "Nothing", "", 3)],
        name="Post-Op Selection",
        default="EMPTY")

    obj = None
    obj_coll = None
    hub_vector = None
    og_rot = None
    empty = None
    instances = []
    hub_loc = None
    align_rot_2d = None
    align_rot_3d = None
    align_2d = True
    adjust_mode = False
    adjust_og_count = 2
    adjust_og_limit = 2
    batch = []
    og_batch = []
    og_orient = ["GLOBAL", "MEDIAN"]
    single = True

    _timer = None
    _handle = None
    region = None
    rv3d = None
    screen_x = 0
    mouse_pos = [0, 0]
    numbers = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE')
    hcol = (1, 1, 1, 1)
    tcol = (1, 1, 1, 1)
    scol = (1, 1, 1, 1)
    fs = [48, 64, 110, 68, 20, 13, 98]
    tick = 0
    tock = 0
    input_nrs = []

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

    def draw_callback_px(self, context, pos):
        val = str(self.count)
        degs = str(self.degrees)
        hpos, vpos = self.fs[0], self.fs[1]
        hpos = pos - self.fs[2]
        font_id = 0
        blf.enable(font_id, 4)
        blf.position(font_id, hpos, vpos + self.fs[3], 0)
        blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
        blf.size(font_id, self.fs[4], 72)
        blf.shadow(font_id, 5, 0, 0, 0, 1)
        blf.shadow_offset(font_id, 1, -1)
        blf.draw(font_id, "Radial Instances: " + val)
        # Mode display
        blf.size(font_id, self.fs[5], 72)
        blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
        blf.position(font_id, hpos, vpos + self.fs[6], 0)
        m = "Limit: " + degs + "\u00b0"
        if not self.adjust_mode:
            if self.align:
                if self.align_2d:
                    m += " - Auto-Align 2D"
                else:
                    m += " - Auto-Align 3D"
            else:
                m += " - Auto-Align: OFF"
            modes = "[ " + m + " ]"
        else:
            modes = "[ Adjustment Mode ]"

        blf.draw(font_id, modes)

    def create_empty(self, name):
        d = sorted(self.obj.dimensions)
        size = d[2] * 0.75
        e = bpy.data.objects.new(name, None)
        self.obj_coll.objects.link(e)
        e.empty_display_size = size
        e.empty_display_type = 'SPHERE'
        return e

    def duplicate(self):
        if self.single:
            for i in range(1, self.count):
                new = self.obj.copy()
                self.obj_coll.objects.link(new)
                self.instances.append(new)
                self.batch.append([new])
        else:
            # much slower, didn't want to deal with the parenting...
            for o in self.instances:
                o.select_set(False)
            for o in self.og_batch:
                o.select_set(True)
            c = []
            for i in range(1, self.count):
                bpy.ops.object.duplicate(linked=True)
                c = bpy.context.selected_objects[:]
                self.instances.extend(c)
                self.batch.append(c)
            for o in self.instances + self.og_batch:
                o.select_set(True)

    def undo_duplicate(self):
        self.instances = [i for i in self.instances if i not in self.og_batch]
        for o in self.instances:
            bpy.data.objects.remove(o, do_unlink=True)
        self.instances = []
        self.batch = []

    def rotate(self):
        if self.degrees == 360:
            step = radians(self.degrees) / self.count
        else:
            step = radians(self.degrees) / (self.count - 1)
        for i, batch in enumerate(self.batch, 1):
            o = batch[0]
            angle = step * i
            mtx = (
                    Matrix.Translation(self.hub_loc) @
                    Matrix.Rotation(angle, 4, self.hub_vector) @
                    Matrix.Translation(-self.hub_loc)
            )
            o.matrix_world = mtx @ o.matrix_world

    def rotate_align(self, n, ov, axidx):
        def rot(a):
            mtx = (
                    Matrix.Translation(self.obj.location) @
                    Matrix.Rotation(a, 4, self.hub_vector)
            )
            return mtx @ self.obj.matrix_world
        plane_n = planarize(n, self.hub_vector)
        angle = ov.rotation_difference(plane_n).angle
        # better way to know if angle should be + or - ?!
        rot_c1 = rot(angle)
        rot_c2 = rot(-angle)
        if angle_check_first(rot_c1, rot_c2, axidx, plane_n):
            return rot_c1.to_euler()
        else:
            return rot_c2.to_euler()

    def rotate_align_3d(self, n, ov, axidx):
        def rot(a, b, t_vec):
            mtx = (
                    Matrix.Translation(self.obj.location) @
                    Matrix.Rotation(a, 4, self.hub_vector) @
                    Matrix.Rotation(b, 4, t_vec)
            )
            return mtx @ self.obj.matrix_world
        plane_n = planarize(n, self.hub_vector)
        angle_a = ov.rotation_difference(plane_n).angle
        t = ov.cross(self.hub_vector)
        plane_t = planarize(n, t)
        angle_b = ov.rotation_difference(plane_t).angle
        # better way to know if angle(S!) should be + or - ?!
        rot_c1 = rot(angle_a, 0, t)
        rot_c2 = rot(-angle_a, 0, t)
        if angle_check_first(rot_c1, rot_c2, axidx, plane_n):
            rot_c3 = rot(angle_a, angle_b, t)
            rot_c4 = rot(angle_a, -angle_b, t)
            if angle_check_first(rot_c3, rot_c4, axidx, n):
                return rot_c3.to_euler()
            else:
                return rot_c4.to_euler()
        else:
            rot_c3 = rot(-angle_a, angle_b, t)
            rot_c4 = rot(-angle_a, -angle_b, t)
            if angle_check_first(rot_c3, rot_c4, axidx, n):
                return rot_c3.to_euler()
            else:
                return rot_c4.to_euler()

    def toggle_align_2d(self):
        if self.align:
            self.align_2d = not self.align_2d
            self.undo_duplicate()
            if not self.align_2d:
                self.obj.rotation_euler = self.align_rot_3d
            else:
                self.obj.rotation_euler = self.align_rot_2d
            bpy.context.evaluated_depsgraph_get().update()
            self.duplicate()
            self.rotate()

    def toggle_align(self):
        self.align = not self.align
        self.undo_duplicate()
        if not self.align:
            self.obj.rotation_euler = self.og_rot
        else:
            if not self.align_2d:
                self.obj.rotation_euler = self.align_rot_3d
            else:
                self.obj.rotation_euler = self.align_rot_2d
        bpy.context.evaluated_depsgraph_get().update()
        self.duplicate()
        self.rotate()

    def update_count(self, val, num=False):
        if num:
            if not isinstance(val, int):
                nrs = len(val)
                if nrs == 3:
                    val = (self.input_nrs[0] * 100) + (self.input_nrs[1] * 10) + self.input_nrs[2]
                elif nrs == 2:
                    val = (self.input_nrs[0] * 10) + self.input_nrs[1]
                else:
                    val = self.input_nrs[0]
            self.count = val
        else:
            self.count += val
        if self.count < 2:
            self.count = 2
        self.undo_duplicate()
        self.duplicate()
        self.rotate()

    def update_degree_limit(self, val):
        self.undo_duplicate()
        self.degrees += val
        if self.degrees < self.step_degrees:
            self.degrees = self.step_degrees
        self.duplicate()
        self.rotate()

    def set_adjustmode(self, instances):
        self.instances = []
        # Fake Src selection
        self.obj = instances[0]
        children = list(self.obj.children_recursive)
        bpy.ops.object.select_all(action="DESELECT")
        if children:
            for c in children:
                c.select_set(True)
        # rest will be instances
        for o in instances:
            co = list(o.children_recursive) + [o]
            self.instances.extend(co)
        self.load_props()
        self.adjust_og_count = int(self.count)
        self.adjust_mode = True

    def load_props(self):
        self.degrees = self.empty["RI_OG_DEG"]
        self.align = self.empty["RI_OG_ALN"]
        self.align_2d = self.empty["RI_OG_A2D"]
        self.count = self.empty["RI_OG_CNT"]

    def save_props(self):
        self.empty["RI_OG_CNT"] = self.count
        self.empty["RI_OG_DEG"] = self.degrees
        self.empty["RI_OG_ALN"] = self.align
        self.empty["RI_OG_A2D"] = self.align_2d
        self.empty["RI_OG_EAX"] = self.align_2d

    def invoke(self, context, event):
        self.region = context.region
        self.rv3d = context.space_data.region_3d
        self.screen_x = int(self.region.width * 0.5)
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)
        return self.execute(context)

    def execute(self, context):
        # SOURCE OBJECT & INITS
        prefix = "RadialEG_"
        self.screen_x = int(context.region.width * .5)
        k = context.preferences.addons[__package__].preferences
        cursor = context.scene.cursor

        self.hcol = k.modal_color_header
        self.tcol = k.modal_color_text
        self.scol = k.modal_color_subtext
        scale_factor = context.preferences.view.ui_scale * k.ui_scale
        self.fs = [int(round(n * scale_factor)) for n in self.fs]
        self.batch, self.instances = [], []

        self.hub_loc = cursor.location
        self.obj = context.object

        # ADJUSTMENT MODE CHECK
        self.instances = []
        self.adjust_mode = False
        parents = find_parents(self.obj)
        if self.obj.type == "EMPTY" and prefix in self.obj.name:
            if self.obj.children:
                self.empty = self.obj
                self.empty.select_set(False)
                c = list(self.empty.children)
                self.set_adjustmode(c)
            else:
                self.report({"INFO"}, "Invalid Radial Instances Setup")
                return {"CANCELLED"}
        elif parents:
            e = [o for o in parents if o.type == "EMPTY" and prefix in o.name]
            if e:
                self.empty = e[0]
                c = list(self.empty.children)
                if c:
                    self.set_adjustmode(c)
                else:
                    self.report({"INFO"}, "Invalid Radial Instances Setup")
                    return {"CANCELLED"}

        self.obj.select_set(True)
        context.view_layer.objects.active = self.obj
        self.obj_coll = self.obj.users_collection[0]
        self.og_batch = [o for o in context.selected_objects if o.type == "MESH"]
        if len(self.og_batch) > 1:
            self.single = False

        # "Did you apply scale?"
        for o in self.og_batch:
            apply_transform(o, False, False, True)
        # bkp
        self.og_orient = getset_transform("CURSOR", "CURSOR")
        self.og_rot = self.obj.rotation_euler.copy()

        # ALIGNMENT
        if self.adjust_mode:
            self.hub_loc = self.empty.location
            obj_axis_idx = self.empty["RI_OG_HUB"]
            self.hub_vector = vector_from_matrix(self.obj.matrix_world, axis=obj_axis_idx)
            self.undo_duplicate()
            context.evaluated_depsgraph_get().update()
        else:
            # Forced parenting for multi object selection
            if not self.single:
                c = [o for o in self.og_batch if o != self.obj]
                unparent(c)
                for o in c:
                    o.parent = self.obj
                    o.matrix_parent_inverse = self.obj.matrix_world.inverted()

            inv_mtx = self.obj.matrix_world.to_3x3().inverted()
            view_n = Vector(context.space_data.region_3d.view_matrix[2].to_3d())
            idx = get_axis(inv_mtx, view_n)

            n = Vector(self.obj.location - self.hub_loc).normalized()
            if n.magnitude == 0:
                self.report({"INFO"}, "Fail: Object origin at same place as cursor!")
                return {"CANCELLED"}

            obj_axis_idx = get_axis(inv_mtx, n)
            obj_vec = vector_from_matrix(self.obj.matrix_world, axis=obj_axis_idx)
            obj_d = n.dot(obj_vec)
            if obj_d < 0:
                n.negate()
            self.hub_vector = vector_from_matrix(self.obj.matrix_world, axis=idx)

            # 2d
            self.align_rot_2d = self.rotate_align(n, obj_vec, obj_axis_idx)
            # 3d
            self.align_rot_3d = self.rotate_align_3d(n, obj_vec, obj_axis_idx)

            # INITIAL ALIGN
            if self.align:
                if not self.align_2d:
                    self.obj.rotation_euler = self.align_rot_3d
                else:
                    self.obj.rotation_euler = self.align_rot_2d

            # HUB-GROUP EMPTY
            if self.empty_parent:
                empty_name = prefix + self.obj.name
                self.empty = self.create_empty(empty_name)
                self.empty.location = self.hub_loc
                self.empty.rotation_euler = cursor.rotation_euler
                # Store empty as hub-axis for adj mode
                self.empty["RI_OG_HUB"] = idx
                # Update Required Now
                context.evaluated_depsgraph_get().update()
                # Parent
                self.obj.parent = self.empty
                self.obj.matrix_parent_inverse = self.empty.matrix_world.inverted()
                self.empty.select_set(False)

        # INITIAL OPERATION
        self.duplicate()
        self.rotate()

        # GO MODAL
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)
        args = (context, self.screen_x)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        # SET STATUS BAR HELP
        if self.adjust_mode:
            status_help = [
                "[WHEEL/0-9] Count",
                "[CTRL-WHEEL] Limit Degrees",
                "[MMB,ALT-MBs] Navigation",
                "[ENTER/SPACEBAR/LMB] Apply",
                "[ESC/RMB] Cancel"
            ]
        else:
            status_help = [
                "[WHEEL/0-9] Count",
                "[CTRL-WHEEL] Limit Degrees",
                "[A] Auto-Align Toggle",
                "[D] Align 2D/3D Toggle",
                "[MMB,ALT-MBs] Navigation",
                "[ENTER/SPACEBAR/LMB] Apply",
                "[ESC/RMB] Cancel"
            ]
        set_status_text(context, status_help)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        #
        # INPUTS
        #
        if event.type == 'TIMER':
            self.tick += 1

        if event.type in self.numbers and event.value == 'PRESS':
            nr = self.numbers.index(event.type)
            self.input_nrs.append(nr)
            self.tock = int(self.tick)

        if self.tick - self.tock >= 1:
            if len(self.input_nrs) > 0:
                self.update_count(self.input_nrs, True)
                self.input_nrs = []
                context.area.tag_redraw()

        if event.type == 'WHEELUPMOUSE':
            if event.ctrl:
                self.update_degree_limit(self.step_degrees)
            else:
                self.update_count(1)
            context.area.tag_redraw()

        elif event.type == 'WHEELDOWNMOUSE':
            if event.ctrl:
                self.update_degree_limit(-self.step_degrees)
            else:
                self.update_count(-1)
            context.area.tag_redraw()

        if not self.adjust_mode:
            if event.type == 'A' and event.value == 'PRESS':
                self.toggle_align()
                context.area.tag_redraw()

            elif event.type == 'D' and event.value == 'PRESS':
                self.toggle_align_2d()
                context.area.tag_redraw()
        #
        # NAVIGATION
        #
        if event.alt and event.type in {"LEFTMOUSE", "MIDDLEMOUSE", "RIGHTMOUSE"} or \
                event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}
        #
        # APPLY
        #
        if event.type in {'RET', 'SPACE'} or event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.workspace.status_text_set(None)

            if self.selection == "NONE":
                bpy.ops.object.select_all(action="DESELECT")
            else:
                for i in self.instances + self.og_batch:
                    i.select_set(True)

            if self.empty is not None:
                self.save_props()
                if self.selection == "EMPTY":
                    self.empty.select_set(True)
                    context.view_layer.objects.active = self.empty
            else:
                unparent(self.instances + self.og_batch)

            restore_transform(self.og_orient)
            refresh_ui()
            return {'FINISHED'}
        #
        # CANCEL
        #
        elif event.type == 'ESC' or event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.workspace.status_text_set(None)

            if self.adjust_mode:
                self.load_props()
                context.evaluated_depsgraph_get().update()
                self.update_count(self.adjust_og_count, True)
                self.empty.select_set(True)
            else:
                self.undo_duplicate()
                if self.empty:
                    bpy.data.objects.remove(self.empty, do_unlink=True)
                self.obj.rotation_euler = self.og_rot

            for o in self.og_batch:
                o.select_set(True)
            context.view_layer.objects.active = self.obj

            restore_transform(self.og_orient)
            refresh_ui()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


#
# CLASS REGISTRATION
#
def register():
    bpy.utils.register_class(KeRadialInstances)


def unregister():
    bpy.utils.unregister_class(KeRadialInstances)
