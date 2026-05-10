#!/usr/bin/env python3

# ============================================================
# Batch render .blend files using Blender built-in CLI rendering
# Uses EACH SCENE'S OWN render output path already saved in .blend
#
# It scans recursively for .blend files whose names contain NAME_FILTER,
# detects scenes marked:
#     scene.render_scene == True
# then renders with:
#     blender -b file.blend -S SceneName -f 1
#
# Requires your addon installed in Blender.
# ============================================================

import subprocess
from pathlib import Path
import json

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

ROOT_DIR = "/path/to/root/folder"
SEARCH_DEPTH = 2
NAME_FILTER = "project"
BLENDER_EXE = "blender"

# ------------------------------------------------------------


def find_blend_files(root_dir, name_filter, max_depth=None):
    """
    Recursively find .blend files whose names contain name_filter.

    Parameters
    ----------
    root_dir : str | Path
        Root folder to start searching from.
    name_filter : str
        Case-insensitive substring that must appear in filename.
    max_depth : int | None
        Maximum subfolder depth relative to root_dir.

        0 = only root folder
        1 = root + direct subfolders
        2 = root + subfolders of subfolders
        None = unlimited depth
    """

    root = Path(root_dir).resolve()

    for file in root.rglob("*.blend"):
        # relative path from root
        rel = file.relative_to(root)

        # number of folders between root and file
        depth = len(rel.parts) - 1

        if max_depth is not None and depth > max_depth:
            continue

        if name_filter.lower() in file.name.lower():
            yield file


# ------------------------------------------------------------
# STEP 1 : Query scenes marked for rendering
# ------------------------------------------------------------


def get_marked_scenes(blend_file):
    """
    Opens the blend file in background and returns
    scene names where scene.render_scene == True
    """

    probe_script = r"""
import bpy
import json

result = []

for scene in bpy.data.scenes:
    if getattr(scene, "batch_render_scene", False):
        result.append(scene.name)

print("JSON_RESULT=" + json.dumps(result))
"""

    cmd = [BLENDER_EXE, "-b", str(blend_file), "--python-expr", probe_script]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    for line in proc.stdout.splitlines():
        if line.startswith("JSON_RESULT="):
            return json.loads(line[len("JSON_RESULT=") :])

    return []


# ------------------------------------------------------------
# STEP 2 : Render scene using its SAVED blender filepath
# ------------------------------------------------------------


def render_scene(blend_file, scene_name):

    cmd = [BLENDER_EXE, "-b", str(blend_file), "-S", scene_name, "-f", "1"]

    print("Running:")
    print(" ".join(cmd))

    subprocess.run(cmd)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------


def main():

    files = list(find_blend_files(ROOT_DIR, NAME_FILTER, SEARCH_DEPTH))

    print(f"Found {len(files)} blend files")

    for blend in files:
        print(f"\nScanning {blend}")

        scenes = get_marked_scenes(blend)

        if not scenes:
            print("  No marked scenes")
            continue

        print("  Scenes to render:", scenes)

        for scene in scenes:
            render_scene(blend, scene)


if __name__ == "__main__":
    main()
