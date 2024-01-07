import bpy
from .PTB_Functions import word_wrap, draw_notification
from bpy.types import (
    Context,
    Panel,
)

class PTB_PT_Panel:
    bl_label = "Pidgeon Tool Bag"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {"DEFAULT_CLOSED"}


class PTB_PT_PTB_Panel(PTB_PT_Panel, Panel):
    bl_label = "Pidgeon Tool Bag"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="SHADERFX")

    def draw(self, context: Context):
        layout = self.layout


class PTB_PT_Info_Panel(PTB_PT_Panel, Panel):
    bl_label = "Info"
    bl_parent_id = "PTB_PT_PTB_Panel"

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon="INFO")

    def draw(self, context: Context):
        layout = self.layout
        col = layout.column()
        
        draw_notification(col)

        box = col.box()

        row = box.row()
        row.label(text="Pidgeon Tool Bag:")
        row.label(text="v2.0.1")

        row = box.row()
        row.label(text="Super Project Manager:")
        row.label(text="v1.5.0")

        row = box.row()
        row.label(text="Super Fast Render:")
        row.label(text="v4.0.0")

        row = box.row()
        row.label(text="Super Advanced Camera:")
        row.label(text="v2.1.1")

        row = box.row()
        row.label(text="Super Image Denoiser:")
        row.label(text="v5.0.1")

        row = box.row()
        row.label(text="Super Image Upscaler:")
        row.label(text="v1.0.0")

        row = box.row()
        row.label(text="Super Resolution Render:")
        row.label(text="v2.1.0")

        row = box.row()
        row.label(text="Super Render Farm:")
        row.label(text="v0.3.0")

        box = col.box()
        
        word_wrap(
            string="This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\n\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA. Alternatively, see https://www.gnu.org/licenses/",
            layout=box,
            alignment="CENTER",
            max_char=70
        )


class PTB_PT_Socials_Panel(PTB_PT_Panel, Panel):
    bl_label = "Our Socials"
    bl_parent_id = "PTB_PT_PTB_Panel"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="FUND")

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("wm.url_open", text="Join our Discord!").url = "https://discord.gg/cnFdGQP"
        row = col.row()
        row.operator("wm.url_open", text="YouTube").url = "https://www.youtube.com/channel/UCgLo3l_ZzNZ2BCQMYXLiIOg"
        row.operator("wm.url_open", text="BlenderMarket").url = "https://blendermarket.com/creators/kevin-lorengel"
        row.operator("wm.url_open", text="Instagram").url = "https://www.instagram.com/pidgeontools/"
        row.operator("wm.url_open", text="Twitter").url = "https://twitter.com/PidgeonTools"
        col.operator("wm.url_open", text="Support and Feedback!", icon="HELP").url = "https://discord.gg/cnFdGQP"


classes = (
    PTB_PT_PTB_Panel,
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
