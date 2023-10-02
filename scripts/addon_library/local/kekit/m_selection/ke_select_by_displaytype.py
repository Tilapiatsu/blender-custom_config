from bpy.props import StringProperty
from bpy.types import Operator
from .._utils import get_prefs


class KeSelectByDisplayType(Operator):
    bl_idname = "object.ke_select_by_displaytype"
    bl_label = "Select by Display Type"
    bl_description = "Select objects in scene by viewport display type"
    bl_options = {'REGISTER', 'UNDO'}

    dt : StringProperty(name="Display Type", default="BOUNDS", options={"HIDDEN"})

    def execute(self, context):
        k = get_prefs()
        ac = k.sel_type_coll
        ac_objects = []
        ac_check = True
        if ac:
            ac_objects = [o for o in context.view_layer.active_layer_collection.collection.objects]

        dt_is_bounds = False
        bounds = ['CAPSULE', 'CONE', 'CYLINDER', 'SPHERE', 'BOX']
        if self.dt in bounds:
            dt_is_bounds = True

        for o in context.scene.objects:
            if ac:
                ac_check = True if o in ac_objects else False
            if o.visible_get() and ac_check:
                if dt_is_bounds and o.display_type == 'BOUNDS':
                    if o.display_bounds_type == self.dt:
                        o.select_set(True)
                else:
                    if o.display_type == self.dt:
                        o.select_set(True)

        return {'FINISHED'}
