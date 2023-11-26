import bmesh
import bpy
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty
from bpy.types import Operator, Panel
from mathutils import Vector
from .._utils import get_scene_unit, get_face_islands, pick_closest_edge, get_prefs


def get_props(preset="0"):
    k = get_prefs()
    p = k.mc_prefs[:]
    v1, v2, v3, v4 = 0, 0, 0, 0
    if preset == "0":
        v1, v2, v3, v4 = p[0], p[1], p[2], p[3]
    elif preset == "1":
        v1, v2, v3, v4 = p[4], p[5], p[6], p[7]
    elif preset == "2":
        v1, v2, v3, v4 = p[8], p[9], p[10], p[11]
    elif preset == "3":
        v1, v2, v3, v4 = p[12], p[13], p[14], p[15]
    elif preset == "4":
        v1, v2, v3, v4 = p[16], p[17], p[18], p[19]
    elif preset == "5":
        v1, v2, v3, v4 = p[20], p[21], p[22], p[23]
    elif preset == "6":
        v1, v2, v3, v4 = p[24], p[25], p[26], p[27]
    elif preset == "7":
        v1, v2, v3, v4 = p[28], p[29], p[30], p[31]
    return v1, str(int(v2)), v3, bool(v4)


class UIMultiCutModule(Panel):
    bl_idname = "UI_PT_M_MULTICUT"
    bl_label = "MultiCut"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_MODELING"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        toggle = context.scene.kekit_temp.toggle
        k = get_prefs()

        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_x = 1
        row.prop(k, "mc_relative", text="")
        row.scale_x = 0.25
        row.prop(k, "mc_center", text="")
        row.scale_x = 1
        row.prop(k, "mc_fixed", text="")

        col = layout.column(align=False)

        row = col.row(align=True)
        if toggle:
            row.prop(k, "mc_name0", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % k.mc_name0)
            v1, v2, v3, v4 = get_props(preset="0")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC1")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 0

        row = col.row(align=True)
        if toggle:
            row.prop(k, "mc_name1", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % k.mc_name1)
            v1, v2, v3, v4 = get_props(preset="1")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC2")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 1

        row = col.row(align=True)
        if toggle:
            row.prop(k, "mc_name2", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % k.mc_name2)
            v1, v2, v3, v4 = get_props(preset="2")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC3")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 2

        row = col.row(align=True)
        if toggle:
            row.prop(k, "mc_name3", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % k.mc_name3)
            v1, v2, v3, v4 = get_props(preset="3")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC4")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 3

        row = col.row(align=True)
        if toggle:
            row.prop(k, "mc_name4", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % k.mc_name4)
            v1, v2, v3, v4 = get_props(preset="4")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC5")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 4

        row = col.row(align=True)
        if toggle:
            row.prop(k, "mc_name5", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % k.mc_name5)
            v1, v2, v3, v4 = get_props(preset="5")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC6")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 5

        row = col.row(align=True)
        if toggle:
            row.prop(k, "mc_name6", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % k.mc_name6)
            v1, v2, v3, v4 = get_props(preset="6")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC7")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 6

        row = col.row(align=True)
        if toggle:
            row.prop(k, "mc_name7", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % k.mc_name7)
            v1, v2, v3, v4 = get_props(preset="7")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC8")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 7

        row = col.row(align=True)
        row.prop(context.scene.kekit_temp, "toggle", text="Manual Rename", toggle=True)


def set_name(v1, v2, v3, v4):
    if bool(v4):
        # Fixed Offset
        c = " (C)" if int(v2) == 1 else ""
        u, v = get_scene_unit(v3)
        v = round(v, 3)
        if u == '\u0027' and v < 1:
            # imperial < 1 feet-> inches
            u, v = '\u0022', v * 12
        else:
            # metric units
            v = round(v3, 3)
            if 1 > v >= 0.01:
                u, v = 'cm', v * 100
            elif v < 0.01:
                u, v = 'mm', v * 1000
        # de-floating whole nrs
        if v.is_integer():
            v = int(v)
        e1 = str(v) + " " + u
        e2 = ""
    else:
        # Relative Offset
        c = "50-" if int(v2) == 1 else ""
        v = int(round(v1, 3) * 100)
        e1 = str(v) + "-"
        e2 = str(100 - v)

    return e1 + c + e2


class KeMultiCutPrefs(Operator):
    bl_idname = "ke.mcprefs"
    bl_label = "Store Preset"
    bl_description = "Stores values to slot MC1-8\n(Note: Will be stored as Fixed, if fixed offset is not 0)"
    bl_options = {'REGISTER'}

    preset: IntProperty(name="Preset", default=0)

    def execute(self, context):
        k = get_prefs()
        v1 = float(k.mc_relative) / 100
        v2 = float(k.mc_center)
        v3 = float(k.mc_fixed)
        v4 = 0.0 if v3 == 0 else 1.0
        # print(v1,v2,v3,v4)
        p = k.mc_prefs
        if self.preset == 0:
            p[0], p[1], p[2], p[3] = v1, v2, v3, v4
            k.mc_name0 = set_name(v1, v2, v3, v4)
        elif self.preset == 1:
            p[4], p[5], p[6], p[7] = v1, v2, v3, v4
            k.mc_name1 = set_name(v1, v2, v3, v4)
        elif self.preset == 2:
            p[8], p[9], p[10], p[11] = v1, v2, v3, v4
            k.mc_name2 = set_name(v1, v2, v3, v4)
        elif self.preset == 3:
            p[12], p[13], p[14], p[15] = v1, v2, v3, v4
            k.mc_name3 = set_name(v1, v2, v3, v4)
        elif self.preset == 4:
            p[16], p[17], p[18], p[19] = v1, v2, v3, v4
            k.mc_name4 = set_name(v1, v2, v3, v4)
        elif self.preset == 5:
            p[20], p[21], p[22], p[23] = v1, v2, v3, v4
            k.mc_name5 = set_name(v1, v2, v3, v4)
        elif self.preset == 6:
            p[24], p[25], p[26], p[27] = v1, v2, v3, v4
            k.mc_name6 = set_name(v1, v2, v3, v4)
        elif self.preset == 7:
            p[28], p[29], p[30], p[31] = v1, v2, v3, v4
            k.mc_name7 = set_name(v1, v2, v3, v4)
        return {'FINISHED'}


def ring_and_rim(startedge):
    rim_verts = []
    ring_edges = []
    sv = startedge.verts[0]
    max_count = 1000
    revisited = 0

    for loop in startedge.link_loops[:]:
        start = loop
        edges = [loop.edge]
        rim = [sv]
        prev_sv = sv

        i = 0
        while i < max_count:
            loop = loop.link_loop_radial_next.link_loop_next.link_loop_next

            if len(loop.face.edges) != 4 or loop.face.hide:
                break

            for e in loop.face.edges:
                if e != edges[-1]:
                    next_v = e.other_vert(prev_sv)
                    if next_v:
                        prev_sv = next_v
                        rim.append(next_v)
                        break

            edges.append(loop.edge)

            if loop.face.tag:
                revisited += 1

            loop.face.tag = True

            if loop == start or loop.edge.is_boundary:
                break
            i += 1

        rim_verts.extend(rim)
        ring_edges.extend(edges)

    return list(set(ring_edges)), list(set(rim_verts)), revisited


class KeMultiCut(Operator):
    bl_idname = "mesh.ke_multicut"
    bl_label = "MultiCut"
    bl_description = "(Select edge) Like Loop Cut combined with Offset Edge Slide for the ends.\n" \
                     "(Face Mode) Slices selection islands\n" \
                     "Assign custom presets (MC1-8), save kekit prefs.\n" \
                     "Use in the N-panel, MultiCut Pie-Menu or Shortcuts.\n" \
                     "Redo-panel for session overrides (Does not change presets)"
    bl_options = {'REGISTER', 'UNDO'}

    o_even: EnumProperty(items=[
        ("1", "ON", "", 1),
        ("0", "OFF", "", 2)],
        name="Even", default="0")

    o_center: EnumProperty(items=[
        ("1", "ON", "", 1),
        ("0", "OFF", "", 2)],
        name="Center Cuts", default="0")

    o_relative: FloatProperty(name="Relative Offset", default=0.01, min=0, max=0.5)
    o_fixed: FloatProperty(name="Fixed Offset", default=0, subtype="DISTANCE", unit="LENGTH")
    using_fixed: BoolProperty(default=False, options={"HIDDEN"})

    preset: EnumProperty(items=[
        ("0", "", "", 1),
        ("1", "", "", 2),
        ("2", "", "", 3),
        ("3", "", "", 4),
        ("4", "", "", 5),
        ("5", "", "", 6),
        ("6", "", "", 7),
        ("7", "", "", 8),
        ("SET", "", "", 9)],
        name="Preset", default="0")

    mouse_pos = [0, 0]
    mtx = None

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def draw(self, context):
        k = get_prefs()
        layout = self.layout.split(factor=0.03)
        col = layout.column()
        col.separator()

        main = layout.column().split(factor=0.93)
        col = main.column(align=True)

        if not self.using_fixed:

            split = col.split(factor=1)
            row = split.row(align=True)
            row.label(text="Even")
            row.prop(self, "o_even", expand=True)

            col.separator(factor=0.75)

            row = col.row(align=True).split(factor=0.31)
            row.label(text="Offset")
            row.prop(self, "o_relative", text="", expand=True)

        else:
            col.separator(factor=0.75)

            row = col.row(align=True).split(factor=0.31)
            row.label(text="Fixed Offset")
            row.prop(self, "o_fixed", text="", expand=True)

        col.separator(factor=0.75)

        split = col.split(factor=.31)
        split.label(text="Center Cut")
        row = split.row(align=True)
        row.prop(self, "o_center", expand=True)

        col.separator(factor=1.5)

        split = col.split(factor=.31)
        split.label(text="Presets")
        row = split.column(align=True)
        row.prop_enum(self, "preset", "0", text='%s' % k.mc_name0, icon='NONE')
        row.prop_enum(self, "preset", "1", text='%s' % k.mc_name1, icon='NONE')
        row.prop_enum(self, "preset", "2", text='%s' % k.mc_name2, icon='NONE')
        row.prop_enum(self, "preset", "3", text='%s' % k.mc_name3, icon='NONE')
        row.prop_enum(self, "preset", "4", text='%s' % k.mc_name4, icon='NONE')
        row.prop_enum(self, "preset", "5", text='%s' % k.mc_name5, icon='NONE')
        row.prop_enum(self, "preset", "6", text='%s' % k.mc_name6, icon='NONE')
        row.prop_enum(self, "preset", "7", text='%s' % k.mc_name7, icon='NONE')

        col.separator(factor=1.5)

    def get_props(self, p):
        v1, v2, v3, v4 = 0, 0, 0, 0
        if self.preset == "0":
            v1, v2, v3, v4 = p[0], p[1], p[2], p[3]
        elif self.preset == "1":
            v1, v2, v3, v4 = p[4], p[5], p[6], p[7]
        elif self.preset == "2":
            v1, v2, v3, v4 = p[8], p[9], p[10], p[11]
        elif self.preset == "3":
            v1, v2, v3, v4 = p[12], p[13], p[14], p[15]
        elif self.preset == "4":
            v1, v2, v3, v4 = p[16], p[17], p[18], p[19]
        elif self.preset == "5":
            v1, v2, v3, v4 = p[20], p[21], p[22], p[23]
        elif self.preset == "6":
            v1, v2, v3, v4 = p[24], p[25], p[26], p[27]
        elif self.preset == "7":
            v1, v2, v3, v4 = p[28], p[29], p[30], p[31]
        return v1, str(int(v2)), v3, bool(v4)

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode[:]
        k = get_prefs()

        # Old hacky way (that still works more reliably) to update object data...
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()

        # Preset Values - SET is the "launch" values - 1-8 temp preset restore from redo
        if self.preset != "SET":
            self.o_relative, self.o_center, self.o_fixed, self.using_fixed = \
                self.get_props(k.mc_prefs[:])
            self.preset = "SET"

        offsets = [self.o_relative, 1 - self.o_relative]

        if self.o_relative == 0.5 or self.o_relative == 0:
            rd = True
        else:
            rd = False

        even = bool(int(self.o_even))
        # Even doesn't work with fixed offset
        if self.using_fixed:
            fixed_offset = True
            even = False
        else:
            fixed_offset = False

        cuts = 2 + int(self.o_center)

        # Selection Checks / bmesh
        bm = bmesh.from_edit_mesh(context.object.data)
        self.mtx = context.object.matrix_world

        ring_edges = []
        sel_edges = []
        sel_faces = []

        if sel_mode[2]:
            # Finding edge on island selection straight ring-loop(s)
            sel_faces = [f for f in bm.faces if f.select]

            if sel_faces:
                sel_edges = [e for e in bm.edges if e.select]
                sel_verts = [v for v in bm.verts if v.select]

                f_islands = get_face_islands(bm, sel_verts, sel_edges, sel_faces)
                # print("Island Count:", len(f_islands))
                for island in f_islands:
                    if len(island) >= 2:
                        start = island[0].edges
                        for f in island[1:]:
                            for e in f.edges:
                                if e in start:
                                    ring_edges.append(e)
                                    break
                    elif len(island) == 1:
                        e = pick_closest_edge(context, mtx=self.mtx, mousepos=self.mouse_pos, edges=island[0].edges)
                        if e:
                            ring_edges.append(e)

            if ring_edges:
                sel_edges = ring_edges
                bpy.ops.mesh.hide(unselected=True)

            context.tool_settings.mesh_select_mode = (False, True, False)

            if ring_edges:
                for e in bm.edges:
                    e.select_set(False)
                for e in ring_edges:
                    e.select_set(True)
            else:
                bpy.ops.view3d.select(extend=False, location=self.mouse_pos)

        if not ring_edges:
            sel_edges = [e for e in bm.edges if e.select]

        if not sel_edges:
            self.report({"INFO"}, "No Edge(s) selected?")
            return {'CANCELLED'}

        # Process
        same_ring = []
        new_edges = []
        loop_select = False
        ring_verts = []
        verts = []

        for start_edge in sel_edges:

            if start_edge not in same_ring:

                ring_edges, rim_verts, revisited = ring_and_rim(start_edge)

                # Check overlap for selection later
                if len(ring_edges) != revisited:
                    loop_select = True

                # check for multiple start-edges on the same ring to skip
                for oe in sel_edges:
                    if oe in ring_edges and oe != start_edge:
                        same_ring.append(oe)

                rim_verts = [v.index for v in rim_verts]
                connect_verts = []

                # find the shortest edge to use relative even against.
                elens = [e.calc_length() for e in ring_edges]
                shortest = sorted(elens)[0]
                even_fo = offsets[0] * shortest

                for e, elen in zip(ring_edges, elens):
                    ring_verts.extend([v.index for v in e.verts])
                    o = offsets

                    # re-calculate offsets if fixed
                    if fixed_offset or even:
                        if even:
                            fo = even_fo / elen
                        else:
                            fo = self.o_fixed / elen
                            if fo > 1:
                                fo = 0.9999
                            elif fo < 0:
                                fo = 0.0001

                        if fo < 1:
                            o[0] = fo
                            o[-1] = 1 - fo

                    # with >1 center cuts spacing - [code removed] - TBD - spacing weirdness

                    # "First Vert" det. by (1st) loop.vert. Direction flips from loop-cycle system
                    loop_flip = False
                    lv = e.link_loops[0].vert
                    if lv != e.verts[0]:
                        loop_flip = True

                    # Edge Vector Pos Offsets (cut placement)
                    sv = lv.co
                    n = Vector(e.other_vert(lv).co - sv)

                    if loop_flip:
                        o = offsets[::-1]

                    new_cos = [sv + (i * n) for i in o]

                    # Split & "Slide" offset (& store idx)
                    geom = bmesh.ops.bisect_edges(bm, edges=[e], cuts=cuts, edge_percents={})
                    # edge percents doesn't work with more than 1 cut? how does it work? [undocumented]

                    new_verts = [i for i in geom['geom_split'] if isinstance(i, bmesh.types.BMVert)]

                    connect_verts.append([v.index for v in new_verts])

                    new_verts[0].co = new_cos[0]
                    new_verts[-1].co = new_cos[-1]

                # ......and all the verts have 'died', re-assign with stored idx (seems fine)
                bm.verts.ensure_lookup_table()

                rim_verts_upd = []
                connect_loops = [[] for _ in range(len(connect_verts[0]))]

                for i in rim_verts:
                    rim_verts_upd.append(bm.verts[i])

                for ig in connect_verts:
                    upd = []
                    for i in ig:
                        upd.append(bm.verts[i])

                    # check that the vert order starts on the rim
                    evs = []
                    for e in upd[0].link_edges:
                        evs.append(e.other_vert(upd[0]))

                    if not any(i in evs for i in rim_verts_upd):
                        upd.reverse()

                    # assign to loop-lists for connecting
                    for i, v in enumerate(upd):
                        connect_loops[i].append(v)

                nedges = []
                verts = []
                for vloop in connect_loops:
                    trim = list(set(vloop))
                    verts.extend(trim)
                    geom = bmesh.ops.connect_verts(bm, verts=trim, check_degenerate=False, faces_exclude=[])
                    nedges.append(geom['edges'])

                new_edges.append(nedges)

        # Finalize
        bm.select_flush(False)

        for ring in new_edges:
            for e in ring[0] + ring[-1]:
                e.select_set(True)

        if rd:
            for i in ring_verts:
                verts.append(bm.verts[i])

            verts = list(set(verts))  # ???
            bmesh.ops.remove_doubles(bm, verts=verts, dist=0.0002)

        bmesh.update_edit_mesh(context.object.data)

        # Lazy connecting overlapping cuts, not really needed 99% of the time, so, it'll do.
        if len(sel_edges) > 1 and loop_select:
            bpy.ops.mesh.loop_multi_select(ring=False)

        if sel_mode[2] and sel_faces:
            bpy.ops.mesh.reveal(select=False)

        if sum(context.object.scale) != 3 and fixed_offset:
            self.report({"INFO"}, "Fixed offset: Scale has not been applied -> Incorrect fixed values")

        return {'FINISHED'}
