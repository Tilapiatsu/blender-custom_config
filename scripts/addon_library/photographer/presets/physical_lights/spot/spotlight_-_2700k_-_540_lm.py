import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'SPOT'
light.spot_blend = 0.15000000596046448
light.shadow_soft_size = 0.029999999329447746
physical_light.spot_size = 1.1344640254974365
physical_light.light_unit = 'lumen'
physical_light.use_light_temperature = True
physical_light.light_temperature = 2700
physical_light.color = (1.0, 0.3967552185058594, 0.09530746936798096)
physical_light.normalizebycolor = True
physical_light.power = 20.061687469482422
physical_light.advanced_power = 10.0
physical_light.efficacy = 683.0
physical_light.lumen = 540.0
physical_light.candela = 543.5139770507812
physical_light.per_square_meter = True
physical_light.intensity = 10.0
physical_light.light_exposure = 0.0
