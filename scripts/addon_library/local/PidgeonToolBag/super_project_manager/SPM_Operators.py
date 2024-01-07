#region import

import os
import bpy
import time

from bpy.props import (
    StringProperty,
    IntProperty,
)
from bpy.types import (
    Context,
    Event,
    UILayout,
    Operator
)

from bpy_extras.io_utils import ImportHelper

from .SPM_Functions import *

#endregion import

BPS_DATA_DIR = os.path.join(os.path.expanduser("~"), "Blender Addons Data", "blender-project-starter")
BPS_DATA_FILE = os.path.join(BPS_DATA_DIR, "BPS.json")


class SPM_OT_Build_Project(Operator):
    bl_idname = "superprojectmanager.build_project"
    bl_label = "Build Project"
    bl_description = "Build Project Operator "
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):

        D = bpy.data
        scene = context.scene
        prefs: 'AddonPreferences' = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        projectpath = os.path.join(context.scene.project_location, context.scene.project_name)
        filename = context.scene.save_file_name

        # Set the prefix.
        prefix = ""
        if prefs.prefix_with_project_name:
            prefix = context.scene.project_name + "_"

        # Set the list of Subfolders.
        folders = prefs.automatic_folders
        if context.scene.project_setup == "Custom_Setup":
            folders = prefs.custom_folders

        # Set the render outputfolder FULL path.
        is_render_outputfolder_set = [e.render_outputpath for e in folders]
        render_outputfolder = None

        if True in is_render_outputfolder_set:
            unparsed_string = folders[is_render_outputfolder_set.index(
                True)].folder_name
            render_outputfolder = Subfolders(
                unparsed_string, prefix).compile_paths(os.path.join(context.scene.project_location, context.scene.project_name))[-1]  # Use last path.

        # Create the Project Folder.
        if not os.path.isdir(projectpath):
            os.makedirs(projectpath)

        # Build all Project Folders
        for folder in folders:
            try:
                s = Subfolders(folder.folder_name, prefix)
                s.build_folders(os.path.join(context.scene.project_location, context.scene.project_name))
            except:
                pass

        # Set the subfolder of the Blender file.
        subfolder: str = prefs.save_folder.strip()

        # Set the path the Blender File gets saved to.
        filepath = D.filepath
        old_filepath = None
        if filepath == "":
            filepath = save_filepath(context, filename, subfolder)
        elif not is_file_in_project_folder(context, D.filepath):
            old_filepath = D.filepath
            filepath = save_filepath(context, filename, subfolder)
            if not context.scene.save_file_with_new_name:
                filepath = save_filepath(context, os.path.basename(
                    D.filepath).split(".blend")[0], subfolder)
        elif context.scene.save_blender_file_versioned:
            filepath = generate_file_version_number(
                D.filepath.split(".blen")[0].split("_v0")[0])

        # Set the render Output path automatically.
        if prefs.auto_set_render_outputpath and render_outputfolder and context.scene.set_render_output:
            context.scene.render.filepath = "//" + \
                os.path.relpath(render_outputfolder, os.path.dirname(filepath)) + "\\"

        if context.scene.save_blender_file:
            bpy.ops.wm.save_as_mainfile(filepath=filepath,
                                        compress=scene.compress_save,
                                        relative_remap=scene.remap_relative
                                        )

            if context.scene.cut_or_copy and old_filepath:
                os.remove(old_filepath)

        # Add the project to the list of unfinished projects.
        if context.scene.add_new_project:
            add_unfinished_project(projectpath)

        # Store all the necessary data in the project info file
        write_project_info(projectpath, filepath)

        # Open the project directory in the explorer, if wanted.
        if context.scene.open_directory:
            open_location = os.path.join(context.scene.project_location,
                                   context.scene.project_name)
            open_location = os.path.realpath(open_location)

            bpy.ops.wm.path_open(filepath=open_location)

        return {"FINISHED"}


class SPM_OT_add_folder(Operator):
    bl_idname = "superprojectmanager.add_folder"
    bl_label = "Add Folder"
    bl_description = "Add a Folder with the subfolder \
Layout Folder>>Subfolder>>Subsubfolder."

    coming_from: StringProperty()

    def execute(self, context: Context):
        pref: 'AddonPreferences' = context.preferences.addons[__package__.split(".")[0]].preferences

        if self.coming_from == "prefs":
            folder = pref.automatic_folders.add()

        else:
            folder = pref.custom_folders.add()

        return {"FINISHED"}


class SPM_OT_remove_folder(Operator):
    bl_idname = "superprojectmanager.remove_folder"
    bl_label = "Remove Folder"
    bl_description = "Remove the selected Folder."

    index: IntProperty()
    coming_from: StringProperty()

    def execute(self, context: Context):
        pref: 'AddonPreferences' = context.preferences.addons[__package__.split(".")[0]].preferences

        if self.coming_from == "prefs":
            folder = pref.automatic_folders.remove(self.index)

        else:
            folder = pref.custom_folders.remove(self.index)

        return {"FINISHED"}


# class SPM_OT_add_project(Operator, ImportHelper):
#     bl_idname = "superprojectmanager.add_project"
#     bl_label = "Add Project"
#     bl_description = "Add a Project"

#     filter_glob: StringProperty(default='*.filterall', options={'HIDDEN'})

#     def execute(self, context: Context):
#         projectpath = os.path.dirname(self.filepath)

#         message_type, message = add_unfinished_project(projectpath)
#         self.report(message_type, message)
#         return {"FINISHED"}

#     def draw(self, context: Context):
#         layout = self.layout
#         layout.label(text="Please select a project Directory")


# class SPM_OT_finish_project(Operator):
#     bl_idname = "superprojectmanager.finish_project"
#     bl_label = "Finish Project"
#     bl_description = "Finish the selected Project."
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()
#     project_name: StringProperty()

#     def execute(self, context: Context):
#         finish_project(self.index)
#         return {'FINISHED'}

#     def invoke(self, context: Context, event: Event):
#         return context.window_manager.invoke_props_dialog(self)

#     def draw(self, context: Context):
#         layout: UILayout = self.layout
#         # layout.prop(self, "disable")

#         layout.label(
#             text="Congratulations, you've finished your project!")
#         layout.separator()

#         confirmation_text = f"Click OK below to remove '{self.project_name}' from your ToDo List."
#         if len(confirmation_text) > 55:
#             # Break up the confirmation text, if it is longer than 55 characters.
#             pieces = confirmation_text.split(" ")
#             confirmation_lines = []

#             line = ""
#             for p in pieces:
#                 if len(line + p) > 55:
#                     confirmation_lines.append(line)
#                     line = ""

#                 line += p + " "

#             confirmation_lines.append(line)

#             # Display the confirmation text line by line
#             for line in confirmation_lines:
#                 row = layout.row()
#                 row.scale_y = 0.6
#                 row.label(text=line)

#         else:
#             layout.label(text=confirmation_text)


# class SPM_OT_redefine_project_path(Operator, ImportHelper):
#     bl_idname = "superprojectmanager.redefine_project_path"
#     bl_label = "Update Project path"
#     bl_description = "Your project has changed location - \
# please update the project path"

#     name: StringProperty()
#     filter_glob: StringProperty(default='*.filterall', options={'HIDDEN'})
#     index: IntProperty()

#     def execute(self, context: Context):
#         projectpath = os.path.dirname(self.filepath)
#         self.redefine_project_path(self.index, projectpath)

#         message = "Successfully changed project path: " + \
#             os.path.basename(projectpath)
#         self.report({'INFO'}, message)
#         return {"FINISHED"}

#     def draw(self, context: Context):
#         name = self.name

#         layout = self.layout
#         layout.label(text="Please select your project Directory for:")
#         layout.label(text=name)

#     def redefine_project_path(self, index, new_path):
#         data = decode_json(BPS_DATA_FILE)

#         data["unfinished_projects"][index][1] = new_path
#         encode_json(data, BPS_DATA_FILE)


# class SPM_OT_open_blender_file(Operator):
#     """Open the latest Blender-File of a project"""
#     bl_idname = "superprojectmanager.open_blender_file"
#     bl_label = "Open Blender File"
#     bl_options = {'REGISTER', 'UNDO'}

#     filepath: StringProperty()
#     message_type: StringProperty()
#     message: StringProperty()

#     def execute(self, context: Context):

#         bpy.ops.wm.open_mainfile(filepath=self.filepath)
#         self.report(
#             {self.message_type}, self.message)
#         return {"FINISHED"}


# class SPM_OT_define_blend_file_location(Operator, ImportHelper):
#     """This Operator is used to (re)define the location of the projects main Blender File"""
#     bl_idname = "superprojectmanager.define_blend_file_location"
#     bl_label = "Define Project Blender File Path"
#     bl_options = {'REGISTER', 'UNDO'}
#     bl_description = "Can't find the right path to the Blender File. \
# Please select the latest Blender File of you Project."

#     filter_glob: StringProperty(default='*.blend', options={'HIDDEN'})
#     message_type: StringProperty()
#     message: StringProperty()
#     projectpath: StringProperty()

#     def execute(self, context: Context):
#         # print(self.filepath)
#         write_project_info(self.projectpath, self.filepath)

#         message = "Successfully defined Blender Filepath: " + \
#             os.path.basename(self.filepath)
#         self.report({'INFO'}, message)

#         bpy.ops.superprojectmanager.open_blender_file(
#             filepath=self.filepath, message_type="INFO", message=f"Opened the project file found in {self.filepath}")
#         return {"FINISHED"}

#     def draw(self, context: Context):
#         name = os.path.basename(self.projectpath)

#         layout = self.layout
#         layout.label(text=self.message_type + ": " + self.message)
#         layout.label(text="Please select your project Directory for:")
#         layout.label(text=name)


# class SPM_OT_rearrange_up(Operator):
#     """Rearrange a Project or Label one step up."""
#     bl_idname = "superprojectmanager.rearrange_up"
#     bl_label = "Rearrange Up"
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()

#     def execute(self, context: Context):
#         index = self.index
#         data = decode_json(BPS_DATA_FILE)

#         data["unfinished_projects"][index], data["unfinished_projects"][index -
#                                                                         1] = data["unfinished_projects"][index - 1], data["unfinished_projects"][index]

#         encode_json(data, BPS_DATA_FILE)
#         return {'FINISHED'}


# class SPM_OT_rearrange_down(Operator):
#     """Rearrange a Project or Label one step down."""
#     bl_idname = "superprojectmanager.rearrange_down"
#     bl_label = "Rearrange Down"
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()

#     def execute(self, context: Context):
#         index = self.index
#         data = decode_json(BPS_DATA_FILE)

#         data["unfinished_projects"][index], data["unfinished_projects"][index +
#                                                                         1] = data["unfinished_projects"][index + 1], data["unfinished_projects"][index]

#         encode_json(data, BPS_DATA_FILE)
#         return {'FINISHED'}


# class SPM_OT_rearrange_to_top(Operator):
#     """Rearrange a Project or Label to the top."""
#     bl_idname = "superprojectmanager.rearrange_to_top"
#     bl_label = "Rearrange to Top"
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()

#     def execute(self, context: Context):
#         index = self.index
#         data = decode_json(BPS_DATA_FILE)

#         element = data["unfinished_projects"].pop(index)

#         data["unfinished_projects"].insert(0, element)

#         encode_json(data, BPS_DATA_FILE)
#         return {'FINISHED'}


# class SPM_OT_rearrange_to_bottom(Operator):
#     """Rearrange a Project or Label to the bottom."""
#     bl_idname = "superprojectmanager.rearrange_to_bottom"
#     bl_label = "Rearrange to Bottom"
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()

#     def execute(self, context: Context):
#         index = self.index
#         data = decode_json(BPS_DATA_FILE)

#         element = data["unfinished_projects"].pop(index)

#         data["unfinished_projects"].append(element)

#         encode_json(data, BPS_DATA_FILE)
#         return {'FINISHED'}


# class SPM_OT_add_label(Operator):
#     """Add a category Label to the open projects list."""
#     bl_idname = "superprojectmanager.add_label"
#     bl_label = "Add Label"
#     bl_options = {'REGISTER', 'UNDO'}

#     label: StringProperty()

#     def execute(self, context: Context):
#         data = decode_json(BPS_DATA_FILE)

#         data["unfinished_projects"].append(["label", self.label])

#         encode_json(data, BPS_DATA_FILE)
#         return {'FINISHED'}

#     def invoke(self, context: Context, event: Event):
#         return context.window_manager.invoke_props_dialog(self)

#     def draw(self, context: Context):
#         layout: UILayout = self.layout

#         layout.prop(self, "label", text="Category Label Text:")


# class SPM_OT_remove_label(Operator):
#     """Remove a category Label from the open projects list."""
#     bl_idname = "superprojectmanager.remove_label"
#     bl_label = "Remove Label"
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()

#     def execute(self, context: Context):
#         data = decode_json(BPS_DATA_FILE)

#         data["unfinished_projects"].pop(self.index)

#         encode_json(data, BPS_DATA_FILE)
#         return {'FINISHED'}


# class SPM_OT_change_label(Operator):
#     """Change a category Label from the open projects list."""
#     bl_idname = "superprojectmanager.change_label"
#     bl_label = "Change Label"
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()
#     label: StringProperty()

#     def execute(self, context: Context):
#         data = decode_json(BPS_DATA_FILE)

#         data["unfinished_projects"][self.index] = ["label", self.label]

#         encode_json(data, BPS_DATA_FILE)
#         return {'FINISHED'}

#     def invoke(self, context: Context, event: Event):
#         return context.window_manager.invoke_props_dialog(self)

#     def draw(self, context: Context):
#         layout: UILayout = self.layout

#         layout.prop(self, "label", text="Category Label Text:")


class SPM_OT_add_structure_set(Operator):
    """Adds a new folder structure set."""
    bl_idname = "superprojectmanager.add_structure_set"
    bl_label = "Add Folder Structure Set"
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty()

    def execute(self, context: Context):
        prefs: 'AddonPreferences' = context.preferences.addons[__package__.split(".")[0]].preferences

        data = decode_json(BPS_DATA_FILE)

        data["automatic_folders"][self.name] = []

        encode_json(data, BPS_DATA_FILE)

        prefs.folder_structure_sets = self.name

        return {'FINISHED'}

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context):
        layout = self.layout

        layout.prop(self, "name", text="Folder Structure Set Name:")


class SPM_OT_remove_structure_set(Operator):
    """Remove a folder structure set"""
    bl_idname = "superprojectmanager.remove_structure_set"
    bl_label = "Remove Set"
    bl_options = {'REGISTER', 'UNDO'}

    structure_set: StringProperty()

    def execute(self, context: Context):
        prefs: AddonPreferences = context.preferences.addons[__package__.split(".")[0]].preferences
        prefs.folder_structure_sets = "Default Folder Set"

        if self.structure_set == "Default Folder Set":
            self.report({'ERROR'}, "You can't delete the default folder set.")
            return {'FINISHED'}

        data = decode_json(BPS_DATA_FILE)
        data["automatic_folders"].pop(self.structure_set)
        encode_json(data, BPS_DATA_FILE)

        return {'FINISHED'}


# class SPM_OT_add_panel_project(Operator):
#     """Add a project to the project panel."""
#     bl_idname = "superprojectmanager.add_panel_project"
#     bl_label = "Add"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context: 'Context'):
#         data: dict = decode_json(BPS_DATA_FILE)
#         prefs: 'AddonPreferences' = context.preferences.addons[__package__.split(".")[0]].preferences

#         project_path = os.path.normpath(
#             context.space_data.params.directory.decode("utf-8"))

#         options = data.get("filebrowser_panel_options", [])[:]
#         options.append(project_path)

#         data["filebrowser_panel_options"] = options

#         encode_json(data, BPS_DATA_FILE)

#         prefs.active_project = project_path

#         return {'FINISHED'}


# class SPM_OT_remove_panel_project(Operator):
#     """Remove a project from the project panel."""
#     bl_idname = "superprojectmanager.remove_panel_project"
#     bl_label = "remove"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context: 'Context'):
#         data: dict = decode_json(BPS_DATA_FILE)
#         prefs: 'AddonPreferences' = context.preferences.addons[__package__.split(".")[0]].preferences

#         options = data.get("filebrowser_panel_options", [])[:]
#         options.remove(prefs.active_project)

#         data["filebrowser_panel_options"] = options

#         encode_json(data, BPS_DATA_FILE)

#         prefs.active_project = options[0]

#         return {'FINISHED'}


# class SPM_OT_panel_folder_base(Operator):
#     """Base operator for panel folder operations"""
#     bl_idname = "superprojectmanager.panel_folder_base"
#     bl_label = "Panel Folder Base"
#     bl_options = {'REGISTER', 'UNDO'}

#     def invoke(self, context: Context, event: Event):
#         prefs: 'AddonPreferences' = context.preferences.addons[__package__.split(".")[0]].preferences

#         if os.path.exists(os.path.join(prefs.active_project, ".blender_pm")):
#             return self.execute(context)

#         return context.window_manager.invoke_props_dialog(self)

#     def draw(self, context: Context):
#         layout: 'UILayout' = self.layout

#         layout.label(text="This project is missing important metadata.")
#         layout.label(
#             text="Do you want to continue? (Metadata will be added now)")

#     def execute(self, context: 'Context'):
#         prefs: 'AddonPreferences' = context.preferences.addons[__package__.split(".")[0]].preferences
#         project_metadata_file = os.path.join(prefs.active_project, ".blender_pm")

#         if not os.path.exists(project_metadata_file):
#             encode_json({"blender_files": {
#                 "main_file": "",
#                 "other_files": []
#             }, "build_date": time.time()}, project_metadata_file)

#         set_file_hidden(project_metadata_file, False)

#         data: dict = decode_json(project_metadata_file)

#         folders = data.get("displayed_project_folders", [])[:]

#         if len(folders) == 0:
#             for f in prefs.project_paths:
#                 folders.append({"folder_path": f.path})

#         data["displayed_project_folders"] = self.manipulate_folders(
#             context, folders)
#         encode_json(data, project_metadata_file)
#         register_project_folders(prefs.project_paths, prefs.active_project)

#         set_file_hidden(project_metadata_file)

#         return {'FINISHED'}

#     def manipulate_folders(self, context: 'Context', folders: 'list') -> list:
#         return folders


# class SPM_OT_add_panel_project_folder(SPM_OT_panel_folder_base):
#     """Add the current folder path to the project panel."""
#     bl_idname = "superprojectmanager.add_panel_project_folder"
#     bl_label = "Add Folder"
#     bl_options = {'REGISTER', 'UNDO'}

#     def manipulate_folders(self, context: Context, folders: list) -> list:
#         folders = folders[:]

#         folder_path = os.path.normpath(
#             context.space_data.params.directory.decode("utf-8"))
#         folders.append({"folder_path": folder_path})

#         paths = []
#         i = 0
#         while i < len(folders):
#             if folders[i].get("folder_path", "") in paths:
#                 folders.pop(i)
#                 continue

#             paths.append(folders[i].get("folder_path", ""))
#             i += 1

#         return folders


# class SPM_OT_remove_panel_project_folder(SPM_OT_panel_folder_base):
#     """Remove a folder from the project panel."""
#     bl_idname = "superprojectmanager.remove_panel_project_folder"
#     bl_label = "remove"
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()

#     def manipulate_folders(self, context: Context, folders: list) -> list:
#         folders = folders[:]
#         folders.pop(self.index)

#         return folders


# class SPM_OT_move_panel_project_folder(SPM_OT_panel_folder_base):
#     """Rearrange the project panel"""
#     bl_idname = "superprojectmanager.move_panel_project_folder"
#     bl_label = "Move"
#     bl_options = {'REGISTER', 'UNDO'}

#     index: IntProperty()
#     direction: IntProperty()

#     def manipulate_folders(self, context: Context, folders: list) -> list:
#         folders = folders[:]

#         f = folders.pop(self.index)
#         folders.insert(self.index + self.direction, f)

#         return folders


classes = (
    SPM_OT_add_folder,
    SPM_OT_remove_folder,
    SPM_OT_Build_Project,
    # SPM_OT_add_project,
    # SPM_OT_finish_project,
    # SPM_OT_redefine_project_path,
    # SPM_OT_open_blender_file,
    # SPM_OT_define_blend_file_location,
    # SPM_OT_rearrange_up,
    # SPM_OT_rearrange_down,
    # SPM_OT_rearrange_to_top,
    # SPM_OT_rearrange_to_bottom,
    # SPM_OT_add_label,
    # SPM_OT_remove_label,
    # SPM_OT_change_label,
    SPM_OT_add_structure_set,
    SPM_OT_remove_structure_set,
    # SPM_OT_add_panel_project,
    # SPM_OT_remove_panel_project,
    # SPM_OT_add_panel_project_folder,
    # SPM_OT_remove_panel_project_folder,
    # SPM_OT_move_panel_project_folder,
)


def register_function():
    prefs: 'AddonPreferences' = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
    register_automatic_folders(prefs.automatic_folders, prefs.previous_set)
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_function():
    prefs: 'AddonPreferences' = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
    unregister_automatic_folders(prefs.automatic_folders, prefs.previous_set)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
