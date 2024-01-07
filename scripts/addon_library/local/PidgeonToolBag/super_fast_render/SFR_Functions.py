#region import

import bpy
import os
import numpy as np
import time
from ..pidgeon_tool_bag.PTB_Functions import bcolors
from pathlib import Path

try:
    import cv2
except Exception:
    pass

try:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except Exception:
    pass

#endregion import

#region TestRender

def set_bounces(bounces):
    """ Set the bounce settings for the render. """
    cycles = bpy.context.scene.cycles
    cycles.diffuse_bounces = bounces[0]
    cycles.glossy_bounces = bounces[1]
    cycles.transmission_bounces = bounces[2]
    cycles.volume_bounces = bounces[3]
    cycles.transparent_max_bounces = bounces[4]
    cycles.max_bounces = bounces[0] + bounces[1] + bounces[2] + bounces[3]

    if bounces[5] == 0: cycles.caustics_reflective = False
    else: cycles.caustics_reflective = True

    if bounces[6] == 0: cycles.caustics_refractive = False
    else: cycles.caustics_refractive = True

def calculate_brightness_difference(image_a, image_b):
    """ Calculate the average brightness difference between two images. """
    diff = image_b.astype(float) - image_a.astype(float)
    avg_diff = np.mean(np.abs(diff))
    avg_diff = round(avg_diff, 2)
    return avg_diff

def plot_data_rso(render_times, brightness_differences, bounces, bounce_type):
    """ Plot the render time against brightness difference for each bounce. """
    settings = bpy.context.scene.sfr_settings
    fig, ax1 = plt.subplots()

    # Plotting render time
    color = 'tab:red'
    ax1.set_xlabel('Bounces')
    ax1.set_ylabel('Render Time (seconds)', color=color)
    ax1.plot(bounces, render_times, 'o-', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Create a second y-axis for brightness difference
    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Delta', color=color)
    ax2.plot(bounces, brightness_differences, 's-', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.title(f'Render Time and Delta vs Bounces - {bounce_type}')
    fig.tight_layout() 
    plt.savefig(bpy.path.abspath(f'{settings.benchmark_path}/{bounce_type}.png'))
    plt.close()

#endregion TestRender

#region TextureOptimization
 
def test_opencv_format_support(file_path):
    image = cv2.imread(file_path)
    if image is None:
        return False

    path = bpy.path.abspath(bpy.context.scene.sfr_settings.benchmark_path)
    test_output = os.path.join(path, "test_output.png")
    cv2.imwrite(test_output, image)
    time.sleep(0.1)

    try:
        os.remove(test_output)
        return True
    except (IOError, PermissionError):
        return False
    
def resize_image(currFile, resizeFactor):
    path = bpy.path.abspath("//textures/")
    full_path = os.path.join(path, currFile)
    settings = bpy.context.scene.sfr_settings

    if not test_opencv_format_support(full_path):
        print(bcolors.WARNING + f"Unsupported file type or error reading file: {currFile}, skipping " + bcolors.ENDC)
        return False
    
    out_file = str(Path(currFile).with_suffix(f".{settings.converted_texture_format}"))

    resizeFactor = pow(2, resizeFactor)
    image = cv2.imread(full_path)

    new_size = (image.shape[1] // resizeFactor, image.shape[0] // resizeFactor)
    image_resized = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    
    cv2.imwrite(os.path.join(path, out_file), image_resized)
    print(bcolors.OKCYAN + f"Successful optimization of {currFile}" + bcolors.ENDC)

    if Path(os.path.normcase(currFile)).suffix != f".{settings.converted_texture_format}":
        os.remove(full_path)
        print(bcolors.OKCYAN + f"Removed {currFile}" + bcolors.ENDC)

    return True

def add_to_resized_textures(texture, type, resized_textures):
    if not texture in resized_textures:
        resized_textures[texture] = []
    resized_textures[texture].append(type)

    if len(resized_textures[texture]) > 1:
        types = ", ".join(resized_textures[texture])
        print(bcolors.WARNING + f"Texture {texture} matched multiple types: {types}. Will not resize again"+ bcolors.ENDC)
        return True
    
    return False
    
def resize_texture(file, setting, prop, type, resized_textures):
    nc_file = os.path.normcase(file)
    if setting < 0:
        return False
    if [name for name in prop if name in nc_file]:
        if add_to_resized_textures(file, type, resized_textures):
            return True
        return resize_image(file, setting)

def remap_texture(file):
    nc_file = os.path.normcase(file)
    file_path = "//textures"
    settings = bpy.context.scene.sfr_settings
    orig_path = file_path + "\\" + file
    orig_nc_path = file_path + "\\" + nc_file
    png_file = str(Path(file).with_suffix(f".{settings.converted_texture_format}"))

    for img in bpy.data.images:
        if img.filepath in (orig_path, orig_nc_path):
            img.filepath = os.path.join(file_path, png_file)
            img.reload()

#endregion TextureOptimization

#region RenderEstimator


def plot_data_estimator(render_times, frames):
    """ Plot the frames against render time. """
    settings = bpy.context.scene.sfr_settings
    fig, ax1 = plt.subplots()

    # Plotting render time
    color = 'tab:red'
    ax1.set_xlabel('Frames')
    ax1.set_ylabel('Render Time (seconds)', color=color)
    ax1.plot(frames, render_times, 'o-', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.title(f'Render Time vs Frame')
    fig.tight_layout() 
    plt.savefig(bpy.path.abspath(f'{settings.benchmark_path}/RenderTimes.png'))
    plt.close()

#endregion RenderEstimator