import bpy
import blf
import bmesh
from bpy.props import BoolProperty
from math import degrees
from bpy_extras.view3d_utils import region_2d_to_location_3d
from mathutils import Vector
from .._utils import mouse_raycast, set_status_text, get_prefs, mesh_world_coords, find_closest_edge_kd, \
    find_closest_co_kd


def draw_callback_px(self, context, pos):
    if self.angle_mode:
        val = str(round(degrees(self.val), 2)) + "\u00B0"
    elif self.percent_mode:
        val = str(round(self.val, 2)) + "%"
    else:
        val = str(round(self.val, 4))
    seg = str(int(self.seg))

    font_id = 0
    vpos = int(self.fs[1] * 2)
    if self.nonmesh_target:
        hpos = pos
        sub_hpos = pos
    else:
        w, _h = blf.dimensions(font_id, self.modtxt)
        hpos = pos - int(w * 0.9)
        sub_hpos = pos - self.fs[6]

    blf.enable(font_id, 4)
    blf.position(font_id, hpos, vpos + self.fs[3], 0)
    blf.color(font_id, self.hcol[0], self.hcol[1], self.hcol[2], self.hcol[3])
    blf.size(font_id, self.fs[4])
    blf.shadow(font_id, 5, 0, 0, 0, 1)
    blf.shadow_offset(font_id, 1, -1)

    if self.nonmesh_target:
        profile = ""
    else:
        profile = "Profile: " + str(round(self.active_mod.profile, 1))
    offset = int(self.fs[4] * 1.25)

    blf.position(font_id, sub_hpos, vpos + offset, 0)
    blf.draw(font_id, "Bevel: " + val)
    blf.position(font_id, sub_hpos, vpos , 0)
    blf.draw(font_id, "Segments: " + seg)
    blf.position(font_id, sub_hpos, vpos - offset, 0)
    blf.size(font_id, self.fs[5])
    blf.draw(font_id, profile)

    blf.size(font_id, self.fs[4])
    blf.position(font_id, hpos, vpos - self.fs[1], 0)
    blf.draw(font_id, self.modtxt)

    modetxt = ""
    blf.size(font_id, self.fs[5])
    blf.position(font_id, sub_hpos, vpos + self.fs[6], 0)
    if self.offset_mode:
        modetxt = "[ (O)ffset Mode ]"
    elif self.extrude_mode:
        modetxt = "[ (E)xtrude Mode ]"
    elif self.angle_mode:
        modetxt = "[ (A)ngle Mode ]"
    blf.draw(font_id, modetxt)


class KeBevelTweaker(bpy.types.Operator):
    bl_idname = "view3d.ke_bevel_tweaker"
    bl_label = "Bevel Tweaker"
    bl_description = ("Object Mode: Mouse over edge used by a Bevel Modifier you want to tweak\n"
                      "Edit Mode: Select (at least 1) edge (or vertex) to tweak.\n"
                      "See Wiki for complete docs")
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    skip_pie: BoolProperty(default=False, options={"HIDDEN", 'SKIP_SAVE'})

    mouse_pos = Vector((0, 0))
    active_mod = None
    bevel_mods = []
    edge_weight_mods = []
    vertex_group_mods = []
    mods = {}
    modtxt = ""
    obj = None
    nonmesh_target = None
    _timer = None
    _handle = None
    first_run = 0
    first_set = False
    em_pie_run = False
    screen_x = 0
    hcol = (1, 1, 1, 1)
    tcol = (1, 1, 1, 1)
    scol = (1, 1, 1, 1)
    fs = [64, 64, 110, 64, 20, 15, 40, 20, 10]
    og_overlay = [False, False]
    offset_mode = False
    extrude_mode = False
    angle_mode = False
    percent_mode = False
    og_settings = []
    new_mx = 0
    prev_mx = 0
    sensitivity = 0.015
    sensitivity_multiplier = 1
    precision = 0.1
    precision_multiplier = 1
    val = 0
    display_val = 0
    seg = 0
    numbers = ('ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE')
    digits = {'ONE': "1", 'TWO': "2", 'THREE': "3", 'FOUR': "4", 'FIVE': "5", 'SIX': "6", 'SEVEN': "7", 'EIGHT': "8",
              'NINE': "9"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D" and bpy.app.version >= (4, 3)

    def raycast(self, context):
        obj, hit_wloc, hit_normal, face_index = mouse_raycast(context, self.mouse_pos, evaluated=True)
        # Double-check with viewpicker since raycasting is only good for "real mesh" ?
        if face_index is None:
            bpy.ops.view3d.select(extend=False, location=(int(self.mouse_pos[0]), int(self.mouse_pos[1])))
            obj = context.object
            if obj.type in {'CURVE', 'FONT'}:
                if hasattr(obj.data, "bevel_depth"):
                    self.nonmesh_target = True
        return obj, hit_wloc, hit_normal, face_index

    def toggle_overlays(self, context, restore=False):
        # Hide some distracting ui elements during tweak
        if not restore:
            self.og_overlay = context.space_data.overlay.show_cursor, context.space_data.overlay.show_object_origins
            context.space_data.overlay.show_cursor = False
            context.space_data.overlay.show_object_origins = False
        else:
            context.space_data.overlay.show_cursor = self.og_overlay[0]
            context.space_data.overlay.show_object_origins = self.og_overlay[1]

    def backup_mod_settings(self):
        self.og_settings = [self.active_mod.width, self.active_mod.segments,
                            self.active_mod.angle_limit, self.active_mod.width_pct]
        # set starting points
        if self.angle_mode:
            self.sensitivity = 1
        else:
            self.sensitivity = (self.og_settings[0] / 10.5) * self.sensitivity_multiplier
        self.val = self.og_settings[0]
        self.seg = self.og_settings[1]

    def restore_mod_settings(self, mod):
        mod.width, mod.segments, mod.angle_limit, mod.width_pct = self.og_settings

    def init_modal(self, context):
        # prep for percent
        if not self.nonmesh_target:
            if self.active_mod.offset_type == "PERCENT":
                self.percent_mode = True
                self.sensitivity = 1

            # map to nr keys
            maxlen = len(self.numbers)
            if len(self.bevel_mods) > maxlen:
                self.bevel_mods = self.bevel_mods[:maxlen]
            self.numbers = self.numbers[:len(self.bevel_mods)]
            for nr, m in zip(self.numbers, self.bevel_mods):
                self.mods[nr] = m.name

            # bkp original settings
            self.backup_mod_settings()

            self.toggle_overlays(context)
            self.update_mod_txt()
        else:
            self.og_settings = [self.obj.data.bevel_depth, self.obj.data.bevel_resolution, self.obj.data.extrude]

        # Only really "need" the timer to avoid modifier inputs when first running script! bleh.
        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step=0.01, window=context.window)
        wm.modal_handler_add(self)
        # and ui
        args = (self, context, self.screen_x)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW',
                                                              'POST_PIXEL')
        status_help = [
            "[1-9] Set Active Bevel (+SHIFT=NoReset)",
            "[MOUSE] Width (+SHIFT=Precision)",
            "[WHEEL] Segments",
            "[A] Angle",
            "[W,Q] Wireframe, Clamp",
            "[Z,X,C] Profile: 0.5, 0.7, 1.0",
            "[E,O] Extrude & Offset (Curves)",
            "[MMB, ALT-MBs] Navigation",
            "[ENTER/SPACEBAR/LMB] Apply",
            "[ESC/RMB] Cancel"]
        # UPDATE STATUS BAR
        set_status_text(context, status_help, mb="", kb="", spacing=2)

    def update_mod_txt(self):
        self.modtxt = ""
        active_name = self.active_mod.name
        for nr in self.mods:
            name = self.mods[nr]
            num = self.digits[nr]
            if name == active_name:
                self.modtxt += f"[ {num}: {name} ] \u2E3A "
            else:
                self.modtxt += f"{num}: {name} \u2E3A "
        if self.modtxt:
            self.modtxt = self.modtxt[:-2]

    def switch_active_mod(self, context, new_active_name, no_reset=False):
        # toggle off all the modes
        self.angle_mode = False
        self.percent_mode = False
        self.obj = context.scene.objects[self.obj.name]
        if not no_reset:
            self.restore_mod_settings(self.obj.modifiers[self.active_mod.name])
        # switch
        self.active_mod = self.obj.modifiers[new_active_name]
        if self.active_mod.offset_type == "PERCENT":
            self.percent_mode = True
        self.backup_mod_settings()
        self.update_mod_txt()
        bpy.ops.object.modifier_set_active(modifier=self.active_mod.name)

    def get_mods(self):
        self.edge_weight_mods = []
        self.vertex_group_mods = []
        if self.obj.type == "MESH":
            for m in self.obj.modifiers:
                if m.type == "BEVEL":
                    self.bevel_mods.append(m)
                    if m.limit_method == "WEIGHT" and m.edge_weight:
                        self.edge_weight_mods.append(m)
                    elif m.limit_method == "VGROUP" and m.vertex_group:
                        self.vertex_group_mods.append(m)

    def get_other_bevels(self):
        #  ...else set the active mod to first angle bevel mod
        for m in self.bevel_mods:
            if m.limit_method == "ANGLE":
                self.active_mod = m
                break
        # ...and if you're using [insert madness here] - just set the last listed as active
        if self.active_mod is None:
            self.active_mod = self.bevel_mods[-1]

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        self.screen_x = int(context.region.width * 0.5)
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        self.sensitivity_multiplier = k.bt_multiplier
        self.precision_multiplier = k.bt_multiplier_p
        # self.sensitivity = 0.02 * self.sensitivity_multiplier
        self.hcol = k.modal_color_header
        self.tcol = k.modal_color_text
        self.scol = k.modal_color_subtext
        scale_factor = context.preferences.view.ui_scale * k.ui_scale
        self.fs = [int(round(n * scale_factor)) for n in self.fs]
        # need to reset some of these here
        self.first_run = 0
        self.first_set = False
        self.bevel_mods = []
        self.edge_weight_mods = []
        self.vertex_group_mods = []
        self.active_mod = None

        if context.mode == "EDIT_MESH":
            if k.bt_em_pie:
                # opt mode to use bevel pie menu in edit mode instead
                if not self.skip_pie:
                    # (except when run FROM the pie menu)
                    bpy.ops.wm.call_menu_pie("INVOKE_DEFAULT", name="VIEW3D_MT_ke_pie_bevel")
                    return {"FINISHED"}

            # check obj selection
            self.obj = context.object
            if not self.obj:
                self.report({"WARNING"}, "No Context Object!")
                return {"CANCELLED"}

            # check modifiers
            self.get_mods()
            if not self.bevel_mods:
                self.report({"WARNING"}, "No Bevel Modifiers found!")
                return {"CANCELLED"}

            # check mesh selection
            bm = bmesh.from_edit_mesh(self.obj.data)
            sel_edges = [e for e in bm.edges if e.select]
            sel_verts = [v for v in bm.verts if v.select]
            if not sel_verts:
                self.report({"WARNING"}, "No Mesh Element Selected!")
                return {"CANCELLED"}

            active_eg = None

            if sel_edges:
                edge = sel_edges[-1]
                # layer = bm.edges.layers.float.get("bevel_weight_edge")
                edge_layers = [a for a in bm.edges.layers.float.values()]

                for layer in edge_layers:
                    if edge[layer] == 1:
                        active_eg = layer
                        break

                if active_eg is not None:
                    for mod in self.edge_weight_mods:
                        if active_eg.name == mod.edge_weight:
                            self.active_mod = mod
                            break

            # vertex groups, for completeness? might be some reason to use them...
            if not self.active_mod:
                vgroups = self.obj.vertex_groups
                vert_idx = sel_verts[-1].index
                verts_vgroups = self.obj.data.vertices[vert_idx].groups

                vgroupname = ""
                for grp in verts_vgroups:
                    if grp.weight:
                        vgroupname = vgroups[grp.group].name

                for m in self.bevel_mods:
                    if m.limit_method == "VGROUP" and m.vertex_group == vgroupname:
                        self.active_mod = m
                        break

            if self.active_mod is None:
                # ...or angle bevel or whatever ;>
                self.get_other_bevels()

            self.init_modal(context)
            return {'RUNNING_MODAL'}
            # return {'FINISHED'}

        elif context.mode != "OBJECT" and context.active_object:
            bpy.ops.object.mode_set(mode='OBJECT')
        # else:
        #     # maybe try to fix every edge case leater...
        #     return {"CANCELLED"}

        # hide blocking wireframe objects for raycast
        hidden = []
        for o in context.scene.objects:
            if o.display_type in {'WIRE', 'BOUNDS'} and not o.hide_viewport:
                o.hide_viewport = True
                hidden.append(o)

        # Raycast Note: Just getting obj and using hit_wloc to find nearest unevaluated edge - later.
        # (To avoid having to toggle on/off visibility for all modifiers for unevaluated data?)
        self.obj, hit_wloc, hit_normal, face_index = self.raycast(context)

        if hidden:
            for o in hidden:
                o.hide_viewport = False

        if self.obj is None and context.object:
            self.obj = context.object
        if not self.obj:
            self.report({"WARNING"}, "No Object Mesh Surface found!")
            return {"CANCELLED"}

        # "De-Context?" to avoid mesh data name getting "corrupted" (as evaluated) when using subd too ?!
        self.obj = bpy.data.objects[self.obj.name]

        if not hit_wloc:
            # print("close enough result for missing - mouse not over mesh / edges?")
            hit_wloc = self.obj.location

        # CURVE MODAL
        if self.nonmesh_target:
            self.init_modal(context)
            self.seg = self.obj.data.bevel_resolution
            return {'RUNNING_MODAL'}

        # Get modifiers
        self.get_mods()
        if not self.bevel_mods:
            self.report({"WARNING"}, "No Bevel Modifiers found!")
            return {"CANCELLED"}

        # Edge weights take priority
        if self.edge_weight_mods or self.vertex_group_mods:
            # Trying to "mouse pick" which edge Bevel modifier is active from edge under mouse (in Object mode)
            region = context.region
            region_data = context.space_data.region_3d

            # The ONLY way to get un-evaluated mesh data in object mode? :
            # to-do: maybe find the attr grp via eval data? though, this works & less geo to loop?
            uneval_mesh = bpy.data.meshes[self.obj.data.name]
            # or edit mode mouse over? : bm.from_mesh(bpy.data.meshes[self.obj.data.name])

            # Find the nearest bunch of edges to mouse pos (3d->2d could work, but need calc depth (+ occluded) still?)
            vcoords = mesh_world_coords(uneval_mesh, self.obj.matrix_world)
            mouse_3d = region_2d_to_location_3d(region, region_data, self.mouse_pos, hit_wloc)
            indices = find_closest_edge_kd(uneval_mesh.edges[:], vcoords, mouse_3d)
            # nearest_edge = uneval_mesh.edges[idx]
            edge_groups = [a for a in uneval_mesh.attributes.values() if
                           a.domain == "EDGE" and a.data_type == "FLOAT"]
            # Try to find edge groups used by nearest edge
            # only using 1st found - manually switch in modal (if using same edge in multiple attr groups)
            active_eg = None

            for grp in edge_groups:
                attr = uneval_mesh.attributes[grp.name]
                for idx in indices:
                    # print(attr.data[idx].value, attr.data[idx])
                    if attr.data[idx].value == 1:
                        active_eg = grp
                        break

            if active_eg is not None:
                for mod in self.edge_weight_mods:
                    if active_eg.name == mod.edge_weight:
                        self.active_mod = mod
                        break

            if self.active_mod is None and self.vertex_group_mods:
                # ...just for completeness?
                indices = find_closest_co_kd(vcoords, mouse_3d)
                vgroups = self.obj.vertex_groups
                verts_vgroups = uneval_mesh.vertices[indices[0]].groups

                # again just grabbing the 1st
                vgroupname = ""
                for vg in verts_vgroups:
                    if vg.weight:
                        vgroupname = vgroups[vg.group].name

                for m in self.bevel_mods:
                    if m.limit_method == "VGROUP" and m.vertex_group == vgroupname:
                        self.active_mod = m
                        break

        if self.active_mod is None:
            # print("or angle bevel or something...")
            self.get_other_bevels()

        self.init_modal(context)

        return {'RUNNING_MODAL'}
        # return {'FINISHED'}

    def modal(self, context, event):

        if not self.first_set:
            if not self.nonmesh_target:
                # re-context since it changed for modal...
                self.obj = context.scene.objects[self.obj.name]
                self.active_mod = self.obj.modifiers[self.active_mod.name]
            self.first_set = True

        if event.type == 'TIMER':
            # silly delay for mode inputs (in case shortcut is clashing on input keys)
            if self.first_run < 1:
                self.first_run += 0.1

        # KEY INPUT
        if self.first_run > 1:

            if event.shift and event.type in self.numbers and event.value == 'PRESS':
                if not self.nonmesh_target:
                    self.switch_active_mod(context, self.mods[event.type], no_reset=True)

            if event.type in self.numbers and event.value == 'PRESS':
                if not self.nonmesh_target:
                    self.switch_active_mod(context, self.mods[event.type])

            if event.type == 'W' and event.value == 'PRESS':
                context.space_data.overlay.show_wireframes = not context.space_data.overlay.show_wireframes
                context.area.tag_redraw()
            elif event.type == 'O' and event.value == 'PRESS':
                if self.nonmesh_target:
                    self.offset_mode = not self.offset_mode
                    if self.offset_mode:
                        self.extrude_mode = False

            elif event.type == 'E' and event.value == 'PRESS':
                if self.nonmesh_target:
                    self.extrude_mode = not self.extrude_mode
                    if self.extrude_mode:
                        self.offset_mode = False

            elif event.type == 'Z' and event.value == 'PRESS':
                if not self.nonmesh_target:
                    self.active_mod.profile = 0.5
            elif event.type == 'X' and event.value == 'PRESS':
                if not self.nonmesh_target:
                    self.active_mod.profile = 0.7
            elif event.type == 'C' and event.value == 'PRESS':
                if not self.nonmesh_target:
                    self.active_mod.profile = 1.0

            elif event.type == 'Q' and event.value == 'PRESS':
                if not self.nonmesh_target:
                    self.active_mod.use_clamp_overlap = not self.active_mod.use_clamp_overlap

            elif event.type == 'A' and event.value == 'PRESS':
                if not self.nonmesh_target and self.active_mod.limit_method == "ANGLE":
                    self.angle_mode = not self.angle_mode

            # SEGMENTS ETC
            if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                if self.nonmesh_target:
                    if event.type == 'WHEELDOWNMOUSE':
                        v = self.obj.data.bevel_resolution - 1
                        self.obj.data.bevel_resolution = v
                        self.seg = v
                    elif event.type == 'WHEELUPMOUSE':
                        v = self.obj.data.bevel_resolution + 1
                        self.obj.data.bevel_resolution = v
                        self.seg = v
                else:
                    if event.type == 'WHEELDOWNMOUSE':
                        v = self.active_mod.segments - 1
                        self.active_mod.segments = v
                        self.seg = v
                    elif event.type == 'WHEELUPMOUSE':
                        v = self.active_mod.segments + 1
                        self.active_mod.segments = v
                        self.seg = v

        if event.shift and event.type == 'MOUSEMOVE':
            # PRECISION MODE (MM)
            p_val = round((0.001 * self.precision_multiplier), 4)
            self.new_mx = event.mouse_x
            if self.new_mx > self.prev_mx:
                self.val += p_val
            elif self.new_mx < self.prev_mx:
                self.val -= p_val
            if self.val < 0:
                self.val = 0
            self.prev_mx = self.new_mx

        elif event.type == 'MOUSEMOVE':
            self.new_mx = event.mouse_x
            if self.new_mx > self.prev_mx:
                self.val += self.sensitivity
            elif self.new_mx < self.prev_mx:
                self.val -= self.sensitivity
            if self.val < 0:
                self.val = 0
            self.prev_mx = self.new_mx

        if self.first_run > 1:
            # MAIN - BEVEL
            if event.type == 'MOUSEMOVE':
                if self.nonmesh_target:
                    if self.extrude_mode:
                        self.obj.data.extrude = self.val
                    elif self.offset_mode:
                        self.obj.data.offset = self.val
                    else:
                        self.obj.data.bevel_depth = self.val
                elif self.angle_mode:
                    self.active_mod.angle_limit = self.val
                elif self.percent_mode:
                    self.active_mod.width_pct = self.val
                else:
                    self.active_mod.width = self.val

            # NAVIGATION
            elif event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
                    event.alt and event.type == "RIGHTMOUSE" or \
                    event.shift and event.type == "MIDDLEMOUSE" or \
                    event.ctrl and event.type == "MIDDLEMOUSE":
                return {'PASS_THROUGH'}

        # EXIT
        if event.type in {'LEFTMOUSE', 'RET', 'SPACE'}:
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.workspace.status_text_set(None)
            self.toggle_overlays(context, restore=True)
            context.area.tag_redraw()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if self.nonmesh_target:
                self.obj.data.bevel_depth = self.og_settings[0]
                self.obj.data.bevel_resolution = self.og_settings[1]
                self.obj.data.extrude = self.og_settings[2]
            else:
                self.restore_mod_settings(self.active_mod)

            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.workspace.status_text_set(None)
            self.toggle_overlays(context, restore=True)
            context.area.tag_redraw()
            return {'FINISHED'}

        return {'RUNNING_MODAL'}
