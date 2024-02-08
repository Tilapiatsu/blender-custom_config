import bpy
from bpy.types import Operator
from .._utils import get_prefs


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
        elif properties.mode == "DUPE":
            return "Duplicates mesh/object & runs selected TT Move Operator (Grab/MAM/VPT)"
        elif properties.mode == "F_DUPE":
            return "TT Dupe Forced - Overrides Toggle value -> Unlinked duplication"
        elif properties.mode == "F_LINKDUPE":
            return "TT Linked Dupe Forced - Overrides Toggle value -> Linked duplication"
        else:
            return "Toggles TT Move/Rotate/Scale between using Default Transform / MouseAxis / Viewplane\n" \
                   "Note: Preferred default state can be set by saving kit settings\n" \
                   "Icons visibility: keKit/Context Tools/TT Toggle/Hide Icons"

    def execute(self, context):
        k = get_prefs()
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
