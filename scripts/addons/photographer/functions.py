import bpy
import math

ev_lookup =	 ["Starlight","Aurora Borealis","Half Moon","Full Moon","Full Moon in Snowscape",
			"Dim artifical light","Dim artifical light","Distant view of lit buildings",
			"Distant view of lit buildings","Fireworks","Candle","Campfire","Home interior",
			"Night Street","Office Lighting","Neon Signs","Skyline after Sunset","Sunset",
			"Heavy Overcast","Bright Cloudy","Hazy Sun","Sunny","Bright Sun"]

# sRGB to linear function
def srgb_to_linear(x):
	a = 0.055
	if x <= 0.04045 :
		y = x * (1.0 / 12.92)
	else:
		y = pow( (x + a) * (1.0 / (1 + a)), 2.4)
	return y

def srgb_to_luminance(color):	
	luminance = 0.2126729*color[0] + 0.7151522*color[1] + 0.072175*color[2]
	return luminance

def update_exposure_guide(self,context,ev):
	if ev <= 16 and ev >= -6:
		ev = int(ev+6)
		ev_guide = ev_lookup[ev]
	else:
		ev_guide = "Out of realistic range"
	return ev_guide

def calc_exposure_value(self, context,settings):
	if settings.exposure_mode == 'EV':
		EV = settings.ev - settings.exposure_compensation
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
		EV = round(EV, 2) - settings.exposure_compensation
	return EV