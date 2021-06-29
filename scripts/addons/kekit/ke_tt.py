bl_info = {
    "name": "keTransformToolToggle",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 5),
    "blender": (2, 90, 0),
}

import bpy
from mathutils import Vector

class VIEW3D_OT_KE_TT(bpy.types.Operator):
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
               ("TOGGLE_DUPE", "TT Dupe Mode", "", "TOGGLE_DUPE", 9)
               ],
        name="Level Mode",
        options={'HIDDEN'},
        default="TOGGLE_MOVE")

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "MOVE":
            return "TT Move - can be toggled between using Default Transform Tools / MouseAxis / Viewplane"
        elif properties.mode == "ROTATE":
            return "TT Rotate - can be toggled between using Default Transform Tools / MouseAxis / Viewplane"
        elif properties.mode == "ROTATE":
            return "TT Scale - can be toggled between using Default Transform Tools / MouseAxis / Viewplane"
        elif properties.mode == "TOGGLE_DUPE":
            return "TT Linked Dupe Toggle - Duplicate Linked or not using TT Dupe\n Also used by MouseAxis Dupe & VPtransform Dupe"
        else:
            return "Toggles TT Move/Rotate/Scale between using Default Transform / MouseAxis / Viewplane\n" \
                   "Note: Preferred default state can be set by saving kit settings"

    def execute(self, context):
        tt_handles = bpy.context.scene.kekit.tt_handles
        tt_mode = bpy.context.scene.kekit.tt_mode
        tt_linkdupe = bpy.context.scene.kekit.tt_linkdupe

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
                bpy.ops.view3d.ke_mouse_axis_move('INVOKE_DEFAULT', mode='SCL')
            elif tt_mode[2]:
                bpy.ops.view3d.ke_vptransform('INVOKE_DEFAULT', transform='RESIZE')

        elif self.mode == "DUPE":
            if tt_mode[0]:
                if context.mode == 'EDIT_MESH' and context.object.type == 'MESH':
                    bpy.ops.mesh.duplicate_move('INVOKE_DEFAULT')
                else:
                    if tt_linkdupe:
                        bpy.ops.object.duplicate_move_linked('INVOKE_DEFAULT', OBJECT_OT_duplicate={"linked":True, "mode":'TRANSLATION'})
                    else:
                        bpy.ops.object.duplicate_move('INVOKE_DEFAULT', OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'})
            elif tt_mode[1]:
                bpy.ops.view3d.ke_mouse_axis_move('INVOKE_DEFAULT', mode='DUPE')
            elif tt_mode[2]:
                bpy.ops.view3d.ke_vptransform('INVOKE_DEFAULT', transform='COPYGRAB')

        elif self.mode == "TOGGLE_DUPE":
            bpy.context.scene.kekit.tt_linkdupe = not tt_linkdupe
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
            tt_mode[0] = not tt_mode[0]
            if tt_mode[0]:
                tt_mode[1], tt_mode[2] = False, False

        elif self.mode == "TOGGLE_ROTATE":
            tt_mode[1] = not tt_mode[1]
            if tt_mode[1]:
                tt_mode[0], tt_mode[2] = False, False

        elif self.mode == "TOGGLE_SCALE":
            tt_mode[2] = not tt_mode[2]
            if tt_mode[2]:
                tt_mode[0], tt_mode[1] = False, False

        if not any(tt_mode):
            tt_mode[0], tt_mode[1], tt_mode[1] = True, False, False

        context.area.tag_redraw()

        if context.scene.kekit.tt_select:
            active = context.workspace.tools.from_space_view3d_mode(context.mode, create=False).idname
            builtins = ["builtin.move", "builtin.rotate", "builtin.scale"]
            if active in builtins and not tt_mode[0] or not tt_handles:
                bpy.ops.wm.tool_set_by_id(name="builtin.select")

        return {"FINISHED"}


class VIEW3D_HT_KE_TT(bpy.types.Header):
    bl_label = "Transform Toggle Menu"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        layout = self.layout
        if not bpy.context.scene.kekit.tt_hide:
            tt_mode = bpy.context.scene.kekit.tt_mode
            tt_link = bpy.context.scene.kekit.tt_linkdupe

            row = layout.row(align=True)
            row.operator("view3d.ke_tt", text="", icon='OBJECT_ORIGIN', depress=tt_mode[0]).mode = "TOGGLE_MOVE"
            row.operator("view3d.ke_tt", text="", icon='EMPTY_AXIS', depress=tt_mode[1]).mode = "TOGGLE_ROTATE"
            row.operator("view3d.ke_tt", text="", icon='AXIS_SIDE', depress=tt_mode[2]).mode = "TOGGLE_SCALE"
            row.separator(factor=0.5)
            row.operator("view3d.ke_tt", text="", icon='LINKED', depress=tt_link).mode = "TOGGLE_DUPE"


class VIEW3D_OT_ke_vptransform(bpy.types.Operator):
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

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        self.world_only = bpy.context.scene.kekit.vptransform
        self.rot_got = bpy.context.scene.kekit.rot_got
        self.loc_got = bpy.context.scene.kekit.loc_got
        self.scl_got = bpy.context.scene.kekit.scl_got

        if self.world_only:
            # set Global
            bpy.ops.transform.select_orientation(orientation='GLOBAL')
            og_transform = "GLOBAL"
        else:
            # check current transform
            og_transform = str(context.scene.transform_orientation_slots[0].type)

        # Get Viewplane
        rm = context.space_data.region_3d.view_matrix
        v = Vector(rm[2])
        xz, xy, yz = Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0))
        dic = {(True, False, True): abs(xz.dot(v)), (True, True, False): abs(xy.dot(v)),
               (False, True, True): abs(yz.dot(v))}
        vplane = sorted(dic, key=dic.get)[-1]

        # Set Transforms
        if self.transform == 'TRANSLATE':
            if self.loc_got:
                if og_transform == "GLOBAL":
                    bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=vplane)
                else:
                    bpy.ops.wm.tool_set_by_id(name="builtin.move")
            else:
                bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=vplane)

        elif self.transform == 'ROTATE':
            if self.rot_got:
                if og_transform == "GLOBAL":
                    bpy.ops.transform.rotate('INVOKE_DEFAULT', constraint_axis=vplane)
                else:
                    bpy.ops.wm.tool_set_by_id(name="builtin.rotate")
            else:
                bpy.ops.transform.rotate('INVOKE_DEFAULT', constraint_axis=vplane)

        elif self.transform == 'RESIZE':
            if self.scl_got:
                if og_transform == "GLOBAL":
                    bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=vplane)
                else:
                    bpy.ops.wm.tool_set_by_id(name="builtin.scale")
            else:
                bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=vplane)

        # Copygrab
        elif self.transform == 'COPYGRAB':

            if context.mode == 'EDIT_MESH' and context.object.type == 'MESH':
                bpy.ops.mesh.duplicate('INVOKE_DEFAULT')

            elif context.mode == 'OBJECT':
                if bpy.context.scene.kekit.tt_linkdupe:
                    bpy.ops.object.duplicate('INVOKE_DEFAULT', linked=True)
                else:
                    bpy.ops.object.duplicate('INVOKE_DEFAULT', linked=False)
            else:
                return {'CANCELLED'}
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=vplane)

        return {'FINISHED'}


classes = (VIEW3D_OT_KE_TT, VIEW3D_OT_ke_vptransform)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_HT_header.prepend(VIEW3D_HT_KE_TT.draw)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(VIEW3D_HT_KE_TT.draw)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
