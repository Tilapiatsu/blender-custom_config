import bpy
from abc import ABC, abstractmethod
from .KeymapManager import KeymapManager
from .blender_version import bversion
from . log_list import TILA_Config_Log as Log


# TODO  
#  Need to read : https://wiki.blender.org/wiki/Source/Depsgraph
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
# - Vertex Normal Pie Menu :  Thief
# - Need to fix the rotate/scaling pivot point in UV context
# - Create a simple Bevel like Modo Does : Bevel + Inset + Segment count
# - Script to visualize Texture checker in all objects in the viewport
# - Fix the smart edit mode in UV context

class TILA_Config_Keymaps(ABC, KeymapManager.KeymapManager):
	k_viewfit = 'MIDDLEMOUSE'
	k_manip = 'LEFTMOUSE'
	k_cursor = 'MIDDLEMOUSE'
	k_nav = 'MIDDLEMOUSE'
	k_menu = 'SPACE'
	k_select = 'LEFTMOUSE'
	k_lasso = 'RIGHTMOUSE'
	k_lasso_through = 'MIDDLEMOUSE'
	k_box = 'LEFTMOUSE'
	k_box_through = 'MIDDLEMOUSE'
	k_select_attatched = 'MIDDLEMOUSE'
	k_context = 'RIGHTMOUSE'
	k_more = 'UP_ARROW'
	k_less = 'DOWN_ARROW'
	k_linked = 'W'
	k_vert_mode = 'ONE'
	k_edge_mode = 'TWO'
	k_face_mode = 'THREE'
	k_move = 'G'
	k_rotate = 'R'
	k_scale = 'S'

	def __init__(self):
		super(TILA_Config_Keymaps, self).__init__()
		self.log_progress = Log(bpy.context.window_manager.tila_config_log_list, 'tila_config_log_list_idx')

	@abstractmethod
	def set_keymaps(self):
		pass

	def print_status(self, message, start=True):
		print("----------------------------------------------------------------")
		print(f"{message}")
		print("----------------------------------------------------------------")
		print("")
		if start:
			self.log_progress.start(f"{message}")
		else:
			self.log_progress.done(f"{message}")

class TILA_Config_Keymaps_Global(TILA_Config_Keymaps):
	addon_name = "Global"

	def __init__(self):
		super(TILA_Config_Keymaps_Global, self).__init__()

	# Global Keymap Functions
	def global_keys(self):
		# Disable Keymap
		self.kmi_set_active(False, type='X')
		self.kmi_set_active(False, type='X', shift=True)
		self.kmi_set_active(False, type='TAB', ctrl=True, shift=True)
		self.kmi_set_active(False, idname='wm.call_panel', type='X', ctrl=True)

		# Set global Keymap
		self.kmi_set_replace("wm.call_menu_pie", "TAB", "PRESS", ctrl=True, properties={'name': 'VIEW3D_MT_object_mode_pie'})
		self.kmi_set_replace("wm.window_fullscreen_toggle", "F11", "PRESS")
		self.kmi_set_replace('screen.animation_play', self.k_menu, 'PRESS', shift=True)
		self.kmi_set_replace('screen.userpref_show', 'F4', 'PRESS')
		
		if self.km.name in ['3D View', 'Mesh']:
			# self.kmi_set_replace("popup.hp_properties", 'Q', 'PRESS', disable_double=True)
			self.kmi_set_replace('popup.hp_materials', 'M', 'PRESS', disable_double=True)
			self.kmi_set_replace('popup.hp_render', 'EQUAL', 'PRESS', disable_double=True)
			# self.kmi_set_replace('wm.call_menu_pie', 'D', 'PRESS', alt=True, shift=True, properties={'name': 'HP_MT_pie_rotate90'})
   
		# self.kmi_set_replace('wm.call_menu_pie', 'A', 'PRESS', ctrl=True, alt=True, shift=True, properties={'name': 'HP_MT_pie_add'})
		self.kmi_set_replace('wm.call_menu_pie', 'TAB', 'PRESS', ctrl=True, shift=True, properties={'name': 'TILA_MT_pie_areas'})
		
	def navigation_keys(self, pan=None, orbit=None, dolly=None, roll=None):
		# if self.km.name in ['3D View', 'Image']:
		# 	Value = "PRESS"
		# else:
		# 	Value = "CLICK_DRAG"
		if orbit:
			self.kmi_set_replace(orbit, self.k_manip, "PRESS", alt=True, disable_double=True)
		if pan:
			self.kmi_set_replace(pan, self.k_manip, "PRESS", alt=True, shift=True, disable_double=True)
		if dolly:
			self.kmi_set_replace(dolly, self.k_manip, "CLICK_DRAG", alt=True, ctrl=True, disable_double=True)
		if roll:
			self.kmi_set_replace(roll, self.k_context, "PRESS", alt=True, disable_double=True)

	def mode_selection(self):
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', properties={'mode': 0, 'use_extend': False, 'use_expand': False, 'alt_mode': False, 'get_border': False}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', properties={'mode': 1, 'use_extend': False, 'use_expand': False, 'alt_mode': False, 'get_border': False}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', properties={'mode': 2, 'use_extend': False, 'use_expand': False, 'alt_mode': False, 'get_border': False}, disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', shift=True, properties={'mode': 0, 'use_extend': True, 'use_expand': False, 'alt_mode': False, 'get_border': False}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', shift=True, properties={'mode': 1, 'use_extend': True, 'use_expand': False, 'alt_mode': False, 'get_border': False}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', shift=True, properties={'mode': 2, 'use_extend': True, 'use_expand': False, 'alt_mode': False, 'get_border': False}, disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', ctrl=True, properties={'mode': 0, 'use_extend': False, 'use_expand': True, 'alt_mode': False, 'get_border': False}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', ctrl=True, properties={'mode': 1, 'use_extend': False, 'use_expand': True, 'alt_mode': False, 'get_border': False}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', ctrl=True, properties={'mode': 2, 'use_extend': False, 'use_expand': True, 'alt_mode': False, 'get_border': False}, disable_double=True)

		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', ctrl=True, shift=True, properties={'mode': 0, 'use_extend': True, 'use_expand': True, 'alt_mode': False, 'get_border': False}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', ctrl=True, shift=True, properties={'mode': 1, 'use_extend': True, 'use_expand': True, 'alt_mode': False, 'get_border': False}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', ctrl=True, shift=True, properties={'mode': 2, 'use_extend': True, 'use_expand': True, 'alt_mode': False, 'get_border': False}, disable_double=True)
		
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_vert_mode, 'PRESS', alt=True, properties={'mode': 0, 'use_extend': False, 'use_expand': False, 'get_border': True}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_edge_mode, 'PRESS', alt=True, properties={'mode': 1, 'use_extend': False, 'use_expand': False, 'get_border': True}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', self.k_face_mode, 'PRESS', alt=True, properties={'mode': 2, 'use_extend': False, 'use_expand': False, 'get_border': True}, disable_double=True)
		self.kmi_set_replace('view3d.tila_smart_editmode', 'TAB', 'PRESS', properties={'alt_mode': True}, disable_double=True)

	def collection_visibility(self, collection_visibility_tool):
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_1', 'PRESS', any=True, properties={'collection_index': 1})
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_2', 'PRESS', any=True, properties={'collection_index': 2})
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_3', 'PRESS', any=True, properties={'collection_index': 3})
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_4', 'PRESS', any=True, properties={'collection_index': 4})
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_5', 'PRESS', any=True, properties={'collection_index': 5})
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_6', 'PRESS', any=True, properties={'collection_index': 6})
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_7', 'PRESS', any=True, properties={'collection_index': 7})
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_8', 'PRESS', any=True, properties={'collection_index': 8})
		self.kmi_set_replace(collection_visibility_tool, 'NUMPAD_9', 'PRESS', any=True, properties={'collection_index': 9})
		self.kmi_set_active(False, idname=collection_visibility_tool, type='ZERO')

	def selection_keys(self,
						select_tool=None, 
						lasso_tool=None, select_through_tool=None,
						box_tool=None, box_through_tool=None, node_box_tool=None,
						circle_tool=None, gp_circle_tool=None,
						shortestpath_tool=None, shortestring_tool=None,
						loop_tool=None, ring_tool=None,
						loop_multiselect_tool=None, ring_multiselect_tool=None,
						more_tool=None, less_tool=None,
						next_tool=None, previous_tool=None, 
						linked_tool=None, linked_pick_tool=None,
						invert_tool=None, inner_tool=None,
						collection_tool=None):

		# Select / Deselect / Add
		if select_tool:
			if self.km.name in ['Node Editor']:
				value = 'PRESS'
			else:
				value = 'CLICK'
			self.kmi_set_active(False ,select_tool, self.k_select, ctrl=False, shift=False)
			self.kmi_set_replace(select_tool, self.k_select, value, properties={'deselect_all': True, 'deselect': False, 'extend': False, 'center':False, 'toggle': False, 'object': False}, disable_double=True)
			self.kmi_set_active(False ,select_tool, self.k_select, ctrl=False, shift=True)
			self.kmi_set_replace(select_tool, self.k_select, value, shift=True, properties={'deselect_all': False, 'deselect': False, 'extend': True, 'center':False, 'toggle': False, 'object': False}, disable_double=True)
			self.kmi_set_active(False ,select_tool, self.k_select, ctrl=True, shift=False)
			self.kmi_set_replace(select_tool, self.k_select, value, ctrl=True, properties={'deselect_all': False, 'deselect': True, 'extend': False, 'center':False, 'toggle': False, 'object': False}, disable_double=True)
		
		# Lasso Select / Deselect / Add
		if lasso_tool:
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'CLICK_DRAG', properties={'mode': 'SET'}, disable_double=True)
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'CLICK_DRAG', shift=True, properties={'mode': 'ADD'}, disable_double=True)
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'CLICK_DRAG', ctrl=True, properties={'mode': 'SUB'}, disable_double=True)

		# Lasso through Select / Deselect / Add
		if select_through_tool:
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'CLICK_DRAG', properties={'type': 'LASSO', 'mode': 'SET'}, disable_double=True)
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'CLICK_DRAG', shift=True, properties={'type': 'LASSO', 'mode': 'ADD'}, disable_double=True)
			self.kmi_set_replace(select_through_tool, self.k_lasso_through, 'CLICK_DRAG', ctrl=True, properties={'type': 'LASSO', 'mode': 'SUB'}, disable_double=True)
		
		# Box Select / Deselect / Add
		if box_tool:
			self.kmi_set_replace(box_tool, self.k_box, 'CLICK_DRAG', properties={'mode': 'SET', 'wait_for_input': False, 'tweak': False}, disable_double=True)
			self.kmi_set_replace(box_tool, self.k_box, 'CLICK_DRAG', shift=True, properties={'mode': 'ADD', 'wait_for_input': False, 'tweak': False}, disable_double=True)
			self.kmi_set_replace(box_tool, self.k_box, 'CLICK_DRAG', ctrl=True, properties={'mode': 'SUB', 'wait_for_input': False, 'tweak': False}, disable_double=True)
		
		if node_box_tool:
			self.kmi_set_replace(node_box_tool, self.k_select, 'CLICK_DRAG', properties={'mode': 'SET', 'wait_for_input': False, 'tweak': True}, disable_double=True)
			self.kmi_set_replace(node_box_tool, self.k_box, 'CLICK_DRAG', shift=True, properties={'mode': 'ADD', 'wait_for_input': False, 'tweak': False}, disable_double=True)
			self.kmi_set_replace(node_box_tool, self.k_box, 'CLICK_DRAG', ctrl=True, properties={'mode': 'SUB', 'wait_for_input': False, 'tweak': False}, disable_double=True)

		# Box Through Select / Deselect / Add
		if box_through_tool:
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'CLICK_DRAG', properties={'type': 'BOX', 'mode': 'SET'}, disable_double=True)
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'CLICK_DRAG', shift=True, properties={'type': 'BOX', 'mode': 'ADD'}, disable_double=True)
			self.kmi_set_replace(box_through_tool, self.k_box_through, 'CLICK_DRAG', ctrl=True, properties={'type': 'BOX', 'mode': 'SUB'}, disable_double=True)
		
		# Circle
		if circle_tool:
			if self.km.name in ['Weight Paint', 'Vertex Paint', 'Image Paint', 'Grease Pencil Stroke Weight Mode', 'Grease Pencil Stroke Sculpt Mode', 'Paint Face Mask (Weight, Vertex, Texture)', 'Grease Pencil Stroke Paint Mode', 'Grease Pencil Stroke Vertex Mode']:
				self.kmi_set_replace(circle_tool, self.k_cursor, 'CLICK_DRAG', shift=True, properties={'wait_for_input': False, 'mode': 'ADD', 'radius': 5}, disable_double=True)
				self.kmi_set_replace(circle_tool, self.k_cursor, 'CLICK_DRAG', ctrl=True, properties={ 'wait_for_input': False, 'mode': 'SUB', 'radius': 5}, disable_double=True)

			else:
				self.kmi_set_replace(circle_tool, self.k_select, 'CLICK_DRAG', shift=True, properties={'wait_for_input': False, 'mode': 'ADD', 'radius': 5}, disable_double=True)
				self.kmi_set_replace(circle_tool, self.k_select, 'CLICK_DRAG', ctrl=True, properties={'wait_for_input': False, 'mode': 'SUB', 'radius': 5}, disable_double=True)

		if gp_circle_tool:
			self.kmi_set_replace(gp_circle_tool, self.k_select, 'CLICK_DRAG', shift=True, properties={'wait_for_input': False, 'mode': 'ADD', 'radius': 5}, disable_double=True)
			self.kmi_set_replace(gp_circle_tool, self.k_select, 'CLICK_DRAG', ctrl=True, properties={'wait_for_input': False, 'mode': 'SUB', 'radius': 5}, disable_double=True)

		#  shortest Path Select / Deselect / Add
		if shortestpath_tool:
			self.kmi_remove(idname=shortestpath_tool)
			self.kmi_set_replace(shortestpath_tool, self.k_context, 'CLICK', shift=True, disable_double=True, properties={'use_fill': False, 'use_face_step': False, 'use_topology_distance': False})
			self.kmi_set_replace(shortestpath_tool, self.k_context, 'CLICK', ctrl=True, shift=True, disable_double=True, properties={'use_fill': True, 'use_face_step': False, 'use_topology_distance': False})

		#  shortest ring
		if shortestring_tool:
			self.kmi_set_replace(shortestring_tool, self.k_cursor, 'CLICK', shift=True, disable_double=True, properties={'use_fill': False, 'use_face_step': True, 'use_topology_distance': False})

		# Loop Select / Deselect / Add
		if loop_tool:
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', disable_double=True, properties={'extend': False, 'deselect': False})
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', shift=True, properties={'extend': True, 'ring': False, 'deselect': False}, disable_double=True)
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', ctrl=True, properties={'extend': False, 'deselect': True}, disable_double=True)

		# Ring Select / Deselect / Add
		if ring_tool:
			self.kmi_set_replace(ring_tool, self.k_cursor, 'CLICK', ctrl=True, properties={'ring': True, 'deselect': True, 'extend': False, 'toggle': False}, disable_double=True)
			self.kmi_set_replace(ring_tool, self.k_cursor, 'CLICK', ctrl=True, shift=True, properties={'ring': True, 'deselect': False, 'extend': True, 'toggle': False}, disable_double=True)

		# Loop multiselect
		if loop_multiselect_tool:
			self.kmi_set_replace(loop_multiselect_tool, 'L', 'PRESS', properties={'ring': False}, disable_double=True)
		
		# Ring multiselect
		if ring_multiselect_tool:
			self.kmi_set_replace(ring_multiselect_tool, 'L', 'PRESS', alt=True, properties={'ring': True}, disable_double=True)

		# Select More / Less
		if more_tool:
			self.kmi_set_replace(more_tool, self.k_more, 'PRESS', shift=True, repeat=True)

		if less_tool:
			self.kmi_set_replace(less_tool, self.k_less, 'PRESS', shift=True, repeat=True)
		
		# Select Next / Previous
		if next_tool:
			self.kmi_set_replace(next_tool, self.k_more, 'PRESS')

		if previous_tool:
			self.kmi_set_replace(previous_tool, self.k_less, 'PRESS')

		# Linked
		if linked_tool:
			self.kmi_set_replace(linked_tool, self.k_linked, 'DOUBLE_CLICK', ctrl=False, properties={'deselect': False, 'delimit': {'SEAM'}})
		
		if linked_pick_tool:
			if self.km.name in ['Curve', 'Lattice', 'Grease Pencil', 'Particle', 'UV Editor']:
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=False, properties={'deselect': False, 'extend': True}, disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, properties={'deselect': True, 'extend': True}, disable_double=True)
			elif self.km.name in ['Weight Paint', 'Vertex Paint', 'Image Paint', 'Paint Face Mask (Weight, Vertex, Texture)', 'Grease Pencil Stroke Weight Mode', 'Grease Pencil Stroke Sculpt Mode', 'Grease Pencil Stroke Paint Mode']:
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=False, alt=False, shift=False, properties={'deselect': False},  disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, alt=False, shift=False, properties={'deselect': True},  disable_double=True)
			else:
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=False, alt=False, shift=False, properties={'deselect': False, 'delimit': {'SEAM'}}, disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, properties={'deselect': True, 'delimit': {'SEAM'}}, disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', shift=True, properties={'deselect': False, 'delimit': {'MATERIAL'}}, disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, shift=True, properties={'deselect': True, 'delimit': {'MATERIAL'}}, disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', alt=True, properties={'deselect': False, 'delimit': {'UV'}}, disable_double=True)
				self.kmi_set_replace(linked_pick_tool, self.k_linked, 'PRESS', ctrl=True, alt=True, properties={'deselect': True, 'delimit': {'UV'}}, disable_double=True)

		if invert_tool:
			self.kmi_set_replace(invert_tool, self.k_context, 'CLICK', ctrl=True, alt=True, shift=True, properties={'action': 'INVERT'})

		if inner_tool:
			self.kmi_set_replace(inner_tool, self.k_select, 'CLICK', ctrl=True, alt=True, shift=True, disable_double=True)

		if collection_tool:
			self.kmi_set_replace(collection_tool, self.k_select, 'DOUBLE_CLICK', shift=False, properties={'type': 'COLLECTION', 'extend': False}, disable_double=True)
			self.kmi_set_replace(collection_tool, self.k_select, 'DOUBLE_CLICK', shift=True, properties={'type': 'COLLECTION', 'extend': True}, disable_double=True)

	def selection_tool(self, tool='builtin.select', alt='builtin.select_box'):
		# select_tool = self.kmi_find(idname='wm.tool_set_by_id', properties=KeymapManager.bProp([('name', 'builtin.select_box'}))
		# if select_tool:
		# 	self.kmi_prop_setattr(select_tool.properties, "name", 'Select')
		# 	self.kmi_prop_setattr(select_tool.properties, "cycle", False)
		if self.km.name in ['Sculpt', 'Sculpt Curves']:
			if self.km.name == 'Sculpt':
				toolname = 'sculpt_tool'
			elif self.km.name == 'Sculpt Curves':
				toolname = 'curves_sculpt_tool'

			self.kmi_set_replace('paint.brush_select', self.k_menu, 'PRESS', properties={toolname: tool, 'toggle': True}, disable_double=True)
			if alt:
				self.kmi_set_replace('paint.brush_select', self.k_manip, 'PRESS', ctrl=True, shift=True, properties={toolname: alt, 'toggle': True})
		else:
			self.kmi_set_replace('wm.tool_set_by_id', self.k_menu, "PRESS", properties={'name': tool, 'cycle': False})
			if alt:
				self.kmi_set_replace('wm.tool_set_by_id', self.k_menu, "PRESS", ctrl=True, properties={'name': alt, 'cycle': False})

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
			self.kmi_set_replace(duplicate, 'D', 'PRESS', ctrl=True, shift=False, properties=duplicate_prop, disable_double=True)
		if duplicate_link:
			self.kmi_set_replace(duplicate_link, 'D', 'PRESS', ctrl=True, shift=True, properties=duplicate_link_prop, disable_double=True)

	def hide_reveal(self, hide=None, unhide=None, inverse=None):
		if hide:
			self.kmi_set_replace(hide, 'H', 'PRESS', properties={'unselected': False})
			self.kmi_set_replace(hide, 'H', 'PRESS', ctrl=True, properties={'unselected': True})
		if unhide:
			self.kmi_set_replace(unhide, 'H', 'PRESS', alt=True, shift=True, properties={'select': False})
		if inverse:
			self.kmi_set_replace(inverse, 'H', 'PRESS', ctrl=True, alt=True, shift=True)

	def snap(self, snapping=None, snapping_prop=None):
		type = 'X'
		self.kmi_set_replace('wm.context_toggle', type, 'PRESS', properties={'data_path': 'tool_settings.use_snap'})
		if snapping is not None and snapping_prop is not None:
			self.kmi_set_replace(snapping, type, 'PRESS', ctrl=True, shift=True, properties=snapping_prop)
		self.kmi_set_replace('view3d.toggle_snapping', type, 'PRESS', shift=True)

	def tool_sculpt(self, sculpt=None):
		if sculpt:
			self.kmi_set_replace(sculpt, 'W', 'PRESS', ctrl=True, alt=True, shift=True)

	def tool_smooth(self):
		self.kmi_set_replace('mesh.vertices_smooth', 'S', 'PRESS', ctrl=True, alt=True, shift=False, properties={'repeat': 50})
	
	def tool_proportional(self):
		self.modal_set_replace('PROPORTIONAL_SIZE', 'MOUSEMOVE', 'ANY', alt=True)
	
	def tool_smart_delete(self):
		self.kmi_set_active(False, type='DEL')
		self.kmi_set_replace('object.tila_smartdelete', 'DEL', 'PRESS', properties={'menu': False}, disable_double=True)
		self.kmi_set_replace('object.tila_smartdelete', 'DEL', 'PRESS', alt=True, properties={'menu': True}, disable_double=True)

	def tool_radial_control(self, radius=None, opacity=None, eraser_radius=None, fill_color=None):
		type = 'Q'
		if radius:
			self.kmi_set_replace('wm.radial_control', type, 'ANY', properties=radius, disable_double=True)
		if opacity:
			self.kmi_set_replace('wm.radial_control', type, 'ANY', alt=True, shift=True, properties=opacity, disable_double=True)
		if eraser_radius:
			self.kmi_set_replace('wm.radial_control', type, 'ANY', ctrl=True, alt=True, properties=eraser_radius, disable_double=True)
		if fill_color:
			self.kmi_set_replace('wm.radial_control', self.k_lasso, 'ANY', properties=fill_color, disable_double=True)

	def tool_sample_color(self, tool):
		if tool:
			self.kmi_set_replace(tool, 'C', 'PRESS', disable_double=True)

	def tool_subdivision(self):
		#  Disabling subdivision_set shortcut
		self.kmi_set_active(False, 'object.subdivision_set', type='ZERO')
		self.kmi_set_active(False, 'object.subdivision_set', type='ONE')
		self.kmi_set_active(False, 'object.subdivision_set', type='TWO')
		self.kmi_set_active(False, 'object.subdivision_set', type='THREE')
		self.kmi_set_active(False, 'object.subdivision_set', type='FOUR')
		self.kmi_set_active(False, 'object.subdivision_set', type='FIVE')

		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_PLUS', 'PRESS', properties={'subd': 1, 'mode': 'RELATIVE', 'force_subd': False, 'algorithm': 'CATMULL_CLARK'}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_PLUS', 'PRESS', shift=True, properties={'subd': 1, 'mode': 'RELATIVE', 'force_subd': True, 'algorithm': 'CATMULL_CLARK'}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_PLUS', 'PRESS', ctrl=True, properties={'subd': 1, 'mode': 'RELATIVE', 'force_subd': False, 'algorithm': 'LINEAR'}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_PLUS', 'PRESS', ctrl=True, shift=True, properties={'subd': 1, 'mode': 'RELATIVE', 'force_subd': True, 'algorithm': 'LINEAR'}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_PLUS', 'PRESS', ctrl=False, alt=True, shift=True, properties={'mode': 'MAX', 'force_subd': False}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_delete_subdiv', 'NUMPAD_PLUS', 'PRESS', ctrl=True, alt=True, shift=True, properties={'delete_target': 'HIGHER'}, disable_double=True)
		

		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_MINUS', 'PRESS', properties={'subd': -1, 'mode': 'RELATIVE', 'force_subd': False, 'algorithm': 'CATMULL_CLARK'}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_MINUS', 'PRESS', shift=True, properties={'subd': -1, 'mode': 'RELATIVE', 'force_subd': True, 'algorithm': 'CATMULL_CLARK'}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_MINUS', 'PRESS', ctrl=True, properties={'subd': -1, 'mode': 'RELATIVE', 'force_subd': False, 'algorithm': 'LINEAR'}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_MINUS', 'PRESS', ctrl=True, shift=True, properties={'subd': -1, 'mode': 'RELATIVE', 'force_subd': True, 'algorithm': 'LINEAR'}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'NUMPAD_MINUS', 'PRESS', ctrl=False, alt=True, shift=True, properties={'mode': 'MIN', 'force_subd': False}, disable_double=True)
		self.kmi_set_replace('sculpt.tila_multires_delete_subdiv', 'NUMPAD_MINUS', 'PRESS', ctrl=True, alt=True, shift=True, properties={'delete_target': 'LOWER'}, disable_double=True)

		self.kmi_set_replace('sculpt.tila_multires_rebuild_subdiv', 'NUMPAD_ASTERIX', 'PRESS', ctrl=True, alt=True, shift=True)
		self.kmi_set_replace('sculpt.tila_multires_apply_base', 'NUMPAD_ENTER', 'PRESS', ctrl=True, alt=True, shift=True)

		self.kmi_set_replace('object.subdivision_set', 'NUMPAD_PLUS', 'PRESS', alt=True, properties={'level': 1, 'relative': True}, disable_double=True)
		self.kmi_set_replace('object.subdivision_set', 'NUMPAD_MINUS', 'PRESS', alt=True, properties={'level': -1, 'relative': True}, disable_double=True)

		if self.km.name in ['Sculpt']:
			self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'D', 'PRESS', properties={'subd': 1, 'mode': 'RELATIVE', 'force_subd': False, 'algorithm': 'CATMULL_CLARK'})
			self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'D', 'PRESS', ctrl=True,  properties={'subd': 1, 'mode': 'RELATIVE', 'force_subd': True, 'algorithm': 'CATMULL_CLARK'})
			self.kmi_set_replace('sculpt.tila_multires_subdiv_level', 'D', 'PRESS', shift=True,  properties={'subd': -1, 'mode': 'RELATIVE', 'force_subd': False, 'algorithm': 'CATMULL_CLARK'})
		
	def tool_center(self, pivot=None, orientation=None, action_center_context=None):
		print(pivot, orientation)
		# if pivot:
		# 	if self.km.name in ['Uv Editor']:
		# 		self.kmi_set_replace('wm.context_menu_enum', 'X', 'PRESS', ctrl=True, properties={'name', pivot), ('keep_open', False}, disable_double=True)
		# 	else:
		# 		self.kmi_set_replace('wm.call_panel', 'X', 'PRESS', ctrl=True, properties={'name', pivot), ('keep_open', False}, disable_double=True)
		if orientation:
			self.kmi_set_replace('wm.call_panel', 'X', 'PRESS', ctrl=True, shift=True, properties={'name': orientation, 'keep_open': False}, disable_double=True)
		if action_center_context:
			self.kmi_set_replace('wm.call_menu', 'X', 'PRESS', alt=True, properties={'name': 'TILA_MT_action_center'}, disable_double=True)
	
	def tool_transform(self, cage_scale=None):
		self.kmi_set_replace('wm.tool_set_by_id', self.k_move, 'PRESS', properties={'name': 'builtin.move'}, disable_double=True)
		self.kmi_set_replace('wm.tool_set_by_id', self.k_rotate, 'PRESS', properties={'name': 'builtin.rotate'}, disable_double=True)
		self.kmi_set_replace('wm.tool_set_by_id', self.k_scale, 'PRESS', properties={'name': 'builtin.scale'}, disable_double=True)
		if cage_scale:
			self.kmi_set_replace('wm.tool_set_by_id', 'T', 'PRESS', ctrl=True, properties={'name': cage_scale}, disable_double=True)

	def isolate(self):
		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, properties={'force_object_isolate': False})
		self.kmi_set_replace('view3d.tila_isolate', 'X', 'PRESS', ctrl=True, alt=True, shift=True, properties={'force_object_isolate': True})
	
	def join(self):
		self.kmi_set_replace('object.tila_smart_join', 'J', 'PRESS', ctrl=True, shift=False, alt=False, properties={'apply_modifiers': False, 'duplicate': False}, disable_double=True)
		self.kmi_set_replace('object.tila_smart_join', 'J', 'PRESS', ctrl=True, shift=True, alt=False, properties={'apply_modifiers': True, 'duplicate': False}, disable_double=True)
		self.kmi_set_replace('object.tila_smart_join', 'J', 'PRESS', ctrl=True, shift=True, alt=True, properties={'apply_modifiers': True, 'duplicate': True}, disable_double=True)

	# Keymap define
	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		##### Window
		self.kmi_init(name='Window', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		# self.kmi_set_replace("wm.call_menu_pie", self.k_menu, "PRESS", ctrl=True, shift=True, alt=True)
		# self.kmi_set_replace("wm.revert_without_prompt", "N", "PRESS", shift=True)
		
		self.kmi_set_active(False, idname='wm.call_menu', type='F2')
		self.kmi_set_active(False, idname='wm.toolbar')
		self.selection_tool(tool='builtin.select_box')
		
		self.kmi_init(name='Window', space_type='EMPTY', region_type='WINDOW', addon=False)
		self.kmi_set_active(False, 'wm.save_as_mainfile', type='S', value='PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('import_scene.tila_universal_multi_importer', 'I', 'PRESS', ctrl=True, alt=False, shift=False)

		# MACHINE3tools
		# self.kmi_set_replace('wm.call_menu_pie', 'S', "PRESS", ctrl=True, shift=True, properties={'name': 'MACHIN3_MT_save_pie'}, disable_double=True)
		
		# Atomic Data Manager
		# self.kmi_set_replace('atomic.invoke_pie_menu_ui', 'DEL', "PRESS", ctrl=True, shift=True, disable_double=True)
		

		##### 3D View
		self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool()
		self.tool_smart_delete()
		self.kmi_set_active(False, idname='view3d.select_circle', type="C")
		self.kmi_set_active(False, idname='view3d.cursor3d', type="RIGHTMOUSE")
		self.kmi_set_active(False, idname='view3d.rotate', type="MIDDLEMOUSE")
		self.kmi_set_active(False, idname='view3d.dolly', type="MIDDLEMOUSE")
		self.kmi_set_active(False, idname='wm.tool_set_by_id', type="W")
		self.kmi_set_replace('view3d.navigate', 'NUMPAD_SLASH', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)

		self.navigation_keys(pan='view3d.move',
							orbit='view3d.rotate',
							dolly='view3d.zoom',
					   		roll='view3d.rotate_canvas')

		self.selection_keys(select_tool='view3d.select', 
							lasso_tool='view3d.select_lasso',
							select_through_tool='view3d.tila_select_through',
					  		circle_tool='view3d.select_circle',
							collection_tool='object.select_grouped')

		# self.kmi_set_active(False, idname='view3d.select', shift=True)

		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)
		self.snap(snapping='wm.call_panel', snapping_prop={'name': 'VIEW3D_PT_snapping'})

		self.mode_selection()
		
		self.kmi_set_replace('view3d.toggle_symetry', 'X', 'PRESS', disable_double=True)
		# self.kmi_set_replace('wm.context_toggle', 'X', 'PRESS', alt=True, shift=True, properties={'data_path': 'tool_settings.use_snap'}, disable_double=True)

		self.kmi_set_replace('view3d.view_persportho', 'NUMPAD_ASTERIX', 'PRESS')
		self.kmi_set_replace('view3d.collection_manager', 'M', 'PRESS',  ctrl=True, alt=True, shift=True, disable_double=True)

		self.collection_visibility('object.hide_collection')

		self.kmi_set_replace('view3d.view_selected', 'A', 'PRESS', ctrl=True, shift=True)

		self.tool_center(pivot='VIEW3D_PT_pivot_point', orientation='VIEW3D_PT_transform_orientations', action_center_context='VIEW3D')

		self.kmi_set_replace('wm.call_menu_pie', 'Q', 'PRESS', ctrl=True, alt=True, shift=True, properties={'name': 'HP_MT_pie_boolean'})
		self.kmi_set_replace('view3d.toggle_wireframe', 'F5', 'PRESS', properties={'mode': 'OVERLAY', 'selected': False}, disable_double=True)
		self.kmi_set_replace('view3d.toggle_wireframe', 'F5', 'PRESS', shift=True, properties={'mode': 'OVERLAY', 'selected': True}, disable_double=True)
		self.kmi_set_replace('view3d.toggle_wireframe', 'F5', 'PRESS', ctrl=True, properties={'mode': 'SET', 'selected': False}, disable_double=True)
		self.kmi_set_replace('view3d.toggle_wireframe', 'F5', 'PRESS', ctrl=True, shift=True, properties={'mode': 'SET', 'selected': True}, disable_double=True)
		self.kmi_set_replace('view3d.toggle_wireframe', 'F5', 'PRESS', ctrl=True, alt=True, shift=True, properties={'mode': 'RETOPO', 'selected': False}, disable_double=True)

		self.kmi_set_replace('wm.call_menu_pie', 'F', 'PRESS', alt=True, shift=True, properties={'name': 'UVTOOLKIT_MT_pie_3dview'})
		
		self.kmi_set_active(False, 'wm.call_menu_pie', type='Z')
		self.kmi_set_replace('wm.call_menu_pie', 'Z', 'PRESS', properties={'name':'TILA_MT_pie_render_mode'}, disable_double=True)

		self.kmi_set_replace('object.transfer_mode', self.k_cursor, 'CLICK', alt=True, disable_double=True)

		self.kmi_set_replace('view3d.tila_orthographic_navigation', self.k_cursor, 'CLICK_DRAG', ctrl=False, alt=True, shift=False, disable_double=True, properties={'relative_to_selected_element': False})
		self.kmi_set_replace('view3d.tila_orthographic_navigation', self.k_cursor, 'CLICK_DRAG', ctrl=False, alt=True, shift=True, disable_double=True, properties={'relative_to_selected_element': True})

		self.kmi_set_replace('view3d.tila_action_center_3d_cursor_toggle', 'S', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)
		self.kmi_set_replace('view3d.toggle_overlay', 'F6', 'PRESS', properties={'mode': 'SOFT'})
		self.kmi_set_replace('view3d.toggle_overlay', 'F6', 'PRESS', ctrl=True, properties={'mode': 'TOGGLE'})

		self.kmi_set_active(enable=False, idname='view3d.view_axis', type=self.k_cursor, value='CLICK_DRAG',  alt=True, direction='NORTH')
		self.kmi_set_active(enable=False, idname='view3d.view_axis', type=self.k_cursor, value='CLICK_DRAG',  alt=True, direction='EAST')
		self.kmi_set_active(enable=False, idname='view3d.view_axis', type=self.k_cursor, value='CLICK_DRAG',  alt=True, direction='SOUTH')
		self.kmi_set_active(enable=False, idname='view3d.view_axis', type=self.k_cursor, value='CLICK_DRAG',  alt=True, direction='WEST')

		# kekit
		# self.kmi_set_replace('view3d.ke_get_set_material', 'M', 'PRESS', shift=True)

		# # MouseLook_Navigation
		# self.kmi_set_replace('mouselook_navigation.navigate', self.k_cursor, 'CLICK_DRAG', ctrl=False, alt=True, shift=False,  disable_double=True)

		# Rotate an HDRI
		# self.kmi_set_replace('rotate.hdri', self.k_context, 'PRESS', ctrl=True, alt=True, shift=False,  disable_double=True)
		# self.kmi_set_active(enable=True, idname='rotate.hdri')
		
		# GreasePencil tools
		# self.kmi_set_replace('view3d.rotate_canvas', self.k_context, 'PRESS', alt=True, disable_double=True)

		# Polysource
		# self.kmi_set_active(enable=False, idname='wm.call_menu_pie', type=self.k_menu, value='PRESS', properties={'name': 'PS_MT_tk_menu'})

        ##### View3D Walk Modal
		self.kmi_init(name='View3D Walk Modal', space_type='VIEW_3D', region_type='WINDOW', modal=True)
		self.kmi_set_active(False, propvalue='FORWARD')
		self.kmi_set_active(False, propvalue='FORWARD_STOP')
		self.kmi_set_active(False, propvalue='LEFT')
		self.kmi_set_active(False, propvalue='LEFT_STOP')
		self.kmi_set_active(False, propvalue='DOWN')
		self.kmi_set_active(False, propvalue='DOWN_STOP')
		self.kmi_set_active(False, propvalue='SLOW_ENABLE')
		self.kmi_set_active(False, propvalue='SLOW_DISABLE')
		self.modal_set_replace('FORWARD', 'Z', 'PRESS', disable_double=True)
		self.modal_set_replace('FORWARD_STOP', 'Z', 'RELEASE', disable_double=True)
		self.modal_set_replace('LEFT', 'Q', 'PRESS', disable_double=True)
		self.modal_set_replace('LEFT_STOP', 'Q', 'RELEASE', disable_double=True)
		self.modal_set_replace('DOWN', 'A', 'PRESS', disable_double=True)
		self.modal_set_replace('DOWN_STOP', 'A', 'RELEASE', disable_double=True)
		self.modal_set_replace('SLOW_ENABLE', 'LEFT_CTRL', 'PRESS', disable_double=True)
		self.modal_set_replace('SLOW_DISABLE', 'LEFT_CTRL', 'RELEASE', disable_double=True)
		self.modal_set_replace('AXIS_LOCK_Z', 'W', 'PRESS', disable_double=True)

		##### 3D View Generic
		self.kmi_init(name='3D View Generic', space_type='VIEW_3D', region_type='WINDOW')

		###### 3d Cursor
		self.kmi_set_replace('view3d.cursor3d', self.k_cursor, 'CLICK', ctrl=True, alt=True, shift=True, properties={'use_depth': True, 'orientation': 'GEOM'}, disable_double=True)
		self.kmi_set_replace('transform.translate', self.k_cursor, 'CLICK_DRAG', ctrl=True, alt=True, shift=True, properties={'cursor_transform': True, 'release_confirm': True, 'orient_type': 'NORMAL', 'snap': True, 'snap_align': True})

		###### View2D
		self.kmi_init(name='View2D', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')

		###### View2D buttons List
		self.kmi_init(name='View2D Buttons List', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')

		###### Image
		self.kmi_init(name='Image', space_type='IMAGE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_active(False, 'image.view_pan', self.k_cursor, 'PRESS', shift=True)
		self.navigation_keys(pan='image.view_pan', orbit=None, dolly='image.view_zoom')
		

		###### UV Editor
		self.kmi_init(name='UV Editor', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool()
		self.tool_transform(cage_scale='builtin.transform')
		self.selection_keys(select_tool='uv.select',
					  		lasso_tool='uv.select_lasso',
							box_through_tool='uv.select_box',
					  		circle_tool='uv.select_circle',
					  		loop_tool='uv.select_loop',
					  		more_tool='uv.select_more',
					  		less_tool='uv.select_less',
							shortestpath_tool='uv.shortest_path_pick',
					  		linked_tool='uv.select_linked',
							linked_pick_tool='uv.select_linked_pick',
							invert_tool='uv.select_all')
		
		self.kmi_set_replace('image.view_selected', 'A', 'PRESS', ctrl=True, shift=True, disable_double=True)
		self.kmi_set_replace('uv.cursor_set', self.k_cursor, 'PRESS', ctrl=True, alt=True, shift=True)
		self.tool_smooth()
		self.hide_reveal(hide='uv.hide', unhide='uv.reveal')
		self.snap(snapping='wm.context_menu_enum', snapping_prop={'data_path': 'tool_settings.snap_uv_element'})
		self.tool_center(pivot='space_data.pivot_point', orientation='IMAGE_PT_snapping')

		self.kmi_set_replace('wm.tool_set_by_id', 'W', 'PRESS', ctrl=True, alt=True, shift=True, properties={'name': 'builtin_brush.Grab'})
		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.uv_sculpt.brush.size', 
								'data_path_secondary': 'tool_settings.unified_paint_settings.size', 
								'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size', 
								'rotation_path': 'tool_settings.uv_sculpt.brush.texture_slot.angle', 
								'color_path': 'tool_settings.uv_sculpt.brush.cursor_color_add', 
								'image_id': 'tool_settings.uv_sculpt.brush',
								'release_confirm': True},
						   		opacity={'data_path_primary': 'tool_settings.uv_sculpt.brush.strength', 
								   'data_path_secondary': 'tool_settings.unified_paint_settings.strength', 
								   'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength', 
								   'rotation_path': 'tool_settings.uv_sculpt.brush.texture_slot.angle', 
								   'color_path': 'tool_settings.uv_sculpt.brush.cursor_color_add', 
								   'image_id': 'tool_settings.uv_sculpt.brush',
									'release_confirm': True},
						   		eraser_radius={'data_path_primary': 'tool_settings.uv_sculpt.brush.texture_slot.angle', 
								   'rotation_path': 'tool_settings.uv_sculpt.brush.texture_slot.angle', 
								   'color_path': 'tool_settings.uv_sculpt.brush.cursor_color_add', 
								   'image_id': 'tool_settings.uv_sculpt.brush',
									'release_confirm': True})


		self.kmi_set_replace('uv.minimize_stretch', 'R', 'PRESS', ctrl=True, disable_double=True, properties={'iterations': 10})
		self.kmi_set_replace('wm.call_menu_pie', 'F', 'PRESS', alt=True, shift=True, properties={'name': 'UVTOOLKIT_MT_pie_uv_editor'})

		self.kmi_set_replace('uv.stitch', 'V', 'PRESS',  disable_double=True)
		self.kmi_set_replace('uv.select_split', 'V', 'PRESS', shift=True, disable_double=True)
		self.kmi_set_replace('uv.uv_face_rip', 'V', 'PRESS', ctrl=True, disable_double=True)


		self.kmi_set_replace('uv.toolkit_straighten', 'G', 'PRESS', ctrl=True, disable_double=True, properties={'gridify': False})
		self.kmi_set_replace('uv.toolkit_unwrap_selected', 'E', 'PRESS', ctrl=True, disable_double=True, properties={'gridify': False, 'method': 'ANGLE_BASED'})
		kmi = self.kmi_find('uv.toolkit_distribute')
		if kmi is not None:
			kmi.active = False
		self.kmi_set_replace('uv.toolkit_distribute', 'D', 'PRESS', disable_double=True, properties={'preserve_edge_length': True})
		self.kmi_set_replace('uvpackmaster3.pack', 'P', 'PRESS', ctrl=True, disable_double=True)

		# bpy.ops.transform.translate(value=(-1, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)


		self.kmi_set_replace('transform.translate', 'UP_ARROW', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True, properties={'value': (0.0,1.0,0.0), 'release_confirm': True, 'orient_matrix': ((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'orient_matrix_type': 'GLOBAL'})
		self.kmi_set_replace('transform.translate', 'DOWN_ARROW', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True, properties={'value': (0.0,-1.0,0.0), 'release_confirm': True, 'orient_matrix': ((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'orient_matrix_type': 'GLOBAL'})
		self.kmi_set_replace('transform.translate', 'LEFT_ARROW', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True, properties={'value': (-1.0,0.0,0.0), 'release_confirm': True, 'orient_matrix': ((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'orient_matrix_type': 'GLOBAL'})
		self.kmi_set_replace('transform.translate', 'RIGHT_ARROW', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True, properties={'value': (1.0,0.0,0.0), 'release_confirm': True, 'orient_matrix': ((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'orient_matrix_type': 'GLOBAL'})

		self.kmi_set_replace('uv.toolkit_align_uv', 'UP_ARROW', 'PRESS', ctrl=True, alt=False, shift=False, disable_double=True, properties={'align_uv': 'MAX_V'})
		self.kmi_set_replace('uv.toolkit_align_uv', 'DOWN_ARROW', 'PRESS', ctrl=True, alt=False, shift=False, disable_double=True, properties={'align_uv': 'MIN_V'})
		self.kmi_set_replace('uv.toolkit_align_uv', 'LEFT_ARROW', 'PRESS', ctrl=True, alt=False, shift=False, disable_double=True, properties={'align_uv': 'MIN_U'})
		self.kmi_set_replace('uv.toolkit_align_uv', 'RIGHT_ARROW', 'PRESS', ctrl=True, alt=False, shift=False, disable_double=True, properties={'align_uv': 'MAX_U'})
		self.kmi_set_replace('wm.call_menu_pie', 'X', 'PRESS', alt=True, disable_double=True, properties={'name': 'IMAGE_MT_pivot_pie'})

		self.kmi_set_replace('view2d.tila_action_center_2d_cursor_toggle', 'S', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)

		# Machin3Tools
		# self.kmi_set_replace('wm.call_menu_pie', 'D', "PRESS", alt=True, shift=True, properties={'name': 'MACHIN3_MT_uv_align_pie'}, disable_double=True)

		# UV Toolkit
		# self.kmi_set_replace('uv.toolkit_orient_to_edge', 'D', "PRESS", ctrl=True, alt=True, shift=True, disable_double=True)
		

		###### Mesh
		self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.mode_selection()
		self.tool_transform(cage_scale='builtin.scale_cage')

		self.kmi_set_replace('wm.call_menu_pie', 'X', 'PRESS', alt=True, shift=True, properties={'name': 'HP_MT_pie_symmetry'}, disable_double=False)
		self.kmi_set_replace('wm.call_menu_pie', 'Q', 'PRESS', alt=True, shift=True, properties={'name': 'TILA_MT_pie_distribute'}, disable_double=True)

		self.selection_keys(shortestpath_tool='mesh.shortest_path_pick',
							shortestring_tool='mesh.shortest_path_pick',
							loop_tool='view3d.tila_smart_loopselect',
					  		ring_tool='mesh.edgering_select',
							loop_multiselect_tool='mesh.loop_multi_select',
							ring_multiselect_tool='mesh.loop_multi_select',
							more_tool='mesh.select_more',
							less_tool='mesh.select_less',
							next_tool='mesh.select_next_item',
							previous_tool='mesh.select_prev_item',
							linked_tool='mesh.select_linked',
							linked_pick_tool='mesh.select_linked_pick',
							invert_tool='mesh.select_all', inner_tool='mesh.loop_to_region')

		self.kmi_set_active(True, idname='mesh.select_linked_pick', type=self.k_linked)
		self.kmi_set_active(False, idname='object.switch_object')
		self.kmi_set_active(False, idname='ls.select', type=self.k_select, value='DOUBLE_CLICK')
		self.kmi_set_active(False, idname='ls.select', type=self.k_select, value='DOUBLE_CLICK', shift=False)

		self.duplicate(duplicate='mesh.duplicate_move')
		self.hide_reveal(hide='mesh.hide', unhide='mesh.reveal', inverse='view3d.inverse_visibility')
		self.tool_smart_delete()

		self.tool_smooth()
		self.kmi_set_active(False, 'view3d.select_box')
		self.kmi_set_replace('view3d.smart_bevel', 'B', 'PRESS', disable_double=True)
		self.kmi_set_replace('mesh.hp_extrude', 'E', 'PRESS', disable_double=True)
		self.kmi_set_replace('mesh.knife_tool', 'C', 'PRESS', disable_double=True)
		# self.kmi_set_replace('wm.tool_set_by_id', 'C', 'PRESS', alt=True, shift=True, properties={'name': 'builtin.loop_cut'})
		self.kmi_set_replace('mesh.bridge_edge_loops', 'B', 'PRESS', shift=True)
		self.kmi_set_replace('mesh.edge_collapse', 'DEL', 'PRESS', shift=True)
		self.kmi_set_replace('mesh.merge', 'DEL', 'PRESS', alt=True, shift=True, properties={'type': 'LAST'},  disable_double=True)
		self.kmi_set_replace('mesh.fill', 'P', 'PRESS', shift=True, properties={'use_beauty': True})
		self.kmi_set_replace('mesh.fill_grid', 'P', 'PRESS', alt=True, properties={'use_interp_simple': False})
		self.kmi_set_replace('mesh.edge_face_add', 'P', 'PRESS', disable_double=True)
		self.kmi_set_replace('mesh.flip_normals', 'F', 'PRESS', disable_double=True)
		self.kmi_set_replace('mesh.subdivide', 'D', 'PRESS', disable_double=True)
		self.kmi_set_replace('transform.shrink_fatten', 'E', 'PRESS', alt=True, shift=True, disable_double=True)
		self.kmi_set_replace('transform.edge_bevelweight', 'E', 'PRESS', ctrl=True, shift=True, disable_double=True)
		
		# self.kmi_set_replace('transform.vert_slide', 'S', 'PRESS', ctrl=True, alt=True, properties={'correct_uv': True})

		# self.kmi_set_replace('wm.tool_set_by_id', 'F', 'PRESS', shift=True, properties={'name': 'mesh_tool.poly_quilt'}, disable_double=True)

		self.kmi_set_replace('mesh.remove_doubles', 'M', 'PRESS', ctrl=True, shift=True, disable_double=True)
		self.kmi_set_replace('mesh.separate_and_select', 'D', 'PRESS', ctrl=True, shift=True, properties={'by_loose_parts': False})
		self.kmi_set_replace('mesh.separate_and_select', 'D', 'PRESS', ctrl=True, alt=True, shift=True, properties={'by_loose_parts': True})

		self.tool_subdivision()

		self.tool_sculpt('sculpt.sculptmode_toggle')
		
		self.tool_center(pivot='VIEW3D_PT_pivot_point', orientation='VIEW3D_PT_transform_orientations')

		self.isolate()
		self.join()

		self.kmi_set_replace('mesh.toggle_use_automerge', 'BACK_SLASH', 'PRESS')
		# self.kmi_set_replace('object.merge_tool', 'M', 'PRESS')
		self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', ctrl=False, alt=False, shift=True, properties={'name': 'VIEW3D_MT_snap_pie'}, disable_double=True)
		self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', alt=True, shift=True, properties={'name': 'TILA_MT_pie_normal'}, disable_double=True)
		# self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', ctrl=True, alt=True, shift=True, properties={'name', 'TILA_MT_pie_uv'}, disable_double=True)

		self.kmi_set_replace("mesh.edge_rotate", 'V', "PRESS", properties={'use_ccw': False}, disable_double=True)
		self.kmi_set_replace("mesh.edge_rotate", 'V', "PRESS", shift=True, properties={'use_ccw': True}, disable_double=True)

		self.kmi_set_replace('mesh.quads_convert_to_tris', 'T', "PRESS", shift=True, properties={'quad_method': 'BEAUTY', 'ngon_method': 'BEAUTY'}, disable_double=True)
		self.kmi_set_replace('mesh.tris_convert_to_quads', 'T', "PRESS", alt=True, shift=True)

		# KE_Kit
		# kmi = self.kmi_find(idname='wm.call_menu', type='C', ctrl=True)
		# if kmi is not None:
		# 	kmi.shift = True

		# kmi = self.kmi_find(idname='wm.call_menu', type='V', ctrl=True)
		# if kmi is not None:
		# 	kmi.shift = True

		# self.kmi_set_replace('view3d.ke_copyplus', 'C', "PRESS", ctrl=True, properties={'mode': 'COPY'}, disable_double=True)
		# self.kmi_set_replace('view3d.ke_copyplus', 'X', "PRESS", ctrl=True, properties={'mode': 'CUT'}, disable_double=True)
		# self.kmi_set_replace('view3d.ke_copyplus', 'V', "PRESS", ctrl=True, properties={'mode': 'PASTE'}, disable_double=True)

		# self.kmi_set_replace('mesh.ke_direct_loop_cut', 'C', "PRESS", alt=True, shift=True, properties={'mode': 'SLIDE'}, disable_double=True)

		# MACHINE3tools
		# kmi = self.kmi_set_replace('machin3.clean_up', 'ZERO', "PRESS", ctrl=True, alt=True, shift=True)
		# self.kmi_set_replace('wm.call_menu_pie', 'D', "PRESS", alt=True, shift=True, properties={'name': 'MACHIN3_MT_align_pie'}, disable_double=True)
		# self.kmi_set_active(False, 'machin3.select')

		# F2
		# self.kmi_set_replace('mesh.f2', 'P', 'PRESS', disable_double=True)

		# MAXVIZ
		self.kmi_set_replace('mesh.tila_smart_pivot', 'S', 'PRESS', alt=True, disable_double=True)

		# EdgeFlow
		# self.kmi_set_replace('mesh.set_edge_flow', 'F', 'PRESS', alt=True, properties={'tension': 180, 'iterations': 1, 'min_angle': 120}, disable_double=True)


		###### Object Mode
		self.kmi_init(name='Object Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.tool_transform(cage_scale='builtin.scale_cage')

		self.selection_keys(more_tool='object.select_more', less_tool='object.select_less')

		self.duplicate(duplicate='object.duplicate', duplicate_link='object.duplicate', duplicate_link_prop={'linked': True})

		self.selection_keys(invert_tool='object.select_all')

		self.tool_subdivision()
		self.kmi_set_replace('object.delete', 'DEL', 'PRESS', ctrl=True, alt=True, shift=True, properties={'use_global': True, 'confirm': True})

		self.isolate()

		self.join()
		
		self.kmi_set_replace('object.move_to_collection', 'M', 'PRESS', ctrl=True, alt=True, disable_double=True)
		self.kmi_set_replace('view3d.collection_manager', 'M', 'PRESS', shift=True, disable_double=True)
		self.kmi_set_replace('object.apply_all_modifiers', 'PAGE_DOWN', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)
		
		# Set collection visibility shortcut
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		
		self.tool_sculpt('view3d.tila_smart_sculptmode')
		self.kmi_set_replace('wm.call_menu_pie', 'S', 'PRESS', alt=True, shift=True, properties={'name': 'TILA_MT_pie_normal'}, disable_double=True)

		self.kmi_set_replace('outliner.tila_group_selected', 'G', 'PRESS', ctrl=True, properties={'mode': 'GROUP_TO_BIGGER_NUMBER'}, disable_double=True)
		self.kmi_set_replace('outliner.tila_group_selected', 'G', 'PRESS', ctrl=True, shift=True, properties={'mode': 'MOVE_TO_ACTIVE'}, disable_double=True)

		self.kmi_set_replace('object.tila_multires_project_subdivide', 'P', 'PRESS', ctrl=True, alt=True, shift=True, disable_double=True)

		# MACHIN3tools
		# self.kmi_set_replace('machin3.align', 'A', "PRESS", alt=True, disable_double=True)
		# self.kmi_set_replace('machin3.mirror', 'X', "PRESS", alt=True, shift=True, properties={'flick':True, 'remove':False}, disable_double=True)

		###### Sculpt
		self.kmi_init(name='Sculpt', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_sculpt('sculpt.sculptmode_toggle')
		self.selection_tool(tool='GRAB', alt='MASK')
		self.tool_transform()

		self.tool_subdivision()

		self.kmi_set_active(False, idname='object.switch_object')

		self.kmi_set_replace('object.voxel_size_edit', 'R', 'PRESS', shift=True, disable_double=True)
		self.kmi_set_replace('object.quadriflow_remesh', 'R', 'PRESS', ctrl=True, disable_double=True)

		self.kmi_set_replace('object.tila_duplicate', self.k_manip, 'CLICK_DRAG', ctrl=True, alt=True, shift=True, properties={'linked': False, 'move': True})

		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.sculpt.brush.size', 
								'data_path_secondary': 'tool_settings.unified_paint_settings.size', 
								'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size', 
								'rotation_path': 'tool_settings.sculpt.brush.texture_slot.angle', 
								'color_path': 'tool_settings.sculpt.brush.cursor_color_add', 
								'image_id': 'tool_settings.sculpt.brush', 
								'release_confirm': True},
						   		opacity={'data_path_primary': 'tool_settings.sculpt.brush.strength', 
								   'data_path_secondary': 'tool_settings.unified_paint_settings.strength', 
								   'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength', 
								   'rotation_path': 'tool_settings.sculpt.brush.texture_slot.angle', 
								   'color_path': 'tool_settings.sculpt.brush.cursor_color_add', 
								   'image_id': 'tool_settings.sculpt.brush', 
								   'release_confirm': True},
						   		eraser_radius={'data_path_primary': 'tool_settings.sculpt.brush.texture_slot.angle', 
								   'rotation_path': 'tool_settings.sculpt.brush.texture_slot.angle', 
								   'color_path': 'tool_settings.sculpt.brush.cursor_color_add', 
								   'image_id': 'tool_settings.sculpt.brush', 
								   'release_confirm': True})

		self.kmi_set_replace('sculpt.dynamic_topology_toggle', 'D', 'PRESS', ctrl=True, alt=True, shift=True)
		
		self.kmi_set_replace('paint.brush_select', self.k_menu, 'PRESS', ctrl=True, properties={'sculpt_tool': 'CLAY_STRIPS', 'toggle': True})
		self.kmi_set_replace('paint.brush_select', self.k_menu, 'PRESS', alt=True, properties={'sculpt_tool': 'SNAKE_HOOK', 'toggle': True})
		self.kmi_set_replace('paint.mask_lasso_gesture', self.k_context, 'CLICK_DRAG', ctrl=True, alt=False, shift=False, properties={'value': 1.0, 'mode': 'VALUE'}, disable_double=True)
		self.kmi_set_replace('paint.mask_lasso_gesture', self.k_context, 'CLICK_DRAG', ctrl=False, alt=False, shift=True, properties={'value': 0.0, 'mode': 'VALUE'}, disable_double=True)
		self.kmi_set_replace('paint.mask_flood_fill', self.k_context, 'PRESS', ctrl=True, alt=True, shift=True, properties={'mode': 'INVERT'})
		self.kmi_set_replace('paint.mask_flood_fill', self.k_context, 'PRESS', ctrl=True, shift=True, properties={'mode': 'VALUE', 'value': 0})
		self.kmi_set_replace('sculpt.tila_mask_faceset', self.k_context, 'CLICK', ctrl=True, properties={'mode': 'MASK'})
		self.kmi_set_replace('sculpt.tila_mask_faceset', self.k_context, 'CLICK', shift=True, properties={'mode': 'TOGGLE'})

		self.kmi_set_replace('paint.hide_show', self.k_nav, 'CLICK_DRAG', ctrl=True,  properties={'action': 'HIDE', 'wait_for_input': False, 'area': 'INSIDE'}, disable_double=True)
		self.kmi_set_replace('paint.hide_show', self.k_nav, 'CLICK_DRAG', shift=True, properties={'action': 'HIDE', 'wait_for_input': False, 'area': 'OUTSIDE'}, disable_double=True)
		self.kmi_set_replace('paint.hide_show', self.k_nav, 'PRESS', ctrl=True, alt=True, shift=True, properties={'action': 'SHOW', 'wait_for_input': False, 'area': 'ALL'}, disable_double=True)
		self.kmi_set_replace('sculpt.face_set_change_visibility', self.k_nav, 'PRESS', ctrl=False, shift=False, alt=False, properties={'mode': 'TOGGLE'}, disable_double=True)
		self.kmi_set_replace('sculpt.face_set_change_visibility', self.k_nav, 'RELEASE', ctrl=True, shift=False, alt=False, properties={'mode': 'HIDE_ACTIVE'}, disable_double=True)
		

		self.kmi_set_replace('sculpt.face_sets_create', 'W', 'PRESS', properties={'mode': 'MASKED'}, disable_double=True)
		self.kmi_set_replace('sculpt.face_sets_create', 'W', 'PRESS', alt=True, properties={'mode': 'VISIBLE'}, disable_double=True)
		self.kmi_set_replace('sculpt.face_set_edit', 'W', 'PRESS', ctrl=True, properties={'mode': 'SHRINK'}, disable_double=True)
		self.kmi_set_replace('sculpt.face_set_edit', 'W', 'PRESS', ctrl=True, shift=True, properties={'mode': 'GROW'}, disable_double=True)

		self.kmi_set_replace('sculpt.set_pivot_position', self.k_manip, 'PRESS', ctrl=True, alt=True, shift=True, properties={'mode': 'SURFACE'}, disable_double=True)

		self.kmi_set_replace('wm.context_toggle', 'F', 'PRESS', shift=True, properties={'data_path': 'space_data.overlay.show_sculpt_face_sets'}, disable_double=True)

		# self.kmi_set_replace('view3d.tila_inverse_visibility', self.k_nav, 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('sculpt.face_set_invert_visibility', self.k_nav, 'PRESS', ctrl=True, alt=True, shift=True, properties={'mode': 'INVERT'}, disable_double=True)
		self.kmi_set_replace('sculpt.sculpt.sample_color', 'S', 'PRESS', disable_double=True)

		if bversion >= 3.2: 
			# Curves
			self.kmi_init(name='Curves', space_type='EMPTY', region_type='WINDOW')
			self.global_keys()
			self.right_mouse()

			self.selection_keys(more_tool='curves.select_more', less_tool='curves.select_less')
			
			###### Sculpt Curves
			self.kmi_init(name='Sculpt Curves', space_type='EMPTY', region_type='WINDOW')
			self.global_keys()
			self.right_mouse()
			self.tool_sculpt(sculpt='curves.sculptmode_toggle')
			self.selection_tool(tool='COMB', alt='SELECTION_PAINT')

			self.tool_radial_control(radius={'data_path_primary': 'tool_settings.curves_sculpt.brush.size', 
									'data_path_secondary': 'tool_settings.unified_paint_settings.size', 
									'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size', 
									'rotation_path': 'tool_settings.curves_sculpt.brush.texture_slot.angle', 
									'color_path': 'tool_settings.curves_sculpt.brush.cursor_color_add', 
									'image_id': 'tool_settings.curves_sculpt.brush', 
									'release_confirm': True},
									opacity={'data_path_primary': 'tool_settings.curves_sculpt.brush.strength', 
									'data_path_secondary': 'tool_settings.unified_paint_settings.strength', 
									'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength', 
									'rotation_path': 'tool_settings.curves_sculpt.brush.texture_slot.angle', 
									'color_path': 'tool_settings.curves_sculpt.brush.cursor_color_add', 
									'image_id': 'tool_settings.curves_sculpt.brush', 
									'release_confirm': True},
									eraser_radius={'data_path_primary': 'tool_settings.curves_sculpt.brush.texture_slot.angle', 
									'rotation_path': 'tool_settings.curves_sculpt.brush.texture_slot.angle', 
									'color_path': 'tool_settings.curves_sculpt.brush.cursor_color_add', 
									'image_id': 'tool_settings.curves_sculpt.brush', 
									'release_confirm': True})

			self.kmi_set_replace('sculpt_curves.select_all', self.k_context, 'PRESS', ctrl=True, alt=True, shift=True, properties={'action': 'INVERT'})

		###### Curve
		self.kmi_init(name='Curve', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.tool_transform(cage_scale='builtin.scale_cage')
		self.right_mouse()
		self.duplicate(duplicate='curve.duplicate_move')
		self.tool_smart_delete()
		self.kmi_set_replace('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.shortest_path_pick', self.k_select, 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True, ctrl=True, shift=True, properties={'wait_for_input': False})
		self.kmi_set_replace('curve.separate', 'D', 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.subdivide', 'D', 'PRESS')
		kmi = self.kmi_set_replace('transform.tilt', 'T', 'PRESS', shift=True)
		kmi.active = True

		self.selection_keys(select_tool='curve.select',
					  		lasso_tool='curve.select_lasso',
					  		circle_tool='curve.select_circle',
					  		loop_tool='curve.select_loop',
					  		more_tool='curve.select_more',
					  		less_tool='curve.select_less',
					  		linked_tool='curve.select_linked',
							linked_pick_tool='curve.select_linked_pick',
							invert_tool='curve.select_all')

		###### Outliner
		self.kmi_init(name='Outliner', space_type='OUTLINER', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('outliner.item_rename', 'F2', 'PRESS')

		self.duplicate(duplicate='object.tila_duplicate', duplicate_prop={'linked': False, 'move': False}, duplicate_link='object.tila_duplicate', duplicate_link_prop={'linked': True, 'move': False})

		self.tool_smart_delete()
		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)
		self.kmi_set_replace('outliner.tila_select_hierarchy', self.k_select, 'DOUBLE_CLICK')
		self.kmi_set_replace('outliner.show_active', 'A', 'PRESS', ctrl=True, shift=True, disable_double=True)

		self.isolate()
		self.join()

		self.kmi_set_replace('outliner.tila_group_selected', 'G', 'PRESS', ctrl=True, properties={'mode': 'GROUP_TO_BIGGER_NUMBER'}, disable_double=True)
		self.kmi_set_replace('outliner.tila_group_selected', 'G', 'PRESS', ctrl=True, shift=True, properties={'mode': 'MOVE_TO_ACTIVE'}, disable_double=True)

		###### File Browser
		self.kmi_init(name='File Browser', space_type='FILE_BROWSER', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_smart_delete()
		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)

		###### Dopesheet
		self.kmi_init(name='Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='action.duplicate_move')
		self.selection_keys(more_tool='action.select_more', less_tool='action.select_less')

		###### Mask Editing
		self.kmi_init(name='Mask Editing', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('mask.duplicate_move', 'D', 'PRESS', ctrl=True)
		self.selection_keys(more_tool='mask.select_more',
							less_tool='mask.select_less', linked_tool='mask.select_linked_pick')

		# Sequencer
		self.kmi_init(name='Sequencer', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_keys(more_tool='sequencer.select_more', less_tool='sequencer.select_less')

		###### Graph Editor
		self.kmi_init(name='Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='graph.duplicate_move')
		self.selection_keys(more_tool='graph.select_more', less_tool='graph.select_less')

		###### Property Editor
		self.kmi_init(name='Property Editor', space_type='PROPERTIES', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')
		
		###### Vertex Paint
		self.kmi_init(name='Vertex Paint', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool(tool='builtin_brush.Draw')

		self.tool_radial_control(
								radius={'data_path_primary': 'tool_settings.vertex_paint.brush.size', 
								'data_path_secondary': 'tool_settings.unified_paint_settings.size', 
								'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size', 
								'rotation_path': 'tool_settings.vertex_paint.brush.texture_slot.angle', 
								'color_path': 'tool_settings.vertex_paint.brush.cursor_color_add', 
								'image_id': 'tool_settings.vertex_paint.brush',
								'release_confirm': True},
								opacity={'data_path_primary': 'tool_settings.vertex_paint.brush.strength', 
								'data_path_secondary': 'tool_settings.unified_paint_settings.strength', 
								'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength', 
								'rotation_path': 'tool_settings.vertex_paint.brush.texture_slot.angle', 
								'color_path': 'tool_settings.vertex_paint.brush.cursor_color_add', 
								'image_id': 'tool_settings.vertex_paint.brush',
								'release_confirm': True},
								eraser_radius={'data_path_primary': 'tool_settings.vertex_paint.brush.texture_slot.angle', 
								'rotation_path': 'tool_settings.vertex_paint.brush.texture_slot.angle', 
								'color_path': 'tool_settings.vertex_paint.brush.cursor_color_add', 
								'image_id': 'tool_settings.vertex_paint.brush',
								'release_confirm': True})

		self.tool_sample_color('paint.sample_color')
		self.kmi_set_replace('view3D.toggle_symetry', 'X', 'PRESS', shift=True)
		self.selection_keys(more_tool='paint.vert_select_more', less_tool='paint.vert_select_less',
							lasso_tool='view3d.select_lasso', circle_tool='view3d.select_circle', linked_tool='paint.face_select_linked')

		# self.kmi_set_replace('paint.weight_gradient', self.k_manip, 'PRESS', ctrl=True, shift=True, properties={'type': 'LINEAR'})
		# self.kmi_set_replace('paint.weight_gradient', self.k_manip, 'PRESS', ctrl=True, shift=True, alt=True, properties={'type': 'RADIAL'})

		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', shift=True, properties={'tool': 'VERTEX', 'mode': 'BLUR', 'brush': 'Blur'})
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', ctrl=True, properties={'tool': 'VERTEX', 'mode': 'DRAW', 'brush': 'Multiply'})

		###### Weight Paint
		self.kmi_init(name='Weight Paint', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool(tool='builtin_brush.Draw')
		
		self.tool_radial_control(
		radius={'data_path_primary': 'tool_settings.weight_paint.brush.size', 
		'data_path_secondary': 'tool_settings.unified_paint_settings.size', 
		'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size', 
		'rotation_path': 'tool_settings.weight_paint.brush.texture_slot.angle', 
		'color_path': 'tool_settings.weight_paint.brush.cursor_color_add', 
		'image_id': 'tool_settings.weight_paint.brush',
		'release_confirm': True},
		opacity={'data_path_primary': 'tool_settings.weight_paint.brush.strength', 
		'data_path_secondary': 'tool_settings.unified_paint_settings.strength', 
		'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength', 
		'rotation_path': 'tool_settings.weight_paint.brush.texture_slot.angle', 
		'color_path': 'tool_settings.weight_paint.brush.cursor_color_add', 
		'image_id': 'tool_settings.weight_paint.brush',
		'release_confirm': True},
		eraser_radius={'data_path_primary': 'tool_settings.weight_paint.brush.texture_slot.angle', 
		'rotation_path': 'tool_settings.weight_paint.brush.texture_slot.angle', 
		'color_path': 'tool_settings.weight_paint.brush.cursor_color_add', 
		'image_id': 'tool_settings.weight_paint.brush',
		'release_confirm': True})
		
		self.kmi_set_active(enable=False, idname='paint.weight_set')

		self.selection_keys(more_tool='paint.vert_select_more', less_tool='paint.vert_select_less',
							lasso_tool='view3d.select_lasso', circle_tool='view3d.select_circle', linked_tool='paint.face_select_linked')
	
		self.tool_sample_color('paint.weight_sample')

		self.kmi_set_replace('paint.weight_gradient', self.k_manip, 'PRESS', ctrl=True, shift=True, properties={'type': 'LINEAR'})
		self.kmi_set_replace('paint.weight_gradient', self.k_manip, 'PRESS', ctrl=True, shift=True, alt=True, properties={'type': 'RADIAL'})

		self.kmi_set_replace('paint.weight_sample_group', self.k_context, 'RELEASE', disable_double=True)
		
		# self.kmi_set_replace('wm.tool_set_by_id', self.k_manip, 'PRESS', ctrl=True, shift=True, alt=True, properties={'name': 'builtin_brush.Draw'})
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', shift=True, properties={'tool': 'WEIGHT', 'mode': 'AVERAGE', 'brush': 'Average'})
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', ctrl=True, properties={'tool': 'WEIGHT', 'mode': 'DRAW', 'brush': 'Subtract'})

		self.kmi_set_replace('paint.weight_set', self.k_linked, 'PRESS')

		self.kmi_set_replace('paint.toggle_brushweight', 'X', 'PRESS')

		self.kmi_set_replace('view3D.toggle_symetry', 'X', 'PRESS', shift=True)
		
		
		###### Image Paint
		self.kmi_init(name='Image Paint', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool(tool='builtin_brush.Draw')

		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.image_paint.brush.size', 
		'data_path_secondary': 'tool_settings.unified_paint_settings.size', 
		'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size', 
		'rotation_path': 'tool_settings.image_paint.brush.texture_slot.angle', 
		'color_path': 'tool_settings.image_paint.brush.cursor_color_add', 
		'image_id': 'tool_settings.image_paint.brush',
		'fill_color_path': 'tool_settings.image_paint.brush.color', 
		'fill_color_override_path': 'tool_settings.unified_paint_settings.color', 
		'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
		'zoom_path': 'space_data.zoom', 'secondary_tex': True,
		'release_confirm': True},
		opacity={'data_path_primary': 'tool_settings.image_paint.brush.strength', 
		'data_path_secondary': 'tool_settings.unified_paint_settings.strength', 
		'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength', 
		'rotation_path': 'tool_settings.image_paint.brush.texture_slot.angle', 
		'color_path': 'tool_settings.image_paint.brush.cursor_color_add', 
		'image_id': 'tool_settings.image_paint.brush',
		'fill_color_path': 'tool_settings.image_paint.brush.color', 
		'fill_color_override_path': 'tool_settings.unified_paint_settings.color', 
		'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
		'secondary_tex': True,
		'release_confirm': True},
		eraser_radius={'data_path_primary': 'tool_settings.image_paint.brush.texture_slot.angle', 
		'rotation_path': 'tool_settings.image_paint.brush.texture_slot.angle', 
		'color_path': 'tool_settings.image_paint.brush.cursor_color_add', 
		'image_id': 'tool_settings.image_paint.brush',
		'fill_color_path': 'tool_settings.image_paint.brush.color', 
		'fill_color_override_path': 'tool_settings.unified_paint_settings.color', 
		'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color'})
		# fill_color={'fill_color_path': 'tool_settings.image_paint.brush.color', 
		# 'fill_color_override_path': 'tool_settings.unified_paint_settings.color', 
		# 'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
		# 'zoom_path': 'space_data.zoom', 'secondary_tex': True,
		# 'release_confirm': True})

		self.selection_keys(more_tool='paint.vert_select_more', less_tool='paint.vert_select_less',
							lasso_tool='view3d.select_lasso', circle_tool='view3d.select_circle', linked_tool='paint.face_select_linked')
		
		self.tool_sample_color('paint.sample_color')
		
		self.kmi_set_replace('paint.toggle_brushweight', 'X', 'PRESS')

		self.kmi_set_replace('view3D.toggle_symetry', 'X', 'PRESS', shift=True)

		###### Node Tool: Tweak
		self.kmi_init(name='Node Tool: Tweak', space_type='NODE_EDITOR', region_type='WINDOW')
		# self.selection_keys(select_tool='node.select')

		###### Node Tool: Select Box
		self.kmi_init(name='Node Tool: Select Box', space_type='NODE_EDITOR', region_type='WINDOW')
		# self.selection_keys(select_tool='node.select')

		###### Node Editor
		self.kmi_init(name='Node Editor', space_type='NODE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# self.selection_keys(select_tool='node.select')
		# self.duplicate(duplicate='node.duplicate_move_keep_inputs', duplicate_prop={'keep_inputs': True, 'linked': True})
		self.kmi_set('node.duplicate_move_keep_inputs', type='D', value='PRESS', ctrl=True,
					 alt=False, shift=False, properties={'keep_inputs': True, 'linked': True})
		self.snap(snapping='wm.context_menu_enum', snapping_prop={'data_path': 'tool_settings.snap_node_element'})
		self.kmi_set_replace('node.view_selected', 'A', 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('node.add_search', self.k_menu, 'PRESS')
		
		self.kmi_set_replace('node.backimage_move', self.k_cursor, 'PRESS', disable_double=True)
		self.kmi_set_replace('node.backimage_zoom', self.k_lasso_through, 'CLICK_DRAG', direction='EAST', alt=True, properties={'factor': 1.2}, disable_double=True)
		self.kmi_set_replace('node.backimage_zoom', self.k_lasso_through, 'CLICK_DRAG', direction='WEST', alt=True, properties={'factor': 0.8}, disable_double=True)

		self.kmi_set_replace('node.node_copy_color', 'C', 'PRESS', ctrl=True, shift=True, disable_double=True)
		# self.kmi_set_replace('node.join', 'J', 'PRESS', ctrl=True, disable_double=True)
		self.kmi_set_replace('node.detach', 'J', 'PRESS', alt=True, disable_double=True)
		
		# Noodler
		# self.kmi_set_replace('noodler.draw_route', 'E', 'PRESS', disable_double=True)
		# self.kmi_set_replace('noodler.chamfer', 'B', 'PRESS', disable_double=True)
		# self.kmi_set_replace('noodler.draw_frame', 'J', 'PRESS', ctrl=True, disable_double=True)
		# self.kmi_set_replace('noodler.dependency_select', self.k_manip, 'DOUBLE_CLICK', shift=True, properties={'mode': "downstream", 'repsel': True}, disable_double=True)
		# self.kmi_set_replace('noodler.dependency_select', self.k_manip, 'DOUBLE_CLICK', ctrl=True, properties={'mode': "upstream", 'repsel': True}, disable_double=True)

		###### Animation
		self.kmi_init(name='Animation', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		###### Armature
		self.kmi_init(name='Armature', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='armature.duplicate_move')
		self.tool_transform(cage_scale='builtin.scale_cage')
		self.selection_keys(more_tool='armature.select_more', less_tool='armature.select_less')

		###### Pose
		self.kmi_init(name='Pose', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_transform()
		# MACHIN3tools
		# self.kmi_set_replace('machin3.align', 'A', "PRESS", alt=True, disable_double=True)

		###### Metaball
		self.kmi_init(name='Metaball', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_transform(cage_scale='builtin.scale_cage')
		self.duplicate(duplicate='mball.duplicate_metaelems')
		self.selection_tool()
		self.tool_smart_delete()
		self.kmi_set_replace('mball.tila_metaball_adjust_parameter', 'S', 'PRESS', alt=True, shift=True, properties={'param': 'STIFFNESS'}, disable_double=True)
		self.kmi_set_replace('mball.tila_metaball_adjust_parameter', 'R', 'PRESS', alt=True, shift=True, properties={'param': 'RESOLUTION'}, disable_double=True)
		self.kmi_set_replace('mball.tila_metaball_type_cycle', 'W', 'PRESS', ctrl=True, properties={'direction': 'NEXT'}, disable_double=True)
		self.kmi_set_replace('mball.tila_metaball_type_cycle', 'W', 'PRESS', ctrl=True, shift=True, properties={'direction': 'PREVIOUS'}, disable_double=True)
		self.kmi_set_replace('mball.tila_metaball_substract_toggle', 'X', 'PRESS', disable_double=True)

		###### NLA Editor
		self.kmi_init(name='NLA Editor', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='nla.duplicate', duplicate_link='nla.duplicate', duplicate_link_prop={'linked': True})
		
		###### Lattice
		self.kmi_init(name='Lattice', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_transform(cage_scale='builtin.scale_cage')
		self.selection_keys(select_tool='view3d.select', 
							lasso_tool='view3d.select_lasso',
							select_through_tool='view3d.tila_select_through',
					  		circle_tool='view3d.select_circle',
							invert_tool='lattice.select_all',
							more_tool='lattice.select_more', 
					  		less_tool='lattice.select_less')

		###### Grease Pencil
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

		self.isolate()

		# Grease Pencil Tools
		self.kmi_set_replace('animation.time_scrub', self.k_menu, 'PRESS', shift=True)

		###### Grease Pencil Stroke Edit Mode
		self.kmi_init(name='Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.tool_transform(cage_scale='builtin.scale_cage')
		self.duplicate(duplicate='gpencil.duplicate_move')
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		self.tool_smart_delete()
		self.kmi_set_active(False, idname='gpencil.dissolve')
		self.kmi_set_active(False, idname='gpencil.active_frames_delete_all')
		self.kmi_set_replace('gpencil.dissolve', 'DEL', 'PRESS', shift=True, properties={'type': 'POINTS'}, disable_double=True)
		self.kmi_set_replace('gpencil.active_frames_delete_all', 'DEL', 'PRESS', ctrl=True, alt=True, shift=True)
		self.selection_keys(gp_circle_tool='gpencil.select_circle',
							more_tool='gpencil.select_more',
					  		less_tool='gpencil.select_less',
							invert_tool='gpencil.select_all',
							linked_tool='gpencil.select_linked',
							linked_pick_tool='gpencil.select_linked')
		self.kmi_set_replace('gpencil.stroke_subdivide', 'D', 'PRESS',  properties={'only_selected': False}, disable_double=True)
		self.isolate()
		self.tool_center(pivot='VIEW3D_PT_pivot_point', orientation='VIEW3D_PT_transform_orientations', action_center_context='VIEW3D')
		

		###### Grease Pencil Stroke Paint Mode
		self.kmi_init(name='Grease Pencil Stroke Paint Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='gpencil.duplicate_move')
		self.collection_visibility('object.hide_collection')
		self.mode_selection()
		self.selection_tool(tool='builtin_brush.Draw')
		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.gpencil_paint.brush.size', 'release_confirm': True},
								opacity={'data_path_primary': 'tool_settings.gpencil_paint.brush.gpencil_settings.pen_strength', 'release_confirm': True},
								eraser_radius={'data_path_primary': 'q.edit.grease_pencil_eraser_radius', 'release_confirm': True})
		
		self.selection_keys(circle_tool='gpencil.select_circle',
			  				linked_pick_tool='gpencil.select_linked',
							more_tool='gpencil.select_more',
							less_tool='gpencil.select_less',
							invert_tool='gpencil.select_all',
							lasso_tool='gpencil.select_lasso',
							)

		###### Grease Pencil Stroke Paint (Draw brush)
		self.kmi_init(name='Grease Pencil Stroke Paint (Draw brush)', space_type='EMPTY', region_type='WINDOW')
		kmi = self.kmi_find(idname='gpencil.draw', ctrl=False, alt=True, shift=False)
		if kmi is not None:
			kmi.ctrl = True
			kmi.alt = False
			kmi.shift = True

		kmi = self.kmi_find(idname='gpencil.draw', ctrl=False, alt=True, shift=True)
		if kmi is not None:
			kmi.ctrl = True
			kmi.alt = True
			kmi.shift = True
		
		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.gpencil_paint.brush.size', 'release_confirm': True},
						   		opacity={ 'data_path_primary': 'tool_settings.gpencil_paint.brush.gpencil_settings.pen_strength', 'release_confirm': True},
								eraser_radius={'data_path_primary': 'q.edit.grease_pencil_eraser_radius', 'release_confirm': True})

		# Grease Pencil Stroke Vertex Mode
		self.kmi_init(name='Grease Pencil Stroke Vertex Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.gpencil_vertex_paint.brush.size', 'release_confirm': True},
						   		opacity={ 'data_path_primary': 'tool_settings.gpencil_vertex_paint.brush.gpencil_settings.pen_strength', 'release_confirm': True},
								eraser_radius={'data_path_primary': 'q.edit.grease_pencil_eraser_radius', 'release_confirm': True})
		
		# kmi = self.kmi_find(idname='gpencil.draw', ctrl=False, alt=True, shift=False)
		# if kmi is not None:
		# 	kmi.ctrl = True
		# 	kmi.alt = False
		# 	kmi.shift = True

		# kmi = self.kmi_find(idname='gpencil.draw', ctrl=False, alt=True, shift=True)
		# if kmi is not None:
		# 	kmi.ctrl = True
		# 	kmi.alt = True
		# 	kmi.shift = True

		

		###### Grease Pencil Stroke Sculpt Mode
		self.kmi_init(name='Grease Pencil Stroke Sculpt Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.mode_selection()
		self.selection_tool(tool='builtin_brush.Grab')
		# self.kmi_set_replace('wm.tool_set_by_id', 'G', 'PRESS', properties={'name': 'builtin_brush.Grab'})
		
		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.gpencil_sculpt_paint.brush.size',
								   'release_confirm': True},
						   opacity={'data_path_primary': 'tool_settings.gpencil_sculpt_paint.brush.strength',
									'release_confirm': True},
						   eraser_radius={'data_path_primary': 'tool_settings.gpencil_sculpt_paint.brush.texture_slot.angle',
										  'rotation_path': 'tool_settings.gpencil_sculpt_paint.brush.texture_slot.angle',
										  'color_path': 'tool_settings.gpencil_sculpt_paint.brush.cursor_color_add',
										  'image_id': 'tool_settings.gpencil_sculpt_paint.brush',
										  'fill_color_path': 'tool_settings.gpencil_sculpt_paint.brush.color',
										  'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
										  'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
										  'release_confirm': True})
						#    fill_color={'fill_color_path': 'tool_settings.gpencil_sculpt_paint.brush.color',
						# 			   'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
						# 			   'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
						# 			   'zoom_path': 'space_data.zoom', 'secondary_tex': True,
						# 			   'release_confirm': True})
		
		self.selection_keys(circle_tool='gpencil.select_circle',
							linked_pick_tool='gpencil.select_linked',
							more_tool='gpencil.select_more',
							less_tool='gpencil.select_less',
							invert_tool='gpencil.select_all',
							lasso_tool='gpencil.select_lasso'
							)
		
		
		# Grease Pencil Stroke Vertex Mode
		self.kmi_init(name='Grease Pencil Stroke Vertex Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.mode_selection()
		self.selection_tool(tool='builtin_brush.Draw')
		
		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.gpencil_vertex_paint.brush.size',
								   'release_confirm': True},
						   opacity={'data_path_primary': 'tool_settings.gpencil_vertex_paint.brush.strength',
									'release_confirm': True},
						   eraser_radius={'data_path_primary': 'tool_settings.gpencil_vertex_paint.brush.texture_slot.angle',
										  'rotation_path': 'tool_settings.gpencil_vertex_paint.brush.texture_slot.angle',
										  'color_path': 'tool_settings.gpencil_vertex_paint.brush.cursor_color_add',
										  'image_id': 'tool_settings.gpencil_vertex_paint.brush',
										  'fill_color_path': 'tool_settings.gpencil_vertex_paint.brush.color',
										  'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
										  'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
										  'release_confirm': True})
						#    fill_color={'fill_color_path': 'tool_settings.gpencil_vertex_paint.brush.color',
						# 			   'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
						# 			   'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
						# 			   'zoom_path': 'space_data.zoom', 'secondary_tex': True,
						# 			   'release_confirm': True})
		

		self.selection_keys(circle_tool='gpencil.select_circle',
							linked_pick_tool='gpencil.select_linked',
							more_tool='gpencil.select_more',
							less_tool='gpencil.select_less',
							invert_tool='gpencil.select_all',
							lasso_tool='gpencil.select_lasso'
							)
		
		# Grease Pencil Stroke Weight Mode
		self.kmi_init(name='Grease Pencil Stroke Weight Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.mode_selection()
		self.selection_tool(tool='builtin_brush.Weight')
		
		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.gpencil_weight_paint.brush.size',
								   'release_confirm': True},
						   opacity={'data_path_primary': 'tool_settings.gpencil_weight_paint.brush.strength',
									'release_confirm': True},
						   eraser_radius={'data_path_primary': 'tool_settings.gpencil_weight_paint.brush.texture_slot.angle',
										  'rotation_path': 'tool_settings.gpencil_weight_paint.brush.texture_slot.angle',
										  'color_path': 'tool_settings.gpencil_weight_paint.brush.cursor_color_add',
										  'image_id': 'tool_settings.gpencil_weight_paint.brush',
										  'fill_color_path': 'tool_settings.gpencil_weight_paint.brush.color',
										  'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
										  'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
										  'release_confirm': True})
						#    fill_color={'fill_color_path': 'tool_settings.gpencil_weight_paint.brush.color',
						#                'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
						#                'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
						#                'zoom_path': 'space_data.zoom', 'secondary_tex': True,
						#                'release_confirm': True})
		
		self.selection_keys(gp_circle_tool='gpencil.select_circle',
							linked_pick_tool='gpencil.select_linked',
							more_tool='gpencil.select_more',
							less_tool='gpencil.select_less',
							invert_tool='gpencil.select_all'
							)
		
		self.kmi_set_replace('wm.tool_set_by_id', self.k_manip, 'PRESS', ctrl=True, shift=True, alt=True, properties={'name': 'builtin_brush.Weight'})
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', shift=True, properties={'tool': 'WEIGHT', 'mode': 'AVERAGE', 'brush': 'Average'})
		self.kmi_set_replace('paint.tila_brush_select_and_paint', self.k_manip, 'PRESS', ctrl=True, properties={'tool': 'WEIGHT', 'mode': 'DRAW', 'brush': 'Subtract'})
		
		# Paint Face Mask (Weight, Vertex, Texture)
		self.kmi_init(name='Paint Face Mask (Weight, Vertex, Texture)',
					  space_type='EMPTY', region_type='WINDOW')

		self.selection_keys(more_tool='paint.face_select_more',
							less_tool='paint.face_select_less',
							linked_pick_tool='paint.face_select_linked_pick')
		
		# Paint Vertex Selection (Weight, Vertex)
		self.kmi_init(name='Paint Vertex Selection (Weight, Vertex)',
					  space_type='EMPTY', region_type='WINDOW')

		self.selection_keys(more_tool='paint.vert_select_more',
							less_tool='paint.vert_select_less')
		
		###### Frames
		self.kmi_init(name='Frames', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('screen.animation_play', 'SPACE', 'PRESS', ctrl=True, shift=True,  properties={'reverse': False})

		###### Screen
		self.kmi_init(name='Screen', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('screen.screen_full_area', 'SPACE', 'PRESS', ctrl=True, alt=True)
		self.kmi_set_replace('screen.screen_full_area', 'SPACE', 'PRESS', ctrl=True, alt=True, shift=True, properties={'use_hide_panels': True})

		###### Particle
		self.kmi_init(name='Particle', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.mode_selection()
		self.tool_radial_control(radius={'data_path_primary': 'tool_settings.particle_edit.brush.size',
		'release_confirm': True},
		opacity={'data_path_primary': 'tool_settings.particle_edit.brush.strength'})

		kmi = self.kmi_find(idname='wm.call_menu', type=self.k_context)
		kmi.value = 'RELEASE'
		self.selection_keys(lasso_tool='view3d.select_lasso',
							select_through_tool='view3d.tila_select_through',
							more_tool='particle.select_more',
					  		less_tool='particle.select_less',
					  		linked_tool='particle.select_linked',
							linked_pick_tool='particle.select_linked_pick',
							invert_tool='particle.select_all')
		

		###### Transform Modal Map
		self.kmi_init(name='Transform Modal Map', space_type='EMPTY', region_type='WINDOW')
		self.tool_proportional()
		
		###### Knife Tool Modal Map
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
		
		###### Gesture Box Modal Map
		self.kmi_init(name='Gesture Box', space_type='EMPTY', region_type='WINDOW')
		self.modal_set_replace('SELECT', self.k_cursor, 'RELEASE', any=True)
		
		self.print_status(f"Assignment of {self.addon_name} complete", start=False)

class TILA_Config_Keymaps_Empty(TILA_Config_Keymaps):
	addon_name = "Empty"

	def __init__(self):
		super(TILA_Config_Keymaps_Empty, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)

class TILA_Config_Keymaps_PolyQuilt(TILA_Config_Keymaps):
	addon_name = "PolyQuilt"

	def __init__(self):
		super(TILA_Config_Keymaps_PolyQuilt, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		if self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('wm.tool_set_by_id', 'F', 'PRESS', shift=True, properties={'name': 'mesh_tool.poly_quilt'}, disable_double=True)

		###### 3D View Tool: Edit Mesh, PolyQuilt
		if self.kmi_init(name='3D View Tool: Edit Mesh, PolyQuilt', space_type='VIEW_3D', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_active(False, idname='mesh.poly_quilt', type='LEFTMOUSE', value='PRESS', ctrl=False, shift=False, alt=False, oskey=False)
			self.kmi_set_active(False, idname='mesh.poly_quilt', type='LEFTMOUSE', value='PRESS', ctrl=True, shift=True, alt=False, oskey=False)
			self.kmi_set_active(False, idname='mesh.poly_quilt', type='LEFTMOUSE', value='PRESS', ctrl=True, shift=False, alt=False, oskey=False)
			self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', properties={'tool_mode': 'LOWPOLY'}, disable_double=True)
			self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', shift=True, properties={'tool_mode': 'BRUSH', 'brush_type': 'SMOOTH'})
			self.kmi_set_replace('mesh.poly_quilt', self.k_cursor, 'PRESS', shift=True, properties={'tool_mode': 'BRUSH', 'brush_type': 'MOVE'}, disable_double=True)
			self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', ctrl=True, properties={'tool_mode': 'EXTRUDE'}, disable_double=True)
			self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', ctrl=True, shift=True, properties={'tool_mode': 'EDGELOOP'}, disable_double=True)
			self.kmi_set_replace('mesh.poly_quilt', self.k_cursor, 'PRESS', ctrl=True, properties={'tool_mode': 'KNIFE'}, disable_double=True)
			self.kmi_set_replace('mesh.poly_quilt', self.k_context, 'PRESS', ctrl=True, shift=True, properties={'tool_mode': 'LOOPCUT'}, disable_double=True)
			self.kmi_set_replace('mesh.poly_quilt', self.k_manip, 'PRESS', ctrl=True, alt=True, shift=True, properties={'tool_mode': 'DELETE'}, disable_double=True)

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)

class TILA_Config_Keymaps_MACHIN3tools(TILA_Config_Keymaps):
	addon_name = "MACHIN3tools"

	def __init__(self):
		super(TILA_Config_Keymaps_MACHIN3tools, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		if self.kmi_init(name='Window', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('wm.call_menu_pie', 'S', "PRESS", ctrl=True, shift=True, properties={'name': 'MACHIN3_MT_save_pie'}, disable_double=True)

		if self.kmi_init(name='UV Editor', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('wm.call_menu_pie', 'D', "PRESS", alt=True, shift=True, properties={'name': 'MACHIN3_MT_uv_align_pie'}, disable_double=True)

		if self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('machin3.clean_up', 'ZERO', "PRESS", ctrl=True, alt=True, shift=True)
			self.kmi_set_active(True, 'machin3.clean_up', 'ZERO', "PRESS", ctrl=True, alt=True, shift=True)
			self.kmi_set_replace('wm.call_menu_pie', 'D', "PRESS", alt=True, shift=True, properties={'name': 'MACHIN3_MT_align_pie'}, disable_double=True)
			self.kmi_set_active(False, 'machin3.select')

		if self.kmi_init(name='Object Mode', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('machin3.align', 'A', "PRESS", alt=True, disable_double=False)
			# self.kmi_set_replace('machin3.mirror', 'X', "PRESS", alt=True, shift=True, properties={'flick': True, 'remove': False}, disable_double=False)
			self.kmi_set_active(True, 'machin3.mirror', 'X', "PRESS", alt=True, shift=True, properties={'flick': True, 'remove': False})

		if self.kmi_init(name='Pose', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('machin3.align', 'A', "PRESS", alt=True, disable_double=False)
			
		self.print_status(f"Assignment of {self.addon_name} complete", start=False)

class TILA_Config_Keymaps_noodler(TILA_Config_Keymaps):
	addon_name = "noodler"

	def __init__(self):
		super(TILA_Config_Keymaps_noodler, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		self.kmi_init(name='Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', addon=False, restore_to_default=False)
		self.kmi_set_replace('noodler.draw_route', 'E', 'PRESS', disable_double=True)
		self.kmi_set_replace('noodler.chamfer', 'B', 'PRESS', disable_double=True)
		self.kmi_set_replace('noodler.draw_frame', 'J', 'PRESS')
		self.kmi_set_replace('noodler.dependency_select', self.k_manip, 'DOUBLE_CLICK', shift=True, properties={'mode': "downstream", 'repsel': True}, disable_double=True)
		self.kmi_set_replace('noodler.dependency_select', self.k_manip, 'DOUBLE_CLICK', ctrl=True, properties={'mode': "upstream", 'repsel': True}, disable_double=True)

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)

class TILA_Config_Keymaps_atomic_data_manager(TILA_Config_Keymaps):
	addon_name = "atomic_data_manager"

	def __init__(self):
		super(TILA_Config_Keymaps_atomic_data_manager, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		if self.kmi_init(name='Window', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('atomic.invoke_pie_menu_ui', 'DEL', "PRESS", ctrl=True, shift=True, disable_double=True)

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)

class TILA_Config_Keymaps_kekit(TILA_Config_Keymaps):
	addon_name = "kekit"

	def __init__(self):
		super(TILA_Config_Keymaps_kekit, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		if self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('view3d.ke_get_set_material', 'M', 'PRESS', shift=True)

		if self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			kmi = self.kmi_find(idname='wm.call_menu', type='C', ctrl=True)
			if kmi is not None:
				kmi.shift = True

			kmi = self.kmi_find(idname='wm.call_menu', type='V', ctrl=True)
			if kmi is not None:
				kmi.shift = True

			self.kmi_set_replace('view3d.ke_copyplus', 'C', "PRESS", ctrl=True, properties={'mode': 'COPY'}, disable_double=True)
			self.kmi_set_replace('view3d.ke_copyplus', 'X', "PRESS", ctrl=True, properties={'mode': 'CUT'}, disable_double=True)
			self.kmi_set_replace('view3d.ke_copyplus', 'V', "PRESS", ctrl=True, properties={'mode': 'PASTE'}, disable_double=True)

			self.kmi_set_replace('mesh.ke_direct_loop_cut', 'C', "PRESS", alt=True, shift=True, properties={'mode': 'SLIDE'}, disable_double=True)

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)
		
class TILA_Config_Keymaps_rotate_an_hdri(TILA_Config_Keymaps):
	addon_name = "rotate_an_hdri"

	def __init__(self):
		super(TILA_Config_Keymaps_rotate_an_hdri, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		if self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW', addon=False, restore_to_default=False):
			# self.kmi_set_active(enable=False, idname='rotate.hdri')
			self.kmi_set_replace('rotate.hdri', self.k_context, 'CLICK_DRAG', ctrl=True, alt=True, shift=False,  disable_double=True)

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)
		
class TILA_Config_Keymaps_Poly_Source(TILA_Config_Keymaps):
	addon_name = "Poly_Source"

	def __init__(self):
		super(TILA_Config_Keymaps_Poly_Source, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		if self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_active(enable=False, idname='wm.call_menu_pie', type=self.k_menu, value='PRESS', properties={'name': 'PS_MT_tk_menu'})

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)
		
class TILA_Config_Keymaps_uv_toolkit(TILA_Config_Keymaps):
	addon_name = "uv_toolkit"

	def __init__(self):
		super(TILA_Config_Keymaps_uv_toolkit, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		if self.kmi_init(name='UV Editor', space_type='EMPTY', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('uv.toolkit_orient_to_edge', 'D', "PRESS", ctrl=True, alt=True, shift=True, disable_double=True)

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)

class TILA_Config_Keymaps_pin_verts(TILA_Config_Keymaps):
	addon_name = "pin_verts"

	def __init__(self):
		super(TILA_Config_Keymaps_pin_verts, self).__init__()

	def set_keymaps(self):
		self.print_status(f"Assigning {self.addon_name} Keymaps")

		if self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW', addon=False, restore_to_default=False):
			self.kmi_set_replace('sna.modal_operator_5f468', 'P', "PRESS", ctrl=True, alt=True, shift=True, disable_double=True)

		self.print_status(f"Assignment of {self.addon_name} complete", start=False)
		
# class TILA_Config_Keymaps_EdgeFlow(TILA_Config_Keymaps):
# 	addon_name = "EdgeFlow"

# 	def __init__(self):
# 		super(TILA_Config_Keymaps_EdgeFlow, self).__init__()

# 	def set_keymaps(self):
# 		self.print_status(f"Assigning {self.addon_name} Keymaps")

# 		if self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW', addon=True, restore_to_default=False):
# 			self.kmi_set_replace('mesh.set_edge_flow', 'F', 'PRESS', alt=True, properties={'tension': 180, 'iterations': 1, 'min_angle': 120}, disable_double=True)

# 		self.print_status(f"Assignment of {self.addon_name} complete", start=False)

		