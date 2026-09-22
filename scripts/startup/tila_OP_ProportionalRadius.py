bl_info = {
    "name": "Proportional Radius Adjuster",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (4, 3, 0),
    "location": "3D View",
    "description": ("Adjust Blender's proportional editing radius independently using a mouse-drag modal operator."),
    "category": "3D View",
}

import bpy
import gpu
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

MIN_RADIUS = 1e-5
MAX_RADIUS = 5000.0

# Number of horizontal pixels required for a 100% radius change.
# Lower = faster.
PIXELS_PER_RADIUS = 200.0

# Circle appearance.
CIRCLE_SEGMENTS = 96
CIRCLE_LINE_WIDTH = 2.0


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------


def _world_radius_to_screen_radius(
    region,
    region_3d,
    mouse_xy,
    world_radius,
):
    """
    Estimate how many screen pixels correspond to `world_radius`
    at the mouse position.

    We use the view's projection by sampling points on a view-facing
    plane at the mouse depth.
    """

    if world_radius <= 0.0:
        return 0.0

    mouse = Vector(mouse_xy)

    # Obtain a 3D point at the depth represented by the mouse position.
    #
    # The view distance itself is not a useful depth here, so use the
    # region's view center as a stable reference.
    depth_location = region_3d.view_location.copy()

    center_3d = view3d_utils.region_2d_to_location_3d(
        region,
        region_3d,
        mouse,
        depth_location,
    )

    # Find the screen-space displacement corresponding to the desired
    # world-space radius using binary search.
    #
    # This is preferable to using region_3d.view_distance directly,
    # especially with perspective views.
    low = 0.0
    high = 4096.0

    for _ in range(24):
        mid = (low + high) * 0.5

        sample_xy = Vector((mouse.x + mid, mouse.y))

        sample_3d = view3d_utils.region_2d_to_location_3d(
            region,
            region_3d,
            sample_xy,
            depth_location,
        )

        distance = (sample_3d - center_3d).length

        if distance < world_radius:
            low = mid
        else:
            high = mid

    return (low + high) * 0.5


def draw_circle(operator, context):
    """Draw the proportional radius circle around the mouse."""

    if operator.mouse_position is None:
        return

    region = context.region
    space = context.space_data

    if not space or space.type != "VIEW_3D":
        return

    region_3d = space.region_3d

    mouse = Vector(operator.mouse_position)

    radius_px = _world_radius_to_screen_radius(
        region,
        region_3d,
        mouse,
        operator.current_radius,
    )

    # Prevent the circle from becoming invisible or ridiculously large.
    radius_px = max(2.0, min(radius_px, 10000.0))

    points = []

    for i in range(CIRCLE_SEGMENTS + 1):
        angle = (i / CIRCLE_SEGMENTS) * 6.283185307179586

        x = mouse.x + radius_px * __import__("math").cos(angle)
        y = mouse.y + radius_px * __import__("math").sin(angle)

        points.append((x, y))

    shader = gpu.shader.from_builtin("UNIFORM_COLOR")

    batch = batch_for_shader(
        shader,
        "LINE_STRIP",
        {
            "pos": points,
        },
    )

    gpu.state.blend_set("ALPHA")
    gpu.state.line_width_set(CIRCLE_LINE_WIDTH)

    shader.bind()

    # Orange-ish neutral viewport indicator.
    shader.uniform_float(
        "color",
        (0.0, 0.65, 0.9, 0.7),
    )

    batch.draw(shader)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set("NONE")


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------


class VIEW3D_OT_adjust_proportional_radius(bpy.types.Operator):
    bl_idname = "view3d.adjust_proportional_radius"
    bl_label = "Adjust Proportional Radius"
    bl_description = "Adjust proportional editing radius by dragging the mouse"
    bl_options = {"REGISTER", "UNDO"}

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    start_mouse_x: int
    start_radius: float
    current_radius: float

    mouse_position = None

    _draw_handle = None
    _area = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_radius(self, context, event):
        """
        Update the proportional radius from horizontal mouse movement.
        """

        dx = event.mouse_x - self.start_mouse_x

        # Base change.

        change = dx / PIXELS_PER_RADIUS

        # Precision / boost.

        if event.shift:
            change *= 0.5

        if event.ctrl:
            change *= 2.0

        new_radius = self.start_radius + change

        new_radius = max(
            MIN_RADIUS,
            min(MAX_RADIUS, new_radius),
        )

        self.current_radius = new_radius

        context.scene.tool_settings.proportional_distance = new_radius

    # ------------------------------------------------------------------
    # Invoke
    # ------------------------------------------------------------------

    def invoke(self, context, event):

        if context.area.type != "VIEW_3D":
            self.report(
                {"WARNING"},
                "This operator can only be used in the 3D View",
            )
            return {"CANCELLED"}

        tool_settings = context.scene.tool_settings

        self.start_radius = tool_settings.proportional_distance
        self.current_radius = self.start_radius

        self.start_mouse_x = event.mouse_x

        self.mouse_position = (
            event.mouse_region_x,
            event.mouse_region_y,
        )

        self._area = context.area

        # Add viewport draw callback.
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_circle,
            (self, context),
            "WINDOW",
            "POST_PIXEL",
        )

        context.window_manager.modal_handler_add(self)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}

    # ------------------------------------------------------------------
    # Modal
    # ------------------------------------------------------------------

    def modal(self, context, event):

        # Keep the draw callback alive only while this operator is active.
        if context.area:
            context.area.tag_redraw()

        # --------------------------------------------------------------
        # Mouse movement
        # --------------------------------------------------------------

        if event.type == "MOUSEMOVE":
            self.mouse_position = (
                event.mouse_region_x,
                event.mouse_region_y,
            )

            self._update_radius(context, event)

            return {"RUNNING_MODAL"}

        # --------------------------------------------------------------
        # Confirm
        # --------------------------------------------------------------

        if event.value == "RELEASE":
            self._finish(context)

            return {"FINISHED"}

        # --------------------------------------------------------------
        # Cancel
        # --------------------------------------------------------------

        if (
            event.type
            in {
                "RIGHTMOUSE",
                "ESC",
            }
            and event.value == "PRESS"
        ):
            context.scene.tool_settings.proportional_distance = self.start_radius

            self._finish(context)

            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    # ------------------------------------------------------------------
    # Finish
    # ------------------------------------------------------------------

    def _finish(self, context):

        if self._draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(
                self._draw_handle,
                "WINDOW",
            )

            self._draw_handle = None

        if context.area:
            context.area.tag_redraw()

    def cancel(self, context):

        context.scene.tool_settings.proportional_distance = self.start_radius

        self._finish(context)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (VIEW3D_OT_adjust_proportional_radius,)


addon_keymaps = []


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    # --------------------------------------------------------------
    # Example shortcut
    #
    # F is intentionally used here as an example. The operator will
    # also appear in Blender's keymap search, so the user can replace
    # this shortcut through Preferences > Keymap.
    # --------------------------------------------------------------

    # wm = bpy.context.window_manager
    #
    # kc = wm.keyconfigs.addon
    #
    # if kc:
    #     km = kc.keymaps.new(
    #         name="3D View",
    #         space_type="VIEW_3D",
    #     )
    #
    #     kmi = km.keymap_items.new(
    #         VIEW3D_OT_adjust_proportional_radius.bl_idname,
    #         type="Q",
    #         value="PRESS",
    #     )
    #
    #     addon_keymaps.append((km, kmi))


def unregister():

    # Remove keymaps.

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()

    # Remove classes.

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
