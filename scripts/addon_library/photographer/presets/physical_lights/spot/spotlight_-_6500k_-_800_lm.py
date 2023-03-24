import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'SPOT'
light.spot_blend = 0.15000000596046448
light.shadow_soft_size = 0.029999999329447746
physical_light.spot_size = 1.0471975803375244
physical_light.light_unit = 'lumen'
physical_light.use_light_temperature = True
physical_light.light_temperature = 6500
physical_light.color = (1.0, 1.0, 1.0)
physical_light.normalizebycolor = True
physical_light.power = 17.48544692993164
physical_light.advanced_power = 10.0
physical_light.efficacy = 683.0
physical_light.lumen = 800.0
physical_light.candela = 543.5139770507812
physical_light.per_square_meter = True
physical_light.intensity = 10.0
physical_light.light_exposure = 0.0
