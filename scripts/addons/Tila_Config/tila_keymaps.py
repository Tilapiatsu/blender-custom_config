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

import bpy
import os


class bKeymap():
	def __init__(self, kmi):
		self.kmi = kmi
		self.idname = kmi.idname
		self.type = kmi.type
		self.value = kmi.value
		self.map_type = kmi.map_type
		
		self.alt = kmi.alt
		self.any = kmi.any
		self.ctrl = kmi.ctrl
		self.shift = kmi.shift
		self.oskey = kmi.oskey
		self.key_modifier = kmi.key_modifier
		self.properties = kmi.properties

		self.idname = kmi.idname

	def to_string(self):
		string = ''
		if self.any:
			string += "Any "
		if self.ctrl:
			string += "Ctrl "
		if self.alt:
			string += "Alt "
		if self.shift:
			string += "Shift "
		if self.oskey:
			string += "OsKey "
		if self.key_modifier != 'NONE':
			string += self.key_modifier + " "
		if self.type != "NONE":
			string += self.type
		return string


class bProp():
	def __init__(self, prop):
	
		for p in prop:
			setattr(self, p[0], p[1])


def kmi_props_setattr(kmi_props, attr, value):
	try:
		setattr(kmi_props, attr, value)
	except AttributeError:
		print("Warning: property '%s' not found in keymap item '%s'" %
			  (attr, kmi_props.__class__.__name__))
	except Exception as e:
		print("Warning: %r" % e)


def kmi_props_getattr(kmi_props, attr):
	try:
		return getattr(kmi_props, attr)
	except AttributeError:
		print("Warning: property '%s' not found in keymap item '%s'" % (attr, kmi_props.__class__.__name__))
	except Exception as e:
		print("Warning: %r" % e)


def kmi_props_list(kmi_props):
	prop = dir(kmi_props)[3:]
	skip = ['path', 'constraint_axis']
	for s in skip:
		if s in prop:
			prop.remove(s)
	return prop


class TilaKeymaps():
	keymap_List = {"new": [],
					"replaced": []}

	def __init__(self):

		# Define global variables
		self.wm = bpy.context.window_manager
		self.kca = self.wm.keyconfigs.addon
		self.kcu = self.wm.keyconfigs.user

		self.km = None
		self.ukmis = None
		self.akmis = None

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

	# Property
	@property
	def km_idname(self):
		try:
			return [k.idname for k in self.ukmis]
		except Exception as e:
			print("Warning: %r" % e)

	# Decorators
	def replace_km_dec(func):
		def func_wrapper(self, idname, type, value, alt=False, any=False, ctrl=False, shift=False, oskey=False, key_modifier='NONE', properties=()):
			
			new_kmi = func(self, idname, type, value, alt=alt, any=any, ctrl=ctrl, shift=shift, oskey=oskey, key_modifier=key_modifier, properties=properties)
			
			keymlap_List = {'km': self.km, 'kmis': self.ukmis, 'new_kmi': new_kmi}
			duplicates = [k for k in self.ukmis if k.idname == idname]

			if len(duplicates):
				for k in duplicates:
					if self.compare_tool(new_kmi, k):
						# TODO if multiple keymap is assigned to the same command, how to replace the proper one ?
						print("{} : '{}' tool found, replace keymap '{}' to '{}'".format(self.km.name, k.idname, k.to_string(), new_kmi.to_string()))

						k_old = bKeymap(k)

						keymlap_List['old_kmi'] = k_old
						keymlap_List['old_kmi_id'] = k.id

						# Replace keymap attribute
						self.replace_km(new_kmi, k)

						# Store keymap in class variable
						self.keymap_List["replaced"].append(keymlap_List)
						
						return k

				return new_kmi
		return func_wrapper

	# Functions

	def replace_km(self, km_src, km_dest):
		km_dest.key_modifier = km_src.key_modifier
		km_dest.map_type = km_src.map_type
		km_dest.type = km_src.type
		km_dest.value = km_src.value

		km_dest.any = km_src.any
		km_dest.alt = km_src.alt
		km_dest.ctrl = km_src.ctrl
		km_dest.shift = km_src.shift
		km_dest.oskey = km_src.oskey

	def compare_km(self, kmi1, kmi2):
		return kmi1.type == kmi2.type and kmi1.ctrl == kmi2.ctrl and kmi1.alt == kmi2.alt and kmi1.shift == kmi2.shift and kmi1.any == kmi2.any and	kmi1.oskey == kmi2.oskey and kmi1.key_modifier == kmi2.key_modifier and kmi1.map_type == kmi2.map_type and kmi1.value == kmi2.value

	def compare_tool(self, kmi1, kmi2):
		kmi1_props = kmi_props_list(kmi1.properties)
		kmi2_props = kmi_props_list(kmi2.properties)

		if len(kmi1_props) != len(kmi2_props):
			return False
		else:
			for i in range(len(kmi1_props)):
				if kmi1_props[i] != kmi2_props[i]:
					return False
				else:
					prop1 = kmi_props_getattr(kmi1.properties, kmi1_props[i])
					prop2 = kmi_props_getattr(kmi2.properties, kmi2_props[i])

					if prop1 != prop2:
						return False
			else:
				return True

	def compare_prop(self, prop1, prop2):
		if prop2 is None:
			return None
		else:
			kmi1_props = kmi_props_list(prop1)
			kmi2_props = kmi_props_list(prop2)

			if len(kmi1_props) != len(kmi2_props):
				return False
			else:
				for i in range(len(kmi1_props)):
					if kmi1_props[i] != kmi2_props[i]:
						return False
					else:
						p1 = kmi_props_getattr(prop1, kmi1_props[i])
						p2 = kmi_props_getattr(prop2, kmi2_props[i])

						if p1 != p2:
							return False
				else:
					return True

	@replace_km_dec
	def set_replace_km(self, idname, type, value, alt=False, any=False, ctrl=False, shift=False, oskey=False, key_modifier='NONE', properties=()):
		kmi = self.set_km(idname, type, value, alt=alt, any=any, ctrl=ctrl, shift=shift, oskey=oskey, key_modifier=key_modifier, properties=properties)
		return kmi

	def set_km(self, idname, type, value, alt=False, any=False, ctrl=False, shift=False, oskey=False, key_modifier='NONE', properties=()):
		kmi = self.km.keymap_items.new(idname, type, value, alt=alt, any=any, ctrl=ctrl, shift=shift, oskey=oskey, key_modifier=key_modifier)
		kmi.active = True
		for p in properties:
			kmi_props_setattr(kmi.properties, p[0], p[1])
		print("{} : assigning new tool '{}' to keymap '{}'".format(self.km.name, kmi.idname, kmi.to_string()))

		# Store keymap in class variable
		self.keymap_List["new"].append((self.km, kmi))

		return kmi

	def find_km(self, idname=None, type=None, value=None, alt=None, any=None, ctrl=None, shift=None, oskey=None, key_modifier=None, properties=None):
		def compare_attr(src_attr, comp_attr):
			if comp_attr is not None:
				if comp_attr != src_attr:
					return False
				else:
					return True
			else:
				return None

		for k in self.ukmis:
			if compare_attr(k.idname, idname) is False:
				continue

			if compare_attr(k.type, type) is False:
				continue

			if compare_attr(k.value, value) is False:
				continue
			
			if compare_attr(k.alt, alt) is False:
				continue

			if compare_attr(k.any, any) is False:
				continue

			if compare_attr(k.ctrl, ctrl) is False:
				continue

			if compare_attr(k.shift, shift) is False:
				continue

			if compare_attr(k.oskey, oskey) is False:
				continue

			if compare_attr(k.key_modifier, key_modifier) is False:
				continue

			if self.compare_prop(k.properties, properties) is False:
				continue
			
			return k

		else:
			return None		

	# Global Keymap Functions

	def init_kmi(self, name, space_type='EMPTY', region_type='WINDOW', modal=False, tool=False):
		self.ukmis = self.kcu.keymaps[name].keymap_items
		self.km = self.kca.keymaps.new(name, space_type=space_type, region_type=region_type, modal=modal, tool=tool)
		self.akmis = self.kca.keymaps[name].keymap_items

	def global_keys(self):
		self.set_replace_km("screen.userpref_show", "TAB", "PRESS", ctrl=True)
		self.set_replace_km("wm.window_fullscreen_toggle", "F11", "PRESS")
		self.set_replace_km('screen.animation_play', self.k_menu, 'PRESS', shift=True)
		self.set_replace_km("popup.hp_properties", 'V', "PRESS", ctrl=True, shift=True)

	def navigation_keys(self, pan=None, orbit=None, dolly=None):
		if orbit:
			self.set_replace_km(orbit, self.k_manip, "PRESS", alt=True)
		if pan:
			self.set_replace_km(pan, self.k_manip, "PRESS", alt=True, shift=True)
		if dolly:
			self.set_replace_km(dolly, self.k_manip, "PRESS", alt=True, ctrl=True)

	def selection_keys(self,
						select_tool=None, 
						lasso_tool=None,
						shortestpath_tool=None,
						loop_tool=None, ring_tool=None,
						more_tool=None, less_tool=None,
						linked_tool=None):

		# Select / Deselect / Add
		if select_tool:
			self.set_replace_km(select_tool, self.k_select, 'CLICK')
			self.set_replace_km(select_tool, self.k_select, 'CLICK', shift=True, properties=[('extend', True)])
			self.set_replace_km(select_tool, self.k_select, 'CLICK', ctrl=True, properties=[('deselect', True)])
	
		# Lasso Select / Deselect / Add
		if lasso_tool:
			self.set_replace_km(lasso_tool, self.k_lasso, 'ANY')
			self.set_replace_km(lasso_tool, self.k_lasso, 'ANY', shift=True, properties=[('mode', 'ADD')])
			self.set_replace_km(lasso_tool, self.k_lasso, 'ANY', ctrl=True, properties=[('mode', 'SUB')])

		#  shortest Path Select / Deselect / Add
		if shortestpath_tool:
			self.set_replace_km(shortestpath_tool, self.k_context, 'CLICK', shift=True)

		# Loop Select / Deselect / Add
		if loop_tool:
			self.set_replace_km(loop_tool, self.k_select, 'DOUBLE_CLICK')
			self.set_replace_km(loop_tool, self.k_select, 'DOUBLE_CLICK', shift=True, properties=[('extend', True), ('ring', False)])
			self.set_replace_km(loop_tool, self.k_select, 'DOUBLE_CLICK', ctrl=True, properties=[('extend', False), ('deselect', True)])

		# Ring Select / Deselect / Add
		if ring_tool:
			self.set_replace_km(ring_tool, self.k_cursor, 'CLICK', ctrl=True, properties=[('ring', True), ('deselect', True), ('extend', False), ('toggle', False)])
			self.set_replace_km(ring_tool, self.k_cursor, 'CLICK', ctrl=True, shift=True, properties=[('ring', True), ('deselect', False), ('extend', True), ('toggle', False)])
			self.set_replace_km(ring_tool, self.k_cursor, 'DOUBLE_CLICK', ctrl=True, properties=[('ring', True), ('deselect', True), ('extend', False), ('toggle', False)])

		# Select More / Less
		if more_tool:
			self.set_replace_km(more_tool, self.k_more, 'PRESS', shift=True)

		if less_tool:
			self.set_replace_km(less_tool, self.k_less, 'PRESS', shift=True)

		# Linked
		if linked_tool:
			self.set_replace_km(linked_tool, self.k_linked, 'PRESS')

	def selection_tool(self):
		self.set_replace_km('wm.tool_set_by_name', self.k_menu, "PRESS", properties=[('name', 'Select'), ('cycle', False)])

	def right_mouse(self):
		kmi = self.find_km(idname='wm.call_menu', type='RIGHTMOUSE', value='PRESS')

		if kmi is None:
			print('Cant find right mouse button contextual menu')
		else:
			kmi.value = 'RELEASE'

	# Keymap define

	def set_tila_keymap(self):
		print("----------------------------------------------------------------")
		print("Assigning Tilapiatsu's keymaps")
		print("----------------------------------------------------------------")
		print("")

		# Window
		self.init_kmi(name='Window', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.set_replace_km("wm.call_menu_pie", self.k_menu, "PRESS", ctrl=True, shift=True, alt=True)
		self.set_replace_km("wm.revert_without_prompt", "N", "PRESS", shift=True)
		self.set_replace_km('wm.console_toggle', 'TAB', 'PRESS', ctrl=True, shift=True)
		self.set_replace_km('outliner.item_rename', 'F2', 'PRESS')

		toolbar = self.find_km(idname='wm.toolbar')
		if toolbar:
			toolbar.active = False

		# 3D View
		self.init_kmi(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		select_tool = self.find_km(idname='wm.tool_set_by_name', properties=bProp((('text', 'Select Box'))))
		if select_tool:
			kmi_props_setattr(select_tool, "text", 'Select')

		self.selection_tool()
		self.navigation_keys(pan='view3d.move',
							orbit='view3d.rotate',
							dolly='view3d.dolly')

		self.selection_keys(select_tool='view3d.select', 
							lasso_tool='view3d.select_lasso')
		
		# 3d Cursor
		kmi = self.set_replace_km('view3d.cursor3d', self.k_cursor, 'CLICK', ctrl=True, alt=True, shift=True, properties=[('use_depth', True)])
		kmi_props_setattr(kmi.properties, 'orientation', 'GEOM')
		self.set_replace_km('transform.translate', 'EVT_TWEAK_M', 'ANY', ctrl=True, alt=True, shift=True, properties=[('cursor_transform', True), ('release_confirm', True)])

		# View2D
		self.init_kmi(name='View2D', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')

		# View2D buttons List
		self.init_kmi(name='View2D Buttons List', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='view2d.pan', orbit=None, dolly='view2d.zoom')

		# Image
		self.init_kmi(name='Image', space_type='IMAGE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()
		self.navigation_keys(pan='image.view_pan', orbit=None, dolly='image.view_zoom')

		# UV Editor
		self.init_kmi(name='UV Editor', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# Mesh
		self.init_kmi(name='Mesh', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.selection_keys(shortestpath_tool='mesh.shortest_path_pick',
							loop_tool='mesh.loop_select',
							ring_tool='mesh.loop_select',
							more_tool='mesh.select_more',
							less_tool='mesh.select_less',
							linked_tool='mesh.select_linked_pick')

		# Object Mode
		self.init_kmi(name='Object Mode', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()

		# Curve
		self.init_kmi(name='Curve', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.selection_tool()
		self.right_mouse()
		self.set_replace_km('curve.select_linked', self.k_select, 'DOUBLE_CLICK', shift=True)
		self.set_replace_km('curve.select_linked_pick', self.k_select, 'DOUBLE_CLICK')
		self.set_replace_km('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
		self.set_replace_km('curve.shortest_path_pick', self.k_select, 'PRESS', ctrl=True, shift=True)
		self.set_replace_km('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)

		# Outliner
		self.init_kmi(name='Outliner', space_type='OUTLINER', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# Dopesheet
		self.init_kmi(name='Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW')
		# self.ukmis = self.kcu.keymaps['Dopesheet'].keymap_items
		# self.km = self.kca.keymaps.new('Dopesheet Editor', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
		self.global_keys()
		self.right_mouse()

		# Grease Pencil
		self.init_kmi(name='Grease Pencil', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# Graph Editor
		self.init_kmi(name='Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# Node Editor
		self.init_kmi(name='Node Editor', space_type='NODE_EDITOR', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

		# Animation
		self.init_kmi(name='Animation', space_type='EMPTY', region_type='WINDOW')
		self.global_keys()
		self.right_mouse()

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
	k_lasso =  'RIGHTMOUSE'

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
