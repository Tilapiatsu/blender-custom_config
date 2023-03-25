import bpy, os, re
from ..utils import (
get_item_scene,
)

def convert_items_to_dic(self, context):
    props = bpy.context.scene.rentask
    colle = props.rentask_colle
    cmd_dic = {}

    for item in colle:
        if not item.use_render:
            continue
        if not item.blendfile:
            continue

        tgt_sc = get_item_scene(item)
        item_option_dic = {}

        for key in item.keys():
            item_option_dic[key] = getattr(item,key)
        item_option_dic["__end_processing_type__"] = props.rentask_main.end_processing_type

        cmd_dic[item.name] = item_option_dic

    return cmd_dic
