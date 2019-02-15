
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy
bl_info = {
    "name": "Isolate",
    "description": "contextual Isolate function that work in object and edit mode",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}


class TILA_isolate(bpy.types.Operator):
    bl_idname = "view3d.tila_isolate"
    bl_label = "Isolate"

    force_object_isolate = bpy.props.BoolProperty(name='force_object_isolate', default=False)

    is_isolated = False
    isolated_items = []

    def modal(self, context, event):
        pass

    def isolate(self, isolate=None, reveal=None):
        if len(self.selected_objects) == 0 or self.is_isolated:
            reveal()
            self.is_isolated = False
            self.isolated_items = []
        else:
            isolate(unselected=True)
            self.is_isolated = True
            self.isolated_items.append(self.selected_objects)

    def invoke(self, context, event):
        self.selected_objects = bpy.context.selected_objects
        if context.space_data.type == 'VIEW_3D':

            if bpy.context.mode == 'OBJECT':
                self.isolate(isolate=bpy.ops.object.hide_view_set, reveal=bpy.ops.object.hide_view_clear)
            elif bpy.context.mode in ['EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE']:
                self.isolate(isolate=bpy.ops.mesh.hide, reveal=bpy.ops.mesh.reveal)
            elif bpy.context.mode in ['PAINT_GPENCIL', 'EDIT_GPENCIL', 'SCULPT_GPENCIL']:
                pass

        if context.space_data.type == 'OUTLINER':
            pass

        return {'FINISHED'}


classes = (
    TILA_isolate
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
