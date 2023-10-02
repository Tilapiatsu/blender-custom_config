from bpy.types import Menu
from .._utils import get_prefs, is_registered


class KePieShading(Menu):
    bl_label = "keShading"
    bl_idname = "KE_MT_shading_pie"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def draw(self, context):
        k = get_prefs()
        xp = k.experimental
        layout = self.layout
        shading = None
        view = context.space_data
        if view.type == 'VIEW_3D':
            shading = view.shading
        if shading is None:
            print("Pie Menu not drawn: Incorrect Context Fallback")
            return {'CANCELLED'}

        pie = layout.menu_pie()

        # SLOT
        pie.prop(shading, "type", expand=True)

        # SLOT
        if shading.type == 'RENDERED':
            c = pie.row()
            b = c.column()
            col = b.box().column()
            col.scale_y = 0.9
            col.prop(shading, "use_scene_lights_render")
            col.prop(shading, "use_scene_world_render")
            if is_registered("VIEW3D_OT_ke_bg_sync"):
                col.operator("view3d.ke_bg_sync", icon="SHADING_TEXTURE")
            else:
                col.label(text="BG sync N/A")
            # col.separator(factor=1.2)

            row = col.row()
            row.prop(shading, "render_pass", text="")
            row.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
            c.separator(factor=2.5)
            b.separator(factor=3.5)
        else:
            pie.separator()

        # SLOT
        if shading.type == 'SOLID' and shading.light != 'FLAT':
            spacer = pie.row()
            spacer.label(text="")

            col = spacer.box().column()
            sub = col.row()

            if shading.light == 'STUDIO':
                prefs = context.preferences
                system = prefs.system

                if not system.use_studio_light_edit:
                    sub.scale_y = 0.6
                    sub.scale_x = .738
                    sub.template_icon_view(shading, "studio_light", scale_popup=3.0)
                else:
                    sub.prop(
                        system,
                        "use_studio_light_edit",
                        text="Disable Studio Light Edit",
                        icon='NONE',
                        toggle=True,
                    )
                sub2 = sub.column()
                sub2.scale_x = 1.3
                sub2.scale_y = 1.8
                p = sub2.column(align=False)
                p.prop(shading, "use_world_space_lighting", text="World Space Lighting", icon='WORLD', toggle=True)
                p.operator("preferences.studiolight_show", text="Preferences", emboss=False, icon='PREFERENCES')
                p.separator(factor=0.3)
                if xp:
                    p.prop(shading, "studiolight_rotate_z", text="RotateZ")
                else:
                    p.label(text="Rot Disabled")

            elif shading.light == 'MATCAP':
                sub.scale_y = 0.6
                sub.scale_x = .7
                sub.template_icon_view(shading, "studio_light", scale_popup=3.0)

                sub = sub.column()
                sub.scale_y = 1.8
                sub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
                sub.operator("view3d.toggle_matcap_flip", emboss=False, text="", icon='ARROW_LEFTRIGHT')

        elif shading.type == 'RENDERED' and not shading.use_scene_world_render:
            b = pie.row()
            c = b.column()

            col = b.box().column()
            col.scale_y = 0.65
            col.scale_x = 0.7
            sub = col.row()
            sub.template_icon_view(shading, "studio_light", scale_popup=3)

            sub2 = sub.column()
            sub2.scale_y = 1.4
            sub2.scale_x = 1.1
            if xp:
                sub2.prop(shading, "studiolight_rotate_z", text="RotateZ")
            else:
                sub2.label(text="Rot Disabled")
            sub2.prop(shading, "studiolight_intensity", text="Intensity")
            sub2.prop(shading, "studiolight_background_alpha", text="Alpha")
            sub2.prop(shading, "studiolight_background_blur", text="Blur")
            b.separator(factor=13.5)
            c.separator(factor=2.5)

        else:
            pie.separator()

        # SLOT
        if shading.type == 'MATERIAL':
            r = pie.row()
            c = r.column()
            c.separator(factor=16)
            col = c.box().column()
            col.scale_y = 0.9
            col.prop(shading, "use_scene_lights")
            col.prop(shading, "use_scene_world")
            col.operator("view3d.ke_bg_sync", icon="SHADING_TEXTURE")
            # col.separator(factor=1.2)
            row = col.row()
            row.prop(shading, "render_pass", text="")
            row.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
            r.separator(factor=2.4)

        else:
            pie.separator()

        # SLOT
        r = pie.row()
        r.separator(factor=2.4)
        c = r.column()

        if shading.type == 'SOLID':
            c.separator(factor=3)
            col = c.box().column()
            col.ui_units_x = 12
            lights = col.row()
            lights.prop(shading, "light", expand=True)
            col.separator(factor=0.5)
            col.grid_flow(columns=3, align=True).prop(shading, "color_type", expand=True)

            obj = context.object
            if shading.color_type == 'SINGLE':
                col.column().prop(shading, "single_color", text="")

            elif obj and shading.color_type == "OBJECT":
                obj_type = obj.type
                is_geometry = (obj_type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME', 'HAIR',
                                            'POINTCLOUD'})
                is_empty_image = (obj_type == 'EMPTY' and obj.empty_display_type == 'IMAGE')
                is_dupli = (obj.instance_type != 'NONE')
                is_gpencil = (obj_type == 'GPENCIL')
                if is_geometry or is_dupli or is_empty_image or is_gpencil:
                    col.column().prop(obj, "color", text="")

            col.separator(factor=0.5)
            opt = col.row(align=True)
            opt.alignment = "CENTER"
            opt.prop(shading, "show_shadows", text="Shadows", toggle=True)
            opt.prop(shading, "show_cavity", text="Cavity", toggle=True)
            opt.prop(shading, "show_specular_highlight", text="Specular", toggle=True)

        elif shading.type == 'MATERIAL':
            if not shading.use_scene_world:
                c.separator(factor=16)
                col = c.box().column()
                sub = col.row()
                sub.scale_y = 0.65
                sub.scale_x = 0.7
                sub.template_icon_view(shading, "studio_light", scale_popup=3)

                sub2 = sub.column()
                sub2.scale_y = 1.4
                sub2.scale_x = 1.1
                if xp:
                    sub2.prop(shading, "studiolight_rotate_z", text="RotateZ")
                else:
                    sub2.label(text="Rot Disabled")
                sub2.prop(shading, "studiolight_intensity", text="Intensity")
                sub2.prop(shading, "studiolight_background_alpha", text="Alpha")
                sub2.prop(shading, "studiolight_background_blur", text="Blur")
