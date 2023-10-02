import bpy
import bmesh
from bpy.props import BoolProperty
from bpy.types import Operator
from mathutils import Vector
from .._utils import get_selected, get_prefs


def history_verts(bm_history):
    pre_verts = []
    for sel in bm_history:
        if type(sel).__name__ == "BMFace" or type(sel).__name__ == "BMEdge":
            pre_verts.extend(sel.verts)
        else:
            pre_verts.append(sel)
    return pre_verts


class KeGetSetEditMesh(Operator):
    bl_idname = "view3d.ke_get_set_editmesh"
    bl_label = "Get & Set Object in Edit Mode"
    bl_description = "Switch to object under mouse pointer (and set Edit Mode) from either Object or Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}

    extend : BoolProperty(default=False, options={'HIDDEN'})
    mouse_pos = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    @classmethod
    def description(cls, context, properties):
        if properties.extend:
            return "Get & Set Object in Edit Mode Extend: This variant mode extends your selection"
        else:
            return "Switch to object under mouse pointer (and set Edit Mode) from either Object or Edit Mode"

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        elementpick = bool(k.getset_ep)
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL', 'ARMATURE'}

        if context.mode == "SCULPT":
            bpy.ops.object.transfer_mode('INVOKE_DEFAULT')
            return {"FINISHED"}

        if context.mode != "OBJECT":
            # sel by viewpicker since raycasting is more trouble...
            bpy.ops.object.mode_set(mode='OBJECT')

        og_obj = get_selected(context, use_cat=True, cat=cat)
        if og_obj:
            og_obj.select_set(False)

        bpy.ops.view3d.select(extend=self.extend, location=(int(self.mouse_pos[0]), int(self.mouse_pos[1])))
        hit_obj = context.object

        if og_obj and self.extend:
            og_obj.select_set(True)

        if hit_obj:
            context.view_layer.objects.active = hit_obj

            if hit_obj.type in cat:
                if hit_obj.type == 'GPENCIL':
                    bpy.ops.object.mode_set(mode='EDIT_GPENCIL')
                else:
                    bpy.ops.object.mode_set(mode='EDIT')

            if elementpick and hit_obj.type == "MESH":
                # Element Selection mode by viewpicker & restore, not very clean, but hey..
                self.extend = True
                element = ""
                og_selmode = context.tool_settings.mesh_select_mode[:]

                bm = bmesh.from_edit_mesh(context.object.data)

                if bm.select_history:
                    pre_verts = history_verts(bm.select_history)
                else:
                    pre_verts = []

                context.tool_settings.mesh_select_mode = (True, True, True)

                bpy.ops.view3d.select(extend=self.extend, location=(int(self.mouse_pos[0]), int(self.mouse_pos[1])))

                if bm.select_history:
                    last_verts = history_verts(bm.select_history)
                    element = type(bm.select_history[-1]).__name__

                    if pre_verts:
                        for v in last_verts:
                            if v not in pre_verts:
                                v.select_set(False)
                    else:
                        bm.select_history[-1].select_set(False)

                    bm.select_flush(False)

                if element == "BMVert":
                    context.tool_settings.mesh_select_mode = (True, False, False)
                elif element == "BMEdge":
                    context.tool_settings.mesh_select_mode = (False, True, False)
                elif element == "BMFace":
                    context.tool_settings.mesh_select_mode = (False, False, True)
                else:
                    context.tool_settings.mesh_select_mode = og_selmode

        self.extend = False

        return {'FINISHED'}
