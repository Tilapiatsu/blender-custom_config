import bpy

datatypes = []

for d in dir(bpy.data):
    if d.startswith('_'):
        continue

    data_type = getattr(bpy.data, d)

    if not isinstance(data_type, bpy.types.bpy_prop_collection):
        continue

    datatypes.append(d)

output_text = r'C:\Users\tilap\AppData\Roaming\Blender Foundation\Blender\\4.5\scripts\helpers\all_datatypes\blender_datatypes.txt'
with open(output_text, 'a') as f:
    f.write(f'Blender {bpy.app.version}\n{datatypes}\n\n')
bpy.ops.wm.quit_blender()