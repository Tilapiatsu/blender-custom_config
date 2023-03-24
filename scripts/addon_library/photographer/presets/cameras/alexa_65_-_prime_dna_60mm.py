import bpy
camera = bpy.context.scene.camera.data
photographer = bpy.context.scene.camera.data.photographer

photographer.sensor_type = '54.12'
photographer.aperture = 2.200000047683716
photographer.aperture_preset = '2.8'
photographer.aperture_slider_enable = True
camera.lens = 60.0
camera.dof.use_dof = True
camera.dof.aperture_ratio = 1.0
camera.dof.aperture_blades = 11
camera.dof.aperture_rotation = 0.0
