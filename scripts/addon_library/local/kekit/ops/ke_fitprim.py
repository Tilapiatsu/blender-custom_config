from cmath import sqrt as cmath_sqrt
from math import cos, pi, sqrt
import blf
import bmesh
import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.view3d_utils import (
    region_2d_to_location_3d,
    region_2d_to_vector_3d,
    location_3d_to_region_2d
)
from bpy_types import Panel, Operator
from mathutils import Vector, Matrix
from mathutils.geometry import intersect_ray_tri
from .._utils import (
    vertloops,
    average_vector,
    get_distance,
    correct_normal,
    get_midpoint,
    get_closest_midpoint,
    rotation_from_vector,
    point_to_plane,
    get_selection_islands,
    mouse_raycast,
    pie_pos_offset,
    flatten,
    tri_order,
    set_active_collection,
    set_status_text,
    get_view_type,
    get_prefs
)


class UIFitPrimModule(Panel):
    bl_idname = "UI_PT_M_FITPRIM"
    bl_label = "FitPrim"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_GEO"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Cube", icon="MESH_CUBE").ke_fitprim_option = "BOX"
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Cylinder", icon="MESH_CYLINDER").ke_fitprim_option = "CYL"
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Plane", icon="MESH_PLANE").ke_fitprim_option = "PLANE"
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Sphere", icon="MESH_UVSPHERE").ke_fitprim_option = "SPHERE"
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim QuadSphere", icon="SPHERE").ke_fitprim_option = "QUADSPHERE"
        col.separator()
        col.label(text="Options")
        col.prop(k, "fitprim_unit", text="No-sel Unit Size")
        col.separator()
        col.prop(k, "fitprim_sides", text="Cylinder Default Sides:")
        col.prop(k, "fitprim_modal", text="Modal Cylinder")
        col.prop(k, "fitprim_sphere_seg", text="Sphere Segments")
        col.prop(k, "fitprim_sphere_ring", text="Sphere Rings")
        col.prop(k, "fitprim_quadsphere_seg", text="QuadSphere Div")
        col.prop(k, "fitprim_select", text="Select Result (Edit Mesh)")
        col.prop(k, "fitprim_item", text="Make Object")


def draw_callback_px(self, context, pos):
    val = self.cyl_sides
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
        blf.draw(font_id, "Cylinder Sides: " + str(val))
    else:
        context.workspace.status_text_set(None)
        return {'CANCELLED'}


def find_height(p1, p2, b, c):
    # Using Heron's formula w bizarre cmath workarounds imsure
    a = max(p1, p2) - min(p1, p2)
    s = (a + b + c) / 2
    area = cmath_sqrt(s * (s - a) * (s - b) * (s - c))
    area = round(float(area.real + area.imag), 4)
    if area == 0 or a == 0:
        return None
    else:
        return (area * 2) / a


def get_shortest(wmat, edges):
    s = []
    for e in edges:
        verts = e.verts
        v1, v2 = wmat @ verts[0].co, wmat @ verts[1].co
        d = round(get_distance(v1, v2), 4)
        s.append(d)
    return sorted(s)[0]


def get_sides(obj_mtx, vecs, vps):
    psides = []  # parallell sides
    start_vec = []
    h, p1, p2, b, c = None, None, None, None, None
    # center, side = None, None
    s1 = [Vector((0, 0, 0)), Vector((0, 0, 1))]
    os1 = [Vector((1, 0, 0)), Vector((0, 0, 1))]

    # Find sides...improvised mess, optimize later...maybe
    dotsum = 0
    for i, v in enumerate(vecs):
        osides = []
        rem = []

        # detect cylinderish ngon
        for oi, ov in enumerate(vecs):
            d = round(abs(v.dot(ov)), 4)
            if d == 1 and vps[i] != vps[oi]:
                osides.append(vps[oi])
                rem.extend(ov)
                dotsum += d

        if osides:
            p = [vps[i]] + osides
            psides.append(p)
            for r in rem:
                if r in vecs:
                    vecs.remove(r)
    if psides:
        s = vertloops(psides[0])
        if len(s) == 2:
            if s[1]:
                s1 = [obj_mtx @ v.co for v in s[0]]
                s2 = [obj_mtx @ v.co for v in s[1]]
                p1 = round(get_distance(s1[0], s1[-1]), 4)
                p2 = round(get_distance(s2[0], s2[-1]), 4)
            else:
                # print("failsafe")
                s1 = [obj_mtx @ v.co for v in s[0]]
                p1 = round(get_distance(s1[0], s1[-1]), 4)
                p2 = p1

        other_sides = [i for i in vps if i not in psides[0]]
        os = vertloops(other_sides)

        if len(os) == 2:
            if os[1]:
                os1 = [obj_mtx @ v.co for v in os[0]]
                os2 = [obj_mtx @ v.co for v in os[1]]
                b = round(get_distance(os1[0], os1[-1]), 4)
                c = round(get_distance(os2[0], os2[-1]), 4)
                v1 = Vector((os1[0] - os1[-1])).normalized()
                v2 = Vector((os2[0] - os2[-1])).normalized()
                p = round(abs(v1.dot(v2)), 4)
                # check if not parallel for trapezoid
                # print("other sides dot", p)
                if p != 1:
                    h = find_height(p1, p2, b, c)

    vcos = list(set(flatten(vps)))
    poslist = [obj_mtx @ v.co for v in vcos]
    center = Vector(average_vector(poslist))

    if dotsum == len(vps) and dotsum != 4:
        # cylinder, probably. ->ngon
        h, p1, p2 = None, None, None

    if h is not None:
        # print("Trapezoid mode")
        side = h
        start_vec = Vector((s1[0] - s1[-1])).normalized()

    elif p1 and p2:
        # print("Rectangle mode")
        if p1 < p2:
            side = p1
        else:
            side = p2

        start_vec = Vector((s1[0] - s1[-1])).normalized()

        if b and c:
            # Re-swap to shorter side for rec fit
            if sum((b, c)) < sum((p1, p2)):
                if b < c:
                    side = b
                else:
                    side = c
                start_vec = Vector((os1[0] - os1[-1])).normalized()

    else:
        # print("Ngon mode")
        radpos = poslist[0]
        rad = get_distance(center, radpos)
        pi_rad = rad * cos(pi / len(vps))
        side = pi_rad * 2

    if not start_vec:
        # print("Start-vec failsafe")
        start_vec = vecs[0]

    # Weighted center override
    if h is None:
        avg = Vector()
        w = 0
        for vp in vps:
            d = get_distance(vp[0].co, vp[1].co)
            avgp = average_vector((obj_mtx @ vp[0].co, obj_mtx @ vp[1].co))
            avg += avgp * d
            w += d
        center = avg / w

    return side, center, start_vec


class KeFitPrim(Operator):
    bl_idname = "view3d.ke_fitprim"
    bl_label = "FitPrim"
    bl_description = "Creates (unit or unit+height) box or cylinder primitve based on selection (or not = ground)\n" \
                     "VERTEX: Fits *along* 2 Selected verts\n" \
                     "EDGE: Fits *in* selection(s) \n" \
                     "POLY: Fits *on* selection(s)"
    bl_options = {'REGISTER', 'UNDO'}

    ke_fitprim_option : EnumProperty(
        items=[("BOX", "Box Mode", "", 1),
               ("CYL", "Cylinder Mode", "", 2),
               ("SPHERE", "UV Sphere", "", 3),
               ("QUADSPHERE", "QuadSphere", "", 4),
               ("PLANE", "Plane", "", 5)
               ],
        name="FitPrim Options",
        default="BOX")

    ke_fitprim_pieslot : StringProperty(
        default="NONE",
        description="Pie-Slot Mouse Offset")

    ke_fitprim_itemize : BoolProperty(
        name="Make Object", description="Makes new object also from Edit mode", default=False)

    itemize = False
    boxmode = True
    sphere = False
    world = False
    settings = (0, 0, 0)
    _handle = None
    _timer = None
    cyl_sides = 16
    unit = .1
    is_modal = True
    select = True
    screen_x = 0
    sphere_seg = 32
    sphere_ring = 16
    quadsphere_seg = 4
    mouse_pos = Vector((0, 0))
    edit_mode = ""
    hcol = (1, 1, 1, 1)
    tcol = (1, 1, 1, 1)
    scol = (1, 1, 1, 1)
    fs = [64, 64, 110, 64, 20, 15, 40, 20, 10]
    og_cloc = []
    og_crot = []
    tick = 0
    tock = 0
    input_nrs = []

    numbers = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE')
    numpad = ('NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7',
              'NUMPAD_8', 'NUMPAD_9')

    # @classmethod
    # def poll(cls, context):
    #     return context.object is not None

    def draw(self, context):
        layout = self.layout

    def invoke(self, context, event):
        self.screen_x = int(context.region.width * 0.5)
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)
        # Pie-Menu offset compensations:
        if self.ke_fitprim_pieslot:
            self.mouse_pos = pie_pos_offset(self.mouse_pos, self.ke_fitprim_pieslot)
            self.ke_fitprim_pieslot = "NONE"
        return self.execute(context)

    def modal(self, context, event):
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

                if val < 3:
                    val = 3

                if val != self.cyl_sides:
                    self.cyl_sides = val
                    bpy.ops.mesh.delete(type='FACE')
                    bpy.ops.mesh.primitive_cylinder_add(vertices=self.cyl_sides, radius=self.settings[0],
                                                        depth=self.settings[1] * 2, enter_editmode=False, align='WORLD',
                                                        location=self.settings[2], rotation=self.settings[3])
                    context.area.tag_redraw()
                    self.input_nrs = []

        if event.type == 'WHEELUPMOUSE' and 2 < self.cyl_sides < 256:
            self.cyl_sides += 1
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.mesh.primitive_cylinder_add(vertices=self.cyl_sides, radius=self.settings[0],
                                                depth=self.settings[1] * 2, enter_editmode=False, align='WORLD',
                                                location=self.settings[2], rotation=self.settings[3])
            context.area.tag_redraw()

        elif event.type == 'WHEELDOWNMOUSE' and 3 < self.cyl_sides < 256:
            self.cyl_sides -= 1
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.mesh.primitive_cylinder_add(vertices=self.cyl_sides, radius=self.settings[0],
                                                depth=self.settings[1] * 2, enter_editmode=False, align='WORLD',
                                                location=self.settings[2], rotation=self.settings[3])
            context.area.tag_redraw()

        elif event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                event.alt and event.type == "RIGHTMOUSE" or \
                event.shift and event.type == "MIDDLEMOUSE" or \
                event.ctrl and event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}

        elif event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'ESC', 'RET', 'SPACE'}:
            context.area.tag_redraw()
            context.window_manager.event_timer_remove(self._timer)

            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            if self.itemize or self.edit_mode == "OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.shade_smooth()
                context.object.data.use_auto_smooth = True
                # bpy.ops.view3d.snap_cursor_to_center()
                cursor = context.scene.cursor
                cursor.location = self.og_cloc
                cursor.rotation_euler = self.og_crot

            if not self.select and not self.itemize and not self.edit_mode == "OBJECT":
                bpy.ops.mesh.select_all(action='DESELECT')

            context.space_data.overlay.show_cursor = True
            self.ke_fitprim_itemize = False
            context.workspace.status_text_set(None)

            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        k = get_prefs()
        self.hcol = k.modal_color_header
        self.tcol = k.modal_color_text
        self.scol = k.modal_color_subtext
        scale_factor = context.preferences.view.ui_scale * k.ui_scale
        self.fs = [int(round(n * scale_factor)) for n in self.fs]

        if self.ke_fitprim_option == "BOX":
            self.boxmode, self.world = True, False
        elif self.ke_fitprim_option == "CYL":
            self.boxmode, self.world = False, False
        elif self.ke_fitprim_option == "SPHERE":
            self.boxmode, self.world, self.sphere = False, False, True
        elif self.ke_fitprim_option == "QUADSPHERE":
            self.boxmode, self.world, self.sphere = False, False, True
        else:
            self.boxmode, self.world, self.sphere = False, False, False

        if k.fitprim_item:
            self.itemize = True
        else:
            self.itemize = self.ke_fitprim_itemize

        self.is_modal = k.fitprim_modal
        self.cyl_sides = k.fitprim_sides
        self.select = k.fitprim_select
        self.unit = round(k.fitprim_unit, 4)
        self.sphere_ring = k.fitprim_sphere_ring
        self.sphere_seg = k.fitprim_sphere_seg
        self.quadsphere_seg = k.fitprim_quadsphere_seg

        self.edit_mode = context.mode
        sel_mode = (False, False, False)
        sel_verts = []
        sel_verts2 = []
        multi_object_mode = False
        non_mesh_clones = []
        side = []
        island_mode = False

        cursor = context.scene.cursor
        self.og_cloc = cursor.location.copy()
        self.og_crot = cursor.rotation_euler.copy()
        og_orientation = str(context.scene.transform_orientation_slots[0].type)

        if self.itemize or self.edit_mode == "OBJECT" and context.object is not None:
            set_active_collection(context, context.object)

        #
        # MULTI OBJECT CHECK & SETUP
        #
        if self.edit_mode == "EDIT_MESH" and context.object:
            sel_mode = [b for b in context.tool_settings.mesh_select_mode]
            other_side = []
            sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
            if len(sel_obj) == 2:
                multi_object_mode = True

            obj = context.active_object
            obj_mtx = obj.matrix_world.copy()
            second_obj = []

            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()
            bm.verts.ensure_lookup_table()

            sel_verts = [v for v in bm.verts if v.select]

            if sel_mode[2]:
                sel_poly = [p for p in bm.faces if p.select]
                active_face = bm.faces.active
                if active_face not in sel_poly:
                    active_face = None

            if multi_object_mode:
                second_obj = [o for o in sel_obj if o != obj][0]
                bm2 = bmesh.from_edit_mesh(second_obj.data)
                obj_mtx2 = second_obj.matrix_world.copy()

                sel_poly2 = [p for p in bm2.faces if p.select]
                if sel_poly2:
                    active_face2 = bm2.faces.active
                    if active_face2 not in sel_poly2:
                        active_face2 = None
                    if active_face2:
                        sel_verts2 = active_face2.verts
                    else:
                        sel_verts2 = sel_poly2[0].verts
                        active_face2 = sel_poly2[0]  # haxxfixxx
                else:
                    sel_verts2 = [v for v in bm2.verts if v.select]

                if not sel_verts2:
                    multi_object_mode = False

                elif sel_mode[0]:
                    # Just for 2-vert mode in multiobj mode
                    ole = sel_verts2[0].link_edges[:]
                    other_side = get_shortest(obj_mtx2, ole)

            side = None
            distance = 0
            normal, setpos, setrot, center = None, None, None, None

        #
        # NO SELECTION MODE
        #
        if not sel_verts or self.edit_mode == "OBJECT":

            # todo: (Linux only?) "pie menu op refuses to grab event data in invoke (or something) bug? temp-workaround:
            if self.screen_x == 0:
                print("FitPrim: Pie-Invoke/Event Bug. Congratulations. Fallback: Context Object used for mousepos ref.")
                cpos = average_vector([Vector(i) for i in context.object.bound_box])
                self.mouse_pos = location_3d_to_region_2d(context.region, context.region_data, cpos)

            # Check mouse over target
            if not self.edit_mode == "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")

            hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos, evaluated=True)

            if not self.edit_mode == "OBJECT":
                bpy.ops.object.mode_set(mode="EDIT")

            if self.edit_mode != "OBJECT" and hit_obj is not None:
                hit_obj.update_from_editmode()

                if len(hit_obj.modifiers) > 0:
                    self.report({"INFO"}, "FitPrim: Selected elements required in Edit Mode if Modifiers exist")
                    return {"CANCELLED"}

            if hit_obj and hit_face is not None:
                # mouse over placement on face
                self.world = False
                mtx = hit_obj.matrix_world
                eks = hit_obj.data.polygons[hit_face].edge_keys
                vecs = []

                for vp in eks:
                    vc1 = mtx @ hit_obj.data.vertices[vp[0]].co
                    vc2 = mtx @ hit_obj.data.vertices[vp[1]].co
                    vecs.append(Vector(vc1 - vc2).normalized())

                evps = []
                for vp in eks:
                    v1, v2 = hit_obj.data.vertices[vp[0]], hit_obj.data.vertices[vp[1]]
                    evps.append([v1, v2])

                side, center, start_vec = get_sides(mtx, vecs, evps)

                if self.ke_fitprim_option == "PLANE" and self.edit_mode == "OBJECT":
                    setpos = center
                    # setpos = mtx @ hit_obj.data.polygons[hit_face].center
                    side *= 2

                else:
                    offset = hit_normal * (side / 2)
                    setpos = center + offset
                    # setpos = mtx @ hit_obj.data.polygons[hit_face].center + offset

                setrot = rotation_from_vector(hit_normal, start_vec)

            else:
                # VOID SIZE CLONE MODE
                void_size_clone = 0
                if self.edit_mode == "OBJECT":
                    sel_obj = context.selected_objects[:]
                    if sel_obj:
                        bounds_x, bounds_y, bounds_z = [], [], []
                        for o in sel_obj:
                            if o.type == "MESH":
                                for b in o.bound_box:
                                    bb = o.matrix_world @ Vector(b)
                                    bounds_x.append(bb[0])
                                    bounds_y.append(bb[1])
                                    bounds_z.append(bb[2])
                            else:
                                non_mesh_clones.append(o)
                        if bounds_x:
                            bounds_x, bounds_y, bounds_z = sorted(bounds_x), sorted(bounds_y), sorted(bounds_z)
                            d = sorted(
                                [bounds_x[-1] - bounds_x[0], bounds_y[-1] - bounds_y[0], bounds_z[-1] - bounds_z[0]])
                            void_size_clone = d[-1]

                # view placement compensation & Z0 drop
                view_vec = region_2d_to_vector_3d(context.region, context.space_data.region_3d, self.mouse_pos)
                view_pos = context.space_data.region_3d.view_matrix.inverted().translation
                raypos = []

                if get_view_type() != "ORTHO":
                    ground = ((0, 0, 0), (0, 1, 0), (1, 0, 0))
                    raypos = intersect_ray_tri(ground[0], ground[1], ground[2], view_vec, view_pos, False)
                    snap_val = str(self.unit).split('.')
                    if int(snap_val[0]) > 0:
                        snap = 0
                    else:
                        snap = len(snap_val[1])

                if raypos:
                    setpos = Vector((round(raypos[0], snap), round(raypos[1], snap), self.unit / 2))
                else:
                    setpos = region_2d_to_location_3d(context.region, context.space_data.region_3d, self.mouse_pos,
                                                      view_vec)

                if non_mesh_clones and void_size_clone == 0:
                    bpy.ops.object.duplicate()
                    new = context.selected_objects
                    # Calc offsets if more than one
                    vecs, offsets = [], []
                    if len(new) > 1:
                        cpos = average_vector([o.location for o in new])
                        for o in new:
                            vecs.append(Vector((o.location - cpos)).normalized())
                            offsets.append(get_distance(o.location, cpos))
                    # Place
                    for i, o in enumerate(new):
                        pos = setpos
                        if offsets:
                            pos = setpos + (offsets[i] * vecs[i])
                        o.location = pos
                    return {"FINISHED"}

                self.world = True
                if void_size_clone > 0:
                    side = void_size_clone
                else:
                    side = self.unit
                if self.ke_fitprim_option == "PLANE" and self.edit_mode == "OBJECT":
                    side *= 2

            distance = side
            sel_mode = (True, False, False)

        #
        # VERT MODE(s)
        #
        elif sel_mode[0]:

            if len(sel_verts) == 1 and not multi_object_mode:
                # 1-VERT MODE
                self.world = True
                side = get_shortest(obj_mtx, sel_verts[0].link_edges[:])
                distance = side
                setpos = obj_mtx @ sel_verts[0].co

            elif len(sel_verts) == 2 and not multi_object_mode or \
                    multi_object_mode and len(sel_verts2) == 1 and len(sel_verts) == 1:
                # 2 Vert mode
                if multi_object_mode:
                    p1 = obj_mtx @ sel_verts[0].co
                    p2 = obj_mtx2 @ sel_verts2[0].co
                    side = [other_side]
                    con_edges = sel_verts[0].link_edges[:]
                    side.append(get_shortest(obj_mtx,  con_edges))
                    side = sorted(side)[0]
                else:
                    p1 = obj_mtx @ sel_verts[0].co
                    p2 = obj_mtx @ sel_verts[1].co
                    con_edges = sel_verts[0].link_edges[:] + sel_verts[1].link_edges[:]
                    side = get_shortest(obj_mtx, con_edges)

                v_1 = Vector(p1 - p2).normalized()
                v_2 = Vector((0, 0, 1))
                if round(abs(v_1.dot(v_2)), 4) == 1 :
                    v_2 = Vector((1, 0, 0))
                n_v = v_1.cross(v_2).normalized()
                u_v = n_v.cross(v_1).normalized()
                t_v = u_v.cross(n_v).normalized()

                setrot = Matrix((u_v, n_v, t_v)).to_4x4().inverted()
                distance = get_distance(p1, p2)
                setpos = Vector(get_midpoint(p1, p2))

            elif len(sel_verts) == 4 or multi_object_mode and len(sel_verts2) + len(sel_verts) <= 4:
                # 4-vert Rectangle mode
                # holy brute force batman
                if not second_obj:
                    second_obj = obj
                tri = tri_order(((obj, sel_verts), (second_obj, sel_verts2)))
                q = tri[-1]
                # just placing a unit prim with min side in the center (for this one) so disregarding other vecs
                v1 = Vector(tri[0][0].matrix_world @ tri[0][1].co - tri[1][0].matrix_world @ tri[1][1].co)
                v2 = Vector(tri[0][0].matrix_world @ tri[0][1].co - tri[2][0].matrix_world @ tri[2][1].co)
                d1 = get_distance(tri[0][0].matrix_world @ tri[0][1].co, tri[1][0].matrix_world @ tri[1][1].co)
                d4 = get_distance(q[0].matrix_world @ q[1].co, tri[2][0].matrix_world @ tri[2][1].co)

                if d1 < d4:
                    side = d1
                else:
                    side = d4
                distance = side

                ap1 = average_vector([obj_mtx @ v.co for v in sel_verts])
                if sel_verts2:
                    ap2 = average_vector([obj_mtx2 @ v.co for v in sel_verts2])
                    setpos = average_vector((ap1, ap2))
                else:
                    setpos = ap1

                n = v1.normalized().cross(v2.normalized())
                u = n.cross(v1.normalized())
                t = u.cross(n)
                setrot = Matrix((u, n, t)).to_4x4().inverted()

            else:
                self.report({"INFO"}, "FitPrim: Invalid Vert Mode Selection: Select 1, 2 or 4 verts")
                return {"CANCELLED"}

        #
        # EDGE MODE
        #
        elif sel_mode[1]:

            one_line, loops, loops2 = False, [], []
            sel_edges = [e for e in bm.edges if e.select]
            vps = [e.verts[:] for e in sel_edges]

            active_edge = bm.select_history.active
            if active_edge:
                active_edge_facenormals = [correct_normal(obj_mtx, p.normal) for p in active_edge.link_faces]
                active_edge_normal = Vector(average_vector(active_edge_facenormals)).normalized()

            # GET ISLANDS
            if multi_object_mode and active_edge:
                # print("multi obj mode") # todo: limited multiobj mode, rework one-for-all?
                sel_edges2 = [e for e in bm2.edges if e.select]
                vps2 = [e.verts for e in sel_edges2]
                p1 = vertloops(vps)
                p2 = vertloops(vps2)
                if p1 and p2:
                    a1, a2 = obj_mtx @ p1[0][0].co, obj_mtx @ p1[0][-1].co
                    b1, b2 = obj_mtx2 @ p2[0][0].co, obj_mtx2 @ p2[0][-1].co
                else:
                    a1, a2 = obj_mtx @ sel_verts[0].co, obj_mtx @ sel_verts[-1].co
                    b1, b2 = obj_mtx2 @ sel_verts2[0].co, obj_mtx2 @ sel_verts2[-1].co

                b_avg = get_midpoint(b1, b2)
                spacing, mp = get_closest_midpoint(a1, a2, b_avg)

                u_v = Vector(a1 - b1).normalized()
                t_v = Vector(a1 - a2).normalized()
                n_v = u_v.cross(t_v).normalized()

                setrot = rotation_from_vector(n_v, t_v, rotate90=True)
                setpos = mp
                side = spacing
                distance = spacing

            elif active_edge:  # same (active) obj island selections
                if len(sel_edges) > 1:

                    if len(sel_edges) == 2 and not bool(set(sel_edges[0].verts).intersection(sel_edges[1].verts)):
                        a1p, a2p = sel_edges[0].verts, sel_edges[1].verts
                        a1, a2 = obj_mtx @ a1p[0].co, obj_mtx @ a1p[1].co
                        b_avg = average_vector([obj_mtx @ a2p[0].co, obj_mtx @ a2p[1].co])

                        lf1 = sel_edges[0].link_faces[:]
                        lf = [f for f in sel_edges[1].link_faces[:] if f in lf1]

                        v1 = Vector((obj_mtx @ a1p[0].co - obj_mtx @ a1p[1].co)).normalized()

                        if not lf:
                            u_v = Vector(a1 - (obj_mtx @ a2p[0].co)).normalized()
                            t_v = Vector(a1 - a2).normalized()
                            n_v = u_v.cross(t_v).normalized()
                            setrot = rotation_from_vector(n_v, t_v, rotate90=True)
                        else:
                            n = correct_normal(obj_mtx, lf[0].normal)
                            t = v1
                            setrot = rotation_from_vector(n, t, rotate90=True)

                        spacing, mp = get_closest_midpoint(a1, a2, b_avg)
                        setpos = mp
                        side = spacing
                        distance = spacing
                    else:
                        loops = vertloops(vps)

                if len(loops) > 1:
                    # print ("single obj - multi loop", len(loops))
                    # Check for closed loops
                    a_ep1, a_ep2 = loops[0][0], loops[0][-1]
                    b_ep1, b_ep2 = loops[1][0], loops[1][-1]
                    if a_ep1 == a_ep2:
                        a_ep2 = loops[0][-2]
                    if b_ep1 == b_ep2:
                        b_ep2 = loops[1][-2]

                    # get coords & set vals
                    a1, a2 = obj_mtx @ a_ep1.co, obj_mtx @ a_ep2.co
                    b1, b2 = obj_mtx @ b_ep1.co, obj_mtx @ b_ep2.co

                    b_avg = get_midpoint(b1, b2)
                    spacing, mp = get_closest_midpoint(a1, a2, b_avg)

                    u_v = Vector((0, 0, 1))
                    t_v = Vector(a1 - a2).normalized()
                    if abs(u_v.dot(t_v)) == 1:
                        u_v = Vector((1, 0, 0))

                    n_v = u_v.cross(t_v).normalized()

                    setrot = rotation_from_vector(n_v, t_v, rotate90=False)
                    setpos = mp
                    side = spacing
                    distance = spacing

                elif len(loops) == 1 or len(sel_edges) == 1:
                    # print ("single obj - single loop")
                    single_line = False
                    if len(sel_edges) != 1:
                        if loops[0][0] != loops[0][-1]:
                            single_line = True

                    if len(sel_edges) != 1 and not single_line:
                        vecs = [Vector((obj_mtx @ vp[0].co) - (obj_mtx @ vp[1].co)).normalized() for vp in vps]
                        normal = average_vector([correct_normal(obj_mtx, v.normal) for v in flatten(vps)])

                        side, center, start_vec = get_sides(obj_mtx, vecs, vps)
                        distance = side
                        setpos = center
                        setrot = rotation_from_vector(normal, start_vec)

                    elif len(sel_edges) == 1 or single_line:
                        # print("1 edge --> one line", one_line)
                        p1, p2 = obj_mtx @ sel_verts[0].co, obj_mtx @ sel_verts[1].co
                        t_v = Vector(p1 - p2).normalized()
                        n_v = active_edge_normal

                        setrot = rotation_from_vector(n_v, t_v)
                        distance = get_distance(p1, p2)
                        setpos = get_midpoint(p1, p2)
                        side = distance
                    else:
                        print("Unexpected: Aborting operation.")
                        return {'CANCELLED'}

        #
        # FACE MODE
        #
        elif sel_mode[2] and active_face and sel_poly:
            fail_island = False

            # GET ISLANDS
            if multi_object_mode and active_face:
                first_island = sel_verts
                point = obj_mtx @ active_face.calc_center_median()
                firstcos = [obj_mtx @ v.co for v in active_face.verts]
                secondcos = [obj_mtx2 @ v.co for v in active_face2.verts]

                if firstcos and secondcos:
                    island_mode = True

                    distance = point_to_plane(point, firstcos, secondcos)
                    if distance:
                        distance = abs(distance)
                    else:
                        # print("Multi obj Point to plane failed for some reason - using single island mode.")
                        # island_mode = False
                        fail_island = True

            elif len(sel_poly) > 1:  # same (active) obj island selections
                first_island, second_island = get_selection_islands(sel_poly, active_face)
                # Ofc, needs correct order for point to plane, and I'll just rely on face.verts for that:
                calc_island_1 = active_face.verts[:]
                calc_island_2 = []
                for p in sel_poly:
                    verts = p.verts[:]
                    for v in verts:
                        if v in second_island:
                            calc_island_2 = verts
                            break

                if len(first_island) != 0 and len(second_island) != 0:
                    firstcos = [obj_mtx @ v.co for v in calc_island_1]
                    secondcos = [obj_mtx @ v.co for v in calc_island_2]
                    distance = point_to_plane(obj_mtx @ active_face.calc_center_median(), firstcos, secondcos)

                    if distance:
                        distance = abs(distance)
                        island_mode = True
                    else:
                        # print("Point to plane failed for some reason - using single island mode.")
                        fail_island = True
                    # print(distance)
                else:
                    # Ngon mode
                    first_island = sel_verts

            # GETVALUES
            if island_mode or fail_island:
                bpy.ops.mesh.select_all(action='DESELECT')

                for v in first_island:
                    bm.verts[v.index].select = True

                bmesh.update_edit_mesh(obj.data)
                bpy.ops.mesh.select_mode(type='VERT')
                bpy.ops.mesh.select_mode(type='FACE')
                bm.faces.ensure_lookup_table()

            faces = [f for f in bm.faces if f.select]
            normal = average_vector([correct_normal(obj_mtx, f.normal) for f in faces])
            bpy.ops.mesh.region_to_loop()

            sel_edges = [e for e in bm.edges if e.select]
            vps = [e.verts[:] for e in sel_edges]
            vecs = [Vector((obj_mtx @ vp[0].co) - (obj_mtx @ vp[1].co)).normalized() for vp in vps]
            if vecs:
                side, center, start_vec = get_sides(obj_mtx, vecs, vps)
                setrot = rotation_from_vector(normal, start_vec)

        #
        # PROCESS
        #
        if side:
            if self.ke_fitprim_option == "PLANE" and self.edit_mode != "OBJECT":
                if sel_mode[2]:
                    setpos = center

            elif len(sel_verts) == 0 or sel_mode[0] or sel_mode[1]:
                side *= .5
                distance = distance / 2
                if self.sphere and sel_mode[0]:
                    if not len(sel_verts) == 0:
                        side = distance

            elif sel_mode[2]:
                if island_mode:
                    side *= .5
                    offset = normal * distance * .5
                    distance *= .5
                    if self.sphere:
                        side = distance
                else:
                    side *= .5
                    distance = side
                    offset = normal * side

                setpos = center + offset
                if not island_mode and self.sphere:
                    setpos = setpos - offset

            # SET FINAL ROTATION
            if self.world:
                setrot = (0, 0, 0)
                if self.ke_fitprim_option == "PLANE" and not sel_verts:
                    setpos[2] = 0
            else:
                setrot = setrot.to_euler()

            # RUN OP
            if not self.edit_mode == "OBJECT":
                bpy.ops.mesh.select_mode(type='FACE')

            if self.itemize:
                if self.edit_mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.transform.select_orientation(orientation='GLOBAL')
                cursor.location = setpos
                cursor.rotation_euler = setrot

            #
            # CUBE
            #
            if self.boxmode:
                bpy.ops.mesh.ke_primitive_box_add(width=side, depth=side, height=distance,
                                                  align='WORLD', location=setpos, rotation=setrot)
                if self.itemize or self.edit_mode == "OBJECT":
                    bpy.ops.object.shade_smooth()
                    context.object.data.use_auto_smooth = True

            #
            # PLANE
            #
            elif self.ke_fitprim_option == "PLANE":

                # side *= 2
                enter = True

                if self.edit_mode == 'OBJECT' or self.itemize:
                    enter = False

                bpy.ops.mesh.primitive_plane_add(enter_editmode=enter, align='WORLD', location=setpos,
                                                 rotation=setrot, size=side, scale=(1, 1, 1), calc_uvs=True)
                if self.itemize or self.edit_mode == "OBJECT":
                    bpy.ops.object.shade_smooth()
                    context.object.data.use_auto_smooth = True

            #
            # SPHERE
            #
            elif self.sphere and not self.ke_fitprim_option == "QUADSPHERE":
                bpy.ops.mesh.primitive_uv_sphere_add(segments=self.sphere_seg, ring_count=self.sphere_ring, radius=side,
                                                     align='WORLD', location=setpos, rotation=setrot)
                if self.itemize or self.edit_mode == "OBJECT":
                    bpy.ops.object.shade_smooth()
                    context.object.data.use_auto_smooth = True

            #
            # QUADSPHERE
            #
            elif self.ke_fitprim_option == "QUADSPHERE":
                cutnr = self.quadsphere_seg

                # calc compensated subd radius from cube
                v1_pos = setpos[0] + side, setpos[1] + side, setpos[2] + side
                rad = sqrt(sum([(a - b) ** 2 for a, b in zip(setpos, v1_pos)]))
                diff = side / rad

                side = (side * diff)
                distance = side

                bpy.ops.mesh.ke_primitive_box_add(width=side, depth=side, height=distance,
                                                  align='WORLD', location=setpos, rotation=setrot, name="QuadSphere")

                if self.itemize or self.edit_mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.subdivide(number_cuts=cutnr, smoothness=1)
                    bpy.ops.mesh.faces_shade_smooth()
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.mesh.subdivide(number_cuts=cutnr, smoothness=1)
                    bpy.ops.mesh.faces_shade_smooth()

                bpy.ops.ed.undo_push()
                # context.object.data.use_auto_smooth = as_check

                if self.itemize or self.edit_mode == "OBJECT":
                    bpy.ops.object.shade_smooth()
                    context.object.data.use_auto_smooth = True

            #
            # CYLINDER
            #
            else:
                bpy.ops.mesh.primitive_cylinder_add(vertices=self.cyl_sides, radius=side, depth=distance * 2,
                                                    enter_editmode=False, align='WORLD',
                                                    location=setpos, rotation=setrot)

                if self.is_modal:
                    if self.itemize or self.edit_mode == "OBJECT":
                        bpy.ops.object.mode_set(mode="EDIT")

                    self.settings = (side, distance, setpos, setrot)
                    context.window_manager.modal_handler_add(self)

                    self._timer = context.window_manager.event_timer_add(0.5, window=context.window)

                    args = (self, context, self.screen_x)
                    self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW',
                                                                          'POST_PIXEL')
                    context.space_data.overlay.show_cursor = False

                    # UPDATE STATUS BAR
                    status_help = [
                        "[WHEEL] Side Count",
                        "[MMB, ALT-MBs] Navigation",
                        "[ESC/ENTER/SPACEBAR LMB/RMB] Apply",
                        "[ESC/RMB] Cancel"]
                    set_status_text(context, status_help)

                    return {'RUNNING_MODAL'}

            if multi_object_mode and not self.itemize:
                second_obj.select_set(state=True)
                obj.select_set(state=True)
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()
        else:
            self.report({"INFO"}, "FitPrim: Invalid Selection / No Active Element?")

        if not self.select and not self.itemize and not self.edit_mode == "OBJECT":
            bpy.ops.mesh.select_all(action='DESELECT')

        if self.itemize:
            bpy.ops.transform.select_orientation(orientation=og_orientation)
            cursor.location = self.og_cloc
            cursor.rotation_euler = self.og_crot
            context.active_object.select_set(state=True)

        self.ke_fitprim_itemize = False
        return {"FINISHED"}
