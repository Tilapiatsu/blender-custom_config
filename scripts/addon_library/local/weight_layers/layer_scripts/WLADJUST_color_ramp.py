from .WL_layer_functions import CustomAdjustmentSettingsBase
import bpy


class CustomLayerSettings(CustomAdjustmentSettingsBase):

    hoho: bpy.props.BoolProperty()

    def draw_adjustment(self, context, layout):
        col = layout.column(align=True)
        adjustment_node = self.node
        ramp_node = [n for n in adjustment_node.node_tree.nodes if n.type == "VALTORGB"][0]
        col.scale_y = 0.9
        self.draw_color_ramp(col, ramp_node)

    def draw_layer(self, context, layout):
        col = layout.column(align=False)
        ramp_node = [n for n in self.node.node_tree.nodes if n.type == "VALTORGB"][0]
        col.scale_y = 0.9
        self.draw_color_ramp(col, ramp_node)
