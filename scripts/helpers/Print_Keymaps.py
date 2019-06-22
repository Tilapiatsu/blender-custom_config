import bpy

wm = bpy.context.window_manager
kca = wm.keyconfigs.addon
kcu = wm.keyconfigs.user

kmis = kcu.keymaps

for kmi in kmis:
	print(kmi.name)
