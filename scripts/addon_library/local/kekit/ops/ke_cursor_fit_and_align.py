import bmesh
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator
from bpy_extras.view3d_utils import region_2d_to_location_3d
from mathutils import Vector, Matrix
from .._utils import (
    get_prefs,
    rotation_from_vector,
    mouse_raycast,
    average_vector,
    get_distance,
    vector_from_matrix,
    is_tf_applied,
    bm_selections,
)


def draw_callback_view(self, context):
    # Temp xyz axis-gizmo
    gpu.state.line_width_set(2)
    # gpu.state.blend_set("NONE")

    if self.axis_lines:
        x = batch_for_shader(self.shader, 'LINES', {"pos": self.axis_lines[0]})
        self.shader.uniform_float("color", (0.85, 0.15, 0.15, 1))
        x.draw(self.shader)

        y = batch_for_shader(self.shader, 'LINES', {"pos": self.axis_lines[1]})
        self.shader.uniform_float("color", (0.25, 0.8, 0.3, 1))

        y.draw(self.shader)

        z = batch_for_shader(self.shader, 'LINES', {"pos": self.axis_lines[2]})
        self.shader.uniform_float("color", (0.15, 0.50, 0.85, 1))
        z.draw(self.shader)


class KeCursorFitAlign(Operator):
    bl_idname = "view3d.ke_cursor_fit_align"
    bl_label = "Cursor Fit & Align"
    bl_description = "Snap Cursor to selected + orient to FACE/VERT/EDGE normal. \n" \
                     "No selection = Cursor reset\n" \
                     "Object mode: Mouse over object places Cursor on face center OR\n" \
                     "Obj selected and mouse over nothing, matches obj rot/loc."
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    cursor_orient_set = True
    mouse_pos = Vector((0, 0))
    ctx = None
    pos = Vector()
    og = ["GLOBAL", "MEDIAN_POINT", "XYZ"]
    keep_cursor_tf = False
    apply_custom = True
    lfn = None
    lfavgpos = None
    axis_lines = None
    axis_line_length = 0.015
    shader = None
    _handle_view = None
    _timer = None
    start_time = 0
    end = False

    def use_blender_tf(self):
        om = Matrix()
        try:
            bpy.ops.transform.create_orientation(name='keTF', use_view=False, use=True, overwrite=True)
            om = self.ctx.scene.transform_orientation_slots[0].custom_orientation.matrix.copy()
            bpy.ops.transform.delete_orientation()
        except RuntimeError:
            pass
        self.set_cursor(om)
        self.apply_custom = False

    def set_cursor(self, rot):
        # Apply - (rotmtx should now be worldspace)
        if self.lfn and self.lfavgpos:
            # Check z-dir 1st
            x, y, z = vector_from_matrix(rot)
            lfncheck = round(z.dot(self.lfn), 3)
            lfavgvec = (self.pos - self.lfavgpos).normalized()
            lfavgcheck = round(z.dot(lfavgvec), 3)
            # print("LFN:", lfncheck, " LFAVG:", lfavgcheck)
            if lfncheck < 0 and lfavgcheck <= 0:
                # print("lfn NEG")
                rot = Matrix((x, -y, -z)).to_4x4().inverted_safe()
            if lfavgcheck < 0 and lfncheck == 0:
                # print("lfavgvec NEG")
                rot = Matrix((x, -y, -z)).to_4x4().inverted_safe()
        q = rot.to_euler("XYZ")
        self.ctx.scene.cursor.rotation_mode = "XYZ"
        self.ctx.scene.cursor.rotation_euler = q
        # Floating point rounding (zero-floats over 3 dec.pts still "looks wrong" to ppl)
        crot = self.ctx.scene.cursor.rotation_euler
        crot.x = round(crot.x, 4)
        crot.y = round(crot.y, 4)
        crot.z = round(crot.z, 4)
        self.ctx.scene.cursor.location = self.pos
        bpy.ops.transform.select_orientation(orientation="CURSOR")
        self.ctx.tool_settings.transform_pivot_point = "CURSOR"

    def restore_cursor(self):
        if not self.keep_cursor_tf:
            bpy.ops.transform.select_orientation(orientation=self.og[0])
            self.ctx.scene.tool_settings.transform_pivot_point = self.og[1]
            self.ctx.scene.cursor.rotation_mode = self.og[2]

    def quit(self):
        wm = self.ctx.window_manager
        wm.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle_view, 'WINDOW')
        self.ctx.area.tag_redraw()

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        self.start_time = 0
        self.end = False
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        self.keep_cursor_tf = k.cursorfit
        self.ctx = context
        self.apply_custom = True
        self.lfn = None
        self.lfavgpos = None
        scale_check = True
        # Axis preview gizmo
        use_axis_gizmo = k.cursor_gizmo

        # GRAB CURRENT (Original) ORIENT & PIVOT (to restore at the end)
        self.og = [str(context.scene.transform_orientation_slots[0].type),
                   str(context.scene.tool_settings.transform_pivot_point),
                   str(context.scene.cursor.rotation_mode)]

        if context.object:
            # to-do: Multi-object in edit mode support - not possible with blenders custom tf's, so...
            if not is_tf_applied(context.object)[2]:
                scale_check = False

        #
        # CURVES
        #
        if context.object and context.object.type in {'CURVE', 'GPENCIL'} and context.mode != "OBJECT":
            # print("CURVE EDIT MODE")
            obj_mtx = context.object.matrix_world
            cos = []

            if context.object.type == "CURVE":
                if context.object.data.splines:
                    for s in context.object.data.splines:
                        if s.type == 'BEZIER':
                            for p in s.bezier_points:
                                if p.select_control_point:
                                    cos.append(obj_mtx @ p.co)
                        if s.type == 'NURBS':
                            for p in s.points:
                                co = p.co.copy()
                                co.resize_3d()
                                if p.select:
                                    cos.append(obj_mtx @ co)

            if context.object.type == "GPENCIL":
                for gplayer in context.object.data.layers:
                    for frame in gplayer.frames:
                        for stroke in frame.strokes:
                            for p in stroke.points:
                                if p.select:
                                    cos.append(obj_mtx @ p.co)

            if len(cos) > 1:
                self.use_blender_tf()
                bpy.ops.view3d.snap_cursor_to_selected()
            else:
                bpy.ops.view3d.snap_cursor_to_center()

            # Bleh
            if cos and context.object.type == "GPENCIL":
                bpy.ops.gpencil.snap_cursor_to_selected()

        #
        # EDIT MESH
        #
        if context.mode == "EDIT_MESH":
            sel_mode = context.tool_settings.mesh_select_mode[:]
            obj = context.edit_object
            obj_mtx = obj.matrix_world.copy()
            mtx_inv = obj_mtx.inverted_safe().transposed().to_3x3()
            bm = bmesh.from_edit_mesh(obj.data)

            active, sel_verts, sel_edges, sel_faces = bm_selections(bm, sel_mode)
            vert_count = len(sel_verts)

            # JUST RESET CURSOR IF NO ELEMENTS ARE SELECTED
            if vert_count == 0:
                bpy.ops.view3d.snap_cursor_to_center()
                return {'FINISHED'}

            # VARs
            vert_coords = [v.co for v in sel_verts]
            pos = average_vector(vert_coords)
            self.pos = obj_mtx @ pos
            lf = set([i for j in [v.link_faces for v in sel_verts] for i in j])
            if lf:
                self.lfavgpos = obj_mtx @ average_vector([f.calc_center_median().freeze() for f in lf])
            z = y = x = Vector()

            # PROCESS
            if sel_faces and sel_mode[2]:
                # print("[FACE MODE]")
                if len(sel_faces) > 1:
                    fn = [mtx_inv @ f.normal for f in sel_faces]
                    # Check faces facing each other
                    active_only = False
                    for f in fn:
                        for of in fn:
                            d = f.dot(of)
                            if d < 0:
                                active_only = True
                                break
                    if active_only:
                        # print("Z: Facing vectors cancelling out - using active only")
                        z = active.normal
                        y = active.calc_tangent_edge_diagonal()
                        x = z.cross(y).normalized()
                        self.set_cursor(obj_mtx @ Matrix((x, y, z)).to_4x4().inverted_safe())
                    else:
                        self.use_blender_tf()
                else:
                    self.use_blender_tf()

            elif sel_mode[1] and sel_edges:
                # print("[EDGE MODE]")
                edge_vec = (active.verts[1].co - active.verts[0].co).normalized()
                sel_edge_count = len(sel_edges)
                if lf:
                    self.lfn = average_vector([i.normal for j in [e.link_faces for e in sel_edges] for i in j])

                if sel_edge_count == 1:
                    # print("Z: 1-EDGE ALIGNED")
                    if lf:
                        self.use_blender_tf()
                    else:
                        z = edge_vec
                        y = active.verts[0].normal
                        x = y.cross(z).normalized()

                if sel_edge_count == 2:
                    # print("Z: 2-EDGE CROSS special")
                    elf = [i for j in [e.link_faces for e in sel_edges] for i in j]
                    shared = [f for f in elf if elf.count(f) > 1]
                    if shared:
                        z = shared[0].normal
                        y = edge_vec
                        x = z.cross(y).normalized()
                    elif self.lfn and not [e for e in sel_edges if e.is_boundary]:
                        x = edge_vec
                        z = self.lfn
                        y = x.cross(z).normalized()
                    else:
                        h_vert = [v for v in sel_verts if v not in active.verts][0]
                        h = (h_vert.co - active.verts[0].co).normalized()
                        z = edge_vec.cross(h).normalized()
                        y = z.cross(edge_vec)
                        x = edge_vec
                    rot = obj_mtx @ Matrix((y, x, z)).to_4x4().inverted_safe()
                    self.set_cursor(rot)

                else:
                    if not lf:
                        # WIRE EDGES (not in a straight line)
                        self.use_blender_tf()
                    else:
                        # EDGES (W. LINKFACES, INCL BORDER EDGES)
                        edges = set(sel_edges)
                        edges = [e for e in edges if e != active]

                        le = set()
                        for v in sel_verts:
                            for vle in v.link_edges:
                                le.add(vle)
                        edges += list(le)

                        # Find good vecs for crossp from the edges selected (& linked)
                        best_vec = Vector(), 9
                        for e in edges:
                            vec = (e.verts[0].co - e.verts[1].co).normalized()
                            d = abs(round(vec.dot(edge_vec), 5))
                            if d < best_vec[1]:
                                best_vec = vec, d
                                if d == 0:
                                    break

                        if best_vec[1] > 0:
                            # print("No good crossp vec found - using blender default tf")
                            self.use_blender_tf()
                        else:
                            y = best_vec[0]
                            x = edge_vec
                            z = x.cross(y).normalized()

                # APPLY EDGES MODES
                if self.apply_custom:
                    self.set_cursor(obj_mtx @ Matrix((x, y, z)).to_4x4().inverted_safe())

            else:
                if vert_count == 2:
                    # print("[2-VERTEX MODE]")
                    other_vert = [v for v in sel_verts if v != active][0]
                    z = (active.co - other_vert.co).normalized()
                    y = z.orthogonal()
                    x = z.cross(y).normalized()
                    self.set_cursor(obj_mtx @ Matrix((y, x, z)).to_4x4().inverted_safe())
                else:
                    # print("[VERTEX / FALL-BACK MODE] (Blender Custom Transform)")
                    self.use_blender_tf()

        #
        # OBJECT MODE
        #
        elif context.mode == "OBJECT":
            # print("[OBJECT MODE]")
            sel_obj = [o for o in context.selected_objects]
            active_object = context.active_object if context.active_object in sel_obj else None
            hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

            # excluding if mod deform/ change the mesh's location to avoid any None type errror. contrib: Wahyu Nugraha
            m_deform = ['ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANDEFORM', 'LATTICE', 'MESH_DEFORM',
                        'SHRINKWRAP',
                        'SIMPLE_DEFORM', 'SMOOTH', 'CORRECTIVE_SMOOTH', 'LAPLACIANSMOOTH', 'SURFACE_DEFORM', 'WARP',
                        'WAVE']

            if hit_normal and hit_obj:
                mfs = []
                # Terrible workaround for raycast index issue
                if len(hit_obj.modifiers) > 0:
                    for m in hit_obj.modifiers:
                        if m.show_viewport and m.type not in m_deform:
                            mfs.append(m)
                            m.show_viewport = False
                    # casting again for unevaluated index (TBD: better method)
                    hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

                obj_mtx = hit_obj.matrix_world.copy()

                if not is_tf_applied(hit_obj)[2]:
                    scale_check = False
                else:
                    scale_check = True

                bm = bmesh.new()
                bm.from_mesh(hit_obj.data)
                bm.faces.ensure_lookup_table()

                normal = bm.faces[hit_face].normal
                tangent = bm.faces[hit_face].calc_tangent_edge_diagonal()
                self.pos = obj_mtx @ bm.faces[hit_face].calc_center_median()

                rot_mtx = rotation_from_vector(normal, tangent, rw=True)
                rot_mtx = obj_mtx @ rot_mtx
                self.set_cursor(rot_mtx)
                # restore vis for workaround
                if mfs:
                    for m in mfs:
                        m.show_viewport = True
            else:
                # NO HIT SELECTION
                if len(sel_obj) == 1:
                    self.pos = sel_obj[0].matrix_world.to_translation()
                    self.set_cursor(sel_obj[0].matrix_world)

                elif len(sel_obj) == 2:
                    # print("2 OBJ - ALIGN (TOWARDS ACTIVE)")
                    self.pos = average_vector([o.matrix_world.to_translation() for o in sel_obj])
                    if active_object is not None:
                        if sel_obj[0] == active_object:
                            target, start = active_object, sel_obj[-1]
                        else:
                            target, start = active_object, sel_obj[0]
                    else:
                        start, target = sel_obj[0], sel_obj[-1]
                    z = (target.location - start.location).normalized()
                    y = z.orthogonal()
                    x = z.cross(y).normalized()
                    rot = Matrix((y, x, z)).to_4x4().inverted_safe()
                    self.set_cursor(rot)

                elif len(sel_obj) >= 3:
                    # print("3+ OBJ - ALIGN (AS LAST)")
                    self.pos = average_vector([o.matrix_world.to_translation() for o in sel_obj])
                    if active_object:
                        rot = active_object.matrix_world
                    else:
                        rot = sel_obj[-1].matrix_world
                    self.set_cursor(rot)
                else:
                    # print("NO SELECTION -> RESET")
                    bpy.ops.view3d.snap_cursor_to_center()

        if not self.keep_cursor_tf:
            self.restore_cursor()

        if not scale_check:
            self.report({"INFO"}, "Object Scale is not applied")

        #
        # MODAL AXIS PREVIEW
        #
        if use_axis_gizmo:
            # Calc Axis size - Just some % relative to screen res Y
            cpos = context.scene.cursor.location
            # TBD: something smarter...
            h = context.region.height
            self.axis_line_length = (h * 0.015) / h
            p1, p2 = (0, h), (0, int(h - self.axis_line_length))
            v1 = region_2d_to_location_3d(context.region, context.region_data, p1,
                                          cpos)
            v2 = region_2d_to_location_3d(context.region, context.region_data, p2,
                                          cpos)

            # Cursor Axis coords
            d = get_distance(v1, v2)
            self.axis_line_length = d * 70

            cmtx = context.scene.cursor.rotation_euler.to_matrix()
            x_vec, y_vec, z_vec = vector_from_matrix(cmtx)
            self.axis_lines = [
                (cpos, cpos + (x_vec * self.axis_line_length)),
                (cpos, cpos + (y_vec * self.axis_line_length)),
                (cpos, cpos + (z_vec * self.axis_line_length))
            ]

            # Prep for GPU draw & run Modal
            self.shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            bpy.app.handlers.frame_change_post.clear()

            args = (self, context)
            self._handle_view = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_view, args, 'WINDOW', 'POST_VIEW')

            wm = context.window_manager
            self._timer = wm.event_timer_add(time_step=0.004, window=context.window)
            wm.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        return {"FINISHED"}

    def modal(self, context, event):
        if context.area and event.type == 'TIMER':
            if self._timer.time_duration > 10:
                self.end = True
            else:
                self.start_time = self._timer.time_duration

        if event.type in {"MOUSEMOVE", "MOUSEROTATE", "WHEELUPMOUSE", "WHEELDOWNMOUSE", "INBETWEEN_MOUSEMOVE"}:
            return {'PASS_THROUGH'}

        elif event.type in {"LEFTMOUSE", "MIDDLEMOUSE", "RIGHTMOUSE"} and self.start_time > 0.2:
            self.end = True
            return {'PASS_THROUGH'}

        elif event.type not in {"NONE", "TIMER"} and self.start_time > 0.2:
            self.quit()
            return {'FINISHED'}

        if self.end:
            self.quit()
            return {'FINISHED'}

        return {'RUNNING_MODAL'}
