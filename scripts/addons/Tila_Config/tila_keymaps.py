from .Tila_KeymapManager import KeymapManager
import bpy
import os

bl_info = {
	"name": "Tilapiatsu Hotkeys",
	"description": "Hotkeys",
	"author": "Tilapiatsu",
	"version": (0, 1, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"wiki_url": "",
	"category": "Hotkeys"
	}


# TODO  
#  Need to read : https://wiki.blender.org/wiki/Source/Depsgraph
# - Change the default Cliping distance
# - Create an action center pie menu : https://blenderartists.org/t/modo-me-the-modo-action-centers-in-blender-and-more-2-80-2-79/1145899
# 		- Automatic
# 		- Selection
# 		- Selection Border
# 		- Selection Center Auto Axis
# 		- Element
# 		- View --> OK
# 		- Origin
# 		- Parent
# 		- Local --> OK
# 		- Pivot
# 		- Pivot Center Parent Axis
# 		- Pivot Wold Axis
# 		- Cursor
# 		- Custom
# - Fix th area pie menu shortcut which dosn't workin in all context
# - Remove double with modal control
# - Vertex Normal Pie Menu : Mark Hard, Mark Soft, update normal, Thief
# - UV Pie Menu : Split, sew, mak seam etc
# - Need to fix the rotate/scaling pivot point in UV context
# - Create a simple Bevel like Modo Does : Bevel + Inset + Segment count
# - Script to visualize Texture checker in all objects in the viewport
# - Fix the uv transform too which is always scaling uniformally
# - Fix the smart edit mode in UV context




# Addon to Enable

# -	  Pro Renderer : https://www.amd.com/en/technologies/radeon-prorender-downloads





class TilaKeymaps(KeymapManager.KeymapManager):

	def __init__(self):

		super(TilaKeymaps, self).__init__()

		self.k_viewfit = 'MIDDLEMOUSE'
		self.k_manip = 'LEFTMOUSE'
		self.k_cursor = 'MIDDLEMOUSE'
		self.k_nav = 'MIDDLEMOUSE'
		self.k_menu = 'SPACE'
		self.k_select = 'LEFTMOUSE'
		self.k_lasso = 'EVT_TWEAK_R'
		self.k_lasso_through = 'EVT_TWEAK_M'
		self.k_box = 'EVT_TWEAK_L'
		self.k_box_through = 'EVT_TWEAK_M'
		self.k_select_attatched = 'EVT_TWEAK_M'
		self.k_context = 'RIGHTMOUSE'
		self.k_more = 'UP_ARROW'
		self.k_less = 'DOWN_ARROW'
		self.k_linked = 'W'
		self.k_vert_mode = 'ONE'
		self.k_edge_mode = 'TWO'
		self.k_face_mode = 'THREE'

		self.k_move = 'G'
		self.k_rotate = 'R'
		self.k_scale = 'S'

	# Global Keymap Functions

	def global_keys(self):
		self.kmi_set_replace("wm.call_menu_pie", "TAB", "PRESS", ctrl=True, properties=[('name', 'VIEW3D_MT_object_mode_pie')])
		self.kmi_set_replace("wm.window_fullscreen_toggle", "F11", "PRESS")
		self.kmi_set_replace('screen.animation_play', self.k_menu, 'PRESS', shift=True)
		
		if self.km.name in ['3D View']:
			self.kmi_set_replace("popup.hp_properties", 'V', "PRESS")
			self.kmi_set_replace('popup.hp_materials', 'M', 'PRESS')
			self.kmi_set_replace('popup.hp_render', 'EQUAL', 'PRESS')
			self.kmi_set_replace('wm.call_menu_pie', 'D', 'PRESS', alt=True, shift=True, properties=[('name', 'HP_MT_pie_rotate90')])
   
		self.kmi_set_replace('wm.call_menu_pie', 'A', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('name', 'HP_MT_pie_add')])
		self.kmi_set_replace('wm.call_menu_pie', 'TAB', 'PRESS', ctrl=True, shift=True, properties=[('name', 'HP_MT_pie_areas')])
		self.kmi_set_replace('wm.call_menu_pie', 'X', 'PRESS', alt=True, shift=True, properties=[('name', 'HP_MT_pie_symmetry')], disable_double=True)
		# Disable Keymap
		self.kmi_set_active(False, type='X')
		self.kmi_set_active(False, type='X', shift=True)
		self.kmi_set_active(False, type='TAB', ctrl=True, shift=True)
		self.kmi_set_active(False, idname='wm.call_panel', type='X', ctrl=True)

	def navigation_keys(self, pan=None, orbit=None, dolly=None, roll=None):
		if orbit:
			self.kmi_set_replace(orbit, self.k_manip, "PRESS", alt=True)
		if pan:
			if self.km.name in ['3D View']:
				self.kmi_set_replace(pan, self.k_manip, "CLICK", alt=True, shift=True)
			else:
				self.kmi_set_replace(pan, self.k_manip, "CLICK_DRAG", alt=True, shift=True)
		if dolly:
			self.kmi_set_replace(dolly, self.k_manip, "PRESS", alt=True, ctrl=True)
		if roll:
			self.kmi_set_replace(roll, self.k_context, "PRESS", alt=True)

	def mode_selection(self):
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', properties=[('mode', 0), ('use_extend', False), ('use_expand', False), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', properties=[('mode', 1), ('use_extend', False), ('use_expand', False), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', properties=[('mode', 2), ('use_extend', False), ('use_expand', False), ('alt_mode', False)], disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', shift=True, properties=[('mode', 0), ('use_extend', True), ('use_expand', False), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', shift=True, properties=[('mode', 1), ('use_extend', True), ('use_expand', False), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', shift=True, properties=[
							 ('mode', 2), ('use_extend', True), ('use_expand', False), ('alt_mode', False)], disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', ctrl=True, properties=[('mode', 0), ('use_extend', False), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', ctrl=True, properties=[
							 ('mode', 1), ('use_extend', False), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', ctrl=True, properties=[
							 ('mode', 2), ('use_extend', False), ('use_expand', True), ('alt_mode', False)], disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', ctrl=True, shift=True, properties=[('mode', 0), ('use_extend', True), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', ctrl=True, shift=True, properties=[('mode', 1), ('use_extend', True), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', ctrl=True, shift=True, properties=[('mode', 2), ('use_extend', True), ('use_expand', True), ('alt_mode', False)], disable_double=True)
		
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', alt=True, properties=[('mode', 0), ('use_extend', False), ('use_expand', False), ('get_border', True)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', alt=True, properties=[('mode', 1), ('use_extend', False), ('use_expand', False), ('get_border', True)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', alt=True, properties=[('mode', 2), ('use_extend', False), ('use_expand', False), ('get_border', True)], disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', 'TAB', 'PRESS', properties=[('alt_mode', True)], disable_double=True)

	def collection_visibility(self, collection_visibility_tool):
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_1', 'PRESS', any=True, properties=[('collection_index', 1)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_2', 'PRESS', any=True, properties=[('collection_index', 2)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_3', 'PRESS', any=True, properties=[('collection_index', 3)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_4', 'PRESS', any=True, properties=[('collection_index', 4)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_5', 'PRESS', any=True, properties=[('collection_index', 5)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_6', 'PRESS', any=True, properties=[('collection_index', 6)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_7', 'PRESS', any=True, properties=[('collection_index', 7)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_8', 'PRESS', any=True, properties=[('collection_index', 8)])
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_9', 'PRESS', any=True, properties=[('collection_index', 9)])
		self.kmi_set_active(False, idname=collection_visibility_tool, type='ZERO')

	def selection_keys(self,
						select_tool=None, 
						lasso_tool=None, select_through_tool=None,
						box_tool=None, box_through_tool=None, node_box_tool=None,
						circle_tool=None, gp_circle_tool=None,
						shortestpath_tool=None,
						loop_tool=None, ring_tool=None,
						more_tool=None, less_tool=None,
						next_tool=None, previous_tool=None, 
						linked_tool=None, linked_pick_tool=None,
						invert_tool=None, inner_tool=None):

		# Select / Deselect / Add
		if select_tool:
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK', properties=[('deselect_all', True)], disable_double=True)
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK', shift=True, properties=[('extend', True)], disable_double=True)
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK', ctrl=True, properties=[('deselect', True)], disable_double=True)
		
		# Lasso Select / Deselect / Add
		if lasso_tool:
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY', disable_double=True)
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY', shift=True, properties=[('mode', 'ADD')], disable_double=True)
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY', ctrl=True, properties=[('mode', 'SUB')], disable_double=True)

		# Lasso through Select / Deselect / Add
		if select_through_tool:
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'ANY', properties=[('type', 'LASSO'), ('mode', 'SET')], disable_double=True)
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'ANY', shift=True, properties=[('type', 'LASSO'), ('mode', 'ADD')], disable_double=True)
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'ANY', ctrl=True, properties=[('type', 'LASSO'), ('mode', 'SUB')], disable_double=True)
		
		# Box Select / Deselect / Add
		if box_tool:
			self.kmi_set_replace(box_tool, self.k_box, 'ANY', properties=[('mode', 'SET'), ('wait_for_input', False), ('tweak', False)], disable_double=True)
			self.kmi_set_replace(box_tool, self.k_box, 'ANY', shift=True, properties=[('mode', 'ADD'), ('wait_for_input', False), ('tweak', False)], disable_double=True)
			self.kmi_set_replace(box_tool, self.k_box, 'ANY', ctrl=True, properties=[('mode', 'SUB'), ('wait_for_input', False), ('tweak', False)], disable_double=True)
		
		if node_box_tool:
			self.kmi_set_replace(node_box_tool, self.k_select, 'CLICK_DRAG', properties=[('mode', 'SET'), ('wait_for_input', False), ('tweak', True)], disable_double=True)
			self.kmi_set_replace(node_box_tool, self.k_box, 'ANY', shift=True, properties=[('mode', 'ADD'), ('wait_for_input', False), ('tweak', False)], disable_double=True)
			self.kmi_set_replace(node_box_tool, self.k_box, 'ANY', ctrl=True, properties=[('mode', 'SUB'), ('wait_for_input', False), ('tweak', False)], disable_double=True)

		# Box Through Select / Deselect / Add
		if box_through_tool:
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'ANY', properties=[('type', 'BOX'), ('mode', 'SET')], disable_double=True)
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'ANY', shift=True, properties=[('type', 'BOX'), ('mode', 'ADD')], disable_double=True)
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'ANY', ctrl=True, properties=[('type', 'BOX'), ('mode', 'SUB')], disable_double=True)
		
		# Circle
		if circle_tool:
			self.kmi_set_replace(circle_tool, self.k_select, 'CLICK_DRAG', shift=True, properties=[('wait_for_input', False), ('mode', 'ADD'), ('radius', 10)], disable_double=True)
			self.kmi_set_replace(circle_tool, self.k_select, 'CLICK_DRAG', ctrl=True, properties=[('wait_for_input', False), ('mode', 'SUB'), ('radius', 10)], disable_double=True)

		if gp_circle_tool:
			self.kmi_set_replace(gp_circle_tool, self.k_select, 'CLICK_DRAG', shift=True, properties=[('wait_for_input', False), ('mode', 'ADD'), ('radius', 10)], disable_double=True)
			self.kmi_set_replace(gp_circle_tool, self.k_select, 'CLICK_DRAG', ctrl=True, properties=[('wait_for_input', False), ('mode', 'SUB'), ('radius', 10)], disable_double=True)

		#  shortest Path Select / Deselect / Add
		if shortestpath_tool:
			self.kmi_remove(idname=shortestpath_tool)
			self.kmi_set_replace(shortestpath_tool, self.k_context, 'CLICK', shift=True, disable_double=True, properties=[('use_fill', False), ('use_face_step', False), ('use_topology_distance', False)])

		# Loop Select / Deselect / Add
		if loop_tool:
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', disable_double=True)
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', shift=True, properties=[('extend', True), ('ring', False)], disable_double=True)
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', ctrl=True, properties=[('extend', False), ('deselect', True)], disable_double=True)

		# Ring Select / Deselect / Add
		if ring_tool:
			self.kmi_set_replace(ring_tool, self.k_cursor, 'CLICK', ctrl=True, properties=[('ring', True), ('deselect', True), ('extend', True), ('toggle', False)], disable_double=True)
			self.kmi_set_replace(ring_tool, self.k_cursor, 'CLICK', shift=True, properties=[('ring', True), ('deselect', False), ('extend', True), ('toggle', False)], disable_double=True)

		# Select More / Less
		if more_tool:
			self.kmi_set_replace(more_tool, self.k_more, 'PRESS', shift=True)

		if less_tool:
			self.kmi_set_replace(less_tool, self.k_less, 'PRESS', shift=True)
		
		# Select Next / Previous
		if next_tool:
			self.kmi_set_replace(next_tool, self.k_more, 'PRESS')

		if previous_tool:
			self.kmi_set_replace(previous_tool, self.k_less, 'PRESS')

		# Linked
		if linked_tool:
			self.kmi_set_replace(linked_tool, self.k_linked, 'DOUBLE_CLICK', ctrl=False, properties=[('deselect', False), ('delimit', {'SEAM'})])
			
		
		if linked_pick_tool:
			if self.km.name in ['Curve', 'Lattice', 'Grease Pencil', 'Particle']:
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=False, properties=[('deselect', False)])
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, properties=[('deselect', True)])

			else:
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=False, properties=[('deselect', False), ('delimit', {'SEAM'})], disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, properties=[('deselect', True), ('delimit', {'SEAM'})], disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', shift=True, properties=[('deselect', False), ('delimit', {'MATERIAL'})], disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, shift=True, properties=[('deselect', True), ('delimit', {'MATERIAL'})], disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', alt=True, properties=[('deselect', False), ('delimit', {'UV'})], disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, alt=True, properties=[('deselect', True), ('delimit', {'UV'})], disable_double=True)

		if invert_tool:
			self.kmi_set_replace(invert_tool, self.k_context, 'CLICK', ctrl=True, alt=True, shift=True, properties=[('action', 'INVERT')])

		if inner_tool:
			self.kmi_set_replace(inner_tool, self.k_select, 'CLICK', ctrl=True, alt=True, shift=True, disable_double=True)

	def selection_tool(self, tool='builtin.select'):
		# select_tool = self.kmi_find(idname='wm.tool_set_by_id', properties=KeymapManager.bProp([('name', 'builtin.select_box')]))
		# if select_tool:
		# 	self.kmi_prop_setattr(select_tool.properties, "name", 'Select')
		# 	self.kmi_prop_setattr(select_tool.properties, "cycle", False)
		if self.km.name in ['Sculpt']:
			self.kmi_set_replace('paint.brush_select', self.k_menu, "PRESS", properties=[('name', tool)])
		else:
			self.kmi_set_replace('wm.tool_set_by_id', self.k_menu, "PRESS", properties=[('name', tool), ('cycle', False)])


	def right_mouse(self):
		kmi = self.kmi_find(idname='wm.call_menu', type='RIGHTMOUSE', value='PRESS')

		if kmi is None:
			print('Cant find right mouse button contextual menu')
		else:
			kmi.value = 'RELEASE'
		
		kmi = self.kmi_find(idname='wm.call_panel', type='RIGHTMOUSE', value='PRESS')

		if kmi is None:
			print('Cant find right mouse button contextual menu')
		else:
			kmi.value = 'RELEASE'

	def duplicate(self, duplicate=None, duplicate_prop=None, duplicate_link=None, duplicate_link_prop=None):
		if duplicate:
			kmi = self.kmi_set_replace(duplicate, 'D', 'PRESS', ctrl=True)
			if duplicate_prop:
				self.kmi_prop_setattr(kmi.properties, duplicate_prop[0], duplicate_prop[1])
		if duplicate_link:
			kmi = self.kmi_set_replace(duplicate_link, 'D', 'PRESS', ctrl=True, shift=True)
			if duplicate_link_prop:
				self.kmi_prop_setattr(kmi.properties, duplicate_link_prop[0], duplicate_link_prop[1])

	def hide_reveal(self, hide=None, unhide=None, inverse=None):
		if hide:
			self.kmi_set_replace(hide, 'H', 'PRESS', properties=[('unselected', False)])
			self.kmi_set_replace(hide, 'H', 'PRESS', ctrl=True, properties=[('unselected', True)])
		if unhide:
			self.kmi_set_replace(unhide, 'H', 'PRESS', alt=True, shift=True, properties=[('select', False)])
		if inverse:
			self.kmi_set_replace(inverse, 'H', 'PRESS', ctrl=True, alt=True, shift=True)

	def snap(self, snapping=None, snapping_prop=None):
		type = 'X'
		self.kmi_set_replace('wm.context_toggle', type, 'PRESS', properties=[('data_path', 'tool_settings.use_snap')])
		if snapping is not None and snapping_prop is not None:
			self.kmi_set_replace(snapping, type, 'PRESS', shift=True, properties=snapping_prop)

	def tool_sculpt(self, sculpt=None):
		if sculpt:
			self.kmi_set_replace(sculpt, 'W', 'PRESS', ctrl=True, alt=True, shift=True)

	def tool_smooth(self):
		self.kmi_set_replace('wm.tool_set_by_id', 'S', 'PRESS', shift=True, properties=[('name', 'builtin.smooth')])
	
	def tool_proportional(self):
		self.modal_set_replace('PROPORTIONAL_SIZE', 'MOUSEMOVE', 'ANY', alt=True)
	
	def tool_smart_delete(self):
		self.kmi_set_active(False, type='DEL')
		self.kmi_set_replace('object.tila_smartdelete', 'DEL', 'PRESS')

	def tool_radial_control(self, radius=None, opacity=None, eraser_radius=None, fill_color=None):
		type = 'S'
		if radius:
			self.kmi_set_replace('wm.radial_control', type, 'PRESS', properties=radius, disable_double=True)
		if opacity:
			self.kmi_set_replace('wm.radial_control', type, 'PRESS', shift=True, properties=opacity, disable_double=True)
		if eraser_radius:
			self.kmi_set_replace('wm.radial_control', type, 'PRESS', ctrl=True, alt=True, properties=eraser_radius, disable_double=True)

	def tool_sample_color(self, tool):
		if tool:
			self.kmi_set_replace(tool, 'C', 'PRESS', disable_double=True)

	def tool_subdivision(self, subdivision=None):
		#  Disabling subdivision_set shortcut
		self.kmi_set_active(False, subdivision, type='ZERO')
		self.kmi_set_active(False, subdivision, type='ONE')
		self.kmi_set_active(False, subdivision, type='TWO')
		self.kmi_set_active(False, subdivision, type='THREE')
		self.kmi_set_active(False, subdivision, type='FOUR')
		self.kmi_set_active(False, subdivision, type='FIVE')

		self.kmi_set_replace(subdivision, 'NUMPAD_PLUS', 'PRESS', properties=[('level', 1), ('relative', True)])
		self.kmi_set_replace(subdivision, 'NUMPAD_MINUS', 'PRESS', disable_double=True, properties=[('level', -1), ('relative', True)])

	def tool_center(self, pivot=None, orientation=None, action_center_context=None):
		print(pivot, orientation)
		if pivot:
			self.kmi_set_replace('wm.call_panel', 'X', 'PRESS', ctrl=True, properties=[('name', pivot), ('keep_open', False)], disable_double=True)
		if orientation:
			self.kmi_set_replace('wm.call_panel', 'X', 'PRESS', ctrl=True, shift=True, properties=[('name', orientation), ('keep_open', False)], disable_double=True)
		if action_center_context:
			self.kmi_set_replace('wm.call_menu', 'X', 'PRESS', alt=True, properties=[('name', 'TILA_MT_action_center')], disable_double=True)
	
	def tool_transform(self):
		self.kmi_set_replace('wm.tool_set_by_id', self.k_move, 'PRESS', properties=[('name', 'builtin.move')])
		self.kmi_set_replace('wm.tool_set_by_id', self.k_rotate, 'PRESS', properties=[('name', 'builtin.rotate')])
		self.kmi_set_replace('wm.tool_set_by_id', self.k_scale, 'PRESS', properties=[('name', 'builtin.scale')])

	# Keymap define
	def set_tila_keymap(self):
		print("----------------------------------------------------------------")
		print("Assigning Tilapiatsu's keymaps")
		print("----------------------------------------------------------------")
		print("")

		# Window
		self.kmi_init(name='Window', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		# self.kmi_set_replace("wm.call_menu_pie", self.k_menu, "PRESS", ctrl=True, shift=True, alt=True)
		self.kmi_set_replace("wm.revert_without_prompt", "N", "PRESS", shift=True)
		
		self.kmi_set_active(False, idname='wm.call_menu', type='F2')
		self.kmi_set_active(False, idname='wm.toolbar')
		self.selection_tool(tool='builtin.select_box')

		# 3D View
		self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool()
		self.tool_smart_delete()
		self.kmi_set_active(False, idname='view3d.select_circle', type="C")
		self.kmi_set_active(False, idname='view3d.cursor3d', type="RIGHTMOUSE")

		self.navigation_keys(pan='view3d.move',
							orbit='view3d.rotate',
							dolly='view3d.zoom',
					   		roll='view3d.view_roll')

		self.selection_keys(select_tool='view3d.select', 
							lasso_tool='view3d.select_lasso',
							select_through_tool='view3d.tila_select_through',
					  		circle_tool='view3d.select_circle')

		# self.kmi_set_active(False, idname='view3d.select', shift=True)

		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)
		self.snap(snapping='wm.call_panel', snapping_prop=[('name', 'VIEW3D_PT_snapping')])

		self.mode_selection()
		
		self.kmi_set_replace('view3d.toggle_x_symetry', 'X', 'PRESS', disable_double=True)
		# self.kmi_set_replace('wm.context_toggle', 'X', 'PRESS', alt=True, shift=True, properties=[('data_path', 'tool_settings.use_snap')], disable_double=True)

		self.kmi_set_replace('wm.tool_set_by_id', 'F', 'PRESS', shift=True, properties=[('name', 'mesh_tool.poly_quilt')], disable_double=True)

		self.kmi_set_replace('view3d.view_persportho', 'NUMPAD_ASTERIX', 'PRESS')

		self.collection_visibility('object.hide_collection')

		self.kmi_set_replace('view3d.view_selected', 'A', 'PRESS', ctrl=True, shift=True)

		self.tool_center(pivot='VIEW3D_PT_pivot_point', orientation='VIEW3D_PT_transform_orientations', action_center_context='VIEW3D')

		self.kmi_set_replace('wm.call_menu_pie', 'Q', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('name', 'HP_MT_boolean')])
		self.kmi_set_replace('view3d.toggle_wireframe', 'F5', 'PRESS', properties=[('selected', False)], disable_double=True)
		self.kmi_set_replace('view3d.toggle_wireframe', 'F5', 'PRESS', shift=True, properties=[('selected', True)], disable_double=True)

		self.kmi_set_replace('wm.call_menu_pie', 'F', 'PRESS', alt=True, shift=True, properties=[('name', 'UVTOOLKIT_MT_pie')])

		# 3d Cursor
		self.kmi_set_replace('view3d.cursor3d', self.k_cursor, 'CLICK', ctrl=True, alt=True, shift=True, properties=[('use_depth', True), ('orientation','GEOM')], disable_double=True)
		self.kmi_set_replace('transform.translate', 'EVT_TWEAK_M', 'ANY', ctrl=True, alt=True, shift=True, properties=[('cursor_transform', True), ('release_confirm', True), ('orient_type', 'NORMAL'), ('snap', True), ('snap_align', True)])

		# View2D
		self.kmi_init(name='View2D', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')

		# View2D buttons List
		self.kmi_init(name='View2D Buttons List', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')

		# Image
		self.kmi_init(name='Image', space_type='IMAGE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='image.view_pan', orbit=None, dolly='image.view_zoom')

		# UV Editor
		self.kmi_init(name='UV Editor', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool()
		self.selection_keys(select_tool='uv.select',
					  		lasso_tool='uv.select_lasso',
							box_through_tool='uv.select_box',
					  		circle_tool='uv.select_circle',
					  		loop_tool='uv.select_loop',
					  		more_tool='uv.select_more',
					  		less_tool='uv.select_less',
					  		linked_tool='uv.select_linked',
							linked_pick_tool='uv.select_linked_pick',
							invert_tool='uv.select_all')
		
		self.kmi_set_replace('uv.cursor_set', self.k_cursor, 'PRESS', ctrl=True, alt=True, shift=True)
		self.tool_smooth()
		self.hide_reveal(hide='uv.hide', unhide='uv.reveal')
		self.snap(snapping='wm.context_menu_enum', snapping_prop=[('data_path', 'tool_settings.snap_uv_element')])
		self.tool_center(pivot='SpaceImageEditor.pivot_point')

		# Mesh
		self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.mode_selection()
		self.tool_transform()

		self.kmi_set_replace('view3d.toggle_x_symetry', 'X', 'PRESS', disable_double=True)

		self.selection_keys(shortestpath_tool='mesh.shortest_path_pick',
							loop_tool='mesh.loop_select',
					  		ring_tool='mesh.edgering_select',
							more_tool='mesh.select_more',
							less_tool='mesh.select_less',
							next_tool='mesh.select_next_item',
							previous_tool='mesh.select_prev_item',
							linked_tool='mesh.select_linked',
							linked_pick_tool='mesh.select_linked_pick',
							invert_tool='mesh.select_all', inner_tool='mesh.loop_to_region')

		# self.kmi_set_active(False, idname='mesh.select_linked_pick', ctrl=False)
		# self.kmi_set_active(False, idname='mesh.select_linked_pick', ctrl=True, alt=False, shift=False, properties=[('deselect', True)])

		self.duplicate(duplicate='mesh.duplicate_move')
		self.hide_reveal(hide='mesh.hide', unhide='mesh.reveal', inverse='view3d.inverse_visibility')
		self.tool_smart_delete()

		self.tool_smooth()
		self.kmi_set_active(False, 'view3d.select_box')
		self.kmi_set_replace('mesh.smart_bevel', 'B', 'PRESS')
		self.kmi_set_replace('mesh.hp_extrude', 'E', 'PRESS')
		self.kmi_set_replace('mesh.knife_tool', 'C', 'PRESS')
		self.kmi_set_replace('wm.tool_set_by_id', 'C', 'PRESS', alt=True, shift=True, properties=[('name', 'builtin.loop_cut')])
		self.kmi_set_replace('mesh.bridge_edge_loops', 'B', 'PRESS', shift=True)
		self.kmi_set_replace('mesh.edge_collapse', 'DEL', 'PRESS', shift=True)
		self.kmi_set_replace('mesh.fill', 'P', 'PRESS', shift=True, properties=[('use_beauty', True)])
		self.kmi_set_replace('mesh.edge_face_add', 'P', 'PRESS')
		self.kmi_set_replace('mesh.flip_normals', 'F', 'PRESS')
		self.kmi_set_replace('mesh.subdivide', 'D', 'PRESS')
		self.kmi_set_replace('transform.shrink_fatten', 'E', 'PRESS', alt=True, shift=True, disable_double=True)
		self.kmi_set_replace('transform.vert_slide', 'S', 'PRESS', ctrl=True, alt=True, properties=[('correct_uv', True)])

		self.kmi_set_replace('mesh.remove_doubles', 'M', 'PRESS', ctrl=True, shift=True, disable_double=True)
		kmi = self.kmi_set_replace('mesh.separate_and_select', 'D', 'PRESS', ctrl=True, shift=True)

		self.tool_subdivision(subdivision='object.subdivision_set')

		self.tool_sculpt('sculpt.sculptmode_toggle')
		
		self.tool_center(pivot='VIEW3D_PT_pivot_point', orientation='VIEW3D_PT_transform_orientations')

		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)

		self.kmi_set_replace('mesh.toggle_use_automerge', 'BACK_SLASH', 'PRESS')
		# self.kmi_set_replace('object.merge_tool', 'M', 'PRESS')
		# self.kmi_set_replace('transform.tosphere', 'S', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)
		self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', alt=True, shift=True, properties=[('name', 'TILA_MT_pie_normal')], disable_double=True)
		self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('name', 'TILA_MT_pie_uv')], disable_double=True)

		self.kmi_set_replace("mesh.edge_rotate", 'V', "PRESS", disable_double=True)
		self.kmi_set_replace("mesh.edge_rotate", 'V', "PRESS", shift=True, properties=[('use_ccw', True)], disable_double=True)

		self.kmi_set_replace('mesh.quads_convert_to_tris', 'T', "PRESS", ctrl=True, properties=[('quad_method','BEAUTY'), ('ngon_method','BEAUTY')])
		self.kmi_set_replace('mesh.tris_convert_to_quads', 'T', "PRESS", alt=True, shift=True)

		# Object Mode
		self.kmi_init(name='Object Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.tool_transform()
		self.duplicate(duplicate='object.duplicate_move', duplicate_link='object.duplicate_move_linked')

		self.selection_keys(invert_tool='object.select_all')

		self.kmi_set_replace('view3d.toggle_x_symetry', 'X', 'PRESS', disable_double=True)

		self.tool_subdivision(subdivision='object.subdivision_set')
		self.kmi_set_replace('object.delete', 'DEL', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('use_global', True), ('confirm', True)])

		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)
		
		self.kmi_set_replace('object.move_to_collection', 'M', 'PRESS', ctrl=True, alt=True, disable_double=True)
		# Set collection visibility shortcut
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		
		self.tool_sculpt('sculpt.sculptmode_toggle')
		self.kmi_set_replace('transform.tosphere', 'S', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)
		self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', alt=True, shift=True, properties=[('name', 'TILA_MT_pie_normal')], disable_double=True)

		# 3D View Tool: Select
		self.kmi_init(name='3D View Tool: Tweak', space_type='EMPTY', region_type='WINDOW')
		self.kmi_set_replace('view3d.select', self.k_select, 'PRESS', properties=[('deselect_all', True)], disable_double=True)
		
		# Sculpt
		self.kmi_init(name='Sculpt', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool(tool='builtin.select_box')
		self.right_mouse()
		self.tool_sculpt('sculpt.sculptmode_toggle')
		self.selection_tool('GRAB')
		
		self.kmi_set_replace('view3d.toggle_x_symetry', 'X', 'PRESS', disable_double=True)

		self.tool_radial_control(radius=[('data_path_primary', 'tool_settings.sculpt.brush.size'), ('data_path_secondary', 'tool_settings.unified_paint_settings.size'), ('use_secondary', 'tool_settings.unified_paint_settings.use_unified_size'), ('rotation_path', 'tool_settings.sculpt.brush.texture_slot.angle'), ('color_path', 'tool_settings.sculpt.brush.cursor_color_add'), ('image_id', 'tool_settings.sculpt.brush')],
						   		opacity=[('data_path_primary', 'tool_settings.sculpt.brush.strength'), ('data_path_secondary', 'tool_settings.unified_paint_settings.strength'), ('use_secondary', 'tool_settings.unified_paint_settings.use_unified_strength'), (
							   'rotation_path', 'tool_settings.sculpt.brush.texture_slot.angle'), ('color_path', 'tool_settings.sculpt.brush.cursor_color_add'), ('image_id', 'tool_settings.sculpt.brush')],
						   		eraser_radius=[('data_path_primary', 'tool_settings.sculpt.brush.texture_slot.angle'), ('rotation_path', 'tool_settings.sculpt.brush.texture_slot.angle'), ('color_path', 'tool_settings.sculpt.brush.cursor_color_add'), ('image_id', 'tool_settings.sculpt.brush')])

		self.kmi_set_replace('sculpt.tila_multires_subdivision', 'D', 'PRESS', properties=[('subd', 1), ('relative', True), ('increase_subd', False)])
		self.kmi_set_replace('sculpt.tila_multires_subdivision', 'D', 'PRESS', ctrl=True, properties=[('subd', 1), ('relative', True), ('increase_subd', True)])
		self.kmi_set_replace('sculpt.tila_multires_subdivision', 'D', 'PRESS', shift=True, properties=[('subd', -1), ('relative', True), ('increase_subd', False)])
		self.kmi_set_replace('sculpt.dynamic_topology_toggle', 'D', 'PRESS', ctrl=True, alt=True, shift=True)
		
		self.kmi_set_replace('paint.mask_lasso_gesture', self.k_context, 'PRESS', ctrl=True, properties=[('value', 1.0), ('mode', 'VALUE')])
		self.kmi_set_replace('paint.mask_lasso_gesture', self.k_context, 'PRESS', shift=True, properties=[('value', 0.0), ('mode', 'VALUE')])
		self.kmi_set_replace('paint.mask_flood_fill', self.k_context, 'PRESS', ctrl=True, alt=True, shift=True, properties=[('mode', 'INVERT')])

		self.kmi_set_replace('paint.hide_show', self.k_nav, 'CLICK_DRAG', ctrl=True,  properties=[('action', 'HIDE'), ('wait_for_input', False), ('area', 'INSIDE')], disable_double=True)
		self.kmi_set_replace('paint.hide_show', self.k_nav, 'CLICK_DRAG', shift=True, properties=[('action', 'HIDE'), ('wait_for_input', False), ('area', 'OUTSIDE')], disable_double=True)
		self.kmi_set_replace('paint.hide_show', self.k_nav, 'PRESS', ctrl=True, alt=True, shift=True, properties=[('action', 'SHOW'), ('wait_for_input', False), ('area', 'ALL')], disable_double=True)
		self.kmi_set_replace('view3d.inverse_visibility', self.k_nav, 'PRESS', alt=True, shift=True)
		

		# Curve
		self.kmi_init(name='Curve', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.tool_transform()
		self.right_mouse()
		self.duplicate(duplicate='curve.duplicate_move')
		self.tool_smart_delete()
		self.kmi_set_replace('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.shortest_path_pick', self.k_select, 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True, ctrl=True, shift=True, properties=[('wait_for_input', False)])
		self.kmi_set_replace('curve.separate', 'D', 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.subdivide', 'D', 'PRESS')

		self.selection_keys(select_tool='curve.select',
					  		lasso_tool='curve.select_lasso',
					  		circle_tool='curve.select_circle',
					  		loop_tool='curve.select_loop',
					  		more_tool='curve.select_more',
					  		less_tool='curve.select_less',
					  		linked_tool='curve.select_linked',
							linked_pick_tool='curve.select_linked_pick',
							invert_tool='curve.select_all')

		# Outliner
		self.kmi_init(name='Outliner', space_type='OUTLINER', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('outliner.item_rename', 'F2', 'PRESS')

		self.tool_smart_delete()
		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)
		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)

		# File Browser
		self.kmi_init(name='File Browser', space_type='FILE_BROWSER', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_smart_delete()
		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)

		# Dopesheet
		self.kmi_init(name='Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='node.duplicate_move', duplicate_link='node.duplicate_move_keep_inputs')

		# Mask Editing
		self.kmi_init(name='Mask Editing', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('mask.duplicate_move', 'D', 'PRESS', ctrl=True)

		# Graph Editor
		self.kmi_init(name='Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='graph.duplicate_move')

		# Property Editor
		self.kmi_init(name='Property Editor', space_type='PROPERTIES', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')
		
		# Vertex Paint
		self.kmi_init(name='Vertex Paint', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		self.kmi_set_replace('view3d.toggle_x_symetry', 'X', 'PRESS', disable_double=True)

		self.tool_radial_control(
		radius=[('data_path_primary', 'tool_settings.vertex_paint.brush.size'), 
		('data_path_secondary', 'tool_settings.unified_paint_settings.size'), 
		('use_secondary', 'tool_settings.unified_paint_settings.use_unified_size'), 
		('rotation_path', 'tool_settings.vertex_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.vertex_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.vertex_paint.brush')],
		opacity=[('data_path_primary', 'tool_settings.vertex_paint.brush.strength'), 
		('data_path_secondary', 'tool_settings.unified_paint_settings.strength'), 
		('use_secondary', 'tool_settings.unified_paint_settings.use_unified_strength'), 
		('rotation_path', 'tool_settings.vertex_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.vertex_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.vertex_paint.brush')],
		eraser_radius=[('data_path_primary', 'tool_settings.vertex_paint.brush.texture_slot.angle'), 
		('rotation_path', 'tool_settings.vertex_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.vertex_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.vertex_paint.brush')])

		self.tool_sample_color('paint.sample_color')

		# self.kmi_set_replace('paint.weight_gradient', self.k_manip, 'PRESS', ctrl=True, shift=True, properties=[('type', 'LINEAR')])
		# self.kmi_set_replace('paint.weight_gradient', self.k_manip, 'PRESS', ctrl=True, shift=True, alt=True, properties=[('type', 'RADIAL')])

		self.kmi_set_replace('wm.tool_set_by_id', self.k_manip, 'PRESS', ctrl=True, shift=True, alt=True, properties=[('name', 'builtin_brush.Draw')])
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', shift=True, properties=[('tool', 'VERTEX'), ('brush', 'BLUR')])
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', ctrl=True, properties=[('tool', 'VERTEX'), ('brush', 'AVERAGE')])

		# Weight Paint
		self.kmi_init(name='Weight Paint', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		self.kmi_set_replace('view3d.toggle_x_symetry', 'X', 'PRESS', disable_double=True)
		
		self.tool_radial_control(
		radius=[('data_path_primary', 'tool_settings.weight_paint.brush.size'), 
		('data_path_secondary', 'tool_settings.unified_paint_settings.size'), 
		('use_secondary', 'tool_settings.unified_paint_settings.use_unified_size'), 
		('rotation_path', 'tool_settings.weight_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.weight_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.weight_paint.brush')],
		opacity=[('data_path_primary', 'tool_settings.weight_paint.brush.strength'), 
		('data_path_secondary', 'tool_settings.unified_paint_settings.strength'), 
		('use_secondary', 'tool_settings.unified_paint_settings.use_unified_strength'), 
		('rotation_path', 'tool_settings.weight_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.weight_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.weight_paint.brush')],
		eraser_radius=[('data_path_primary', 'tool_settings.weight_paint.brush.texture_slot.angle'), 
		('rotation_path', 'tool_settings.weight_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.weight_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.weight_paint.brush')])

		self.tool_sample_color('paint.weight_sample')

		self.kmi_set_replace('paint.weight_gradient', self.k_manip, 'PRESS', ctrl=True, shift=True, properties=[('type', 'LINEAR')])
		self.kmi_set_replace('paint.weight_gradient', self.k_manip, 'PRESS', ctrl=True, shift=True, alt=True, properties=[('type', 'RADIAL')])

		self.kmi_set_replace('wm.tool_set_by_id', self.k_manip, 'PRESS', ctrl=True, shift=True, alt=True, properties=[('name', 'builtin_brush.Draw')])
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', shift=True, properties=[('tool', 'WEIGHT'), ('brush', 'BLUR')])
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', ctrl=True, properties=[('tool', 'WEIGHT'), ('brush', 'AVERAGE')])
		
		# Image Paint
		self.kmi_init(name='Image Paint', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool(tool='builtin.select_box')
		self.right_mouse()
		
		self.kmi_set_replace('view3d.toggle_x_symetry', 'X', 'PRESS', disable_double=True)

		self.tool_radial_control(radius=[('data_path_primary', 'tool_settings.image_paint.brush.size'), 
		('data_path_secondary', 'tool_settings.unified_paint_settings.size'), 
		('use_secondary', 'tool_settings.unified_paint_settings.use_unified_size'), 
		('rotation_path', 'tool_settings.image_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.image_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.image_paint.brush'),
		('fill_color_path', 'tool_settings.image_paint.brush.color'), 
		('fill_color_override_path', 'tool_settings.unified_paint_settings.color'), 
		('fill_color_override_test_path', 'tool_settings.unified_paint_settings.use_unified_color'),
		('zoom_path', 'space_data.zoom'), ('secondary_tex', True)],
		opacity=[('data_path_primary', 'tool_settings.image_paint.brush.strength'), 
		('data_path_secondary', 'tool_settings.unified_paint_settings.strength'), 
		('use_secondary', 'tool_settings.unified_paint_settings.use_unified_strength'), 
		('rotation_path', 'tool_settings.image_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.image_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.image_paint.brush'),
		('fill_color_path', 'tool_settings.image_paint.brush.color'), 
		('fill_color_override_path', 'tool_settings.unified_paint_settings.color'), 
		('fill_color_override_test_path', 'tool_settings.unified_paint_settings.use_unified_color'),
		('secondary_tex', True)],
		eraser_radius=[('data_path_primary', 'tool_settings.image_paint.brush.texture_slot.angle'), 
		('rotation_path', 'tool_settings.image_paint.brush.texture_slot.angle'), 
		('color_path', 'tool_settings.image_paint.brush.cursor_color_add'), 
		('image_id', 'tool_settings.image_paint.brush'),
		('fill_color_path', 'tool_settings.image_paint.brush.color'), 
		('fill_color_override_path', 'tool_settings.unified_paint_settings.color'), 
		('fill_color_override_test_path', 'tool_settings.unified_paint_settings.use_unified_color')],
		fill_color=[('fill_color_path', 'tool_settings.image_paint.brush.color'), 
		('fill_color_override_path', 'tool_settings.unified_paint_settings.color'), 
		('fill_color_override_test_path', 'tool_settings.unified_paint_settings.use_unified_color'),
		('zoom_path', 'space_data.zoom'), ('secondary_tex', True)])

		self.tool_sample_color('paint.sample_color')

		# Node Editor
		self.kmi_init(name='Node Editor', space_type='NODE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		self.selection_keys(node_box_tool='node.select_box')
		self.kmi_set_active(False, idname='node.select_box', type=self.k_box)
		# self.kmi_set_active(False, idname='transform.translate', type=self.k_box)
		# self.kmi_set_active(False, idname='transform.translate', type=self.k_box, properties=[('release_confirm', True)])
		self.kmi_remove(idname='transform.translate', type=self.k_box)
		self.kmi_remove(idname='node.translate_attach', type=self.k_box)
		self.kmi_remove(idname='node.translate_attach', type=self.k_box)

		self.kmi_set_replace('transform.translate', self.k_box, 'ANY', properties=[('release_confirm', True)])
		# self.kmi_set_replace('node.translate_attach', self.k_select_attatched, 'ANY')

		self.duplicate(duplicate='node.duplicate_move', duplicate_link='node.duplicate_move_keep_inputs')
		self.snap(snapping='wm.context_menu_enum', snapping_prop=[('data_path', 'tool_settings.snap_node_element')])
		self.kmi_set_replace('node.view_selected', 'A', 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('node.add_search', self.k_menu, 'PRESS')

		# Animation
		self.kmi_init(name='Animation', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# Armature
		self.kmi_init(name='Armature', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='armature.duplicate_move')

		# Metaball
		self.kmi_init(name='Metaball', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='mball.duplicate_move')

		# NLA Editor
		self.kmi_init(name='NLA Editor', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='nla.duplicate', duplicate_link='nla.duplicate', duplicate_link_prop=('linked', True))
		
		# Lattice
		self.kmi_init(name='Lattice', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_transform()
		self.selection_keys(select_tool='view3d.select', 
							lasso_tool='view3d.select_lasso',
							select_through_tool='view3d.tila_select_through',
					  		circle_tool='view3d.select_circle',
							invert_tool='lattice.select_all')

		# Grease Pencil
		self.kmi_init(name='Grease Pencil', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.mode_selection()
		# self.selection_tool('builtin_brush.Draw')
		self.duplicate(duplicate='gpencil.duplicate_move')
		self.selection_keys(select_tool='gpencil.select',
							lasso_tool='gpencil.select_lasso',
					  		gp_circle_tool='gpencil.select_circle',
					  		more_tool='gpencil.select_more',
					  		less_tool='gpencil.select_less',
					  		next_tool='gpencil.select_first',
					  		previous_tool='gpencil.select_last',
					  		linked_tool='gpencil.select_linked',
							linked_pick_tool='gpencil.select_linked_pick')

		self.tool_sculpt('gpencil.sculptmode_toggle')

		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)

		# Grease Pencil Stroke Edit Mode
		self.kmi_init(name='Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='gpencil.duplicate_move')
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		self.tool_smart_delete()
		self.kmi_set_active(False, idname='gpencil.dissolve')
		self.kmi_set_active(False, idname='gpencil.active_frames_delete_all')
		self.kmi_set_replace('gpencil.dissolve', 'DEL', 'PRESS', shift=True, properties=[('type', 'POINTS')], disable_double=True)
		self.kmi_set_replace('gpencil.active_frames_delete_all', 'DEL', 'PRESS', ctrl=True, alt=True, shift=True)
		self.selection_keys(gp_circle_tool='gpencil.select_circle',
							more_tool='gpencil.select_more',
					  		less_tool='gpencil.select_less',
							invert_tool='gpencil.select_all')

		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True)
		

		# Grease Pencil Stroke Paint Mode
		self.kmi_init(name='Grease Pencil Stroke Paint Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='gpencil.duplicate_move')
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		self.tool_radial_control(radius=[('data_path_primary', 'tool_settings.gpencil_paint.brush.size')], opacity=[('data_path_primary', 'tool_settings.gpencil_paint.brush.gpencil_settings.pen_strength')],
								 eraser_radius=[('data_path_primary', 'preferences.edit.grease_pencil_eraser_radius')])
		
		# Grease Pencil Stroke Paint (Draw brush)
		self.kmi_init(name='Grease Pencil Stroke Paint (Draw brush)', space_type='EMPTY', region_type='WINDOW')
		kmi = self.kmi_find(idname='gpencil.draw', ctrl=False, alt=True, shift=False)
		if kmi:
			kmi.ctrl = True
			kmi.alt = False
			kmi.shift = True

		kmi = self.kmi_find(idname='gpencil.draw', ctrl=False, alt=True, shift=True)
		if kmi:
			kmi.ctrl = True
			kmi.alt = True
			kmi.shift = True

		
		# Grease Pencil Stroke Sculpt Mode
		self.kmi_init(name='Grease Pencil Stroke Sculpt Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_radial_control(radius=[('data_path_primary', 'tool_settings.gpencil_sculpt.brush.size')], opacity=[('data_path_primary', 'tool_settings.gpencil_sculpt.brush.strength')])
		self.kmi_set_replace('wm.tool_set_by_id', 'G', 'PRESS', properties=[('name', 'builtin_brush.Grab')])
		
		# Frames
		self.kmi_init(name='Frames', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('screen.animation_play', 'SPACE', 'PRESS', ctrl=True, shift=True,  properties=[('reverse', True)])

		# Screen
		self.kmi_init(name='Screen', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('screen.screen_full_area', 'SPACE', 'PRESS', ctrl=True, alt=True)
		self.kmi_set_replace('screen.screen_full_area', 'SPACE', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('use_hide_panels', True)])

		# Particle
		self.kmi_init(name='Particle', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.mode_selection()
		self.tool_radial_control(radius=[('data_path_primary', 'tool_settings.particle_edit.brush.size')],
		opacity=[('data_path_primary', 'tool_settings.particle_edit.brush.strength')])

		kmi = self.kmi_find(idname='wm.call_menu', type=self.k_context)
		kmi.value = 'RELEASE'
		self.selection_keys(lasso_tool='view3d.select_lasso',
							select_through_tool='view3d.tila_select_through',
							more_tool='particle.select_more',
					  		less_tool='particle.select_less',
					  		linked_tool='particle.select_linked',
							linked_pick_tool='particle.select_linked_pick',
							invert_tool='particle.select_all')
		

		# Transform Modal Map
		self.kmi_init(name='Transform Modal Map', space_type='EMPTY', region_type='WINDOW')
		self.tool_proportional()
		
		# Knife Tool Modal Map
		self.kmi_init(name='Knife Tool Modal Map', space_type='EMPTY', region_type='WINDOW')
		panning = self.kmi_find(propvalue='PANNING')
		if panning:
			panning.type = self.k_select
			panning.value = 'ANY'
			panning.any = True

		add_cut = self.kmi_find(propvalue='ADD_CUT')
		if add_cut:
			add_cut.type = 'RIGHTMOUSE'

		end_cut = self.kmi_find(propvalue='NEW_CUT')
		if end_cut:
			end_cut.type = 'MIDDLEMOUSE'

		self.modal_set_replace('NEW_CUT', 'SPACE', 'PRESS')
		
		# Gesture Box Modal Map
		self.kmi_init(name='Gesture Box', space_type='EMPTY', region_type='WINDOW')
		self.modal_set_replace('SELECT', self.k_cursor, 'RELEASE', any=True)

		# 3D View Tool: Edit Mesh, PolyQuilt
		self.kmi_init(name='3D View Tool: Edit Mesh, PolyQuilt', space_type='VIEW_3D', region_type='WINDOW')
		self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', ctrl=True, shift=True, properties=[('tool_mode', 'EXTRUDE')], disable_double=True)
		self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', ctrl=True, properties=[('lock_hold', True)], disable_double=True)
		
		print("----------------------------------------------------------------")
		print("Assignment complete")
		print("----------------------------------------------------------------")
		print("")


keymap_List = {}
def register():
	TK = TilaKeymaps()
	TK.set_tila_keymap()

	keymap_List['new'] = TK.keymap_List['new']
	keymap_List['replaced'] = TK.keymap_List['replaced']
	# print("----------------------------------------------------------------")
	# print("Disabling redundant keymap ")
	# print("----------------------------------------------------------------")
	# print("")
	# for kmi in TK.keymap_List["disable"]:
	# 	print("Disabling '{}'".format(kmi.name))
	# 	kmi.active = False

def unregister():
	print("----------------------------------------------------------------")
	print("Reverting Tilapiatsu's keymap")
	print("----------------------------------------------------------------")
	print("")

	TK = TilaKeymaps()
	for k in keymap_List['replaced']:
		try:
			TK.km = k['km']
			print("{} : Replacing '{}' : '{}'  by '{}' : '{}'".format(k['km'].name, k['new_kmi'].idname, k['new_kmi'].to_string(), k['old_kmi'].idname, k['old_kmi'].to_string()))
			TK.replace_km(k['old_kmi'], k['kmis'].from_id(k['old_kmi_id']))
		except Exception as e:
			print("Warning: %r" % e)

	for k in keymap_List['new']:
		try:
			TK.km = k[0]
			print("{} : Removing keymap for '{}' : '{}'".format(k[0].name, k[1].idname, k[1].to_string()))
			TK.km.keymap_items.remove(k[1])
			
		except Exception as e:
			print("Warning: %r" % e)
	
	keymap_List.clear()

	print("----------------------------------------------------------------")
	print("Revert complete")
	print("----------------------------------------------------------------")
	print("")

if __name__ == "__main__":
	register()
