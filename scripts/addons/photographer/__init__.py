bl_info = {
	"name": "Photographer",
	"description": "Adds Exposure, White Balance, Resolution and Autofocus controls to your camera",
	"author": "Fabien 'chafouin' Christin, @fabienchristin", 
	"version": (2, 1, 1),
	"blender": (2, 80, 0),
	"location": "Properties Editor > Data > Camera",
	"support": "COMMUNITY",
	"category": "Camera"}

import bpy
import os
import bgl
import math
import functools
from bpy_extras import view3d_utils
from bpy.props import (StringProperty,
					   BoolProperty,
					   IntProperty,
					   FloatProperty,
					   EnumProperty,
					   PointerProperty,
					   )
from bpy.types import (Panel,
					   Operator,
					   PropertyGroup,
					   AddonPreferences,
					   )
from mathutils import Vector
import functools
# from . import master_camera

# Global variables						 
min_color_temperature = 2000
max_color_temperature = 14000
default_color_temperature = 6500
min_color_tint = -100
max_color_tint = 100
default_tint = 0

# Creating Color Temperature to RGB look up tables from http://www.vendian.org/mncharity/dir3/blackbody/UnstableURLs/bbr_color.html
# Using 6500 as default white: purposefully changed 255,249,251 to 255,255,255
color_temperature_red = ((2000, 255),(2200,255),(2400,255),(2700,255),(3000,255),(3300,255),(3600,255),(3900,255),(4300,255),(5000,255),(6000,255),(6500, 255),(7000,247),(8000,229),(9000,217),(10000,207),(11000,200),(12000,195),(13000,120),(14000, 30))
color_temperature_green = ((2000,141),(2200,152),(2400,162),(2700,174),(3000,185),(3300,195),(3600,203),(3900,206),(4300,219),(5000,231),(6000,246),(6500, 255),(7000,243),(8000,233),(9000,225),(10000,218),(11000,213),(12000,209),(13000,200),(14000, 100))
color_temperature_blue = ((2000,11),(2200,41),(2400,60),(2700,84),(3000,105),(3300,124),(3600,141),(3900,159),(4300,175),(5000,204),(6000,237),(6500, 255),(7000,255),(8000,255),(9000,255),(10000,255),(11000,255),(12000,255),(13000,255),(14000,255))
temperature_ratio = ((23.1818,2000),(6.2195,2200),(4.25,2400),(3.0357,2700),(2.4286,3000),(2.0565,3300),(1.8085,3600),(1.6038,3900),(1.5839,4300),(1.25,5000),(1.0759,6000),(1,6500),(0.8980,8000),(0.851,9000),(0.8118,10000),(0.7843,11000),(0.7647,12000),(0.4706,13000),(0.1176,14000))
ev_lookup =	 ["Starlight","Aurora Borealis","Half Moon","Full Moon","Full Moon in Snowscape","Dim artifical light","Dim artifical light","Distant view of lit buildings","Distant view of lit buildings","Fireworks","Candle","Campfire","Home interior","Night Street","Office Lighting","Neon Signs","Skyline after Sunset","Sunset","Heavy Overcast","Bright Cloudy","Hazy Sun","Sunny","Bright Sun"]

class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__
																									  
	exposure_mode_pref : bpy.props.EnumProperty(
		name = "Default Exposure Mode",
		description = "Choose the default Exposure Mode",
		items = [('EV','EV', ''),('MANUAL','Manual','')],
		default = 'EV',
	)
	
	shutter_speed_slider_pref : bpy.props.BoolProperty(
		name = "Shutter Speed / Angle",
		description = "Use Slider for Shutter Speed / Angle",
		default = False
	)
	
	aperture_slider_pref : bpy.props.BoolProperty(
		name = "Aperture",
		description = "Use Slider for Aperture",
		default = False
	)
	
	iso_slider_pref : bpy.props.BoolProperty(
		name = "ISO",
		description = "Use Slider for ISO setting",
		default = False
	)
			
	def draw(self, context):
			layout = self.layout
			wm = bpy.context.window_manager
			
			box = layout.box()
			percentage_columns = 0.4
			# Default Exposure mode
			split = box.split(factor = percentage_columns)
			split.label(text = "Default Exposure Mode :")
			row = split.row(align=True)
			row.prop(self, 'exposure_mode_pref', expand=True)
			
			# Use camera values presets or sliders
			row = box.row(align=True)
			split = row.split(factor = percentage_columns)
			split.label(text = "Use Sliders instead of real Camera values for :")
			col = split.column()
			row = col.row()
			row.prop(self, 'shutter_speed_slider_pref')
			row.prop(self, 'aperture_slider_pref')
			row.prop(self, 'iso_slider_pref')
			layout.label(text="Changing these default values will take effect after saving the User Preferences and restarting Blender.")
			
			layout.separator()
			
			# Useful links

			box = layout.box()
			row = box.row(align=True)
			row.label(text='Useful links : ')
			row.operator("wm.url_open", text="Blender Artists Forum post").url = "https://blenderartists.org/t/addon-photographer-camera-exposure-white-balance-and-autofocus/1101721"
			row.operator("wm.url_open", text="Video Tutorials").url = "https://www.youtube.com/playlist?list=PLDS3IanhbCIXERthzS7cWG1lnGQwQq5vB"
			
 
bpy.utils.register_class (AddonPreferences)
 
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


class PHOTOGRAPHER_PT_Panel(bpy.types.Panel):
	# bl_idname = "CAMERA_PT_Photographer"
	bl_label = "Photographer"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"
	
	@classmethod	
	def poll(cls, context):
		# Add Panel properties to cameras
		return context.camera
		
	def draw(self, context):
		layout = self.layout
		settings = context.camera.photographer
		scene = bpy.context.scene
		
		# UI if camera isn't active
		if scene.camera != bpy.context.active_object:
			layout.label(text="This is not the Active Camera")

			row = layout.row()
			row.operator("photographer.makecamactive", text="Make Active Camera")
			row.operator("photographer.selectactivecam", text="Select Active Camera")

		col = layout.column()
		# Enable UI if Camera is Active
		if scene.camera != bpy.context.active_object:
			col.enabled = False

		col.operator("photographer.updatesettings", text="Apply all Settings")	   

class PHOTOGRAPHER_PT_Panel_Exposure(bpy.types.Panel):
	# bl_idname = "CAMERA_PT_Photographer_Exposure"
	bl_label = "Exposure"
	bl_parent_id = "PHOTOGRAPHER_PT_Panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"

	def draw_header_preset(self, context):
		layout = self.layout
		settings = context.camera.photographer
		layout.enabled = settings.exposure_enabled
		row = layout.row(align=False)
		row.alignment = 'RIGHT'

		ev = calc_exposure_value(self, context)
		ev = str("%.2f" % ev)
		ev_guide = update_exposure_guide(self, context)
		row.label(text = ev_guide + " - " + "EV: " + ev )

	def draw_header(self, context):

		settings = context.camera.photographer

		self.layout.prop(settings, "exposure_enabled", text="")
		

	def draw(self, context):
		layout = self.layout
		settings = context.camera.photographer
		scene = bpy.context.scene

		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.
		layout.enabled = settings.exposure_enabled

		layout.row().prop(settings, 'exposure_mode',expand=True)
		if settings.exposure_mode == 'EV':
			layout.prop(settings, 'ev', slider=True)


		# Settings in EV Mode
		if settings.exposure_mode == 'EV':

			# Shutter Speed parameter
			row = layout.row(align = True)
			row.enabled = settings.motionblur_enabled
			if settings.shutter_mode == 'SPEED':
				if not settings.shutter_speed_slider_enable:
					row.prop(settings, 'shutter_speed_preset', text='Shutter Speed')
				else:
					row.prop(settings, 'shutter_speed', slider=True)
				row.operator("photographer.setshutterangle",icon="DRIVER_ROTATIONAL_DIFFERENCE", text="")
				row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

			if settings.shutter_mode == 'ANGLE':
				if not settings.shutter_speed_slider_enable:
					row.prop(settings, 'shutter_angle_preset', text='Shutter Angle')
				else:
					row.prop(settings, 'shutter_angle', slider=True)
				row.operator("photographer.setshutterspeed",icon="PREVIEW_RANGE", text="")
				row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')
			
			# Aperture parameter
			row = layout.row(align = True)
			row.enabled = settings.dof_enabled
			if not settings.aperture_slider_enable:
				row.prop(settings, 'aperture_preset', text='Aperture')
			else:
				row.prop(settings, 'aperture', slider=True, text='Aperture F-stop')
			row.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')

		else:

			# Shutter Speed parameter
			if settings.shutter_mode == 'SPEED':
				row = layout.row(align = True)
				if not settings.shutter_speed_slider_enable:
					row.prop(settings, 'shutter_speed_preset', text='Shutter Speed')
				else:
					row.prop(settings, 'shutter_speed', slider=True)
				row.operator("photographer.setshutterangle",icon="DRIVER_ROTATIONAL_DIFFERENCE", text="")
				row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

			if settings.shutter_mode == 'ANGLE':
				row = layout.row(align = True)
				if not settings.shutter_speed_slider_enable:
					row.prop(settings, 'shutter_angle_preset', text='Shutter Angle')
				else:
					row.prop(settings, 'shutter_angle', slider=True)
				row.operator("photographer.setshutterspeed",icon="PREVIEW_RANGE", text="")
				row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')
				
			
			# Aperture parameter
			row = layout.row(align = True)
			if not settings.aperture_slider_enable:
				row.prop(settings, 'aperture_preset', text='Aperture')
			else:
				row.prop(settings, 'aperture', slider=True, text='Aperture F-stop / Depth of Field only')
			row.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')

			# ISO parameter
			row = layout.row(align = True)

			if not settings.iso_slider_enable:
				row.prop(settings, 'iso_preset', text='ISO')
			else:
				row.prop(settings, 'iso', slider=True)
			row.prop(settings,'iso_slider_enable', icon='SETTINGS', text='')
			
		col = layout.column(align=False)
		col.prop(settings, 'motionblur_enabled', text='Affect Motion Blur')

		# Check if the Motion Blur is enabled in the Render Settings	
		if settings.motionblur_enabled and not scene.render.use_motion_blur:
			row = layout.row()
			row.label(text="Motion Blur is disabled")
			row.operator("photographer.rendermotionblur", text="Enable Motion Blur")
		
		col.prop(scene.camera.data.dof, "use_dof", text='Affect Depth of Field')
			
		row = layout.row()
		row.alignment = 'RIGHT'

		framerate_guide = "FPS : " + str(round(scene.render.fps/scene.render.fps_base,2))
		if settings.shutter_mode == 'ANGLE':
			shutter_speed_guide = " - " + "Shutter Speed : 1/" + str(int(settings.shutter_speed)) + "s"
			framerate_guide += shutter_speed_guide
		if settings.shutter_mode == 'SPEED':
			shutter_angle_guide = " - " + "Shutter Angle : " + str(round(settings.shutter_angle,1))
			framerate_guide += shutter_angle_guide
		row.label(text = framerate_guide)



class PHOTOGRAPHER_PT_Panel_WhiteBalance(bpy.types.Panel):
	# bl_idname = "CAMERA_PT_Photographer_White_Balance"
	bl_label = "White Balance"
	bl_parent_id = "PHOTOGRAPHER_PT_Panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"

	def draw_header_preset(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.operator("white_balance.picker",text='', icon='EYEDROPPER', emboss=False)
		row.operator("white_balance.reset", text='', icon='LOOP_BACK', emboss=False)

	def draw_header(self, context):

		self.layout.prop(context.scene.view_settings, "use_curve_mapping", text="")

	def draw(self, context):
		layout = self.layout
		settings = context.camera.photographer
		scene = bpy.context.scene

		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.
		layout.enabled = context.scene.view_settings.use_curve_mapping

		row = layout.row(align=True)
		row.prop(settings, "color_temperature", slider=True)
		row.prop(settings, "preview_color", text='')

		row = layout.row(align=True)
		row.prop(settings, "tint", slider=True)
		row.prop(settings, "preview_color_tint", text='')


class PHOTOGRAPHER_PT_Panel_Resolution(bpy.types.Panel):
	# bl_idname = "CAMERA_PT_Photographer_Resolution"
	bl_label = "Resolution"
	bl_parent_id = "PHOTOGRAPHER_PT_Panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"

	def draw_header_preset(self, context):
		layout = self.layout
		settings = context.camera.photographer
		layout.enabled = settings.resolution_enabled
		
		row = layout.row(align=True)
		row.alignment = 'RIGHT'
		# Resolution
		resolution_x = str(int(context.scene.render.resolution_x * context.scene.render.resolution_percentage/100))
		resolution_y = str(int(context.scene.render.resolution_y * context.scene.render.resolution_percentage/100))
		row.label(text = resolution_x + " x " + resolution_y + " pixels")

	def draw_header(self, context):

		settings = context.camera.photographer

		self.layout.prop(settings, "resolution_enabled", text="")

	def draw(self, context):
		layout = self.layout
		settings = context.camera.photographer
		scene = bpy.context.scene

		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.
		layout.enabled = settings.resolution_enabled

		col = layout.column()
		col.alignment = 'RIGHT'

		col.prop(settings, 'resolution_mode')

		sub = col.column(align=True)
		
		if settings.resolution_mode == 'CUSTOM':
			sub.prop(settings, "resolution_x", text='Resolution X')
			sub.prop(settings, "resolution_y", text='Y')
			sub.prop(context.scene.render, "resolution_percentage", text='%')
			col.row().prop(settings, 'resolution_rotation',expand=True)

		if not settings.resolution_mode == 'CUSTOM':
			sub.prop(settings, "longedge")
			sub.prop(context.scene.render, "resolution_percentage", text='%')
			if not settings.resolution_mode == '11':
				col.row().prop(settings, 'resolution_rotation',expand=True)

class PHOTOGRAPHER_PT_Panel_Autofocus(bpy.types.Panel):
	# bl_idname = "CAMERA_PT_Photographer_Autofocus"
	bl_label = "Continuous Autofocus"
	bl_parent_id = "PHOTOGRAPHER_PT_Panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"
	
	def draw_header(self, context):

		settings = context.camera.photographer
		self.layout.prop(settings, "af_continuous_enabled", text="")
	
	def draw(self, context):
			layout = self.layout
			settings = context.camera.photographer
			scene = bpy.context.scene

			layout.use_property_split = True
			layout.use_property_decorate = False  # No animation.

			col = layout.column(align=True)
			col.prop(settings, "af_continuous_interval", slider=True)


def get_addon_preferences():
	addon_name = os.path.basename(os.path.dirname(os.path.abspath(__file__).split("utils")[0]))
	user_preferences = bpy.context.preferences
	addon_prefs = user_preferences.addons[addon_name].preferences 
	
	return addon_prefs		  
		
#Camera Exposure functions ##############################################################

# Update Toggle
def update_settings(self,context):
	

	if context.scene.camera:
		settings = context.scene.camera.data.photographer

		if settings.exposure_enabled:
			update_aperture(self, context)
			update_shutter_speed(self, context)
			update_iso(self, context)
			update_shutter_angle(self, context)
		
			if context.scene.camera.data.dof.focus_distance == 0:
				context.scene.camera.data.dof.focus_distance = 3
			# if context.scene.render.engine == 'CYCLES' and settings.dof_enabled:
				# context.scene.camera.data.cycles.aperture_type = 'FSTOP'				  
						
			if settings.resolution_enabled:
				update_resolution(self,context)
			
			if context.scene.view_settings.use_curve_mapping:
				settings.color_temperature = settings.color_temperature
				settings.tint = settings.tint
				set_tint_color(self,context)

def update_exposure_guide(self,context):
	EV = calc_exposure_value(self,context)
	if EV <= 16 and EV >= -6:		
		EV = int(EV+6)
		ev_guide = ev_lookup[EV]
	else:
		ev_guide = "Out of realistic range"
	return ev_guide
	   
def calc_exposure_value(self, context):
	settings = context.scene.camera.data.photographer
	if settings.exposure_mode == 'EV':
		EV = settings.ev
	else:
		
		if not settings.aperture_slider_enable:
			aperture = float(settings.aperture_preset)
		else:
			aperture = settings.aperture
		A = aperture
		
		if not settings.shutter_speed_slider_enable and settings.shutter_mode == 'SPEED':
			shutter_speed = float(settings.shutter_speed_preset)
		else:
			shutter_speed = settings.shutter_speed
		S = 1 / shutter_speed
		
		if not settings.iso_slider_enable:
			iso = float(settings.iso_preset)
		else:
			iso = settings.iso
		I = iso
		
		EV = math.log((100*(A*A)/(I*S)), 2)
		EV = round(EV, 2)
	return EV

# Update EV
def update_ev(self,context):
	EV = calc_exposure_value(self,context)
		
	bl_exposure = -EV+8
	context.scene.view_settings.exposure = bl_exposure
	
# Update Aperture
def update_aperture(self, context):
	settings = context.scene.camera.data.photographer
	if settings.dof_enabled :
		if context.scene.camera == context.view_layer.objects.active:
			if not settings.aperture_slider_enable:
				context.scene.camera.data.dof.aperture_fstop = float(settings.aperture_preset) * context.scene.unit_settings.scale_length
				context.scene.camera.data.dof.aperture_fstop = float(settings.aperture_preset)
			else:
				context.scene.camera.data.dof.aperture_fstop = settings.aperture * context.scene.unit_settings.scale_length
				context.scene.camera.data.dof.aperture_fstop = settings.aperture
	
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


# Update Resolution	   
def update_resolution(self,context):
	settings = context.scene.camera.data.photographer
		
	resolution_x = 1920
	resolution_x = 1080
		
	if settings.resolution_mode == 'CUSTOM':
		resolution_x = settings.resolution_x
		resolution_y = settings.resolution_y
	
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
			
		
			
		
#White Balance functions ##############################################################
		
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
	
def convert_RGB_to_temperature_table(red, blue):
	
	table_ratio = InterpolatedArray(temperature_ratio)
	
	# Min and Max ratios from the table
	maxratio = 23.1818
	minratio = 0.1176
	
	# Make sure to not divide by 0
	if blue == 0:
		ratio = minratio
	else: ratio = red / blue
	
	#Clamping ratio to avoid looking outside of the table
	ratio = maxratio if ratio > maxratio else minratio if ratio < minratio else ratio

	color_temperature = table_ratio[ratio]
	
	return (color_temperature)

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

# sRGB to linear function
def s2lin(x):
	a = 0.055
	if x <= 0.04045 :
		y = x * (1.0 / 12.92)
	else:
		y = pow( (x + a) * (1.0 / (1 + a)), 2.4)
	return y	
	
def convert_RBG_to_whitebalance(picked_color):
	photographer = bpy.context.camera.photographer
	#Need to convert picked color to linear
	red = s2lin(picked_color[0])
	green = s2lin(picked_color[1])
	blue = s2lin(picked_color[2])
	
	average = (red + blue) / 2
	
	# Calculating Curves values
	red_mult = red / average
	green_mult = green / average
	blue_mult = blue / average

	# # Accurate multiplier to test accuracy of color temperature conversion
	# bpy.context.scene.view_settings.curve_mapping.white_level[0] = red_mult
	# bpy.context.scene.view_settings.curve_mapping.white_level[1] = green_mult
	# bpy.context.scene.view_settings.curve_mapping.white_level[2] = blue_mult
		
	# Convert Curve value to Tint
	if green_mult < 1 :
		photographer.tint = (green_mult - 1) * 200 # Reverse Tint Math
	else:
		photographer.tint = (green_mult - 1) * 50 # Reverse Tint Math
  
	# Convert Curve value to Temperature
	photographer.color_temperature = convert_RGB_to_temperature_table(red_mult,blue_mult)
	
def calc_color_temperature_color(temperature):
	return convert_temperature_to_RGB_table(temperature)

def calc_tint_preview_color(tint):
	return convert_tint_to_color_preview(tint)	 

def get_color_temperature_color_preview(self):
	def_k = calc_color_temperature_color(default_color_temperature)
	# inverting
	def_k = (def_k[2],def_k[1],def_k[0])
	photographer = bpy.context.scene.camera.data.photographer
	
	# Convert Temperature to Color
	white_balance_color = calc_color_temperature_color(photographer.color_temperature)
	# Set preview color in the UI - inverting red and blue channels
	self['preview_color'] = (white_balance_color[2],white_balance_color[1],white_balance_color[0])
	return self.get('preview_color', def_k)	 

def set_color_temperature_color(self, context):
	photographer = bpy.context.scene.camera.data.photographer
	
	# Convert Temperature to Color
	white_balance_color = calc_color_temperature_color(photographer.color_temperature)
	
	if context.scene.camera == context.view_layer.objects.active:
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
	self['preview_color_tint'] = calc_tint_preview_color(photographer.tint)
	def_tint = calc_tint_preview_color(default_tint)
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

def set_picked_white_balance(picked_color):
	convert_RBG_to_whitebalance(picked_color)

def update_af_continuous(self,context):
	settings = context.scene.camera.data.photographer
	if settings.af_continuous_enabled:
		bpy.ops.photographer.check_focus_object()
		bpy.app.timers.register(focus_continuous)
		if settings.af_animate:
			bpy.app.handlers.frame_change_pre.append(stop_playback)
	else:
		
		if bpy.app.timers.is_registered(focus_continuous):
			bpy.app.timers.unregister(focus_continuous)
		
		
def create_af_target(context,location):
	camera = context.scene.camera
	settings = camera.data.photographer
	
	af_target = bpy.data.objects.new(camera.name + "_AF_Tracker", None)
	af_target.empty_display_type = "CUBE"
	af_target.show_name = True
	af_target.show_in_front = True
	
	context.scene.camera.data.dof.focus_object = af_target
	
	# new_loc = camera.matrix_world.inverted() @ location
	
	settings.af_target = af_target
	settings.af_target.location = location
	
	context.view_layer.active_layer_collection.collection.objects.link(af_target)
	
def delete_af_target(context):
	camera = context.scene.camera
	settings = camera.data.photographer
	af_target = settings.af_target
	
	settings.af_target = None
	
	use_dof = camera.data.dof.use_dof 
	if use_dof == False:
		camera.data.dof.use_dof = True
		if camera.data.dof.focus_object == af_target:
			context.scene.camera.data.dof.focus_object == None
	camera.data.dof.use_dof = use_dof
	
	
	context.view_layer.active_layer_collection.collection.objects.unlink(af_target)
	
	obj = bpy.data.objects
	obj.remove(obj[af_target.name])

# Photo Mode parameters ####################################################	
class PhotographerSettings(bpy.types.PropertyGroup):
	# bl_idname = __name__

	# UI Properties
	# initRefresh = bpy.props.BoolProperty(
		# name = "initRefresh",
		# description = "Is the automatic Panel refresh working?",
		# default = False
	# )
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
		default = bpy.context.preferences.addons[__name__].preferences.exposure_mode_pref if bpy.context.preferences.addons[__name__].preferences.exposure_mode_pref else 'EV',
		update = update_settings
		# default = 'EV',
	)
	ev : bpy.props.FloatProperty(
		name = "Exposure Value",
		description = "Exposure Value: look at the Chart",
		soft_min = -6,
		soft_max = 16,
		step = 1,
		precision = 2,
		default = 8.0,
		update = update_ev
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
		default = 50,
		update = update_shutter_speed
	)
	shutter_speed_slider_enable : bpy.props.BoolProperty(
		name = "Shutter Speed Slider",
		description = "Enable Shutter Speed slider instead of preset list",
		default = bpy.context.preferences.addons[__name__].preferences.shutter_speed_slider_pref if bpy.context.preferences.addons[__name__].preferences.shutter_speed_slider_pref else False,
		update = update_shutter_speed
		# default = False,
	)
	shutter_speed_preset : bpy.props.EnumProperty(
		name = "Shutter Speed",
		description = "Camera Shutter Speed",
		items = [('0.033','30 "',''),('0.04','25 "',''),('0.05','20 "',''),('0.066','15 "',''),('0.077','13 "',''),('0.1','10 "',''),('0.125','8 "',''),('0.1666','6 "',''),('0.2','5 "',''),('0.25','4 "',''),('0.3125','3.2 "',''),('0.4','2.5 "',''),
		('0.5','2 "',''),('0.625','1.6 "',''),('0.769','1.3 "',''),('1','1 "',''),('1.25','0.8 "',''),('1.666','0.6 "',''),('2','0.5 "',''),('2.5','0.4 "',''),('3.333','0.3 "',''),('4','1 / 4 s',''),('5','1 / 5 s',''),('6','1 / 6 s',''),
		('8','1 / 8 s',''),('10','1 / 10 s',''),('13','1 / 13 s',''),('15','1 / 15 s',''),('20','1 / 20 s',''),('25','1 / 25 s',''),('30','1 / 30 s',''),('40','1 / 40 s',''),('50','1 / 50 s',''),('60','1 / 60 s',''),('80','1 / 80 s',''),
		('100','1 / 100 s',''),('125','1 / 125 s',''),('160','1 / 160 s',''),('200','1 / 200 s',''),('250','1 / 250 s',''),('320','1 / 320 s',''),('400','1 / 400 s',''),('500','1 / 500 s',''),('640','1 / 640 s',''),('800','1 / 800 s',''),
		('1000','1 / 1000 s',''),('1250','1 / 1250 s',''),('1600','1 / 1600 s',''),('2000','1 / 2000 s',''),('2500','1 / 2500 s',''),('3200','1 / 3200 s',''),('4000','1 / 4000 s',''),('5000','1 / 5000 s',''),('6400','1 / 6400 s',''),('8000','1 / 8000 s', '')],
		default = '50',
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
		default = bpy.context.preferences.addons[__name__].preferences.aperture_slider_pref,
		update = update_aperture
	)
	aperture_preset : bpy.props.EnumProperty(
		name = "Lens Aperture Presets",
		description = "Lens Aperture",
		items = [('0.95','f / 0.95',''),('1.2','f / 1.2',''),('1.4','f / 1.4',''),('1.8','f / 1.8',''),('2.0','f / 2.0',''),('2.4','f / 2.4',''),('2.8','f / 2.8',''),('3.5','f / 3.5',''),('4.0','f / 4.0',''),('4.9','f / 4.9',''),('5.6','f / 5.6',''),
		('6.7','f / 6.7',''),('8.0','f / 8.0',''),('9.3','f / 9.3',''),('11','f / 11',''),('13','f / 13',''),('16','f / 16',''),('20','f / 20',''),('22','f / 22','')],
		default = '5.6',
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
		default = bpy.context.preferences.addons[__name__].preferences.iso_slider_pref,
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
	preview_color : bpy.props.FloatVectorProperty(
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
		items = [('CUSTOM','Custom',''),('11','1:1', ''),('32','3:2', ''),('43','4:3', ''),('67','6:7', ''),('169','16:9', ''),('2351','2.35:1', '')],
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
	
class PHOTOGRAPHER_OT_SetShutterAngle(bpy.types.Operator):
	bl_idname = "photographer.setshutterangle"
	bl_label = "Switch to Shutter Angle"
	bl_description = "Switch to Shutter Angle"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		context.camera.photographer.shutter_mode = 'ANGLE'
		update_settings(self,context)
		return{'FINISHED'}

class PHOTOGRAPHER_OT_SetShutterSpeed(bpy.types.Operator):
	bl_idname = "photographer.setshutterspeed"
	bl_label = "Switch to Shutter Speed"
	bl_description = "Switch to Shutter Speed"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		context.camera.photographer.shutter_mode = 'SPEED'
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
	
class PHOTOGRAPHER_OT_WBReset(bpy.types.Operator):
	bl_idname = "white_balance.reset"
	bl_label = "Reset White Balance"
	bl_description = "Reset White Balance"
	bl_options = {'REGISTER', 'UNDO'}
 
	def execute(self, context):
		context.camera.photographer.color_temperature = default_color_temperature
		context.camera.photographer.tint = default_tint
		return{'FINISHED'} 

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
		
class PHOTOGRAPHER_OT_WBPicker(bpy.types.Operator):
	bl_idname = "white_balance.picker"
	bl_label = "Pick White Balance"
	bl_description = "Pick a grey area in the 3D view to adjust the White Balance"
	bl_options = {'REGISTER', 'UNDO'}
 
	# Create stored values for cancelling
	stored_color_temperature = 6500
	stored_tint = 0
	stored_cm_display_device = "sRGB"
	stored_cm_view_transform = "Filmic"
	
	stored_cm_look = "None"
	
	def modal(self, context, event):
		context.area.tag_redraw()
		
		# Reset White Balance to pick raw image, not an already white balanced one
		context.camera.photographer.color_temperature = default_color_temperature
		context.camera.photographer.tint = default_tint
		# Disabling color management to be able to convert picked color easily
		context.scene.display_settings.display_device = "sRGB"
		context.scene.view_settings.view_transform = "Standard"
 
		# Allow navigation for Blender and Maya shortcuts
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
			return {'PASS_THROUGH'}
			
		if event.type == 'LEFTMOUSE':

			# Picking color when releasing left mouse button
			if event.value == 'RELEASE' and not self.record:

				self.record = True
				self.mouse_position=(event.mouse_x, event.mouse_y)
				# Restore Mouse Cursor from Eyedropper Icon
				if self.cursor_set: context.window.cursor_modal_restore()
				
				buf = bgl.Buffer(bgl.GL_FLOAT, [1, 3])
				x,y = self.mouse_position
				
				# Sampling pixels under the mouse when released
				bgl.glReadPixels(x, y, 1,1 , bgl.GL_RGB, bgl.GL_FLOAT, buf)
				rgb = buf[0]
				# Calculate and apply Color Temperature and Tint
				set_picked_white_balance(rgb)
				
				# Restore Color Management Settings
				context.scene.display_settings.display_device = self.stored_cm_display_device 
				context.scene.view_settings.view_transform = self.stored_cm_view_transform
				context.scene.view_settings.look = self.stored_cm_look
		
				return {'FINISHED'}

		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			# Restore previous settings if cancelled
			context.camera.photographer.color_temperature = self.stored_color_temperature
			context.camera.photographer.tint = self.stored_tint
			
			# Restore Color Management Settings
			context.scene.display_settings.display_device = self.stored_cm_display_device 
			context.scene.view_settings.view_transform = self.stored_cm_view_transform
			context.scene.view_settings.look = self.stored_cm_look
		
			# Restore Mouse Cursor from Eyedropper Icon
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}
			
		return {'RUNNING_MODAL'}
		
	def invoke(self, context, event):
			args = (self, context)
			context.window_manager.modal_handler_add(self)
			
			# Set Cursor to Eyedropper icon
			context.window.cursor_modal_set('EYEDROPPER')
			self.cursor_set = True
			self.record = False
			
			# Store current white balance settings in case of cancelling
			self.stored_color_temperature = context.camera.photographer.color_temperature
			self.stored_tint = context.camera.photographer.tint
			
			self.stored_cm_display_device = context.scene.display_settings.display_device
			self.stored_cm_view_transform = context.scene.view_settings.view_transform
			self.stored_cm_look = context.scene.view_settings.look
		
			context.area.tag_redraw()
			return {'RUNNING_MODAL'}
 

	
def update_af_target(context,location):
	camera = context.scene.camera
	settings = camera.data.photographer
	settings.af_target.location = (10,10,10)
	
def set_af_key(context):
	camera = context.scene.camera
	settings = camera.data.photographer
	
	current_frame = context.scene.frame_current
	camera.data.dof.keyframe_insert(data_path='focus_distance', frame=(current_frame))
	
def stop_playback(scene):
	settings = scene.camera.data.photographer

	if scene.frame_current == scene.frame_end:
		bpy.ops.screen.animation_cancel(restore_frame=False)
		settings.af_continuous_enabled = False
		bpy.app.handlers.frame_change_pre.remove(stop_playback)

# def lerp_focus_distance(ray_length, context):
	# context.scene.camera.data.dof.focus_distance = context.scene.camera.data.dof.focus_distance + (ray_length - context.scene.camera.data.dof.focus_distance) / 2
	# return 0.02
	
# Focus picker 
def focus_raycast(context, event, continuous):

	scene = bpy.context.scene
	cam = scene.camera
	cam_matrix = cam.matrix_world
	
	org = cam_matrix @ Vector((0.0, 0.0, 0.0))
	
	if continuous:
		dst = cam_matrix @ Vector((0.0, 0.0, 100.0 * -1))
	else:
		region = context.region
		rv3d = context.region_data
		coord = event.mouse_region_x, event.mouse_region_y

		# Get the ray from the viewport and mouse
		view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
		dst = ray_origin + view_vector
		
	dir = dst - org
	
	vl = bpy.context.view_layer

	result, location, normal, index, object, matrix = scene.ray_cast(vl, org, dir)

	
	if result:
		length = (location - org).length
		
		# if continuous:		
			# bpy.app.timers.register(functools.partial(lerp_focus_distance, length, context))
			
			# dist_diff = abs(length - context.scene.camera.data.dof.focus_distance)
			# print (dist_diff)
			# if dist_diff < 0.1:
				# # if bpy.app.timers.is_registered(lerp_focus_distance):
				# bpy.app.timers.unregister(lerp_focus_distance)
		# else:
		context.scene.camera.data.dof.focus_distance = length
	
	else:
		context.scene.camera.data.dof.focus_distance = 100
		
	return location
			

class PHOTOGRAPHER_OT_FocusSingle(bpy.types.Operator):
	"""Autofocus Single: Click where you want to focus"""
	bl_idname = "photographer.focus_single"
	bl_label = "Photographer Focus Single"

	def modal(self, context, event):
		# Allow navigation for Blender and Maya shortcuts
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
			return {'PASS_THROUGH'}
		
		settings = context.scene.camera.data.photographer
		
		# Disable AF-C if using AF-C
		if settings.af_continuous_enabled:
			settings.af_continuous_enabled = False
		
		# Enter focus picker
		if event.type == 'LEFTMOUSE':
			if event.value == 'RELEASE':
				if context.space_data.type == 'VIEW_3D':
					try:
						#Enable DoF
						context.scene.camera.data.dof.use_dof = True
						focus_raycast(context, event, False)
						if context.scene.camera.data.dof.focus_object is not None:
							self.report({'WARNING'}, "There is an object set as focus target which will override the results of the Autofocus")
						
						
						#Set key if animate is on
						if settings.af_animate:
							bpy.ops.object.select_all(action='DESELECT')
							bpy.data.objects[context.scene.camera.name].select_set(True)
							context.view_layer.objects.active = context.scene.camera
							
							set_af_key(context)
						
					except:
						self.report({'ERROR'}, "An error occured during the raycast. Is the targeted object a mesh?")
					context.window.cursor_modal_restore()				  
					return {'FINISHED'}
				else:
					self.report({'WARNING'}, "Active space must be a View3d")
					if self.cursor_set: context.window.cursor_modal_restore()
				return {'CANCELLED'}
		
		# Cancel Modal with RightClick and ESC
		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}
		  
	def invoke(self, context, event):
		self.cursor_set = True
		context.window.cursor_modal_set('EYEDROPPER')
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

class PHOTOGRAPHER_OT_FocusTracking(bpy.types.Operator):
	"""Autofocus Tracket: Click where you want to place the tracker"""
	bl_idname = "photographer.focus_tracking"
	bl_label = "Photographer Focus Tracking"

	def modal(self, context, event):
		# Allow navigation for Blender and Maya shortcuts
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
			return {'PASS_THROUGH'}
		
		settings = context.scene.camera.data.photographer
		
		#Store the current object selection
		current_sel = bpy.context.selected_objects
		
		
		# Disable AF-C if using AF-C
		if settings.af_continuous_enabled:
			settings.af_continuous_enabled = False
		
		# Enter focus picker
		if event.type == 'LEFTMOUSE':
			if event.value == 'RELEASE':
				if context.space_data.type == 'VIEW_3D':
					try:
						
						#Enable DoF
						context.scene.camera.data.dof.use_dof = True
						
						#Select what's under the mouse and store its name
						bpy.ops.view3d.select(extend=False, deselect=False, location=(event.mouse_region_x, event.mouse_region_y))
						parent_obj = bpy.context.selected_objects[0]
						
						#Restore the previous selection
						if current_sel:
							for o in current_sel:
								bpy.data.objects[o.name].select_set(True)
						else:
							bpy.ops.object.select_all(action='DESELECT')
						
						#Raycast and store the hit location
						location = focus_raycast(context, event, False)

						#Calculate the location relative to the parent object
						new_loc = parent_obj.matrix_world.inverted() @ location					
						
						#Create AF Tracking target object at the hit location
						create_af_target(context,new_loc)
						
						settings.af_target.empty_display_size = (1.0/parent_obj.scale.x)/10.0
						#Parent the target object to the object under the mask
						settings.af_target.parent = parent_obj
						
						#Set the Tracking to enable
						settings.af_tracking_enabled = True
					
					except:
						self.report({'ERROR'}, "An error occured during the raycast. Is the targeted object a mesh?")
					context.window.cursor_modal_restore()				  
					return {'FINISHED'}
				else:
					self.report({'WARNING'}, "Active space must be a View3d")
					if self.cursor_set: context.window.cursor_modal_restore()
				return {'CANCELLED'}
		
		# Cancel Modal with RightClick and ESC
		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}
		  
	def invoke(self, context, event):
		self.cursor_set = True
		context.window.cursor_modal_set('EYEDROPPER')
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}
		
		
class PHOTOGRAPHER_OT_FocusTracking_Cancel(bpy.types.Operator):
	"""Autofocus Single: Click where you want to focus"""
	bl_idname = "photographer.focus_tracking_cancel"
	bl_label = "Photographer Focus Tracking Cancel"
	
	def execute(self, context):
	
		settings = context.scene.camera.data.photographer
		
		try:
			delete_af_target(context)
		except:
			settings.af_target = None
			self.report({'WARNING'}, "The AF-Track target object is not present in the scene anymore")
			
		settings.af_tracking_enabled = False
		
		return{'FINISHED'}

class PHOTOGRAPHER_OT_CheckFocusObject(bpy.types.Operator):
	"""Autofocus Single: Click where you want to focus"""
	bl_idname = "photographer.check_focus_object"
	bl_label = "Photographer Check Focus Object"
	
	def execute(self, context):
	
		settings = context.scene.camera.data.photographer
		if context.scene.camera.data.dof.focus_object is not None:
			self.report({'WARNING'}, "There is an object set as focus target which will override the results of the Autofocus.")
		
		return{'FINISHED'}
		


# Focus continuous timer function	   
def focus_continuous():
	context = bpy.context
	scene = context.scene
	settings = context.scene.camera.data.photographer
	timer = settings.af_continuous_interval
	
	#Enable DoF
	context.scene.camera.data.dof.use_dof = True
	
	# Do not AF-C if active camera is not a camera
	if context.scene.camera:
		if context.scene.camera.type == 'CAMERA':
			settings = context.scene.camera.data.photographer
			if settings.af_continuous_enabled :
				focus_raycast(context, None, True)
				
				#Little trick to update viewport as the header distance doesn't update automatically
				exposure = bpy.context.scene.view_settings.exposure
				bpy.context.scene.view_settings.exposure = exposure
				
			#Set key if animate is on
			if settings.af_animate:
				#Select camera to see the keyframes
				bpy.ops.object.select_all(action='DESELECT')
				bpy.data.objects[context.scene.camera.name].select_set(True)
				context.view_layer.objects.active = context.scene.camera
				set_af_key(context)

	return timer
				

		
def focus_single_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA':
						settings = context.scene.camera.data.photographer
						# if context.scene.camera == bpy.context.active_object:
						if settings.af_tracking_enabled == False:
							icon_af = 'RESTRICT_RENDER_OFF'
							if settings.af_animate:
								icon_af = 'KEYTYPE_KEYFRAME_VEC'
							self.layout.operator("photographer.focus_single", text="AF-S", icon=icon_af)
	
def focus_continuous_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA' :
						settings = context.scene.camera.data.photographer
						if settings.af_tracking_enabled == False:
						
							icon_af = 'HOLDOUT_ON'
							if settings.af_animate:
								icon_af = 'KEYTYPE_KEYFRAME_VEC'
							
							self.layout.prop(settings, "af_continuous_enabled", text="AF-C", icon=icon_af )
							
def focus_animate_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA' :
						settings = context.scene.camera.data.photographer
						self.layout.prop(settings, "af_animate", text="", icon="KEY_HLT" )

def focus_tracking_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA':
						settings = context.scene.camera.data.photographer
						if settings.af_tracking_enabled == False:
							self.layout.operator("photographer.focus_tracking", text="AF-Track", icon='OBJECT_DATA')
						if settings.af_tracking_enabled:
							self.layout.operator("photographer.focus_tracking_cancel", text="Cancel AF Tracking", icon='OBJECT_DATA')
		
def focus_distance_header(self, context):
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA' and not context.scene.camera.data.photographer.af_tracking_enabled:
						dof_distance = str(round(context.scene.camera.data.dof.focus_distance*context.scene.unit_settings.scale_length,2))
						if not context.scene.unit_settings.system == 'NONE':
							dof_distance = dof_distance + "m"
						self.layout.label(text=dof_distance)


# MASTER CAMERA #
def interpolate_location(obj1, obj2, time):
		
	obj1.rotation_euler.x = obj1.rotation_euler.x + (obj2.rotation_euler.x - obj1.rotation_euler.x)/time
	obj1.rotation_euler.y = obj1.rotation_euler.y + (obj2.rotation_euler.y - obj1.rotation_euler.y)/time
	obj1.rotation_euler.z = obj1.rotation_euler.z + (obj2.rotation_euler.z - obj1.rotation_euler.z)/time
	
	obj1.location = obj1.location + (obj2.location - obj1.location)/time
	
	distance = (obj2.location - obj1.location).length
	
	return distance

def interpolate_float(obj1, obj2, time):

	obj1 = obj1 + (obj2 - obj1) / time
	distance = obj2 - obj1
	
	return distance

def match_camera():
	context = bpy.context
	
	master_cam = bpy.data.objects.get('MasterCamera')
	# target_cam = bpy.data.objects.get(camera)
	target_cam = master_cam.data.photographer.target_camera
	
	match_speed = master_cam.data.photographer.match_speed
	settings_speed = match_speed / 2
	if settings_speed < 1:
		settings_speed == 1
	master_cam.data.photographer.is_matching = True
	
	distance = interpolate_location(master_cam,target_cam, match_speed)

	if master_cam.data.sensor_width != target_cam.data.sensor_width:
		master_cam.data.sensor_width = master_cam.data.sensor_width + (target_cam.data.sensor_width - master_cam.data.sensor_width)/settings_speed

	if not master_cam.data.photographer.af_continuous_enabled:
		master_cam.data.dof.use_dof = target_cam.data.dof.use_dof
		# interpolate_float(master_cam.data.dof.focus_distance,target_cam.data.dof.focus_distance, settings_speed)
		master_cam.data.dof.focus_distance = master_cam.data.dof.focus_distance +(target_cam.data.dof.focus_distance - master_cam.data.dof.focus_distance)/settings_speed
	


	if context.scene.view_settings.use_curve_mapping:
		# interpolate_float(master_cam.data.photographer.color_temperature,target_cam.data.photographer.color_temperature, settings_speed)
		# interpolate_float(master_cam.data.photographer.tint,target_cam.data.photographer.tint, settings_speed)
		master_cam.data.photographer.color_temperature = master_cam.data.photographer.color_temperature + (target_cam.data.photographer.color_temperature - master_cam.data.photographer.color_temperature)/settings_speed
		master_cam.data.photographer.tint = master_cam.data.photographer.tint + (target_cam.data.photographer.tint - master_cam.data.photographer.tint)/settings_speed
		
	if target_cam.data.photographer.exposure_enabled:
		master_cam.data.photographer.exposure_enabled = True
		# interpolate_float(master_cam.data.photographer.aperture,target_cam.data.photographer.aperture, settings_speed)
		# interpolate_float(master_cam.data.photographer.ev,target_cam.data.photographer.ev, settings_speed)
		
		master_cam.data.photographer.exposure_mode = target_cam.data.photographer.exposure_mode
		if target_cam.data.photographer.exposure_mode == 'EV':
			master_cam.data.photographer.ev = master_cam.data.photographer.ev + (target_cam.data.photographer.ev - master_cam.data.photographer.ev)/settings_speed
		
		if target_cam.data.photographer.exposure_mode == 'MANUAL':
			
			# ISO
			if master_cam.data.photographer.iso_slider_enable == False:
				master_cam.data.photographer.iso_slider_enable = True
				
			if target_cam.data.photographer.iso_slider_enable == False:
				target_cam.data.photographer.iso = float(target_cam.data.photographer.iso_preset)
			
			master_cam.data.photographer.iso = master_cam.data.photographer.iso + (target_cam.data.photographer.iso - master_cam.data.photographer.iso)/settings_speed
			
			# Shutter Speed or Shutter Angle
			if target_cam.data.photographer.shutter_mode == 'SPEED':
			
				if master_cam.data.photographer.shutter_speed_slider_enable == False:
					master_cam.data.photographer.shutter_speed_slider_enable = True

				if target_cam.data.photographer.shutter_speed_slider_enable == False:
					target_cam.data.photographer.shutter_speed = float(target_cam.data.photographer.shutter_speed_preset)
					
				master_cam.data.photographer.shutter_speed = master_cam.data.photographer.shutter_speed + (target_cam.data.photographer.shutter_speed - master_cam.data.photographer.shutter_speed)/settings_speed
			
			if target_cam.data.photographer.shutter_mode == 'ANGLE':
				
				if master_cam.data.photographer.shutter_angle_slider_enable == False:
					master_cam.data.photographer.shutter_angle_slider_enable = True

				if target_cam.data.photographer.shutter_angle_slider_enable == False:
					target_cam.data.photographer.shutter_angle = float(target_cam.data.photographer.shutter_angle_preset)
					
				master_cam.data.photographer.shutter_angle = master_cam.data.photographer.shutter_angle + (target_cam.data.photographer.shutter_angle - master_cam.data.photographer.shutter_angle)/settings_speed	

		# Aperture 	
		if master_cam.data.photographer.aperture_slider_enable == False:
			master_cam.data.photographer.aperture_slider_enable = True

		if target_cam.data.photographer.aperture_slider_enable == False:
			target_cam.data.photographer.aperture = float(target_cam.data.photographer.aperture_preset)
		
		master_cam.data.photographer.aperture = master_cam.data.photographer.aperture + (target_cam.data.photographer.aperture - master_cam.data.photographer.aperture)/settings_speed		
		
	
	if master_cam.data.lens != target_cam.data.lens:
		# interpolate_float(master_cam.data.lens,target_cam.data.lens, settings_speed)
		master_cam.data.lens = master_cam.data.lens + (target_cam.data.lens - master_cam.data.lens) / settings_speed
	
	#Little trick to update viewport
	bpy.ops.photographer.updatesettings()

	# print (length)
	threshold = 0.003
	if distance < threshold:
		master_cam.data.photographer.is_matching = False
		return None
	
	return 0.01

# SET CAMERA VIEW
class MASTERCAMERA_OT_LookThrough(bpy.types.Operator):
	bl_idname = 'mastercamera.look_through'
	bl_label = 'Look through'
	bl_description = "Set as Scene camera"
	bl_options = {'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):

		context.view_layer.objects.active = bpy.data.objects[self.camera]
		
		cam = bpy.data.objects.get(self.camera)
		if cam.data.show_name != True:
			cam.data.show_name = True
			
		bpy.ops.view3d.object_as_camera()
		update_settings(self,context)

		return{'FINISHED'}


class MASTERCAMERA_OT_AddMasterCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.add_mastercam'
	bl_label = 'Add Master Camera'
	bl_description = "Create a Master Camera that can fly to other cameras"
	bl_options = {'UNDO'}

	def execute(self,context):
		if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
			context.area.spaces[0].region_3d.view_perspective='PERSP'
		
		if bpy.data.objects.get('MasterCamera') and bpy.data.objects.get('MasterCamera').type != 'CAMERA':
				self.report({'ERROR'}, "There is already an object named Master Camera which isn't a camera. Please delete or rename it")
		else:
			bpy.ops.object.camera_add()
			context.active_object.name = "MasterCamera"
			master_cam_obj = bpy.data.objects[bpy.context.active_object.name]
			context.scene.camera = master_cam_obj
			bpy.ops.view3d.camera_to_view()
			master_cam_obj.data.show_name = True
			
		return{'FINISHED'}
		
class MASTERCAMERA_OT_AddCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.add_cam'
	bl_label = 'Add Camera'
	bl_description = "Add a new Camera from the current view"
	bl_options = {'UNDO'}

	def execute(self,context):
		if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
			context.area.spaces[0].region_3d.view_perspective='PERSP'
		new_cam = bpy.ops.object.camera_add()

		new_cam_obj = bpy.data.objects[bpy.context.active_object.name]
		context.scene.camera = new_cam_obj
		bpy.ops.view3d.camera_to_view()
		new_cam_obj.data.show_name = True
		
		return{'FINISHED'}
			
# Delete Camera
class MASTERCAMERA_OT_DeleteCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.delete_cam'
	bl_label = 'Delete Camera'
	bl_description = "Delete camera"
	bl_options = {'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):
		cam=bpy.data.objects[self.camera]
		bpy.data.objects.remove(cam)
		
		return{'FINISHED'}
		
# Delete Master Camera
class MASTERCAMERA_OT_DeleteMasterCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.delete_mastercam'
	bl_label = 'Delete Master Camera'
	bl_description = "Delete Master Camera"
	bl_options = {'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):
		cam=bpy.data.objects[self.camera]
		
		bpy.data.objects.remove(cam)
		return{'FINISHED'}

class MASTERCAMERA_PT_ToolPanelUi(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'View'	
	bl_label = "Photographer"
	

	def draw(self, context):
		layout = self.layout

		scene = context.scene
	
		col = layout.column(align=True)
		# Master Camera 
		master_row = col.row(align=True)
		
		master_cam = 'MasterCamera'

		cam_list=[cam.name for cam in context.scene.collection.all_objects if cam.type=='CAMERA']
		if master_cam in cam_list:
			if context.scene.camera == bpy.data.objects.get(master_cam):
				master_row.operator("mastercamera.look_through", text=master_cam,  icon='OUTLINER_DATA_CAMERA').camera=master_cam
			else:
				master_row.operator("mastercamera.look_through", text=master_cam).camera=master_cam
			master_row.operator("mastercamera.delete_cam", text="", icon="PANEL_CLOSE").camera=master_cam
			row = col.row(align=True)
			row.prop(bpy.data.objects.get(master_cam).data.photographer, "match_speed", slider=True)
					
		else:
			master_row.operator("mastercamera.add_mastercam", text='Add Master Camera', icon='OUTLINER_DATA_CAMERA')
		
		
		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text= "Camera List:")
		row = col.row(align=True)
		row.operator("mastercamera.add_cam", text='Add Camera')

		col = layout.column(align=True)
		if master_cam in cam_list:
			cam_list.remove('MasterCamera')
		for cam in cam_list:
			row = col.row(align=True)
			if context.scene.camera is not None:
				if context.scene.camera == bpy.data.objects.get(master_cam):
					row.operator("view3d.switch_camera", text="", icon="PLAY").camera=cam
					# row.enabled = not bpy.data.objects.get(master_cam).data.photographer.is_matching
			if context.scene.camera == bpy.data.objects.get(cam):			
				row.operator("mastercamera.look_through", text=cam, icon='RESTRICT_RENDER_OFF').camera=cam
			else:
				row.operator("mastercamera.look_through", text=cam).camera=cam
			row.operator("mastercamera.delete_cam", text="", icon="PANEL_CLOSE").camera=cam
		
		# col = layout.column(align=True)


class MASTERCAMERA_OT_SwitchCamera(bpy.types.Operator):
	bl_idname = "view3d.switch_camera"
	bl_label = "Switch to this camera"
	bl_description = "Switch to this camera"
	bl_options = {'REGISTER', 'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):
		cam = self.camera
		
		if bpy.app.timers.is_registered(match_camera):
			bpy.app.timers.unregister(match_camera)
		
		if bpy.data.objects.get('MasterCamera') and bpy.data.objects.get('MasterCamera').type == 'CAMERA':
			if context.scene.camera != bpy.data.objects.get('MasterCamera'):
				context.scene.camera = bpy.data.objects.get('MasterCamera')
			
			master_cam = bpy.data.objects.get('MasterCamera')
			# context.scene.camera.data.photographer.target_camera = bpy.data.objects.get(cam)
			master_cam.data.photographer.target_camera = bpy.data.objects.get(cam)

			if master_cam.data.photographer.target_camera is None:
				self.report({'WARNING'}, "The camera" + target_camera + " doesn't exist anymore. Are you using a keyboard shortcut assigned to an old camera? Either create a camera named" + target_cam+ ", or remove the shortcut")
				
			else: bpy.app.timers.register(match_camera)
				
		else:
			self.report({'WARNING'}, "There is no Master Camera in the scene. Please create one first")

		return {'FINISHED'}




classes = ( 
	PHOTOGRAPHER_PT_Panel,
	PHOTOGRAPHER_PT_Panel_Exposure,
	PHOTOGRAPHER_PT_Panel_WhiteBalance,
	PHOTOGRAPHER_PT_Panel_Resolution,
	PHOTOGRAPHER_PT_Panel_Autofocus,
	PhotographerSettings,
	PHOTOGRAPHER_OT_SetShutterAngle,
	PHOTOGRAPHER_OT_SetShutterSpeed,
	PHOTOGRAPHER_OT_RenderMotionBlur,
	PHOTOGRAPHER_OT_WBReset,
	PHOTOGRAPHER_OT_MakeCamActive,
	PHOTOGRAPHER_OT_UpdateSettings,
	PHOTOGRAPHER_OT_SelectActiveCam,
	PHOTOGRAPHER_OT_WBPicker,
	PHOTOGRAPHER_OT_FocusSingle,
	PHOTOGRAPHER_OT_FocusTracking,
	PHOTOGRAPHER_OT_FocusTracking_Cancel,
	PHOTOGRAPHER_OT_CheckFocusObject,
	MASTERCAMERA_PT_ToolPanelUi,
	MASTERCAMERA_OT_LookThrough,
	MASTERCAMERA_OT_SwitchCamera,
	MASTERCAMERA_OT_AddMasterCamera,
	MASTERCAMERA_OT_AddCamera,
	MASTERCAMERA_OT_DeleteCamera,
	MASTERCAMERA_OT_DeleteMasterCamera,
)

def register():
	from bpy.utils import register_class

	for cls in classes:
		print(cls)
		register_class(cls)

	bpy.types.Camera.photographer = PointerProperty(type=PhotographerSettings)
	bpy.types.VIEW3D_HT_header.append(focus_single_button)
	bpy.types.VIEW3D_HT_header.append(focus_continuous_button)
	bpy.types.VIEW3D_HT_header.append(focus_animate_button)
	bpy.types.VIEW3D_HT_header.append(focus_tracking_button)
	bpy.types.VIEW3D_HT_header.append(focus_distance_header)
	

def unregister():
	from bpy.utils import unregister_class

	bpy.types.VIEW3D_HT_header.remove(focus_single_button)
	bpy.types.VIEW3D_HT_header.remove(focus_continuous_button)
	bpy.types.VIEW3D_HT_header.remove(focus_animate_button)
	bpy.types.VIEW3D_HT_header.remove(focus_tracking_button)
	bpy.types.VIEW3D_HT_header.remove(focus_distance_header)

	for cls in classes:
		unregister_class(cls)
	del bpy.types.Camera.photographer
	
	unregister_class (AddonPreferences)