import bpy

from ..pidgeon_tool_bag.PTB_Functions import template_boxtitle
from ..pidgeon_tool_bag.PTB_PropertiesRender_Panel import PTB_PT_Panel
from ..__init__ import PTB_Preferences

from bpy.types import (
    Context,
    Panel,
)

class SRF_PT_General_Panel(PTB_PT_Panel, Panel):
    bl_label = "Super Render Farm"
    bl_parent_id = "PTB_PT_PTB_Panel"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="NETWORK_DRIVE")

    def draw(self, context: Context):
        scene = context.scene
        settings = scene.srf_settings
        colmain = self.layout.column(align=False)
        unsupported_formats = ["AVI_JPEG", "AVI_RAW", "FFMPEG"]
        enable_ca = True

        colaction = colmain.column()
        colaction.scale_y = 1.5
        colaction.operator("pidgeontoolbag.open_addon_prefs", text="Open Master Settings", icon="EXTERNAL_DRIVE")

        boxrs = colmain.box()
        template_boxtitle(settings, boxrs, "rs", "Render Settings", "MOD_HUE_SATURATION")
        if settings.show_rs:

            boxrsgeneral = boxrs.box()
            template_boxtitle(settings, boxrsgeneral, "rs_general", "General Settings", "SETTINGS")
            if settings.show_rs_general:
                col = boxrsgeneral.column()
                boxrsaddons = col.box()
                colrsaddons = boxrsaddons.column()
                colrsaddons.prop(settings, "rs_use_sfr", toggle=True)
                colrsaddons.prop(settings, "rs_use_sidt", toggle=True)
                col.separator(factor=0.2)
                col.prop(settings, "rs_test_render", toggle=True)
                col.prop(settings, "rs_batch_size")

                boxrsadvanced = boxrsgeneral.box()
                template_boxtitle(settings, boxrsadvanced, "rs_advanced", "Advanced Settings", "SYSTEM")
                if settings.show_rs_advanced:
                    col = boxrsadvanced.column()
                    row = col.row()
                    row.alignment = "CENTER"
                    row.label(text="Transfer Method")
                    row = col.row()
                    row.prop(settings, "rs_transfer_method", expand=True)
                    if settings.rs_transfer_method == "0":
                        coltcp = col.box()
                        coltcp.label(text="Everything is automatic", icon="INFO")
                    elif settings.rs_transfer_method == "1":
                        colsmb = col.box()
                        if settings.master_smb_url == "":
                            rowsmb = colsmb.row()
                            rowsmb.label(text="SMB URL is empty", icon="CANCEL")
                            rowsmb.prop(settings, "master_smb_url")
                            enable_ca = False
                        if settings.master_smb_user == "":
                            rowsmb = colsmb.row()
                            rowsmb.label(text="SMB Username is empty", icon="ERROR")
                            rowsmb.prop(settings, "master_smb_user")
                        if settings.master_smb_pass == "":
                            rowsmb = colsmb.row()
                            rowsmb.label(text="SMB Password is empty", icon="ERROR")
                            rowsmb.prop(settings, "master_smb_pass")
                    elif settings.rs_transfer_method == "2":
                        colftp = col.box()
                        if settings.master_ftp_url == "":
                            rowftp = colftp.row()
                            rowftp.label(text="FTP URL is empty", icon="CANCEL")
                            rowftp.prop(settings, "master_ftp_url")
                            enable_ca = False
                        if settings.master_ftp_user == "":
                            rowftp = colftp.row()
                            rowftp.label(text="FTP Username is empty", icon="ERROR")
                            rowftp.prop(settings, "master_ftp_user")
                        if settings.master_ftp_pass == "":
                            rowftp = colftp.row()
                            rowftp.label(text="FTP Password is empty", icon="ERROR")
                            rowftp.prop(settings, "master_ftp_pass")
                    col.separator()
                    col.prop(settings, "rs_render_device")
                    col.prop(settings, "rs_close_blender", text="Close Blender on render start",toggle=True)

        if scene.render.image_settings.file_format in unsupported_formats:
            enable_ca = False
            rowmain = colmain.row()
            rowmain.alignment = "CENTER"
            rowmain.scale_y = 1.5
            rowmain.label(text="Unsupported file format", icon="CANCEL")
            colmain.operator("superrenderfarm.gotooutput", text="Go To Outputs", icon="OUTPUT")

        colaction = colmain.column()
        colaction.scale_y = 1.5
        colaction.enabled = enable_ca
        colaction.operator("superrenderfarm.pack_external_and_save", text="Pack External Data and Save", icon="FILE_TICK")
        rowaction = colaction.row(align=True)
        rowaction.operator("superrenderfarm.start_render", text="Start Render", icon="RENDER_ANIMATION")
        rowaction.operator("superrenderfarm.openfolderrender", text="", icon="FILE_FOLDER")

classes = (
    SRF_PT_General_Panel,
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

