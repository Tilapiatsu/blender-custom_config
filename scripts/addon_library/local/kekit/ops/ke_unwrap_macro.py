import bpy
from addon_utils import check
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import Operator
from .._utils import get_override_by_type, get_prefs


class KeUnwrapMacro(Operator):
    bl_idname = "view3d.ke_unwrap_macro"
    bl_label = "Unwrap Macro"
    bl_description = ("A simple macro script to do common (to me) UV-unwrapping tasks in 1 click\n"
                      "Requires TexTools Add-on. Please read the wiki documentation")
    bl_options = {'REGISTER', 'UNDO'}

    udim_pack: BoolProperty(default=False, name="Auto-Pack", description="Pack UV's")
    multiedit: BoolProperty(default=False, name="Use Same UDIM",
                            description="ON : All selected objects will be packed into 1 UDIM\n"
                                        "OFF: Each packed separately\n"
                                        "Note: Edit Mode is always ON (muti-edit mode)")
    margin: FloatProperty(default=0.03, min=0.0, max=1.0, name="Pack Margin")
    rotate: BoolProperty(name="Allow Rotation", default=False)
    auto_seam: BoolProperty(default=True, name="Auto-Seam",
                            description="Auto-apply UV-seams by angle. (Disabled by OMAS option toggle)")
    angle: FloatProperty(default=0.523599, min=0.0, max=3.1415, subtype="ANGLE", name="Seam Angle")
    align: BoolProperty(name="Canvas Align", default=True)
    alignment: EnumProperty(items=[
        ("topleft", "Top Left", "", 1),
        ("top", "Top", "", 2),
        ("topright", "Top Right", "", 3),
        ("left", "Left", "", 4),
        ("center", "Center", "", 5),
        ("right", "Right", "", 6),
        ("bottomleft", "Bottom Left", "", 7),
        ("bottom", "Bottom", "", 8),
        ("bottomright", "Bottom Right", "", 9),
        ("horizontal", "Horizontal", "", 10),
        ("vertical", "Vertical", "", 11),
    ], name="Alignment", default="bottomleft")
    texel: IntProperty(name="Texel Override", default=0, min=0, max=65536, subtype="PIXEL",
                       description="Change TexTools texel density (set to zero to use previous value)")
    opt_seam = False

    @classmethod
    def poll(cls, context):
        return context.object and context.space_data.type == "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column(align=True)
        if self.opt_seam:
            col.enabled = False
        col.prop(self, "auto_seam", toggle=True)
        row = col.row()
        if not self.auto_seam:
            row.enabled = False
        row.prop(self, "angle", toggle=True)
        col.separator(factor=1.5)

        col = layout.column(align=True)
        col.prop(self, "udim_pack", toggle=True)
        row = col.row()
        if not self.udim_pack:
            row.enabled = False
        row.prop(self, "rotate", toggle=True)
        row = col.row()
        if not self.udim_pack:
            row.enabled = False
        row.prop(self, "multiedit", toggle=True)
        row = col.row()
        if not self.udim_pack:
            row.enabled = False
        row.prop(self, "margin")
        col.separator(factor=1.5)

        row = col.row()
        if self.udim_pack:
            row.enabled = False
        row.prop(self, "align", toggle=True)
        row = col.row()
        if not self.align or self.udim_pack:
            row.enabled = False
        row.prop(self, "alignment")
        col.separator(factor=1.5)

        col.prop(self, "texel")
        layout.separator(factor=1)

    def unwrap_macro(self):
        # alignments will only work in face mode
        bpy.ops.uv.select_mode(type='FACE')
        bpy.ops.uv.select_all(action='SELECT')
        try:
            bpy.ops.uv.textools_island_align_world()
        except RuntimeError:
            pass
        bpy.ops.uv.textools_texel_density_set()

        if self.align:
            bpy.context.scene.texToolsSettings.align_mode = 'CANVAS'
            bpy.ops.uv.textools_align(direction=self.alignment)

    def autoseam(self):
        if self.auto_seam:
            bpy.ops.mesh.mark_seam(clear=True)
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.edges_select_sharp(sharpness=self.angle)
            bpy.ops.mesh.mark_seam(clear=False)

    def pack(self):
        if self.udim_pack:
            bpy.ops.uv.pack_islands(udim_source='ACTIVE_UDIM', rotate=self.rotate, scale=True, merge_overlap=False,
                                    margin=self.margin, shape_method='CONCAVE')

    def set_texeldensity(self):
        texels = bpy.context.scene.texToolsSettings.texel_density
        if self.texel != 0:
            texels = self.texel
            bpy.context.scene.texToolsSettings.texel_density = float(self.texel)
        if texels < 512:
            self.report({"INFO"}, "TexTools Texel Density is set to %i" % texels)

    def execute(self, context):
        # SELECTION
        self.opt_seam = False
        if get_prefs().uv_obj_seam:
            self.opt_seam = True
            self.auto_seam = False
            if context.mode == "OBJECT":
                self.auto_seam = True

        context.object.select_set(True)
        sel_obj = list(context.selected_objects)

        # TT REQ CHECK
        #  TexTools addon-name includes version nr(!) Not updated often(?), but could change,
        #  so, to avoid version hassle:
        ttcheck = False
        for i in context.preferences.addons:
            name = str(i.module)
            if "textools" in name.lower():
                if all(check(name)):
                    ttcheck = True
                    break

        if not ttcheck:
            self.report({"INFO"}, "Cancelled: TexTools Add-on not found")
            return {"CANCELLED"}

        # CTX Overrides
        og = "VIEW_3D"
        ovp = get_override_by_type(og)

        # Check Materials
        for obj in sel_obj:
            for m in obj.material_slots:
                if m.material is not None:
                    if not m.material.use_nodes:
                        self.report({"INFO"}, "Aborted: Non-nodes material found - TexTools needs nodes")
                        return {"CANCELLED"}

        # PROCESS
        if context.mode == "OBJECT":
            # All objects processed at the same time in multi-edit mode:
            bpy.ops.object.editmode_toggle()
            # VP Edit
            context.scene.tool_settings.use_uv_select_sync = False
            self.autoseam()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True, margin=0.03)
            # UV Edit (temporary)
            ovp[1].type = "IMAGE_EDITOR"
            context.area.ui_type = 'UV'
            self.set_texeldensity()
            self.unwrap_macro()

            if self.udim_pack and not self.multiedit:
                # Back to 3D View and more macro
                ovp[1].type = og
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action="DESELECT")

                for obj in sel_obj:
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                    bpy.ops.object.editmode_toggle()
                    # UV Edit
                    ovp[1].type = "IMAGE_EDITOR"
                    context.area.ui_type = 'UV'
                    self.pack()
                    ovp[1].type = og
                    # VP Edit
                    bpy.ops.object.editmode_toggle()
                    obj.select_set(False)

                for obj in sel_obj:
                    obj.select_set(True)
            else:
                self.pack()
                ovp[1].type = og
                # And back to object mode:
                bpy.ops.object.editmode_toggle()
        else:
            # VP Edit
            context.scene.tool_settings.use_uv_select_sync = False
            self.autoseam()
            bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True, margin=0.03)
            # UV Edit (temporary)
            ovp[1].type = "IMAGE_EDITOR"
            context.area.ui_type = 'UV'
            self.set_texeldensity()
            self.unwrap_macro()
            self.pack()
            ovp[1].type = og

        return {"FINISHED"}
