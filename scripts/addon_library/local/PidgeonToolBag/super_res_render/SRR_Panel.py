import bpy
from math import ceil
from ..pidgeon_tool_bag.PTB_PropertiesRender_Panel import PTB_PT_Panel
from ..pidgeon_tool_bag.PTB_Functions import template_boxtitle

from bpy.types import (
    Context,
    Panel,
)

class SRR_PT_General_Panel(PTB_PT_Panel, Panel):
    bl_label = "Super Resolution Render"
    bl_parent_id = "PTB_PT_PTB_Panel"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="SNAP_GRID")

    def draw(self, context: Context):
        layout = self.layout
        scene = context.scene
        render = scene.render
        settings = scene.srr_settings
        status = settings.status

        res_x = render.resolution_x
        res_y = render.resolution_y

        number_divisions = int(settings.subdivisions)
        tiles_per_side = 2 ** number_divisions
        total_tiles = tiles_per_side ** 2
        ideal_tile_x = res_x / tiles_per_side
        ideal_tile_y = res_y / tiles_per_side
        max_tile_x = ceil(ideal_tile_x)
        max_tile_y = ceil(ideal_tile_y)

        panel_active = not status.is_rendering

        colmain = self.layout.column(align=False)
        boxmain = colmain.box()
        template_boxtitle(settings, boxmain, "general", "General Settings", "OPTIONS")
        if settings.show_general:
            boxrow = boxmain.row()
            boxrow.scale_y = 1.5
            boxrow.enabled = panel_active
            boxrow.prop(settings, "render_method", expand=True)
            boxrow = boxmain.row()
            boxrow.scale_y = 1.5
            boxrow.enabled = panel_active
            boxrow.prop(settings, "subdivisions", expand=True)

            if not settings.render_method == "camsplit":
                boxcol = boxmain.column()
                boxcol.enabled = panel_active
                boxcol.prop(settings, "render_path")
                boxcol.prop(settings, "start_tile", expand=True)


        boxmain = colmain.box()
        template_boxtitle(settings, boxmain, "info", "Info", "INFO")
        if settings.show_info:
            boxrow = boxmain.row()
            
            if settings.render_method == "camsplit":
                boxrow.label(text="Suggested Resolution:")
                boxrow.label(text=f"{max_tile_x}px x {max_tile_y}px ({(100 / tiles_per_side):.3g}%)")
            else:
                boxrow.label(text="Max Tile:")
                boxrow.label(text=f"{max_tile_x}px x {max_tile_y}px")
            
                if not status.is_rendering:
                    boxrow = boxmain.row()
                    boxrow.label(text="Rendering:")
                    boxrow.label(text=f"Tile: {status.tiles_done}/{status.tiles_total} - ({status.percent_complete:.1f}%)")


        boxactions = colmain.box()
        boxactions.scale_y = 1.5
        if settings.render_method == "camsplit":
            boxactions.operator("superresrender.splitcam", text="Split Active Camera", icon="MESH_GRID")
        else:
            if not status.is_rendering:
                rowactions = boxactions.row(align=True)
                rowactions.operator("superresrender.startrender", text="Start Rendering", icon="PLAY")
                rowactions.operator("superresrender.openfolder", text="", icon="FILE_FOLDER")
            else:
                rowactions = boxactions.row(align=True)
                rowactions.operator("superresrender.stoprender", text="Stop Rendering", icon="CANCEL")
                rowactions.operator("superresrender.openfolder", text="", icon="FILE_FOLDER")

        boxactions = colmain.box()
        boxactions.scale_y = 1.5
        boxactions.operator("superresrender.merge", text="Merge Frames", icon="FILE_REFRESH")




classes = (
    SRR_PT_General_Panel,
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

