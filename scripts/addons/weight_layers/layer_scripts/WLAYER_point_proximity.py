from .WL_layer_functions import CustomLayerSettingsBase


class CustomLayerSettings(CustomLayerSettingsBase):

    def draw_layer(self, context, layout):
        layer_node = self.node
        self.draw_mix_settings(layout)
        bools = [i for i in layer_node.inputs if i.type == "BOOLEAN" and not i.links]
        type = "VECTOR" if not bools[1].default_value else "OBJECT"
        location_input = [i for i in layer_node.inputs if i.type == type and not i.links][0]
        for socket in bools:
            self.draw_aligned_boolean(layout, socket)
        location_input.draw(context, layout, layer_node, location_input.name)
        self.draw_adjustments_stack(context, layout)
