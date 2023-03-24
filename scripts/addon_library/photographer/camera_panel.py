import bpy
from .functions import calc_exposure_value, update_exposure_guide
from . import (
	camera_presets,
)


class PHOTOGRAPHER_PT_Panel(bpy.types.Panel):
	# bl_idname = "CAMERA_PT_Photographer"
	bl_label = "Photographer"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		# Add Panel properties to cameras
		return context.camera

	def draw(self, context):
		layout = self.layout
		settings = context.camera.photographer
		scene = bpy.context.scene

		# UI if camera isn't active
		if scene.camera != bpy.context.active_object:
			layout.label(text="This is not the Active Camera")

			row = layout.row()
			row.operator("photographer.makecamactive", text="Make Active Camera")
			row.operator("photographer.selectactivecam", text="Select Active Camera")

		col = layout.column()
		# Enable UI if Camera is Active
		if scene.camera != bpy.context.active_object:
			col.enabled = False

		col.operator("photographer.updatesettings", text="Apply all Settings")


#### CAMERA SETTINGS PANEL ####
class PHOTOGRAPHER_PT_ViewPanel_Camera(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Photographer'
	bl_label = 'Scene Camera and Lens'

	@classmethod
	def poll(cls, context):
		# Add Panel properties to cameras
		return context.scene.camera

	
	def draw_header_preset(self, context):
		camera_presets.PHOTOGRAPHER_PT_CameraPresets.draw_panel_header(self.layout)
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False
		
		camera = context.scene.camera.data
		settings = context.scene.camera.data.photographer
	
		col = layout.column(align=True)
		col.prop(settings,'sensor_type')
		if settings.sensor_type == 'CUSTOM':
			col.prop(camera,'sensor_width')
		# col = layout.column(align=True)	
		# col.prop(camera,'clip_start')
		# col.prop(camera,'clip_end')		
		layout.prop(camera,'lens')
		
		layout.prop(camera.dof,'use_dof', text='Enable Depth of Field')
		
		# Aperture parameter
		row = layout.row(align = True)

		if bpy.context.scene.render.engine == 'LUXCORE':
			use_dof = context.scene.camera.data.luxcore.use_dof
		else:
			use_dof = context.scene.camera.data.dof.use_dof

		row.enabled = use_dof
		if not settings.aperture_slider_enable:
			row.prop(settings, 'aperture_preset', text='Aperture')
		else:
			row.prop(settings, 'aperture', slider=True, text='Aperture F-stop')
		row.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')
		
		col = layout.column(align=True)
		col.prop(camera.dof,'aperture_ratio', text="Anamorphic Ratio")
		col.prop(camera.dof,'aperture_blades')
		col.prop(camera.dof,'aperture_rotation')	
		if camera.dof.use_dof:
			col.enabled = True
		else:
			col.enabled = False
				

		
#### EXPOSURE PANELS ####		

def exposure_header_preset(self, context, settings, guide):
		layout = self.layout
		layout.enabled = settings.exposure_enabled
		row = layout.row(align=False)
		row.alignment = 'RIGHT'

		ev = calc_exposure_value(self, context, settings)
		if guide == True:
			ev_guide = update_exposure_guide(self, context, ev)
			row.label(text = ev_guide + " - " + "EV: " + str("%.2f" % ev) )
		else:
			row.label(text = "EV: " + str("%.2f" % ev) )

def exposure_header(self, context, settings):
		self.layout.prop(settings, "exposure_enabled", text="")


def exposure_panel(self, context, settings, show_aperture):
		layout = self.layout
		scene = bpy.context.scene

		layout.use_property_split = True
		layout.use_property_decorate = False
		layout.enabled = settings.exposure_enabled

		layout.row().prop(settings, 'exposure_mode',expand=True)

		# Settings in EV Mode
		if settings.exposure_mode == 'EV':
			layout.prop(settings, 'ev', slider=True)
			layout.prop(settings, 'exposure_compensation', text='Exposure Compensation')


			# Shutter Speed parameter
			row = layout.row(align = True)
			row.enabled = settings.motionblur_enabled
			if settings.shutter_mode == 'SPEED':
				if not settings.shutter_speed_slider_enable:
					row.prop(settings, 'shutter_speed_preset', text='Shutter Speed')
				else:
					row.prop(settings, 'shutter_speed', slider=True)
				row.operator("photographer.setshutterangle",icon="DRIVER_ROTATIONAL_DIFFERENCE", text="")
				row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

			if settings.shutter_mode == 'ANGLE':
				if not settings.shutter_speed_slider_enable:
					row.prop(settings, 'shutter_angle_preset', text='Shutter Angle')
				else:
					row.prop(settings, 'shutter_angle', slider=True)
				row.operator("photographer.setshutterspeed",icon="PREVIEW_RANGE", text="")
				row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

			# Aperture parameter
			row = layout.row(align = True)

			if bpy.context.scene.render.engine == 'LUXCORE':
				use_dof = context.scene.camera.data.luxcore.use_dof
			else:
				use_dof = context.scene.camera.data.dof.use_dof

			row.enabled = use_dof
			if show_aperture:
				if not settings.aperture_slider_enable:
					row.prop(settings, 'aperture_preset', text='Aperture')
				else:
					row.prop(settings, 'aperture', slider=True, text='Aperture F-stop / DOF only')
				row.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')

		else:

			# Shutter Speed parameter
			if settings.shutter_mode == 'SPEED':
				row = layout.row(align = True)
				if not settings.shutter_speed_slider_enable:
					row.prop(settings, 'shutter_speed_preset', text='Shutter Speed')
				else:
					row.prop(settings, 'shutter_speed', slider=True)
				row.operator("photographer.setshutterangle",icon="DRIVER_ROTATIONAL_DIFFERENCE", text="")
				row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')

			if settings.shutter_mode == 'ANGLE':
				row = layout.row(align = True)
				if not settings.shutter_speed_slider_enable:
					row.prop(settings, 'shutter_angle_preset', text='Shutter Angle')
				else:
					row.prop(settings, 'shutter_angle', slider=True)
				row.operator("photographer.setshutterspeed",icon="PREVIEW_RANGE", text="")
				row.prop(settings,'shutter_speed_slider_enable', icon='SETTINGS', text='')


			# Aperture parameter
			row = layout.row(align = True)
			if not settings.aperture_slider_enable:
				row.prop(settings, 'aperture_preset', text='Aperture')
			else:
				row.prop(settings, 'aperture', slider=True, text='Aperture F-stop')
			row.prop(settings,'aperture_slider_enable', icon='SETTINGS', text='')

			# ISO parameter
			row = layout.row(align = True)

			if not settings.iso_slider_enable:
				row.prop(settings, 'iso_preset', text='ISO')
			else:
				row.prop(settings, 'iso', slider=True)
			row.prop(settings,'iso_slider_enable', icon='SETTINGS', text='')
			layout.prop(settings, 'exposure_compensation', text='Exposure Compensation')


		col = layout.column(align=False)
		col.prop(settings, 'motionblur_enabled', text='Affect Motion Blur')

		# Check if the Motion Blur is enabled in the Render Settings
		if settings.motionblur_enabled and not scene.render.use_motion_blur:
			row = layout.row(align = True)
			row.label(icon= 'ERROR', text="Motion Blur is disabled")
			row.operator("photographer.rendermotionblur", text="Enable Motion Blur")

		# Hide Affect Depth of Field in 3D View Panel
		if show_aperture:
			if bpy.context.scene.render.engine == 'LUXCORE':
				col.prop(scene.camera.data.luxcore, "use_dof", text='Affect Depth of Field')
			else:
				col.prop(scene.camera.data.dof, "use_dof", text='Affect Depth of Field')

		col.prop(settings, 'falsecolor_enabled', text='False Color')

		row = layout.row()
		row.alignment = 'RIGHT'

		framerate_guide = "FPS : " + str(round(scene.render.fps/scene.render.fps_base,2))
		if settings.shutter_mode == 'ANGLE':
			shutter_speed_guide = " - " + "Shutter Speed : 1/" + str(int(settings.shutter_speed)) + "s"
			framerate_guide += shutter_speed_guide
		if settings.shutter_mode == 'SPEED':
			shutter_angle_guide = " - " + "Shutter Angle : " + str(round(settings.shutter_angle,1))
			framerate_guide += shutter_angle_guide
		row.label(text = framerate_guide)



class PHOTOGRAPHER_PT_Panel_Exposure(bpy.types.Panel):
	bl_label = 'Exposure'
	bl_parent_id = 'PHOTOGRAPHER_PT_Panel'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return context.camera

	def draw_header_preset(self, context):
		settings = context.camera.photographer
		exposure_header_preset(self,context,settings, True)

	def draw_header(self, context):
		settings = context.camera.photographer
		exposure_header(self,context,settings)

	def draw(self, context):
		settings = context.camera.photographer
		show_aperture = True
		exposure_panel(self,context,settings,show_aperture)

class PHOTOGRAPHER_PT_ViewPanel_Exposure(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Photographer'
	bl_label = 'Exposure'
	
	@classmethod
	def poll(cls, context):
		return context.scene.camera is not None
	
	def draw_header_preset(self, context):
		settings = context.scene.camera.data.photographer
		exposure_header_preset(self,context,settings, False)

	def draw_header(self, context):
		settings = context.scene.camera.data.photographer
		exposure_header(self,context,settings)

	def draw(self, context):
		settings = context.scene.camera.data.photographer
		show_aperture = False
		exposure_panel(self,context,settings,show_aperture)


#### WHITE BALANCE PANELS ####		

def whitebalance_header_preset(self, context,use_scene_camera):
	layout = self.layout
	row = layout.row(align=True)
	row.operator("white_balance.picker",text='', icon='EYEDROPPER', emboss=False).use_scene_camera=use_scene_camera
	row.operator("white_balance.reset", text='', icon='LOOP_BACK', emboss=False).use_scene_camera=use_scene_camera

def whitebalance_header(self, context):
	self.layout.prop(context.scene.view_settings, "use_curve_mapping", text="")

def whitebalance_panel(self, context, settings):
	layout = self.layout
	scene = bpy.context.scene

	layout.use_property_split = True
	layout.use_property_decorate = False  # No animation.
	layout.enabled = context.scene.view_settings.use_curve_mapping

	row = layout.row(align=True)
	row.prop(settings, "color_temperature", slider=True)
	row.prop(settings, "preview_color_temp", text='')

	row = layout.row(align=True)
	row.prop(settings, "tint", slider=True)
	row.prop(settings, "preview_color_tint", text='')


class PHOTOGRAPHER_PT_Panel_WhiteBalance(bpy.types.Panel):
	bl_label = "White Balance"
	bl_parent_id = "PHOTOGRAPHER_PT_Panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return context.camera
		
	def draw_header_preset(self, context):
		whitebalance_header_preset(self,context,False)

	def draw_header(self, context):
		whitebalance_header(self,context)

	def draw(self, context):
		settings = context.camera.photographer
		whitebalance_panel(self,context,settings)

class PHOTOGRAPHER_PT_ViewPanel_WhiteBalance(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Photographer'
	bl_label = 'White Balance'
	
	@classmethod
	def poll(cls, context):
		return context.scene.camera is not None
	
	def draw_header_preset(self, context):
		whitebalance_header_preset(self,context,True)

	def draw_header(self, context):
		whitebalance_header(self,context)

	def draw(self, context):
		settings = context.scene.camera.data.photographer
		whitebalance_panel(self,context,settings)


#### RESOLUTION PANELS ####	

def resolution_header_preset(self, context, settings):
	layout = self.layout
	layout.enabled = settings.resolution_enabled

	row = layout.row(align=True)
	row.alignment = 'RIGHT'
	# Resolution
	resolution_x = str(int(context.scene.render.resolution_x * context.scene.render.resolution_percentage/100))
	resolution_y = str(int(context.scene.render.resolution_y * context.scene.render.resolution_percentage/100))
	row.label(text = resolution_x + " x " + resolution_y)

def resolution_header(self, context, settings):
	self.layout.prop(settings, "resolution_enabled", text="")

def resolution_panel(self, context, settings):
	layout = self.layout
	scene = bpy.context.scene

	layout.use_property_split = True
	layout.use_property_decorate = False  # No animation.
	layout.enabled = settings.resolution_enabled

	col = layout.column()
	col.alignment = 'RIGHT'

	col.prop(settings, 'resolution_mode')

	sub = col.column(align=True)

	if settings.resolution_mode == 'CUSTOM_RES':
		sub.prop(settings, "resolution_x", text='Resolution X')
		sub.prop(settings, "resolution_y", text='Y')
		sub.prop(context.scene.render, "resolution_percentage", text='%')
		col.row().prop(settings, 'resolution_rotation',expand=True)

	elif settings.resolution_mode == 'CUSTOM_RATIO':
		sub.prop(settings, "ratio_x", text='Ratio X')
		sub.prop(settings, "ratio_y", text='Y')
		sub.separator()
		sub.prop(settings, "resolution_x", text='Resolution X')
		sub.prop(context.scene.render, "resolution_percentage", text='%')
		col.row().prop(settings, 'resolution_rotation',expand=True)

	else:
		sub.prop(settings, "longedge")
		sub.prop(context.scene.render, "resolution_percentage", text='%')
		if not settings.resolution_mode == '11':
			col.row().prop(settings, 'resolution_rotation',expand=True)
				


class PHOTOGRAPHER_PT_Panel_Resolution(bpy.types.Panel):
	bl_label = "Resolution"
	bl_parent_id = "PHOTOGRAPHER_PT_Panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"
	
	@classmethod
	def poll(cls, context):
		return context.camera
	
	def draw_header_preset(self, context):
		settings = context.camera.photographer
		resolution_header_preset(self,context,settings)

	def draw_header(self, context):
		settings = context.camera.photographer
		resolution_header(self,context,settings)

	def draw(self, context):
		settings = context.camera.photographer
		resolution_panel(self,context,settings)


				
class PHOTOGRAPHER_PT_ViewPanel_Resolution(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Photographer'
	bl_label = 'Resolution'
	
	@classmethod
	def poll(cls, context):
		return context.scene.camera is not None
	
	def draw_header_preset(self, context):
		settings = context.scene.camera.data.photographer
		resolution_header_preset(self,context,settings)

	def draw_header(self, context):
		settings = context.scene.camera.data.photographer
		resolution_header(self,context,settings)

	def draw(self, context):
		settings = context.scene.camera.data.photographer
		resolution_panel(self,context,settings)

#### MASTER CAMERA PANEL ####

class MASTERCAMERA_PT_ViewPanel(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Photographer'
	bl_label = "Camera List"


	def draw(self, context):
		layout = self.layout

		scene = context.scene

		col = layout.column(align=True)
		# Master Camera
		master_row = col.row(align=True)

		master_cam = 'MasterCamera'

		cam_list=[cam.name for cam in context.scene.collection.all_objects if cam.type=='CAMERA']
		if master_cam in cam_list:
			if context.scene.camera == bpy.data.objects.get(master_cam):
				master_row.operator("mastercamera.look_through", text=master_cam,  icon='OUTLINER_DATA_CAMERA').camera=master_cam
			else:
				master_row.operator("mastercamera.look_through", text=master_cam).camera=master_cam
			master_row.operator("mastercamera.delete_cam", text="", icon="PANEL_CLOSE").camera=master_cam
			row = col.row(align=True)
			row.prop(bpy.data.objects.get(master_cam).data.photographer, "match_speed", slider=True)

		else:
			master_row.operator("mastercamera.add_mastercam", text='Add Master Camera', icon='OUTLINER_DATA_CAMERA')


		col = layout.column(align=True)
		row = col.row(align=True)
		row.label(text= "Camera List:")
		row = col.row(align=True)
		row.operator("mastercamera.add_cam", text='Add Camera')

		col = layout.column(align=True)
		if master_cam in cam_list:
			cam_list.remove('MasterCamera')
		for cam in cam_list:
			row = col.row(align=True)
			if context.scene.camera is not None:
				if context.scene.camera == bpy.data.objects.get(master_cam):
					row.operator("view3d.switch_camera", text="", icon="PLAY").camera=cam
					# row.enabled = not bpy.data.objects.get(master_cam).data.photographer.is_matching
			if context.scene.camera == bpy.data.objects.get(cam):
				row.operator("mastercamera.look_through", text="", icon='RESTRICT_RENDER_OFF').camera=cam
			else:
				row.operator("mastercamera.look_through", text="", icon='RESTRICT_RENDER_ON').camera=cam
			row.operator("mastercamera.select_cam", text=cam).camera=cam
			row.operator("mastercamera.delete_cam", text="", icon="PANEL_CLOSE").camera=cam

		
		view = context.space_data
		render = scene.render
		if view.lock_camera:
			icon="LOCKVIEW_ON"
		else:
			icon="LOCKVIEW_OFF"
		
		row = layout.row()
		split = row.split(factor=0.7, align=False)
		split.prop(view, "lock_camera", text="Lock Camera to View", icon=icon )
		split.prop(render, "use_border", text="Border")
		
		if context.scene.camera:
			photographer = context.scene.camera.data.photographer
			layout.operator("photographer.updatesettings", text="Apply Photographer Settings")

#### AUTOFOCUS PANELS ####

class PHOTOGRAPHER_PT_Panel_Autofocus(bpy.types.Panel):
	# bl_idname = "CAMERA_PT_Photographer_Autofocus"
	bl_label = "Continuous Autofocus"
	bl_parent_id = "PHOTOGRAPHER_PT_Panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"

	def draw_header(self, context):
		settings = context.camera.photographer
		self.layout.prop(settings, "af_continuous_enabled", text="")

	def draw(self, context):
		settings = context.camera.photographer
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.

		col = layout.column(align=True)
		col.prop(settings, "af_continuous_interval", slider=True)

class PHOTOGRAPHER_PT_ViewPanel_Autofocus(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Photographer'
	bl_label = "Autofocus"

	@classmethod
	def poll(cls, context):
		return context.scene.camera is not None

	# def draw_header(self, context):
	# 	if not context.scene.camera.data.photographer.af_tracking_enabled:
	# 		dof_distance = str(round(context.scene.camera.data.dof.focus_distance*context.scene.unit_settings.scale_length,2))
	# 		if not context.scene.unit_settings.system == 'NONE':
	# 			dof_distance = dof_distance + "m"
	# 		self.layout.prop(text=dof_distance)
		
	def draw(self, context):
		settings = context.scene.camera.data.photographer
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.
	
		col = layout.column(align=True)
		
		if context.scene.camera:
			if context.scene.camera.type == 'CAMERA':
				if settings.af_tracking_enabled == False:
					icon_afs = 'RESTRICT_RENDER_OFF'
					if settings.af_animate:
						icon_afs = 'KEYTYPE_KEYFRAME_VEC'
					col.operator("photographer.focus_single", text="AF-S", icon=icon_afs)
					if settings.af_tracking_enabled == False:
						col.operator("photographer.focus_tracking", text="AF-Track", icon='OBJECT_DATA')
					if settings.af_tracking_enabled:
						col.operator("photographer.focus_tracking_cancel", text="Cancel AF Tracking", icon='OBJECT_DATA')
					
					col.separator()
					icon_afc = 'HOLDOUT_ON'
					if settings.af_animate:
						icon_afc = 'KEYTYPE_KEYFRAME_VEC'
					col.prop(settings, "af_continuous_enabled", text="Enable AF-C", icon=icon_afc)
					col_afc_int = col.column(align=True)
					col_afc_int.enabled = settings.af_continuous_enabled
					col_afc_int.prop(settings, "af_continuous_interval", slider=True)
					
					col.separator()
					col.prop(settings, "af_animate", text="Animate AF", icon="KEY_HLT" )