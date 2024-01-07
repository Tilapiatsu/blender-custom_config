import bpy

from ..pidgeon_tool_bag.PTB_PropertiesRender_Panel import PTB_PT_Panel
from ..pidgeon_tool_bag.PTB_Functions import template_boxtitle

from bpy.types import (
    Context,
    Panel,
)

class SPM_PT_General_Panel(PTB_PT_Panel, Panel):
    bl_label = "Super Project Manager"
    bl_parent_id = "PTB_PT_PTB_Panel"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="FILE_BLEND")

    def draw(self, context: Context):
        settings = context.scene.spm_settings
        prefs = bpy.context.preferences.addons[__package__.split(".")[0]].preferences

        colmain = self.layout.column()
        boxps = colmain.box()
        template_boxtitle(settings, boxps, "project_starter", "Project Starter", "NEWFOLDER")
        if settings.show_project_starter:

            colps = boxps.column()
            box = colps.box()
            box.prop(context.scene, "project_name")
            box.prop(context.scene, "project_location")
            box.prop(context.scene, "save_blender_file", toggle=True)
            colps.separator()

            box = colps.box()
            box.prop(context.scene, "save_file_name")
            box.prop(prefs, "save_folder")
            row = box.row()
            row.prop(context.scene, "remap_relative", toggle=True)
            row.prop(context.scene, "compress_save", toggle=True)
            colps.separator()

            box = colps.box()
            row = box.row()
            row.scale_y = 1.5
            row.prop(context.scene, "project_setup", expand=True)
            col = box.column()
            if context.scene.project_setup == "Custom_Setup":
                boxcustom = col.box()
                boxcustom.label(text="Custom Folder Setup", icon="FILE_FOLDER")

                render_outpath_active = True in [e.render_outputpath for e in prefs.custom_folders]

                for index, folder in enumerate(prefs.custom_folders):
                    rowfolder = boxcustom.row()
                    rowfolder.prop(folder, "folder_name", text="")

                    if prefs.auto_set_render_outputpath:
                        colfolder = rowfolder.column()
                        colfolder.enabled = folder.render_outputpath or not render_outpath_active
                        colfolder.prop(folder, "render_outputpath", text="", icon="OUTPUT", emboss=folder.render_outputpath)

                    op = rowfolder.operator("superprojectmanager.remove_folder", text="", emboss=False, icon="PANEL_CLOSE")
                    op.index = index
                    op.coming_from = "panel"

                rowfolder = boxcustom.row()
                op = rowfolder.operator("superprojectmanager.add_folder", icon="PLUS")
                op.coming_from = "panel"
            
            else:
                # open preferences
                colbutton = col.column()
                colbutton.scale_y = 1.5
                colbutton.operator("pidgeontoolbag.open_addon_prefs", text="Open Preferences", icon="PREFERENCES")

            col.separator()
            col.prop(context.scene, "open_directory", toggle=True)
            col.separator()
            colaction = col.column()
            colaction.scale_y = 1.5
            colaction.operator("superprojectmanager.build_project", text="Build Project")

classes = (
    SPM_PT_General_Panel,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

