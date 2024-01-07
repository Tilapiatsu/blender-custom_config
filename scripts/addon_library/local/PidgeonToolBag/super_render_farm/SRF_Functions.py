import bpy
import bpy
from bpy.types import (
    Context,
    Operator,
    OperatorProperties,
)

import sys
from os import path
import os
import requests
import json
import urllib.request
import subprocess
from zipfile import ZipFile
import shutil
import sqlite3

import json

import time
from random import choice

def download_latest_release(master: bool = False):
    recommended_version = 2

    version_url = "https://raw.githubusercontent.com/PidgeonTools/PidgeonRenderFarm/master/Versions.json"
    
    #latest_version = ""
    latest_supported_version = ""

    try:
        reqst = requests.get(version_url)
        json_string = json.loads(reqst.text)
        #latest_version = json_string["Versions"][-1]["Name"]
        
        for version in json_string["Versions"]:
            if version["ID"] == recommended_version:
                latest_supported_version = version["Name"]
                break
    except:
        print("Version file not found")
        print("Not ready to use!")
        return
    
    addon_path = os.path.dirname(os.path.realpath(__file__))
    download_dir = path.join(addon_path, "pidgeon_render_farm")
    folder_name = ""
    download_path = ""

    type_mc = "Master" if master else "Client"

    platform = sys.platform
    if platform == "linux" or platform == "linux2":
        folder_name = f"PRF_{type_mc}_Linux"
    elif platform == "win32":
        folder_name = f"PRF_{type_mc}_Windows"
    elif platform == "darwin":
        folder_name = f"PRF_{type_mc}_OSX"

    file_name = folder_name + ".zip"

    download_path = path.join(download_dir, file_name)

    try:
        if os.path.isdir(path.join(download_dir, folder_name)):
            shutil.rmtree(path.join(download_dir, folder_name))
    except Exception as e:
        print("Pre-download cleanup failed!")
        print("Not ready to use!")
        print(e)
        return

    try:
        urllib.request.urlretrieve(f"https://github.com/PidgeonTools/PidgeonRenderFarm/releases/download/{latest_supported_version}/{file_name}", download_path)
    except:
        print(f"File {file_name} not found in the latest release.")
        print(f"latest release: {latest_supported_version}")
        print("Not ready to use!")
        return

    try:
        with ZipFile(download_path, 'r') as zip:
            zip.extractall(download_dir)
        
        # file_names = os.listdir(path.join(download_dir, folder_name))
        # for file_name in file_names:
        #     shutil.move(os.path.join(download_dir, folder_name, file_name), download_dir)
    except:
        print("File extraction failed")
        print("Not ready to use!")
        return

    try:
        # shutil.rmtree(path.join(download_dir, folder_name))
        os.remove(download_path)
    except Exception as e:
        print("Cleanup failed")
        print(e)

def start_pidgeon_render_farm(self, context):
    scene = context.scene
    settings = scene.srf_settings
    chars: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    import shutil

    project_object = {
        "ID": ''.join(choice(chars) for i in range(8)),
        "Blender_Version": bpy.app.version_string,
        "Full_Path_Blend": bpy.data.filepath,
        "File_transfer_Mode": int(settings.rs_transfer_method),
        "Use_SID_Temporal": settings.rs_use_sidt,
        "Use_SFR": settings.rs_use_sfr,
        "Render_Test_Frame": settings.rs_test_render,
        "Render_Engine": scene.render.engine,
        "Output_File_Format": scene.render.image_settings.file_format,
        "Video_Generate": False,
        "Batch_Size": settings.rs_batch_size,
        "Time_Per_Frame": 0,
        "RAM_Use": 0,
        "First_Frame": scene.frame_start,
        "Last_Frame": scene.frame_end,
        "Frame_Step": scene.frame_step,
        "Frames_Total": (scene.frame_end - (scene.frame_start - 1)),
        "Keep_ZIP": True,
        "Download_Remote_Input": True,
    }

    if settings.master_db_override != "":
        settings.master_working_directory = settings.master_db_override
    elif settings.master_prf_override != "":
        settings.master_working_directory = path.join(settings.master_prf_override, project_object["ID"])
    else:
        settings.master_working_directory = path.join("pidgeon_render_farm", project_object["ID"])

    if settings.rs_use_sfr:
        # Try to call SFR
        try:
            bpy.ops.render.superfastrender_benchmark()
            # Save the new settings
            bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
        except AttributeError:
            print("SuperFastRender is NOT installed!")

    if settings.rs_use_sidt:
        # Try to call SFR
        try:
            bpy.ops.render.superfastrender_benchmark()
            # Save the new settings
            bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
        except AttributeError:
            print("SuperFastRender is NOT installed!")

    if settings.rs_test_render:
        startTime = time.time()
        bpy.context.scene.render.filepath = path.join(path.dirname(context.preferences.addons[__package__]
                                                                    .preferences.script_location), "frame_######")
        bpy.context.scene.frame_current = bpy.context.scene.frame_start
        bpy.ops.render.render()
        project_object["Time_Per_Frame"] = time.time() - startTime

    if project_object["Video_Generate"]:
        project_object["Video_FPS"] = scene.render.fps
        project_object["Video_Rate_Control"] = "CBR"
        project_object["Video_Rate_Control_Value"] = 0

        project_object["Video_Resize"] = False

        if project_object["Video_Resize"]:
            project_object["Video_Dimensions"] = {
                "X": 0,
                "Y": 0
            }

    json_string:str = json.dumps(project_object, indent = 4)

    json_string = json_string.replace("'", '"')
    json_string = json_string.replace("False", "false")
    json_string = json_string.replace("True", "true")

    folder_name = ""
    platform = sys.platform
    if platform == "linux" or platform == "linux2":
        folder_name = "PRF_Master_Linux"
    elif platform == "win32":
        folder_name = "PRF_Master_Windows"
    elif platform == "darwin":
        folder_name = "PRF_Master_OSX"

    prf_dir: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pidgeon_render_farm", "Release", folder_name)
    if settings.master_prf_override != "":
        prf_dir = settings.master_prf_override

    # write the dictionary to the file
    with open(path.join(prf_dir, "startup_project.prfp"), 'w') as f:
        f.write(json_string)
        f.close()

    addon_path = os.path.dirname(os.path.realpath(__file__))
    settings_path = os.path.join(addon_path, "pidgeon_render_farm", "master_settings.json")

    exe: str = "Master"
    platform = sys.platform
    if platform == "win32":
        exe += ".exe"
    exe_path: str = os.path.join(prf_dir, exe)

    # test the path for the json
    if not path.exists(settings_path):
        # report to the user to save the settings
        print("Settings not found!")
        self.report({'ERROR'}, "Settings not found! Please save the settings in the properties first!")
        return
        
    shutil.copy2(settings_path, path.join(prf_dir, "master_settings_override.json"))

    if platform == "win32":
        from subprocess import CREATE_NEW_CONSOLE
        subprocess.Popen(exe_path, creationflags=CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(f"'{exe_path}'", cwd=prf_dir, shell=True)
    
    return project_object

def prepare_scene():
    return

def display_progress_thread(context, project):
    scene = context.scene
    settings = scene.srf_settings

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    empty = bpy.context.view_layer.objects.active
    empty.name = "PRF_Progress_Empty"
    empty.scale = (0, 0, 0)
    bpy.context.scene.frame_current = scene.frame_start-1

    i: int = scene.frame_start
    while i <= scene.frame_end:
        empty.keyframe_insert(data_path='empty_display_size', frame=i)
        i += scene.frame_step

    fcurves = empty.animation_data.action.fcurves
    for fcurve in fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.type = "EXTREME"

    folder_name = ""
    platform = sys.platform
    if platform == "linux" or platform == "linux2":
        folder_name = "PRF_Master_Linux"
    elif platform == "win32":
        folder_name = "PRF_Master_Windows"
    elif platform == "darwin":
        folder_name = "PRF_Master_OSX"

    prf_dir: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pidgeon_render_farm", "Release", folder_name)
    if settings.master_prf_override != "":
        prf_dir = settings.master_prf_override

    db_path: str =  path.join(prf_dir, "Database")
    if settings.master_db_override != "":
        db_path = settings.master_db_override

    # wait 2 second 5 times
    for i in range(5):
        if path.exists(db_path):
            break
        time.sleep(2)
    connection = sqlite3.connect(path.join(db_path, "Project.db"))
    cursor = connection.cursor()

    # Initialize variables
    frames_total: int = 0
    frames_left: int = -1
    frames_done: int = -1
    table_count: int = 0

    # Wait until PRF has created the project table
    while table_count == 0:
        time.sleep(3)
        try:
            cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{project["ID"]}";')
            table_count = len(cursor.fetchall())
        except:
            pass

    while frames_total <= 0:
        time.sleep(3)
        try:
            cursor.execute(f'SELECT * FROM {project["ID"]}')
            frames_total = len(cursor.fetchall())
        except:
            pass

    while frames_done <= frames_done:
        time.sleep(3)
        
        # Select all frames from the database
        cursor.execute(f'SELECT * FROM {project["ID"]}')
        frames_left = 0
        frames_done = 0
        frames_total = 0

        for frame in cursor.fetchall():
            frames_total += 1

            # Adjust the keyframes used to display the progress
            set_curves(frame, fcurves)

            if frame[1] == "Rendering" or frame[1] == "Open":
                frames_left += 1
            else:
                frames_done += 1

        set_pointer(scene, fcurves)

    # Cut the connection to the database and remove the empty object
    cursor.close()
    connection.close()
    empty.select_set(True)
    bpy.ops.object.delete()
    empty.delete()

def set_curves(frame, fcurves):
    no:int = frame[0]
    state:str = frame[1]

    if state == "Rendering":
        for fcurve in fcurves:
            fcurve.keyframe_points[int(no)-1].type = "KEYFRAME"
    elif state == "Open":
        for fcurve in fcurves:
            fcurve.keyframe_points[int(no)-1].type = "EXTREME"
    elif state == "Rendered":
        for fcurve in fcurves:
            fcurve.keyframe_points[int(no)-1].type = "JITTER"

def set_pointer(scene, fcurves):
    bpy.context.scene.frame_current = scene.frame_start-1
    for keyframe in fcurves[0].keyframe_points:
        if keyframe.type == "JITTER":
            bpy.context.scene.frame_current = bpy.context.scene.frame_current+1
        else:
            break

def save_settings(settings):
    # save to a json file
    # get the addon path
    addon_path = os.path.dirname(os.path.realpath(__file__))
    settings_path = os.path.join(addon_path,"pidgeon_render_farm","master_settings.json")
    
    # turn the settings into a dictionary
    settings_dict = {
        "Enable_Logging": settings.master_logging,
        "Port": settings.master_port,
        "Allow_Data_Collection": settings.master_analytics,
        "Blender_Installations": [
            {
            "Version": bpy.app.version_string,
            "Executable": bpy.app.binary_path,
            "Render_Device": "CPU",
            "Allowed_Render_Engines": [ "other" ],
            "CPU_Thread_Limit": 4
            }
        ],
        "Client_Limit": settings.master_client_limit,
        "Allow_Computation": True,
        "IPv4_Overwrite": settings.master_ipoverride,
        "Database_Connection": {
            "Mode": 0
        },
    }

    if settings.master_ftp_url != "":
        settings_dict["FTP_Connection"] = {
            "User": settings.master_ftp_user,
            "Password": settings.master_ftp_pass,
            "URL": settings.master_ftp_url
        }
    if settings.master_smb_url != "":
        settings_dict["FTP_Connection"] = {
            "User": settings.master_smb_user,
            "Password": settings.master_smb_pass,
            "URL": settings.master_smb_url
        }
    if settings.master_db_override != "":
        settings_dict["Database_Connection"]["Path"] =  settings.master_db_override
    elif settings.master_prf_override != "":
        settings_dict["Database_Connection"]["Path"] =  path.join(os.path.dirname(os.path.realpath(__file__)), settings.master_prf_override, "Database")
    # else:
    #     settings_dict["Database_Connection"]["Path"] =  path.join(os.path.dirname(os.path.realpath(__file__)), "pidgeon_render_farm", "Database")

    json_string: str = json.dumps(settings_dict, indent = 4)
    json_string = json_string.replace("'",'"')
    json_string = json_string.replace("True", "true")
    json_string = json_string.replace("False", "false")

    # write the dictionary to the file
    with open(settings_path, 'w') as f:
        f.write(json_string)
        f.close()