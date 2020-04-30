import bpy
light = bpy.context.light
physical_light = bpy.context.light.photographer

light.type = 'POINT'
physical_light.light_unit = 'candela'
physical_light.use_light_temperature = True
physical_light.light_temperature = 1850
physical_light.color = (1.0, 0.2186063975095749, 0.0013658714015036821)
physical_light.normalizebycolor = True
physical_light.power = 0.049846574664115906
physical_light.advanced_power = 10.0
physical_light.efficacy = 683.0
physical_light.lumen = 6830.0
physical_light.candela = 1.0
physical_light.intensity = 10.0
physical_light.light_exposure = 0.0
light.shadow_soft_size = 0.019999999552965164
