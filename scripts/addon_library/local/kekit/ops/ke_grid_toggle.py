from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty


class KeGridToggle(Operator):
    bl_idname = "view3d.ke_grid_toggle"
    bl_label = "Grid Scale Toggle"
    bl_description = ("Toggles between 4 Grid Scale Factor values (Op also in keOverlays Pie Menu)\n"
                      "Values hardcoded (tbd) to: 1.0, 0.5, 0.25 & 0.1")

    factor : FloatProperty(default=1.0)
    toggle : BoolProperty(default=False)

    def execute(self, context):
        new_value = self.factor
        if self.toggle:
            values = [1.0, 0.5, 0.25, 0.1] * 2
            current = round(context.space_data.overlay.grid_scale, 4)
            if current in values:
                next_index = values.index(current) + 1
                new_value = values[next_index]
            else:
                new_value = values[0]
        context.space_data.overlay.grid_scale = new_value
        return {"FINISHED"}
