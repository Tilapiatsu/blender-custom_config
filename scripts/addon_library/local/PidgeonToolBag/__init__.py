import os, sys
module_path = os.path.join(os.path.dirname(__file__), "python_modules")
sys.path.append(module_path) # Add a module path for this specific addon

import bpy
from bpy.app.handlers import persistent

from .pidgeon_tool_bag import PTB_init
from .super_project_manager import SPM_init
from .super_fast_render import SFR_init
from .super_advanced_camera import SAC_init, SAC_Functions
from .super_real_sound import SRS_init
from .super_image_denoiser import SID_init
from .super_image_upscaler import SIU_init
from .super_res_render import SRR_init
from .super_render_farm import SRF_init
from .super_easy_analytics import SEA_init

from .pidgeon_tool_bag import (
    PTB_PropertiesRender_Panel,
)
from .pidgeon_tool_bag.PTB_Functions import (
    template_boxtitle,
)
from .super_project_manager.SPM_Functions import (
    active_project_enum,
    active_project_enum_update,
    structure_sets_enum,
    structure_sets_enum_update,
    subfolder_enum,
    get_active_project_path,
    set_active_project_path,
    Subfolders,
)

from bpy.props import (
    StringProperty,
    EnumProperty,
    CollectionProperty,
    BoolProperty,
    IntProperty
)

bl_info = {
    "name": "Pidgeon Tool Bag (PTB)",
    "author": "Kevin Lorengel, Crafto Hohenvels",
    "version": (2, 1, 0),
    "blender": (4, 0, 1),
    "location": "",
    "description": "A collection of all Pidgeon Tools addons.",
    "warning": "",
    "wiki_url": "https://discord.gg/cnFdGQP",
    "endpoint_url": "",
    "tracker_url": "",
    "category": "",
}

#region PreferencePanel


class project_folder_props(bpy.types.PropertyGroup):

    render_outputpath: BoolProperty(
        name="Render Output",
        description="Set the last path this folder input results in as output path for your renders",
        default=False)
    folder_name: StringProperty(
        name="Folder Name",
        description="Automatic Setup Folder. Format for Adding Subfolders: Folder>>Subfolder>>Subsubfolder",
        default="")
        
class FilebrowserEntry(bpy.types.PropertyGroup):

    icon: StringProperty(default="FILE_FOLDER")
    is_valid: BoolProperty()
    """Whether this path is currently reachable"""

    name: StringProperty()

    path: StringProperty()

    use_save: BoolProperty()
    """Whether this path is saved in bookmarks, or generated from OS"""

class PTB_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__  

    previous_set: StringProperty(default="Default Folder Set")

    custom_folders: CollectionProperty(type=project_folder_props)

    automatic_folders: CollectionProperty(type=project_folder_props)

    active_project: EnumProperty(
        name="Active Project",
        description="Which project should be displayed in the Filebrowser panel.",
        items=active_project_enum,
        update=active_project_enum_update
    )

    project_paths: CollectionProperty(type=FilebrowserEntry)
    active_project_path: IntProperty(
        name="Custom Property",
        get=get_active_project_path,
        set=set_active_project_path
    )

    layout_tab: EnumProperty(
        name="UI Section",
        description="Display the different UI Elements of the Super Project Manager preferences.",
        items=[
            ("misc_settings", "General", "General settings of Super Project Manager."),
            ("folder_structure_sets", "Folder Structures",
             "Manage your folder structure settings."),
            ("updater", "Updater", "Check for updates and install them."),
        ],
        default="misc_settings")

    folder_structure_sets: EnumProperty(
        name="Folder Structure Set",
        description="A list of all available folder sets.",
        items=structure_sets_enum,
        update=structure_sets_enum_update
    )

    prefix_with_project_name: BoolProperty(
        name="Project Name Prefix",
        description="If enabled, use the project name as prefix for all folders",
        default=False,
    )

    auto_set_render_outputpath: BoolProperty(
        name="Auto Set Render Output Path",
        description="If enabled, the feature to automatically set the Render Output path can be used",
        default=False,
    )

    default_project_location: StringProperty(
        name="Default Project Location",
        subtype="DIR_PATH",
        default=os.path.expanduser("~")
    )

    save_folder: EnumProperty(
        name="Save to",
        items=subfolder_enum
    )

    preview_subfolders: BoolProperty(
        name="Preview compiled Subfolders",
        description="Show the compiled subfolder-strings in the preferences",
        default=False
    )

    def draw(self, context):
        scene = context.scene
        prefs = context.preferences.addons[__package__].preferences
        layout = self.layout
        col = layout.column(align=True)

        ### GENERAL ###
        
        col.label(text="Pidgeon Tool Bag (PTB) Preferences", icon="PREFERENCES")

        colmain = self.layout.column(align=False)

        boxdependencies = colmain.box()
        col = boxdependencies.column()
        col.label(text="Dependencies", icon="FILE_FOLDER")
        row = col.row()
        row.scale_y = 1.5
        row.operator("pidgeontoolbag.install_dependencies", icon="SORT_ASC")
        
        ### SUPER RENDER FARM ###
#region SuperRenderFarm
        settings = scene.srf_settings
        boxmaster = colmain.box()
        template_boxtitle(settings, boxmaster, "master", "Super Render Farm: Master Settings", "EXTERNAL_DRIVE")
        if settings.show_master:

            boxmastergeneral = boxmaster.box()
            template_boxtitle(settings, boxmastergeneral, "master_general", "General Settings", "SETTINGS")
            if settings.show_master_general:
                col = boxmastergeneral.column()
                #col.prop(settings, "master_working_directory")
                row = col.row()
                row.scale_y = 1.5
                row.operator("superrenderfarm.download_master", text="Download Master", icon="SORT_ASC")
                row.operator("wm.url_open", text="Download Client", icon="SORT_ASC").url = "https://github.com/PidgeonTools/PidgeonRenderFarm/releases/latest"
                col.separator()
                row = col.row()
                row.prop(settings, "master_logging", toggle=True)
                row.prop(settings, "master_analytics", toggle=True)
                row.prop(settings, "master_data", toggle=True)
                col.prop(settings, "master_port")
                col.separator()

                boxmasteradvanced = col.box()
                template_boxtitle(settings, boxmasteradvanced, "master_advanced", "Advanced Settings", "SYSTEM")
                if settings.show_master_advanced:
                    colmasteradvanced = boxmasteradvanced.column()
                    colmasteradvanced.prop(settings, "master_ipoverride")
                    colmasteradvanced.prop(settings, "master_prf_override")
                    colmasteradvanced.prop(settings, "master_db_override")
                    colmasteradvanced.prop(settings, "master_client_limit")
                    colmasteradvanced.prop(settings, "others_pull_frequency")
                    colmasteradvanced.separator()

                    boxmasterftp = colmasteradvanced.box()
                    template_boxtitle(settings, boxmasterftp, "master_ftp", "FTP Settings", "PLUGIN")
                    if settings.show_master_ftp:
                        col = boxmasterftp.column()
                        col.prop(settings, "master_ftp_url")
                        col.separator()
                        col.prop(settings, "master_ftp_user")
                        col.prop(settings, "master_ftp_pass")
                    colmasteradvanced.separator(factor=0.2)

                    boxmastersmb = colmasteradvanced.box()
                    template_boxtitle(settings, boxmastersmb, "master_smb", "SMB Settings", "PLUGIN")
                    if settings.show_master_smb:
                        col = boxmastersmb.column()
                        col.prop(settings, "master_smb_url")
                        col.separator()
                        col.prop(settings, "master_smb_user")
                        col.prop(settings, "master_smb_pass")

                colsave = boxmastergeneral.column()
                colsave.scale_y = 1.5
                colsave.operator("superrenderfarm.save_master_settings", text="Save Settings", icon="FILE_TICK")
#endregion SuperRenderFarm

        ### SUPER PROJECT MANAGER ###
#region SuperProjectManager
        settings = scene.spm_settings
        boxmain = colmain.box()
        boxcolmain = boxmain.column()
        template_boxtitle(settings, boxcolmain, "main", "Super Project Manager", "FILE_BLEND")
        if settings.show_main:

            boxgeneral = boxcolmain.box()
            template_boxtitle(settings, boxgeneral, "general", "General Settings", "SETTINGS")
            if settings.show_general:
                col = boxgeneral.column()
                col.prop(prefs, "default_project_location")
                row = col.row()
                row.prop(prefs, "prefix_with_project_name",toggle=True)
                row.prop(prefs, "auto_set_render_outputpath",toggle=True)
            
            boxfolders = boxcolmain.box()
            template_boxtitle(settings, boxfolders, "folders", "Folder Settings", "FILE_FOLDER")
            if settings.show_folders:
                col = boxfolders.column()

                col.label(text="Folder Structure Set")
                row = col.row(align=True)
                row.prop(prefs, "folder_structure_sets", text="", icon="FILE_FOLDER")
                row.operator("superprojectmanager.add_structure_set", icon="ADD", text="")
                op = row.operator("superprojectmanager.remove_structure_set", icon="REMOVE", text="")
                op.structure_set = self.previous_set
                col.separator()
                box = col.box()
                box.label(text="Folder Structure Set: " + prefs.folder_structure_sets)

                compiled_preview_string = ""
                for index, folder in enumerate(self.automatic_folders):
                    render_outpath_active = True in [e.render_outputpath for e in self.automatic_folders]

                    row = box.row()
                    row.split(factor=0.1)  # Padding left

                    # Folder Name/Path Property
                    row.prop(folder, "folder_name", text="")

                    # Render Output Path
                    if self.auto_set_render_outputpath:
                        col = row.column()
                        col.enabled = folder.render_outputpath or not render_outpath_active
                        col.prop(folder, "render_outputpath", text="", icon="OUTPUT", emboss=folder.render_outputpath)

                    # Remove Icon
                    op = row.operator("superprojectmanager.remove_folder", text="", emboss=False, icon="PANEL_CLOSE")
                    op.index = index
                    op.coming_from = "prefs"
                    row.split(factor=0.1)  # Padding right

                    for warning in Subfolders(folder.folder_name).warnings:
                        row = box.row()
                        row.split(factor=0.1)  # Padding left
                        row.label(text=warning, icon="ERROR")
                        box.separator(factor=0.4)
                        row.split(factor=0.1)  # Padding right


                    compiled_preview_string += "((" + folder.folder_name + "))++"

                box.separator(factor=0.1)

                row = box.row()
                row.split(factor=0.1)  # Padding left

                op = row.operator("superprojectmanager.add_folder",icon="PLUS")
                op.coming_from = "prefs"
                row.split(factor=0.1)  # Padding right
                box.separator(factor=0.4)  # Padding bottom

                # Expand/Collapse Preview of compiled subfolders
                row = box.row()
                row.alignment = "LEFT"
                icon = "TRIA_DOWN" if self.preview_subfolders else "TRIA_RIGHT"
                row.prop(self, "preview_subfolders", emboss=False, icon=icon, text="Preview")

                # Preview complete folder structure
                if self.preview_subfolders:
                    prefix = ""
                    if self.prefix_with_project_name:
                        prefix = "Project_Name_"

                    for line in str(Subfolders(compiled_preview_string, prefix)).split("\n"):
                        row = box.row()
                        row.split(factor=0.1)
                        row.scale_y = 0.3
                        row.label(text=line)
#endregion SuperProjectManager

#endregion PreferencePanel

#  _____   ___   _____ 
# /  ___| / _ \ /  __ \
# \ `--. / /_\ \| /  \/
#  `--. \|  _  || |    
# /\__/ /| | | || \__/\
# \____/ \_| |_/ \____/
                     
                     
bpy.types.Scene.new_effect_type = bpy.props.EnumProperty(
    items=SAC_Functions.enum_previews_from_directory_effects)

bpy.types.Scene.new_bokeh_type = bpy.props.EnumProperty(
    items=SAC_Functions.enum_previews_from_directory_bokeh)

bpy.types.Scene.new_camera_bokeh_type = bpy.props.EnumProperty(
    items=SAC_Functions.enum_previews_from_directory_bokeh)

bpy.types.Scene.new_filter_type = bpy.props.EnumProperty(
    items=SAC_Functions.enum_previews_from_directory_filter)

bpy.types.Scene.new_gradient_type = bpy.props.EnumProperty(
    items=SAC_Functions.enum_previews_from_directory_gradient)

#  _________________ 
# /  ___| ___ \ ___ \
# \ `--.| |_/ / |_/ /
#  `--. \    /|    / 
# /\__/ / |\ \| |\ \ 
# \____/\_| \_\_| \_|
                   

@persistent
def load_handler(dummy):
    try:
        settings = bpy.context.scene.srr_settings
        settings.status.is_rendering = False
        settings.status.should_stop = False
    except:
        pass            

#  _____                                  _ 
# |  __ \                                | |
# | |  \/  ___  _ __    ___  _ __   __ _ | |
# | | __  / _ \| '_ \  / _ \| '__| / _` || |
# | |_\ \|  __/| | | ||  __/| |   | (_| || |
#  \____/ \___||_| |_| \___||_|    \__,_||_|
                                          

classes_pre = (
    project_folder_props,
    FilebrowserEntry,
    PTB_Preferences,
)

classes_post = (
    PTB_PropertiesRender_Panel.PTB_PT_Info_Panel,
    PTB_PropertiesRender_Panel.PTB_PT_Socials_Panel,
)

classes_all = classes_pre + classes_post
dev_mode = False

def register():
    for cls in classes_pre:
        try:
            bpy.utils.register_class(cls)
        except (RuntimeError, Exception) as e:
            print(f"Failed to register {cls}: {e}")

    # RELEASED
    PTB_init.register_function()
    SPM_init.register_function()
    SFR_init.register_function()
    SAC_init.register_function()
    SID_init.register_function()
    SIU_init.register_function()
    SRR_init.register_function()
    SRF_init.register_function()
    # IN DEVELOPMENT
    if dev_mode:
        SRS_init.register_function()
        SEA_init.register_function()

    for cls in classes_post:
        bpy.utils.register_class(cls)
    
    bpy.app.handlers.load_post.append(load_handler)

def unregister():
    # IN DEVELOPMENT
    if dev_mode:
        SRS_init.unregister_function()
        SEA_init.unregister_function()
    # RELEASED
    SRF_init.unregister_function()
    SRR_init.unregister_function()
    SIU_init.unregister_function()
    SID_init.unregister_function()
    SAC_init.unregister_function()
    SFR_init.unregister_function()
    SPM_init.unregister_function()
    PTB_init.unregister_function()

    for cls in reversed(classes_all):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")
        