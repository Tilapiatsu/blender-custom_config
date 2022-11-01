from PIL import Image
import os, math
# Import Image

source_folder = r'E:\Projects\RND\MipCreation\Textures'
skip_existing_mip = True

mip0_folder = os.path.join(source_folder, '0')

if not os.path.exists(mip0_folder):
    exit()

for i in os.listdir(mip0_folder):
    filename, extension = os.path.splitext(i)
    if extension in ['.exr']:
        print(f'Skipping unsuported format : "{extension}"')
        continue

    print(f'Creating Mips for {i}')
    image = Image.open(os.path.join(mip0_folder, i))
    
    mip0_size = image.size
    for s in range(1,5):
        destination_folder = os.path.join(source_folder, str(s))
        destination_file = os.path.join(destination_folder, i)
        if not os.path.exists(destination_folder):
            os.mkdir(destination_folder)
        else:
            if skip_existing_mip:
                if os.path.exists(destination_file):
                    print(f'skipping MIP{s} Already exists!')
                    continue

        size = (int(mip0_size[0]/math.pow(2,s)),int(mip0_size[1]/math.pow(2,s)))
        print(f'Resizing immage to {size} MIP{s}')
        mip_image = image.resize(size, resample = Image.Resampling.LANCZOS)

        
        print(f'Saving immage to {destination_file}')
        mip_image.save(destination_file)


