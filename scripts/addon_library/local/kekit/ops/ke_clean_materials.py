from bpy.types import Operator


class KeCleanUnusedMaterials(Operator):
    bl_idname = "object.ke_clean_unused_materials"
    bl_label = "Clean Unused Materials & Slots"
    bl_description = "Like the vanilla 'Renove Unused Materials' + removes unused slots from selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode == "OBJECT"

    def execute(self, context):
        context.object.select_set(True)

        for obj in context.selected_objects:
            to_remove = set()
            # Unused slot (no material):
            for slot in obj.material_slots:
                if slot.material is None:
                    to_remove.add(slot.name)
            # Unused material slots:
            for slot in obj.material_slots:
                if not any(p.material_index == slot.slot_index for p in obj.data.polygons):
                    to_remove.add(slot.name)
            # Remove
            for s in to_remove:
                obj.data.materials.pop(index=obj.material_slots[s].slot_index)

        return {"FINISHED"}
