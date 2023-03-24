import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'SUN'
light.angle = 0.009180432185530663
physical_light.use_light_temperature = True
physical_light.light_temperature = 5600
physical_light.color = (1.0, 0.8468732237815857, 0.7590044736862183)
physical_light.normalizebycolor = True
physical_light.sunlight_unit = 'illuminance'
physical_light.irradiance = 186.1399688720703
physical_light.illuminance = 111000.0
