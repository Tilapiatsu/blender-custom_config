from PIL import Image
import os
# Import Image

source_folder = r'E:\Projects\RND\TextureConversion'
source_image_format = '.tif'
destination_image_format = '.png'

for i in os.listdir(source_folder):
    filename, extension = os.path.splitext(i)
    if extension != source_image_format:
        continue

    print(f'Converting {i} to {filename + destination_image_format}')
    image = Image.open(os.path.join(source_folder, i))
    rgb_image = image.convert('RGB')

    rgb_image.save(os.path.join(source_folder, filename) + destination_image_format)

