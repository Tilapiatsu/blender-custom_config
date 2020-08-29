bl_info = {
    "name": "keFitPrim",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 3, 2),
    "blender": (2, 80, 0),
}
import bpy
import blf
import bmesh
from .ke_utils import get_loops, average_vector, get_distance, correct_normal, get_midpoint, get_closest_midpoint, \
    rotation_from_vector, point_to_plane, get_selection_islands
from mathutils import Vector, Matrix
from math import cos, pi
from bpy_extras.view3d_utils import region_2d_to_location_3d


# -------------------------------------------------------------------------------------------------------------------
def draw_callback_px(self, context, pos):
    val = self.cyl_sides
    hpos, vpos = 64, 64
    if pos: hpos = pos - 110
    if val:
        font_id = 0
        blf.enable(font_id, 4)
        blf.position(font_id, hpos, vpos + 64, 0)
        blf.color(font_id, 0.796, 0.7488, 0.6435, 1)
        blf.size(font_id, 20, 72)
        blf.shadow(font_id, 5, 0, 0, 0, 1)
        blf.shadow_offset(font_id, 1, -1)
        blf.draw(font_id, "Cylinder Sides: " + str(val))
        blf.size(font_id, 15, 72)
        blf.position(font_id, hpos, vpos + 40, 0)
        blf.color(font_id, 0.8, 0.8, 0.8, 1)
        blf.draw(font_id, "Increment: Mouse Wheel Up / Down")
        blf.position(font_id, hpos, vpos + 20, 0)
        blf.draw(font_id, "Apply:        LMB, RMB, Esc, Enter or Spacebar")
        blf.size(font_id, 10, 72)
        blf.position(font_id, hpos, vpos, 0)
        blf.color(font_id, 0.5, 0.5, 0.5, 1)
        blf.draw(font_id, "Navigation: Blender (-MMB) or Ind.Std (Alt-) Defaults Pass-Through")
    else:
        return {'CANCELLED'}


def get_sides(obj_mtx, start_vec, vecs, vps, legacy=True):
    side, center = 0.0, (0,0,0)
    sides = []
    for i, v in enumerate(vecs):
        vec = v
        if start_vec.dot(v) < 0:
            vec.negate()
        angle = start_vec.angle(vec)
        if -0.33 < angle < 0.33:
            sides.append(vps[i])

    sides = get_loops(sides, legacy)

    side_lengths = []

    if len(sides) == 2:
        # print("rectangle mode")
        v1 = round(get_distance(obj_mtx @ sides[0][0].co, obj_mtx @ sides[-1][0].co), 4)
        v2 = round(get_distance(obj_mtx @ sides[0][0].co, obj_mtx @ sides[0][-1].co), 4)
        v3 = round(get_distance(obj_mtx @ sides[0][0].co, obj_mtx @ sides[-1][-1].co), 4)
        side_lengths.append(v1)
        side_lengths.append(v2)
        side_lengths.append(v3)
        side = sorted(side_lengths)[0]
        poslist = [obj_mtx @ v.co for vertpair in vps for v in vertpair]
        center = Vector(average_vector(poslist))

    else:
        # print("ngon mode")
        poslist = [obj_mtx @ vp[0].co for vp in vps]
        radpos = poslist[0]
        center = Vector(average_vector(poslist))
        rad = get_distance(center, radpos)
        pi_rad = rad * cos(pi / len(vps))
        side = pi_rad * 2

    return side, sides, center


def get_shortest(wmat, edges):
    s = []
    for e in edges:
        verts = e.verts
        v1, v2 = wmat @ verts[0].co, wmat @ verts[1].co
        d = round(get_distance(v1, v2), 4)
        s.append(d)
    return sorted(s)[0]
# ---------------------------------------------------------------- ---------------------------------------------------


class VIEW3D_OT_ke_fitprim(bpy.types.Operator):
    bl_idname = "view3d.ke_fitprim"
    bl_label = "ke_fitprim"
    bl_description = "Creates (unit or unit+height) box or cylinder primitve based on selection." \
                     "VERTEX: Fits *along* 2 Selected verts. EDGE: Fits *in* selection/s. POLY: Fits *on* selection/s."
    bl_options = {'REGISTER'}  # TODO: undo/panel not gonna work in this setup...

    ke_fitprim_option: bpy.props.EnumProperty(
        items=[("BOX", "Box Mode", "", "BOX_MODE", 1),
               ("CYL", "Cylinder Mode", "", "CYL_MODE", 2),
               ("SPHERE", "UV Sphere", "", "SPHERE", 3),
               ("QUADSPHERE", "QuadSphere", "", "QUADSPHERE", 4),
               ],
    name="FitPrim Options",
        default="BOX")

    ke_fitprim_itemize: bpy.props.BoolProperty(
        name="Make Object", description="Makes new object from edit mesh fitprim", default=False)

    itemize = False
    boxmode = True
    sphere = False
    world = False
    settings = (0, 0, 0)
    _handle = None
    cyl_sides = 16
    unit = .1
    modal = True
    select = True
    screen_x = 0
    sphere_seg = 32
    sphere_ring = 16
    quadsphere_seg = 4
    mouse_pos = Vector((0, 0))
    edit_mode = ""

    def invoke(self, context, event):
        self.screen_x = int(bpy.context.region.width *.5)
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def modal(self, context, event):
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
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            if self.itemize or self.edit_mode == "OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.shade_smooth()
                bpy.context.object.data.use_auto_smooth = True
                bpy.ops.view3d.snap_cursor_to_center()

            if not self.select and not self.itemize and not self.edit_mode == "OBJECT":
                bpy.ops.mesh.select_all(action='DESELECT')

            bpy.context.space_data.overlay.show_cursor = True
            self.ke_fitprim_itemize = False
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def execute(self, context):

        if self.ke_fitprim_option == "BOX":
            self.boxmode, self.world = True, False
        elif self.ke_fitprim_option == "CYL":
            self.boxmode, self.world = False, False
        elif self.ke_fitprim_option == "SPHERE":
            self.boxmode, self.world, self.sphere = False, False, True
        elif self.ke_fitprim_option == "QUADSPHERE":
            self.boxmode, self.world, self.sphere = False, False, True

        if bpy.context.scene.kekit.fitprim_item:
            self.itemize = True
        else:
            self.itemize = self.ke_fitprim_itemize

        self.modal = bpy.context.scene.kekit.fitprim_modal
        self.cyl_sides = bpy.context.scene.kekit.fitprim_sides
        self.select = bpy.context.scene.kekit.fitprim_select
        self.unit = bpy.context.scene.kekit.fitprim_unit
        self.sphere_ring = bpy.context.scene.kekit.fitprim_sphere_ring
        self.sphere_seg = bpy.context.scene.kekit.fitprim_sphere_seg
        self.quadsphere_seg = bpy.context.scene.kekit.fitprim_quadsphere_seg

        self.edit_mode = bpy.context.mode
        sel_verts = []
        multi_object_mode = False
        # -----------------------------------------------------------------------------------------
        # MULTI OBJECT CHECK & SETUP
        # -----------------------------------------------------------------------------------------
        if self.edit_mode == "EDIT_MESH":
            sel_mode = [b for b in bpy.context.tool_settings.mesh_select_mode]
            other_side = []

            multi_object_mode = False

            sel_obj = [o for o in bpy.context.objects_in_mode if o.type == "MESH"]
            if len(sel_obj) == 2:
                multi_object_mode = True

            obj = bpy.context.active_object
            obj_mtx = obj.matrix_world.copy()

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
            vps = []
            normal, setpos, setrot, center = None, None, None, None
            first_island = None
            island_mode = False

        # -----------------------------------------------------------------------------------------
        # NO SELECTION MODE
        # -----------------------------------------------------------------------------------------
        if not sel_verts or self.edit_mode == "OBJECT":
            self.world = True
            screenpos = region_2d_to_location_3d(context.region, context.space_data.region_3d, self.mouse_pos, (0,0,0))
            setpos = screenpos
            side = self.unit
            distance = side
            sel_mode = (True,False,False)

        # -----------------------------------------------------------------------------------------
        # VERT MODE(s)
        # -----------------------------------------------------------------------------------------
        elif sel_mode[0] and len(sel_verts) == 1 and not multi_object_mode:
            # 1-VERT MODE
            self.world = True
            side = get_shortest(obj_mtx, sel_verts[0].link_edges[:])
            distance = side
            setpos = obj_mtx @ sel_verts[0].co

        elif sel_mode[0]:
            # 2+ Vert mode
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

            v_1 = p1 - p2
            v_2 = Vector((0, 0, 1))
            if v_1.dot(v_2) < 0 :
                v_2 = Vector((1, 0, 0))
            n_v = v_1.cross(v_2).normalized()
            u_v = n_v.cross(v_1).normalized()
            t_v = u_v.cross(n_v).normalized()

            setrot = Matrix((u_v, n_v, t_v)).to_4x4().inverted()
            distance = get_distance(p1, p2)
            setpos = Vector(get_midpoint(p1, p2))

        # -----------------------------------------------------------------------------------------
        # EDGE MODE
        # -----------------------------------------------------------------------------------------
        elif sel_mode[1]:

            one_line, loops, loops2 = False, [], []
            sel_edges = [e for e in bm.edges if e.select]
            vps = [e.verts for e in sel_edges]

            active_edge = bm.select_history.active
            if active_edge:
                active_edge_facenormals = [correct_normal(obj_mtx, p.normal) for p in active_edge.link_faces]
                active_edge_normal = Vector(average_vector(active_edge_facenormals)).normalized()

            # GET ISLANDS
            if multi_object_mode and active_edge:
                # print("multi obj mode") # todo: limited multiobj mode, rework one-for-all?
                sel_edges2 = [e for e in bm2.edges if e.select]
                vps2 = [e.verts for e in sel_edges2]
                p1 = get_loops(vps, legacy=True)
                p2 = get_loops(vps2, legacy=True)
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
                        # b1, b2 = obj_mtx @ a2p[0].co, obj_mtx @ a2p[1].co
                        b_avg = average_vector([obj_mtx @ a2p[0].co, obj_mtx @ a2p[1].co])

                        u_v = Vector(a1 - (obj_mtx @ a2p[0].co)).normalized()
                        t_v = Vector(a1 - a2).normalized()
                        n_v = u_v.cross(t_v).normalized()

                        setrot = rotation_from_vector(n_v, t_v, rotate90=True)
                        spacing, mp = get_closest_midpoint(a1, a2, b_avg)
                        setpos = mp
                        side = spacing
                        distance = spacing
                    else:
                        loops = get_loops(vps, legacy=True)

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
                    if u_v.dot(t_v) > 0:
                        u_v = Vector((1, 0, 0))
                    n_v = u_v.cross(t_v).normalized()

                    setrot = rotation_from_vector(n_v, t_v, rotate90=False)
                    setpos = mp
                    side = spacing
                    distance = spacing

                elif len(loops) == 1 or len(sel_edges) == 1:
                    # print ("single obj - single loop")
                    vecs = [(obj_mtx @ vp[0].co) - (obj_mtx @ vp[1].co) for vp in vps]
                    start_vec = vecs[-1]
                    side, sides, center = get_sides(obj_mtx, start_vec, vecs, vps)
                    # if len(sel_edges) == 4:
                        # print("FIX")

                    # ONE LINE (ONE EDGE or SINGLE STRAIGHT LINE) MODE------------------------------
                    if len(sides) == 1 and len(sides[0]) == len(sel_verts):
                        # print("1 side --> one line:", sides[0])
                        one_line = sides[0][0], sides[0][-1]

                    elif len(sel_edges) == 1:
                        # print("1 edge --> one line", one_line)
                        one_line = sel_verts

                    if one_line:
                        # print ("one line. center, points, normal:", center, one_line, active_edge_normal)
                        p1, p2 = obj_mtx @ one_line[0].co, obj_mtx @ one_line[1].co
                        t_v = Vector(p1 - p2).normalized()
                        n_v = active_edge_normal

                        setrot = rotation_from_vector(n_v, t_v)
                        distance = get_distance(p1, p2)
                        setpos = get_midpoint(p1, p2)
                        side = distance

                    else:
                        # RECT CHECK SIDES OR NGON MODE--------------------------------------------
                        # print("Edge Rect/Ngon mode. Sides:", len(sides))
                        b_candidate = sides[0][0].link_edges
                        b_candidate = [e.verts for e in b_candidate]
                        b = [v for vp in b_candidate for v in vp if v not in sides[0] and v in sel_verts]
                        if b:
                            b = obj_mtx @ b[0].co
                            a = obj_mtx @ sides[0][0].co - obj_mtx @ sides[0][1].co
                            b = obj_mtx @ sides[0][0].co - b

                            t_v = Vector(a).normalized()
                            u_v = Vector(b).normalized()
                            n_v = u_v.cross(t_v).normalized()

                            setrot = rotation_from_vector(n_v, t_v, rotate90=True)
                            distance = side
                            setpos = center
                        else:
                            side = None

        # -----------------------------------------------------------------------------------------
        # FACE MODE
        # -----------------------------------------------------------------------------------------
        elif sel_mode[2] and active_face and sel_poly:
            fail_island = False

            # GET ISLANDS
            if multi_object_mode and active_face:
                print (active_face, active_face2)
                first_island = sel_verts
                point = obj_mtx @ active_face.calc_center_median()

                # firstcos = [obj_mtx @ v.co for v in sel_verts]
                # secondcos = [obj_mtx2 @ v.co for v in sel_verts2]
                # todo: Oopsie doopsie - cant just feed random cos to the plane calc ;> rewrite at some point. for now:
                firstcos = [obj_mtx @ v.co for v in active_face.verts]
                secondcos = [obj_mtx2 @ v.co for v in active_face2.verts]

                if firstcos and secondcos:
                    island_mode = True

                    distance = point_to_plane(point, firstcos, secondcos)
                    if distance:
                        distance = abs(distance)
                    else:
                        print("Multi obj Point to plane failed for some reason - using single island mode.")
                        # island_mode = False
                        fail_island = True

            else:  # same (active) obj island selections
                first_island, second_island = get_selection_islands(sel_poly, active_face)

                if len(first_island) != 0 and len(second_island) != 0:
                    firstcos = [obj_mtx @ v.co for v in first_island]  # needs order sort
                    secondcos = [obj_mtx @ v.co for v in second_island]
                    print (firstcos[0], secondcos[0])
                    distance = point_to_plane(obj_mtx @ active_face.calc_center_median(), firstcos, secondcos)

                    if distance:
                        distance = abs(distance)
                        island_mode = True
                    else:
                        print("Point to plane failed for some reason - using single island mode.")
                        fail_island = True
                    print(distance)
                else:
                    # Ngon mode
                    first_island = sel_verts


            # GET PRIMARY SELECTION VALUES
            ngoncheck = len(active_face.verts)
            if sel_mode[2] and len(sel_verts) < 4:
                ngoncheck = 5  # todo: better solution for tris...


            if island_mode or fail_island:
                bpy.ops.mesh.select_all(action='DESELECT')

                for v in first_island:
                    bm.verts[v.index].select = True

                bmesh.update_edit_mesh(obj.data, True)
                bpy.ops.mesh.select_mode(type='VERT')
                bpy.ops.mesh.select_mode(type='FACE')
                bm.faces.ensure_lookup_table()

            bpy.ops.mesh.region_to_loop()
            # return {'FINISHED'}

            sel_edges = [e for e in bm.edges if e.select]
            vps = [e.verts for e in sel_edges]
            vecs = [(obj_mtx @ vp[0].co) - (obj_mtx @ vp[1].co) for vp in vps]

            normal = correct_normal(obj_mtx, active_face.normal)
            start_vec = vecs[-1]
            setrot = rotation_from_vector(normal, start_vec)

            print("Rectangle or Ngon mode",ngoncheck, island_mode, fail_island)
            if ngoncheck <= 4:
                side, sides, center = get_sides(obj_mtx, start_vec, vecs, vps, legacy=False)
            else:
                side, sides, center = get_sides(obj_mtx, start_vec, vecs, vps, legacy=True)

        # -----------------------------------------------------------------------------------------
        # PROCESS
        # -----------------------------------------------------------------------------------------
        if side:
            if len(sel_verts) == 0 or sel_mode[0] or sel_mode[1]:
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
            else:
                setrot = setrot.to_euler()

            # RUN OP
            if not self.edit_mode == "OBJECT":
                bpy.ops.mesh.select_mode(type='FACE')

            if self.itemize:
                if self.edit_mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                cursor = bpy.context.scene.cursor
                bpy.ops.transform.select_orientation(orientation='GLOBAL')
                cursor.location = setpos
                cursor.rotation_euler = setrot

            if self.boxmode:
                bpy.ops.mesh.primitive_box_add(width=side, depth=side, height=distance,
                                               align='WORLD', location=setpos, rotation=setrot)
                if self.itemize or self.edit_mode == "OBJECT":
                    bpy.ops.object.shade_smooth()
                    bpy.context.object.data.use_auto_smooth = True

            elif self.sphere and not self.ke_fitprim_option == "QUADSPHERE":
                bpy.ops.mesh.primitive_uv_sphere_add(segments=self.sphere_seg, ring_count=self.sphere_ring, radius=side,
                                                     align='WORLD', location=setpos, rotation=setrot)
                if self.itemize or self.edit_mode == "OBJECT":
                    bpy.ops.object.shade_smooth()
                    bpy.context.object.data.use_auto_smooth = True

            elif self.ke_fitprim_option == "QUADSPHERE":
                bpy.ops.mesh.primitive_round_cube_add(align='WORLD', location=setpos, rotation=setrot, radius=side,
                                                      size=(0, 0, 0), arc_div=self.quadsphere_seg, lin_div=0,
                                                      div_type='CORNERS')

                if self.itemize or self.edit_mode == "OBJECT":
                    bpy.ops.object.shade_smooth()
                    bpy.context.object.data.use_auto_smooth = True

            else:
                bpy.ops.mesh.primitive_cylinder_add(vertices=self.cyl_sides, radius=side, depth=distance * 2,
                                                    enter_editmode=False, align='WORLD',
                                                    location=setpos, rotation=setrot)

                if self.modal:
                    if self.itemize or self.edit_mode == "OBJECT":
                        bpy.ops.object.mode_set(mode="EDIT")

                    self.settings = (side, distance, setpos, setrot)
                    context.window_manager.modal_handler_add(self)

                    args = (self, context, self.screen_x)
                    self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW',
                                                                          'POST_PIXEL')
                    bpy.context.space_data.overlay.show_cursor = False
                    return {'RUNNING_MODAL'}

            if multi_object_mode and not self.itemize:
                second_obj.select_set(state=True)
                obj.select_set(state=True)
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()

        else:
            self.report({"INFO"}, "FitPrim: Incorrect Selection? / Edit Mode? / No Active Element?")

        if not self.select and not self.itemize and not self.edit_mode == "OBJECT":
            bpy.ops.mesh.select_all(action='DESELECT')

        if self.itemize:
            bpy.ops.view3d.snap_cursor_to_center()
            bpy.context.active_object.select_set(state=True)

        self.ke_fitprim_itemize = False
        return {"FINISHED"}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (VIEW3D_OT_ke_fitprim,
           )


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
