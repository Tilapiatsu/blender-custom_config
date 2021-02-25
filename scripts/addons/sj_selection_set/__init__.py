# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "SJ Selection Set",
    "description": "Selection Set.",
    "author": "CaptainHansode",
    "version": (1, 0, 3),
    "blender": (2, 80, 0),
    "location":  "View3D > Sidebar > SJT Tab",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Object"
}
# web:  https://sakaiden.com
# twitter: https://twitter.com/CaptainHansode


import bpy
import collections
import json
import random
import copy


def select_current_selset(self, context):
    r"""選択"""
    if len(context.scene.sj_sel_set_items) is 0:
        return None

    index = int(self.selection_set_dplist)
    obj_list = json.loads(
        context.scene.sj_sel_set_items[index].object_list,
        object_pairs_hook=collections.OrderedDict)
    
    if len(obj_list) is 0:
        return None

    bpy.ops.object.select_all(action='DESELECT')
    for obj in obj_list:
        if bpy.context.scene.objects.get(obj):
            bpy.data.objects[obj].select_set(True)

    # 今のオブジェクトをアクティブ化する仕様メンドクサ!
    if bpy.context.scene.objects.get(obj_list[0]):
        context.view_layer.objects.active = bpy.data.objects[obj_list[0]]
    return None


def get_selection_list_items(scene, context):
    r"""セレクションセットのリスト取得"""
    items = []
    # イテレーターで取得
    for i, item in enumerate(context.scene.sj_sel_set_items, 0):
        # items.append((str(i), item.name, ''))
        items.append((str(i), item.set_name, ''))

    if len(items) is 0:
        items.append(('0', 'Selection Set Empty.', ''))

    return items


def get_sel_set_item_name(self):
    return self["set_name"]


def set_sel_set_item_name(self, value):
    self["set_name"] = value
    # 自分以外の名前から検索
    current_names = [i.set_name for i in bpy.context.scene.sj_sel_set_items]
    current_names.remove(value)
    new_name = value
    cnt = 1
    while new_name in current_names:
        new_name = '{}.{:03d}'.format(new_name.split('.')[0], cnt)
        cnt = cnt + 1
    self["set_name"] = new_name
    return None


class SJSelectionSetItem(bpy.types.PropertyGroup):
    r"""Selection set collection item"""
    # 注意デフォルトでもっている値はNameで、selfのキー名はname
    # =で書くのと :で書くので違う
    # Name: bpy.props.StringProperty(
    #     default="SelectionSet",
    #     get=get_sel_set_item_name,
    #     set=set_sel_set_item_name
    #     )
    set_name: bpy.props.StringProperty(
        default="SelectionSet",
        name="Selection set name",
        get=get_sel_set_item_name,
        set=set_sel_set_item_name
        )
    object_list: bpy.props.StringProperty(
        name="Objects in set",
        description="",
        default="")


class SJSelectionSetProperties(bpy.types.PropertyGroup):
    r"""カスタムプロパティを定義する"""
    # selection_set_data: bpy.props.StringProperty(name='', default='{}')
    selection_set_dplist: bpy.props.EnumProperty(
        items=get_selection_list_items,
        name="Selection Set",
        description="Selection Set",
        update=select_current_selset
    )


class SJSelectionSetAddItem(bpy.types.Operator):
    r"""Add new selection set"""
    bl_idname = "sj_selection_set.add_selset"
    bl_label = ""
    bl_description = "Add new selection set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        r""""""
        # 何か選択してないと無効はつかいづらいかも?
        # return bpy.context.selected_objects
        # return bpy.context.active_object is not None
        return True

    def execute(self, context):
        r""""""
        if len(bpy.context.selected_objects) is 0:
            msg = 'Please Select any object.'
            # raiseするとスクリプトエラーっぽく吐かれちゃうからやめる
            # raise Exception("Please Select any object.")
            def draw(self, context):
                self.layout.label(text=msg)
            bpy.context.window_manager.popup_menu(draw, title="Info", icon="INFO")
            self.report({'INFO'}, msg)
            return {'FINISHED'}
        new_item = context.scene.sj_sel_set_items.add()

        # 名前かぶらないようにする
        current_names = [i.set_name for i in context.scene.sj_sel_set_items]
        new_name = 'SelectionSet'
        cnt = 1
        while new_name in current_names:
            new_name = 'SelectionSet.{:03d}'.format(cnt)
            cnt = cnt + 1
        new_item.set_name = new_name

        index = len(context.scene.sj_sel_set_items) - 1
        context.scene.sj_sel_set_item_index = index
        context.scene.sj_sel_set_props.selection_set_dplist = str(index)

        obj_list = [obj.name for obj in bpy.context.selected_objects]
        new_item.object_list = json.dumps(obj_list)

        # ドロップダウンリストを更新 こんなんでいいのかな?
        get_selection_list_items(self, context)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return {'FINISHED'}


class SJSelectionSetDeleteItem(bpy.types.Operator):
    r"""Delete selected set"""
    bl_idname = "sj_selection_set.delete_item"
    bl_label = ""
    bl_description = "Delete selected set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.sj_sel_set_items

    def execute(self, context):
        r""""""
        sjss = context.scene.sj_sel_set_props
        s_list = context.scene.sj_sel_set_items
        index = context.scene.sj_sel_set_item_index
        s_list.remove(index)

        index = min(max(0, index - 1), len(s_list) - 1)
        context.scene.sj_sel_set_item_index = index

        # update
        get_selection_list_items(self, context)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        # if len(s_list) is not 0:  # 更新で選択されちゃうので外す
        #     sjss.selection_set_dplist = str(index)
        return {'FINISHED'}


class SJSelectionSetDeleteItemToolHeaderBt(bpy.types.Operator):
    r"""Delete selected set tool header button"""
    bl_idname = "sj_selection_set.delete_item_toolheader_bt"
    bl_label = ""
    bl_description = "Delete selected set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.sj_sel_set_items

    def execute(self, context):
        r""""""
        sjss = context.scene.sj_sel_set_props
        s_list = context.scene.sj_sel_set_items
        if (len(s_list) is 0) or (sjss.selection_set_dplist == ""):
            return {'FINISHED'}

        index = int(sjss.selection_set_dplist)
        s_list.remove(index)
        
        index = min(max(0, index - 1), len(s_list) - 1)
        context.scene.sj_sel_set_item_index = index
        # update
        get_selection_list_items(self, context)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        # if len(s_list) is not 0:
        #     sjss.selection_set_dplist = str(index)
        return {'FINISHED'}


class SJSelectionSetMoveUpItem(bpy.types.Operator):
    r"""Move Up selected set"""
    bl_idname = "sj_selection_set.move_up_item"
    bl_label = ""
    bl_description = "Move Up selected set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.sj_sel_set_items

    def execute(self, context):
        r""""""
        s_list = context.scene.sj_sel_set_items
        index = context.scene.sj_sel_set_item_index
        list_length = len(context.scene.sj_sel_set_items) - 1
        neighbor = index - 1
        s_list.move(neighbor, index)
        context.scene.sj_sel_set_item_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}


class SJSelectionSetMoveDownItem(bpy.types.Operator):
    r"""Move Down selected set"""
    bl_idname = "sj_selection_set.move_down_item"
    bl_label = ""
    bl_description = "Move Down selected set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.sj_sel_set_items

    def execute(self, context):
        r""""""
        s_list = context.scene.sj_sel_set_items
        index = context.scene.sj_sel_set_item_index
        list_length = len(context.scene.sj_sel_set_items) - 1
        neighbor = index + 1
        s_list.move(neighbor, index)
        context.scene.sj_sel_set_item_index = max(0, min(neighbor, list_length))
        return {'FINISHED'}


class SJSelectionSetClearItem(bpy.types.Operator):
    r"""clear selection set"""
    bl_idname = "sj_selection_set.clear_item"
    bl_label = ""
    bl_description = "Clear all selection set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.sj_sel_set_items

    def execute(self, context):
        r""""""
        context.scene.sj_sel_set_items.clear()
        context.scene.sj_sel_set_props.selection_set_dplist = '0'
        # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        # invoke_confirmだとbl_label入れないとダメっぽい？
        wm = context.window_manager
        # self.bl_label = msg
        # return wm.invoke_confirm(self, event)
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        self.layout.label(text="Clear all selection set?")


class SJSelectionSetAddObjToSet(bpy.types.Operator):
    r"""Add object to selection set"""
    bl_idname = "sj_selection_set.add_obj_to_set"
    bl_label = ""
    bl_description = "Add object to selection set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.sj_sel_set_items

    def execute(self, context):
        r""""""
        if len(bpy.context.selected_objects) is 0:
            return {'FINISHED'}

        index = context.scene.sj_sel_set_item_index
        item = context.scene.sj_sel_set_items[index]
        current_obj_list = copy.copy(json.loads(
            item.object_list,
            object_pairs_hook=collections.OrderedDict))

        select_obj_list = [obj.name for obj in bpy.context.selected_objects if obj.name not in current_obj_list]
        for obj in select_obj_list:
            current_obj_list.append(obj)
        item.object_list = json.dumps(list(set(current_obj_list)))
        return {'FINISHED'}


class SJSelectionSetRemoveObjToSet(bpy.types.Operator):
    r"""Remove object to selection set"""
    bl_idname = "sj_selection_set.remove_obj_to_set"
    bl_label = ""
    bl_description = "Remove object to selection set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.sj_sel_set_items

    def execute(self, context):
        r""""""
        index = context.scene.sj_sel_set_item_index
        item = context.scene.sj_sel_set_items[index]
        current_obj_list = copy.copy(json.loads(
            item.object_list,
            object_pairs_hook=collections.OrderedDict))
        
        new_obj_list = []
        select_obj_list = [obj.name for obj in bpy.context.selected_objects]
        for obj in current_obj_list:    
            if obj in select_obj_list:
                continue
            new_obj_list.append(obj)
        item.object_list = json.dumps(new_obj_list)
        return {'FINISHED'}


class SJSelectionSetSelect(bpy.types.Operator):
    r"""Select objects in selected set"""
    bl_idname = "sj_selection_set.select"
    bl_label = ""
    bl_description = "Select objects in selected set"

    @classmethod
    def poll(cls, context):
        return context.scene.sj_sel_set_items

    def execute(self, context):
        r""""""
        index = context.scene.sj_sel_set_item_index
        obj_list = json.loads(
            context.scene.sj_sel_set_items[index].object_list,
            object_pairs_hook=collections.OrderedDict)

        if len(obj_list) is 0:
            return {'FINISHED'}
        
        bpy.ops.object.select_all(action='DESELECT')
        for obj in obj_list:
            if bpy.context.scene.objects.get(obj):
                bpy.data.objects[obj].select_set(True)

        if bpy.context.scene.objects.get(obj_list[0]):
            context.view_layer.objects.active = bpy.data.objects[obj_list[0]]
        return {'FINISHED'}


class SJSelectionSetEditList(bpy.types.UIList):
    r""""""
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "set_name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


class SJSelectionSetPanel(bpy.types.Panel):
    r"""UI On Tool Header"""
    bl_label = "SJ Selection Set"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}  # デフォルトでは閉じている

    def draw(self, context):
        # TODO:多分正しい方法がほかにあると思う 突貫でいいや
        if context.active_object is not None:
            if context.active_object.mode != "OBJECT":
                return None

        layout = self.layout
        sjss = context.scene.sj_sel_set_props
        
        row = layout.row(align=True)
        # row.scale_x = 1.5
        row.prop(sjss, "selection_set_dplist", text="", translate=False)
        row = layout.row(align=True)
        row.operator("sj_selection_set.add_selset", icon="ADD")
        row.operator("sj_selection_set.delete_item_toolheader_bt", icon="REMOVE")
        # row.operator('sj_selection_set.clear_item', icon='X')


class SJSelectionSetListPanel(bpy.types.Panel):
    r"""UI"""
    bl_label = "SJ Selection Set List"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "SJT"
    bl_options = {'DEFAULT_CLOSED'}  # デフォルトでは閉じている

    def draw(self, context):
        layout = self.layout
        sjss = context.scene.sj_sel_set_props
        
        row = layout.row()
        sub_row = row.column()
        sub_row.prop(sjss, "selection_set_dplist", text="Selection Set")
        sub_row = row.row(align=True)
        # sub_row.scale_x = 1.2
        sub_row.operator("sj_selection_set.add_selset", icon="ADD")
        sub_row.operator("sj_selection_set.delete_item", icon="REMOVE")
        sub_row.operator("sj_selection_set.move_up_item", icon="SORT_DESC")
        sub_row.operator("sj_selection_set.move_down_item", icon="SORT_ASC")
        sub_row = row.column()
        sub_row.alignment = "RIGHT"
        sub_row.operator("sj_selection_set.clear_item", icon="X")
        # sub_row.operator('sj_selection_set.clear_item', icon='TRASH')
        row = layout.row()
        row.template_list(
            "SJSelectionSetEditList", "Sel Set List", context.scene, "sj_sel_set_items", context.scene, "sj_sel_set_item_index", rows=1)
        
        if len(context.scene.sj_sel_set_items) is 0:
            return None

        layout.separator(factor=2)
        row = layout.row(align=True)
        row.label(text="Add or remove objects to Selection set.")
        row = layout.row(align=True)
        row.scale_x = 2.0
        row.operator("sj_selection_set.select", icon="RESTRICT_SELECT_ON")
        row.operator("sj_selection_set.add_obj_to_set", icon="ADD")
        row.operator("sj_selection_set.remove_obj_to_set", icon="REMOVE")

        row = layout.row(align=True)
        index = context.scene.sj_sel_set_item_index
        item = context.scene.sj_sel_set_items[index]
        row.enabled = False
        row.prop(item, "object_list", text="Objects in set")
        # row.label(text="Objects in set: {}".format(
        #     context.scene.sj_sel_set_items[index].object_list))


classes = (
    SJSelectionSetItem,
    SJSelectionSetProperties,
    SJSelectionSetEditList,

    SJSelectionSetAddItem,
    SJSelectionSetDeleteItem,
    SJSelectionSetDeleteItemToolHeaderBt,
    SJSelectionSetMoveUpItem,
    SJSelectionSetMoveDownItem,
    SJSelectionSetClearItem,

    SJSelectionSetAddObjToSet,
    SJSelectionSetRemoveObjToSet,
    SJSelectionSetSelect,

    SJSelectionSetPanel,
    SJSelectionSetListPanel
    )


# Register all operators and panels
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # プロパティを追加する
    bpy.types.Scene.sj_sel_set_props = bpy.props.PointerProperty(type=SJSelectionSetProperties)

    # コレクションを追加
    bpy.types.Scene.sj_sel_set_items = bpy.props.CollectionProperty(type=SJSelectionSetItem)
    bpy.types.Scene.sj_sel_set_item_index = bpy.props.IntProperty(
        name="sj_sel_set_active_index", default=0)

    # bpy.types.VIEW3D_HT_header.append(SJSelectionSetPanel.draw)
    bpy.types.VIEW3D_HT_tool_header.append(SJSelectionSetPanel.draw)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # プロパティを削除
    del bpy.types.Scene.sj_sel_set_props
    # bpy.types.VIEW3D_HT_header.remove(SJSelectionSetPanel.draw)
    bpy.types.VIEW3D_HT_tool_header.remove(SJSelectionSetPanel.draw)


if __name__ == "__main__":
    register()
