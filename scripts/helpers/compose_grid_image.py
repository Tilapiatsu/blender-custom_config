from PIL import Image
import os
import math

### Parameters
source_folder = r'C:\Users\lhlau\Documents\Tilapiatsu\Projects\RND\GridImage'
source_image_format = '.png'
destination_resolution = (2048, 4096)
background_color = (0,0,0,0)
use_contains = False
contains = 'filename'
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
			bottom_command = r'min('
			for j in range(max_row_size):
				top_command += f'original_crops[{i + j}][1]'
				bottom_command += f'original_crops[{i + j}][3]'
				if j < max_row_size-1:
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
		right_command = r'min('
		left = 0
		right = 0
		for j in range(row_count):
			if i + max_row_size >= len(original_crops):
				continue
			
			left_command += f'original_crops[{i + max_row_size}][0]'
			right_command += f'original_crops[{i + max_row_size}][2]'
			if j < row_count-1:
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

		image_path = os.path.join(source_folder, i)
		with Image.open(image_path) as image:
			bbox = image.getbbox()
			# Store Image Path and BBox to crop later
			images_to_process.append((image_path, bbox))
	
	return images_to_process


def get_image_size(images_to_process, max_row_size):
	image_path = images_to_process[0][0]
	image_size = ()
	row_count = math.ceil(len(images_to_process) / max_row_size)
	with Image.open(image_path) as image:
		image_size = (image.size[0] * max_row_size, image.size[1] * row_count)
	
	return image_size

images_to_process = get_images_to_process(source_folder)
max_row_height = get_max_row_height(images_to_process, max_row_size)
max_collumn_width = get_max_collumn_width(images_to_process, max_row_size)
image_size = get_image_size(images_to_process, max_row_size)

row_number = 0
image_number = 0
image_pathes = [i[0] for i in images_to_process]
final_image = Image.new('RGBA', image_size, background_color)

for image_path in image_pathes:

	with Image.open(image_path) as image:
		height_crop = max_row_height[math.floor(image_number / max_row_size)]
		width_crop =  max_collumn_width[image_number % max_row_size]
		# print(height_crop, width_crop)

		image.crop((width_crop[0], height_crop[0], width_crop[1], height_crop[1]))
		
		paste_position = (	image.size[0] * (image_number % max_row_size),
							image.size[1] * math.floor(image_number / max_row_size),
							image.size[0] * (image_number % max_row_size) + image.size[0],
							image.size[1] * math.floor(image_number / max_row_size) + image.size[1])
		
		# print(image_number, paste_position)

		final_image.paste(image, paste_position)

	image_number += 1

final_image.save(os.path.join(source_folder, 'composite.png'))

	
	# print(f'Resizing file {i} to {destination_resolution}')
	# resized_image = image.resize(destination_resolution, resample = Image.Resampling.LANCZOS)

	# resized_image.save(os.path.join(source_folder, i))

