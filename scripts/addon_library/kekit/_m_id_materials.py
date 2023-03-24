import bpy
from bpy.types import Panel, Operator


#
# MODULE UI
#
class UIIDMaterialsModule(Panel):
    bl_idname = "UI_PT_M_IDMATERIALS"
    bl_label = "ID Materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Apply")
        row.label(text="Set Name")
        row.label(text="Set Color")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 1
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm01_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm01", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 2
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm02_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm02", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 3
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm03_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm03", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 4
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm04_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm04", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 5
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm05_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm05", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 6
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm06_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm06", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 7
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm07_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm07", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 8
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm08_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm08", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 9
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm09_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm09", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 10
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm10_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm10", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 11
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm11_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm11", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 12
        row.scale_x = 1
        row.prop(context.preferences.addons[__package__].preferences, "idm12_name", text="")
        row.scale_x = 0.5
        row.prop(context.preferences.addons[__package__].preferences, "idm12", text="")


def clamp_color(values, low=0.1, high=0.9):
    """Vector4 Color - clamps R,G & B but not Alpha"""
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


#
# MODULE OPERATORS (MISC)
#
class KeIDMaterial(Operator):
    bl_idname = "view3d.ke_id_material"
    bl_label = "ID Material"
    bl_description = "Applies ID Material to Object(s) / Faces"
    bl_options = {'REGISTER', 'UNDO'}

    m_id : bpy.props.IntProperty(name="m_id", default=4, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # Grab Settings
        k = context.preferences.addons[__package__].preferences
        object_color = k.object_color

        if self.m_id == 1:
            m_col = k.idm01
            m_name = k.idm01_name
        elif self.m_id == 2:
            m_col = k.idm02
            m_name = k.idm02_name
        elif self.m_id == 3:
            m_col = k.idm03
            m_name = k.idm03_name
        elif self.m_id == 4:
            m_col = k.idm04
            m_name = k.idm04_name
        elif self.m_id == 5:
            m_col = k.idm05
            m_name = k.idm05_name
        elif self.m_id == 6:
            m_col = k.idm06
            m_name = k.idm06_name
        elif self.m_id == 7:
            m_col = k.idm07
            m_name = k.idm07_name
        elif self.m_id == 8:
            m_col = k.idm08
            m_name = k.idm08_name
        elif self.m_id == 9:
            m_col = k.idm09
            m_name = k.idm09_name
        elif self.m_id == 10:
            m_col = k.idm10
            m_name = k.idm10_name
        elif self.m_id == 11:
            m_col = k.idm11
            m_name = k.idm11_name
        else:
            m_col = k.idm12
            m_name = k.idm12_name

        # Assign ID Mat
        sel_mode = str(context.mode)
        sel_obj = [o for o in context.selected_objects]

        for obj in sel_obj:

            context.view_layer.objects.active = obj

            if obj.type != "MESH":
                bpy.ops.object.material_slot_add()
                obj.active_material = bpy.data.materials[m_name]
                bpy.ops.object.material_slot_assign()

                # non-mesh just use the top slot
                for s in range(len(obj.material_slots)):
                    bpy.ops.object.material_slot_move(direction='UP')

                bpy.ops.object.material_slot_remove_unused()

            else:
                obj.update_from_editmode()

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

                if m_col[3] != 1:
                    context.object.active_material.blend_method = 'BLEND'
                    context.object.active_material.shadow_method = 'NONE'

                if object_color:
                    context.object.color = m_col

                obj.update_from_editmode()

        # NOTE: pie menu won't show until preview is generated, pie hides icon until then (open mat tab)
        # QND Hack "fix":
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.ui_type == 'PROPERTIES':
                    area.spaces.active.context = 'MATERIAL'
                    area.tag_redraw()

        bpy.ops.ed.undo_push()

        return {'FINISHED'}


#
# MODULE REGISTRATION
#
classes = (
    UIIDMaterialsModule,
    KeIDMaterial
)

modules = (
)


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_idmaterials:
        for c in classes:
            bpy.utils.register_class(c)
        
        for m in modules:
            m.register()


def unregister():
    if "bl_rna" in UIIDMaterialsModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
        
        for m in modules:
            m.unregister()


if __name__ == "__main__":
    register()
