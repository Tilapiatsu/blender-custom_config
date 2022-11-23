from PIL import Image
import os
# Import Image

# source_folder = r'E:\Projects\RND\TextureConversion'
source_folder = r'C:\Folder'
source_image_format = '.png'
destination_resolution = (2048, 4096)
use_contains = True
contains = 'SubString'

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

    print(f'Resizing file {i} to {destination_resolution}')
    image = Image.open(os.path.join(source_folder, i))
    resized_image = image.resize(destination_resolution, resample = Image.Resampling.LANCZOS)

    resized_image.save(os.path.join(source_folder, i))

