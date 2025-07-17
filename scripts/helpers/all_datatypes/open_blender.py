import os
import subprocess


root = r'E:\00_PortableApps\BlenderLauncher\BlenderVersions\stable'

output_text = r'C:\Users\tilap\AppData\Roaming\Blender Foundation\Blender\\4.5\scripts\helpers\all_datatypes\blender_datatypes.txt'

with open(output_text, 'w') as f:
    f.write('')

for bfolder in os.listdir(root):
    blender_exe = os.path.join(root, bfolder, 'blender.exe')
    print(blender_exe)
    if os.path.exists(blender_exe):
        subprocess.check_call([ blender_exe,
                                "-b",
                                "--python",
                                r"C:\Users\tilap\AppData\Roaming\Blender Foundation\Blender\\4.5\scripts\helpers\all_datatypes\get_all_datatypes.py"])