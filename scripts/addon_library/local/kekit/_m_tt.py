import bpy
from bpy.types import Panel, Operator
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import region_2d_to_location_3d
from ._utils import average_vector, getset_transform, restore_transform, mouse_raycast


#
# MODULE UI
#
class UITTModule(Panel):
    bl_idname = "UI_PT_M_TT"
    bl_label = "Transform Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        tt_mode = k.tt_mode
        tt_link = k.tt_linkdupe
        col = layout.column(align=True)
        sub = col.box()
        scol = sub.column(align=True)
        srow = scol.row(align=True)
        srow.label(text="TT Toggle")
        srow.operator("view3d.ke_tt", text="", icon='OBJECT_ORIGIN', depress=tt_mode[0]).mode = "TOGGLE_MOVE"
        srow.operator("view3d.ke_tt", text="", icon='EMPTY_AXIS', depress=tt_mode[1]).mode = "TOGGLE_ROTATE"
        srow.operator("view3d.ke_tt", text="", icon='AXIS_SIDE', depress=tt_mode[2]).mode = "TOGGLE_SCALE"
        scol.separator(factor=0.6)
        srow = scol.row(align=True)
        srow.operator('view3d.ke_tt', text="TT Move").mode = "MOVE"
        srow.operator('view3d.ke_tt', text="TT Rotate").mode = "ROTATE"
        srow.operator('view3d.ke_tt', text="TT Scale").mode = "SCALE"
        srow = scol.row(align=True)
        srow.operator('view3d.ke_tt', text="TT Dupe").mode = "DUPE"
        srow.operator('view3d.ke_tt', text="TT Cycle").mode = "TOGGLE_CYCLE"
        scol.separator(factor=0.6)
        srow = scol.row(align=True)
        srow.prop(k, "tt_handles", text="Giz")
        srow.prop(k, "tt_select", text="Sel")
        srow.prop(k, "mam_scl", text="MAS")
        if tt_link:
            scol.operator("view3d.ke_tt", text="Dupe Linked Toggle", icon="LINKED",
                          depress=tt_link).mode = "TOGGLE_DUPE"
        else:
            scol.operator("view3d.ke_tt", text="Dupe Linked Toggle", icon="UNLINKED",
                          depress=tt_link).mode = "TOGGLE_DUPE"
        scol.operator('view3d.ke_tt', text="Force Unlinked", icon="UNLINKED").mode = "F_DUPE"
        scol.operator('view3d.ke_tt', text="Force Linked", icon="LINKED").mode = "F_LINKDUPE"

        col.separator()
        sub = col.box()
        scol = sub.column(align=True)
        srow = scol.row(align=True)
        srow.label(text="Mouse Axis", icon="EMPTY_AXIS")
        srow = scol.row(align=True)
        split = srow.split(factor=0.89, align=True)
        subrow1 = split.row(align=True)
        subrow1.operator('view3d.ke_mouse_axis_move', text="Move").mode = "MOVE"
        subrow1.operator('view3d.ke_mouse_axis_move', text="Rotate").mode = "ROT"
        subrow1.operator('view3d.ke_mouse_axis_move', text="Scale").mode = "SCL"
        subrow2 = split.row(align=True)
        subrow2.prop(k, "mam_scale_mode", text="C", toggle=True)
        srow = scol.row(align=True)
        srow.operator('view3d.ke_mouse_axis_move', text="Move Dupe").mode = "DUPE"
        srow.operator('view3d.ke_mouse_axis_move', text="Move Cursor").mode = "CURSOR"
        col.separator()

        sub = col.box()
        scol = sub.column(align=True)
        scol.label(text="View Plane", icon="AXIS_SIDE")
        scol.operator("VIEW3D_OT_ke_vptransform", text="VPDupe").transform = "COPYGRAB"
        scol.separator(factor=0.6)
        row = scol.row(align=True)
        row.operator("VIEW3D_OT_ke_vptransform", text="VPGrab").transform = "TRANSLATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPRotate").transform = "ROTATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPResize").transform = "RESIZE"
        row = scol.row(align=True)
        row.prop(k, "loc_got", text="GGoT")
        row.prop(k, "rot_got", text="RGoT")
        row.prop(k, "scl_got", text="SGoT")
        scol.prop(k, "vptransform", toggle=True)


class KeTTHeader(bpy.types.Header):
    bl_idname = "VIEW3D_HT_KE_TT"
    bl_label = "Transform Toggle Menu"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        tt_mode = k.tt_mode
        tt_link = k.tt_linkdupe
        row = layout.row(align=True)
        row.operator("view3d.ke_tt", text="", icon='OBJECT_ORIGIN', depress=tt_mode[0]).mode = "TOGGLE_MOVE"
        row.operator("view3d.ke_tt", text="", icon='EMPTY_AXIS', depress=tt_mode[1]).mode = "TOGGLE_ROTATE"
        row.operator("view3d.ke_tt", text="", icon='AXIS_SIDE', depress=tt_mode[2]).mode = "TOGGLE_SCALE"
        row.separator(factor=0.5)
        if tt_link:
            row.operator("view3d.ke_tt", text="", icon='LINKED', depress=tt_link).mode = "TOGGLE_DUPE"
        else:
            row.operator("view3d.ke_tt", text="", icon='UNLINKED', depress=tt_link).mode = "TOGGLE_DUPE"


#
# MODULE OPERATORS (MISC)
#
class KeTT(Operator):
    bl_idname = "view3d.ke_tt"
    bl_label = "Transform Tool Toggle"
    bl_options = {'REGISTER'}

    mode: bpy.props.EnumProperty(
        items=[("TOGGLE_MOVE", "TT Move Mode", "", "TOGGLE_MOVE", 1),
               ("TOGGLE_ROTATE", "TT Rotate Mode", "", "TOGGLE_ROTATE", 2),
               ("TOGGLE_SCALE", "TT Scale Mode", "", "TOGGLE_SCALE", 3),
               ("TOGGLE_CYCLE", "TT Cycle Modes", "", "TOGGLE_CYCLE", 4),
               ("MOVE", "TT Move", "", "MOVE", 5),
               ("ROTATE", "TT Rotate", "", "ROTATE", 6),
               ("SCALE", "TT Scale", "", "SCALE", 7),
               ("DUPE", "TT Dupe", "", "DUPE", 8),
               ("TOGGLE_DUPE", "TT Dupe Mode", "", "TOGGLE_DUPE", 9),
               ("F_DUPE", "TT Dupe Forced", "", "F_DUPE", 10),
               ("F_LINKDUPE", "TT LinkDupe Forced", "", "F_LINKDUPE", 11)
               ],
        name="Level Mode",
        options={'HIDDEN'},
        default="TOGGLE_MOVE")

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "MOVE":
            return "TT Move - can be toggled between using Default Transform Tools / MouseAxis / Viewplane\n" \
                   "Can also be used in 2D editors (UV, Nodes)"
        elif properties.mode == "ROTATE":
            return "TT Rotate - can be toggled between using Default Transform Tools / MouseAxis / Viewplane\n" \
                   "Can also be used in 2D editors (UV, Nodes)"
        elif properties.mode == "ROTATE":
            return "TT Scale - can be toggled between using Default Transform Tools / MouseAxis / Viewplane\n" \
                   "Can also be used in 2D editors (UV, Nodes)"
        elif properties.mode == "TOGGLE_DUPE":
            return "TT Linked Dupe Toggle - Duplicate Linked or not using TT Dupe\n" \
                   "Also used by MouseAxis Dupe & VPtransform Dupe"
        elif properties.mode == "F_DUPE":
            return "TT Dupe Forced - Overrides Toggle value -> Unlinked duplication"
        elif properties.mode == "F_LINKDUPE":
            return "TT Linked Dupe Forced - Overrides Toggle value -> Linked duplication"
        else:
            return "Toggles TT Move/Rotate/Scale between using Default Transform / MouseAxis / Viewplane\n" \
                   "Note: Preferred default state can be set by saving kit settings\n" \
                   "Icons visibility: keKit/Context Tools/TT Toggle/Hide Icons"

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        tt_handles = k.tt_handles
        tt_mode = k.tt_mode
        tt_linkdupe = k.tt_linkdupe

        # Forcing modes overrides
        if self.mode == "F_DUPE":
            self.mode = "DUPE"
            tt_linkdupe = False
            k.tt_linkdupe = False
        elif self.mode == "F_LINKDUPE":
            self.mode = "DUPE"
            tt_linkdupe = True
            k.tt_linkdupe = True

        if context.space_data.type in {"IMAGE_EDITOR", "NODE_EDITOR"}:
            if tt_mode[2]:
                tt_mode = (False, True, False)

        if self.mode == "MOVE":
            if tt_mode[0]:
                if tt_handles:
                    bpy.ops.wm.tool_set_by_id(name="builtin.move")
                else:
                    bpy.ops.transform.translate('INVOKE_DEFAULT')
            elif tt_mode[1]:
                bpy.ops.view3d.ke_mouse_axis_move('INVOKE_DEFAULT', mode='MOVE')
            elif tt_mode[2]:
                bpy.ops.view3d.ke_vptransform('INVOKE_DEFAULT', transform='TRANSLATE')

        elif self.mode == "ROTATE":
            if tt_mode[0]:
                if tt_handles:
                    bpy.ops.wm.tool_set_by_id(name="builtin.rotate")
                else:
                    bpy.ops.transform.rotate('INVOKE_DEFAULT')
            elif tt_mode[1]:
                bpy.ops.view3d.ke_mouse_axis_move('INVOKE_DEFAULT', mode='ROT')
            elif tt_mode[2]:
                bpy.ops.view3d.ke_vptransform('INVOKE_DEFAULT', transform='ROTATE')

        elif self.mode == "SCALE":

            if tt_mode[0]:
                if tt_handles:
                    bpy.ops.wm.tool_set_by_id(name="builtin.scale")
                else:
                    bpy.ops.transform.resize('INVOKE_DEFAULT')

            elif tt_mode[1]:
                if not k.mam_scl:
                    bpy.ops.transform.resize('INVOKE_DEFAULT')
                else:
                    bpy.ops.view3d.ke_mouse_axis_move('INVOKE_DEFAULT', mode='SCL')

            elif tt_mode[2]:
                bpy.ops.view3d.ke_vptransform('INVOKE_DEFAULT', transform='RESIZE')

        elif self.mode == "DUPE":
            if tt_mode[0]:
                if context.mode == 'EDIT_MESH' and context.object.type == 'MESH':
                    bpy.ops.mesh.duplicate_move('INVOKE_DEFAULT')
                elif context.mode != "OBJECT" and context.object:
                    if context.object.type == "CURVE":
                        bpy.ops.curve.duplicate('INVOKE_DEFAULT')
                else:
                    if tt_linkdupe:
                        bpy.ops.object.duplicate_move_linked(
                            'INVOKE_DEFAULT', OBJECT_OT_duplicate={"linked": True, "mode": 'TRANSLATION'})
                    else:
                        bpy.ops.object.duplicate_move(
                            'INVOKE_DEFAULT', OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'})
            elif tt_mode[1]:
                bpy.ops.view3d.ke_mouse_axis_move('INVOKE_DEFAULT', mode='DUPE')
            elif tt_mode[2]:
                bpy.ops.view3d.ke_vptransform('INVOKE_DEFAULT', transform='COPYGRAB')

        elif self.mode == "TOGGLE_DUPE":
            k.tt_linkdupe = not tt_linkdupe
            context.area.tag_redraw()
            return {"FINISHED"}

        elif self.mode == "TOGGLE_CYCLE":
            if tt_mode[0]:
                tt_mode[0], tt_mode[1], tt_mode[2] = False, True, False
            elif tt_mode[1]:
                tt_mode[0], tt_mode[1], tt_mode[2] = False, False, True
            else:
                tt_mode[0], tt_mode[1], tt_mode[2] = True, False, False

        # Note: These actually set the TT mode : not type...naming sux
        elif self.mode == "TOGGLE_MOVE":
            # tt_mode[0] = not tt_mode[0]
            tt_mode[0] = True
            if tt_mode[0]:
                tt_mode[1], tt_mode[2] = False, False

        elif self.mode == "TOGGLE_ROTATE":
            # tt_mode[1] = not tt_mode[1]
            tt_mode[1] = True
            if tt_mode[1]:
                tt_mode[0], tt_mode[2] = False, False

        elif self.mode == "TOGGLE_SCALE":
            # tt_mode[2] = not tt_mode[2]
            tt_mode[2] = True
            if tt_mode[2]:
                tt_mode[0], tt_mode[1] = False, False

        if not any(tt_mode):
            tt_mode[0], tt_mode[1], tt_mode[1] = True, False, False

        context.area.tag_redraw()

        if k.tt_select and self.mode in {'TOGGLE_MOVE', 'TOGGLE_SCALE', 'TOGGLE_ROTATE', 'TOGGLE_CYCLE'}:
            active = context.workspace.tools.from_space_view3d_mode(context.mode, create=False).idname
            builtins = ["builtin.move", "builtin.rotate", "builtin.scale"]
            if active in builtins and not tt_mode[0] or not tt_handles:
                bpy.ops.wm.tool_set_by_id(name="builtin.select")

        return {"FINISHED"}


class KeVPTransform(bpy.types.Operator):
    bl_idname = "view3d.ke_vptransform"
    bl_label = "VP-Transform"
    bl_description = "Runs Grab,Rotate or Scale with View Planes auto-locked based on your viewport rotation."
    bl_options = {'REGISTER'}

    transform: bpy.props.EnumProperty(
        items=[("TRANSLATE", "Translate", "", 1),
               ("ROTATE", "Rotate", "", 2),
               ("RESIZE", "Resize", "", 3),
               ("COPYGRAB", "Duplicate & Move", "", 4),
               ],
        name="Transform",
        default="ROTATE")

    world_only: bpy.props.BoolProperty(default=True)
    rot_got: bpy.props.BoolProperty(default=True)
    loc_got: bpy.props.BoolProperty(default=False)
    scl_got: bpy.props.BoolProperty(default=False)

    tm = None
    obj = None

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        k = context.preferences.addons[__package__].preferences
        sel_obj = [o for o in context.selected_objects]
        if not sel_obj:
            self.report({"INFO"}, " No objects selected ")
            return {'CANCELLED'}

        if sel_obj and context.object is None:
            self.obj = sel_obj[0]

        elif context.object is not None:
            self.obj = context.object
        else:
            self.report({"INFO"}, " No valid objects selected ")
            return {'CANCELLED'}

        context.view_layer.objects.active = self.obj

        self.world_only = k.vptransform
        self.rot_got = k.rot_got
        self.loc_got = k.loc_got
        self.scl_got = k.scl_got

        ct = context.scene.tool_settings
        pe_use = ct.use_proportional_edit
        pe_connected = ct.use_proportional_connected
        pe_proj = ct.use_proportional_projected
        pe_falloff = ct.proportional_edit_falloff

        if self.world_only:
            # set Global
            bpy.ops.transform.select_orientation(orientation='GLOBAL')
            og_transform = "GLOBAL"
        else:
            # check current transform
            og_transform = str(context.scene.transform_orientation_slots[0].type)

        # Transform
        if og_transform == "GLOBAL":
            self.tm = Matrix.Identity(3)

        elif og_transform == "CURSOR":
            self.tm = context.scene.cursor.matrix.to_3x3()

        elif og_transform == "LOCAL" or og_transform == "NORMAL":
            if og_transform == "NORMAL":
                og_transform = "LOCAL"
            self.tm = self.obj.matrix_world.to_3x3().normalized()

        elif og_transform == "VIEW":
            self.tm = context.space_data.region_3d.view_matrix.inverted().to_3x3()

        elif og_transform == "GIMBAL":
            self.report({"INFO"}, "Gimbal Orientation not supported")
            return {'CANCELLED'}

        # Get Viewplane
        rm = context.space_data.region_3d.view_matrix
        if og_transform == "GLOBAL":
            v = Vector(rm[2])
        else:
            v = self.tm.inverted() @ Vector(rm[2]).to_3d()

        xz, xy, yz = Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0))
        dic = {(True, False, True): abs(xz.dot(v)), (True, True, False): abs(xy.dot(v)),
               (False, True, True): abs(yz.dot(v))}
        vplane = sorted(dic, key=dic.get)[-1]

        # Set Transforms
        if self.transform == 'TRANSLATE':
            if self.loc_got:
                if og_transform == "GLOBAL":
                    bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=vplane,
                                                use_proportional_edit=pe_use,
                                                proportional_edit_falloff=pe_falloff,
                                                use_proportional_connected=pe_connected,
                                                use_proportional_projected=pe_proj
                                                )
                else:
                    bpy.ops.wm.tool_set_by_id(name="builtin.move")
            else:
                bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=vplane,
                                            orient_matrix_type=og_transform, orient_type=og_transform,
                                            use_proportional_edit=pe_use,
                                            proportional_edit_falloff=pe_falloff,
                                            use_proportional_connected=pe_connected,
                                            use_proportional_projected=pe_proj
                                            )

        elif self.transform == 'ROTATE':
            if self.rot_got:
                if og_transform == "GLOBAL":
                    bpy.ops.transform.rotate('INVOKE_DEFAULT', constraint_axis=vplane,
                                             use_proportional_edit=pe_use,
                                             proportional_edit_falloff=pe_falloff,
                                             use_proportional_connected=pe_connected,
                                             use_proportional_projected=pe_proj
                                             )
                else:
                    bpy.ops.wm.tool_set_by_id(name="builtin.rotate")
            else:
                bpy.ops.transform.rotate('INVOKE_DEFAULT', constraint_axis=vplane,
                                         orient_matrix_type=og_transform, orient_type=og_transform,
                                         use_proportional_edit=pe_use,
                                         proportional_edit_falloff=pe_falloff,
                                         use_proportional_connected=pe_connected,
                                         use_proportional_projected=pe_proj
                                         )

        elif self.transform == 'RESIZE':
            if self.scl_got:
                if og_transform == "GLOBAL":
                    bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=vplane,
                                             use_proportional_edit=pe_use,
                                             proportional_edit_falloff=pe_falloff,
                                             use_proportional_connected=pe_connected,
                                             use_proportional_projected=pe_proj
                                             )
                else:
                    bpy.ops.wm.tool_set_by_id(name="builtin.scale")
            else:
                bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=vplane,
                                         orient_matrix_type=og_transform, orient_type=og_transform,
                                         use_proportional_edit=pe_use,
                                         proportional_edit_falloff=pe_falloff,
                                         use_proportional_connected=pe_connected,
                                         use_proportional_projected=pe_proj
                                         )

        # Copygrab
        elif self.transform == 'COPYGRAB':

            if context.mode == 'EDIT_MESH' and context.object.type == 'MESH':
                bpy.ops.mesh.duplicate('INVOKE_DEFAULT')
            elif context.mode != 'OBJECT' and self.obj.type == "CURVE":
                bpy.ops.curve.duplicate('INVOKE_DEFAULT')
            elif context.mode == 'OBJECT':
                if k.tt_linkdupe:
                    bpy.ops.object.duplicate('INVOKE_DEFAULT', linked=True)
                else:
                    bpy.ops.object.duplicate('INVOKE_DEFAULT', linked=False)
            else:
                return {'CANCELLED'}
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=vplane,
                                        orient_matrix_type=og_transform, orient_type=og_transform)

        return {'FINISHED'}


class KeMouseAxisMove(bpy.types.Operator):
    bl_idname = "view3d.ke_mouse_axis_move"
    bl_label = "Mouse Axis Move"
    bl_description = "Runs Grab/Rotate or Resize with Axis auto-locked based on your mouse movement\n" \
                     "(or viewport when rotating)\n" \
                     "using -recalculated- orientation based on the selected Orientation type."
    bl_options = {'REGISTER'}

    mode: bpy.props.EnumProperty(
        items=[("MOVE", "Move", "", 1),
               ("DUPE", "Duplicate", "", 2),
               ("ROT", "Rotate", "", 3),
               ("SCL", "Resize", "", 4),
               ("CURSOR", "Cursor", "", 5)
               ],
        name="Mode",
        default="MOVE")

    mouse_pos = Vector((0, 0))
    startpos = Vector((0, 0, 0))
    tm = Matrix().to_3x3()
    rv = None
    ot = "GLOBAL"
    obj = None
    obj_loc = None
    em_types = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
    em_normal_mode = False
    pe_use = False
    pe_proj = False
    pe_connected = False
    pe_falloff = "SMOOTH"
    is_editor2d = False
    sculpthack = False
    scale_mode = False

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "DUPE":
            return "Duplicates mesh/object before running Mouse Axis Move"
        elif properties.mode == "CURSOR":
            return "Mouse Axis Move for the Cursor. Global orientation or Cursor orientation " \
                   "(used in all modes except Global)"
        else:
            return "Runs Grab, Rotate or Resize with Axis auto-locked based on your mouse movement " \
                   "(or viewport when Rot) " \
                   "using recalculated orientation based on the selected Orientation type.\n" \
                   "Can also be used in 2D editors (UV, Nodes)"

    @classmethod
    def get_mpos(cls, context, coord, pos):
        region = context.region
        rv3d = context.region_data
        return region_2d_to_location_3d(region, rv3d, coord, pos)

    def invoke(self, context, event):
        k = context.preferences.addons[__package__].preferences
        self.scale_mode = k.mam_scale_mode

        if context.mode == "SCULPT":
            self.sculpthack = True
            bpy.ops.object.mode_set(mode="OBJECT")

        # mouse track start
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)

        # Proportional Edit Support
        ct = context.scene.tool_settings
        self.pe_use = ct.use_proportional_edit
        self.pe_connected = ct.use_proportional_connected
        self.pe_proj = ct.use_proportional_projected
        self.pe_falloff = ct.proportional_edit_falloff

        if context.space_data.type in {"IMAGE_EDITOR", "NODE_EDITOR"}:
            self.is_editor2d = True
            if self.mode == "ROT":
                self.ot = "VIEW"
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

        sel_obj = [o for o in context.selected_objects]

        self.obj = context.active_object

        if not sel_obj and context.object:
            sel_obj = [context.object]

        if sel_obj:
            if not self.obj:
                self.obj = sel_obj[0]

            if len(sel_obj) > 1:
                self.obj_loc = average_vector([o.location for o in sel_obj])
            else:
                self.obj_loc = sel_obj[0].location

        if not self.obj:
            self.report({"INFO"}, " No valid objects selected ")
            return {'CANCELLED'}

        context.view_layer.objects.active = self.obj

        # Mouse vec start ( lazy edit mode overwrite later)
        if self.mode != "ROT":
            self.startpos = self.get_mpos(context, self.mouse_pos, self.obj_loc)

        is_em = False
        if self.obj.type == "GPENCIL":
            is_em = bool(self.obj.data.use_stroke_edit_mode)
        else:
            if self.obj.type in self.em_types:
                is_em = bool(self.obj.data.is_editmode)

        if self.mode == "SCL" and self.scale_mode:
            # Check if mouse is over obj to use unconstrained scale
            if is_em:
                bpy.ops.object.mode_set(mode="OBJECT")
            hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos, evaluated=True)
            if is_em:
                bpy.ops.object.mode_set(mode="EDIT")

            if hit_obj is not None:
                # Check if mouse is over SELECTED ELEMENTS to use unconstrained scale
                if is_em and hit_obj.name == self.obj.name:
                    sel_poly = [p.index for p in self.obj.data.polygons if p.select]
                    if hit_face in sel_poly:
                        bpy.ops.transform.resize('INVOKE_DEFAULT')
                        return {'FINISHED'}
                # Object mode selection check
                if not is_em:
                    c = [o.name for o in context.selected_objects]
                    if hit_obj.name in c:
                        bpy.ops.transform.resize('INVOKE_DEFAULT')
                        return {'FINISHED'}

        # get rotation vectors
        og = getset_transform(setglobal=False)
        self.ot = og[0]

        if og[0] == "NORMAL" and not is_em:
            og[0] = "LOCAL"
            bpy.ops.transform.select_orientation(orientation="LOCAL")

        if self.mode == "CURSOR":
            if og[0] == "GLOBAL":
                pass
            else:
                og[0] = "CURSOR"
                self.tm = context.scene.cursor.matrix.to_3x3()

        else:
            # check type
            if is_em:
                em = True
            else:
                em = "OBJECT"

            if og[0] == "GLOBAL":
                pass

            elif og[0] == "CURSOR":
                self.tm = context.scene.cursor.matrix.to_3x3()

            elif og[0] == "LOCAL" or og[0] == "NORMAL" and not em:
                self.tm = self.obj.matrix_world.to_3x3().normalized()
                self.ot = "LOCAL"

            elif og[0] == "VIEW":
                self.tm = context.space_data.region_3d.view_matrix.inverted().to_3x3()

            elif og[0] == "GIMBAL":
                self.report({"INFO"}, "Gimbal Orientation not supported")
                return {'CANCELLED'}

            # NORMAL / SELECTION
            elif em != "OBJECT":
                self.obj.update_from_editmode()
                sel = [v for v in self.obj.data.vertices if v.select]
                sel_co = average_vector([self.obj.matrix_world @ v.co for v in sel])
                # Use selection for mouse start 2d pos instead of obj loc
                self.startpos = self.get_mpos(context, self.mouse_pos, sel_co)

                if sel:
                    try:
                        bpy.ops.transform.create_orientation(name='keTF', use_view=False, use=True, overwrite=True)
                        self.tm = context.scene.transform_orientation_slots[0].custom_orientation.matrix.copy()
                        bpy.ops.transform.delete_orientation()
                        restore_transform(og)
                        # if og[1] == "ACTIVE_ELEMENT":
                        # self.em_normal_mode = Truew

                    except RuntimeError:
                        print("Fallback: Invalid selection for Orientation - Using Local")
                        # Normal O. with a entire cube selected will fail create_o.
                        bpy.ops.transform.select_orientation(orientation='LOCAL')
                        self.tm = self.obj.matrix_world.to_3x3()
                else:
                    self.report({"INFO"}, " No elements selected ")
                    return {'CANCELLED'}
            else:
                self.report({"INFO"}, "Unsupported Orientation Mode")
                return {'CANCELLED'}

            if self.mode == "DUPE":
                if context.mode != "OBJECT" and self.obj.type == "CURVE":
                    bpy.ops.curve.duplicate('INVOKE_DEFAULT')
                elif em != "OBJECT":
                    bpy.ops.mesh.duplicate('INVOKE_DEFAULT')
                else:
                    if k.tt_linkdupe:
                        bpy.ops.object.duplicate('INVOKE_DEFAULT', linked=True)
                    else:
                        bpy.ops.object.duplicate('INVOKE_DEFAULT', linked=False)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            # mouse track end candidate
            new_mouse_pos = Vector((int(event.mouse_region_x), int(event.mouse_region_y)))
            t1 = abs(new_mouse_pos[0] - self.mouse_pos[0])
            t2 = abs(new_mouse_pos[1] - self.mouse_pos[1])

            if t1 > 10 or t2 > 10 or self.mode == "ROT":

                if self.is_editor2d:
                    if t1 > 10:
                        axis = True, False, False
                        oa = "Z"
                    else:
                        axis = False, True, False
                        oa = "Z"
                    if self.mode == "ROT":
                        axis = False, False, False
                else:
                    if self.mode == "ROT":
                        # no need to track mouse vec
                        rm = context.space_data.region_3d.view_matrix
                        v = self.tm.inverted() @ Vector(rm[2]).to_3d()
                        x, y, z = abs(v[0]), abs(v[1]), abs(v[2])

                    else:
                        # mouse vec end
                        newpos = self.get_mpos(context, new_mouse_pos, self.startpos)
                        v = self.tm.inverted() @ Vector(self.startpos - newpos).normalized()
                        x, y, z = abs(v[0]), abs(v[1]), abs(v[2])

                    if x > y and x > z:
                        axis = True, False, False
                        oa = "X"
                    elif y > x and y > z:
                        axis = False, True, False
                        oa = "Y"
                    else:
                        axis = False, False, True
                        oa = "Z"

                if self.mode == "ROT":
                    bpy.ops.transform.rotate('INVOKE_DEFAULT', orient_axis=oa, orient_type=self.ot,
                                             orient_matrix=self.tm, orient_matrix_type=self.ot,
                                             constraint_axis=axis, mirror=True,
                                             use_proportional_edit=self.pe_use,
                                             proportional_edit_falloff=self.pe_falloff,
                                             use_proportional_connected=self.pe_connected,
                                             use_proportional_projected=self.pe_proj)
                elif self.mode == "SCL":
                    bpy.ops.transform.resize('INVOKE_DEFAULT', orient_type=self.ot,
                                             orient_matrix=self.tm, orient_matrix_type=self.ot,
                                             constraint_axis=axis, mirror=True,
                                             use_proportional_edit=self.pe_use,
                                             proportional_edit_falloff=self.pe_falloff,
                                             use_proportional_connected=self.pe_connected,
                                             use_proportional_projected=self.pe_proj)

                elif self.mode == "CURSOR":
                    bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type=self.ot, orient_matrix_type=self.ot,
                                                constraint_axis=axis, mirror=True,
                                                use_proportional_edit=self.pe_use,
                                                proportional_edit_falloff=self.pe_falloff,
                                                use_proportional_connected=self.pe_connected,
                                                use_proportional_projected=self.pe_proj)
                else:
                    # if self.em_normal_mode:
                    #     axis = False, False, True
                    bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type=self.ot, orient_matrix_type=self.ot,
                                                constraint_axis=axis, mirror=True,
                                                use_proportional_edit=self.pe_use,
                                                proportional_edit_falloff=self.pe_falloff,
                                                use_proportional_connected=self.pe_connected,
                                                use_proportional_projected=self.pe_proj)
                if self.sculpthack:
                    bpy.ops.object.mode_set(mode="SCULPT")
                return {'FINISHED'}

        elif event.type == 'ESC':
            # Justincase
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


#
# MODULE REGISTRATION
#
classes = (
    UITTModule,
    KeMouseAxisMove,
    KeVPTransform,
    KeTT,
    KeTTHeader
)

modules = (
)


def register():
    k = bpy.context.preferences.addons[__package__].preferences
    if k.m_tt:
        for c in classes:
            bpy.utils.register_class(c)
        
        for m in modules:
            m.register()

        if k.tt_icon_pos == "LEFT":
            bpy.types.VIEW3D_HT_header.prepend(KeTTHeader.draw)
        elif k.tt_icon_pos == "CENTER":
            bpy.types.VIEW3D_MT_editor_menus.append(KeTTHeader.draw)
        elif k.tt_icon_pos == "RIGHT":
            bpy.types.VIEW3D_HT_header.append(KeTTHeader.draw)


def unregister():
    if "bl_rna" in UITTModule.__dict__:
        bpy.types.VIEW3D_HT_header.remove(KeTTHeader.draw)
        bpy.types.VIEW3D_MT_editor_menus.remove(KeTTHeader.draw)

        for c in reversed(classes):
            bpy.utils.unregister_class(c)
        
        for m in modules:
            m.unregister()


if __name__ == "__main__":
    register()
