
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy, bmesh
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

	def invoke(self, context, event):
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
			selection = bpy.context.object

			data = selection.data
			bm = bmesh.new()
			bm.from_mesh(data)

			total_edge_sel = data.total_edge_sel

			if total_edge_sel == 0:
				return False

			border = [e for e in bm.edges if e.is_boundary and e.select]
			bm.free()
   
			return len(border) > 0
		
		def get_mesh_element_selection(mode):
			selection = bpy.context.object

			data = selection.data
			bm = bmesh.new()
			bm.from_mesh(data)
   
			if mode == 'VERT':
				total_vert_sel = data.total_vert_sel
				if total_vert_sel == 0:
					return []

				return [e for e in bm.verts if e.select]

			if mode == 'EDGE':
				total_edge_sel = data.total_edge_sel
				if total_edge_sel == 0:
					return []

				return [e for e in bm.edges if e.select]
 
			if mode == 'FACE':
				total_face_sel = data.total_face_sel
				if total_face_sel == 0:
					return []

				return [e for e in bm.faces if e.select]

			bm.free()
		
		def select_elements(mode, elements):
			for e in elements:
				e.select_set(True)
  
		if bpy.context.mode == 'EDIT_MESH':
			method = switch_mesh_mode
			if self.extend:
				pass
				self.selected_elements = get_mesh_element_selection(mode=self.mesh_mode[self.mode])
			if bpy.context.scene.tool_settings.mesh_select_mode[0]:
				bpy.ops.mesh.loop_select(extend=self.extend, ring=False, deselect=False)
			elif bpy.context.scene.tool_settings.mesh_select_mode[1]:
				# temporay run the previous loop
				bpy.ops.mesh.loop_select("INVOKE_DEFAULT", extend=self.extend, deselect=self.deselect)
				
				# if border_edge_selected(self):
				# 	bpy.ops.mesh.select_similar(type='FACE', threshold=0.01)
				# 	select_elements(self, self.selected_elements)   
				# else:
				# 	bpy.ops.ls.select()
				# 	select_elements(self, self.selected_elements)     

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

		return {'FINISHED'}


classes = (
	TILA_smart_loopselect,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()
