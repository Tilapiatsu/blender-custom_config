import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, EnumProperty
from .._utils import set_active_collection


class KeEmptyParent(Operator):
    bl_idname = "object.ke_emptyparent"
    bl_label = "EmptyParent"
    bl_description = "Parent objects to a new Empty object (options in redo panel)"
    bl_options = {'REGISTER', 'UNDO'}

    children: EnumProperty(
        items=[("SEL", "Selected", "EmptyParent selected Objects", 1),
               ("COL", "Collection", "EmptyParent ALL objects in the Active Obj's (1st) collection", 2)],
        name="Children", default="SEL")

    parent_pos: EnumProperty(
        items=[("ACTIVE", "Active", "EmptyParent at Active Obj Origin", 1),
               ("CURSOR", "Cursor", "EmptyParent at Cursor", 2),
               ("ORIGO", "Origo", "EmptyParent at Origo (0,0,0)", 3)],
        name="Placement", default="ACTIVE")

    parent_rot: BoolProperty(name="Use Rotation", default=False,
        description="EmptyParent will copy the rotation from Active Obj or Cursor (only)")

    empty_size: FloatProperty(
        name="Size", default=0, min=0, max=99, precision=3,
        description="Display size of the EmptyParent.\n'0' is automatic (0.75 * longest bbox axis, fallback 1m)")

    empty_type: EnumProperty(
        items=[("PLAIN_AXES", "Plain Axes", "", 1),
               ("ARROWS", "Arrows", "", 2),
               ("SINGLE_ARROW", "Single Arrow", "", 3),
               ("CIRCLE", "Circle", "", 4),
               ("CUBE", "Cube", "", 5),
               ("SPHERE", "Sphere", "", 6),
               ("CONE", "Cone", "", 7)],
        name="Display Type", default="PLAIN_AXES")

    parent_type: EnumProperty(
        items=[("STANDARD", "Standard", "Selected objects are parented to EmptyParent", 1),
               ("KEEP", "Keep Transform", "Selected objects are parented to EmptyParent", 2),
               ("NOINVERSE", "No Inverse", "Selected objects are parented to EmptyParent", 3),
               ("KEEPNOINV", "Keep+NoInverse", "Selected objects are parented to EmptyParent", 4)],
        name="Parenting", default="STANDARD")

    @classmethod
    def poll(cls, context):
        return context.active_object

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "children", expand=True)
        layout.prop(self, "parent_pos", expand=True)
        layout.prop(self, "parent_rot", toggle=True)
        layout.prop(self, "empty_type", expand=True)
        layout.prop(self, "empty_size")
        layout.prop(self, "parent_type", expand=True)
        layout.separator()

    def execute(self, context):
        active = context.active_object

        # Size
        if active.type == "MESH":
            bbsize = sorted(active.bound_box.data.dimensions[:])[2] * 0.75
        else:
            bbsize = 1

        # Size override
        if round(self.empty_size, 3) > 0:
            bbsize = self.empty_size

        set_active_collection(context, active)
        active_coll = context.collection
        cursor = context.scene.cursor
        if self.children == "COL":
            sel_obj = active_coll.objects[:] + [active]
        else:
            sel_obj = context.selected_objects[:] + [active]

        empty = bpy.data.objects.new("EmptyParent", None)
        active_coll.objects.link(empty)
        empty.empty_display_size = bbsize
        empty.empty_display_type = self.empty_type

        if self.parent_pos == "ACTIVE":
            empty.location = active.location
            if self.parent_rot:
                empty.rotation_euler = active.rotation_euler
        elif self.parent_pos == "CURSOR":
            empty.location = cursor.location
            if self.parent_rot:
                empty.rotation_euler = cursor.rotation_euler
        # Origo: empty is placed at origo by default

        bpy.ops.object.select_all(action="DESELECT")
        empty.select_set(True)
        context.view_layer.objects.active = empty

        for obj in sel_obj:
            obj.select_set(True)
            if self.parent_type == "KEEP":
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            elif self.parent_type == "NOINVERSE":
                bpy.ops.object.parent_no_inverse_set(keep_transform=False)
            elif self.parent_type == "KEEPNOINV":
                bpy.ops.object.parent_no_inverse_set(keep_transform=True)
            else:
                # STANDARD
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
            obj.select_set(False)

        return {'FINISHED'}
