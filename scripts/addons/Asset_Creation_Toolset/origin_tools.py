import bpy

from . import utils


#-------------------------------------------------
#Align Origin To Min
class Align_Min(bpy.types.Operator):
	"""Origin To Min """
	bl_idname = "object.align_min"
	bl_label = "Origin To Min"
	bl_options = {'REGISTER', 'UNDO'}
	align_type: bpy.props.StringProperty()
	
	def execute(self, context):
		act = bpy.context.scene.act

		# Save selected objects and current position of 3D Cursor
		current_selected_obj = bpy.context.selected_objects
		current_active_obj = bpy.context.active_object
		saved_cursor_loc = bpy.context.scene.cursor.location.copy()
		bpy.ops.object.mode_set(mode = 'OBJECT')
		# Change individual origin point
		for x in current_selected_obj:
			# Select only current object (for setting origin)
			bpy.ops.object.select_all(action='DESELECT')
			x.select_set(True);
			bpy.context.view_layer.objects.active = x
			# Save current origin and relocate 3D Cursor
			saved_origin_loc = x.location.copy() 
			if x.type == 'MESH':
				bpy.ops.object.mode_set(mode = 'EDIT')
				
				if self.align_type == 'X':
					min_co = utils.Find_Min_Max_Verts(x, 0, 0)
					if min_co == None:
						min_co = saved_origin_loc[0]
				if self.align_type == 'Y':
					min_co = utils.Find_Min_Max_Verts(x, 1, 0)
					if min_co == None:
						min_co = saved_origin_loc[1]
				if self.align_type == 'Z':
					min_co = utils.Find_Min_Max_Verts(x, 2, 0)
					if min_co == None:
						min_co = saved_origin_loc[2]
				
				if act.align_geom_to_orig == False:
					bpy.ops.object.mode_set(mode = 'OBJECT')
					if self.align_type == 'X':
						bpy.context.scene.cursor.location = [min_co, saved_origin_loc[1], saved_origin_loc[2]] 
					if self.align_type == 'Y':
						bpy.context.scene.cursor.location = [saved_origin_loc[0], min_co, saved_origin_loc[2]] 
					if self.align_type == 'Z':
						bpy.context.scene.cursor.location = [saved_origin_loc[0], saved_origin_loc[1], min_co]
						
					# Apply origin to Cursor position
					bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
					# Reset 3D Cursor position  
					bpy.context.scene.cursor.location = saved_cursor_loc
				
				if act.align_geom_to_orig == True:
					if self.align_type == 'X':
						difference = saved_origin_loc[0] - min_co
					if self.align_type == 'Y':
						difference = saved_origin_loc[1] - min_co
					if self.align_type == 'Z':
						difference = saved_origin_loc[2] - min_co
					
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')
					if self.align_type == 'X':
						bpy.ops.transform.translate(value=(difference, 0, 0), constraint_axis=(True, False, False), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.align_type == 'Y':
						bpy.ops.transform.translate(value=(0, difference, 0), constraint_axis=(False, True, False), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.align_type == 'Z':
						bpy.ops.transform.translate(value=(0, 0, difference), constraint_axis=(False, False, True), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
						
					bpy.ops.object.mode_set(mode = 'OBJECT')

		# Select again objects
		for j in current_selected_obj:
			j.select_set(True);
			
		bpy.context.view_layer.objects.active = current_active_obj

		return {'FINISHED'}
	

#-------------------------------------------------
#Align Origin To Max
class Align_Max(bpy.types.Operator):
	"""Origin To Max """
	bl_idname = "object.align_max"
	bl_label = "Origin To Max"
	bl_options = {'REGISTER', 'UNDO'}
	align_type: bpy.props.StringProperty()
	
	def execute(self, context):
		act = bpy.context.scene.act

		# Save selected objects and current position of 3D Cursor
		current_selected_obj = bpy.context.selected_objects
		current_active_obj = bpy.context.active_object
		saved_cursor_loc = bpy.context.scene.cursor.location.copy()
		bpy.ops.object.mode_set(mode = 'OBJECT')
		# Change individual origin point
		for x in current_selected_obj:
			# Select only current object (for setting origin)
			bpy.ops.object.select_all(action='DESELECT')
			x.select_set(True);
			bpy.context.view_layer.objects.active = x
			# Save current origin and relocate 3D Cursor
			saved_origin_loc = x.location.copy() 
			if x.type == 'MESH':
				bpy.ops.object.mode_set(mode = 'EDIT')
				
				if self.align_type == 'X':
					max_co = utils.Find_Min_Max_Verts(x, 0, 1)
					if max_co == None:
						max_co = saved_origin_loc[0]
				if self.align_type == 'Y':
					max_co = utils.Find_Min_Max_Verts(x, 1, 1)
					if max_co == None:
						max_co = saved_origin_loc[1]
				if self.align_type == 'Z':
					max_co = utils.Find_Min_Max_Verts(x, 2, 1)
					if max_co == None:
						max_co = saved_origin_loc[2]
				
				if act.align_geom_to_orig == False:
					bpy.ops.object.mode_set(mode = 'OBJECT')
					if self.align_type == 'X':
						bpy.context.scene.cursor.location = [max_co, saved_origin_loc[1], saved_origin_loc[2]] 
					if self.align_type == 'Y':
						bpy.context.scene.cursor.location = [saved_origin_loc[0], max_co, saved_origin_loc[2]] 
					if self.align_type == 'Z':
						bpy.context.scene.cursor.location = [saved_origin_loc[0], saved_origin_loc[1], max_co]
						
					# Apply origin to Cursor position
					bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
					# Reset 3D Cursor position  
					bpy.context.scene.cursor.location = saved_cursor_loc
				
				if act.align_geom_to_orig == True:
					if self.align_type == 'X':
						difference = saved_origin_loc[0] - max_co
					if self.align_type == 'Y':
						difference = saved_origin_loc[1] - max_co
					if self.align_type == 'Z':
						difference = saved_origin_loc[2] - max_co
					
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')
					if self.align_type == 'X':
						bpy.ops.transform.translate(value=(difference, 0, 0), constraint_axis=(True, False, False), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.align_type == 'Y':
						bpy.ops.transform.translate(value=(0, difference, 0), constraint_axis=(False, True, False), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.align_type == 'Z':
						bpy.ops.transform.translate(value=(0, 0, difference), constraint_axis=(False, False, True), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
						
					bpy.ops.object.mode_set(mode = 'OBJECT')

		# Select again objects
		for j in current_selected_obj:
			j.select_set(True);
			
		bpy.context.view_layer.objects.active = current_active_obj

		return {'FINISHED'}

	
#-----------------------------------------------------
#Align Cursor
class Align_Cur(bpy.types.Operator):
	"""Origin Align To Cursor"""
	bl_idname = "object.align_cur"
	bl_label = "Origin To Cursor"
	bl_options = {'REGISTER', 'UNDO'}
	align_type: bpy.props.StringProperty()
	
	def execute(self, context):
		act = bpy.context.scene.act

		# Save selected objects and current position of 3D Cursor
		current_selected_obj = bpy.context.selected_objects
		current_active_obj = bpy.context.active_object
		saved_cursor_loc = bpy.context.scene.cursor.location.copy()
		bpy.ops.object.mode_set(mode = 'OBJECT')
		# Change individual origin point
		for x in current_selected_obj:
			# Select only current object (for setting origin)
			bpy.ops.object.select_all(action='DESELECT')
			x.select_set(True);
			# Save current origin and relocate 3D Cursor
			saved_origin_loc = x.location.copy()
			#Align to 3D Cursor
			if self.align_type == 'X':
				bpy.context.scene.cursor.location = [saved_cursor_loc[0], saved_origin_loc[1], saved_origin_loc[2]] 
			if self.align_type == 'Y':
				bpy.context.scene.cursor.location = [saved_origin_loc[0], saved_cursor_loc[1], saved_origin_loc[2]] 
			if self.align_type == 'Z':
				bpy.context.scene.cursor.location = [saved_origin_loc[0], saved_origin_loc[1], saved_cursor_loc[2]] 
			# Apply origin to Cursor position
			if act.align_geom_to_orig == False:
				bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
			else:
				if self.align_type == 'X':
					difference = saved_cursor_loc[0] - saved_origin_loc[0]
					bpy.ops.transform.translate(value=(difference, 0, 0), constraint_axis=(True, False, False), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.align_type == 'Y':
					difference = saved_cursor_loc[1] - saved_origin_loc[1]
					bpy.ops.transform.translate(value=(0, difference, 0), constraint_axis=(False, True, False), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.align_type == 'Z':
					difference = saved_cursor_loc[2] - saved_origin_loc[2]
					bpy.ops.transform.translate(value=(0, 0, difference), constraint_axis=(False, False, True), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
			# Reset 3D Cursor position  
			bpy.context.scene.cursor.location = saved_cursor_loc
		
		# Select again objects
		for j in current_selected_obj:
			j.select_set(True);
		
		return {'FINISHED'}


#------------------------------------------------------
#Align Coordinate
class Align_Co(bpy.types.Operator):
	"""Origin Align To Spec Coordinate"""
	bl_idname = "object.align_co"
	bl_label = "Origin Align To Spec Coordinate"
	bl_options = {'REGISTER', 'UNDO'}
	align_type: bpy.props.StringProperty()

	def execute(self, context):
		act = bpy.context.scene.act

		wrong_align_co = False
		#Check coordinate if check this option
		try:
			align_coordinate = float(act.align_co)
		except:
			self.report({'INFO'}, 'Coordinate is wrong')
			wrong_align_co = True   
		
		if wrong_align_co == False:
			# Save selected objects and current position of 3D Cursor
			current_selected_obj = bpy.context.selected_objects
			saved_cursor_loc = bpy.context.scene.cursor.location.copy()
			bpy.ops.object.mode_set(mode = 'OBJECT')
			# Change individual origin point
			for x in current_selected_obj:
				# Select only current object (for setting origin)
				bpy.ops.object.select_all(action='DESELECT')
				x.select_set(True);
				# Save current origin and relocate 3D Cursor
				saved_origin_loc = x.location.copy()
				
				#Align to Coordinate
				if self.align_type == 'X':
					bpy.context.scene.cursor.location = [align_coordinate, saved_origin_loc[1], saved_origin_loc[2]] 
				if self.align_type == 'Y':
					bpy.context.scene.cursor.location = [saved_origin_loc[0], align_coordinate, saved_origin_loc[2]] 
				if self.align_type == 'Z':
					bpy.context.scene.cursor.location = [saved_origin_loc[0], saved_origin_loc[1], align_coordinate] 
				
				if act.align_geom_to_orig == False:
					bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
				else:
					if self.align_type == 'X':
						difference = align_coordinate - saved_origin_loc[0]
						bpy.ops.transform.translate(value=(difference, 0, 0), constraint_axis=(True, False, False), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.align_type == 'Y':
						difference = align_coordinate - saved_origin_loc[1]
						bpy.ops.transform.translate(value=(0, difference, 0), constraint_axis=(False, True, False), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.align_type == 'Z':
						difference = align_coordinate - saved_origin_loc[2]
						bpy.ops.transform.translate(value=(0, 0, difference), constraint_axis=(False, False, True), orient_type='GLOBAL', orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
				# Reset 3D Cursor position  
				bpy.context.scene.cursor.location = saved_cursor_loc
			
			# Select again objects
			for j in current_selected_obj:
				j.select_set(True);
			
		return {'FINISHED'}


#-------------------------------------------------------
#Set Origin To Selection
class Set_Origin_To_Select(bpy.types.Operator):
	"""Set Origin To Selection"""
	bl_idname = "object.set_origin_to_select"
	bl_label = "Set Origin To Selection"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		selected_obj = bpy.context.selected_objects
		saved_cursor_loc = bpy.context.scene.cursor.location.copy()
		bpy.ops.view3d.snap_cursor_to_selected()
		bpy.ops.object.mode_set(mode = 'OBJECT')
		# Apply origin to Cursor position
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		# Reset 3D Cursor position  
		bpy.context.scene.cursor.location = saved_cursor_loc
		bpy.ops.object.mode_set(mode = 'EDIT')
		
		return {'FINISHED'} 	


#-------------------------------------------------------
#Origin Tools UI Panel
class VIEW3D_PT_Origin_Tools_Panel(bpy.types.Panel):
	bl_label = "Origin Tools"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "ACT"

	@classmethod
	def poll(self, context):
		preferences = bpy.context.preferences.addons[__package__].preferences
		return (context.object is not None and (context.mode == 'OBJECT' or context.mode == 'EDIT_MESH')) and preferences.origin_enable

	def draw(self, context):
		act = bpy.context.scene.act
		
		layout = self.layout
		if context.object is not None:
			if context.mode == 'OBJECT':
				row = layout.row()
				row.label(text="Origin Align")
				
				row = layout.row()
				row.prop(act, "align_geom_to_orig", text="Geometry To Origin")
				
				#--Aligner Labels----
				row = layout.row(align=True)
				row.label(text="X")
				row.label(text="Y")
				row.label(text="Z")
				
				#--Aligner Min Buttons----
				row = layout.row(align=True)
				row.operator("object.align_min", text="Min").align_type='X'
				row.operator("object.align_min", text="Min").align_type='Y'
				row.operator("object.align_min", text="Min").align_type='Z'
				
				#--Aligner Max Buttons----
				row = layout.row(align=True)
				row.operator("object.align_max", text="Max").align_type='X'
				row.operator("object.align_max", text="Max").align_type='Y'
				row.operator("object.align_max", text="Max").align_type='Z'
				
				#--Aligner Cursor Buttons----
				row = layout.row(align=True)
				row.operator("object.align_cur", text="Cursor").align_type='X'
				row.operator("object.align_cur", text="Cursor").align_type='Y'
				row.operator("object.align_cur", text="Cursor").align_type='Z'
				
				#--Aligner Coordinates Buttons----
				row = layout.row(align=True)
				row.operator("object.align_co", text="Coordinate").align_type='X'
				row.operator("object.align_co", text="Coordinate").align_type='Y'
				row.operator("object.align_co", text="Coordinate").align_type='Z'

				row = layout.row()
				row.prop(act, "align_co", text="Coordinate")
				
		if context.object is not None:
			if context.object.mode == 'EDIT':
				row = layout.row()
				row.operator("object.set_origin_to_select", text="Set Origin To Selected")

		else:
			row = layout.row()
			row.label(text=" ")


classes = (
	Align_Min,
	Align_Max,
	Align_Cur,
	Align_Co,
	Set_Origin_To_Select,
)	


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)