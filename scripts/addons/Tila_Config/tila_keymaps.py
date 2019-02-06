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
# - Create a rename /batch rename feature
# - Modify the camera behaviour to slow the dolly speed based on the distance from the object
# - select next/previous
# - Smart edit mode


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
		self.k_context = 'RIGHTMOUSE'
		self.k_more = 'UP_ARROW'
		self.k_less = 'DOWN_ARROW'
		self.k_linked = 'W'

	# Global Keymap Functions

	def global_keys(self):
		self.kmi_set_replace("screen.userpref_show", "TAB", "PRESS", ctrl=True)
		self.kmi_set_replace("wm.window_fullscreen_toggle", "F11", "PRESS")
		self.kmi_set_replace('screen.animation_play', self.k_menu, 'PRESS', shift=True)
		self.kmi_set_replace("popup.hp_properties", 'V', "PRESS", ctrl=True, shift=True)
		# Disable Keymap
		self.kmi_set_active(False, type='X')
		self.kmi_set_active(False, type='X', shift=True)

	def navigation_keys(self, pan=None, orbit=None, dolly=None):
		if orbit:
			self.kmi_set_replace(orbit, self.k_manip, "PRESS", alt=True)
		if pan:
			self.kmi_set_replace(pan, self.k_manip, "PRESS", alt=True, shift=True)
		if dolly:
			self.kmi_set_replace(dolly, self.k_manip, "PRESS", alt=True, ctrl=True)

	def selection_keys(self,
						select_tool=None, 
						lasso_tool=None,
                    	circle_tool=None,
						shortestpath_tool=None,
						loop_tool=None, ring_tool=None,
						more_tool=None, less_tool=None,
						linked_tool=None):

		# Select / Deselect / Add
		if select_tool:
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK')
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK', shift=True, properties=[('extend', True)])
			self.kmi_set_replace(select_tool, self.k_select, 'CLICK', ctrl=True, properties=[('deselect', True)])
	
		# Lasso Select / Deselect / Add
		if lasso_tool:
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY')
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY', shift=True, properties=[('mode', 'ADD')])
			self.kmi_set_replace(lasso_tool, self.k_lasso, 'ANY', ctrl=True, properties=[('mode', 'SUB')])

		# Circle
		if circle_tool:
			self.kmi_set_replace(circle_tool, self.k_select, 'CLICK_DRAG', shift=True, properties=[('wait_for_input', False), ('radius', 10)])
			self.kmi_set_replace(circle_tool, self.k_select, 'CLICK_DRAG', ctrl=True, properties=[('wait_for_input', False), ('deselect', True), ('radius', 10)])
		
		#  shortest Path Select / Deselect / Add
		if shortestpath_tool:
			self.kmi_set_replace(shortestpath_tool, self.k_context, 'CLICK', shift=True)

		# Loop Select / Deselect / Add
		if loop_tool:
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK')
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', shift=True, properties=[('extend', True), ('ring', False)])
			self.kmi_set_replace(loop_tool, self.k_select, 'DOUBLE_CLICK', ctrl=True, properties=[('extend', False), ('deselect', True)])

		# Ring Select / Deselect / Add
		if ring_tool:
			self.kmi_set_replace(ring_tool, self.k_cursor, 'CLICK', ctrl=True, properties=[('ring', True), ('deselect', False), ('extend', False), ('toggle', False)])
			self.kmi_set_replace(ring_tool, self.k_cursor, 'CLICK', ctrl=True, shift=True, properties=[('ring', True), ('deselect', False), ('extend', True), ('toggle', False)])
			self.kmi_set_replace(ring_tool, self.k_cursor, 'DOUBLE_CLICK', ctrl=True, shift=True, properties=[('ring', True), ('deselect', True), ('extend', False), ('toggle', False)])

		# Select More / Less
		if more_tool:
			self.kmi_set_replace(more_tool, self.k_more, 'PRESS', shift=True)

		if less_tool:
			self.kmi_set_replace(less_tool, self.k_less, 'PRESS', shift=True)

		# Linked
		if linked_tool:
			self.kmi_set_replace(linked_tool, self.k_linked, 'PRESS')
			self.kmi_set_replace(linked_tool, self.k_linked, 'PRESS', ctrl=True, properties=[('deselect', True)])

	def selection_tool(self):
		select_tool = self.kmi_find(idname='wm.tool_set_by_name', properties=KeymapManager.bProp([('name', 'Select Box')]))
		if select_tool:
			self.kmi_prop_setattr(select_tool.properties, "name", 'Select')
			self.kmi_prop_setattr(select_tool.properties, "cycle", False)
		self.kmi_set_replace('wm.tool_set_by_name', self.k_menu, "PRESS", properties=[('name', 'Select'), ('cycle', False)])

	def right_mouse(self):
		kmi = self.kmi_find(idname='wm.call_menu', type='RIGHTMOUSE', value='PRESS')

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

	def hide_reveal(self, hide=None, unhide=None):
		if hide:
			self.kmi_set_replace(hide, 'H', 'PRESS', properties=[('unselected', False)])
			self.kmi_set_replace(hide, 'H', 'PRESS', ctrl=True, properties=[('unselected', True)])
		if unhide:
			self.kmi_set_replace(unhide, 'H', 'PRESS', alt=True, shift=True, properties=[('select', False)])

	def snap(self, snapping=None, snapping_prop=None):
		type = 'X'

		self.kmi_set_replace('wm.context_toggle', type, 'PRESS', properties=[('data_path', 'tool_settings.use_snap')])
		if snapping and snapping_prop:
			self.kmi_set_replace(snapping, type, 'PRESS', shift=True, properties=snapping_prop)

	def tool_smooth(self):
		self.kmi_set_replace('wm.tool_set_by_name', 'S', 'PRESS', shift=True, properties=[('name', 'Smooth')])
	
	def tool_proportional(self):
		self.modal_set_replace('PROPORTIONAL_SIZE', 'MOUSEMOVE', 'ANY', alt=True)
	
	def tool_smart_delete(self):
		self.kmi_set_active(False, type='DEL')
		self.kmi_set_replace('object.tila_smartdelete', 'DEL', 'PRESS')

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
		self.kmi_set_replace("wm.call_menu_pie", self.k_menu, "PRESS", ctrl=True, shift=True, alt=True)
		self.kmi_set_replace("wm.revert_without_prompt", "N", "PRESS", shift=True)
		self.kmi_set_replace('wm.console_toggle', 'TAB', 'PRESS', ctrl=True, shift=True)
		
		self.kmi_set_active(False, idname='wm.call_menu', type='F2')
		self.kmi_set_active(False, idname='wm.toolbar')
		self.selection_tool()

		# 3D View
		self.kmi_init(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.selection_tool()
		self.tool_smart_delete()
		# Disabling zoom key
		self.kmi_set_active(False, ctrl=True, type=self.k_cursor)
		self.kmi_set_active(False, idname='view3d.select_circle', type="C")
		self.navigation_keys(pan='view3d.move',
							orbit='view3d.rotate',
							dolly='view3d.dolly')

		self.selection_keys(select_tool='view3d.select', 
							lasso_tool='view3d.select_lasso',
                      		circle_tool='view3d.select_circle')
		
		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)
		self.snap(snapping='wm.call_panel', snapping_prop=[('name', 'VIEW3D_PT_snapping')])

		# 3d Cursor
		kmi = self.kmi_set_replace('view3d.cursor3d', self.k_cursor, 'CLICK', ctrl=True, alt=True, shift=True, properties=[('use_depth', True)])
		self.kmi_prop_setattr(kmi.properties, 'orientation', 'GEOM')
		self.kmi_set_replace('transform.translate', 'EVT_TWEAK_M', 'ANY', ctrl=True, alt=True, shift=True, properties=[('cursor_transform', True), ('release_confirm', True)])

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
                      		circle_tool='uv.select_circle',
                      		loop_tool='uv.select_loop',
                      		more_tool='uv.select_more',
                      		less_tool='uv.select_less',
                      		linked_tool='uv.select_linked_pick')
		
		self.kmi_set_replace('uv.cursor_set', self.k_cursor, 'PRESS', ctrl=True, alt=True, shift=True)
		self.tool_smooth()
		self.hide_reveal(hide='uv.hide', unhide='uv.reveal')
		self.snap(snapping='wm.context_menu_enum', snapping_prop=[('data_path', 'tool_settings.snap_uv_element')])

		# Mesh
		self.kmi_init(name='Mesh', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		
		self.selection_keys(shortestpath_tool='mesh.shortest_path_pick',
							loop_tool='mesh.loop_select',
                      		ring_tool='mesh.edgering_select',
							more_tool='mesh.select_more',
							less_tool='mesh.select_less',
							linked_tool='mesh.select_linked_pick')

		self.duplicate(duplicate='mesh.duplicate_move')
		self.hide_reveal(hide='mesh.hide', unhide='mesh.reveal')
		self.tool_smart_delete()

		self.tool_smooth()
		self.kmi_set_active(False, 'view3d.select_box')
		self.kmi_set_replace('mesh.bevel', 'B', 'PRESS')
		# self.kmi_set_replace('wm.tool_set_by_name', 'C', 'PRESS', properties=[('name', 'Knife')])
		self.kmi_set_replace('mesh.knife_tool', 'C', 'PRESS')
		self.kmi_set_replace('wm.tool_set_by_name', 'C', 'PRESS', alt=True, shift=True, properties=[('name', 'Loop Cut')])
		self.kmi_set_replace('mesh.bridge_edge_loops', 'B', 'PRESS', shift=True)
		self.kmi_set_replace('mesh.edge_collapse', 'DEL', 'PRESS', shift=True)
		self.kmi_set_replace('mesh.fill', 'P', 'PRESS', shift=True, properties=[('use_beauty', True)])
		self.kmi_set_replace('mesh.edge_face_add', 'P', 'PRESS')
		self.kmi_set_replace('mesh.flip_normals', 'F', 'PRESS')
		self.kmi_set_replace('mesh.subdivide', 'D', 'PRESS')

		# Object Mode
		self.kmi_init(name='Object Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.duplicate(duplicate='object.duplicate_move', duplicate_link='object.duplicate_move_linked')
		self.kmi_set_replace('object.delete', 'DEL', 'PRESS', ctrl=True, alt=True, shift=True, properties=[('use_global', True),('confirm', True)])

		# Curve
		self.kmi_init(name='Curve', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.duplicate(duplicate='curve.duplicate_move')
		self.kmi_set_replace('curve.select_linked', self.k_select, 'DOUBLE_CLICK', shift=True)
		self.kmi_set_replace('curve.select_linked_pick', self.k_select, 'DOUBLE_CLICK')
		self.kmi_set_replace('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.shortest_path_pick', self.k_select, 'PRESS', ctrl=True, shift=True)
		self.kmi_set_replace('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)

		# Outliner
		self.kmi_init(name='Outliner', space_type='OUTLINER', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.kmi_set_replace('outliner.item_rename', 'F2', 'PRESS')

		self.tool_smart_delete()
		self.kmi_set_replace('object.tila_emptymesh', 'N', 'PRESS', ctrl=True, alt=True, shift=True)

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

		# Node Editor
		self.kmi_init(name='Node Editor', space_type='NODE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='node.duplicate_move', duplicate_link='node.duplicate_move_keep_inputs')
		self.snap(snapping='wm.context_menu_enum', snapping_prop=[('data_path', 'tool_settings.snap_node_element')])

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

		# Grease Pencil
		self.kmi_init(name='Grease Pencil', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# Grease Pencil Stroke Edit Mode
		self.kmi_init(name='Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.duplicate(duplicate='gpencil.duplicate_move')

		# Transform Modal Map
		self.kmi_init(name='Transform Modal Map', space_type='EMPTY', region_type='WINDOW')
		self.tool_proportional()
		
		# Knife Tool Modal Map
		self.kmi_init(name='Knife Tool Modal Map', space_type='EMPTY', region_type='WINDOW')
		panning = self.kmi_find(propvalue='PANNING')
		panning.type = self.k_select
		panning.value = 'ANY'
		panning.any = True

		panning = self.kmi_find(propvalue='ADD_CUT')
		panning.type = 'RIGHTMOUSE'

		self.modal_set_replace('NEW_CUT', 'SPACE', 'PRESS')
		
		print("----------------------------------------------------------------")
		print("Assignment complete")
		print("----------------------------------------------------------------")
		print("")


def hp_keymaps():

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	k_viewfit = 'MIDDLEMOUSE'
	k_manip = 'LEFTMOUSE'
	k_cursor = 'RIGHTMOUSE'
	k_nav = 'MIDDLEMOUSE'
	k_menu = 'SPACE'
	k_select = 'LEFTMOUSE'
	k_lasso = 'RIGHTMOUSE'

	def global_keys():
		kmi = km.keymap_items.new("screen.userpref_show", "TAB", "PRESS", ctrl=True)
		kmi = km.keymap_items.new("wm.window_fullscreen_toggle", "F11", "PRESS")
		kmi = km.keymap_items.new('screen.animation_play', 'PERIOD', 'PRESS')
		kmi = km.keymap_items.new("popup.hp_properties", 'V',"PRESS", ctrl=True, shift=True)
	# kmi = km.keymap_items.new('gpencil.blank_frame_add', 'B', 'PRESS', key_modifier='FOUR')
# "ACCENT_GRAVE"
#Window
	km = kc.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('object.hide_viewport', 'H', 'PRESS')
	kmi = km.keymap_items.new('wm.save_homefile', 'U', 'PRESS', ctrl=True)     
	kmi = km.keymap_items.new('transform.translate', 'SPACE', 'PRESS')

	kmi = km.keymap_items.new('view3d.smart_delete', 'X', 'PRESS')
	kmi = km.keymap_items.new('mesh.dissolve_mode', 'X', 'PRESS',ctrl=True)
#kmi = km.keymap_items.new('transform.resize', 'SPACE', 'PRESS', alt=True)
	kmi = km.keymap_items.new('transform.rotate', 'C', 'PRESS')
	kmi = km.keymap_items.new("wm.window_fullscreen_toggle","F11","PRESS")
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True).properties.name="pie.areas"
	kmi = km.keymap_items.new("wm.revert_without_prompt","N","PRESS", alt=True)
	kmi = km.keymap_items.new("screen.redo_last","D","PRESS")
	kmi = km.keymap_items.new('wm.console_toggle', 'TAB', 'PRESS', ctrl=True, shift=True)     

	kmi = km.keymap_items.new("wm.call_menu_pie","S","PRESS", ctrl=True).properties.name="pie.save"
	kmi = km.keymap_items.new("wm.call_menu_pie","S","PRESS", ctrl=True, shift=True).properties.name="pie.importexport"
	kmi = km.keymap_items.new('script.reload', 'U', 'PRESS', shift=True)
	kmi = km.keymap_items.new("screen.repeat_last","THREE","PRESS", ctrl=True, shift=True)
	kmi = km.keymap_items.new("ed.undo","TWO","PRESS", ctrl=True, shift=True)
	kmi = km.keymap_items.new('popup.hp_materials', 'V', 'PRESS', shift=True)   
	kmi = km.keymap_items.new('screen.frame_jump', 'PERIOD', 'PRESS', shift=True)
# Map Image
	km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('image.view_all', k_viewfit, 'PRESS', ctrl=True, shift=True)
	kmi_props_setattr(kmi.properties, 'fit_view', True)
	kmi = km.keymap_items.new('image.view_pan', k_nav, 'PRESS', shift=True)
	kmi = km.keymap_items.new('image.view_zoom', k_nav, 'PRESS', ctrl=True)

# Map Node Editor
	km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('node.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('node.select_box', 'EVT_TWEAK_L', 'ANY')
	kmi_props_setattr(kmi.properties, 'extend', True)
	kmi_props_setattr(kmi.properties, 'tweak', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map View2D
	km = kc.keymaps.new('View2D', space_type='EMPTY', region_type='WINDOW', modal=False)
# Map Animation
	km = kc.keymaps.new('Animation', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('anim.change_frame', k_select, 'PRESS')

	

# Map Graph Editor
	km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('graph.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('graph.cursor_set', k_cursor, 'PRESS')
	# kmi = km.keymap_items.new('graph.select_lasso', 'EVT_TWEAK_L', 'ANY', shift=True, ctrl=True)
	# kmi_props_setattr(kmi.properties, 'extend', True)
	# kmi = km.keymap_items.new('graph.select_lasso', 'EVT_TWEAK_L', 'ANY', ctrl=True)
	# kmi_props_setattr(kmi.properties, 'deselect', True)
	kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY', ctrl=True, shift=True)
	kmi_props_setattr(kmi.properties, 'deselect', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY')
	kmi_props_setattr(kmi.properties, 'extend', False)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('graph.select_box', 'EVT_TWEAK_L', 'ANY', shift=True)
	kmi_props_setattr(kmi.properties, 'extend', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map UV Editor
	km = kc.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True, alt=True).properties.name="pie.rotate90"
	kmi = km.keymap_items.new('uv.select_lasso', 'EVT_TWEAK_L', 'ANY', shift=True, ctrl=True)
	kmi_props_setattr(kmi.properties, 'extend', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('uv.select_lasso', 'EVT_TWEAK_L', 'ANY', ctrl=True)
	kmi_props_setattr(kmi.properties, 'deselect', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('uv.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
	kmi_props_setattr(kmi.properties, 'extend', True)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('uv.select_border', 'EVT_TWEAK_L', 'ANY')
	kmi_props_setattr(kmi.properties, 'extend', False)
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
# Map Mask Editing
#    km = kc.keymaps.new('Mask Editing', space_type='EMPTY', region_type='WINDOW', modal=False)
#3D View
	km = kc.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('mesh.hp_extrude', 'SPACE', 'PRESS', shift=True)
	kmi = km.keymap_items.new('view3d.render_border', 'B', 'PRESS',shift=True, ctrl=True)
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True).properties.name="pie.areas"
#    kmi = km.keymap_items.new('view3d.select_lasso', 'EVT_TWEAK_L', 'ANY', alt=True)
	kmi = km.keymap_items.new('view3d.view_selected', k_nav, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('view3d.move', k_nav, 'PRESS', shift=True)
	kmi = km.keymap_items.new('view3d.zoom', k_nav, 'PRESS', ctrl=True)
	kmi = km.keymap_items.new('view3d.rotate', k_nav, 'PRESS')
	kmi = km.keymap_items.new('view3d.manipulator', k_manip, 'PRESS')
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True).properties.name="pie.select"
	kmi = km.keymap_items.new("wm.call_menu_pie", k_menu, 'PRESS',ctrl=True, alt=True).properties.name="pie.rotate90"
	kmi = km.keymap_items.new("wm.call_menu_pie", 'V', 'PRESS').properties.name="pie.view"
	kmi = km.keymap_items.new('wm.call_menu_pie', k_menu,'PRESS',ctrl=True, shift=True).properties.name="pie.pivots"
	kmi = km.keymap_items.new("wm.call_menu_pie","Z","PRESS").properties.name="pie.shading"
	kmi = km.keymap_items.new("wm.call_menu_pie","D","PRESS",ctrl=True, shift=True).properties.name="pie.specials"
	kmi = km.keymap_items.new("wm.call_menu_pie","ONE","PRESS").properties.name="pie.modifiers"
	kmi = km.keymap_items.new("wm.call_menu_pie","X","PRESS",shift=True).properties.name="pie.symmetry"
	kmi = km.keymap_items.new('wm.call_menu_pie', 'B', 'PRESS',ctrl=True).properties.name="pie.hp_boolean"
	kmi = km.keymap_items.new("screen.repeat_last","Z","PRESS",ctrl=True, alt=True)
	kmi = km.keymap_items.new("screen.repeat_last","WHEELINMOUSE","PRESS",ctrl=True, shift=True, alt=True)
	kmi = km.keymap_items.new("ed.undo","WHEELOUTMOUSE","PRESS",ctrl=True, shift=True, alt=True)
	kmi = km.keymap_items.new("view3d.screencast_keys","U","PRESS",alt=True)
	kmi = km.keymap_items.new("paint.sample_color","V","PRESS",ctrl=True, shift=True)
	kmi = km.keymap_items.new('view3d.select_lasso', k_select, 'CLICK_DRAG', shift=True, ctrl=True)
	kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG', ctrl=True).properties.mode='SUB'
	kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG', shift=True).properties.mode='ADD'
	kmi = km.keymap_items.new('view3d.select_box', k_select, 'CLICK_DRAG').properties.mode='SET'
	kmi = km.keymap_items.new("wm.search_menu","FIVE","PRESS")
	kmi = km.keymap_items.new("view3d.subdivision_toggle","TAB","PRESS")
	kmi = km.keymap_items.new("view3d.smart_snap_cursor","RIGHTMOUSE","PRESS",ctrl=True)
	kmi = km.keymap_items.new("view3d.smart_snap_origin","RIGHTMOUSE","PRESS",ctrl=True, shift=True)
#Mesh
	km = kc.keymaps.new(name='Mesh')
	global_keys()
	#kmi = km.keymap_items.new('view3d.extrude_normal', 'EVT_TWEAK_L', 'ANY', shift=True)
	kmi = km.keymap_items.new("mesh.dupli_extrude_cursor", 'E', 'PRESS')
	kmi = km.keymap_items.new("transform.edge_bevelweight", 'E', 'PRESS', ctrl=True, shift=True)
	#kmi = km.keymap_items.new("mesh.primitive_cube_add_gizmo", 'EVT_TWEAK_L', 'ANY', alt=True)
	kmi = km.keymap_items.new('view3d.select_through_border', k_select, 'CLICK_DRAG')
	kmi = km.keymap_items.new('view3d.select_through_border_add', k_select, 'CLICK_DRAG', shift=True)
	kmi = km.keymap_items.new('view3d.select_through_border_sub', k_select, 'CLICK_DRAG', ctrl=True)
	kmi = km.keymap_items.new("wm.call_menu_pie","A","PRESS", shift=True).properties.name="pie.add"
	kmi = km.keymap_items.new("wm.call_menu","W","PRESS").properties.name="VIEW3D_MT_edit_mesh_specials"
	kmi = km.keymap_items.new("screen.userpref_show","TAB","PRESS", ctrl=True)
	kmi = km.keymap_items.new("view3d.subdivision_toggle","TAB","PRESS")
#    kmi = km.keymap_items.new('mesh.select_all', k_select, 'CLICK', ctrl=True)
#    kmi_props_setattr(kmi.properties, 'action', 'INVERT')
	kmi = km.keymap_items.new('mesh.shortest_path_pick', 'LEFTMOUSE', 'CLICK',ctrl=True, shift=True).properties.use_fill=True
	kmi = km.keymap_items.new('mesh.select_linked', k_select, 'DOUBLE_CLICK')
	kmi_props_setattr(kmi.properties, 'delimit', {'SEAM'})
	kmi = km.keymap_items.new('mesh.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
	kmi_props_setattr(kmi.properties, 'delimit', {'SEAM'})
	kmi = km.keymap_items.new('mesh.select_more', 'WHEELINMOUSE', 'PRESS',ctrl=True, shift=True)    
	kmi = km.keymap_items.new('mesh.select_less', 'WHEELOUTMOUSE', 'PRESS',ctrl=True, shift=True)
	kmi = km.keymap_items.new('mesh.select_more', 'Z', 'PRESS',alt=True)    
	kmi = km.keymap_items.new('mesh.select_next_item', 'WHEELINMOUSE', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.select_next_item', 'Z', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.select_prev_item', 'WHEELOUTMOUSE', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.edgering_select', k_select, 'DOUBLE_CLICK', alt=True).properties.extend = False
	kmi = km.keymap_items.new('mesh.loop_multi_select', k_select, 'DOUBLE_CLICK', alt=True, shift=True)
	kmi = km.keymap_items.new('mesh.loop_select', k_select, 'PRESS', alt=True, shift=True).properties.extend = True
	kmi = km.keymap_items.new('mesh.loop_select', k_select, 'PRESS', alt=True).properties.extend = False
	kmi = km.keymap_items.new('mesh.normals_make_consistent', 'N', 'PRESS', ctrl=True).properties.inside = False
	kmi = km.keymap_items.new("wm.call_menu_pie","FOUR","PRESS").properties.name="GPENCIL_PIE_tool_palette"
	kmi = km.keymap_items.new("mesh.select_prev_item","TWO","PRESS")
	kmi = km.keymap_items.new("mesh.select_next_item","THREE","PRESS")
	kmi = km.keymap_items.new("mesh.select_less","TWO","PRESS", ctrl=True)
	kmi = km.keymap_items.new("mesh.select_more","THREE","PRESS", ctrl=True)
	kmi = km.keymap_items.new("mesh.inset", "SPACE", "PRESS", alt=True)
	kmi = km.keymap_items.new("mesh.push_and_slide","G","PRESS", shift=True)
#    kmi_props_setattr(kmi.properties, 'use_even_offset', True)
	kmi = km.keymap_items.new('mesh.separate_and_select', 'P', 'PRESS')
#    kmi = km.keymap_items.new('view3d.extrude_normal', 'B', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.bridge_edge_loops', 'B', 'PRESS', shift=True)
	kmi = km.keymap_items.new('mesh.bridge_edge_loops', 'B', 'PRESS', ctrl=True, shift=True).properties.number_cuts = 12
	kmi = km.keymap_items.new('transform.edge_bevelweight','B', 'PRESS', alt=True).properties.value = 1
	kmi = km.keymap_items.new('mesh.smart_bevel','B', 'PRESS')
	kmi = km.keymap_items.new('mesh.merge', 'J', 'PRESS', ctrl=True)
	kmi_props_setattr(kmi.properties, 'type', 'LAST')
	kmi = km.keymap_items.new('mesh.reveal', 'H', 'PRESS', ctrl=True, shift=True)
#Grease Pencil
	km = kc.keymaps.new('Grease Pencil', space_type='EMPTY', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('gpencil.select_linked', k_select, 'DOUBLE_CLICK')
	kmi = km.keymap_items.new('gpencil.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
	kmi = km.keymap_items.new('gpencil.select_box', k_select,'CLICK_DRAG')
	kmi_props_setattr(kmi.properties, 'mode', 'SET')
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('gpencil.select_box', k_select,'CLICK_DRAG', ctrl=True)
	kmi_props_setattr(kmi.properties, 'mode', 'SUB')
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)
	kmi = km.keymap_items.new('gpencil.select_box', k_select, 'CLICK_DRAG', shift=True)
	kmi_props_setattr(kmi.properties, 'mode', 'ADD')
	kmi_props_setattr(kmi.properties, 'wait_for_input',False)

#Object Mode
	km = kc.keymaps.new(name='Object Mode')
	global_keys()    
	kmi = km.keymap_items.new('object.select_all', k_select, 'CLICK_DRAG')
	kmi_props_setattr(kmi.properties, 'action', 'DESELECT')
#    kmi = km.keymap_items.new('object.select_all', k_select, 'CLICK', ctrl=True)
#    kmi_props_setattr(kmi.properties, 'action', 'INVERT')
	kmi = km.keymap_items.new('object.hide_view_clear', 'H', 'PRESS', ctrl=True, shift=True)

# Map Curve
	km = kc.keymaps.new('Curve', space_type='EMPTY', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('curve.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
	kmi = km.keymap_items.new('curve.select_linked_pick', k_select, 'DOUBLE_CLICK')
	kmi = km.keymap_items.new('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('curve.shortest_path_pick', k_select, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)

# Outliner
	km = kc.keymaps.new('Outliner', space_type='OUTLINER', region_type='WINDOW', modal=False)
	global_keys()

#    kmi = km.keymap_items.new('outliner.collection_drop', k_select, 'CLICK_DRAG',shift=True)
#    kmi = km.keymap_items.new('outliner.select_box', 'EVT_TWEAK_L', 'ANY')
	kmi = km.keymap_items.new('outliner.show_active', k_nav, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('wm.delete_without_prompt', 'X', 'PRESS')
# Map DOPESHEET_EDITOR
	km = kc.keymaps.new('Dopesheet Editor', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
	global_keys()
	kmi = km.keymap_items.new('time.start_frame_set', 'S', 'PRESS')
	kmi = km.keymap_items.new('time.end_frame_set', 'E', 'PRESS')
	kmi = km.keymap_items.new('time.view_all', 'HOME', 'PRESS')
	kmi = km.keymap_items.new('time.view_all', k_viewfit, 'PRESS', ctrl=True, shift=True)
	kmi = km.keymap_items.new('time.view_all', 'NDOF_BUTTON_FIT', 'PRESS')
	kmi = km.keymap_items.new('time.view_frame', 'NUMPAD_0', 'PRESS')

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
