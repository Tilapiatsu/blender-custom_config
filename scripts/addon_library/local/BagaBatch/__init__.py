# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "BagaBatch",
    "author" : "Antoine Bagattini",
    "description" : "Batch generate previews for the Asset Browser",
    "blender" : (3, 6, 0),
    "version" : (1, 0, 0),
    "location" : "3D View",
    "category" : "Generic"
}

import bpy
import os
import bpy.utils.previews
from bpy.types import WindowManager
from bpy.props import (EnumProperty)

from .bagabatch_ui import BAGABATCH_PT_Panel,BAGABATCH_UL_assetslib_list, BAGABATCH_OT_select_folder, BAGABATCH_OT_set_asset_type, BAGABATCH_OT_toggle_folder,BAGABATCH_OT_toggle_catalog,BAGABATCH_OT_select_catalog
from .bagabatch_render import BAGABATCH_OP_batch_preview
from .bagabatch_render_coll import BAGABATCH_OP_batch_coll_preview
from .bagabatch_utils import BAGABATCH_tooltips


def check_moulah_version():
    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_name = 'bagabatch_saveassets.py'
    file_path = os.path.join(current_directory, file_name)

    return(os.path.isfile(file_path))


if check_moulah_version():
    from .bagabatch_saveassets import BAGABATCH_OT_saveasset,BAGABATCH_OT_edit_assets,BAGABATCH_UL_mat_list,MATERIAL_UL_mats


class BAGABATCH_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    prefs = bpy.context.preferences
    filepaths = prefs.filepaths
    asset_libraries = filepaths.asset_libraries

    addon_pref_preview: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    addon_pref: bpy.props.BoolProperty(name="Addon Preferences", default=False)


    library_pipe: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    render_preferences: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    how_it_works: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    preferences: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    save_location: bpy.props.BoolProperty(name="Addon Preferences", default=True)
    save_path: bpy.props.StringProperty(name="Addon Preferences", default=asset_libraries[bpy.context.preferences.filepaths.active_asset_library].path)

    asset_type: bpy.props.BoolProperty(name="Assets Type", default=True)
    render_all_assets_coll: bpy.props.BoolProperty(
        name="Render all assets collection", 
        default=False,
        description="'All Marked Assets' = All Collections marked as assets in this scene will be rendered | 'Active Coll' = Render preview and Mark Assets the selected collection",
    )

    # CAMERA VIEW
    use_current_orientation: bpy.props.BoolProperty(name="Use Current View Orientation", default=False)
    use_view: bpy.props.BoolProperty(name="Use User View", default=True)
    force_focus_selected: bpy.props.BoolProperty(name="Fit view on object in user View", default=True)

    sun_orientation: bpy.props.FloatProperty(name="render_pref", default=90)
    camera_orientation: bpy.props.FloatProperty(name="render_pref", default=-45)
 
    render_engine: bpy.props.BoolProperty(name="Render Engine", default=False)
    render_exposition: bpy.props.FloatProperty(name="render_pref", default=0, min=-10, max=10)
    render_resolution: bpy.props.IntProperty(name="render_pref", default=256, min=2)

    # CYCLES
    cycles_samples: bpy.props.IntProperty(name="cycle_pref", default=32, min=2)
    cycles_transp_bounces: bpy.props.IntProperty(name="cycle_pref", default=8, min=0)
    cycles_denoise: bpy.props.BoolProperty(name="cycle_pref", default=True)
    cycles_transparent_background: bpy.props.BoolProperty(name="cycle_pref", default=True)

    # EEVEE
    eevee_samples: bpy.props.IntProperty(name="eevee_pref", default=16, min=2)
    eevee_ao: bpy.props.BoolProperty(name="eevee_pref", default=True)
    eevee_ssr: bpy.props.BoolProperty(name="eevee_pref", default=True)
    eevee_refract: bpy.props.BoolProperty(name="eevee_pref", default=False)
    eevee_transparent_background: bpy.props.BoolProperty(name="eevee_pref", default=True)

    # EXPORT
    prefix: bpy.props.StringProperty(name="Asset_Prefix", default="")
    use_export: bpy.props.StringProperty(name="Asset_Prefix", default="")
    export_type: bpy.props.StringProperty(name="Asset_Type", default="object")
    export_all_assets_coll: bpy.props.BoolProperty(name="Asset_Prefix", default=True)
    destination_library: bpy.props.BoolProperty(name="Asset_Prefix", default=False)
    asset_location: bpy.props.BoolProperty(name="Asset_Prefix", default=False)
    asset_category: bpy.props.BoolProperty(name="Asset_Prefix", default=False)
    target_catalog: bpy.props.StringProperty(name="Asset_Prefix", default="")
    cats_expand: bpy.props.StringProperty(name="Asset_Prefix", default="")
    uuid: bpy.props.StringProperty(name="Asset_Prefix", default="")
    remplace_link_coll_file: bpy.props.BoolProperty(name="Replace Coll", default=False)
    save_preview: bpy.props.BoolProperty(name="Save Preview", default=False)
    preview_filepath: bpy.props.StringProperty(name="",subtype='FILE_PATH')


    # DATA
    data: bpy.props.BoolProperty(name="Asset_data", default=False)
    description: bpy.props.StringProperty(name="Asset_data", default="")
    license: bpy.props.StringProperty(name="Asset_data", default="")
    copyright: bpy.props.StringProperty(name="Asset_data", default="")
    author: bpy.props.StringProperty(name="Asset_data", default="")
    # MATERIAL SOURCE


    def draw(self, context):
        layout = self.layout
        pref = context.preferences.addons['BagaBatch'].preferences        
        
        ###################################################################################
        # ADDON PREFERENCES
        ###################################################################################
        box = layout.box()
        box.prop(self, 'addon_pref_preview', text = "Preview Preferences", emboss = False, icon = "SEQ_PREVIEW")
        if self.addon_pref_preview == True:
            box.label(text="Asset Type :")
            row = box.row(align=True)
            row.prop(pref, 'asset_type', text="Object", icon = "OBJECT_DATA")
            row.prop(pref, 'asset_type', text="Collection", icon = "OUTLINER_COLLECTION", invert_checkbox = True)
            if pref.asset_type==False:
                row = box.row(align=True)
                row.prop(pref, 'render_all_assets_coll', text="Active Coll", toggle=True, invert_checkbox = True)
                row.prop(pref, 'render_all_assets_coll', text="All Marked Assets", toggle=True) 
            
            box.label(text="Camera Orientation :")
            row = box.row(align=True)
            row.prop(pref, 'use_current_orientation', text="Current", icon = "HIDE_OFF")
            row.prop(pref, 'use_current_orientation', text="Default", icon = "OUTLINER_OB_CAMERA", invert_checkbox = True)

            if pref.use_current_orientation:
                row = box.row(align=True)
                row.prop(pref, 'use_view', text="View", icon = "CAMERA_STEREO")
                row.prop(pref, 'use_view', text="Active Camera", icon = "OUTLINER_OB_CAMERA", invert_checkbox = True) 
                if pref.use_view:
                    box.prop(pref, 'force_focus_selected', text="Fit view to object")
            else:
                box.prop(pref, 'camera_orientation', text="Rotation Offset")

        box = layout.box()
        box.prop(self, 'addon_pref', text = "Render Preferences", emboss = False, icon = "SCENE")
        if self.addon_pref == True:
            col = box.column()
            col.label(text="Render Settings :")
            col.prop(pref, 'render_resolution', text="Resolution")

            row = col.row(align=True)
            row.scale_y=1.4
            row.prop(pref, 'render_engine', text="Cycles", invert_checkbox = True, toggle=True)
            row.prop(pref, 'render_engine', text="EEVEE", toggle=True)

            # CYCLES SETTINGS
            if pref.render_engine == False:
                box = col.box()
                box.label(text="Cycles Settings :")
                row=box.row()
                row.prop(pref, 'cycles_samples', text="Samples")
                row.prop(context.scene, "render_device", text="")
                box.prop(pref, 'cycles_transp_bounces', text="Transparency Bounces")
                box.prop(pref, 'cycles_denoise', text="Denoise")
                box.prop(pref, 'cycles_transparent_background', text="Transparent Background")
                box.prop(pref, 'render_exposition', text="Exposition", slider = True)
                box.prop(pref, 'sun_orientation', text="Default Sun Orientation (° deg)")

            # EEVEE SETTINGS
            else:
                box = col.box()
                box.label(text="EEVEE Settings :")
                box.prop(pref, 'eevee_samples', text="Samples")
                box.prop(pref, 'eevee_ao', text="Ambient Occlusion")
                box.prop(pref, 'eevee_ssr', text="Screen Space Reflection")
                if pref.eevee_ssr:
                    box.prop(pref, 'eevee_refract', text="Refraction")
                box.prop(pref, 'eevee_transparent_background', text="Transparent Background")
                box.prop(pref, 'render_exposition', text="Exposition", slider = True)
                box.prop(pref, 'sun_orientation', text="Default Sun Orientation (° deg)")

        row = layout.row(align=True)
        row.scale_y=1.5
        row.operator("wm.url_open", text="Contact on Discord").url = "https://discord.gg/pxuj3bzmSR"       
        row.operator("wm.url_open", text="Contact via BlenderMarket ").url = "https://blendermarket.com/products/bagabatch/faq"       

        col = layout.column()
        col.scale_y=2
        col.operator("wm.url_open", text="Our Addons !", icon = 'FUND').url = "https://blendermarket.com/creators/antoine-bagattini"


def enum_previews_from_directory_items(self, context):
    enum_items = []

    if context is None:
        return enum_items
    directory = os.path.join(os.path.dirname(__file__), "cycles_preview")

    pcoll = preview_collections["main"]

    if directory == pcoll.scene_previews_dir:
        return pcoll.scene_previews

    if directory and os.path.exists(directory):
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.scene_previews = enum_items
    pcoll.scene_previews_dir = directory
    return pcoll.scene_previews


if check_moulah_version():
    classes = [
        BAGABATCH_PT_Panel,
        BAGABATCH_Preferences,
        BAGABATCH_OP_batch_preview,
        BAGABATCH_OP_batch_coll_preview,
        BAGABATCH_UL_assetslib_list,
        BAGABATCH_OT_saveasset,
        BAGABATCH_OT_edit_assets,
        BAGABATCH_OT_select_folder,
        BAGABATCH_OT_toggle_folder,
        BAGABATCH_OT_toggle_catalog,
        BAGABATCH_OT_select_catalog,
        BAGABATCH_OT_set_asset_type,
        BAGABATCH_UL_mat_list,
        BAGABATCH_tooltips,
        MATERIAL_UL_mats,
        ]
else:
    classes = [
        BAGABATCH_PT_Panel,
        BAGABATCH_Preferences,
        BAGABATCH_OP_batch_preview,
        BAGABATCH_OP_batch_coll_preview,
        BAGABATCH_UL_assetslib_list,
        BAGABATCH_OT_select_folder,
        BAGABATCH_OT_toggle_folder,
        BAGABATCH_OT_toggle_catalog,
        BAGABATCH_OT_select_catalog,
        BAGABATCH_OT_set_asset_type,
        ]

preview_collections = {}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    WindowManager.scene_previews = EnumProperty(
        items=enum_previews_from_directory_items,
    )
    pcoll = bpy.utils.previews.new()
    pcoll.scene_previews_dir = ""
    pcoll.scene_previews = ()

    bpy.types.Scene.render_device = bpy.props.EnumProperty(
        items=[
            ('GPU', "GPU", ""),
            ('CPU', "CPU", "")
        ],
        name="Render Device",
        description="Choose the device for Cycles rendering"
    )

    preview_collections["main"] = pcoll

    bpy.types.Scene.selected_folder = bpy.props.StringProperty()
    bpy.types.Scene.active_lib_path = bpy.props.StringProperty()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del WindowManager.scene_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    del bpy.types.Scene.render_device

    if hasattr(bpy.types.Scene, 'selected'):
        del bpy.types.Scene.selected


if __name__ == "__main__":
    register()