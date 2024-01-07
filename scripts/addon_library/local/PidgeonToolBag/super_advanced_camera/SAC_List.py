import bpy

from .SAC_Functions import mute_update

from bpy.types import (
    PropertyGroup,
    UIList,
)


class SAC_EffectList(PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Untitled")
    icon: bpy.props.StringProperty(name="Icon", default="NONE")
    warn: bpy.props.BoolProperty(name="Warn", default=False, description="This effect is not viewport compatible.\nIt will work in the final render.\n\nThis is a limitation of Blender.\nDisable this effect to see the viewport.")
    mute: bpy.props.BoolProperty(name="Mute", default=False, update=mute_update, description="Disable this effect for viewport and final render.")
    EffectGroup: bpy.props.StringProperty(name="Effect Group", default="")
    ID: bpy.props.StringProperty(name="ID", default="")


class SAC_UL_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            main_row = layout.row(align=True)

            # Create the first part of the layout
            split = main_row.split(factor=0.66, align=False)
            # split.prop(item, "name", text="", emboss=False, icon=item.icon)
            split.label(text=f"{item.ID} - {item.name}", icon=item.icon)

            row = split.row(align=True)
            row.emboss = 'NONE_OR_STATUS'

            # Create a new row for the warning icon
            warning_row = main_row.row(align=True)
            warning_row.prop(item, "warn", text="", emboss=False, icon='ERROR' if item.warn else 'NONE')

            # Create a new row for the mute button on the far right
            mute_row = main_row.row(align=True)
            mute_row.prop(item, "mute", text="", emboss=False, icon='HIDE_OFF' if not item.mute else 'HIDE_ON')
            if item.mute:
                split.active = False


classes = (
    SAC_EffectList,
    SAC_UL_List,
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
