import bpy
from bpy.props import *
from bpy.types import UIList
from ..utils import preference


#
class LAZYSHAPEKEYS_UL_sync_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item,"mute",text="",icon="CHECKBOX_DEHLT" if item.mute else "CHECKBOX_HLT",emboss=False)
        row.prop(item,"value",text=item.name,slider=True)
