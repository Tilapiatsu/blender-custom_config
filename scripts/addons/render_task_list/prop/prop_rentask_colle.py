import bpy
from bpy.props import *
from bpy.types import PropertyGroup
from ..utils import (
get_item_scene
)


def poll_override_mat(self, object):
	return (not object.grease_pencil)


def poll_camera(self, object):
	props = bpy.context.scene.rentask
	colle = props.rentask_colle
	item = colle[props.rentask_index]
	tgt_sc = get_item_scene(item)

	return object.name in tgt_sc.collection.all_objects and object.type == 'CAMERA'


def update_camera_name(self, context):
	props = bpy.context.scene.rentask
	colle = props.rentask_colle
	item = colle[props.rentask_index]
	item.camera = item.camera_tmp_search.name


def update_index(self, context):
	props = context.scene.save_cam_other
	if props.rentask_use_update_index:
		bpy.ops.rentask.cam_load(item=context.scene.save_cam_collection_index)


class RENTASKLIST_PR_rentask_colle(PropertyGroup):
	cindex  : IntProperty(name='Index')
	name    : StringProperty(default="task",name="Task Name")
	use_render : BoolProperty(name="Use Render",default=True)
	is_tmp_item : BoolProperty()
	is_excluse_item : BoolProperty()
	parent_item_name : StringProperty()

	thread : IntProperty(name="Number of Threads", default=0, min=0, max=64)
	blendfile : StringProperty(name="External Blend Filepath",subtype='FILE_PATH',description="Renders a blend file other than the current file")
	frame : StringProperty(name="Frame",description="Specifies the frame to render\nYou can specify each frame as discrete\nYou can specify the frame range using ' - ' or ' .. '\nExample : 3,10,15,50-70,450..800")
	frame_start : IntProperty(name="Frame Start",min=-1,default=-1)
	frame_end : IntProperty(name="Frame End",min=-1,default=-1)

	user_script_file : StringProperty(name="User Script File",description="User script (.py) to be tun before rendering")
	user_script_text_block : PointerProperty(name="Text Block", type=bpy.types.Text,description="- Execute a block of text in the current blend file\n- Useful for running multi-line programs that are not as filed")



	camera_pointer : PointerProperty(name="Camera",description="",type=bpy.types.Object,poll=poll_camera)
	camera : StringProperty(name="Camera",description="")
	scene : StringProperty(name="Scene",description="")
	view_layer : StringProperty(name="View Layer",description="Need to disable the 'use nodes' in composite editor")
	world : StringProperty(name="World",description="")
	camera_all : BoolProperty(name="All Camera",description="")
	scene_all : BoolProperty(name="All Scene",description="")
	view_layer_all : BoolProperty(name="All View Layers",description="")
	light_individually_all : BoolProperty(name="All lights individually",description="")
	scene_follow_render_setting : BoolProperty(name="Follow Render Settings of Current Scene",default=True)

	thread : IntProperty(name="Threads", default=0, min=0, soft_max=64,max=64,description="The number of threads used for rendering.\nIf you specify 0, all logical threads are used.\nIf you want to do some other work while rendering, set it to 1 or more")

	items = [
		('IMAGE', "Image", "","RENDER_STILL", 0),
		('ANIME', "Animation", "","RENDER_ANIMATION", 1),
		]
	mode : EnumProperty(items=items, name="Rendering Mode", default='IMAGE',description="Select Frame rendering or Animation rendering")

	items = [
		('NONE', "None", "","NONE", 0),
		('BLENDER_EEVEE', "Eevee", "","SHADING_RENDERED", 1),
		('BLENDER_WORKBENCH', "Workbench", "","SHADING_SOLID", 2),
		('CYCLES', "Cycles", "","SHADING_TEXTURE",3),
		('OTHER', "Other", "","RADIOBUT_OFF",4),
		]
	engine : EnumProperty(items=items, name="Render Engine", default='NONE',description="Engine to use for rendering")
	engine_other : StringProperty(name="Other Engine Name",description="- Used to specify other than the default rendering engine\n- Uppercase only\n- You can get the current engine name with 'bpy.context.scene.render.engine'")
	resolution_x : IntProperty(default=0,name="Resolution X",min=0,description="",subtype="PIXEL")
	resolution_y : IntProperty(default=0,name="Resolution Y",min=0,description="",subtype="PIXEL")
	resolution_percentage : IntProperty(default=0,name="Resolution Percentage",min=0,soft_max=100,description="",subtype="PERCENTAGE")

	items = [
	('NONE',"None","","NONE",0),
	("BMP", "BMP", "Output image in bitmap format.","FILE_IMAGE",1),
	("IRIS", "Iris", "Output image in (old!) SGI IRIS format.","FILE_IMAGE",2),
	("PNG", "PNG", "Output image in PNG format.","FILE_IMAGE",3),
	("JPEG", "JPEG", "Output image in JPEG format.","FILE_IMAGE",4),
	("JPEG2000", "JPEG 2000", "Output image in JPEG 2000 format.","FILE_IMAGE",5),
	("TARGA", "Targa", "Output image in Targa format.","FILE_IMAGE",6),
	("TARGA_RAW", "Targa Raw", "Output image in uncompressed Targa format.","FILE_IMAGE",7),
	("CINEON", "Cineon", "Output image in Cineon format.","FILE_IMAGE",8),
	("DPX", "DPX", "Output image in DPX format.","FILE_IMAGE",9),
	("OPEN_EXR_MULTILAYER", "OpenEXR MultiLayer", "Output image in multilayer OpenEXR format.","FILE_IMAGE",10),
	("OPEN_EXR", "OpenEXR", "Output image in OpenEXR format.","FILE_IMAGE",11),
	("HDR", "Radiance HDR", "Output image in Radiance HDR format.","FILE_IMAGE",12),
	("TIFF", "TIFF", "Output image in TIFF format.","FILE_IMAGE",13),
	("AVI_JPEG", "AVI JPEG", "Output video in AVI JPEG format.","FILE_MOVIE",14),
	("AVI_RAW", "AVI Raw", "Output video in AVI Raw format.","FILE_MOVIE",15),
	("FFMPEG", "FFmpeg video", "The most versatile way to output video files.","FILE_MOVIE",16),
		]
	file_format : EnumProperty(items=items, name="File format", default='NONE',description="File format to save the rendered images as")

	filepath : StringProperty(name="Output Path",subtype="FILE_PATH",description="Directory/name to save animations.\nYou can use '#' to set the frame count character when rendering the animation.\nExample: image _ #### _ test → image_0001_test",default="")

	items = [
	('NONE',"None","","NONE",0),
	('objects',"Object","","OBJECT_DATA",1),
	('collections',"Collection","","GROUP",2),
	# ('materials',"Material","","MATERIAL_DATA",3),
	# ('lights',"Light","","LIGHT_DATA",4),
	]
	hide_data_type : EnumProperty(default="NONE",name = "Hide Data", items= items)
	hide_data_name : StringProperty(name="Hide Data Name")
	material_override_mat : StringProperty(name="Material Override")
	material_override_restore_scene_name : StringProperty()
	hide_data_tmp_list : StringProperty()
	frame_tmp_num : IntProperty(default=-1)
	samples : IntProperty(name="Samples",min=0)
