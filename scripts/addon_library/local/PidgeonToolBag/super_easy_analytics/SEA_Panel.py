import bpy
from ..pidgeon_tool_bag.PTB_PropertiesRender_Panel import PTB_PT_Panel
from ..pidgeon_tool_bag.PTB_Functions import template_boxtitle

from bpy.types import (
    Context,
    Panel,
)

class SEA_PT_General_Panel(PTB_PT_Panel, Panel):
    bl_label = "Super Easy Analytics"
    bl_parent_id = "PTB_PT_PTB_Panel"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="ZOOM_ALL")

    def draw(self, context: Context):
        settings = bpy.context.scene.sea_settings

        colmain = self.layout.column(align=False)
        boxmain = colmain.box()
        template_boxtitle(settings, boxmain, "dummy", "COMING SOON", "OPTIONS")
        if settings.show_dummy:
            boxmain.label(text="Super Easy Analytics is developed by Beedy.", icon="INFO")
            boxmain.label(text="You can track the development on our discord server.", icon="INFO")
            boxmain.operator("wm.url_open", text="Join Discord", icon="URL").url = "https://discord.gg/cnFdGQP"


classes = (
    SEA_PT_General_Panel,
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

