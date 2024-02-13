import bpy
from bpy.props import EnumProperty
from bpy.types import Operator
from bpy_extras.view3d_utils import region_2d_to_location_3d
from mathutils import Vector, Matrix
from .._utils import average_vector, getset_transform, restore_transform, mouse_raycast, get_prefs


class KeMouseAxisMove(Operator):
    bl_idname = "view3d.ke_mouse_axis_move"
    bl_label = "Mouse Axis Move"
    bl_description = "Runs Grab/Rotate or Resize with Axis auto-locked based on your mouse movement\n" \
                     "(or viewport when rotating)\n" \
                     "using -recalculated- orientation based on the selected Orientation type."
    bl_options = {'REGISTER'}

    mode: EnumProperty(
        items=[("MOVE", "Move", "", 1),
               ("DUPE", "Duplicate", "", 2),
               ("ROT", "Rotate", "", 3),
               ("SCL", "Resize", "", 4),
               ("CURSOR", "Cursor", "", 5),
               ("F_DUPE", "Duplicate Unlinked", "", 6),
               ("F_LINKDUPE", "Duplicate Linked", "", 7),
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
    linkdupe = False

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "DUPE":
            return "Duplicates mesh/object before running Mouse Axis Move"
        elif properties.mode == "CURSOR":
            return "Mouse Axis Move for the Cursor. Global orientation or Cursor orientation " \
                   "(Cursor mode used in all modes except Global)"
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
        k = get_prefs()
        self.scale_mode = k.mam_scale_mode
        self.linkdupe = bool(k.tt_linkdupe)

        # Forcing modes overrides
        if self.mode == "F_DUPE":
            self.mode = "DUPE"
            self.linkdupe = False

        elif self.mode == "F_LINKDUPE":
            self.mode = "DUPE"
            self.linkdupe = True

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
                    except RuntimeError:
                        print("Fallback: Invalid selection for Orientation - Using Local")
                        # Normal O. with an entire cube selected will fail create_o.
                        bpy.ops.transform.select_orientation(orientation='LOCAL')
                        self.tm = self.obj.matrix_world.to_3x3()
                else:
                    self.report({"INFO"}, " No elements selected ")
                    return {'CANCELLED'}
            else:
                self.report({"INFO"}, "Unsupported Orientation Mode")
                return {'CANCELLED'}

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
                else:
                    if self.mode == "DUPE":

                        if context.mode != "OBJECT":
                            if self.obj.type == "CURVE":
                                # bpy.ops.curve.duplicate('INVOKE_DEFAULT')
                                bpy.ops.curve.duplicate_move('INVOKE_DEFAULT',
                                    TRANSFORM_OT_translate={"orient_type": self.ot,
                                                            "orient_matrix_type": self.ot,
                                                            "constraint_axis": axis,
                                                            "use_proportional_edit": self.pe_use,
                                                            "proportional_edit_falloff": self.pe_falloff,
                                                            "use_proportional_connected": self.pe_connected,
                                                            "use_proportional_projected": self.pe_proj})
                            elif self.obj.type == "MESH":
                                # bpy.ops.mesh.duplicate('INVOKE_DEFAULT')
                                bpy.ops.mesh.duplicate_move('INVOKE_DEFAULT',
                                    TRANSFORM_OT_translate={"orient_type": self.ot,
                                                            "orient_matrix_type": self.ot,
                                                            "constraint_axis": axis,
                                                            "use_proportional_edit": self.pe_use,
                                                            "proportional_edit_falloff": self.pe_falloff,
                                                            "use_proportional_connected": self.pe_connected,
                                                            "use_proportional_projected": self.pe_proj})

                        elif context.mode == "OBJECT":
                            if not self.linkdupe:
                                bpy.ops.object.duplicate_move('INVOKE_DEFAULT',
                                    TRANSFORM_OT_translate={"orient_type": self.ot,
                                                            "orient_matrix_type": self.ot,
                                                            "constraint_axis": axis,
                                                            "use_proportional_edit": self.pe_use,
                                                            "proportional_edit_falloff": self.pe_falloff,
                                                            "use_proportional_connected": self.pe_connected,
                                                            "use_proportional_projected": self.pe_proj})
                            else:
                                bpy.ops.object.duplicate_move_linked('INVOKE_DEFAULT',
                                    TRANSFORM_OT_translate={"orient_type": self.ot,
                                                            "orient_matrix_type": self.ot,
                                                            "constraint_axis": axis,
                                                            "use_proportional_edit": self.pe_use,
                                                            "proportional_edit_falloff": self.pe_falloff,
                                                            "use_proportional_connected": self.pe_connected,
                                                            "use_proportional_projected": self.pe_proj})
                    else:
                        bpy.ops.transform.translate('INVOKE_DEFAULT',
                                                    orient_type=self.ot, orient_matrix_type=self.ot,
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
