import bpy

from . import (camera, camera_panel)

SHOW_DEFAULT_LIGHT_PANELS_DESCRIPTION = ( "In case a Blender updates adds new Light features and Photographer is not updated,"
			"these features might not be visible in the Physical Light panel.\n"
			"This option allows you to show both panels at the same time"
)

photographer_panel_classes = (
	camera_panel.MASTERCAMERA_PT_ViewPanel,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_Camera,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_Exposure,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_Autofocus,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_WhiteBalance,
	camera_panel.PHOTOGRAPHER_PT_ViewPanel_Resolution,
)

def update_photographer_category(self,context):	
	for cls in photographer_panel_classes:
		# is_panel = hasattr(bpy.types, str(cls))
		# if is_panel:
		try:
			bpy.utils.unregister_class(cls)
		except:
			pass
		cls.bl_category = self.category
		bpy.utils.register_class(cls)


def update_exposure(self,context):
	photographer = context.scene.camera.data.photographer
	if photographer.exposure_enabled:
		camera.update_ev(self,context)
		
class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	category : bpy.props.StringProperty(
		description="Choose a name for the category of the panel. You can write the name of an existing panel",
		default="Photographer",
		update=update_photographer_category
	)
   
	exposure_mode_pref : bpy.props.EnumProperty(
		name = "Default Exposure Mode",
		description = "Choose the default Exposure Mode",
		items = [('EV','EV', ''),('MANUAL','Manual','')],
		default = 'EV',
	)

	shutter_speed_slider_pref : bpy.props.BoolProperty(
		name = "Shutter Speed / Angle",
		description = "Use Slider for Shutter Speed / Angle",
		default = False
	)

	aperture_slider_pref : bpy.props.BoolProperty(
		name = "Aperture",
		description = "Use Slider for Aperture",
		default = False
	)

	iso_slider_pref : bpy.props.BoolProperty(
		name = "ISO",
		description = "Use Slider for ISO setting",
		default = False
	)
	
	show_af_buttons_pref : bpy.props.BoolProperty(
		name = "Show Autofocus buttons in 3D View header",
		description = "AF buttons will be available in the Add-on panels anyway",
		default = True
	)
	
	use_physical_lights : bpy.props.BoolProperty(
		name = "Use Physical lights",
		description = "Replace Light properties with advanced Physical Light properties",
		default = True
	)
	
	show_default_light_panels : bpy.props.BoolProperty(
		name = "Keep showing Blender Light panels",
		description = SHOW_DEFAULT_LIGHT_PANELS_DESCRIPTION,
		default = False
	)
	
	default_light_threshold : bpy.props.FloatProperty(
		name = "Default Light Threshold",
		description = "Defines the Light Sampling Threshold that will be multiplied by the Exposure Value",
		default = 0.01,
		min = 0,
		max = 1,
		precision = 5,
	)
	
	aces_ue_match : bpy.props.BoolProperty(
		name = "Match Blender ACES to Unreal ACES",
		description = "Blender ACES is darker than Unreal ACES tonemapper for some unknown reason. Check this box to fix this discrepancy. \n"
					"This setting is only effective when using ACES in Blender",
		default = True,
		update = update_exposure,
	)
	
	lens_attenuation : bpy.props.FloatProperty(
		name = "Lens Attenuation factor",
		description = "Default value of 0.78 will cancel lens attenuation calculations and will match Unreal 4.25 camera exposure. \n"
					"ISO standard recommends a lens transmittance of 0.65, which is sometimes used by other render engines to match real cameras"	,
		default = 0.78,
		min = 0.01,
		max = 1,
		precision = 3,
		update = update_exposure,
	)	



	def draw(self, context):
			layout = self.layout
			wm = bpy.context.window_manager

			# box = layout.box()
			percentage_columns = 0.4
			
			# Camera options
			col = layout.column(align=True)
			col.label(text='CAMERA UI')
			box = col.box()
			row = box.row(align=True)
			row.label(text="Panel Category:")
			row.prop(self, "category", text="")
			
			# Default Exposure mode
			split = box.split(factor = percentage_columns)
			split.label(text = "Default Exposure Mode :")
			row = split.row(align=True)
			row.prop(self, 'exposure_mode_pref', expand=True)
			# Use camera values presets or sliders
			row = box.row(align=True)
			split = row.split(factor = percentage_columns)
			split.label(text = "Use Sliders instead of real Camera values for :")
			col2 = split.column()
			row = col2.row()
			row.prop(self, 'shutter_speed_slider_pref')
			row.prop(self, 'aperture_slider_pref')
			row.prop(self, 'iso_slider_pref')
			
			box.prop(self, 'show_af_buttons_pref')
		
			col.label(text="Changing these default values will take effect after saving the User Preferences and restarting Blender.", icon='INFO')

			layout.separator()
			
			# Exposure Calculation
			col = layout.column(align=True)
			col.label(text='EXPOSURE SETTINGS')
			box = col.box()
			
			box.prop(self,'lens_attenuation')
			box.prop(self, 'aces_ue_match')
		
			layout.separator()
						
			# Physical lights options
			col = layout.column(align=True)
			col.label(text='LIGHT UI')
			box = col.box()
			box.prop(self, 'use_physical_lights', text='Use Physical Lights (supported by Cycles, EEVEE and Workbench)')
			col = box.column(align=True)
			if self.use_physical_lights:
				col.enabled = True
			else:
				col.enabled = False
			col.prop(self, 'show_default_light_panels')

			layout.separator()
			
			# Render options
			col = layout.column(align=True)
			col.label(text='RENDER OPTIONS')
			box = col.box()
			row = box.row(align=True)
			split = row.split(factor = percentage_columns)
			split.label(text = "Light Sampling Threshold :")
			split.prop(self, 'default_light_threshold', text = '')
			
			layout.separator()
			
			# Useful links
			box = layout.box()
			row = box.row(align=True)
			row.label(text='Useful links : ')
			row.operator("wm.url_open", text="Documentation").url = "https://blenderartists.org/t/addon-photographer-camera-exposure-white-balance-and-autofocus/1101721"
			row.operator("wm.url_open", text="Video Tutorials").url = "https://www.youtube.com/playlist?list=PLDS3IanhbCIXERthzS7cWG1lnGQwQq5vB"
			row.operator("wm.url_open", text="Blender Artists Forum").url = "https://blenderartists.org/t/addon-photographer-camera-exposure-white-balance-and-autofocus/1101721"

