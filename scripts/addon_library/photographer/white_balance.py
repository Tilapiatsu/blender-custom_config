import bpy

import bgl
import math

from .functions import srgb_to_linear
from . import camera
from bpy.props import BoolProperty

# Default Global variables
default_color_temperature = 6500
default_tint = 0
stored_cm_view_transform = 'Filmic'
temperature_ratio = ((23.1818,2000),(6.2195,2200),(4.25,2400),(3.0357,2700),(2.4286,3000),(2.0565,3300),(1.8085,3600),(1.6038,3900),(1.5839,4300),(1.25,5000),(1.0759,6000),(1,6500),(0.8980,8000),(0.851,9000),(0.8118,10000),(0.7843,11000),(0.7647,12000),(0.4706,13000),(0.1176,14000))

#White Balance functions ##############################################################

def convert_RGB_to_temperature_table(red, blue):

	table_ratio = camera.InterpolatedArray(temperature_ratio)

	# Min and Max ratios from the table
	maxratio = 23.1818
	minratio = 0.1176

	# Make sure to not divide by 0
	if blue == 0:
		ratio = minratio
	else: ratio = red / blue

	#Clamping ratio to avoid looking outside of the table
	ratio = maxratio if ratio > maxratio else minratio if ratio < minratio else ratio

	color_temperature = table_ratio[ratio]

	return (color_temperature)

def convert_RBG_to_whitebalance(picked_color,use_scene_camera):
	if use_scene_camera:
		settings = bpy.context.scene.camera.data.photographer
	else:
		settings = bpy.context.camera.photographer
	#Need to convert picked color to linear
	red = srgb_to_linear(picked_color[0])
	green = srgb_to_linear(picked_color[1])
	blue = srgb_to_linear(picked_color[2])

	average = (red + blue) / 2

	# Calculating Curves values
	red_mult = red / average
	green_mult = green / average
	blue_mult = blue / average

	# # Accurate multiplier to test accuracy of color temperature conversion
	# bpy.context.scene.view_settings.curve_mapping.white_level[0] = red_mult
	# bpy.context.scene.view_settings.curve_mapping.white_level[1] = green_mult
	# bpy.context.scene.view_settings.curve_mapping.white_level[2] = blue_mult

	# Convert Curve value to Tint
	if green_mult < 1 :
		settings.tint = (green_mult - 1) * 200 # Reverse Tint Math
	else:
		settings.tint = (green_mult - 1) * 50 # Reverse Tint Math

	# Convert Curve value to Temperature
	settings.color_temperature = convert_RGB_to_temperature_table(red_mult,blue_mult)

def set_picked_white_balance(picked_color,use_scene_camera):
	convert_RBG_to_whitebalance(picked_color,use_scene_camera)

class PHOTOGRAPHER_OT_WBReset(bpy.types.Operator):
	bl_idname = "white_balance.reset"
	bl_label = "Reset White Balance"
	bl_description = "Reset White Balance"
	bl_options = {'UNDO'}

	use_scene_camera: BoolProperty(default=False)
	
	def execute(self, context):
		if self.use_scene_camera:
			context.scene.camera.data.photographer.color_temperature = default_color_temperature
			context.scene.camera.data.photographer.tint = default_tint			
		else:
			context.camera.photographer.color_temperature = default_color_temperature
			context.camera.photographer.tint = default_tint
		return{'FINISHED'}

class PHOTOGRAPHER_OT_WBPicker(bpy.types.Operator):
	bl_idname = "white_balance.picker"
	bl_label = "Pick White Balance"
	bl_description = "Pick a grey area in the 3D view to adjust the White Balance"
	bl_options = {'REGISTER', 'UNDO'}

	# Create stored values for cancelling
	stored_color_temperature = 6500
	stored_tint = 0
	stored_cm_display_device = "sRGB"
	stored_cm_view_transform = "Filmic"

	stored_cm_look = "None"
	
	use_scene_camera: BoolProperty(default=False)

	def modal(self, context, event):
		#context.area.tag_redraw()

		# Reset White Balance to pick raw image, not an already white balanced one
		if self.use_scene_camera:
			if context.scene.camera.data.photographer.color_temperature != default_color_temperature:
				context.scene.camera.data.photographer.color_temperature = default_color_temperature
			if context.scene.camera.data.photographer.tint != default_tint:	
				context.scene.camera.data.photographer.tint = default_tint		
		else:
			if context.camera.photographer.color_temperature != default_color_temperature:
				context.camera.photographer.color_temperature = default_color_temperature
			if context.camera.photographer.tint != default_tint:
				context.camera.photographer.tint = default_tint
	
		# Disabling color management to be able to convert picked color easily
		if	context.scene.display_settings.display_device != "sRGB":
			context.scene.display_settings.display_device = "sRGB"
		if context.scene.view_settings.view_transform != "Standard":
			context.scene.view_settings.view_transform = "Standard"

		# Allow navigation for Blender and Maya shortcuts
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
			return {'PASS_THROUGH'}

		if event.type == 'LEFTMOUSE':

			# Picking color when releasing left mouse button
			if event.value == 'RELEASE' and not self.record:

				self.record = True
				self.mouse_position=(event.mouse_x, event.mouse_y)
				# Restore Mouse Cursor from Eyedropper Icon
				if self.cursor_set: context.window.cursor_modal_restore()

				buf = bgl.Buffer(bgl.GL_FLOAT, [1, 3])
				x,y = self.mouse_position

				red = 0
				green = 0
				blue = 0

				#Sample a 9*9 pixels square
				for i in range(x-4, x+4):
					for j in range(y-4, y+4):
						bgl.glReadPixels(i, j, 1,1 , bgl.GL_RGB, bgl.GL_FLOAT, buf)
						red = red + buf[0][0]
						green = green + buf[0][1]
						blue = blue + buf[0][2]

				average_r = red / 81
				average_g = green / 81
				average_b = blue / 81

				average = [average_r,average_g,average_b]

				# Sampling pixels under the mouse when released
				# bgl.glReadPixels(x, y, 1,1 , bgl.GL_RGB, bgl.GL_FLOAT, buf)
				# rgb = buf[0]
				# Calculate and apply Color Temperature and Tint
				set_picked_white_balance(average,self.use_scene_camera)

				# Restore Color Management Settings
				context.scene.display_settings.display_device = self.stored_cm_display_device
				context.scene.view_settings.view_transform = self.stored_cm_view_transform

				context.scene.view_settings.look = self.stored_cm_look

				return {'FINISHED'}

		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			# Restore previous settings if cancelled
			if self.use_scene_camera:
				context.scene.camera.data.photographer.color_temperature = self.stored_color_temperature
				context.scene.camera.data.photographer.tint = self.stored_tint
			else:
				context.camera.photographer.color_temperature = self.stored_color_temperature
				context.camera.photographer.tint = self.stored_tint
				
			# Restore Color Management Settings
			context.scene.display_settings.display_device = self.stored_cm_display_device
			context.scene.view_settings.view_transform = self.stored_cm_view_transform
			context.scene.view_settings.look = self.stored_cm_look

			# Restore Mouse Cursor from Eyedropper Icon
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):
			args = (self, context)
			context.window_manager.modal_handler_add(self)

			# Set Cursor to Eyedropper icon
			context.window.cursor_modal_set('EYEDROPPER')
			self.cursor_set = True
			self.record = False

			# Store current white balance settings in case of cancelling
			if self.use_scene_camera:
				self.stored_color_temperature = context.scene.camera.data.photographer.color_temperature
				self.stored_tint = context.scene.camera.data.photographer.tint
			else:
				self.stored_color_temperature = context.camera.photographer.color_temperature
				self.stored_tint = context.camera.photographer.tint

			self.stored_cm_display_device = context.scene.display_settings.display_device
			self.stored_cm_view_transform = context.scene.view_settings.view_transform

			if context.scene.view_settings.look == "":
				self.stored_cm_look = "None"
			else:
				self.stored_cm_look = context.scene.view_settings.look


			# context.area.tag_redraw()
			return {'RUNNING_MODAL'}