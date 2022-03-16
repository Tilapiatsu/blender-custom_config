bl_info = {
	"name": "Asset Creation Toolset",
	"description": "Toolset for easy create assets for Unity 3D/3D Stocks/etc.",
	"author": "Ivan 'mrven' Vostrikov",
	"wiki_url": "https://gum.co/hPXIh",
	"tracker_url": "https://blenderartists.org/t/asset-creation-toolset-2-6-1-update-23-jan-2020/686880",
	"version": (3, 1, 5),
	"blender": (2, 90, 0),
	"location": "3D View > Toolbox",
	"category": "Object",
}

modules_names = ['props', 'preferences', 'utils', 'origin_tools', 'rename_tools', 'uv_tools', 'import_export_tools', 'material_tools', 'other_tools']


modules_full_names = {}
for current_module_name in modules_names:
	modules_full_names[current_module_name] = ('{}.{}'.format(__name__, current_module_name))

import sys
import importlib


for current_module_full_name in modules_full_names.values():
	if current_module_full_name in sys.modules:
		importlib.reload(sys.modules[current_module_full_name])
	else:
		globals()[current_module_full_name] = importlib.import_module(current_module_full_name)
		setattr(globals()[current_module_full_name], 'modulesNames', modules_full_names)

def register():
	for current_module_name in modules_full_names.values():
		if current_module_name in sys.modules:
			if hasattr(sys.modules[current_module_name], 'register'):
				sys.modules[current_module_name].register()

def unregister():
	for current_module_name in modules_full_names.values():
		if current_module_name in sys.modules:
			if hasattr(sys.modules[current_module_name], 'unregister'):
				sys.modules[current_module_name].unregister()