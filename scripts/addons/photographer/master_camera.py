import bpy

from . import camera 

# MASTER CAMERA #
def interpolate_location(obj1, obj2, time):

	obj1.rotation_euler.x = obj1.rotation_euler.x + (obj2.rotation_euler.x - obj1.rotation_euler.x)/time
	obj1.rotation_euler.y = obj1.rotation_euler.y + (obj2.rotation_euler.y - obj1.rotation_euler.y)/time
	obj1.rotation_euler.z = obj1.rotation_euler.z + (obj2.rotation_euler.z - obj1.rotation_euler.z)/time

	obj1.location = obj1.location + (obj2.location - obj1.location)/time

	distance = (obj2.location - obj1.location).length

	return distance

def interpolate_float(obj1, obj2, time):

	obj1 = obj1 + (obj2 - obj1) / time
	distance = obj2 - obj1

	return distance

def match_camera():
	context = bpy.context

	master_cam = bpy.data.objects.get('MasterCamera')
	# target_cam = bpy.data.objects.get(camera)
	target_cam = master_cam.data.photographer.target_camera

	match_speed = master_cam.data.photographer.match_speed
	settings_speed = match_speed / 2
	if settings_speed < 1:
		settings_speed == 1
	master_cam.data.photographer.is_matching = True

	distance = interpolate_location(master_cam,target_cam, match_speed)

	if master_cam.data.sensor_width != target_cam.data.sensor_width:
		master_cam.data.sensor_width = master_cam.data.sensor_width + (target_cam.data.sensor_width - master_cam.data.sensor_width)/settings_speed

	if not master_cam.data.photographer.af_continuous_enabled:

		if bpy.context.scene.render.engine == 'LUXCORE':
			master_cam.data.luxcore.use_dof = target_cam.data.luxcore.use_dof
		else:
			master_cam.data.dof.use_dof = target_cam.data.dof.use_dof
			# interpolate_float(master_cam.data.dof.focus_distance,target_cam.data.dof.focus_distance, settings_speed)
			master_cam.data.dof.focus_distance = master_cam.data.dof.focus_distance +(target_cam.data.dof.focus_distance - master_cam.data.dof.focus_distance)/settings_speed



	if context.scene.view_settings.use_curve_mapping:
		# interpolate_float(master_cam.data.photographer.color_temperature,target_cam.data.photographer.color_temperature, settings_speed)
		# interpolate_float(master_cam.data.photographer.tint,target_cam.data.photographer.tint, settings_speed)
		master_cam.data.photographer.color_temperature = master_cam.data.photographer.color_temperature + (target_cam.data.photographer.color_temperature - master_cam.data.photographer.color_temperature)/settings_speed
		master_cam.data.photographer.tint = master_cam.data.photographer.tint + (target_cam.data.photographer.tint - master_cam.data.photographer.tint)/settings_speed

	if target_cam.data.photographer.exposure_enabled:
		master_cam.data.photographer.exposure_enabled = True
		# interpolate_float(master_cam.data.photographer.aperture,target_cam.data.photographer.aperture, settings_speed)
		# interpolate_float(master_cam.data.photographer.ev,target_cam.data.photographer.ev, settings_speed)

		master_cam.data.photographer.exposure_mode = target_cam.data.photographer.exposure_mode
		if target_cam.data.photographer.exposure_mode == 'EV':
			master_cam.data.photographer.ev = master_cam.data.photographer.ev + (target_cam.data.photographer.ev - master_cam.data.photographer.ev)/settings_speed

		if target_cam.data.photographer.exposure_mode == 'MANUAL':

			# ISO
			if master_cam.data.photographer.iso_slider_enable == False:
				master_cam.data.photographer.iso_slider_enable = True

			if target_cam.data.photographer.iso_slider_enable == False:
				target_cam.data.photographer.iso = float(target_cam.data.photographer.iso_preset)

			master_cam.data.photographer.iso = master_cam.data.photographer.iso + (target_cam.data.photographer.iso - master_cam.data.photographer.iso)/settings_speed

			# Shutter Speed or Shutter Angle
			if target_cam.data.photographer.shutter_mode == 'SPEED':

				if master_cam.data.photographer.shutter_speed_slider_enable == False:
					master_cam.data.photographer.shutter_speed_slider_enable = True

				if target_cam.data.photographer.shutter_speed_slider_enable == False:
					target_cam.data.photographer.shutter_speed = float(target_cam.data.photographer.shutter_speed_preset)

				master_cam.data.photographer.shutter_speed = master_cam.data.photographer.shutter_speed + (target_cam.data.photographer.shutter_speed - master_cam.data.photographer.shutter_speed)/settings_speed

			if target_cam.data.photographer.shutter_mode == 'ANGLE':

				if master_cam.data.photographer.shutter_angle_slider_enable == False:
					master_cam.data.photographer.shutter_angle_slider_enable = True

				if target_cam.data.photographer.shutter_angle_slider_enable == False:
					target_cam.data.photographer.shutter_angle = float(target_cam.data.photographer.shutter_angle_preset)

				master_cam.data.photographer.shutter_angle = master_cam.data.photographer.shutter_angle + (target_cam.data.photographer.shutter_angle - master_cam.data.photographer.shutter_angle)/settings_speed

		# Aperture
		if master_cam.data.photographer.aperture_slider_enable == False:
			master_cam.data.photographer.aperture_slider_enable = True

		if target_cam.data.photographer.aperture_slider_enable == False:
			target_cam.data.photographer.aperture = float(target_cam.data.photographer.aperture_preset)

		master_cam.data.photographer.aperture = master_cam.data.photographer.aperture + (target_cam.data.photographer.aperture - master_cam.data.photographer.aperture)/settings_speed


	if master_cam.data.lens != target_cam.data.lens:
		# interpolate_float(master_cam.data.lens,target_cam.data.lens, settings_speed)
		master_cam.data.lens = master_cam.data.lens + (target_cam.data.lens - master_cam.data.lens) / settings_speed

	#Little trick to update viewport
	bpy.ops.photographer.updatesettings()

	# print (length)
	threshold = 0.003
	if distance < threshold:
		master_cam.data.photographer.is_matching = False
		return None

	return 0.01

# SET CAMERA VIEW
class MASTERCAMERA_OT_LookThrough(bpy.types.Operator):
	bl_idname = 'mastercamera.look_through'
	bl_label = 'Look through'
	bl_description = "Set as Scene Camera and look through it"
	bl_options = {'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):

		context.view_layer.objects.active = bpy.data.objects[self.camera]

		cam = bpy.data.objects.get(self.camera)
		if cam.data.show_name != True:
			cam.data.show_name = True

		bpy.ops.view3d.object_as_camera()
		camera.update_settings(self,context)

		return{'FINISHED'}

class MASTERCAMERA_OT_SelectCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.select_cam'
	bl_label = 'Select camera'
	bl_description = "Select this camera"
	bl_options = {'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):

		bpy.ops.object.select_all(action='DESELECT')
		bpy.data.objects[self.camera].select_set(True)
		context.view_layer.objects.active = bpy.data.objects[self.camera]

		return{'FINISHED'}

class MASTERCAMERA_OT_AddMasterCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.add_mastercam'
	bl_label = 'Add Master Camera'
	bl_description = "Create a Master Camera that can fly to other cameras"
	bl_options = {'UNDO'}

	def execute(self,context):
		if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
			context.area.spaces[0].region_3d.view_perspective='PERSP'

		if bpy.data.objects.get('MasterCamera') and bpy.data.objects.get('MasterCamera').type != 'CAMERA':
				self.report({'ERROR'}, "There is already an object named Master Camera which isn't a camera. Please delete or rename it")
		else:
			bpy.ops.object.camera_add()
			context.active_object.name = "MasterCamera"
			master_cam_obj = bpy.data.objects[bpy.context.active_object.name]
			context.scene.camera = master_cam_obj
			bpy.ops.view3d.camera_to_view()
			master_cam_obj.data.show_name = True

		return{'FINISHED'}

class MASTERCAMERA_OT_AddCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.add_cam'
	bl_label = 'Add Camera'
	bl_description = "Add a new Camera from the current view"
	bl_options = {'UNDO'}

	def execute(self,context):
		if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
			context.area.spaces[0].region_3d.view_perspective='PERSP'
		new_cam = bpy.ops.object.camera_add()

		new_cam_obj = bpy.data.objects[bpy.context.active_object.name]
		context.scene.camera = new_cam_obj
		bpy.ops.view3d.camera_to_view()
		new_cam_obj.data.show_name = True

		return{'FINISHED'}

# Delete Camera
class MASTERCAMERA_OT_DeleteCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.delete_cam'
	bl_label = 'Delete Camera'
	bl_description = "Delete camera"
	bl_options = {'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):
		cam=bpy.data.objects[self.camera]
		bpy.data.objects.remove(cam)

		return{'FINISHED'}

# Delete Master Camera
class MASTERCAMERA_OT_DeleteMasterCamera(bpy.types.Operator):
	bl_idname = 'mastercamera.delete_mastercam'
	bl_label = 'Delete Master Camera'
	bl_description = "Delete Master Camera"
	bl_options = {'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):
		cam=bpy.data.objects[self.camera]

		bpy.data.objects.remove(cam)
		return{'FINISHED'}

class MASTERCAMERA_OT_SwitchCamera(bpy.types.Operator):
	bl_idname = "view3d.switch_camera"
	bl_label = "Switch to this camera"
	bl_description = "Switch to this camera"
	bl_options = {'REGISTER', 'UNDO'}

	camera: bpy.props.StringProperty()

	def execute(self,context):
		cam = self.camera

		if bpy.app.timers.is_registered(match_camera):
			bpy.app.timers.unregister(match_camera)

		if bpy.data.objects.get('MasterCamera') and bpy.data.objects.get('MasterCamera').type == 'CAMERA':
			if context.scene.camera != bpy.data.objects.get('MasterCamera'):
				context.scene.camera = bpy.data.objects.get('MasterCamera')

			master_cam = bpy.data.objects.get('MasterCamera')
			# context.scene.camera.data.photographer.target_camera = bpy.data.objects.get(cam)
			master_cam.data.photographer.target_camera = bpy.data.objects.get(cam)

			if master_cam.data.photographer.target_camera is None:
				self.report({'WARNING'}, "The camera" + target_camera + " doesn't exist anymore. Are you using a keyboard shortcut assigned to an old camera? Either create a camera named" + target_cam+ ", or remove the shortcut")

			else: bpy.app.timers.register(match_camera)

		else:
			self.report({'WARNING'}, "There is no Master Camera in the scene. Please create one first")

		return {'FINISHED'}