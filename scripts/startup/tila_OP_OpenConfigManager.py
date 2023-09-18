import bpy
import addon_utils
bl_info = {
	"name": "Tila : Open Config Manager",
	"description": "Open the Config Manager",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (3, 6, 0),
	"location": "",
	"warning": "",
	"doc_url": "",
	"category": "Window"
}

addon_name = 'Tila_ConfigManager'

class TILA_OpenConfigManager(bpy.types.Operator):
	bl_idname = "window.tila_open_config_manager"
	bl_label = "Open Config Manager"
	bl_options = {'REGISTER'}

	auto_enable_addon : bpy.props.BoolProperty(name='force_object_isolate', default=True)

	def execute(self, context):
		if self.auto_enable_addon:
			if addon_name not in bpy.context.preferences.addons.keys():
				addon_utils.enable(addon_name, default_set=True, persistent=False, handle_error=None)
		
		bpy.ops.preferences.addon_show(module=addon_name)
		bpy.ops.tila.config_import_addon_list()

		return {'FINISHED'}


classes = (
	TILA_OpenConfigManager,
)

# _, unregister = bpy.utils.register_classes_factory(classes)
addon_keymaps = [] 

def register_keymaps():
    user_preferences = bpy.context.preferences
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon 
    km = kc.keymaps.new(name="Window", space_type='EMPTY', region_type='WINDOW')  
    kmi = km.keymap_items.new("window.tila_open_config_manager",'F4', 'PRESS', shift=False, ctrl=True, alt=False)     
    kmi.active = True
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    ''' clears all addon level keymap hotkeys stored in addon_keymaps '''
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps['3D View Generic']
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

def register():

	for cl in classes:
		bpy.utils.register_class(cl)

	register_keymaps()

def unregister():
	unregister_keymaps()

	for cl in classes:
		bpy.utils.unregister_class(cl)

if __name__ == "__main__":
	register()
