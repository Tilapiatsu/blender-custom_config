import bpy

from bpy_extras import view3d_utils					   
from mathutils import Vector


# AF Tracker functions	

def create_af_target(context,location):
	camera = context.scene.camera
	settings = camera.data.photographer

	af_target = bpy.data.objects.new(camera.name + "_AF_Tracker", None)
	af_target.empty_display_type = "CUBE"
	af_target.show_name = True
	af_target.show_in_front = True

	context.scene.camera.data.dof.focus_object = af_target

	# new_loc = camera.matrix_world.inverted() @ location

	settings.af_target = af_target
	settings.af_target.location = location

	context.view_layer.active_layer_collection.collection.objects.link(af_target)

def delete_af_target(context):
	camera = context.scene.camera
	settings = camera.data.photographer
	af_target = settings.af_target

	settings.af_target = None

	if bpy.context.scene.render.engine == 'LUXCORE':
		use_dof = context.scene.camera.data.luxcore.use_dof
	else:
		use_dof = context.scene.camera.data.dof.use_dof

	if use_dof == False:
		use_dof = True
		if camera.data.dof.focus_object == af_target:
			context.scene.camera.data.dof.focus_object == None


	context.view_layer.active_layer_collection.collection.objects.unlink(af_target)

	obj = bpy.data.objects
	obj.remove(obj[af_target.name])


def update_af_target(context,location):
	camera = context.scene.camera
	settings = camera.data.photographer
	settings.af_target.location = (10,10,10)

def set_af_key(context):
	camera = context.scene.camera
	settings = camera.data.photographer

	current_frame = context.scene.frame_current
	camera.data.dof.keyframe_insert(data_path='focus_distance', frame=(current_frame))

def stop_playback(scene):
	settings = scene.camera.data.photographer

	if scene.frame_current == scene.frame_end:
		bpy.ops.screen.animation_cancel(restore_frame=False)
		settings.af_continuous_enabled = False
		bpy.app.handlers.frame_change_pre.remove(stop_playback)

# def lerp_focus_distance(ray_length, context):
	# context.scene.camera.data.dof.focus_distance = context.scene.camera.data.dof.focus_distance + (ray_length - context.scene.camera.data.dof.focus_distance) / 2
	# return 0.02

# Focus picker
def focus_raycast(context, event, continuous):

	scene = bpy.context.scene
	cam = scene.camera
	cam_matrix = cam.matrix_world

	org = cam_matrix @ Vector((0.0, 0.0, 0.0))

	if continuous:
		dst = cam_matrix @ Vector((0.0, 0.0, 100.0 * -1))
	else:
		region = context.region
		rv3d = context.region_data
		coord = event.mouse_region_x, event.mouse_region_y

		# Get the ray from the viewport and mouse
		view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
		dst = ray_origin + view_vector

	dir = dst - org

	vl = bpy.context.view_layer

	result, location, normal, index, object, matrix = scene.ray_cast(vl, org, dir)


	if result:
		length = (location - org).length
		# else:
		context.scene.camera.data.dof.focus_distance = length

	else:
		context.scene.camera.data.dof.focus_distance = 100

	return location


class PHOTOGRAPHER_OT_FocusSingle(bpy.types.Operator):
	"""Autofocus Single: Click where you want to focus"""
	bl_idname = "photographer.focus_single"
	bl_label = "Photographer Focus Single"

	def modal(self, context, event):
		# Allow navigation for Blender and Maya shortcuts
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
			return {'PASS_THROUGH'}

		settings = context.scene.camera.data.photographer

		# Disable AF-C if using AF-C
		if settings.af_continuous_enabled:
			settings.af_continuous_enabled = False

		# Enter focus picker
		if event.type == 'LEFTMOUSE':
			if event.value == 'RELEASE':
				if context.space_data.type == 'VIEW_3D':
					try:
						#Enable DoF
						if bpy.context.scene.render.engine == 'LUXCORE':
							use_dof = context.scene.camera.data.luxcore.use_dof
						else:
							use_dof = context.scene.camera.data.dof.use_dof

						use_dof = True
						focus_raycast(context, event, False)
						if context.scene.camera.data.dof.focus_object is not None:
							self.report({'WARNING'}, "There is an object set as focus target which will override the results of the Autofocus")


						#Set key if animate is on
						if settings.af_animate:
							bpy.ops.object.select_all(action='DESELECT')
							bpy.data.objects[context.scene.camera.name].select_set(True)
							context.view_layer.objects.active = context.scene.camera

							set_af_key(context)

					except:
						self.report({'ERROR'}, "An error occured during the raycast. Is the targeted object a mesh?")
					context.window.cursor_modal_restore()
					return {'FINISHED'}
				else:
					self.report({'WARNING'}, "Active space must be a View3d")
					if self.cursor_set: context.window.cursor_modal_restore()
				return {'CANCELLED'}

		# Cancel Modal with RightClick and ESC
		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):
		self.cursor_set = True
		context.window.cursor_modal_set('EYEDROPPER')
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

class PHOTOGRAPHER_OT_FocusTracking(bpy.types.Operator):
	"""Autofocus Tracket: Click where you want to place the tracker"""
	bl_idname = "photographer.focus_tracking"
	bl_label = "Photographer Focus Tracking"

	def modal(self, context, event):
		# Allow navigation for Blender and Maya shortcuts
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
			return {'PASS_THROUGH'}

		settings = context.scene.camera.data.photographer

		#Store the current object selection
		current_sel = context.selected_objects
		active_obj = context.view_layer.objects.active

		# Disable AF-C if using AF-C
		if settings.af_continuous_enabled:
			settings.af_continuous_enabled = False

		# Enter focus picker
		if event.type == 'LEFTMOUSE':
			if event.value == 'RELEASE':
				if context.space_data.type == 'VIEW_3D':
					try:

						#Enable DoF

						if bpy.context.scene.render.engine == 'LUXCORE':
							use_dof = context.scene.camera.data.luxcore.use_dof
						else:
							use_dof = context.scene.camera.data.dof.use_dof

						use_dof = True

						#Select what's under the mouse and store its name
						bpy.ops.view3d.select(extend=False, deselect=False, location=(event.mouse_region_x, event.mouse_region_y))
						parent_obj = bpy.context.selected_objects[0]

						#Raycast and store the hit location
						location = focus_raycast(context, event, False)

						#Calculate the location relative to the parent object
						new_loc = parent_obj.matrix_world.inverted() @ location

						#Create AF Tracking target object at the hit location
						create_af_target(context,new_loc)

						settings.af_target.empty_display_size = (1.0/parent_obj.scale.x)/10.0
						#Parent the target object to the object under the mask
						settings.af_target.parent = parent_obj

						#Set the Tracking to enable
						settings.af_tracking_enabled = True

						bpy.ops.object.select_all(action='DESELECT')
						#Restore the previous selection
						if current_sel:
							bpy.ops.object.select_all(action='DESELECT')
							for o in current_sel:
								bpy.data.objects[o.name].select_set(True)
						if active_obj:
							context.view_layer.objects.active = active_obj


					except:
						self.report({'ERROR'}, "An error occured during the raycast. Is the targeted object a mesh?")
					context.window.cursor_modal_restore()
					return {'FINISHED'}
				else:
					self.report({'WARNING'}, "Active space must be a View3d")
					if self.cursor_set: context.window.cursor_modal_restore()
				return {'CANCELLED'}

		# Cancel Modal with RightClick and ESC
		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):
		self.cursor_set = True
		context.window.cursor_modal_set('EYEDROPPER')
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}


class PHOTOGRAPHER_OT_FocusTracking_Cancel(bpy.types.Operator):
	"""Autofocus Single: Click where you want to focus"""
	bl_idname = "photographer.focus_tracking_cancel"
	bl_label = "Photographer Focus Tracking Cancel"

	def execute(self, context):

		settings = context.scene.camera.data.photographer

		try:
			delete_af_target(context)
		except:
			settings.af_target = None
			self.report({'WARNING'}, "The AF-Track target object is not present in the scene anymore")

		settings.af_tracking_enabled = False

		return{'FINISHED'}


class PHOTOGRAPHER_OT_CheckFocusObject(bpy.types.Operator):
	"""Autofocus Single: Click where you want to focus"""
	bl_idname = "photographer.check_focus_object"
	bl_label = "Photographer Check Focus Object"

	def execute(self, context):

		settings = context.scene.camera.data.photographer
		if context.scene.camera.data.dof.focus_object is not None:
			self.report({'WARNING'}, "There is an object set as focus target which will override the results of the Autofocus.")

		return{'FINISHED'}



# Focus continuous timer function
def focus_continuous():
	context = bpy.context
	scene = context.scene
	settings = context.scene.camera.data.photographer
	timer = settings.af_continuous_interval

	#Enable DoF
	if bpy.context.scene.render.engine == 'LUXCORE':
		use_dof = context.scene.camera.data.luxcore.use_dof
	else:
		use_dof = context.scene.camera.data.dof.use_dof

	use_dof = True

	# Do not AF-C if active camera is not a camera
	if context.scene.camera:
		if context.scene.camera.type == 'CAMERA':
			settings = context.scene.camera.data.photographer
			if settings.af_continuous_enabled :
				focus_raycast(context, None, True)

				#Little trick to update viewport as the header distance doesn't update automatically
				exposure = bpy.context.scene.view_settings.exposure
				bpy.context.scene.view_settings.exposure = exposure

			#Set key if animate is on
			if settings.af_animate:
				#Select camera to see the keyframes
				bpy.ops.object.select_all(action='DESELECT')
				bpy.data.objects[context.scene.camera.name].select_set(True)
				context.view_layer.objects.active = context.scene.camera
				set_af_key(context)

	return timer



def focus_single_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA':
						settings = context.scene.camera.data.photographer
						# if context.scene.camera == bpy.context.active_object:
						if settings.af_tracking_enabled == False:
							icon_af = 'RESTRICT_RENDER_OFF'
							if settings.af_animate:
								icon_af = 'KEYTYPE_KEYFRAME_VEC'
							self.layout.operator("photographer.focus_single", text="AF-S", icon=icon_af)

def focus_continuous_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA' :
						settings = context.scene.camera.data.photographer
						if settings.af_tracking_enabled == False:

							icon_af = 'HOLDOUT_ON'
							if settings.af_animate:
								icon_af = 'KEYTYPE_KEYFRAME_VEC'

							self.layout.prop(settings, "af_continuous_enabled", text="AF-C", icon=icon_af )

def focus_animate_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA' :
						settings = context.scene.camera.data.photographer
						self.layout.prop(settings, "af_animate", text="", icon="KEY_HLT" )

def focus_tracking_button(self, context):
	# Hide AF buttons if the active camera in the scene isn't a camera
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA':
						settings = context.scene.camera.data.photographer
						if settings.af_tracking_enabled == False:
							self.layout.operator("photographer.focus_tracking", text="AF-Track", icon='OBJECT_DATA')
						if settings.af_tracking_enabled:
							self.layout.operator("photographer.focus_tracking_cancel", text="Cancel AF Tracking", icon='OBJECT_DATA')

def focus_distance_header(self, context):
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			if area.spaces[0].region_3d.view_perspective == 'CAMERA' :
				if context.scene.camera:
					if context.scene.camera.type == 'CAMERA' and not context.scene.camera.data.photographer.af_tracking_enabled:
						dof_distance = str(round(context.scene.camera.data.dof.focus_distance*context.scene.unit_settings.scale_length,2))
						if not context.scene.unit_settings.system == 'NONE':
							dof_distance = dof_distance + "m"
						self.layout.label(text=dof_distance)