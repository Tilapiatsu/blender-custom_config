

import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty, PointerProperty



class UVPM3_OT_BrowseGroupingSchemes(bpy.types.Operator):
    bl_options = {'INTERNAL'}
    bl_idname = 'uvpackmaster3.browse_grouping_schemes'
    bl_label = 'Browse Grouping Schemes'
    bl_description = "Browse Grouping Schemes"

    active_grouping_scheme_idx : IntProperty(name='', description='', default=0)

    def execute(self, context):
        scene_props = context.scene.uvpm3_props
        scene_props.active_grouping_scheme_idx = self.active_grouping_scheme_idx
        return {'FINISHED'}


class UVPM3_MT_BrowseGroupingSchemes(bpy.types.Menu):
    bl_idname = "UVPM3_MT_BrowseGroupingSchemes"
    bl_label = "Grouping Schemes"

    def draw(self, context):
        grouping_schemes = context.scene.uvpm3_props.grouping_schemes

        enumerated_grouping_schemes = list(enumerate(grouping_schemes))
        enumerated_grouping_schemes.sort(key=lambda i: i[1].name)

        layout = self.layout
        for idx, grouping_scheme in enumerated_grouping_schemes:
            operator = layout.operator(UVPM3_OT_BrowseGroupingSchemes.bl_idname, text=grouping_scheme.name)
            operator.active_grouping_scheme_idx = idx


class UVPM3_UL_GroupInfo(bpy.types.UIList):
    bl_idname = 'UVPM3_UL_GroupInfo'

    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname, _index):
        group_info = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.2)
            split.prop(group_info, "color", text="", emboss=True)
            row = split.row().split(factor=0.8)
            row.prop(group_info, "name", text="", emboss=False)
            row.label(text="[D]" if group_info.is_default() else "   ")

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class UVPM3_UL_TargetBoxes(bpy.types.UIList):
    bl_idname = 'UVPM3_UL_TargetBoxes'
    
    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname, _index):
        target_box = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text="Box {}: {}".format(_index, target_box.label()))

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
