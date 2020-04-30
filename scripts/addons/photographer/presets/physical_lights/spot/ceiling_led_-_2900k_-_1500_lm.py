import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'SPOT'
light.spot_blend = 0.6000000238418579
light.shadow_soft_size = 0.03500000014901161
physical_light.spot_size = 1.9945622682571411
physical_light.light_unit = 'lumen'
physical_light.use_light_temperature = True
physical_light.light_temperature = 2900
physical_light.color = (1.0, 0.43598365783691406, 0.12833361327648163)
physical_light.normalizebycolor = True
physical_light.power = 17.991670608520508
physical_light.advanced_power = 0.0
physical_light.efficacy = 683.0
physical_light.lumen = 1500.0
physical_light.candela = 346.6791076660156
physical_light.per_square_meter = False
physical_light.intensity = 10.0
physical_light.light_exposure = 0.0
