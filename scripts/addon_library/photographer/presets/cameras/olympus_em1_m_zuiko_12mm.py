import bpy
camera = bpy.context.scene.camera.data
photographer = bpy.context.scene.camera.data.photographer

photographer.sensor_type = '18'
photographer.aperture = 1.2
photographer.aperture_preset = '1.2'
photographer.aperture_slider_enable = False
camera.lens = 12.0
camera.dof.use_dof = True
camera.dof.aperture_ratio = 1.0
camera.dof.aperture_blades = 9
camera.dof.aperture_rotation = 0.0
