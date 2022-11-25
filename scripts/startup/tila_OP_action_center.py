import bpy

class TILA_action_center_cursor_toggle(bpy.types.Operator):
	bl_idname = "view3d.tila_action_center_cursor_toggle"
	bl_label = "Toggle Action Center Cursor"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if context.window_manager.ac_use_cursor:
			bpy.ops.view3d.tila_action_center('EXEC_DEFAULT', action_center='GLOBAL')
		else:
			bpy.ops.view3d.tila_action_center('EXEC_DEFAULT', action_center='CURSOR')
		
		context.window_manager.ac_use_cursor = not context.window_manager.ac_use_cursor

		return {'FINISHED'}
					
class TILA_action_center(bpy.types.Operator):
	bl_idname = "view3d.tila_action_center"
	bl_label = "Set action center"
	bl_options = {'REGISTER', 'UNDO'}

	action_center : bpy.props.StringProperty(name="Action Center", default='AUTO')
	context : bpy.props.StringProperty(name="context", default='VIEW3D')

	compatible_action_center = ['AUTO',
								'SELECTION',
								'SELECTION_BORDER',
								'SELECTION_CENTER_AUTO_AXIS',
								'ELEMENT',
								'VIEW',
								'ORIGIN',
								'PARENT',
								'GLOBAL',
								'GLOBAL_INDIVIDUAL',
								'LOCAL',
								'PIVOT',
								'PIVOT_CENTER_PARENT_AXIS',
								'PIVOT_WORLD_AXIS',
								'CURSOR',
								'CURSOR_ORIENT',
								'CUSTOM']

	def set_snapping_settings(self, context):
		context.scene.tool_settings.snap_elements = {'VERTEX', 'EDGE', 'FACE'}
		context.scene.tool_settings.use_snap_self = True
		context.scene.tool_settings.use_snap_align_rotation = True
		context.scene.tool_settings.use_snap_project = True
		context.scene.tool_settings.use_snap_rotate = True

	def get_face_selection(self, context):
		pass
	
	def set_transform_orientation(self, context, value):
		for i in range(1,4):
			context.scene.transform_orientation_slots[i].type = value

	
	def run_tool(self, context, event=None, update=False):
		try:
			event_type = None if event is None else event.type
			
			if self.action_center == 'AUTO':
				self.report({'INFO'}, 'Automatic Action Center')
				if event_type is None:
					self.set_transform_orientation(context, 'GLOBAL')
					context.scene.tool_settings.transform_pivot_point = 'CURSOR'
					bpy.ops.view3d.snap_cursor_to_selected()
				if event_type == 'RIGHTMOUSE' and event.value == 'PRESS':
					self.set_transform_orientation(context, 'GLOBAL')
					context.scene.tool_settings.transform_pivot_point = 'CURSOR'
					bpy.ops.view3d.snap_cursor_to_selected()
					bpy.ops.view3d.cursor3d('INVOKE_DEFAULT', use_depth=False, orientation='NONE')
				if event_type == 'MOUSEMOVE' and  event.value == 'PRESS':
					self.set_transform_orientation(context, 'GLOBAL')
					context.scene.tool_settings.transform_pivot_point = 'CURSOR'
					bpy.ops.view3d.snap_cursor_to_selected()
					self.set_snapping_settings(context)
					bpy.ops.transform.translate('INVOKE_DEFAULT', snap=True, snap_align=True, cursor_transform=True, release_confirm=True, orient_type='NORMAL')
				

				
			if self.action_center == 'SELECTION':
				self.report({'INFO'}, 'Selection Action Center')
				self.set_transform_orientation(context, 'NORMAL')
				context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
			if self.action_center == 'SELECTION_BORDER':
				self.report({'INFO'}, 'Selection Border Action Center')
				context.scene.tool_settings.transform_pivot_point = 'CURSOR'
				selection = self.get_face_selection(context)
				bpy.ops.mesh.region_to_loop()

			if self.action_center == 'SELECTION_CENTER_AUTO_AXIS':
				self.report({'INFO'}, 'Selection Center Auto Axis Action Center')
				self.set_transform_orientation(context, 'GLOBAL')
				context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
			if self.action_center == 'ELEMENT':
				self.report({'INFO'}, 'Element Action Center')
				context.scene.tool_settings.use_snap = True
				context.scene.tool_settings.snap_elements = {'VERTEX', 'EDGE'}
				if event_type == 'RIGHTMOUSE' and event.value == 'PRESS':
					bpy.ops.view3d.cursor3d('INVOKE_DEFAULT', use_depth=True, orientation='GEOM')
				if event_type == 'MOUSEMOVE' and  event.value == 'PRESS':
					self.set_snapping_settings(context)
					bpy.ops.transform.translate('INVOKE_DEFAULT', snap=True, snap_align=True, cursor_transform=True, release_confirm=True, orient_type='NORMAL')
					self.set_transform_orientation(context, 'CURSOR')
				context.scene.tool_settings.transform_pivot_point = 'CURSOR'
			if self.action_center == 'VIEW':
				self.report({'INFO'}, 'View Action Center')
				self.set_transform_orientation(context, 'VIEW')
				context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
			if self.action_center == 'ORIGIN':
				self.report({'INFO'}, 'Origin Action Center')
				self.set_transform_orientation(context, 'CURSOR')
				context.scene.tool_settings.transform_pivot_point = 'CURSOR'
				context.scene.cursor.location[0] = 0
				context.scene.cursor.location[1] = 0
				context.scene.cursor.location[2] = 0
				context.scene.cursor.rotation_euler[0] = 0
				context.scene.cursor.rotation_euler[1] = 0
				context.scene.cursor.rotation_euler[2] = 0
			if self.action_center == 'PARENT':
				self.report({'INFO'}, 'Parent Action Center')
				self.set_transform_orientation(context, 'CURSOR')
				context.scene.tool_settings.transform_pivot_point = 'CURSOR'
				parent = context.object if context.object.parent is None else context.object.parent
				context.scene.cursor.location[0] = parent.location[0]
				context.scene.cursor.location[1] = parent.location[1]
				context.scene.cursor.location[2] = parent.location[2]
				context.scene.cursor.rotation_euler[0] = parent.rotation_euler[0]
				context.scene.cursor.rotation_euler[1] = parent.rotation_euler[1]
				context.scene.cursor.rotation_euler[2] = parent.rotation_euler[2]
			if self.action_center == 'GLOBAL':
				self.report({'INFO'}, 'Global Action Center')
				self.set_transform_orientation(context, 'GLOBAL')
				context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
			if self.action_center == 'GLOBAL_INDIVIDUAL':
				self.report({'INFO'}, 'Global Individual Action Center')
				self.set_transform_orientation(context, 'GLOBAL')
				context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
			if self.action_center == 'LOCAL':
				self.report({'INFO'}, 'Local Action Center')
				self.set_transform_orientation(context, 'NORMAL')
				context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
			if self.action_center == 'PIVOT':
				self.report({'INFO'}, 'Pivot Action Center')
				self.set_transform_orientation(context, 'LOCAL')
				context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
			if self.action_center == 'PIVOT_CENTER_PARENT_AXIS':
				self.report({'INFO'}, 'Pivot Center Parent Axis Action Center')
				self.set_transform_orientation(context, 'CURSOR')
				context.scene.tool_settings.transform_pivot_point = 'CURSOR'
				parent = context.object if context.object.parent is None else context.object.parent
				context.scene.cursor.location[0] = context.object.location[0]
				context.scene.cursor.location[1] = context.object.location[1]
				context.scene.cursor.location[2] = context.object.location[2]
				context.scene.cursor.rotation_euler[0] = parent.rotation_euler[0]
				context.scene.cursor.rotation_euler[1] = parent.rotation_euler[1]
				context.scene.cursor.rotation_euler[2] = parent.rotation_euler[2]
			if self.action_center == 'PIVOT_WORLD_AXIS':
				self.report({'INFO'}, 'Pivot Wold Axis Action Center')
				self.set_transform_orientation(context, 'GLOBAL')
				context.scene.tool_settings.transform_pivot_point = 'CURSOR'
				context.scene.cursor.location[0] = context.object.location[0]
				context.scene.cursor.location[1] = context.object.location[1]
				context.scene.cursor.location[2] = context.object.location[2]
			if self.action_center == 'CURSOR':
				self.report({'INFO'}, 'Cursor Action Center')
				self.set_transform_orientation(context, 'CURSOR')
				context.scene.tool_settings.transform_pivot_point = 'CURSOR'
			if self.action_center == 'CURSOR_ORIENT':
				self.report({'INFO'}, 'Cursor Orient Action Center')
				self.set_transform_orientation(context, 'CURSOR')
				context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
			if self.action_center == 'CUSTOM':
				self.report({'INFO'}, 'Custom Action Center')
		except RuntimeError as e:
			print('Runtime Error :\n{}'.format(e))

	def modal(self, context, event):
		if event.type == 'SPACE' and event.value == 'PRESS':
			self.revert_state(context)
			return {'FINISHED'}
		if event.type in {'ESC'}:  # Cancel
			self.revert_state(context)
			return {'CANCELLED'}
		if event.type == 'RIGHTMOUSE' and event.value == 'PRESS' or event.type == 'MOUSEMOVE' and event.value == 'PRESS':
			self.run_tool(context, event)
		if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
			self.run_tool(context, event, update=True)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		if self.action_center in self.compatible_action_center:
			self.report({'INFO'}, 'Action Center {} is compatible'.format(self.action_center))
			self.run_tool(context)
			# context.window_manager.modal_handler_add(self)
		else:
			return{'FINISHED'}
		return {'RUNNING_MODAL'}

	def revert_state(self, context):
		context.scene.tool_settings.use_snap = False
		context.scene.tool_settings.snap_elements = set({})

class TILA_MT_action_center(bpy.types.Menu):
	bl_idname = "TILA_MT_action_center"
	bl_label = "Action Center"

	def draw(self, context):
		layout = self.layout
		view = context.space_data
		obj = context.active_object

		# if context.mode == "EDIT_MESH":
		layout.operator("view3d.tila_action_center", icon='DOT', text='Automatic').action_center = 'AUTO'
		layout.operator("view3d.tila_action_center", icon='SELECT_SET', text='Selection').action_center = 'SELECTION'
		layout.operator("view3d.tila_action_center", icon='SELECT_SET', text='Selection Border').action_center = 'SELECTION_BORDER'
		layout.operator("view3d.tila_action_center", icon='SELECT_SET', text='Selection Center Auto Axis').action_center = 'SELECTION_CENTER_AUTO_AXIS'
		layout.operator("view3d.tila_action_center", icon='VERTEXSEL', text='Element').action_center = 'ELEMENT'
		layout.operator("view3d.tila_action_center", icon='LOCKVIEW_ON', text='View').action_center = 'VIEW'
		layout.operator("view3d.tila_action_center", icon='OBJECT_ORIGIN', text='Global').action_center = 'GLOBAL'
		layout.operator("view3d.tila_action_center", icon='OBJECT_ORIGIN', text='Global Individual').action_center = 'GLOBAL_INDIVIDUAL'
		layout.operator("view3d.tila_action_center", icon='OUTLINER_DATA_EMPTY', text='Origin').action_center = 'ORIGIN'
		layout.operator("view3d.tila_action_center", icon='OUTLINER_DATA_EMPTY', text='Parent').action_center = 'PARENT'
		layout.operator("view3d.tila_action_center", icon='OUTLINER_DATA_EMPTY', text='Local').action_center = 'LOCAL'
		layout.operator("view3d.tila_action_center", icon='LAYER_ACTIVE', text='Pivot').action_center = 'PIVOT'
		layout.operator("view3d.tila_action_center", icon='LAYER_ACTIVE', text='Pivot Center Parent Axis').action_center = 'PIVOT_CENTER_PARENT_AXIS'
		layout.operator("view3d.tila_action_center", icon='LAYER_ACTIVE', text='Pivot Wold Axis').action_center = 'PIVOT_WORLD_AXIS'
		layout.operator("view3d.tila_action_center", icon='PIVOT_CURSOR', text='Cursor').action_center = 'CURSOR'
		layout.operator("view3d.tila_action_center", icon='PIVOT_CURSOR', text='Cursor Orient').action_center = 'CURSOR_ORIENT'
		layout.operator("view3d.tila_action_center", icon='ADD', text='Custom').action_center = 'CUSTOM'


classes = (
	TILA_action_center_cursor_toggle,
	TILA_action_center,
	TILA_MT_action_center
)

def register():
	bpy.types.WindowManager.ac_use_cursor = bpy.props.BoolProperty(name="Use Cursor", default=False)
	for cl in classes:
		bpy.utils.register_class(cl)
	


def unregister():
	for cl in classes:
		bpy.utils.unregister_class(cl)

	del bpy.types.WindowManager.ac_use_cursor


if __name__ == "__main__":
	register()