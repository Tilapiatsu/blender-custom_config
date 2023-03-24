import bpy
from bpy.props import (BoolProperty,
					   FloatProperty,
					   EnumProperty,
					   FloatVectorProperty,
					   )

import math
from . import (functions,
	camera,
)

stored_power = 1
stored_advanced_power = 1
stored_efficacy = 683
stored_lumen = 683
stored_candela = 5
stored_irradiance = 1
stored_illuminance = 10

INTENSITY_DESCRIPTION = (
    "Brightness multiplier"
)

EXPOSURE_DESCRIPTION = (
    "Power-of-2 step multiplier. "
    "An EV step of 1 will double the brightness of the light"
)

POWER_DESCRIPTION = (
    "Power in watt; Radiometric unit used by default in Cycles"
)

ADVANCED_POWER_DESCRIPTION = (
    "Power in watt with tweakable luminous efficacy value and energy conserving option"
)

EFFICACY_DESCRIPTION = (
    "Luminous efficacy in lumens per watt"
)

LUMEN_DESCRIPTION = (
    "Luminous flux in lumens, assuming a maximum possible luminous efficacy of 683 lm/W.\n"
    "Photometric unit, it should be normalized by Color Luminance.\n"
    "Best for Point lights, using Lightbulb packages as reference"
)

CANDELA_DESCRIPTION = (
    "Luminous intensity in candela (luminous power per unit solid angle).\n"
    "Photometric unit, it should be normalized by Color Luminance.\n"
    "Best for Spot lights to maintain brighness when changing Angle" 
)

IRRADIANCE_DESCRIPTION = (
    "Radiant flux per unit area in Watts per square meter."
)

ILLUMINANCE_DESCRIPTION = (
    "Luminous flux per unit area in Lumens per square meter, called Lux. \n"
    "Photometric unit, it should be normalized by Color Luminance." 
)

PER_SQUARE_METER_DESCRIPTION = (
    "Divides intensity by the object surface to maintain brightness when changing Size.\n"
    "Candela per square meter is also called Nit" 
)

LUX_DESCRIPTION = (
    "Illuminance in Lux (luminous flux incident on a surface in lumen per square meter).\n"
    "Photometric unit, it should be normalized by Color Luminance"
)

NORMALIZEBYCOLOR_DESCRIPTION = (
    "Normalize intensity by the Color Luminance.\n"
    "Recommended for Photometric units (Lumen, Candela, Lux) to simulate \n"
    "the luminous efficiency function"
)

SPOT_SIZE_DESCRIPTION = (
	"Angle of the spotlight beam"
)

SIZE_DESCRIPTION = (
	"Size of the area of the area light, X direction size for rectangle shapes"
)

SIZE_Y_DESCRIPTION = (
	"Size of the area of the area light, Y direction size for rectangle shapes"
)

def store_units(self,context):
	global stored_power
	global stored_advanced_power
	global stored_efficacy
	global stored_lumen
	global stored_candela
	global stored_intensity
	
	light = context.light
	
	stored_power = light.energy
	stored_advanced_power = light.energy / advanced_power_factor(self,context)
	stored_lumen = light.energy / lumen_factor(self,context)
	stored_candela = light.energy /  candela_factor(self,context)
	stored_intensity = light.energy / artistic_factor(self,context)

def update_unit(self,context):
	global stored_power
	global stored_advanced_power
	global stored_efficacy
	global stored_lumen
	global stored_candela
	global stored_intensity
	
	if context.view_layer.objects.active.type == "LIGHT":
		settings = context.light.photographer

		if settings.light_unit == 'artistic':
			settings.intensity = stored_intensity

		if settings.light_unit == 'power':
			settings.power = stored_power

		if settings.light_unit == 'advanced_power':
			settings.advanced_power = stored_advanced_power

		if settings.light_unit == 'lumen':
			settings.lumen = stored_lumen

		if settings.light_unit == 'candela':
			settings.candela = stored_candela
			
def store_sun_units(self,context):
	global stored_irradiance
	global stored_illuminance

	light = context.light
	
	stored_irradiance = light.energy
	stored_illuminance = light.energy / illuminance_factor(self,context)
			
def update_sunlight_unit(self,context):
	global stored_irradiance
	global stored_illuminance
	
	if context.view_layer.objects.active.type == "LIGHT":
		settings = context.light.photographer

		if context.light.type == 'SUN':
			if settings.sunlight_unit == 'irradiance':
				settings.irradiance = stored_irradiance

			if settings.sunlight_unit == 'illuminance':
				settings.illuminance = stored_illuminance

def normalizebycolor(self,context):
	if context.view_layer.objects.active.type == "LIGHT":
		light = context.light
		settings = context.light.photographer
		if settings.normalizebycolor:
			x = functions.srgb_to_luminance(settings.color)
		else:
			x = 1
		return x
	
def artistic_factor(self,context):
	if context.view_layer.objects.active.type == "LIGHT":
		settings = context.light.photographer
		x = pow(2, settings.light_exposure)
		
		return x 

def advanced_power_factor(self,context):
	if context.view_layer.objects.active.type == "LIGHT":
		light = context.light
		settings = context.light.photographer
		
		if settings.light_type == 'SPOT':
			x = settings.efficacy / (683 * 2 * math.pi * (1 - math.cos(settings.spot_size/2)))* 4 * math.pi
			# Cycles Spotlight doesn't conserve energy by default and needs to be compensated.
		elif settings.light_type == 'AREA':
			x = settings.efficacy / (683 * 2)
		
		else:
			x = settings.efficacy / 683
			
		return x

def lumen_factor(self,context):
	if context.view_layer.objects.active.type == "LIGHT":
		light = context.light
		settings = context.light.photographer
		
		if settings.light_type == 'SPOT':
			x = 1 / (683 * 2 * math.pi * (1 - math.cos(settings.spot_size/2))) * 4 * math.pi
			# Cycles Spotlight doesn't conserve energy by default and needs to be compensated.
		elif settings.light_type == 'AREA':
			# Using 155 degrees angle for area lights to match brightness with spotlight
			x = 1 / (683 * 2 * (1 - math.cos(math.radians(155)/2))) 
		else:
			x = 1/ 683
		
		return x / normalizebycolor(self,context)
	
def candela_factor(self,context):
	if context.view_layer.objects.active.type == "LIGHT":
		light = context.light
		settings = context.light.photographer
		
		x = 1 / 683 * 4 * math.pi
		
		if settings.light_type == 'AREA':
			if settings.per_square_meter:
				obj_surface = context.object.scale[0] * context.object.scale[1]
				if settings.shape in {'SQUARE', 'DISK'}:
					x *= (settings.size * settings.size * obj_surface)
					x /=  math.pi
				elif settings.shape in {'RECTANGLE', 'ELLIPSE'}:
					x *= (settings.size * settings.size_y * obj_surface)
					x /=  math.pi					
			else:
				x /= math.pi
		
		return x / normalizebycolor(self,context)

def illuminance_factor(self,context):
	if context.view_layer.objects.active.type == "LIGHT":
		light = context.light
		settings = context.light.photographer
		
		x = 1 / 683
		
		return x / normalizebycolor(self,context)
		

def update_energy(self,context):
	if context.view_layer.objects.active.type == "LIGHT":
		light = context.light
		settings = context.light.photographer
		
		if settings.light_type == 'SUN':
			if settings.sunlight_unit == 'irradiance':
				light.energy = settings.irradiance
	
			elif settings.sunlight_unit == 'illuminance':
				light.energy = settings.illuminance * illuminance_factor(self,context)
	
		else:
			try:
				if settings.light_type == 'AREA':
					light.size = settings.size
					light.size_y = settings.size_y
			except AttributeError:
			    pass	
			
			if settings.light_unit == 'artistic':
				light.energy = settings.intensity * artistic_factor(self,context)
				
			elif settings.light_unit == 'power':
				light.energy = settings.power
				
			elif settings.light_unit == 'advanced_power':
				light.energy = settings.advanced_power * advanced_power_factor(self,context)
				
			elif settings.light_unit == 'lumen':
				light.energy = settings.lumen * lumen_factor(self,context)
											
			elif settings.light_unit == 'candela':
				light.energy = settings.candela * candela_factor(self,context)
			
		
		# Updating stored previous size values to check	if brightness needs to be re-calculated
		settings.spot_size_old = settings.spot_size
		settings.size_old = settings.size
		settings.size_y_old = settings.size_y

		store_units(self,context)
		store_sun_units(self,context)
		
# def update_sun_energy(self,context):
# 	if context.view_layer.objects.active.type == "LIGHT":
# 		light = context.light
# 		settings = context.light.photographer
# 
# 		# if settings.light_type == 'SUN':
# 		if settings.light_unit == 'irradiance':
# 			light.energy = settings.irradiance
# 
# 		elif settings.light_unit == 'illuminance':
# 			light.energy = settings.illuminance * illuminance_factor(self,context)
# 
# 		store_sun_units(self,context)		


# def update_spot_size(self,context):
# 	if context.view_layer.objects.active.type == "LIGHT":
# 		light = context.light
# 		settings = context.light.photographer
# 
# 		if settings.light_type == 'SPOT':
# 			light.spot_size = settings.spot_size
# 			update_energy(self,context)
			
def get_type(self):
	if self.id_data.type == 'POINT':
		return 0
	if self.id_data.type == 'SUN':
		return 1
	if self.id_data.type == 'SPOT':
		return 2
	if self.id_data.type == 'AREA':
		return 3

def set_type(self, light_type):
	if light_type == 0:
		self.id_data.type = 'POINT'
	if light_type == 1:
		self.id_data.type = 'SUN'
	if light_type == 2:
		self.id_data.type = 'SPOT'
	if light_type == 3:
		self.id_data.type = 'AREA'
	
	update_energy(self,bpy.context)
	return None

def get_irradiance(self):
	store_sun_units(self,bpy.context)
	return self.id_data.energy
	
def set_irradiance(self, irradiance):
	self.id_data.energy = irradiance
	return None

def get_illuminance(self):
	return self.id_data.energy / illuminance_factor(self,bpy.context)
	
def set_illuminance(self, illuminance):
	self.id_data.energy = illuminance * illuminance_factor(self,bpy.context)
	return None
	
def get_power(self):
	store_units(self,bpy.context)
	return self.id_data.energy
	
def set_power(self, power):
	self.id_data.energy = power
	return None

def get_advanced_power(self):
	return self.id_data.energy / advanced_power_factor(self,bpy.context)
	
def set_advanced_power(self,advanced_power):
	self.id_data.energy = advanced_power * advanced_power_factor(self,bpy.context)
	return None 
	
def get_color(self):
	return self.id_data.color
	
def set_color(self, color):
	self.id_data.color = color
	update_energy(self, bpy.context)
	return None
	
def get_shape(self):
	if self.id_data.shape == 'SQUARE':
		return 0
	if self.id_data.shape == 'RECTANGLE':
		return 1
	if bpy.context.light.shape == 'DISK':
		return 2
	if bpy.context.light.shape == 'ELLIPSE':
		return 3

def set_shape(self, shape):
	if shape == 0:
		self.id_data.shape = 'SQUARE'
	if shape == 1:
		self.id_data.shape = 'RECTANGLE'
	if shape == 2:
		self.id_data.shape = 'DISK'
	if shape == 3:
		self.id_data.shape = 'ELLIPSE'
	update_energy(self, bpy.context)

def get_size(self):
	if self.id_data.type == 'AREA':
		return self.id_data.size
	else:
		return 1

def set_size(self, size):
	if self.id_data.type == 'AREA':
		self.id_data.size = size
		update_energy(self, bpy.context)
	return None

def get_size_y(self):
	if self.id_data.type == 'AREA':
		return self.id_data.size_y
	else:
		return 1
		
def set_size_y(self, size_y):
	if self.id_data.type == 'AREA':
		self.id_data.size_y = size_y
		update_energy(self, bpy.context)
	return None

def get_spot_size(self):
	if self.id_data.type == 'SPOT':
		return self.id_data.spot_size
	else:
		return 1	
		
def set_spot_size(self, spot_size):
	if self.id_data.type == 'SPOT':
		self.id_data.spot_size = spot_size
		update_energy(self, bpy.context)
	return None

def get_light_temperature_color(self):
	color = camera.convert_temperature_to_RGB_table(self.light_temperature)
	color = [functions.srgb_to_linear(color[0]), functions.srgb_to_linear(color[1]), functions.srgb_to_linear(color[2])]
	return color
	
def set_light_temperature_color(self, context):
	color = camera.convert_temperature_to_RGB_table(context.light.photographer.light_temperature)
	color = [functions.srgb_to_linear(color[0]), functions.srgb_to_linear(color[1]), functions.srgb_to_linear(color[2])]
	self.id_data.color = color
	update_energy(self, bpy.context)
	

class PhotographerLightSettings(bpy.types.PropertyGroup):	

	light_types = [  
		("POINT", "Point", "Omnidirectional point light source",0),
	    ("SUN", "Sun", "Constant direction parallel ray light source",1),
	    ("SPOT", "Spot", "Directional cone light source",2),
	    ("AREA", "Area", "Directional area light source",3),
    ]
	light_type: EnumProperty(name="Light Type", items=light_types, get=get_type, set=set_type)
	
	color: FloatVectorProperty(
		name = "Color", description="Light Color",
		subtype ='COLOR', min=0.0, max=1.0, size=3,
		default = (1.0,1.0,1.0),
		get = get_color,
		set = set_color,
	)
	
	light_temperature : bpy.props.IntProperty(
		name="Color Temperature", description="Color Temperature (Kelvin)",
		min=1000, max=12000, default=6500,
		update=set_light_temperature_color
	)
	use_light_temperature: bpy.props.BoolProperty(
		name="Use Light Color Temperature",
		default=False,
		update=set_light_temperature_color
	)
	
	preview_color_temp : bpy.props.FloatVectorProperty(
		name='Preview Color', description="Color Temperature preview color",
		subtype='COLOR', min=0.0, max=1.0, size=3,
		get=get_light_temperature_color,
		set=set_light_temperature_color
	)

	sunlight_units = [  
        ("irradiance", "Irradiance (W/m2)", "Irradiance in Watt per square meter",1),
		("illuminance", "Illuminance (Lux)", "Illuminance in Lux",2),
    ]
	
	sunlight_unit: EnumProperty(name="Light Unit", items=sunlight_units, default='irradiance', update=update_sunlight_unit)
	irradiance: FloatProperty(name="Irradiance W/m2", default=1, min=0, precision=3 ,description=IRRADIANCE_DESCRIPTION, get=get_irradiance, set=set_irradiance)
	illuminance: FloatProperty(name="Lux", default=10, min=0, precision=2 ,description=ILLUMINANCE_DESCRIPTION, update=update_energy)
		
	light_units = [  
        ("power", "Power", "Radiant flux in Watt",1),
		("advanced_power", "Power (Advanced)", "Radiant flux in Watt",4),
        ("lumen", "Lumen", "Luminous flux in Lumen",2),
        ("candela", "Candela", "Luminous intensity in Candela",3),
		("artistic", "Artistic", "Artist friendly unit using Gain and Exposure",0),
    ]
	
	light_unit: EnumProperty(name="Light Unit", items=light_units, default='power', update=update_unit)
	intensity: FloatProperty(name="Intensity", default=10, min=0, description=INTENSITY_DESCRIPTION, update=update_energy)
	light_exposure: FloatProperty(name="Exposure", default=0, soft_min=-10,soft_max=10, precision=2, description=EXPOSURE_DESCRIPTION,
							update=update_energy)
	power: FloatProperty(name="Power", default=10, min=0, unit='POWER', precision=4 ,description=POWER_DESCRIPTION, get=get_power, set=set_power)
	advanced_power: FloatProperty(name="Power (Advanced)", default=10, min=0, unit='POWER', precision=4 ,description=POWER_DESCRIPTION, update=update_energy)
	efficacy: FloatProperty(name="Efficacy (lm/W)", default=683, min=0, description=EFFICACY_DESCRIPTION, update=update_energy)
	lumen: FloatProperty(name="Lumen", default=6830, min=0, precision=2, description=LUMEN_DESCRIPTION, update=update_energy)
	candela: FloatProperty(name="Candela", default=543.514, min=0, precision=3, description=CANDELA_DESCRIPTION, update=update_energy)
	normalizebycolor: BoolProperty(name="Normalize by Color Luminance", default=True, description=NORMALIZEBYCOLOR_DESCRIPTION, update=update_energy)
	spot_size: FloatProperty(name='Cone Angle (Size)', default=0.785398, min=0.0174533, max=3.14159, precision=3, unit='ROTATION', get=get_spot_size, set=set_spot_size, description=SPOT_SIZE_DESCRIPTION)
	spot_size_old: FloatProperty(name='Cone Angle (Size)', default=0.785398, min=0.0174533, max=3.14159, precision=3, unit='ROTATION')
	per_square_meter: BoolProperty(name="Per square meter", default=False, description=PER_SQUARE_METER_DESCRIPTION, update=update_energy)

	light_shapes = [  
        ("SQUARE", "Square", ""),
		("RECTANGLE", "Rectangle", ""),
        ("DISK", "Disk", ""),
        ("ELLIPSE", "Ellipse", ""),
    ]
	
	shape: EnumProperty(name="Shape", items=light_shapes, default='SQUARE', get=get_shape, set=set_shape)
	size: FloatProperty(name='Size', default=0.25, min=0, precision=3, unit='LENGTH', get=get_size, set=set_size, description=SIZE_DESCRIPTION)
	size_old: FloatProperty(name='Size', default=0.25, min=0, precision=3, unit='LENGTH', description=SIZE_DESCRIPTION)
	size_y: FloatProperty(name='Size Y', default=0.25, min=0, precision=3, unit='LENGTH',get=get_size_y, set=set_size_y, description=SIZE_Y_DESCRIPTION)
	size_y_old: FloatProperty(name='Size Y', default=0.25, min=0, precision=3, unit='LENGTH', description=SIZE_Y_DESCRIPTION)

