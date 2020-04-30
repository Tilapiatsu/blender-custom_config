import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'POINT'
physical_light.light_unit = 'lumen'
physical_light.use_light_temperature = True
physical_light.light_temperature = 5000
physical_light.color = (1.0, 0.7758222222328186, 0.6172065734863281)
physical_light.normalizebycolor = True
physical_light.power = 1.4424012899398804
physical_light.advanced_power = 10.0
physical_light.efficacy = 683.0
physical_light.lumen = 800.0
physical_light.candela = 543.5139770507812
physical_light.intensity = 10.0
physical_light.light_exposure = 0.0
light.shadow_soft_size = 0.05000000074505806
