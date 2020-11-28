import bpy
from mathutils import Vector
from bpy.types import Operator
from .ke_utils import mouse_raycast


class VIEW3D_OT_ke_get_set_editmesh(Operator):
    bl_idname = "view3d.ke_get_set_editmesh"
    bl_label = "Get & Set Object in Edit Mode"
    bl_description = "Selects object under mouse pointer (and switches to Edit Mode)"
    bl_options = {'REGISTER', 'UNDO'}

    mouse_pos = Vector((0, 0))

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        sel_mode = str(bpy.context.mode)
        if sel_mode == "EDIT_MESH":
            sel_mode = "EDIT"

        og_obj = bpy.context.active_object
        if og_obj:
            bpy.ops.object.mode_set(mode='OBJECT')

        best_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

        if best_obj is not None:

            best_original = best_obj.original

            if context.space_data.local_view and og_obj != best_original:
                visible = [obj for obj in context.visible_objects if obj.type == 'MESH']
                if best_original not in visible:
                    bpy.ops.object.mode_set(mode=sel_mode)
                    return {'CANCELLED'}

            if og_obj == best_original:
                context.view_layer.objects.active = og_obj
                bpy.ops.object.mode_set(mode='EDIT')
                return {'FINISHED'}

            best_original.select_set(True)
            if og_obj:
                og_obj.select_set(False)
            context.view_layer.objects.active = best_original
            bpy.ops.object.mode_set(mode='EDIT')

        else:
            bpy.ops.object.mode_set(mode=sel_mode)

        return {'FINISHED'}


class VIEW3D_OT_ke_get_set_material(Operator):
    bl_idname = "view3d.ke_get_set_material"
    bl_label = "Get & Set Material"
    bl_description = "Samples material under mouse pointer and applies it to the selection"
    bl_options = {'REGISTER'}

    offset: bpy.props.IntVectorProperty(name="Offset", default=(0, 0), size=2)

    mouse_pos = Vector((0, 0))

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x - self.offset[0]
        self.mouse_pos[1] = event.mouse_region_y - self.offset[1]
        return self.execute(context)

    def execute(self, context):

        og_obj = bpy.context.active_object
        sel_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        obj, hit_wloc, hit_normal, face_index = mouse_raycast(context, self.mouse_pos)

        if face_index is not None:
            target_index = obj.data.polygons[face_index].material_index

            slots = obj.material_slots[:]

            if slots:
                target_material = obj.material_slots[target_index].material
                og_mat = None
                for slot_index, slot in enumerate(og_obj.material_slots):
                    if slot.name:
                        if slot.material.name == target_material.name:
                            og_mat = slot_index

                bpy.ops.object.mode_set(mode='EDIT')

                if sel_mode == "OBJECT":
                    bpy.ops.mesh.select_all(action='SELECT')

                if og_mat is not None:
                    # print("Found & Assigned Existing Material Slot")
                    og_obj.active_material_index = og_mat
                    bpy.ops.object.material_slot_assign()

                else:
                    # print("creating new material slot and linking material")
                    bpy.ops.object.material_slot_add()
                    og_obj.active_material = bpy.data.materials[target_material.name]
                    bpy.ops.object.material_slot_assign()

            else:
                if sel_mode == "EDIT_MESH":
                    bpy.ops.object.mode_set(mode='EDIT')
                self.report({"INFO"}, "GetSetMaterial: No Material found")

            obj.update_from_editmode()
            return {'FINISHED'}

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
