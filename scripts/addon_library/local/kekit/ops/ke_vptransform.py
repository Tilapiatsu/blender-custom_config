import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty
from mathutils import Vector, Matrix
from .._utils import get_prefs


class KeVPTransform(Operator):
    bl_idname = "view3d.ke_vptransform"
    bl_label = "VP-Transform"
    bl_description = "Runs Grab,Rotate or Scale with View Planes auto-locked based on your viewport rotation."
    bl_options = {'REGISTER'}

    transform: EnumProperty(
        items=[("TRANSLATE", "Translate", "", 1),
               ("ROTATE", "Rotate", "", 2),
               ("RESIZE", "Resize", "", 3),
               ("COPYGRAB", "Duplicate & Move", "", 4),
               ],
        name="Transform",
        default="ROTATE")

    world_only: BoolProperty(default=True)
    rot_got: BoolProperty(default=True)
    loc_got: BoolProperty(default=False)
    scl_got: BoolProperty(default=False)

    tm = None
    obj = None

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        k = get_prefs()
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

            if context.mode != "OBJECT":
                if self.obj.type == "CURVE":
                    bpy.ops.curve.duplicate_move('INVOKE_DEFAULT',
                             TRANSFORM_OT_translate={"orient_matrix_type": og_transform,
                                                     "constraint_axis": vplane,
                                                     "use_proportional_edit": pe_use,
                                                     "proportional_edit_falloff": pe_falloff,
                                                     "use_proportional_connected": pe_connected,
                                                     "use_proportional_projected": pe_proj})
                elif self.obj.type == "MESH":
                    bpy.ops.mesh.duplicate_move('INVOKE_DEFAULT',
                            TRANSFORM_OT_translate={"orient_matrix_type": og_transform,
                                                    "constraint_axis": vplane,
                                                    "use_proportional_edit": pe_use,
                                                    "proportional_edit_falloff": pe_falloff,
                                                    "use_proportional_connected": pe_connected,
                                                    "use_proportional_projected": pe_proj})

            elif context.mode == "OBJECT":
                if not k.tt_linkdupe:
                    bpy.ops.object.duplicate_move('INVOKE_DEFAULT',
                          TRANSFORM_OT_translate={"orient_matrix_type": og_transform,
                                                  "constraint_axis": vplane,
                                                  "use_proportional_edit": pe_use,
                                                  "proportional_edit_falloff": pe_falloff,
                                                  "use_proportional_connected": pe_connected,
                                                  "use_proportional_projected": pe_proj})
                else:
                    bpy.ops.object.duplicate_move_linked('INVOKE_DEFAULT',
                         TRANSFORM_OT_translate={"orient_matrix_type": og_transform,
                                                 "constraint_axis": vplane,
                                                 "use_proportional_edit": pe_use,
                                                 "proportional_edit_falloff": pe_falloff,
                                                 "use_proportional_connected": pe_connected,
                                                 "use_proportional_projected": pe_proj})
            else:
                print("VPT: Invalid selection?")
                return {'CANCELLED'}

        return {'FINISHED'}
