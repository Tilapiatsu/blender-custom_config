from PIL import Image
import os
# Import Image

# source_folder = r'E:\Projects\RND\TextureConversion'
source_folder = r'D:\Folder'
source_image_format = '.png'
destination_resolution = (4096, 2048)

for i in os.listdir(source_folder):
    filename, extension = os.path.splitext(i)
    if extension != source_image_format:
        continue

    print(f'Resizing file {i} to {destination_resolution}')
    image = Image.open(os.path.join(source_folder, i))
    resized_image = image.resize(destination_resolution, resample = Image.Resampling.LANCZOS)

    resized_image.save(os.path.join(source_folder, i))

