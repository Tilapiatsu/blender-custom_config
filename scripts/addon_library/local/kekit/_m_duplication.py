import bpy
from bpy.types import Panel
from . import ke_copyplus, ke_mouse_mirror_flip, ke_lineararray, ke_radialarray, ke_radial_instances, ke_exex, \
    ke_extract_and_edit


#
# MODULE UI
#
class UIDupeModule(Panel):
    bl_idname = "UI_PT_M_DUPE"
    bl_label = "Duplication"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_category = __package__
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        col = layout.column(align=True)
        hrow = col.row(align=True)
        hrow.scale_y = 0.5
        hrow.enabled = False
        hrow.label(text="Duplication")
        col.separator(factor=0.5)
        row = col.row(align=True)
        split = row.split(factor=0.78, align=True)
        subrow1 = split.row(align=True)
        subrow1.operator('view3d.ke_copyplus', text="Cut+").mode = "CUT"
        subrow1.operator('view3d.ke_copyplus', text="Copy+").mode = "COPY"
        subrow1.operator('view3d.ke_copyplus', text="Paste+").mode = "PASTE"
        subrow2 = split.row(align=True)
        subrow2.prop(k, "plus_merge", toggle=True)
        subrow2.prop(k, "plus_mpoint", toggle=True)

        row = col.row(align=True)
        split = row.split(factor=0.65, align=True)
        split.operator('mesh.ke_extract_and_edit', text="Extract & Edit")
        split.operator('mesh.ke_exex', text="ExEx")

        row = col.row(align=True)
        split = row.split(factor=0.65, align=True)
        split.operator('view3d.ke_mouse_mirror_flip', icon="MOUSE_MOVE", text="Mouse Mirror").mode = "MIRROR"
        split.operator('view3d.ke_mouse_mirror_flip', icon="MOUSE_MOVE", text="Flip").mode = "FLIP"

        row = col.row(align=True)
        split = row.split(factor=0.75, align=True)
        split.operator("view3d.ke_lineararray", text="Linear Instances").convert = True
        split.operator("view3d.ke_lineararray", text="LA").convert = False
        row = col.row(align=True)
        split = row.split(factor=0.75, align=True)
        split.operator("view3d.ke_radial_instances")
        split.operator("view3d.ke_radialarray", text="RA")


#
# MODULE REGISTRATION
#
classes = (
    UIDupeModule,
)

modules = (
    ke_copyplus,
    ke_mouse_mirror_flip,
    ke_lineararray,
    ke_radialarray,
    ke_radial_instances,
    ke_exex,
    ke_extract_and_edit,
)


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_dupe:
        for c in classes:
            bpy.utils.register_class(c)

        for m in modules:
            m.register()


def unregister():
    if "bl_rna" in UIDupeModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)

        for m in modules:
            m.unregister()


if __name__ == "__main__":
    register()
