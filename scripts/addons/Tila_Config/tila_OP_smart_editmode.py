
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

    mode = bpy.props.IntProperty(name='mode', default=0)
    use_extend = bpy.props.BoolProperty(name='use_extend', default=False)
    use_expand = bpy.props.BoolProperty(name='use_expand', default=False)
    alt_mode = bpy.props.BoolProperty(name='alt_mode', default=False)

    mesh_mode = ['VERT', 'EDGE', 'FACE']
    gpencile_mode = ['POINT', 'STROKE', 'SEGMENT']

    def modal(self, context, event):
        pass

    def invoke(self, context, event):
        def switch_mesh_mode(self, current_mode):
            if self.mesh_mode[self.mode] == current_mode:
                bpy.ops.object.editmode_toggle()
            else:
                bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

        def switch_gpencil_mode(self, current_mode):
            if self.gpencile_mode[self.mode] == current_mode:
                bpy.ops.object.editmode_toggle()
            else:
                bpy.ops.gpencil.selectmode_toggle(mode=self.mesh_mode[self.mode])

        if bpy.context.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()

            if bpy.context.active_object.type == 'MESH':
                bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

            elif bpy.context.active_object.type == 'GPENCIL':
                if self.alt_mode:
                    bpy.ops.gpencil.paintmode_toggle()
                else:
                    bpy.ops.gpencil.editmode_toggle()

        elif bpy.context.mode == 'EDIT_MESH':
            if self.alt_mode:
                bpy.ops.object.editmode_toggle()
            else:
                if bpy.context.scene.tool_settings.mesh_select_mode[0]:
                    switch_mesh_mode(self, 'VERT')
                if bpy.context.scene.tool_settings.mesh_select_mode[1]:
                    switch_mesh_mode(self, 'EDGE')
                if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                    switch_mesh_mode(self, 'FACE')

        elif bpy.context.mode in ['EDIT_GPENCIL']:
            if self.alt_mode:
                bpy.ops.gpencil.editmode_toggle()
            else:
                if bpy.context.scene.tool_settings.gpencil_selectmode == 'POINT':
                    switch_gpencil_mode(self, 'POINT')
                if bpy.context.scene.tool_settings.gpencil_selectmode == 'STROKE':
                    switch_gpencil_mode(self, 'STROKE')
                if bpy.context.scene.tool_settings.gpencil_selectmode == 'SEGMENT':
                    switch_gpencil_mode(self, 'SEGMENT')
        else:
            bpy.ops.object.editmode_toggle()

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
