import bpy
import mathutils
from time import time
from bpy.types import Panel


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def get_registered_references_name(context) -> list:
    return [r.reference.name for r in context.scene.tila_opacity_controled_references]


class TILA_ReferenceObjectItem(bpy.types.PropertyGroup):
    reference: bpy.props.PointerProperty(name="Reference Object", type=bpy.types.Object)


class TILA_OBJECT_PT_RegisterOpacityControl(Panel):
    bl_label = "Global Opacity Control"
    bl_idname = "OBJECT_PT_GlobalOpacityControl"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (
            context.object.type == "EMPTY" and context.object.data is not None and context.object.data.type == "IMAGE"
        )

    def draw(self, context):
        layout = self.layout

        if context.object.name not in get_registered_references_name(context):
            layout.operator("object.tila_register_opacity_control_object")
        else:
            layout.operator("object.tila_unregister_opacity_control_object")


class TILA_RegisterOpacityControlObjectOperator(bpy.types.Operator):
    bl_idname = "object.tila_register_opacity_control_object"
    bl_label = "Register Reference"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object.name not in get_registered_references_name(context)

    def execute(self, context):
        for o in context.selected_objects:
            if o.name in get_registered_references_name(context):
                continue
            ref = context.scene.tila_opacity_controled_references.add()
            ref.reference = bpy.data.objects.get(o.name)

        return {"FINISHED"}


class TILA_UnRegisterOpacityControlObjectOperator(bpy.types.Operator):
    bl_idname = "object.tila_unregister_opacity_control_object"
    bl_label = "UnRegister Reference"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object.name in get_registered_references_name(context)

    def execute(self, context):
        for o in context.selected_objects:
            if o.name not in get_registered_references_name(context):
                continue
            index = find_reference_in_collection(context, bpy.data.objects[o.name])
            if index == -1:
                continue
            context.scene.tila_opacity_controled_references.remove(index)

        return {"FINISHED"}


def find_reference_in_collection(context, reference_object: bpy.types.Object) -> int:
    for i, r in enumerate(context.scene.tila_opacity_controled_references):
        if reference_object == r.reference:
            return i

    return -1


class TILA_SetRefImagesOpacityOperator(bpy.types.Operator):
    bl_idname = "view3d.tila_set_ref_images_opacity"
    bl_label = "Set Reference Images Opacity"
    bl_options = {"REGISTER"}

    force_opacity: bpy.props.BoolProperty(name="Force Opacity", default=True)

    def store_opacity_state(self, context) -> None:
        self.opacity_state = []
        for r in context.scene.tila_opacity_controled_references:
            self.opacity_state.append(r.reference.use_empty_image_alpha)
            r.reference.use_empty_image_alpha = True

    def reset_opacity_state(self, context) -> None:
        for i, r in enumerate(context.scene.tila_opacity_controled_references):
            r.reference.use_empty_image_alpha = self.opacity_state[i]

    def set_opacity_value(self, context, value: float) -> None:
        for r in context.scene.tila_opacity_controled_references:
            r.reference.color[3] = clamp(r.reference.color[3] + value, 0, 1)

    def execute(self, context):
        self.reset_opacity_state(context)
        return {"FINISHED"}

    def modal(self, context, event):
        if event.type in {"MOUSEMOVE"}:
            # Get current mouse coordination (region)
            self.pos_current = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
            self.opacity_offset = ((self.pos_current - self.initial_pos) / self.sensitivity).x
            self.set_opacity_value(context, self.opacity_offset)
            self.initial_pos = self.pos_current

        if event.type in {self.input_type, "LEFTMOUSE"} and event.value == "RELEASE":
            self.execute(context)
            return {"FINISHED"}

        if event.type == "ESC":  # Cancel
            self.execute(context)
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        self.current_area = context.area
        self.input_type = event.type
        self.hud = True
        self.use_view_center = True
        self.opacity_state = []
        self.opacity_offset = 0.0
        self.sensitivity = 100

        if self.force_opacity:
            self.store_opacity_state(context)

        # Get current mouse coordination
        self.pos_current = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))

        self.initial_pos = self.pos_current  # for draw debug, else no need

        self.timer = time()
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


### --- REGISTER

classes = (
    TILA_ReferenceObjectItem,
    TILA_RegisterOpacityControlObjectOperator,
    TILA_UnRegisterOpacityControlObjectOperator,
    TILA_OBJECT_PT_RegisterOpacityControl,
    TILA_SetRefImagesOpacityOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.tila_registered_opacity_control = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.tila_opacity_controled_references = bpy.props.CollectionProperty(type=TILA_ReferenceObjectItem)


def unregister():
    del bpy.types.Scene.tila_opacity_controled_references
    del bpy.types.Object.tila_registered_opacity_control

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
