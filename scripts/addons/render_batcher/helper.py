import bpy, os, shutil, stat

def create_folder_if_neeed(path):
	if not os.path.exists(path):
			os.makedirs(path)

def delete_folder_if_exist(path):
	if os.path.exists(path):
		shutil.rmtree(path, onerror=file_acces_handler)

def file_acces_handler(func, path, exc_info):
    print('Handling Error for file ' , path)
    print(exc_info)
    # Check if file access issue
    if not os.access(path, os.W_OK):
       # Try to change the permision of file
       os.chmod(path, stat.S_IWUSR)
       # call the calling function again
       func(path)

def get_current_frame_range(context):
	return context.scene.frame_end + 1 - context.scene.frame_start

def get_curr_render_extension(context):
	return '.png'
