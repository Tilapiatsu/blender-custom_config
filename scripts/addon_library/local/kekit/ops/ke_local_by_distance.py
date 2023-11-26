import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty
from .._utils import get_distance


class KeLocalByDistance(Operator):
    bl_idname = "object.ke_local_by_distance"
    bl_label = "Local Mode by Distance"
    bl_description = "Include objects in Local Mode by distance to selected object"
    bl_options = {'REGISTER', 'UNDO'}

    distance: FloatProperty(
        name="Distance",
        min=0,
        max=9999,
        default=4.0
    )
    type: BoolProperty(
        name="Same Type Only",
        default=False
    )
    invert: BoolProperty(
        name="Invert Range",
        default=False
    )
    frame: BoolProperty(
        name="Frame View",
        default=False
    )

    def execute(self, context):

        if context.space_data.local_view:
            bpy.ops.view3d.localview()

        sel_obj = context.object
        objects = context.scene.objects
        reselect = [o for o in context.selected_objects]

        if self.type:
            objects = [i for i in objects if i.type == sel_obj.type]
        selected = []

        for o in objects:
            d = get_distance(sel_obj.location, o.location)
            if self.invert:
                if d >= self.distance:
                    o.select_set(True)
                    selected.append(o)
            else:
                if d <= self.distance:
                    o.select_set(True)
                    selected.append(o)

        bpy.ops.view3d.localview(frame_selected=self.frame)

        for o in selected:
            o.select_set(False)
        for o in reselect:
            o.select_set(True)

        return {"FINISHED"}
