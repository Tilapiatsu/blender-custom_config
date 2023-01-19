import bpy
import numpy as np
import bmesh

bl_info = {
	"name": "Tila : Create Bounding Box",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}

CUBE_FACE_INDICES = (
	(0, 1, 3, 2),
	(2, 3, 7, 6),
	(6, 7, 5, 4),
	(4, 5, 1, 0),
	(2, 6, 4, 0),
	(7, 3, 1, 5),
)

class TILA_CreateBoundingBox(bpy.types.Operator):
	bl_idname = "object.tila_create_bounding_box"
	bl_label = "TILA : Create Bounding Box"
	bl_options = {'REGISTER', 'UNDO'}

	orientation: bpy.props.EnumProperty(name="Orientation", items=[("BEST", "Best", ""), ("WORLD", "World", "")])
	push : bpy.props.FloatProperty(name="Push", default=0)

	compatible_type = ['MESH']
	mode = None

	def execute(self, context):
		if bpy.context.mode == 'OBJECT':
			self.mode = 'OBJECT'
			self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]
		
			if not len(self.object_to_process):
				return {'CANCELLED'}

			for o in self.object_to_process:
				self.create_bounding_box(o)

		elif bpy.context.mode == 'EDIT_MESH':
			self.mode = 'MESH'
			self.create_bounding_box(bpy.context.selected_objects[0])
		elif bpy.context.mode == 'EDIT_CURVE':
			pass
	
		return {'FINISHED'}


	# Bounding box calculation from "iyadahmed":
	# https://gist.github.com/iyadahmed/8874b92c27dee9d3ca63ab86bfc76295
	@staticmethod
	def gen_cube_verts():
		for x in range(-1, 2, 2):
			for y in range(-1, 2, 2):
				for z in range(-1, 2, 2):
					yield x, y, z


	def minimum_bounding_box_pca(self, points):
		"""Calculate minimum bounding box using PCA, return bounding box points and face indices"""
		cov_mat = np.cov(points, rowvar=False, bias=True)
		eig_vals, eig_vecs = np.linalg.eigh(cov_mat)

		change_of_basis_mat = eig_vecs
		inv_change_of_basis_mat = np.linalg.inv(change_of_basis_mat)

		aligned = points.dot(inv_change_of_basis_mat.T)

		bb_min = aligned.min(axis=0)
		bb_max = aligned.max(axis=0)

		center = (bb_max + bb_min) / 2
		center_world = center.dot(change_of_basis_mat.T)

		bb_points = np.array(list(TILA_CreateBoundingBox.gen_cube_verts()), dtype=np.float64)
		bb_points *= (bb_max - bb_min) / 2
		bb_points = bb_points.dot(change_of_basis_mat.T)
		bb_points += center_world

		return bb_points, CUBE_FACE_INDICES

	def get_vertex_selection(self, obj):
		all_verts = obj.data.vertices
		if self.mode == 'MESH':
			n = len([v for v in obj.data.vertices if v.select])
			verts = np.empty(n * 3)
			
			# return all_verts.foreach_get("select", verts)
			return all_verts
		elif self.mode == 'OBJECT':
			return all_verts
		else:
			return []

	def create_bounding_box(self, obj: bpy.types.Object):
		verts = self.get_vertex_selection(obj)

		if not len(verts):
			return

		n = len(verts)
		vert_co_arr = np.empty(n * 3)
		verts.foreach_get("co", vert_co_arr)
		vert_co_arr.shape = n, 3

		corners, faces = self.minimum_bounding_box_pca(vert_co_arr)

		bbox_mesh = bpy.data.meshes.new("bbox")
		bbox_mesh.from_pydata(corners, [], faces)
		bbox_mesh.validate()

		bm = bmesh.new()
		bm.from_mesh(bbox_mesh)
		bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
		bm.to_mesh(bbox_mesh)
		bm.free()

		bbox_object = bpy.data.objects.new(obj.name + "_bbox", bbox_mesh)

		# bbox_object.data = bbox_mesh
		obj.users_collection[0].objects.link(bbox_object)
		self.match_transform(obj, bbox_object)
	
	def match_transform(self, to_match_object, destination_object):
		target = bpy.context.object
		loc = destination_object.matrix_world.to_translation()
		rot = destination_object.matrix_world.to_euler('XYZ')
		scl = destination_object.matrix_world.to_scale()

		to_match_object.location = loc
		to_match_object.rotation_euler = rot
		to_match_object.scale = scl

		return {'FINISHED'}



classes = (TILA_CreateBoundingBox,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()
