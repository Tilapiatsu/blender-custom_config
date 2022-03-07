from .WL_layer_functions import CustomLayerSettingsBase
import bpy


class CustomLayerSettings(CustomLayerSettingsBase):

    def texture_enum_items(self, context):
        items = []
        for node in self.layer.layer_group.nodes:
            if "TEX" in node.type:
                name = node.name
                items.append((node.label, name, name))

        items.sort(key=lambda item: int(item[0]))
        return items

    def texture_enum_update(self, context):
        self.node.inputs[2].default_value = int(self.texture_enum)

    texture_enum: bpy.props.EnumProperty(items=texture_enum_items, update=texture_enum_update)

    def on_creation(self, context):
        self.texture_enum_update(context)

    def draw_layer(self, context, layout):
        self.draw_mix_settings(layout)
        layout.separator(factor=0.5)
        layout.prop(self, "texture_enum", text="", icon="TEXTURE_DATA")
        layout.separator(factor=0.5)
        nodes = {n.label: n for n in self.layer.layer_group.nodes}
        node = nodes[self.texture_enum]
        node.draw_buttons(context, layout)
        layout.separator(factor=0.5)
        layout = layout.column(align=True)
        self.draw_node_inputs(context, layout, node)
        self.draw_node_inputs(context, layout)
        self.draw_adjustments_stack(context, layout)
