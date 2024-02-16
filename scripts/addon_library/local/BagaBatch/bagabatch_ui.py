import bpy
import os
from pathlib import Path

if not hasattr(bpy.types.Scene, "folder_props"):
    bpy.types.Scene.folder_props = {}

class BAGABATCH_UL_assetslib_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)

# FILE EXPLORER
class BAGABATCH_OT_select_folder(bpy.types.Operator):
    bl_idname = "bagabatch.select_folder"
    bl_label = "Select Folder"
    
    folder_path: bpy.props.StringProperty()
    entry_path: bpy.props.StringProperty()
    prop_id: bpy.props.StringProperty()

    def execute(self, context):
        pref = context.preferences.addons['BagaBatch'].preferences
        pref.save_path = self.folder_path
        
        bpy.ops.bagabatch.toggle_folder('INVOKE_DEFAULT', folder_path=self.entry_path, prop_id=self.prop_id)

        return {'FINISHED'}

class BAGABATCH_OT_toggle_folder(bpy.types.Operator):
    bl_idname = "bagabatch.toggle_folder"
    bl_label = "Toggle Folder View"

    folder_path: bpy.props.StringProperty()
    prop_id: bpy.props.StringProperty()

    def execute(self, context):
        bpy.types.Scene.folder_props[self.prop_id] = not bpy.types.Scene.folder_props[self.prop_id]
        return {'FINISHED'}

def draw_folder_hierarchy(layout, path, level=0,next_lvl=2):
    pref = bpy.context.preferences.addons['BagaBatch'].preferences
    if os.path.exists(path):
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    # utiliser chemin complet pour éviter les souci de noms
                    prop_id = f"folder_props['{entry.path}']"
                    if prop_id not in bpy.types.Scene.folder_props:
                        bpy.types.Scene.folder_props[prop_id] = False
                    has_subfolders = any(os.path.isdir(os.path.join(entry.path, d)) for d in os.listdir(entry.path))

                    col = layout.column(align=True)
                    split = col.split(factor=0.05)

                    col_toogle = split.column(align=True).column(align=True)
                    col_toogle.alignment = 'RIGHT'

                    col_new =split.column(align=True).column(align=True)
                    row = col_new.row(align=True)

                    if level < next_lvl and has_subfolders:
                        # bouton pour show/hide les sous-dossiers
                        icon = 'TRIA_RIGHT' if not bpy.types.Scene.folder_props[prop_id] else 'TRIA_DOWN'
                        op = col_toogle.operator("bagabatch.toggle_folder", text="", icon=icon, emboss=False)
                        op.folder_path = entry.path
                        op.prop_id = prop_id
                    else:
                        col_toogle.label(text="  ")

                    
                    is_selected= False
                    if pref.save_path==entry.path:
                        is_selected= True
                    row.alignment = 'LEFT'
                    oz=row.operator("bagabatch.select_folder", text=entry.name, depress  = is_selected, emboss=is_selected)
                    oz.folder_path = entry.path
                    oz.entry_path=entry.path
                    oz.prop_id=prop_id
                    
                    if bpy.types.Scene.folder_props[prop_id]:
                        draw_folder_hierarchy(col_new, entry.path, level + 1,next_lvl+1)

# CONVERT TXT TO catalog_data = 'uuid': uuid / 'path': path / 'name': name
def load_catalog_data(file_path):
    catalog_data = []
    file_path_with_name = os.path.join(file_path, "blender_assets.cats.txt")
    if os.path.exists(file_path_with_name) == False:
        return None
    with open(file_path_with_name, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split(':')
                if len(parts) == 3:
                    uuid, path, _ = parts
                    name = path.split('/')[-1].split('-')[-1]
                    catalog_data.append({
                        'uuid': uuid,
                        'path': path,
                        'name': name
                    })
    if catalog_data == []:
        return None
    else:
        return catalog_data

# CATALOG
class BAGABATCH_OT_toggle_catalog(bpy.types.Operator):
    bl_idname = "bagabatch.toggle_catalog"
    bl_label = "Toggle Folder View"

    path: bpy.props.StringProperty()

    def execute(self, context):
        pref = context.preferences.addons['BagaBatch'].preferences
        
        list_cats_open = pref.cats_expand.split(";")
        if self.path in list_cats_open:
            list_cats_open.remove(self.path)
            pref.cats_expand = ";".join(list_cats_open)
        else:
            pref.cats_expand += self.path + ";"
        return {'FINISHED'}

class BAGABATCH_OT_select_catalog(bpy.types.Operator):
    bl_idname = "bagabatch.select_catalog"
    bl_label = "Toggle Folder View"

    path: bpy.props.StringProperty()
    uuid: bpy.props.StringProperty()

    def execute(self, context):
        pref = context.preferences.addons['BagaBatch'].preferences
        pref.target_catalog = self.path
        pref.uuid = str(self.uuid)
        return {'FINISHED'}

def draw_catalog(layout, catalog_data, target_level=0, path="", draw=True):
    pref = bpy.context.preferences.addons['BagaBatch'].preferences
    sublevel=False
    for cats in catalog_data:
        
        current_level = cats['path'].count('/')
        
        if current_level == target_level and path in cats['path']:
            list_cats_open = pref.cats_expand.split(";")
            if path in list_cats_open or draw==True:
                embled = pref.target_catalog == cats['path']
                column = layout.column(align=True)
                split = column.split(factor=0.15*(current_level+1), align=True)
                
                row_top = split.row(align=True)
                row_bottom = split.row(align=True)   

                op = row_bottom.operator("bagabatch.select_catalog", text=cats['name'], depress=embled, emboss=embled)
                op.path = cats['path']
                op.uuid = cats['uuid']

                if cats['path'] in list_cats_open:
                    icon = 'TRIA_DOWN'
                else:
                    sublev = False
                    icon = 'TRIA_RIGHT'
                sublev = draw_catalog(layout, catalog_data, target_level=target_level+1,path=cats['path'], draw=False)

                if sublev:
                    rocol = row_top.column(align=True)
                    split = rocol.split(factor=0.6, align=True)
                    row_top_bis = split.row(align=True)
                    row_bottom_bis = split.row(align=True)
                    row_bottom_bis.operator("bagabatch.toggle_catalog",text="", icon=icon,emboss=False).path=cats['path']

            sublevel=True

    return sublevel

class BAGABATCH_OT_set_asset_type(bpy.types.Operator):
    bl_idname = "bagabatch.set_asset_type"
    bl_label = "Set Asset Type"
    type: bpy.props.StringProperty()
    def execute(self, context):
        pref = context.preferences.addons['BagaBatch'].preferences
        pref.export_type = self.type
        return {'FINISHED'}

# PANEL
class BAGABATCH_PT_Panel(bpy.types.Panel):
    bl_label = "BagaBatch"
    bl_idname = "BAGABATCH_PT_preview_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BagaBatch'

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        pref = context.preferences.addons['BagaBatch'].preferences
        # col_alert = layout.column(align=True)
        # col_alert.alert=True
        # col_alert.label(text="BETA VERSION", icon ='ERROR')
        # col_alert.label(text="Only for testing !")

        # IN CASE THE RENDER CRASH AND THE USER RECOVER THE SCENE
        if context.scene.name.startswith("TEMP_BB_"):
            layout.alert=True
            layout.label(text="Your Blender Crashed ?", icon ='ERROR')
            layout.label(text="Please, go back to your scene.")
        else:

            col = layout.column(align=True)
            col.scale_y=1.4
            col.template_icon_view(wm, "scene_previews")
            col = layout.column(align=True)
            col.scale_y=2.5
            if pref.asset_type:
                col.operator("bagabatch.batch_preview", text= 'Generate Assets Thumbnails !')
            else:
                col.operator("bagabatch.batch_coll_preview", text= 'Generate Assets Thumbnails !')

            col = layout.column(align=True)
            col.separator(factor = 1)
            box = col.box()
            box.prop(pref, 'preferences', text = "Preview Settings", emboss = False, icon = "SEQ_PREVIEW")
            if pref.preferences == True:
            
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

            col.separator(factor = 1)
            box = col.box()
            box.prop(pref, 'render_preferences', text = "Render Settings", emboss = False, icon = "SCENE")
            if pref.render_preferences == True:
                box.label(text="Render Settings :")
                box.prop(pref, 'render_resolution', text="Resolution")

                row = box.row(align=True)
                row.scale_y=1.5
                row.prop(pref, 'render_engine', text="Cycles", invert_checkbox = True, toggle=True)
                row.prop(pref, 'render_engine', text="EEVEE", toggle=True)

                
                current_directory = os.path.dirname(os.path.abspath(__file__))
                file_name = 'bagabatch_saveassets.py'
                file_path = os.path.join(current_directory, file_name)
                if os.path.isfile(file_path):
                    box.prop(pref, 'save_preview', text="Save Preview as PNG :")
                    if pref.save_preview == True:
                        col_path = box.column(align=True)
                        if pref.preview_filepath =="": col_path.alert=True
                        col_path.prop(pref, 'preview_filepath')

                # CYCLES SETTINGS
                if pref.render_engine == False:
                    box = box.box()
                    box.label(text="Cycles Settings :")
                    box.prop(pref, 'cycles_samples', text="Samples")
                    box.prop(context.scene, "render_device", text="")
                    box.prop(pref, 'cycles_transp_bounces', text="Transparency Bounces")
                    box.prop(pref, 'cycles_denoise', text="Denoise")
                    box.prop(pref, 'cycles_transparent_background', text="Transparent Background")
                    box.prop(pref, 'render_exposition', text="Exposition", slider = True)
                    box.prop(pref, 'sun_orientation', text="Sun Orientation")

                # EEVEE SETTINGS
                else:
                    box = box.box()
                    box.label(text="EEVEE Settings :")
                    box.prop(pref, 'eevee_samples', text="Samples")
                    box.prop(pref, 'eevee_ao', text="Ambient Occlusion")
                    box.prop(pref, 'eevee_ssr', text="Screen Space Reflection")
                    if pref.eevee_ssr:
                        box.prop(pref, 'eevee_refract', text="Refraction")
                    box.prop(pref, 'eevee_transparent_background', text="Transparent Background")
                    box.prop(pref, 'render_exposition', text="Exposition", slider = True)
                    box.prop(pref, 'sun_orientation', text="Sun Orientation")

                    

            current_directory = os.path.dirname(os.path.abspath(__file__))
            file_name = 'bagabatch_saveassets.py'
            file_path = os.path.join(current_directory, file_name)
            if os.path.isfile(file_path):

                col.separator(factor = 1)
                box_main = col.box()
                box_main.prop(pref, 'library_pipe', text = "Export", emboss = False, icon = "ASSET_MANAGER")
                if pref.library_pipe == True:

                    bigbutton=box_main.row(align=True)
                    bigbutton.scale_y=2
                    bigbutton.operator("bagabatch.saveasset", text = "Export Assets")
                    bigbutton.scale_x=2
                    bigbutton.prop(pref, 'how_it_works', text = "", icon = "INFO")

                    if pref.how_it_works == True:
                        tips=box_main.box()
                        tips=tips.column(align=True)
                        tips.scale_y=0.7
                        tips.label(text="Save Assets export your asset in existing library.")
                        tips.label(text="Assets will be saved as individual blend files.")
                        tips.separator(factor = 4)
                        tips.label(text="Export Steps :")
                        tips.separator(factor = 2)
                        tips.label(text="1 - Select assets (objects or collections) to save.")
                        tips.separator(factor = 1)
                        tips.label(text="2 - Set the asset type below.")
                        tips.separator(factor = 1)
                        tips.label(text="3 - Specify the destination library for the assets.")
                        tips.separator(factor = 1)
                        tips.label(text="4 - If your library contains subfolders :")
                        tips.label(text="     Go to Asset Location > Library Subfolder")
                        tips.label(text="     Asset will be saved directly in selected subfolders")
                        tips.separator(factor = 1)
                        tips.label(text="PS : Render a preview first !")
                        tips.label(text="     Export button won't do it.")

                    col_select=box_main.column(align=True)
                    asset_types = ['object', 'collection', 'material']
                    row = col_select.row(align=True)
                    for a in asset_types:
                        row.operator("bagabatch.set_asset_type", text= a.capitalize(), depress=pref.export_type==a).type=a

                    if pref.export_type=="collection":
                        row = col_select.row(align=True)
                        row.prop(pref, 'export_all_assets_coll', text="Active Collection", toggle=True, invert_checkbox = True)
                        row.prop(pref, 'export_all_assets_coll', text="All Marked Assets", toggle=True)
                        row = col_select.row(align=True)
                        row.prop(pref, 'remplace_link_coll_file', text="Remove & Link coll", toggle=True)
                        tips = row.operator("bagabatch.tooltips", text="", depress = False, icon = 'INFO')
                        tips.message = "Once the collection is exported as .blend files to the specified library below, it will be unlinked from your scene and a link will be made from the exported collection to your scene. This feature is very useful for optimizing your scenes, however, use this feature only if you are familiar with Blender's linking system!"
                        tips.title = "Export and remove asset, link"
                        tips.size = 50
                        tips.url = "None"


                        if pref.remplace_link_coll_file==True:
                            col_select.label(text="- Coll will be unlinked from scene")
                            col_select.label(text="- Exported coll will be linked to scene")

                    box_dest = box_main.box()
                    box_dest.prop(pref, 'destination_library', text = "Destination Library", emboss = False, icon = "ASSET_MANAGER")
                    if pref.destination_library == True:
                        lib = bpy.context.preferences.filepaths
                        box_dest.label(text="Select Asset Destination Library :")
                        box_dest.template_list("BAGABATCH_UL_assetslib_list", "", lib, "asset_libraries", lib, "active_asset_library")

                    box_loc = box_main.box()
                    box_loc.prop(pref, 'asset_location', text = "Library: Asset Location", emboss = False, icon = "FILEBROWSER")
                    if pref.asset_location == True:
                        box_loc.label(text="File location in the Library folder:")
                        row = box_loc.row(align=True)
                        row.prop(pref, 'save_location', text="Current Library", toggle=True)
                        row.prop(pref, 'save_location', text="Library Subfolder", toggle=True, invert_checkbox = True)

                        prefs = bpy.context.preferences
                        filepaths = prefs.filepaths
                        asset_libraries = filepaths.asset_libraries
                        active_lib_path = asset_libraries[bpy.context.preferences.filepaths.active_asset_library].path

                        if pref.save_location==False:

                            box_exp=box_loc.box()
                            is_selected= False
                            if pref.save_path==active_lib_path:
                                is_selected= True
                            box_exp.operator("bagabatch.select_folder", text="Use : "+asset_libraries[bpy.context.preferences.filepaths.active_asset_library].name, depress  = is_selected).folder_path = active_lib_path
                            box_exp.label(text="Library Folders :", icon ='FILE_FOLDER')
                            if os.path.exists(active_lib_path):
                                has_subfolders = any(os.path.isdir(os.path.join(active_lib_path, d)) for d in os.listdir(active_lib_path))
                            else:
                                has_subfolders = False
                            if has_subfolders:
                                col_exp=box_exp.column(align=True)
                                draw_folder_hierarchy(col_exp, active_lib_path)
                            else:
                                box_exp.label(text="No Subfolder")
                            box_exp.label(text="Assets will be saved in :", icon='INFO')
                            box_exp.label(text=pref.save_path)

                    box_cat = box_main.box()
                    box_cat.prop(pref, 'asset_category', text = "Asset Catalog", emboss = False)
                    if pref.asset_category == True:
                        box_cat.label(text="Assets Category in the Catalog")
                        file_path = bpy.context.preferences.filepaths.asset_libraries[bpy.context.preferences.filepaths.active_asset_library].path
                        catalog_data = load_catalog_data(file_path)
                        if catalog_data is None:
                            box_cat.label(text="No Catalog Found")
                        else:
                            col_cat=box_cat.column(align=True)
                            draw_catalog(col_cat, catalog_data)

                    box_data = box_main.box()
                    col_data = box_data.column(align=True)
                    col_data.prop(pref, 'data', text = "Asset Metadata", emboss = False, icon = "TEXT")
                    if pref.data == True:
                        col_data.separator(factor = 1)
                        col_data.prop(pref, 'description', text = "Description")
                        col_data.prop(pref, 'license', text = "License")
                        col_data.prop(pref, 'copyright', text = "Copyright")
                        col_data.prop(pref, 'author', text = "Author")

            col.separator(factor = 1)
            col.operator("wm.url_open", text="Our Addons !", icon = 'FUND').url = "https://blendermarket.com/creators/antoine-bagattini"

classes = [
    BAGABATCH_OT_set_asset_type,
]