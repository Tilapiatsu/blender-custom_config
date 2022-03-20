bl_info = {
	"name" : "Select Border",
	"author" : "DarkosDK",
	"version" : (1, 0),
	"blender" : (2, 78, 0),
	"location" : "View3D > W > Select Border",
	"description" : "Add to selection all boundary edges linked to active edge. Even if it is not a loop",
	"warning" : "",
	"wiki_url" : "",
	"category" : "Mesh",
	}

import bpy
import bmesh

def find_neighbours_boundary(bm, edge_index):
	vrts = bm.edges[edge_index].verts
	bound_edge = []
	for i in vrts:
		edges = [edge for edge in i.link_edges if edge.is_boundary]
		for d in edges:
			bound_edge.append(d.index)
	bound_edge_arr = set(bound_edge)
	bound_edge = list(bound_edge_arr)
	bound_edge.remove(edge_index)
	return (bound_edge)
	
#operator Select Border
class VIEW3D_MT_edit_mesh_selectborder(bpy.types.Operator):
	"""Add to selection all boundary edges linked to active edge"""
	bl_idname = "mesh.select_border"
	bl_label = "Select Border Edges"
	bl_options = {'REGISTER', 'UNDO'}
	
	extend : bpy.props.BoolProperty(name='extend', default=False)
	deselect : bpy.props.BoolProperty(name='deselect', default=False)
	
	debug=True
	@property
	def mode(self):
		if bpy.context.tool_settings.mesh_select_mode[0]:
			return 0
		if bpy.context.tool_settings.mesh_select_mode[1]:
			return 1
		if bpy.context.tool_settings.mesh_select_mode[2]:
			return 2

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		return (ob and context.mode == 'EDIT_MESH' and context.tool_settings.mesh_select_mode[1] == True)
	
	def get_mesh_element_selection(self, mode):
		if mode == 0:
			total_vert_sel = self.data.total_vert_sel
			if total_vert_sel == 0:
				return []

			return [e.index for e in self.bmesh.verts if e.select]

		if mode == 1:
			total_edge_sel = self.data.total_edge_sel
			if total_edge_sel == 0:
				return []

			return [e.index for e in self.bmesh.edges if e.select]

		if mode == 2:
			total_face_sel = self.data.total_face_sel
			if total_face_sel == 0:
				return []

			return [e.index for e in self.bmesh.faces if e.select]

	def print_debug(self, message):
		if self.debug:
			print('Smart LoopSelect :', message)
   
	def invoke(self, context, event):
		self.loc = event.mouse_region_x, event.mouse_region_y
		return self.execute(context)
     
	def execute(self, context):
    	
		self.print_debug('Border Select')
		# Get the active mesh
		obj = bpy.context.edit_object
		self.data = obj.data
		
		# Get a BMesh representation
		self.bmesh = bmesh.from_edit_mesh(self.data)
		
		self.selected_items = self.get_mesh_element_selection(self.mode)
		
		# check if any element selected
		if len(self.bmesh.select_history) == 0:
			self.report({'WARNING'}, 'Select edge')
		else:
			my_edge = self.bmesh.select_history.active.index

			border_edges = [my_edge]
			border_check = [my_edge]
			self.bmesh.edges.ensure_lookup_table()
			if self.bmesh.edges[my_edge].is_boundary:
				i = True
				while i:
					check_edges = []
					for j in border_check:
						arr = find_neighbours_boundary(self.bmesh, j)
						check_edges.extend(arr)
					new_edges = list(set(check_edges) - set(border_edges))
					if len(new_edges) == 0:
						i = False
					else:
						border_edges.extend(new_edges)
						border_check = new_edges
				
				if self.extend:
					border_edges += self.selected_items
				if self.deselect:
					bpy.ops.view3d.select(deselect=True, extend=False, location=self.loc)

				for k in border_edges:
					self.bmesh.edges[k].select = not self.deselect
			else:
				self.report({'WARNING'}, 'Select edge is not a boundary edge')#print("Select edge is not a boundary edge")

			# Show the updates in the viewport
			# and recalculate n-gon tessellation.
			bmesh.update_edit_mesh(mesh=self.data, loop_triangles=True)
			
		
		return {'FINISHED'}
	

classes = (
	VIEW3D_MT_edit_mesh_selectborder,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()



