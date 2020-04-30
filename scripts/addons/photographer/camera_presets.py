import bpy

from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu, Operator

class PHOTOGRAPHER_MT_CameraPresets(Menu):
	bl_label = 'Camera Presets'
	preset_subdir = 'photographer/cameras'
	preset_operator = 'script.execute_preset'
	draw = Menu.draw_preset

class PHOTOGRAPHER_OT_AddCameraPreset(AddPresetBase, Operator):
	bl_idname = 'photographer.camera_add_preset'
	bl_label = 'Save Camera preset'
	preset_menu = 'PHOTOGRAPHER_MT_CameraPresets'
	
	# Common variable used for all preset values
	preset_defines = [ 
		'camera = bpy.context.scene.camera.data',
		'photographer = bpy.context.scene.camera.data.photographer',
	]
	
	preset_values = [
		'photographer.sensor_type',
		'photographer.aperture',
		'photographer.aperture_preset',
		'photographer.aperture_slider_enable',
		'camera.lens',
		'camera.dof.use_dof',
		'camera.dof.aperture_ratio',	
		'camera.dof.aperture_blades',			
		'camera.dof.aperture_rotation',
	]
	
	# Directory to store the presets
	preset_subdir = 'photographer/cameras'
	
class PHOTOGRAPHER_PT_CameraPresets(PresetPanel, Panel):
	bl_label = 'Camera Presets'
	preset_subdir = 'photographer/cameras'
	preset_operator = 'script.execute_preset'
	preset_add_operator = 'photographer.camera_add_preset'
	
	@classmethod
	def poll(cls,context):
		return bpy.context.scene.camera