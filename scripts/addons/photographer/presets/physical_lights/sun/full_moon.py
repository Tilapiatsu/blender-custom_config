import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'SUN'
light.angle = 0.008726646192371845
physical_light.use_light_temperature = True
physical_light.light_temperature = 4100
physical_light.color = (1.0, 0.6618756651878357, 0.38642942905426025)
physical_light.normalizebycolor = True
physical_light.sunlight_unit = 'illuminance'
physical_light.irradiance = 0.00020508727175183594
physical_light.illuminance = 0.10000000149011612
