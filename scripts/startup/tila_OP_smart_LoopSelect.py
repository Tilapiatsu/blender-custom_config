
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy, bmesh, math
from bpy_extras.view3d_utils import location_3d_to_region_2d

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

	def __init__(self):
		self._active_vert = None
		self._active_edge = None
		self._active_face = None
	
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
		if self._active_vert is None:
			if self.bmesh.select_history.active is not None:
				self._active_vert = self.bmesh.verts[self.bmesh.select_history.active.index]
			else:
				self._active_vert = self.bmesh._active_vert[self.bmesh.select_history[-1].index]
		return self._active_vert
 
	@property
	def active_edge(self):
		if self._active_edge is None:
			if self.bmesh.select_history.active is not None:
				self._active_edge = self.bmesh.edges[self.bmesh.select_history.active.index]
			else:
				# self.bmesh.select_history.validate()
				for e in self.bmesh.select_history:
					print(e.index)
				self._active_edge = self.bmesh.edges[self.bmesh.select_history[-1].index]
		return self._active_edge

	@property
	def active_face(self):
		if self._active_face is None:
			if self.bmesh.select_history.active is not None:
				self._active_face = self.bmesh.faces[self.bmesh.select_history.active.index]
			else:
				for e in self.bmesh.select_history:
					print(e.index)
				self._active_face = self.bmesh.faces[self.bmesh.select_history[-1].index]
		return self._active_face
  
	def init_bmesh(self, context):
		selection = context.object
		self.data = selection.data
		self.bmesh = bmesh.from_edit_mesh(selection.data)

	def invoke(self, context, event):
	 
		self.init_bmesh(context)
		self.selected_elements = self.bmesh.select_history
		if not self.extend and not self.deselect:
			self.bmesh.select_flush(True)

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
		
		def select_elements(self, deselect, elements):
			for e in elements:
				e.select_set(not deselect)

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

		def select_edge_loop(self, edge, angle_threshold):
			edge_angle = math.degrees(edge.calc_face_angle(0))
			if edge_angle < angle_threshold:
				bpy.ops.mesh.loop_select("INVOKE_DEFAULT", extend=self.extend, deselect=self.deselect)
			else:
				bpy.ops.ls.select()
    

		if bpy.context.mode in ['EDIT_MESH']:
			# vert selection mode   
			if bpy.context.scene.tool_settings.mesh_select_mode[0]:
				bpy.ops.mesh.loop_select('INVOKE_DEFAULT', extend=self.extend, ring=False, deselect=False)
			
   			# Edge selection mode
			elif bpy.context.scene.tool_settings.mesh_select_mode[1]:
				# select Border edgeloop
				if border_edge_selected(self) is not None:
					bpy.ops.mesh.select_border('INVOKE_DEFAULT', extend=self.extend, deselect=self.deselect)
					if self.extend:
						select_elements(self, False, self.selected_elements)
				
				# select ngon borders
				elif ngon_edge_selected(self) is not None:
					select_elements(self, self.deselect, ngon_edge_selected(self).edges)
					if self.extend and len(self.selected_elements):
						select_elements(False, self.selected_elements)
				
	   			#  Fallback : select edge loop
				else:
					select_edge_loop(self, self.active_edge, 94.5)
					if self.extend:
						select_elements(self, False, self.selected_elements)
		
			# Face selection mode
			elif bpy.context.scene.tool_settings.mesh_select_mode[2]:
				bpy.ops.mesh.loop_select('INVOKE_DEFAULT', extend=self.extend, ring=False, deselect=False, toggle=False)

		elif bpy.context.mode in ['EDIT_CURVE']:
			pass
		elif bpy.context.mode in ['EDIT_GPENCIL', 'PAINT_GPENCIL', 'SCULPT_GPENCIL', 'WEIGHT_GPENCIL']:
			pass

		elif bpy.context.mode in ['PAINT_WEIGHT', 'PAINT_VERTEX']:
			pass
		elif bpy.context.mode in ['PARTICLE']:
			pass
		else:
			pass

		bmesh.update_edit_mesh(mesh=self.data, loop_triangles=True)

		return {'FINISHED'}


classes = (
	TILA_smart_loopselect,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()
