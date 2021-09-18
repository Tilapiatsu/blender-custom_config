import bpy
import bmesh
from mathutils import Vector
from bpy.types import Operator
from .ke_utils import mouse_raycast, get_selected


class VIEW3D_OT_ke_get_set_editmesh(Operator):
    bl_idname = "view3d.ke_get_set_editmesh"
    bl_label = "Get & Set Object in Edit Mode"
    bl_description = "Selects object under mouse pointer (and switches to Edit Mode)"
    bl_options = {'REGISTER', 'UNDO'}

    extend : bpy.props.BoolProperty(default=False, options={'HIDDEN'})
    mouse_pos = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def history_verts(self, bm_history):
        pre_verts = []
        for sel in bm_history:
            if type(sel).__name__ == "BMFace" or type(sel).__name__ == "BMEdge":
                pre_verts.extend(sel.verts)
            else:
                pre_verts.append(sel)
        return pre_verts

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        elementpick = bool(context.scene.kekit.getset_ep)
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL', 'ARMATURE'}

        # sel by viewpicker since raycasting is only good for "real mesh" ?
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode='OBJECT')

        og_obj = get_selected(context, use_cat=True, cat=cat)
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
                    pre_verts = self.history_verts(bm.select_history)
                else:
                    pre_verts = []

                context.tool_settings.mesh_select_mode = (True, True, True)

                bpy.ops.view3d.select(extend=self.extend, location=(int(self.mouse_pos[0]), int(self.mouse_pos[1])))

                if bm.select_history:
                    last_verts = self.history_verts(bm.select_history)
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


class VIEW3D_OT_ke_get_set_material(Operator):
    bl_idname = "view3d.ke_get_set_material"
    bl_label = "Get & Set Material"
    bl_description = "Samples material under mouse pointer and applies it to the selection"
    bl_options = {'REGISTER', 'UNDO'}

    offset: bpy.props.IntVectorProperty(name="Offset", default=(0, 0), size=2, options={'HIDDEN'})
    mouse_pos = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x - self.offset[0]
        self.mouse_pos[1] = event.mouse_region_y - self.offset[1]
        return self.execute(context)

    def execute(self, context):
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR'}
        target_index = None
        nonmesh_target = False

        sel_obj = bpy.context.selected_objects[:]
        sel_mode = bpy.context.mode[:]
        og_active_obj = context.active_object

        bpy.ops.object.mode_set(mode='OBJECT')

        # sel_type_non = []
        for o in sel_obj:
            if o.type not in cat:
                self.report({"INFO"}, "GetSetMaterial: Invalid Object Type Selected")
                return {"CANCELLED"}

        obj, hit_wloc, hit_normal, face_index = mouse_raycast(context, self.mouse_pos, evaluated=True)

        # Double-check with viewpicker since raycasting is only good for "real mesh" ?
        if face_index is None:
            bpy.ops.view3d.select(extend=False, location=(int(self.mouse_pos[0]), int(self.mouse_pos[1])))
            obj = context.object
            if obj.type in cat and obj.type != 'MESH':
                nonmesh_target = True
                target_index = 0

        if face_index is not None or nonmesh_target :
            if target_index is None:
                target_index = obj.data.polygons[face_index].material_index
            slots = obj.material_slots[:]

            if slots:
                target_material = obj.material_slots[target_index].material
                for o in sel_obj:
                    o.select_set(False)
                if nonmesh_target:
                    obj.select_set(False)

                for o in sel_obj:
                    o.select_set(True)
                    context.view_layer.objects.active = o
                    og_mat = None
                    for slot_index, slot in enumerate(o.material_slots):
                        if slot.name:
                            if slot.material.name == target_material.name:
                                og_mat = slot_index

                    if o.type == "MESH":
                        bpy.ops.object.mode_set(mode='EDIT')
                        if sel_mode == "OBJECT":
                            bpy.ops.mesh.select_all(action='SELECT')

                    if og_mat is not None:
                        # print("Found & Assigned Existing Material Slot")
                        o.active_material_index = og_mat
                        bpy.ops.object.material_slot_assign()

                    else:
                        # print("creating new material slot and linking material")
                        bpy.ops.object.material_slot_add()
                        o.active_material = bpy.data.materials[target_material.name]
                        bpy.ops.object.material_slot_assign()

                    if o.type != "MESH":
                        # non-mesh just use the top slot
                        for s in range(len(o.material_slots)):
                            bpy.ops.object.material_slot_move(direction='UP')

                    if sel_mode == "OBJECT":
                        bpy.ops.object.mode_set(mode='OBJECT')

                    o.select_set(False)

                for o in sel_obj:
                    o.select_set(True)

                if sel_mode == "OBJECT":
                    bpy.ops.object.material_slot_remove_unused()
                else:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.material_slot_remove_unused()
                    bpy.ops.object.mode_set(mode='EDIT')

            else:
                if sel_mode == "EDIT_MESH":
                    bpy.ops.object.mode_set(mode='EDIT')
                self.report({"INFO"}, "GetSetMaterial: No Material found")

            obj.update_from_editmode()

            if sel_mode == "OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT')

            return {'FINISHED'}

        else:
            # Restore sel
            if obj:
                obj.select_set(False)
            for o in sel_obj:
                o.select_set(True)
            if og_active_obj:
                context.view_layer.objects.active = og_active_obj
            self.report({"INFO"}, "GetSetMaterial: No Material found")
            return {'CANCELLED'}

        if sel_mode == "EDIT_MESH":
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    VIEW3D_OT_ke_get_set_editmesh,
    VIEW3D_OT_ke_get_set_material,
    )

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
