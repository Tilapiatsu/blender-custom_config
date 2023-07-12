from PIL import Image
import os
# Import Image

source_folder = r'D:\path'
source_image_format = '.png'
destination_resolution = (2048, 4096)
use_contains = True
contains = 'filename'
max_row_size = 4

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
        images_to_process.append({image_path:bbox + bbox * 0.1})

for image_path in images_to_process:

    print(f'Resizing file {i} to {destination_resolution}')
    resized_image = image.resize(destination_resolution, resample = Image.Resampling.LANCZOS)

    resized_image.save(os.path.join(source_folder, i))

