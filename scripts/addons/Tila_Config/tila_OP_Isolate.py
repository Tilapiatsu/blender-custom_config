
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

    is_isolated=False
    isolated_items=[]

    def modal(self, context, event):
        pass

    def isolate(self, isolate=None, reveal=None):
        if self.active_object is None or self.is_isolated:
            reveal()
        else:
            isolate(unselected=True)
            self.is_isolated=True
            self.isolated_items.append(self.active_object)

    def invoke(self, context, event):
        self.active_object = bpy.context.active_object
        if context.space_data.type == 'VIEW_3D':
            
            if bpy.context.mode == 'OBJECT':
                self.isolate(isolate=bpy.ops.object.hide_view_set, reveal=bpy.ops.object.hide_view_clear)
            elif bpy.context.mode in ['EDIT_MESH','EDIT_CURVE', 'EDIT_SURFACE']:
                pass
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
