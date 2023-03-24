bl_info = {
	"name": "Photographer",
	"description": "Adds Exposure, White Balance, Resolution and Autofocus controls to your camera",
	"author": "Fabien 'chafouin' Christin, @fabienchristin",
	"version": (3, 0, 2),
	"blender": (2, 83, 0),
	"location": "View3D > Side Panel > Photographer",
	"support": "COMMUNITY",
	"category": "Camera"}

import bpy, os, shutil

from bpy.props import  PointerProperty

from . import (
	autofocus,
	camera,
	camera_presets,
	light,
	functions,
	master_camera,
	prefs,
	white_balance,
	camera_panel,
	light_panel,
	light_presets,
	render_panel,
)


classes = (
	# Settings
	camera.PhotographerCameraSettings,
	light.PhotographerLightSettings,
	
	# Camera Operators
	camera.PHOTOGRAPHER_OT_MakeCamActive,
	camera.PHOTOGRAPHER_OT_UpdateSettings,
	camera.PHOTOGRAPHER_OT_SelectActiveCam,
	camera.PHOTOGRAPHER_OT_SetShutterAngle,
	camera.PHOTOGRAPHER_OT_SetShutterSpeed,
	camera.PHOTOGRAPHER_OT_RenderMotionBlur,
	white_balance.PHOTOGRAPHER_OT_WBReset,
	white_balance.PHOTOGRAPHER_OT_WBPicker,
	autofocus.PHOTOGRAPHER_OT_FocusSingle,
	autofocus.PHOTOGRAPHER_OT_FocusTracking,
	autofocus.PHOTOGRAPHER_OT_FocusTracking_Cancel,
	autofocus.PHOTOGRAPHER_OT_CheckFocusObject,
	master_camera.MASTERCAMERA_OT_LookThrough,
	master_camera.MASTERCAMERA_OT_SelectCamera,
	master_camera.MASTERCAMERA_OT_SwitchCamera,
	master_camera.MASTERCAMERA_OT_AddMasterCamera,
	master_camera.MASTERCAMERA_OT_AddCamera,
	master_camera.MASTERCAMERA_OT_DeleteCamera,
	master_camera.MASTERCAMERA_OT_DeleteMasterCamera,
	
	# Camera UI
	camera_panel.PHOTOGRAPHER_PT_Panel,
	camera_panel.PHOTOGRAPHER_PT_Panel_Exposure,
	camera_panel.PHOTOGRAPHER_PT_Panel_WhiteBalance,
	camera_panel.PHOTOGRAPHER_PT_Panel_Resolution,
	camera_panel.PHOTOGRAPHER_PT_Panel_Autofocus,
	camera_panel.MASTERCAMERA_PT_ViewPanel,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_Camera,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_Exposure,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_Autofocus,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_WhiteBalance,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_Resolution,
	
	# Camera Presets
	camera_presets.PHOTOGRAPHER_MT_CameraPresets,
	camera_presets.PHOTOGRAPHER_OT_AddCameraPreset,
	camera_presets.PHOTOGRAPHER_PT_CameraPresets,
	
	# Light Presets
	light_presets.PHOTOGRAPHER_PT_PhysicalLightPointPresets,
	light_presets.PHOTOGRAPHER_PT_PhysicalLightSunPresets,
	light_presets.PHOTOGRAPHER_PT_PhysicalLightSpotPresets,
	light_presets.PHOTOGRAPHER_PT_PhysicalLightAreaPresets,
	light_presets.PHOTOGRAPHER_OT_AddPointPreset,
	light_presets.PHOTOGRAPHER_OT_AddSunPreset,
	light_presets.PHOTOGRAPHER_OT_AddSpotPreset,
	light_presets.PHOTOGRAPHER_OT_AddAreaPreset,
	light_presets.PHOTOGRAPHER_MT_PhysicalLightPointPresets,
	light_presets.PHOTOGRAPHER_MT_PhysicalLightSunPresets,
	light_presets.PHOTOGRAPHER_MT_PhysicalLightSpotPresets,
	light_presets.PHOTOGRAPHER_MT_PhysicalLightAreaPresets,
	
	# Light UI
	light_panel.PHOTOGRAPHER_PT_Panel_Light,
	light_panel.PHOTOGRAPHER_PT_EEVEE_light_distance,
	light_panel.PHOTOGRAPHER_PT_spot,
	light_panel.PHOTOGRAPHER_OT_CalculateLightSize,
	light_panel.PHOTOGRAPHER_OT_CopySpotSize,
	light_panel.PHOTOGRAPHER_OT_SwitchColorMode,
	
	# Render UI
	render_panel.PHOTOGRAPHER_OT_UpdateLightThreshold,

)

def eevee_light_panel_poll(cls,context):
	return (bpy.context.preferences.addons[__package__].preferences.show_default_light_panels or not bpy.context.preferences.addons[__package__].preferences.use_physical_lights) and (context.light) and (context.engine in {'BLENDER_EEVEE'})
		
def eevee_light_distance_poll(cls,context):
	return (bpy.context.preferences.addons[__package__].preferences.show_default_light_panels or not bpy.context.preferences.addons[__package__].preferences.use_physical_lights) and (context.light and context.light.type != 'SUN')  and (context.engine in {'BLENDER_EEVEE'})

def spot_panel_poll(cls,context):
	return (bpy.context.preferences.addons[__package__].preferences.show_default_light_panels or not bpy.context.preferences.addons[__package__].preferences.use_physical_lights) and (context.light and context.light.type == 'SPOT')  and (context.engine in {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'})

def area_panel_poll(cls,context):
	return (bpy.context.preferences.addons[__package__].preferences.show_default_light_panels or not bpy.context.preferences.addons[__package__].preferences.use_physical_lights) and (context.light and context.light.type == 'AREA')  and (context.engine in {'BLENDER_RENDER', 'BLENDER_WORKBENCH'})

def light_panel_poll(cls,context):
	return (bpy.context.preferences.addons[__package__].preferences.show_default_light_panels or not bpy.context.preferences.addons[__package__].preferences.use_physical_lights) and (context.engine in {'BLENDER_RENDER', 'BLENDER_WORKBENCH'})
	
def cycles_light_panel_poll(cls,context):
	return (bpy.context.preferences.addons[__package__].preferences.show_default_light_panels or not bpy.context.preferences.addons[__package__].preferences.use_physical_lights) and (context.light) and (context.engine in {'CYCLES'})
		
def cycles_spot_panel_poll(cls,context):
	return (bpy.context.preferences.addons[__package__].preferences.show_default_light_panels or not bpy.context.preferences.addons[__package__].preferences.use_physical_lights) and (context.light and context.light.type == 'SPOT') and (context.engine in {'CYCLES'})	


def listfiles(path):
	files = []
	for dirName, subdirList, fileList in os.walk(path):
		# print(dirName)
		# print(subdirList)
		# print(fileList)
		dir = dirName.replace(path, '')
		for fname in fileList:
			files.append(os.path.join(dir, fname))
	return files

def register():
	
	# Installing bundled presets if they don't exist
	presets_folder = bpy.utils.user_resource('SCRIPTS', "presets")
	photographer_presets_folder = os.path.join(presets_folder, 'photographer')
	# Create presets folder if it doesn't exist
	if not os.path.exists(photographer_presets_folder):
		os.makedirs(photographer_presets_folder, exist_ok=True)
	# Check what's in the presets folder
	destination = listfiles(photographer_presets_folder)
	
	
	addon_folder = bpy.utils.user_resource('SCRIPTS', "addons")
	bundled_presets_folder = os.path.join(addon_folder, 'photographer','presets')
	# Check what's in the add-on presets folder
	source = listfiles(bundled_presets_folder)
	
	# Compare the folders
	difference = set(source) - set(destination)
	if len(difference) != 0:
		print('Photographer will install bundled Cameras and Physical Lights presets:' + str(difference))
		
	for f in difference:
		file = os.path.join(bundled_presets_folder, f[1:])
		dest_file = os.path.join(photographer_presets_folder, f[1:])
		dest_folder = os.path.dirname(dest_file)
		if not os.path.exists(dest_folder):
			os.makedirs(dest_folder,exist_ok=True)

		shutil.copy2(file, dest_folder)

	
	from bpy.utils import register_class, unregister_class
	from bpy.types import (
		DATA_PT_EEVEE_light,
		DATA_PT_EEVEE_light_distance,
		DATA_PT_spot,
		DATA_PT_area,
		DATA_PT_light,
		DATA_PT_EEVEE_shadow,
		DATA_PT_EEVEE_shadow_cascaded_shadow_map,
		DATA_PT_EEVEE_shadow_contact,
		CYCLES_LIGHT_PT_light,
		CYCLES_LIGHT_PT_nodes,
		CYCLES_LIGHT_PT_spot,
		DATA_PT_custom_props_light
	)
	
	# Unregistering light panels to place Physical Light panel
	light_classes=(
		DATA_PT_EEVEE_shadow,
		DATA_PT_EEVEE_shadow_cascaded_shadow_map,
		DATA_PT_EEVEE_shadow_contact,
		CYCLES_LIGHT_PT_nodes,
		CYCLES_LIGHT_PT_spot,
		DATA_PT_custom_props_light,
	)
	
	for cls in light_classes:
		unregister_class(cls)
	
	# Registering classes
	for cls in classes:
		register_class(cls)
		
	# Registering Panel classes	- Preferences sets bl_category
	context = bpy.context
	preferences = context.preferences.addons[__name__].preferences
	prefs.update_photographer_category(preferences,context)

	# Change polls to hide or show default light panels
	DATA_PT_EEVEE_light.poll = classmethod(eevee_light_panel_poll)
	DATA_PT_EEVEE_light_distance.poll = classmethod(eevee_light_distance_poll)
	DATA_PT_spot.poll = classmethod(spot_panel_poll)
	DATA_PT_area.poll = classmethod(area_panel_poll)
	DATA_PT_light.poll = classmethod(light_panel_poll)
	CYCLES_LIGHT_PT_light.poll = classmethod(cycles_light_panel_poll)
	CYCLES_LIGHT_PT_spot.poll = classmethod(cycles_spot_panel_poll)
	
	bpy.types.Camera.photographer = PointerProperty(type=camera.PhotographerCameraSettings)
	bpy.types.Light.photographer = PointerProperty(type=light.PhotographerLightSettings)
	bpy.types.CYCLES_RENDER_PT_sampling_advanced.append(render_panel.light_threshold_button)
	bpy.types.RENDER_PT_eevee_shadows.append(render_panel.light_threshold_button)

	if bpy.context.preferences.addons[__package__].preferences.show_af_buttons_pref:
		bpy.types.VIEW3D_HT_header.append(autofocus.focus_single_button)
		bpy.types.VIEW3D_HT_header.append(autofocus.focus_continuous_button)
		bpy.types.VIEW3D_HT_header.append(autofocus.focus_animate_button)
		bpy.types.VIEW3D_HT_header.append(autofocus.focus_tracking_button)
		bpy.types.VIEW3D_HT_header.append(autofocus.focus_distance_header)
		bpy.types.VIEW3D_HT_header.append(camera.lock_camera_button)


	# Registrering light panels again
	for cls in light_classes:
		register_class(cls)
	

def revert_eevee_light_panel_poll(cls,context):
	return (context.engine in {'BLENDER_EEVEE'})
	
def revert_eevee_light_distance_poll(cls,context):
	return (context.light and context.light.type != 'SUN')  and (context.engine in {'BLENDER_EEVEE'})

def revert_spot_panel_poll(cls,context):	
	return (context.light and context.light.type == 'SPOT')  and (context.engine in {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'})
	
def revert_area_panel_poll(cls,context):
	return (context.light and context.light.type == 'AREA')  and (context.engine in {'BLENDER_RENDER', 'BLENDER_WORKBENCH'})

def revert_light_panel_poll(cls,context):	
	return (context.engine in {'BLENDER_RENDER', 'BLENDER_WORKBENCH'})

def revert_cycles_light_panel_poll(cls,context):
	return (context.light) and (context.engine in {'CYCLES'})	
	
def revert_cycles_spot_panel_poll(cls,context):
	return (context.light and context.light.type == 'SPOT') and (context.engine in {'CYCLES'})	

####	

def unregister():
	from bpy.utils import unregister_class, register_class
	from bpy.types import (
		DATA_PT_EEVEE_light,
		DATA_PT_EEVEE_light_distance,
		DATA_PT_spot,
		DATA_PT_area,
		DATA_PT_light,
		CYCLES_LIGHT_PT_light,
		CYCLES_LIGHT_PT_spot,
	)

	DATA_PT_EEVEE_light.poll = classmethod(revert_eevee_light_panel_poll)
	DATA_PT_EEVEE_light_distance.poll = classmethod(revert_eevee_light_distance_poll)
	DATA_PT_spot.poll = classmethod(revert_spot_panel_poll)
	DATA_PT_area.poll = classmethod(revert_area_panel_poll)
	DATA_PT_light.poll = classmethod(revert_light_panel_poll)
	CYCLES_LIGHT_PT_light.poll = classmethod(revert_cycles_light_panel_poll)
	CYCLES_LIGHT_PT_spot.poll = classmethod(revert_cycles_spot_panel_poll)

	if bpy.context.preferences.addons[__package__].preferences.show_af_buttons_pref:
		bpy.types.VIEW3D_HT_header.remove(autofocus.focus_single_button)
		bpy.types.VIEW3D_HT_header.remove(autofocus.focus_continuous_button)
		bpy.types.VIEW3D_HT_header.remove(autofocus.focus_animate_button)
		bpy.types.VIEW3D_HT_header.remove(autofocus.focus_tracking_button)
		bpy.types.VIEW3D_HT_header.remove(autofocus.focus_distance_header)
		bpy.types.VIEW3D_HT_header.append(camera.lock_camera_button)
		
	bpy.types.CYCLES_RENDER_PT_sampling_advanced.remove(render_panel.light_threshold_button)

	for cls in classes:
		unregister_class(cls)
	del bpy.types.Camera.photographer
	del bpy.types.Light.photographer

	# unregister_class (prefs.AddonPreferences)