import bpy

from ..pidgeon_tool_bag.PTB_PropertiesRender_Panel import PTB_PT_Panel

from bpy.types import (
    Context,
    Panel,
)

def template_passes(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_passes", emboss=False, text="Passes", icon="RENDERLAYERS")
    if settings.show_passes:
        boxcol = box.column()
        boxrow = boxcol.row()
        boxrow.prop(settings, "diffuse", icon="MESH_CIRCLE", toggle=True)
        boxrow.prop(settings, "glossy", icon="NODE_MATERIAL", toggle=True)
        boxrow.prop(settings, "transmission", icon="SPHERE", toggle=True)
        boxrow = boxcol.row()
        boxrow.prop(settings, "emission", icon="LIGHT_SUN", toggle=True)
        boxrow.prop(settings, "environment", icon="WORLD_DATA", toggle=True)
        boxrow.prop(settings, "volume", icon="VOLUME_DATA", toggle=True)
        boxcol.separator(factor=0.5)
        boxcol.operator("superimagedenoiser.detectpasses", icon="VIEWZOOM")

def template_advanced_settings(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_advanced", emboss=False, text="Advanced Settings", icon="SYSTEM")
    if settings.show_advanced:
        boxcol = box.column()
        boxcol.prop(settings, "overscan")
        boxcol.prop(settings, "frame_compensation", toggle=True)

def template_quality(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings,"show_quality", emboss=False, text="Quality", icon="IPO_EASE_IN_OUT")
    if settings.show_quality:
        boxcol = box.column()
        boxrow = boxcol.row(align=True)
        boxrow.scale_y = 1.5
        boxrow.prop(settings, "quality", expand=True)

        if not settings.quality == "Standard":
            template_passes(boxcol, settings)

def template_sidt_general(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_general", emboss=False, text="General Settings", icon="SETTINGS")
    if settings.show_general:
        boxcol = box.column()
        boxcol.prop(settings, "working_directory", icon="FILE_FOLDER")
        boxcol.prop(settings, "custom_name", icon="TEXT")
        boxrow = boxcol.row()
        boxrow.prop(settings, "multilayer_exr", icon="RENDERLAYERS", toggle=True)
        boxrowexr = boxrow.row()
        boxrowexr.enabled = settings.multilayer_exr
        boxrowexr.prop(settings, "multilayer_exr_path")
        template_advanced_settings(boxcol, settings)

def template_sidt_render(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_sidt_render", emboss=False, text="Step 1: Render", icon="RENDER_ANIMATION")
    if settings.show_sidt_render:
        boxcol = box.column()
        boxcol.prop(settings, "smaller_exr_files", icon="FULLSCREEN_EXIT")
        boxcol.prop(bpy.context.scene.render, "use_overwrite", text="Overwrite existing files", toggle=True, icon="CURRENT_FILE")
        boxrow = box.row(align=True)
        boxrow.scale_y = 1.5
        boxrow.operator("superimagedenoiser.sidtrender", icon="RENDER_ANIMATION")
        boxrow.scale_x = 1.5
        boxrow.operator("superimagedenoiser.openfolderrendered", icon="FILE_FOLDER", text="")

def template_sidt_motionblur(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_sidt_denoise_mb", emboss=False, text="Motion Blur", icon="ONIONSKIN_ON" if settings.motion_blur else "ONIONSKIN_OFF")
    if settings.show_sidt_denoise_mb:
        boxcol = box.column()
        boxcol.prop(settings, "motion_blur", toggle=True)
        mbcol = boxcol.column()
        mbcol.enabled = settings.motion_blur
        mbcol.use_property_split = False
        mbcol.prop(settings, "motion_blur_samples")
        mbcol.prop(settings, "motion_blur_shutter_speed")
        mbcol.separator(factor=0.5)
        mbcol.prop(settings, "motion_blur_min_speed")
        mbcol.prop(settings, "motion_blur_max_speed")
        mbcol.separator(factor=0.5)
        if settings.motion_blur_curved_interpolation:
            mbci_icon = "IPO_BEZIER"
        else:
            mbci_icon = "IPO_LINEAR"
        mbcol.prop(settings, "motion_blur_curved_interpolation", toggle=True, icon=mbci_icon)

def template_sidt_ted(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_sidt_denoise_ted", emboss=False, text="TED-Filter", icon="NLA")
    if settings.show_sidt_denoise_ted:
        boxcol = box.column()
        boxcol.prop(settings, "ted_source")
        boxcol.prop(settings, "ted_threshold")
        boxcol.prop(settings, "ted_radius")

def template_sidt_denoise(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_sidt_denoise", emboss=False, text="Step 2: Denoise", icon="SHADERFX")
    if settings.show_sidt_denoise:
        boxcol = box.column()
        boxcol.prop(settings, "file_format", icon="IMAGE_DATA")
        boxcol.prop(settings, "use_sac", icon="OUTLINER_DATA_CAMERA")
        if settings.use_sac:
            if not bpy.data.node_groups.get("Super Advanced Camera"):
                boxrow = boxcol.row()
                boxrow.label(text="You need to initialize SAC to use this feature!", icon="ERROR")
                boxrow.operator("superadvancedcamera.superadvancedcamerainit", text="Initialize SAC", icon="SHADERFX")
        template_sidt_motionblur(boxcol, settings)
        template_sidt_ted(boxcol, settings)
        boxrow = box.row(align=True)
        boxrow.scale_y = 1.5
        boxrow.operator("superimagedenoiser.sidtdenoise", icon="SHADERFX")
        boxrow.scale_x = 1.5
        boxrow.operator("superimagedenoiser.openfolderdenoised", icon="FILE_FOLDER", text="")

def template_sidt_combine_video(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_sidt_combine_video", emboss=False, text="Video Settings", icon="RENDER_ANIMATION")
    if settings.show_sidt_combine_video:
        boxcol = box.column()
        boxcol.prop(settings, "ffmpeg_use_autosplit")
        boxcol.prop(settings, "ffmpeg_quality")
        boxcol.prop(settings, "ffmpeg_preset")
        if settings.ffmpeg_quality == "NONE":
            boxcol.prop(settings, "ffmpeg_video_bitrate")

def template_sidt_combine(col, settings):
    box = col.box()
    boxcoltitle = box.column()
    boxcoltitle.scale_y = 1.5
    boxcoltitle.prop(settings, "show_sidt_combine", emboss=False, text="Step 3: Frames to Animation (optional)", icon="SEQUENCE")
    if settings.show_sidt_combine:
        boxcol = box.column()
        boxcol.prop(settings, "file_format_video", icon="IMAGE_DATA")
        template_sidt_combine_video(boxcol, settings)
        boxrow = box.row(align=True)
        boxrow.scale_y = 1.5
        boxrow.operator("superimagedenoiser.sidtcombine", icon="SHADERFX")
        boxrow.scale_x = 1.5
        boxrow.operator("superimagedenoiser.openfoldercombined", icon="FILE_FOLDER", text="")

class SID_PT_General_Panel(PTB_PT_Panel, Panel):
    bl_label = "Super Image Denoiser"
    bl_parent_id = "PTB_PT_PTB_Panel"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="SHADERFX")

    def draw(self, context: Context):
        settings = context.scene.sid_settings

        layout = self.layout
        col = layout.column()
        col.label(text="Denoiser Type", icon="NODE_TEXTURE")
        row = col.row(align=True)
        row.scale_y = 1.5
        row.prop(settings, "denoiser_type", expand=True)
        col.separator()

        if settings.denoiser_type == "SID":
            template_quality(col, settings)
            boxcol = col.box()
            boxcoltitle = boxcol.column()
            boxcoltitle.scale_y = 1.5
            boxcoltitle.prop(settings, "show_general", emboss=False, text="General Settings", icon="SETTINGS")
            if settings.show_general:
                boxcol = boxcol.column()
                boxrow = boxcol.row()
                boxrow.prop(settings, "multilayer_exr", icon="RENDERLAYERS", toggle=True)
                boxrowexr = boxrow.row()
                boxrowexr.enabled = settings.multilayer_exr
                boxrowexr.prop(settings, "multilayer_exr_path")

            col.separator()
            col.operator("superimagedenoiser.addsuperimagedenoiser", icon="ADD")
            col.operator("superimagedenoiser.addsuperimagedenoiser", text="Refresh Super Image Denoiser", icon="FILE_REFRESH")

        elif settings.denoiser_type == "SIDT":
            template_quality(col, settings)
            template_sidt_general(col, settings)
            template_sidt_render(col, settings)
            template_sidt_denoise(col, settings)
            template_sidt_combine(col, settings)

classes = (
    SID_PT_General_Panel,
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

