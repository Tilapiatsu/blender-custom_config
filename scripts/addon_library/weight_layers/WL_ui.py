import bpy

from . import WL_functions
from .WL_constants import IS_AT, AT_ADDON_NAME
from .WL_operators import WEIGHTLAYER_OT_layer_stack_list_actions
from .WL_functions import get_wl_obj, get_wl_icon


class WEIGHTLAYER_UL_LayerStackList(bpy.types.UIList):
    """UIlist for the layer stacks"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        wl_icon = get_wl_icon("weight_layers")
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.emboss = "NONE"

            if item.stack_group:
                row.prop(item.stack_group.wl, "name", text="", icon_value=wl_icon)
                mod_group = WL_functions.get_wl_mod_group(context)
                node = mod_group.nodes.get(str(item.index))
                row.operator("weight_layer.bake_layer_stack",
                             icon="FILE_REFRESH" if item.manual_refresh else "CHECKMARK",
                             text="").stack_index = item.index
                if not item.manual_refresh:
                    row.prop(node,
                             "mute",
                             text="",
                             invert_checkbox=True,
                             icon="RESTRICT_RENDER_ON" if node.mute else "RESTRICT_RENDER_OFF")
            else:
                row.label(text="New Layer stack " + str(index + 1), icon_value=wl_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.emboss = "NONE"
            layout.prop(item.stack_group, "name", text="", icon_value=wl_icon)


class WEIGHTLAYER_PT_stack_settings_panel(bpy.types.Panel):
    """Stack settings panel"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_idname = "WEIGHTLAYER_PT_stack_settings_panel"
    bl_label = "Stack settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        wl = get_wl_obj(context).weight_layers
        layout.prop(wl.layer_stacks[wl.g_index], "manual_refresh")


class WEIGHTLAYER_PT_main_panel(bpy.types.Panel):
    """Weight layers panel"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "WEIGHTLAYER_PT_main_panel"
    bl_label = "Weight Layers"
    bl_category = "Alpha Trees" if IS_AT else "Weight Layers"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        obj = get_wl_obj(context)
        if IS_AT:
            at_prefs = context.preferences.addons[AT_ADDON_NAME].preferences
            return obj and at_prefs.lib_path

        return obj

    def draw(self, context):
        layout = self.layout
        obj = get_wl_obj(context)
        wl = obj.weight_layers
        prefs = WL_functions.get_wl_prefs(context)

        col = WL_functions.draw_ui_list(
            layout,
            list=wl.layer_stacks,
            list_class=WEIGHTLAYER_UL_LayerStackList,
            actions_operator=WEIGHTLAYER_OT_layer_stack_list_actions,
            data=wl,
            list_setting="layer_stacks",
            list_name="Layer_stacks",
            index_data=wl,
            index_name="g_index",
            rows=3,
        )

        if not wl.layer_stacks:
            return

        col.separator(factor=0.5)
        col.popover(panel="WEIGHTLAYER_PT_stack_settings_panel", text="", icon="PREFERENCES")

        slot = wl.layer_stacks[wl.g_index]
        stack_group = slot.stack_group
        mod_group = WL_functions.get_wl_mod_group(context)
        stack_node = mod_group.nodes.get(str(slot.index))
        wl_icon = get_wl_icon("weight_layers")

        row = layout.row(align=True)
        row.prop(slot, "layer_stacks_enum", text="", icon_only=True, icon_value=wl_icon)

        if not stack_group:
            row.operator("weight_layer.new_layer_stack", text="New layer stack", icon="ADD")
            return

        row.prop(stack_group.wl, "name", text="")
        row.operator("weight_layer.copy_layer_stack", text="", icon="DUPLICATE")
        row.operator("weight_layer.new_layer_stack", text="", icon="ADD")
        row.operator("weight_layer.remove_layer_stack", text="", icon="REMOVE")

        if slot.manual_refresh:
            layout.separator(factor=0.1)
            row = layout.row()
            row.scale_y = 1.5
            row.operator("weight_layer.bake_layer_stack", text="Refresh", icon="FILE_REFRESH").stack_index = slot.index
            layout.separator(factor=0.1)
        else:
            layout.separator(factor=0.7)
        layout.menu(menu="WEIGHTLAYER_MT_layer_add", icon="ADD")
        col = layout.column()

        layers = list(stack_group.wl.layers)
        l_reversed = prefs.layer_order == "REVERSED"
        if l_reversed:
            layers.reverse()

        for layer in layers:

            i = layer.index
            layer_group = layer.layer_group
            cache_info = WL_functions.get_layer_cache()
            cache_info = cache_info
            info = WL_functions.get_layer_info(layer_group)
            layer_node = stack_group.nodes[str(i)]

            mod_col = col.column(align=True)
            box = mod_col.box()

            row = box.row(align=True)
            row.scale_x
            row1 = row.row()
            row1.active = not layer_node.mute and not stack_node.mute or slot.manual_refresh
            row1.prop(layer, "show_ui", text="", icon=info["icon"] if info["icon"] else "RENDERLAYERS", emboss=False)
            row1 = row.row()
            row1.prop(layer, "name", text="", emboss=True)

            row1 = row.row(align=True)
            row1.scale_x = 0.9
            row1.prop(layer_node,
                      "mute",
                      invert_checkbox=True,
                      emboss=False,
                      text="",
                      icon="RESTRICT_RENDER_ON" if layer_node.mute else "RESTRICT_RENDER_OFF")

            if l_reversed:
                up = "DOWN"
                down = "UP"
                first = i == len(stack_group.wl.layers) - 1
                last = i == 0
            else:
                up = "UP"
                down = "DOWN"
                first = i == 0
                last = i == len(stack_group.wl.layers) - 1

            sub = row1.row(align=False)
            sub.enabled = not first
            op = sub.operator(
                "weight_layer.layer_actions",
                text="",
                icon="TRIA_UP",
                emboss=False,
            )
            op.action = "MOVE_" + up
            op.index = i

            sub = row1.row(align=True)
            sub.enabled = not last
            op = sub.operator("weight_layer.layer_actions", text="", icon="TRIA_DOWN", emboss=False)
            op.action = "MOVE_" + down
            op.index = i

            op = row1.operator("weight_layer.layer_actions", text="", icon="PANEL_CLOSE", emboss=False)
            op.action = "REMOVE"
            op.index = i

            if layer.show_ui:
                box = mod_col.box()
                boxcol = box.column()
                boxcol.active = not layer_node.mute
                layer.layer_settings.draw_layer(context, boxcol)

            col.separator(factor=0.5)


class WEIGHTLAYER_MT_layer_add(bpy.types.Menu):
    """Add a new weight layer"""
    bl_idname = "WEIGHTLAYER_MT_layer_add"
    bl_label = "Add layer"

    def draw(self, context):
        """Layout inspired by the mask section of Scatter 4 by BD3D,
        as the default operator_menu_enum doesn't support categories (without C code)"""

        layout = self.layout
        layers = WL_functions.get_layer_cache()
        categories = [layers[layer]["category"] for layer in layers]
        categories = list(dict.fromkeys(categories))  # remove duplicates

        categories.sort(reverse=True)

        top_row = layout.row()

        for cat in categories:
            col = top_row.column()
            col.label(text=cat + " " * (16 - len(cat)), icon="ADD")  # add extra spaces to pad out row
            col.separator(factor=0.5)

            for layer_name in layers:
                layer = layers[layer_name]
                if layer["category"] == cat:
                    col.operator("weight_layer.layer_add",
                                 text=layer["name"].capitalize().replace("_", " "),
                                 icon=layer["icon"]).type = layer["name"].upper()


classes = [
    WEIGHTLAYER_PT_stack_settings_panel,
    WEIGHTLAYER_PT_main_panel,
    WEIGHTLAYER_UL_LayerStackList,
    WEIGHTLAYER_MT_layer_add,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
