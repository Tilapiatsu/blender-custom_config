import bpy

from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu, Operator

class PHOTOGRAPHER_MT_PhysicalLightPointPresets(Menu):
	bl_label = 'Physical Point Light Presets'
	preset_subdir = 'photographer/physical_lights/point'
	preset_operator = 'script.execute_preset'
	draw = Menu.draw_preset

	
class PHOTOGRAPHER_MT_PhysicalLightSunPresets(Menu):
	bl_label = 'Physical Sun Light Presets'
	preset_subdir = 'photographer/physical_lights/sun'
	preset_operator = 'script.execute_preset'
	draw = Menu.draw_preset
	
class PHOTOGRAPHER_MT_PhysicalLightSpotPresets(Menu):
	bl_label = 'Physical Spot Light Presets'
	preset_subdir = 'photographer/physical_lights/spot'
	preset_operator = 'script.execute_preset'
	draw = Menu.draw_preset

class PHOTOGRAPHER_MT_PhysicalLightAreaPresets(Menu):
	bl_label = 'Physical Area Light Presets'
	preset_subdir = 'photographer/physical_lights/area'
	preset_operator = 'script.execute_preset'
	draw = Menu.draw_preset

class PHOTOGRAPHER_OT_AddPointPreset(AddPresetBase, Operator):
	bl_idname = 'photographer.physical_light_add_point_preset'
	bl_label = 'Save Physical Point Light preset'
	preset_menu = 'PHOTOGRAPHER_MT_PhysicalLightPointPresets'
	
	# Common variable used for all preset values
	preset_defines = [ 
		'light = bpy.context.light',
		'physical_light = bpy.context.light.photographer',
	]
	
	preset_values = [
		'light.type',
		'physical_light.light_unit',
		'physical_light.use_light_temperature',
		'physical_light.light_temperature',	
		'physical_light.color',			
		'physical_light.normalizebycolor',			
		'physical_light.power',
		'physical_light.advanced_power',
		'physical_light.efficacy',
		'physical_light.lumen',
		'physical_light.candela',
		'physical_light.intensity',
		'physical_light.light_exposure',
		'light.shadow_soft_size',
	]
	
	# Directory to store the presets
	preset_subdir = 'photographer/physical_lights/point'
	
class PHOTOGRAPHER_OT_AddSunPreset(AddPresetBase, Operator):
	bl_idname = 'photographer.physical_light_add_sun_preset'
	bl_label = 'Save Physical Sun Light preset'
	preset_menu = 'PHOTOGRAPHER_MT_PhysicalLightSunPresets'
	
	# Common variable used for all preset values		
	preset_defines = [ 
		'light = bpy.context.light',
		'physical_light = bpy.context.light.photographer',
	]	
	
	preset_values = [
		'light.type',
		'light.angle',
		'physical_light.use_light_temperature',
		'physical_light.light_temperature',
		'physical_light.color',		
		'physical_light.normalizebycolor',				
		'physical_light.sunlight_unit',
		'physical_light.irradiance',
		'physical_light.illuminance',
	]

	# Directory to store the presets
	preset_subdir = 'photographer/physical_lights/sun'
	
class PHOTOGRAPHER_OT_AddSpotPreset(AddPresetBase, Operator):
	bl_idname = 'photographer.physical_light_add_spot_preset'
	bl_label = 'Save Physical Spot Light preset'
	preset_menu = 'PHOTOGRAPHER_MT_PhysicalLightSpotPresets'
	
	# Common variable used for all preset values
	preset_defines = [ 
		'light = bpy.context.light',
		'physical_light = bpy.context.light.photographer',
	]
	
	preset_values = [
		'light.type',
		'light.spot_blend',
		'light.shadow_soft_size',
		'physical_light.spot_size',
		'physical_light.light_unit',
		'physical_light.use_light_temperature',
		'physical_light.light_temperature',	
		'physical_light.color',					
		'physical_light.normalizebycolor',			
		'physical_light.power',
		'physical_light.advanced_power',
		'physical_light.efficacy',
		'physical_light.lumen',
		'physical_light.candela',
		'physical_light.per_square_meter',
		'physical_light.intensity',
		'physical_light.light_exposure',

	]
	
	# Directory to store the presets
	preset_subdir = 'photographer/physical_lights/spot'
	
	
class PHOTOGRAPHER_OT_AddAreaPreset(AddPresetBase, Operator):
	bl_idname = 'photographer.physical_light_add_area_preset'
	bl_label = 'Save Physical Area Light preset'
	preset_menu = 'PHOTOGRAPHER_MT_PhysicalLightAreaPresets'
	
	# Common variable used for all preset values
	preset_defines = [ 
		'light = bpy.context.light',
		'physical_light = bpy.context.light.photographer',
	]
	
	preset_values = [
		'light.type',
		'light.shape',
		'light.size',
		'light.size_y',
		'physical_light.light_unit',
		'physical_light.use_light_temperature',	
		'physical_light.light_temperature',
		'physical_light.color',	
		'physical_light.normalizebycolor',				
		'physical_light.power',
		'physical_light.advanced_power',
		'physical_light.efficacy',
		'physical_light.lumen',
		'physical_light.candela',
		'physical_light.per_square_meter',
		'physical_light.intensity',
		'physical_light.light_exposure',
	]
	
	# Directory to store the presets
	preset_subdir = 'photographer/physical_lights/area'
	
	
class PHOTOGRAPHER_PT_PhysicalLightPointPresets(PresetPanel, Panel):
	bl_label = 'Physical Point Light Presets'
	preset_subdir = 'photographer/physical_lights/point'
	preset_operator = 'script.execute_preset'
	preset_add_operator = 'photographer.physical_light_add_point_preset'
	
	@classmethod
	def poll(cls,context):
		return bpy.context.light.type == 'POINT'

class PHOTOGRAPHER_PT_PhysicalLightSunPresets(PresetPanel, Panel):
	bl_label = 'Physical Light Sun Presets'
	preset_subdir = 'photographer/physical_lights/sun'
	preset_operator = 'script.execute_preset'
	preset_add_operator = 'photographer.physical_light_add_sun_preset'
	
	@classmethod
	def poll(cls,context):
		return bpy.context.light.type == 'SUN'
		
class PHOTOGRAPHER_PT_PhysicalLightSpotPresets(PresetPanel, Panel):
	bl_label = 'Physical Spot Light Presets'
	preset_subdir = 'photographer/physical_lights/spot'
	preset_operator = 'script.execute_preset'
	preset_add_operator = 'photographer.physical_light_add_spot_preset'
	
	@classmethod
	def poll(cls,context):
		return bpy.context.light.type == 'SPOT'
		
class PHOTOGRAPHER_PT_PhysicalLightAreaPresets(PresetPanel, Panel):
	bl_label = 'Physical Light Area Presets'
	preset_subdir = 'photographer/physical_lights/area'
	preset_operator = 'script.execute_preset'
	preset_add_operator = 'photographer.physical_light_add_area_preset'
	
	@classmethod
	def poll(cls,context):
		return bpy.context.light.type == 'AREA'