'''
Lazy Shapekeys Addon (C) 2021-2022 Bookyakuno
Created by Bookyakuno
License : GNU General Public License version3 (http://www.gnu.org/licenses/)
'''

bl_info = {
    "name" : "Lazy Shapekeys",
    "author" : "Bookyakuno",
    "version" : (1, 0, 2),
    "blender" : (3, 00, 0),
    "location" : "3D View",
    "description" : "Shapekeys Utility. Transfer Shape(Forced) / Create Objects for All Shape Keys.",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "UI"
}


if "bpy" in locals():
    import importlib
    reloadable_modules = [
    "op",
    "ui",
    "utils",
    "props",

    ]
    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

from . import (
op,
ui,
utils,
props,
)
from .ui.ui_replace_sk_menu import LAZYSHAPEKEYS_PT_shape_keys
from .ui.ui_panel import LAZYSHAPEKEYS_PT_main
from .utils import *
from .props import *
import bpy
from bpy.props import *
from bpy.types import AddonPreferences, UIList


lmda = lambda s,c:s.layout;None
keep_DATA_PT_shape_keys = bpy.types.DATA_PT_shape_keys.draw


def update_use_folder_split(self,context):
    addon_prefs = preference()

    if addon_prefs.use_folder_split:
        bpy.types.DATA_PT_shape_keys.draw = lmda
        bpy.types.DATA_PT_shape_keys.prepend(LAZYSHAPEKEYS_PT_shape_keys)
    else:
        bpy.types.DATA_PT_shape_keys.draw = keep_DATA_PT_shape_keys
        bpy.types.DATA_PT_shape_keys.remove(LAZYSHAPEKEYS_PT_shape_keys)


def update_panel(self, context):
    message = ": Updating Panel locations has failed"
    try:
        cate = context.preferences.addons[__name__.partition('.')[0]].preferences.category
        if cate:
            for panel in panels:
                if "bl_rna" in panel.__dict__:
                    bpy.utils.unregister_class(panel)

            for panel in panels:
                panel.bl_category = cate
                bpy.utils.register_class(panel)

        else:
            for panel in panels:
                if "bl_rna" in panel.__dict__:
                    bpy.utils.unregister_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
    pass



class LAZYSHAPEKEYS_MT_AddonPreferences(AddonPreferences):
    bl_idname = __name__
    category : StringProperty(name="Tab Category", description="Choose a name for the category of the panel", default="Addons", update=update_panel)
    tab_addon_menu : EnumProperty(name="Tab", description="", items=[('OPTION', "Option", "","DOT",0),('LINK', "Link", "","URL",1)], default='OPTION')
    use_folder_split : BoolProperty(name="Use Folder Split in List Menu",description="Make the shape key block with '@' at the beginning of the name line into a folder.\nAdd a step to the shape key list menu to make it easier to classify",update=update_use_folder_split)
    folder_token : StringProperty(name="Folder Token",default="@")
    sk_menu_use_slider : BoolProperty(name="Use Slider Display",default=False)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self,"tab_addon_menu",expand=True)

        if self.tab_addon_menu == "OPTION":
            layout.prop(self,"category")
            layout.prop(self,"use_folder_split")

            if self.use_folder_split:
                box = layout.box()
                box.prop(self,"folder_token")
                box.prop(self,"sk_menu_use_slider")
                layout.separator()


        elif self.tab_addon_menu == "LINK":
            row = layout.row()
            row.label(text="Link:")
            row.operator( "wm.url_open", text="gumroad", icon="URL").url = "https://gum.co/VLdwV"


def draw_menu(self,context):
    layout = self.layout
    layout.separator()
    layout.operator("lazy_shapekeys.shape_keys_transfer_forced",icon="MOD_DATA_TRANSFER")
    layout.operator("lazy_shapekeys.shape_keys_create_obj_from_all",icon="DUPLICATE")
    if bpy.app.version >= (2,83,0):
        icon_val = "CHECKMARK"
    else:
        icon_val = "NONE"
    layout.operator("lazy_shapekeys.shape_keys_apply_modifier",icon=icon_val)



# def draw_MESH_UL_shape_keys(self,):
# 	layout.label(text="hoge",icon="NONE")

panels = (
LAZYSHAPEKEYS_PT_main,
)

classes = (
LAZYSHAPEKEYS_Props,
LAZYSHAPEKEYS_sync_colle,
LAZYSHAPEKEYS_MT_AddonPreferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


    op.register()
    ui.register()
    update_panel(None, bpy.context)

    bpy.types.Scene.lazy_shapekeys = PointerProperty(type=LAZYSHAPEKEYS_Props)
    bpy.types.Scene.lazy_shapekeys_colle = CollectionProperty(type=LAZYSHAPEKEYS_sync_colle)
    bpy.types.MESH_MT_shape_key_context_menu.append(draw_menu)
    # bpy.types.ShapeKey.name
    # bpy.types.ShapeKey.lazy_shapekeys = PointerProperty(type=LAZYSHAPEKEYS_Props)
    update_use_folder_split(None,bpy.context)

    try:
        bpy.app.translations.register(__name__, GetTranslationDict())
    except Exception as e: print(e)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for cls in reversed(panels):
        bpy.utils.unregister_class(cls)

    op.unregister()
    ui.unregister()

    bpy.types.DATA_PT_shape_keys.draw = keep_DATA_PT_shape_keys
    bpy.types.DATA_PT_shape_keys.remove(LAZYSHAPEKEYS_PT_shape_keys)


    try:
        bpy.app.translations.unregister(__name__)
    except Exception as e: print(e)

    # del bpy.types.ShapeKey.lazy_shapekeys
    del bpy.types.Scene.lazy_shapekeys
    del bpy.types.Scene.lazy_shapekeys_colle
    bpy.types.MESH_MT_shape_key_context_menu.remove(draw_menu)


if __name__ == "__main__":
    register()
