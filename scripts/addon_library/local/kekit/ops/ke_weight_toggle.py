from bpy.types import Operator
from bpy.props import EnumProperty
import bmesh
import bpy
from .._utils import refresh_ui, get_prefs, get_selected


class KeWeightToggle(Operator):
    bl_idname = "mesh.ke_toggle_weight"
    bl_label = "Toggle Weight"
    bl_description = "Toggles specified weighting on or off on selected elements"
    bl_options = {'REGISTER', 'UNDO'}

    wtype : EnumProperty(
        items=[("BEVEL", "Bevel Weight", "", 1),
               ("CREASE", "Crease Weight", "", 2)],
        name="Weight Type",
        default="BEVEL", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode != "OBJECT"

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects if o.type == "MESH" and o.mode != "OBJECT"]
        if not sel_obj:
            obj = get_selected(context)
            obj.select_set(True)
            sel_obj = [obj]

        k = get_prefs()
        em = context.tool_settings.mesh_select_mode
        vertex_mode = bool(em[0])
        face_mode = bool(em[2])
        if face_mode:
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

        if self.wtype == "CREASE":
            v_type = "crease_vert"
            e_type = "crease_edge"
        else:
            v_type = "bevel_weight_vert"
            e_type = "bevel_weight_edge"

        for o in sel_obj:
            mesh = o.data
            bm = bmesh.from_edit_mesh(mesh)

            if vertex_mode:
                bw = bm.verts.layers.float.get(v_type, None)
            else:
                bw = bm.edges.layers.float.get(e_type, None)

            if bw is not None:

                vals = []
                if vertex_mode:
                    sel = [v for v in bm.verts if v.select]
                else:
                    sel = [e for e in bm.edges if e.select]
                for element in sel:
                    # Inverting here
                    val = float(not round(element[bw]))
                    vals.append(val)

                if k.toggle_same and len(vals) > 1:
                    if all(v == 0 for v in vals):
                        val = 0
                    elif all(v == 1 for v in vals):
                        val = 1
                    else:
                        c = max(set(vals), key=vals.count)
                        # Reverting, for "same" option
                        if c == 1:
                            val = 0
                        else:
                            val = 1
                    vals = [val] * len(vals)

                for element, val in zip(sel, vals):
                    element[bw] = val
            else:
                if vertex_mode:
                    bw = bm.verts.layers.float.new(v_type)
                    sel = [v for v in bm.verts if v.select]
                else:
                    bw = bm.edges.layers.float.new(e_type)
                    sel = [e for e in bm.edges if e.select]
                for element in sel:
                    element[bw] = 1.0

            bmesh.update_edit_mesh(mesh)

            # Add modifier if not present
            if k.toggle_add:
                bmod = []
                smod = []
                wmod = []
                for m in o.modifiers:
                    if m.type == "BEVEL":
                        if m.limit_method == "WEIGHT":
                            bmod.append(m)
                    elif m.type == "SUBSURF":
                        smod.append(m)
                    elif m.type == "WEIGHTED_NORMAL":
                        wmod.append(m)

                if not bmod or not smod:
                    bpy.ops.object.editmode_toggle()
                    if not bmod and self.wtype == "BEVEL":
                        mod = o.modifiers.new("Bevel", "BEVEL")
                        mod.width = 0.02
                        mod.limit_method = "WEIGHT"
                        mod.miter_outer = 'MITER_ARC'
                        mod.is_active = True
                        mod.show_expanded = True
                        if k.korean:
                            mod.profile = 1
                            mod.segments = 2
                        else:
                            mod.segments = 3

                        # Auto add WN mod too (or sort if present) ?
                        # if not k.korean:
                        #     if not wmod:
                        #         context.object.data.use_auto_smooth = True
                        #         mod = o.modifiers.new(name="kWeightedN", type="WEIGHTED_NORMAL")
                        #         mod.keep_sharp = True
                        #     else:
                        #         bpy.ops.ke.mod_order(obj_name=o.name, mod_type="WEIGHTED_NORMAL", top=False)

                    elif not smod and self.wtype == "CREASE":
                        bpy.ops.view3d.ke_subd(level_mode="TOGGLE")
                    bpy.ops.object.editmode_toggle()

                    # open modifier tab if not already open
                    p_area = None
                    m_active = False
                    for window in context.window_manager.windows:
                        for area in window.screen.areas:
                            if area.ui_type == 'PROPERTIES':
                                p_area = area
                                if area.spaces.active.context == 'MODIFIER':
                                    m_active = True
                                    area.tag_redraw()
                    if not m_active and p_area:
                        p_area.spaces.active.context = 'MODIFIER'
                        p_area.tag_redraw()

        refresh_ui()
        if face_mode:
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        return {"FINISHED"}
