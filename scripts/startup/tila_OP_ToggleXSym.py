import bpy
bl_info = {
	"name": "toggle_X_Symetry",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}


class TILA_ToggleSymOperator(bpy.types.Operator):
	bl_idname = "view3d.toggle_symetry"
	bl_label = "TILA: Toggle Symetry"
	bl_options = {'REGISTER', 'UNDO'}

	axis: bpy.props.EnumProperty(items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")], default='X')
	
	def execute(self, context):
		if context.space_data.type not in ['VIEW_3D']:
			return {'FINISHED'}
			
		if len(context.selected_objects) == 0:
			return {'FINISHED'}

		if self.axis == 'X':
			context.object.use_mesh_mirror_x = not context.object.use_mesh_mirror_x
			self.report({'INFO'}, 'X Symetry {}'.format('ON' if context.object.use_mesh_mirror_x else 'OFF'))
		elif self.axis == 'Y':
			context.object.use_mesh_mirror_y = not context.object.use_mesh_mirror_y
			self.report({'INFO'}, 'Y Symetry {}'.format('ON' if context.object.use_mesh_mirror_y else 'OFF'))
		elif self.axis == 'Z':
			context.object.use_mesh_mirror_z = not context.object.use_mesh_mirror_z
			self.report({'INFO'}, 'Z Symetry {}'.format('ON' if context.object.use_mesh_mirror_z else 'OFF'))
		
		bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
		return {'FINISHED'}

classes = (TILA_ToggleSymOperator,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()
