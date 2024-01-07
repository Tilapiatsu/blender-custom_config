import bpy
from ..pidgeon_tool_bag.PTB_PropertiesRender_Panel import PTB_PT_Panel
from ..pidgeon_tool_bag.PTB_Functions import template_boxtitle, dependencies

from bpy.types import (
    Context,
    Panel,
)

class SIU_PT_General_Panel(PTB_PT_Panel, Panel):
    bl_label = "Super Image Upscaler"
    bl_parent_id = "PTB_PT_PTB_Panel"
    
    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="OBJECT_HIDDEN")

    def draw(self, context: Context):
        settings = bpy.context.scene.siu_settings

        colmain = self.layout.column(align=False)
        # boxmain = colmain.box()

        if not dependencies.checked("siu"):
            dependencies.check_dependencies(["siu"])
        
        if dependencies.needs_install("siu"):
            boxcol_base = colmain.box()
            boxcol_base.label(text="Dependencies not found. Please install them.", icon="ERROR")
            boxcol_base.operator("pidgeontoolbag.install_dependencies", text="Install Dependencies", icon="FILE_REFRESH")
        
        # boxcol = boxmain.box()
        # boxrow = boxcol.row(align=True)
        # boxrow.scale_y = 1.5
        # boxrow.prop(settings, "upscaler_type", expand=True)

        if settings.upscaler_type == "esrgan":

            boxcol_esrgan = colmain.box()
            boxcol_esrgan.enabled = not dependencies.needs_install("siu")
            
            template_boxtitle(settings, boxcol_esrgan, "general", "General Settings", "OPTIONS")
            if settings.show_general:
                col = boxcol_esrgan.column(align=False)
                col.prop(settings, "input_folder", text="Input Folder")
                col.prop(settings, "output_folder", text="Output Folder")
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.5
                row.prop(settings, "device", expand=True)

                col.separator(factor=0.5)
                coladvanced = col.column(align=False)
                boxadvanced = coladvanced.box()
                template_boxtitle(settings, boxadvanced, "advanced", "Advanced Settings", "SYSTEM")
                if settings.show_advanced:
                    boxoutput = boxadvanced.box()
                    coloutput = boxoutput.column(align=False)
                    coloutput.prop(settings, "output_prefix", text="Output Prefix")
                    coloutput.prop(settings, "output_suffix", text="Output Suffix")
                    coloutput.separator()
                    rowoutput = coloutput.row(align=True)
                    rowoutput.prop(settings, "output_format", expand=True)
                    coloutput.separator()
                    rowoutput = coloutput.row(align=True)
                    rowoutput.active = False
                    rowoutput.label(text="Output Image:")
                    rowoutput.label(text=f"{settings.output_prefix}Image{settings.output_suffix}.{settings.output_format}")

                    boxmodels = boxadvanced.box()
                    colmodels = boxmodels.column(align=False)

                    if settings.model_primary == "":
                        colmodels.label(text="No models found.", icon="ERROR")
                        colmodels.operator("wm.url_open", text="Download Base Model", icon="URL").url = "https://drive.google.com/drive/u/0/folders/17VYV_SoZZesU6mbxz2dMAIccSSlqLecY"
                        colmodels.separator()
                        colmodels.label(text="Recommended models:", icon="INFO")
                        colmodels.label(text="RRDB_ESRGAN_x4.pth for Primary Model")
                        colmodels.label(text="RRDB_PSNR_x4.pth for Secondary Model")
                        colmodels.separator()
                        colmodels.operator("superimageupscaler.openfoldermodels", text="Model Folder", icon="FILE_FOLDER")
                    else: 
                        rowmodels = colmodels.row(align=True)
                        rowmodels.prop(settings, "model_primary")
                        rowmodels.operator("superimageupscaler.openfoldermodels", text="", icon="FILE_FOLDER")
                        rowmodels = colmodels.row(align=True)
                        rowmodels.prop(settings, "model_secondary")
                        rowmodels.operator("superimageupscaler.openfoldermodels", text="", icon="FILE_FOLDER")
                        colmodels.separator()
                        colmodels.prop(settings, "model_blend", text="Blend Factor")
                        colmodels.operator("wm.url_open", text="Download Base Model", icon="URL").url = "https://drive.google.com/drive/u/0/folders/17VYV_SoZZesU6mbxz2dMAIccSSlqLecY"

                    boxsettings = boxadvanced.box()
                    colsettings = boxsettings.column(align=False)
                    
                    colsettings.prop(settings, "mode_type", text="Mode")
                    colsettings.prop(settings, "scale_factor", text="Scale Factor")
          
        if settings.upscaler_type == "stable":

            boxcol_stable = colmain.box()
            boxcol_stable.enabled = not dependencies.needs_install("siu") 

            template_boxtitle(settings, boxcol_stable, "general", "General Settings", "OPTIONS")
            if settings.show_general:
                col = boxcol_stable.column(align=False)
                col.label(text="IN DEVELOPMENT - COMING SOON", icon="ERROR")


                col.separator(factor=0.5)
                coladvanced = col.column(align=False)
                boxadvanced = coladvanced.box()
                template_boxtitle(settings, boxadvanced, "advanced", "Advanced Settings", "SYSTEM")
                if settings.show_advanced:
                    boxindev = boxadvanced.box()
                    colindev = boxindev.column(align=False)
                    colindev.label(text="IN DEVELOPMENT - COMING SOON", icon="ERROR")


        colactions = colmain.column(align=False)
        boxactions = colactions.box()
        boxactions.scale_y = 1.5
        rowactions = boxactions.row(align=True)
        rowactions.operator("superimageupscaler.upscale_images", text="Upscale Images", icon="OBJECT_HIDDEN")
        rowactions.operator("superimageupscaler.openfolderupscaled", text="", icon="FILE_FOLDER")


classes = (
    SIU_PT_General_Panel,
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

