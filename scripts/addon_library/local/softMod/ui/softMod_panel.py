import bpy
from .. import bl_info
from .. api.object_handlers import SoftWidgetHandler, SoftDeformedHandler


version = ".".join([ str(x) for x in bl_info["version"]])

class SOFTMOD_PT_Panel(bpy.types.Panel):
    global version
    bl_idname = "SOFTMOD_PT_Panel"
    bl_label =  "SoftMod v{}".format(version)
    bl_category = "SoftMod"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ""

    def draw(self, context):
        layout=self.layout
        soft_mod= context.scene.soft_mod
        soft_widget = None
        if context.active_object:
            soft_widget = context.object.soft_widget
        scene = context.scene
        active_mesh = None

        gp_row = layout.row (align=True)
        gp_row.prop (soft_mod , "show_global_properties" , text="SoftMod Global" ,
                    icon='TRIA_DOWN' if soft_mod.show_widget_properties else 'TRIA_RIGHT')

        if soft_mod.show_global_properties:
            w_size_row_title = layout.row(align=True)
            w_size_row_title.label(text = "Widgets Size:")

            w_size_row = layout.row()
            w_size_row.prop (soft_mod , "widget_global_size" , text="", toggle=True)

            w_create_row_title = layout.row(align=True)
            w_create_row_title.label(text = "Create Delete Soft Mods:")
            row = layout.row ()
            row.operator("object.create_softmod_op", text="Create")

            falloff_label = "Surface Falloff"
            if context.active_object:
                if context.active_object.type == "GPENCIL":
                    falloff_label = "Active Layer"


            row.prop (soft_mod , "surf_falloff" , text=falloff_label)



            row2 = layout.row()
            row2.operator("object.delete_custom", text="Delete SoftMod")

            w_link_row_title = layout.row(align=True)
            w_link_row_title.label(text="Constrain Soft Mods:")

            parent_row = layout.row ()
            parent_row.operator ("object.parent_widget" , text="Parent Widgets")

            unparent_row = layout.row ()
            unparent_row.operator ("object.unparent_widget" , text="Unparent Widgets")

            w_utility_row_title = layout.row(align=True)
            w_utility_row_title.label(text="Soft Mods Utilities:")

            toggle_all_row = layout.row ()
            toggle_all_row.operator ("object.softmod_toggle" , text="Toggle Influences")


            convert_row = layout.row()
            convert_row.operator( "object.convert_widget_to_shape_key", text="Selected to Shape Keys")

            w_smooth_row_title = layout.row(align=True)
            w_smooth_row_title.label(text="Smooth SoftMod:")

            row5 = layout.row()
            row5.operator("object.softmod_smooth", text="Smooth Weights")

            smooth_op1 = layout.row()
            smooth_op1.prop(soft_mod, "smooth_factor", text="Factor")

            #smooth_op2 = layout.row()
            smooth_op1.prop(soft_mod, "smooth_iterations", text="Iterations")

            smooth_op3 = layout.row()
            smooth_op3.prop(soft_mod, "smooth_expand", text="Smooth Expand")


        active = bpy.context.active_object
        if not active:
            return
        widget = SoftWidgetHandler.from_widget (active)
        if widget:
            active_mesh = widget.deformed

            w_row = layout.row (align=True)

            w_row.prop (soft_mod , "show_widget_properties" , text="Active: {}".format(widget.name) ,
                      icon='TRIA_DOWN' if soft_mod.show_widget_properties else 'TRIA_RIGHT')
            if soft_mod.show_widget_properties:
                #text_row = layout.row()
                #text_row.prop(widget.widget, "name", text = "")
                #text_row.enabled = False

                w_type_row = layout.row ()
                w_type_row.prop (widget.widget , "empty_display_type" , text="Display As:" )

                w_size_row = layout.row ()
                w_size_row.prop (soft_widget , "widget_relative_size" , text="Widget relative size")

                row6 = layout.row()
                row6.prop (widget.widget , '["influence"]' , slider=True)

                envelope_row = layout.row()
                envelope_row.prop (widget.armature.modifier, 'use_vertex_groups', text="Use Vertex Groups")
                paint_row = layout.row()
                paint_row.operator ("object.softmod_paint" , text="Paint SoftMod")
                rad_row = layout.row()
                rad_row.prop (widget.widget , '["radius"]' , slider=True)
                if widget.armature.modifier.use_vertex_groups:
                    rad_row.enabled = False

                toggle_row = layout.row()
                toggle_row.operator ("object.softmod_toggle" , text="Toggle States")

                #text_row = layout.row()
                #text_row.prop(soft_mod, "widget_name", text = "")
                #rename_row = layout.row()
                #rename_row.operator("object.rename_softmod", text = "Rename")
                mod = widget.armature.modifier
                if mod:
                    pres_vol_row = layout.row ()
                    pres_vol_row.prop (mod , "use_deform_preserve_volume" , text="Preserve Volume")
                mirror_bone = widget.armature.mirror_deform_bone.bone
                if mirror_bone:
                    mirror_tog_row = layout.row()
                    mirror_tog_row.prop(mirror_bone, "use_deform", text = "Activate symmetry")
                    if mirror_bone.use_deform:


                        top_sym_row = layout.row()
                        top_sym_row.prop (soft_widget , "topologycal_sym" , text="Topology mirror")

                        mirror_row = layout.row ()
                        mirror_row.operator ("object.mirror_soft_weights" , text="Mirror Weights")

                if not widget.armature.modifier.use_vertex_groups:
                    paint_row.enabled = False
        if not active_mesh and active.type == "MESH":
            active_mesh = SoftDeformedHandler(active)

        if not active_mesh:
            return
        m_row = layout.row (align=True)
        m_row.prop (soft_mod , "show_mesh_properties" , text=active_mesh.name ,
                  icon='TRIA_DOWN' if soft_mod.show_mesh_properties else 'TRIA_RIGHT')
        if soft_mod.show_mesh_properties:
            bake_row = layout.row()
            bake_row.operator("object.convert_to_shape_key", text="Capture Shape Key")

            if context.active_object.mode == "WEIGHT_PAINT":
                widget = active_mesh.widget_from_active_v_group()


                paint_label_row = layout.row()
                paint_label_row.alignment = "CENTER"

                paint_label_row.label(text="Weight Paint Options:")

                active_mirror_row = layout.row()
                active_mirror_row.operator("object.activate_mirror_weight", text="Paint Opposite Group")

                paint_weight_row = layout.row()
                paint_weight_row.prop(scene.tool_settings.unified_paint_settings,"weight", text = "Weight")

                paint_size_row = layout.row()
                paint_size_row.prop(scene.tool_settings.unified_paint_settings,"size", text = "Brush Size")

                #paint_smooth_row = layout.row ()
                #paint_smooth_row.operator ("object.smooth_paint_weight" , text="Smooth Weight")

                if widget:
                    mirror_bone = widget.armature.mirror_deform_bone.bone
                    if mirror_bone:
                        mirror_tog_row = layout.row ()
                        mirror_tog_row.prop (mirror_bone , "use_deform" , text="Activate symmetry")
                        if mirror_bone.use_deform:

                            mirror_paint_row = layout.row()
                            mirror_paint_row.operator("object.mirror_paint_weight", text="Mirror to Opposite Group")

                            top_sym_row = layout.row ()
                            top_sym_row.prop (soft_widget , "topologycal_sym" , text="Topology mirror")