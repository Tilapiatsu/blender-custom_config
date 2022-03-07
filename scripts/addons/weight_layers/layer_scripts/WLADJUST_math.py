from .WL_layer_functions import CustomAdjustmentSettingsBase


class CustomLayerSettings(CustomAdjustmentSettingsBase):

    def draw_adjustment(self, context, layout):
        adjustment_node = self.node
        math_node = [n for n in adjustment_node.node_tree.nodes if n.type == "MATH"][0]
        row = layout.row(align=True)
        self.draw_math_node_operation(row, math_node)
        self.draw_node_inputs(context, row, adjustment_node)

    def draw_layer(self, context, layout):
        self.draw_adjustment(context, layout)