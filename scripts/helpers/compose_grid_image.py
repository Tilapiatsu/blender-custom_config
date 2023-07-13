from PIL import Image
import os
# Import Image

source_folder = r'D:\path'
source_image_format = '.png'
destination_resolution = (2048, 4096)
use_contains = False
contains = 'filename'
max_row_size = 4
crop_overscan = 0.1

def get_max_row_height(images_to_process, max_row_size):
    original_crops =  [i[1] for i in images_to_process]
    print('images_to_process', images_to_process)
    print('original_crops', original_crops)
    max_crops = []
    for i in range(len(original_crops)):
        if i % max_row_size == 0:
            command = 'max_crops.append(min('
            for j in range(0,max_row_size):
                command += f'original_crops[{i+j}]'
                if j < max_row_size-1:
                    command += ', '
                else:
                    command += '))'
            print(command)
            exec(command)
    return max_crops


def get_max_collumn_height(image_to_process, max_row_size):
    pass

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

    image_path = os.path.join(source_folder, i)
    with Image.open(image_path) as image:
        bbox = image.getbbox()
        # Store Image Path and BBox to crop later
        images_to_process.append((image_path, bbox))

print(get_max_row_height(images_to_process, max_row_size))
row_number = 0
image_number = 0

for image in images_to_process:
    image_number += 1

    if image_number % max_row_size == 0:
        row_number += 1
    
    
    # print(f'Resizing file {i} to {destination_resolution}')
    # resized_image = image.resize(destination_resolution, resample = Image.Resampling.LANCZOS)

    # resized_image.save(os.path.join(source_folder, i))

