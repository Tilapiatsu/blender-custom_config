
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy, bmesh, math
bl_info = {
	"name": "Smart LoopSelect",
	"description": "Automatically triggers the proper operator depending on the contect",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"doc_url": "",
	"category": "3D View"
}


class TILA_smart_loopselect(bpy.types.Operator):
	bl_idname = "view3d.tila_smart_loopselect"
	bl_label = "Smart Edit Mode"
	bl_options = {'REGISTER', 'UNDO'}

	
	extend : bpy.props.BoolProperty(name='extend', default=False)
	deselect : bpy.props.BoolProperty(name='deselect', default=False)


	mesh_mode = ['VERT', 'EDGE', 'FACE']
	gpencil_mode = ['POINT', 'STROKE', 'SEGMENT']
	uv_mode = ['VERTEX', 'EDGE', 'FACE', 'ISLAND']
	particle_mode = ['PATH', 'POINT', 'TIP']
	selected_elements = []
	max_elements = 1000

	@classmethod
	def poll(cls, context):
		return context.space_data.type in ['VIEW_3D']

	def modal(self, context, event):
		pass

	@property
	def mode(self):
		if bpy.context.tool_settings.mesh_select_mode[0]:
			return 0
		if bpy.context.tool_settings.mesh_select_mode[1]:
			return 1
		if bpy.context.tool_settings.mesh_select_mode[2]:
			return 2

	@property
	def active_vert(self):
		return self.bmesh.vert[self.bmesh.select_history.active.index]	
 
	@property
	def active_edge(self):
		return self.bmesh.edges[self.bmesh.select_history.active.index]

	@property
	def active_face(self):
		return self.bmesh.faces[self.bmesh.select_history.active.index]
  
	def init_bmesh(self, context):
		selection = context.object
		self.data = selection.data
		self.bmesh = bmesh.from_edit_mesh(selection.data)

	def invoke(self, context, event):
		self.init_bmesh(context)

		def switch_mesh_mode(self, current_mode):
			if self.mesh_mode[self.mode] == current_mode:
				bpy.ops.object.editmode_toggle()
			else:
				bpy.ops.mesh.select_mode(extend=self.extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

		def switch_gpencil_mode(self, current_mode):
			if self.gpencil_mode[self.mode] == current_mode:
				bpy.ops.gpencil.editmode_toggle()
			else:
				bpy.context.scene.tool_settings.gpencil_selectmode_edit = self.gpencil_mode[self.mode]

		def switch_uv_mode(self, current_mode):
			if bpy.context.scene.tool_settings.use_uv_select_sync:
				switch_mesh_mode(self, self.mesh_mode[mesh_mode_link(self, current_mode)])
			else:
				bpy.context.scene.tool_settings.uv_select_mode = self.uv_mode[self.mode]
		
		def mesh_mode_link(self, mode):
			for m in self.mesh_mode:
				if mode in m:
					return self.mesh_mode.index(m)
				else:
					return 0

		def select_border(self, current_mode):
			# if self.mesh_mode[self.mode] != current_mode:
			if self.mesh_mode[self.mode] != 'FACE':
				bpy.ops.mesh.region_to_loop()
				switch_mesh_mode(self, current_mode)
			else:
				pass

		def switch_particle_mode(self):
			bpy.context.scene.tool_settings.particle_edit.select_mode = self.particle_mode[self.mode] 

		def border_edge_selected(self):
			if len(self.bmesh.select_history) == 0:
				return None
			if self.bmesh.edges[self.bmesh.select_history.active.index].is_boundary:
				return self.bmesh.edges[self.bmesh.select_history.active.index]
			else:
				return None
		
		def ngon_edge_selected(self):
			if len(self.bmesh.select_history) == 0:
				return None
			active = self.bmesh.edges[self.bmesh.select_history.active.index]
			for f in active.link_faces:
				if len(f.edges) > 4:
					return f
			return None
		
		def get_mesh_element_selection(mode):
			selection = bpy.context.object

			if mode == 'VERT':
				total_vert_sel = self.data.total_vert_sel
				if total_vert_sel == 0:
					return []

				return [e for e in self.bmesh.verts if e.select]

			if mode == 'EDGE':
				total_edge_sel = self.data.total_edge_sel
				if total_edge_sel == 0:
					return []

				return [e for e in self.bmesh.edges if e.select]
 
			if mode == 'FACE':
				total_face_sel = self.data.total_face_sel
				if total_face_sel == 0:
					return []

				return [e for e in self.bmesh.faces if e.select]
		
		def select_elements(mode, elements):
			for e in elements:
				e.select_set(True)

		#   Dosn't Work
		def get_linked_border_edges(edge, border_edges, evaluated_verts):
			if len(border_edges) >= 100:
				return border_edges
			for v in edge.verts:
				if v in evaluated_verts:
					continue
				
				print("Evaluating Verts = ", v.index)
				evaluated_verts.append(v)

				for e in v.link_edges:
					if e in border_edges:
						continue
					if e.is_boundary:
						print("Edge contains boundary = ", e.index)
						border_edges.append(e)
						border_edges += get_linked_border_edges(e, border_edges, evaluated_verts)

			return border_edges

		def select_loop(self, edge, angle_threshold):
			print(math.degrees(edge.calc_face_angle(0)))
			if math.degrees(edge.calc_face_angle(0)) < angle_threshold:
				bpy.ops.mesh.loop_select("INVOKE_DEFAULT", extend=self.extend, deselect=self.deselect)
			else:
				bpy.ops.ls.select()

		if bpy.context.mode == 'EDIT_MESH':
			method = switch_mesh_mode
			if self.extend:
				pass
				self.selected_elements = get_mesh_element_selection(mode=self.mesh_mode[self.mode])
			if bpy.context.scene.tool_settings.mesh_select_mode[0]:
				bpy.ops.mesh.loop_select(extend=self.extend, ring=False, deselect=False)
    
			elif bpy.context.scene.tool_settings.mesh_select_mode[1]:
				# select Border edgeloop
				if border_edge_selected(self) is not None:
					bpy.ops.mesh.select_border('INVOKE_DEFAULT')
					select_elements(self, self.selected_elements)
				
    			# select ngon borders
				elif ngon_edge_selected(self) is not None:
					select_elements(self, ngon_edge_selected(self).edges)
					select_elements(self, self.selected_elements)
    			
       			#  Fallback : select edge loop
				else:
					select_loop(self, self.active_edge, 100)
					select_elements(self, self.selected_elements) 

			elif bpy.context.scene.tool_settings.mesh_select_mode[2]:
				method(self, 'FACE')

		elif bpy.context.mode == 'EDIT_CURVE':
			if self.alt_mode:
				bpy.ops.object.mode_set(mode='OBJECT')
			else:
				pass
		elif bpy.context.mode in ['EDIT_GPENCIL', 'PAINT_GPENCIL', 'SCULPT_GPENCIL', 'WEIGHT_GPENCIL']:
			if self.alt_mode:
				bpy.ops.object.mode_set(mode='OBJECT')
			else:
				switch_gpencil_mode(self, bpy.context.scene.tool_settings.gpencil_selectmode_edit)

		elif bpy.context.mode in ['PAINT_WEIGHT', 'PAINT_VERTEX']:
			if self.alt_mode:
				bpy.ops.object.mode_set(mode='OBJECT')
			else:
				if self.mode == 0 and not bpy.context.object.data.use_paint_mask_vertex:                   
					bpy.context.object.data.use_paint_mask_vertex = True
				elif self.mode == 2 and not bpy.context.object.data.use_paint_mask:
					bpy.context.object.data.use_paint_mask = True
				elif self.mode == 1:
					pass
				else:
					bpy.context.object.data.use_paint_mask_vertex = False
					bpy.context.object.data.use_paint_mask = False
		
		elif bpy.context.mode in ['PARTICLE']:
			if self.alt_mode:
				bpy.ops.object.mode_set(mode='OBJECT')
			else:
				switch_particle_mode(self)

		else:
			bpy.ops.object.mode_set(mode='OBJECT')

		bmesh.update_edit_mesh(mesh=self.data, loop_triangles=True)

		return {'FINISHED'}


classes = (
	TILA_smart_loopselect,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()
