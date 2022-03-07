import bpy
from bpy.props import *
from bpy.types import PropertyGroup

def update_tgt_colle(self,context):
    if not bpy.context.scene.lazy_shapekeys.tgt_colle:
        return
    bpy.ops.lazy_shapekeys.shape_keys_sync_update()


def update_sync_value(self,context):
    props = bpy.context.scene.lazy_shapekeys
    if not props.tgt_colle:
        return
    for obj in props.tgt_colle.objects:
        if obj.type in {"MESH", "CURVE", "SURFACE","LATTICE"}:
            if obj.data.shape_keys:
                if self.name in obj.data.shape_keys.key_blocks:
                    obj.data.shape_keys.key_blocks[self.name].value = self.value


def update_sync_mute(self,context):
    props = bpy.context.scene.lazy_shapekeys
    if not props.tgt_colle:
        return
    for obj in props.tgt_colle.objects:
        if obj.type in {"MESH", "CURVE", "SURFACE","LATTICE"}:
            if obj.data.shape_keys:
                if self.name in obj.data.shape_keys.key_blocks:
                    obj.data.shape_keys.key_blocks[self.name].mute = self.mute




class LAZYSHAPEKEYS_Props(PropertyGroup):
    # folder_name : StringProperty()
    tgt_colle : PointerProperty(name="Target",type=bpy.types.Collection,update=update_tgt_colle)
    sync_colle_index : IntProperty(min=0)

class LAZYSHAPEKEYS_sync_colle(PropertyGroup):
    name : StringProperty()
    # slider_min : FloatProperty()
    # slider_max : FloatProperty()
    value : FloatProperty(name="Value",update=update_sync_value,min=0,max=1)
    mute : BoolProperty(name="Mute",update=update_sync_mute)
