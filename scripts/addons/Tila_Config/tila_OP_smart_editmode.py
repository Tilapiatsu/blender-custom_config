
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
    gpencil_mode = ['POINT', 'STROKE', 'SEGMENT']

    def modal(self, context, event):
        pass

    def invoke(self, context, event):
        def switch_mesh_mode(self, current_mode):
            if self.mesh_mode[self.mode] == current_mode:
                bpy.ops.object.editmode_toggle()
            else:
                bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

        def switch_gpencil_mode(self, current_mode):
            if self.gpencil_mode[self.mode] == current_mode:
                bpy.ops.gpencil.editmode_toggle()
            else:
                bpy.context.scene.tool_settings.gpencil_selectmode = self.gpencil_mode[self.mode]

        if bpy.context.mode == 'OBJECT':
            if bpy.context.active_object is None:
                return {'CANCELED'}
            if bpy.context.active_object.type == 'MESH':
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

            elif bpy.context.active_object.type == 'GPENCIL':
                if self.alt_mode:
                    bpy.ops.gpencil.paintmode_toggle()
                else:
                    bpy.ops.gpencil.editmode_toggle()
                    bpy.context.scene.tool_settings.gpencil_selectmode = self.gpencil_mode[self.mode]

        elif bpy.context.mode == 'EDIT_MESH':
            if self.alt_mode:
                bpy.ops.object.editmode_toggle()
            else:
                if bpy.context.scene.tool_settings.mesh_select_mode[0]:
                    switch_mesh_mode(self, 'VERT')
                elif bpy.context.scene.tool_settings.mesh_select_mode[1]:
                    switch_mesh_mode(self, 'EDGE')
                elif bpy.context.scene.tool_settings.mesh_select_mode[2]:
                    switch_mesh_mode(self, 'FACE')

        elif bpy.context.mode in ['EDIT_GPENCIL', 'PAINT_GPENCIL', 'SCULPT_GPENCIL', 'WEIGHT_GPENCIL']:
            if self.alt_mode:
                bpy.ops.gpencil.paintmode_toggle()
            else:
                switch_gpencil_mode(self, bpy.context.scene.tool_settings.gpencil_selectmode)
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
