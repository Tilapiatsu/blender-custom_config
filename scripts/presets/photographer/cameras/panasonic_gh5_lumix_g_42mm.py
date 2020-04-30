import bpy
camera = bpy.context.scene.camera.data
photographer = bpy.context.scene.camera.data.photographer

photographer.sensor_type = '18'
photographer.aperture = 1.7
photographer.aperture_preset = '1.8'
photographer.aperture_slider_enable = True
camera.lens = 42.0
camera.dof.use_dof = True
camera.dof.aperture_ratio = 1.0
camera.dof.aperture_blades = 7
camera.dof.aperture_rotation = 0.0
