
import bpy
from bpy.props import IntProperty

from .grouping_scheme import GroupingSchemeAccess


# --------------------- GENERAL ---------------------

class SetPropPropertiesMixin:

    value : IntProperty(
        name='Value',
        description='',
        default=0)


class UVPM3_OT_SetPropBase(bpy.types.Operator):

    def execute(self, context):
        target = self.get_target_obj(context)

        if target is None:
            return {'CANCELLED'}

        setattr(target, self.PROP_ID, self.value)
        return {'FINISHED'}


class UVPM3_MT_SetPropBase(bpy.types.Menu):

    def draw(self, context):
        layout = self.layout

        for entry in self.VALUES:
            if isinstance(entry, tuple):
                value, label = entry
            else:
                value = entry
                label = str(entry)

            operator = layout.operator(self.OPERATOR_IDNAME, text=label)
            operator.value = value


class ScenePropsTargetObjMixin:

    def get_target_obj(self, context):
        scene_props = context.scene.uvpm3_props
        return scene_props


class GroupOverridesTargetObjMixin(GroupingSchemeAccess):

    def get_target_obj(self, context):
        self.init_access(context)
        active_group = self.get_active_group()

        if active_group is None:
            return None

        return active_group.overrides


# --------------------- ROT STEP ---------------------

class UVPM3_OT_SetRotStepBase(UVPM3_OT_SetPropBase):

    bl_label = 'Set Rotation Step'
    bl_description = "Set Rotation Step to one of the suggested values"
    PROP_ID = 'rotation_step'
    

class UVPM3_OT_SetRotStepScene(UVPM3_OT_SetRotStepBase, ScenePropsTargetObjMixin, SetPropPropertiesMixin):

    bl_idname = 'uvpackmaster3.set_rot_step_scene'

    

class UVPM3_OT_SetRotStepGroup(UVPM3_OT_SetRotStepBase, GroupOverridesTargetObjMixin, SetPropPropertiesMixin):

    bl_idname = 'uvpackmaster3.set_rot_step_group'

    


class UVPM3_MT_SetRotStepBase(UVPM3_MT_SetPropBase):

    VALUES = [1, 2, 3, 5, 6, 9, 10, 15, 18, 30, 45, 90, 180]


class UVPM3_MT_SetRotStepScene(UVPM3_MT_SetRotStepBase):

    bl_idname = "UVPM3_MT_SetRotStepScene"
    bl_label = "Set Rotation Step"

    OPERATOR_IDNAME = UVPM3_OT_SetRotStepScene.bl_idname


class UVPM3_MT_SetRotStepGroup(UVPM3_MT_SetRotStepBase):

    bl_idname = "UVPM3_MT_SetRotStepGroup"
    bl_label = "Set Rotation Step"

    OPERATOR_IDNAME = UVPM3_OT_SetRotStepGroup.bl_idname



# --------------------- TEX SIZE ---------------------

class UVPM3_OT_SetPixelMarginTexSizeBase(UVPM3_OT_SetPropBase):

    bl_label = 'Set Texture Size'
    bl_description = "Set Texture Size to one of the suggested values"
    PROP_ID = 'pixel_margin_tex_size'
    

class UVPM3_OT_SetPixelMarginTexSizeScene(UVPM3_OT_SetPixelMarginTexSizeBase, ScenePropsTargetObjMixin, SetPropPropertiesMixin):

    bl_idname = 'uvpackmaster3.set_pixel_margin_tex_size_scene'


    
class UVPM3_OT_SetPixelMarginTexSizeGroup(UVPM3_OT_SetPixelMarginTexSizeBase, GroupOverridesTargetObjMixin, SetPropPropertiesMixin):

    bl_idname = 'uvpackmaster3.set_pixel_margin_tex_size_group'

    

class UVPM3_MT_SetPixelMarginTexSizeBase(UVPM3_MT_SetPropBase):

    VALUES = [
        16,
        32,
        64,
        128,
        256,
        512,
        (1024, '1K'),
        (2048, '2K'),
        (4096, '4K'),
        (8192, '8K'),
        (16384,'16K')]


class UVPM3_MT_SetPixelMarginTexSizeScene(UVPM3_MT_SetPixelMarginTexSizeBase):

    bl_idname = "UVPM3_MT_SetPixelMarginTexSizeScene"
    bl_label = "Set Texture Size"

    OPERATOR_IDNAME = UVPM3_OT_SetPixelMarginTexSizeScene.bl_idname


class UVPM3_MT_SetPixelMarginTexSizeGroup(UVPM3_MT_SetPixelMarginTexSizeBase):

    bl_idname = "UVPM3_MT_SetPixelMarginTexSizeGroup"
    bl_label = "Set Texture Size"

    OPERATOR_IDNAME = UVPM3_OT_SetPixelMarginTexSizeGroup.bl_idname
