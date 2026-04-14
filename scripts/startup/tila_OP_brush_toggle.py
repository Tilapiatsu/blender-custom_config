import bpy
from pathlib import Path
from bversion import BVERSION

bl_info = {
    "name": "Tila : Brush toggle",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class TILA_Brush:
    def __init__(
        self,
        relative_asset_identifier: str,
        asset_library_type: str,
        asset_library_identifier: str,
        force_strength: bool = False,
        strength: float = -1.0,
        force_weight: bool = False,
        weight: float = -1.0,
    ):
        self.relative_asset_identifier = str(Path(relative_asset_identifier))
        self.asset_library_type = asset_library_type
        self.asset_library_identifier = asset_library_identifier
        self.force_strength = force_strength
        self.strength = strength
        self.force_weight = force_weight
        self.weight = weight

    @property
    def name(self):
        return Path(self.relative_asset_identifier).stem

    def activate(self):
        bpy.ops.brush.asset_activate(
            relative_asset_identifier=self.relative_asset_identifier,
            asset_library_type=self.asset_library_type,
            asset_library_identifier=self.asset_library_identifier,
        )

    def __eq__(self, other):
        if isinstance(other, TILA_Brush):
            return (
                self.relative_asset_identifier == other.relative_asset_identifier
                and self.asset_library_type == other.asset_library_type
                and self.asset_library_identifier == other.asset_library_identifier
            )
        return False


compatible_modes = [
    "SCULPT",
    "VERTEX",
    "WEIGHT",
    "IMAGE",
    "GPENCIL_PAINT",
    "GPENCIL_SCULPT",
    "GPENCIL_WEIGHT",
    "GPENCIL_VERTEX",
    "SCULPT_CURVES",
]


def mode_enum():
    enum = []
    for m in compatible_modes:
        enum.append((m, m.lower().replace("_", " "), ""))

    return enum


compatible_asset_library_types = ["ALL", "LOCAL", "ESSENTIALS", "CUSTOM"]


def asset_library_types_enum():
    enum = []
    for m in compatible_asset_library_types:
        enum.append((m, m.lower().replace("_", " "), ""))

    return enum


class TILA_PG_Brush(bpy.types.PropertyGroup):
    relative_asset_identifier: bpy.props.StringProperty(name="relative_asset_identifier", default="")
    asset_library_type: bpy.props.StringProperty(name="asset_library_type", default="")
    asset_library_identifier: bpy.props.StringProperty(name="asset_library_identifier", default="")
    force_strength: bpy.props.BoolProperty(name="force strength", default=False)
    strength: bpy.props.FloatProperty(name="strength", default=1.0)
    force_weight: bpy.props.BoolProperty(name="force weight", default=False)
    weight: bpy.props.FloatProperty(name="weight", default=1.0)


class TILA_Brush_toggle(bpy.types.Operator):
    bl_idname = "brush.tila_brush_toggle"
    bl_label = "Brush Toggle"

    mode: bpy.props.EnumProperty(name="mode", items=mode_enum(), default="SCULPT")
    default_relative_asset_identifier: bpy.props.StringProperty(
        name="default brush", default="brushes/essentials_brushes-mesh_sculpt.blend/Brush/Grab"
    )
    default_asset_library_type: bpy.props.StringProperty(name="asset library type", default="ESSENTIALS")
    default_asset_library_identifier: bpy.props.StringProperty(name="asset library identifier", default="")
    default_strength: bpy.props.FloatProperty(name="default strength", default=1.0)
    default_weight: bpy.props.FloatProperty(name="default weight", default=1.0)
    relative_asset_identifier: bpy.props.StringProperty(
        name="brush", default="brushes/essentials_brushes-mesh_sculpt.blend/Brush/Grab"
    )
    asset_library_type: bpy.props.EnumProperty(
        name="asset library type", default="ESSENTIALS", items=asset_library_types_enum()
    )
    asset_library_identifier: bpy.props.StringProperty(name="asset library identifier", default="")
    toggle_back_on_release: bpy.props.BoolProperty(name="toggle back on release", default=False)
    force_strength: bpy.props.BoolProperty(name="force strength", default=False)
    strength: bpy.props.FloatProperty(name="strength", default=1.0)
    force_weight: bpy.props.BoolProperty(name="force weight", default=False)
    weight: bpy.props.FloatProperty(name="weight", default=1.0)

    initial_brush = None
    brush_is_set = False
    press = False
    _current_tool = None

    @property
    def current_tool(self):
        if self._current_tool is None:
            if bpy.context.mode == "SCULPT":
                self._current_tool = bpy.context.tool_settings.sculpt

            elif bpy.context.mode == "VERTEX":
                self._current_tool = bpy.context.tool_settings.vertex_paint

            elif bpy.context.mode == "WEIGHT":
                self._current_tool = bpy.context.tool_settings.weight_paint

            elif bpy.context.mode == "IMAGE":
                self._current_tool = bpy.context.tool_settings.image_paint

            elif bpy.context.mode == "PAINT_GREASE_PENCIL":
                self._current_tool = bpy.context.tool_settings.gpencil_paint

            elif bpy.context.mode == "SCULPT_GREASE_PENCIL":
                self._current_tool = bpy.context.tool_settings.gpencil_sculpt_paint

            elif bpy.context.mode == "WEIGHT_GREASE_PENCIL":
                self._current_tool = bpy.context.tool_settings.gpencil_weight_paint

            elif bpy.context.mode == "VERTEX_GREASE_PENCIL":
                self._current_tool = bpy.context.tool_settings.gpencil_vertex_paint

            elif bpy.context.mode == "SCULPT_CURVES":
                self._current_tool = bpy.context.tool_settings.curves_sculpt

        return self._current_tool

    def get_release_condition(self, event):
        if BVERSION < 3.2:
            return event.type == "MOUSEMOVE" and event.value == "RELEASE"
        else:
            return (
                event.type in ["MOUSEMOVE", "LEFTMOUSE", "RIGHTMOUSE", "WINDOW_DEACTIVATE"]
                and event.value in ["RELEASE", "NOTHING"]
                and self.press
            )

    def get_run_condition(self, event):
        if BVERSION < 3.2:
            return event.type == "MOUSEMOVE" and event.value == "PRESS"
        else:
            return event.type == "MOUSEMOVE" and event.value == "NOTHING" and not self.press

    def set_initial_brush(self):
        self.target_brush = TILA_Brush(
            self.relative_asset_identifier,
            self.asset_library_type,
            self.asset_library_identifier,
            force_strength=self.force_strength,
            strength=self.strength if self.force_strength else -1.0,
            force_weight=self.force_weight,
            weight=self.weight if self.force_weight else -1.0,
        )

        self.default_brush = TILA_Brush(
            self.default_relative_asset_identifier,
            self.default_asset_library_type,
            self.default_asset_library_identifier,
            strength=self.default_strength,
            weight=self.default_weight,
        )

        self.previous_brush = TILA_Brush(
            bpy.context.window_manager.tila_previous_brush.relative_asset_identifier,
            bpy.context.window_manager.tila_previous_brush.asset_library_type,
            bpy.context.window_manager.tila_previous_brush.asset_library_identifier,
            strength=bpy.context.window_manager.tila_previous_brush.strength,
            weight=bpy.context.window_manager.tila_previous_brush.weight,
        )

        self.current_brush = TILA_Brush(
            self.current_tool.brush_asset_reference.relative_asset_identifier,
            self.current_tool.brush_asset_reference.asset_library_type,
            self.current_tool.brush_asset_reference.asset_library_identifier,
            strength=self.current_tool.brush.strength,
            weight=self.current_tool.brush.weight,
        )

    def store_previous_brush(
        self, relative_asset_identifier, asset_library_type, asset_library_identifier, strength, weight
    ):
        bpy.context.window_manager.tila_previous_brush.relative_asset_identifier = relative_asset_identifier
        bpy.context.window_manager.tila_previous_brush.asset_library_type = asset_library_type
        bpy.context.window_manager.tila_previous_brush.asset_library_identifier = asset_library_identifier
        bpy.context.window_manager.tila_previous_brush.strength = strength
        bpy.context.window_manager.tila_previous_brush.weight = weight

    def set_brush_settings(self, brush: TILA_Brush):
        self.store_previous_brush(
            self.current_tool.brush_asset_reference.relative_asset_identifier,
            self.current_tool.brush_asset_reference.asset_library_type,
            self.current_tool.brush_asset_reference.asset_library_identifier,
            self.current_tool.brush.strength,
            self.current_tool.brush.weight,
        )
        brush.activate()

        if self.force_strength and brush.force_strength:
            self.current_tool.brush.strength = self.strength
        elif brush == self.default_brush and brush == self.current_brush:
            self.current_tool.brush.strength = self.previous_brush.strength

        if self.force_weight and brush.force_weight:
            self.current_tool.brush.weight = self.weight
        elif brush == self.default_brush and brush == self.current_brush:
            self.current_tool.brush.weight = self.previous_brush.weight

        self.brush_is_set = True

    def run_tool(self, brush: TILA_Brush):
        try:
            if self.mode not in compatible_modes:
                return {"CANCELLED"}

            if not self.brush_is_set:
                if brush == self.current_brush:
                    brush = self.previous_brush
                    brush.force_strength = self.force_strength
                    brush.force_weight = self.force_weight
                elif brush == self.default_brush and self.current_brush == self.default_brush:
                    brush = self.previous_brush
                    brush.force_strength = self.force_strength
                    brush.force_weight = self.force_weight
                elif brush == self.previous_brush:
                    brush = self.default_brush
                    brush.force_strength = self.force_strength
                    brush.force_weight = self.force_weight

                self.set_brush_settings(brush)

            if self.toggle_back_on_release:
                if self.mode == "SCULPT":
                    if brush != self.default_brush:
                        bpy.ops.sculpt.brush_stroke("INVOKE_DEFAULT")

                elif self.mode == "VERTEX":
                    if brush != self.default_brush:
                        bpy.ops.paint.vertex_paint("INVOKE_DEFAULT")

                elif self.mode == "WEIGHT":
                    if brush != self.default_brush:
                        bpy.ops.paint.weight_paint("INVOKE_DEFAULT")

                elif self.mode == "IMAGE":
                    if brush != self.default_brush:
                        bpy.ops.paint.image_paint("INVOKE_DEFAULT")

                elif self.mode == "PAINT_GREASE_PENCIL":
                    if brush != self.default_brush:
                        bpy.ops.grease_pencil.brush_stroke("INVOKE_DEFAULT")

                elif self.mode == "SCULPT_GREASE_PENCIL":
                    if brush != self.default_brush:
                        bpy.ops.grease_pencil.sculpt_paint("INVOKE_DEFAULT")

                elif self.mode == "WEIGHT_GREASE_PENCIL":
                    if brush != self.default_brush:
                        bpy.ops.grease_pencil.weight_brush_stroke("INVOKE_DEFAULT")

                elif self.mode == "VERTEX_GREASE_PENCIL":
                    if brush != self.default_brush:
                        bpy.ops.grease_pencil.vertex_brush_stroke("INVOKE_DEFAULT")

                elif self.mode == "SCULPT_CURVES":
                    if brush != self.default_brush:
                        bpy.ops.sculpt_curves.brush_stroke("INVOKE_DEFAULT")

        except RuntimeError as e:
            print("Runtime Error :\n{}".format(e))

    def modal(self, context, event):
        if event.type in {"ESC"}:  # Cancel
            self.brush_is_set = False
            self.run_tool(self.default_brush)
            self.brush_is_set = False
            return {"CANCELLED"}
        elif self.get_release_condition(event=event):
            self.press = False
            self.brush_is_set = False
            self.run_tool(self.default_brush)
            self.brush_is_set = False
            return {"FINISHED"}
        elif self.get_run_condition(event=event):
            self.press = True
            self.run_tool(self.target_brush)
        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        self._current_tool = None
        if self.mode in compatible_modes:
            self.set_initial_brush()
            if self.toggle_back_on_release:
                context.window_manager.modal_handler_add(self)
                return {"RUNNING_MODAL"}
            else:
                self.run_tool(self.target_brush)
                self.brush_is_set = False
                return {"FINISHED"}
        else:
            return {"FINISHED"}


classes = (TILA_Brush_toggle, TILA_PG_Brush)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.WindowManager.tila_previous_brush = bpy.props.PointerProperty(name="Previous Brush", type=TILA_PG_Brush)


def unregister():

    del bpy.types.WindowManager.tila_previous_brush

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
