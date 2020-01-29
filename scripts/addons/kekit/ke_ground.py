bl_info = {
	"name": "keGround",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 1, 0),
	"blender": (2, 80, 0),
}
import bpy
import bmesh

def zmove(value, zonly=True):
	if zonly: values = (0, 0, value)
	else: values = value
	bpy.ops.transform.translate(value=values, orient_type='GLOBAL',
								orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
								mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
								proportional_size=1, use_proportional_connected=False,
								use_proportional_projected=False, release_confirm=True)


class MESH_OT_ke_ground(bpy.types.Operator):
	bl_idname = "mesh.ke_ground"
	bl_label = "Ground (or Center)"
	bl_description = "Ground (or Center) selected elements (Auto-connects)"
	bl_options = {'REGISTER', 'UNDO'}

	ke_ground_option: bpy.props.EnumProperty(
		items=[("GROUND", "Ground to Z0", "", "GROUND", 1),
			   ("CENTER", "Ground & Center on Z", "", "CENTER", 2),
			   ("CENTER_ALL", "Center XYZ", "", "CENTER_ALL", 3),
			   ("UNDER", "(Under)Ground to Z0", "", "UNDER", 4),
			   ("CUSTOM", "Ground to custom Z", "", "CUSTOM", 5),
			   ("CUSTOM_CENTER", "Center to custom Z", "", "CUSTOM_CENTER", 6)],
		name="Ground Options",
		default="GROUND")

	ke_ground_custom: bpy.props.FloatProperty(
		name="Custom Z Location:", description="Set custom coordinate on Z axis", default=0)

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		obj = bpy.context.active_object
		mat = obj.matrix_world.copy()
		offset = 0

		# Grab bbox & settings
		bm = bmesh.from_edit_mesh(obj.data)
		vc = [mat @ v.co for v in bm.verts if v.select]
		zs = sorted([c[2] for c in vc])

		# Process
		if vc:
			if self.ke_ground_option == "GROUND":
				offset = round(zs[0], 4) * -1

			elif self.ke_ground_option == "CENTER":
				offset = round(zs[0] + ((zs[-1] - zs[0]) / 2), 4) * -1

			elif self.ke_ground_option == "CENTER_ALL":
				zx = sorted([c[0] for c in vc])
				zy = sorted([c[1] for c in vc])
				xo = round(zx[0] + ((zx[-1] - zx[0]) / 2), 4) * -1
				yo = round(zy[0] + ((zy[-1] - zy[0]) / 2), 4) * -1
				zo = round(zs[0] + ((zs[-1] - zs[0]) / 2), 4) * -1
				zmove((xo,yo,zo), zonly=False)

			elif self.ke_ground_option == "UNDER":
				offset = round(zs[-1], 4) * -1

			elif self.ke_ground_option == "CUSTOM":
				offset = (round(zs[0], 4) - self.ke_ground_custom) * -1

			elif self.ke_ground_option == "CUSTOM_CENTER":
				offset = (round(zs[0] + ((zs[-1] - zs[0]) / 2), 4) - self.ke_ground_custom)* -1

			if offset and self.ke_ground_option != "CENTER_ALL":
				zmove(offset)
		else:
			self.report({"INFO"}, "Ground: Selection Error?")

		# elif mode == "OBJECT":
		# Todo: MEH! Maybe something more useful in the future...removing to save me some hotkey trouble

		# 	for o in bpy.context.selected_objects:
		# 		if o.type == "MESH":
		#
		# 			if self.ke_ground_option == "CENTER_ALL":
		# 				o.location = (0, 0, 0)
		#
		# 			elif self.ke_ground_option == "CUSTOM" or self.ke_ground_option == "CUSTOM_CENTER":
		# 				o.location[2] = self.ke_ground_custom
		#
		# 			else:
		# 				o.location[2] = 0

		return {"FINISHED"}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	MESH_OT_ke_ground,
)

def register():
	for c in classes:
		bpy.utils.register_class(c)

def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)

if __name__ == "__main__":
	register()
