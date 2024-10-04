try:
    from PIL import Image
    
except ModuleNotFoundError as e:
    print(e)
    import subprocess
    import sys
    print(subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pillow']))
    from PIL import Image

import os
import math
import bpy


### Parameters
source_folder = bpy.path.abspath('c:\\path')
source_image_format = '.png'
max_destination_resolution = (6000, 6000)
background_color = (0, 0, 0, 1)
use_contains = True
save_jpeg = True
save_png = True
contains = 'contains'
output_filename = contains
max_row_size = 4
crop_overscan = 0.02

def get_max_row_height(images_to_process, max_row_size):
    original_crops = [i[1] for i in images_to_process]
    max_crops = []
    for i in range(len(original_crops)):
        if i % max_row_size == 0:
            top = 0
            bottom = 0
            top_command = r'min('
            bottom_command = r'max('
            for j in range(max_row_size):
                index = min(i+j, len(original_crops)-1)
                top_command += f'original_crops[{index}][1]'
                bottom_command += f'original_crops[{index}][3]'
                if index < i+j:
                    top_command += ')'
                    bottom_command += ')'
                elif j < max_row_size-1:
                    top_command += ', '
                    bottom_command += ', '
                else:
                    top_command += ')'
                    bottom_command += ')'
            top = eval(top_command)
            bottom = eval(bottom_command)
            max_crops.append((top, bottom))

    return max_crops


def get_max_collumn_width(images_to_process, max_row_size):
    original_crops = [i[1] for i in images_to_process]
    max_crops = []
    row_count = math.ceil(len(original_crops) / max_row_size)
    for i in range(max_row_size):
        left_command = r'min('
        right_command = r'max('
        left = 0
        right = 0
        for j in range(row_count):
            index = min(i + max_row_size * j, len(original_crops)-1)
            left_command += f'original_crops[{index}][0]'
            right_command += f'original_crops[{index}][2]'
            if index < i + max_row_size * j -1:
                left_command += ')'
                right_command += ')'
            elif j < row_count-1:
                left_command += ', '
                right_command += ', '
            else:
                left_command += ')'
                right_command += ')'
        left = eval(left_command)
        right = eval(right_command)

        max_crops.append((left, right))

    return max_crops


def get_images_to_process(source_folder):
    images_to_process = []

    for i in os.listdir(source_folder):
        filename, extension = os.path.splitext(i)
        if extension != source_image_format:
            print(f'Skipping {i}')
            continue
        if use_contains:
            if contains not in filename:
                print(filename)
                print(f'Skipping {i}')
                continue
        if filename == output_filename + '_composite':
            print(f'Skipping {i}')
            continue

        image_path = os.path.join(source_folder, i)
        with Image.open(image_path) as image:
            bbox = image.getbbox()
            # Store Image Path and BBox to crop later
            images_to_process.append((image_path, bbox))
    
    return images_to_process


def get_image_size(images_to_process, max_row_size, max_row_height, max_collumn_width):
    image_path = images_to_process[0][0]
    image_size = (0, 0)
    uncroped_image_size = (0, 0)

    with Image.open(image_path) as image:
        uncroped_image_size = (image.size[0], image.size[1])

    print('uncroped', uncroped_image_size)

    for i in range(len(images_to_process)):
        height_crop = (0, 0)
        if i < max_row_size:
            width_crop =  max_collumn_width[i % max_row_size]

        if i % max_row_size == 0: # if new row
            height_crop = max_row_height[math.floor(i / max_row_size)]

        if i < max_row_size :
            image_size = (	math.floor((image_size[0] - width_crop[0] + width_crop[1]) * (1 + crop_overscan)),
                            image_size[1])
            
        image_size = (	image_size[0],
                        math.floor((image_size[1] - height_crop[0] + height_crop[1]) * (1 + crop_overscan))  )
        
        print('image_size_iter =', image_size)

    return image_size


def get_resized_dimensions(image_size, max_size):
    new_width = image_size[0]
    new_height = image_size[1]
    if new_width > max_size[0]:
        print(f'width_too_big = {image_size[0]} / {max_size[0]}')
        new_width = max_size[0]
        new_height = math.floor(image_size[1] * max_size[0] / image_size[0])

    if new_height > max_size[1]:
        print(f'height_too_big = {image_size[1]} / {max_size[1]}')
        new_width = math.floor(image_size[0] * max_size[1] / image_size[1])
        new_height = max_size[1]

    print(f'resized_dimensions = ({new_width}, {new_height})')
    return (new_width, new_height)
    

images_to_process = get_images_to_process(source_folder)

for i in range(len(images_to_process)):
    print(f'images_to_process_{i} =', images_to_process[i][0])
    print(f'bbox_{i} = ', images_to_process[i][1])

max_row_height = get_max_row_height(images_to_process, max_row_size)
max_collumn_width = get_max_collumn_width(images_to_process, max_row_size)

print('max_row_height =', max_row_height)
print('max_collumn_width =', max_collumn_width)

image_size = get_image_size(images_to_process, max_row_size, max_row_height, max_collumn_width)
print('image_size =', image_size)

row_number = 0
image_number = 0
image_pathes = [i[0] for i in images_to_process]
final_image = Image.new('RGBA', image_size, background_color)
paste_position = (0, 0, 0, 0)
new_row = 0

if not len(image_pathes):
    exit()

for image_path in image_pathes:
    if image_number != 0:
        if image_number % max_row_size == 0:
            row_number +=1
            paste_position = (0, paste_position[3], 0, 0)

    with Image.open(image_path) as image:
        height_crop = max_row_height[math.floor(image_number / max_row_size)]
        width_crop =  max_collumn_width[image_number % max_row_size]

        cropped = image.crop((	width_crop[0], 
                                height_crop[0],
                                width_crop[1],
                                height_crop[1]))

        print(f'crop_size_{image_number} =', cropped.size)
        if image_number % max_row_size == 0:
            paste_position = (	paste_position[0], # Left 0
                                paste_position[1] + math.floor(image_size[1] / max_row_size * crop_overscan * 8), # Top 1
                                paste_position[2], # Right 2
                                paste_position[1] + cropped.size[1] + math.floor(image_size[1] / max_row_size * crop_overscan * 8)) # Bottom 3

        paste_position = (	paste_position[2] + math.floor(image_size[0] / max_row_size * crop_overscan  * 2), # Left 0
                            paste_position[1], # Top 1
                            paste_position[2] + cropped.size[0] + math.floor(image_size[0] / max_row_size * crop_overscan  * 2), # Right 2
                            paste_position[3] ) # Bottom 3
        
        print('paste_position =', paste_position)
        final_image.paste(cropped, paste_position)

    image_number += 1


resized_dimensions = get_resized_dimensions(image_size, max_destination_resolution)
if resized_dimensions[0] < image_size[0] and resized_dimensions[1] < image_size[1]:
    print('Resizing image ...')
    final_image = final_image.resize((resized_dimensions[0], resized_dimensions[1]))

if save_png:
    destination = os.path.join(source_folder, output_filename + '_composite.png')
    print('saving Image : ', destination)
    final_image.save(destination)
if save_jpeg:
    destination = os.path.join(source_folder, output_filename + '_composite.jpg')
    print('saving Image : ', destination)
    jpg = Image.new('RGBA', resized_dimensions, background_color)
    jpg.alpha_composite(final_image)
    jpg = jpg.convert('RGB')
    jpg.save(destination)

print('Composite Done !!!')

