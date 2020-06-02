import bpy
from bpy.types import Menu, Operator, Panel

# -------------------------------------------------------------------------------------------------
# Operators
# -------------------------------------------------------------------------------------------------
class VIEW3D_OT_ke_pieops(Operator):
    bl_idname = "ke.pieops"
    bl_label = "Pie Operators"
    bl_options = {'REGISTER'}

    pop: bpy.props.IntProperty(default=0)

    def execute(self, context):

        # 0 - ABSOLUTE GRID TOGGLE
        if self.pop == 0:
            context.tool_settings.use_snap_grid_absolute = not context.tool_settings.use_snap_grid_absolute

        return {'FINISHED'}




class VIEW3D_OT_ke_snap_target(Operator):
    bl_idname = "ke.snap_target"
    bl_label = "Snap Target"
    bl_options = {'REGISTER', 'UNDO'}

    ke_snaptarget: bpy.props.EnumProperty(
        items=[("CLOSEST", "Closest", "Closest", "", 1),
               ("CENTER", "Center", "Center", "", 2),
               ("MEDIAN", "Median", "Median", "", 3),
               ("ACTIVE", "Active", "Active", "", 4),
               ("PROJECT", "Project Self", "Project Self", "", 5),
               ("ALIGN", "Align Rotation", "Align Rotation", "", 6)],
        name="Snap Target",
        default="CLOSEST")

    def execute(self, context):
        ct = bpy.context.scene.tool_settings
        if self.ke_snaptarget == 'PROJECT':
            ct.use_snap_self = not ct.use_snap_self
        elif self.ke_snaptarget == 'ALIGN':
            ct.use_snap_align_rotation = not ct.use_snap_align_rotation
        else:
            ct.snap_target = self.ke_snaptarget
        return {'FINISHED'}


class VIEW3D_OT_ke_snap_element(Operator):
    bl_idname = "ke.snap_element"
    bl_label = "Snap Element"
    bl_options = {'REGISTER', 'UNDO'}

    ke_snapelement: bpy.props.EnumProperty(
        items=[("INCREMENT", "Increment", "", "SNAP_INCREMENT", 1),
               ("VERTEX", "Vertex", "", "SNAP_VERTEX", 2),
               ("EDGE", "Edge", "", "SNAP_EDGE", 3),
               ("FACE", "Face", "", "SNAP_FACE", 4),
               ("VOLUME", "Volume", "", "SNAP_VOLUME", 5),
               ("MIX", "Element Mix", "", "SNAP_MIX", 6)],
        name="Snap Element",
        default="INCREMENT")


    def execute(self, context):
        ct = bpy.context.scene.tool_settings
        ct.use_snap = True

        if self.ke_snapelement == "MIX":
            ct.snap_elements = {'VERTEX', 'EDGE', 'EDGE_MIDPOINT', 'FACE'}

        elif self.ke_snapelement == "EDGE":
            ct.snap_elements = {'EDGE', 'EDGE_MIDPOINT'}

        elif self.ke_snapelement == "INCREMENT":
            ct.snap_elements = {'INCREMENT'}
            ctx_mode = bpy.context.mode
            if ctx_mode == "OBJECT":
                ct.use_snap_grid_absolute = True
            else:
                ct.use_snap_grid_absolute = False
        else:
            ct.snap_elements = {self.ke_snapelement}

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Custom Pie Menus    Note: COMPASS STYLE REF PIE SLOT POSITIONS:   W, E, S, N, NW, NE, SW, SE
# -------------------------------------------------------------------------------------------------

class VIEW3D_MT_PIE_ke_snapping(Menu):
    bl_label = "keSnapping"
    bl_idname = "VIEW3D_MT_ke_pie_snapping"

    def draw(self, context):
        ct = bpy.context.scene.tool_settings
        layout = self.layout

        pie = layout.menu_pie()
        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3

        if not ct.use_snap_grid_absolute:
            cbox.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=False).pop = 0
        else:
            cbox.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=True).pop = 0

        cbox.separator()

        if not ct.use_snap_self:
            cbox.operator("ke.snap_target", text="Project Self", icon="PROP_PROJECTED",depress=False).ke_snaptarget = "PROJECT"
        else:
            cbox.operator("ke.snap_target", text="Project Self", icon="PROP_PROJECTED",depress=True).ke_snaptarget = "PROJECT"

        if not ct.use_snap_align_rotation:
            cbox.operator("ke.snap_target", text="Align Rotation", icon="ORIENTATION_NORMAL", depress=False).ke_snaptarget = "ALIGN"
        else:
            cbox.operator("ke.snap_target", text="Align Rotation", icon="ORIENTATION_NORMAL", depress=True).ke_snaptarget = "ALIGN"

        cbox.separator()

        if not ct.snap_target == "MEDIAN":
            cbox.operator("ke.snap_target", text="Median", icon="PIVOT_MEDIAN", depress=False).ke_snaptarget = "MEDIAN"
        else:
            cbox.operator("ke.snap_target", text="Median", icon="PIVOT_MEDIAN", depress=True).ke_snaptarget = "MEDIAN"

        if not ct.snap_target == "ACTIVE":
            cbox.operator("ke.snap_target", text="Active", icon="PIVOT_ACTIVE", depress=False).ke_snaptarget = "ACTIVE"
        else:
            cbox.operator("ke.snap_target", text="Active", icon="PIVOT_ACTIVE", depress=True).ke_snaptarget = "ACTIVE"

        if not ct.snap_target == "CLOSEST":
            cbox.operator("ke.snap_target", text="Closest", icon="NORMALS_VERTEX_FACE", depress=False).ke_snaptarget = "CLOSEST"
        else:
            cbox.operator("ke.snap_target", text="Closest", icon="NORMALS_VERTEX_FACE", depress=True).ke_snaptarget = "CLOSEST"

        pie = layout.menu_pie()
        pie.operator("ke.snap_element", text="Vertex", icon="SNAP_VERTEX").ke_snapelement = "VERTEX"
        pie.operator("ke.snap_element", text="Element Mix", icon="SNAP_ON").ke_snapelement = "MIX"
        pie.operator("ke.snap_element", text="Increment/Grid", icon="SNAP_GRID").ke_snapelement = "INCREMENT"
        pie.separator()
        pie.operator("ke.snap_element", text="Edge", icon="SNAP_EDGE").ke_snapelement = "EDGE"
        pie.separator()
        pie.operator("ke.snap_element", text="Face", icon="SNAP_FACE").ke_snapelement = "FACE"



class VIEW3D_MT_PIE_ke_fit2grid(Menu):
    bl_label = "keFit2Grid"
    bl_idname = "VIEW3D_MT_ke_pie_fit2grid"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fit2grid", text="50cm").set_grid = 0.5
        pie.operator("view3d.ke_fit2grid", text="5cm").set_grid = 0.05
        pie.operator("view3d.ke_fit2grid", text="15cm").set_grid = 0.15
        pie.operator("view3d.ke_fit2grid", text="1cm").set_grid = 0.01
        pie.operator("view3d.ke_fit2grid", text="1m").set_grid = 1.0
        pie.operator("view3d.ke_fit2grid", text="2.5cm").set_grid = 0.025
        pie.operator("view3d.ke_fit2grid", text="25cm").set_grid = 0.25
        pie.operator("view3d.ke_fit2grid", text="10cm").set_grid = 0.1


class VIEW3D_MT_PIE_ke_fit2grid_micro(Menu):
    bl_label = "keFit2Grid_micro"
    bl_idname = "VIEW3D_MT_ke_pie_fit2grid_micro"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fit2grid", text="5mm").set_grid = 0.005
        pie.operator("view3d.ke_fit2grid", text="5µm").set_grid = 0.0005
        pie.operator("view3d.ke_fit2grid", text="1.5mm").set_grid = 0.0015
        pie.operator("view3d.ke_fit2grid", text="1µm").set_grid = 0.0001
        pie.operator("view3d.ke_fit2grid", text="1cm").set_grid = 0.01
        pie.operator("view3d.ke_fit2grid", text="2.5µm").set_grid = 0.00025
        pie.operator("view3d.ke_fit2grid", text="5µm").set_grid = 0.0005
        pie.operator("view3d.ke_fit2grid", text="1mm").set_grid = 0.001


class VIEW3D_MT_PIE_ke_overlays(Menu):
    bl_label = "keOverlays"
    bl_idname = "VIEW3D_MT_ke_pie_overlays"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3

        if bpy.context.space_data.shading.show_backface_culling:
            cbox.operator("view3d.ke_overlays", text="Backface Culling", icon="XRAY", depress=True).overlay = "BACKFACE"
        else:
            cbox.operator("view3d.ke_overlays", text="Backface Culling", icon="XRAY", depress=False).overlay = "BACKFACE"



        if bpy.context.space_data.overlay.show_extra_indices:
            cbox.operator("view3d.ke_overlays", text="Indices", icon="LINENUMBERS_ON", depress=True).overlay = "INDICES"
        else:
            cbox.operator("view3d.ke_overlays", text="Indices", icon="LINENUMBERS_ON", depress=False).overlay = "INDICES"

        if bpy.context.space_data.overlay.show_extras:
            cbox.operator("view3d.ke_overlays", text="Extras", icon="LIGHT_SUN", depress=True).overlay = "EXTRAS"
        else:
            cbox.operator("view3d.ke_overlays", text="Extras", icon="LIGHT_SUN", depress=False).overlay = "EXTRAS"

        if bpy.context.space_data.overlay.show_cursor:
            cbox.operator("view3d.ke_overlays", text="Cursor", icon="CURSOR", depress=True).overlay = "CURSOR"
        else:
            cbox.operator("view3d.ke_overlays", text="Cursor", icon="CURSOR", depress=False).overlay = "CURSOR"

        if bpy.context.space_data.overlay.show_object_origins:
            cbox.operator("view3d.ke_overlays", text="Origins", icon="OBJECT_ORIGIN", depress=True).overlay = "ORIGINS"
        else:
            cbox.operator("view3d.ke_overlays", text="Origins", icon="OBJECT_ORIGIN", depress=False).overlay = "ORIGINS"

        if bpy.context.space_data.overlay.show_outline_selected:
            cbox.operator("view3d.ke_overlays", text="Outline", icon="MESH_CIRCLE", depress=True).overlay = "OUTLINE"
        else:
            cbox.operator("view3d.ke_overlays", text="Outline", icon="MESH_CIRCLE", depress=False).overlay = "OUTLINE"

        cbox.separator()
        try:
            if bpy.context.scene.ke_focus[0] or not bpy.context.scene.ke_focus[0]:  #silly existance check

                if not bpy.context.scene.ke_focus[0] and not bpy.context.scene.ke_focus[10]:
                    cbox.operator("view3d.ke_focusmode", text="Focus Mode", icon="FULLSCREEN_ENTER",
                                  depress=False).supermode = False
                    cbox.operator("view3d.ke_focusmode", text="Super Focus Mode", icon="FULLSCREEN_ENTER",
                                  depress=False).supermode = True

                elif bpy.context.scene.ke_focus[0] and not bpy.context.scene.ke_focus[10]:
                    cbox.operator("view3d.ke_focusmode", text="Focus Mode (Off)", icon="FULLSCREEN_EXIT",
                                  depress=True).supermode = False

                elif bpy.context.scene.ke_focus[10]:
                    cbox.operator("view3d.ke_focusmode", text="Super Focus Mode (Off)", icon="FULLSCREEN_EXIT",
                                  depress=True).supermode = True

        except:
            cbox.operator("view3d.ke_focusmode", text="Focus Mode", icon="FULLSCREEN_ENTER",
                          depress=False).supermode = False
            cbox.operator("view3d.ke_focusmode", text="Super Focus", icon="FULLSCREEN_ENTER",
                          depress=False).supermode = True

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3
        if bpy.context.space_data.overlay.show_edge_seams:
            cbox.operator("view3d.ke_overlays", text="Edge Seams", icon="UV_ISLANDSEL", depress=True).overlay = "SEAMS"
        else:
            cbox.operator("view3d.ke_overlays", text="Edge Seams", icon="UV_ISLANDSEL", depress=False).overlay = "SEAMS"

        if bpy.context.space_data.overlay.show_edge_sharp:
            cbox.operator("view3d.ke_overlays", text="Edge Sharp", icon="MESH_CUBE", depress=True).overlay = "SHARP"
        else:
            cbox.operator("view3d.ke_overlays", text="Edge Sharp", icon="MESH_CUBE", depress=False).overlay = "SHARP"

        if bpy.context.space_data.overlay.show_edge_crease:
            cbox.operator("view3d.ke_overlays", text="Edge Crease", icon="META_CUBE", depress=True).overlay = "CREASE"
        else:
            cbox.operator("view3d.ke_overlays", text="Edge Crease", icon="META_CUBE", depress=False).overlay = "CREASE"

        if bpy.context.space_data.overlay.show_edge_bevel_weight:
            cbox.operator("view3d.ke_overlays", text="Edge Bevel Weight", icon="MOD_BEVEL", depress=True).overlay = "BEVEL"
        else:
            cbox.operator("view3d.ke_overlays", text="Edge Bevel Weight", icon="MOD_BEVEL", depress=False).overlay = "BEVEL"

        cbox.separator()
        if bpy.context.space_data.overlay.show_vertex_normals:
            cbox.operator("view3d.ke_overlays", text="Vertex Normals", icon="NORMALS_VERTEX", depress=True).overlay = "VN"
        else:
            cbox.operator("view3d.ke_overlays", text="Vertex Normals", icon="NORMALS_VERTEX", depress=False).overlay = "VN"

        if bpy.context.space_data.overlay.show_split_normals:
            cbox.operator("view3d.ke_overlays", text="Split Normals", icon="NORMALS_VERTEX_FACE", depress=True).overlay = "SN"
        else:
            cbox.operator("view3d.ke_overlays", text="Split Normals", icon="NORMALS_VERTEX_FACE", depress=False).overlay = "SN"

        if bpy.context.space_data.overlay.show_face_normals:
            cbox.operator("view3d.ke_overlays", text="Face Normals", icon="NORMALS_FACE", depress=True).overlay = "FN"
        else:
            cbox.operator("view3d.ke_overlays", text="Face Normals", icon="NORMALS_FACE", depress=False).overlay = "FN"

        cbox.separator()
        if bpy.context.space_data.overlay.show_face_orientation:
            cbox.operator("view3d.ke_overlays", text="Face Orientation", icon="FACESEL", depress=True).overlay = "FACEORIENT"
        else:
            cbox.operator("view3d.ke_overlays", text="Face Orientation", icon="FACESEL", depress=False).overlay = "FACEORIENT"

        pie = layout.menu_pie()
        pie.operator("view3d.ke_overlays", text="All Overlays", icon="OVERLAY").overlay = "ALL"
        pie.operator("view3d.ke_overlays", text="All Edge Overlays", icon="UV_EDGESEL").overlay = "ALLEDIT"
        # pie.separator()


class VIEW3D_MT_PIE_ke_orientpivot(Menu):
    bl_label = "keOrientPivot"
    bl_idname = "VIEW3D_MT_ke_pie_orientpivot"

    def draw(self, context):
        mode = bpy.context.mode
        obj = context.active_object
        layout = self.layout
        pie = layout.menu_pie()

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3
        cbox.prop(context.scene.transform_orientation_slots[0], "type", expand=True)
        cbox.separator()
        cbox.separator()
        cbox.operator("view3d.ke_opc", text=" O&P Combo 3  ", icon="HANDLETYPE_FREE_VEC").combo = "3"

        c = pie.column()
        cbox = c.box().column()
        cbox.scale_y = 1.3

        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='BOUNDING_BOX_CENTER')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='CURSOR')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='INDIVIDUAL_ORIGINS')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='MEDIAN_POINT')
        cbox.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='ACTIVE_ELEMENT')
        if (obj is None) or (mode in {'OBJECT', 'POSE', 'WEIGHT_PAINT'}):
            cbox.prop(context.scene.tool_settings, "use_transform_pivot_point_align")
        else:
            cbox.separator()
            cbox.separator()
        cbox.separator()
        cbox.separator()
        cbox.operator("view3d.ke_opc", text="O&P Combo 4", icon="HANDLETYPE_FREE_VEC").combo = "4"

        # pie.separator()
        pie.operator("view3d.ke_opc", text="O&P Combo 1", icon="KEYTYPE_BREAKDOWN_VEC").combo = "1"
        pie.operator("view3d.ke_opc", text="O&P Combo 2", icon="KEYTYPE_JITTER_VEC").combo = "2"


class VIEW3D_MT_PIE_ke_shading(Menu):
    bl_label = "keShading"
    bl_idname = "VIEW3D_MT_ke_pie_shading"

    def get_shading(cls, context):
        # Get settings from 3D viewport or OpenGL render engine
        view = context.space_data
        if view.type == 'VIEW_3D':
            return view.shading
        else:
            return context.scene.display.shading

    def draw(self, context):
        view = context.space_data
        layout = self.layout
        shading = self.get_shading(context)
        pie = layout.menu_pie()

        # SLOT --------------------------------------------------------------------------------
        pie.prop(view.shading, "type", expand=True)

        # SLOT --------------------------------------------------------------------------------
        if shading.type == 'RENDERED':
            c = pie.row()
            col = c.box().column()
            col.prop(shading, "use_scene_lights")
            col.prop(shading, "use_scene_world")
            col.separator()
            col.prop(shading, "render_pass", text="")

            spacer = c.column()
            spacer.label(text="")
        else:
            pie.separator()

        # SLOT --------------------------------------------------------------------------------
        if shading.type == 'SOLID' and shading.light != 'FLAT':
            spacer = pie.row()
            spacer.label(text="")

            col = spacer.box().column()
            sub = col.row()

            if shading.light == 'STUDIO':
                prefs = context.preferences
                system = prefs.system

                if not system.use_studio_light_edit:
                    sub.scale_y = 0.6  # smaller studiolight preview
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
                sub2.scale_y = 1.8
                sub2.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
                sub2.prop(shading, "use_world_space_lighting", text="", icon='WORLD', toggle=True)
                sub2.active = shading.use_world_space_lighting
                sub2.prop(shading, "studiolight_rotate_z", text="")


            elif shading.light == 'MATCAP':
                sub.scale_y = 0.6  # smaller matcap preview
                sub.template_icon_view(shading, "studio_light", scale_popup=3.0)

                sub = sub.column()
                sub.scale_y = 1.8
                sub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')
                sub.operator("view3d.toggle_matcap_flip", emboss=False, text="", icon='ARROW_LEFTRIGHT')


        elif shading.type == 'RENDERED' and not shading.use_scene_world:
            spacer = pie.row()
            spacer.label(text="")

            col = spacer.box().column()
            sub = col.row()
            sub.scale_y = 0.6
            sub.template_icon_view(shading, "studio_light", scale_popup=3)

            sub2 = sub.column()
            sub2.scale_y = 1.8
            sub2.prop(shading, "studiolight_rotate_z", text="")
            sub2.prop(shading, "studiolight_intensity", text="")
            sub2.prop(shading, "studiolight_background_alpha", text="")

            psub = sub.column()
            psub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')

        else:
            pie.separator()


        # SLOT --------------------------------------------------------------------------------
        if shading.type == 'MATERIAL':
            c = pie.row()
            col = c.box().column()
            col.prop(shading, "use_scene_lights")
            col.prop(shading, "use_scene_world")
            col.separator()
            col.prop(shading, "render_pass", text="")

            spacer = c.column()
            spacer.label(text="")
        else:
            pie.separator()


        # SLOT --------------------------------------------------------------------------------
        c = pie.row()
        spacer = c.column()

        if shading.type == 'SOLID':
            spacer.label(text="")
            col = c.box().column()
            lights = col.row()
            lights.prop(shading, "light", expand=True)
            col.separator()
            col.grid_flow(columns=3, align=True).prop(shading, "color_type", expand=True)
            if shading.color_type == 'SINGLE':
                col.column().prop(shading, "single_color", text="")

        elif shading.type == 'MATERIAL':
            if not shading.use_scene_world:
                spacer.label(text="")

                col = c.box().column()
                sub = col.row()
                sub.scale_y = 0.6
                sub.template_icon_view(shading, "studio_light", scale_popup=3)

                sub2 = sub.column()
                sub2.scale_y = 1.8
                sub2.prop(shading, "studiolight_rotate_z", text="")
                sub2.prop(shading, "studiolight_intensity", text="")
                sub2.prop(shading, "studiolight_background_alpha", text="")

                psub = sub.column()
                psub.operator("preferences.studiolight_show", emboss=False, text="", icon='PREFERENCES')


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    VIEW3D_OT_ke_snap_element,
    VIEW3D_OT_ke_snap_target,
    VIEW3D_MT_PIE_ke_snapping,
    VIEW3D_OT_ke_pieops,
    VIEW3D_MT_PIE_ke_fit2grid,
    VIEW3D_MT_PIE_ke_fit2grid_micro,
    VIEW3D_MT_PIE_ke_overlays,
    VIEW3D_MT_PIE_ke_orientpivot,
    VIEW3D_MT_PIE_ke_shading,
    )

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
