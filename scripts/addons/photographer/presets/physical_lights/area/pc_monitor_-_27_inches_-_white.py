import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'AREA'
light.shape = 'RECTANGLE'
light.size = 0.5979999899864197
light.size_y = 0.3370000123977661
physical_light.light_unit = 'candela'
physical_light.use_light_temperature = False
physical_light.light_temperature = 6500
physical_light.color = (1.0, 1.0, 1.0)
physical_light.normalizebycolor = True
physical_light.power = 0.29506000876426697
physical_light.advanced_power = 10.0
physical_light.efficacy = 683.0
physical_light.lumen = 800.0
physical_light.candela = 250.0
physical_light.per_square_meter = True
physical_light.intensity = 10.0
physical_light.light_exposure = 0.0
