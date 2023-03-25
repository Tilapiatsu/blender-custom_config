import bpy
import bmesh
from mathutils import Vector
from bpy.types import Operator
from ._utils import mouse_raycast, get_selected


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

    extend : bpy.props.BoolProperty(default=False, options={'HIDDEN'})
    mouse_pos = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        elementpick = bool(context.preferences.addons[__package__].preferences.getset_ep)
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


class KeGetSetMaterial(Operator):
    bl_idname = "view3d.ke_get_set_material"
    bl_label = "Get & Set Material"
    bl_description = "Samples material under mouse pointer and applies it to the selection"
    bl_options = {'REGISTER', 'UNDO'}

    offset: bpy.props.IntVectorProperty(name="Offset", default=(0, 0), size=2, options={'HIDDEN'})
    mouse_pos = Vector((0, 0))
    nonmesh_target = False
    target_index = None
    cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D" and context.selected_objects

    def raycast(self, context):
        obj, hit_wloc, hit_normal, face_index = mouse_raycast(context, self.mouse_pos, evaluated=True)
        # Double-check with viewpicker since raycasting is only good for "real mesh" ?
        if face_index is None:
            bpy.ops.view3d.select(extend=False, location=(int(self.mouse_pos[0]), int(self.mouse_pos[1])))
            obj = context.object
            if obj.type in self.cat and obj.type != 'MESH':
                self.nonmesh_target = True
                self.target_index = 0
        return obj, hit_wloc, hit_normal, face_index

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x - self.offset[0]
        self.mouse_pos[1] = event.mouse_region_y - self.offset[1]
        return self.execute(context)

    def execute(self, context):
        hidden = []
        sel_obj = context.selected_objects[:]
        sel_mode = context.mode[:]
        og_active_obj = context.active_object

        bpy.ops.object.mode_set(mode='OBJECT')

        for o in sel_obj:
            if o.type not in self.cat:
                self.report({"INFO"}, "GetSetMaterial: Invalid Object Type Selected")
                return {"CANCELLED"}

        obj, hit_wloc, hit_normal, face_index = self.raycast(context)

        if obj.display_type in {'WIRE', 'BOUNDS'}:
            # Hiding *all* of them just in case there's stacked layers of 'em.
            # Only doing this if we hit a wire mesh (just-in-case perf issue)
            for o in context.scene.objects:
                if o.display_type in {'WIRE', 'BOUNDS'} and not o.hide_viewport:
                    o.hide_viewport = True
                    hidden.append(o)
            # ...and AGAIN:
            obj, hit_wloc, hit_normal, face_index = self.raycast(context)

        if face_index is not None or self.nonmesh_target :
            if self.target_index is None:
                self.target_index = obj.data.polygons[face_index].material_index
            slots = obj.material_slots[:]

            if slots:
                target_material = obj.material_slots[self.target_index].material
                for o in sel_obj:
                    o.select_set(False)
                if self.nonmesh_target:
                    obj.select_set(False)

                for o in sel_obj:
                    o.select_set(True)
                    context.view_layer.objects.active = o
                    og_mat = None
                    screw_type = None
                    for slot_index, slot in enumerate(o.material_slots):
                        if slot.name:
                            if slot.material.name == target_material.name:
                                og_mat = slot_index

                    if o.type == "MESH":
                        if sel_mode == "OBJECT":
                            screw_type = [m for m in o.modifiers if m.type == "SCREW"]
                            if not screw_type:
                                bpy.ops.object.mode_set(mode='EDIT')
                                bpy.ops.mesh.select_all(action='SELECT')
                        else:
                            bpy.ops.object.mode_set(mode='EDIT')

                    if og_mat is not None:
                        # print("Found & Assigned Existing Material Slot")
                        o.active_material_index = og_mat
                        bpy.ops.object.material_slot_assign()
                    else:
                        # print("creating new material slot and linking material")
                        bpy.ops.object.material_slot_add()
                        o.active_material = bpy.data.materials[target_material.name]
                        bpy.ops.object.material_slot_assign()

                    # Cleanup
                    # 'Remove_unused' does not work on 'screw-mesh' (it's checking non-existant geo?)
                    if o.type != "MESH" or screw_type:
                        # print("'Non-mesh' just use the top slot")
                        for s in range(len(o.material_slots)):
                            bpy.ops.object.material_slot_move(direction='UP')
                    else:
                        if sel_mode == "OBJECT":
                            bpy.ops.object.mode_set(mode='OBJECT')
                            bpy.ops.object.material_slot_remove_unused()
                        else:
                            bpy.ops.object.mode_set(mode='OBJECT')
                            bpy.ops.object.material_slot_remove_unused()
                            bpy.ops.object.mode_set(mode='EDIT')

                    o.select_set(False)

                for o in sel_obj:
                    o.select_set(True)

            else:
                if sel_mode == "EDIT_MESH":
                    bpy.ops.object.mode_set(mode='EDIT')
                self.report({"INFO"}, "GetSetMaterial: No Material found")

            obj.update_from_editmode()

            if sel_mode == "OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT')

            if hidden:
                for o in hidden:
                    o.hide_viewport = False
            return {'FINISHED'}

        else:
            # Restore sel
            if hidden:
                for o in hidden:
                    o.hide_viewport = False
            if obj:
                obj.select_set(False)
            for o in sel_obj:
                o.select_set(True)
            if og_active_obj:
                context.view_layer.objects.active = og_active_obj
            self.report({"INFO"}, "GetSetMaterial: No Material found")
            return {'CANCELLED'}


#
# Class Registration & Unregistration
#
classes = (
    KeGetSetEditMesh,
    KeGetSetMaterial,
    )

modules = ()


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
