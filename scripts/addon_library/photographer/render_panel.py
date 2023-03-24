import bpy

class PHOTOGRAPHER_OT_UpdateLightThreshold(bpy.types.Operator):
	bl_idname = "photographer.updatelightthreshold"
	bl_label = "Calculate Light Threshold from Exposure"
	bl_description = "Calculate Light Threshold according to Exposure to avoid grain in low exposure scenes"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if context.scene.render.engine == 'CYCLES':
			context.scene.cycles.light_sampling_threshold = bpy.context.preferences.addons[__package__].preferences.default_light_threshold / pow(2,context.scene.view_settings.exposure)
			#trick to update render
			bpy.context.scene.view_settings.exposure = bpy.context.scene.view_settings.exposure
			
		if context.scene.render.engine == 'BLENDER_EEVEE':
			context.scene.eevee.light_threshold = bpy.context.preferences.addons[__package__].preferences.default_light_threshold / pow(2,context.scene.view_settings.exposure)
		return{'FINISHED'}

def light_threshold_button(self, context):
	layout = self.layout
	layout.operator("photographer.updatelightthreshold")




	
