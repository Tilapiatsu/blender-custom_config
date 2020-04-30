import bpy
import math
from bpy.props import (BoolProperty,
					   FloatProperty,
					   EnumProperty,
					   FloatVectorProperty,
					   )

from . import (
	autofocus,
	functions,
	prefs,
	)
	
# Default Global variables
min_color_temperature = 2000
max_color_temperature = 14000
default_color_temperature = 6500
min_color_tint = -100
max_color_tint = 100
default_tint = 0
stored_cm_view_transform = 'Filmic'

# Creating Color Temperature to RGB look up tables from http://www.vendian.org/mncharity/dir3/blackbody/UnstableURLs/bbr_color.html
# Using 6500 as default white: purposefully changed 255,249,251 to 255,255,255
color_temperature_red = ((1000, 255),(1200,255),(1400,255),(1600,255),(1800,255),(2000, 255),(2200,255),(2400,255),(2700,255),(3000,255),(3300,255),(3600,255),(3900,255),(4300,255),(5000,255),(6000,255),(6500, 255),(7000,245),(8000,227),(9000,214),(10000,204),(11000,196),(12000,191),(13000,120),(14000, 30))
color_temperature_green = ((1000, 56),(1200,83),(1400,101),(1600,115),(1800,126),(2000,137),(2200,147),(2400,157),(2700,169),(3000,180),(3300,190),(3600,199),(3900,206),(4300,219),(5000,228),(6000,243),(6500, 255),(7000,243),(8000,233),(9000,225),(10000,219),(11000,215),(12000,211),(13000,200),(14000, 100))
color_temperature_blue = ((1000, 0),(1200,0),(1400,0),(1600,0),(1800,0),(2000,18),(2200,44),(2400,63),(2700,87),(3000,107),(3300,126),(3600,143),(3900,159),(4300,175),(5000,206),(6000,239),(6500, 255),(7000,255),(8000,255),(9000,255),(10000,255),(11000,255),(12000,255),(13000,255),(14000,255))

class InterpolatedArray(object):
  # An array-like object that provides interpolated values between set points.

	def __init__(self, points):
		self.points = sorted(points)

	def __getitem__(self, x):
		if x < self.points[0][0] or x > self.points[-1][0]:
			raise ValueError
		lower_point, upper_point = self._GetBoundingPoints(x)
		return self._Interpolate(x, lower_point, upper_point)

	def _GetBoundingPoints(self, x):
	#Get the lower/upper points that bound x.
		lower_point = None
		upper_point = self.points[0]
		for point  in self.points[1:]:
			lower_point = upper_point
			upper_point = point
			if x <= upper_point[0]:
				break
		return lower_point, upper_point

	def _Interpolate(self, x, lower_point, upper_point):
	#Interpolate a Y value for x given lower & upper bounding points.
		slope = (float(upper_point[1] - lower_point[1]) / (upper_point[0] - lower_point[0]))
		return lower_point[1] + (slope * (x - lower_point[0]))


bpy.utils.register_class (prefs.AddonPreferences)

#Camera Exposure update functions ##############################################################

def update_settings(self,context):

	if context.scene.camera:
		settings = context.scene.camera.data.photographer

		if bpy.context.scene.render.engine == 'LUXCORE':
			tonemapper = context.scene.camera.data.luxcore.imagepipeline.tonemapper

			if settings.exposure_enabled:
				tonemapper.enabled = True
				tonemapper.type = 'TONEMAP_LINEAR'
				tonemapper.linear_scale = 1/683

		if settings.exposure_enabled:
			update_aperture(self, context)
			update_shutter_speed(self, context)
			update_iso(self, context)
			update_shutter_angle(self, context)
			update_falsecolor(self,context)

		if context.scene.camera.data.dof.focus_distance == 0:
			context.scene.camera.data.dof.focus_distance = 3

		if settings.resolution_enabled:
			update_resolution(self,context)

		if context.scene.view_settings.use_curve_mapping:
			settings.color_temperature = settings.color_temperature
			settings.tint = settings.tint
			set_tint_color(self,context)

		if settings.exposure_enabled == False:
				context.scene.view_settings.exposure = 0

# Update EV
def update_ev(self,context):
	settings = context.scene.camera.data.photographer
	EV = functions.calc_exposure_value(self,context,settings)
	
	bl_exposure = -EV+9.416 #Applying the 683 lm/W conversion (2^9.416 = 683)
	
	if bpy.context.preferences.addons[__package__].preferences.aces_ue_match and context.scene.display_settings.display_device == 'ACES' and context.scene.view_settings.view_transform != 'Raw':
		# Blender ACES is darker than Unreal ACES, even after 4.25 exposure changes. 1/0.65 = 2^0.621
		bl_exposure += 0.621
	
	bl_exposure -= math.log2(0.78/bpy.context.preferences.addons[__package__].preferences.lens_attenuation)
	
	context.scene.view_settings.exposure = bl_exposure

# Update Aperture
def update_aperture(self, context):
	settings = context.scene.camera.data.photographer

	if bpy.context.scene.render.engine == 'LUXCORE':
		use_dof = context.scene.camera.data.luxcore.use_dof
	else:
		 use_dof = context.scene.camera.data.dof.use_dof


	if use_dof :
		# if context.scene.camera == context.view_layer.objects.active:
		if not settings.aperture_slider_enable:
			if bpy.context.scene.render.engine == 'LUXCORE':
				context.scene.camera.data.luxcore.fstop = float(settings.aperture_preset) * context.scene.unit_settings.scale_length
			else:
				context.scene.camera.data.dof.aperture_fstop = float(settings.aperture_preset) * context.scene.unit_settings.scale_length
		else:
			if bpy.context.scene.render.engine == 'LUXCORE':
				context.scene.camera.data.luxcore.fstop = settings.aperture * context.scene.unit_settings.scale_length
			else:
				context.scene.camera.data.dof.aperture_fstop = settings.aperture * context.scene.unit_settings.scale_length

	update_ev(self, context)

# Update Shutter Speed
def update_shutter_speed(self,context):
	scene = bpy.context.scene
	settings = context.scene.camera.data.photographer
	if settings.shutter_mode == 'SPEED':
		fps = scene.render.fps / scene.render.fps_base
		if not settings.shutter_speed_slider_enable:
			settings.shutter_angle = (fps * 360) / float(settings.shutter_speed_preset)
		else:
			settings.shutter_angle = (fps * 360) / settings.shutter_speed
		if settings.motionblur_enabled:
				scene.render.motion_blur_shutter = settings.shutter_angle / 360
				# Matching Eevee to Cycles
				scene.eevee.motion_blur_shutter = scene.render.motion_blur_shutter

	if settings.exposure_mode == 'MANUAL':
		update_ev(self, context)


def update_shutter_angle(self,context):
	scene = bpy.context.scene
	settings = context.scene.camera.data.photographer
	if settings.shutter_mode == 'ANGLE':
		fps = scene.render.fps / scene.render.fps_base

		if not settings.shutter_speed_slider_enable:
			shutter_angle = float(settings.shutter_angle_preset)
		else:
			shutter_angle = settings.shutter_angle

		settings.shutter_speed = 1 / (shutter_angle / 360) * fps

		if settings.motionblur_enabled:
			if scene.render.engine == 'Cycles':
				scene.render.motion_blur_shutter = shutter_angle / 360
				# Matching Eevee to Cycles
				scene.eevee.motion_blur_shutter = scene.render.motion_blur_shutter

	if settings.exposure_mode == 'MANUAL':
		update_ev(self, context)

# Update ISO
def update_iso(self, context):
	update_ev(self, context)


def update_falsecolor(self,context):
	settings = context.scene.camera.data.photographer

	if context.scene.view_settings.view_transform != 'False Color':
		global stored_cm_view_transform
		stored_cm_view_transform = context.scene.view_settings.view_transform
		# print (stored_cm_view_transform)

	if settings.falsecolor_enabled:
		context.scene.view_settings.view_transform = 'False Color'

	else:
		context.scene.view_settings.view_transform = stored_cm_view_transform

# Update Resolution
def update_resolution(self,context):
	settings = context.scene.camera.data.photographer

	resolution_x = 1920
	resolution_x = 1080

	if settings.resolution_mode == 'CUSTOM_RES':
		resolution_x = settings.resolution_x
		resolution_y = settings.resolution_y
		
	if settings.resolution_mode == 'CUSTOM_RATIO':
		resolution_x = settings.resolution_x 
		resolution_y = settings.resolution_x * (settings.ratio_y / settings.ratio_x)

	if settings.resolution_mode == '11':
		resolution_x = settings.longedge
		resolution_y = resolution_x

	if settings.resolution_mode == '32':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/3)*2

	if settings.resolution_mode == '43':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/4)*3

	if settings.resolution_mode == '67':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/7)*6

	if settings.resolution_mode == '169':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/16)*9

	if settings.resolution_mode == '169':
		resolution_x = settings.longedge
		resolution_y = (settings.longedge/16)*9

	if settings.resolution_mode == '2351':
		resolution_x = settings.longedge
		resolution_y = settings.longedge/2.35

	if settings.resolution_rotation == 'LANDSCAPE':
		context.scene.render.resolution_x = resolution_x
		context.scene.render.resolution_y = resolution_y

	if settings.resolution_rotation == 'PORTRAIT':
		context.scene.render.resolution_x = resolution_y
		context.scene.render.resolution_y = resolution_x

def get_color_temperature_color_preview(self):
	def_k = convert_temperature_to_RGB_table(default_color_temperature)
	# inverting
	def_k = (def_k[2],def_k[1],def_k[0])
	photographer = bpy.context.scene.camera.data.photographer

	# Convert Temperature to Color
	white_balance_color = convert_temperature_to_RGB_table(photographer.color_temperature)
	# Set preview color in the UI - inverting red and blue channels
	self['preview_color'] = (white_balance_color[2],white_balance_color[1],white_balance_color[0])
	return self.get('preview_color', def_k)

def set_color_temperature_color(self, context):
	photographer = bpy.context.scene.camera.data.photographer

	# Convert Temperature to Color
	white_balance_color = convert_temperature_to_RGB_table(photographer.color_temperature)

	# if context.scene.camera == context.view_layer.objects.active:
		# Calculate Curves values from color - ignoring green which is set by the Tint
	red = white_balance_color[0]
	blue = white_balance_color[2]
	average = (red + blue) / 2

	# Apply values to Red and Blue white levels
	context.scene.view_settings.curve_mapping.white_level[0] = red / average
	context.scene.view_settings.curve_mapping.white_level[2] = blue / average

	#Little trick to update viewport as Color Management Curves don't update automatically
	exposure = bpy.context.scene.view_settings.exposure
	bpy.context.scene.view_settings.exposure = exposure

def get_tint_preview_color(self):
	photographer = bpy.context.scene.camera.data.photographer

	# Set preview color in the UI
	self['preview_color_tint'] = convert_tint_to_color_preview(photographer.tint)
	def_tint = convert_tint_to_color_preview(default_tint)
	return self.get('preview_color_tint', def_tint)

def set_tint_color(self, context):
	photographer = context.scene.camera.data.photographer

	if photographer.tint < 0:
		tint_curve_mult = photographer.tint / 200 + 1 # Diving by 200 instead of 100 to avoid green level to go lower than 0.5. Gives more precision to the slider.
	else:
		tint_curve_mult = photographer.tint / 50 + 1  # Diving by 50 to avoid green level to go higher than 3. Gives more precision to the slider.

	# Apply value to Green white level
	bpy.context.scene.view_settings.curve_mapping.white_level[1] = tint_curve_mult

	#Little trick to update viewport as Color Management Curves don't update automatically
	exposure = bpy.context.scene.view_settings.exposure
	bpy.context.scene.view_settings.exposure = exposure

def convert_temperature_to_RGB_table(color_temperature):

	# Interpolate Tables
	table_red = InterpolatedArray(color_temperature_red)
	table_green = InterpolatedArray(color_temperature_green)
	table_blue = InterpolatedArray(color_temperature_blue)

	# Convert Temperature to RGB using the look up tables
	red = table_red[color_temperature]
	green = table_green[color_temperature]
	blue = table_blue[color_temperature]

	return (red / 255, green / 255, blue / 255)

def convert_tint_to_color_preview(color_tint):
	red = 1.0
	green = 1.0
	blue = 1.0

	if color_tint < 0:
		red = red + color_tint / 150 # Dividing with 150. Not an accurate match to the actual Tint math, purposefully different so the preview color is pleasing
		blue = blue + color_tint / 150

	if color_tint > 0:
		green = green - color_tint / 150

	return red, green, blue

def update_af_continuous(self,context):
	settings = context.scene.camera.data.photographer
	if settings.af_continuous_enabled:
		bpy.ops.photographer.check_focus_object()
		bpy.app.timers.register(autofocus.focus_continuous)
		if settings.af_animate:
			bpy.app.handlers.frame_change_pre.append(stop_playback)
	else:

		if bpy.app.timers.is_registered(autofocus.focus_continuous):
			bpy.app.timers.unregister(autofocus.focus_continuous)

def update_sensor_size(self,context):
	camera = context.scene.camera.data
	settings = context.scene.camera.data.photographer
	
	if camera.sensor_fit == "VERTICAL":
		camera.sensor_fit = "HORIZONTAL"
	if settings.sensor_type != 'CUSTOM':
		camera.sensor_width = float(settings.sensor_type)

def lock_camera_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA' :
						if area.spaces[0].lock_camera:
							icon="LOCKVIEW_ON"
						else:
							icon="LOCKVIEW_OFF"
						self.layout.prop(area.spaces[0], "lock_camera", text="", icon=icon )
						

class PHOTOGRAPHER_OT_MakeCamActive(bpy.types.Operator):
	bl_idname = "photographer.makecamactive"
	bl_label = "Make Camera Active"
	bl_description = "Make this Camera the active camera in the Scene"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.context.scene.camera = bpy.context.active_object
		update_settings(self,context)
		return{'FINISHED'}

class PHOTOGRAPHER_OT_UpdateSettings(bpy.types.Operator):
	bl_idname = "photographer.updatesettings"
	bl_label = "Update Settings"
	bl_description = "If you changed DoF, Framerate, Resolution or Curves settings outside of the Photographer addon, reapply the settings to make sure they are up to date"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		update_settings(self,context)
		return{'FINISHED'}

class PHOTOGRAPHER_OT_SelectActiveCam(bpy.types.Operator):
	bl_idname = "photographer.selectactivecam"
	bl_label = "Select Active Camera"
	bl_description = "Select the Active Camera in the Scene"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.data.objects[context.scene.camera.name].select_set(True)
		context.view_layer.objects.active = context.scene.camera

		return{'FINISHED'}

class PHOTOGRAPHER_OT_SetShutterAngle(bpy.types.Operator):
	bl_idname = "photographer.setshutterangle"
	bl_label = "Switch to Shutter Angle"
	bl_description = "Switch to Shutter Angle"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		try:
			context.camera.photographer.shutter_mode = 'ANGLE'
		except AttributeError:
			context.scene.camera.data.photographer.shutter_mode = 'ANGLE'
		update_settings(self,context)
		return{'FINISHED'}

class PHOTOGRAPHER_OT_SetShutterSpeed(bpy.types.Operator):
	bl_idname = "photographer.setshutterspeed"
	bl_label = "Switch to Shutter Speed"
	bl_description = "Switch to Shutter Speed"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		try:
			context.camera.photographer.shutter_mode = 'SPEED'
		except AttributeError:
			context.scene.camera.data.photographer.shutter_mode = 'SPEED'
		update_settings(self,context)
		return{'FINISHED'}

class PHOTOGRAPHER_OT_RenderMotionBlur(bpy.types.Operator):
	bl_idname = "photographer.rendermotionblur"
	bl_label = "Enable Motion Blur render"
	bl_description = "Enable Motion Blur in the Render Settings"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		context.scene.render.use_motion_blur = True
		context.scene.eevee.use_motion_blur = True
		return{'FINISHED'}


class PhotographerCameraSettings(bpy.types.PropertyGroup):

	sensor_type : bpy.props.EnumProperty(
		name = "Sensor Type",
		description = "Camera Sensor Size",
		items = [('CUSTOM','Custom',''),('5.79','Super 8',''),('12.52','Super 16','12.52'),('13.20','1 inch',''),('18','Micro Four Third',''),('23.6','APS-C',''),('24.89','Super 35',''),('36','Fullframe 35mm',''),('54.12','ARRI Alexa 65',''),('56','Medium Format 6x6',''),('84','Medium Format 6x9','')],
		default = '36',
		update = update_sensor_size
	)

	exposure_enabled : bpy.props.BoolProperty(
		name = "Enable Exposure Controls",
		default = True,
		update = update_settings
	)
	dof_enabled : bpy.props.BoolProperty(
		name = "Enable Depth of Field control",
		description = "Depth of Field will be controlled by the Aperture Value",
		default = True,
		update = update_settings
	)
	motionblur_enabled : bpy.props.BoolProperty(
		name = "Enable Motion Blur control",
		description = "Motion Blur will be controlled by the Shutter Speed / Shutter Angle values",
		default = False,
		update = update_settings
	)

	# Exposure properties
	exposure_mode : bpy.props.EnumProperty(
		name = "Exposure Mode",
		description = "Choose the Exposure Mode",
		items = [('EV','EV', ''),('MANUAL','Manual','')],
		default = bpy.context.preferences.addons[__package__].preferences.exposure_mode_pref if bpy.context.preferences.addons[__package__].preferences.exposure_mode_pref else 'EV',
		update = update_settings
	)
	ev : bpy.props.FloatProperty(
		name = "Exposure Value",
		description = "Exposure Value: look at the Chart",
		soft_min = -6,
		soft_max = 16,
		step = 1,
		precision = 2,
		default = 9.416 - math.log2(0.78 / bpy.context.preferences.addons[__package__].preferences.lens_attenuation),
		update = update_ev
	)
	exposure_compensation : bpy.props.FloatProperty(
		name = "Exposure Compensation",
		description = "Exposure Value: look at the Chart",
		soft_min = -3,
		soft_max = 3,
		step = 1,
		precision = 2,
		default = 0,
		update = update_ev
	)
	falsecolor_enabled : bpy.props.BoolProperty(
		name = "Enable False Color view transform to validate your exposure",
		default = False,
		update = update_settings
	)

	# Shutter Speed properties
	shutter_mode : bpy.props.EnumProperty(
		name = "Shutter Mode",
		description = "Choose the Shutter Mode",
		items = [('SPEED','Shutter Speed',''),('ANGLE','Shutter Angle', '')],
		default = 'SPEED',
		update = update_settings
	)
	shutter_speed : bpy.props.FloatProperty(
		name = "Shutter Speed 1/X second",
		description = "Shutter Speed - controls the amount of Motion Blur",
		soft_min = 0.1,
		soft_max = 1000,
		precision = 2,
		default = 100,
		update = update_shutter_speed
	)
	shutter_speed_slider_enable : bpy.props.BoolProperty(
		name = "Shutter Speed Slider",
		description = "Enable Shutter Speed slider instead of preset list",
		default = bpy.context.preferences.addons[__package__].preferences.shutter_speed_slider_pref if bpy.context.preferences.addons[__package__].preferences.shutter_speed_slider_pref else False,
		update = update_shutter_speed
	)
	shutter_speed_preset : bpy.props.EnumProperty(
		name = "Shutter Speed",
		description = "Camera Shutter Speed",
		items = [('0.033','30 "',''),('0.04','25 "',''),('0.05','20 "',''),('0.066','15 "',''),('0.077','13 "',''),('0.1','10 "',''),('0.125','8 "',''),('0.1666','6 "',''),('0.2','5 "',''),('0.25','4 "',''),('0.3125','3.2 "',''),('0.4','2.5 "',''),
		('0.5','2 "',''),('0.625','1.6 "',''),('0.769','1.3 "',''),('1','1 "',''),('1.25','0.8 "',''),('1.666','0.6 "',''),('2','0.5 "',''),('2.5','0.4 "',''),('3.333','0.3 "',''),('4','1 / 4 s',''),('5','1 / 5 s',''),('6','1 / 6 s',''),
		('8','1 / 8 s',''),('10','1 / 10 s',''),('13','1 / 13 s',''),('15','1 / 15 s',''),('20','1 / 20 s',''),('25','1 / 25 s',''),('30','1 / 30 s',''),('40','1 / 40 s',''),('50','1 / 50 s',''),('60','1 / 60 s',''),('80','1 / 80 s',''),
		('100','1 / 100 s',''),('125','1 / 125 s',''),('160','1 / 160 s',''),('200','1 / 200 s',''),('250','1 / 250 s',''),('320','1 / 320 s',''),('400','1 / 400 s',''),('500','1 / 500 s',''),('640','1 / 640 s',''),('800','1 / 800 s',''),
		('1000','1 / 1000 s',''),('1250','1 / 1250 s',''),('1600','1 / 1600 s',''),('2000','1 / 2000 s',''),('2500','1 / 2500 s',''),('3200','1 / 3200 s',''),('4000','1 / 4000 s',''),('5000','1 / 5000 s',''),('6400','1 / 6400 s',''),('8000','1 / 8000 s', '')],
		default = '100',
		update = update_shutter_speed
	)

	# Shutter Angle properties
	shutter_angle : bpy.props.FloatProperty(
		name = "Shutter Angle",
		description = "Shutter Angle in degrees - controls the Shutter Speed and amount of Motion Blur",
		soft_min = 1,
		soft_max = 360,
		precision = 1,
		default = 180,
		update = update_shutter_angle
	)
	shutter_angle_preset : bpy.props.EnumProperty(
		name = "Shutter Angle",
		description = "Camera Shutter Angle",
		items = [('8.6','8.6 degree',''),('11','11 degree',''),('22.5','22.5 degree',''),('45','45 degree',''),('72','72 degree',''),('90','90 degree',''),('144','144 degree',''),('172.8','172.8 degree',''),('180','180 degree',''),
		('270','270 degree',''),('360','360 degree','')],
		default = '180',
		update = update_shutter_angle
	)

	# Aperture properties
	aperture : bpy.props.FloatProperty(
		name = "Aperture F-stop",
		description = "Lens aperture - controls the Depth of Field",
		soft_min = 0.5,
		soft_max = 32,
		precision = 1,
		default = 2.4,
		update = update_aperture
	)
	aperture_slider_enable : bpy.props.BoolProperty(
		name = "Aperture Slider",
		description = "Enable Aperture slider instead of preset list",
		default = bpy.context.preferences.addons[__package__].preferences.aperture_slider_pref,
		update = update_aperture
	)
	aperture_preset : bpy.props.EnumProperty(
		name = "Lens Aperture Presets",
		description = "Lens Aperture",
		items = [('0.95','f / 0.95',''),('1.2','f / 1.2',''),('1.4','f / 1.4',''),('1.8','f / 1.8',''),('2.0','f / 2.0',''),('2.4','f / 2.4',''),('2.8','f / 2.8',''),('3.5','f / 3.5',''),('4.0','f / 4.0',''),('4.9','f / 4.9',''),('5.6','f / 5.6',''),
		('6.7','f / 6.7',''),('8.0','f / 8.0',''),('9.3','f / 9.3',''),('11','f / 11',''),('13','f / 13',''),('16','f / 16',''),('20','f / 20',''),('22','f / 22','')],
		default = '2.8',
		update = update_aperture
	)

	# ISO properties
	iso : bpy.props.IntProperty(
		name = "ISO",
		description = "ISO setting",
		soft_min = 50,
		soft_max = 12800,
		default = 100,
		update = update_iso
	)
	iso_slider_enable : bpy.props.BoolProperty(
		name = "Iso Slider",
		description = "Enable ISO setting slider instead of preset list",
		default = bpy.context.preferences.addons[__package__].preferences.iso_slider_pref,
		update = update_iso
	)
	iso_preset : bpy.props.EnumProperty(
		name = "Iso Presets",
		description = "Camera Sensitivity",
		items = [('100','100',''),('125','125',''),('160','160',''),('200','200',''),('250','250',''),('320','320',''),('400','400',''),('500','500',''),('640','640',''),('800','800',''),('1000','1000',''),('1250','1250',''),
		('1600','1600',''),('2000','2000',''),('2500','2500',''),('3200','3200',''),('4000','4000',''),('5000','5000',''),('6400','6400',''),('8000','8000',''),('10000','10000',''),('12800','12800',''),('16000','16000',''),
		('20000','20000',''),('25600','25600',''),('32000','32000',''),('40000','40000',''),('51200','51200','')],
		default = '100',
		update = update_iso
	)

	# White Balance properties
	color_temperature : bpy.props.IntProperty(
		name="Color Temperature", description="Color Temperature (Kelvin)",
		min=min_color_temperature, max=max_color_temperature, default=default_color_temperature,
		update=set_color_temperature_color
	)
	preview_color_temp : bpy.props.FloatVectorProperty(
		name='Preview Color', description="Color Temperature preview color",
		subtype='COLOR', min=0.0, max=1.0, size=3,
		get=get_color_temperature_color_preview,
		set=set_color_temperature_color
	)
	tint : bpy.props.IntProperty(
		name="Tint", description="Green or Magenta cast",
		min=min_color_tint, max=max_color_tint, default=default_tint,
		update=set_tint_color
	)
	preview_color_tint : bpy.props.FloatVectorProperty(
		name="Preview Color Tint", description="Tint preview color",
		subtype='COLOR', min=0.0, max=1.0, size=3,
		get=get_tint_preview_color,
		set=set_tint_color
	)

	# Resolution properties
	resolution_enabled : bpy.props.BoolProperty(
		name = "Enable Exposure Controls",
		default = False,
		update = update_resolution
	)
	resolution_mode : bpy.props.EnumProperty(
		name = "Resolution Mode",
		description = "Choose Custom Resolutions or Ratio presets",
		items = [('CUSTOM_RES','Custom Resolution',''),('CUSTOM_RATIO','Custom Ratio',''),('11','1:1', ''),('32','3:2', ''),('43','4:3', ''),('67','6:7', ''),('169','16:9', ''),('2351','2.35:1', '')],
		update = update_resolution
	)
	resolution_x : bpy.props.IntProperty(
		name="X", description="Horizontal Resolution",
		min=0, default=1920,subtype='PIXEL',
		update=update_resolution
	)
	resolution_y : bpy.props.IntProperty(
		name="Y", description="Vertical Resolution",
		min=0, default=1080, subtype='PIXEL',
		update=update_resolution
	)
	ratio_x : bpy.props.FloatProperty(
		name="X", description="Horizontal Ratio",
		min=0, default=16, precision=2,
		update=update_resolution
	)
	ratio_y : bpy.props.FloatProperty(
		name="Y", description="Vertical Ratio",
		min=0, default=9, precision=2,
		update=update_resolution
	)
	longedge : bpy.props.FloatProperty(
		name="Long Edge", description="Long Edge Resolution",
		min=0, default=1920, subtype='PIXEL',
		update=update_resolution
	)
	resolution_rotation : bpy.props.EnumProperty(
		name = "Orientation",
		description = "Choose the rotation of the camera",
		items = [('LANDSCAPE','Landscape',''),('PORTRAIT','Portrait', '')],
		update=update_resolution
	)

	# AF-C property
	af_continuous_enabled : bpy.props.BoolProperty(
		name = "AF-C",
		description = "Autofocus Continuous: Realtime focus on the center of the frame",
		default = False,
		update = update_af_continuous,
	)
	af_target : bpy.props.PointerProperty(
		type=bpy.types.Object,
		name="AF Tracking Target",
		description="The object which will be used for DoF focus."
	)
	af_continuous_interval : bpy.props.FloatProperty(
		name="AF-C interval", description="Number of seconds between each autofocus update",
		soft_min = 0.05,
		min = 0.01,
		soft_max = 3,
		precision = 2,
		default = 0.6,
		subtype='TIME'
	)
	af_tracking_enabled : bpy.props.BoolProperty(
		name = "AF-Track",
		description = "Autofocus Tracking: Place a tracker on an object and it will stay in focus",
		default = False,
	)
	af_animate : bpy.props.BoolProperty(
		name = "Animate Autofocus",
		description = "Set keys on focus distance when using AF-S and AF-C",
		default = False,
	)

	# Master Camera Settings
	match_speed : bpy.props.FloatProperty(
		name = "Transition Speed",
		description = "Speed at which it switches to the other camera. The higher the slower. 1 is instant",
		default = 10.0,
		min = 1.0,
		soft_max = 30.0,
	)
	is_matching : bpy.props.BoolProperty(
		name = "Is matchin camera",
		default = False,
	)
	target_camera : bpy.props.PointerProperty(
		type=bpy.types.Object,
		name="Target Camera",
		description="The camera that the Master Camera will match"
	)