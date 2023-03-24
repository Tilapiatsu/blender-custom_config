import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'POINT'
physical_light.light_unit = 'lumen'
physical_light.use_light_temperature = True
physical_light.light_temperature = 2700
physical_light.color = (1.0, 0.3967552185058594, 0.09530746936798096)
physical_light.normalizebycolor = True
physical_light.power = 1.890917420387268
physical_light.advanced_power = 10.0
physical_light.efficacy = 683.0
physical_light.lumen = 650.0
physical_light.candela = 543.5139770507812
physical_light.intensity = 10.0
physical_light.light_exposure = 0.0
light.shadow_soft_size = 0.05
