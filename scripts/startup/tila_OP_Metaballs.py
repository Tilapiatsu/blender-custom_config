import bpy, bpy_extras, gpu, bgl, blf
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
import math

bl_info = {
	"name": "Metaballs",
	"description": "Facilitate the edit of Metaballs in viewport",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (3, 20, 0),
	"location": "",
	"warning": "",
	"doc_url": "",
	"category": "3D View"
}

shader2D = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

def draw_circle2D( pos , radius , color = (1,1,1,1), fill = False , subdivide = 64, width : float = 1.0  ):
	r = radius
	dr = math.pi * 2 / subdivide
	vertices = [( pos[0] + r * math.cos(i*dr), pos[1] + r * math.sin(i*dr)) for i in range(subdivide+1)]

	bgl.glEnable(bgl.GL_LINE_SMOOTH)
	bgl.glLineWidth( width )   
	bgl.glEnable(bgl.GL_BLEND)    
	bgl.glDisable(bgl.GL_DEPTH_TEST)    
	shader2D.bind()
	shader2D.uniform_float("color", color )
	primitiveType = 'TRI_FAN' if fill else 'LINE_STRIP'
	batch = batch_for_shader(shader2D, primitiveType , {"pos": vertices} )
	batch.draw(shader2D)
	bgl.glLineWidth(1)
	bgl.glDisable(bgl.GL_LINE_SMOOTH)

class TILA_metaball_adjust_parameter(bpy.types.Operator):
	bl_idname = "mball.tila_metaball_adjust_parameter"
	bl_label = "TILA : Adjust Metaballs Parameter"
	bl_options = {'REGISTER', 'UNDO'}
	
	param: bpy.props.EnumProperty(name="parameter", items=[("STIFFNESS", "Stiffness", ""), ("RADIUS", "Radius", ""),('RESOLUTION', 'Resolution', '')])

	active_object = None
	compatible_type = ['META']
	processing = None
	cancelling = False
	resolution_clamp = 0.1, 2

	@property
	def selected_elements(self):
		if self.active_object is None:
			return 0
		selected_elements = []
		for e in self.active_object.data.elements:
			if e.select:
				selected_elements.append(e)
		return selected_elements

	
	def modal(self, context, event):
		if event.type == 'ESC':
			self.cancelling = True

		# print(event.value, event.type)

		if self.cancelling:
			self.revert_initial_values()
			bpy.types.SpaceView3D.draw_handler_remove(self._value_handler, 'WINDOW')
			self.report({'INFO'}, 'TILA Metaballs : Cancelled')
			return {"CANCELLED"}

		if event.value == 'CLICK' or (event.value == 'PRESS' and event.type == 'ENTER'):
			self.report({'INFO'}, 'TILA Metaballs : Complete')
			# bpy.context.window_manager.event_timer_remove(self._timer)
			bpy.types.SpaceView3D.draw_handler_remove(self._value_handler, 'WINDOW')
			return {"FINISHED"}

		if event.type == 'MOUSEMOVE' and event.value == 'NOTHING':
			self.update_all_values(event)

		return {"PASS_THROUGH"}

	def invoke(self, context, event):
		self.active_object = bpy.context.object
		if self.active_object is None:
			return {"CANCELLED"}

		if self.param != 'RESOLUTION' and not len(self.selected_elements):
			return {"CANCELLED"}

		self.set_initial_position(event)
		self.set_current_position(event)
		self.previous_distance = self.get_mouse_distance()

		self.get_initial_value()

		self._value_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_value, (), 'WINDOW', 'POST_PIXEL')

		bpy.context.window_manager.modal_handler_add(self)

		return {"RUNNING_MODAL"}

	def get_offset(self, event):
		curr_dist = self.get_mouse_distance()
		offset = curr_dist - self.previous_distance
		mult = 0.001 if event.shift else 0.01
		mult = mult * 10 if self.param == 'STIFFNESS' else mult
		offset = offset * mult
		self.set_current_position(event)
		self.previous_distance = curr_dist
		return offset
	
	def set_initial_position(self, event):
		if self.active_object.data.elements.active is not None:
			pos = self.active_object.data.elements.active.co
		else:
			pos = self.active_object.location

		self.initial_mouseposition = bpy_extras.view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.region_data, pos)
		
	def set_current_position(self, event):
		self.current_position = event.mouse_region_x, event.mouse_region_y
	
	def get_mouse_distance(self):
		return math.dist([self.current_position[0], self.current_position[1]], [self.initial_mouseposition[0], self.initial_mouseposition[1]])

	def update_all_values(self, event):
		offset = self.get_offset(event)

		if self.param == 'RESOLUTION':
			value = getattr(self.active_object.data, self.param.lower()) - offset
			
			if value > self.resolution_clamp[0] and value < self.resolution_clamp[1]:
				self.value = value
				setattr(self.active_object.data, self.param.lower(), self.value)

		else:
			for e in self.active_object.data.elements:
				if not e.select:
					continue

				self.value = getattr(e, self.param.lower()) + offset
				setattr(e, self.param.lower(), self.value)


	def get_initial_value(self):
		if self.param == 'RESOLUTION':
			self.initial_value = [self.active_object.data.resolution]
		else:
			self.initial_value = []
			for e in self.active_object.data.elements:
				self.initial_value.append(getattr(e, self.param.lower()))

	def revert_initial_values(self):
		if self.param == 'RESOLUTION':
			self.active_object.data.resolution = self.initial_value[0]
		else:
			for i, e in enumerate(self.active_object.data.elements):
				setattr(e, self.param.lower(), self.initial_value[i])

	def draw_value(self):
		font_id = 0
		blf.size(font_id, 17, 72)

		blf.color(font_id, 1, 1, 1, 0.5)
		blf.position(font_id, bpy.context.region.width/2, 20, 0)
		blf.draw(font_id, f'{self.param.lower()} : {str(self.value)[:4]}')

classes = (
	TILA_metaball_adjust_parameter,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()