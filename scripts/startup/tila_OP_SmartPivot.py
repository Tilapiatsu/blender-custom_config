import bpy
import bmesh
from mathutils import Vector, Matrix

bl_info = {
	"name": "Tila : Smart Pivot",
	"description": "Move Pivot to the average position of all selected elements",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"doc_url": "",
	"category": "Mesh"
}

class TILA_smart_pivot(bpy.types.Operator):
	bl_idname = "mesh.tila_smart_pivot"
	bl_label = "Tila : Move Pivot to Selection"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.mode == 'EDIT' and obj.type in ['MESH'] and obj.data.total_vert_sel > 0

	def execute(self, context):
		obj = context.active_object
		bm = bmesh.from_edit_mesh(obj.data)

		# Get the average location of all selected elements
		selection = [v for v in bm.verts if v.select]
		selected_edge_faces = [e.verts for e in bm.edges if e.select] + [f.verts for f in bm.faces if f.select]
		for e in selected_edge_faces:
			for v in e:
				selection.append(v)

		if not selection:
			return {'CANCELLED'}
		avg_loc = sum([v.co for v in selection], Vector()) / len(selection)

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.scene.tool_settings.use_transform_data_origin = True
		bpy.ops.transform.translate(value=avg_loc)
		bpy.context.scene.tool_settings.use_transform_data_origin = False
		bpy.ops.object.mode_set(mode='EDIT')

		return {'FINISHED'}

classes = (
	TILA_smart_pivot,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()
