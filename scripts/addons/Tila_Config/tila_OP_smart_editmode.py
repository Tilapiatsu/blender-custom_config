
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy
bl_info = {
    "name": "Smart Edit Mode",
    "description": "Automatically switch to edit mode when selecting vertex, edge or polygon mode",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}


class TILA_smart_editmode(bpy.types.Operator):
    bl_idname = "view3d.tila_smart_editmode"
    bl_label = "Smart Edit Mode"

    type = bpy.props.StringProperty(name="type", default='VERT')
    use_extend = bpy.props.BoolProperty(name='use_extend', default=False)
    use_expand = bpy.props.BoolProperty(name='use_expand', default=False)

    def modal(self, context, event):
        pass

    def invoke(self, context, event):
        if bpy.context.mode in [ 'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_TEXT']:
            bpy.ops.object.editmode_toggle()
        else:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.type)

        return {'FINISHED'}
 
classes = (
    TILA_smart_editmode
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
