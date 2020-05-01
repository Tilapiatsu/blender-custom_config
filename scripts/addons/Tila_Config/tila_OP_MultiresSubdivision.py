
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy
bl_info = {
    "name": "Multires Subdivision",
    "description": "Facilitate the use of multires subdivision",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}


class TILA_multires_subdiv_level(bpy.types.Operator):
    bl_idname = "sculpt.tila_multires_subdiv_level"
    bl_label = "TILA : Multires Set Subdivision Level"

    subd = bpy.props.IntProperty(name='subd', default=0)
    relative = bpy.props.BoolProperty(name='relative', default=False)
    force_subd = bpy.props.BoolProperty(name='force_subd', default=False)
    mode = bpy.props.StringProperty(name='mode', default='CATMULL_CLARK')

    multires_modifier = None
    active_object = None
    modifier_name = 'Multires'
    modifier_type = 'MULTIRES'

    def modal(self, context, event):
        pass

    def offset_subdivision(self):
        if self.multires_modifier.render_levels < self.multires_modifier.sculpt_levels + self.subd:
            if self.force_subd:
                bpy.ops.object.multires_subdivide(modifier=self.multires_modifier.name, mode=self.mode)
        elif self.multires_modifier.sculpt_levels + self.subd < 0:
            if self.force_subd:
                try:
                    bpy.ops.object.multires_unsubdivide(modifier=self.multires_modifier.name)
                except RuntimeError:
                    self.report({'INFO'}, 'Tila Multires subdiv : Can\'t unsubdivide more')
                    return {'CANCELLED'}
        else:
            self.multires_modifier.sculpt_levels = self.multires_modifier.sculpt_levels + self.subd

        self.multires_modifier.levels = self.multires_modifier.levels + self.subd

    def set_subdivision(self):
        if self.multires_modifier.render_levels < self.subd:
            if self.force_subd:
                for l in range(self.subd - self.multires_modifier.render_levels):
                    bpy.ops.object.multires_subdivide(modifier=self.multires_modifier.name, mode=self.mode)

        self.multires_modifier.sculpt_levels = self.subd
        self.multires_modifier.levels = self.subd

    def invoke(self, context, event):

        self.active_object = bpy.context.active_object

        if self.active_object is None:
            return {'CANCELLED'}

        self.multires_modifier = [m for m in self.active_object.modifiers if m.type == self.modifier_type]

        if not len(self.multires_modifier):
            self.multires_modifier = self.active_object.modifiers.new(name=self.modifier_name, type=self.modifier_type)
        else:
            self.multires_modifier = self.multires_modifier[0]

        if self.relative:
            self.offset_subdivision()
        else:
            self.set_subdivision()

        return {'FINISHED'}

class TILA_multires_rebuild_subdiv(bpy.types.Operator):
    bl_idname = "sculpt.tila_multires_rebuild_subdiv"
    bl_label = "TILA : Multires Rebuild Subdivision"

    multires_modifier = None
    active_object = None
    modifier_name = 'Multires'
    modifier_type = 'MULTIRES'

    def invoke(self, context, event):

        self.active_object = bpy.context.active_object

        if self.active_object is None:
            return {'CANCELLED'}

        self.multires_modifier = [m for m in self.active_object.modifiers if m.type == self.modifier_type]

        if not len(self.multires_modifier):
            self.multires_modifier = self.active_object.modifiers.new(name=self.modifier_name, type=self.modifier_type)
        else:
            self.multires_modifier = self.multires_modifier[0]

        bpy.ops.object.multires_rebuild_subdiv(modifier=self.multires_modifier.name)

        return {'FINISHED'}

class TILA_multires_delete_subdiv(bpy.types.Operator):
    bl_idname = "sculpt.tila_multires_delete_subdiv"
    bl_label = "TILA : Multires Delete Subdivision"

    delete_target = bpy.props.StringProperty(name='subd', default='HIGHER')

    multires_modifier = None
    active_object = None
    modifier_name = 'Multires'
    modifier_type = 'MULTIRES'
    targets = ['HIGHER', 'LOWER']

    def invoke(self, context, event):

        self.active_object = bpy.context.active_object

        if self.active_object is None or self.delete_target not in self.targets:
            return {'CANCELLED'}

        self.multires_modifier = [m for m in self.active_object.modifiers if m.type == self.modifier_type]

        if not len(self.multires_modifier):
            self.multires_modifier = self.active_object.modifiers.new(name=self.modifier_name, type=self.modifier_type)
        else:
            self.multires_modifier = self.multires_modifier[0]

        if self.delete_target == self.targets[0] and self.multires_modifier.render_levels > 0:
            bpy.ops.object.multires_higher_levels_delete(modifier=self.multires_modifier.name)
        elif self.delete_target == self.targets[1] and self.multires_modifier.levels < self.multires_modifier.render_levels:
            bpy.ops.object.multires_lower_levels_delete(modifier=self.multires_modifier.name)

        return {'FINISHED'}

class TILA_multires_apply_base(bpy.types.Operator):
    bl_idname = "sculpt.tila_multires_apply_base"
    bl_label = "TILA : Multires Apply Base"

    multires_modifier = None
    active_object = None
    modifier_name = 'Multires'
    modifier_type = 'MULTIRES'

    def invoke(self, context, event):

        self.active_object = bpy.context.active_object

        if self.active_object is None:
            return {'CANCELLED'}

        self.multires_modifier = [m for m in self.active_object.modifiers if m.type == self.modifier_type]

        if not len(self.multires_modifier):
            self.multires_modifier = self.active_object.modifiers.new(name=self.modifier_name, type=self.modifier_type)
        else:
            self.multires_modifier = self.multires_modifier[0]

        bpy.ops.object.multires_base_apply(modifier=self.multires_modifier.name)

        return {'FINISHED'}


classes = (
    TILA_multires_subdiv_level,
    TILA_multires_rebuild_subdiv,
    TILA_multires_delete_subdiv,
    TILA_multires_apply_base
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
