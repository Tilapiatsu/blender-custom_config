bl_info = {
    "name": "keIDMaterial",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
}

import bpy
import addon_utils
from bpy.types import Operator
from bpy.props import IntProperty
from bpy.utils import register_class, unregister_class


def clamp_color(values, low=0.1, high=0.9):
    '''Vector4 Color - clamps R,G & B but not Alpha'''
    clamped = [low if v < low else high if v > high else v for v in values[:3]]
    clamped.append(values[3])
    return clamped


def get_material_index(obj, matname):
    mid = None
    for slot_index, slot in enumerate(obj.material_slots):
        if slot.name:
            if slot.material.name == matname:
                mid = slot_index
    return mid


class VIEW3D_OT_ke_id_material(Operator):
    bl_idname = "view3d.ke_id_material"
    bl_label = "ID Material"
    bl_description = "Applies ID Material to Object(s) / Faces"
    bl_options = {'REGISTER', 'UNDO'}

    m_id : IntProperty(default=4)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context: 'Context'):
        layout = self.layout

    def execute(self, context):
        # Grab Settings
        object_color = context.scene.kekit.object_color
        # matvp_color= context.scene.kekit.matvp_color
        # vpmuted = context.scene.kekit.vpmuted

        if self.m_id == 1:
            m_col = context.scene.kekit.idm01
            m_name = context.scene.kekit.idm01_name
        elif self.m_id == 2:
            m_col = context.scene.kekit.idm02
            m_name = context.scene.kekit.idm02_name
        elif self.m_id == 3:
            m_col = context.scene.kekit.idm03
            m_name = context.scene.kekit.idm03_name
        elif self.m_id == 4:
            m_col = context.scene.kekit.idm04
            m_name = context.scene.kekit.idm04_name
        elif self.m_id == 5:
            m_col = context.scene.kekit.idm05
            m_name = context.scene.kekit.idm05_name
        elif self.m_id == 6:
            m_col = context.scene.kekit.idm06
            m_name = context.scene.kekit.idm06_name
        elif self.m_id == 7:
            m_col = context.scene.kekit.idm07
            m_name = context.scene.kekit.idm07_name
        elif self.m_id == 8:
            m_col = context.scene.kekit.idm08
            m_name = context.scene.kekit.idm08_name
        elif self.m_id == 9:
            m_col = context.scene.kekit.idm09
            m_name = context.scene.kekit.idm09_name
        elif self.m_id == 10:
            m_col = context.scene.kekit.idm10
            m_name = context.scene.kekit.idm10_name
        elif self.m_id == 11:
            m_col = context.scene.kekit.idm11
            m_name = context.scene.kekit.idm11_name
        elif self.m_id == 12:
            m_col = context.scene.kekit.idm12
            m_name = context.scene.kekit.idm12_name

        # Assign ID Mat
        sel_mode = str(context.mode)
        sel_obj = [o for o in context.selected_objects]

        for obj in sel_obj:

            obj.update_from_editmode()
            context.view_layer.objects.active = obj

            if sel_mode == "EDIT_MESH":
                sel_poly = [p for p in obj.data.polygons if p.select]
                if not sel_poly:
                    break
            elif sel_mode == "OBJECT":
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

            # slotcount = len(obj.material_slots[:])
            existing_idm = bpy.data.materials.get(m_name)

            if existing_idm:
                using_slot = get_material_index(obj, m_name)
            else:
                using_slot = None

            if using_slot is not None:
                # print("EXISTING MATERIAL FOUND - SLOT RE-USED")
                obj.active_material_index = using_slot

            elif existing_idm and using_slot is None:
                # print("EXISTING MATERIAL FOUND - SLOT ADDED")
                obj.data.materials.append(existing_idm)
                obj.active_material_index = get_material_index(obj, m_name)

            else:
                # print("NEW MATERIAL ADDED")
                new = bpy.data.materials.new(name=m_name)
                obj.data.materials.append(new)
                obj.active_material_index = get_material_index(obj, m_name)

            bpy.ops.object.material_slot_assign()

            # Clean up materials & slots
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.material_slot_remove_unused()
            if sel_mode == 'EDIT_MESH':
                bpy.ops.object.mode_set(mode='EDIT')

            # # Set Colors
            context.object.active_material.diffuse_color = m_col

            if object_color:
                context.object.color = m_col

            obj.update_from_editmode()

        bpy.ops.ed.undo_push()

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (VIEW3D_OT_ke_id_material,
           )

def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)


if __name__ == "__main__":
    register()
