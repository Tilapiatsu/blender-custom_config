import bpy


addon_keymaps = []
# Keymap List
def add_keymap_automirror():
	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')

	kmi = km.keymap_items.new("automirror.automirror", 'X', 'PRESS', alt=True, shift=True, ctrl=True)
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.mirror_mirror", 'X', 'PRESS',alt=True, shift = True)
	kmi.properties.axis_x = True
	kmi.properties.axis_y = False
	kmi.properties.axis_z = False
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.mirror_mirror", 'Y', 'PRESS', alt=True, shift = True)
	kmi.properties.axis_x = False
	kmi.properties.axis_y = True
	kmi.properties.axis_z = False
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.mirror_mirror", 'Z', 'PRESS', alt=True, shift = True)
	kmi.properties.axis_x = False
	kmi.properties.axis_y = False
	kmi.properties.axis_z = True
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new("automirror.toggle_mirror", 'F', 'PRESS', alt=True, shift = True)
	addon_keymaps.append((km, kmi))


def remove_keymap_automirror():
	for l in addon_keymaps:
		for km, kmi in l:
			km.keymap_items.remove(kmi)

		l.clear()
		del l[:]
